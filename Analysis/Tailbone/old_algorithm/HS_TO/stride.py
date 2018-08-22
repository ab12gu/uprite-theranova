# filename: stride.py
# by: abhay gupta
# 8/1/2018
#
# Description: simply finds velocity based on position...

def vel(time, position, velocity, hs_locations):
	import statistics as stats

	stride_velocity = []
	mean_stride_velocity = []

	for i in range(0,len(hs_locations)-1):
		
		indices = [round(x*100) for x in time]
		start_index = indices.index(round(hs_locations[i]*100))
		end_index = indices.index(round(hs_locations[i+1]*100))
		
		stride_velocity = stride_velocity + [9.81 * (position[end_index] - \
				position[start_index])/(time[end_index]-time[start_index])]
		
		mean_stride_velocity = mean_stride_velocity + [9.81* \
				stats.mean(velocity[start_index:(end_index+1)])]

	return stride_velocity, mean_stride_velocity
