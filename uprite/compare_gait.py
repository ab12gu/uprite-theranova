####
# filename: compare_gait.py
# by: Abhay Gupta
# date: 09/21/18
#
# description: compare properties of zeno & uprite TO_HS
####

# Library imports
import pickle
import os
import csv
import logging
import argparse
from enum import Enum
from pathlib import Path


class PaceTypes(Enum):
    SLOW = 'S'
    CALM = 'C'
    FAST = 'F'


class GaitTypes(Enum):
    STRIDE = 'stride'
    RIGHT_STEP = 'right_step'
    LEFT_STEP = 'left_step'
    DOUBLE_STANCE = 'double_stance'
    RIGHT_SINGLE_STANCE = 'right_single_stance'
    LEFT_SINGLE_STANCE = 'left_single_stance'
    CADENCE = 'cadence'


def extract(directory, output):
    """Compare gait of zeno and uprite system"""
    # iterate through each patient file
    patient_number = directory[-6:]
    print("Extrating data from patient: ", patient_number)

    """Extract Pickle Data"""
    zeno = extract_zeno_pickle_data(directory)
    uprite = extract_uprite_pickle_data(directory)

    """Find Gait Parameters from HS & TO"""
    error_by_pace = get_error_by_pace(uprite, zeno)

    """Add data to csv_file"""
    for p in PaceTypes:
        output.writerow([patient_number, p.value] + error_by_pace[p.value])

    return


def get_error_by_pace(gait_names, uprite, zeno):
    error_per_pace = {}
    for p in PaceTypes:
        error_per_pace[p.value] = []

        for gait_name in gait_names:
            error = get_gait_percent_error(gait_name, p, uprite, zeno)
            error_per_pace[p.value].append(error)
    return error_per_pace


def get_gait_percent_error(gait_name, p, uprite, zeno):
    if uprite[p.value] is None:
        error = None
    else:
        UR = uprite[p.value][gait_name]
        ZN = zeno[p.value][gait_name]
        if UR is None:
            error = None
        else:
            error = (UR - ZN) / ZN
    return error


def extract_zeno_pickle_data(directory):
    zeno_file = os.path.join(directory, 'zeno_gait.pkl')
    with open(zeno_file, 'rb') as afile:
        zeno = pickle.load(afile)
    return zeno


def extract_uprite_pickle_data(uprite_file):
    file_check = Path(uprite_file)
    if not file_check.is_file():
        logging.error("File not found at {}".format(uprite_file))
        uprite = {}
        for p in PaceTypes:
            uprite[p.value] = None
    else:
        with open(uprite_file, 'rb') as afile:
            uprite = pickle.load(afile)
    return uprite


def input_check(directory, output_file, do_append):
    if do_append:
        with open(output_file, "a") as dst:
            csv_writer = csv.writer(dst)
    else:
        with open(output_file, "w") as dst:
            csv_writer = csv.writer(dst)
            csv_writer.writerow(header)

    if os.path.isdir(directory):
        subdirectories = os.listdir(directory)
        for subdirectory in subdirectories:
            if not os.path.isdir(subdirectory):
                continue
            extract(subdirectory, csv_writer)
    else:
        extract(directory, csv_writer)


def parse_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--directory",
                            help="The directory where the source data files "
                                 "are located.",
                            type=str,
                            required=True)
    arg_parser.add_argument("--output_file",
                            help="The CSV file to output data to.",
                            type=str,
                            required=True)
    arg_parser.add_argument("--append",
                            help="Indicates that the output file should be "
                                 "appended to.",
                            type="store_true")
    args = arg_parser.parse_args()
    return args


if __name__ == '__main__':
    print('Running test files... skipping GUI')
    args = parse_args()
    input_directory = args.directory
    output_file = args.output_file
    do_append = args.append
    input_check(input_directory, output_file, do_append)
