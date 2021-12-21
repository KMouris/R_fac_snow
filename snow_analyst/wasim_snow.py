"""Additional module which uses snow storage from hydrological model instead of satellite imagery to simulate snow
processes
1. load snow storage rasters
2. resample and snap snow storage rasters
"""
import config_input
from package_handling import *
import resampling
import file_management


def main():
    # 1. Get all file paths into a list: All raster files must be .txt format
    snow_raster_wasim_paths = sorted(glob.glob(config_input.snow_wasim_path + "/*.txt"))

    # 2. Filter raster list to only include rasters corresponding to the analysis date range
    snow_raster_wasim_paths = file_management.filter_raster_lists(snow_raster_wasim_paths, config_input.start_date, config_input.end_date,
                                                             "WaSim snow raster")

    # 3. loop trough list and resample snow storage rasters
    for i in snow_raster_wasim_paths:
        # 3.1 Extract date from raster files
        date = file_management.get_date(i)

        # 3.2 Resample raster to sample resolution and save with the correct date (make function)
        original_snow_storage_name = os.path.join(config_input.snow_wasim_path, i)
        resampled_snow_storage = os.path.join(config_input.results_path, f'wasim', f"Snow_WaSim_{str(date.strftime('%Y%m'))}.tif")
        resampling.main(original_snow_storage_name, config_input.snapraster_path, config_input.shape_path, resampled_snow_storage)

        # 3.3 create binary rasters to detect snow cover similar to satellite imagery
        # 3.3.1 extract information
        dataset, array, geotransform = gu.raster2array(os.path.join(config_input.results_path, f'wasim', f"Snow_WaSim_{str(date.strftime('%Y%m'))}.tif"))

        # 3.3.2 create binary raster using 10 mm threshold as snow cover
        snowcover = np.where(array > 10, 1, 0)
        binary_wasim = os.path.join(file_management.snow_cover_path, f"Snow_WaSim_binary_{str(date.strftime('%Y%m'))}.tif")
        gu.create_raster(binary_wasim, snowcover, epsg=32634, nan_val=-9999, rdtype=gdal.GDT_UInt32, geo_info=geotransform)


if __name__ == '__main__':
    main()
