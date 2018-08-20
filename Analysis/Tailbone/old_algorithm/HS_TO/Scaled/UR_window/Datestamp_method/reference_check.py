#
# filename: reference_check.py
#
# by: Abhay Gupta
#
# Date: 08/14/18
#
# Description: create an analysis file for datetime for UR && RS
#


def extract(data, RS_data, padding):
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
			
		interval[w] = [window_start, window_end]

	UR_log = data['UR']['sensorData']['tailBone']['accel']['data']['seconds']
	UR_log2 = data['UR']['sensorData']['tailBone']['accel']['data']['z']
	len_RS = offset + end_last_step
	len_UR = len(UR_log)/100
	
	return(interval, len_RS, len_UR, window, recording_offset)

