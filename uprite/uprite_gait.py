####
# filename: uprite_gait.py
# by: Abhay Gupta
# date: 09/20/18
#
# description: extract the gait parameters for the uprite walkway
####

# Library imports
import pickle
import os
import sys
import csv
import statistics as stats
import time as clocktime
from pathlib import Path

# global variables
top = ['Patient', 'Pace', 'Stride time', 'Right step time',
	   'Left step time', 'Double stance time', 'Right Single Stance',
	   'Left Single Stance', 'Cadence']
	
def extract(directory, output):
	"""Extract gait characteristics for uprite system"""

	pace = ['S', 'C', 'F']
	orientation = ['r', 'l']
	foot = ['HS', 'TO']
	patient_number = directory[-6:]

	# iterate through each patient file
	patient_number = directory[-6:]
	print("Extrating data from patient: ", patient_number)
	gait = {}

	# Extract Pickle Data
	uprite_file = os.path.join(directory, 'uprite_hs_to.pkl')
	if Path(uprite_file).is_file():
		with open(uprite_file, 'rb') as afile:
			uprite = pickle.load(afile)
	else:
		return

	# Find Gait Parameters from HS & TO"""

	gait_names = ['stride', 'right_step', 'left_step', 'double_stnace', 'right_single_stance', 'left_single_stance', 'cadence']
	stride = []
	right_step = []
	left_step = []
	double_stance = []
	right_single_stance = []
	left_single_stance = []
	cadence = []

	characteristics = {}

	# iterate through each pace type
	for p in pace:
		gait[p] = []
		characteristics[p] = {}

		if not uprite:
			characteristics[p] = None
			gait[p].append(None)
			continue
	
		# stride time
		stride_amount = len(uprite[p]['HS']['r'])
		if (stride_amount < 2):
			gait[p].append(None)
		else:
			for d in range(1, len(uprite[p]['HS']['r'])):
				stride.append(uprite[p]['HS']['r'][d] - uprite[p]['HS']['r'][d - 1])
			gait[p].append(stats.mean(stride)/100)

		# Find if right foot or left foot is first
		right_heel = uprite[p]['HS']['r']
		left_heel = uprite[p]['HS']['l']
		right_toe = uprite[p]['TO']['r']
		left_toe = uprite[p]['TO']['l']


		if len(right_heel) > 1 and len(left_heel) > 1:

			length = min(len(right_heel), len(left_heel))


			for d in range(1, length): # need to check which step was taken first
				if right_heel[d] < left_heel[d]:
					left_step.append(left_heel[d] - right_heel[d])
					right_step.append(right_heel[d] - left_heel[d-1])
					if d <= len(right_toe)-1:
						double_stance.append(right_toe[d] - left_heel[d])
				else:
					right_step.append(left_heel[d] - right_heel[d-1])
					left_step.append(right_heel[d-1] - left_heel[d - 1])
					if d <= len(right_toe)-1:
						double_stance.append(right_toe[d] - left_heel[d-1])

			if d <= len(left_toe)-1:
				right_single_stance.append(left_heel[d] - left_toe[d-1])

			if d <= len(right_toe)-1:
				left_single_stance.append(right_heel[d] - right_toe[d-1])

			gait[p].append(stats.mean(right_step)/100)
			gait[p].append(stats.mean(left_step)/100)
	
			length = len(right_heel)
			if length < 3:
				cadence = None
			else:
				cadence = (right_heel[length - 2] - right_heel[1])/(2*(length-1)) # skips first and last steps
				cadence = cadence/100


			if double_stance:
				gait[p].append(stats.mean(double_stance)/100)
			else:
				gait[p].append(None)

			if right_single_stance:
				gait[p].append(stats.mean(right_single_stance)/100)
			else:
				gait[p].append(None)

			if left_single_stance:
				gait[p].append(stats.mean(left_single_stance)/100)
			else:
				gait[p].append(None)

			gait[p].append(cadence)
		else:
			for i in range(0,6):
				gait[p].append(None)


		# save all gaits in pickle file structure
		for i in range(0, len(gait[p])):
			characteristics[p][gait_names[i]] = gait[p][i]

	with open(os.path.join(directory, 'uprite_gait.pkl'), 'wb') as afile:
		pickle.dump(characteristics, afile)

	"""Add data to csv_file"""
	for p in pace:
		output.writerow([patient_number, p] + gait[p])

def input_check(directory, folder_type):
	"""Check input folder type"""

	if (folder_type == 'n'): # run single patient file
		with open('../docs/uprite_gait.csv', 'a') as csvfile:
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
				if filename == '.DS_Store':
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
	#directory = '../../data_files/analyzed_data/no_003'
	#folder_type = 'n'

	input_check(directory, folder_type)






