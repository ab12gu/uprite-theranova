#####
# main file for gait data analysis
# By: Abhay Gupta
#
#
#
######

# import scipy.io as sio
import math
from sys import exit
import re
import os
import pickle
import glob

# Function imports
import mat_to_dict as convert
import print_struct as visual

# Scipt imports
import RS_to_dict as convert2  # parses reference system data

input_directory = '../../../GC_Parsed_Data/KateHamelStudy_11_2017'
output_directory = '../../../AG_Parsed_Data/Structs'

# create new filenames & store the .mat files as obj python files
for c, filename in enumerate(os.listdir(input_directory)):
	
	print('counter is', c)
	
	"""Looking for UR data"""
	if filename.endswith(".DS_Store"):
		continue
	else:
		"""Extracting patient number"""
		# print(filename)
		patient_number = re.findall("nova(\d+)", filename)
		patient_number = ''.join(patient_number)

		name = 'no_' + patient_number

		print(name)
		"""Extracting mat file"""
		directory = os.path.join(input_directory, filename)

		up_dir = glob.glob(directory + '/DATA*')
		up_dir = ''.join(up_dir)

		"""Parse through RS data"""
		np = ['S', 'C', 'F']
		
		RS_data = {} # Create empty dict
		for i in np:
			RF_file = glob.glob(directory + '/' + i + 'P*')
			RS_data[i] = convert2.fn(RF_file)

		"""Converting mat struct file to python dict"""
		print(1)
		mat_file = os.path.join(up_dir, "imuData.mat")  # put into external file...
		UR_data = convert.fn(mat_file, up_dir)
		# print(type(UR_data))

		data = {'RS' : RS_data, 'UR' : UR_data}

		#################
			
		# Need to do it from here to see 
		E_data = convert.fn('imuDataE.mat', up_dir)
		E_data = E_data['sensorData']
		F_data = convert.fn('imuDataF.mat', up_dir)
		F_data = F_data['sensorData']

		sensor_loc = ['leftAnkle', 'leftHip', 'rightAnkle', 'rightHip', 'tailBone']
		sensor_type = ['accel', 'gyro']

		E = {}
		F = {}

		
		for i in range(0,5):
			F[i] = {}
			E[i] = {}
			print('test')
			for j in range(0,2):
				temp = F_data[sensor_loc[i]][sensor_type[j]]['data']['x']
				F[i][j] = temp
				temp = E_data[sensor_loc[i]][sensor_type[j]]['data']['x']
				E[i][j] = temp
				print(temp)
				if not temp:
					print("list is empty")


		exit('Closing Program')
		
		# Visualize entire struct:
		# visual.print_all_keys(data)
		# visual.print_keys(data, 3)

		"""Saving obj into pickle file :)"""
		with open(os.path.join(output_directory, name + '.pkl'), 'wb') as afile:
			pickle.dump(data, afile)
	
		

# Output an excel document stating whether there is data


