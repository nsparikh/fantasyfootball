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


	option_list = NoArgsCommand.option_list + (
		make_option('--verbose', action='store_true'),
	)

	def handle_noargs(self, **options):
		week_number = 9

		#for t in Team.objects.all().exclude(id=33):
		#	print t.name, self.updateDepthPositions(t)

		#players = Player.objects.all().order_by('id')
		#for i in range(0, len(players)):
			#p = players[i]
			#print i, p.name, self.updatePlayerTeam(p)
			#print i, p.name, self.createEmptyGameData(p, 2014, week_number)
			#print i, p.name, self.updatePlayerEspnProjection(p, 2014, week_number)

		
	# Creates empty GameData objects for the player in the given week and year
	def createEmptyGameData(self, player, year, week_number):
		# If player is a FA, no need to create one
		if player.team.id == 33: return False

		# Get PK for this week and year
		gdId = int(str(player.id) + str(year)[2:] + str(week_number).zfill(2))

		# First see if already exists
		try:
			gd = GameData.objects.get(id=gdId)
			return False
		except: # This means it doesn't already exist, so create an "empty" one
			matchup = Matchup.objects.get(Q(home_team=player.team) | Q(away_team=player.team), 
				year=year, week_number=week_number)
			nullDp = DataPoint.objects.get(id=1)
			gd = GameData(id=gdId, player=player, matchup=matchup, projection=None, 
				espn_projection=None, yahoo_projection=None, cbs_projection=None,
				performance_score=None, data=nullDp)
			gd.save()
			return True

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
	def updatePlayerYearData(self, player, year):
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

	# Helper method to tell whether the given data point has all null fields
	def isAllNullDataPoint(self, dp):
		dpFields = [field for field in dp._meta.get_all_field_names() if (
			'data' not in field and field != 'id')]
		for field in dpFields:
			if getattr(dp, field) is not None: return False
		return True

	# Scrapes the ESPN projection for the player in the given week and year
	# Updates the corresponding GameData object
	# Returns True if it is updated successfully
	def updatePlayerEspnProjection(self, player, year, week_number):
		# If this player is a FA, there's no data
		if player.team.id == 33: return False

		# Get the GameData object, if there is one
		try:
			gd = GameData.objects.get(player=player, matchup__year=year, 
				matchup__week_number=week_number)

			# If it's a bye week or if it's already done, 
			# don't try to update
			if (gd.matchup.bye or gd.espn_projection is not None):
				return False
		except:
			return False

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
			return False

		# Multiple players could have the same last name, so we need to find the right one
		table = data.split('<tr id="plyr') 
		for i in range(1, len(table)):
			row = table[i].split('<td')
			scrapedEspnId = int(row[1][row[1].index('id="playername_')+15 : 
				row[1].index('" style')])
			if scrapedEspnId == player.espn_id: # Just need the projection column
				if 'BYE' in row[2]: return False # Don't need to do anything if FA or Bye week

				r = 14
				projection = row[r][(row[r].index('>')+1) : row[r].index('</td>')]
				projection = None if (projection=='--') else int(projection)

				# Find the corresponding GameData object and update it
				if projection is not None:
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

	def updatePlayerTeam(self, player, year):
		if player.position.id == 5: return False # D/ST aren't going to change teams

		# Read in the page data and get the chunk with the info we need
		data = urllib2.urlopen(self.playerProfilePrefix + str(player.espn_id)).read()
		if '<div class="team-logo"></div>' in data:
			data = data[data.index('<div class="team-logo"></div>') : ]
		else:
			data = data[data.index('<div class="player-bio">') : ]

		data = data[data.index('<div class="line-divider"></div>') : ]
		numPosText = '<li class="first">#'

		try:
			data = data[data.index(numPosText)+len(numPosText) : ]

			# Get the player's team
			teamCode = data[data.index('_/name/')+7 : data.index('</a>')]
			teamAbbr = teamCode[ : teamCode.index('/')]
			team = Team.objects.get(abbr__iexact=teamAbbr)
			yd = YearData.objects.get(player=player, year=year)
			if team.id != player.team.id:
				player.team = team
				player.save()
				yd.team = team
				yd.save()
				return team.name
		except: # Player has no number/position -- Free Agent
			if player.team.id != 33:
				player.team = Team.objects.get(id=33)
				player.save()
				yd.team = team
				yd.save()
				return player.team.name

		return False


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


		




