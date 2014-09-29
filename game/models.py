from django.db import models

# PK FORMAT:
# pxxxx
# p = position: QB=1, RB=2, WR=3, TE=4, D/ST=5, K=6
# xxxx = random 4 digits
class Player(models.Model):
	espn_id = models.IntegerField()
	name = models.CharField(max_length=200)
	height = models.IntegerField() # height in inches
	weight = models.IntegerField() # weight in lbs
	dob = models.DateField('Date of Birth', null=True)
	team = models.ForeignKey('Team')
	position = models.ForeignKey('Position')
	depth_position = models.IntegerField(null=True)
	number = models.IntegerField()
	status = models.CharField(max_length=200, null=True)

	def __unicode__(self):
		return self.name

	def fixtureString(self):
		return ('{ ' + '"model":"game.Player", "pk":'+str(self.id) +  
			', "fields":{"espn_id":' + str(self.espn_id) + 
			', "name":"' + self.name + 
			'", "height":' + str(self.height) + 
			', "weight":' + str(self.weight) + 
			', "dob":"' + ('null' if self.dob is None else str(self.dob)) + 
			'", "team":' + str(self.team.id) + 
			', "position":' + str(self.position.id) + 
			', "depth_position":' + ('null' if self.depth_position is None else str(self.depth_position)) + 
			', "number":' + str(self.number) + 
			', "status":' + ('null' if self.status is None else ('"'+self.status+'"')) + '} },')

	def as_dict(self):
		return {
			"id": self.id,
			"espn_id": self.espn_id, 
			"name": self.name,
			"height": self.height,
			"weight": self.weight,
			"dob": str(self.dob),
			"team": self.team.as_dict(),
			"position": self.position.as_dict(),
			"depth_position": self.depth_position,
			"number": self.number,
			"status": self.status
		}

class Position(models.Model):
	# Primary keys: QB=1, RB=2, WR=3, TE=4, D/ST=5, K=6
	name = models.CharField(max_length=200)
	abbr = models.CharField(max_length=200)

	def __unicode__(self):
		return self.name

	def fixtureString(self):
		return ('{ ' + '"model":"game.Position", "pk":'+str(self.id) +  
			', "fields":{"espn_id":' + str(self.espn_id) + 
			', "name":"' + self.name + 
			'", "abbr":"' + self.abbr + '"} },')

	def as_dict(self):
		return {
			"id": self.id,
			"name": self.name,
			"abbr": self.abbr
		}

class Team(models.Model):
	# Team primary keys in order:
	#["Dal", "NYG", "Phi", "Wsh", "Ari", "SF", "Sea", "StL", 
	# "Chi", "Det", "GB", "Min", "Atl", "Car", "NO", "TB", 
	# "Buf", "Mia", "NE", "NYJ", "Den", "KC", "Oak", "SD", 
	# "Bal", "Cin", "Cle", "Pit", "Hou", "Ind", "Jac", "Ten", "FA"]

	espn_id = models.IntegerField()
	name = models.CharField(max_length=200)
	abbr = models.CharField(max_length=200)
	stadium = models.CharField(max_length=200)
	division = models.CharField(max_length=200, null=True)

	def __unicode__(self):
		return self.name

	def fixtureString(self):
		return ('{ ' + '"model":"game.Team", "pk":'+str(self.id) +  
			', "fields":{"espn_id":' + str(self.espn_id) + 
			', "name":"' + self.name + 
			'", "abbr":"' + self.abbr + 
			'", "stadium":"' + self.stadium +
			'", "division":' + ('null' if self.division is None else '"'+self.division+'"') + '} },')

	def as_dict(self):
		return {
			"id": self.id,
			"espn_id": self.espn_id,
			"name": self.name,
			"abbr": self.abbr,
			"stadium": self.stadium,
			"division": self.division
		}

# PK FORMAT: t1t2yyww
# t1, t2 = teams playing ordered by PK
# t1 may be 1-digit (bc can't have leading 0's)
# if BYE week, then format will be tt00yyww
class Matchup(models.Model):
	espn_game_id = models.IntegerField(null=True)
	year = models.IntegerField()
	date = models.DateField(null=True)
	week_number = models.IntegerField()
	bye = models.NullBooleanField(default=None)
	home_team = models.ForeignKey('game.Team', related_name='home_team')
	away_team = models.ForeignKey('game.Team', null=True, related_name='away_team')
	win = models.NullBooleanField(default=None, null=True) # True if home_team wins
	home_team_points = models.IntegerField(null=True) # Points for home_team
	away_team_points = models.IntegerField(null=True) # Points for away_team

	def __unicode__(self):
		if self.away_team:
			return (self.home_team.name + ' vs ' + self.away_team.name + ', WEEK ' + 
				str(self.week_number) + ' ' + str(self.year))
		return self.home_team.name + ' BYE WEEK ' + str(self.week_number) + ' ' + str(self.year)

	def fixtureString(self):
		return ( '{ ' + '"model":"game.Matchup", "pk":'+str(self.id) +  
			', "fields":{"espn_game_id":' + ('null' if self.espn_game_id is None else str(self.espn_game_id)) + 
			', "year":' + str(self.year) + 
			', "date":' + ('null' if self.date is None else '"'+str(self.date)+'"') + 
			', "week_number":' + str(self.week_number) +
			', "bye":' + str(self.bye).lower() + 
			', "home_team":' + str(self.home_team.id) + 
			', "away_team":' + ('null' if self.away_team is None else str(self.away_team.id)) + 
			', "win":' + ('null' if self.win is None else str(self.win).lower()) +
			', "home_team_points":' + ('null' if self.home_team_points is None else str(self.home_team_points)) + 
			', "away_team_points":' + ('null' if self.away_team_points is None else str(self.away_team_points)) + '} },' )

	def as_dict(self):
		return {
			"id": self.id,
			"espn_game_id": self.espn_game_id,
			"year": self.year,
			"date": str(self.date),
			"week_number": self.week_number,
			"bye": self.bye,
			"home_team": self.home_team.as_dict(),
			"away_team": self.away_team.as_dict(),
			"win": self.win,
			"home_team_points": self.home_team_points,
			"away_team_points": self.away_team_points
		}
