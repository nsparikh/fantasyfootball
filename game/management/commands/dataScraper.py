from django.db.models import Count, Avg, Sum, Q

from game.models import Player, Position, Team, Matchup
from data.models import YearData, GameData, DataPoint

from django.core.management.base import NoArgsCommand, make_option

import datetime
import time
import urllib2
from random import randint

class Command(NoArgsCommand):

	help = 'Update Matchups, weekly/yearly data'
	suffixes = ['Jr.', 'Sr.', 'III']
	weekDataPrefix = 'http://games.espn.go.com/ffl/leaders?&scoringPeriodId='
	yearDataPrefix = 'http://games.espn.go.com/ffl/leaders?&seasonTotals=true&seasonId='
	teamSchedulePrefix = 'http://espn.go.com/nfl/team/schedule/_/name/'
	teamDepthPrefix = 'http://espn.go.com/nfl/team/depth/_/name/'
	projectionPrefix = 'http://games.espn.go.com/ffl/tools/projections?&scoringPeriodId='
	playerProfilePrefix = 'http://espn.go.com/nfl/players/profile?playerId='
	playerStatsPrefix = 'http://espn.go.com/nfl/player/stats/_/id/'
	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


	option_list = NoArgsCommand.option_list + (
		make_option('--verbose', action='store_true'),
	)

	def handle_noargs(self, **options):
		for player in Player.objects.all().order_by('id'):
			print player.id, player.name, self.updatePlayerEspnProjection(player, 2014, 12, True)

		
	# Creates empty GameData objects for the player in the given week and year
	# Returns the object but DOES NOT SAVE TO DATABASE
	def getEmptyGameData(self, player, year, week_number):
		# If player is a FA, no need to create one
		if player.team.id == 33: return None

		# Get PK for this week and year
		gdId = int(str(player.id) + str(year)[2:] + str(week_number).zfill(2))

		# First see if already exists
		try:
			gd = GameData.objects.get(id=gdId)
			return None
		except: # This means it doesn't already exist, so create an "empty" one
			matchup = Matchup.objects.get(Q(home_team=player.team) | Q(away_team=player.team), 
				year=year, week_number=week_number)
			nullDp = DataPoint.objects.get(id=1)
			gd = GameData(id=gdId, player=player, matchup=matchup, projection=None, 
				espn_projection=None, yahoo_projection=None, cbs_projection=None,
				performance_score=None, data=nullDp)
			return gd

	# Scrapes the data for the player in the given week and year
	# 	If week_number is 0, then scrapes the data for the whole season
	# Creates a new DataPoint object or updates it and saves it
	# Returns the DataPoint object
	def getPlayerDataPoint(self, player, year, week_number, current_week_number):
		# Get the player's last name
		nameArr = player.name.split(' ')
		lastName = nameArr[1]
		if len(nameArr) > 2 and nameArr[2] not in self.suffixes: 
			lastName = nameArr[2]

		(rowEndKey, rStart, hasSpan) = ('</td>', 6, False)
		if week_number == current_week_number: (rowEndKey, hasSpan) = ('</span>', True)

		if week_number > 0:
			url = (self.weekDataPrefix + str(week_number) + 
				'&seasonId=' + str(year) + '&search=' + lastName)
			if player.position.id == 5:
				url = (self.weekDataPrefix + str(week_number) + '&seasonId=' + 
					str(year) + '&slotCategoryId=16&proTeamId=' + str(player.team.espn_id))
		else: # Get the season data
			url = self.yearDataPrefix + str(year) + '&search=' + lastName
			if player.position.id == 5:
				url = (self.yearDataPrefix + str(year) + '&slotCategoryId=16&proTeamId=' + 
					str(player.team.espn_id))
			rStart = 3

		# Read in the page data
		data = urllib2.urlopen(url).read()
		try:
			data = data[data.index('<table class="playerTableTable') : ]
			data = data[ : data.index('</table>')]
		except: 
			return None

		# Multiple players could have the same last name, so we need to find the right one
		table = data.split('<tr id="plyr') 
		for i in range(1, len(table)):
			row = table[i].split('<td')
			scrapedEspnId = int(row[1][row[1].index('id="playername_')+15 : 
				row[1].index('" style')])
			#scrapedName = row[1][row[1].index('cache="true">')+13 : row[1].index('</a>')]
			if scrapedEspnId == player.espn_id: #or scrapedName == player.name:
				if 'BYE' in row[3] and player.team.espn_id > 0: return None

				# Get the corresponding DataPoint, or create a new one
				# ID format: pppppyyww
				dpId = int(str(player.id) + str(year)[2:] + str(week_number).zfill(2))
				try: dp = DataPoint.objects.get(id=dpId)
				except: dp = DataPoint(id=dpId)

				# Scrape data!
				fields = [('passC', rStart), ('passA', rStart), ('passYds', rStart+1), 
					('passTDs', rStart+2), ('passInt', rStart+3),
					('rush', rStart+5), ('rushYds', rStart+6), ('rushTDs', rStart+7),
					('rec', rStart+9), ('recYds', rStart+10), ('recTDs', rStart+11), ('recTar', rStart+12),
					('misc2pc', rStart+14), ('miscFuml', rStart+15), ('miscTDs', rStart+16), 
					('points', rStart+18)]
				for fTuple in fields:
					r = fTuple[1]
					rowString = row[r]
					if hasSpan: rowString = rowString.replace('>', '', 1)

					if fTuple[0]=='passC':
						if hasSpan: amt = rowString[rowString.index('_1">') + 4 : rowString.index(rowEndKey)]
						else: amt = rowString[rowString.index('>') + 1 : rowString.index('/')]
					elif fTuple[0]=='passA':
						if hasSpan: amt = rowString[rowString.index('_0">') + 4 : rowString.index('</span></td>')]
						else: amt = rowString[rowString.index('/') + 1 : rowString.index(rowEndKey)]
					else:
						amt = rowString[rowString.index('>') + 1 : rowString.index(rowEndKey)]

					amt = None if (amt=='--') else int(amt)
					setattr(dp, fTuple[0], amt)

				if self.isAllNullDataPoint(dp): return None

				dp.save()
				return dp
		return None

	# Gets the data for the player in the given week and year
	# Updates or creates the corresponding GameData object 
	def updatePlayerGameData(self, player, year, week_number, current_week_number):

		# If this player is a FA, there's no data
		if player.team.id == 33: return False

		# Get the GameData object, if there is one
		try:
			gd = GameData.objects.get(player=player, matchup__year=year, 
				matchup__week_number=week_number)

			# If it's a bye week or the game is in the future or if it's already done, 
			# don't try to update
			if (gd.matchup.bye or gd.data.points > 0 or
				gd.matchup.date >= datetime.date(datetime.now())):
				return False
		except: 
			# If there is no GameData object, create one
			gdId = int(str(player.id) + str(year)[2:] + str(week_number).zfill(2))
			gd = GameData(id=gdId, player=player, projection=None, espn_projection=None, 
				yahoo_projection=None, cbs_projection=None, performance_score=None)
			matchup = Matchup.objects.get(Q(home_team=player.team) | Q(away_team=player.team),
				year=year, week_number=week_number)
			gd.matchup = matchup

		# Get the DataPoint object and update the GameData object
		dp = self.getPlayerDataPoint(player, year, week_number, current_week_number)
		gd.data = DataPoint.objects.get(id=1) if dp is None else dp

		gd.save()
		return True

	# Gets the data for the player in the given year
	# Updates the corresponding YearData object
	def scrapePlayerYearData(self, player, year):
		# Get the YearData object (there should be one for every player)
		try: yd = YearData.objects.get(player=player, year=year)
		except: return False

		# Get the data and update the YearData object
		dp = self.getPlayerDataPoint(player, year, 0, -1)
		if dp is None:
			yd.data = DataPoint.objects.get(id=1)
			return False

		yd.data = dp
		yd.save()
		return True

	# Computes the player's year data from the stored game data
	def updatePlayerYearData(self, player, year):
		# Get the YearData object (there should be one for every player)
		try: yd = YearData.objects.get(player=player, year=year)
		except: return False

		# Add all of the data points together
		dp = DataPoint.objects.get(id=1)
		for gd in GameData.objects.filter(player=player, matchup__year=year):
			dp = self.addDataPoints(dp, gd.data)
		
		# Check if resulting point is all null or all zero
		if self.isAllNullDataPoint(dp): yd.data = DataPoint.objects.get(id=1)
		elif self.isAllZeroDataPoint(dp): yd.data = DataPoint.objects.get(id=100)
		else: 
			dp.id = int(str(player.id) + str(year)[2:] + '00')
			dp.save()
			yd.data = dp
		yd.save()
		return True

	# Helper method to tell whether the given data point has all null fields
	def isAllNullDataPoint(self, dp):
		dpFields = [field for field in dp._meta.get_all_field_names() if (
			'data' not in field and field != 'id')]
		for field in dpFields:
			if getattr(dp, field) is not None: return False
		return True

	# Helper method to tell whether the given data point has all zero fields
	def isAllZeroDataPoint(self, dp):
		dpFields = [field for field in dp._meta.get_all_field_names() if (
			'data' not in field and field != 'id')]
		for field in dpFields:
			if getattr(dp, field) is not None and getattr(dp, field) > 0: return False
		return True

	# Helper method to "add" two data points
	# Returns a data point with ID=100 -- this needs to be updated!
	# Does not check if all null or all zero
	def addDataPoints(self, dp1, dp2):
		dp = DataPoint.objects.get(id=100)
		dpFields = [field for field in dp._meta.get_all_field_names() if (
			'data' not in field and field != 'id')]
		for field in dpFields:
			if getattr(dp1, field) is None and getattr(dp2, field) is None:
				setattr(dp, field, None)
			elif getattr(dp1, field) is None:
				setattr(dp, field, getattr(dp2, field))
			elif getattr(dp2, field) is None:
				setattr(dp, field, getattr(dp1, field))
			else:
				setattr(dp, field, getattr(dp1, field) + getattr(dp2, field))
		return dp


	# Scrapes the ESPN projection for the player in the given week and year
	# Updates the corresponding GameData object
	# Returns True if it is updated successfully
	def updatePlayerEspnProjection(self, player, year, week_number, create_gamedata=False):
		# If this player is a FA, there's no data
		if player.team.id == 33: return None

		# Get the GameData object, if there is one
		try:
			gd = GameData.objects.get(player=player, matchup__year=year, 
				matchup__week_number=week_number)

			# If it's a bye week or if it's already done, 
			# don't try to update
			if (gd.matchup.bye or gd.espn_projection is not None):
				return None
		except:
			if create_gamedata:
				gd = self.getEmptyGameData(player, year, week_number)
			else: return None

		# Get the player's last name
		nameArr = player.name.split(' ')
		lastName = nameArr[1]
		if len(nameArr) > 2 and nameArr[2] not in self.suffixes: 
			lastName = nameArr[2]

		url = (self.projectionPrefix + str(week_number) + 
			'&seasonId=' + str(year) + '&search=' + lastName)
		if player.position.id == 5:
			url = (self.projectionPrefix + str(week_number) + '&seasonId=' + 
				str(year) + '&slotCategoryId=16&proTeamId=' + str(player.team.espn_id))

		# Read in the page data
		data = urllib2.urlopen(url).read()
		try:
			data = data[data.index('<table class="playerTableTable') : ]
			data = data[ : data.index('</table>')]
		except: 
			return None

		# Multiple players could have the same last name, so we need to find the right one
		table = data.split('<tr id="plyr') 
		for i in range(1, len(table)):
			row = table[i].split('<td')
			scrapedEspnId = int(row[1][row[1].index('id="playername_')+15 : 
				row[1].index('" style')])
			if scrapedEspnId == player.espn_id: # Just need the projection column
				if 'BYE' in row[2]: return None # Don't need to do anything if FA or Bye week

				r = 14
				projection = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				projection = None if (projection=='--') else int(projection)

				# Find the corresponding GameData object and update it
				if projection is not None:
					gd.espn_projection = projection
					gd.save()
					return projection
		return None

	# Gets and saves the matchups for the team in the given year
	def getTeamMatchups(self, team, year):
		# Read the data from the web page
		data = urllib2.urlopen(self.teamSchedulePrefix + team.abbr + '/year/' + str(year)).read()
		data = data[data.index(str(year) + ' Regular Season Schedule') : data.index(str(year) + ' Preseason Schedule')].split('<tr')[2:]

		# Go through each row in the table
		for i in range(len(data)-1):
			row = data[i]
			if '"colhead"' in row or '"stathead"' in row: continue

			row = row.split('<td')
			week_number = int(row[1][1 : row[1].index('</td>')])
			print 'Week number', week_number

			# If the matchup already exists, no need to get all the data so move on to the next week
			try:
				Matchup.objects.get(Q(home_team=team) | Q(away_team=team), 
					year=year, week_number=week_number)
				print 'already have data'
				continue
			except:
				pass

			# Initialize variables as per bye week
			date = None
			home_team = team
			away_team = None
			win = None
			espn_game_id = None
			bye = True
			win = None
			home_team_points = None
			away_team_points = None
			pk = int(str(team.id) + '00' + str(year)[2:] + str(week_number).zfill(2))

			# If it's not a bye week, get the necessary info
			if 'BYE WEEK' not in row[2]:
				bye = False
				date = str(year) + '-'
				month = self.months.index(row[2][6 : 9]) + 1
				day = row[2][10 : row[2].index('</td>')]
				date += str(month) + '-' + str(day)
				date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

				opp = row[3]
				opp = opp[opp.index('name/')+5 : ]
				opp = opp[ : opp.index('/')]
				if 'vs' in row[3]:
					home_team = team
					away_team = Team.objects.get(abbr__iexact=opp)
				else:
					home_team = Team.objects.get(abbr__iexact=opp)
					away_team = team

				win = None
				curTeamWin = False
				if 'game-status win' in row[4]: curTeamWin = True
				if curTeamWin and home_team == team: win = True
				elif not curTeamWin and home_team != team: win = True
				else: win = False

				result = row[4][row[4].index('gameId=') : ]
				espn_game_id = int(result[result.index('=')+1 : result.index('"')])
				pointsFor = int(result[result.index('>')+1 : result.index('-')].replace('OT', ''))
				pointsAgainst = int(result[result.index('-')+1 : result.index('</a>')].replace('OT', ''))
				if win:
					home_team_points = pointsFor
					away_team_points = pointsAgainst
				else:
					home_team_points = pointsAgainst
					away_team_points = pointsFor

				t1 = min(home_team, away_team)
				t2 = max(home_team, away_team)
				pk = int(str(t1.id) + str(t2.id).zfill(2) + str(year)[2:] + str(week_number).zfill(2))

			matchup = Matchup(id=pk, espn_game_id=espn_game_id, year=year, date=date, 
				week_number=week_number, bye=bye, home_team=home_team, away_team=away_team,
				win=win, home_team_points=home_team_points, away_team_points=away_team_points)
			print matchup.id, matchup.espn_game_id, matchup.year, matchup.date, matchup.week_number, matchup.bye, matchup.home_team, matchup.away_team, matchup.win, matchup.home_team_points, matchup.away_team_points
			matchup.save()

	# Scrapes the data for the team in the given week and year
	# Updates the corresponding Matchup object
	# Returns True if the Matchup is updated successfully, False if not
	def updateMatchup(self, team, year, week_number):
		matchup = Matchup.objects.get(Q(home_team=team) | Q(away_team=team), 
			year=year, week_number=week_number)

		 # Don't need to do anything for a bye week, in the future,
		 # or if it has already been updated
		if (matchup.bye or matchup.date >= datetime.datetime.now().date() or 
			matchup.home_team_points is not None): 
			return False

		# Read in the page data
		abbr = 'jax' if team.abbr.lower()=='jac' else team.abbr.lower()
		url = self.teamSchedulePrefix + abbr + '/year/' + str(year)
		data = urllib2.urlopen(url).read()

		table = data[data.index(str(year) + ' Regular Season Schedule') : 
			data.index(str(year) + ' Preseason Schedule')].split('<tr')[2:]

		for i in range(len(table)-1):
			row = table[i]
			if '"colhead"' in row or '"stathead"' in row: continue

			row = row.split('<td')
			curWeek = int(row[1][1 : row[1].index('</td>')])

			if curWeek == week_number: # Get espn_game_id, win, score
				win = None
				curTeamWin = False
				if 'game-status win' in row[4]: curTeamWin = True
				if curTeamWin and matchup.home_team.id == team.id: win = True
				elif not curTeamWin and matchup.home_team.id != team.id: win = True
				else: win = False

				result = row[4][row[4].index('gameId=') : ]
				espn_game_id = int(result[result.index('=')+1 : result.index('"')])
				pointsFor = int(result[result.index('>')+1 : result.index('-')])
				pointsAgainst = int((result[result.index('-')+1 : result.index('</a>')]).replace('OT', ''))
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

	# Assigns the appropriate matchup to the player's GameData object
	def assignMatchup(self, player, year, week_number):
		ydId = int(str(player.id) + str(year)[2:])
		yd = YearData.objects.get(id=ydId)
		if yd.team is None or yd.team.id == 33: return False

		gdId = int(str(player.id) + str(year)[2:] + str(week_number).zfill(2))
		try: 
			gd = GameData.objects.get(id=gdId)
			matchup = Matchup.objects.get(Q(home_team=yd.team) | Q(away_team=yd.team), 
				year=year, week_number=week_number)
			gd.matchup = matchup
			gd.save()
			return True
		except: 
			return False



	# Scrapes the depth positions of players on the team
	# Updates the Player objects on that team
	def updateDepthPositions(self, team):
		if team.id == 33: return False

		# Clear depth position of all players for this team before updating
		for p in Player.objects.filter(team=team, depth_position__isnull=False):
			if p.position.id < 5: # Don't need to do D/ST or K
				p.depth_position = None
				p.save()

		# Read in the data and get the chunk we want
		abbr = team.abbr.lower() if team.name != 'Jacksonville Jaguars' else 'jax'
		data = urllib2.urlopen(self.teamDepthPrefix + abbr + '/' + 
			team.name.lower().replace(' ', '-')).read()
		data = data[data.index('<tr class="oddrow">') : ]
		data = data[ : data.index('</table>')]

		table = data.split('<tr')
		for i in range(1, len(table)):
			row = table[i]
			cells = row.split('<td>')[1:]
			pos = cells[0][ : cells[0].index('</td>')]

			if pos in ['QB', 'RB', 'WR', 'TE']:
				for depth_pos in range(1, len(cells)):
					cell = cells[depth_pos]
					if '<a href' in cell: # There is a player here
						cell = cell[cell.index('_/id/')+5 : ]
						playerEspnId = int(cell[ : cell.index('/')])
						try:
							p = Player.objects.get(espn_id=playerEspnId)
							p.depth_position = depth_pos
							p.save()
						except:
							print 'error on', playerEspnId

		return True

	# Update's the given player's team in the given year
	def updatePlayerTeam(self, player, year, current_year):
		if player.position.id == 5: return False # D/ST aren't going to change teams
		
		yd = YearData.objects.get(player=player, year=year)

		# Read in the page data and get the chunk with the info we need
		data = urllib2.urlopen(self.playerStatsPrefix + str(player.espn_id)).read()
		try:
			data = data[data.index('<tr class="stathead"') : ]
		except: # Player has no stats
			yd.team = None
			yd.save()
			return None

		data = data[ : data.index('</table>')]
		rows = data.split('<tr')[1:]

		# Go though each row in the table of stats
		for row in rows:
			if 'colhead' in row or 'stathead' in row or 'total' in row: continue
			rowYearTd = row.split('<td>')[1]
			rowYear = int(rowYearTd[ : rowYearTd.index('</td>')])
			if rowYear == year:
				# Get the team for this year
				rowTeamTd = row.split('<td>')[2]
				rowTeamTd = rowTeamTd[rowTeamTd.index('_/name/')+7 : rowTeamTd.index('</a>')]
				teamAbbr = rowTeamTd[ : rowTeamTd.index('/')]
				team = Team.objects.get(abbr__iexact=teamAbbr)
				yd.team = team
				yd.save()

				# If current year, update the Player object
				if year == current_year:
					player.team = team
					player.save()
				return team

		# This means the player didn't have any stats from the given year
		yd.team = Team.objects.get(id=33)
		return None

	# Scrapes the player info and creates the new player with the given ESPN ID
	def createNewPlayer(self, espn_id):

		# Read in the page data and get the chunk with the info we need
		data = urllib2.urlopen(self.playerProfilePrefix + str(espn_id)).read()
		if '<div class="team-logo"></div>' in data:
			data = data[data.index('<div class="team-logo"></div>') : ]
		else:
			data = data[data.index('<div class="player-bio">') : ]

		data = data[ : data.index('<div class="player-select-header">')]

		# Get the player's name
		name = data[data.index('<h1>')+4 : data.index('</h1>')]
		data = data[data.index('<div class="line-divider"></div>') : ]

		# Get the player's number and position
		numPosText = '<li class="first">#'
		numPosCode = data[data.index(numPosText)+len(numPosText) : ]
		numPosCode = numPosCode[ : numPosCode.index('</li>')]
		number = int(numPosCode.split(' ')[0])
		posAbbr = numPosCode.split(' ')[1]
		position = Position.objects.get(abbr=posAbbr)
		data = data[data.index(numPosText)+len(numPosText) : ]

		# Get the player's height and weight
		hwCode = data[data.index('<li>')+4 : data.index(' lbs</li>')]
		feet = int(hwCode[ : hwCode.index("'")])
		inches = int(hwCode[hwCode.index("'")+2 : hwCode.index('"')])
		height = feet*12 + inches
		weight = int(hwCode[hwCode.index('", ')+3 : ])

		# Get the player's team
		teamCode = data[data.index('_/name/')+7 : data.index('</a>')]
		teamAbbr = teamCode[ : teamCode.index('/')]
		team = Team.objects.get(abbr__iexact=teamAbbr)
		data = data[data.index('<ul class="player-metadata') : ]

		# Get the player's DOB
		dobCode = data[data.index('</span>')+7 : data.index('</li>')]
		month = time.strptime(dobCode[ : 3],'%b').tm_mon
		day = int(dobCode[dobCode.index(' ')+1 : dobCode.index(',')])
		dobCode = dobCode[dobCode.index(', ')+2 : ]
		year = int(dobCode[ : dobCode.index(' ')])
		dob = datetime.date(year, month, day)

		# Generate an ID for the player and create the Player object
		playerId = self.generatePlayerId(position.id)
		player = Player(id=playerId, name=name, espn_id=espn_id, height=height, 
			weight=weight, dob=dob, team=team, position=position, 
			depth_position=None, number=number, status=None)
		player.save()
		print player.fixtureString()

		# TODO: Create a new YearData ?

	# Generates a random 5-digit player ID that starts with the position_id
	# Ensures that it is unique
	def generatePlayerId(self, position_id):
		playerIDs = [ p.id for p in Player.objects.all() ]
		while True:
			randId = (position_id*10000) + randint(0, 9999)
			if randId not in playerIDs: 
				return randId


		




