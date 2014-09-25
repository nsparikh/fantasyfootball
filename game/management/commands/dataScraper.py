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
		# Write what we want to do here



	# Scrapes the data for the player in the given week and year
	# Creates a new DataPoint object or updates it and saves it
	# Returns the DataPoint object
	def getPlayerGameDataPoint(player, year, week_number):
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
	def isAllNullDataPoint(dp):
		dpFields = [field for field in dp._meta.get_all_field_names() if (
			'data' not in field and field != 'id')]
		for field in dpFields:
			if dp.field is not None: return False
		return True




