import os
import math
import scipy.stats
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

"""
Explore arrest data by neighborhood
"""

# UPDATE THESE VARIABLES TO PRODUCE DIFFERENT DATA OUTPUT
neighborhood = 'Northeast Bronx'
era = 'quarter'

# UPDATE THESE VARIABLES AS NEW DATA BECOMES AVAILABLE
new_year = 2023
new_quarter = 1
census_new_year = 2021

# Read in relevant datasets
data = pd.read_csv('arrest_data/increase_by_zone/neighborhood_increase_by_' + era + '.csv')
unfiltered_data = pd.read_csv('arrest_data/arrest_data.csv')
census_data = pd.read_csv('census_data/census_data_neighborhood.csv')

# Create text file to write data output to
f = open("neighborhood_info/" + neighborhood.replace(" ", "") + "/neighborhood_info.txt", "w")

# Filter arrest data by mode (quarter or year)
if era == "quarter":
    year = new_year
    year_data = data.loc[(data["ARREST_YEAR"] == new_year) & (data["ARREST_QUARTER"] == new_quarter)].reset_index()
    year_unfiltered_data = unfiltered_data.loc[(unfiltered_data["ARREST_YEAR"] == new_year) & (unfiltered_data["ARREST_QUARTER"] == new_quarter)].reset_index()
elif era == "year":
    if new_quarter == 3:
        year = new_year
    else:
        year = new_year-1
    year_data = data[data["ARREST_YEAR"] == year].reset_index()
    year_unfiltered_data = unfiltered_data[unfiltered_data["ARREST_YEAR"] == year].reset_index()

# Filter census data by year
year_census_data = census_data[census_data["Year"] == census_new_year].reset_index()

# Get arrests by population
arrests_by_pop = []

for index, row in year_data.iterrows():
    neigh = row["Neighborhood"]
    neigh_population = year_census_data[year_census_data["Neighborhood"] == neigh].iloc[0]["Population"]
    if neigh_population == 0:
        by_pop = 0
    else:
        by_pop = round((row["#_ARRESTS"]/neigh_population)*100, 2)
    arrests_by_pop.append(by_pop)

year_data["ARRESTS_BY_POP"] = pd.Series(arrests_by_pop)


# Filter by neighborhood
neighborhood_data = year_data[year_data["Neighborhood"] == neighborhood].reset_index() # Filter arrest data to neighborhood for most recent year / quarter
neighborhood_census_data = year_census_data[year_census_data["Neighborhood"] == neighborhood].reset_index() # Filter census data to neighborhood for most recent year / quarter
neighborhood_unfiltered_data = year_unfiltered_data[year_unfiltered_data["Neighborhood"] == neighborhood].reset_index() # Filter unfiltered arrest data to neighborhood for most recent year / quarter
all_neighborhood_unfiltered_data = unfiltered_data[unfiltered_data["Neighborhood"] == neighborhood].reset_index() # Filter unfiltered arrest data to neighborhood



# Produce basic info
print("Information on " + neighborhood + " in " + str(year), end="")
f.write("Information on " + neighborhood + " in " + str(year))
if era == "quarter":
    print(", Quarter " + str(new_quarter + 1))
    f.write(", Quarter " + str(new_quarter + 1) + "\n\n")
else:
    print()
    f.write("\n\n")

# Print / write # of arrests in year / quarter
print("\t# Arrests:", neighborhood_data.iloc[0]["#_ARRESTS"])
f.write("\t# Arrests: " + str(neighborhood_data.iloc[0]["#_ARRESTS"]) + "\n")

# Print / write rank of neighborhood by # of arrests in year / quarter
sort_by_arrests = year_data.sort_values('#_ARRESTS', ascending=False)["Neighborhood"].tolist()
print("\tRank by # Arrests:", (sort_by_arrests.index(neighborhood)+1), "/", len(sort_by_arrests))
print()
f.write("\tRank by # Arrests: " + str((sort_by_arrests.index(neighborhood)+1)) + "/" +  str(len(sort_by_arrests)) + "\n\n")

# Print / write % change in arrests for neighborhood in year / quarter
print("\t% Change in Arrests:", round(neighborhood_data.iloc[0]["ARREST_CHANGE"], 2))
f.write("\t% Change in Arrests: " + str(round(neighborhood_data.iloc[0]["ARREST_CHANGE"], 2)) + "\n")

