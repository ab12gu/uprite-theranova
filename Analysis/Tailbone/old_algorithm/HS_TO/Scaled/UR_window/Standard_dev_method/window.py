#
# filename: window.py
# 
# by: Abhay Gupta
#
# Description: Finds longest range of low standard deviation

# Finds the longest minimum standard deviation range
# Need to break into pairs, because no standard deviation of single value
# Worked well with threshold = 0.03 for accel_data of patient_009
def low_stdev(data, threshold):
	import statistics as stats
	from statistics import stdev
	
	list_so_far = []
	list_ending_here = []

	for i, x in enumerate(zip(data[::2], data[1::2]), 1):
		j = i*2
		x = list(x)
		if (stdev(x) < threshold):
			if (list_ending_here == []):
				list_ending_here = x
				temp_start_index = j
				temp_end_index = j+1
			elif not False in [abs(y - mean) < threshold for y in x]:
				list_ending_here.extend(x)
				temp_end_index += 2
			else:
				list_ending_here = x
				temp_start_index = j
				temp_end_index = j+1
			mean = stats.mean(list_ending_here)
		else:
			list_ending_here = []
		
		if (len(list_ending_here) > len(list_so_far)):
			list_so_far = list_ending_here[:]
			start_index = temp_start_index
			end_index = temp_end_index
		
	return [start_index, end_index]

# Records every low-stdev range
def all_low_stdev(data, threshold, size):
	import statistics as stats
	from statistics import stdev
	
	list_so_far = []
	list_ending_here = []
	interval = []
	for i, x in enumerate(zip(data[::2], data[1::2]), 1):
		j = i*2
		x = list(x)
		if (stdev(x) < threshold):
			if (list_ending_here == []):
				list_ending_here = x
				temp_start_index = j
				temp_end_index = j+1
			elif not False in [abs(y - mean) < threshold for y in x]:
				list_ending_here.extend(x)
				temp_end_index += 2
			else:
				list_ending_here = x
				temp_start_index = j
				temp_end_index = j+1
			mean = stats.mean(list_ending_here)
		else:
			list_ending_here = []
		
		if (size < len(list_ending_here) > len(list_so_far)):
			list_so_far = list_ending_here[:]
			start_index = temp_start_index
			end_index = temp_end_index
			interval.append([start_index, end_index])

	return interval
	
