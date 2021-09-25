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

*Python* libraries: *geo_utils*, *gdal*, *matplotlib.pyplot*, *numpy*, *pandas*, *rasterstats*, *scipy*, *tqdm*
> The geo_utils package can be downloaded [here](https://geo-utils.readthedocs.io/en/latest/) and/or the path where the package is saved can be defined in the config.py file.

*Standard* libraries: *calendar*, *datetime*, *glob*, *logging*, *math*, *re*, *os*, *sys*, *time*

## Input Data
The following input data has to be provided to run the whole code:

| Input argument | Type | Description |
|-----------------|------|-------------|
|`start_date`| STRING | Determines time interval for analysis (format: YYYYMM) |
|`end_date`| STRING | Determines time interval for analysis (format: YYYYMM)  |
|`snapraster_path`| STRING |Path (name.tif) of the raster to which to snap the resampled rasters|
|`shape_path`| STRING |  Path (name.shp) of the shapefile to which to clip the resampled rasters|
|`precipitation_path`| STRING | Folder of precipitation rasters |
|`temperature_path`| STRING | Folder of temperature rasters|
|`si_folder_path`| STRING | Folder of satellite images |
|`fEL_path`| STRING | Path to raster file expressing the influence of site elevation and latitude on the rainfall erosivity|
|`results_path`| STRING |Path of the main result folder|


## Modules
Overview of the main modules without detailed explanation of each function.
### pt_raster_manipulation.py
- reads precipitation and temperature values from .txt ASCII raster files (in either monthly, daily or hourly time 
intervals).
- saves the data for each raster cell in .csv files with the following information: 
year-month-day-hour-minute-second-Precipitation-Temperature-Row-Column

| Input argument | Type | Description |
|-----------------|------|-------------|
|`precipitation_path`| STRING | Folder of precipitation rasters |
|`temperature_path`| STRING | Folder of temperature rasters|

Each input .txt file corresponds to the data for the given year-month-day-hour (format: YYYYMMDD_0HH.txt).

**Result folder:** `PT_CSV_per_cell` contains .csv files for every cell  (format: row_columns.csv).

### rain_snow_rasters.py
- determines if precipitation is snow or rain.
- generates a rain and snow raster resampled (Inverse distance weighting) and snapped to a desired raster format based on an example raster (snapraster, e.g. DEM used in RUSLE) or manually defined by the user. 

| Input argument | Type | Description |
|-----------------|------|-------------|
|`PT_path_input`| STRING | Folder of cell-specific precipitation and temperature over time |
|`T_snow`| INTEGER | Temperature Threshold for snowfall|
|`snapraster_path`| STRING |Path (name.tif) of the raster to which to snap the resampled rasters|
|`shape_path`| STRING |  Path (name.shp) of the shapefile to which to clip the resampled rasters|

**Result folder:** 

`rain_per_month` contains monthly rain raster files (.tif) snapped and clipped to target raster format.
  `snow_per_month` contains monthly snow raster files (.tif) snapped and clipped to target raster format.
  
### si_merge_clip.py
- reads input Sentinel 2 satellite images.
- merges raster bands from different locations
(e.g. TDL and TDK).
- clips the merged raster to the boundary shapefile.
- resamples merged rasters to the desired cell resolution.

| Input argument | Type | Description |
|-----------------|------|-------------|
|`si_folder_path`| STRING | Folder of satellite images |
|`image_list`| LIST | Name (STR) of bands to merge, clip and resample|
|`image_location_folder_name`| STRING | Name of the folder in which the satellite images are directly located|
|`shape_path`| STRING |  Path (name.shp) of the shapefile to which to clip the resampled rasters|

**Result folder:** `SatelliteImages` contains post-processed satellite data raster files in target raster format.

### snow_cover.py
- reads the band data from each resampled raster band to arrays and determines which areas correspond to snow.
- generates a binary raster, where 1 means there is snow presence, and 0 means there is none.

| Input argument | Type | Description |
|-----------------|------|-------------|
|`si_folder_path`| STRING | Folder of satellite images|
|`NDSI_min`| FLOAT |NDSI threshold|
|`blue_min`| FLOAT | Blue band threshold|

**Result folder:** `snow_cover` contains binary raster for each date (SnowCover_YYYY_MM.tif)

### snow_melt
- calculates monthly snow cover dynamics
- identifies monthly snowmelt

| Input argument | Type | Description |
|-----------------|------|-------------|
|`snow_raster_input`| STRING | Folder of monthly snowfall|
|`snowcover_raster_input`| STRING |Folder of monthly snowcover|

**Result folder:** 
`Snowmelt` contains snowmelt (mm) raster for each date (snowmeltYY_MM.tif).
`Snow_end_month` contains accumulated snow (SWE in mm) raster for each date (snow_end_month_YY_MM.tif).

### Rfactor_REM_db
- calculates the RUSLE R factor (in this case: Rainfall erosivity model for complex terrains).

| Input argument | Type | Description |
|-----------------|------|-------------|
|`rain_raster_input`| STRING | Folder of monthly rainfall|
|`fEL_path`| STRING |Path to raster file expressing the influence of site elevation and latitude on the rainfall erosivity|

**Result folder:** 
`R_factor_REM_db` contains R factor raster files based on the rainfall erosivity for each date (RFactor_REM_db_YYYYMM.tif).

### total_R_factor.py
- calculates a total R factor based on the erosive forces of snowmelt and precipitation.

| Input argument | Type | Description |
|-----------------|------|-------------|
|`r_factor_input`| STRING | Folder of monthly rainfall erosivity|
|`snow_factor`| INT |Factor which accounts for snowmelt erosivity|

**Result folder:** 
`R_factor_Total` contains total R factor raster files for each date (RFactor_total_YYYYMM.tif).

# Code diagrams 
![R_fac_snow_diagram](https://user-images.githubusercontent.com/65073126/134778560-534a8ebd-f428-43c2-bcc6-0a90281f08b9.jpg)

## snow_melt
![snow_melt_diagram](https://user-images.githubusercontent.com/65073126/134778556-fdaf66b8-f8d1-4442-864b-55181e7e5989.jpg)

## Rfactor_REM_db
![Rfactor_diagram](https://user-images.githubusercontent.com/65073126/134778584-3b4eee05-09ce-4f70-86de-eab7978c5c79.jpg)
