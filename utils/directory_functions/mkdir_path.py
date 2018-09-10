# found online

from errno import EEXIST
from os import makedirs,path

def mkdir_path(mypath):
    '''Creates a directory. equivalent to using mkdir -p on the command line'''

    try:
        makedirs(mypath)
    except OSError as exc: # Python >2.5
        if exc.errno == EEXIST and path.isdir(mypath):
            pass
        else: raise

