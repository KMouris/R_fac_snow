"""
Code resamples an input raster to the extent and cell resolution of (snap) raster. It follows the following steps:
    1. Saves input (original) raster to an array and extracts the coordinates and data value from each cell center
    2. Saves the XYZ coordinates to a .csv file and then into a .vrt file
    3. Gets the coordinates of the output raster cells (from the snap raster's resolution and extent) and interpolates
     the value at these new points, using the XYZ data from the original raster.
        3.1 The code uses an "Inverse Distance Weighted with Nearest Neighbor" interpolation algorithm from gdal_warp
    4. Clips the resampled raster to the snap raster extent, or to the extent of the input shape boundary.
"""

from config_input import *
import raster_calculations as rc


start_time = time.time()


# ----------------Save FUNCTIONS----------------------------------------------------------------------------- #

def save_csv(points, save_name):
    """
    Function receives an array with X, Y, Z point coordinates and converts it to a dataframe, with the corresponding
    column names and then saves the data frame as a .txt file

    :param points: np.array with (X,Y,Z) coordinates of cell centers
    :param save_name: file path name with which to save input point array to .txt format
    :return:
    """
    columns = ["x", "y", "z"]  # Set column names
    df = pd.DataFrame(data=points, index=None, columns=columns)  # Save points array to a pandas data frame
    # print(df)

    # Save table to .txt format
    df.to_csv(save_name, index=False, sep=',', na_rep="", decimal='.')


# ----------------Calculation FUNCTIONS----------------------------------------------------------------------------- #

def get_raster_points(array, gt):
    """
    Function gets the coordinates (X, Y, Z) of the center of all cells that have values and returns an array with the
    coordinate point data

    :param array: npp.array with original raster data
    :param gt: tuple with original raster geotransform data
    :return: np.array where the coordinate and values of the value cell centers are saved
    """

    # 1. Get [y,x] [rows, columns] coordinates of all cells where there are values (non np.nan)
    coord = np.argwhere(~np.isnan(array))
    # print(coord.shape)

    # 2. Initialize an array with the same number of rows as non-zero cell values and 3 columns (X, Y, Z values)
    points = np.zeros((int(coord.shape[0]) - 1, 3))

    # 3. Get upper left corner coordinates from Geotransform (Top left corner X, cell size, 0, Top left corner Y, 0,
    # -cell size)
    upper_left_x = gt[
        0]  # X coordinate of upper left corner. From this point, all cells go towards the right (positive)
    upper_left_y = gt[3]  # Y coordinate of upper left corner. From this point all points go south (negative)
    size = gt[1]  # Cell resolution

    # print("gt: ", gt)
    # print("Upper Left X: ", upper_left_x, "\nUpper Left Y: ", upper_left_y, "\nSize: ", size)

    for i in range(0, int(coord.shape[0]) - 1):  # go through all cells in coord array
        # 1.Fill in x coordinate in row 0
        points[i][0] = upper_left_x + coord[i][1] * size + (size / 2)

        # 2.Fill in x coordinate in row 1
        points[i][1] = upper_left_y - coord[i][0] * size - (size / 2)

        # 3. Fill in the precipitation value in row 2
        points[i][2] = array[int(coord[i][0])][int(coord[i][1])]
        # print("Index in coord: ", i, " - Row in Array: ", points[i][0], " - Column in array: ", points[i][1],
        #       " - Value: ", points[i][2] )

    # print("Points: ", points[0][2])

    # # The name of the .csv file must be "file" and it must be in the program working folder for it to be later read
    # a .vrt file # In the VRT_File function. Does not work otherwise. FIle will be rewritten in each loop and erased
    # at the end. points_path = "file.csv"  # Create the .csv file name as "file.csv" - SaveCSV(points, points_path)
    # Save the XYZ coordinates array to a .csv file

    return points  # Return XYZ.csv file path


def generate_vrt_file(csv_file):
    """
    Function receives a .csv file path, which was created in the "GetRasterPoints" and is then copied to a vrt file.
    The .csv file MUST BE named "file", since that name is automatically called in the vrt file creation.

    :param csv_file: .csv file path with point coordinates (x,y,z) generated in "GetRasterPoints" function
    :return: .vrt file path
    """
    # Create a .vrt file with the same name as .csv by changing the extension to .vrt (virtual). .vrt file will be
    # overwritten in each loop and erased at the end of the loop
    vrt_name = csv_file.replace(".csv", ".vrt")

    # print("Name \'VRT\': ", vrt_name)

    # Check if VRT file previously exists. If it does, erase it:
    if os.path.exists(vrt_name):
        os.remove(vrt_name)

    # Create VRT file with coordinate information (located in file.csv file) :
    vrt = open(vrt_name, 'w')  # Open .vrt file
    # Create the .vrt file with the following code, which remains constant always
    vrt.write("<OGRVRTDataSource>\n \
        <OGRVRTLayer name=\"file\">\n \
        <SrcDataSource>file.csv</SrcDataSource>\n \
        <SrcLayer>file</SrcLayer> \n \
        <GeometryType>wkbPoint25D</GeometryType>\n \
        <LayerSRS>EPSG:32634</LayerSRS>\n \
        <GeometryField encoding=\"PointFromColumns\" x=\"x\" y=\"y\" z=\"z\"/>\n \
        </OGRVRTLayer>\n \
        </OGRVRTDataSource>")
    vrt.close()

    # Print the information in the .vrt file to make sure it is working correctly (and full).
    # os.system("ogrinfo -al " + vrt_name)

    return vrt_name


