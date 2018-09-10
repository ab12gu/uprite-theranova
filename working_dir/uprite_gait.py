####
# filename: compare_gait.py
# by: Abhay Gupta
# date: 08/21/18
#
# description: compare properties of zeno & uprite TO_HS
####

# Library imports
import pickle
import os
import sys
import csv
import statistics as stats
import time as clocktime

# global variables
top = ['Patient', 'System', 'Pace', 'Stride time', 'Right step time',
		   'Left step time', 'Double stance time', 'Cadence']
	
def extract(directory, output):
	"""Compare gait of zeno and uprite system"""

	start_time = clocktime.time()


	pace = ['S', 'C', 'F']
	system = ['zeno', 'uprite']
	orientation = ['r', 'l']
	foot = ['HS', 'TO']

	# iterate through each patient file
	patient_number = directory[-6:]
	print("Extrating data from patient: ", patient_number)
	gait = {}

	"""Extract Pickle Data"""
	zeno_file = os.path.join(directory, 'zeno_hs_to.pkl')
	uprite_file = os.path.join(directory, 'uprite_hs_to.pkl')
	with open(zeno_file, 'rb') as afile:
		zeno = pickle.load(afile)
	with open(uprite_file, 'rb') as afile:
		uprite = pickle.load(afile)

	"""Find Gait Parameters from HS & TO"""

	for p in pace:
		for i in foot:
			for j in orientation:
				uprite[p][i][j] = [x / 100 for x in uprite[p][i][j]]
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
		gait['zeno'][p] = []
		gait['uprite'][p] = []

		for d in range(1, len(zeno[p]['HS']['r'])):
			stride['zeno'].append(zeno[p]['HS']['r'][d] - zeno[p]['HS']['r'][d - 1])
		for d in range(1, len(uprite[p]['HS']['r'])):
			stride['uprite'].append(uprite[p]['HS']['r'][d] - uprite[p]['HS']['r'][d - 1])

		gait['zeno'][p].append(stats.mean(stride['zeno']))
		if not stride['uprite']:
			gait['uprite'][p].append(None)
		else:
			gait['uprite'][p].append(stats.mean(stride['uprite']))

		# right & left step time
		# Find if right foot or left foot is first
		right = zeno[p]['HS']['r']
		left = zeno[p]['HS']['l']
		length = min(len(right), len(left))

		for d in range(1, length):
			if right[d] > left[d]:
				right_step['zeno'].append(right[d] - left[d])
				left_step['zeno'].append(left[d] - right[d - 1])
			else:
				right_step['zeno'].append(left[d] - right[d])
				left_step['zeno'].append(right[d] - left[d - 1])

		gait['zeno'][p].append(stats.mean(right_step['zeno']))
		gait['zeno'][p].append(stats.mean(left_step['zeno']))

	# double stance time
		gait['zeno'][p].extend(['', ''])
		gait['uprite'][p].extend(['', '', '', ''])

	# find the % difference
	gait['dif'] = {}

	for p in pace:
		gait['dif'][p] = [] 
		for i in range(0, len(gait['uprite'][p])):
			if i > 0: # only do first one rn... due to missing analyzes
				continue
			elif gait['uprite'][p][0] is None:
				gait['dif'][p].append(None)
				continue
			gait['dif'][p].append((gait['uprite'][p][i] - gait['zeno'][p][i]) / gait['zeno'][p][i])
		gait['dif'][p].extend(['', '', '', ''])
		

	"""Add data to csv_file"""
	for p in pace:
		output.writerow([patient_number, 'uprite', p] + gait['uprite'][p])
		output.writerow(['', 'zeno', p] + gait['zeno'][p])
		output.writerow(['', '', '% Error'] + gait['dif'][p])

	print('Successful run!') 
	print('-----------RUNTIME: %s second ----' % (clocktime.time() - start_time))

def input_check(directory, folder_type):
	"""Check input folder type"""

	if (folder_type == 'n'): # run single patient file
		with open('../docs/compare_gait.csv', 'a') as csvfile:
			output = csv.writer(csvfile)

			extract(directory, output)
	else: # iterate through every patient file
		start_time = clocktime.time()

		with open('../docs/uprite_gait.csv', 'w') as csvfile:
			output = csv.writer(csvfile)
			output.writerow(top)
		
			for c, filename in enumerate(os.listdir(directory)):
				if c < 0:
					continue

				print("Current patient iteration: ", c)
				afile = os.path.join(directory, filename)
				extract(afile, output)

		print('Successful run!') 
		print('-----------RUNTIME: %s second ----' % (clocktime.time() - start_time))

		

if __name__ == '__main__':
	print('Running test files... skipping GUI')

	directory = '../../data_files/analyzed_data'
	folder_type = 'y'
	directory = '../../data_files/analyzed_data/no_003'
	folder_type = 'n'

	input_check(directory, folder_type)

	#zeno_input_directory = '../../data_files/temp/zeno'
	#uprite_input_directory = '../../data_files/temp/uprite/HS_TO/Direct_GC'





