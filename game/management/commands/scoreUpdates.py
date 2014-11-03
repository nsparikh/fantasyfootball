from django.db.models import Count, Avg, Sum, Q

from game.models import Player, Position, Team, Matchup
from data.models import YearData, GameData, DataPoint

from django.core.management.base import NoArgsCommand, make_option

class Command(NoArgsCommand):

	help = ''
	numTeams = 32

	option_list = NoArgsCommand.option_list + (
		make_option('--verbose', action='store_true'),
	)

	def handle_noargs(self, **options):
		pass


	# Computes the performance scores for each player in the given year/week
	# Saves to database
	def computePerformanceScores(self, year, week_number):
		print 'COMPUTING PERFORMANCE SCORES:', year, 'WEEK', week_number
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
					if not matchup.bye:
						opponent = matchup.home_team if yd.team.id==matchup.away_team.id else matchup.away_team
						score = self.playerPerformanceScore(player, year, week_number, opponent)

					# Save the score
					gameData.performance_score = score
					gameData.save()
				except:
					pass


	# Computes the performance score of the given player in the year and week 
	# player is a Player object, opponent is a Team object
	# The performance score is computed as follows:
	#	offScore = (total fantasy pts earned this season) - 
	#		(avg total fantasy pts earned across all players of this pos and depth_pos)
	#	defScore = (avg total fantasy pts earned by all players of 
	#			    this pos and depth_pos across each defense) - 
	#		(total fantasy pts earned by players of this pos and depth_pos against this defense)
	#	score = offScore - defScore
	def playerPerformanceScore(self, player, year, week_number, opponent):
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


	# Computes the projection of the given player in the year and week
	def playerProjection(self, player, year, week_number, opponent):
		pass
