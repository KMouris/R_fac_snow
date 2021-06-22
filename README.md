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
### pt_raster_manipulation.py
Code reads precipitation and temperature values from .txt ASCII raster files (in either monthly, daily or hourly time 
intervals) and saves the data for each raster cell in .csv files with the following information: 
year-month-day-hour-minute-second-Precipitation-Temperature-Row-Column

| Input argument | Type | Description |
|-----------------|------|-------------|
|`precipitation_path`| STRING | Path of precipitation rasters |
|`temperature_path`| STRING | Path of temperature rasters|

Each input .txt file corresponds to the data for the given year-month-day-hour (format: YYYYMMDD_0HH.txt).

**Result folder:** `PT_CSV_per_cell` contains .csv files for every cell  (format: row_columns.csv)

### 

## Input Data
The following rasters have to be provided to run the code:
1. Raster files of temperature and precipitation
1. Raster of measured snow depth 
2. Raster of satellite data of the snow cover with the values 0 and 1, describing if there is snow (1) or if there is not (0)
3. Shapefile defining the zone for the statistical calculations 

Both rasters listed in 1. and 2. have to be provided as `.tif` rasters and have to include the month and the year in the following way:

***yy_mm**.tif

