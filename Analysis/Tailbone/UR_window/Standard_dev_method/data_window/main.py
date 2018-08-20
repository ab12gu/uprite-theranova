#
# filename: main.py
# by: Abhay Gupta
#
# Description: Find windows of relevant recorded data from UR based on RS data
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
root = str(Path(os.path.abspath(__file__)).parents[6]) # Create a root directory
p = os.path.abspath(root + '/uprite_analysis/') # for custom functions
sys.path.append(p)
from custom_functions import *
from window import *

# Change plot line width
plt.rcParams['lines.linewidth'] = 0.5

# Directories
input_directory = root + '/AG_Parsed_Data/Structs'
RS_directory =  root + '/AG_Parsed_Data/RS'
output_directory = root + '/AG_parsed_Data/UR/Accel/data_windows'

start_time = clocktime.time()
pace = ['S', 'C', 'F']
coordinates = ['x', 'y', 'z']

# Iterate trough every patient file
for c, filename in enumerate(os.listdir(input_directory)):
	
	patient_number = filename.split('.')[0]
	print("Extracting data for patient:", patient_number)

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
	interval = datestamp(data, RS_data)
	for w in pace: 
		interval[w] = [my_round(x*100) for x in interval[w]]
	
	window = {}
	# Ask user if values are window is accurate and record (forward time)
	for c, w in enumerate(pace):
		for d in coordinates:
			plt.plot(accel_data[d])
			plt.axvline(interval[w][0], color = 'g', linewidth = 3)
			plt.axvline(interval[w][1], color = 'g', linewidth = 3)
			shade = ['blue', 'blue']
			shade2 = ['red', 'red']
			for i in range(0, len(intervals[d]['unsteady'])):
				plt.axvspan(intervals[d]['unsteady'][i][0], \
					intervals[d]['unsteady'][i][1], \
					color = shade[i % 2], alpha = 0.1)
			for i in range(0, len(intervals[d]['steady'])):
				plt.axvspan(intervals[d]['steady'][i][0], \
					intervals[d]['steady'][i][1], \
					color = shade2[i % 2], alpha = 0.1)
			
			# Compare unsteady data to window size
			# Cutt of all data less than 3/4ths, then start from leftmost.
			# Plot only cuts that are 3/4ths length

			# Next window uses previous window into account
			max_inv = 0
			index = 0
			for i, x in enumerate(intervals[d]['unsteady']):
				temp = abs(x[2] - interval[w][2])
				print(x[0], x[1], x[2], interval[w][2], temp)				
				
				if ((1/temp) > max_inv):
					max_inv = 1/temp
					index = i
			
			plt.axvspan(intervals[d]['unsteady'][index][0], \
					intervals[d]['unsteady'][index][1], color='y', linewidth=3)
		
			
			indices = [1, 1]	
			plt.show()			
			window['forward'] = indices	
			

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
		#plt.title('Recorded Time |' + 'RS:' + str(len_RS) + 'UR:' + \
				#				str(len_UR))	
		plt.show(block=True)










	head = []
	with open(os.path.join(output_directory, filename), 'wb') as afile:
		pickle.dump(head, afile)














print('Successful run!') 
print('-----------RUNTIME: %s second ----' % (clocktime.time() - start_time))
