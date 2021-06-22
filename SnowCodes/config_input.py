
"""
Input configuration: Input files and folders that are constant for all programs
"""
# import all needed basic python libraries
try:
    import glob
    import logging
    import os
    import sys
    import time
    import datetime
    import calendar
    import re
except ModuleNotFoundError as b:
    print('ModuleNotFoundError: Missing basic libraries (required: glob, logging, os, sys, time, datetime, calendar, re')
    print(b)

# import additional python libraries
try:
    import gdal
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import rasterstats as rs
    import math
    import scipy
    from tqdm import tqdm
except ModuleNotFoundError as e:
    print('ModuleNotFoundError: Missing fundamental packages (required: gdal, maptlotlib.pyplot, numpy, '
          'pandas, rasterstats, scipy')
    print(e)

# sys.path.extend([f'./{name}' for name in os.listdir(".") if os.path.isdir(name)])

"""
Boolean variables to determine which programs to run and which input parameters to include 
    - run_pt_manipulation: 'True' to run precipitation and temperature manipulation file to obtain the .csv files which 
        are used in "Ero_Sno" to determine precipitation and snow rasters. 'False' to directly input the .csv files with 
        the temperature and precipitation values for each raster cell. 
    - run_ero_snow: 'True' to run Ero_Sno program to calculate rain and snow rasters, 'False' to input the snow and/or
     precipitation rasters directly for the snow_melt
    - run_snow_cover: "True" to run snow_cover code, 'False' to directly input the binary snow raster, to 
        calculate areas of snow from satellite images
    - run_satellite_image_clip_merge: 'True' to run si_clip_merge.py and merge and clip the input satellite images. 
        'False if user inputs previously clipped and merged satellite images. 
    - run_snow_melt: 'True' to run the python programs to calculate the snow at the end of the month and the total snow
        melt from the snow detection and snow rasters.
    - run_r_factor: 'True' to run the python program to calculate the R(ain) factor for the RUSLE model, from the rain
        rasters
    - run_total_factor: 'True' to calculate the total precipitation factor (rain + snow)
"""
run_pt_manipulation = False
run_rain_snow_rasters = False
run_snow_cover = False
run_satellite_image_clip_merge = False
run_snow_melt = True
run_r_factor = False
run_total_factor = False
# ------------------------------------------------------------------------------------------------------------------- #

"""
Files needed regardless of which codes to run: 
    -snapraster_path: path (including folder location, name and extension (must be .tif) with the raster to use as snap 
        (obtain projection, extension and raster resolution). It is usually the fildembanja.tif raster file 
    -shape_path = path (including folder location and name.shp) of shapefile to clip rasters with which to clip the 
        resulting raster with 
    -start_data, end_date: in YYYYMM format, determines the time interval to analyze for. If they are the same, only 
        one month will be analyzed and run_snow_melt will automatically turn to "False" 
    - results path: path where to save all results 
    - geo_utils_path: path where geoutils modules are located
"""
snapraster_path = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Snow_Codes\Modifications_MF\Input\DEM\fildemBanja.tif'
shape_path = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Snow_Codes\Modifications_MF\Input\Shapes\totalboundary.shp'
# shape_path = r'Y:\Abt1\hiwi\Oreamuno\GIS\ArcBanja_Jan20\catchment_banja_adap.shp'

# results_path = r'' + os.path.abspath('../Results')
results_path = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Snow_Codes\Modifications_MF\Git_scores\Results'

start_date = '201605'
end_date = '201804'

