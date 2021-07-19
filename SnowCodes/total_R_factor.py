from config_input import *
import file_management
import raster_calculations


def main():
    # 1. Get lists with Rfactor and snow melt rasters
    filenames_r_factor = sorted(glob.glob(r_factor_path + "\*.tif"))
    filenames_snow_melt = sorted(glob.glob(snow_melt_path + "\*.tif"))

    # 2. Filter precipitation raster list to only include rasters corresponding to the analysis date range
    filenames_r_factor = file_management.filter_raster_lists(filenames_r_factor, start_date, end_date,
                                                             "R factor")
    filenames_snow_melt = file_management.filter_raster_lists(filenames_snow_melt, start_date, end_date,
                                                              "snow melt")

    # 3. Check that files are in order and correspond to the same dates:
    file_management.compare_dates(filenames_r_factor, filenames_snow_melt, "R factor", "snow melt")

    # 4. Check raster extents:
    raster_calculations.compare_extents(filenames_r_factor[0], filenames_snow_melt[0])

    # 5. Get raster data (GEOtransform and projection from any raster:
    gt, proj = raster_calculations.get_raster_data(filenames_r_factor[0])

    # 6. Loop through each file (date) in each raster list:
    for R, S in zip(filenames_r_factor, filenames_snow_melt):
        date = file_management.get_date(R)

        # 6.1 Extract data from snow melt into masked array:
        s_array = raster_calculations.raster_to_array(S, mask=True)

        # 6.2 Extract data from R factor raster
        r_array = raster_calculations.raster_to_array(R, mask=True)

        # 6.3 Multiply snow melt raster by the snow multiplication factor to get snow melt factor
        s_array = np.multiply(s_array, snow_factor)

        # 6.4 Add the R factor and S factor values:
        total_factor = np.add(s_array, r_array)

        # 6.5 Unmask arrays: convert masked cells to np.nan
        total_factor = np.where(total_factor.mask == True, np.nan, total_factor)

        # 6.6 Save rasters:
        output_name = total_factor_path + "\\RFactor_total_" + str(date.strftime('%Y%m')) + ".tif"
        raster_calculations.save_raster(total_factor, output_name, gt, proj, nodata=np.nan)


if __name__ == '__main__':
    main()
