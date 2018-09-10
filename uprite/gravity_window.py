####
# filename: gravity_window.py
# by: Abhay Gupta
#
# Description: Find gravity windows from UR data
####

# Library imports
import sys
import os
import pickle
import csv
import statistics as stats
import math
import matplotlib.pyplot as plt
import time as clocktime
from copy import deepcopy

# Custom function imports
from utils.math_functions.general_math import my_round
from utils.signal_analysis.window import *

# Change plot line width
plt.rcParams['lines.linewidth'] = 0.5

def extract(directory):
	"""find gravity windows from uprite data"""

	start_time = clocktime.time()
	pace = ['S', 'C', 'F']
	coordinates = ['x', 'y', 'z']
	counter = 0

	patient_number = directory[-6:]
	print("Extracting data for patient:", patient_number)

	# open file	all data, and reference system HS_TO data
	uprite_pickle_file = os.path.join(directory, 'python_struct.pkl')
	with open(uprite_pickle_file, 'rb') as afile: 
		data = pickle.load(afile) # Import all data

	# Check flags if there is no data
	accel_flag = data['Flags']['tailBone']['accel']
	if (accel_flag == 0):
		print('No data recorded in patient:', patient_number)
		return

	# find Windows of data
	# extract only raw tailbone data
	accel_data = data['UR']['sensorData']['tailBone']['accel']['data']

	# Calculate ranges of appropriate gravity vector
	threshold = 0.03 # Maximum allowable standard deviation
	size = 100
	intervals = {}
	plot = 0
	
	# Find the gravity vector....
	gravity = all_low_stdev(accel_data['z'], threshold, size)
	gravity = gravity['steady']		
	gravity.sort(key=lambda x: x[2])
	check = 0
	
	while(check == 0):	
		plt.close()
		plt.plot(accel_data['z'])
		plt.axvspan(gravity[-1][0], gravity[-1][1], color = 'blue', alpha = 0.5)
		plt.title('accel z')
		plt.show(block = False)
		
		# Ask user if this is appropriate start window 
		check = int(input("Enter 1 for perfect_cut: "))	
		if check == 1:
			window = [gravity[-1][0], gravity[-1][1]]
		else:
			gravity = gravity[:-1]

	with open(os.path.join(directory, 'gravity_window.pkl'), 'wb') as afile:
		pickle.dump(window, afile)

	# save plot 

	home = '../../figures/tailbone/' 
	home = os.path.join(home, patient_number)

	output = os.path.join(home, 'accel_gravity_window.pdf')
	plt.savefig(output)
	plt.close()

	print('Successful run!') 
	print('-----------RUNTIME: %s second ----' % (clocktime.time() - start_time))

def input_check(directory, folder_type):
	"""Check input folder type"""

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

if __name__ == '__main__':
	print('Skipping GUI... running function directly')

	directory = '../../data_files/analyzed_data'
	folder_type = 'y'
	directory = '../../data_files/analyzed_data/no_003'
	folder_type = 'n'

	input_check(directory, folder_type)

