import scipy.stats
import pandas as pd
import matplotlib.pyplot as plt

"""
Rough data production file: Creates figures describing general arrest trends
"""

# UPDATE THESE WHEN NEW DATA IS AVAILABLE
new_year = 2023
new_quarter = 1
new_census_year = 2021

# Read in datasets
data = pd.read_csv('arrest_data/arrest_data.csv', low_memory=False)
census_data = pd.read_csv('census_data/census_data_neighborhood.csv', low_memory=False)

# Calculate newest year for which complete data is available
new_full_year = new_year

if new_quarter < 3:
    new_full_year = new_year-1

# Create specific datasets
data_by_year = data.groupby(["ARREST_YEAR"])["ARREST_KEY"].size().reset_index(name = "COUNT") # Number of arrests by year
data_newest = data_by_year[data_by_year["ARREST_YEAR"] == new_full_year] # Arrest data for newest full year
data_comp = data_by_year[data_by_year["ARREST_YEAR"] == new_full_year-1] # Arrest data for second-newest full year
year_change = ((data_newest.iloc[0]["COUNT"] - data_comp.iloc[0]["COUNT"])/data_comp.iloc[0]["COUNT"])*100 # Get change in arrests between two most recent full years

# Calculate and prints increase in arrests between two most recent years
print("% Change in Arrests from " + str(new_full_year-1) + " to " + str(new_full_year) + ":", round(year_change, 2))
print("\tThere were " + str(data_newest.iloc[0]["COUNT"] - data_comp.iloc[0]["COUNT"]) + " more arrests in " + str(new_full_year) + " than in " + str(new_full_year-1))
print()

# Calculate the estimated % of NYC population that identified as non-white in 2021
census_newest = census_data[census_data["Year"] == 2021]
total_population = census_newest["Population"].tolist()
total_population = sum([p for p in total_population if not pd.isna(p)])
white_population = census_newest["Race: White"].tolist()
white_population = sum([p for p in white_population if not pd.isna(p)])
print("% of NYC Population Estimated Non-White in 2021: " + str(round(((total_population-white_population)/total_population)*100, 2)))

# Calculate the % of arrests that were of non-white individuals in the newest full year of data
data_newest = data[data["ARREST_YEAR"] == new_full_year]
data_newest_by_race = data.groupby(["PERP_RACE"])["ARREST_KEY"].size().reset_index(name = "COUNT")
white_count = data_newest_by_race[data_newest_by_race["PERP_RACE"] == "WHITE"].iloc[0]["COUNT"] + data_newest_by_race[data_newest_by_race["PERP_RACE"] == "WHITE HISPANIC"].iloc[0]["COUNT"]
total_count = sum(data_newest_by_race["COUNT"].tolist())
print("% of NYC Arrests Non-White in " + str(new_full_year) + ": " + str(round(((total_count-white_count)/total_count)*100, 2)))
print()

# Calculate the estimated % of NYC population that identified as Black in 2021
black_population = census_newest["Race: Black or African American"].tolist()
black_population = sum([p for p in black_population if not pd.isna(p)])
print("% of NYC Population Estimated Black in 2021: " + str(round((black_population/total_population)*100, 2)))

# Calculate the % of arrests that were of Black individuals in the newest full year of data
black_count = data_newest_by_race[data_newest_by_race["PERP_RACE"] == "BLACK"].iloc[0]["COUNT"] + data_newest_by_race[data_newest_by_race["PERP_RACE"] == "BLACK HISPANIC"].iloc[0]["COUNT"]
print("% of NYC Arrests Black in " + str(new_full_year) + ": " + str(round((black_count/total_count)*100, 2)))
print()

# Plot the estimated % of the NYC population that identified as Black or Other in 2021 as a pie chart
population_by_race = [black_population, total_population-black_population]
ex = [0.05, 0]
plt.pie(population_by_race, explode=ex, colors = ['#6cb9a7', 'black'], labels=["BLACK", "OTHER"], autopct='%1.1f%%', textprops = {'weight':'bold'}, startangle = 90)
plt.title("POPULATION")
plt.savefig('figures/population.png', bbox_inches = 'tight', dpi=300)
plt.close()

