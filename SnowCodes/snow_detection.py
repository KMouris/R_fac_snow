import config_input
from config_input import *
import file_management
import raster_calculations as rc

"""
Authors: Kilian Mouris and María Fernanda Morales Oreamuno 

2 step program: 
    1. Reads input Sentinel 2 satellite images and first merges the B02, B03, B04 and B11 raster bands from 2 satellites
     (TDL and TDK) and the clips the merged raster to the boundary shapefile and then resamples them to a 25x25 cell
      resolution .tif raster
    2. Reads the band data from each resampled raster band to arrays and determines which areas corresponds to snow in
     the satellite images.
NOTES: 
- Main function "calculate_snow_cover" does all the calculations for one sensing date at a time. 
- Program can be run individually or through "SnowCode_Main"
- Program generates a binary raster, where 1 means there is snow presence, and 0 means there is none. 
- An error is generates if any of the needed bands (02, 03, 04, 11) are not available. If the TCI rasters are not 
available, the program will skip this step, since it is not necessary for the calculations. 

Input files: [In Input_configuration]
1. SI_folder_path: Folder with satellite images for a given date: folder must have a subfolder for each satellite 
(e.g. one for TDL and one for TDK)
2. image_list: Name of bands to merge, clip and resample. The name in the list must correspond to the final suffix of 
the satellite image name (DO NOT CHANGE)
3. image_location_folder_name: Name of the folder in which the satellite images are directly located (IMG_DATA)
4. shape_path: path (location in folder + name.shp) of the shapefile with which to clip the resampled rastersshape file: 
5. Thresholds for snow detection (NDSI, Red and Blue)

"""


def find_image_path(suffix, path):
    """
    Function loops through each file in the folder "path" and looks for the file whose last 3 digits correspond to
     "suffix" and return the given file's path. If the file does not exist, and it should correspond to a band (02, 03,
     04, or 11) it generates an error. If it corresponds to "TCI", it is not necessary for calculation purposes so it
     returns a "0" in order to break the loop.
    :param suffix: Last 3 digits in the image name to merge in the given loop
    :param path: folder path in which the satellite images are located, and which should be looped to find the image
     with the given suffix
    :return: the complete image path, if the file with suffix "suffix" exists. If it doesn't, and the suffix is "TCI"
    then it returns a value of "0", and the loop is broken in the main loop.
    """
    for file in os.listdir(path):
        name = os.path.splitext(os.path.basename(file))[0]
        if name[-3:] == suffix:
            file_name = file
            break
    try:
        complete_path = path + "\\" + file_name
        return complete_path
    except UnboundLocalError:
        if suffix == "TCI":
            return "0"
        else:
            message = "There is no {} band in satellite image input. Check input files."
            sys.exit(message)


