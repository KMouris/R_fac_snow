"""Main algorithm which the different .py programs to calculate the total R factor for month or group of months,
for the RUSLE method.

It calls the following files in the following order:
 *pt_raster_manipulation.py: generates .csv files with temperature and precipitation data for each date in the
 analysis period.
 *rain_snow_rasters.py:  generates monthly snow and rain rasters from input precipitation and temperature data.
 *snow_cover.py: Detects areas of snow from input satellite (Sentinel2) data and returns a binary data raster,
  where 1 equals an area of snow and 0 no snow
 *snow_melt_main.py: generates rasters with monthly snow melt data for each month being analyzed
 *Rfactor_main.py: generates rasters with the precipitation R factor, using the equation by Diodato, N. & Bellochi, G.
 (2007)
 *total_R_factor.py: calculates the snow melt R factor and generates rasters with the total R factor values, per month,
 as a the sum of the precipitation and snow melt R factor.
"""

import config_input
import file_management
import pt_raster_manipulation
import rain_snow_rasters
import snow_cover
import total_R_factor
import wasim_snow
from Rfactor_REM_db import Rfactor_main
from package_handling import *
from snow_melt import snow_melt_main

if __name__ == '__main__':

    # initialize ascii data
    config_input.initialize_ascii()

    # Generate a list with all the dates to run through and include in the analysis
    date_list = file_management.get_date_list(config_input.start_date, config_input.end_date)

    #  RUN PT_raster_manipulation
    # Generate .csv files with daily/hourly precipitation and temperature per input raster cell
    if config_input.run_pt_manipulation:
        print("Generating .csv files from precipitation and temperature data")
        # Run PT_Manipulation to get .csv files with precipitation and temperature data
        if config_input.start_date.strftime('%Y%m') == config_input.end_date.strftime('%Y%m'):  # If only one date
            pt_raster_manipulation.generate_csv(date=config_input.start_date)
        else:  # if more than one date is being run
            for date in date_list:
                pt_raster_manipulation.generate_csv(date)
        print("Finished running PT_raster manipulation.")

    # RUN rain_snow_rasters
    # Generate the rain and snow rasters from the precipitation and temperature  in .csv files
    if config_input.run_rain_snow_rasters:
        print("Generating rain and snow rasters")
        # save all contents in the folder to a list
        csv_list = os.listdir(config_input.PT_path)
        # Check if more folders or if there are .csv files (to determine if 1 run or multiple)
        # If any .csv files in folder, loop through 1 folder
        if any(".csv" in string for string in csv_list):
            rain_snow_rasters.generate_rain_snow_rasters(config_input.PT_path)
        else:  # Loop through each sub-folder
            # clip csv_list to include only dates within input range
            csv_list = file_management.filter_raster_lists(
                csv_list, config_input.start_date, config_input.end_date, "rain_snow_rasters.py")
            for date in csv_list:  # Run code for each folder (date) at a time
                path = os.path.join(config_input.PT_path, date)
                rain_snow_rasters.generate_rain_snow_rasters(path)
        print("Finished rain and snow raster generation")

    # RUN snow_cover
    # Generate a binary snow detection raster, to determine cells with snow
    if config_input.run_snow_cover:
        # list with satellite image folders
        si_list = os.listdir(config_input.si_folder_path)
        if config_input.input_si_dates:  # If user inputs the dates to use:
            si_list = file_management.check_input_si_dates(
                si_list, date_list, config_input.si_image_dates)
        else:  # get images whose sensing date is closest to end of month
            if len(si_list) == 2:  # if only 2 folders, only one sensing date was given
                si_list = [os.path.basename(config_input.si_folder_path)]
            # If no dates to directly use (user input), get the satellite image closest to the end of the month.
            si_list = file_management.generate_satellite_image_date_list(
                si_list, date_list)
        print("Folders to loop through:, ", si_list)
        for f, d in zip(si_list, date_list):
            path = os.path.join(config_input.si_folder_path, str(f))
            snow_cover.calculate_snow_cover(path, d)

    # RUN wasim_snow
    if config_input.run_wasim_snow:
        print("Analyze snow raster from hydrological model WaSim")
        wasim_snow.process_wasim_results()

    # RUN snow_melt
    # Generate end of month snow rasters and snow melt rasters
    if config_input.run_snow_melt:
        snow_melt_main.process_snow_melt()

    # RUN Rfactor_REM_db
    if config_input.run_r_factor:
        Rfactor_main.calculate_REM_db()

    # RUN total_precit_factor
    if config_input.run_total_factor:
        total_R_factor.calculate_tot_R()
