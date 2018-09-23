####
# filename: math_functions.py
# by: Abhay Gupta
#
# description: custom math functions
####

# Removes idiotic rounding of python...
def my_round(x):
    import math
    return int(x + math.copysign(0.5, x))
