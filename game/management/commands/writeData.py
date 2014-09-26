from django.db.models import Count, Avg, Sum, Q

from game.models import Player, Position, Team, Matchup
from data.models import YearData, GameData, DataPoint

from django.core.management.base import NoArgsCommand, make_option

import time
import os

class Command(NoArgsCommand):

	help = ''

	option_list = NoArgsCommand.option_list + (
		make_option('--verbose', action='store_true'),
	)

	def handle_noargs(self, **options):
		# Write what we want to do here
		self.writeDataAndPoints(YearData, 2014)
		#self.writeSeedData(Matchup, 2013)


	# Writes the data and corresponding DataPoints to JSON fixture-style files
	# Filename is ModelYYYY_timestamp or ModelPointsYYYY_timestamp, 
	#	where timestamp is current date and time (hour/minute)
	# Meant to be used with any of the data.models
	def writeDataAndPoints(self, dataModel, year):
		dataFile = open('data/fixtures/backups/' + dataModel.__name__ + 
			str(year) + '_' + time.strftime('%Y%m%d%H%M') + '.json', 'w')
		dataPointsFile = open('data/fixtures/backups/' + dataModel.__name__ 
			+ 'Points' + str(year) + '_' + time.strftime('%Y%m%d%H%M') + 
			'.json', 'w')

		dataFile.write('[\n')
		dataPointsFile.write('[\n')

		dataList = dataModel.objects.filter(year=year).order_by('player', 'id')
		#dataList = dataModel.objects.filter(matchup__year=year).order_by('player', 'matchup__week_number')
		for d in dataList:
			dataFile.write(d.fixtureString() + '\n')
			if d.data.id > 1: dataPointsFile.write(d.data.fixtureString() + '\n')

		# Get rid of the final commas
		dataFile.seek(-2, os.SEEK_END)
		dataFile.truncate()
		dataPointsFile.seek(-2, os.SEEK_END)
		dataPointsFile.truncate()

		dataFile.write('\n]')
		dataPointsFile.write('\n]')
		dataFile.close()
		dataPointsFile.close()

	# Writes the seed data to JSON fixture-style files for the given model
	# Filename is ModelYYYY_timestamp, 
	#	where timestamp is current date and time (hour/minute)
	# Meant to be used with any of the game.models
	def writeSeedData(self, dataModel, year):
		outFile = open('game/fixtures/backups/' + dataModel.__name__ + 
			str(year) + '_' + time.strftime('%Y%m%d%H%M') + '.json', 'w')
		outFile.write('[\n')

		dataList = dataModel.objects.filter(year=year).order_by('id')
		#dataList = dataModel.objects.all().order_by('id')
		for d in dataList:
			outFile.write(d.fixtureString() + '\n')

		# Get rid of the final comma and add the closing bracket
		outFile.seek(-2, os.SEEK_END)
		outFile.truncate()
		outFile.write('\n]')
		outFile.close()





