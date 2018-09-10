####
# filename: extract_uprite.py
# by: Abhay Gupta
# date: 09/04/18
#
# description: find hs and to of all data
####

import statistics as stats
from utils.data_structure_functions import difference
from utils.math_functions.general_math import my_round

def max_jerk(accel, accel_peaks):
	"""Use Jerk to find to, GC uncited"""

	# find differnce between acceleration data-points
	accel_first_diff = difference.first(accel,1)
	to_locations = []
	temp = []

	for i in range(0, len(accel_peaks)):

		# find large window
		start_index = accel_peaks[i] 

		if i == len(accel_peaks)-1: # if last element
			end_index = len(accel)-11 # reverse index offset...
		else:
			end_index = my_round(stats.mean([accel_peaks[i+1], accel_peaks[i]])) # index is center of peaks
	
		# find locaton of highest jerk
		sig = accel_first_diff[start_index:end_index] # half way to next peak
		to_location = start_index + sig.index(max(sig))
		temp.append(to_location)
	
		# refine window
		search_min = to_location - 5
		search_max = to_location + 5+1

		# find location of highest jerk
		sig = accel[search_min:search_max]
		to_location = search_min + sig.index(max(sig)) 
		to_locations.append(to_location) # plot the peaks and troughs of the data 

	return(to_locations, temp)


