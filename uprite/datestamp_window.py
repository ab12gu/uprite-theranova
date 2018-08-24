#
# filename: main.py
# by: Abhay Gupta
#
# Description: Scale the original GC's TO-HS uprite analysis to all patients 
#

# Library imports
import sys
import os
import pickle
import csv
import statistics as stats
import math
import matplotlib.pyplot as plt
import time as clocktime
from numpy.linalg import inv
from copy import deepcopy

# Custom function imports
from utils.math_functions.general_math import my_round
from utils.visualize_structure import visualize_structure as visual
from utils.compare_data.compare_log import extract as compare

# Change plot line width
plt.rcParams['lines.linewidth'] = 0.5

def extract(directory):
	"""Create data windows on uprite data based on time recorded on zeno walkway"""

	start_time = clocktime.time()
	# Iterate trough every patient file
		
	patient_number = directory[-6:]
	print("Extracting data for patient:", patient_number)

	"""Extract Pickle Data"""
	# open file	
	uprite_pickle_file = os.path.join(directory, 'uprite_hs_to.pkl')
	zeno_pickle_file = os.path.join(directory, 'zeno_hs_to.pkl')
	with open(uprite_pickle_file, 'rb') as afile:
		data = pickle.load(afile)
	with open(zeno_pickle_file, 'rb') as afile:
		zeno_data = pickle.load(afile)

	# Check flags if there is no data
	accel_flag = data['Flags']['tailBone']['accel']
	gyro_flag = data['Flags']['tailBone']['gyro']
	if (accel_flag == 0 or gyro_flag == 0):
		print('No data recorded in patient:', patient_number)
		return

	#visual.print_keys(zeno_data,10)
	padding = 0 # in seconds
	interval, len_zeno, len_UR, window, offset = \
		compare(data, zeno_data, padding)
	pace = ['S', 'C', 'F']
	for w in pace: 
		interval[w] = [my_round(x*100) for x in interval[w]]

	"""Extract HS & TO for uprite system"""
	
	"""First find all Troughs"""
	# extract only raw tailbone data
	accel_data = data['UR']['sensorData']['tailBone']['accel']['data']
	gyro_data = data['UR']['sensorData']['tailBone']['gyro']['data']

	# Change to only range of standing (where gravity is the only effect)

	if interval['S'][0] > 0 and interval['S'][1] > 0:
		fig = plt.figure(dpi = 300)
		plt.subplots_adjust(wspace = 0.5, hspace = 0.5)
		for c, w in enumerate(pace,1):
			plt.subplot(220+c )
			plt.plot(accel_data['x'][interval[w][0]:interval[w][1]])
			plt.plot(accel_data['y'][interval[w][0]:interval[w][1]])
			plt.plot(accel_data['z'][interval[w][0]:interval[w][1]])
			plt.title(window[c-1])
		plt.subplot(224)
		plt.plot(accel_data['x'])
		plt.plot(accel_data['y'])
		plt.plot(accel_data['z'])
		for w in pace:
			plt.axvline(interval[w][0], color = 'b', linestyle = '--')
			plt.axvline(interval[w][1], color = 'b', linestyle = '--')
		plt.axvline(offset*100, color = 'r', linestyle = '--')
		plt.axvline(interval['S'][0] +1600, color = 'r')	
		fig.suptitle(filename + ' || ' + str(offset))
		#plt.title('Recorded Time |' + 'zeno:' + str(len_zeno) + 'UR:' + str(len_UR))	
		plt.show(block=True)

	print('Successful run!') 
	print('-----------RUNTIME: %s second ----' % (clocktime.time() - start_time))

def input_check(directory, folder_type):
	"""check input folder type"""

	if (folder_type == 'n'):
		extract(directory)
	else:
		# iterate through folder
		start_time = clocktime.time()
		for c, filename in enumerate(os.listdir(directory)):
			if c < 0:
				continue
			if filename == '.DS_Store':
				continue

			print("Current patient iteration: ", c)
			afile = os.path.join(directory, filename)
			extract(afile)

		print('Successful run!') 
		print('-----------RUNTIME: %s second ----' % (clocktime.time() - start_time))



if __name__ == '__main__':
	print('Skipping GUI... running function directly')

	directory = '../../data_files/analyzed_data'
	folder_type = 'y'
	directory = '../../data_files/analyzed_data/no_003'
	folder_type = 'n'

	input_check(directory, folder_type)

	# Directories
	input_directory = '../../data_files/temp/Structs'
	zeno_directory =  '../../data_files/temp/zeno'
	output_directory = '../../data_files/temp/UR'



