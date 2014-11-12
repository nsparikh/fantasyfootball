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

		pos = Position.objects.get(id=3)
		year = 2014
		weight = 'uniform'

		for i in range(1, 16):
			numNeighbors = i*10
			for week_number in range(2, 10):
				(xArray, yArray) = self.getDataForModel(pos, year, week_number)
				knn = self.buildModel(xArray, yArray, numNeighbors, weight)
				totalError = 0
				espnError = 0
				for p in Player.objects.filter(position=pos).order_by('id'):
					try:
						gd = GameData.objects.get(player=p, 
							matchup__year=year, matchup__week_number=week_number)
						projection = self.playerProjection(knn, p, year, week_number)
						totalError += abs(gd.data.points - projection)
						espnError += abs(gd.data.points - gd.espn_projection)
					except: # No matching game data
						pass
				outstring = (pos.name+','+str(year)+','+str(week_number)+','+str(numNeighbors)+
					','+weight+','+str(totalError)+','+str(espnError)+'\n')
				print outstring
				outfile.write(outstring)
	


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

		# Compute avg points earned across all players of this position
		position = player.position
		if (position.id, week_number) not in self.avgPtsEarnedDict:
			self.avgPtsEarnedDict[(position.id, week_number)] = self.computeWeeklyAveragePointsEarned(
				position, year, week_number)

		# Compute weekly avg points earned by this player and difference between it and league avg
		ptsEarned = self.computeAveragePointsEarned(player, year, week_number)
		if ptsEarned is None: return None
		diffPtsEarned = ptsEarned - self.avgPtsEarnedDict[(position.id, week_number)]

		# Compute avg pts allowed to players of this position across all defenses
		opponent = (matchup.home_team if playerTeam.id==matchup.away_team.id else matchup.away_team)
		if (opponent.id, week_number) not in self.avgDefPtsAllowedDict:
			self.avgDefPtsAllowedDict[(opponent.id, week_number)] = self.computeWeeklyAveragePointsAllowed(
				position, year, week_number)

		# Compute points allowed to players of this position by opponent's defense and 
		# difference between it and league average
		ptsAllowed = self.computeAveragePointsAllowed(opponent, player.position, year, week_number)
		diffPtsAllowed = ptsAllowed - self.avgDefPtsAllowedDict[(opponent.id, week_number)]

		# Make the prediction!
		vect = np.array([ptsEarned, diffPtsEarned, ptsAllowed, diffPtsAllowed])
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
		print 'GETTING DATA for', position.abbr, 'to week', cur_week_number, year

		# Dictionaries of data that will be used in feature vectors
		dataDict = {} # Maps (player ID, week) to arrays of features [(1), (2), (3), (4)]
		labelsDict = {} # Maps (player ID, week) to actual fantasy points earned that week

		# Get data from each week up to the given week number
		for week_number in range(2, cur_week_number+1):
			# Get matchups for this week
			matchups = Matchup.objects.filter(year=year, week_number=week_number)

			# Go through each team and compute each defense's points allowed
			defDict = {} # Maps team ID to feature (4)
			for team in Team.objects.exclude(id=33):
				defPtsAllowed = self.computeAveragePointsAllowed(team, position, year, week_number)
				defDict[team.id] = defPtsAllowed

			# Go through each player of this position and compute points earned
			for player in Player.objects.filter(position=position):
				# Get player's team in this year
				playerTeam = YearData.objects.get(year=year, player=player).team
				if playerTeam.id == 33: continue # Don't need FA data

				# Get player's matchup for this week; if bye week, continue
				curMatchup = matchups.get(Q(home_team=playerTeam) | Q(away_team=playerTeam))
				if curMatchup.bye: continue

				# Compute total fantasy points earned by this player so far
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
				if (opponent.id, week_number) not in self.avgDefPtsAllowedDict:
					self.avgDefPtsAllowedDict[(opponent.id, week_number)] = self.computeLeagueAveragePointsAllowed(
						position, year, week_number)

				# Assign the values in the dictionary
				dataDict[(player.id, week_number)] = [
					ptsEarned, 
					ptsEarned - self.avgPtsEarnedDict[(position.id, week_number)], 
					defPtsAllowed, 
					defPtsAllowed - self.avgDefPtsAllowedDict[(opponent.id, week_number)]
				]

				# Add fantasy points to labels dict
				try: 
					curWeekPts = GameData.objects.get(player=player, 
						matchup__year=year, matchup__week_number=week_number).data.points
				except: curWeekPts = None
				labelsDict[(player.id, week_number)] = curWeekPts if curWeekPts is not None else 0

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


	# Computes the player's weekly average fantasy points earned up to week_number
	# (does not include data from week_number)
	def computeAveragePointsEarned(self, player, year, week_number):
		numWeeksPlayed = len(Matchup.objects.filter(Q(home_team=player.team) | 
			Q(away_team=player.team), year=year, week_number__lt=week_number, bye=False))
		ptsEarned = GameData.objects.filter(player=player, matchup__year=year, 
			matchup__week_number__lt=week_number).aggregate(
			Sum('data__points'))['data__points__sum']
		if ptsEarned is not None:# and ptsEarned > 0:
			ptsEarned /= (numWeeksPlayed*1.0)
		return ptsEarned

	# Computes the league weekly average points earned across players of position
	def computeLeagueAveragePointsEarned(self, position, year, week_number):
		sumPlayerAverages = 0
		numPlayers = 0
		for p in Player.objects.filter(position=position):
			weeklyAvgPtsEarned = GameData.objects.filter(player=p, matchup__year=year,
				matchup__week_number__lt=week_number).exclude(data__id=1).aggregate(
				Avg('data__points'))['data__points__avg']
			if weeklyAvgPtsEarned is not None:# and weeklyAvgPtsEarned > 0:
				sumPlayerAverages += weeklyAvgPtsEarned
				numPlayers += 1
		weeklyAvg = sumPlayerAverages*1.0 / numPlayers
		return weeklyAvg

	# Compute weekly average fantasy points allowed on team's defense by players of position
	def computeAveragePointsAllowed(self, team, position, year, week_number):
		numWeeksPlayed = len(Matchup.objects.filter(Q(home_team=team) | 
			Q(away_team=team), year=year, week_number__lt=week_number, bye=False))
		defPtsAllowed = GameData.objects.filter(Q(matchup__home_team=team) | 
			Q(matchup__away_team=team), player__position=position,
			matchup__year=year, matchup__week_number__lt=week_number).exclude(
			player__team=team).aggregate(
			Sum('data__points'))['data__points__sum'] / (numWeeksPlayed*1.0)
		return defPtsAllowed

	# Computes league weekly average points allowed across all defenses to players of position
	def computeLeagueAveragePointsAllowed(self, position, year, week_number):
		sumAverages = 0
		for team in Team.objects.exclude(id=33):
			numWeeksPlayed = len(Matchup.objects.filter(Q(home_team=team) | 
				Q(away_team=team), year=year, week_number__lt=week_number, bye=False))
			weeklyAvgPtsAllowed = (GameData.objects.filter(Q(matchup__home_team=team) | 
				Q(matchup__away_team=team), player__position=position,
				matchup__year=year, matchup__week_number__lt=week_number).exclude(
				player__team=team).aggregate(Sum('data__points'))['data__points__sum'] / 
				(numWeeksPlayed*1.0))
			sumAverages += weeklyAvgPtsAllowed
		weeklyAvg = sumAverages*1.0 / self.numTeams
		return weeklyAvg






