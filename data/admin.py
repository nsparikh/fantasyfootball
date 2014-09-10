from django.contrib import admin
from data.models import DataPoint, YearData, GameData

class DataPointAdmin(admin.ModelAdmin):
	fieldsets = [
		('Passing', {'fields': ['passC', 'passA', 'passYds', 'passTDs', 'passInt']}),
		('Rushing', {'fields': ['rush', 'rushYds', 'rushTDs']}),
		('Receiving', {'fields': ['rec', 'recYds', 'recTDs', 'recTar']}),
		('Misc', {'fields': ['misc2pc', 'miscFuml', 'miscTDs']}),
		(None, {'fields': ['points']})
	]
	list_display = ('id', 'passYds', 'rushYds', 'recYds', 'points')


admin.site.register(DataPoint, DataPointAdmin)
admin.site.register(YearData)
admin.site.register(GameData)