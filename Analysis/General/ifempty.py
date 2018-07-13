# Filename: ifempty.py
# By: Abhay Gupta
#
#
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
		
		print('counter', c)
		print(filename)
		"""Extract Pickle Data"""
		pickle_file = input_directory + '/' +  filename 
		with  open(pickle_file, 'rb') as filename:
			data = pickle.load(filename)

		"""Find if data is empty"""

		
		#visual.print_keys(data, 9)

		# Need to do it from here to see 
		check_data = data['UR']['sensorData']

		
		filename = filename.split('.', 1)[0]
		output = {}
		data['Flags'] = {}
		print(filename)
		counter = 0

		for i in range(0,5):
			data['Flags'][sensor_loc[i]] = {}
			for j in range(0,2):
				
				if sensor_loc[i] in check_data:	
					check = check_data[sensor_loc[i]][sensor_type[j]]['data']['x']
					if not check: #if empty
						out = 'None'
						check = 0
					else: #if not empty
						out = str(len(check)/100)
						check = 1
				else:
					out = 'None'
					check = 0
					
				data['Flags'] = {sensor_loc[i] : {sensor_type[j] : check}}
				output[counter] = out
				counter += 1
			
		out = {pat[0]: filename}
		for n in range(0,counter):
			out[header_names[n+1]] = output[n]

		writer.writerow(out)

		visual.print_keys(data, 9)

		#with open(pickle_file, 'ab') as afile:
		#	t = 'n'
