####
# filename: extract_uprite.py
# by: Abhay Gupta
# date: 08/20/18
#
# description: run GC's to & hs algorithm on all uprite data/gravity windows
####

# Library imports
import sys
import os
import pickle
import statistics as stats
import math
import matplotlib.pyplot as plt
import time as clocktime
from copy import deepcopy
from numpy.linalg import inv
import numpy as np

# Custom function imports
from utils.math_functions.general_math import my_round
from utils.signal_analysis.filt import lowpass
from utils.signal_analysis.filt import highpass
from utils.math_functions import integrate_IMU as integrate
from utils.math_functions import stride
from utils.data_structure_functions import difference
from utils.signal_analysis import find_peaks

# Change plot line width
plt.rcParams['lines.linewidth'] = 0.5

# global variables
pace = ['S', 'C', 'F']
coordinates = ['x', 'y', 'z']
orientation = ['r', 'l']

def open_files(directory):

	data_file = os.path.join(directory, 'python_struct.pkl')
	data_window_file = os.path.join(directory, 'data_window.pkl')
	gravity_window_file = os.path.join(directory, 'gravity_window.pkl')
	with open(data_file, 'rb') as afile: 
		data = pickle.load(afile) # Import all patient data
	with open(data_window_file, 'rb') as afile:
		data_wdw = pickle.load(afile) # Import data windows
	with open(gravity_window_file, 'rb') as afile:
		grav_wdw = pickle.load(afile) # Import gravity windows
	
	return(data, data_wdw, grav_wdw)


