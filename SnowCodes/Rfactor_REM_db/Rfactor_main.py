from config_input import *
from Rfactor_REM_db import Rfactor_raster_calculations as raster_calc
from Rfactor_REM_db import Rfactor_data_management as data_management

"""
Author: María Fernanda Morales Oreamuno 

Function calculates the R factor (Rain factor) for the RUSLE method for calculating soil loss and soil yield using the 
REM(DB) rainfall erosivity model for complex terrains. 
 The equations for the R factor are obtained from the following manuscript: 
     Diodato, N. & Bellochi, G. (2007). Estimating monthly (R)USLE climate input in a Mediterranean region using limited 
    data. 
    (https://doi.org/10.1016/j.jhydrol.2007.08.008)
 

It receives input monthly precipitation rasters, in .tif format, and calculates the monthly RFactor
# corresponding to each input file. The resulting file is in .tif format with th same raster properties as
# the input files

MISSING: 
- Add function to clip input raster path list to analyze only the input data range 
- Change how the program reads the file date (get_Date())

"""


# ----------------------------------- FUNCTIONS ---------------------------------------------------------------------#


def monthly_factor(m):
    """
    Function receives the month and calculates the monthly factor for the REM(DB) rainfall erosivity model for complex
    terrain from Duidato & Belucchi (2007).
    :param m: month, in numbers
    :return: fm (monthly factor)
    """
    fm = 0.3696 * (1 - 1.0888 * math.cos(2 * math.pi * m / (2.9048 + m)))  # Formula with cos(x), with x in radians
    # print("f(m) for month ", m, " = ", fm)
    return fm


def RFactor(m, p_array, fEL_array):
    """
    Function receives the month corresponding to the file (and calculates the monthly factor with the corresponding
    function),the monthly precipitation array and the f(E,L) array and calculates the RFactor using the REM(DB) from
    Diodato & Belucchi (2007)
    :param m: month (in number format)
    :param p_array: monthly precipitation raster data as np.array
    :param fEL_array: f_EL raster data as np.array
    :return: array of R factor values for each cell
    """
    # Calculate the monthly factor f(m):
    fm = monthly_factor(m)

    # Calculate the RFactor with the Diodato and Belocchi equation:
    np.seterr(all='ignore')  # Ignore float-induced errors, to avoid error printing in the command window
    RFactor = 0.207 * np.power(p_array * (fm + fEL_array), 1.561)
    RFactor = np.where(RFactor.mask == True, np.nan, RFactor)  # Convert all masked cells to np.nan values

    # print("Value to a power: ", RFactor[1000][1000])
    # print("NAN value: ", RFactor[1][1])

    return RFactor


def main():
    start_time = time.time()

    # ------------------------- Initial Procedure ------------------------------------------------------------------ #

    # 1. Save all monthly precipitation rasters, with .tif extension, in a list, to iterate over them
    filenames = glob.glob(rain_raster_path + "\*.tif")

    # 2. Filter precipitation raster list to only include rasters corresponding to the analysis date range
    filenames = data_management.filter_raster_lists(filenames, start_date, end_date)

    # 3. Compare one of the Monthly precipitation files with the input f(EL) raster to make sure they have the
    # same properties
    raster_calc.check_input_rasters(filenames[0], fEL_path)

    # 3. Get the raster data, such as geotransform (GT) and projection (Proj) from the first file in the folder,
    # and assume the rest have the same information
    GT, Proj = raster_calc.get_raster_data(filenames[0])

    # 4. Save the f(E,L) raster to a masked array, since it remains constant for each iteration
    f_EL_array = raster_calc.raster_to_array(fEL_path)

    # ---------------------------- Main Loop ----------------------------------------------------------------------- #

    for file in filenames:  # Iterate through each monthly precipitation file
        # 1. Get complete name of raster being analyzed (including extension)
        name = os.path.basename(file)
        print("Running for: ", name)

        # 2. Get the date and them month for the corresponding file
        date = data_management.get_date(name)
        month = float(date.month)

        # 3. Save the precipitation raster as a masked array
        precip_array = raster_calc.raster_to_array(file)

        # 4. Calculate RFactor raster
        R_factor_array = RFactor(month, precip_array, f_EL_array)
        # print("RFactor data: ", precip_array[0][660])

        # 5. Save RFactor array to a .tif raster
        output_name = r_factor_path + "\\RFactor_REM_db_" + str(date.strftime('%Y%m')) + ".tif"
        raster_calc.save_raster(R_factor_array, output_name, GT, Proj)

    print('Total time: ', time.time() - start_time)


if __name__ == '__main__':
    main()