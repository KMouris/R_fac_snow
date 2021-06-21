
import file_management
import snow_cover
import rain_snow_rasters
import pt_raster_manipulation
import config_input
from config_input import *

from snow_melt import main as snow_main
from Rfactor_REM_db import Rfactor_main
import total_precip_factor


"""
Main code author: Maria Fernanda Morales Oreamuno
Main code in order to call the rain and snow raster generation and Snow Detection programs for a given month or group 
of months 
    - rain_snow_rasters: generates monthly snow and rain rasters from input precipitation and temperature data. 
    - Snow_Detection: Detects areas of snow from input satellite (Sentinel2) data and returns a binary data raster, 
      where 1 equals an area of snow and 0 no snow

Notes: 
"""

if __name__ == '__main__':

    config_input.init()

    # Generate a list with all the dates to run through and include in the analysis
    date_list = file_management.get_date_list(start_date, end_date)

# --- RUN PT_raster_manipulation -------------------------------------------------------------------------------- #
    # Generate .csv files with daily/hourly precipitation and temperature per input raster cell --------------------- #
    if run_pt_manipulation:
        print("Generating .csv files from precipitation and temperature data ****************************************")
        # Run PT_Manipulation to get .csv files with precipitation and temperature data
        if start_date.strftime('%Y%m') == end_date.strftime('%Y%m'):  # If only one date
            pt_raster_manipulation.generate_csv(date=start_date)
        else:  # if more than one date is being run
            for date in date_list:
                pt_raster_manipulation.generate_csv(date)
        print("Finished running PT_raster manipulation. *************************************************************")
# ------------------------------------------------------------------------------------------------------------------- #

# --- RUN rain_snow_rasters ----------------------------------------------------------------------------------------- #
    # Generate the rain and snow rasters from the precipitation and temperature  in .csv files ---------------------- #
    if run_rain_snow_rasters:
        print("Generating rain and snow rasters")
        # save all contents in the folder to a list
        csv_list = os.listdir(PT_path)
        # Check if more folders or if there are .csv files (to determine if 1 run or multiple)
        if any(".csv" in string for string in csv_list):  # If any .csv files in folder, loop through 1 folder
            rain_snow_rasters.generate_rain_snow_rasters(config_input.PT_path)
        else:  # Loop through each sub-folder
            # clip csv_list to include only dates within input range
            csv_list = file_management.filter_raster_lists(csv_list, start_date, end_date, "rain_snow_rasters.py")
            for date in csv_list:  # Run code for each folder (date) at a time
                rain_snow_rasters.generate_rain_snow_rasters(PT_path + "\\" + date)
        print("Finished rain and snow raster generation")
# ------------------------------------------------------------------------------------------------------------------- #

# --- RUN snow_detection -------------------------------------------------------------------------------------------- #
    # Generate a binary snow detection raster, to determine cells with snow ----------------------------------------- #
    if run_snow_cover:
        si_list = os.listdir(SI_folder_path)  # list with satellite image folders
        if input_si_dates:  # If user inputs the dates to use:
            si_list = file_management.check_input_si_dates(si_list, date_list, si_image_dates)
        else:  # get images whose sensing date is closest to end of month
            if len(si_list) == 2:  # if only 2 folders, only one sensing date was given
                si_list = [os.path.basename(SI_folder_path)]
            # If no dates to directly use (user input), get the satellite image closest to the end of the month.
            si_list = file_management.generate_satellite_image_date_list(si_list, date_list)
        print("Folders to loop through:, ", si_list)
        for f, d in zip(si_list, date_list):
            path = SI_folder_path + "\\" + str(f)
            snow_cover.calculate_snow_cover(path, d)
# ------------------------------------------------------------------------------------------------------------------- #

# --- RUN snow_melt ------------------------------------------------------------------------------------------------- #
    # Generate end of month snow rasters and snow melt rasters
    if run_snow_melt:
        snow_main.main()
# ------------------------------------------------------------------------------------------------------------------- #

# --- RUN Rfactor_REM_db -------------------------------------------------------------------------------------------- #
    if run_r_factor:
        Rfactor_main.main()
# ------------------------------------------------------------------------------------------------------------------- #

# --- RUN total_precit_factor --------------------------------------------------------------------------------------- #
    if run_total_factor:
        total_precip_factor.main()
# ------------------------------------------------------------------------------------------------------------------- #









