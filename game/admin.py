from django.contrib import admin
from game.models import Player, Position, Team

class PlayerAdmin(admin.ModelAdmin):
	fieldsets = [
		('Demographic Information', {'fields': ['name', 'height', 'weight', 'dob']}),
		('Player Information', {'fields': ['team', 'position', 'depth_position', 'number']})
	]
	list_display = ('name', 'position', 'team')
	search_fields = ['name']

class TeamAdmin(admin.ModelAdmin):
	fields = ['name', 'stadium']
	search_fields = ['name']

admin.site.register(Player, PlayerAdmin)
admin.site.register(Position)
admin.site.register(Team, TeamAdmin)