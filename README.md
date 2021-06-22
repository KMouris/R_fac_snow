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

Note: It is possible to execute individual parts of the code separately. It can be easily adjusted and defined in the config.py file.
Depending on your input data some pre-processing steps might not be necessary. 


## Libraries

Will be added as soon as code is released.

## Modules
Overview of the main modules without an explanation of each function.
### pt_raster_manipulation.py
Code reads precipitation and temperature values from .txt ASCII raster files (in either monthly, daily or hourly time 
intervals) and saves the data for each raster cell in .csv files with the following information: 
year-month-day-hour-minute-second-Precipitation-Temperature-Row-Column

| Input argument | Type | Description |
|-----------------|------|-------------|
|`precipitation_path`| STRING | Folder of precipitation rasters |
|`temperature_path`| STRING | Folder of temperature rasters|

Each input .txt file corresponds to the data for the given year-month-day-hour (format: YYYYMMDD_0HH.txt).

**Result folder:** `PT_CSV_per_cell` contains .csv files for every cell  (format: row_columns.csv)

### rain_snow_rasters.py
Program determines if precipitation is snow or rain, from input .csv files, and generates a rain and snow raster, 
resampled and snapped to a desired cell resolution (based on an example raster (snapraster, e.g. DEM used in RUSLE, or manually defined by the user).

| Input argument | Type | Description |
|-----------------|------|-------------|
|`PT_path_input`| STRING | Folder of cell-specific precipitation and temperature over time |
|`T_snow`| INTEGER | Temperature Threshold for snowfall|
|`snapraster_path`| STRING |path (name.tif) of the raster to which to snap the resampled rasters|
|`shape_path`| STRING |  path (name.shp) of the shapefile to which to clip the resampled rasters|

**Result folder:** 

`rain_per_month` contains monthly rain raster files (.tif) snapped and clipped to example raster
  `snow_per_month` contains monthly snow raster files (.tif) snapped and clipped to example raster
## Input Data
The following rasters have to be provided to run the code:
