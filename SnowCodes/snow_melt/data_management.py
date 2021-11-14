# from config import *
from config_input import *    # CHANGE: calls all folders input file "config_input", which contains all variables and
#                             imports all needed modules
from log import *


class DataManagement:
    """
    Class with useful and robust methods for managing output folders, extracting information from raster files and
    writing raster files using the previously extracted information.

    Attributes:
        path: STR of path needed to manage output folders
        filename: STR of filename

    Methods:
        folder_creation(): Method creates folder at instantiated path if it does not already exists.
        get_date(): Method gets the month and the year from the instantiated filenames.
        create_date_string(): Method which returns a date string by calling the get_date method.
        get_proj_data(): Method which gets the projection and geotransformation from a raster file (osgeo.gdal.Dataset).
        save_raster(res_path, array, gt, proj): Static Method which creates and saves raster-file (.tif) from an
                                                existing array using a defined projection.

    """
    def __init__(self, path, filename):
        """
        Assign values to class attributes when a new instance is initiated.
        :param path: STR of path needed to manage output folders
        :param filename: STR of filename
        """
        self.path = path
        self.filename = filename

    def folder_creation(self):
        """
        Method creates folder at instantiated path if it does not already exists
        :return: None
        """
        try:
            # check if folder exists, if not create folder
            if not os.path.exists(self.path):
                logger.info("Creating folder: %s " % self.path)
                os.makedirs(self.path)
            if not os.path.exists(os.path.join(self.path, "Snowmelt")):
                logger.info("Creating folder: %s " % os.path.join(self.path, "Snowmelt"))
                os.makedirs(os.path.join(self.path, "Snowmelt"))
            if not os.path.exists(os.path.join(self.path, "Snow_end_month")):
                logger.info("Creating folder: %s " % os.path.join(self.path, "Snow_end_month"))
                os.makedirs(os.path.join(self.path, "Snow_end_month"))
            if not os.path.exists(os.path.join(self.path, "Plots")):
                logger.info("Creating folder: %s " % os.path.join(self.path, "Plots"))
                os.makedirs(os.path.join(self.path, "Plots"))
            else:
                logger.info("The folder already exists and is not created")
            return 0
        except OSError as o:
            logger.error("OSError: Directory could not be created")
            print(o)
            pass

    def get_date(self):
        """
        Method gets the month and the year from the instantiated filenames
        :return:    sm_month:  INT specifying the month
                    sm_year:   INT specifying the year
        """
        try:
            sm_year = int((self.filename[-9]) + (self.filename[-8]))
            sm_month = int((self.filename[-6]) + (self.filename[-5]))
            return sm_month, sm_year
        except ValueError as v:
            logger.error("ValueError: Invalid file name. Please make sure that the file name consists of 14 characters "
                         "and contains month and year (YY_mm)")
            print(v)

    def get_date_format(self):
        """
            Author: Maria Fernanda Morales Oreamuno
            Function extracts the date from the input file/folder name, in datetime format. The date should be in
            YYYYMM, YYYYMMDD, or YYYYMMDD0HH format
            :param file_path: file or folder path
            :param day: boolean which is True if the file name contains the day and false if it doesnt contain the day
            :param hour: boolean which is True if the file name contains the hours and false it it doesn't
            :param end: Boolean that is True if the date is needed at the end of the month. It is "False" by default
            :return: file date in datetime format
            """
        file_name = os.path.basename( self.filename)  # Get file name (which should contain the date)
        digits = ''.join(re.findall(r'\d+', file_name))  # Combine all digits to a string (removes any integer)

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
                sys.exit("Wrong input date format in input file {}.".format(self.filename))
        elif len(digits) == 8:  # YYYYMMDD format:
            # print("Date format in YYYYMMDD")
            try:
                date = datetime.datetime.strptime(digits, '%Y%m%d')
            except ValueError:
                sys.exit("Wrong input date format in input file {}.".format(self.filename))
        elif len(digits) == 10:  # YYYYMMDDHH
            # print("Date format in YYYYMMDD_HH")
            try:
                date = datetime.datetime.strptime(digits, '%Y%m%d%H')
            except ValueError:
                sys.exit("Wrong input date format in input file {}.".format(self.filename))
        elif len(digits) == 11:  # YYYYMMDD0HH
            # print("Date format in YYYYMMDD_0HH")
            try:
                date = datetime.datetime.strptime(digits, '%Y%m%d0%H')
            except ValueError:
                sys.exit("Wrong input date format in input file {}.".format(self.filename))
        else:
            sys.exit("Check input date format. It must be in either YYYYMM, MMYYYY or YYMM.")

        return date

    def create_date_string(self):
        """
        Method which returns a date string by calling the get_date method
        :return: datestring: STR in the format (YY_mm)
        """
        # # get month and year from get_date() method
        # sm_month, sm_year = self.get_date()
        # # create date string (Format: YY/mm)
        # datestring = (str(sm_year) + '_' + str(sm_month))

        # Get date: in datetime format:
        date = self.get_date_format()
        # create date string (Format: YY/mm)
        datestring = (str(date.strftime('%y')) + '_' + str(date.strftime('%m')))

        return datestring

    def get_proj_data(self):
        """
        Method which get the projection and geotransformation from a raster file (osgeo.gdal.Dataset)
        :return: gt: TUPLE defining a gdal.DataSet.GetGeoTransform object
                 proj: STR defining a gdal.DataSet.GetProjection object
        """
        try:
            raster = gdal.Open(self.filename)  # Extract raster from path
        except RuntimeError as re:
            logger.error("RuntimeError: Raster can't be accessed")
            print(re)
            sys.exit(1)  # code shouldn't run any further if this error occurs
        gt = raster.GetGeoTransform()  # Get geotransformation data
        proj = raster.GetProjection()  # Get projection of raster
        return gt, proj  # Return both variables

    @staticmethod
    def save_raster(res_path, array, gt, proj):
        """
        Static Method which creates and saves raster-file (.tif) from an existing array using a defined projection
        and geotransformation data
        :param res_path: STR of path and result filename
        :param array: NUMPY.NDARRAY of values to rasterize
        :param gt: TUPLE defining a gdal.DataSet.GetGeoTransform object
        :param proj: STR defining a gdal.DataSet.GetProjection object
        :return: saves raster file in the selected dir (path) : osgeo.gdal.Dataset (uses GTiff driver)
        """
        # Get drivers to save outputs as raster .tif files
        driver = gdal.GetDriverByName("GTiff")
        driver.Register()

        # Instantiate the raster files to save, providing all needed information
        outrs = driver.Create(res_path, xsize=array.shape[1], ysize=array.shape[0], bands=1, eType=gdal.GDT_Float32)

        # Assign raster data and assign the array to the raster
        outrs.SetGeoTransform(gt)  # Set geo transform data
        outrs.SetProjection(proj)  # Set projection
        outband = outrs.GetRasterBand(1)  # Create a band in which the array will be written
        outband.WriteArray(array)  # Write array into band
        outband.SetNoDataValue(np.nan)  # Set no data value as np.nan
        outband.ComputeStatistics(0)  # Compute and include standard raster statistics

        # Release raster band
        outband.FlushCache()

        logger.info("Saved raster: %s " % os.path.basename(res_path))
        return 0