def calculate_snow_cover(folder, date):
    """
    Main function to calculate the snow cover.
    :param folder: Folder where satellite images to use are located. The file name should have the sensing date in the
     name in format "YYYYMMDD"
    :param date: analysis date being looped through or being analyzed
    :return: ---
    """
    # --------------------------------- Satellite Image Merge and Clip ---------------------------------------------- #
    print(" Analyzing date {} with satellite image sensing date {}". format(date.strftime('%Y%m'), folder))

    sat_time = time.time()

    # Get satellite image date -------------------------------------------------------------------------------------- #
    si_date = file_management.get_date(folder)

    # Generate folder in which to save the results from the satellite clip and merge for the given date ------------- #
    # ---- Generate a folder to save the Satellite Clipping and Merging
    SI_results = snow_cover_path + "\\" + "SatelliteImages"
    file_management.create_folder(SI_results)
    # ---- Generate a folder to save the resulting rasters for the given date CHANGE NAME IF A SPECIFIC FORMAT IS NEEDED
    SI_results = SI_results + "\\" + str(si_date.strftime("%Y%m%d"))
    file_management.create_folder(SI_results)

    # -- Save to a list all folders in main folder (each sub-folder corresponds to a satellite image location) ------ #
    satellite_list = os.listdir(folder)

    # -- Loop through each sub-folder to find the location of the "image_location_folder_name" ---------------------- #
    location_images = np.full(len(satellite_list), "", dtype=object)  # array to save the location where images are
    for i in range(0, len(satellite_list)):  # Loop through each satellite
        path = folder + "\\" + satellite_list[i]  # Satellite [i] complete path
        # Search all files and subdirectories for image location folder (input) and save to an array
        for root, dirs, files in os.walk(path):
            if os.path.basename(root) == image_location_folder_name:
                location_images[i] = root
                break

    # --- LOOP: through each suffix or band name to merge and clip -------------------------------------------------- #
    band_results = []
    for suffix in image_list:  # Call variable from configuration
        print("Suffix: ", suffix)
        images = np.full(location_images.shape, "", dtype=object)
        # -- Search the files for each satellite to find the satellite image corresponding to the given suffix ------ #
        for i in range(0, location_images.shape[0]):  # Search in each file location folder for each satellite
            # Save the complete satellite image path for the given suffix, for each satellite
            # images[i] = file_management.FindImagePath(suffix, location_images[i])
            images[i] = find_image_path(suffix, location_images[i])

        # -- 0. Check list ------------------------------------------------------------------------------------------ #
        if any(i == "0" for i in images):
            print("There are no TCI images in one or more of the satellite image files for {}. Skipping rasters".format(str(si_date.strftime("%Y%m%d"))))
            break

        # -- 1. Merge all images in the list ------------------------------------------------------------------------ #
        merge_name = SI_results + "\\Merged_" + suffix + "_" + si_date.strftime("%Y%m%d") + ".tif"
        rc.merge(images, merge_name)

        # -- 2. Check merged resolution ----------------------------------------------------------------------------- #
        # Check if merged rasters have the same resolution. If not, resample to smaller resolution. So all original
        # merged rasters have the same resolution before clipping
        resol = rc.get_resolution(merge_name)
        if resol == 10:
            pass
        else:  # Resample rasters that have a resolution different to 10x10
            name2 = merge_name
            merge_name = SI_results + "\\Merged_" + suffix + "_" + si_date.strftime("%Y%m%d") + "resampled.tif"
            rc.warp_resample(merge_name, name2, resolution=10)
            print("Resampling {} raster from 20 to 10".format(suffix))
            if os.path.exists(name2):
                os.remove(name2)

        # -- 3. Clip the merged rasters to shapefile ---------------------------------------------------------------- #
        clip_name = SI_results + "\\" + suffix + "_" + si_date.strftime("%Y%m%d") + "_clip.tif"
        rc.clip(shape_path, clip_name, merge_name)

        # -- 4. Resample clipped raster ----------------------------------------------------------------------------- #
        if file_management.has_number(suffix):
            resample_name = SI_results + "\\" + suffix + "_" + si_date.strftime("%Y%m%d") + "_r.tif"
            rc.warp_resample(resample_name, clip_name, resolution=25)

            # Add band rasters to a list to later assign them to bands
            band_results.append(resample_name)

        # -- 5. Erase merged file (can be commented out if user wants to save merged file) -------------------------- #
        if os.path.exists(merge_name):
            os.remove(merge_name)

    print("Time to Merge-Clip satellite image data: ", time.time() - sat_time)

    # --------------------------------- Snow Detection Calculation -------------------------------------------------- #

    Band2 = band_results[0]  # B02 raster
    Band3 = band_results[1]  # B03 raster
    Band4 = band_results[2]  # B04 raster
    Band11 = band_results[3]  # B11 raster

    # Extract raster, raster data as array, raster geotransform
    blue_dataset, blue_array, blue_geotransform = gu.raster2array(Band2)
    green_dataset, green_array, green_geotransform = gu.raster2array(Band3)
    red_dataset, red_array, red_geotransform = gu.raster2array(Band4)
    SWIR_dataset, SWIR_array, SWIR_geotransform = gu.raster2array(Band11)


    # NDSI calculation
    NDSI = (green_array-SWIR_array)/(green_array+SWIR_array)

    # Calculate Snow Array
    red_blue = np.where(np.logical_and(red_array > red_min, blue_array > blue_min), 1, 0)
    Snow = np.where(np.logical_and(NDSI>NDSI_min, red_blue == 1), 1, 0)

    # Save resulting snow Raster
    snow_raster = snow_cover_path + "\\SnowCover_" + date.strftime("%Y%m") + ".tif"
    np.savetxt('Snow', Snow, fmt='%s')
    gu.create_raster(snow_raster, Snow, epsg=32634, nan_val=-9999, rdtype=gdal.GDT_UInt32, geo_info=blue_geotransform)


def main():
    """
    QUESTION: IF RUNNING FILE INDIVIDUALLY, DO I ALLOW IT TO BE ONLY FOR 1 MONTH OR TO I PUT HERE THE SAME LOOP AS IN
    THE MAIN CODE?
    :return:
    """
    calculate_snow_cover(SI_folder_path, start_date)

if __name__ == '__main__':
    print("Running code directly")
    main()

