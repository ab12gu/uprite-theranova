####
# filename: struct_functions
# by: Abhay Gupta
# s-date: 7/11/2018
####

# evaluates how many lines are in a file
def file_len(fname):
	with open(fname) as f:
		for i, l in enumerate(f):
			pass
	return i+1

