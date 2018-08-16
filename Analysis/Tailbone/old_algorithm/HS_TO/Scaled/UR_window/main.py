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
plt.rcParams['lines.linewidth'] = 0.5  
import time as clocktime
from numpy.linalg import inv
from copy import deepcopy

# Custom function imports
import filt
p = os.path.abspath('../../../Python/')
sys.path.append(p) # used for importing custom functions
from math_func import my_round
p = os.path.abspath('../../../../../../Data/Parsing Program/')
sys.path.append(p) 
from custom_functions import *
import print_struct as visual
import reference_check as dif

# Change plot line width
plt.rcParams['lines.linewidth'] = 0.5

# Directories
input_directory = '../../../../../../../AG_Parsed_Data/Structs'
RS_directory =  '../../../../../../../AG_Parsed_Data/RS'
output_directory = '../../../../../../../AG_parsed_Data/UR'

start_time = clocktime.time()
# Iterate trough every patient file
for c, filename in enumerate(os.listdir(input_directory)):
	
	patient_number = filename.split('.')[0]
	print("Extracting data for patient:", patient_number)

	"""Extract Pickle Data"""
	# open file	
	pickle_file = os.path.join(input_directory, filename)
	RS_pickle_file = os.path.join(RS_directory, filename)
	with open(pickle_file, 'rb') as afile:
		data = pickle.load(afile)
	with open(RS_pickle_file, 'rb') as afile:
		RS_data = pickle.load(afile)

	# Check flags if there is no data
	accel_flag = data['Flags']['tailBone']['accel']
	gyro_flag = data['Flags']['tailBone']['gyro']
	if (accel_flag == 0 or gyro_flag == 0):
		print('No data recorded in patient:', patient_number)
		continue

	#visual.print_keys(RS_data,10)
	padding = 0 # in seconds
	interval, len_RS, len_UR, window, offset = \
		dif.extract(data, RS_data, padding)
	pace = ['S', 'C', 'F']
	for w in pace: 
		interval[w] = [my_round(x*100) for x in interval[w]]

	"""Extract HS & TO for uprite system"""
	
	"""First find all Troughs"""
	# extract only raw tailbone data
	accel_data = data['UR']['sensorData']['tailBone']['accel']['data']
	gyro_data = data['UR']['sensorData']['tailBone']['gyro']['data']

	#plt.plot(accel_data['z'])
	#plt.show()
	# data starts a 0; therefore first few points are garbage
	accel_data['x'] = accel_data['x'][4:]
	accel_data['x'] = accel_data['x'][4:]
	accel_data['x'] = accel_data['x'][4:]

	gyro_data['x'] = gyro_data['x'][4:]
	gyro_data['x'] = gyro_data['y'][4:]
	gyro_data['z'] = gyro_data['z'][4:]
	
	# Get gravity by putting low acceleration trough low pass filter...
	f_cuts = [0.1/50, 0.7/50] # Passband & Stopband cutoffs
	fs = 100
	rip_tol = [0.001, 0.1]

	gravity_from_accel = {}
	gravity_from_accel['x'] = filt.lowpass(accel_data['x'], f_cuts, fs, rip_tol)
	gravity_from_accel['y'] = filt.lowpass(accel_data['y'], f_cuts, fs, rip_tol)
	gravity_from_accel['z'] = filt.lowpass(accel_data['z'], f_cuts, fs, rip_tol)

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
		#plt.title('Recorded Time |' + 'RS:' + str(len_RS) + 'UR:' + \
				#				str(len_UR))	
		plt.show(block=True)










	head = []
	with open(os.path.join(output_directory, filename), 'wb') as afile:
		pickle.dump(head, afile)














print('Successful run!') 
print('-----------RUNTIME: %s second ----' % (clocktime.time() - start_time))
