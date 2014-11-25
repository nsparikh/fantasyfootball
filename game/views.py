from django.shortcuts import get_object_or_404, render, render_to_response
from django.core.urlresolvers import reverse
from django.views import generic
from datetime import date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Avg, Sum, Q
import json

from game.models import Player, Position, Team, Matchup
from data.models import YearData, GameData, DataPoint


def getWeekAndYear(request):
	(min_week, max_week) = (1, 17)
	(min_year, max_year) = (2013, 2014) 

	current_week = 12 # TODO: change this each week?
	current_year = 2014

	changedYear = False
	if request.GET.get('year'):
		request.session['year'] = max(min_year, min(int(request.GET.get('year')), current_year))
		changedYear = True
	year = request.session.get('year', current_year)
	request.session['year'] = year

	# Set the 'max' week based on whether it's the current season or a past one
	request.session['max_week'] = current_week if request.session['year'] == current_year else max_week

	# If the user changed the week number, it will be in the get request
	# We need to update the record in the session
	if request.GET.get('week') and not changedYear:
		request.session['week_number'] = max(min_week, min(int(request.GET.get('week')), 
			request.session['max_week']))
	elif changedYear: request.session['week_number'] = request.session['max_week']
	week_number = request.session.get('week_number', request.session['max_week'])

	return (week_number, year)

# TODO: Clean up this code!!
def players(request):
	player_list = None
	# Request parameters:
	# sort = name, team, pos, any of data vars (default=points)
	# order = asc or desc
	# pos = all, qb, rb, wr, te, dst, k, flex
	sortMatch = {
		'name':'player__name', 
		'team':'player__team__name',
		'pos':'player__position__abbr'
	}
	sort = 'points' # parameter to order players by
	originalSort = 'points'
	order = 'desc' # ordering of list
	pos = 'ALL' # position(s) to display in list

	(week_number, year) = getWeekAndYear(request)

	# TODO: clean this code up
	# Configure sort variable to have proper format for database access
	if 'sort' in request.GET: 
		sort = request.GET['sort']
		originalSort = request.GET['sort']
	if sort in sortMatch: sort = sortMatch[sort]
	else: sort = 'data__'+sort

	# Add '-' to sort variable if sort order is descending
	if originalSort == 'name' or originalSort == 'team' or originalSort == 'pos': order = 'asc'
	if 'order' in request.GET: order = request.GET['order'].lower()
	sort = sort if order=='asc' else '-'+sort

	# Filter data based on position
	if 'pos' in request.GET: pos = request.GET['pos'].upper()
	if pos in ['QB', 'RB', 'WR', 'TE', 'K']:
		player_list = YearData.objects.filter(
			player__position__abbr__iexact=pos, year=year
		)
	elif pos == 'DST':
		player_list = YearData.objects.filter(
			player__position__abbr__iexact='D/ST', year=year
		)
	elif pos == 'FLEX':
		player_list = YearData.objects.filter(
			player__position__abbr__in=['RB', 'WR', 'TE'], year=year
		)
	else:
		player_list = YearData.objects.filter(year=year)

	# Place any players with null data at the end
	player_list = player_list.annotate(
		null_sort=Count(sort.replace('-', ''))).order_by(
		'-null_sort', sort, 'player__name')

	# Paginate player_list
	paginator = Paginator(player_list, 50) # show 50 players per page
	page = request.GET.get('page')
	try:
		player_list = paginator.page(page)
	except PageNotAnInteger:
		player_list = paginator.page(1)
	except EmptyPage:
		player_list = paginator.page(paginator.num_pages)

	# Put into JSON format for javascript access
	player_list_json = json.dumps([ obj.as_dict() for obj in player_list ], cls=DjangoJSONEncoder)
	return render(request, 'game/players.html', {
		'player_list': player_list,
		'player_list_json': player_list_json,
		'posList': ['ALL', 'QB', 'RB', 'WR', 'TE', 'DST', 'K', 'FLEX'],
		'curPos': pos,
		'sortList': [
			('name','Name', 'Player Name'), ('team','Team', 'Player Team'), 
			('pos','Pos', 'Player Position'), ('passC','C', 'Pass Completions'), 
			('passA','A', 'Pass Attempts'), ('passYds','Yds', 'Passing Yards'), 
			('passTDs','TD', 'Passing Touchdowns'), ('passInt','Int', 'Interceptions Thrown'), 
			('rush','Rush', 'Rushing Attempts'), ('rushYds','Yds', 'Rushing Yards'), 
			('rushTDs','TD', 'Rushing Touchdowns'), ('rec','Rec', 'Total Receptions'), 
			('recYds','Yds', 'Receiving Yards'), ('recTDs','TD', 'Receiving Touchdowns'),
			('recTar','Tar', 'Receiving Targets'), ('misc2pc','2PC', '2pt Conversions'), 
			('miscFuml','Fuml', 'Fumbles Lost'), ('miscTDs','TD', 'Return Touchdowns'), 
			('points','Pts', 'Fantasy Points')
		],
		'curSort': originalSort
	})

