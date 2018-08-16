# Filename: ifempty.py
# By: Abhay Gupta
#
# Description: Checks UR data if any empty data
# ... records the amount of time recordeed for UR data in csv file
# ... and adds flag to pickle data file to state whether data is empty
#

import sys
import os

p = os.path.abspath('../../Data/Parsing Program/')
sys.path.append(p)

import print_struct as visual
import pickle
import csv

input_directory = '../../../AG_Parsed_Data/Structs'


sensor_loc = ['leftAnkle', 'leftHip', 'rightAnkle', 'rightHip', 'tailBone']
abbrev = ['LA', 'LH', 'RA', 'RH', 'TB']
sensor_type = ['accel', 'gyro']
pat = ['Patient Name']

from itertools import product
header_names =  pat + list(map(''.join, product(abbrev,[' '],sensor_type))) 
print(header_names)


top = ['Presents the amount of recorded time per patient (in seconds) by UpRite Sensors']

with open('data_check.csv', 'w') as csvfile:
	begin = csv.writer(csvfile)
	begin.writerow(top)

	for i in range(0,5):
		begin.writerow({abbrev[i] + '='+ sensor_loc[i]})
	for i in range(0,2):
		begin.writerow('')
	
with open('data_check.csv', 'a') as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames = header_names)

	writer.writeheader()
	for c, filename in enumerate(os.listdir(input_directory)):

		"""Extract Pickle Data"""
		pickle_file = input_directory + '/' +  filename 
		with open(pickle_file, 'rb') as afile:
			data = pickle.load(afile)

		"""Find if data is empty"""
		
		# Initialize values 
		check_data = data['UR']['sensorData']
		filename = filename.split('.', 1)[0]
		output = {}
		data['Flags'] = {}
		counter = 0
		
		print('Checking file ', filename)

		for i in range(0,len(sensor_loc)):
			data['Flags'][sensor_loc[i]] = {}
			
			for j in range(0,len(sensor_type)):
				data['Flags'][sensor_loc[i]][sensor_type[j]] = {}
				
				if sensor_loc[i] in check_data:	
					check = check_data[sensor_loc[i]][sensor_type[j]]['data']['x']
					if not check: #if empty
						out = None
						check = 0
					else: #if not empty
						out = len(check)/100
						check = 1
				else:
					out = 'None'
					check = 0
				
				data['Flags'][sensor_loc[i]][sensor_type[j]] = check
				output[counter] = str(out)
				counter += 1
			
		out = {pat[0]: filename}
		for n in range(0,counter):
			out[header_names[n+1]] = output[n]

		writer.writerow(out)

		with open(pickle_file, 'wb') as afile:
			pickle.dump(data , afile)

		# Check if file really has flags added...
		with open(pickle_file, 'rb') as afile:
				data = pickle.load(afile)
		visual.print_keys(data, 9)
