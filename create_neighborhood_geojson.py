import pandas as pd
import geopandas as gpd
from shapely.ops import unary_union
from data_storage import zip_to_neighborhood, neighborhood_to_zip

"""
Create geojson file for neighborhoods
"""

# Find list of neighborhoods
neighborhoods = list(set(zip_to_neighborhood.values()))

# Read in zipcode objects
map_df = gpd.read_file('shapefiles/all_bounds.geojson')
map_df = map_df[map_df["id"] == "zipcode"]

# Find all zipcodes in map
zips_in_map = map_df["nameCol"].unique().tolist()
str_dict_zips = [str(z) for z in list(zip_to_neighborhood.keys())]

# Create list of neighborhood polygons
neighborhood_lst = []
for n in neighborhoods:
    # Create list of zipcodes to join to form neighborhood
    zip_polys = []
    
    for zip in neighborhood_to_zip[n]:
        # Convert unusual zipcode to necessary format
        if len(str(zip)) < 3:
            zip = "00083"
        # Add zipcode to list
        zip_polys.append(map_df[map_df["nameCol"] == str(zip)].iloc[0]["geometry"])

    # Merge zipcodes to neighborhood shape
    merged_polys = unary_union(zip_polys)
    
    # Add new neighborhood polygon to list
    neighborhood_lst.append([n, merged_polys])

# Create GeoDataFrame with neighborhood polygons
neighborhood_df = pd.DataFrame(neighborhood_lst, columns=["nameCol", "geometry"])
neighborhood_df = gpd.GeoDataFrame(neighborhood_df)

# Save neighborhood polygon file
neighborhood_df.to_file('shapefiles/neighborhoods.geojson', driver="GeoJSON")