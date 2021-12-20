
"""
config_input.py contains the required user input (e.g. input and output folder paths, settings for the statistical
calculation) and the handling of packages.
"""
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


"""Boolean variables to determine which modules to run and which input parameters to include:
    - run_pt_manipulation: 'True' to run 'pt_raster_manipulation' code to obtain the .csv files which are used in
        "rain_snow_rasters.py" to determine precipitation and snow rasters. 'False' to directly input the .csv
        files with the temperature and precipitation values for each raster cell.
    - run_ero_snow: 'True' to run Ero_Sno program to calculate rain and snow rasters, 'False' to input the snow and/or
        precipitation rasters directly.
    - run_snow_cover: 'True' to run 'snow_cover.py' code, 'False' to directly input the binary snow raster, to calculate
        areas of snow cover from satellite images.
    - run_satellite_image_clip_merge: 'True' to run si_clip_merge.py and merge and clip the raw input satellite images.
        'False' if user sets previously clipped and merged satellite images.
    - run_snow_melt: 'True' to run the python programs to calculate the snow at the end of the month and the total snow
        melt from the snow detection and snow rasters.
    - run_r_factor: 'True' to run the python program to calculate the R(ain) factor for the RUSLE model, from the rain
        rasters.
    - run_total_factor: 'True' to calculate the total precipitation factor (rain + snow) """
run_pt_manipulation = True
run_rain_snow_rasters = True
run_snow_cover = False
run_satellite_image_clip_merge = False
run_snow_melt = True
run_r_factor = True
run_total_factor = True

""" Files needed regardless of which codes to run:
    - snapraster_path: string, path (including name.ext) of raster with which to snap (obtain projection, extension and
        raster resolution). It is usually DEM raster file.
    - shape_path: string, path (including folder location and name.shp) of shape file with which to clip resulting
     rasters
    - results path: string, path where to save all results.
    - start_date, end_date: string in YYYYMM format, determines the time interval to analyze for. If they are the same,
        only one month will be analyzed and run_snow_melt will automatically turn to "False".
    - geo_utils_path: string, path where geoutils package is located."""
snapraster_path = r'' + os.path.abspath('../input/DEM/fildemBanja.tif')
shape_path = r'' + os.path.abspath('../input/Shapes/totalboundary.shp')
results_path = r'' + os.path.abspath('../results')

# start_date = '201605'
start_date = '201712'
end_date = '201804'

"""If run_pt_manipulation = 'True'
- precipitation_path: string, folder path which contains .txt ASCII rasters with the precipitation data values for each
    time interval. Each .txt file corresponds to the data for the given year-month-day-hour. The file name corresponds
    to the date in the format YYYYMMDD_0HH.
- temperature_path: string, folder path which contains .txt ASCII rasters with the temperature data values for each time
     interval. Each .txt file corresponds to the data for the given year-month-day-hour. The file name corresponds to
    the date in the format YYYYMMDD_0HH."""
precipitation_path = r'' + os.path.abspath('../input/Precipitation_Data/Precip_daily_Banja_v2')
temperature_path = r'' + os.path.abspath('../input/Temperature_daily')


"""If run_pt_manipulation = 'False' (AND run_rain_snow_rasters = True)
- PT_path: string, folder path with precipitation and Temperature data. There must be a folder each month in the
    analysis  time span. Each folder contains .csv files for each cell in the final raster, whose name corresponds to
    row_column of each cell. Each row in the array is a different year-month-day-hour. The format of the column is
    year-month-day-hour-minute-second-Precipitation-Temperature-Row-Column.
-  Original raster information: Number of columns, number of rows, coordinates of lower left corner (xllcorner and
    yllcorner), cellsize (cell resolution) and nodata value."""

PT_path_input = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Snow_Codes\Modifications_MF\results\PT_CSV_per_cell'
original_columns = 170
original_rows = 115
xllcorner = 350000.000000
yllcorner = 4445000.000000
cellsize = 1000
nodata = -9999.0

""" If run_rain_snow_rasters = True:
- T_snow: float with minimum temperature threshold to detect snowfall, very low value means the whole precipitation is
    considered as rain."""
T_snow = 0

""" If run_rain_snow_rasters = False: (AND run_snow_melt is True OR run_r_factor is True)
- snow_raster: string, folder path where .tif snow rasters are located (needed for snow_melt calculation)
- rain_raster: string, folder path where .tif rain rasters are located (needed for R factor calculation)"""
snow_raster_input = r'/home/IWS/mouris/Desktop/Test_snow_codes_seb/R_fac_snow/results/snow_per_month/'
rain_raster_input = r'/home/IWS/mouris/Desktop/Test_snow_codes_seb/R_fac_snow/results/rain_per_month/'

