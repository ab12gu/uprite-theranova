# filename: peaks.py
# by: abhay gupta
#
# date: 9/3/18
#
# description: find peaks?

# GC's notes: (why the fuck is he talking about ecg?)
# findRRpeaks: locates the R peaks of the ecg signal
# ecg is the ecg signal (WTF)
# fs is the rate of sample (okay...)

# get the filtered ECG value
# update 9/29/2016. ecg is not filtered. For full algorithm, which does a 
# backwards and forward analyssi, use findRRpeaks(ecg, fs) (wtf...)


def forward(signal, search_size, min_distance, max_distance, fs):
	import difference
	import numpy as np
	import math
	import statistics as stats
	# find difference between values of signal
	first_diff = {}
	first_diff['norm'] = difference.first(signal, 1)
	first_diff['abs'] = first_diff['norm'] # no absolute value? wtf 	

	# define windows for smallest and largest possible steps
	slow_step = max_distance
	fast_step = min_distance
	time_window = max_distance

	window_counter = 0

	# define a binary range?
	old_max_value = 2**32
	old_min_value = -2**32

	# arbitrary factors?
	high_threshold_scale_factor = 5/8
	low_threshold_scale_factor = 1/4
	
	high_to_low = 0
	low_to_high = 0
	high_threshold_met = 0
	low_threshold_met = 0

	max_value = 2**32
	min_value = 2**32

	# initialize values?
	last_peak_loc = 0
	avg_value_buffer = [0] * time_window
	
	# Find max/min of signal differences
	# Only takes in account first time window? where time-win defined as 
	# max step distance...
	# Range checked to be correct
	old_max_value = max(first_diff['abs'][:time_window]) #should iter?
	old_min_value = min(first_diff['abs'][:time_window]) #same?
	high_threshold = old_max_value*high_threshold_scale_factor #scaled down?
	avg_value = stats.mean(first_diff['abs'][:time_window])
	low_threshold = avg_value

	
	# HIGH-THRES - cutoff for high accelation range (logical)
	# LOW-THRES - cutoff using mean accelartion? (kinda logical)

	# wtf.. GC randomly reversed max/min values
	max_value = -2**32
	min_value = 2**32
	
	# initializing terms
	low_to_high_locs = []
	high_to_low_locs = []
	peaks_found = []
	avg_value_buffer = []

	# used for post analysis and plotting
	old_max_values = [old_max_value] # first range max value
	old_min_values = [old_min_value] # first range min value
	high_thresholds = [high_threshold]
	low_thresholds = [low_threshold]
	window_intervals = [1]
	avg_values = [avg_value]

	# Main analysis?
	for i in range(0,len(first_diff['abs'])): #range should be len(signal)-1
		if (window_counter <= time_window): #starts at 0, till max_step_size

			# find the min and max value in this window (wtf min max are opp)
			max_value = max(first_diff['abs'][i], max_value) # find largest dif
			min_value = min(first_diff['abs'][i], min_value) # find minim diff
			avg_value_buffer.append(first_diff['abs'][i]) # current dif...

			if (first_diff['abs'][i] > high_threshold): # current dif vs dif thres
				if not high_threshold_met: # if met value is false
					high_threshold_met = 1 # change to true
					if low_threshold_met: #parameter set from prior iteration?
						low_to_high_locs.append(i) 
						low_to_high = 1 # what
						low_threshold_met = 0 # reset the low threshold met flag
			elif (first_diff['abs'][i] < low_threshold):
				if not low_threshold_met:
					low_threshold_met = 1
					if high_threshold_met: # Check prev thres
						high_to_low_locs.append(i)
						high_to_low = 1
						high_threshold_met = 0#reset the high threshold met flag

						# peak has been found... now record it
						if low_to_high == 1 and high_to_low == 1:
							# locate the local maximum in this area of the sign
							last_low_to_high = low_to_high_locs[-1]- search_size
							if (last_low_to_high < 0):
								last_low_to_high = 0 # make sure min >= 0
							
							last_high_to_low = high_to_low_locs[-1]+ search_size
							if (last_high_to_low > len(signal)):
								last_high_to_low = len(signal) 

							# location of max value 
							sig = signal[last_low_to_high:last_high_to_low+1]
							local_peak_loc = sig.index(max(sig))
							
							peak_loc = local_peak_loc + last_low_to_high
							
							# check if is within usual human step range
							if (peak_loc - last_peak_loc) >= fast_step and \
								(peak_loc - last_peak_loc) <= slow_step:
								peaks_found.append(peak_loc)

							# reset the last stored peak location
							last_peak_loc = peak_loc

							low_to_high = 0
							high_to_low = 0
						else:
							low_to_high = 0
							high_to_low = 0
			window_counter += 1

		if (window_counter >= time_window):
			old_max_value = max_value
			old_min_value = min_value
			high_threshold = old_max_value* high_threshold_scale_factor
			avg_value = stats.mean(avg_value_buffer)
			low_threshold = avg_value

			max_value = -2^32
			min_value = 2^23

			old_max_values.append(old_max_value)
			old_min_values.append(old_min_value)
			high_thresholds.append(high_threshold)
			low_thresholds.append(low_threshold)
			window_intervals.append(i)
			avg_values.append(avg_value)

			window_counter = 0
	
	if len(peaks_found) > 1:
		heart_rate = fs/stats.mean([60*x for x in difference.first(peaks_found, 1)])
	else:
		heart_rate = None
	
	return peaks_found, low_to_high_locs, high_to_low_locs, heart_rate

























	
