from django.contrib import admin
from data.models import DataPoint, YearData, GameData

class DataPointAdmin(admin.ModelAdmin):
	readonly_fields = ('passC', 'passA', 'passYds', 'passTDs', 'passInt', 
		'rush', 'rushYds', 'rushTDs', 'rec', 'recYds', 'recTDs', 'recTar',
		'misc2pc', 'miscFuml', 'miscTDs', 'points')
	fieldsets = [
		('Passing', {'fields': ['passC', 'passA', 'passYds', 'passTDs', 'passInt']}),
		('Rushing', {'fields': ['rush', 'rushYds', 'rushTDs']}),
		('Receiving', {'fields': ['rec', 'recYds', 'recTDs', 'recTar']}),
		('Misc', {'fields': ['misc2pc', 'miscFuml', 'miscTDs']}),
		(None, {'fields': ['points']})
	]
	list_display = ('id', 'passYds', 'rushYds', 'recYds', 'points')

class GameDataAdmin(admin.ModelAdmin):
	readonly_fields = ('id', 'player', 'matchup', 'data', 'projection', 
		'espn_projection', 'yahoo_projection', 'cbs_projection',  'performance_score')
	fields = ('id', 'player', 'matchup', 'projection', 'espn_projection', 
		'yahoo_projection', 'cbs_projection', 'performance_score', 'data')
	list_display = ('player', 'matchup')
	search_fields = ['id', 'player__name']

admin.site.register(DataPoint, DataPointAdmin)
admin.site.register(YearData)
admin.site.register(GameData, GameDataAdmin)