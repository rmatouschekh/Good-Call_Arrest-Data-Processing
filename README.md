# Arrest Data Processing – Good Call

* add_correct_zones.py
  * Processes new arrest data and adds to existing data file
  * Stores aboutput in **arrest_data**
  * Download new arrest data from [NYC Open Data](https://data.cityofnewyork.us/Public-Safety/NYPD-Arrest-Data-Year-to-Date-/uip8-fykc)
    * Replace **NYPD_Arrest_Data__Year_to_Date_.csv** with new file
  * To use, first download [arrest_data.csv](https://drive.google.com/file/d/1CQbzaVZD8SDz0huVwl5_n0E0WkuAQzm6/view?usp=sharing) and place in **arrest_data** folder
  * *Re-run when new arrest data released*
* create_data.py
  * Creates quarter and year specific datafiles for each zone type
  * Stores output in **arrest_data/increase_by_zone**
  * *Re-run when new arrest data released*
* create_gifs.py
  * Creates new figures and gifs
  * Stores output in **gifs**
  * *Re-run whenever new figures needed*
* create_neighborhood_geojson.py
  * Creates geojson file for neighborhoods
  * Stores output in **shapefiles**
  * *Does not need to be re-run*
* data_storage.py
  * Contains data dictionaries used in other files
* get_neighborhood_info.py
  * Creates information for specific neighborhood
  * Stores output in **neighborhood_info**
  * *Re-run whenever new neighborhood data required*
* get_top_facts.py
  * Creates figures and facts describing general arrest trends
  * Stores output in **figures**
* process_census_data.py
  * Processes new census data to create updated zipcode and neighborhood files
  * Stores output in **census_data**
  * Download new census data from [census.gov](https://data.census.gov)
    * Tables to download: DP02, DP03, and DP05
    * Download tables listed by zipcode for New York state
  * *Re-run whenever new census data released*
