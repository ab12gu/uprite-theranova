####
# filename: print_hs_to.py
# by: Abhay Gupta
# date: 08/21/18
#
# description: create excel data of zeno and uprite to and hs data
####

# Library imports
import pickle
import os
import sys
import csv
import statistics as stats
from pathlib import Path

# global variables
top = ['Patient', 'System', 'Pace', 'Stride time', 'Right step time', \
       'Left step time', 'Double stance time', 'Cadence']


def extract(directory, output):
    """save to and hs data for uprite and zeno sensors"""

    pace = ['S', 'C', 'F']
    system = ['RS', 'UR']
    orientation = ['r', 'l']
    foot = ['HS', 'TO']

    patient_number = directory[-6:]
    print("Extrating data from patient: ", patient_number)

    # open files
    zeno_file = os.path.join(directory, 'zeno_hs_to.pkl')
    uprite_file = os.path.join(directory, 'uprite_hs_to.pkl')
    with open(zeno_file, 'rb') as afile:
        RS = pickle.load(afile)
    ur_file = Path(uprite_file)
    if ur_file.is_file():
        with open(uprite_file, 'rb') as afile:
            UR = pickle.load(afile)
    else:
        UR = {}

    # export hs and to data
    for p in pace:
        for o in orientation:
            for f in foot:
                if p not in UR.keys() or f not in UR[p].keys():
                    temp = [None]
                else:
                    UR[p][f][o] = [x / 100 for x in UR[p][f][o]]
                    temp = UR[p][f][o]
                output.writerow([patient_number, p, 'RS', o, f] + temp)
                output.writerow([patient_number, p, 'UR', o, f] + temp)
        output.writerow([])


def input_check(directory, foldertype):
    """Save matlab to python data depending on input folder type"""

    if (foldertype == 'n'):  # run single patient
        with open('../docs/hs_to_data.csv', 'a') as csvfile:
            output = csv.writer(csvfile)

            extract(directory, output)
    else:  # iterate through all patients
        with open('../docs/hs_to_data.csv', 'w') as csvfile:
            output = csv.writer(csvfile)
            output.writerow(top)

            for c, filename in enumerate(os.listdir(directory)):
                if (filename == '.DS_Store'):
                    continue
                afile = os.path.join(directory, filename)

                print("Current patient iteration: ", c)
                extract(afile, output)


if __name__ == '__main__':
    print('Running test files... skipping GUI')

    directory = '../../data_files/analyzed_data'
    foldertype = 'y'

    # directory = '../../data_files/analyzed_data/no_003'
    # foldertype = 'n'
    input_check(directory, foldertype)
