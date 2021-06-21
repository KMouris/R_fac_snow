import file_management
from config_input import *
import raster_calculations as rc

"""
@author: María Fernanda Morales Oreamuno 

File reads input Sentinel 2 satellite images and first merges the B02, B03, B04 and B11 raster bands from 2 satellites
(TDL and TDK) and the clips the merged raster to the boundary shapefile and then resamples them to a 25x25 cell
resolution .tif raster (to match other input raster files)

Receives one folder at a time, corresponding to 1 sensing date, and reads Sentinel 2 satellite images for the given, 
sensing dates. Images corresponding to different satellites (e.g. TDL and TDK) must be in different folders within the 
main sensing date folder, and the satellite images must be in a folder, whose name is a user input under the variable 
'image_location_folder_name'. 

File can be called individually or through the main.py file. 

Needed input files: [in config_input]
1. SI_folder_path: Folder with satellite images for a given date: folder must have a subfolder for each satellite 
(e.g. one for TDL and one for TDK)
2. image_list: Name of bands to merge, clip and resample. The name in the list must correspond to the final suffix of 
the satellite image name (DO NOT CHANGE)
3. image_location_folder_name: Name of the folder in which the satellite images are directly located (IMG_DATA)
4. shape_path: path (location in folder + name.shp) of the shapefile with which to clip the resampled rastersshape file:
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


def sat_image_merge_clip(folder):
    sat_time = time.time()

    # Get satellite image date -------------------------------------------------------------------------------------- #
    si_date = file_management.get_date(folder)

    # Generate folder in which to save the results from the satellite clip and merge for the given date ------------- #
    # ---- Generate a folder to save the Satellite Clipping and Merging
    SI_results = results_path + "\\" + "SatelliteImages"
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
            print("There are no TCI images in one or more of the satellite image files for {}. Skipping rasters".format(
                str(si_date.strftime("%Y%m%d"))))
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

    return band_results


def main():
    # Same code as in main_snow_codes.py
    # Generate a list with all the dates to run through and include in the analysis
    date_list = file_management.get_date_list(start_date, end_date)

    if run_snow_cover:
        si_list = os.listdir(SI_folder_path)  # list with satellite image folders
        if input_si_dates:  # If user inputs the dates to use:
            si_list = file_management.check_input_si_dates(si_list, date_list, si_image_dates)
        else:  # get images whose sensing date is closest to end of month
            if len(si_list) == 2:  # if only 2 folders, only one sensing date was given
                si_list = [os.path.basename(SI_folder_path)]
            # If no dates to directly use (user input), get the satellite image closest to the end of the month.
            si_list = file_management.generate_satellite_image_date_list(si_list, date_list)
        print("Folders to loop through:, ", si_list)
        for f, d in zip(si_list, date_list):
            path = SI_folder_path + "\\" + str(f)
            band_paths = sat_image_merge_clip(path)
            print("Band results: ", band_paths)


if __name__ == '__main__':
    print("Running code directly")
    main()