####
# filename: zeno_extract.py
# by: Abhay Gupta
#
# description: extract only HS and TO data from reference system
#
####

# Library imports
import pickle
import csv
import sys
import os

from utils.visualize_structure import visualize_structure as visual

def extract(directory, output):
	"""Extract TO & HS from zeno data"""
	
	pace = ['S', 'C', 'F']
	orientation = ['r', 'l']
	foot_place = ['HS', 'TO']
	modifier = 'python_struct.pkl'
	savefile = 'zeno_hs_to.pkl'
	
	patient_name = directory[-6:]
	print("Extract file: ", patient_name)
	pickle_file = os.path.join(directory, modifier)
	with open(pickle_file, 'rb') as afile:
		data = pickle.load(afile)
			
	# extract HS & TO for reference system
	# visual.print_keys(data,5)
	head = {}
	for w in pace:
		df = data['RS'][w]['data'][1]

		zeno = {}
		for i in foot_place:
			zeno[i] = {}
			for j in orientation:
				zeno[i][j] = []
		
		prev_side = None
		double_start_step = 'no'
		double_end_step = 'no'
		count = 0

		import matplotlib.pyplot as plt
		from matplotlib.widgets import Cursor

		#heel = list(map(float, df.iloc[14:,0].tolist()))
		#toe = list(map(float, df.iloc[14:,1].tolist()))

		#fig = plt.figure(figsize=(11, 7))
		#ax = fig.add_subplot(1, 1, 1)
		#for i in range(0, len(toe)):
			#ax.axvline(x=toe[i], color = 'r')
		#for i in range(0, len(heel)):
			#ax.axvline(x=heel[i], color = 'b')
		#print(type(heel[1]))
		#cursor = Cursor(ax, useblit=True, color='k', linewidth=1)
		#plt.show()
		
		# iterate through all steps
		for i in range(14,len(df.index)):
			HS = float(df.iloc[i,0])
			TO = float(df.iloc[i,1])
	
			side = df.index[i][0]
			
			if i == len(df.index)-1:
				next_side = None
			else:
				next_side = df.index[i+1][0]
	
			# Check if double-start step
			if (i == 14 and next_side == side):
				print("Starting collecting late")
				double_start_step = 'yes'
				continue

			# Check if double-end step
			if (side == prev_side):
				print("Ending collection early")
				double_end_step = 'yes'
				break
			
			# Store HS & TO data
			if (side == 'R'):
				zeno['HS']['r'].append(float(HS))
				zeno['TO']['r'].append(float(TO))
			elif (side == 'L'):
				zeno['HS']['l'].append(float(HS))
				zeno['TO']['l'].append(float(TO))
			else: # data check
				print('The index value is weird ', side)
				quit()
	
			prev_side = side
			count += 1		
		
		print(zeno)
		fig = plt.figure(figsize=(11, 7))
		ax = fig.add_subplot(1, 1, 1)
		for i in range(0, len(zeno['HS']['r'])):
			ax.axvline(x=zeno['HS']['r'][i], color = 'r')
		for i in range(0, len(zeno['HS']['l'])):
			ax.axvline(x=zeno['HS']['l'][i], color = 'b')
		for i in range(0, len(zeno['TO']['r'])):
			ax.axvline(x=zeno['TO']['r'][i], color = 'g')
		for i in range(0, len(zeno['TO']['l'])):
			ax.axvline(x=zeno['TO']['l'][i], color = 'k')
		cursor = Cursor(ax, useblit=True, color='k', linewidth=1)
		plt.show()

		head[w] = zeno
		output.writerow([patient_name, w, count, double_start_step, double_end_step])
	
	pickle_file = os.path.join(directory, savefile)
	with open(pickle_file, 'wb') as afile:
		pickle.dump(head, afile)

	return output

def input_check(directory, foldertype):
	"""Save matlab to python data depending on input folder type"""

	if (foldertype == 'n'):
		with open('../docs/zeno_hs_to.csv', 'a') as csvfile:
			output = csv.writer(csvfile)

			extract(directory, output)
	else:
		with open('../docs/zeno_hs_to.csv', 'w') as csvfile:
			output = csv.writer(csvfile)
			top = ['Patient', 'Pace', 'Steps', 'Start late double-step', 'End early double-step']
			output.writerow(top)

			for c, filename in enumerate(os.listdir(directory)):
				if (filename == '.DS_Store'):
					continue
				afile = os.path.join(directory, filename)
				extract(afile, output)

if __name__ == '__main__':
	print('Running test files... skipping GUI')

	directory = '../../data_files/analyzed_data'
	foldertype = 'y'
	
	directory = '../../data_files/analyzed_data/no_131'
	foldertype = 'n'
	input_check(directory, foldertype)


