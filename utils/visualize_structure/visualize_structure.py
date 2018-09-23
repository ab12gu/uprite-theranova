# prints the entire structure of the array

def print_all_keys(d, indent=0):
    for key, value in d.items():
        print('-' * indent + str(key))
        if isinstance(value, dict):
            print_all_keys(value, indent + 1)


def print_keys(d, level, indent=0):
    if indent >= level:
        return
    for key, value in d.items():
        print('-' * indent + str(key))
        if isinstance(value, dict):
            print_keys(value, level, indent + 1)


"""Notes on how to call variable"""
# for key,value in d['sensorData']['tailBone']['accel']['data'].items():
#     print(key)
