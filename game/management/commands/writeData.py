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
		self.writeSeedData(Matchup, 2014, True)
		#self.writeDataAndPoints(GameData, 2014, True)
		#self.writeDataAndPoints(YearData, 2014, True)
		


	# Writes the data and corresponding DataPoints to JSON fixture-style files
	# Filename is ModelYYYY_timestamp or ModelPointsYYYY_timestamp, 
	#	where timestamp is current date and time (hour/minute)
	# If overwrite is set to True, will overwrite the default fixture files
	# Meant to be used with any of the data.models
	def writeDataAndPoints(self, dataModel, year, overwrite=False):
		dataFilename = ('data/fixtures/backups/' + dataModel.__name__ + 
			str(year) + '_' + time.strftime('%Y%m%d%H%M') + '.json')
		dataPointsFilename = ('data/fixtures/backups/' + dataModel.__name__ 
			+ 'Points' + str(year) + '_' + time.strftime('%Y%m%d%H%M') + '.json')
		dataFile = open(dataFilename, 'w')
		dataPointsFile = open(dataPointsFilename, 'w')

		dataFile.write('[\n')
		dataPointsFile.write('[\n')

		print 'writing data'

		# TODO: uncomment line for YearData
		#dataList = dataModel.objects.filter(year=year).order_by('id')
		dataList = dataModel.objects.filter(matchup__year=year).order_by('id')
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

		print 'done writing data'

		if overwrite:
			print 'overwriting default files'
			originalFile = open(dataFilename)
			overwriteFile = open('data/fixtures/' + dataModel.__name__ + str(year) + '.json', 'w')
			overwriteFile.writelines([line for line in originalFile])
			originalFile.close()
			overwriteFile.close()

			originalPointsFile = open(dataPointsFilename)
			overwritePointsFile = open('data/fixtures/' + dataModel.__name__ + 
				'Points' + str(year) + '.json', 'w')
			overwritePointsFile.writelines([line for line in originalPointsFile])
			originalPointsFile.close()
			overwritePointsFile.close()


	# Writes the seed data to JSON fixture-style files for the given model
	# Filename is ModelYYYY_timestamp, 
	#	where timestamp is current date and time (hour/minute)
	# Meant to be used with any of the game.models
	def writeSeedData(self, dataModel, year, overwrite=False):
		outFilename = ('game/fixtures/backups/' + dataModel.__name__ + 
			str(year) + '_' + time.strftime('%Y%m%d%H%M') + '.json')
		outFile = open(outFilename, 'w')
		outFile.write('[\n')

		# TODO: uncomment line for Matchup
		dataList = dataModel.objects.filter(year=year).order_by('week_number', 'id')
		#dataList = dataModel.objects.all().order_by('id')
		for d in dataList:
			outFile.write(d.fixtureString() + '\n')

		# Get rid of the final comma and add the closing bracket
		outFile.seek(-2, os.SEEK_END)
		outFile.truncate()
		outFile.write('\n]')
		outFile.close()

		if overwrite:
			print 'overwriting'
			originalFile = open(outFilename)
			overwriteFile = open('game/fixtures/' + dataModel.__name__ + str(year) + '.json', 'w')
			overwriteFile.writelines([line for line in originalFile])

		





