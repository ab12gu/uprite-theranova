#
# filename: main.py
# by: Abhay Gupta
#
# description: extract only HS and TO data from reference system
#

import sys
import os

# Don't know if necessary rn...
p = os.path.abspath('../../../../../../Data/Parsing Program/')
sys.path.append(p) # used to import print_struct
import print_struct as visual

# Library imports
import pickle
import csv

input_directory = '../../../../../../../AG_Parsed_Data/Structs' 
output_directory = '../../../../../../../AG_Parsed_Data/RS' 

top = ['Patient', 'Pace', 'Steps', 'Start late double-step', \
		'End early double-step']
with open('data_check.csv', 'w') as csvfile:
	output = csv.writer(csvfile)
	output.writerow(top)

# iterate through each patient file
	for c, filename in enumerate(os.listdir(input_directory)):

		"""Extract Pickle Data"""
		pickle_file = input_directory + '/' + filename
		with open(pickle_file, 'rb') as afile:
			data = pickle.load(afile)
		

		"""Extract HS & TO for reference system"""
		# visual.print_keys(data,5)
		pace = ['S', 'C', 'F']
		head = {}
		for w in pace:
			df = data['RS'][w]['data'][1]

			RS = {}
			foot_place = ['HS', 'TO']
			orientation = ['r', 'l']

			for i in foot_place:
				RS[i] = {}
				for j in orientation:
					RS[i][j] = []
			
			prev_side = None
			double_start_step = 0
			double_end_step = 0
			count = 0
			
			# iterate through all steps
			for i in range(14,len(df.index)):
				HS = df.iloc[i,0]
				TO = df.iloc[i,1]
		
				side = df.index[i][0]
				
				if i == len(df.index)-1:
					next_side = None
				else:
					next_side = df.index[i+1][0]
		
				# Check if double-start step
				if (i == 14 and next_side == side):
					print("Starting collecting late")
					double_start_step = 1
					continue

				# Check if double-end step
				if (side == prev_side):
					print("Ending collection early")
					double_end_step = 1
					break
				
				# Store HS & TO data
				if (side == 'R'):
					RS['HS']['r'].append(float(HS))
					RS['TO']['r'].append(float(TO))
				elif (side == 'L'):
					RS['HS']['l'].append(float(HS))
					RS['TO']['l'].append(float(TO))
				else: # data check
					print('The index value is weird ', side)
					quit()

				prev_side = side
				count += 1
			head[w] = RS
			output.writerow([filename.split('.')[0], w, count, \
					double_start_step, double_end_step])
			
		with open(os.path.join(output_directory, filename), 'wb') as afile:
			pickle.dump(head, afile)