# Print / write rank of neighborhood by % change in arrests in year / quarter
sort_by_change = year_data.sort_values('ARREST_CHANGE', ascending=False)["Neighborhood"].tolist()
print("\tRank by % Change in Arrests:", (sort_by_change.index(neighborhood)+1), "/", len(sort_by_change))
print()
f.write("\tRank by % Change in Arrests: " + str((sort_by_change.index(neighborhood)+1)) + "/" + str(len(sort_by_change)) + "\n\n")

# Print / write arrests by population
print("\tArrests by Population:", neighborhood_data.iloc[0]["ARRESTS_BY_POP"])
f.write("\tArrests by Population: " + str(neighborhood_data.iloc[0]["ARRESTS_BY_POP"]) + "\n")

# Print / write rank of neighborhood by arrests by population in year / quarter
sort_by_population = year_data.sort_values('ARRESTS_BY_POP', ascending=False)["Neighborhood"].tolist()
print("\tRank by Arrests by Population:", (sort_by_population.index(neighborhood)+1), "/", len(sort_by_population))
print()
f.write("\tRank by Arrests by Population: " + str(sort_by_population.index(neighborhood)+1) + "/" + str(len(sort_by_population)) + "\n\n")

# Print / write 5 most common offenses in neighborhood in year / quarter
prominent_offenses = neighborhood_unfiltered_data["Offense"].value_counts().nlargest(n=5)
print("\tMost Common Offense Types:")
f.write("\tMost Common Offense Types:\n")
for o in prominent_offenses.index:
    print("\t\t" + o + ":", str(round((prominent_offenses[o]/len(neighborhood_unfiltered_data.index))*100, 2)) + "%")
    f.write("\t\t" + o + ": " + str(round((prominent_offenses[o]/len(neighborhood_unfiltered_data.index))*100, 2)) + "%\n")
print()
f.write("\n")

# Find arrests by ages for neighborhood in year / quarter
ages = ["<18", "18-24", "25-44", "45-64", "65+"]
age_values_dict = neighborhood_unfiltered_data["AGE_GROUP"].value_counts()
age_values = [(age_values_dict[a]/len(neighborhood_unfiltered_data.index))*100 for a in ages]

# Plot arrests by ages for neighborhood in year / quarter as bar chart
plt.figure(figsize = (10, 7.5))
plt.bar(ages, age_values, color='maroon')
plt.xlabel("Age Group")
plt.ylabel("% of Arrests")
plt.title("% of Arrests by Age")
plt.tight_layout()
plt.savefig('neighborhood_info/' + neighborhood.replace(" ", "") + '/arrests_by_age.png', bbox_inches='tight')
plt.close()


# Plot arrests by age over time
years = list(set(unfiltered_data["ARREST_YEAR"].tolist()))
years = sorted(years)
years = years[:years.index(year)]
colors = ['green', 'orange', 'blue', 'purple', 'yellow']

plt.figure(figsize = (10, 7.5))
old_age_values = [0] * len(years)
for a in ages:
    age_unfiltered = all_neighborhood_unfiltered_data[all_neighborhood_unfiltered_data["AGE_GROUP"] == a]
    age_values = [len(age_unfiltered[age_unfiltered["ARREST_YEAR"] == y].index) for y in years]
    plt.bar(years, age_values, color=colors[ages.index(a)], bottom = old_age_values, label = a)
    old_age_values = [old_age_values[i] + age_values[i] for i in range(len(old_age_values))]

plt.xlabel("Year")
plt.ylabel("# Arrests by Age Group")
plt.title("# Arrests by Age Group per Year")
plt.xticks(years, years)
plt.legend()
plt.tight_layout()
plt.savefig('neighborhood_info/' + neighborhood.replace(" ", "") + '/arrests_by_year_by_age.png', bbox_inches='tight')
plt.close()


# Plot arrests by race in year / quarter
races = ['WHITE', 'BLACK', 'ASIAN / PACIFIC ISLANDER', 'AMERICAN INDIAN / ALASKAN NATIVE', 'TWO+', 'UNKNOWN', 'OTHER']

# Create arrests by race data
race_values_dict = neighborhood_unfiltered_data["PERP_RACE"].value_counts()
race_values_arr = []
for r in races:
    if r in race_values_dict:
        if r in ["WHITE", "BLACK"] and r + " HISPANIC" in race_values_dict:
            race_values_arr.append(((race_values_dict[r] + race_values_dict[r + " HISPANIC"])/len(neighborhood_unfiltered_data.index))*100)
        else:
            race_values_arr.append((race_values_dict[r]/len(neighborhood_unfiltered_data.index))*100)
    else:
        race_values_arr.append(0)

