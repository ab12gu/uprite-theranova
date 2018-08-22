#
# filename: main.py
#
# by: Abhay Gupta
#
# description: compare properties of RS & UR TO_HS

# Library imports
import pickle
import os
import sys
import csv
import statistics as stats

# Custom Library Imports 
from pathlib import Path
root = str(Path(os.path.abspath(__file__)).parents[4]) # Create a root directory
p = os.path.abspath(root + '/uprite_analysis/') # for custom functions
sys.path.append(p)
from custom_functions import *

RS_input_dir = root + '/AG_Parsed_data/RS'
UR_input_dir = root + '/AG_Parsed_data/UR/HS_TO/Direct_GC'

top = ['Patient','System', 'Pace', 'Stride time', 'Right step time', \
		'Left step time', 'Double stance time', 'Cadence']
pace = ['S', 'C', 'F']

system = ['RS', 'UR']
orientation = ['r', 'l']
foot = ['HS', 'TO']

with open('gain_analysis.csv', 'w') as csvfile:
	output = csv.writer(csvfile)
	output.writerow(top)

# iterate through each patient file
	for c, filename in enumerate(os.listdir(UR_input_dir)):
		if c < 2:
			continue

		patient_number = filename.split('.')[0] 	
		print("Extrating data from patient: ", patient_number)
		print("Current patient iteration: ", c)
		gait = {}

		"""Extract Pickle Data"""	
		RS_file = RS_input_dir + '/' + filename
		UR_file = UR_input_dir + '/' + filename
		with open(RS_file, 'rb') as afile:
			RS = pickle.load(afile)
		with open(UR_file, 'rb') as afile:
			UR = pickle.load(afile)
		
		"""Find Gait Parameters from HS & TO"""
	
		for p in pace:
			for i in foot:
				for j in orientation:
					UR[p][i][j] = [x/100 for x in UR[p][i][j]]	
		stride = {}
		right_step = {}
		left_step = {}
		for w in system:
			gait[w] = {}
			stride[w] = []
			right_step[w] = []
			left_step[w] = []
		
		# stride time
		for p in pace:
			gait['RS'][p] = []
			gait['UR'][p] = []

			for c in range(1, len(RS[p]['HS']['r'])):
				stride['RS'].append(RS[p]['HS']['r'][c] - RS[p]['HS']['r'][c-1])
			for c in range(1, len(UR[p]['HS']['r'])):
				stride['UR'].append(UR[p]['HS']['r'][c] - UR[p]['HS']['r'][c-1])
		
			gait['RS'][p].append(stats.mean(stride['RS']))
			if (len(stride['UR']) == 0):
				gait['UR'][p].append(None)
			else:
				gait['UR'][p].append(stats.mean(stride['UR']))
		
		# right & left step time
			# Find if right foot or left foot is first
			right = RS[p]['HS']['r']
			left = RS[p]['HS']['l']
			length = min(len(right), len(left))

			for c in range(1, length):
				if right[c] > left[c]:
					right_step['RS'].append(right[c]-left[c])
					left_step['RS'].append(left[c]-right[c-1])
				else:
					right_step['RS'].append(left[c]-right[c])
					left_step['RS'].append(right[c]-left[c-1])
			
			gait['RS'][p].append(stats.mean(right_step['RS']))
			gait['RS'][p].append(stats.mean(left_step['RS']))

		# double stance time
			gait['RS'][p].extend(['',''])
			gait['UR'][p].extend(['','','',''])
		
		gait['dif'] = []
		for i in range(0, len(gait['UR'])):
			if i > 0:
				continue
			elif gait['UR'][p][0] == None:
				gait['dif'].append(None)
				continue
			gait['dif'].append((gait['UR'][p][i] - gait['RS'][p][i])/gait['RS'][p][i])
		
		print(gait['dif'])
		
		gait['dif'].extend(['','','',''])

		"""Add data to csv_file"""
		for p in pace:
			output.writerow([filename, 'UR', p] + gait['UR'][p])
			output.writerow(['', 'RS', p] + gait['RS'][p])
			output.writerow(['', '', '% Error'] + gait['dif'])
		







