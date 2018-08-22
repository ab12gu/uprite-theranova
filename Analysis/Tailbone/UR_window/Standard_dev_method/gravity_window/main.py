#
# filename: main.py
# by: Abhay Gupta
#
# Description: Find gravity windows from UR data
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
p = os.path.abspath('../') # add parent folder for window function
sys.path.append(p)
from custom_functions import *
from window import *

# Change plot line width
plt.rcParams['lines.linewidth'] = 0.5

# Directories
input_directory = root + '/AG_Parsed_Data/Structs'
RS_directory =  root + '/AG_Parsed_Data/RS'
output_directory = root + '/AG_parsed_Data/UR/Accel/test/'

start_time = clocktime.time()
pace = ['S', 'C', 'F']
coordinates = ['x', 'y', 'z']
counter = 0

# Iterate trough every patient file
for c, filename in enumerate(os.listdir(input_directory)):
	if c < 39:
		continue

	patient_number = filename.split('.')[0]
	print("Extracting data for patient:", patient_number)
	print("Current Patient iteration:", c)

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
	
	# Find the gravity vector....
	gravity = all_low_stdev(accel_data['z'], threshold, size)
	gravity = gravity['steady']		
	gravity.sort(key=lambda x: x[2])
	check = 0
	
	while(check == 0):	
		plt.plot(accel_data['z'])
		plt.axvspan(gravity[-1][0], gravity[-1][1], color = 'blue', alpha = 0.5)
		plt.show(block = False)
		
		# Ask user if this is appropriate start window 
		check = int(input("Enter 1 for perfect_cut: "))	
		if check == 1:
			window = [gravity[-1][0], gravity[-1][1]]
		else:
			gravity = gravity[:-1]
		plt.close()

	with open(os.path.join(output_directory, filename), 'wb') as afile:
		pickle.dump(window, afile)


print('Successful run!') 
print('-----------RUNTIME: %s second ----' % (clocktime.time() - start_time))
