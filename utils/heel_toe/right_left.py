####
# filename: extract_uprite.py
# by: Abhay Gupta
# date: 09/04/18
#
# description: find hs and to of all data
####

def right_left(accel_peaks, all_gyro_spikes,  gyro_troughs, to_locations):
	"""finds all HS and TO :)"""

	HS = {}
	TO = {}
	HS['r'] = []
	HS['l'] = []
	TO['r'] = []
	TO['l'] = []
	
	for i in range(0,len(gyro_troughs)): #iterate through all troughs

		if (i != len(gyro_troughs)-1): # make sure i isn't last element

			# find all the peaks between the troughs...
			first_trough = gyro_troughs[i]
			second_trough = gyro_troughs[i+1]
			gyro_peak = [x for x in all_gyro_spikes if first_trough < x < second_trough]

			if not gyro_peak: #check if empty
				continue

			if len(gyro_peak) > 1: # more than single peak
				gyro_peak = gyro_peak[0] # so only take in account first value? wtf...

				# find acceleration peaks between gyro_trough and next_gyro_spike (window)
				accel_peak = [x for x in accel_peaks if first_trough < x < gyro_peak]

				if (accel_peaks and len(accel_peak) == 1): # if only 1 peak and there is acceleration peaks
					accel_peak = accel_peak[0] # remove out of list

					HS['r'].append(accel_peak) # right heel is after first gyro trough

					to_location = [x for x in to_locations if first_trough < x < gyro_peak] # find closest toe off (in same window)
					[TO['l'].append(x) for x in to_location] # save all toes offs in window
			else: # only 1 peak
				gyro_peak = gyro_peak[0] # list to float

			# find acceleration peaks between trough and peak
			accel_peak = [x for x in accel_peaks if first_trough < x < gyro_peak] 

			if (accel_peaks and len(accel_peak) == 1): # if only 1 peak and there is acceleration peaks
				accel_peak = accel_peak[0] # list to float

				# right heel is acceleration peak beween window (same as before)
				HS['r'].append(accel_peak)

				to_location = [x for x in to_locations if first_trough < x < gyro_peak] # find closest toe off (in same window)
				[TO['l'].append(x) for x in to_location] # save all toe offs in window

			# other leg movement
			accel_peak = [x for x in accel_peaks if gyro_peak < x < second_trough]

			if (accel_peak and len(accel_peak) == 1):
				accel_peak = accel_peak[0] # list to float

				HS['l'].append(accel_peak)

				to_location = [x for x in to_locations if gyro_peak < x < second_trough]
				[TO['r'].append(x) for x in to_location]

		else: # last element...
			first_trough = gyro_troughs[i]
			gyro_peak = [x for x in all_gyro_spikes if x > first_trough]

			if not gyro_peak:
				continue
			
			gyro_peak = gyro_peak[0] #save only first peak
	
			# last step is right foot step...
			accel_peak = [x for x in accel_peaks if first_trough < x < gyro_peak]

			if (accel_peak and len(accel_peak) == 1):
				accel_peak = accel_peak[0]

				HS['r'].append(accel_peak)

				to_location = [x for x in to_locations if first_trough < x < gyro_peak]
				[TO['l'].append(x) for x in to_location]

	return HS, TO


