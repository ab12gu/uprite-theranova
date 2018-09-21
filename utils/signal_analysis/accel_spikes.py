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

	import matplotlib.pyplot as plt

	# Calculations
	fs = 100
	Ny = fs/2
	f_cuts = [10/Ny, 11/Ny]
	ripple_tol = [0.001, 0.1]

	accel = lowpass(accel, f_cuts, fs, ripple_tol)

	# Search for accelerometer peaks/troughs -direction
	# Initialize approimate step ranges
	fs = 100
	search_size = 5
	min_dist = my_round(1/4*100)
	ma_dist = my_round(1/0.4*100)

	all_accel_peaks = []
	
	# search for acceleration peaks depending on gyroscope peak location
	for i in range(0,len(gyro_peaks)-1):

		start_index = gyro_peaks[i]
		end_index = gyro_peaks[i+1]

		search_size = 5
		fs = 100
		min_dist = my_round(1/4*100)
		ma_dist = len(accel[start_index:end_index+1])

		accel_peak = find_peaks.forward(accel[start_index:end_index+1], search_size, min_dist, ma_dist, fs)
		
		accel_peak = [x+start_index for x in accel_peak]
		
		all_accel_peaks = all_accel_peaks + accel_peak

	return(all_accel_peaks, accel)


