import config_input
from config_input import *
import Resampling
import raster_calculations as rc
import file_management

"""
Code authors: Kilian Mouris & Maria Fernanda Morales Oreamuno (resampling)

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


# -----------------------------------------------FUNCTIONS----------------------------------------------------------- #

def snow_ident(station, T_snow):
    """
    Function determines if the precipitation in each time step is in rain or snow form. It is considered snow if
     T < T_threshold

    :param station: np.array with a Year-Month-Date-Hour in each row, and Precipitation and Temperature in columns [6]
    and[7] respectively.
    :return: Data-frame with 3 columns: total precipitation, Rain and Snow. Each row corresponds to a Y-M-D-H
    combination (in order).
    """
    df_snow = pd.DataFrame([])  # Data frame to save results in each iteration
    iterations = station.shape[0]  # Indicates the number of rows, which equals the number of iterations
    for i in range(0, iterations):  # For each row (For each date)
        df_snow.at[i, 'Total Precipitation (mm)'] = station[i, 6]  # Save the precipitation in column 1
        if station[i, 7] < T_snow:  # If temperature is below threshold temperature (it is snow)
            df_snow.at[i, 'Snow (mm)'] = station[i, 6]
            df_snow.at[i, 'Rain (mm)'] = 0
        else:  # If temperature is above threshold temperature (it is rain)
            df_snow.at[i, 'Rain (mm)'] = station[i, 6]
            df_snow.at[i, 'Snow (mm)'] = 0
    return df_snow


def snow_station(station, snow):
    """
    Function calculates the total monthly (or for the given month or time period in the input files) precipitation, rain
    and snow and returns the monthly values in a dataframe

    :param station: np.array with a Year-Month-Date-Hour in each row, and Precipitation and Temperature in columns [6] and
     [7] respectively and cell row and cell column in columns [7] and [8] respectively.
    :param snow: data-frame with total precipitation, rain, and snow columns. Ech row corresponds to a different time
    step
    :return: data-frame with total precipitation, total rain and total snow within the time period in "station"
    input file
    """
    snow_station = pd.DataFrame([])  # create empty dataframe in which to save the results
    celly = station[1, 8]  # Get cell row (from row 1, though any row would work)
    cellx = station[1, 9]  # Get cell column (from row 1, though any row would work)

    # Save the cell row and column
    snow_station.at[1, 'Cellx'] = cellx  # Save cell row in column [0] called "Cellx"
    snow_station.at[1, 'Celly'] = celly  # Save cell column in column [0] called "Cellx"

    # Add all rows in each column and save it to the corresponding column
    snow_station.at[1, 'Total Prec (mm)'] = snow['Total Precipitation (mm)'].sum(axis=0)
    snow_station.at[1, 'Rain (mm)'] = snow['Rain (mm)'].sum(axis=0)
    snow_station.at[1, 'Snow (mm)'] = snow['Snow (mm)'].sum(axis=0)

    return snow_station


def generate_rain_snow_rasters(path):
    """Function reads .csv files with precipitation and temperature rasters and generates a snow and rain raster for the
    time frame in .csv file (which should be 1 month)

    Args:
        path: folder path where .csv files (one for each cell in the original rasters) are located

    Returns: ---

    """
    print("Running rain and snow raster generation.\n Reading data from: ", path)
    start_time = time.time()

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

    # Create lists for cell location (column and row), Precipitation, Rain and Snow
    cellx = []
    celly = []
    prec = []
    rain = []
    snowfall = []

    # --------------------------------------------------------------------------------------------------------------- #
    # --Loop through each cell (each .csv file) in the input folder-------------------------------------------------- #
    # for file in filenames:
    d = "Generating data for date: " + os.path.basename(path)
    for file in tqdm(filenames, desc=d):
        # Save data from each .csv file into a Numpy Array (assumes input file has a header row, which must be ignored)
        station_file = np.array(pd.read_csv(file, delimiter=','))

        # Calculate whether there is rain or snow in each hour (or each time step)
        snow = snow_ident(station_file, T_snow)
        # print("Results from snow: \n", snow)

        # Calculate snow and rain per period and station
        snowperstation = snow_station(station_file, snow)

        # Append cell specific values to list (much faster than df.append)
        cellx.append(snowperstation['Cellx'].values)
        celly.append(snowperstation['Celly'].values)
        prec.append(snowperstation['Total Prec (mm)'].values)
        rain.append(snowperstation['Rain (mm)'].values)
        snowfall.append(snowperstation['Snow (mm)'].values)

    # |-----------------------------------------------------------|
    print("Time to generate data: ", time.time() - start_time)  # |
    # |-----------------------------------------------------------|

    # --------------------------------------------------------------------------------------------------------------- #

    # Create df containing all information from lists
    cell_result = pd.DataFrame(
        {'Cellx': cellx, 'Celly': celly, 'Total Precipitation (mm)': prec, 'Rain (mm)': rain, 'Snow (mm)': snowfall})
    np.savetxt('CellResult', cell_result, fmt='%s')

    # print("Results: \n", cell_result)

    # --------------------------------------------------------------------------------------------------------------- #

    # Create an array in which to save the values for each cell, with same rows and columns as the original rasters - #
    result_array_snow = np.full((rows, columns), no_data)  # Array for snow
    result_array_rain = np.full((rows, columns), no_data)  # Array for rain

    # --Loop through each cell (each row in cell_result dataframe) in the input folder------------------------------ #
    for m in range(0, rows):  # Each row, or 'y' value
        for k in range(0, columns):  # Each column or 'x' value
            if m in cell_result['Celly'].values and k in cell_result['Cellx'].values:
                value_snow = cell_result['Snow (mm)'].loc[(cell_result['Celly'] == m) & (cell_result['Cellx'] == k)]
                value_rain = cell_result['Rain (mm)'].loc[(cell_result['Celly'] == m) & (cell_result['Cellx'] == k)]
            else:
                value_snow = no_data
                value_rain = no_data
            # Assign values
            try:
                result_array_snow[m, k] = value_snow  # save snow value to the corresponding row-column
                result_array_rain[m, k] = value_rain  # save rain value to the corresponding row-column
            except ValueError:
                result_array_snow[m, k] = no_data
                result_array_rain[m, k] = no_data

    # --------------------------------------------------------------------------------------------------------------- #

    # ---- Resample snow and rain rasters to the same cell resolution as the snap raster: --------------------------- #
    print("Resampling rasters")
    # # -----------------------------|
    # resample_time = time.time()  # |
    # # -----------------------------|

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

    # # |---------------------------------------------------------------------|
    # print("Time to resample raster data: ", time.time() - resample_time)  # |
    # # |---------------------------------------------------------------------|


def main():
    # Running code directly allows for only one month to be run at a time
    generate_rain_snow_rasters(PT_path_input)


if __name__ == '__main__':
    print("Calling rain_snow_rasters directly")
    main()
else:
    pass
