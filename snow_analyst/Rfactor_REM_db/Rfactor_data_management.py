"""Calls functions needed in the "RFactor_main" python program,
located in the same folder. The functions
deal directly with input files/folders.
"""

from package_handling import *


def filter_raster_lists(raster_list, s_date, e_date):
    """Filters input list to only include dates in between the start and end
    date (analysis range). If there are no files for the given date range
    (new_list is empty), function throws an error.

    :param raster_list: list with file paths, whose names contain the date in either YYYYMM or YYMM format
    :param s_date: analysis start date (in datetime format)
    :param e_date: analysis end date (in datetime format)
    :return: filtered list, without the files that are not within the analysis date range.
    """
    new_list = []
    for elem in raster_list:
        date = get_date(elem)
        if s_date <= date <= e_date:
            new_list.append(elem)

    if len(new_list) == 0:
        message = "ERROR: There are no input rain raster files corresponding to the input date range. Check input."
        sys.exit(message)

    # Check if there is one input file per month to analyze
    n_months = (e_date.year - s_date.year) * 12 + e_date.month - \
               s_date.month + 1  # months to analyze
    if not n_months == len(new_list):
        message = "ERROR: Missing rain (precipitation) rasters in input folder." + \
                  "Check input rasters for missing date or check date range."
        sys.exit(message)

    return new_list


def get_date(file_path):
    """Extracts the date from the input file/folder name. The date should be in
    YYYYMM, YYYYMMDD, or YYYYMMDD0HH format

    :param file_path: file or folder path
    :return: file date in datetime format
    """
    file_name = os.path.basename(
        file_path)  # Get file name (which should contain the date)
    # Combine all digits to a string (removes any integer)
    digits = ''.join(re.findall(r'\d+', file_name))

    if len(digits) == 6:  # Either MMYYYY or YYYYMM
        if int(digits[0:2]) > 12:  # YYYYMM format
            try:
                date = datetime.datetime.strptime(digits, '%Y%m')
            except ValueError:
                sys.exit("Wrong input date format.")
        else:  # MMYYYY format
            try:
                date = datetime.datetime.strptime(digits, '%m%Y')
            except ValueError:
                sys.exit("Wrong input date format.")
    elif len(digits) == 4:  # Should be YY_MM
        try:
            date = datetime.datetime.strptime(digits, '%y%m')
        except ValueError:
            sys.exit("Wrong input date format in input file {}.".format(file_path))
    elif len(digits) == 8:  # YYYYMMDD format:
        try:
            date = datetime.datetime.strptime(digits, '%Y%m%d')
        except ValueError:
            sys.exit("Wrong input date format in input file {}.".format(file_path))
    elif len(digits) == 10:  # YYYYMMDDHH
        try:
            date = datetime.datetime.strptime(digits, '%Y%m%d%H')
        except ValueError:
            sys.exit("Wrong input date format in input file {}.".format(file_path))
    elif len(digits) == 11:  # YYYYMMDD0HH
        try:
            date = datetime.datetime.strptime(digits, '%Y%m%d0%H')
        except ValueError:
            sys.exit("Wrong input date format in input file {}.".format(file_path))
    else:
        sys.exit(
            "Check input date format. It must be in either YYYYMM, MMYYYY or YYMM.")

    return date
