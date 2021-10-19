"""
Program determines if precipitation is snow or rain, from input files, and generates a rain and snow raster,
resampled to 25x25 cell resolution 

NOTES:
- Program runs for one month at a time. Therefore, the folder path it receives must contain .csv files for a given
    month. The program will not differentiate between months within a given .csv file.
- If multiple dates are to be analyzed, input a folder with multiple subfolders, one for each month and whose folder
    name corresponds to the date. The main_snow_codes file will loop through each folder and run rain_snow_rasters
    for each.
- Program can be run individually or through "SnowCode_Main" and will run if input folder contains the .csv files for
a given month
- Code calls program "Resampling" in order to resample the rasters to the given cell resolution of 25x25

Input files:
1. Path: Folder with .csv file with precipitation and temperature values per cell. Each file must correspond to a cell
in the original raster  and must contain the following information: year-month-day-hour-minute-second-Precipitation...
...Temperature-Row-Column (these .csv files are the result from the pt_raster_manipulation python program)
2. T_snow: Temperature threshold
3. Original raster information (original_columns, original_rows, xllcorner, yllcorner, cellsize, nodata values)
    This can be inputted automatically in config_input or obtained from the input rasters read from
    pt_raster_manipulation
4. snapraster_path: path (including name and .tif extension) of the raster to which to snap the resulting resampled
 rasters
5. shape_path: path (location in folder + name.shp) of the shapefile with which to clip the resampled rasters
"""

import config_input
from config_input import *
import Resampling
import raster_calculations as rc
import file_management


def generate_rain_snow_rasters(path):
    """Function reads .csv files with precipitation and temperature rasters and generates a snow and rain raster for the
    time frame in .csv file (which should be 1 month)

    Args:
        path: folder path where .csv files (one for each cell in the original rasters) are located
    """

    # Get all the .csv files in the input folder, and save the names in a list, to iterate through them
    filenames = glob.glob(path + "\*.csv")

    # Check inputs:
    if len(filenames) == 0:
        message = "ERROR: Input folder '{}' has no .csv files.".format(path)
        sys.exit(message)

    # Generate folder to save original rasters:
    save_original_snow = snow_raster_path + "\\Originals"
    file_management.create_folder(save_original_snow)
    save_original_rain = rain_raster_path + "\\Originals"
    file_management.create_folder(save_original_rain)

    # Extract data from input raster if pt_raster_manipulation has been run before:
    no_data = config_input.ascii_data[5]
    rows = int(config_input.ascii_data[1])
    columns = int(config_input.ascii_data[0])

    # ------------------------------------------ Generate rasters -------------------------------------------------- #
    result_array_snow = np.full((rows, columns), no_data)  # Array for snow
    result_array_rain = np.full((rows, columns), no_data)  # Array for rain
    d = "Generating rain/snow data rasters for date: " + os.path.basename(path)
    for f in tqdm(range(0, len(filenames)), desc=d):
        file = filenames[f]
        station_file = np.array(pd.read_csv(file, delimiter=','))

        rn = np.sum(np.where(station_file[:, 7] > T_snow, station_file[:, 6], 0))  # rain
        sn = np.sum(np.where(station_file[:, 7] < T_snow, station_file[:, 6], 0))  # snow
        rw = int(station_file[0, 8])  # row
        cl = int(station_file[0, 9])  # column

        result_array_snow[rw, cl] = sn
        result_array_rain[rw, cl] = rn
    # --------------------------------------------------------------------------------------------------------------- #

    # ---- Resample snow and rain rasters to the same cell resolution as the snap raster: --------------------------- #
    # Get year and month from any of the .csv input files
    month = int(station_file[1, 1])
    if month < 10:
        month = '0' + str(month)
    date = str(int(station_file[1, 0])) + str(month)
    # print("Date: ", date)

    # Get original raster (coarse) data:
    gt_original = rc.get_ascii_gt(config_input.ascii_data)

    # -- Get result rasters projection from the snap raster: -------------------------------------------------------- #
    gt_snap, proj = rc.get_raster_data(snapraster_path)

    # -- Save rasters with original cell resolution ----------------------------------------------------------------- #
    original_snow_name = save_original_snow + "\\OriginalSnow_" + str(date) + ".tif"
    original_rain_name = save_original_rain + "\\OriginalRain_" + str(date) + ".tif"

    rc.save_raster(result_array_snow, original_snow_name, gt_original, proj, nodata)
    rc.save_raster(result_array_rain, original_rain_name, gt_original, proj, nodata)

    # -- Resample rasters to sample raster resolution and save: ----------------------------------------------------- #
    resampled_snow_name = snow_raster_path + "\\Snow_" + str(date) + ".tif"
    resampled_rain_name = rain_raster_path + "\\Rain_" + str(date) + ".tif"

    Resampling.main(original_snow_name, snapraster_path, shape_path, resampled_snow_name)
    Resampling.main(original_rain_name, snapraster_path, shape_path, resampled_rain_name)

    # Delete the original rasters
    if os.path.exists(original_snow_name):
        os.remove(original_snow_name)

    if os.path.exists(original_rain_name):
        os.remove(original_rain_name)


def main():
    # Running code directly allows for only one month to be run at a time
    generate_rain_snow_rasters(PT_path_input)


if __name__ == '__main__':
    print("Calling rain_snow_rasters directly")
    main()
else:
    pass
