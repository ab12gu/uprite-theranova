####
# filename: zeno_to_dict.py
# by: Abhay Gupta
#
# description: converts the RS data to a 2D numpy array
# also separates out initial pre-step data
####


def offset(directory):
	"""Reads first step info from xlsx file"""
	import glob
	from openpyxl import load_workbook
	import re

	filename = glob.glob(directory + '/' + 'Theranova*')  # extract filename

	# extract first step for each gait test type
	wb = load_workbook(filename=filename[0])
	ws = wb['Sheet1']
	output = []
	for i, row in enumerate(ws.rows):
		for column, cell in enumerate(row):
			string = cell.value
			if (string is None or string[0] > '9' and string[0] != "T"):
				continue
			if column == 1:
				step = re.findall(r'\d+', string)[-1]
				if (string.rfind('R') > string.rfind('L')):
					output.append('Right ' + step)
				else:
					output.append('Left ' + step)
	return output


def convert(RS_file, offset):
	"""Parsing through Zeno data"""
	from datetime import datetime
	import numpy as np
	import pandas as pd
	import re
	import itertools

	from utils.custom_functions.struct_functions import file_len

	# Show full arrays for np:
	np.set_printoptions(threshold=np.inf)

	# Data File
	header_size = 10
	a = np.genfromtxt(RS_file[0], delimiter=';', skip_header=header_size, usecols=np.arange(0,49),
						usemask=False, dtype=None, comments=None, encoding=None, missing_values='1')

	# Header File
	row_len = file_len(RS_file[0])
	a_size = (row_len - 1) - header_size

	b = np.genfromtxt(RS_file[0], delimiter=';', skip_footer=a_size, usecols=np.arange(0,2),
						usemask=False, dtype=None, comments=None, encoding=None, missing_values='1')

	# date_stamp data
	gender = b[1, 1]
	time_stamp = b[6, 1]
	time_stamp = datetime.strptime(time_stamp, '%m/%d/%Y %I:%M:%S %p')

	# Array labels
	row_labels = a[1:, 0]
	row_labels2 = a[1:, 1]
	np.put(row_labels2, [0, 3, 7, 8, 11], 'Total')

	# combine double row labels to single label
	for i in range(0, len(row_labels)):
		if (i < 14):
			row_labels[i] = row_labels.item(i) + '_' + row_labels2.item(i)
		else:
			row_labels[i] = row_labels2.item(i)

	col_labels = a[0, 2:]  # column labels

	# keep only data array
	a = np.copy(a[1:a_size, 2:50])

	# create a units table
	units_dict = {}
	i = 0
	for x in np.nditer(col_labels):
		if (i == 42):
			units1 = units_dict
			units_dict = {}
		x = np.array_str(x)
		w = x.split(' (', 1)
		if (len(w) == 2):
			units_dict[w[0]] = '(' + w[1]
		else:
			w = w[0].replace('.', ' ')
			w = w.split(' %', 1)
			if (len(w) == 2):
				units_dict[w[0]] = '%' + w[1]
			else:
				units_dict[w[0]] = None
		col_labels[i] = w[0]
		i += 1
	units2 = units_dict
	units = {1: units1, 2: units2}

	# secondary data set (averages of data)
	data2 = np.copy(a[3, 42:47])
	d_labels = np.copy(col_labels[42:47])
	data2 = pd.DataFrame(data2, d_labels)
	data2 = data2.to_dict()

	# primary data set (individual datapoints)
	begin = row_labels.tolist().index(offset)
	a = np.delete(a, range(42, 47), axis=1)
	a = np.delete(a, range(14, begin), axis=0)
	row_labels = np.delete(row_labels, range(14, begin), 0)
	col_labels = np.delete(col_labels, range(42, 47), 0)

	a = pd.DataFrame(a, index=row_labels, columns=col_labels)
	data1 = a

	# Method of accessing data
	# print(a.loc['#Samples_Total']['First Contact'])

	# Please note that you can change the dataframe back into a dict for consistent data acess:
	# data1 = data1.to_dict()

	# store all data structures under one dict
	zeno_dict = {'data': {1: data1, 2: data2[0]},'units': units, \
				'datetime': time_stamp,'gender': gender}

	return zeno_dict
