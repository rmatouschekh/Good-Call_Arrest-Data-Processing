import os
import pandas as pd
from PIL import Image
import geopandas as gpd
import matplotlib.pyplot as plt

"""
Create figures and gifs displaying interesting data
"""

# Delete images in given folder – used to clean images created for gifs
def delete_images(img_folder):
    for img in img_folder:
        os.remove(img)

# Create gif from list of images
def make_gif(frame_list, path):
    frames = [Image.open(image) for image in frame_list]
    frame_one = frames[0]
    frame_one.save(path, format="GIF", append_images=frames,
               save_all=True, duration=1000, loop=0)

# Create figure and save given: population or area, specific or general
def create_map(mode, merged, vmin, vmax, output_path, t, frame_mode):
    # Create values based on mode
    if 'pop' in mode:
        column = "ARRESTS_BY_POP"
        cmap = 'Reds'
        title = "Arrests by Population"
        suffix = '_by_pop'
    elif 'increase' in mode:
        column = "ARREST_CHANGE"
        cmap = 'coolwarm'
        title = "% Change in Arrests"
        suffix = '_increase'
    
    if 'specific' in mode:
        suffix = suffix + '_SPECIFIC_' + frame_mode.upper()
    
    # Create map given specifications
    fig = merged.plot(column = column, cmap=cmap, figsize=(10,10), legend=True, vmin=vmin, vmax=vmax, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    fig.axis('off')
    fig.set_title(title, fontdict={'fontsize': '25', 'fontweight' : '3'})
    time_label = str(t)
    fig.annotate(time_label,
            xy=(0.1, .075), xycoords='figure fraction',
            horizontalalignment='left', verticalalignment='bottom',
            fontsize=20)
    
    # Save figure
    filepath = os.path.join(output_path, str(t) + suffix + '.jpg')
    chart = fig.get_figure()
    chart.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()

    # Return path to new image
    return filepath

# UPDATE THIS TO CHANGE FIGURES CREATED (year or quarter)
mode = "quarter"

# Define zone types
zones = {"Community District": "cd", "Police Precinct": "pp", "City Council District": "cc", "Congressional District": "nycongress", "Zipcode": "zipcode" , "State Assembly District": "sa", "State Senate District": "ss", "Neighborhood": None}
# Define zone types for which the census provides population info
pop_zones = ["Zipcode", "Neighborhood"]

# Loop through zone types
for z in zones:
    print(z)

    # Create gifs and figures for change in arrest data over time

    # Define path to save figures and gifs to
    output_path = 'gifs/' + z.lower().replace(" ", "_")

    # Filter data based on mode
    if mode == "year":
        data = pd.read_csv('arrest_data/increase_by_zone/' + z.lower().replace(" ", "_") + '_increase_by_year.csv')
        data = data[data["ARREST_YEAR"] != 2023]

        data_change = data.dropna(subset=["ARREST_CHANGE"])

        time_zones = data_change["ARREST_YEAR"].unique().tolist()
        time_zones.sort()
    else:
        data = pd.read_csv('arrest_data/increase_by_zone/' + z.lower().replace(" ", "_") + '_increase_by_quarter.csv')

        data_change = data.dropna(subset=["ARREST_CHANGE"])

        time_zones = [str(int(row["ARREST_YEAR"])) + "-" + str(int(row["ARREST_QUARTER"])) for index, row in data_change.iterrows()]
        time_zones = list(set(time_zones))
        time_zones.sort()

    # Load in polygons for zone type
    if zones[z]:
        map_df = gpd.read_file('shapefiles/all_bounds.geojson')
        map_df = map_df[map_df["id"] == zones[z]]
        map_df["nameCol"] = map_df["nameCol"].astype(float)
    else:
        map_df = gpd.read_file('shapefiles/neighborhoods.geojson')

    # Find the min and max values for color scale in gif / image
    boundary_value = max(abs(data_change["ARREST_CHANGE"].min()), abs(data_change["ARREST_CHANGE"].max()))
    if boundary_value > 100:
        boundary_value = 100
    vmin, vmax = -boundary_value, boundary_value

    # Create frame for each time unit (quarter or year)
    frames = []
    for t in time_zones:
        # Filter data based on mode (quarter or year)
        if mode == "year":
            subset_data = data_change[data_change["ARREST_YEAR"] == t]
        else:
            subset_data = data_change.loc[(data_change["ARREST_YEAR"] == int(t.split("-")[0])) & (data_change["ARREST_QUARTER"] == int(t.split("-")[1]))]
        
        # Merge data with polygon dataset
        merged = subset_data.set_index(z.replace(" ", "_")).join(map_df.set_index("nameCol"))
        merged = gpd.GeoDataFrame(merged)

        # Create specific images with specific color scale for latest year or quarter
            # UPDATE t VALUES BASED ON LATEST FULL YEAR OR QUARTER
        if (mode == "year" and t == 2022) or (mode != "year" and t == "2023-1"):
            spec_boundary_value = max(abs(subset_data["ARREST_CHANGE"].min()), abs(subset_data["ARREST_CHANGE"].max()))
            create_map('increase_specific', merged, -spec_boundary_value, spec_boundary_value, output_path, t, mode)
        
        # Append gif frame to list
        frames.append(create_map('increase', merged, vmin, vmax, output_path, t, mode))
    
    # Create gif out of frames for each time unit
    make_gif(frames, output_path + "/" + z.lower().replace(" ", "_") + "_increase_" + mode.upper() + ".gif")
    # Delete individual images
    delete_images(frames)

    # Create gifs and images for population data if it exists
    if z in pop_zones:
        # Load and filter population data
        pop_data = pd.read_csv('census_data/census_data_' + z.lower() + '.csv')
        data_pop = data[data["ARREST_YEAR"] > 2010] # Census only has data after 2010
        data_pop = data_pop.reset_index()

        # Filter data by mode (quarter or year)
        if mode == "year":
            time_zones = data_pop["ARREST_YEAR"].unique().tolist()
            time_zones.sort()
        else:
            time_zones = [str(int(row["ARREST_YEAR"])) + "-" + str(int(row["ARREST_QUARTER"])) for index, row in data_pop.iterrows()]
            time_zones = list(set(time_zones))
            time_zones.sort()

        # Create arrests by population data for each year or quarter
        arrests_by_pop = []
        for index, row in data_pop.iterrows():
            c = row[z.replace(" ", "_")]
            year = row["ARREST_YEAR"]

            # Floor all values after 2021 (year of latest census data)
                # UPDATE YEAR WHEN NEW CENSUS DATA RELEASED
            if year > 2021:
                year = 2021.0
            
            # Find the population for year and zone
            subset_pop = pop_data.loc[(pop_data[z.replace(" ", "_")] == c) & (pop_data["Year"] == year)]

            if len(subset_pop.index) > 0:
                # Say arrests by population is zero if population value is 0 or NaN
                    # Zeroes out data for zones with missing population values
                if subset_pop["Population"].iloc[0] == 0 or not subset_pop["Population"].iloc[0]:
                    arrests_by_pop.append(0)
                else:
                    arrests_by_pop.append((row["#_ARRESTS"]/subset_pop["Population"].iloc[0])*100)
            else:
                # Zeroes out data for zones not in census data
                arrests_by_pop.append(0)
        
        # Add arrests by population to dataset
        data_pop["ARRESTS_BY_POP"] = pd.Series(arrests_by_pop)
        
        # Find the max value for color scale in gif / image
        vmin, vmax = 0, data_pop["ARRESTS_BY_POP"].max()

        # Create frame for each time unit (quarter or year)
        frames = []
        for t in time_zones:
            # Filter data based on mode (quarter or year)
            if mode == "year":
                subset_data = data_pop[data_pop["ARREST_YEAR"] == t]
            else:
                subset_data = data_pop.loc[(data_pop["ARREST_YEAR"] == int(t.split("-")[0])) & (data_pop["ARREST_QUARTER"] == int(t.split("-")[1]))]

            # Merge data with polygon dataset
            merged = subset_data.set_index(z.replace(" ", "_")).join(map_df.set_index("nameCol"))
            merged = gpd.GeoDataFrame(merged)

            # Create specific images with specific color scale for latest year or quarter
                # UPDATE t VALUES BASED ON LATEST FULL YEAR OR QUARTER
            if (mode == "year" and t == 2022) or (mode != "year" and t == "2023-1"):
                create_map('pop_specific', merged, 0, subset_data["ARRESTS_BY_POP"].max(), output_path, t, mode)
            
            # Append gif frame to list
            frames.append(create_map('pop', merged, vmin, vmax, output_path, t, mode))
        
        # Create gif out of frames for each time unit
        make_gif(frames, output_path + "/" + z.lower().replace(" ", "_") + "_by_pop_" + mode.upper() + ".gif")
        # Delete individual figures
        delete_images(frames)