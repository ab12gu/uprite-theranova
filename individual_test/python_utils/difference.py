# filename: difference
# by: abhay gupta
#
# date: 09/02/2018
#
# description: difference between values
# values are spaced by interval

def first(value, interval):
    first_diff = [0] * len(value)
    for i in range(interval, len(value)):
        first_diff[i] = value[i] - value[i - interval]

    return first_diff
