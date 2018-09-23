import scipy.io as sio
import re
from pprint import pprint
import json


def fn(directory):
    mat_file = directory + '/imuData.mat'
    sio.whosmat(mat_file)

    # input data
    mat_to_obj = sio.loadmat(mat_file, struct_as_record=False, squeeze_me=True)

    """Reformating time_stamp to date: YYYY-MM-DD & time: hh:mm:ss"""
    time_stamp = mat_to_obj['__header__']
    time = time_stamp.decode("utf-8")
    time = time[-20:]
    date = time[:6] + time[-5:]
    time = time[7:15]

    """Re-organizing class & nested-objects"""

    sensorData = mat_to_obj['sensorData']

    return sensorData


    # accel_x = sensorData.tailBone.accel.data.x #1D array
    # accel_y = sensorData.tailBone.accel.data.y #1D array
    # accel_z = sensorData.tailBone.accel.data.z #1D array
    # time_step = sensorData.tailBone.accel.data.seconds #1D array

    # Features:
    # accel_x.shape
    # type(accel_x)

    # Call a value:
    # accel_x[1]
