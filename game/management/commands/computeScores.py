from django.db.models import Count, Avg, Sum, Q

from game.models import Player, Position, Team, Matchup
from data.models import YearData, GameData, DataPoint

from django.core.management.base import NoArgsCommand, make_option
from django.core.exceptions import ObjectDoesNotExist

import numpy as np
from sklearn import neighbors
from sklearn import preprocessing
from sklearn.svm import SVR

import os

class Command(NoArgsCommand):

	help = ''
	numTeams = 32
	cDict = {
		'QB': 13,
		'RB': 1,
		'WR': 100,
		'TE': 100, 
		'K': 10
	}
	avgPtsEarnedDict = {} # Maps (position ID, week number) => avg pts earned
	avgDefPtsAllowedDict = {} # Maps (position ID, week number) => avg pts allowed

	option_list = NoArgsCommand.option_list + (
		make_option('--verbose', action='store_true'),
	)

	def handle_noargs(self, **options):
		#for pos in Position.objects.all().exclude(id=5):
			#self.getDataForModel(pos, 2014, 12, True)
			#self.computePlayerProjections(pos, 13)
		#self.computePlayerPerformanceScores(2014, 13)

		

	# Computes and saves all player projections for the given position in the week
	# ASSUMES YEAR IS 2014, and given week number must be >=2
	def computePlayerProjections(self, position, proj_week_number):
		print 'COMPUTING PROJECTIONS FOR', position.abbr, 'WEEK', proj_week_number
		year = 2014
		week_number = proj_week_number - 1

		weekError = 0
		espnWeekError = 0

		# Model parameters
		norm = 'l2'
		kernel = 'rbf'
		c = self.cDict[position.abbr]
		epsilon = 0.0
		gamma = 7.0

		# Load the 2013 data that was previously computed and saved to file
		xArray2013 = np.loadtxt('projectionArrays/xArray2013_'+
			position.abbr.lower()+'.txt')
		yArray2013 = np.loadtxt('projectionArrays/yArray2013_'+
			position.abbr.lower()+'.txt')

		# Get the data for the week and concat with 2013 data
		xArray2014 = np.loadtxt('projectionArrays/xArray2014_week'+str(week_number)+
			'_'+position.abbr.lower()+'.txt')
		yArray2014 = np.loadtxt('projectionArrays/yArray2014_week'+str(week_number)+
			'_'+position.abbr.lower()+'.txt')
		xArray = np.concatenate((xArray2013, xArray2014))
		yArray = np.concatenate((yArray2013, yArray2014))

		# Normalize the data
		normalizer = preprocessing.Normalizer(norm)
		xArray = normalizer.fit_transform(xArray)

		# Build the model
		model = self.buildSVMModel(xArray, yArray, kernel, c, epsilon, gamma)
		#model = self.buildKNNModel(xArray, yArray, numNeighbors, 'uniform')

		# Predict for every player of this position
		for p in Player.objects.filter(position=position).order_by('id'):
			try:
				gd = GameData.objects.get(player=p, 
					matchup__year=year, matchup__week_number=proj_week_number)
				projection = self.playerProjection(model, normalizer, p, year, proj_week_number)
				if projection is None or gd.data.id==1 or gd.espn_projection is None: continue
				weekError += abs(gd.data.points - projection)
				espnWeekError += abs(gd.data.points - gd.espn_projection)
				print p.id, p.name, projection[0]
				gd.projection = projection[0]
				gd.save()
			except ObjectDoesNotExist:
				continue
		#return (weekError, espnWeekError)

	# Computes the projection of the given player in the year and week
	#	using the model provided
	def playerProjection(self, model, normalizer, player, year, week_number):
		# Make the prediction!
		vect = self.playerFeatureVector(player, year, week_number)
		if vect is None: return None
		vect = normalizer.transform(vect)
		return model.predict(vect)


	# Computes the performance scores for each player in the given year/week
	# Saves to database
	def computePlayerPerformanceScores(self, year, week_number):
		print 'COMPUTING PERFORMANCE SCORES:', year, 'WEEK', week_number
		players = Player.objects.all().order_by('id')
		matchups = Matchup.objects.filter(year=year, week_number=week_number)
		
		# Calculate and save score for every player
		for player in players:
			yd = YearData.objects.get(player=player, year=year)
			if yd.team.id == 33: continue
			try:
				matchup = matchups.get(Q(home_team=yd.team) | Q(away_team=yd.team))
				gameData = GameData.objects.get(player=player, matchup=matchup)
			except ObjectDoesNotExist:
				continue

			# If it's a bye week, set score as 0
			if matchup.bye: score = 0
			else: score = self.playerPerformanceScore(player, year, week_number)

			# Save the score
			print player.id, player.name, score
			gameData.performance_score = score
			gameData.save()


	# Computes the performance score of the given player in the year and week 
	# player is a Player object, opponent is a Team object
	# The performance score is computed as follows:
	#	offScore = (avg fantasy pts earned this season) - 
	#		(league avg fantasy pts earned across all players of this pos and depth_pos)
	#	defScore = (avg fantasy pts earned by all players of 
	#			    this pos and depth_pos across each defense) - 
	#		(leage avg fantasy pts earned by players of this pos and depth_pos against this defense)
	#	score = offScore - defScore
	def playerPerformanceScore(self, player, year, week_number):
		vect = self.playerFeatureVector(player, year, week_number)
		if vect is None: return None
		offScore = vect[0][1]
		defScore = vect[0][3]

		# Compute and return the performance score
		score = offScore - defScore
		return score


	# Gets the data for building the prediction model
	# Returns a tuple of (x, y) -- two numpy arrays corresponding to the feature
	#	vectors and "labels" or actual fantasy points earned for players of 
	#	this position in the given year and through the given week
	# Uses the given year's data points through the given week as training data
	# Computes feature vectors for each week through week_number, using cumulative
	#	data from week 1 through that week
	# Four features for each player in each week up to given week number (not inclusive):
	# 1) weekly avg fantasy points earned so far by this player
	# 2) difference in (1) and league average across all players of this position
	# 3) weekly avg fantasy points allowed to players of this position
	# 4) diff in (3) and league average across all defenses
	def getDataForModel(self, position, year, cur_week_number, write_file=True):
		print 'GETTING DATA for', position.abbr, 'through week', cur_week_number, year

		# Dictionaries of data that will be used in feature vectors
		dataDict = {} # Maps (player ID, week) to arrays of features
		labelsDict = {} # Maps (player ID, week) to actual fantasy points earned that week

		# Get data from each week up to the given week number
		for week_number in range(1, cur_week_number+1):
			# Get matchups for this week
			matchups = Matchup.objects.filter(year=year, week_number=week_number)

			# Go through each team and compute each defense's average points allowed
			defDict = {} # Maps team ID to average points allowed
			for team in Team.objects.exclude(id=33):
				defPtsAllowed = self.computeAveragePointsAllowed(team, position, year, week_number)
				defDict[team.id] = defPtsAllowed

			# Go through each player of this position and compute points earned
			for player in Player.objects.filter(position=position).order_by('id'):
				# Assign the values in the dictionary
				featureVect = self.playerFeatureVector(player, year, week_number)
				if featureVect is None: continue
				dataDict[(player.id, week_number)] = featureVect

				# Assign actual number of fantasy points earned as "label"
				try: 
					curWeekPts = GameData.objects.get(player=player, 
						matchup__year=year, matchup__week_number=week_number).data.points
				except: curWeekPts = None
				labelsDict[(player.id, week_number)] = curWeekPts if curWeekPts is not None else 0

		# Get numpy arrays of data and "labels" (fantasy points)
		xArray = self.dictToNumpy(dataDict, 4)
		yArray = self.dictToNumpy(labelsDict, 1)
		if write_file:
			np.savetxt(('projectionArrays/xArray'+str(year)+'_week'+str(cur_week_number)+
				'_'+position.abbr.lower()+'.txt'), xArray)
			np.savetxt(('projectionArrays/yArray'+str(year)+'_week'+str(cur_week_number)+
				'_'+position.abbr.lower()+'.txt'), yArray)
		return (xArray, yArray)


	# Builds and fits the KNN model with the provided parameters
	# weights is either 'uniform' or 'distance'
	def buildKNNModel(self, xArray, yArray, numNeighbors, weights):
		print 'BUILDING KNN MODEL with parameters:', numNeighbors, 'neighbors,', weights, 'weighting'
		knn = neighbors.KNeighborsRegressor(n_neighbors=numNeighbors, weights=weights)
		#knn = neighbors.RadiusNeighborsRegressor(radius=numNeighbors, weights=weights)
		knn.fit(xArray, yArray)
		return knn

	# Builds and fits the SVM model with the provided kernel parameter
	# kernel is 'linear', 'poly', 'rbf', 'sigmoid', 'precomputed'
	def buildSVMModel(self, xArray, yArray, kernel, c, epsilon, gamma):
		print ('BUILDING SVM MODEL with parameters:'+kernel+', c:'+str(c)+
			', epsilon:'+str(epsilon)+', gamma:'+str(gamma))
		svm = SVR(kernel=kernel, C=c, epsilon=epsilon, gamma=gamma)
		svm.fit(xArray, yArray)
		return svm

	# Convert data from inputDict to numpy array
	# yDim is the number of columns in the array
	# Returns an array ordered by key
	def dictToNumpy(self, inputDict, yDim):
		npArray = np.zeros([ len(inputDict), yDim ])
		if yDim == 1: npArray = np.zeros([ len(inputDict) ])
		i = 0
		keyList = inputDict.keys()
		keyList.sort()
		for key in keyList:
			npArray[i] = inputDict[key]
			i += 1
		return npArray

	# Returns a numpy array that is the feature vector for the given player
	# for the given year / week
	def playerFeatureVector(self, player, year, week_number):
		# Get the player's team in the given year
		position = player.position
		playerTeam = YearData.objects.get(year=year, player=player).team
		if playerTeam is None or playerTeam.id == 33: return None

		# Get the week's matchup; if it's a bye week then no projection
		matchup = Matchup.objects.get(Q(home_team=playerTeam) | Q(away_team=playerTeam), 
			year=year, week_number=week_number)
		if matchup.bye: return None

		# Compute weekly avg points earned by this player
		ptsEarned = self.computeAveragePointsEarned(player, year, week_number)
		if ptsEarned is None: return None

		# Compute avg points earned across all players of this position and difference 
		# between it and the player's weekly avg
		if (position.id, week_number) not in self.avgPtsEarnedDict:
			self.avgPtsEarnedDict[(position.id, week_number)] = self.computeLeagueAveragePointsEarned(
				position, year, week_number)
		diffPtsEarned = ptsEarned - self.avgPtsEarnedDict[(position.id, week_number)]

		# Compute avg pts allowed to players of this position across all defenses
		opponent = (matchup.home_team if playerTeam.id==matchup.away_team.id else matchup.away_team)
		if (position.id, week_number) not in self.avgDefPtsAllowedDict:
			self.avgDefPtsAllowedDict[(position.id, week_number)] = self.computeLeagueAveragePointsAllowed(
				position, year, week_number)

		# Compute points allowed to players of this position by opponent's defense and 
		# difference between it and league average
		ptsAllowed = self.computeAveragePointsAllowed(opponent, position, year, week_number)
		diffPtsAllowed = ptsAllowed - self.avgDefPtsAllowedDict[(position.id, week_number)]

		vect = np.array([[ptsEarned, diffPtsEarned, ptsAllowed, diffPtsAllowed]])
		return vect

	# Computes the player's weekly average fantasy points earned through week_number
	def computeAveragePointsEarned(self, player, year, week_number):
		numWeeksPlayed = len(Matchup.objects.filter(Q(home_team=player.team) | 
			Q(away_team=player.team), year=year, week_number__lte=week_number, bye=False))
		if numWeeksPlayed == 0: return None

		ptsEarned = GameData.objects.filter(player=player, matchup__year=year, 
			matchup__week_number__lte=week_number).aggregate(
			Sum('data__points'))['data__points__sum']
		if ptsEarned is not None: #and ptsEarned > 0:
			ptsEarned /= (numWeeksPlayed*1.0)
		return ptsEarned

	# Computes the league weekly average points earned across players of position
	# If depth_pos is given, then compute average across only players of depth_pos
	def computeLeagueAveragePointsEarned(self, position, year, week_number):
		sumPlayerAverages = 0
		numPlayers = 0

		for p in Player.objects.filter(position=position):
			weeklyAvgPtsEarned = self.computeAveragePointsEarned(p, year, week_number)
			if weeklyAvgPtsEarned is not None:# and weeklyAvgPtsEarned > 0:
				sumPlayerAverages += weeklyAvgPtsEarned
				numPlayers += 1
		weeklyAvg = sumPlayerAverages*1.0 / numPlayers
		return weeklyAvg

	# Computes weekly average fantasy points allowed on team's defense by players of position
	# If depth_pos is given, then compute average across only players of depth_pos
	def computeAveragePointsAllowed(self, team, position, year, week_number):
		numWeeksPlayed = len(Matchup.objects.filter(Q(home_team=team) | 
			Q(away_team=team), year=year, week_number__lte=week_number, bye=False))
		gameDataList = GameData.objects.filter(Q(matchup__home_team=team) | 
			Q(matchup__away_team=team), player__position=position,
			matchup__year=year, matchup__week_number__lte=week_number).exclude(
			player__team=team)

		defPtsAllowed = gameDataList.aggregate(
			Sum('data__points'))['data__points__sum'] / (numWeeksPlayed*1.0)
		return defPtsAllowed

	# Computes league weekly average points allowed across all defenses to players of position
	def computeLeagueAveragePointsAllowed(self, position, year, week_number):
		sumAverages = 0
		for team in Team.objects.exclude(id=33):
			weeklyAvgPtsAllowed = self.computeAveragePointsAllowed(
				team, position, year, week_number)
			sumAverages += weeklyAvgPtsAllowed
		weeklyAvg = sumAverages*1.0 / self.numTeams
		return weeklyAvg






