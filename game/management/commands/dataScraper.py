from django.db.models import Count, Avg, Sum, Q

from game.models import Player, Position, Team, Matchup
from data.models import YearData, GameData, DataPoint

from django.core.management.base import NoArgsCommand, make_option

import time

class Command(NoArgsCommand):

	help = ''
	suffixes = ['Jr.', 'Sr.', 'III']
	weekDataPrefix = 'http://games.espn.go.com/ffl/leaders?&scoringPeriodId='
	yearDataPrefix = 'http://games.espn.go.com/ffl/leaders?&seasonTotals=true&seasonId='
	teamSchedulePrefix = 'http://espn.go.com/nfl/team/schedule/_/name/'
	projectionPrefix = 'http://games.espn.go.com/ffl/tools/projections?&scoringPeriodId='


	option_list = NoArgsCommand.option_list + (
		make_option('--verbose', action='store_true'),
	)

	def handle_noargs(self, **options):
		# Write what we want to do here
		writeDataAndPoints(GameData, 2013)


	# Scrapes the data for the player in the given week and year
	# 	If week_number is 0, then scrapes the data for the whole season
	# Creates a new DataPoint object or updates it and saves it
	# Returns the DataPoint object
	def getPlayerDataPoint(self, player, year, week_number):
		# Get the player's last name
		nameArr = player.name.split(' ')
		lastName = nameArr[1]
		if len(nameArr) > 2 and nameArr[2] not in self.suffixes: 
			lastName = nameArr[2]

		if week_number > 0:
			url = (weekDataPrefix + str(week_number) + 
				'&seasonId=' + str(year) + '&search=' + lastName)
			if player.position.id == 5:
				url = (weekDataPrefix + str(week_number) + '&seasonId=' + 
					str(year) + '&slotCategoryId=16&proTeamId=' + str(player.team.espn_id)
		else: # Get the season data
			url = yearDataPrefix + str(year) + '&search=' + lastName
			if player.position.id == 5:
				url = (yearDataPrefix + str(year) + '&slotCategoryId=16&proTeamId=' + 
					str(player.team.espn_id))

		# Read in the page data
		data = urllib2.urlopen(url).read()

		# Multiple players could have the same last name, so we need to find the right one
		table = data.split('<tr id="plyr') 
		for i in range(1, len(table)):
			row = table[i].split('<td')
			scrapedEspnId = int(row[1][row[1].index('id="playername_')+15 : 
				row[1].index('" style')])
			if scrapedEspnId == player.espn_id:
				if 'BYE' in row[3] and player.team.espn_id > 0: return None

				# Get the corresponding DataPoint, or create a new one
				# ID format: pppppyyww
				dpId = int(str(player.id) + str(year)[2:] + str(week_number).zfill(2))
				dp = DataPoint.objects.get(id=dpId)
				if dp is None: dp = DataPoint(id=dpId)

				# Scrape data!
				r = 6
				if player.team.espn_id == 0: r -= 1 # Will automatically list BYE

				passC = (row[r][(row[r].index('>')+1) : row[r].index('/')])
				dp.passC = None if (passC=='--') else int(passC)

				passA = row[r][(row[r].index('/')+1) : row[r].index('</td>')]
				dp.passA = None if (passA=='--') else int(passA)
				r += 1

				passYds = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				dp.passYds = None if (passYds=='--') else int(passYds)
				r += 1

				passTDs = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				dp.passTDs = None if (passTDs=='--') else int(passTDs)
				r += 1

				passInt = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				dp.passInt = None if (passInt=='--') else int(passInt)
				r += 2

				rush = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				dp.rush = None if (rush=='--') else int(rush)
				r += 1

				rushYds = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				dp.rushYds = None if (rushYds=='--') else int(rushYds)
				r += 1

				rushTDs = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				dp.rushTDs = None if (rushTDs=='--') else int(rushTDs)
				r += 2

				rec = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				dp.rec = None if (rec=='--') else int(rec)
				r += 1

				recYds = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				dp.recYds = None if (recYds=='--') else int(recYds)
				r += 1

				recTDs = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				dp.recTDs = None if (recTDs=='--') else int(recTDs)
				r += 1

				recTar = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				dp.recTar = None if (recTar=='--') else int(recTar)
				r += 2

				misc2pc = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				dp.misc2pc = None if (misc2pc=='--') else int(misc2pc)
				r += 1

				miscFuml = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				dp.miscFuml = None if (miscFuml=='--') else int(miscFuml)
				r += 1

				miscTDs = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				dp.miscTDs = None if (miscTDs=='--') else int(miscTDs)
				r += 2

				points = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				dp.points = None if (points=='--') else int(points)
				
				if isAllNullDataPodp): return None

				dp.save()
				return dp
		return None

	# Gets the data for the player in the given week and year
	# Updates or creates the corresponding GameData object 
	def updatePlayerGameData(self, player, year, week_number):

		# Get the GameData object, if there is one
		gd = GameData.objects.get(player=player.id, matchup__year=year, 
			matchup__week_number=week_number)

		# Get the DataPoint object
		dp = getPlayerGameDataPoint(player, year, week_number)

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
	def isAllNullDataPoint(self, dp):
		dpFields = [field for field in dp._meta.get_all_field_names() if (
			'data' not in field and field != 'id')]
		for field in dpFields:
			if dp.field is not None: return False
		return True

	# Scrapes the ESPN projection for the player in the given week and year
	# Updates the corresponding GameData object
	# Returns True if it is updated successfully
	def updatePlayerEspnProjection(self, player, year, week_number):
		# Get the player's last name
		nameArr = player.name.split(' ')
		lastName = nameArr[1]
		if len(nameArr) > 2 and nameArr[2] not in self.suffixes: 
			lastName = nameArr[2]

		url = (projectionPrefix + str(week_number) + 
			'&seasonId=' + str(year) + '&search=' + lastName)
		if player.position.id == 5:
			url = (projectionPrefix + str(week_number) + '&seasonId=' + 
				str(year) + '&slotCategoryId=16&proTeamId=' + str(player.team.espn_id)

		# Read in the page data
		data = urllib2.urlopen(url).read()

		# Multiple players could have the same last name, so we need to find the right one
		table = data.split('<tr id="plyr') 
		for i in range(1, len(table)):
			row = table[i].split('<td')
			scrapedEspnId = int(row[1][row[1].index('id="playername_')+15 : 
				row[1].index('" style')])
			if scrapedEspnId == player.espn_id: # Just need the projection column
				if 'BYE' in row[3] and player.team.espn_id > 0: return # Don't need to do anything

				r = 14
				projection = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				projection = None if (projection=='--') else int(projection)

				# Find the corresponding GameData object and update it
				if projection is not None:
					gd = GameData.objects.get(player=player, matchup__year=year, 
						matchup__week_number=week_number)
					gd.espn_projection = projection
					gd.save()
					return True
		return False


	# Scrapes the data for the team in the given week and year
	# Updates the corresponding Matchup object
	# Returns True if the Matchup is updated successfully, False if not
	def updateMatchup(self, team, year, week_number):
		matchup = Matchup.objects.get(Q(home_team=team) | Q(away_team=team), 
			year=year, week_number=week_number)

		if matchup.bye: return # Don't need to do anything for a bye week

		# Read in the page data
		url = teamSchedulePrefix + team.abbr.lower() + '/year/' + str(year)
		data = urllib2.urlopen(url).read()

		table = data[data.index(str(year) + ' Regular Season Schedule') : 
			data.index(str(year) + ' Preseason Schedule')].split('<tr')[2:]

		for i in range(len(data)-1):
			row = data[i]
			if '"colhead"' in row or '"stathead"' in row: continue

			row = row.split('<td')
			curWeek = row[1][1 : row[1].index('</td>')]
			if curWeek == week_number: # Get espn_game_id, win, score
				win = None
				curTeamWin = False
				if 'game-status win' in row[4]: curTeamWin = True
				if curTeamWin and matchup.home_team.id == team.id: win = True
				elif not curTeamWin and matchup.home_team.id != team.id: win = True
				else: win = False

				result = row[4][row[4].index('gameId=') : ]
				espn_game_id = result[result.index('=')+1 : result.index('"')]
				pointsFor = result[result.index('>')+1 : result.index('-')]
				pointsAgainst = result[result.index('-')+1 : result.index('</a>')]
				if win:
					home_team_points = pointsFor
					away_team_points = pointsAgainst
				else:
					home_team_points = pointsAgainst
					away_team_points = pointsFor

				matchup.win = win
				matchup.espn_game_id = espn_game_id
				matchup.home_team_points = home_team_points
				matchup.away_team_points = away_team_points

				matchup.save()
				return True # Indicates that the Matchup was successfully updated

			return False