# Plot the % of arrests that were of Black or Other individuals in the newest full year as a pie chart
counts_by_race = [black_count, total_count-black_count]
plt.pie(counts_by_race, explode=ex, colors = ['#6cb9a7', 'black'], labels=["BLACK", "OTHER"], autopct='%1.1f%%', textprops = {'weight':'bold'}, startangle = 90)
plt.title("ARRESTS")
plt.savefig('figures/counts.png', bbox_inches = 'tight', dpi=300)
plt.close()

# Calculate and print estimated % of NYC population that identified as hispanic in 2021
hispanic_population = census_newest["Ethnicity: Hispanic or Latino"].tolist()
hispanic_population = sum([p for p in hispanic_population if not pd.isna(p)])
print("% of NYC Population Estimated Hispanic in 2021: " + str(round((hispanic_population/total_population)*100, 2)))

# Calculate and print % of arrests that were of hispanic individuals in newest full year
hispanic_count = data_newest_by_race[data_newest_by_race["PERP_RACE"] == "WHITE HISPANIC"].iloc[0]["COUNT"] + data_newest_by_race[data_newest_by_race["PERP_RACE"] == "BLACK HISPANIC"].iloc[0]["COUNT"]
print("% of NYC Arrests Hispanic in " + str(new_full_year) + ": " + str(round((hispanic_count/total_count)*100, 2)))
print()


# NO NEIGHBORHOOD CORRELATIONS DEMONSTRATED SIGNIFICANCE

# Produce data by neighborhood
neighborhood_data_dict = {}

# Create census data by population
for index, row in census_newest.iterrows():
    if row["Population"]:
        neighborhood_data_dict[row["Neighborhood"]] = {"Population": row["Population"], "Economy: Percent below poverty level": row["Economy: Percent below poverty level"], "Race: Prop. Non-White": (row["Population"]-row["Race: White"])/row["Population"], "Race: Prop. Black": row["Race: Black or African American"]/row["Population"], "Ethnicity: Prop. Hispanic": row["Ethnicity: Hispanic or Latino"]/row["Population"], "Immigration: Prop. Foreign Born": row["Immigration: Foreign-born"]/row["Population"], "Language: Prop. Non-English": row["Language: Not English"]/row["Population"]}

# Find newest arrest data for neighborhoods by year
newest_arrest = pd.read_csv("arrest_data/increase_by_zone/neighborhood_increase_by_year.csv")
newest_arrest = newest_arrest[newest_arrest["ARREST_YEAR"] == new_full_year]

# Calculate arrests by population and % change in arrests for each neighborhood
for index, row in newest_arrest.iterrows():
    if row["Neighborhood"] in neighborhood_data_dict:
        neighborhood_data_dict[row["Neighborhood"]]["Arrests by Pop."] = row["#_ARRESTS"]/neighborhood_data_dict[row["Neighborhood"]]["Population"]
        neighborhood_data_dict[row["Neighborhood"]]["% Change Arrests"] = row["ARREST_CHANGE"]


# Create lists of values to look at correlation of by neighborhood
poverty_level = [neighborhood_data_dict[n]["Economy: Percent below poverty level"] for n in neighborhood_data_dict if "Airport" not in n]
non_white_prop = [neighborhood_data_dict[n]["Race: Prop. Non-White"] for n in neighborhood_data_dict if "Airport" not in n]
black_prop = [neighborhood_data_dict[n]["Race: Prop. Black"] for n in neighborhood_data_dict if "Airport" not in n]
hispanic_prop = [neighborhood_data_dict[n]["Ethnicity: Prop. Hispanic"] for n in neighborhood_data_dict if "Airport" not in n]
foreign_prop = [neighborhood_data_dict[n]["Immigration: Prop. Foreign Born"] for n in neighborhood_data_dict if "Airport" not in n]
non_english_prop = [neighborhood_data_dict[n]["Language: Prop. Non-English"] for n in neighborhood_data_dict if "Airport" not in n]

# Create lists of values to compare census data against by neighborhood
arrest_prop = [neighborhood_data_dict[n]["Arrests by Pop."] for n in neighborhood_data_dict  if "Airport" not in n]
change_arrests = [neighborhood_data_dict[n]["% Change Arrests"] for n in neighborhood_data_dict  if "Airport" not in n]

