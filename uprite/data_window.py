####
# filename: data_window.py
# by: Abhay Gupta
#
# Description: Find windows of relevant recorded data from UR based on zeno data
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
from utils.directory_functions.mkdir_path import mkdir_path 

# Change plot line width
plt.rcParams['lines.linewidth'] = 0.5

def extract(directory):
	"""find relevant data windows from uprite sensor based on zeno data"""

	start_time = clocktime.time()
	pace = ['S', 'C', 'F']
	coordinates = ['x', 'y', 'z']

	patient_number = directory[-6:]
	print("Extracting data for patient:", patient_number)

	"""Extract Pickle Data"""
	# open file	all data, and reference system HS_TO data
	pickle_file = os.path.join(directory, 'python_struct.pkl')
	zeno_pickle_file = os.path.join(directory, 'zeno_hs_to.pkl')
	with open(pickle_file, 'rb') as afile: 
		data = pickle.load(afile) # Import all data
	with open(zeno_pickle_file, 'rb') as afile:
		zeno_data = pickle.load(afile) # Import zeno_TO_HS data

	# Check flags if there is no data
	accel_flag = data['Flags']['tailBone']['accel']
	gyro_flag = data['Flags']['tailBone']['gyro']
	if (accel_flag == 0):
		print('No data recorded in patient:', patient_number)
		return

	"""Find Windows of data"""
	# extract only raw tailbone data
	accel_data = data['UR']['sensorData']['tailBone']['accel']['data']

	# Calculate ranges of appropriate gravity vector
	threshold = 0.03 # Maximum allowable standard deviation
	size = 100
	intervals = {}
	plot = 0

	for w in coordinates:
		intervals[w] = all_low_stdev(accel_data[w], threshold, size)

		# Interval Analysis:
		if (plot == 1):
			shade = ['blue', 'blue']
			shade2 = ['red', 'red']
			plt.figure(dpi = 300)
			plt.plot(accel_data['x'])
			for i in range(0, len(intervals[w]['unsteady'])):
				plt.axvspan(intervals[w]['unsteady'][i][0], \
					intervals[w]['unsteady'][i][1], \
					color = shade[i % 2], alpha = 0.5)
			for i in range(0, len(intervals[w]['steady'])):
				plt.axvspan(intervals[w]['steady'][i][0], \
					intervals[w]['steady'][i][1], \
					color = shade2[i % 2], alpha = 0.5)
			plt.show()

	# Find start-time through datestamp comparision
	zeno_wind = datestamp(data, zeno_data)
	for w in pace: 
		zeno_wind[w] = [my_round(x*100) for x in zeno_wind[w]]
	
	# Initialize some data
	window = {}
	check = 0
	prev_max = math.inf

	# Ask user if values are window is accurate and record data
	while(check == 0):
	
		# Direction and Pace are held constant
		w = 'S'
		d = 'x'
	
		# Plot the dataset
		plt.figure()
		plt.plot(accel_data[d])

		# Plot the zeno datestamp calculated placement
		plt.axvline(zeno_wind[w][0], color = 'g', linewidth = 3)
		plt.axvline(zeno_wind[w][1], color = 'g', linewidth = 3)

		# Shade the steady and unsteady sections of data
		for i in range(0, len(intervals[d]['unsteady'])):
			plt.axvspan(intervals[d]['unsteady'][i][0], \
				intervals[d]['unsteady'][i][1], \
				color = 'red', alpha = 0.1)
		for i in range(0, len(intervals[d]['steady'])):
			plt.axvspan(intervals[d]['steady'][i][0], \
				intervals[d]['steady'][i][1], \
				color = 'blue', alpha = 0.1)
		
		# Slow Window:
		# Calculate unsteady span closest to zeno span
		max_inv = 0
		index = 0
		for i, x in enumerate(intervals[d]['unsteady']):
			temp = abs(x[2] - zeno_wind[w][2]) # Compare span of windows
			if (prev_max > 1/temp > max_inv):
				max_inv = 1/temp
				index = i
		prev_max = max_inv
		
		# Save & plot the window
		slow_window = intervals[d]['unsteady'][index]
		start = slow_window[0]
		end = slow_window[1]
		span = end - start
		if (span < zeno_wind[w][2]):
			center = (start + end)/2
			start = center - zeno_wind[w][2]/2
			end = center + zeno_wind[w][2]/2
		plt.axvspan(start, end, color='y', linewidth=3)
		window['S'] = [my_round(start), my_round(end)]
		
		# Use zeno datestamp to find Calm & Fast windows.	
		# Calm window:	
		start = (zeno_wind['C'][0] - zeno_wind['S'][1]) + slow_window[1]+150
		end = (zeno_wind['C'][1] - zeno_wind['S'][1]) + slow_window[1]+150
		start, end = search([start, end], intervals[d]['unsteady'])
		plt.axvspan(start, end, color='lime', linewidth=3)
		window['C'] = [start, end]	

		# Fast Window:
		start = (zeno_wind['F'][0] - zeno_wind['S'][1]) + slow_window[1]+150
		end = (zeno_wind['F'][1] - zeno_wind['S'][1]) + slow_window[1]+150		
		start, end = search([start, end], intervals[d]['unsteady'])
		plt.axvspan(start, end, color='lime', linewidth=3)
		window['F'] = [start, end]
		plt.title('accel x')

		indices = [start, end]	
		plt.show(block = False)			
		
		# Ask user if this is appropriate start window 
		skip = int(input("Enter 1 for perfect_cut: "))	
		if skip == 1:
			check = 1
			window['flag'] = {}
			window['flag']['auto'] = 1
			window['flag']['S'] = 1
			window['flag']['C'] = 1
			window['flag']['F'] = 1
			continue

		check = int(input("Enter 0 if first window should be recalculated (else 1): "))
		if check == 0:
			continue
		
		window['flag'] = {}
		window['flag']['auto'] =int(input("Enter 0 if algorithm isn't working (else 1): "))
		window['flag']['S'] = int(input("Enter 0 if no slow data (else 1): "))
		window['flag']['C'] = int(input("Enter 0 if no calm data (else 1): "))
		window['flag']['F'] = int(input("Enter 0 if no fast data (else 1): "))
	
	with open(os.path.join(directory, 'data_window.pkl'), 'wb') as afile:
		pickle.dump(window, afile)

	# save plots of files

	if window['flag']['F'] == 0:
		return

	speed = ['slow', 'calm', 'fast']
	home = '../../figures/tailbone/' 
	home = os.path.join(home, patient_number)

	output = os.path.join(home, 'accel_window.pdf')
	plt.savefig(output)
	plt.close()

	gyro_data = data['UR']['sensorData']['tailBone']['gyro']['data']

	for c,p in enumerate(pace):
		output_dir = os.path.join(home, speed[c])
		mkdir_path(output_dir)
		plt.close('all')

		plt.plot(accel_data['x'][window[p][0]:window[p][1]])
		plt.plot(accel_data['y'][window[p][0]:window[p][1]])
		plt.plot(accel_data['z'][window[p][0]:window[p][1]])
		plt.legend(['x', 'y', 'z'])

		output = os.path.join(output_dir, 'accel_data.pdf')
		plt.savefig(output)
		plt.close()

		plt.plot(gyro_data['x'][window[p][0]:window[p][1]])
		plt.plot(gyro_data['y'][window[p][0]:window[p][1]])
		plt.plot(gyro_data['z'][window[p][0]:window[p][1]])
		plt.legend(['x', 'y', 'z'])

		output = os.path.join(output_dir, 'gyro_data.pdf')
		plt.savefig(output)
		plt.close()


	print('Successful run!') 
	print('-----------RUNTIME: %s second ----' % (clocktime.time() - start_time))

def input_check(directory, folder_type):
	"""Check input folder type"""

	if (folder_type == 'n'):
		extract(directory)
	else:
		start_time = clocktime.time()
		# Iterate trough every patient file
		for c, filename in enumerate(os.listdir(directory)):
			if c > 2:
				continue
			if (filename == '.DS_Store'):
				continue

			print("Current Patient iteration:", c)
			afile = os.path.join(directory, filename)
			extract(afile)

		print('Successful run!') 
		print('-----------RUNTIME: %s second ----' % (clocktime.time() - start_time))


if __name__ == '__main__':
	print("Skipping gui... running directly")

	directory = '../../data_files/analyzed_data'
	folder_type = 'y'
	#directory = '../../data_files/analyzed_data/no_003'
	#folder_type = 'n'

	input_check(directory, folder_type)

