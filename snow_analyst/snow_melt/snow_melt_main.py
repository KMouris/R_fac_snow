import config_input
import file_management
from fun import *
from package_handling import *
from zon_statistics import *

start_time = time.time()


@wrapper(entering, exiting)
def raster2list(list_rasterpaths1, list_rasterpaths2):
    """Reads an arbitrary number of raster files from 2 different folders.
    Extracts the date and the corresponding raster arrays and saves them into lists for further calculations.
    :param list_rasterpaths1: LIST of paths to raster files
    :param list_rasterpaths2: LIST of paths to raster files
    :return:    date_list: LIST which contains the year and month of input raster files
                array_list1: LIST which contains the raster arrays of list_rasterpaths1
                array_list2: LIST which contains the raster arrays of list_rasterpaths2
    """
    # create empty lists
    date_list, array_list1, array_list2 = create_lists()
    # loop trough every file to get the dates and raster arrays
    i = 0
    for file in list_rasterpaths1:
        # get the raster path (STR) from the list_rasterpaths (LIST)
        filenames1, filenames2 = get_path_from_list(
            list_rasterpaths1[i], list_rasterpaths2[i])
        # create date string (YY/mm)
        # print("File sent to get date: ", filenames1)
        data_manager = DataManagement(
            path=r'' + os.path.abspath('../Results'), filename=filenames1)
        month_year = data_manager.create_date_string()
        # use raster2array method to get the arrays from the raster files
        datatype, raster_arrays1, geotransform = gu.raster2array(
            filenames1)
        datatype2, raster_arrays2, geotransform2 = gu.raster2array(
            filenames2)
        # write the dates and the raster arrays into lists
        date_list, array_list1, array_list2 = append2list(date_list, array_list1, array_list2, [month_year],
                                                          raster_arrays1, raster_arrays2)
        i += 1  # add to date (row) counter
    return date_list, array_list1, array_list2


@wrapper(entering, exiting)
def snowcalc_over_list(initial_snow, satellite_data, measured_snow_next_period):
    """
    Calculate snow depths for different time periods by iterating over arrays stored in lists.

    :param initial_snow: ARRAY of snow depth at start of first time period
    :param satellite_data: LIST of arrays of snow cover data
    :param measured_snow_next_period: LIST of arrays of measured snow depths
    :return: [snow_end_month: LIST of arrays of actual snow depths at the end of each time period
             snow_melt: LIST of arrays of snow depths acting as snowmelt of each time period]
    """
    # create empty result lists
    snow_end_month, snow_melt, snow_start_month = create_lists()
    snow_start_month.append(initial_snow)
    # perform calculations for every time period by looping through list of arrays
    k = 0
    m = 1
    try:
        for i in measured_snow_next_period:
            snow_end_array, snowmelt_array, snow_start_array = snowdepth(snow_start_month[k],
                                                                         measured_snow_next_period[m],
                                                                         satellite_data[k])
            # appending results to created result lists
            snow_end_month.append(snow_end_array)
            snow_melt.append(snowmelt_array)
            # avoids appending lastly calculated snow_start_array which describes next period without given input data
            if k < len(measured_snow_next_period) - 1:
                snow_start_month.append(snow_start_array)
            k += 1
            if m < len(measured_snow_next_period) - 1:
                m += 1
    except IndexError:
        logger.error("IndexError: Check number of items in list.")
    return snow_end_month, snow_melt


