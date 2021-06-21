import config_input
from config_input import *
import file_management
import raster_calculations as rc
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

Input files: [In Input_configuration]
1. SI_folder_path: Folder with satellite images for a given date: folder must have a subfolder for each satellite 
(e.g. one for TDL and one for TDK) 
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
        band_results = satellite_images.sat_image_merge_clip(folder)
    else:
        pass

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
    NDSI = (green_array - SWIR_array) / (green_array + SWIR_array)
    blue_red_ratio = blue_array / red_array

    # Calculate Snow Array
    red_blue = np.where(np.logical_and(blue_red_ratio > blue_red_min, blue_array > blue_min), 1, 0)
    snow = np.where(np.logical_and(NDSI > NDSI_min, red_blue == 1), 1, 0)

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