# Plot arrests by race in year / quarter as bar chart
plt.figure(figsize = (10, 7.5))
plt.bar(races, race_values_arr, color='maroon')
plt.xticks(rotation='vertical')
plt.xlabel("Race")
plt.ylabel("% of Arrests")
plt.title("% of Arrests by Race")
plt.tight_layout()
plt.savefig('neighborhood_info/' + neighborhood.replace(" ", "") + '/arrests_by_race.png', bbox_inches='tight')
plt.close()


# Plot arrests by ethnicity in year / quarter
ethnicities = ["HISPANIC", "NOT HISPANIC", "OTHER/UNKNOWN"]

# Create arrests by ethnicity data
ethnicity_values = [0, 0, 0]
for r in races + ['WHITE HISPANIC', 'BLACK HISPANIC']:
    if r in ['OTHER', 'UNKNOWN'] and r in race_values_dict:
        ethnicity_values[2] += race_values_dict[r]
    elif r in races and r in race_values_dict:
        ethnicity_values[1] += race_values_dict[r]
    elif r in ['WHITE HISPANIC', 'BLACK HISPANIC'] and r in race_values_dict:
        ethnicity_values[0] += race_values_dict[r]

for i in range(len(ethnicity_values)):
    ethnicity_values[i] = (ethnicity_values[i]/len(neighborhood_unfiltered_data.index))*100

# Plot arrests by ethnicity in year / quarter as proportion of bar
fig, ax = plt.subplots(figsize= (10, 3))
his = ax.barh(["Ethnicity"], [ethnicity_values[0]], color="#6cb9a7", label = "Hispanic or Latino")
ax.bar_label(his, labels = ["HISPANIC\n" + str(round(ethnicity_values[0], 2)) + "%"], label_type='center', color='white', fontweight='bold', fontsize=14)
nots = ax.barh(["Ethnicity"], [ethnicity_values[1]], color="black", left=[ethnicity_values[0]], label = "Not")
ax.bar_label(nots, labels = ["NOT\n" + str(round(ethnicity_values[1], 2)) + "%"], label_type='center', color='white', fontweight='bold', fontsize=14)
other = ax.barh(["Ethnicity"], [ethnicity_values[2]], color="gray", left=[ethnicity_values[1] + ethnicity_values[0]], label = "Other/Unknown")
ax.set_title("% of Arrests")
plt.yticks([], [])
plt.tight_layout()
plt.axis('off')
plt.savefig('neighborhood_info/' + neighborhood.replace(" ", "") + '/arrests_by_ethnicity.png', bbox_inches='tight', dpi=300)
plt.close()


# Plot arrests by race over time
colors = ['green', 'orange', 'blue', 'purple', 'yellow', 'red', 'pink', 'gray']

plt.figure(figsize = (10, 7.5))
old_race_values = [0] * len(years)

for r in races:
    race_unfiltered = all_neighborhood_unfiltered_data[all_neighborhood_unfiltered_data["PERP_RACE"] == r]
    race_values = [len(race_unfiltered[race_unfiltered["ARREST_YEAR"] == y].index) for y in years]
    plt.bar(years, race_values, color=colors[races.index(r)], bottom = old_race_values, label = r)
    old_race_values = [old_race_values[i] + race_values[i] for i in range(len(old_race_values))]

plt.xlabel("Year")
plt.ylabel("# Arrests by Race")
plt.title("# Arrests by Race per Year")
plt.xticks(years, years)
plt.legend()
plt.tight_layout()
plt.savefig('neighborhood_info/' + neighborhood.replace(" ", "") + '/arrests_by_year_by_race.png', bbox_inches='tight')
plt.close()


# Produce census info
population = neighborhood_census_data.iloc[0]["Population"]

print("\tCensus Information")
f.write("\tCensus Information\n")
print("\t\tPopulation:", population)
print()
f.write("\t\tPopulation: " + str(population) + "\n\n")


# Print / write mean median worker earnings
print("\t\tMean Median Worker Earnings:", "$" + str(neighborhood_census_data.iloc[0]["Economy: Median worker earnings"]))
f.write("\t\tMean Median Worker Earnings: $" + str(neighborhood_census_data.iloc[0]["Economy: Median worker earnings"]) + "\n")

