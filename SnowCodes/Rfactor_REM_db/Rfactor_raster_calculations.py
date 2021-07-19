import gdal
import numpy as np
import os
import sys

"""
@author Maria Fernanda Morales Oreamuno 

This program calls functions needed in the "RFactor_main" python program, located in the same folder. The functions
deal directly with gdal commands, such as reading, extracting data and saving gdal raster files.

"""


def check_input_rasters(raster1, raster2):
    """
    Function checks if 2 input rasters (e.g. precipitation raster and fEL raster) have the same cell size, and number of
    rows and columns. It also checks that the extension is similar (not more than 2 cells difference) and if the
    projections are the same. An error is generated if there are significant differences between the rasters. For the
    projection, it gives the user a chance to continue with the raster without the same projection (since they have
     the same extent) or to stop the program in order to manually modify and  check the input rasters
    :param raster1: raster path (in .tif format)
    :param raster2: raster path (in .tif format)
    :return: ---
    """
    # Get data  for each input raster
    raster = gdal.Open(raster1)  # Extract raster from path
    gt_1 = raster.GetGeoTransform()  # Get Geotransform Data: (Top left corner X, cell size, 0, Top left corner Y, 0,
    # -cell size)
    proj_1 = raster.GetProjection()  # Get projection of raster
    x_size_1 = raster.RasterXSize  # Number of columns
    y_size_1 = raster.RasterYSize  # Number of rows

    raster = gdal.Open(raster2)  # Extract raster from path
    gt_2 = raster.GetGeoTransform()  # Get Geotransform Data: (Top left corner X, cell size, 0, Top left corner Y, 0,
    # -cell size)
    proj_2 = raster.GetProjection()  # Get projection of raster
    x_size_2 = raster.RasterXSize  # Number of columns
    y_size_2 = raster.RasterYSize  # Number of rows

    # 1. Check resolution: check if they have the same cell resolution
    if not np.float32(gt_1[1]) == np.float32(gt_2[1]):
        message = "The raster " + str(
            os.path.basename(raster2)), " does not have the same cell size as the other input rasters. Check input"
        sys.exit(message)

    # 2. Check number of rows and columns:
    if not x_size_1 == x_size_2 and not y_size_1 == y_size_2:
        message = "The {} raster does not have the same number of rows and/or columns than input precipitation " \
                  "rasters. Check input".format(os.path.basename(raster2))
        sys.exit(message)

    # 3. Check extent: Check if extent is not shifted by more than 2 cells
    if (abs(np.float32(gt_1[0]) - np.float32(gt_2[0])) > gt_1[1]) or (
            abs(np.float32(gt_1[3]) - np.float32(gt_2[3])) > gt_1[1]):
        message = "The raster " + str(
            os.path.basename(raster2)), " does not have the same extent as the other input rasters. Check input"
        sys.exit(message)

    # 4. Check projection: check if the projection of raster "i" is different to the R factor projection
    if proj_1 != proj_2:
        print("The raster " + str(os.path.basename(raster2)),
              " does not have the same projection as the other input rasters. Nevertheless, they have the same extent.")
        message = "Press 1 if you want to continue with the program or 0 if you want to check the input rasters and " \
                  "stop the program. \n "
        decision = input(message)
        while decision != "0" and decision != "1":  # If the user inputs an invalid option.
            print("Invalid input '", decision, "'.")
            decision = input(message)  # Resend message
        if decision == "0":  # If user wants to stop the program, sys.exit stops the program
            sys.exit("Exit program. Check input raster projections.")


def get_raster_data(raster_path):
    """
    Function extracts only the geotransform and projection from a raster file
    :param raster_path: raster file path
    :return: geotransform and projection
    """
    raster = gdal.Open(raster_path)  # Extract raster from path
    gt = raster.GetGeoTransform()  # Get Geotransform Data: Coordinate upper left X, cell size, 0, Coord. upper left Y,
    #                                   0, -cell size
    proj = raster.GetProjection()  # Get projection of raster

    return gt, proj  # Return both variables


def create_masked_array(array, no_data):
    """
        Function masks al no_data values in an input array, which contains the data values from a raster file so no
        calculations are done with said values
        :param array: array to mask
        :param no_data: data values to mask in array
        :return: masked array
        """
    mskd_array = np.ma.array(array, mask=(array == no_data))  # Mask all NODATA values from the array
    return mskd_array


def raster_to_array(raster_path, mask=True):
    """
        Function extracts raster data from input raster file and returns an array with the raster value data. If the
         mask variable is True, it calls the masked_array function and masks all no_data and returns a masked array. If
         the mask variable it returns the unmasked array
        :param raster_path: path for .tif raster file
        :param mask: boolean which is True when user wants to mask the array and False when you want the original array
        :return: Masked array (masking no data values) or non-masked array, with raster value data
        """
    raster = gdal.Open(raster_path)  # Read raster file
    band = raster.GetRasterBand(1)  # Get raster band (the 1st one, since the inputs have only 1)
    no_data = np.float32(band.GetNoDataValue())  # Get NoData value, since all input rasters could have different values
    #                                                   and assign a numpy type variable
    array = np.float32(band.ReadAsArray())  # Save band info as array and assign the same data type as no_data to
    #                                                   avoid inequalities

    if mask:
        masked_array = create_masked_array(array, no_data)  # Create a masked array from the input data
        return masked_array
    else:
        return array


def save_raster(array, output_path, gt, proj):
    """
        Function saves an array into a .tif raster file.
        :param array: raster data to save to array
        :param output_path: file name (with path and extension) with which to save raster array
        :param gt: geotransform of resulting raster
        :param proj: projection for resulting raster
        :return: ---
        """

    # Step 1: Get drivers in order to save outputs as raster .tif files
    driver = gdal.GetDriverByName("GTiff")  # Get Driver and save it to variable
    driver.Register()  # Register driver variable

    # Step 2: Create the raster files to save, with all the data: folder + name, number of columns (x), number of rows
    # (y), No. of bands, output data type (gdal type)
    outrs = driver.Create(output_path, xsize=array.shape[1], ysize=array.shape[0], bands=1, eType=gdal.GDT_Float32)

    # Step 3: Assign raster data and assign the array to the raster
    outrs.SetGeoTransform(gt)  # assign geo transform data from the original input raster (same size)
    outrs.SetProjection(proj)  # assign projection to raster from original input raster (same projection)
    outband = outrs.GetRasterBand(1)  # Create a band in which to input our array into
    outband.WriteArray(array)  # Read array into band
    outband.SetNoDataValue(np.nan)  # Set no data value as Numpy nan
    outband.ComputeStatistics(0)  # Set the raster statistics to the output raster

    # Step 4: Save raster to folder
    outband.FlushCache()
    outband = None # is this still needed or can we delete it?
    outrs = None

    print("Saved raster: ", os.path.basename(output_path))
