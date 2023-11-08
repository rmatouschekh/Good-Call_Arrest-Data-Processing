import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

"""
Creates files for each zone type with arrest information by quarter and year; used for later data production scripts
"""

# Plot arrests over time (quarter or year)
def plot_by_time(data, key, title):
    plt.figure(figsize=(13,7.5))
    plt.plot([str(d) for d in data[key].tolist()], data["COUNT"].tolist(), marker='o', color='#6cb9a7', markersize=10, linewidth=3)
    plt.xticks(rotation=90)
    plt.ylim((0, max(data["COUNT"].tolist()) + 50000))
    plt.xlabel(title, labelpad=12, weight="bold", fontsize=16)
    plt.ylabel("# Arrests", labelpad=12, weight="bold", fontsize=16)
    plt.title("# Arrests by " + title, pad=15, weight="bold", fontsize=20)
    plt.savefig("figures/arrests_by_" + title.lower() + ".png", bbox_inches = 'tight', dpi=300)
    plt.close()

# UPDATE THESE
new_year = 2023
new_quarter = 1

# Define zones to produce data files for
zones = ["Community_District", "Police_Precinct", "City_Council_District", "Congressional_District", "Zipcode", "State_Assembly_District", "State_Senate_District", "Neighborhood"]

data = pd.read_csv('arrest_data/arrest_data.csv', low_memory=False)

# Find arrests by year
data_by_year = data.groupby(["ARREST_YEAR"])["ARREST_KEY"].size().reset_index(name = "COUNT")
# Remove data for incomplete year
data_by_year = data_by_year[data_by_year["ARREST_YEAR"] != new_year]

# Plot time by year
plot_by_time(data_by_year, "ARREST_YEAR", 'Year')

# Fine arrests by quarter
data_by_quarter = data.groupby(["ARREST_YEAR", "ARREST_QUARTER"])["ARREST_KEY"].size().reset_index(name = "COUNT")
# Create key to use for plotting arrests by quarter
data_by_quarter["TIME_KEY"] = pd.Series([str(row["ARREST_YEAR"]) + " – " + str(row["ARREST_QUARTER"]) for index, row in data_by_quarter.iterrows()])

# Plot arrests by year
plot_by_time(data_by_quarter, "TIME_KEY", 'Quarter')

