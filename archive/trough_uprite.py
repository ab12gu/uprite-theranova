####
# filename: extract_uprite.py
# by: Abhay Gupta
# date: 08/20/18
#
# description: run GC's to & hs algorithm on all uprite data/gravity windows
####

# Library imports
import sys
import os
import pickle
import statistics as stats
import math
import matplotlib.pyplot as plt
import time as clocktime
from copy import deepcopy
from numpy.linalg import inv
import numpy as np

# Custom function imports
from utils.math_functions.general_math import my_round
from utils.signal_analysis.filt import lowpass
from utils.signal_analysis.filt import highpass
from utils.math_functions import integrate_IMU as integrate
from utils.math_functions import stride
from utils.data_structure_functions import difference
from utils.signal_analysis import find_peaks

# Change plot line width
plt.rcParams['lines.linewidth'] = 0.5

# global variables
coordinates = ['x', 'y', 'z']
pace = ['S', 'C', 'F']
orientation = ['r', 'l']


def open_files(directory):
    data_file = os.path.join(directory, 'python_struct.pkl')
    data_window_file = os.path.join(directory, 'data_window.pkl')
    gravity_window_file = os.path.join(directory, 'gravity_window.pkl')
    with open(data_file, 'rb') as afile:
        data = pickle.load(afile)  # Import all patient data
    with open(data_window_file, 'rb') as afile:
        data_wdw = pickle.load(afile)  # Import data windows
    with open(gravity_window_file, 'rb') as afile:
        grav_wdw = pickle.load(afile)  # Import gravity windows

    return (data, data_wdw, grav_wdw)


def extract(directory):
    """extract all the hs & to data from uprite sensor"""
    global coordinates
    global orienation
    global pace

    start_time = clocktime.time()  # record clocktime
    save_data = {}

    # Extract Patient Number
    patient_name = directory[-6:]
    print("Extracting data for patient:", patient_name)

    # Open data_file, gravity_window, data_window
    data, data_wdw, grav_wdw = open_files(directory)

    # Take out acceleration and gyroscope data from tailbone
    accel_all = data['UR']['sensorData']['tailBone']['accel']['data']
    gyro_all = data['UR']['sensorData']['tailBone']['gyro']['data']

    # Round all window coordinates
    for p in pace:
        for i in range(0, 2):
            data_wdw[p][i] = my_round(data_wdw[p][i])
            grav_wdw[i] = my_round(grav_wdw[i])

    print('Interval for motion data:', data_wdw)
    print('Interval for gravity data:', grav_wdw)

    # Check if not enough data
    if (data_wdw['flag']['F'] == 0):
        print('Not enough accel-data recorded')
        return
    elif data_wdw['F'][1] > len(gyro_all['x']):
        print("Not enough gyro data", data_wdw['F'][1], len(gyro_all['x']))
        return

    ### MAY BE UNNEC
    mean_accel = dict()
    for w in coordinates:  # gravity vector
        mean_accel[w] = stats.mean(accel_all[w][grav_wdw[0]:grav_wdw[1]])

    # Initialize variables
    accel = dict()
    gyro = dict()

    # Iterate through slow, calm, fast paces
    for p in pace:

        # cut data with windows
        for w in coordinates:
            accel[w] = accel_all[w][data_wdw[p][0]:data_wdw[p][1]]
            gyro[w] = gyro_all[w][data_wdw[p][0]:data_wdw[p][1]]
        gyro['sec'] = gyro_all['seconds'][data_wdw[p][0]:data_wdw[p][1]]
        accel['sec'] = accel_all['seconds'][data_wdw[p][0]:data_wdw[p][1]]

        ####

        # rename angular_pos variable
        angular_pos = {}

        # Find high-pass angular position for the z direction
        fs = 100
        cut = 0.5
        gyro2_hpf = {}
        gyro2_hpf['z'] = highpass(gyro['z'], fs, cut)
        angular_pos[1] = {}
        angular_pos[1]['z'] = integrate.IMU(gyro['sec'], gyro2_hpf['z'],
                                            units='rad')

        # Find low-pass angular position for the z direction
        fs = 100
        Ny = fs / 2
        cut = [5 / Ny, 6 / Ny]
        angular_pos[2] = {}
        angular_pos[2]['z'] = lowpass(angular_pos[1]['z'], cut, fs, ripple_tol)

        neg_ang_pos = {}
        neg_ang_pos['z'] = angular_pos[2]['z']
        neg_ang_pos['z'] = [0 if x > 0 else x for x in neg_ang_pos['z']]
        neg_ang_pos['z'] = list(map(abs, neg_ang_pos['z']))

        # Search for gyroscope peaks/troughs z-direction
        # Initializing approximate step ranges
        search_size = 40
        min_dist = my_round(1 / 3 * 100)
        max_dist = my_round(1 / 0.5 * 100)
        fs = 100

        # search for all the troughs
        troughs, _, _, _ = find_peaks.forward(neg_ang_pos['z'], search_size,
                                              min_dist, \
                                              max_dist, fs)
        temp = list(reversed(neg_ang_pos['z']))
        backward_troughs, _, _, _ = find_peaks.forward(temp, search_size,
                                                       min_dist, \
                                                       max_dist, fs)
        temp = len(neg_ang_pos['z']) - 1  # used positive again GC?
        backward_troughs = list(reversed([temp - x for x in backward_troughs]))

        all_troughs = sorted(list(set(troughs + backward_troughs)))

        plt.plot(gyro['sec'], angular_pos[2]['z'])
        plt.plot([gyro['sec'][x] for x in all_troughs],
                 [angular_pos[2]['z'][x] for x \
                  in all_troughs], 'c^')

        plt.show()

        ####

        quit()

        #############################################################################################################################
        plt.savefig('../../docs/' + patient_name + p + '.pdf')

    with open(os.path.join(directory, 'uprite_hs_to.pkl'), 'wb') as afile:
        pickle.dump(save_data, afile)

    print("Completed HS & TO for patient: ", patient_name)
    print('Successful run!')
    print(
        '-----------RUNTIME: %s second ----' % (clocktime.time() - start_time))


def input_check(directory, folder_name):
    if (folder_type == 'n'):
        extract(directory)
    else:
        start_time = clocktime.time()
        # iterate through every patient file
        for c, filename in enumerate(os.listdir(directory)):
            if (c < 0):
                continue
            if filename == ".DS_store":
                continue

            print("Current patient iteration:", c)
            afile = os.path.join(directory, filename)
            extract(afile)


if __name__ == '__main__':
    print('Running test files... skipping GUI')

    # directory = '../../data_files/analyzed_data'
    # folder_type = 'y'
    directory = '../../data_files/analyzed_data/no_003'
    folder_type = 'n'

    # input_directory = '../../data_files/temp/Structs/'
    # gravity_input_dir = '../../data_files/temp/UR/gravity_windows'
    # data_input_dir = '../../data_files/temp/UR/data_windows'
    # output_directory = '../../data_files/temp/UR/test'

    input_check(directory, folder_type)
