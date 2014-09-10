from django.conf.urls import patterns, url
from game import views

urlpatterns = patterns('',
	url(r'^players/$', views.players, name='players'),
	url(r'^players/graph$', views.players_graph, name='players_graph'),
	url(r'^players/(?P<pk>\d+)/$', views.PlayerDetailView.as_view(), name='player_detail'),
	url(r'^positions/$', views.PositionView.as_view(), name='positions'),
	url(r'^positions/(?P<pk>\d+)/$', views.PositionDetailView.as_view(), name='position_detail'),
	url(r'^teams/$', views.TeamView.as_view(), name='teams'),
	url(r'^teams/(?P<pk>\d+)/$', views.TeamDetailView.as_view(), name='team_detail')
)