#
# filename: std_window.py
#
# By: Abhay Gupta
#
# Description: Sliding window that checks when standard deviation is large
# source: https://gist.github.com/ximeg/587011a65d05f067a29ce9c22894d1d2/


def window(signal, width, threshold, influence):
	# threshold is multiple of allowable standard deviations	
	import statistics as stats
	
	# Initialize signal results
	output = [0] * len(signal)

	# Initialize filtered series
	filtered_signal = signal[0:width+1]

	# Initialize filters
	avg_filter = [0] * len(signal)
	std_filter = [0] * len(signal)

	# avg filter initilizes to mean of signal
	avg_filter[width - 1] = stats.mean(signal[0:width])
	std_filter[width - 1] = stats.stdev(signal[0:width])	

	for i in range(width+1, len(signal)):
		if (abs(signal[i] - avg_filter[i-1]) > threshold * std_filter[i-1]):
			# signal deviation < threshold
			if (signal[i] > avg_filter[i-1]):
				output[i] = 1 # positive influence	
			else:
				output[i] = -1 # negative influence
	
			# set influence level (1 = same value)
			filtered_signal[i] = influence*signal[i] + \
					(1-influence) * filtered_signal[i-1]

		else: # no threshold breach
			output[i] = 0 # within std
			filtered_signal[i] = signal[i] # Unnecessary...
		
		# adjust the filters
		avg_filter[i] = stats.mean(filtered_signal[i-width:i+1])
		std_filter[i] = 
= np.std(filteredY[(i-lag):i])