# path_geo_utils = r'C:\Users\Mouris\Desktop\Test_Snow\Test_Codes\geo-utils/'
path_geo_utils = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Snow_Codes\geo-utils/'
# ------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------- #
"""
If run_pt_manipulation = 'True'
- precipitation_path: folder path which contains .txt ASCII rasters with the precipitation data values for each time 
    interval. Each .txt file corresponds to the data for the given year-month-day-hour (The file name corresponds to the 
    date in the format YYYYMMDD_0HH)
- temperature_path: folder path which contains .txt ASCII rasters with the temperature data values for each time 
    interval. Each .txt file corresponds to the data for the given year-month-day-hour (The file name corresponds to the 
    date in the format YYYYMMDD_0HH)
"""
precipitation_path = r'' + os.path.abspath('../Input/Precipitation_Data/Precip_Banja_hourly_noCorr')
temperature_path = r'' + os.path.abspath('../Input/Temperature_Data')

"""
If Run_PTManipulation = 'False' (AND run_rain_snow_rasters = True) *************************************************************
    - PT_path = folder with precipitation and Temperature data, for each cell, for time span to analyze. Each file is
     a .csv file corresponding to the row_column of each cell. Each row in the array is a different year-month-day-hour.
     Each column is year-month-day-hour-minute-second-Precipitation-Temperature-Row-Column
    -  Original raster information: number or columns, number of rows, coordinates of lower left corner (xllcorner and 
        yllcorner), cellsize (cell resolution) and nodata value  
"""
PT_path_input = r'C:\Users\Mouris\Desktop\Test_Snow\Test_Codes\Results\PT_CSV_per_cell'
original_columns = 170
original_rows = 115
xllcorner = 350000.000000
yllcorner = 4445000.000000
cellsize = 1000
nodata = -9999.0

# ------------------------------------------------------------------------------------------------------------------- #
"""
If run_rain_snow_rasters = True: 
    - T_snow:minimum temperature threshold, very low value means the whole precipitation is considered as rain
    - Ero_S_results_folder: folder in which to save the snow_ero results (snow and precipitation rasters)
"""
T_snow = 0

"""
If run_rain_snow_rasters = False: (AND run_snow_melt is True OR run_r_factor is True) ********************************
snow_raster: folder path where .tif snow rasters are located (Needed for snow_melt calculation)
rain_raster: folder path where .tif rain rasters are located (needed for R factor calculation)
"""
# snow_raster_input = r'C:\Users\Mouris\Desktop\Test_Snow\Test_Codes\Results\snow_per_month'
snow_raster_input = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Snow_Codes\Modifications_MF\Results\snow_per_month'
rain_raster_input = r'C:\Users\Mouris\Desktop\Test_Snow\Test_Codes\Results\rain_per_month'
# ------------------------------------------------------------------------------------------------------------------- #

"""
If "run_snow_cover" = True: 
    - SI_folder path:  Folder with satellite images for a given date: folder must have a subfolder for each satellite 
        (e.g. one for TDL and one for TDK), The input files can be raw satellite images (located in folder 'image_
        _location_folder_name') or pre-processed (clipped and merged) .tif files. 
    - input_dates_si: boolean that determines if the user sets the image dates to use or if the program calculates the 
        dates automatically. if "True" the program uses the dates in si_image_dates. If "False" the program automatically uses 
    - image_list: Name of bands to merge, clip and resample. The name in the list must correspond to the final suffix of 
        the satellite image name. They must be in the following order: band02, band03, band04, band11
    - image_location_folder_name: Name of the folder in which the satellite images are directly located 
    - Thresholds for snow detection (NDSI, Red and Blue)
"""
SI_folder_path = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Satellite_data\Downloaded_MF'
# SI_folder_path = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Snow_Codes\Modifications_MF\Results\snow_cover\SatelliteImages'

input_si_dates = True
si_image_dates = [20161223]

image_list = ['B02', 'B03', 'B04', 'B11', 'TCI']
image_location_folder_name = "IMG_DATA"

# Thresholds for snow detection
NDSI_min = 0.4
blue_red_min = 0.85
blue_min = 1700

