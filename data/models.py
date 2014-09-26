from django.db import models


# PK FORMAT:
# pppppyyww
# ppppp = 5-digit player PK
# yy = 2-digit year
# ww = 2-digit week number (00=YearData, 99=CareerData)
# ** BLANK DATA: pk=0 **
class DataPoint(models.Model):
	passC = models.IntegerField(null=True)
	passA = models.IntegerField(null=True)
	passYds = models.IntegerField(null=True)
	passTDs = models.IntegerField(null=True)
	passInt = models.IntegerField(null=True)
	rush = models.IntegerField(null=True)
	rushYds = models.IntegerField(null=True)
	rushTDs = models.IntegerField(null=True)
	rec = models.IntegerField(null=True)
	recYds = models.IntegerField(null=True)
	recTDs = models.IntegerField(null=True)
	recTar = models.IntegerField(null=True)
	misc2pc = models.IntegerField(null=True)
	miscFuml = models.IntegerField(null=True)
	miscTDs = models.IntegerField(null=True)
	points = models.IntegerField(null=True)

	def __unicode__(self):
		return str(self.id)

	def fixtureString(self):
		return ( '{ ' + '"model":"data.DataPoint", "pk":'+str(self.id) + 
			', "fields":{"passC":' + str(self.passC) +
			', "passA":' + str(self.passA) +
			', "passYds":' + str(self.passYds) +
			', "passTDs":' + str(self.passTDs) +
			', "passInt":' + str(self.passInt) +
			', "rush":' + str(self.rush) +
			', "rushYds":' + str(self.rushYds) +
			', "rushTDs":' + str(self.rushTDs) +
			', "rec":' + str(self.rec) +
			', "recYds":' + str(self.recYds) +
			', "recTDs":' + str(self.recTDs) +
			', "recTar":' + str(self.recTar) +
			', "misc2pc":' + str(self.misc2pc) +
			', "miscFuml":' + str(self.miscFuml) +
			', "miscTDs":' + str(self.miscTDs) +
			', "points":' + str(self.points) + '} },' )

	def as_dict(self):
		return {
			"id": self.id,
			"passC": self.passC,
			"passA": self.passA,
			"passYds": self.passYds,
			"passTDs": self.passTDs,
			"passInt": self.passInt,
			"rush": self.rush,
			"rushYds": self.rushYds,
			"rushTDs": self.rushTDs,
			"rec": self.rec,
			"recYds": self.recYds,
			"recTDs": self.recTDs,
			"recTar": self.recTar,
			"misc2pc": self.misc2pc,
			"miscFuml": self.miscFuml,
			"miscTDs": self.miscTDs,
			"points": self.points
		}

# PK FORMAT: ppppp
class CareerData(models.Model):
	player = models.ForeignKey('game.Player')
	data = models.ForeignKey(DataPoint)

	def __unicode__(self):
		return self.player.name

	def fixtureString(self):
		return ( '{ ' + '"model":"data.CareerData", "pk":'+str(self.id) + 
			', "fields":{"player":' + str(self.player.id) +
			', "data":' + str(self.data.id) + '} },' )

	def as_dict(self):
		return {
			"id": self.id,
			"player": self.player.as_dict(),
			"data": self.data.as_dict()
		}

# PK FORMAT: pppppyy
class YearData(models.Model):
	year = models.IntegerField()
	player = models.ForeignKey('game.Player')
	team = models.ForeignKey('game.Team', default=33)
	average = models.DecimalField(max_digits=5, decimal_places=2, default=0) # Avg fantasy points per game for the year
	data = models.ForeignKey(DataPoint)

	def __unicode__(self):
		return self.player.name + ',' + str(self.year)

	def fixtureString(self):
		return ('{ ' + '"model":"data.YearData", "pk":'+str(self.id) +  
			', "fields":{"year":' + str(self.year) + 
			', "player":' + str(self.player.id) +
			', "team":' + str(self.team.id) +
			', "average":' + str(self.average) +
			', "data":' + str(self.data.id) + '} },')

	def as_dict(self):
		return {
			"id": self.id,
			"year": self.year,
			"player": self.player.as_dict(),
			"team": self.team.as_dict(),
			"average": self.average,
			"data": self.data.as_dict()
		}

# PK FORMAT: pppppyyww
class GameData(models.Model):
	player = models.ForeignKey('game.Player')
	matchup = models.ForeignKey('game.Matchup', null=True)
	projection = models.DecimalField(max_digits=5, decimal_places=1, null=True)
	espn_projection = models.DecimalField(max_digits=5, decimal_places=1, null=True)
	yahoo_projection = models.DecimalField(max_digits=5, decimal_places=1, null=True)
	cbs_projection = models.DecimalField(max_digits=5, decimal_places=1, null=True)
	performance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
	data = models.ForeignKey(DataPoint)

	def fixtureString(self):
		return ( '{ ' + '"model":"data.GameData", "pk":'+str(self.id) + 
			', "fields":{"player":' + str(self.player.id) +
			', "matchup":' + ('null' if self.matchup is None else str(self.matchup.id)) +
			', "projection":' + ('null' if self.projection is None else str(self.projection)) +  
			', "espn_projection":' + ('null' if self.espn_projection is None else str(self.espn_projection)) + 
			', "yahoo_projection":' + ('null' if self.yahoo_projection is None else str(self.yahoo_projection)) +
			', "cbs_projection":' + ('null' if self.cbs_projection is None else str(self.cbs_projection)) + 
			', "performance_score":' + ('null' if self.performance_score is None else str(self.performance_score)) + 
			', "data":' + str(self.data.id) + '} },' )

	def as_dict(self):
		return {
			"id": self.id,
			"player": self.player.as_dict(),
			"matchup": self.matchup.as_dict(),
			"projection": self.projection,
			"espn_projection": self.espn_projection,
			"yahoo_projection": self.yahoo_projection,
			"cbs_projection": self.cbs_projection,
			"performance_score": self.performance_score,
			"data": self.data.as_dict()
		}



	