# Loop through each zone type
for z in zones:
    print("Producing quarterly data for " + z + "...")
    # Count arrests in each zone in each quarter
    z_df = data[data[z].notna()]
    z_df = z_df.groupby([z, "ARREST_YEAR", "ARREST_QUARTER"])["ARREST_KEY"].size().reset_index(name = "#_ARRESTS")
    
    years = z_df["ARREST_YEAR"].unique().tolist()
    years.sort()
    quarters = z_df["ARREST_QUARTER"].unique().tolist()
    quarters.sort()

    # Remove all data for certain districts; no corresponding census data available for these areas
    if z == "Neighborhood":
        for n in ['Central Park', 'Laguardia Airport', 'JFK Airport']:
            for y in years:
                for q in quarters:
                    z_df.loc[(z_df["Neighborhood"] == n) & (z_df["ARREST_YEAR"] == y) & (z_df["ARREST_QUARTER"] == q), "#_ARRESTS"] = 0
    
    # Loop through each zone (ie each zipcode)
    # Add in missing data values – specfically adds in zeros for any combination of year and quarter expected but missing from dataset
    for zone in z_df[z].unique().tolist():
        zone_df = z_df[z_df[z] == zone]
    
        for y in years:
            if not y in zone_df["ARREST_YEAR"].unique().tolist():
                # Adds mising years
                rows = []
                for q in quarters:
                    if (not y == new_year) or (y == new_year and q <= new_quarter):
                        new_row = {z: zone, "ARREST_YEAR": y, "ARREST_QUARTER": q, "#_ARRESTS": 0}
                        rows.append(new_row)
                rows = pd.DataFrame(rows)
                z_df = pd.concat([z_df, rows], axis=0, ignore_index=True)
            else:
                # Adds missing quarters
                zone_year_df = zone_df[zone_df["ARREST_YEAR"] == y]
                for q in quarters:
                    if not q in zone_year_df["ARREST_QUARTER"].unique().tolist():
                        if (not y == new_year) or (y == new_year and q <= new_quarter):
                            new_row = {z: zone, "ARREST_YEAR": y, "ARREST_QUARTER": q, "#_ARRESTS": 0}
                            new_row = pd.DataFrame([new_row])
                            z_df = pd.concat([z_df, new_row], axis=0, ignore_index=True)

    
    # Find the percent change in arrests between each quarter
    changes = []
    
    for index, row in z_df.iterrows():
        current = row["#_ARRESTS"]

        # Zero out values for first quarter in dataset
        if row["ARREST_YEAR"] == 2006 and row["ARREST_QUARTER"] == 0:
            change = None
        else:
            # Find last quarter's data
            old_year = row["ARREST_YEAR"]
            old_quarter = row["ARREST_QUARTER"]

            if old_quarter == 0:
                old_year = old_year - 1
                old_quarter = 3
            else:
                old_quarter = old_quarter - 1
            
            old = z_df.loc[(z_df[z] == row[z]) & (z_df["ARREST_YEAR"] == old_year) & (z_df["ARREST_QUARTER"] == old_quarter)]["#_ARRESTS"].tolist()[0]

            # Calculate percent change in arrests
            if old == 0:
                if current == 0:
                    change = 0
                else:
                    change = 100
            else:
                change = ((current-old)/old)*100
        
        changes.append(change)
    
    # Save data by quarter
    z_df["ARREST_CHANGE"] = pd.Series(changes)
    z_df.sort_values(by=[z, "ARREST_YEAR", "ARREST_QUARTER"])
    z_df.to_csv("arrest_data/increase_by_zone/" + z.lower() + "_increase_by_quarter.csv", index=False)

    print("Producing yearly data for " + z + "...")
    # Count arrests in each zone in each year
    z_df = data[data[z].notna()]
    z_df = z_df.groupby([z, "ARREST_YEAR"])["ARREST_KEY"].size().reset_index(name = "#_ARRESTS")

    years = z_df["ARREST_YEAR"].unique().tolist()
    years.sort()

    # Remove all data for certain districts; no corresponding census data available for these areas
    if z == "Neighborhood":
        for n in ['Central Park', 'Laguardia Airport', 'JFK Airport']:
            for y in years:
                z_df.loc[(z_df["Neighborhood"] == n) & (z_df["ARREST_YEAR"] == y), "#_ARRESTS"] = 0
    
    # Loop through each zone (ie each zipcode)
    # Add in missing data values – specfically adds in zeros for any combination of year expected but missing from dataset
    for zone in z_df[z].unique().tolist():
        zone_df = z_df[z_df[z] == zone]
    
        for y in years:
            if not y in zone_df["ARREST_YEAR"].unique().tolist():
                new_row = {z: zone, "ARREST_YEAR": y, "#_ARRESTS": 0}
                new_row = pd.DataFrame([new_row])
                z_df = pd.concat([z_df, new_row], axis=0, ignore_index=True)
        
    # Find the percent change in arrests between each year
    changes = []
    
    for index, row in z_df.iterrows():
        current = row["#_ARRESTS"]

        # Zero out values for first year in dataset
        if row["ARREST_YEAR"] == 2006:
            change = None
        else:
            # Find last year's data
            old = z_df.loc[(z_df[z] == row[z]) & (z_df["ARREST_YEAR"] == row["ARREST_YEAR"]-1)]["#_ARRESTS"].tolist()[0]

            # Calculate percent change in arrests
            if old == 0:
                if current == 0:
                    change = 0
                else:
                    change = 100
            else:
                change = ((current-old)/old)*100
        
        changes.append(change)
    
    # Save data by year
    z_df["ARREST_CHANGE"] = pd.Series(changes)
    z_df.sort_values(by=[z, "ARREST_YEAR"])
    z_df.to_csv("arrest_data/increase_by_zone/" + z.lower() + "_increase_by_year.csv", index=False)
