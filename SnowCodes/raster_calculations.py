from config_input import *

"""
Author: María Fernanda Morales 

File contains direct raster calculation functions (meaning it receives a raster path as input) 
"""


def get_snap_raster_data(raster_path):
    """
    Function extracts the raster and gets the basic information such as: GeoTransform, Projection, Extension (As an
    array with ulx, uly, lrx, lry) and cell resolution
    :param raster_path: path where the snap raster is located (including name and .tif extension)
    :return: returns geotransform, projection, snap raster extension, cell size
    """
    raster = gdal.Open(raster_path) #Extract raster from path
    gt = raster.GetGeoTransform()  #Get Geotransform Data: (Top left corner X, cell size, 0, Top left corner Y, 0, -cell size)
    proj = raster.GetProjection()  #Get projection of raster
    XSize = raster.RasterXSize  # Number of columns
    YSize = raster.RasterYSize  # Number of rows

    # print("GT: ", gt)
    # print("Projection: ", proj)
    # print("Number of columns: ", XSize)
    # print("Number of rows: ", YSize)

    cell_size = gt[1]  # Cell resolution
    ulx = gt[0]  # Upper left X or Xmin
    lrx = ulx + cell_size*XSize  # Lower right X or Xmax

    uly = gt[3]  # Upper left Y or Ymax
    lry = uly - cell_size*YSize  # Lower right Y or Ymin

    # print("Min X: ", ulx, "Max X: ", lrx)
    # print("Max Y: ", uly, "Min Y: ", lry)

    snap_data = [ulx, uly, lrx, lry]  # Upper left X, Upper left Y, Lower right X, Lower right Y

    # print("Snap Data: ", snap_data)

    return gt, proj, snap_data, cell_size  # Return all 4 variables


def get_raster_data(raster_path):
    """
    Function extracts only the geotransform and projection from a raster file
    :param raster_path: raster file path
    :return: geotransform and projection
    """
    raster = gdal.Open(raster_path) # Extract raster from path
    gt = raster.GetGeoTransform()  # Get Geotransform Data: (Top left corner X, cell size, 0, Top left corner Y, 0,
    #                                 -cell size)
    proj = raster.GetProjection()  # Get projection of raster

    band = raster.GetRasterBand(1)  # Get raster band (the 1st one, since the inputs have only 1)
    no_data = np.float32(
        band.GetNoDataValue())  # Get NoData value, since all input rasters could have different values and assign a n
    #                               umpy type variable

    return gt, proj


def create_masked_array(array, no_data):
    """
    Function maskes the no_data values in an input array, which contains the data values from a raster file
    :param array: array to mask
    :param no_data: data values to mask in array
    :return: masked array
    """
    mskd_array = np.ma.array(array, mask=(array == no_data))  # Mask all NODATA values from the array
    if math.isnan(no_data):  # if no data value is 'nan'
        mskd_array = np.ma.masked_invalid(array)
    return mskd_array


def raster_to_array(raster_path, mask):
    """
    Function extracts raster data from input raster file and returns a non-masked array
    :param raster_path: path for .tif raster file
    :param mask: boolean which is True when user wants to mask the array and False when you want the original array
    :return: Masked array (masking no data values)
    """
    raster = gdal.Open(raster_path)  # Read raster file
    band = raster.GetRasterBand(1)   #Get raster band (the 1st one, since the inputs have only 1)
    no_data = np.float32(band.GetNoDataValue())  #Get NoData value, since all input rasters could have different values and assign a numpy type variable

    array = np.float32(band.ReadAsArray() )      #Save band info as array and assign the same data type as no_data to avoid inequalities
    if mask:
        masked_array = create_masked_array(array, no_data)  #Create a masked array from the input data
        return masked_array
    else:
        return array


def clip(shape_path, save_path, original_raster):
    """
    Function clips the raster to the same extents as the snap raster (same NODATA cells).
    :param shape_path: path where the .shp file, with which to clip input raster
    :param save_path: file name (including extension and path) where to save the clipped raster
    :param original_raster: raster to clip to shape extent (interpolated raster)
    :return: ---
    """

    # 1. Clip the interpolated (resampled) precipitation raster with the bounding raster shapefile from step 3
    os.system(
        "gdalwarp -cutline " + shape_path + " -crop_to_cutline -dstnodata -9999 -overwrite --config GDALWARP_IGNORE_BAD_CUTLINE YES "
        + original_raster + " " + save_path)

    # 2. Calculate the info for the clipped raster
    os.system("gdalinfo -stats " + save_path)


def merge(raster_list, merge_name):
    """
    Function merges all rasters in the input 'raster list' into one single .tif raster. At intersecting points, the
    merge function gets the highest value (does not average)
    :param raster_list: list or array with the path of every raster to merge
    :param merge_name: file name + extension with which to save the resulting merged raster file
    :return: ---
    """
    # Save array with raster paths to a list
    files_to_mosaic = raster_list.tolist()
    # Merge all rasters in raster_list
    g = gdal.Warp(merge_name, files_to_mosaic, format="GTiff", )
    g = None


def warp_resample(output, input, resolution):
    """
    Function resamples the input raster to a given resolution, using nearest neighbors and the gdal warp function
    :param output: path of output, resampled raster path plus name (must include extension .tif)
    :param input: path of raster to resample (including name.extension)
    :param resolution: cell resolution of the resulting raster
    :return: ---
    """
    # Generate options file: Nearest neighbor resampling algorithm and X resolution = Y resolution = user input
    options = gdal.WarpOptions(resampleAlg='near', xRes=resolution, yRes=resolution)
    r = gdal.Warp(output, input, options=options)
    r = None


