#####
# access_data.py
#
# By: Abhay Gupta
# Date: 07/05/18
#####

##### Notes #####
# Couldn't figure out how to step into a dict twice... Therefore use class/objects :)
# The name of each array isn't printed... you need to have a catalog of each structure:
# Hierarchy: x.sensorData.
# (leftAnkle, leftHip, rightAnkle, rightHip, tailBone.
# (accel, gyro, mag, baro).
# (sampRate, sampRateUnits, scale, scaleUnits, rawdata, data, filterData).
# (x,y,z,seconds)
#####

# Real File Path:



import scipy.io as sio

# inspect contents of file
sio.whosmat('imuData.mat')

# input data
mat_to_obj = sio.loadmat('imuData.mat', struct_as_record=False, squeeze_me=True)
time_stamp = mat_to_obj['__header__']

sensorData = mat_to_obj['sensorData']

accel_x = sensorData.tailBone.accel.data.x  # 1D array
accel_y = sensorData.tailBone.accel.data.y  # 1D array
accel_z = sensorData.tailBone.accel.data.z  # 1D array
time_step = sensorData.tailBone.accel.data.seconds  # 1D array

# Features:
accel_x.shape
type(accel_x)

# Call a value:
accel_x[1]