# Print and plot the correlation between proportion of population below the property level and arrests by population
print("Prop. Poverty Level vs. Arrest Prop.", scipy.stats.pearsonr(poverty_level, arrest_prop))
plt.scatter(poverty_level, arrest_prop, color = 'maroon')
plt.title("Prop. Poverty Level vs. Arrest Prop.")
plt.show()
plt.close()
# Print and plot the correlation between proportion of population below the property level and % change in arrests
print("Prop. Poverty Level vs. Arrest Change", scipy.stats.pearsonr(poverty_level, change_arrests))
plt.scatter(poverty_level, change_arrests, color = 'maroon')
plt.title("Prop. Poverty Level vs. Arrest Change.")
plt.show()
plt.close()
print()

# Print and plot the correlation between proportion of population that identifies as non-white and arrests by population
print("Prop. Non-White vs. Arrest Prop.", scipy.stats.pearsonr(non_white_prop, arrest_prop))
plt.scatter(non_white_prop, arrest_prop, color = 'maroon')
plt.title("Prop. Non-White vs. Arrest Prop.")
plt.show()
plt.close()
# Print and plot the correlation between proportion of population that identifies as non-white and % change in arrests
print("Prop. Non-White vs. Arrest Change", scipy.stats.pearsonr(non_white_prop, change_arrests))
plt.scatter(non_white_prop, change_arrests, color = 'maroon')
plt.title("Prop. Non-White Level vs. Arrest Change.")
plt.show()
plt.close()
print()

# Print and plot the correlation between proportion of population that identifies as Black and arrests by population
print("Prop. Black vs. Arrest Prop.", scipy.stats.pearsonr(black_prop, arrest_prop))
plt.scatter(black_prop, arrest_prop, color = 'maroon')
plt.title("Prop. Black vs. Arrest Prop.")
plt.show()
plt.close()
# Print and plot the correlation between proportion of population that identifies as Black and % change in arrests
print("Prop. Black vs. Arrest Change", scipy.stats.pearsonr(black_prop, change_arrests))
plt.scatter(black_prop, change_arrests, color = 'maroon')
plt.title("Prop. Black Level vs. Arrest Change.")
plt.show()
plt.close()
print()

# Print and plot the correlation between proportion of population that identifies as hispanic and arrests by population
print("Prop. Hispanic vs. Arrest Prop.", scipy.stats.pearsonr(hispanic_prop, arrest_prop))
plt.scatter(hispanic_prop, arrest_prop, color = 'maroon')
plt.title("Prop. Hispanic vs. Arrest Prop.")
plt.show()
plt.close()
# Print and plot the correlation between proportion of population that identifies as hispanic and % change in arrests
print("Prop. Hispanic vs. Arrest Change", scipy.stats.pearsonr(hispanic_prop, change_arrests))
plt.scatter(hispanic_prop, change_arrests, color = 'maroon')
plt.title("Prop. Hispanic vs. Arrest Change.")
plt.show()
plt.close()
print()

# Print and plot the correlation between proportion of population that is foreign and arrests by population
print("Prop. Foreign vs. Arrest Prop.", scipy.stats.pearsonr(foreign_prop, arrest_prop))
plt.scatter(foreign_prop, arrest_prop, color = 'maroon')
plt.title("Prop. Foreign vs. Arrest Prop.")
plt.show()
plt.close()
# Print and plot the correlation between proportion of population that is foreign and % change in arrests
print("Prop. Foreign vs. Arrest Change", scipy.stats.pearsonr(foreign_prop, change_arrests))
plt.scatter(foreign_prop, change_arrests, color = 'maroon')
plt.title("Prop. Foreign vs. Arrest Change.")
plt.show()
plt.close()
print()

# Print and plot the correlation between proportion of population that does not speak English as their primary language and arrests by population
print("Prop. Non-English Speaking vs. Arrest Prop.", scipy.stats.pearsonr(non_english_prop, arrest_prop))
plt.scatter(non_english_prop, arrest_prop, color = 'maroon')
plt.title("Prop. Non-English Speaking vs. Arrest Prop.")
plt.show()
plt.close()
# Print and plot the correlation between proportion of population that does not speak English as their primary language and % change in arrests
print("Prop. Non-English Speaking vs. Arrest Change", scipy.stats.pearsonr(non_english_prop, change_arrests))
plt.scatter(non_english_prop, change_arrests, color = 'maroon')
plt.title("Prop. Non-English Speaking vs. Arrest Change.")
plt.show()
plt.close()
print()