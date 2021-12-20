from package_handling import *

"""
File contains direct raster calculation functions, including .tif files (using gdal) and ASCII .txt files.
"""


def get_snap_raster_data(raster_path):
    """
    Function extracts the raster from input file and gets the basic information such as: GeoTransform, Projection,
    Extension (as an array with ulx, uly, lrx, lry) and cell resolution

    Args:
    :param raster_path: string, with path where the snap raster is located (including name and .tif extension)

    :return: tuples, with geotransform, tuple with projection, list with snap raster extension, float with cell size
    """
    raster = gdal.Open(raster_path)  # Extract raster from path
    gt = raster.GetGeoTransform()  # Get GEOTransform Data: (Top left corner X, cell size, 0, Top left corner Y, 0,
    # -cell size)
    proj = raster.GetProjection()  # Get projection of raster
    x_size = raster.RasterXSize  # Number of columns
    y_size = raster.RasterYSize  # Number of rows

    cell_size = gt[1]  # Cell resolution
    ulx = gt[0]  # Upper left X or Xmin
    lrx = ulx + cell_size * x_size  # Lower right X or Xmax

    uly = gt[3]  # Upper left Y or Ymax
    lry = uly - cell_size * y_size  # Lower right Y or Ymin

    snap_data = [ulx, uly, lrx, lry]  # Upper left X, Upper left Y, Lower right X, Lower right Y

    return gt, proj, snap_data, cell_size  # Return all 4 variables


def get_raster_data(raster_path):
    """
    Function extracts only the GEOTransform and projection from a raster file

    Args:
    :param raster_path: string, raster file path

    :return: tuples with GEOTransform and projection
    """
    raster = gdal.Open(raster_path)  # Extract raster from path
    gt = raster.GetGeoTransform()  # Get GEOTransform Data: (Top left corner X, cell size, 0, Top left corner Y, 0,
    # -cell size)
    proj = raster.GetProjection()  # Get projection of raster

    return gt, proj


def create_masked_array(array, no_data):
    """
    Function masks the no_data values in an input array, which contains the data values from a raster file

    Args:
    :param array: np.array to mask
    :param no_data: float with value to mask in array
    :return: masked np.array
    """
    mskd_array = np.ma.array(array, mask=(array == no_data))  # Mask all nodata values from the array
    if math.isnan(no_data):  # if no data value is 'nan'
        mskd_array = np.ma.masked_invalid(array)
    return mskd_array


def raster_to_array(raster_path, mask):
    """
    Function extracts raster data from input raster file and returns a non-masked array

    Args:
    :param raster_path: string, path for .tif raster file
    :param mask: boolean, which is True when user wants to mask the array and False when you want the original array

    :return: np.array or masked np.array (masking no data values)

    Note: since the input rasters could have different nodata values and different pixel precision, the nodata
    and the raster data are all changed to np.float32 to compare them with the same precision.
    """
    raster = gdal.Open(raster_path)
    band = raster.GetRasterBand(1)
    no_data = np.float32(band.GetNoDataValue())

    array = np.float32(band.ReadAsArray())
    if mask:
        masked_array = create_masked_array(array, no_data)
        return masked_array
    else:
        return array


def clip(clip_path, save_path, original_raster):
    """
    Function clips the raster to the same extents as the snap raster (same no-data cells) using gdal.warp

    Args:
    :param clip_path: string, path where the .shp file, with which to clip input raster
    :param save_path: string, file path (including extension and name) where to save the clipped raster
    :param original_raster: string, path of raster to clip to shape extent (interpolated raster)

    :return: ---
    """
    # Clip the interpolated (resampled) precipitation raster with the bounding raster shapefile from step 3
    os.system(
        "gdalwarp -cutline " + clip_path +
        " -crop_to_cutline -dstnodata -9999 -overwrite --config GDALWARP_IGNORE_BAD_CUTLINE YES "
        + original_raster + " " + save_path)

    # Calculate the info for the clipped raster
    os.system("gdalinfo -stats " + save_path)


def merge(raster_list, merge_name):
    """
    Function merges all rasters in the input 'raster list' into one single .tif raster. At intersecting points, the
    merge function gets the highest value (does not average)

    Args:
    :param raster_list: list or array with the path of every raster to merge
    :param merge_name: path with file name + extension with which to save the resulting merged raster file

    :return: ---
    """
    # Save array with raster paths to a list
    files_to_mosaic = raster_list.tolist()
    # Merge all rasters in raster_list
    g = gdal.Warp(merge_name, files_to_mosaic, format="GTiff", )
    g = None


def warp_resample(output_raster, input_raster, resolution):
    """
    Function resamples the input raster to a given resolution, using nearest neighbors and the gdal warp function

    Args:
    :param output_raster: string, path of output, resampled raster path plus name (must include extension .tif)
    :param input_raster: string, path of raster to resample (including name.extension)
    :param resolution: int, cell resolution of the resulting raster

    :return: ---
    """
    # Generate options file: Nearest neighbor resampling algorithm and X resolution = Y resolution = user input
    options = gdal.WarpOptions(resampleAlg='near', xRes=resolution, yRes=resolution)
    r = gdal.Warp(output_raster, input_raster, options=options)
    r = None


