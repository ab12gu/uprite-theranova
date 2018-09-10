####
# filename: extract_uprite.py
# by: Abhay Gupta
# date: 08/20/18
#
# description: find hs and to of all data
####

# Library imports
import os
import pickle
import time as clocktime

# Custom function imports
import matplotlib.pyplot as plt
from utils.math_functions.general_math import my_round
from utils.signal_analysis.gyro_spikes import gyro_spikes

from utils.signal_analysis.accel_spikes import accel_spikes
from utils.heel_toe.max_jerk import max_jerk
from utils.heel_toe.right_left import right_left

from archive.accel_spikes import accel_spikes as spikes

def open_files(directory):
	"""Open all data files needed for analysis"""

	data_file = os.path.join(directory, 'python_struct.pkl')
	data_window_file = os.path.join(directory, 'data_window.pkl')
	gravity_window_file = os.path.join(directory, 'gravity_window.pkl')
	with open(data_file, 'rb') as afile: 
		data = pickle.load(afile) # Import all patient data
	if data['Flags']['tailBone']['accel'] == 0:
		return(None, None, None)
	with open(data_window_file, 'rb') as afile:
		data_wdw = pickle.load(afile) # Import data windows
	with open(gravity_window_file, 'rb') as afile:
		grav_wdw = pickle.load(afile) # Import gravity windows
	
	return(data, data_wdw, grav_wdw)