""" If "run_snow_cover" = True:
- si_folder_path: string, folder path where satellite images are: each folder must correspond to a sensing date,
    with the date in the name. The input files can be raw satellite images  or pre-processed (clipped and merged)
    .tif files. If raw images are given, then each folder must have a subfolder for each satellite analyzed (e.g.
    one for TDL and one for TDK), and the images must be located in a folder called 'image__location_folder_name'.
- input_si_dates: Boolean that determines if the user sets the image dates to use or if the program calculates the
    dates automatically. If "True" the program uses the dates in si_image_dates list. If "False" the program
    automatically uses the sensing date closest to the end of each month for all months.
- si_image_dates: LIST with sensing dates to use (in YYYYMMDD format) when input_si_dates is 'True'. The program
    determines to which month the input date corresponds. The user can set a sensing date for each month or just
    for some. For the months not set in the list, the program uses the date closest to the end of the month.
- image_list: LIST with Name of bands to merge, clip and resample. The name in the list must correspond to the final
    suffix of the satellite image name. They must be in the following order: band02, band03, band04, band11, TCI.
- image_location_folder_name: String with name of the folder in which the raw satellite images are directly located.
    *Only needed if 'run_satellite_image_clip_merge' = 'True'
    *Note that if using L2A images, if 'IMG_DATA' is set as folder name, the module will use R10 images, when available,
    and R20 for the rest. If 'R20m' is set as the folder name, all bands with a resolution of 20 will be used.

- NDSI_min: float with NDSI threshold for snow detection.
- blue_min: float with Blue band threshold for snow detection."""
si_folder_path = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Satellite_data\Downloaded_MF'
# si_folder_path = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Satellite_data\Converted_L2A'

input_si_dates = False
si_image_dates = [20161223]

image_list = ['B02', 'B03', 'B11', 'TCI']
image_location_folder_name = "IMG_DATA"

# Thresholds for snow detection
NDSI_min = 0.4
blue_min = 1800

"""
If "run_snow_cover" = False (and run_snow_melt is True)
- snowcover_raster_input: string, folder path where .tif binary snow cover rasters are located."""

snowcover_raster_input = r'/home/IWS/mouris/Desktop/Test_snow_codes_seb/R_fac_snow/results/snow_cover'


"""If "run_snow_melt" is True:
- plot_statistic: Boolean where if 'True', plots the snow melt statistics for a given input shapefile.
- shape_zone: string, location of .shp file (can be different that clipping shape) in which to get snow melt statistics.
- statistic_param: string with definition of statistical parameter to be plotted ('min', 'mean', 'max', 'range',
'sum', 'coverage') """
# Input for statistics
# Disable (False) or enable (True) plot
plot_statistic = True
# Location of shapefile used for zonal statistics (different from clipping shape)
shape_zone = r'' + os.path.abspath('../input/Shapes/catchment_kokel.shp')
# Definition of statistical parameter to be plotted ('min', 'mean', 'max', 'range', 'sum', 'coverage')
statistical_param = 'coverage'

# Output folder for plots (DO NOT MODIFY)
plot_result = os.path.join(results_path, 'Plots')

"""If run_snow_melt = False (AND run_total_factor = True)
- snow_melt_input: string, folder path where .tif snow melt rasters are located (each file name must contain the date)
"""

snow_melt_input = r'C:\Users\Mouris\Desktop\Test_Snow\Test_Codes\results\Snowmelt'
# snow_melt_input = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Snow_Codes\Modifications_MF\Git_codes\R_fac_snow\results\Snowmelt'

"""If run_Rfactor = True:
- fEl_path: string, path where the f(E,EL) raster is, including raster name and extension (must be .tif).
"""
fEL_path = r'' + os.path.abspath('../input/DEM/f_L_E.tif')

""" If run_Rfactor is False (AND run_total_factor is True)
- r_factor_input: string, folder path with .tif R factor rasters (with the raster name including the date).
"""
r_factor_input = r'C:\Users\Mouris\Desktop\Test_Snow\Test_Codes\results\R_factor_REM_db'
# r_factor_input = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Snow_Codes\Modifications_MF\results\R_factor_REM_db'

"""If run_total_factor is True:
- snow_factor: (float or int) Factor with which to multiply the snow melt raster values to get the snow melt erosivity.
"""
snow_factor = 2

# ------------------------------------------------------------------------------------------------------------------- #

# import geo_utils
try:
    sys.path.append(os.path.abspath(""))
    import geo_utils as gu
except ModuleNotFoundError:
    print("ModuleNotFoundError: Cannot import geo_utils")

# Import snow_melt codes:
sys.path.append('./snow_melt')  # Add folder for snow melt

# import Rfactor_REM codes:
sys.path.append('./Rfactor_REM_db')  # Add folder for snow melt

def initialize_ascii():
    global ascii_data  # Global variable to store the original ASCII raster data
    # Global variables from pt_raster_manipulation
    if run_pt_manipulation:
        ascii_data = []
    else:
        ascii_data = [
            original_columns,
            original_rows,
            xllcorner,
            yllcorner,
            cellsize,
            nodata,
            ]