# Called on the players graph page
# Retrieves the top 200 performing players (based on fantasy pts)
def players_graph(request):
	(week_number, year) = getWeekAndYear(request)

	player_list = YearData.objects.filter(year=year).annotate(
		null_sort=Count('data__points')).order_by(
		'-null_sort', '-data__points', 'player__name')[0:200]
	player_list_json = json.dumps([ obj.as_dict() for obj in player_list ], cls=DjangoJSONEncoder)
	return render(request, 'game/players_graph.html', {
		'player_list_json': player_list_json
	})

# Called for the player detail pages
class PlayerDetailView(generic.DetailView):
	template_name = 'game/player_detail.html'
	model = Player
	context_object_name = 'player'

	# Retrieves the necessary data for the player detail page
	def get_context_data(self, **kwargs):
		context = super(PlayerDetailView, self).get_context_data(**kwargs)

		(week_number, year) = getWeekAndYear(self.request)

		# Get this player's current year's data 
		yd = YearData.objects.get(player__id=self.object.id, year=year)
		context['cur_season_yeardata'] = yd
		context['cur_season_team'] = yd.team

		# Get the matchup for the week
		matchup = Matchup.objects.get(Q(home_team=yd.team) | Q(away_team=yd.team), 
			year=year, week_number=week_number)
		context['matchup'] = matchup
		context['matchup_location'] = matchup.home_team.stadium[
			matchup.home_team.stadium.index(',')+2 : ]

		# Selected week's data (if any)
		try:
			context['week_gamedata'] = GameData.objects.get(player=self.object.id, matchup=matchup)
		except:
			context['week_gamedata'] = None

		# Previous matchup with this opponent
		if not matchup.bye:
			opponent = matchup.away_team if matchup.home_team.id==yd.team.id else matchup.home_team
			try:
				prev_matchup = Matchup.objects.filter(Q(home_team=yd.team) | 
					Q(away_team=yd.team), date__lte=matchup.date).order_by(
					'-date').exclude(id=matchup.id).filter(
					Q(home_team=opponent) | Q(away_team=opponent))[0]
				home_game = prev_matchup.home_team.id==yd.team.id
				prev_win = (home_game and prev_matchup.win) or (not home_game and not prev_matchup.win)
				prev_matchup_result = (prev_matchup.home_team.abbr + ' vs. ' + prev_matchup.away_team.abbr +
					', ' + ('W ' if prev_win else 'L ') + str(prev_matchup.home_team_points) + 
					'-' + str(prev_matchup.away_team_points))
				context['prev_matchup_date'] = prev_matchup.date
				context['prev_matchup_espn_id'] = prev_matchup.espn_game_id 
			except: prev_matchup_result = None
			context['prev_matchup_result'] = prev_matchup_result


		# Compute total feet and inches (from height in inches)
		context['feet'] = self.object.height / 12
		context['inches'] = self.object.height % 12

		# Compute the player's current age based on DOB
		dob = self.object.dob
		today = date.today()
		if dob is not None:
			context['age'] = today.year - dob.year - (
				(today.month, today.day) < (dob.month, dob.day))
		else: context['age'] = None

		# TODO: figure out where to store images? For now, get directly from ESPN url
		#context['image_path'] = 'game/player_images/' + str(self.object.espn_id) + '.png'
		context['image_path'] = ('http://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/' + 
			str(self.object.espn_id) + '.png')
		context['espn_game_url'] = 'http://sports-ak.espn.go.com/nfl/boxscore?gameId='
		
		# Get this player's full set of current season data
		cur_season_gamedata = GameData.objects.filter(
			player__id=self.object.id, matchup__year=year, matchup__bye=False, 
			matchup__week_number__lte=self.request.session['max_week']
		).exclude(data=1).order_by('matchup__week_number')
		cur_season_gamedata_json = json.dumps([ obj.as_dict() for obj in cur_season_gamedata ], 
			cls=DjangoJSONEncoder)
		context['cur_season_gamedata'] = cur_season_gamedata_json

		# The path for the player detail table template
		context['player_detail_table_path'] = ('game/player_table_' + 
			self.object.position.abbr.replace('/', '').lower() + '.html')

		return context
		

# Called for the positions list page
class PositionView(generic.ListView):
	template_name = 'game/positions.html'
	context_object_name = 'position_list'

	def get_queryset(self):
		return Position.objects.all()

