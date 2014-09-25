from django.db.models import Count, Avg, Sum, Q

from game.models import Player, Position, Team, Matchup
from data.models import YearData, GameData, DataPoint

from django.core.management.base import NoArgsCommand, make_option

class Command(NoArgsCommand):

	help = "asdf"
	numTeams = 32
	suffixes = ['Jr.', 'Sr.', 'III']
	scoringLeadersUrlPrefix = 'http://games.espn.go.com/ffl/leaders?&scoringPeriodId='

	option_list = NoArgsCommand.option_list + (
		make_option('--verbose', action='store_true'),
	)

	def handle_noargs(self, **options):
		for i in range(1, 18):
			print "WEEK", i
			self.computePerformanceScores(2014, i)


	# Computes the performance score of the given player in the year and week 
	# player is a Player object, opponent is a Team object
	# The performance score is computed as follows:
	#	offScore = (total fantasy pts earned this season) - 
	#		(avg fantasy pts earned across all players of this pos and depth_pos)
	#	defScore = (avg fantasy pts earned by all players of 
	#			    this pos and depth_pos across each defense) - 
	#		(total fantasy pts earned by players of this pos and depth_pos against this defense)
	#	score = offScore - defScore
	def performanceScore(self, player, year, week_number, opponent):
		# Total points earned by the player this season
		totalPtsEarned = YearData.objects.get(year=year, player=player.id).data.points
		totalPtsEarned = 0 if totalPtsEarned is None else totalPtsEarned

		# Average points earned across all players of this position and depth_position
		avgPtsEarned = YearData.objects.filter(year=year, player__position=player.position.id, 
			player__depth_position=player.depth_position).aggregate(
			Avg('data__points'))['data__points__avg']

		# Total points allowed on opponent's defense across players of this pos+depth_pos
		defPtsAllowed = GameData.objects.filter(Q(matchup__home_team=opponent.id) | 
			Q(matchup__away_team=opponent.id), player__position=player.position.id, 
			player__depth_position=player.depth_position, matchup__year=year, 
			matchup__week_number__lte=week_number).exclude(
			player__team=opponent.id).aggregate(Sum('data__points'))['data__points__sum']
		defPtsAllowed = 0 if defPtsAllowed is None else defPtsAllowed

		# Average pts allowed on all defenses across players of this pos+depth_pos
		avgPtsAllowed = GameData.objects.filter(player__position=player.position.id, 
			player__depth_position=player.depth_position, matchup__year=year, 
			matchup__week_number__lte=week_number).aggregate(
			Sum('data__points'))['data__points__sum'] / (self.numTeams*1.0)

		# Compute the offensive and defensive scores, overall performance score
		offScore = float(totalPtsEarned - avgPtsEarned)
		defScore = avgPtsAllowed - defPtsAllowed
		score = offScore - defScore
		return score

	# Computes the performance scores for each player in the given year/week
	# Saves to database
	def computePerformanceScores(self, year, week_number):
		players = Player.objects.all().order_by('team', 'name')
		matchups = Matchup.objects.filter(year=year, week_number=week_number)

		# TODO: compute averages for the week here so don't do it every time in performanceScore?
		
		# Calculate and save score for every player
		for player in players:
			yd = YearData.objects.get(player=player, year=year)
			if yd.team.id < 33:
				try:
					matchup = matchups.get(Q(home_team=yd.team) | Q(away_team=yd.team))
					gameData = GameData.objects.get(player=player, matchup=matchup)

					# If it's a bye week, set score as 0
					score = 0
					if matchup and not matchup.bye and not gameData.performance_score: 
						opponent = matchup.home_team if yd.team.id==matchup.away_team.id else matchup.away_team
						score = self.performanceScore(player, year, week_number, opponent)

					# Save the score
					gameData.performance_score = score
					gameData.save()
				except:
					pass

	
	# Scrapes the data for the player in the given week and year
	# Creates a new DataPoint object and saves it
	def createPlayerGameDataPoint(player, year, week_number):
		# Get the player's last name
		nameArr = player.name.split(' ')
		lastName = nameArr[1]
		if len(nameArr) > 2 and nameArr[2] not in self.suffixes: 
			lastName = nameArr[2]

		url = (scoringLeadersUrlPrefix + str(week_number) + 
			'&seasonId=' + str(year) + '&search=' + lastName)
		if player.position.id == 5:
			url = (scoringLeadersUrlPrefix + str(week_number) + '&seasonId=' + 
				str(year) + '&slotCategoryId=16&proTeamId=' + str(player.team.espn_id)

		# Read in the page data
		data = urllib2.urlopen(url).read()
		table = data.split('<tr id="plyr')
		for i in range(1, len(table)):
			row = table[i].split('<td')
			scrapedEspnId = int(row[1][row[1].index('id="playername_')+15 : 
				row[1].index('" style')])
			if scrapedEspnId == player.espn_id:
				if 'BYE' in row[3] and player.team.espn_id > 0: return None

				r = 6
				if player.team.espn_id == 0: # Will automatically list BYE
					r -= 1

					# ID format: pppppyyww
					dpId = int(str(player.id) + str(year)[2:] + str(week_number).zfill(2))
					dp = DataPoint(id=dpId)

					# Scrape data!
					passC = (row[r][(row[r].index('>')+1) : row[r].index('/')])
					dp.passC = None if (passC=='--') else passC

					passA = row[r][(row[r].index('/')+1) : row[r].index('</td>')]
					dp.passA = None if (passA=='--') else passA
					r += 1

					passYds = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
					dp.passYds = None if (passYds=='--') else passYds
					r += 1

					passTDs = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
					dp.passTDs = None if (passTDs=='--') else passTDs
					r += 1

					passInt = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
					dp.passInt = None if (passInt=='--') else passInt
					r += 2

					rush = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
					dp.rush = None if (rush=='--') else rush
					r += 1

					rushYds = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
					dp.rushYds = None if (rushYds=='--') else rushYds
					r += 1

					rushTDs = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
					dp.rushTDs = None if (rushTDs=='--') else rushTDs
					r += 2

					rec = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
					dp.rec = None if (rec=='--') else rec
					r += 1

					recYds = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
					dp.recYds = None if (recYds=='--') else recYds
					r += 1

					recTDs = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
					dp.recTDs = None if (recTDs=='--') else recTDs
					r += 1

					recTar = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
					dp.recTar = None if (recTar=='--') else recTar
					r += 2

					misc2pc = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
					dp.misc2pc = None if (misc2pc=='--') else misc2pc
					r += 1

					miscFuml = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
					dp.miscFuml = None if (miscFuml=='--') else miscFuml
					r += 1

					miscTDs = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
					dp.miscTDs = None if (miscTDs=='--') else miscTDs
					r += 2

					points = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
					dp.points = None if (points=='--') else points
					
					if isAllNullDataPoint(dp): return None

					dp.save()
					return dp
		return None

	# Gets the data for the player in the given week and year
	# Updates or creates the corresponding GameData object 
	def updatePlayerGameData(player, year, week_number):

		# Get the GameData object, if there is one
		gd = GameData.objects.get(player=player.id, matchup__year=year, 
			matchup__week_number=week_number)

		# Get the DataPoint object
		dp = createPlayerGameDataPoint(player, year, week_number)

		# If there is no GameData object, create one
		if gd is None:
			gdId = int(str(player.id) + str(year)[2:] + str(week_number).zfill(2))
			gd = GameData(id=gdId, player=player, projection=None, espn_projection=None, 
				yahoo_projection=None, cbs_projection=None, performance_score=None)
			matchup = Matchup.objects.get(Q(home_team=player.team) | Q(away_team=player.team),
				year=year, week_number=week_number)
			gd.matchup = matchup
			gd.data = 1 if dp is None else dp
		else: # Otherwise just assign the DataPoint
			gd.dp = dp

		gd.save()
	
	# Helper method to tell whether the given data point has all null fields
	def isAllNullDataPoint(dp):
		dpFields = [field for field in dp._meta.get_all_field_names() if (
			'data' not in field and field != 'id')]
		for field in dpFields:
			if dp.field is not None: return False
		return True