# Print / write mean median worker earnings for all neighborhoods
mean_median_earnings = year_census_data["Economy: Median worker earnings"].tolist()
mean_median_earnings = round(sum(mean_median_earnings)/len(mean_median_earnings), 2)
print("\t\t\t(The mean median worker earnings across all neighborhoods is $" + str(mean_median_earnings) + ")")
f.write("\t\t\t(The mean median worker earnings across all neighborhoods is $" + str(mean_median_earnings) + ")\n\n")

# Print / write mean % of population below the poverty level
print("\t\tMean % of Population Below Poverty Level:", neighborhood_census_data.iloc[0]["Economy: Percent below poverty level"])
f.write("\t\tMean % of Population Below Poverty Level: " + str(neighborhood_census_data.iloc[0]["Economy: Percent below poverty level"]) + "\n\n")

# Print / write mean unemployment rate
print("\t\tMean Unemployment Rate:", neighborhood_census_data.iloc[0]["Economy: Unemployment rate"])
print()
f.write("\t\tMean Unemployment Rate: " + str(neighborhood_census_data.iloc[0]["Economy: Unemployment rate"]) + "\n\n")

# Calculate percentage of population by race – adjust to arrest data
race_columns = ["White", "Black or African American", "Asian", "American Indian and Alaska Native", "Two or more", "Unknown", "Other"]
race_values_pop = []
for c in race_columns:
    if 'Asian' in c:
        race_values_pop.append((neighborhood_census_data.iloc[0]["Race: " + c]/population)*100 + (neighborhood_census_data.iloc[0]["Race: Native Hawaiian and Other Pacific Islander"]/population)*100)
    elif 'Unknown' in c:
        race_values_pop.append(0)
    else:
        race_values_pop.append((neighborhood_census_data.iloc[0]["Race: " + c]/population)*100)


N = len(races)
ind = np.arange(N)
width = 0.4
races[3] = "NATIVE AMERICAN"

# Plot % of population by race (black) and % of arrests by race (teal) as bars
fig, ax = plt.subplots(figsize= (10, 7.5))
rects = ax.bar(ind, race_values_arr, width, label = "% of Arrests", color = "#6cb9a7")
ax.bar_label(rects, labels = [str(round(race_values_arr[i], 1)) + "%" for i in range(len(race_values_arr))], padding=3)
rects = plt.bar(ind+width, race_values_pop, width, label = "% of Population", color = "black")
ax.bar_label(rects, labels = [str(round(race_values_pop[i], 1)) + "%" for i in range(len(race_values_arr))], padding=3)
plt.xticks(rotation='vertical')
plt.ylim(0, 80)
plt.xticks(ind + width / 2, races)
plt.legend(loc='best', fontsize=12)
plt.tight_layout()
plt.savefig('neighborhood_info/' + neighborhood.replace(" ", "") + '/population_by_race.png', bbox_inches='tight', dpi=300)
plt.close()

# Find % of population by ethnicity
ethnicity_values = [neighborhood_census_data.iloc[0]["Ethnicity: Hispanic or Latino"], neighborhood_census_data.iloc[0]["Ethnicity: Not Hispanic or Latino"]]
ethnicity_values = [(v / population)*100 for v in ethnicity_values]

# Print / write % of population that identifies as hispanic or latino
print("\t\t% of Population Hispanic or Latino:", str(round((neighborhood_census_data.iloc[0]["Ethnicity: Hispanic or Latino"]/population)*100, 2)) + "%")
f.write("\t\t% of Population Hispanic or Latino: " + str(round((neighborhood_census_data.iloc[0]["Ethnicity: Hispanic or Latino"]/population)*100, 2)) + "%\n")

# Print / write rank of neighborhood by % of population that identifies as hispanic or latino
year_census_data["% Hispanic or Latino"] = round((year_census_data["Ethnicity: Hispanic or Latino"]/year_census_data["Population"])*100, 2)
sort_by_ethnicity = year_census_data.sort_values('% Hispanic or Latino', ascending=False)["Neighborhood"].tolist()
print("\t\tRank by % Hispanic or Latino:", (sort_by_ethnicity.index(neighborhood)+1), "/", len(sort_by_ethnicity))
print()
f.write("\t\tRank by % Hispanic or Latino: " + str(sort_by_ethnicity.index(neighborhood)+1) + "/" + str(len(sort_by_ethnicity)) + "\n\n")

