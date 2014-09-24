from django.contrib import admin
from game.models import Player, Position, Team, Matchup

class PlayerAdmin(admin.ModelAdmin):
	fieldsets = [
		('ID', {'fields': ['id']}),
		('Demographic Information', {'fields': ['name', 'height', 'weight', 'dob']}),
		('Player Information', {'fields': ['team', 'position', 'depth_position', 'number']})
	]
	readonly_fields = ('id', 'name', 'position', 'team')
	list_display = ('name', 'position', 'team')
	search_fields = ['name']

class TeamAdmin(admin.ModelAdmin):
	readonly_fields = ('id', 'name', 'stadium')
	fields = ('id', 'name', 'stadium')
	search_fields = ['name']

admin.site.register(Player, PlayerAdmin)
admin.site.register(Position)
admin.site.register(Team, TeamAdmin)
admin.site.register(Matchup)