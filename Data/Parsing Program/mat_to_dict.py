import scipy.io
import numpy as np
import re

# Convert .mat file to python dict
def fn(filename, directory):
	"""reconstructing dictionaries... To fix remaining mat-objects to key:values"""
	data = scipy.io.loadmat(filename, struct_as_record=False, squeeze_me=True)
	return _check_keys(data, directory)		   


# Below functions are called by loadmat

# Record time-stamp
def time(struct, directory):
	from datetime import datetime
	if directory == None:
		time_stamp = None
	else:
		time_stamp = directory[-26:]
		time_stamp = datetime.strptime(time_stamp, '%m_%d_%Y_%I.%M.%S.%f.%p')
	
	struct['datetime'] = time_stamp
	
	return struct

# Remove unwanted keys
def clean(struct):

	struct.pop('__header__', None)
	struct.pop('__globals__', None)
	struct.pop('__version__', None)
	
	return struct

# Other data manipulation functions
def _check_keys(data, directory):
	for key in data:
		if isinstance(data[key], scipy.io.matlab.mio5_params.mat_struct):
			data[key] = _todict(data[key])
	data = time(data, directory)
	data = clean(data)
	return data

def _todict(matobj):
	d = {}
	for strg in matobj._fieldnames:
		elem = matobj.__dict__[strg]
		if isinstance(elem, scipy.io.matlab.mio5_params.mat_struct):
			d[strg] = _todict(elem)
		elif isinstance(elem, np.ndarray):
			d[strg] = _tolist(elem)
		else:
			d[strg] = elem
	return d

def _tolist(ndarray):
	elem_list = []
	for sub_elem in ndarray.tolist():
		if isinstance(sub_elem, scipy.io.matlab.mio5_params.mat_struct):
			elem_list.append(_todict(sub_elem))
		elif isinstance(sub_elem, np.ndarray):
			elem_list.append(_tolist(sub_elem))
		else:
			elem_list.append(sub_elem)
	return elem_list