def extract(directory):
	"""extract all the hs & to data from uprite sensor"""

	start_time = clocktime.time() # record clocktime
	save_data = {}

	# Extract Patient Number
	patient_name = directory[-6:]
	print("Extracting data for patient:", patient_name)
	
	# Open data_file, gravity_window, data_window
	data, data_wdw, grav_wdw = open_files(directory)
	
	# Take out acceleration and gyroscope data from tailbone
	accel_all = data['UR']['sensorData']['tailBone']['accel']['data']	
	gyro_all = data['UR']['sensorData']['tailBone']['gyro']['data']	
		
	# Round all window coordinates
	for p in pace:
		for i in range(0,2):
			data_wdw[p][i] = my_round(data_wdw[p][i])
			grav_wdw[i] = my_round(grav_wdw[i])
	
	print('Interval for motion data:', data_wdw)
	print('Interval for gravity data:', grav_wdw)

	# Check if not enough data
	if (data_wdw['flag']['F'] == 0):
		print('Not enough accel-data recorded')
		return
	elif data_wdw['F'][1] > len(gyro_all['x']):
		print("Not enough gyro data", data_wdw['F'][1], len(gyro_all['x']))
		return

	# Initialize variables
	mean_accel = {}
	accel_data = {}
	gyro_data = {}
	accel_data['seconds'] = accel_all['seconds']
	gyro_data['seconds'] = gyro_all['seconds']
	
	for w in coordinates:
		mean_accel[w] = stats.mean(accel_all[w][grav_wdw[0]:grav_wdw[1]])

	# Iterate through slow, calm, fast paces
	for p in pace:
		# Extract windowed data
		for w in coordinates:
			accel_data[w] = accel_all[w][data_wdw[p][0]:data_wdw[p][1]]
			gyro_data[w] = gyro_all[w][data_wdw[p][0]:data_wdw[p][1]]
		
		""" STRAIGHT GC (expect start_index/end_index) """
		gravity_strength = math.sqrt(mean_accel['x']**2 + mean_accel['y']**2 + \
		mean_accel['z']**2)

		normalized_mean_accel = {}
		normalized_mean_accel['x'] = mean_accel['x']/gravity_strength
		normalized_mean_accel['y'] = mean_accel['y']/gravity_strength
		normalized_mean_accel['z'] = mean_accel['z']/gravity_strength

		"""NU""" 
		normalized_gravity_vector = [normalized_mean_accel['x'], normalized_mean_accel['y'], \
				normalized_mean_accel['z']]

		# Key asumption here is that the gravity vector is [-1, 0, 0] 
		# so the x axis is upwards and downwards
		# R_yzx
		roll = 0 # math.atan(mean_accel['y']/mean_accel['z'])
		pitch = math.atan(normalized_mean_accel['z']/normalized_mean_accel['x'])
		yaw = math.atan(normalized_mean_accel['y']/math.sqrt(normalized_mean_accel['x']**2 + \
				normalized_mean_accel['z']**2))

		# Indexes used for analysis
		start_index = 0
		end_index = len(accel_data['x'])-1
		
		# Cut data to relevant data
		accel = {}
		accel['sec'] = accel_data['seconds'][start_index:(end_index)]
		accel['x'] = accel_data['x'][start_index:(end_index)]
		accel['y'] = accel_data['y'][start_index:(end_index)]
		accel['z'] = accel_data['z'][start_index:(end_index)]
		time = accel['sec']


		# Put acceleration data through a low pass filter
		# No gravity vector utilized yet.... don't know why it is called it yet...
		f_cuts = [0.1/50, 0.7/50] # Passband & Stopband cutoffs
		sampling_rate = 100 
		ripple_tol = [0.001, 0.1] # Passband & Stopband tolerances

		gravity_accel = {}
		gravity_accel['x'] = lowpass(accel_data['x'], f_cuts, sampling_rate, \
				ripple_tol)
		gravity_accel['y'] = lowpass(accel_data['y'], f_cuts, sampling_rate, \
				ripple_tol)
		gravity_accel['z'] = lowpass(accel_data['z'], f_cuts, sampling_rate, \
				ripple_tol)

		#plt.plot(gravity_accel['x'])
		#plt.show()

		# Change range of data....
		gravity_accel['x'] = gravity_accel['x'][start_index:end_index]
		gravity_accel['y'] = gravity_accel['y'][start_index:end_index]
		gravity_accel['z'] = gravity_accel['z'][start_index:end_index]

		gyro = {}
		gyro['sec'] = gyro_data['seconds'][start_index:end_index]
		gyro['x'] = gyro_data['x'][start_index:end_index]
		gyro['y'] = gyro_data['y'][start_index:end_index]
		gyro['z'] = gyro_data['z'][start_index:end_index]

		# Labeled as high pass... but not high passed...
		gyro_hpf = {}
		gyro_hpf['x'] = gyro['x']
		gyro_hpf['y'] = gyro['y']
		gyro_hpf['z'] = gyro['z']


		# Find the angular position of sensors
		angular_pos = {}
		angular_pos['x'] = integrate.IMU(gyro['sec'], gyro_hpf['x'])
		angular_pos['x'] = [math.pi/180*x for x in angular_pos['x']]
		angular_pos['y'] = integrate.IMU(gyro['sec'], gyro_hpf['y'])
		angular_pos['y'] = [math.pi/180*x for x in angular_pos['y']]
		angular_pos['z'] = integrate.IMU(gyro['sec'], gyro_hpf['z'])
		angular_pos['z'] = [math.pi/180*x for x in angular_pos['z']]

		# Gravity vector...
		# A normalized gravity vector was made earlier.... not used...., but this is used...
		gravity_vector = mean_accel
		gravity_vector_holder = np.empty([3,len(accel['sec'])])

		accel_delta = {}
		accel_delta['x'] = [0] * len(accel['sec'])
		accel_delta['y'] = [0] * len(accel['sec'])
		accel_delta['z'] = [0] * len(accel['sec'])
		accel_delta_vector_holder = np.empty([3,len(accel['sec'])])

		accel2_delta = {}
		accel2_delta['x'] = [0] * len(accel['sec'])
		accel2_delta['y'] = [0] * len(accel['sec'])
		accel2_delta['z'] = [0] * len(accel['sec'])
		accel2_delta_vector_holder = np.empty([3,len(accel['sec'])])

		earth_accel_delta_vector_holder = np.empty([3,len(accel['sec'])])
		earth2_accel_delta_vector_holder = np.empty([3,len(accel['sec'])])
		forward_earth_accel_delta_vector_holder = np.empty([3,len(accel['sec'])])
		forward_position_delta_vector_holder = np.empty([3,len(accel['sec'])])

				
		# Main function?
		#plt.plot(gravity_accel['x'])
		#plt.plot(accel['x'])

		# Note this has a high executable time... need to optimize
		for i in range(0,len(accel['sec'])):

			# Calculate rotation
			# These are the basic rotational matrixes from linar algebra
			# Roll, pitch and yaw respectively

			rotation = {}

			rotation['x'] = np.empty([3,3])
			rotation['x'][0] = [1, 0, 0]
			rotation['x'][1] = [0, math.cos(angular_pos['x'][i]), \
					math.sin(angular_pos['x'][i])]
			rotation['x'][2] = [0, -1*math.sin(angular_pos['x'][i]), \
					math.cos(angular_pos['x'][i])]

			rotation['y'] = np.empty([3,3])
			rotation['y'][0] = [math.cos(angular_pos['y'][i]), 0, \
					-1*math.sin(angular_pos['y'][i])]
			rotation['y'][1] = [0, 1, 0]
			rotation['y'][2] = [math.sin(angular_pos['y'][i]), 0, \
					math.cos(angular_pos['y'][i])]

			rotation['z'] = np.empty([3,3])
			rotation['z'][0] = \
					[math.cos(angular_pos['z'][i]), math.sin(angular_pos['z'][i]), 0]
			rotation['z'][1] = \
					[-1*math.sin(angular_pos['z'][i]), math.cos(angular_pos['z'][i]), 0]
			rotation['z'][2] = [0, 0, 1]  

			# Why is it multiplied y to z to x? wiki says this is the order: z, y, x 
			# This order is due to where the gravity 
			# Matrix multiplication is not communitative
			# Gravity vector is the constant gravity on acceleromter (3x1)

			g_v = np.asarray(list(gravity_vector.values()))
			gravity_vector_holder[:,i] = rotation['y'] @ rotation['z'] @ rotation['x'] @ g_v

			# Difference between the measured acceleration and the direction of gravity
			# Should be actual acceleration value :)
			accel2_delta['x'][i] = accel['x'][i] - gravity_vector_holder[0,i]
			accel2_delta['y'][i] = accel['y'][i] - gravity_vector_holder[1,i]
			accel2_delta['z'][i] = accel['z'][i] - gravity_vector_holder[2,i]
			accel2_delta_vector_holder[:,i] = \
					[accel2_delta['x'][i], accel2_delta['y'][i], accel2_delta['z'][i]]


			# Rotation with removed initial gravitational vector... 
			updated_rotation = {}

			updated_rotation['x'] = np.empty([3,3])
			updated_rotation['x'][0] = [1, 0, 0]
			updated_rotation['x'][1] = \
					[0, math.cos(angular_pos['x'][i]), math.sin(angular_pos['x'][i])]
			updated_rotation['x'][2] = \
					[0, -1*math.sin(angular_pos['x'][i]), math.cos(angular_pos['x'][i])]

			updated_rotation['y'] = np.empty([3,3])
			updated_rotation['y'][0] = [math.cos(angular_pos['y'][i]+pitch), 0, \
					-1*math.sin(angular_pos['y'][i]+pitch)]
			updated_rotation['y'][1] = [0, 1, 0]
			updated_rotation['y'][2] = [math.sin(angular_pos['y'][i]+pitch), 0, \
					math.cos(angular_pos['y'][i]+pitch)]

			updated_rotation['z'] = np.empty([3,3])
			updated_rotation['z'][0] = [math.cos(angular_pos['z'][i]+yaw), \
					math.sin(angular_pos['z'][i]+yaw), 0]
			updated_rotation['z'][1] = [-1*math.sin(angular_pos['z'][i]+yaw), \
					math.cos(angular_pos['z'][i]+yaw), 0]
			updated_rotation['z'][2] = [0, 0, 1]  

			a = inv(updated_rotation['y'] @ updated_rotation['z'] @ updated_rotation['x'])

			earth2_accel_delta_vector_holder[:,i] = a @ accel2_delta_vector_holder[:,i]

			# Acceleration - Low passed acceleration
			# Output: Noise from accelerometer
			accel_delta['x'][i] = accel['x'][i] - gravity_accel['x'][i]
			accel_delta['y'][i] = accel['y'][i] - gravity_accel['y'][i]
			accel_delta['z'][i] = accel['z'][i] - gravity_accel['z'][i]
			accel_delta_vector_holder[:,i] = \
					[accel_delta['x'][i], accel_delta['y'][i], accel_delta['z'][i]]

			updated_gravity_strength = math.sqrt(gravity_accel['x'][i]**2 + \
					gravity_accel['y'][i]**2 + gravity_accel['z'][i]**2)	

			# Normalizing the low passed acceleration...
			# This doesn't really make sense... 
			# you are scaling each acceleration movement, but...
			# this means that there will be the same acceleration each entry... not true...

			updated_normal_mean_accel = {}
			updated_normal_mean_accel['x'] = gravity_accel['x'][i]/updated_gravity_strength
			updated_normal_mean_accel['y'] = gravity_accel['y'][i]/updated_gravity_strength
			updated_normal_mean_accel['z'] = gravity_accel['z'][i]/updated_gravity_strength
			
			# Update pitch and yaw with low-passed data
			new_ang = {}
			new_ang['y'] = math.atan(updated_normal_mean_accel['z']/\
					updated_normal_mean_accel['x']) # updated pitch
			new_ang['z'] = math.atan(updated_normal_mean_accel['y']/math.sqrt(\
					updated_normal_mean_accel['x']**2 + updated_normal_mean_accel['z']**2)) 
			# updated yaw

			# rotate so that the X axis points towards the earth
			# weird because only pitch and yaw rotation 
			# was not used for initial acceleration data, only LP accel

			updated_rotation['y'][0] = [math.cos(new_ang['y']), 0, -1*math.sin(new_ang['y'])]
			updated_rotation['y'][1] = [0, 1, 0]
			updated_rotation['y'][2] = [math.sin(new_ang['y']), 0, math.cos(new_ang['y'])]

			updated_rotation['z'][0] = [math.cos(new_ang['z']), math.sin(new_ang['z']), 0]
			updated_rotation['z'][1] = [-1*math.sin(new_ang['z']), math.cos(new_ang['z']), 0]
			updated_rotation['z'][2] = [0, 0, 1]

			updated_rotation['x'] = np.identity(3)
			
			# I have NO CLUE why we inverted the matrix multiplication
			a = inv(updated_rotation['y'] @ updated_rotation['z'] @ updated_rotation['x'])
			earth_accel_delta_vector_holder[:,i] = a @ accel_delta_vector_holder[:,i]
			
			# rotate so that Z axis is direction of travel?

			if (i>1):
				j = i + 1	

				# find position of non-filtered data...
				# double integration to get position
				coordinates = ['x', 'y', 'z']
				earth_position_temp = {}
				_, earth_position_temp['x'] = integrate.double(accel['sec'][:j], \
						earth_accel_delta_vector_holder[0,:j])
				earth_position_temp['y'] = integrate.IMU(accel['sec'][:j],\
						integrate.IMU(accel['sec'][:j],earth_accel_delta_vector_holder[1,:j]))
				earth_position_temp['z'] = integrate.IMU(accel['sec'][:j],\
						integrate.IMU(accel['sec'][:j],earth_accel_delta_vector_holder[2,:j]))
				
				position_strength = math.sqrt(earth_position_temp['x'][-1]**2 + \
						earth_position_temp['y'][-1]**2 + earth_position_temp['z'][-1]**2)

				# Normalize the distance moved? I don't see the point of this...
				normalized_mean_position = {}
				normalized_mean_position['x'] = earth_position_temp['x'][-1]/position_strength
				normalized_mean_position['y'] = earth_position_temp['y'][-1]/position_strength
				normalized_mean_position['z'] = earth_position_temp['z'][-1]/position_strength

				# Where did this come from?
				roll = math.atan(normalized_mean_position['y']/normalized_mean_position['z'])
				pitch = math.atan(-1*normalized_mean_position['x']/math.sqrt(\
						normalized_mean_position['y']**2 + normalized_mean_position['z']**2))
			
				updated_rotation['x'][0] = [1, 0, 0]	
				updated_rotation['x'][1] = [0, math.cos(roll), math.sin(roll)]
				updated_rotation['x'][2] = [0, -1*math.sin(roll), math.cos(roll)]

				updated_rotation['y'][0] = [math.cos(pitch), 0, -1*math.sin(pitch)]
				updated_rotation['y'][1] = [0, 1, 0]
				updated_rotation['y'][2] = [math.sin(pitch), 0, math.cos(pitch)]

				updated_rotation['z'] = np.identity(3)

				a = inv(updated_rotation['x'] @ updated_rotation['y'] @ updated_rotation['z'])
				
				forward_earth_accel_delta_vector_holder[:,i] = a @ \
						earth_accel_delta_vector_holder[:,i]
				forward_position_delta_vector_holder[:,i] = a @[earth_position_temp['x'][-1],\
						earth_position_temp['y'][-1], earth_position_temp['z'][-1]]
			
		""" NU START """
		# The hpf is only a subtraction of 0.18?
		accel_pure_delta_Hpf = {}
		accel_pure_delta_Hpf['z'] = [x - 0.18 for x in accel['z']] 

		# Calculate the velocity and the position through integration
		pure_velocity = {}
		pure_velocity['z'] = integrate.IMU(accel['sec'], accel_pure_delta_Hpf['z'])

		pure_position = {}
		pure_position['z'] = integrate.IMU(accel['sec'], pure_velocity['z'])
		""" NU END """

		# Integrating the noise to get velocity and position noise
		pure_delta_velocity, pure_delta_position = integrate.double(accel['sec'], accel_delta)

		# hpf is same as no filter
		# Storing Noise?
		accel_delta_hpf = {}
		accel_delta_hpf['x'] = accel_delta['x']
		accel_delta_hpf['y'] = accel_delta['y']
		accel_delta_hpf['z'] = accel_delta['z']

		#plt.plot(accel_delta['x'])
		#plt.show()

		# I double checked... it is noise... wtf
		# Anyways, integrate to get velocity and acceleration
		velocity, position = integrate.double(accel['sec'], accel_delta_hpf)

		# hpf is same as no filter...
		# Gravity vector MM with noise... 
		earth_accel_delta_hpf = {}
		earth_accel_delta_hpf['x'] = earth_accel_delta_vector_holder[0,:]
		earth_accel_delta_hpf['y'] = earth_accel_delta_vector_holder[1,:]
		earth_accel_delta_hpf['z'] = earth_accel_delta_vector_holder[2,:]


		# Find the position and velocity of noise MM gravity vector
		earth_velocity, earth_position = integrate.double(accel['sec'], earth_accel_delta_hpf)
		earth_velocity['z'] = [4*x for x in earth_velocity['z']]
		earth_position['z'] = [4*x for x in earth_position['z']]

		# Why print this variable?
		forward_earth_accel_delta_vector_holder[:, i]

		# Different gravity vector alignment...
		# x-axis aligned with gravity MM with noise
		# Multiply each vector
		forward_earth_accel_delta_hpf = {}
		forward_earth_accel_delta_hpf['x'] = forward_earth_accel_delta_vector_holder[0,:]
		forward_earth_accel_delta_hpf['y'] = forward_earth_accel_delta_vector_holder[1,:]
		forward_earth_accel_delta_hpf['z'] = forward_earth_accel_delta_vector_holder[2,:]

		# get velocity
		forward_earth_velocity = integrate.single(accel['sec'], forward_earth_accel_delta_hpf)
		# multiply it by 4? wtf
		forward_earth_velocity['z'] = [4*x for x in forward_earth_velocity['z']]
		# get position
		forward_earth_position = integrate.single(accel['sec'], forward_earth_velocity)

		# hpf is same as regular again...
		# Difference between measured acceleration and gravity
		# This should be actual values :)
		accel2_delta_hpf = deepcopy(accel2_delta)
		# get the velocity and position
		velocity2, position2 = integrate.double(accel['sec'], accel2_delta_hpf)

		# same as previous, except added rotation from initial gravitational vector throu MM 
		coordinates = ['x', 'y', 'z']

		earth2_accel_delta_hpf = {}
		for c,w in enumerate(coordinates):
			earth2_accel_delta_hpf[w] = earth2_accel_delta_vector_holder[c,:]

		earth2_velocity, earth2_position = integrate.double(accel['sec'], \
			earth2_accel_delta_hpf)

		# figures of all data 
		legend1 = ['gravity removed', 'hpf', 'velocity', 'position'] 

		# figure 1
		plt.figure()
		for axis in coordinates:
			plt.plot(time, [9.81*x for x in pure_delta_position[axis]])
		plt.title('pure delta position')
		plt.legend(coordinates)

		# figure 2
		plt.figure()
		plt.plot(time, [9.81*x for x in accel2_delta['z']])
		plt.plot(time, [9.81*x for x in accel2_delta_hpf['z']])
		plt.plot(time, [9.81*x for x in velocity2['z']])
		plt.plot(time, [9.81*x for x in position2['z']])
		plt.title('z 2')
		plt.legend(legend1)

		# figures 3-5
		for c, axis in enumerate(coordinates):
			plt.figure()
			plt.plot(time, [9.81*x for x in earth_accel_delta_vector_holder[c,:]])
			plt.plot(time, [9.81*x for x in earth_accel_delta_hpf[axis]])
			plt.plot(time, [9.81*x for x in earth_velocity[axis]])
			plt.plot(time, [9.81*x for x in earth_position[axis]])
			plt.title(axis + ' earth')
			plt.legend(legend1)

		# figures 6-8
		for c, axis in enumerate(coordinates):
			plt.figure()
			plt.plot(time, [9.81*x for x in forward_earth_accel_delta_vector_holder[c,:]])
			plt.plot(time, [9.81*x for x in forward_earth_accel_delta_hpf[axis]])
			plt.plot(time, [9.81*x for x in forward_earth_velocity[axis]])
			plt.plot(time, [9.81*x for x in forward_earth_position[axis]])
			plt.title(axis + ' forward earth')
			plt.legend(legend1)

		# figures 9-11
		for c, axis in enumerate(coordinates):
			plt.figure()
			plt.plot(time, [9.81*x for x in earth2_accel_delta_vector_holder[c,:]])
			plt.plot(time, [9.81*x for x in earth2_accel_delta_hpf[axis]])
			plt.plot(time, [9.81*x for x in earth2_velocity[axis]])
			plt.plot(time, [9.81*x for x in earth2_position[axis]])
			plt.title(axis + ' earth 2')
			plt.legend(legend1)


		# GC somehow initilizes tHS parameters....
		HS = {}
		stride_velocity = {}
		mean_stride_velocity = {}
		for i in range(0,5):
			HS[i] = {}
			stride_velocity[i] = {}
			mean_stride_velocity[i] = {}

		HS[0]['r'] = [6.17, 7.27, 8.3500, 9.41, 10.48,  11.6]
		HS[0]['l'] = [5.55,  6.7, 7.7900, 8.85,  9.92, 11.02]
		HS[1]['r'] = [6.13, 7.22, 8.3100, 9.37, 10.45,  11.56]
		HS[1]['l'] = [5.55,  6.68, 7.7600, 8.82,  9.89, 11]
		HS[2]['r'] = [15.09, 16.20, 17.24, 18.29, 19.35]
		HS[2]['l'] = [16.72,  17.76, 18.81]
		HS[3]['r'] = [23.07, 24.14, 25.21, 26.26, 27.37]
		HS[3]['l'] = [22.52, 23.61, 24.67, 25.74, 26.81]
		HS[4]['r'] = [31.05, 32.20, 33.29, 34.37, 35.49]
		HS[4]['l'] = [31.63, 32.74, 33.82, 34.92]


		# Calculate stride velocity by dividing the position by time
		# Heel strike position/time to heel strike
		
		# Deleted bug

		# Another place where HS and TO parameters are randomly found....
		# These paraamters are n ever used... wtf...
		TO = {}
		HS.update({'r':  [4.93, 6.17, 7.27, 8.35, 9.41, 10.48, 11.6, 12.78]})
		TO['r'] = [5.69, 6.83, 7.92, 8.98, 10.05, 11.16, 12.3]
		HS.update({'l': [5.55, 6.7, 7.79, 8.85, 9.92, 11.02, 12.17]})
		TO['l'] = [5.14, 6.31, 7.41, 8.48, 9.56, 10.63, 11.75, 12.88]

		# figure 12a
		orientation = ['r', 'l']
		legend1 = ['right HS', 'right TO', 'left HS', 'left TO']
		linestyles = ['c*', 'm*', 'bo', 'ro']

		plt.figure()
		plt.subplot(211)
		for i in range(0,3):
			plt.plot(time, earth_accel_delta_vector_holder[i,:])
		for c,i in enumerate(orientation,1):
			plt.plot(HS[i], [0] * len(HS[i]), linestyles[(c*2)-2])
			plt.plot(TO[i], [0] * len(TO[i]), linestyles[(c*2)-1])
		plt.legend(coordinates + legend1)

		# figure 12b
		plt.subplot(212)
		for axis in coordinates:
			plt.plot(time, gyro[axis])
		for c,i in enumerate(orientation, 1):
			plt.plot(HS[i], [0] * len(HS[i]), linestyles[c*2-2])
			plt.plot(TO[i], [0] * len(TO[i]), linestyles[c*2-1])
		plt.legend(coordinates + legend1)

		# Calculations
		fs = 100
		Ny = fs/2
		f_cuts = [10/Ny, 11/Ny]
		earth_filt = {}
		earth_filt['x'] = lowpass(earth_accel_delta_vector_holder[0,:], \
				f_cuts, fs, ripple_tol)

		gyro_filt = {}
		gyro_filt['z'] = gyro['z']

		# figure 13a
		plt.figure()
		plt.subplot(211)
		plt.plot(time, earth_filt['x'])
		plt.plot(time, difference.first(earth_filt['x'], 1))
		for c,i in enumerate(orientation, 1):
			plt.plot(HS[i], [0] * len(HS[i]), linestyles[c*2-2])
			plt.plot(TO[i], [0] * len(TO[i]), linestyles[c*2-1])
		plt.legend(['xaccel', 'x diff'] + legend1)

		# figure 13b
		plt.subplot(212)
		plt.plot(gyro['sec'], [500*x for x in angular_pos['z']])
		plt.plot(gyro['sec'], difference.first([500*x for x in angular_pos['z']], 20))
		plt.plot(gyro['sec'], gyro_filt['z'])
		for c,i in enumerate(orientation, 1):
			plt.plot(HS[i], [0] * len(HS[i]), linestyles[c*2-2])
			plt.plot(TO[i], [0] * len(TO[i]), linestyles[c*2-1])
		plt.legend(['z angle', 'z gyro', 'z diff'] + legend1)


		#plt.show(block=False)
		#plt.close('all')
		# GC's second file: feature identification
		# WHY THE FUCK DID HE MAKE THIS INTO A SECOND FILE... 
		# by: abhay gupta :)

		# rename angular_pos variable
		temp = deepcopy(angular_pos)
		angular_pos = {}
		angular_pos[0] = deepcopy(temp)

		# Find high-pass angular position for the z direction
		fs = 100
		cut = 0.5
		gyro2_hpf = {}
		gyro2_hpf['z'] = highpass(gyro['z'], fs, cut)
		angular_pos[1] = {}
		angular_pos[1]['z'] = integrate.IMU(gyro['sec'], gyro2_hpf['z'], units='rad')

		# Find low-pass angular position for the z direction
		fs = 100
		Ny = fs/2
		cut = [5/Ny,6/Ny]
		angular_pos[2] = {}
		angular_pos[2]['z'] = lowpass(angular_pos[1]['z'], cut, fs, ripple_tol)

		pos_ang_pos = {}
		pos_ang_pos['z'] = angular_pos[2]['z']
		pos_ang_pos['z'] = [0 if x < 0 else x for x in pos_ang_pos['z']]

		neg_ang_pos = {}
		neg_ang_pos['z'] = angular_pos[2]['z']
		neg_ang_pos['z'] = [0 if x > 0 else x for x in neg_ang_pos['z']]
		neg_ang_pos['z'] = list(map(abs, neg_ang_pos['z']))

		# Search for gyroscope peaks/troughs z-direction
		# Initializing approximate step ranges
		search_size = 40
		min_dist = my_round(1/3*100)
		max_dist = my_round(1/0.5*100)
		fs = 100

		# search for all the peak
		peaks,_,_,_ = find_peaks.forward(pos_ang_pos['z'], search_size, min_dist, \
				max_dist, fs)
		temp = list(reversed(pos_ang_pos['z']))
		backward_peaks,_,_,_ = find_peaks.forward(temp, search_size, min_dist, \
				max_dist, fs)
		temp = len(pos_ang_pos['z'])-1
		backward_peaks = list(reversed([temp-x for x in backward_peaks]))

		#combine peaks
		all_peaks = sorted(list(set(peaks + backward_peaks)))

		#search for all the troughs
		troughs,_,_,_ = find_peaks.forward(neg_ang_pos['z'], search_size, min_dist, \
				max_dist, fs)
		temp = list(reversed(neg_ang_pos['z']))
		backward_troughs,_,_,_ = find_peaks.forward(temp, search_size, min_dist, \
				max_dist, fs)
		temp = len(pos_ang_pos['z'])-1 # used positive again GC?
		backward_troughs = list(reversed([temp-x for x in backward_troughs]))

		all_troughs = sorted(list(set(troughs + backward_troughs)))

		all_troughs_peaks = sorted(all_peaks + all_troughs)

		# Search for accelerometer peaks/troughs x-direction
		# Initialize approximate step ranges
		search_size = 5
		min_dist = my_round(1/4*100)
		max_dist = my_round(1/0.4*100)
		fs = 100

		# find peaks x-direction
		accel_peaks,_,_,_ = find_peaks.forward(earth_filt['x'], search_size, min_dist, \
				max_dist, fs)
		temp = list(reversed(earth_filt['x']))
		backward_accel_peaks,_,_,_ = find_peaks.forward(temp, search_size, \
				min_dist, max_dist, fs)
		temp = len(earth_filt['x'])-1
		backward_accel_peaks = list(reversed([temp-x for x in backward_accel_peaks]))

		all_accel_peaks = sorted(list(set(accel_peaks + backward_accel_peaks)))
		all_accel_peaks = [] # WHAT THE FUCK GC CLEARING ALL THAT WORK

		# why did GC skip the last index? wtf...
		# Anyways.... calculates in-between peaks? smaller min dist...

		for i in range(0,len(all_troughs_peaks)-1):
			start_index = all_troughs_peaks[i]
			end_index = all_troughs_peaks[i+1]
			search_size = 5
			fs = 100
			min_dist = my_round(1/4*100)
			max_dist = len(earth_filt['x'][start_index:end_index+1])

			accel_peak,_,_,_ = find_peaks.forward(earth_filt['x']\
					[start_index:end_index+1], search_size, min_dist, max_dist, fs)
			
			accel_peak = [x+start_index for x in accel_peak]
			
			all_accel_peaks = all_accel_peaks + accel_peak

		# find differnce between acceleration data-points
		accel_first_diff = difference.first(earth_filt['x'],1)
		to_locations = []


		for i in range(0, len(all_accel_peaks)):

			start_index = all_accel_peaks[i]
			if i == len(all_accel_peaks)-1:
				end_index = len(earth_filt['x'])-11
			else:
				end_index = my_round(stats.mean([all_accel_peaks[i+1], \
						all_accel_peaks[i]]))

			if end_index <= start_index:
				end_index = end_index # absolutely idiotic GC...
			
			sig = accel_first_diff[start_index:end_index]
			
			to_location = start_index + sig.index(max(sig)) #GC subtracted 1 for no rs..

			search_min = to_location - 5
			search_max = to_location + 5+1
			sig = earth_filt['x'][search_min:search_max]
			to_location = search_min + sig.index(max(sig)) 
			to_locations.append(to_location) # plot the peaks and troughs of the data 
		# figure 14a
		plt.figure()
		plt.subplot(211)
		plt.plot(gyro['sec'], angular_pos[2]['z'])
		plt.plot([gyro['sec'][x] for x in all_peaks], [angular_pos[2]['z'][x] for x in \
			all_peaks], 'gx')
		plt.plot([gyro['sec'][x] for x in all_troughs], [angular_pos[2]['z'][x] for x \
			in all_troughs], 'c^')

		# Plot vertical lines at places of peaks and troughs
		[plt.axvline(gyro['sec'][x], color = 'g', linestyle = '--') for x in all_peaks]
		[plt.axvline(gyro['sec'][x], color = 'b', linestyle = '--')for x in all_troughs]

		# figure 14b
		plt.subplot(212)
		plt.plot(gyro['sec'], earth_filt['x'])
		plt.plot([accel['sec'][x] for x in all_accel_peaks], [earth_filt['x'][x] for x \
			in all_accel_peaks], 'gx')
		plt.plot([accel['sec'][x] for x in to_locations], [earth_filt['x'][x] for x in \
			to_locations], 'k^')
		plt.plot(accel['sec'], accel_first_diff)

		# add plots of the hs and to... came randomly
		for c,i in enumerate(orientation, 1):
			plt.plot(HS[i], [0] * len(HS[i]), linestyles[c*2-2])
			plt.plot(TO[i], [0] * len(TO[i]), linestyles[c*2-1])
		plt.legend(['xaccel', 'accel_peaks', 'to location', 'x diff'] + legend1)

		# Plot vertical lines at places of peaks and troughs
		[plt.axvline(gyro['sec'][x], color = 'g', linestyle = '--') for x in all_peaks]
		[plt.axvline(gyro['sec'][x], color = 'b', linestyle = '--')for x in all_troughs]

		patient_name = directory[-6:]
		plt.savefig('../../docs/fig1_' + patient_name + p + '.pdf')


		#^need to put legend on side of graph

		# finds all HS and TO :)
		HS['r'] = []
		HS['l'] = []
		TO['r'] = []
		TO['l'] = []


		for i in range(0,len(all_troughs)):
			if (i != len(all_troughs)-1):
				first_trough = all_troughs[i]
				second_trough = all_troughs[i+1]
				# find all the peaks between the troughs...
				peak = [x for x in all_peaks if first_trough < x < second_trough]
				if not peak:
					continue
				elif len(peak) > 1:
					peak = peak[0] # so only take in account first value? wtf...
					# right leg movement
					# find acceleration peaks between trough and peak
					accel_peak = [x for x in all_accel_peaks \
						if first_trough < x < peak]

					if (not not accel_peaks and len(accel_peak) == 1):
						accel_peak = accel_peak[0]
						HS['r'].append(accel_peak)
						to_location = [x for x in to_locations \
							if first_trough < x < peak]
						[TO['l'].append(x) for x in to_location]
				else:
					peak = peak[0] # so only take in account first value? wtf...
				
				# right leg movement (again?)
				# find acceleration peaks between trough and peak
				accel_peak = [x for x in all_accel_peaks \
					if first_trough < x < peak]

				if (not not accel_peaks and len(accel_peak) == 1):
					accel_peak = accel_peak[0]
					HS['r'].append(accel_peak)
					to_location = [x for x in to_locations \
						if first_trough < x < peak]
					[TO['l'].append(x) for x in to_location]

				# left leg movement
				accel_peak = [x for x in all_accel_peaks if peak < x < second_trough]

				if (not not accel_peak and len(accel_peak) == 1):
					accel_peak = accel_peak[0]
					HS['l'].append(accel_peak)
					to_location = [x for x in to_locations if peak < x < second_trough]
					[TO['r'].append(x) for x in to_location]
			else:
				first_trough = all_troughs[i]
				peak = [x for x in all_peaks if x > first_trough]
				if not not peak:
					peak = peak[0]
				else:
					continue
				
				# righ leg movement
				accel_peak = [x for x in all_accel_peaks if first_trough < x < peak]

				if (not not accel_peak and len(accel_peak) == 1):
					accel_peak = accel_peak[0]
					HS['r'].append(accel_peak)
					to_location = [x for x in to_locations if first_trough < x < peak]
					[TO['l'].append(x) for x in to_location]

