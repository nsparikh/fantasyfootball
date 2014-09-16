from django.shortcuts import get_object_or_404, render, render_to_response
from django.core.urlresolvers import reverse
from django.views import generic
from django.db.models import Count
from datetime import date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json

from game.models import Player, Position, Team
from data.models import YearData, GameData, DataPoint

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
			player__position__abbr__iexact=pos
		)
	elif pos == 'DST':
		player_list = YearData.objects.filter(
			player__position__abbr__iexact='D/ST'
		)
	elif pos == 'FLEX':
		player_list = YearData.objects.filter(
			player__position__abbr__in=['RB', 'WR', 'TE']
		)
	else:
		player_list = YearData.objects.all()

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
	player_list_json = json.dumps([ obj.as_dict() for obj in player_list ])
	return render(request, 'game/players.html', {
		'player_list': player_list,
		'player_list_json': player_list_json,
		'posList': ['ALL', 'QB', 'RB', 'WR', 'TE', 'DST', 'K', 'FLEX'],
		'curPos': pos,
		'sortList': [
			('name','Name'), ('team','Team'), ('pos','Pos'), ('passC','C'), 
			('passA','A'), ('passYds','Yds'), ('passTDs','TD'),
			('passInt','Int'), ('rush','Rush'), ('rushYds','Yds'), 
			('rushTDs','TD'), ('rec','Rec'), ('recYds','Yds'), ('recTDs','TD'),
			('recTar','Tar'), ('misc2pc','2PC'), ('miscFuml','Fuml'), 
			('miscTDs','TD'), ('points','Pts')
		],
		'curSort': originalSort
	})

def players_graph(request):
	player_list = YearData.objects.all().annotate(
		null_sort=Count('data__points')).order_by(
		'-null_sort', '-data__points', 'player__name')[0:200]
	player_list_json = json.dumps([ obj.as_dict() for obj in player_list ])
	return render(request, 'game/players_graph.html', {
		'player_list_json': player_list_json
	})

class PlayerDetailView(generic.DetailView):
	template_name = 'game/player_detail.html'
	model = Player
	context_object_name = 'player'

	def get_context_data(self, **kwargs):
		context = super(PlayerDetailView, self).get_context_data(**kwargs)
		context['feet'] = self.object.height / 12
		context['inches'] = self.object.height % 12

		dob = self.object.dob
		today = date.today()
		if dob is not None:
			context['age'] = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
		else: context['age'] = None

		#context['image_path'] = 'game/player_images/' + str(self.object.espn_id) + '.png'
		context['image_path'] = 'http://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/' + str(self.object.espn_id) + '.png'

		# TODO: change to get current year data
		context['cur_season_yeardata'] = YearData.objects.filter(
			player__id=self.object.id, year=2013
		)[0]

		# TODO: change to get current year from selection
		cur_season_gamedata = GameData.objects.filter(
			player__id=self.object.id, year=2013, bye=False
		).exclude(
			data=1
		)
		cur_season_gamedata_json = json.dumps([ obj.as_dict() for obj in cur_season_gamedata ])
		context['cur_season_gamedata'] = cur_season_gamedata_json

		context['player_detail_table_path'] = 'game/player_table_' + self.object.position.abbr.replace('/', '').lower() + '.html'

		return context
		


class PositionView(generic.ListView):
	template_name = 'game/positions.html'
	context_object_name = 'position_list'

	def get_queryset(self):
		return Position.objects.all()

class PositionDetailView(generic.DetailView):
	template_name = 'game/position_detail.html'
	model = Position
	context_object_name = 'position'

	# How many players of each position can a team have
	posDepthLength = {'QB':3, 'RB':4, 'WR':7, 'TE':5, 'D/ST':1, 'K':1}

	def get_context_data(self, **kwargs):
		context = super(PositionDetailView, self).get_context_data(**kwargs)

		teams = Team.objects.all().exclude(id=33) # We don't want FA
		context['teams_json'] = json.dumps([ obj.as_dict() for obj in teams ])
		teams = teams.order_by('name')

		posId = self.object.id

		# Get the players that are of this position and have a depth chart position
		player_list = Player.objects.all().filter(
			position=posId).exclude(depth_position__isnull=True)

		team_map_list = [] # List of each team id mapped to an ordered list of players
		for t in teams:
			depth_list = [None] * self.posDepthLength[self.object.abbr]
			team_players = player_list.filter(team=t.id)
			for p in team_players:
				index = p.depth_position - 1
				if self.object.id == 3: # WR have multiple in a single depth position
					index = (p.depth_position - 1) * 2
					if depth_list[index] is not None: index += 1
				elif self.object.id == 4: # TE have multiple in depth position 1
					index = p.depth_position if p.depth_position > 1 else p.depth_position - 1
					if depth_list[index] is not None: index += 1
				depth_list[index] = p.as_dict() # QB, RB, D/ST, K

			team_map = { 'team_id' : t.id }
			team_map['players'] = depth_list
			team_map_list.append(team_map)
		context['team_map_list_json'] = json.dumps(team_map_list)

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

	def get_context_data(self, **kwargs):
		context = super(TeamDetailView, self).get_context_data(**kwargs)
		players = Player.objects.all().filter(team=self.object.id)
		context['QB'] = players.filter(position=1)
		context['RB'] = players.filter(position=2)
		context['WR'] = players.filter(position=3).annotate(
			null_sort=Count('depth_position')).order_by(
				'-null_sort', 'depth_position', 'name')
		context['TE'] = players.filter(position=4)
		context['DST'] = players.filter(position=5)
		context['K'] = players.filter(position=6)

		context['numQB'] = len(context['QB'])
		context['numRB'] = len(context['RB'])
		context['numWR'] = len(context['WR'])
		context['numTE'] = len(context['TE'])
		context['numDST'] = len(context['DST'])
		context['numK'] = len(context['K'])

		context['numRows'] = max(context['numQB'], context['numRB'], context['numWR'], 
			context['numTE'], context['numDST'], context['numK'])
		return context




