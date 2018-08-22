#
# filename: main.py
# by: Abhay Gupta
#
# Description: Run GC's script on all UR data/gravity windows
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
from copy import deepcopy

# Custom function imports
from pathlib import Path
root = str(Path(os.path.abspath(__file__)).parents[5]) # Create a root directory
p = os.path.abspath(root + '/uprite_analysis/') # for custom functions
sys.path.append(p)
from custom_functions import *

# Change plot line width
plt.rcParams['lines.linewidth'] = 0.5

# Directories
start_time = clocktime.time()
input_directory = root + '/AG_parsed_data/Structs/'
gravity_input_dir = root + '/AG_Parsed_Data/UR/gravity_windows'
data_input_dir =  root + '/AG_Parsed_Data/UR/data_windows'
output_directory = root + '/AG_parsed_Data/UR/HS_TO/Direct_GC'

pace = ['S', 'C', 'F']
coordinates = ['x', 'y', 'z']
orientation = ['r', 'l']

# Iterate trough every patient file
for c, filename in enumerate(os.listdir(data_input_dir)):

	# Extract Patient Number
	patient_number = filename.split('.')[0]
	print("Extracting data for patient:", patient_number)
	print("Current Patient iteration:", c)
	
	# Open data_file, gravity_window, data_window
	data_file = os.path.join(input_directory, filename)
	data_window_file = os.path.join(data_input_dir, filename)
	gravity_window_file = os.path.join(gravity_input_dir, filename)
	with open(data_file, 'rb') as afile: 
		data = pickle.load(afile) # Import all patient data
	with open(data_window_file, 'rb') as afile:
		data_window = pickle.load(afile) # Import data windows
	with open(gravity_window_file, 'rb') as afile:
		gravity_window = pickle.load(afile) # Import gravity windows

	# Store gravity vector
	

	quit()

	"""Extract Pickle Data"""
	# open file	all data, and reference system HS_TO data
	pickle_file = os.path.join(input_directory, filename)
	RS_pickle_file = os.path.join(RS_directory, filename)
	with open(pickle_file, 'rb') as afile: 
		data = pickle.load(afile) # Import all data
	with open(RS_pickle_file, 'rb') as afile:
		RS_data = pickle.load(afile) # Import RS_TO_HS data

	# Check flags if there is no data
	accel_flag = data['Flags']['tailBone']['accel']
	gyro_flag = data['Flags']['tailBone']['gyro']
	if (accel_flag == 0):
		print('No data recorded in patient:', patient_number)
		continue

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
	RS_wind = datestamp(data, RS_data)
	for w in pace: 
		RS_wind[w] = [my_round(x*100) for x in RS_wind[w]]
	
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

		# Plot the RS datestamp calculated placement
		plt.axvline(RS_wind[w][0], color = 'g', linewidth = 3)
		plt.axvline(RS_wind[w][1], color = 'g', linewidth = 3)

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
		# Calculate unsteady span closest to RS span
		max_inv = 0
		index = 0
		for i, x in enumerate(intervals[d]['unsteady']):
			temp = abs(x[2] - RS_wind[w][2]) # Compare span of windows
			if (prev_max > 1/temp > max_inv):
				max_inv = 1/temp
				index = i
		prev_max = max_inv
		
		# Save & plot the window
		slow_window = intervals[d]['unsteady'][index]
		start = slow_window[0]
		end = slow_window[1]
		span = end - start
		if (span < RS_wind[w][2]):
			center = (start + end)/2
			start = center - RS_wind[w][2]/2
			end = center + RS_wind[w][2]/2
		plt.axvspan(start, end, color='y', linewidth=3)
		window['S'] = [start, end]
		
		# Use RS datestamp to find Calm & Fast windows.	
		# Calm window:	
		start = (RS_wind['C'][0] - RS_wind['S'][1]) + slow_window[1]+150
		end = (RS_wind['C'][1] - RS_wind['S'][1]) + slow_window[1]+150
		start, end = search([start, end], intervals[d]['unsteady'])
		plt.axvspan(start, end, color='lime', linewidth=3)
		window['C'] = [start, end]	

		# Fast Window:
		start = (RS_wind['F'][0] - RS_wind['S'][1]) + slow_window[1]+150
		end = (RS_wind['F'][1] - RS_wind['S'][1]) + slow_window[1]+150		
		start, end = search([start, end], intervals[d]['unsteady'])
		plt.axvspan(start, end, color='lime', linewidth=3)
		window['F'] = [start, end]

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
			counter += 1
			print(counter)
			continue

		check = int(input("Enter 0 if first window is wrong (else 1): "))
		if check == 0:
			continue
		
		window['flag'] = {}
		window['flag']['auto'] =int(input("Enter 0 if no auto data (else 1): "))
		if window['flag']['auto'] != 0:
			counter += 1	
			print(counter)
		window['flag']['S'] = int(input("Enter 0 if no slow data (else 1): "))
		window['flag']['C'] = int(input("Enter 0 if no calm data (else 1): "))
		window['flag']['F'] = int(input("Enter 0 if no fast data (else 1): "))
	
	with open(os.path.join(output_directory, filename), 'wb') as afile:
		pickle.dump(window, afile)

print('Successful run!') 
print('-----------RUNTIME: %s second ----' % (clocktime.time() - start_time))