## Analysis Plots

		# figure 15a
		
		plt.figure()
		plt.subplot(211)
		plt.plot(gyro['sec'], angular_pos[2]['z'])
		plt.plot([gyro['sec'][x] for x in all_peaks], \
			[angular_pos[2]['z'][x] for x in all_peaks], 'gx')
		plt.plot([gyro['sec'][x] for x in all_troughs], \
			[angular_pos[2]['z'][x] for x in all_troughs], 'c^')
		plt.legend(['z angular position', 'peak', 'trough'])

		# figure 15b

		plt.subplot(212)
		plt.plot(accel['sec'], earth_filt['x'])
		plt.plot(accel['sec'], accel_first_diff)
		for c, i in enumerate(orientation, 1):
			plt.plot([accel['sec'][x] for x in HS[i]],
				[earth_filt['x'][x] for x in HS[i]], linestyles[c*2-2])
			plt.plot([accel['sec'][x] for x in TO[i]],\
				[earth_filt['x'][x] for x in TO[i]], linestyles[c*2-1])
		plt.legend(['xaccel', 'x diff'] + legend1)

		# create output file with TO & HS data

		head = ['HS right', 'HS left', 'TO right', 'TO left']
		top = ['Data output for extracted HS and TO measurements'] 
		save_data[p] = {}
		save_data[p]['HS'] = {}
		save_data[p]['HS'] = HS
		save_data[p]['TO'] = {}
		save_data[p]['TO'] = TO

		plt.savefig('../../docs/' + patient_name + p + '.pdf')


	with open(os.path.join(directory, 'uprite_hs_to.pkl'), 'wb') as afile:
		pickle.dump(save_data, afile)   

	print("Completed HS & TO for patient: ", patient_name)
	print('Successful run!') 
	print('-----------RUNTIME: %s second ----' % (clocktime.time() - start_time))

def input_check(directory, folder_name):

	if (folder_type == 'n'):
		extract(directory)
	else:
		start_time = clocktime.time()
		# iterate through every patient file
		for c, filename in enumerate(os.listdir(directory)):
			if (c < 0):
				continue
			if filename == ".DS_store":
				continue

			print("Current patient iteration:", c)
			afile = os.path.join(directory, filename)
			extract(afile)

if __name__ == '__main__':
	print('Running test files... skipping GUI')

	#directory = '../../data_files/analyzed_data'
	#folder_type = 'y'
	directory = '../../data_files/analyzed_data/no_003'
	folder_type = 'n'

	#input_directory = '../../data_files/temp/Structs/'
	#gravity_input_dir = '../../data_files/temp/UR/gravity_windows'
	#data_input_dir = '../../data_files/temp/UR/data_windows'
	#output_directory = '../../data_files/temp/UR/test'

	input_check(directory, folder_type)


