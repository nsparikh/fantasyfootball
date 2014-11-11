from django.db.models import Count, Avg, Sum, Q

from game.models import Player, Position, Team, Matchup
from data.models import YearData, GameData, DataPoint

from django.core.management.base import NoArgsCommand, make_option

import numpy as np
from sklearn import neighbors

class Command(NoArgsCommand):

	help = ''
	numTeams = 32
	avgPtsEarnedDict = {} # Maps (position ID, week number) => avg pts earned
	avgDefPtsAllowedDict = {} # Maps (team ID, week number) => avg pts allowed

	option_list = NoArgsCommand.option_list + (
		make_option('--verbose', action='store_true'),
	)

	def handle_noargs(self, **options):
		outfile = open('results.txt', 'a')

		pos = Position.objects.get(id=1)
		year = 2014
		week_number = 6
		numNeighbors = 100
		weight = 'uniform'

		outfile.write('Position: ' + pos.name + '\n')
		outfile.write('Year: ' + str(year) + '\n')
		outfile.write('Week: ' + str(week_number) + '\n')
		outfile.write('# Neighbors: ' + str(numNeighbors) + '\n')
		outfile.write('Weighting: ' + weight + '\n')  

		(xArray, yArray) = self.getDataForModel(pos, year, week_number-1)
		knn = self.buildModel(xArray, yArray, numNeighbors, weight)

		totalError = 0
		espnError = 0
		for p in Player.objects.filter(position=pos).order_by('id'):
			try:
				gd = GameData.objects.get(player=p, 
					matchup__year=year, matchup__week_number=week_number)
				projection = self.playerProjection(knn, p, year, week_number)
				print p.id, p.name, projection, gd.espn_projection, gd.data.points
				totalError += abs(gd.data.points - projection)
				espnError += abs(gd.data.points - gd.espn_projection)
			except:
				print p.id, p.name, 'no game data'

		outfile.write('Computed error: ' + str(totalError) + '\n')
		outfile.write('ESPN error: ' + str(espnError) + '\n')
		outfile.write('\n')

	
	# Computes the projection of the given player in the year and week
	#	using the model provided
	def playerProjection(self, model, player, year, week_number):
		# Get the player's team in the given year
		playerTeam = YearData.objects.get(year=year, player=player).team
		if playerTeam.id == 33: return None

		# Get the week's matchup; if it's a bye week then no projection
		matchup = Matchup.objects.get(Q(home_team=playerTeam) | Q(away_team=playerTeam), 
			year=year, week_number=week_number)
		if matchup.bye: return None

		# Compute feature (1) -- avg points earned across all players of this position
		position = player.position
		if (position.id, week_number) not in self.avgPtsEarnedDict:
			self.avgPtsEarnedDict[(position.id, week_number)] = self.computeAveragePointsEarned(
				position, year, week_number)

		# Compute feature (2) -- difference in points earned by this player and (1)
		ptsEarned = GameData.objects.filter(player=player, matchup__year=year, 
			matchup__week_number__lt=week_number).aggregate(Sum('data__points'))['data__points__sum']
		if ptsEarned is None: return None
		diffPtsEarned = ptsEarned - self.avgPtsEarnedDict[(position.id, week_number)]

		# Compute feature (3) -- avg pts allowed to players of this position across all defenses
		opponent = (matchup.home_team if playerTeam.id==matchup.away_team.id else matchup.away_team)
		if (opponent.id, week_number) not in self.avgDefPtsAllowedDict:
			self.avgDefPtsAllowedDict[(opponent.id, week_number)] = self.computeAveragePointsAllowed(
				position, year, week_number)

		# Compute feature (4) -- diff in points allowed to players of this position 
		#	by opponent's defense and (3)
		defPtsAllowed = GameData.objects.filter(Q(matchup__home_team=opponent) | 
			Q(matchup__away_team=opponent), player__position=position,
			matchup__year=year, matchup__week_number__lt=week_number).exclude(
			player__team=opponent).aggregate(Sum('data__points'))['data__points__sum']
		diffPtsAllowed = defPtsAllowed - self.avgDefPtsAllowedDict[(opponent.id, week_number)]

		# Make the prediction!
		vect = np.array([
			self.avgPtsEarnedDict[(position.id, week_number)],
			diffPtsEarned,
			self.avgDefPtsAllowedDict[(opponent.id, week_number)],
			diffPtsAllowed
		])
		return model.predict(vect)

	# Gets the data for building the prediction model
	# Returns a tuple of (x, y) -- two numpy arrays corresponding to the feature
	#	vectors and "labels" or actual fantasy points earned for players of 
	#	this position in the given year and through the given week
	# Uses the given year's data points through the given week as training data
	# Computes feature vectors for each week through week_number, using cumulative
	#	data from week 1 through that week
	# Four features for each player in each week through week_number:
	# 1) average total fantasy points earned across all players of this position
	# 2) difference in total fantasy points earned so far by this player and (1)
	# 3) average total fantasy points allowed by players of this position across all defenses
	# 4) diff in total fantasy points allowed by players of this position and (3)
	def getDataForModel(self, position, year, week_number):
		print 'GETTING DATA for', position.name, 'through week', week_number, year

		# Dictionaries of data that will be used in feature vectors
		dataDict = {} # Maps (player ID, week) to arrays of features [(1), (2), (3), (4)]
		labelsDict = {} # Maps (player ID, week) to actual fantasy points earned that week

		# Train the model with data from each week through the given week number
		for week in range(1, week_number+1):
			# Get matchups for this week
			matchups = Matchup.objects.filter(year=year, week_number=week)

			# Go through each team and compute feature (4)
			defDict = {} # Maps team ID to feature (4)
			for team in Team.objects.exclude(id=33):
				# Compute total fantasy points allowed on team's defense by players of position
				defPtsAllowed = GameData.objects.filter(Q(matchup__home_team=team) | 
					Q(matchup__away_team=team), player__position=position,
					matchup__year=year, matchup__week_number__lt=week).exclude(
					player__team=team).aggregate(Sum('data__points'))['data__points__sum']
				defDict[team.id] = defPtsAllowed

			# Go through each player of this position and compute feature (2)
			for player in Player.objects.filter(position=position):
				# Get player's team in this year
				playerTeam = YearData.objects.get(year=year, player=player).team
				if playerTeam.id == 33: continue # Don't need FA data

				# Get player's matchup for this week; if bye week, continue
				curMatchup = matchups.get(Q(home_team=playerTeam) | Q(away_team=playerTeam))
				if curMatchup.bye: continue

				# Compute total fantasy points earned by this player so far
				ptsEarned = GameData.objects.filter(player=player, matchup__year=year, 
					matchup__week_number__lt=week).aggregate(
					Sum('data__points'))['data__points__sum']
				if ptsEarned is not None and ptsEarned > 0:
					# Get feature (4) from already comptued data
					opponent = (curMatchup.home_team if playerTeam.id==curMatchup.away_team.id 
						else curMatchup.away_team)
					defPtsAllowed = defDict[opponent.id]

					# Compute features (1) and (3) if not already computed
					if (position.id, week) not in self.avgPtsEarnedDict:
						self.avgPtsEarnedDict[(position.id, week)] = self.computeAveragePointsEarned(position, year, week)
					if (opponent.id, week) not in self.avgDefPtsAllowedDict:
						self.avgDefPtsAllowedDict[(opponent.id, week)] = self.computeAveragePointsAllowed(position, year, week)

					# Assign the values in the dictionary
					dataDict[(player.id, week)] = [
						self.avgPtsEarnedDict[(position.id, week)], 
						ptsEarned - self.avgPtsEarnedDict[(position.id, week)], 
						self.avgDefPtsAllowedDict[(opponent.id, week)], 
						defPtsAllowed - self.avgDefPtsAllowedDict[(opponent.id, week)]
					]

					# Add fantasy points to labels dict
					curWeekPts = GameData.objects.get(player=player, 
						matchup__year=year, matchup__week_number=week).data.points
					labelsDict[(player.id, week)] = curWeekPts if curWeekPts is not None else 0

		# Get numpy arrays of data and "labels" (fantasy points)
		xArray = self.dictToNumpy(dataDict, 4)
		yArray = self.dictToNumpy(labelsDict, 1)
		return (xArray, yArray)

	# Builds and fits the model with the provided parameters
	# weights is either 'uniform' or 'distance'
	def buildModel(self, xArray, yArray, numNeighbors, weights):
		print 'BUILDING MODEL with parameters:', numNeighbors, 'neighbors,', weights, 'weighting'
		knn = neighbors.KNeighborsRegressor(n_neighbors=numNeighbors, weights=weights)
		knn.fit(xArray, yArray)
		return knn

	# Convert data from inputDict to numpy array
	# yDim is the number of columns in the array
	# Returns an array ordered by key
	def dictToNumpy(self, inputDict, yDim):
		npArray = np.empty([ len(inputDict), yDim ])
		i = 0
		keyList = inputDict.keys()
		keyList.sort()
		for key in keyList:
			npArray[i] = inputDict[key]
			i += 1
		return npArray



	# Computes the average total fantasy points earned across players of the given
	#	position through the given week_number of the given year
	def computeAveragePointsEarned(self, position, year, week_number):
		totalPtsEarned = 0
		numPlayers = 0
		for p in Player.objects.filter(position=position):
			curPtsEarned = GameData.objects.filter(player=p, matchup__year=year, 
				matchup__week_number__lt=week_number).aggregate(
				Sum('data__points'))['data__points__sum']
			if curPtsEarned is not None and curPtsEarned > 0:
				totalPtsEarned += curPtsEarned
				numPlayers += 1
		avgPtsEarned = totalPtsEarned*1.0 / numPlayers
		return avgPtsEarned

	# Computes the average total fantasy points allowed to players of the given
	#	position across all defenses
	def computeAveragePointsAllowed(self, position, year, week_number):
		totalPtsAllowed = 0
		for team in Team.objects.exclude(id=33):
			defPtsAllowed = GameData.objects.filter(Q(matchup__home_team=team) | 
				Q(matchup__away_team=team), player__position=position,
				matchup__year=year, matchup__week_number__lt=week_number).exclude(
				player__team=team).aggregate(Sum('data__points'))['data__points__sum']
			totalPtsAllowed += defPtsAllowed
		avgDefPtsAllowed = totalPtsAllowed*1.0 / self.numTeams
		return avgDefPtsAllowed



