####
# Filename: flag_empty_data.py
# By: Abhay Gupta
#
# Description: Checks UR data if any empty data
# ... records the amount of time recordeed for UR data in csv file
# ... and adds flag to pickle data file to state whether data is empty
####

# standard library imports
import sys
import os
import pickle
import csv
from itertools import product

# custom package imports
from utils.visualize_structure import visualize_structure as visual # see dictionary structure

# global variables
top = ['Presents the amount of recorded time per patient (in seconds) by UpRite Sensors']
sensor_loc = ['leftAnkle', 'leftHip', 'rightAnkle', 'rightHip', 'tailBone']
abbrev = ['LA', 'LH', 'RA', 'RH', 'TB']
modifier = 'python_struct.pkl'
sensor_type = ['accel', 'gyro']
patient_label = ['Patient Name']
sensor_loc = ['leftAnkle', 'leftHip', 'rightAnkle', 'rightHip', 'tailBone']
header_names =  patient_label + list(map(''.join, product(abbrev,[' '],sensor_type))) 

def flag(input_directory, writer):
	"""flags empty data"""
	
	# Find if data is empty. Store in csv file and overwrite pickle file.
	print('Extracting Pickle Data')
	patient_name = input_directory[-6:]
	pickle_file = os.path.join(input_directory, modifier)
	with open(pickle_file, 'rb') as afile:
		data = pickle.load(afile)

	print('Find if data is empty')
	# Initialize values 
	check_data = data['UR']['sensorData']
	print(patient_name)
	output = {}
	data['Flags'] = {}
	counter = 0
	
	print('Checking file ', patient_name)
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
		
	out = {patient_label[0]: patient_name}
	for n in range(0,counter):
		out[header_names[n+1]] = output[n]

	print("Writing to csv file")
	writer.writerow(out)

	with open(pickle_file, 'wb') as afile:
		pickle.dump(data , afile)

	# Check if file really has flags added:
	# with open(pickle_file, 'rb') as afile:
	#	data = pickle.load(afile)
	#	visual.print_keys(data, 9)

def input_check(directory, folder_type):
	"""Save if the data is empty depending on folder type"""

	if (folder_type == 'n'):
		with open('../docs/uprite_data_overview.csv', 'a') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames = header_names)
			flag(directory, writer)
			
	else: # create new csv file, and add to it.
		with open('../docs/uprite_data_overview.csv', 'w') as csvfile: # write header to output csv file
			begin = csv.writer(csvfile)
			begin.writerow(top)

			for i in range(0,5):
				begin.writerow({abbrev[i] + '='+ sensor_loc[i]})
			for i in range(0,2):
				begin.writerow('')

		with open('../docs/uprite_data_overview.csv', 'a') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames = header_names)
			writer.writeheader()

			for c, filename in enumerate(os.listdir(directory)):
				if filename.endswith(".DS_Store"): # skip folder meta-data
					continue
				afile = os.path.join(directory, filename)
				flag(afile, writer)

if __name__ == '__main__':
	print('Running test files... skipping GUI')

	# folder_name = 'n'
	# directory = '../../data_files/analyzed_data/no_002'
	folder_name = 'y'
	directory = '../../data_files/analyzed_data/'
	input_check(directory, folder_name)
