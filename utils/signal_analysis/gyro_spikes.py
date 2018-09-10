####
# filename: gyro_peaks.py
# by: Abhay Gupta
# date: 09/04/18
#
# description: find spikes of angular position
####


from utils.math_functions.general_math import my_round
import matplotlib.pyplot as plt
from utils.signal_analysis import find_peaks
from utils.signal_analysis.filt import general as signal_filt
from utils.math_functions import integrate_IMU as integrate


def gyro_peaks(angular_pos, gyro):
	"""extract all peaks from gyroscope"""

	# keep only positive positions (peaks)
	pos_ang_pos = [0 if x < 0 else x for x in angular_pos]

	# search for all peaks
	fs = 100
	search_size = 40
	min_dist = my_round(1/3*100)
	max_dist = my_round(1/0.5*100)
	

	# forward peaks
	peaks = find_peaks.forward(pos_ang_pos, search_size, min_dist, max_dist, fs)

	# backward peask
	temp = list(reversed(pos_ang_pos))
	backward_peaks = find_peaks.forward(temp, search_size, min_dist, max_dist, fs)
	temp = len(pos_ang_pos)-1
	backward_peaks = list(reversed([temp-x for x in backward_peaks]))

	#combine peaks
	all_peaks = sorted(list(set(peaks + backward_peaks)))

	return(all_peaks)

def gyro_spikes(gyro):
	"""extract all peaks from gyroscope"""

	# initialize datastructures
	angular_pos = {}
	gyro_hpf = {}
	fs = 100
	ripple_tol = [0.001, 0.1]
	
	# high-pass + integration
	Ny = fs/2
	epsilon = 0.5
	cutoff = 0.5
	cut = [(cutoff-epsilon)/Ny,(cutoff+epsilon)/Ny]
	gyro_hpf['z'] = signal_filt(gyro['z'],  cut, fs, ripple_tol, 'high')
	angular_pos['z'] = integrate.IMU(gyro['sec'], gyro_hpf['z'], units='rad')

	#plt.figure()
	#plt.plot(gyro['z'])
	#plt.figure()
	#plt.plot(gyro_hpf['z'])
	#plt.show()

	# low-pass
	Ny = fs/2
	cut = [5/Ny,6/Ny]
	angular_pos['z'] = signal_filt(angular_pos['z'], cut, fs, ripple_tol, 'low')

	all_troughs = gyro_troughs(angular_pos['z'], gyro)
	all_peaks = gyro_peaks(angular_pos['z'], gyro)
	
	#plt.plot(gyro['sec'], angular_pos['z'])
	#plt.plot([gyro['sec'][x] for x in all_troughs], [angular_pos['z'][x] for x in all_troughs], 'c^')
	#plt.plot([gyro['sec'][x] for x in all_peaks], [angular_pos['z'][x] for x in all_peaks], 'co')
	#plt.show()

	all_spikes = sorted(all_peaks + all_troughs)

	return(all_spikes, all_peaks, all_troughs, angular_pos['z'])

def gyro_troughs(angular_pos, gyro):
	"""extract all troughs from gyroscope"""

	from utils.signal_analysis import find_peaks
	import matplotlib.pyplot as plt

	# keep only negative positions (troughs)
	neg_ang_pos = [0 if x > 0 else x for x in angular_pos]
	neg_ang_pos = list(map(abs, neg_ang_pos))	

	#plt.figure()
	#plt.plot(angular_pos['z'])
	#plt.figure()
	#plt.plot(neg_ang_pos['z'])
	#plt.show()

	# search for all troughs
	fs = 100
	search_size = 40
	min_dist = my_round(1/3*100)
	max_dist = my_round(1/0.5*100)
	
	# forward troughs
	troughs = find_peaks.forward(neg_ang_pos, search_size, min_dist, max_dist, fs)
	
	# backward troughs
	offset = list(reversed(neg_ang_pos))
	backward_troughs = find_peaks.forward(offset, search_size, min_dist, max_dist, fs)
	offset = len(neg_ang_pos)-1 # used positive again GC?
	backward_troughs = list(reversed([offset-x for x in backward_troughs]))

	all_troughs = sorted(list(set(troughs + backward_troughs)))
	return all_troughs


