from django.db import models

# PK FORMAT:
# pxxxx
# p = position: QB=1, RB=2, WR=3, TE=4, D/ST=5, K=6
# xxxx = random 4 digits
class Player(models.Model):
	name = models.CharField(max_length=200)
	height = models.IntegerField() # height in inches
	weight = models.IntegerField() # weight in lbs
	dob = models.DateField('Date of Birth')
	team = models.ForeignKey('Team')
	position = models.ForeignKey('Position')
	depth_position = models.IntegerField(null=True)
	number = models.IntegerField()
	espn_id = models.IntegerField()

	def __unicode__(self):
		return self.name

	def as_dict(self):
		return {
			"id": self.id,
			"name": self.name,
			"height": self.height,
			"weight": self.weight,
			"dob": str(self.dob),
			"team": self.team.as_dict(),
			"position": self.position.as_dict(),
			"depth_position": self.depth_position,
			"number": self.number,
			"espn_id": self.espn_id
		}

class Position(models.Model):
	# Primary keys: QB=1, RB=2, WR=3, TE=4, D/ST=5, K=6
	name = models.CharField(max_length=200)
	abbr = models.CharField(max_length=200)

	def __unicode__(self):
		return self.name

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

	name = models.CharField(max_length=200)
	espn_id = models.IntegerField()
	abbr = models.CharField(max_length=200)
	stadium = models.CharField(max_length=200)
	division = models.CharField(max_length=200, null=True)

	def __unicode__(self):
		return self.name

	def as_dict(self):
		return {
			"id": self.id,
			"name": self.name,
			"espn_id": self.espn_id,
			"abbr": self.abbr,
			"stadium": self.stadium
		}