@wrapper(entering, exiting)
def filter_raster_lists(ras_list):
    """
    Function filters input list to only include dates in between the start and end date (analysis range). If there are
    no files for the given date range (new_list is empty), function throws an error.
    [Author: Mar??a Fernanda Morales]
    :param ras_list: list with file paths, whose names contain the date in either YYYYMM or YYMM format
    :return: filtered list, without the files that are not within the analysis date range.
    """
    new_list = []
    for elem in ras_list:
        data_manager = DataManagement(
            path=r'' + os.path.abspath('../Results'), filename=elem)
        date = data_manager.get_date_format()
        if config_input.start_date <= date <= config_input.end_date:
            new_list.append(elem)

    if len(new_list) == 0:
        message = "There are no input files corresponding to the onput date range. Check input."
        sys.exit(message)

    # Check if there is one input file per month to analyze
    n_months = (config_input.end_date.year - config_input.start_date.year) * 12 + \
        config_input.end_date.month - config_input.start_date.month + 1  # months to analyze
    if not n_months == len(new_list):
        message = "There are fewer rasters than months to analyze. Check input rasters."
        sys.exit(message)

    if n_months == 1:
        message = "The snow melt code cannot run for one month only. Check input end_date and set at least 2 months " \
                  "to analyze. "
        sys.exit(message)

    return new_list


@wrapper(entering, exiting)
def process_snow_melt():
    # Get all file paths into a list: All raster files must be .tif format
    #   CHANGE: input file names
    snow_mm_paths = sorted(glob.glob(file_management.snow_raster_path + "/*.tif"))
    snow_cover_paths = sorted(glob.glob(file_management.snow_cover_path + "/*.tif"))

    # Filter file lists to include only files corresponding to the analysis date range: CHANGE
    snow_mm_paths = filter_raster_lists(snow_mm_paths)
    snow_cover_paths = filter_raster_lists(snow_cover_paths)

    # Create folder if it does not already exist
    data_manager = DataManagement(path=config_input.results_path, filename=snow_mm_paths[0])
    data_manager.folder_creation()

    # Check dates at same index
    i = 0
    for _ in snow_cover_paths:
        compare_date(snow_mm_paths[i], snow_cover_paths[i])
        i += 1

    # loop through input raster files, write raster arrays and corresponding dates in lists
    date, snow_mm, snow_cover = raster2list(snow_mm_paths, snow_cover_paths)

    # get projection and geotransformation of input raster
    gt, proj = data_manager.get_proj_data()

    # Check input data
    j = 0
    for file in snow_mm:
        check_data(snow_mm[j], snow_cover[j], snow_mm_paths[j],
                   snow_cover_paths[j], snow_mm_paths, snow_cover_paths)
        j += 1

    # Calculations
    snow_end_month, snow_melt = snowcalc_over_list(
        snow_mm[0], snow_cover, snow_mm)

    # Saving arrays as raster
    k = 0
    for entry in snow_melt:
        # save_path = r'' + os.path.abspath('../Results/Snow_end_month') + "/snow_end_month" + str(date[k][0]) + ".tif"
        save_path = os.path.join(
            config_input.results_path, 'Snow_end_month', f'snow_end_month_{str(date[k][0])}.tif')
        DataManagement.save_raster(save_path, snow_end_month[k], gt, proj)

        save_path = os.path.join(
            config_input.results_path, 'Snowmelt', f'snowmelt_{str(date[k][0])}.tif')
        DataManagement.save_raster(save_path, snow_melt[k], gt, proj)
        k += 1

    # Path to calculated results to be used for statistical calculations
    snow_result_paths = sorted(
        glob.glob(config_input.results_path + '/Snow_end_month' + "/*.tif"))
    snow_result_paths = filter_raster_lists(snow_result_paths)
    # Calculate and plot zonal statistics
    zonal_statistics = ZonStatistics(path_raster=snow_result_paths, shape=config_input.shape_zone, datelist=date,
                                     parameter=config_input.statistical_param)
    zonal_statistics.get_zon_statistic()
    if config_input.plot_statistic:
        logger.info("Plot statistic is enabled")
        zonal_statistics.plot_zon_statistics()
    else:
        logger.info("Plot statistic is disabled")
    print("Total time: ", time.time() - start_time, "seconds")
    # stop logging
    logging.shutdown()


if __name__ == '__main__':
    main()