# Plot the % of population by ethnicity as proportion of bar
fig, ax = plt.subplots(figsize= (10, 3))
his = ax.barh(["Ethnicity"], [ethnicity_values[0]], color="#6cb9a7", label = "Hispanic or Latino")
ax.bar_label(his, labels = ["HISPANIC\n" + str(round(ethnicity_values[0], 2)) + "%"], label_type='center', color='white', fontweight='bold', fontsize=14)
nots = ax.barh(["Ethnicity"], [ethnicity_values[1]], color="black", left=[ethnicity_values[0]], label = "Not")
ax.bar_label(nots, labels = ["NOT\n" + str(round(ethnicity_values[1], 2)) + "%"], label_type='center', color='white', fontweight='bold', fontsize=14)
ax.set_title("% of Population")
plt.yticks([], [])
plt.tight_layout()
plt.axis('off')
plt.savefig('neighborhood_info/' + neighborhood.replace(" ", "") + '/population_by_ethnicity.png', bbox_inches='tight', dpi=300)
plt.close()

# Find % of population by immigration status
immigration_values = [neighborhood_census_data.iloc[0]["Immigration: Native-born"], neighborhood_census_data.iloc[0]["Immigration: Foreign-born – Naturalized citizen"], neighborhood_census_data.iloc[0]["Immigration: Foreign-born: Not US citizen"]]
immigration_values = [(v / population)*100 for v in immigration_values]

# Print / write the % of population that is foreign-born
print("\t\t% of Population Foreign-Born:", str(round((neighborhood_census_data.iloc[0]["Immigration: Foreign-born"]/population)*100, 2)) + "%")
f.write("\t\t% of Population Foreign-Born: " + str(round((neighborhood_census_data.iloc[0]["Immigration: Foreign-born"]/population)*100, 2)) + "%\n")

# Print / write the rank of neighborhood by % of population that is foreign-born
year_census_data["% Foreign-Born"] = round((year_census_data["Immigration: Foreign-born"]/year_census_data["Population"])*100, 2)
sort_by_immigration = year_census_data.sort_values('% Foreign-Born', ascending=False)["Neighborhood"].tolist()
print("\t\tRank by % Foreign-Born:", (sort_by_immigration.index(neighborhood)+1), "/", len(sort_by_immigration))
f.write("\t\tRank by % Foreign-Born: " + str(sort_by_immigration.index(neighborhood)+1) + "/" + str(len(sort_by_immigration)) + "\n")

# Print / write % of population that has naturalized citizenship
print("\t\t\tNaturalized Citizenship:", str(round((neighborhood_census_data.iloc[0]["Immigration: Foreign-born – Naturalized citizen"]/population)*100, 2)) + "%")
f.write("\t\t\tNaturalized Citizenship: " + str(round((neighborhood_census_data.iloc[0]["Immigration: Foreign-born – Naturalized citizen"]/population)*100, 2)) + "%\n")

# Print / write % of population that has no US citizenship
print("\t\t\tNo US Citizenship:", str(round((neighborhood_census_data.iloc[0]["Immigration: Foreign-born: Not US citizen"]/population)*100, 2)) + "%")
print()
f.write("\t\t\tNo US Citizenship: " + str(round((neighborhood_census_data.iloc[0]["Immigration: Foreign-born: Not US citizen"]/population)*100, 2)) + "%\n\n")

# Plot % of population by immigration status as proportion of bar
plt.figure(figsize= (10, 3))
plt.barh(["Immigration Status"], [immigration_values[0]], color="gray", label = "Native-Born")
plt.barh(["Immigration Status"], [immigration_values[1]], color="green", left=[immigration_values[0]], label = "Naturalized Citizen")
plt.barh(["Immigration Status"], [immigration_values[2]], color="orange", left=[immigration_values[0]+immigration_values[1]], label = "No US Citizenship")
plt.legend()
plt.yticks([], [])
plt.xlabel("% of Population")
plt.tight_layout()
plt.savefig('neighborhood_info/' + neighborhood.replace(" ", "") + '/population_by_immigration.png', bbox_inches='tight')
plt.close()

# Calculate % of foreign born population by country of origin
immigration_columns = [c for c in neighborhood_census_data.columns if ("Immigration: Foreign-born – " in c) and ("citizen" not in c)]
immigration_columns = sorted(immigration_columns, key = lambda x: neighborhood_census_data.iloc[0][x], reverse = True)
immigration_labels = [c.replace("Immigration: Foreign-born – ", "") for c in immigration_columns]
immigration_values = [round((neighborhood_census_data.iloc[0][c]/neighborhood_census_data.iloc[0]["Immigration: Foreign-born"])*100, 2) for c in immigration_columns]

