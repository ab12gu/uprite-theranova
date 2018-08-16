# filename: integrate_IMU
# by: Abhay Gupta
#
# Description: numerical integration of data
# -> Extremely simple... basically a single forward step integration
# -> Riemann right sum...

# GC skipped the first data point.... weird...
# Probably due to unnecessary added complication...

def IMU(time, data, units=None):
	import math
	result = [0] * len(time)
	for i in range(1, len(time)):
		result[i] = result[i-1] + data[i]*(time[i]-time[i-1]) 
	
	if units in ('rad', 'radians'):
		result = [math.pi/180*x for x in result]
	
	return result

# so GC constantly re-wrote the integration to get position and velocity.
# Let's just make this a whole lot simpiler...

def single(time, data, units=None):
	if isinstance(data, dict):
		output = {}
		for key in data:
			output[key] = IMU(time, data[key], units)
	else:
		output = IMU(time, data, units)
	
	return output

def double(time, data, units = None):
	output1 = single(time, data, units)
	output2 = single(time, output1, units)
	return output1, output2

