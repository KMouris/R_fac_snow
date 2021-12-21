import config_input
from package_handling import *

""" Functions related to input file/folders, file names, dates and reading/saving
.txt/.csv files """


def check_folder(path, v_name):
    """ Function checks if a given folder exists

    :param path: folder path
    :param v_name: string corresponding to the type of information that should be found in the input folder

    :returns: Error if file does not exist.
    """
    if not os.path.exists(path):
        message = "ERROR: The input folder for '{}' does not exist. Check input '{}'".format(
            v_name, path)
        sys.exit(message)


def create_folder(path):
    """
    Function checks if the folder path "path" exists, and if it doesn't it creates it

    :param path: folder location
    :return: None
    """
    if not os.path.exists(path):
        print("Creating folder: ", path)
        os.makedirs(path)
    else:
        pass
        # print("Folder {} already exists".format(path))


def has_number(string):
    """ Function determines if an input string contains numbers/digits

    :param string: string to analyze
    :return: boolean as True if string has numbers
    """
    return any(i.isdigit() for i in string)


def get_PT_datefiles(paths, date):
    """
    Function receives a list with file paths and saves, to another list, those files whose dates are within the input
    dates month. It also checks if the list is empty, in which case it returns an error.

    :param paths: list with file paths
    :param date: start date (in datetime format)
    :return: list with file paths which correspond to dates within the input date's month
    """

    filenames = []
    for text in paths:
        f_date = get_date(text)
        if f_date.year == date.year and f_date.month == date.month:
            filenames.append(text)
    if len(filenames) == 0:
        message = "The input precipitation and/or temperature files do not contain files for ", str(
            date.strftime('%Y%m'))
        sys.exit(message)
    else:
        # Check if month is incomplete by calculating all possibilities: input files are monthly, daily or hourly
        num_days = int(calendar.monthrange(date.year, date.month)[1])
        num_hours = num_days * 24
        num_3hours = (num_hours / 3)
        if len(filenames) != num_days and len(filenames) != num_hours and len(filenames) != num_3hours:
            message = "Data for the month of{} is incomplete.".format(
                str(date.strftime('%Y%m')))
            sys.exit(message)
    return filenames


def get_date(file_path, end=False):
    """
    Function extracts the date from the input file/folder name. The date should be in YYYYMM, YYYYMMDD, or YYYYMMDD0HH
    format

    :param file_path: file or folder path
    :param end: boolean that is True if the date is needed at the end of the month. It is "False" by default
    :return: file date in datetime format
    """
    file_name = os.path.basename(
        file_path)  # Get file name (which should contain the date)
    # Combine all digits to a string (removes any integer)
    digits = ''.join(re.findall(r'\d+', file_name))

    if len(digits) == 6:  # Either MMYYYY or YYYYMM
        if int(digits[0:2]) > 12:  # YYYYMM format
            try:
                # print(" Date in YYYYMM format")
                date = datetime.datetime.strptime(digits, '%Y%m')
            except ValueError:
                sys.exit("Wrong input date format.")
        else:  # MMYYYY format
            try:
                # print("date in MMYYYY format")
                date = datetime.datetime.strptime(digits, '%m%Y')
            except ValueError:
                sys.exit("Wrong input date format.")
    elif len(digits) == 4:  # Should be YY_MM
        # print("Date format in YYMM")
        try:
            date = datetime.datetime.strptime(digits, '%y%m')
        except ValueError:
            sys.exit("Wrong input date format in input file {}.".format(file_path))
    elif len(digits) == 8:  # YYYYMMDD format:
        # print("Date format in YYYYMMDD")
        try:
            date = datetime.datetime.strptime(digits, '%Y%m%d')
        except ValueError:
            sys.exit("Wrong input date format in input file {}.".format(file_path))
    elif len(digits) == 10:  # YYYYMMDDHH
        # print("Date format in YYYYMMDD_HH")
        try:
            date = datetime.datetime.strptime(digits, '%Y%m%d%H')
        except ValueError:
            sys.exit("Wrong input date format in input file {}.".format(file_path))
    elif len(digits) == 11:  # YYYYMMDD0HH
        # print("Date format in YYYYMMDD_0HH")
        try:
            date = datetime.datetime.strptime(digits, '%Y%m%d0%H')
        except ValueError:
            sys.exit("Wrong input date format in input file {}.".format(file_path))
    else:
        sys.exit(
            "Check input date format. It must be in either YYYYMM, MMYYYY or YYMM.")

    if end:
        date = date.replace(day=calendar.monthrange(date.year, date.month)[1])

    return date


def get_date_list(date1, date2):
    """
    Generates a list with each month between 2 dates

    :param date1: start date (in datetime format)
    :param date2: end date (in datetime format)
    :return: list with months, in datetime format
    """
    date_list = pd.to_datetime(pd.date_range(
        date1, date2, freq='MS').strftime("%Y%m").tolist(), format="%Y%m")
    return date_list


