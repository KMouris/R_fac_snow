"""
Function calculates the R factor (Rain factor) for the RUSLE method for calculating soil loss and sediment yield
using the REM(DB) rainfall erosivity model for complex terrains. The equations for the R factor are obtained from the
following manuscript: Diodato, N. & Bellochi, G. (2007). Estimating monthly (R)USLE climate input in a Mediterranean
region using limited data. (https://doi.org/10.1016/j.jhydrol.2007.08.008)


It receives input monthly precipitation rasters, in .tif format, and calculates the monthly RFactor corresponding to
each input file. The resulting file is in .tif format with th same raster properties as the input files.
"""

from config_input import *
from Rfactor_REM_db import Rfactor_raster_calculations as raster_calc
from Rfactor_REM_db import Rfactor_data_management as data_management


# ----------------------------------- FUNCTIONS ---------------------------------------------------------------------#


def monthly_factor(m):
    """
    Function receives the month and calculates the monthly factor for the REM(DB) rainfall erosivity model for complex
    terrain from Diodato & Bellocchi (2007).
    :param m: month, in numbers (float)
    :return: fm (monthly factor)
    """
    fm = 0.3696 * (1 - 1.0888 * math.cos(2 * math.pi * m / (2.9048 + m)))  # Formula with cos(x), with x in radians
    return fm


def rfactor(m, p_array, f_el_array):
    """
    Function receives the month corresponding to the file (and calculates the monthly factor with the corresponding
    function),the monthly precipitation array and the f(E,L) array and calculates the RFactor using the REM(DB) from
    Diodato & Bellocchi (2007)
    :param f_el_array: f_EL raster data as np.array
    :param m: month (in number format)
    :param p_array: monthly precipitation raster data as np.array
    :return: array of R factor values for each cell
    """
    # Calculate the monthly factor f(m):
    fm = monthly_factor(m)

    # Calculate the RFactor with the Diodato and Belocchi equation:
    np.seterr(all='ignore')  # Ignore float-induced errors, to avoid error printing in the command window
    r_factor = 0.207 * np.power(p_array * (fm + f_el_array), 1.561)
    r_factor = np.where(r_factor.mask == True, np.nan, r_factor)  # Convert all masked cells to np.nan values

    return r_factor


def main():

    # ------------------------- Initial Procedure ------------------------------------------------------------------ #

    # 1. Save all monthly precipitation rasters, with .tif extension, in a list, to iterate over them
    filenames = glob.glob(rain_raster_path + "\*.tif")

    # 2. Filter precipitation raster list to only include rasters corresponding to the analysis date range
    filenames = data_management.filter_raster_lists(filenames, start_date, end_date)

    # 3. Compare one of the Monthly precipitation files with the input f(EL) raster to make sure they have the
    # same properties
    raster_calc.check_input_rasters(filenames[0], fEL_path)

    # 3. Get the raster data, such as geotransform (gt) and projection (proj) from the first file in the folder,
    # and assume the rest have the same information
    gt, proj = raster_calc.get_raster_data(filenames[0])

    # 4. Save the f(E,L) raster to a masked array, since it remains constant for each iteration
    f_el_array = raster_calc.raster_to_array(fEL_path)

    # ---------------------------- Main Loop ----------------------------------------------------------------------- #

    for file in filenames:  # Iterate through each monthly precipitation file
        # 1. Get complete name of raster being analyzed (including extension)
        name = os.path.basename(file)
        print("Running REM R Factor for: ", name)

        # 2. Get the date and them month for the corresponding file
        date = data_management.get_date(name)
        month = float(date.month)

        # 3. Save the precipitation raster as a masked array
        precip_array = raster_calc.raster_to_array(file)

        # 4. Calculate RFactor raster
        r_factor_array = rfactor(month, precip_array, f_el_array)

        # 5. Save RFactor array to a .tif raster
        output_name = r_factor_path + "\\RFactor_REM_db_" + str(date.strftime('%Y%m')) + ".tif"
        raster_calc.save_raster(r_factor_array, output_name, gt, proj)


if __name__ == '__main__':
    main()
