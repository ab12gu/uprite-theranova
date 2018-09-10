####
# filename: accel_peaks.py
# by: Abhay Gupta
# date: 09/05/18
#
# description: find all acceleration peaks
####


# Library imports
from numpy.linalg import inv
import numpy as np
import math

# custom function imports
from utils.math_functions.general_math import my_round
from utils.signal_analysis.filt import lowpass
from utils.signal_analysis import find_peaks


def accel_spikes(accel, gyro_peaks):
	"""Find peaks and troughs of acceleration data"""

	f_cuts = [0.1/50, 0.7/50] # Passband & Stopband cutoffs
	sampling_rate = 100 
	ripple_tol = [0.001, 0.1] # Passband & Stopband tolerances

	# create gravity vector by lowpass filtering acceleraiton data
	gravity_vector = {}
	gravity_vector['x'] = lowpass(accel['x'], f_cuts, sampling_rate, ripple_tol)
	gravity_vector['y'] = lowpass(accel['y'], f_cuts, sampling_rate, ripple_tol)
	gravity_vector['z'] = lowpass(accel['z'], f_cuts, sampling_rate, ripple_tol)
	
	# initialize variables
	accel_delta = {}
	accel_delta['x'] = [0] * len(accel['sec'])
	accel_delta['y'] = [0] * len(accel['sec'])
	accel_delta['z'] = [0] * len(accel['sec'])
	accel_delta_vector = np.empty([3,len(accel['sec'])])

	earth_accel_delta_vector = np.empty([3,len(accel['sec'])])

	rotation = {}
	rotation['x'] = np.empty([3,3])
	rotation['y'] = np.empty([3,3])
	rotation['z'] = np.empty([3,3])

	for i in range(0,len(accel['sec'])):

		# Rotation with removed initial gravitational vector... 

		# Remove gravity from acceleration vector
		accel_delta['x'][i] = accel['x'][i] - gravity_vector['x'][i]
		accel_delta['y'][i] = accel['y'][i] - gravity_vector['y'][i]
		accel_delta['z'][i] = accel['z'][i] - gravity_vector['z'][i]
		accel_delta_vector[:,i] = [accel_delta['x'][i], accel_delta['y'][i], accel_delta['z'][i]]

		# normalize gravity vector
		gravity_strength = math.sqrt(gravity_vector['x'][i]**2
									+ gravity_vector['y'][i]**2
									+ gravity_vector['z'][i]**2)	

		norm_grav = {}
		norm_grav['x'] = gravity_vector['x'][i]/gravity_strength
		norm_grav['y'] = gravity_vector['y'][i]/gravity_strength
		norm_grav['z'] = gravity_vector['z'][i]/gravity_strength

		# Create gravity based rotational vectors (allows to calibrate gravity as you walk)
		grav_ang = {}
		grav_ang['y'] = math.atan(norm_grav['z']/norm_grav['x']) # updated pitch
		grav_ang['z'] = math.atan(norm_grav['y']/math.sqrt(norm_grav['x']**2 + norm_grav['z']**2)) 
		
		rotation['x'] = np.identity(3)

		rotation['y'][0] = [math.cos(grav_ang['y']), 0, -1*math.sin(grav_ang['y'])]
		rotation['y'][1] = [0, 1, 0]
		rotation['y'][2] = [math.sin(grav_ang['y']), 0, math.cos(grav_ang['y'])]

		rotation['z'][0] = [math.cos(grav_ang['z']), math.sin(grav_ang['z']), 0]
		rotation['z'][1] = [-1*math.sin(grav_ang['z']), math.cos(grav_ang['z']), 0]
		rotation['z'][2] = [0, 0, 1]
		
		# I have NO CLUE why we inverted the matrix multiplication
		a = inv(rotation['y'] @ rotation['z'] @ rotation['x'])
		earth_accel_delta_vector[:,i] = a @ accel_delta_vector[:,i]

	
	# Calculations
	fs = 100
	Ny = fs/2
	f_cuts = [10/Ny, 11/Ny]
	ripple_tol = [0.001, 0.1]
	earth_filt = {}
	earth_filt['x'] = lowpass(earth_accel_delta_vector[0,:], f_cuts, fs, ripple_tol)

	# Search for accelerometer peaks/troughs x-direction
	# Initialize approximate step ranges
	fs = 100
	search_size = 5
	min_dist = my_round(1/4*100)
	max_dist = my_round(1/0.4*100)

	all_accel_peaks = []
	
	# search for acceleration peaks depending on gyroscope peak location
	for i in range(0,len(gyro_peaks)-1):

		start_index = gyro_peaks[i]
		end_index = gyro_peaks[i+1]

		search_size = 5
		fs = 100
		min_dist = my_round(1/4*100)
		max_dist = len(earth_filt['x'][start_index:end_index+1])

		accel_peak = find_peaks.forward(earth_filt['x'][start_index:end_index+1], 
										search_size, min_dist, max_dist, fs)
		
		accel_peak = [x+start_index for x in accel_peak]
		
		all_accel_peaks.append(accel_peak)

	return(all_accel_peaks)


