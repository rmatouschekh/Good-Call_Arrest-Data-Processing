import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
from data_storage import zip_to_neighborhood, legal_code_to_offense

"""
Processes new dataset for year and adds to existing data file
"""

# UPDATE THESE
current_year = 2023
new_data_file = "NYPD_Arrest_Data__Year_to_Date_.csv"
current_data_file = "arrest_data.csv"


# Find the zone for the given object
def get_zone(shapes_df, mode, row):
    if row["geometry"].x == 0:
        return None
    elif mode == "zipcode" and row["geometry"].y == 40.706283 and row["geometry"].x == -73.950348:
        # Hard code answer to common error
        return "11211"
    else:
        # Find possible zones
        poss_zones = shapes_df[shapes_df["geometry"].contains(row["geometry"])]

        if len(poss_zones.index) == 1:
            return poss_zones.iloc[0]["nameCol"]
        
        # If the point is not in any zone, find the zone it is nearest to
        elif len(poss_zones.index) == 0:
            min_dist = 1000
            z = None

            for i, r in shapes_df.iterrows():
                if row["geometry"].distance(r["geometry"]) < min_dist:
                    min_dist = row["geometry"].distance(r["geometry"])
                    z = r["nameCol"]

            return z

        # If the point is in multiple zones, choose the zone it is farthest in to
        else:
            max_dist = 0
            z = None

            for i, r in poss_zones.iterrows():
                if r["geometry"].exterior.distance(row["geometry"]) > max_dist:
                    max_dist = r["geometry"].exterior.distance(row["geometry"])
                    z = r["nameCol"]
            
            return z

# Find corresponding neighborhoods (from zipcode) for each entry in the dataset
def get_neighborhoods(data):
    neighs = []

    for index, row in data.iterrows():
        if not pd.isna(row['Zipcode']):
            neighs.append(zip_to_neighborhood[int(row['Zipcode'])])
        else:
            neighs.append(np.nan)
    
    return neighs


# Get the offense descriptions (from law code) for each entry in the dataset
def get_offenses(data):
    offenses = []

    for index, row in data.iterrows():
        if pd.isnull(row["LAW_CODE"]):
            off = "Other"
        else:
            for lc in legal_code_to_offense:
                if lc in row["LAW_CODE"]:
                    off = legal_code_to_offense[lc]
            if not off:
                off = "Other"
        offenses.append(off)
    
    return offenses


# Get the zones (specified by mode) for each entry in the dataset
def get_zones(gdf, shapes_df, mode):
    actual_zone_values = []
    for index, row in gdf.iterrows():
        actual_zone_values.append(get_zone(shapes_df, mode, row))
    
    return actual_zone_values

# Load new dataset
data = pd.read_csv('arrest_data/' + new_data_file)

# Fill any missing latitude and longitude values
data["Latitude"] = data["Latitude"].fillna(0)
data["Longitude"] = data["Longitude"].fillna(0)

# Create geometric shapes for locating points geographically
geometry = [Point(xy) for xy in zip(data['Longitude'], data['Latitude'])]
gdf = GeoDataFrame(data, geometry=geometry)

# Load in geographic shapes for zones
# Source: https://github.com/BetaNYC/nyc-boundaries.git
df = gpd.read_file("shapefiles/all_bounds.geojson")

# Define zones to add to dataset
zones = {"Community District": "cd", "Police Precinct": "pp", "City Council District": "cc", "Congressional District": "nycongress", "Zipcode": "zipcode", "State Assembly District": "sa", "State Senate District": "ss"}
display = False

# Loop through data and add label for each new zone
for z in zones:
    print("Loading " + z + "...")
    shapes_df = df[df["id"] == zones[z]]

    if display:
        shapes_df.plot()
        plt.show()
    
    actual_zone_values = get_zones(gdf, shapes_df, zones[z])

    data[z.replace(" ", "_")] = actual_zone_values

# Get neighborhoods and offenses and add to dataset
data['Neighborhood'] = pd.Series(get_neighborhoods(data))
data['Offense'] = pd.Series(get_offenses(data))

# Select only relevant columns
columns_to_keep = ["ARREST_KEY", "ARREST_DATE", "PD_CD", "PD_DESC", "KY_CD", "OFNS_DESC", "LAW_CODE", "LAW_CAT_CD", "ARREST_BORO", "ARREST_PRECINCT", "JURISDICTION_CODE", "AGE_GROUP", "PERP_SEX", "PERP_RACE", "Latitude", "Longitude", "Community_District", "Police_Precinct", "City_Council_District", "Congressional_District", "State_Assembly_District", "State_Senate_District", "Zipcode", "Neighborhood"]
current_columns = list(data.columns)
data = data.drop(columns=[c for c in current_columns if c not in columns_to_keep])

# Create specific time variables
data["ARREST_QUARTER"] = pd.Series([(int(d.split("/")[0])-1)//3 for d in data["ARREST_DATE"].tolist()])
data["ARREST_YEAR"] = pd.Series([int(d.split("/")[2]) for d in data["ARREST_DATE"].tolist()])

# Load old datafile and remove all data from current year
    # The new file will always contain all data from the current year, with new quarters added periodically - thus we remove all existing data for the year
old_data = pd.read_csv('arrest_data/' + current_data_file)
old_data = old_data[old_data['ARREST_YEAR'] != current_year]

# Combine newly processed data with existing dataset
complete_data = pd.concat([data, old_data])

# Save new file with all data
complete_data.to_csv("arrest_data/arrest_data.csv", index=False)