def filter_raster_lists(raster_list, date1, date2, file_name):
    """
    Filters input list to only include dates in between 2 dates (date1-date2) (analysis range). If there are
    no files for the given date range (new_list is empty) or any month is missing, function throws an error.

    :param raster_list: list with file paths, whose names contain the date in either YYYYMM or YYMM format
    :param date1: analysis start date (in datetime format)
    :param date2: analysis end date (in datetime format)
    :param file_name: string with the name of the input raster file type generating the error

    :return: filtered list, without the files that are not within the analysis date range.
    """
    new_list = []
    for elem in raster_list:
        if not has_number(elem) or sum(c.isdigit() for c in elem) < 4:
            continue
        else:
            date = get_date(elem)
            # timedelta is added because Wasim are from 9 PM
            date2_end = date2 + datetime.timedelta(hours=23)
            if date1 <= date <= date2_end:
                new_list.append(elem)

    if len(new_list) == 0:
        message = "ERROR: There are no {} input raster files corresponding to input date range. Check input.".format(
            file_name)
        sys.exit(message)

    # Check if there is one input file per month to analyze
    n_months = (date2.year - date1.year) * 12 + date2.month - date1.month + 1  # months to analyze
    n_days = (date2.replace(day=calendar.monthrange(
        date2.year, date2.month)[1]) - date1).days + 1
    n_hours = n_days * 24
    if not n_months == len(new_list) and not n_days == len(new_list) and not n_hours == len(new_list):
        message = "ERROR: One or more of the raster files between {} and {} is missing from {} input files.".format(
            str(date1.strftime('%Y%m')), str(date2.strftime('%Y%m')), file_name) + \
                  " Check input rasters for missing date(s) or check date range."
        sys.exit(message)

    return new_list


def compare_dates(list1, list2, name1, name2):
    """
    Checks if the files in 2 different input folders have the same number of files corresponding to the given
    time interval, and if said rasters are in the same order. If not, function throws an error and exists program.

    :param list1: list with file paths from folder 1
    :param list2: list with file paths from folder 2
    :param name1: string with name of raster type from folder 1 (e.g. Precipitation, Temperature)
    :param name2: string with name of raster type from folder 2 (e.g. Precipitation, Temperature)

    :return: ---
    """

    # Check if there are files in both lists:
    if not list1 or not list2:
        message = "There are no {} and/or {} raster files corresponding to the input date range." + \
                  "Check input folder or input data range"
        sys.exit(message)

    # Check if lists have the same number of files
    if not len(list1) == len(list2):
        message = "There are a different number of {} and {} raster files. Check that both file folders have the " \
                  "same time discretization and number of files for the given date range.".format(name1, name2)
        sys.exit(message)

    # If they do have the same number of files: check that the files are in the same order
    for f1, f2 in zip(list1, list2):
        if not get_date(f1) == get_date(f2):
            message = "{} and {} input raster files are not in the correct order. Check input file naming".format(
                name1, name2)
            sys.exit(message)


def generate_satellite_image_date_list(folders, date_list):
    """
    Receives a list with folders, which correspond to a given satellite image sensing date. The folder name
    must be in YYYYMMDD format (otherwise function will erase said folder from the list). Then, for each analysis date
    (in date_list), the function determines which satellite image sensing date is closest to the end of each analysis
    month

    :param folders: list with folder names (string format)
    :param date_list: list with analysis date (in datetime format)

    :return: cropped folder list containing the satellite images to analyze
    """
    folder_date_list = []  # list to save the folder names as dates
    # list to save folder name of those folders whose name corresponds to a date
    mod_folder_list = []
    for f in folders:
        if sum(c.isdigit() for c in f) == 8:  # If folder name is a YYYYMMDD date
            folder_date_list.append(get_date(f))  # convert folder name to date
            # copy folder name, which corresponds to a date, to a new list
            mod_folder_list.append(f)

    # convert folder name (as dates) to a numpy array
    folder_date_list = np.array(folder_date_list)

    return_folder_list = []
    for date in date_list:
        # get last day of the given month in "date"
        date = date.replace(day=calendar.monthrange(date.year, date.month)[1])
        # subtract the analysis date from all folder dates to get day difference between each folder and "date"
        sub = np.abs(np.subtract(date, folder_date_list))
        index = np.argmin(sub)  # get index of min value

        # if time difference is more than 15 days, it is no longer considered the end of the month.
        if sub[index] > datetime.timedelta(days=15):
            message = "There are no available satellite images for the analysis date: " + \
                      str(date.strftime('%Y%m'))
            sys.exit(message)
        else:
            return_folder_list.append(mod_folder_list[index])

    return return_folder_list


