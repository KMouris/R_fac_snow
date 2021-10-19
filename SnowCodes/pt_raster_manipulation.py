"""
Code reads precipitation and temperature values from .txt ASCII raster files (in either monthly, daily or hourly time
intervals) and saves the data for each raster cell in .csv files with the following data:
     year-month-day-hour-minute-second-Precipitation-Temperature-Row-Column

Input files needed:
    - precipitation_path: folder path with .txt ASCII raster files with precipitation values
    - temperature_path: folder path with .txt ASCII raster files with temperature values

     For both folders, each .txt file corresponds to the data for the given year-month-day-hour (The file name
     corresponds to the date in the format YYYYMMDD_0HH)

NOTES:
    - The program assumes and checks that the temperature and precipitation rasters have the same extent and same number
      of value cells.
"""

import file_management
import config_input
from config_input import *
import raster_calculations as rc


def get_values(P_array, T_array, no_data, cells):
    """Function reads the data cells in the original input rasters and returns an array with the extracted P and T data
    from each cell

    :param P_array: np.array with precipitation data
    :param T_array: np.array with temperature data
    :param no_data: float with no data value from the original input rasters
    :param cells: float with number of data cells in the arrays (should be the same for both)
    :return: np.array with the precipitation value, temperature value, cell row index, cell column index
    """
    # Generate an array in which to save the P value, T value, row and column of each cell ( 4 rows)
    value_array = np.zeros((int(cells), 4))

    n = 0  # -counter to fill each row in the new matrix "value", changes value in every "if"
    for i in range(0, P_array.shape[0]):  # -go through every row
        for j in range(0, P_array.shape[1]):  # -goes through every column in original matrix
            if P_array[i, j] != no_data and T_array[i, j] != no_data:
                value_array[n, 0] = P_array[i, j]  # Save precipitation value
                value_array[n, 1] = T_array[i, j]  # Save Temperature value
                value_array[n, 2] = i  # Save in first column the original row value, represented by "i"
                value_array[n, 3] = j  # Save in second column the original column value, represented by "j"
                # print("Saved value: ",storm_array[i,j] )
                n += 1  # -increase the counter to fill a new row in each iteration, only when value fits the
                # criteria in the IF
    return value_array


def fill_3d(date, value_arrays, tdm, row):
    """Function fills the corresponding row value in each array (layer) in the 3D array with the year, month, day, hour,
     minute, second precipitation, temperature, row and column data. Each row corresponds to the given date being looped
     through and each array corresponds to a different cell in the original array

    :param date: date of file being looped through (in datetime format)
    :param value_arrays: array obtained from "get_values" with precipitation value, temperature value, row, column
        values, respectively
    :param tdm: 3D np.array being filled
    :param row: int with row to fill in each array (layer) in the 3D array being filled ("i" in main loop)
    :return: the 3D array filled with the data for the given date, in row "i", in each array
    """
    for k in range(0, tdm.shape[0]):  # Loop through each layer or array in the 3D array
        tdm[k, row, 0] = np.float(date.year)
        tdm[k, row, 1] = np.float(date.month)
        tdm[k, row, 2] = np.float(date.day)
        tdm[k, row, 3] = np.float(date.hour)
        tdm[k, row, 4] = np.float(date.minute)
        tdm[k, row, 5] = np.float(date.second)
        tdm[k, row, 6:] = value_arrays[k, :]
    return tdm


