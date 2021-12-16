import glob
import os, sys
import pandas as pd
import numpy as np
import gdal
import time

import Resampling as Resample
import RasterCalculations as RC


snowraster_path = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Snow_Codes\Modifications_MF\Results\Ero_Sno\OriginalSnow_201712.tif'
# rainraster_path = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Snow_Codes\Modifications_MF\Results\Ero_Sno\OriginalRain_201712.tif'
results_path = r'Y:\Abt1\hiwi\Oreamuno\Tasks\Snow_Codes\Modifications_MF\Results\Ero_Sno\ResampleOnly'

# --Snap raster path (to get projection): --------------------------------------------------------------------------- #
snapraster_path = r'Y:\Abt1\hiwi\Oreamuno\SY_062016_082019\Rasters\fildemBanja.tif'
snap_boundary = r'Y:\Abt1\hiwi\Oreamuno\SY_062016_082019\Rasters\Boundaries\totalboundary.shp'

# Resample rasters to sample raster resolution and save: ------------------------------------------------------------ #
resampled_snow_name = results_path + "\\ResampledSnow_201712_Code.tif"
resampled_warp_name = results_path + "\\ResampledSnow_201712_warp.tif"


Resample.main(snowraster_path, snapraster_path, snap_boundary, resampled_snow_name)
# Resample.Resample_MainCode(rainraster_path, snapraster_path, snap_boundary, resampled_rain_name)

RC.Warp_Resample(resampled_warp_name, snowraster_path, resolution=25)

resampled_clipped_name = results_path + "\\ResampledSnow_201712_warp_clip.tif"
RC.Clip(r'Y:\Abt1\hiwi\Oreamuno\SY_062016_082019\Clipping_Shapes\Total_Catchment\totalboundary.shp',resampled_clipped_name, resampled_warp_name )