# Called for the position detail page
class PositionDetailView(generic.DetailView):
	template_name = 'game/position_detail.html'
	model = Position
	context_object_name = 'position'

	# Retrieves the necessary data for the position detail page
	def get_context_data(self, **kwargs):
		context = super(PositionDetailView, self).get_context_data(**kwargs)

		# Get the list of all of the teams
		teams = Team.objects.all().exclude(id=33) # We don't want FA
		context['teams_json'] = json.dumps([ obj.as_dict() for obj in teams ], cls=DjangoJSONEncoder)
		teams = teams.order_by('name')

		posId = self.object.id

		(week_number, year) = getWeekAndYear(self.request)

		# Get the matchups for the selected week
		matchups = Matchup.objects.all().filter(week_number=week_number, year=year)

		# Get the players that are of this position and have a depth chart position
		player_list = Player.objects.all().filter(
			position__id=posId).exclude(depth_position__isnull=True)
		if posId == 1: player_list = player_list.exclude(depth_position__gte=2)

		# Create a map of each team to an ordered list of players of this position
		team_map_list = [] 
		for t in teams:
			# Figure out the opponent from the matchups (if it's not a BYE week)
			m = matchups.get(Q(home_team=t) | Q(away_team=t))
			if m.bye: opponent = None
			else: opponent = m.home_team.id if t.id==m.away_team.id else m.away_team.id
			
			# Figure out the team's bye week
			num_weeks = week_number
			bye_week = Matchup.objects.get(home_team=t.id, bye=True, year=year).week_number
			if bye_week <= week_number: num_weeks -= 1

			# Ordered list of players for this team of the position
			team_players = player_list.filter(team=t.id).order_by('depth_position', 'name')
			depth_list = [None] * len(team_players)

			if posId == 5:
				p = team_players[0]
				totalPtsEarned = GameData.objects.filter(player=p.id,
					matchup__week_number__lte=week_number, matchup__year=year).aggregate(
					Sum('data__points'))['data__points__sum']

				pScore = [totalPtsEarned, num_weeks, 0, 0, 0, 0, 0, 0, 0, 0]

				for i in range(1, 5):
					allPos = GameData.objects.filter(Q(matchup__home_team=t.id) | Q(matchup__away_team=t.id), 
						player__position=i, matchup__year=year, matchup__week_number__lte=week_number).exclude(
						player__team=t.id)
					totalPosPts = allPos.aggregate(Sum('data__points'))['data__points__sum']
					posCount = allPos.exclude(Q(data=1) | Q(player__depth_position__isnull=True)).count()
					avgPosPts = totalPosPts * 1.0 / posCount
					pScore[i+1] = totalPosPts
					pScore[i+5] = avgPosPts	
				depth_list[0] = (p.as_dict(), pScore)
			else:
				for index in range(len(depth_list)):
					p = team_players[index]
					# Compute score for this player
					pScore = 0
					if opponent is not None:
						try:
							pScore = GameData.objects.get(player=p.id, matchup__year=year, 
								matchup__week_number=week_number).performance_score
							pScore = 0 if pScore is None else pScore
						except:
							pScore = 0
					depth_list[index] = (p.as_dict(), pScore)

			team_map = {'team_id':t.id, 'opponent':opponent, 'players':depth_list}
			team_map_list.append(team_map)

		context['team_map_list_json'] = json.dumps(team_map_list, cls=DjangoJSONEncoder)
		context['position_detail_table_path'] = 'game/position_table_' + self.object.abbr.replace('/', '').lower() + '.html'
		return context

class TeamView(generic.ListView):
	template_name = 'game/teams.html'
	queryset = Team.objects.all()
	context_object_name = 'team_list'

	def get_context_data(self, **kwargs):
		context = super(TeamView, self).get_context_data(**kwargs)
		context['directionList'] = ['East', 'West', 'North', 'South']
		return context

class TeamDetailView(generic.DetailView):
	template_name = 'game/team_detail.html'
	model = Team
	context_object_name = 'team'


	# Need to provide the list of players of each position
	def get_context_data(self, **kwargs):
		context = super(TeamDetailView, self).get_context_data(**kwargs)
		players = Player.objects.all().filter(team=self.object.id)
		context['QB'] = players.filter(position=1).annotate(
			null_sort=Count('depth_position')).order_by(
				'-null_sort', 'depth_position', 'name')
		context['RB'] = players.filter(position=2).annotate(
			null_sort=Count('depth_position')).order_by(
				'-null_sort', 'depth_position', 'name')
		context['WR'] = players.filter(position=3).annotate(
			null_sort=Count('depth_position')).order_by(
				'-null_sort', 'depth_position', 'name')
		context['TE'] = players.filter(position=4).annotate(
			null_sort=Count('depth_position')).order_by(
				'-null_sort', 'depth_position', 'name')
		context['DST'] = players.filter(position=5).annotate(
			null_sort=Count('depth_position')).order_by(
				'-null_sort', 'depth_position', 'name')
		context['K'] = players.filter(position=6).annotate(
			null_sort=Count('depth_position')).order_by(
				'-null_sort', 'depth_position', 'name')

		context['numQB'] = len(context['QB'])
		context['numRB'] = len(context['RB'])
		context['numWR'] = len(context['WR'])
		context['numTE'] = len(context['TE'])
		context['numDST'] = len(context['DST'])
		context['numK'] = len(context['K'])

		context['numRows'] = max(context['numQB'], context['numRB'], context['numWR'], 
			context['numTE'], context['numDST'], context['numK'])
		return context




