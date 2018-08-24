####
# filename: type_check.py
# by: Abhay Gupta
# date: 08/29/18
#
# description: decide whether you need to loop through a directory


def initial_check(input_directory, output_directory, foldertype):
	"""Save matlab to python data depending on input folder type"""

	if (foldertype == 'n'):
		filename = input_directory
		extract(input_directory, output_directory, filename)
	else:
		for c, filename in enumerate(os.listdir(input_directory)): # Loop through files
			# Look for patient folders 
			if filename.endswith(".DS_Store"):
				continue
			else:
				# extracting patient number
				directory = os.path.join(input_directory, filename)
				extract(directory, output_directory, filename)

def loop_check(directory, function_name, foldertype):

	if (foldertype == 'n'):
		extract(directory)
	else:
		for c, filename in enumerate(os.listdir(input_directory)): # Loop through files
			# Look for patient folders 
			if filename.endswith(".DS_Store"):
				continue
			else:
				# extracting patient number
				directory = os.path.join(input_directory, filename)
				extract(directory, output_directory, filename)


	