def compare_extents(raster_path1, raster_path2):
    """
    Function compares the number of rows and columns of 2 input rasters. If they differ, function generates an error
    and exits program.

    Args:
    :param raster_path1: raster path (path and file name.extension)
    :param raster_path2: (path and file name.extension)

    :return: ---
    """
    # Get raster 1 data:
    raster1 = gdal.Open(raster_path1)  # Extract raster from path
    x_size1 = raster1.RasterXSize  # Number of columns
    y_size1 = raster1.RasterYSize  # Number of rows

    raster2 = gdal.Open(raster_path2)  # Extract raster from path
    x_size2 = raster2.RasterXSize  # Number of columns
    y_size2 = raster2.RasterYSize  # Number of rows

    if not x_size1 == x_size2 or not y_size1 == y_size2:
        message = "Raster {} and {} have different raster resolutions and/or number of rows and columns. " \
                  "Check input rasters".format(os.path.basename(raster_path1), os.path.basename(raster_path2))
        sys.exit(message)


def get_resolution(raster):
    """
    Function gets the raster resolution (cell size) from the raster GEOTransform

    Args:
    :param raster: string, raster path

    :return: float, cell resolution of input raster
    """
    gt, proj = get_raster_data(raster)
    resolution = gt[1]
    return resolution


def save_raster(array, output_path, gt, proj, no_data):
    """
    Function saves an array into a .tif raster file.

    Args:
    :param array: np.array with raster data to save
    :param output_path: string, file path (with nam and extension) with which to save raster array
    :param gt: tuple, GEOTransform of resulting raster
    :param proj: tuple, projection for resulting raster
    :param no_data: float, no data value with which to save the raster

    :return: ---
    """
    # Step 1: Get drivers in order to save outputs as raster .tif files
    driver = gdal.GetDriverByName("GTiff")  # Get Driver and save it to variable
    driver.Register()  # Register driver variable

    # #Step 2: Create the raster files to save, with all the data: folder + name, number of columns (x), number of
    # rows (y), No. of bands, output data type (gdal type)
    outrs = driver.Create(output_path, xsize=array.shape[1], ysize=array.shape[0], bands=1, eType=gdal.GDT_Float32)

    # Step 3: Assign raster data and assaign the array to the raster
    outrs.SetGeoTransform(gt)  # assign geo transform data from the original input raster (same size)
    outrs.SetProjection(proj)  # assign projection to raster from original input raster (same projection)
    outband = outrs.GetRasterBand(1)  # Create a band in which to input our array into
    outband.WriteArray(array)  # Read array into band
    outband.SetNoDataValue(no_data)  # Set no data value as Numpy nan
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

    Args:
    :param info_array: np.array with header information of a .txt ASCII raster file, which corresponds to the ASCII
    format data, including [ncols, nrows, xllcorner, yllcorner, cellsize, nodata_value].

    :return: the GT information, obtained from the header information in the format Top left corner X, cell size, 0,
    Top left corner Y, 0, -cell size
    """
    # Get ulx and uly and cell size (resolution)
    ulx = float(info_array[2])  # Get Xmin (or ulx/llx)
    uly = float(info_array[3] + info_array[4] * info_array[
        1])  # Get uly by adding all the rows above the lly from the header information
    cell_size = float(info_array[4])  # Get cell size directly from the header information

    gt_array = [ulx, cell_size, 0.0, uly, 0, -cell_size]
    geotransform = tuple(gt_array)  # Convert to type tuple to be read by save raster functions

    return geotransform


def get_ascii_data(path):
    """
    Function extracts the information from the ASCII file in order to save the ASCII file headerband extracts the
    information needed to create a GEOTransform file (to later save the raster as a.tif file).

    Args:
    :param path: path where a .txt ASCII raster file is located

    :return: the GEOTransform raster information and the ASCII file header (to later save the results)
       """
    # Save the ASCII raster information into a pandas data frame. It will have the following order:
    # ncols, nrows, xllcorner, yllcorner, cellsize, nodata_value
    # IF DELIMITER AND DECIMAL SEPARATOR ARE NOT A SPACE AND A COMMA (respectively) CHANGE THE FOLLOWING LINE
    df_head = pd.read_csv(path, delimiter='\t', header=None, nrows=6)
    # print("Header:\n", df_head)

    # Save info as an array to save the data as GEOTransform type
    info_array = np.array(df_head.iloc[:, 1])

    return info_array


def ascii_to_array(path):
    """
    Function reads a .txt ASCII raster and returns the array (ignoring the first 6 lines)

    Args:
    :param path: path of .txt file (including file name and extension)

    :return: numpy array with raster data
    """
    array = np.array(pd.read_csv(path, delimiter='\t', header=None, skiprows=6))
    return array
