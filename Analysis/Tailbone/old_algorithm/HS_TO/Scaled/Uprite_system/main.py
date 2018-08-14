#
# filename: main.py
# by: Abhay Gupta
#
# description: scaling GC's analyis file
#

import sys
import os

# Don't know if necessary rn...
p = os.path.abspath('../../../../../../Data/Parsing Program/')
sys.path.append(p)

p = os.path.abspath('../../../../Python/')
sys.path.append(p)

# Library imports
import pickle
import csv
import statistics as stats
import math
import matplotlib.pyplot as plt
plt.rcParams['lines.linewidth'] = 0.5
from numpy.linalg import inv
import time as clocktime
from copy import deepcopy


# Custom function imports
import filt
from math_func import my_round

starttime = clocktime.time()

pickle_file = 'no_001.pkl'
input_directory = '../../Python/'

# open data file
with open(input_directory + pickle_file, 'rb') as afile:
	data = pickle.load(afile)

# extract only raw tailbone data
accel_data = data['UR']['sensorData']['tailBone']['gyro']['data']
gyro_data = data['UR']['sensorData']['tailBone']['gyro']['data']

# data starts a 0; therefore first few points are garbage
accel_data['x'] = accel_data['x'][4:]
accel_data['x'] = accel_data['x'][4:]
accel_data['x'] = accel_data['x'][4:]

gyro_data['x'] = gyro_data['x'][4:]
gyro_data['x'] = gyro_data['y'][4:]
gyro_data['z'] = gyro_data['z'][4:]




