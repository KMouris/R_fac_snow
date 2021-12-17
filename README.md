# The Effect of Snow on Soil Erosion - Routines for R-factor Adaptation in the RUSLE

The Python3 algorithms provided with this repository represent an extension and improvement of the Revised Universal Soil Loss Equation RUSLE ([Renard, 1997](https://www.ars.usda.gov/arsuserfiles/64080530/rusle/ah_703.pdf)) by accounting for snowfall and snowmelt. For this purpose, a modified calculation of one of the RUSLE factors, notably the monthly R-factor, is implemented. The approach was tested with a case study of a mountainous Mediterranean region with seasonal snow coverage.

# Approach
The algorithms take hydro-climatic input data and geo-rasters for distinguishing between precipitation in the form of erosive rain or non-erosive snow. Snow-covered areas are detected at the end of every month based on freely available satellite data (e.g. Sentinel-2). The detected snow cover and the observed snowfall serve for the calculation of monthly snowpack dynamics and snowmelt. Ultimately, the erosivity of precipitation (i.e., rainfall erosivity model for complex terrains according to [Diodato, N., Bellocchi, G., 2007](https://www.sciencedirect.com/science/article/pii/S0022169407004477?via%3Dihub)) and erosion caused by snowmelt is calculated and combined into a revised R-factor.

> Note: Individual modules of the provided codes can be run separately as **STANDALONE scripts** and easily adjusted through modifications in the *config.py* file. For instance, depending on the available input data, some of the pre-processing steps might not be necessary.

## Requirements

The algorithms are written in Python3 ([get installation instructions](https://hydro-informatics.com/python-basics/pyinstall.html)) and build on the following external libraries: *gdal*, *matplotlib.pyplot*, *numpy*, *pandas*, *rasterstats*, *scipy*, *tqdm*

In addition, the following standard Python libraries are used: *calendar*, *datetime*, *glob*, *logging*, *math*, *re*, *os*, *sys*, *time*

## Input Data

The below-listed input arguments and data have to be provided to run the algorithms. The input arguments are variables that can be set in `ROOT/snow_analyst/config_input.py`.

| Input argument | Type | Description |
|----------------|------|-------------|
|`start_date`| *string* | Determines time interval for analysis (format: YYYYMM) |
|`end_date`| *string* | Determines time interval for analysis (format: YYYYMM)  |
|`snapraster_path`| *string* |Path (name.tif) of the raster to which to snap the resampled rasters|
|`shape_path`| *string* |  Path (name.shp) of the shapefile to which to clip the resampled rasters|
|`precipitation_path`| *string* | Folder of precipitation rasters |
|`temperature_path`| *string* | Folder of temperature rasters|
|`si_folder_path`| *string* | Folder of satellite images |
|`fEL_path`| *string* | Path to raster file expressing the influence of site elevation and latitude on the rainfall erosivity|
|`results_path`| *string* |Path of the main result folder|


## Modules of the Algorithm

### pt_raster_manipulation.py

The script contains functions for:

* reading precipitation and temperature values from .txt ASCII raster files (in either monthly, daily, or hourly time intervals); every .txt file corresponds to the data for a given year-month-day-hour (format: YYYYMMDD_HH.txt).
* saving modified data for every raster cell in .csv files with the following information:<br>
`year-month-day-hour-minute-second-Precipitation-Temperature-Row-Column`

**Result folder:** `PT_CSV_per_cell` contains .csv files for every cell  (format: row_columns.csv).

The below table lists input arguments that can be defined in `ROOT/snow_analyst/config_input.py` for setting up data directories for precipitation and temperature rasters.

| Input argument | Type | Description |
|----------------|------|-------------|
|`precipitation_path`| *string* | Folder of precipitation rasters |
|`temperature_path`| *string* | Folder of temperature rasters|


### rain_snow_rasters.py

The script contains functions for:

* determining if precipitation is snow or rain.
* generating a rain and snow raster resampled (Inverse distance weighting) and snapped to a desired raster format based on an example raster (snapraster, e.g. DEM used in RUSLE) or manually defined by the user.

**Result folders:**
  * `rain_per_month` contains monthly rain raster files (.tif) snapped and clipped to a target raster format.
  * `snow_per_month` contains monthly snow raster files (.tif) snapped and clipped to a target raster format.

The below table lists input arguments that can be defined in `ROOT/snow_analyst/config_input.py` for setting up data directories.

| Input argument | Type | Description |
|-----------------|------|-------------|
|`PT_path_input`| *string* | Folder of cell-specific precipitation and temperature over time |
|`T_snow`| *int* | Temperature Threshold for snowfall|
|`snapraster_path`| *string* |Path (name.tif) of the raster to which to snap the resampled rasters|
|`shape_path`| *string* |  Path (name.shp) of the shapefile to which to clip the resampled rasters|


### si_merge_clip.py

The script contains functions for:

* reading input (Sentinel 2) satellite images.
* merging raster bands from different locations (e.g., TDL and TDK).
* clipping merged rasters to a boundary shapefile.
* resampling merged rasters to a (desired) target cell resolution.

**Result folder:** `SatelliteImages` contains post-processed satellite data raster files in target raster format.

The below table lists input arguments that can be defined in `ROOT/snow_analyst/config_input.py` for setting up data directories and file names.

| Input argument | Type | Description |
|----------------|------|-------------|
|`si_folder_path`| *string* | Folder of satellite images |
|`image_list`| LIST | Name (STR) of bands to merge, clip, and resample|
|`image_location_folder_name`| *string* | Name of the folder in which the satellite images are directly located|
|`shape_path`| *string* |  Path (name.shp) of the shapefile to which to clip the resampled rasters|


### snow_cover.py

The script contains functions for:

* reading the band data from every resampled raster band to arrays and determining which areas correspond to snow.
* generating a binary raster, where `1` indicates snow-presence, and `0` indicates snow-absence.

**Result folder:** `snow_cover` contains binary raster for each date (SnowCover_YYYY_MM.tif)

The below table lists input arguments that can be defined in `ROOT/snow_analyst/config_input.py` for setting up data directories and threshold values for snow detection.

| Input argument | Type | Description |
|----------------|------|-------------|
|`si_folder_path`| *string* | Folder of satellite images|
|`NDSI_min`| FLOAT |NDSI threshold|
|`blue_min`| FLOAT | Blue band threshold|


### snow_melt

The script contains functions for:

* calculating monthly snow cover dynamics,
* identification of monthly snowmelt.

**Result folders:**
  * `Snowmelt` contains snowmelt (mm) raster for each date (snowmeltYY_MM.tif).
  * `Snow_end_month` contains accumulated snow (SWE in mm) raster for each date (snow_end_month_YY_MM.tif).

The below table lists input arguments that can be defined in `ROOT/snow_analyst/config_input.py` for setting up data directories.

| Input argument | Type | Description |
|-----------------|------|-------------|
|`snow_raster_input`| *string* | Folder of monthly snowfall|
|`snowcover_raster_input`| *string* |Folder of monthly snowcover|


### Rfactor_REM_db.py

The script contains functions for calculating the R-factor of the RUSLE (i.e., here, a rainfall erosivity model for complex terrains).

**Result folder:** `R_factor_REM_db` contains R-factor raster files based on the rainfall erosivity for every date flag (`RFactor_REM_db_YYYYMM.tif`).

The below table lists input arguments that can be defined in `ROOT/snow_analyst/config_input.py` for setting up data directories and file names.

| Input argument | Type | Description |
|-----------------|------|-------------|
|`rain_raster_input`| *string* | Folder of monthly rainfall|
|`fEL_path`| *string* |Path to raster file expressing the influence of site elevation and latitude on the rainfall erosivity|


### total_R_factor.py

The script contains functions for calculating a total R factor based on the erosive forces of snowmelt and precipitation.

**Result folder:** `R_factor_Total` contains total R factor raster files for every date flag (`RFactor_total_YYYYMM.tif`).

The below table lists input arguments that can be defined in `ROOT/snow_analyst/config_input.py` for setting up data directories and a factor driving snowmelt erosivity.

| Input argument | Type | Description |
|-----------------|------|-------------|
|`r_factor_input`| *string* | Folder of monthly rainfall erosivity|
|`snow_factor`| *int* |Factor accounting for snowmelt erosivity|


# Code diagrams
![R_fac_snow_diagram](https://user-images.githubusercontent.com/65073126/134778560-534a8ebd-f428-43c2-bcc6-0a90281f08b9.jpg)

## snow_melt
![snow_melt_diagram](https://user-images.githubusercontent.com/65073126/134778556-fdaf66b8-f8d1-4442-864b-55181e7e5989.jpg)

## Rfactor_REM_db
![Rfactor_diagram](https://user-images.githubusercontent.com/65073126/134778584-3b4eee05-09ce-4f70-86de-eab7978c5c79.jpg)

# Disclaimer

No warranty is expressed or implied regarding the usefulness or completeness of the information and documentation provided. References to commercial products do not imply endorsement by the Authors. The concepts, materials, and methods used in the algorithms and described in the documentation are for informational purposes only. The Authors has made substantial effort to ensure the accuracy of the algorithms and the documentation, but the Authors shall not be held liable, nor his employer or funding sponsors, for calculations and/or decisions made on the basis of application of the scripts and documentation. The information is provided "as is" and anyone who chooses to use the information is responsible for her or his own choices as to what to do with the data. The individual is responsible for the results that follow from their decisions.

This web site contains external links to other, external web sites and information provided by third parties. There may be technical inaccuracies, typographical or other errors, programming bugs or computer viruses contained within the web site or its contents. Users may use the information and links at their own risk. The Authors of this web site excludes all warranties whether express, implied, statutory or otherwise, relating in any way to this web site or use of this web site; and liability (including for negligence) to users in respect of any loss or damage (including special, indirect or consequential loss or damage such as loss of revenue, unavailability of systems or loss of data) arising from or in connection with any use of the information on or access through this web site for any reason whatsoever (including negligence).

## Authors
- Kilian Mouris
- Maria Fernanda Morales Oreamuno
- Sebastian Schwindt
