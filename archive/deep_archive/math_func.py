# filename: math_func
# by: abhay gupta
#
# Description: self-produced mathematical functions
#

import math


# Removes idiotic rounding of python...
def my_round(x):
    return int(x + math.copysign(0.5, x))
