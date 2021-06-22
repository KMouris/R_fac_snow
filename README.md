# Effect of snow on soil erosion - Modification of the R-factor calculation

# Introduction
The overall goal of the project is to extend and improve the Revised Universal Soil Loss Equation RUSLE ([Renard, 1997](https://www.ars.usda.gov/arsuserfiles/64080530/rusle/ah_703.pdf))
by including the effects of snowfall and snowmelt. For this purpose the calculation of the monthly R-factor is modified.
The approach was applied and verified to calculate soil erosion in a Mediterranean area with seasonal snow coverage.

The first step is to distinguish between precipitation in the form of rain (erosive) or snow (non-erosive). 
Additionally, snow-covered areas are detected at the end of each month using freely available satellite data (e.g. Sentinel-2). 
Based on the detected snow cover and the observed snow fall, the code calculates monthly snow pack dynamics and snowmelt.
In the final step, the erosivity of precipitation (in this case: Rainfall erosivity model for complex terrains ([Diodato, N., Bellocchi, G., 2007](https://www.sciencedirect.com/science/article/pii/S0022169407004477?via%3Dihub)) and 
the erosivity due to snowmelt are calculated and combined into a total R-factor.

Note: It is possible to execute individual modules of the code separately. It can be easily adjusted and defined in the config.py file.
Depending on your input data some pre-processing steps might not be necessary. 


## Libraries

Will be added as soon as code is released.

## Input Data
The following have to be provided to run the whole code:

| Input argument | Type | Description |
|-----------------|------|-------------|
|`start_date`| STRING | Determines time interval for analysis (format: YYYYMM) |
|`end_date`| STRING | Determines time interval for analysis (format: YYYYMM)  |
|`results_path`| STRING |Path of the main result folder|
|`snapraster_path`| STRING |Path (name.tif) of the raster to which to snap the resampled rasters|
|`shape_path`| STRING |  Path (name.shp) of the shapefile to which to clip the resampled rasters|
|`precipitation_path`| STRING | Folder of precipitation rasters |
|`temperature_path`| STRING | Folder of temperature rasters|
|`T_snow`| INTEGER | Temperature threshold for snowfall|
|`SI_folder_path`| STRING | Folder of satellite images |
|`image_list`| LIST | Name (STR) of bands to merge, clip and resample|
|`image_location_folder_name`| STRING | Name of the folder in which the satellite images are directly located|
|`NDSI_min`| FLOAT |NDSI threshold|
|`blue_red_min`| FLOAT | Blue to red band ratio threshold|
|`blue_min`| FLOAT | Blue band threshold|

## Modules (not complete)
Overview of the main modules without detailed explanation of each function.
### pt_raster_manipulation.py
- reads precipitation and temperature values from .txt ASCII raster files (in either monthly, daily or hourly time 
intervals)
- saves the data for each raster cell in .csv files with the following information: 
year-month-day-hour-minute-second-Precipitation-Temperature-Row-Column

| Input argument | Type | Description |
|-----------------|------|-------------|
|`precipitation_path`| STRING | Folder of precipitation rasters |
|`temperature_path`| STRING | Folder of temperature rasters|

Each input .txt file corresponds to the data for the given year-month-day-hour (format: YYYYMMDD_0HH.txt).

**Result folder:** `PT_CSV_per_cell` contains .csv files for every cell  (format: row_columns.csv)

### rain_snow_rasters.py
- determines if precipitation is snow or rain
- generates a rain and snow raster resampled and snapped to a desired raster format (based on an example raster (snapraster, e.g. DEM used in RUSLE, or manually defined by the user).

| Input argument | Type | Description |
|-----------------|------|-------------|
|`PT_path_input`| STRING | Folder of cell-specific precipitation and temperature over time |
|`T_snow`| INTEGER | Temperature Threshold for snowfall|
|`snapraster_path`| STRING |Path (name.tif) of the raster to which to snap the resampled rasters|
|`shape_path`| STRING |  Path (name.shp) of the shapefile to which to clip the resampled rasters|

**Result folder:** 

`rain_per_month` contains monthly rain raster files (.tif) snapped and clipped to target raster format
  `snow_per_month` contains monthly snow raster files (.tif) snapped and clipped to target raster format

### si_merge_clip.py
- reads input Sentinel 2 satellite images
- merges the B02, B03, B04 and B11 raster bands from different locations
(e.g. TDL and TDK) 
- clips the merged raster to the boundary shapefile
- resamples merged rasters to the desired cell resolution

| Input argument | Type | Description |
|-----------------|------|-------------|
|`SI_folder_path`| STRING | Folder of satellite images |
|`image_list`| LIST | Name (STR) of bands to merge, clip and resample|
|`image_location_folder_name`| STRING | Name of the folder in which the satellite images are directly located|
|`shape_path`| STRING |  Path (name.shp) of the shapefile to which to clip the resampled rasters|

**Result folder:** `snow_cover\SatelliteImages` contains post-processed satellite data raster files in target raster format

### snow_cover.py
- reads the band data from each resampled raster band to arrays and determines which areas correspond to snow
- generates a binary raster, where 1 means there is snow presence, and 0 means there is none

| Input argument | Type | Description |
|-----------------|------|-------------|
|`SI_folder_path`| STRING | Folder of satellite images|
|`NDSI_min`| FLOAT |NDSI threshold|
|`blue_red_min`| FLOAT | Blue to red band ratio threshold|
|`blue_min`| FLOAT | Blue band threshold|

**Result folder:** `snow_cover` contains binary raster for each date (SnowCover_YYYY_MM.tif)

### snow_melt

### Rfactor_REM_db

### total_R_factor.py
- includes calculation of snow erosivity