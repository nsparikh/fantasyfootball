from django.db.models import Count, Avg, Sum, Q

from game.models import Player, Position, Team, Matchup
from data.models import YearData, GameData, DataPoint

from django.core.management.base import NoArgsCommand, make_option

import urllib2

class Command(NoArgsCommand):

	help = 'Update Matchups, weekly/yearly data'
	playerProfilePrefix = 'http://espn.go.com/nfl/players/profile?playerId='
	searchPrefix = 'http://sports.yahoo.com/nfl/players?type=lastname&first=1&query='

	option_list = NoArgsCommand.option_list + (
		make_option('--verbose', action='store_true'),
	)

	def handle_noargs(self, **options):
		players = Player.objects.all().order_by('id')
		for i in range(len(players)):
			p = players[i]
			if p.yahoo_id is None: print p.name

	def getPlayerYahooId(self, player):
		searchUrl = self.searchPrefix + player.name.replace(' ', '+')
		pageData = urllib2.urlopen(searchUrl).read()
		pageData = pageData[pageData.index('Search Results') : ]
		pageData = pageData[ : pageData.index('</table>')]

		rows = pageData.split('<tr')[2:]
		if 'No players found' in rows[0]:
			return False

		for row in rows:
			elms = row.split('<td>')[1:]
			curName = elms[0][elms[0].index('">')+2 : elms[0].index('</a>')]
			posAbbr = elms[1][ : elms[1].index('</td>')]
			if posAbbr == player.position.abbr:
				yahoo_id = int(elms[0][elms[0].index('players/')+8 : elms[0].index('">')])
				player.yahoo_id = yahoo_id
				player.save()
				return True
		return False

		