def interpolate_points(vrt_file, folder, snap_data, cell_size):
    """
    Function receives the path of the .vrt file, which contains the XYZ points and uses these points to interpolate
    values for a new raster resolution (cell size)

    :param vrt_file: .vrt virtual file path which contains the original raster cell center coordinates
    :param folder: folder path in which to temporarily save the interpolated raster file
    :param snap_data: np.array with snap raster extension [Xmin, Ymax, Xmax, Ymin] or [ulX ulY lrX lrY]
    :param cell_size: float with cell size of the resulting raster (same as snap raster's)
    :return: path for the interpolated raster file
    """
    # 1.Set raster name: This file will later be eliminated, so name does not matter
    raster_name = folder + "\\InterpolatedRaster.tif"
    # print("Raster name: ", raster_name)

    # 2.Check if raster exists, and if it does, erase if:
    if os.path.exists(raster_name):
        os.remove(raster_name)

    # 3.Get the number of columns and rows that the resampled raster must have. Same as the size of the snap raster
    columns = str(int((snap_data[2] - snap_data[0]) / cell_size))  # Get No. of columns in snap raster (as as string)
    rows = str(int((snap_data[1] - snap_data[3]) / cell_size))  # Get No. of rows in snap raster (as a string)

    # 4.Use gdal grid to interpolate:
    # ---- a:interpolation method (Inv distance with nearest neighbor, with smoothing of 0, using a max number of 12
    # ----- points, searching in a 5000 m radius for those max. 12 points)
    # ---- txe: Xmin Xmax,
    # ---- tye: Ymin, Ymax,
    # ---- outsize: columns rows, of: output file format
    # ---- a_srs: coordinate system, ot: out type (float)
    os.system(
        "gdal_grid -a invdistnn:power=2.0:smoothing=0:max_points=12:radius=5000 -txe " + str(snap_data[0]) + " " + str(
            snap_data[2]) +
        " -tye " + str(snap_data[3]) + " " + str(
            snap_data[1]) + " -outsize " + columns + " " + rows + " -of gtiff -a_srs EPSG:32634 " +
        "-ot Float32 " + vrt_file + " " + raster_name)
    return raster_name


def main(original_raster, snap_raster, snap_boundary, save_name):
    """
    Function is the main code, which calls all other resampling functions in order to resample an input raster to a
    different cell resolution and raster extent

    :param original_raster: path for the original raster (in .tif format), to be resampled to a smaller/larger
        resolution
    :param snap_raster: path of raster from which to get gt and projection in order to resample original raster
    :param snap_boundary: path to shape file with which to clip the resampled raster (.shp)
    :param save_name: file path (with name.ext) with which to save resampled raster
    :return: ---
    """
    print("Running Resampling program")

    # 1. Extract the folder in which to save the results
    results_folder = os.path.dirname(save_name)

    # 2 .Get projection and Geotransform from the snap raster:
    gt, proj, snap_data, cell_resolution = rc.get_snap_raster_data(snap_raster)

    # 3. Save the raster data to an array
    original_array = rc.raster_to_array(original_raster, mask=False)
    # --3.1: Convert all -9999 No data cells into numpy nan values
    original_array = np.where(original_array == -9999.0, np.nan, original_array)

    # 4. Get the gt (geotransform) information from the original raster file
    gt_original, proj_original = rc.get_raster_data(original_raster)  # Get gt information from the ASCII file

    # 5. Get the coordinates of the center of all the cells WITH VALUES and save data the XYZ coordinates for each point
    # to an array
    xyz_array = get_raster_points(original_array, gt_original)  # Path with the .csv file with coordinates

    # 6. Save the XYZ coordinate data to a .csv file
    XYZ_CSV = "file.csv"
    save_csv(xyz_array, XYZ_CSV)  # Save array to .csv file

    # 7. Create a .vrt file from the .csv in order to be read by the gdal grid command
    vrt_file = generate_vrt_file(XYZ_CSV)

    # 8. Interpolate points and save the resampled Monthly precipitation raster in the results folder
    # --7.1 Using GDAL_Grid interpolation
    interpolated_path = interpolate_points(vrt_file, results_folder, snap_data, cell_resolution)

    # 9. Final Step. Clip the resampled raster to the extent of the snap raster
    rc.clip(snap_boundary, save_name, interpolated_path)

    # 10. Erase files that are no longer needed:
    # --10.1 Erase the interpolated raster (before clipping)
    if os.path.exists(interpolated_path):
        os.remove(interpolated_path)

    # --10.2 Erase the vrt file
    if os.path.exists(vrt_file):
        os.remove(vrt_file)

    # --10.3 Erase .csv file with points
    if os.path.exists(XYZ_CSV):
        os.remove(XYZ_CSV)
