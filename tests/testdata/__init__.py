import os
import glob

datadir = os.path.abspath(os.path.dirname(__file__))


def get_data_files():
    if os.name == 'nt':
        pattern = os.path.join(datadir, 'nt', '*.yaml')
    else:
        pattern = os.path.join(datadir, 'unix', '*.yaml')
    files = glob.glob(pattern)

    pattern_noplatform = os.path.join(datadir, '*.yaml')
    files += glob.glob(pattern_noplatform)

    filesdict = {}
    for fn in files:
        key = os.path.splitext(os.path.basename(fn))[0]
        filesdict[key] = fn
    return filesdict