def compare_extents(raster_path1, raster_path2):
    """
    Function compares the number of rows and columns of 2 input rasters. If they differ, do something.
    :param raster_path1: raster path (path and file name.extension)
    :param raster_path2: (path and file name.extension)
    :return: ---
    """
    # Get raster 1 data:
    raster1 = gdal.Open(raster_path1)  # Extract raster from path
    XSize1 = raster1.RasterXSize  # Number of columns
    YSize1 = raster1.RasterYSize  # Number of rows

    raster2 = gdal.Open(raster_path2)  # Extract raster from path
    XSize2 = raster2.RasterXSize  # Number of columns
    YSize2 = raster2.RasterYSize  # Number of rows

    if not XSize1 == XSize2 or not YSize1 == YSize2:
        message = "Raster {} and {} have different raster resolutions and/or number of rows and columns. " \
                  "Check input rasters".format(os.path.basename(raster_path1), os.path.basename(raster_path2))
        sys.exit(message)
    # else:
    #     print("Rasters {} and {} have the same resolution".format(os.path.basename(raster_path1),
    #                                                                os.path.basename(raster_path2)))


def get_resolution(raster):
    """
    Function gets the raster resolution (cell size) from the raster GT
    :param raster: raster path
    :return: cell resolution of input raster
    """
    gt, proj = get_raster_data(raster)
    resolution = gt[1]
    return resolution


def save_raster(array, output_path, GT, Proj, nodata):
    """
    Function saves an array into a .tif raster file.
    :param array: raster data to save to array
    :param output_path: file name (with path and extension) with which to save raster array
    :param GT: geotransform of resulting raster
    :param Proj: projection for resulting raster
    :param nodata: no data value with which to save the raster
    :return: ---
    """
    # Step 1: Get drivers in order to save outputs as raster .tif files
    driver = gdal.GetDriverByName("GTiff")  # Get Driver and save it to variable
    driver.Register()  # Register driver variable

    # #Step 2: Create the raster files to save, with all the data: folder + name, number of columns (x), number of
    # rows (y), No. of bands, output data type (gdal type)
    outrs = driver.Create(output_path, xsize=array.shape[1], ysize=array.shape[0], bands=1, eType=gdal.GDT_Float32)

    # Step 3: Assign raster data and assaign the array to the raster
    outrs.SetGeoTransform(GT)  # assign geo transform data from the original input raster (same size)
    outrs.SetProjection(Proj)  # assign projection to raster from original input raster (same projection)
    outband = outrs.GetRasterBand(1)  # Create a band in which to input our array into
    outband.WriteArray(array)  # Read array into band
    outband.SetNoDataValue(nodata)  # Set no data value as Numpy nan
    outband.ComputeStatistics(0)  # Set the raster statistics to the output raster

    # Step 4: Save raster to folder
    outband.FlushCache()
    outband = None
    outrs = None

    print("Saved raster: ", os.path.basename(output_path))

# ------------- ASCII RASTER FUNCTIONS: ---------------------------------------------------------------------------- #


def get_ascii_gt(info_array):
    """
    Function receives the header of a .txt ASCII raster file and rearranges/transforms the data and generates a tuple
    geoTransform variable.
    :param data: header of a .txt ASCII raster file, which corresponds to the ASCII format data, including
     [ncols, nrows, xllcorner, yllcorner, cellsize, nodata_value].
    :return: the GT information, obtained from the header information in the format Top left corner X, cell size, 0,
    Top left corner Y, 0, -cell size
    """
    # Get ulx and uly and cell size (resolution)
    ulx = float(info_array[2])  # Get Xmin (or ulx/llx)
    uly = float(info_array[3] + info_array[4] * info_array[
        1])  # Get uly by adding all the rows above the lly from the header information
    cell_size = float(info_array[4])  # Get cell size directly from the header information

    GT_array = [ulx, cell_size, 0.0, uly, 0, -cell_size]
    GT = tuple(GT_array)  # Convert to type tuple to be read by save raster functions
    # print("GT: ", GT_array)

    return GT


def get_ascii_data(path):
    """
       Function extracts the information from the ASCII file in order to save the ASCII file header
       and extract the information needed to create a GEOTransform file (to later save the raster as a
       .tif file).
       :param file_path: path where a .txt ASCII raster file is located
       :return: the GEOtransform raster information and the ASCII file header (to later save the results)
       """
    # Save the ASCII raster information into a pandas data frame. It will have the following order:
    # ncols, nrows, xllcorner, yllcorner, cellsize, nodata_value
    # IF DELIMITER AND DECIMAL SEPARATOR ARE NOT A SPACE AND A COMMA (respectively) CHANGE THE FOLLOWING LINE
    df_head = pd.read_csv(path, delimiter='\t', header=None, nrows=6)
    # print("Header:\n", df_head)

    # Save info as an array to save the data as GEOtransform type
    info_array = np.array(df_head.iloc[:, 1])

    return info_array


def ascii_to_array(path):
    """
    FUnction reads a .txt ASCII raster and returns the array (ignoring the first 6 lines)
    :param path: path of .txt file (including file name and extension)
    :return: numpy array with raster data
    """
    array = np.array(pd.read_csv(path, delimiter='\t', header=None, skiprows=6))
    return array









