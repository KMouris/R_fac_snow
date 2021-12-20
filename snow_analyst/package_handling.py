""" package_handling.py imports all the needed modules and packages to run the code """


# import all needed modules from the python standard library
try:
    import glob
    import logging
    import math
    import os
    import sys
    import time
    import datetime
    import calendar
    import re
except ModuleNotFoundError as b:
    print('ModuleNotFoundError: Missing basic libraries (required: glob, logging, math, os, sys, time, datetime, '
          'calendar, re')
    print(b)

# import additional python libraries
try:
    import gdal
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import rasterstats as rs
    import scipy
    from tqdm import tqdm
except ModuleNotFoundError as e:
    print('ModuleNotFoundError: Missing fundamental packages (required: gdal, maptlotlib.pyplot, numpy, '
          'pandas, rasterstats, scipy, tqdm')
    print(e)


# import geo_utils
try:
    sys.path.append(os.path.abspath(""))
    import geo_utils as gu
except ModuleNotFoundError:
    print("ModuleNotFoundError: Cannot import geo_utils")
