#####
# Extract GC's test mat file to dict file
# By: Abhay Gupta
#
#
#
#####

# import scipy.io as sio
import sys
import os
import math
import re
import pickle
import glob

# Function imports
p = os.path.abspath('../../../Data/Parsing Program/')
sys.path.append(p)

# Script imports
import mat_to_dict as convert
import print_struct as visual

# Initialize Files
input_directory = None
input_file = 'GC_test_data.mat'
output_directory = ''
name = 'no_001'

accel = convert.fn(input_file, input_directory)
data = {'UR': {'sensorData': {'tailBone': accel}}}
visual.print_all_keys(data)

with open(os.path.join(output_directory, name + '.pkl'), 'wb') as afile:
    pickle.dump(data, afile)
