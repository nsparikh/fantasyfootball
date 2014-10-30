from django.db import models


# PK FORMAT:
# pppppyyww
# ppppp = 5-digit player PK
# yy = 2-digit year
# ww = 2-digit week number (00=YearData, 99=CareerData)
# ** BLANK DATA: pk=0; ALL 0 DATA: pk=100 **
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
	miscTDs = models.IntegerField(null=True) # Return TDs

	# Bonus Points
	bonus40YdPassTDs = models.IntegerField(null=True)
	bonus40YdRushTDs = models.IntegerField(null=True)
	bonus40YdRecTDs = models.IntegerField(null=True)

	# Kicker stats
	fg0_19 = models.IntegerField(null=True)
	fg20_29 = models.IntegerField(null=True)
	fg30_39 = models.IntegerField(null=True)
	fg40_49 = models.IntegerField(null=True)
	fg50 = models.IntegerField(null=True)
	fgMissed = models.IntegerField(null=True)
	pat = models.IntegerField(null=True)

	# D/ST stats
	dstTDs = models.IntegerField(null=True)
	dstInt = models.IntegerField(null=True)
	dstFumlRec = models.IntegerField(null=True)
	dstBlockedKicks = models.IntegerField(null=True)
	dstSafeties = models.IntegerField(null=True)
	dstSacks = models.IntegerField(null=True)
	dstPtsAllowed = models.IntegerField(null=True)

	# Total fantasy points
	points = models.IntegerField(null=True)

	def __unicode__(self):
		return str(self.id)

	def fixtureString(self):
		return ( '{ ' + '"model":"data.DataPoint", "pk":' + str(self.id) + 
			', "fields":{"passC":' + ('null' if self.passC is None else str(self.passC)) +
			', "passA":' + ('null' if self.passA is None else str(self.passA)) +
			', "passYds":' + ('null' if self.passYds is None else str(self.passYds)) +
			', "passTDs":' + ('null' if self.passTDs is None else str(self.passTDs)) +
			', "passInt":' + ('null' if self.passInt is None else str(self.passInt)) +
			', "rush":' + ('null' if self.rush is None else str(self.rush)) +
			', "rushYds":' + ('null' if self.rushYds is None else str(self.rushYds)) +
			', "rushTDs":' + ('null' if self.rushTDs is None else str(self.rushTDs)) +
			', "rec":' + ('null' if self.rec is None else str(self.rec)) +
			', "recYds":' + ('null' if self.recYds is None else str(self.recYds)) +
			', "recTDs":' + ('null' if self.recTDs is None else str(self.recTDs)) +
			', "recTar":' + ('null' if self.recTar is None else str(self.recTar)) +
			', "misc2pc":' + ('null' if self.misc2pc is None else str(self.misc2pc)) +
			', "miscFuml":' + ('null' if self.miscFuml is None else str(self.miscFuml)) +
			', "miscTDs":' + ('null' if self.miscTDs is None else str(self.miscTDs)) +
			', "bonus40YdPassTDs":' + ('null' if self.bonus40YdPassTDs is None else str(self.bonus40YdPassTDs)) +
			', "bonus40YdRushTDs":' + ('null' if self.bonus40YdRushTDs is None else str(self.bonus40YdRushTDs)) +
			', "bonus40YdRecTDs":' + ('null' if self.bonus40YdRecTDs is None else str(self.bonus40YdRecTDs)) +
			', "fg0_19":' + ('null' if self.fg0_19 is None else str(self.fg0_19)) +
			', "fg20_29":' + ('null' if self.fg20_29 is None else str(self.fg20_29)) +
			', "fg30_39":' + ('null' if self.fg30_39 is None else str(self.fg30_39)) +
			', "fg40_49":' + ('null' if self.fg40_49 is None else str(self.fg40_49)) +
			', "fg50":' + ('null' if self.fg50 is None else str(self.fg50)) +
			', "fgMissed":' + ('null' if self.fgMissed is None else str(self.fgMissed)) +
			', "pat":' + ('null' if self.pat is None else str(self.pat)) +
			', "dstTDs":' + ('null' if self.dstTDs is None else str(self.dstTDs)) +
			', "dstInt":' + ('null' if self.dstInt is None else str(self.dstInt)) +
			', "dstFumlRec":' + ('null' if self.dstFumlRec is None else str(self.dstFumlRec)) +
			', "dstBlockedKicks":' + ('null' if self.dstBlockedKicks is None else str(self.dstBlockedKicks)) +
			', "dstSafeties":' + ('null' if self.dstSafeties is None else str(self.dstSafeties)) +
			', "dstSacks":' + ('null' if self.dstSacks is None else str(self.dstSacks)) +
			', "dstPtsAllowed":' + ('null' if self.dstPtsAllowed is None else str(self.dstPtsAllowed)) +
			', "points":' + ('null' if self.points is None else str(self.points)) + '} },' )

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
			"bonus40YdPassTDs": self.bonus40YdPassTDs,
			"bonus40YdRushTDs": self.bonus40YdRushTDs,
			"bonus40YdRecTDs": self.bonus40YdRecTDs,
			"fg0_19": self.fg0_19,
			"fg20_29": self.fg20_29,
			"fg30_39": self.fg30_39,
			"fg40_49": self.fg40_49,
			"fg50": self.fg50,
			"fgMissed": self.fgMissed,
			"pat": self.pat,
			"dstTDs": self.dstTDs,
			"dstInt": self.dstInt,
			"dstFumlRec": self.dstFumlRec,
			"dstBlockedKicks": self.dstBlockedKicks,
			"dstSafeties": self.dstSafeties,
			"dstSacks": self.dstSacks,
			"dstPtsAllowed": self.dstPtsAllowed,
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



	