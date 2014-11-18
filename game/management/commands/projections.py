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
	avgPtsEarnedDict = {} # Maps (position ID, week number) => avg pts earned
	avgDefPtsAllowedDict = {} # Maps (position ID, week number) => avg pts allowed

	option_list = NoArgsCommand.option_list + (
		make_option('--verbose', action='store_true'),
	)

	def handle_noargs(self, **options):
		outfile = open('projectionArrays/resultsWeekly_rb_SVM.txt', 'a')
		seasonOutfile = open('projectionArrays/resultsTotal_rb_SVM.txt', 'a')

		pos = Position.objects.get(id=2)
		year = 2014

		norm = 'l2'
		kernel = 'rbf'
		c = 100
		epsilon = 0.0
		gamma = 7.0

		# Load the 2013 data that was previously computed and saved to file
		xArray2013 = np.loadtxt('projectionArrays/xArray2013_rb.txt')
		yArray2013 = np.loadtxt('projectionArrays/yArray2013_rb.txt')

		# Go through different parameters
		computedSeasonError = 0
		espnSeasonError = 0

		# Go through each week of the 2014 season
		for week_number in range(1, 10):
			# Get the data and concat with 2013 data
			xArray = np.loadtxt('projectionArrays/xArray2014_week'+str(week_number)+'_rb.txt')
			yArray = np.loadtxt('projectionArrays/yArray2014_week'+str(week_number)+'_rb.txt')
			xArray = np.concatenate((xArray2013, xArray))
			yArray = np.concatenate((yArray2013, yArray))

			# Normalize the data
			normalizer = preprocessing.Normalizer(norm)
			xArray = normalizer.fit_transform(xArray)

			# Build the model
			model = self.buildSVMModel(xArray, yArray, kernel, c, epsilon, gamma)

			# Predict for every player. Have to use week_number+1 for playerProjection
			# so that we test on data that's not in the training data set
			totalError = 0
			espnError = 0
			test_week_number = week_number + 1
			print 'TESTING MODEL for week', test_week_number
			for p in Player.objects.filter(position=pos).order_by('id'):
				try:
					gd = GameData.objects.get(player=p, 
						matchup__year=year, matchup__week_number=test_week_number)
					projection = self.playerProjection(model, normalizer, p, year, test_week_number, xArray)
					if projection is None or gd.data.id==1 or gd.espn_projection is None: continue
					totalError += abs(gd.data.points - projection)
					espnError += abs(gd.data.points - gd.espn_projection)
				except ObjectDoesNotExist:
					continue

			computedSeasonError += totalError
			espnSeasonError += espnError

			# Write to file
			outstring = (pos.name+','+str(year)+','+str(test_week_number)+','+kernel+','+
				str(c)+','+str(epsilon)+','+str(gamma)+','+
				norm+','+str(totalError)+','+str(espnError)+'\n')
			if totalError < espnError: print 'LOWER ERROR'
			print outstring
			outfile.write(outstring)
		
		# Write total season results to file
		seasonOutstring = (pos.name+','+str(year)+','+kernel+','+
			str(c)+','+str(epsilon)+','+str(gamma)+','+
			norm+','+str(computedSeasonError)+','+str(espnSeasonError)+'\n')
		print seasonOutstring
		seasonOutfile.write(seasonOutstring)


	# Computes the projection of the given player in the year and week
	#	using the model provided
	def playerProjection(self, model, normalizer, player, year, week_number, xArray):
		# Get the player's team in the given year
		position = player.position
		playerTeam = YearData.objects.get(year=year, player=player).team
		if playerTeam.id == 33: return None

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

		# Make the prediction!
		vect = np.array([[ptsEarned, diffPtsEarned, ptsAllowed, diffPtsAllowed]])
		vect = normalizer.transform(vect)
		return model.predict(vect)

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
	def getDataForModel(self, position, year, cur_week_number):
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
				# Get player's team in this year
				playerTeam = YearData.objects.get(year=year, player=player).team
				if playerTeam is None or playerTeam.id == 33: continue # Don't need FA data

				# Get player's matchup for this week; if bye week, continue
				curMatchup = matchups.get(Q(home_team=playerTeam) | Q(away_team=playerTeam))
				if curMatchup.bye: continue

				# Compute average fantasy points earned by this player so far
				ptsEarned = self.computeAveragePointsEarned(player, year, week_number)
				if ptsEarned is None: continue

				# Get opponent's defense's data from already comptued data
				opponent = (curMatchup.home_team if playerTeam.id==curMatchup.away_team.id 
					else curMatchup.away_team)
				defPtsAllowed = defDict[opponent.id]

				# Compute league average points earned / allowed if not already computed
				if (position.id, week_number) not in self.avgPtsEarnedDict:
					self.avgPtsEarnedDict[(position.id, week_number)] = self.computeLeagueAveragePointsEarned(
						position, year, week_number)
				if (position.id, week_number) not in self.avgDefPtsAllowedDict:
					self.avgDefPtsAllowedDict[(position.id, week_number)] = self.computeLeagueAveragePointsAllowed(
						position, year, week_number)

				# Assign the values in the dictionary
				dataDict[(player.id, week_number)] = [
					ptsEarned, 
					ptsEarned - self.avgPtsEarnedDict[(position.id, week_number)], 
					defPtsAllowed, 
					defPtsAllowed - self.avgDefPtsAllowedDict[(position.id, week_number)]
				]

				# Assign actual number of fantasy points earned as "label"
				try: 
					curWeekPts = GameData.objects.get(player=player, 
						matchup__year=year, matchup__week_number=week_number).data.points
				except: curWeekPts = None
				labelsDict[(player.id, week_number)] = curWeekPts if curWeekPts is not None else 0

		# Get numpy arrays of data and "labels" (fantasy points)
		xArray = self.dictToNumpy(dataDict, 4)
		yArray = self.dictToNumpy(labelsDict, 1)
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

	# Accepts an array of distances, and returns an array of the same shape containing the weights
	def distanceWeight(self, distances):
		weights = []
		for dist in distances[0]:
			w = 1.0 / (dist + 1.0)
			weights.append(w)
		return np.array([weights])


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
	def computeAveragePointsAllowed(self, team, position, year, week_number):
		numWeeksPlayed = len(Matchup.objects.filter(Q(home_team=team) | 
			Q(away_team=team), year=year, week_number__lte=week_number, bye=False))
		defPtsAllowed = GameData.objects.filter(Q(matchup__home_team=team) | 
			Q(matchup__away_team=team), player__position=position,
			matchup__year=year, matchup__week_number__lte=week_number).exclude(
			player__team=team).aggregate(
			Sum('data__points'))['data__points__sum'] / (numWeeksPlayed*1.0)
		return defPtsAllowed

	# Computes league weekly average points allowed across all defenses to players of position
	def computeLeagueAveragePointsAllowed(self, position, year, week_number):
		sumAverages = 0
		for team in Team.objects.exclude(id=33):
			weeklyAvgPtsAllowed = self.computeAveragePointsAllowed(team, position, year, week_number)
			sumAverages += weeklyAvgPtsAllowed
		weeklyAvg = sumAverages*1.0 / self.numTeams
		return weeklyAvg