"""
If "run_snow_cover" = False (and run_snow_melt is True) *************************************************************
    -snowcover_raster_input: folder path where .tif binary snow cover rasters are located: 
"""
# snowcover_raster_input = r'C:\Users\Mouris\Desktop\Test_Snow\Test_Codes\Results\snow_cover'
snowcover_raster_input = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Snow_Codes\Modifications_MF\Results\snow_cover'
# ------------------------------------------------------------------------------------------------------------------- #
"""
If "run_snow_melt" is True: 
    -plot_statistic:  Boolean where if 'True', plots the snow melt statistics for a given input shapefile
    -shape_zone: Location of .shp file (can be different that clipping shape) in which to get snow melt statistics 
   statistic_param: Definition of statistical parameter to be plotted ('min', 'mean', 'max', 'range', 'sum', 'coverage')
"""
# Input for statistics
# Disable (False) or enable (True) plot
plot_statistic = True
# Location of shapefile used for zonal statistics (different from clipping shape)
shape_zone = r'' + os.path.abspath('../Input/Shapes/catchment_kokel.shp')
# Definition of statistical parameter to be plotted ('min', 'mean', 'max', 'range', 'sum', 'coverage')
statistical_param = 'coverage'

# Output folder for plots (DO NOT MODIFY)
plot_result = results_path + '\\Plots'

"""
If run_snow_melt is False (AND run_total_factor is True) *****************************************************
    - snow_melt_input: folder where .tif snow melt rasters are located (each file name must contain the date)
"""

# snow_melt_input = r'C:\Users\Mouris\Desktop\Test_Snow\Test_Codes\Results\Snowmelt'
snow_melt_input = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Snow_Codes\Modifications_MF\Results\Snowmelt'

# ------------------------------------------------------------------------------------------------------------------- #

"""
if run_Rfactor is True: 
    - fEl_path = path where the F(E,EL) raster is, including raster name and extension (must be .tif)

"""

fEL_path = r'C:\Users\Mouris\Desktop\Test_Snow\Test_Codes\Input\DEM\f_L_E.tif'

""" ****************************************************************************************************
if run_Rfactor is False (AND run_total_factor is True)
    -r_factor_input: folder path with .tif R factor rasters (with the raster name including the date)
"""

# r_factor_input = r'C:\Users\Mouris\Desktop\Test_Snow\Test_Codes\Results\R_factor_REM_db'
r_factor_input = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Snow_Codes\Modifications_MF\Results\R_factor_REM_db'
# ------------------------------------------------------------------------------------------------------------------- #

"""
if run_total_factor is True: 
    - snow_factor: factor with which to multiply the snow melt raster values to get the snow melt factor

"""
snow_factor = 2

# ------------------------------------------------------------------------------------------------------------------- #

# import geo_utils
try:
    sys.path.append(path_geo_utils)
    import geo_utils as gu
except ModuleNotFoundError:
    print("ModuleNotFoundError: Cannot import geo_utils")

# Import snow_melt codes:
sys.path.append('./snow_melt')  # Add folder for snow melt

# import Rfactor_REM codes:
sys.path.append('./Rfactor_REM_db')  # Add folder for snow melt

# ------------------------------------------------------------------------------------------------------------------- #
# Global Variables: DO NOT MODIFY

global PT_path         # Global raster to store the path with the per cell .CSV files with precipitation and temp data
global snow_raster_path       # folder path for snow raster data (including file name and .tif extension)
global rain_raster_path       # folder path for precipitation raster data (including file name and .tif extension)
global snow_cover_path        # folder path for snow cover binary raster (1 if satellite image shows snow, 0 if not)
global snow_melt_path         # folder path for snow melt rasters
global r_factor_path          # folder path for r factor rasters
global total_factor_path      # folder to save the total precipitation factor rasters


def init():
    global ascii_data  # Global variable to store the original ASCII raster data
    # Global variables from pt_raster_manipulation
    if run_pt_manipulation:
        ascii_data = []
    else:
        ascii_data = [original_columns, original_rows, xllcorner, yllcorner, cellsize, nodata]










