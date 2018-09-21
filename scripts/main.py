####
# filename: python_structure.py
# by: Abhay Gupta
# date: 08/29/18
#
# description: Run matlab_to_python conversion file
####

# standard library imports
from tkinter import Tk
from tkinter.filedialog import askdirectory

# custom library imports
from uprite.python_data_structure import input_check as create_structure
from uprite.flag_empty_data import input_check as check_uprite_data
from uprite.extract_zeno import input_check as extract_zeno
from uprite.data_window import input_check as data_window
from uprite.gravity_window import input_check as gravity_window
from uprite.extract_uprite import input_check as extract_uprite
from uprite.zeno_gait import input_check as zeno_gait
from uprite.uprite_gait import input_check as uprite_gait
from uprite.compare_gait import input_check as compare_gait
from uprite.print_hs_to import input_check as hs_to

# Ask for data location
Tk().withdraw() # prevent full GUI from opening

# input directory
print("Please select the folder containing raw data")
input_directory = askdirectory()
print("Selected input directory:", input_directory)
folder_type = input("Does the directory contain multiple patient's data? (y or n): ")

# output directory
print("Please select the output folder")
output_directory = askdirectory()
print("Selected all-patients output directory:", output_directory)
output_type = input("Will the directory store multiple patient's data? (y or n): ")

assert output_type == 'y', "The output needs to parent folder containing all patient's data"

create_structure(input_directory, output_directory, folder_type) # create python structure
check_uprite_data(output_directory, folder_type) # check how much data was recorded
extract_zeno(output_directory, folder_type) # extract zeno to & hs data
data_window(output_directory, folder_type) # extract data window
gravity_window(output_directory, folder_type) # extract gravity window
extract_uprite(output_directory, folder_type) # extract uprite to & hs data
zeno_gait(output_directory, folder_type) # calculates physical gait characteristics from TO/HS
uprite_gait(output_directory, folder_type) # calculates physical gait characteristics from TO/HS
compare_gait(output_directory, folder_type) # compare gait parameters
hs_to(output_directory, folder_type) # csv file for hs and to parameters







