
import file_management
from config_input import *
import si_merge_clip as satellite_images

"""
Authors: Kilian Mouris and María Fernanda Morales Oreamuno 

2 step program: 
    1. If 'run_satellite_image_merge_clip' is True', it reads input Sentinel 2 satellite images and first merges the 
        B02, B03, B04 and B11 raster bands from 2 satellites (TDL and TDK) and then clips the merged raster to the 
        boundary shapefile and then resamples them to a 25x25 cell resolution .tif raster. File returns a list with the
        clipped and merges bands, in .tif format.
    2. Reads the band data from each resampled raster band to arrays and determines which areas corresponds to snow in
     the satellite images.
NOTES: 
- Main function "calculate_snow_cover" does all the calculations for one sensing date at a time. 
- Program can be run individually or through "main_snow_codes"
- Program generates a binary raster, where 1 means there is snow presence, and 0 means there is none. 
- An error is generates if any of the needed bands (02, 03, 04, 11) are not available. If the TCI rasters are not 
available, the program will skip this step, since it is not necessary for the calculations. 

Input files/data: [In Input_configuration]
1. SI_folder_path: Folder with satellite images for a given date
    1.1 folder must have a subfolder for each satellite 
        (e.g. one for TDL and one for TDK) in case original satellite images must be clipped and merged. 
    1.2 If input has pre-processed satellite images, the resampled ones must have the band name and '_r' to identify 
        them. 
2. Thresholds for snow detection (NDSI, Red and Blue)

if run_satellite_image_merge_clip: 
1. image_list: Name of bands to merge, clip and resample. The name in the list must correspond to the final suffix of 
the satellite image name (DO NOT CHANGE)
2. image_location_folder_name: Name of the folder in which the satellite images are directly located (IMG_DATA)
3. shape_path: path (location in folder + name.shp) of the shapefile with which to clip the resampled rastersshape file:
"""


def calculate_snow_cover(folder, date):
    """
    Main function to calculate the snow cover.
    :param folder: Folder where satellite images to use are located. The file name should have the sensing date in the
     name in format "YYYYMMDD"
    :param date: analysis date being looped through or being analyzed
    :return: ---
    """
    # --------------------------------- Read Satellite Images to list ---------------------------------------------- #
    print(" Calculating snow cover for date {} with satellite image sensing date: {}".format(date.strftime('%Y%m'),
                                                                                            os.path.split(folder)[1]))
    if run_satellite_image_clip_merge:
        print("     Merging and resampling input satellite images")
        band_results = satellite_images.sat_image_merge_clip(folder)
    else:  # Read pre-processed rasters (clipped and merged) form input folder.
        print("     Reading pre-processed input satellite images")
        band_results = []
        raster_list = glob.glob(folder + "\*.tif")
        if len(raster_list) == 0:  # if there are no .tif files in input folder
            message = "There are no pre-processed rasters available in '{}' folder path. Check user input satellite image folder.".format(folder)
            sys.exit(message)
        for band in image_list:  # Loop through each band name
            if band != "TCI":  # Ignore TCI rasters
                # Check if any file contains the band name, and has a '_r' in the name, identifying it as resampled from
                # the si_merge_clip.py file
                match = [f for f in raster_list if (band in f and "_r" in f)]
                if len(match) == 0:  #If there are no files for the given band: give error
                    s_date = file_management.get_date(folder)
                    message = "ERROR: There is no resampled raster corresponding to band [{}] and sampling date {}. Check input ".format(
                        band, s_date.strftime('%Y%m%d')) +\
                        "\nNOTE: Resampled rasters must be identified by a '_r' in the file name. "
                    sys.exit(message)
                elif len(match) > 1:  # If there is more than one available raster for the given band
                    s_date = file_management.get_date(folder)
                    message = "There is more than 1 available resampled raster file for band [{}] and sampling date {}. Check input.".format(
                    band, s_date.strftime('%Y%m%d'))
                    sys.exit(message)
                else:
                    band_results.append(match[0])

    # --------------------------------- Snow Detection Calculation -------------------------------------------------- #

    Band2 = band_results[0]  # B02 raster
    Band3 = band_results[1]  # B03 raster
    Band11 = band_results[3]  # B11 raster

    # Extract raster, raster data as array, raster geotransform
    blue_dataset, blue_array, blue_geotransform = gu.raster2array(Band2)
    green_dataset, green_array, green_geotransform = gu.raster2array(Band3)
    SWIR_dataset, SWIR_array, SWIR_geotransform = gu.raster2array(Band11)

    # NDSI calculation
    NDSI = (green_array - SWIR_array) / (green_array + SWIR_array)

    # Calculate Snow Array
    snow = np.where(np.logical_and(NDSI > NDSI_min, blue_array > blue_min), 1, 0)

    # Save resulting snow Raster
    snow_raster = snow_cover_path + "\\SnowCover_" + date.strftime("%Y%m") + ".tif"
    np.savetxt('Snow', snow, fmt='%s')
    gu.create_raster(snow_raster, snow, epsg=32634, nan_val=-9999, rdtype=gdal.GDT_UInt32, geo_info=blue_geotransform)


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

