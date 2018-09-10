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

# Records every low-stdev range O(n)
def all_low_stdev(data, threshold, size):
	import statistics as stats
	from statistics import stdev
	
	list_so_far = []
	list_ending_here = []
	interval = []
	temp_start_index = temp_end_index = 0
	list_size = 0
	list_sum = 0

	for i, x in enumerate(zip(data[::2], data[1::2]), 1):
		j = i*2
		x = list(x)
		if (stdev(x) < threshold):
			if (list_ending_here == []):
				list_ending_here = x
				temp_start_index = j
				temp_end_index = j+1
				mean = stats.mean(list_ending_here)
				list_size = 0
				list_sum = 0
			elif not False in [abs(y - mean) < threshold for y in x]:
				list_ending_here.extend(x)
				temp_end_index += 2
				list_size += 2
				list_sum = sum([list_sum] + x)
				mean = list_sum/list_size
			else:
				if ((temp_end_index - temp_start_index) > size):
					interval.append([temp_start_index, temp_end_index, \
						temp_end_index - temp_start_index])
				list_ending_here = x
				temp_start_index = j
				temp_end_index = j+1
				mean = stats.mean(list_ending_here)
				list_size = 0
				list_sum = 0
		else:
			if ((temp_end_index - temp_start_index) > size):
				interval.append([temp_start_index, temp_end_index, \
						temp_end_index-temp_start_index])
			list_ending_here = []
		
		if (size < len(list_ending_here) > len(list_so_far)):
			list_so_far = list_ending_here[:]
			start_index = temp_start_index
			end_index = temp_end_index
	
	if (end_index == j+1):
		interval.append([start_index, end_index, end_index-start_index])	
	
	temp = []
	if (interval[0][0] != 0):
		start = 0
		end = interval[0][0]
		temp.append([start, end, end-start])
	for i in range(0,len(interval)-1):
		start = interval[i][1]
		end = interval[i+1][0]
		temp.append([start, end, end-start])
	if (interval[-1][1] < len(data)-1):
		start = interval[-1][1]
		end = len(data)-1
		temp.append([start, end, end-start])

	intervals = {}
	intervals['steady'] = interval
	intervals['unsteady'] = temp
	
	return intervals

# Uses datestamp of Reference System to find window
def datestamp(data, RS_data, padding = 0):	
	from datetime import datetime
	UR_time = data['UR']['datetime']
	
	step = ['HS', 'TO']
	orientation = ['r', 'l']
	window = []
	
	# Find difference between start of recording data
	pace = ['S', 'C', 'F']
	RS_time = []
	interval = {}
	
	for c, w in enumerate(pace):
		
		RS_steps = []
		RS_time.append(data['RS'][w]['datetime'])
	
		interval[w] = {}

		for i in orientation:
			for j in step:
				RS_steps = RS_steps + RS_data[w][j][i]
		start_first_step = min(RS_steps)
		end_last_step = max(RS_steps)
		window.append(end_last_step - start_first_step)

		recording_offset = (RS_time[0] - UR_time).total_seconds()
		offset = (RS_time[c] - RS_time[0]).total_seconds()	

		window_start = (start_first_step + offset) + recording_offset - padding
		window_end = (end_last_step + offset) + recording_offset + padding
			
		interval[w] = [window_start, window_end, window_end-window_start]

	UR_log = data['UR']['sensorData']['tailBone']['accel']['data']['seconds']
	UR_log2 = data['UR']['sensorData']['tailBone']['accel']['data']['z']
	len_RS = offset + end_last_step
	len_UR = len(UR_log)/100
	
	#return(interval, len_RS, len_UR, window, recording_offset)
	return interval

# finds the window closest to current window
def search(window, data):
	from utils.math_functions.general_math import my_round

	start = window[0]
	end = window[1]
	span = end - start
	distance = 0	

	index = 0
	for i, window in enumerate(data):
		import statistics as stats	
	
		if window[2] > 1/3*span:
			
			start_dif = abs(start - window[0])
			end_dif = abs(end - window[1])
			temp = start_dif + end_dif
			
			if distance < 1/temp:
				distance = 1/temp
				index = i

	start = data[index][0]
	end = data[index][1]

	if (data[index][2] < span):
		center = (start + end)/2
		start = center - span/2
		end = center + span/2

	start = my_round(start)
	end = my_round(end)

	return (start, end) 