def extract(directory):
	"""Find peaks and troughs of data"""

	# initialize variables
	pace = ['S', 'C', 'F']
	coordinates = ['x', 'y', 'z']

	# measure runtime
	start_time = clocktime.time() 

	# Extract Patient Number
	patient_number = directory[-6:]
	print("Extracting data for patient:", patient_number)

	# Open data_file, gravity_window, data_window
	data, data_wdw, grav_wdw = open_files(directory)
	if data == None:
		print('No data for patient')
		return
	
	# Take out acceleration and gyroscope data from tailbone
	accel_data = data['UR']['sensorData']['tailBone']['accel']['data']	
	gyro_data = data['UR']['sensorData']['tailBone']['gyro']['data']	

	#plt.figure()
	#plt.plot(accel_data['z'])
	#plt.figure()
	#plt.plot(gyro_data['z'])

	# Round all window coordinates
	for p in pace:
		for i in range(0,2):
			data_wdw[p][i] = my_round(data_wdw[p][i])
			grav_wdw[i] = my_round(grav_wdw[i])
	
	print('Interval for motion data:', data_wdw)
	print('Interval for gravity data:', grav_wdw)

	# Check if not enough data
	if data_wdw['F'][1] > len(gyro_data['x']):
		print("Not enough gyro data", data_wdw['F'][1], len(gyro_data['x']))
		return

	# Initialize variables
	accel = dict()
	gyro = dict()

	#plt.figure()
	#plt.plot(accel_data['x'])
	# Plot vertical lines at places of peaks and troughs
	#plt.axvline(data_wdw['S'][0], color = 'g', linestyle = '--')
	#plt.axvline(data_wdw['S'][1], color = 'b', linestyle = '--')


	save_data = {}

	# Iterate through slow, calm, fast paces
	for k, p in enumerate(pace):
		print("Extracting data for pace: ", p)

		if (data_wdw['flag']['F'] == 0):
			print('Not enough accel-data recorded')
			continue

		# cut data with windows
		for w in coordinates:
			accel[w] = accel_data[w][data_wdw[p][0]:data_wdw[p][1]]
			gyro[w] = gyro_data[w][data_wdw[p][0]:data_wdw[p][1]]
		gyro['sec'] = gyro_data['seconds'][data_wdw[p][0]:data_wdw[p][1]]
		accel['sec'] = accel_data['seconds'][data_wdw[p][0]:data_wdw[p][1]]	

		# find gyro spikes
		all_gyro_spikes, gyro_peaks, gyro_troughs, ang_pos = gyro_spikes(gyro)
	
		speed = ['slow', 'calm', 'fast']
		home = '../../figures/tailbone/' 
		home = os.path.join(home, patient_number)
		output_dir = os.path.join(home, speed[k])
		
		plt.plot(gyro['sec'], ang_pos)
		plt.plot([gyro['sec'][x] for x in gyro_troughs], [ang_pos[x] for x in gyro_troughs], 'c^')
		plt.plot([gyro['sec'][x] for x in gyro_peaks], [ang_pos[x] for x in gyro_peaks], 'co')
		plt.legend(['angular_position', 'gyro_troughs', 'gyro_peaks'])
		
		output = os.path.join(output_dir, 'gyro_spikes.pdf')
		plt.savefig(output)
		plt.close()
		
		# NOTE: GC only finds peaks for accel, no troughs... weirdo
		accel_peaks = accel_spikes(accel['x'][:], all_gyro_spikes)

		#peaks = spikes(accel, gyro_peaks)

		to_locations, temp = max_jerk(accel['x'][:], accel_peaks)

		from utils.data_structure_functions import difference
		accel_first_diff = difference.first(accel['x'],1)


		plt.plot(accel['sec'], accel_first_diff)
		plt.plot([accel['sec'][x] for x in to_locations], [accel_first_diff[x-1] for x in to_locations], 'k^')
		plt.legend(['accel_diff', 'to_locations'])
			
		output = os.path.join(output_dir, 'to_locations.pdf')
		plt.savefig(output)
		plt.close()


		plt.figure()	
		plt.plot(accel['sec'], accel['x'])
		plt.plot([accel['sec'][x] for x in accel_peaks], [accel['x'][x] for x in accel_peaks], 'co')
		plt.legend(['accel x', 'accel peaks'])
		
		output = os.path.join(output_dir, 'accel_peaks.pdf')
		plt.savefig(output)
		plt.close()


		HS, TO = right_left(accel_peaks, all_gyro_spikes, gyro_troughs, to_locations)

		orientation = ['r', 'l']
		linestyles = ['c*', 'm*', 'bo', 'ro']
		legend1 = ['right HS', 'right TO', 'left HS', 'left TO']

		plt.figure()
		plt.plot(accel['sec'], accel['x'])
		plt.plot(accel['sec'], accel_first_diff)
		for c, i in enumerate(orientation, 1):
			plt.plot([accel['sec'][x] for x in HS[i]],
				[accel['x'][x] for x in HS[i]], linestyles[c*2-2])
			plt.plot([accel['sec'][x] for x in TO[i]],\
				[accel_first_diff[x] for x in TO[i]], linestyles[c*2-1])
		plt.legend(['x accel', 'x diff'] + legend1)
		#plt.show()


		output = os.path.join(output_dir, 'heel_toe.pdf')
		plt.savefig(output)
		plt.close()






		save_data[p] = {}
		save_data[p]['HS'] = {}
		save_data[p]['HS'] = HS
		save_data[p]['TO'] = {}
		save_data[p]['TO'] = TO


	with open(os.path.join(directory, 'uprite_hs_to.pkl'), 'wb') as afile:
		pickle.dump(save_data, afile)   

	# save plot to files



def input_check(directory, folder_type):

	if (folder_type == 'n'):
		extract(directory)
	else:
		start_time = clocktime.time()
		# iterate through every patient file
		for c, filename in enumerate(os.listdir(directory)):
			if (c < 0):
				continue
			if filename == ".DS_Store":
				continue
			print(filename)

			print("Current patient iteration:", c)
			afile = os.path.join(directory, filename)
			extract(afile)

if __name__ == '__main__':
	print('Running test files... skipping GUI')

	#directory = '../../data_files/analyzed_data'
	#folder_type = 'y'
	directory = '../../data_files/analyzed_data/no_003'
	folder_type = 'n'

	input_check(directory, folder_type)