# Plot % of foreign born population by country of origin as bar chart
plt.figure(figsize = (10, 7.5))
plt.bar(immigration_labels, immigration_values, color='maroon')
plt.xticks(rotation='vertical')
plt.xlabel("Country of Birth")
plt.ylabel("% of Foreign-Born Population")
plt.title("% of Foreign-Born Population by Country of Birth")
plt.tight_layout()
plt.savefig('neighborhood_info/' + neighborhood.replace(" ", "") + '/population_by_country_birth.png', bbox_inches='tight')
plt.close()


# Get population aged 5+
population_five_plus = neighborhood_census_data.iloc[0]["Language: Population 5+ years"]

# Get % of population aged 5+ by primary language 
language_values = [neighborhood_census_data.iloc[0]["Language: English only"], neighborhood_census_data.iloc[0]["Language: Not English"]-neighborhood_census_data.iloc[0]["Language: Not English – Speaks English 'less than well'"], neighborhood_census_data.iloc[0]["Language: Not English – Speaks English 'less than well'"]]
language_values = [(v / population_five_plus)*100 for v in language_values]

# Print / write % of population aged 5+ whose primary language is not English
print("\t\t% of Population Primary Language Not-English:", str(round((neighborhood_census_data.iloc[0]["Language: Not English"]/population_five_plus)*100, 2)) + "%")
f.write("\t\t% of Population Primary Language Not-English: " + str(round((neighborhood_census_data.iloc[0]["Language: Not English"]/population_five_plus)*100, 2)) + "%\n")

# Print / write rank of neighborhood % of population aged 5+ whose primary language is not English
year_census_data["% Not English"] = round((year_census_data["Language: Not English"]/year_census_data["Population"])*100, 2)
sort_by_language = year_census_data.sort_values('% Not English', ascending=False)["Neighborhood"].tolist()
print("\t\tRank by % Primary Language Not-English:", (sort_by_language.index(neighborhood)+1), "/", len(sort_by_language))
f.write("\t\tRank by % Primary Language Not-English: " + str(sort_by_language.index(neighborhood)+1) + "/" + str(len(sort_by_language)))

# Plot % of population aged 5+ by primary language as proportion of bar
plt.figure(figsize= (10, 3))
plt.barh(["Language Status"], [language_values[0]], color="gray", label = "English-Only")
plt.barh(["Language Status"], [language_values[1]], color="green", left=[language_values[0]], label = "Speaks English Well")
plt.barh(["Language Status"], [language_values[2]], color="orange", left=[language_values[0]+language_values[1]], label = "Speaks English 'less than well'")
plt.legend()
plt.yticks([], [])
plt.xlabel("% of Population (5+ Years)")
plt.tight_layout()
plt.savefig('neighborhood_info/' + neighborhood.replace(" ", "") + '/population_by_language.png', bbox_inches='tight')
plt.close()

# Calculate % of non-English speaking population aged 5+ by primary language group
languages = ["Spanish", "Other Indo-European", "Asian and Pacific Islander", "Other"]
languages = sorted(languages, key = lambda x: neighborhood_census_data.iloc[0]["Language: " + x], reverse = True)
language_well_values = []
language_less_well_values = []
for l in languages:
    language_well_values.append(((neighborhood_census_data.iloc[0]["Language: " + l]-neighborhood_census_data.iloc[0]["Language: " + l + " – Speaks English 'less than well'"])/neighborhood_census_data.iloc[0]["Language: Not English"])*100)
    language_less_well_values.append((neighborhood_census_data.iloc[0]["Language: " + l + " – Speaks English 'less than well'"]/neighborhood_census_data.iloc[0]["Language: Not English"])*100)

# Plot % of non-English speaking population aged 5+ by primary language group as bar chart
    # Divide by 'speaks English well' and 'speaks English "less than well"'
plt.figure(figsize= (10, 7.5))
plt.bar(languages, language_well_values, color="green", label = "Speaks English Well")
plt.bar(languages, language_less_well_values, color="orange", bottom=language_well_values, label = "Speaks English 'less than well'")
plt.legend()
plt.ylabel("% of Foreign-Born Population (5+ Years)")
plt.xlabel("Language Family")
plt.tight_layout()
plt.savefig('neighborhood_info/' + neighborhood.replace(" ", "") + '/population_by_language_family.png', bbox_inches='tight')
plt.close()
