####
# filename: analyze_data.py	
# by: Abhay Gupta
#
# date: 09/10/18
####

# Library imports
import os
import pickle
import time as clocktime

# Custom function imports
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from utils.math_functions.general_math import my_round

# Change plot line width
plt.rcParams['lines.linewidth'] = 0.75

def open_files(directory):
	"""Open all data files needed for analysis"""

	data_file = os.path.join(directory, 'python_struct.pkl')
	zeno_file = os.path.join(directory, 'zeno_hs_to.pkl')
	data_window_file = os.path.join(directory, 'data_window.pkl')
	with open(data_file, 'rb') as afile: 
		data = pickle.load(afile) # Import all patient data
	if data['Flags']['tailBone']['accel'] == 0:
		return(None, None, None)
	with open(zeno_file, 'rb') as afile:
		zeno = pickle.load(afile)
	with open(data_window_file, 'rb') as afile:
		data_wdw = pickle.load(afile) # Import data windows
	
	return(data, zeno, data_wdw)

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
	data, zeno, data_wdw = open_files(directory)
	if data == None:
		print('No data for patient')
		return
	
	# Take out acceleration and gyroscope data from tailbone
	accel_data = data['UR']['sensorData']['tailBone']['accel']['data']	
	gyro_data = data['UR']['sensorData']['tailBone']['gyro']['data']

	# gather acceleration of all data
	left_foot_accel = data['UR']['sensorData']['leftAnkle']['accel']['data']	
	right_foot_accel = data['UR']['sensorData']['rightAnkle']['accel']['data']	
	left_hip_accel = data['UR']['sensorData']['leftHip']['accel']['data']	
	right_hip_accel = data['UR']['sensorData']['rightHip']['accel']['data']	

	print('Interval for motion data:', data_wdw)

	# Check if not enough data
	if data_wdw['F'][1] > len(gyro_data['x']):
		print("Not enough gyro data", data_wdw['F'][1], len(gyro_data['x']))
		return

	# Initialize variables
	accel = dict()
	gyro = dict()

	# export hs and to data	
	orientation = ['r', 'l']
	foot = ['HS', 'TO']
	to_hs = []	

	for o in orientation:
		for f in foot:
			to_hs = to_hs + zeno['S'][f][o]

	save_data = {}
	print(to_hs)

	# manual 3 stomps
	stomp = [6.1, 6.6, 7.1]
	offset = 10.65
	accel_offset = 19
	gyro_offset = 0
	deviation = 26
	ac = accel_offset + deviation
	gy = gyro_offset + deviation

	accel_data['x'] = [0]*0 + accel_data['x'][ac:]
	gyro_data['z'] = [0]*46 + gyro_data['z'][gy:]
	dist = round(len(zeno['S']['HS']['r'])/2)
	left_lim = zeno['S']['HS']['r'][dist-1]-0.5+offset
	right_lim = zeno['S']['HS']['r'][dist+1]+0.5+offset
	top_lim = 0.05
	bottom_lim = -0.05

	# edit window
	data_wdw['S'][0] = data_wdw['S'][0]-2000
	data_wdw['S'][1] = data_wdw['S'][1]+200

	#gyro_data['z'] = [-1*x for x in gyro_data['z']]
	accel_data['x'] = [-1*x for x in accel_data['x']]

	# test other body parts
	right_foot_accel['z'] = [-1*x for x in right_foot_accel['z']]
	left_foot_accel['x'] = [-1*x for x in left_foot_accel['x']]
	right_hip_accel['x'] = [-1*x for x in right_hip_accel['x']]
	left_hip_accel['x'] = [-1*x for x in left_foot_accel['x']]

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

		fig = plt.figure(figsize=(11, 7))
		ax = fig.add_subplot(1, 1, 1)

		spectrum = ['r', 'r', 'k','k', '#FF9633']
		linestyle = ['-', '--', '-', '--']
		counting = 0

		#ax.plot(accel['sec'], accel['x'], color = '#009999', label = 'tailbone x accel')
		#ax.plot(accel['sec'], gyro['z'], color = '#6600cc', label = 'tailbone z gyro') 
		
		# high-pass + integration

		from utils.math_functions import integrate_IMU as integrate
		from utils.signal_analysis.filt import general as signal_filt
		ripple_tol = [0.001, 0.1]
		fs = 100
		Ny = fs/2
		epsilon = 0.5
		gyro_hpf = {}
		angular_pos = {}
		cutoff = 0.5
		cut = [(cutoff-epsilon)/Ny,(cutoff+epsilon)/Ny]
		gyro_hpf['z'] = signal_filt(gyro['z'],  cut, fs, ripple_tol, 'high')
		angular_pos['z'] = integrate.IMU(gyro['sec'], gyro_hpf['z'], units='rad')
		ax.plot(accel['sec'], angular_pos['z'], color = 'g', label = 'tailbone z gyro') 

		#ax.plot(accel['sec'], right_foot_accel['z'][data_wdw[p][0]:data_wdw[p][1]], color = '#3366cc', label = 'right foot z accel')
		#ax.plot(accel['sec'], right_hip_accel['x'][data_wdw[p][0]:data_wdw[p][1]], color = (0.5,0.5,0.5), label = 'right hip x accel')
		#ax.plot(accel['sec'], left_foot_accel['x'][data_wdw[p][0]:data_wdw[p][1]], color = '#3366cc', label = 'left foot x accel')
		#ax.plot(accel['sec'], left_hip_accel['x'][data_wdw[p][0]:data_wdw[p][1]], color = '#3366cc', label = 'left hip x accel')


		plt.xlim((left_lim, right_lim))
		plt.ylim((bottom_lim, top_lim))

		ax.set_facecolor('0.8')
		mng = plt.get_current_fig_manager()
		mng.full_screen_toggle()

		ax.set_title(patient_number)

		for o in orientation:
			for dot, f in enumerate(foot):
				to_hs = to_hs + zeno['S'][f][o]
				for i in range(0, len(zeno['S'][f][o])):
					if i == 0:
						ax.axvline(x=zeno['S'][f][o][i]+offset, color = spectrum[counting], label=f+' ' + o, linewidth=1, linestyle=linestyle[counting], dashes=(5, 10*dot))
					else:
						ax.axvline(x=zeno['S'][f][o][i]+offset, color = spectrum[counting], linewidth = 1, linestyle=linestyle[counting], dashes=(5, 10*dot))
				counting += 1

		for i in range(0, len(stomp)):
			ax.axvline(x=stomp[i]+offset, color = spectrum[4], label = 'Stomp ' + str(i), linewidth = 1)


		#for i in range(0, len(to_hs)):
			#ax.axvline(x=to_hs[i]+8.58, color = 'r')
		cursor = Cursor(ax, useblit=True, color='k', linewidth=1)
		ax.legend() #['line', 'HS right', 'TO right', 'HS left', 'TO left'])

		for legobj in ax.legend().legendHandles:
			legobj.set_linewidth(2.0)   

		plt.show()

		return

def input_check(directory, folder_type):
	"check if multiple patients"

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
	directory = '../../data_files/analyzed_data/no_008'
	folder_type = 'n'

	input_check(directory, folder_type)