def save_csv_per_cell(tdm, path):
    """Function saves each array in the 3D array (corresponding to each cell in the input rasters) to .csv files.
    Generates a .csv file for each cell, and the name of each file corresponds to the cell row_column location

    :param tdm: 3D np.array with the data for each cell saved to each layer (each array) to save to .csv files
    :param path: folder path in which to save the .csv result files
    :return: ---
    """
    for k in range(0, tdm.shape[0]):  # For each "station" or cell
        # Generate name of .csv, which corresponds to row_column location
        name = path + "\\" + str(tdm[k, 0, 8]) + "_" + str(tdm[k, 0, 9]) + ".csv"

        # Save array "k" in 3D array corresponding to a given cell) to a 2D array
        m = tdm[k, :, :]  # Save current array "k" as a 3D array with 1 layer
        m = np.reshape(m, (int(tdm.shape[1]), int(tdm.shape[2])))  # reshape to a 2D array

        # Save 2D array "k" to a data frame
        df_station = pd.DataFrame(data=m,
                                  columns=["Year", "Month", "Day", "Hour", "Minute", "Second", "Precipitation (mm)",
                                           "Temperature", "Original Row", "Original Column"])
        # print("Saving file: ", name)
        df_station.to_csv(name, sep=',', index=False)


def generate_csv(date):
    """
    Function generates the .csv files from input temperature and precipitation rasters corresponding to a given input
    date. The function filters the raster files in the 'precipitation_path' and 'temperature_path' from the config_input
    file to extract those corresponding to the given input date's month.

    Args:
        date: date (in datetime format) corresponding to the month being analyzed

    Returns: ---

    """
    start_time = time.time()
    print("Analyzing date: {}.".format(str(date.strftime('%Y%m'))))

    # -- Create a folder in which to save the results for the given date -------------------------------------------- #

    save_folder = PT_path + "\\" + str(date.strftime('%Y%m'))
    file_management.create_folder(save_folder)

    # -- Get all txt files in the path directory, and save them in a list ------------------------------------------- #
    filenames_precip = glob.glob(precipitation_path + "\*.txt")
    filenames_temp = glob.glob(temperature_path + "\*.txt")

    # -- Extract from the input folder the files that correspond to the analysis date ------------------------------- #
    filenames_precip = file_management.get_PT_datefiles(filenames_precip, date)
    filenames_temp = file_management.get_PT_datefiles(filenames_temp, date)

    # -- Check the input files: ------------------------------------------------------------------------------------- #
    file_management.compare_dates(filenames_precip, filenames_temp, "Precipitation", "Temperature")

    # -- Get the raster file header from any input raster (Needed for other files) ---------------------------------- #
    ascii_info = rc.get_ascii_data(filenames_precip[0])
    config_input.ascii_data = ascii_info  # Update global variable data

    # -- Get array for any value to get the number of value cells --------------------------------------------------- #
    array = rc.ascii_to_array(filenames_precip[0])
    n_cells = np.count_nonzero(array != ascii_info[5])

    # -- Create 3D array to save results. Each array corresponds to a raster cell, each row to a different time value -
    # and each column to a different data value --------------------------------------------------------------------- #
    n_rows = int(len(filenames_precip))  # number of rows equals number of files in folder
    n_cols = 10  # One for: year, month, day, hour, minute, second, rain, temperature, original row, original column
    tdm = np.empty((n_cells, n_rows, n_cols), dtype=np.dtype('f4'))  # Initiate the 3D matrix, fill it with 0s

    # -- MAIN LOOP -------------------------------------------------------------------------------------------------- #

    for i in range(0, len(filenames_precip)):
        date = file_management.get_date(filenames_precip[i])
        # print("Date: ", date)

        # Extract precipitation and temperature values from ASCII files
        p_array = rc.ascii_to_array(filenames_precip[i])
        t_array = rc.ascii_to_array(filenames_temp[i])

        # Save the data for each value cell in an array: row, column, Precipitation, Temperature
        value_array = get_values(p_array, t_array, no_data=ascii_info[5], cells=n_cells)
        tdm = fill_3d(date, value_array, tdm, i)

    print("Saving results as .csv files for {}".format(date.strftime('%Y%m')))
    # save_csv_per_cell(tdm, config_input.PT_path)
    save_csv_per_cell(tdm, save_folder)

    print(" Generation of CSV per cell files took {} seconds to run.".format(time.time() - start_time))


def main():
    generate_csv(start_date)


if __name__ == '__main__':
    main()
