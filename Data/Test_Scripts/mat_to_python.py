#Convert the .mat data into a python readable program

import scipy.io as sio

mat_contents = sio.loadmat('../Theranova070/DATA.5.04_04_2018_10.25.17.915.AM/imuData.mat')
#mat_contents.items()/Users/newuser/Desktop/My Drive/Theranova/SW/UpRite_SW/uprite_analysis/Data/Parsed Data/KateHamelStudy_11_2017/Theranova01/DATA.5.11_03_2017_09.22.53.978.AM
mat_contents