def check_input_si_dates(folders, date_list, si_image_dates):
    """
    Called if the user sets which satellite image dates to use. There are 2 possibilities:

        1. User sets ALL the satellite image sensing dates, in which case the length of the input si dates will be the
        same as the amount of months to analyze (date_list). The function checks that all folders (sensing dates) exist,
        then checks if they are in order and if each input corresponds to the end of the month (less than 15 days from
        the end)
        2. User sets only SOME satellite image sensing dates, in which case the length of the input si_dates is less
        than the amount of months to analyze. The function checks that all folders (sensing dates) exist, then gets a
        list of the sensing dates that correspond to the END of the month of each analysis date. Then it compares the
        input SI dates with the folders corresponding to the end of the month. If the input date corresponds to the same
        month as one of the "end of the month" dates, then it substitutes it with the input date.

    :param folders: list of available sensing dates
    :param date_list: list with the dates to analyze (in datetime format)
    :param si_image_dates: the user input variable with the sensing dates to use

    :return: list of satellite image sensing dates to analyze.
    """
    # Step 1: # Check if the input dates exist in the input satellite image folder:
    for s_date in si_image_dates:
        if str(s_date) not in folders:
            message = "There is no satellite image for {} in input satellite image folder. Check user input".format(
                str(s_date))
            sys.exit(message)
    # Get list of available satellite images for each date in analysis range, calculated automatically
    last_of_month_list = generate_satellite_image_date_list(folders, date_list)
    folder_date_list = []  # list to save the folder names as dates
    # convert each last_of_month_list folder name to datetime format
    for f in last_of_month_list:
        if sum(c.isdigit() for c in f) == 8:  # If folder name is a YYYYMMDD date
            folder_date_list.append(get_date(f))  # convert folder name to date

    # convert folder name (as dates) to a numpy array
    folder_date_list = np.array(folder_date_list)
    # compare each input si date with the end_of_the_month folder names (in date time format)
    for si_date in si_image_dates:
        # convert input si dae to datetime format
        si_date_format = get_date(str(si_date))
        sub = np.abs(
            np.subtract(si_date_format, folder_date_list))  # subtract the date from each last of the month SI date
        index = np.argmin(sub)  # get index of min value
        # if time difference is less than 30 days, folder_date_list[index] corresponds to the same month as the
        # si_input_Date and thus will be substituted
        if sub[index] < datetime.timedelta(days=30):
            last_of_month_list[index] = si_date

    folders_to_analyze = last_of_month_list

    return folders_to_analyze


if __name__ == '__main__':
    pass
else:
    # Generate folder to save all results:
    create_folder(config_input.results_path)

    # Convert input dates (start and end date) to date format
    config_input.start_date = get_date(config_input.start_date)
    config_input.end_date = get_date(config_input.end_date, end=True)

    if config_input.run_pt_manipulation:
        # Generate folder to save PT_manipulation results (.csv files)
        config_input.PT_path = os.path.join(config_input.results_path, "PT_CSV_per_cell")
        create_folder(config_input.PT_path)
        # check if folders exist:
        check_folder(config_input.precipitation_path, "precipitation_path")
        check_folder(config_input.temperature_path, 'temperature_path')
    else:
        config_input.PT_path = config_input.PT_path_input

    if config_input.run_rain_snow_rasters:
        snow_raster_path = os.path.join(config_input.results_path, "snow_per_month")
        create_folder(snow_raster_path)
        rain_raster_path = os.path.join(config_input.results_path, "rain_per_month")
        create_folder(rain_raster_path)
        # Check if needed input folders exist:
        check_folder(config_input.PT_path, "PT_path")  # Folder with .csv files

    else:
        snow_raster_path = config_input.snow_raster_input
        rain_raster_path = config_input.rain_raster_input

    if config_input.run_snow_cover:
        snow_cover_path = os.path.join(config_input.results_path, "snow_cover")
        create_folder(snow_cover_path)
        # Check if needed input folders exist:
        check_folder(config_input.si_folder_path, 'SI_folder_path')
    else:
        snow_cover_path = config_input.snowcover_raster_input

    if config_input.run_wasim_snow:
        wasim_path = os.path.join(config_input.results_path, "wasim")
        create_folder(wasim_path)
        snow_cover_path = os.path.join(config_input.results_path, "snow_cover")
        create_folder(snow_cover_path)

    if config_input.run_snow_melt:
        snow_melt_path = os.path.join(config_input.results_path, "Snowmelt")
        create_folder(snow_melt_path)
        # check if needed input folders exist:
        check_folder(snow_cover_path, 'snow_cover_path')
        # snow cover raster
        check_folder(snow_raster_path, 'snow_raster_path')
        # snow per month raster
    else:
        snow_melt_path = config_input.snow_melt_input

    if config_input.run_r_factor:
        r_factor_path = os.path.join(config_input.results_path, "R_factor_REM_db")
        create_folder(r_factor_path)
        # Check needed folders:
        check_folder(rain_raster_path, 'rain_raster_path')
        # folder with .tif rain raster files
    else:
        r_factor_path = config_input.r_factor_input

    if config_input.run_total_factor:
        total_factor_path = os.path.join(config_input.results_path, "R_factor_Total")
        create_folder(total_factor_path)
        # Check needed folders:
        check_folder(r_factor_path, 'r_factor_path')
        check_folder(snow_melt_path, 'snow_melt_path')
