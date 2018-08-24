####
# filename: python_data_structure.py
# By: Abhay Gupta
#
# Description: extracts RS & UR data in matlab structs
#
####

# standard library imports
import math
import sys
import re
import os
import pickle
import glob

# custom package imports
from utils.visualize_structure import visualize_structure as visual # see dict structure
from utils.filetype_conversion.zeno_to_dict import convert as zeno_to_dict  # parses reference system data
from utils.filetype_conversion.mat_to_dict import convert as mat_to_dict # .mat filetype conversion
from utils.filetype_conversion.zeno_to_dict import offset as first_step # export first footstep

def extract(input_directory, output_directory, filename):
	"""Save converted matlab to python data"""
	
	# extract patient number
	patient_number = re.findall("nova(\d+)", filename)
	patient_number = ''.join(patient_number)
	if (len(patient_number) == 2):
		patient_number = '0' + patient_number
	name = 'no_' + patient_number
	print("Patient: ", name)

	# skip reference data with different format
	if patient_number in {'001', '006', '007'}:		
		print("Reference data is formatted differently")
		return

	print("Parsing through RS data")
	walk_type = ['S', 'C', 'F']
	offset = first_step(input_directory)
	
	RS_data = {} #Create empty dict
	for c, i in enumerate(walk_type):
		RF_file = glob.glob(input_directory + '/' + i + 'P*')
		RS_data[i] = zeno_to_dict(RF_file, offset[c])

	print("Converting mat struct file to python dict")
	uprite_data_directory = glob.glob(input_directory + '/DATA*')
	uprite_data_directory = ''.join(uprite_data_directory)
	mat_file = os.path.join(uprite_data_directory, "imuData.mat")  # put into external file...
	UR_data = mat_to_dict(mat_file, uprite_data_directory)

	data = {'RS' : RS_data, 'UR' : UR_data}

	# Visualize entire struct:
	# visual.print_all_keys(data)
	# visual.print_keys(data, 4)

	print("Saving obj into pickle file")
	filename = 'python_struct'	
	output_directory = os.path.join(output_directory, name)
	filename = os.path.join(output_directory, filename + '.pkl')

	os.makedirs(os.path.dirname(filename), exist_ok=True) # check directory
	with open(filename, 'wb') as afile:
		pickle.dump(data, afile)


def input_check(input_directory, output_directory, foldertype):
	"""Save matlab to python data depending on input folder type"""

	if (foldertype == 'n'):
		filename = input_directory
		extract(input_directory, output_directory, filename)
	else:
		for c, filename in enumerate(os.listdir(input_directory)): # Loop through files
			# Look for patient folders 
			if filename.endswith(".DS_Store"):
				continue
			else:
				# extracting patient number
				directory = os.path.join(input_directory, filename)
				extract(directory, output_directory, filename)
	
		
if __name__ == '__main__':
	print('Running test files... skipping GUI')

	input_directory = '../../data_files/raw_data/Theranova02'
	output_directory = '../../data_files/analyzed_data/'
	foldertype = 'n'
	input_check(input_directory, output_directory, foldertype)

