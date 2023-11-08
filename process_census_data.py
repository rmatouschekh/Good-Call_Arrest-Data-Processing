import numpy as np
import pandas as pd
from data_storage import zip_to_neighborhood, neighborhood_to_zip, year_to_census_key

"""
Process census data into usable format
"""

# UPDATE THIS WHEN NEW DATA BECOMES AVAILABLE
new_year = 2021

# Get zipcodes
zips = list(zip_to_neighborhood.keys())

# For each year...
rows = []
for i in range(2011, new_year+1):
    # Load data files
    dp02 = pd.read_csv('census_data/DP02/ACSDP5Y' + str(i) + '.DP02-Data.csv', low_memory=False)
    dp03 = pd.read_csv('census_data/DP03/ACSDP5Y' + str(i) + '.DP03-Data.csv', low_memory=False)
    dp05 = pd.read_csv('census_data/DP05/ACSDP5Y' + str(i) + '.DP05-Data.csv', low_memory=False)

    # Access data by zipcode
    for z in zips:
        # Adjust formatting of unusual zipcode
        if z == 83:
            z = "00083"
        
        # Filter data to zipcode
        dp02_zip = dp02[dp02["NAME"] == "ZCTA5 " + str(z)]
        dp03_zip = dp03[dp03["NAME"] == "ZCTA5 " + str(z)]
        dp05_zip = dp05[dp05["NAME"] == "ZCTA5 " + str(z)]

        # Adjust zipcode back to original formatting
        if z == "00083":
            z = 83

        # Get population, race, and ethnicity data
        if len(dp05_zip.index) > 0:
            population = dp05_zip.iloc[0]["DP05_0001E"]
            
            # Race data
            white_pop = dp05_zip.iloc[0][year_to_census_key[i]["white_pop"]]
            black_pop = dp05_zip.iloc[0][year_to_census_key[i]["black_pop"]]
            american_indian_pop = dp05_zip.iloc[0][year_to_census_key[i]["american_indian_pop"]]
            asian_pop = dp05_zip.iloc[0][year_to_census_key[i]["asian_pop"]]
            native_hawaiian_pop = dp05_zip.iloc[0][year_to_census_key[i]["native_hawaiian_pop"]]
            other_pop = dp05_zip.iloc[0][year_to_census_key[i]["other_pop"]]
            two_or_more_pop = dp05_zip.iloc[0][year_to_census_key[i]["two_or_more_pop"]]

            # Hispanic or Latino data
            hispanic_or_latino_pop = dp05_zip.iloc[0][year_to_census_key[i]["hispanic_or_latino_pop"]]
            not_hispanic_or_latino_pop = dp05_zip.iloc[0][year_to_census_key[i]["not_hispanic_or_latino_pop"]]
        else:
            population = np.nan
            white_pop = np.nan
            black_pop = np.nan
            american_indian_pop = np.nan
            asian_pop = np.nan
            native_hawaiian_pop = np.nan
            other_pop = np.nan
            two_or_more_pop = np.nan
            hispanic_or_latino_pop = np.nan
            not_hispanic_or_latino_pop = np.nan   

        # Get economic data
        if len(dp03_zip.index) > 0:
            # Economic data
            median_worker_earnings = dp03_zip.iloc[0]["DP03_0092E"]
            percent_below_poverty = dp03_zip.iloc[0]["DP03_0128PE"]
            unemployment_rate = dp03_zip.iloc[0]["DP03_0009PE"]
        else:
            median_worker_earnings = np.nan
            percent_below_poverty = np.nan
            unemployment_rate = np.nan
        
        # Get immigration and primary language data
        if len(dp03_zip.index) > 0:
            # Immigration data
            native_pop = dp02_zip.iloc[0][year_to_census_key[i]["native_pop"]]
            native_born_in_us_pop = dp02_zip.iloc[0][year_to_census_key[i]["native_born_in_us_pop"]]
            native_born_PR_USI_abroad_pop = dp02_zip.iloc[0][year_to_census_key[i]["native_born_PR_USI_abroad_pop"]]
            foreign_pop = dp02_zip.iloc[0][year_to_census_key[i]["foreign_pop"]]
            foreign_naturalized_pop = dp02_zip.iloc[0][year_to_census_key[i]["foreign_naturalized_pop"]]
            foreign_not_pop = dp02_zip.iloc[0][year_to_census_key[i]["foreign_not_pop"]]
            foreign_europe_pop = dp02_zip.iloc[0][year_to_census_key[i]["foreign_europe_pop"]]
            foreign_asia_pop = dp02_zip.iloc[0][year_to_census_key[i]["foreign_asia_pop"]]
            foreign_africa_pop = dp02_zip.iloc[0][year_to_census_key[i]["foreign_africa_pop"]]
            foreign_oceania_pop = dp02_zip.iloc[0][year_to_census_key[i]["foreign_oceania_pop"]]
            foreign_latin_america_pop = dp02_zip.iloc[0][year_to_census_key[i]["foreign_latin_america_pop"]]
            foreign_north_america_pop = dp02_zip.iloc[0][year_to_census_key[i]["foreign_north_america_pop"]]

            # Language data
            pop_5_plus = dp02_zip.iloc[0][year_to_census_key[i]["pop_5_plus"]]
            english_only = dp02_zip.iloc[0][year_to_census_key[i]["english_only"]]
            not_english = dp02_zip.iloc[0][year_to_census_key[i]["not_english"]]
            not_english_english = dp02_zip.iloc[0][year_to_census_key[i]["not_english_english"]]
            spanish = dp02_zip.iloc[0][year_to_census_key[i]["spanish"]]
            spanish_english = dp02_zip.iloc[0][year_to_census_key[i]["spanish_english"]]
            other_indo_europ = dp02_zip.iloc[0][year_to_census_key[i]["other_indo_europ"]]
            other_indo_europ_english = dp02_zip.iloc[0][year_to_census_key[i]["other_indo_europ_english"]]
            asian_pacific_islander = dp02_zip.iloc[0][year_to_census_key[i]["asian_pacific_islander"]]
            asian_pacific_islander_english = dp02_zip.iloc[0][year_to_census_key[i]["asian_pacific_islander_english"]]
            other = dp02_zip.iloc[0][year_to_census_key[i]["other"]]
            other_english = dp02_zip.iloc[0][year_to_census_key[i]["other_english"]]
        else:
            native_pop = np.nan
            native_born_in_us_pop = np.nan
            native_born_PR_USI_abroad_pop = np.nan
            foreign_pop = np.nan
            foreign_naturalized_pop = np.nan
            foreign_not_pop = np.nan
            foreign_europe_pop = np.nan
            foreign_asia_pop = np.nan
            foreign_africa_pop = np.nan
            foreign_oceania_pop = np.nan
            foreign_latin_america_pop = np.nan
            foreign_north_america_pop = np.nan
            pop_5_plus = np.nan
            english_only = np.nan
            not_english = np.nan
            not_english_english = np.nan
            spanish = np.nan
            spanish_english = np.nan
            other_indo_europ = np.nan
            other_indo_europ_english = np.nan
            asian_pacific_islander = np.nan
            asian_pacific_islander_english = np.nan
            other = np.nan
            other_english = np.nan

        row = [z, i, population, median_worker_earnings, percent_below_poverty, unemployment_rate, white_pop, black_pop, american_indian_pop, asian_pop, native_hawaiian_pop, other_pop, two_or_more_pop, hispanic_or_latino_pop, not_hispanic_or_latino_pop, native_pop, native_born_in_us_pop, native_born_PR_USI_abroad_pop, foreign_pop, foreign_naturalized_pop, foreign_not_pop, foreign_europe_pop, foreign_asia_pop, foreign_africa_pop, foreign_oceania_pop, foreign_latin_america_pop, foreign_north_america_pop, pop_5_plus, english_only, not_english, not_english_english, spanish, spanish_english, other_indo_europ, other_indo_europ_english, asian_pacific_islander, asian_pacific_islander_english, other, other_english]
        rows.append(row)


# Create dataframe of census data by zipcode
df = pd.DataFrame(rows, columns=['Zipcode', 'Year', "Population", "Economy: Median worker earnings", "Economy: Percent below poverty level", "Economy: Unemployment rate", "Race: White", "Race: Black or African American", "Race: American Indian and Alaska Native", "Race: Asian", "Race: Native Hawaiian and Other Pacific Islander", "Race: Other", "Race: Two or more", "Ethnicity: Hispanic or Latino", "Ethnicity: Not Hispanic or Latino", "Immigration: Native-born", "Immigration: Native-born – in the US", "Immigration: Native-born – in Puerto Rico, US islands, or abroad to US parents", "Immigration: Foreign-born", "Immigration: Foreign-born – Naturalized citizen", "Immigration: Foreign-born: Not US citizen", "Immigration: Foreign-born – Europe", "Immigration: Foreign-born – Asia", "Immigration: Foreign-born – Africa", "Immigration: Foreign-born – Oceania", "Immigration: Foreign-born – Latin America", "Immigration: Foreign-born – North America", "Language: Population 5+ years", "Language: English only", "Language: Not English", "Language: Not English – Speaks English 'less than well'", "Language: Spanish", "Language: Spanish – Speaks English 'less than well'", "Language: Other Indo-European", "Language: Other Indo-European – Speaks English 'less than well'", "Language: Asian and Pacific Islander", "Language: Asian and Pacific Islander – Speaks English 'less than well'", "Language: Other", "Language: Other – Speaks English 'less than well'"])
# Replace missing values with np.nan
df = df.replace("-", np.nan)
df = df.replace("(X)", np.nan)

# Save census data by zipcode
df.to_csv('census_data/census_data_zipcode.csv', index=False)


# Find census data by neighborhood

# Define keys to take the mean of
mean_keys = ["Economy: Median worker earnings", "Economy: Percent below poverty level", "Economy: Unemployment rate"]

neighborhood_rows = []
for n in list(neighborhood_to_zip.keys()):
    for y in range(2011, new_year+1):

        # Get data for year
        y_df = df[df["Year"] == y]

        # Define empty neighborhood information
        row = {'Neighborhood': n, 'Year': y, "Population": [], "Economy: Median worker earnings": [], "Economy: Percent below poverty level": [], "Economy: Unemployment rate": [], "Race: White": 0, "Race: Black or African American": 0, "Race: American Indian and Alaska Native": 0, "Race: Asian": 0, "Race: Native Hawaiian and Other Pacific Islander": 0, "Race: Other": 0, "Race: Two or more": 0, "Ethnicity: Hispanic or Latino": 0, "Ethnicity: Not Hispanic or Latino": 0, "Immigration: Native-born": 0, "Immigration: Native-born – in the US": 0, "Immigration: Native-born – in Puerto Rico, US islands, or abroad to US parents": 0, "Immigration: Foreign-born": 0, "Immigration: Foreign-born – Naturalized citizen": 0, "Immigration: Foreign-born: Not US citizen": 0, "Immigration: Foreign-born – Europe": 0, "Immigration: Foreign-born – Asia": 0, "Immigration: Foreign-born – Africa": 0, "Immigration: Foreign-born – Oceania": 0, "Immigration: Foreign-born – Latin America": 0, "Immigration: Foreign-born – North America": 0, "Language: Population 5+ years": 0, "Language: English only": 0, "Language: Not English": 0, "Language: Not English – Speaks English 'less than well'": 0, "Language: Spanish": 0, "Language: Spanish – Speaks English 'less than well'": 0, "Language: Other Indo-European": 0, "Language: Other Indo-European – Speaks English 'less than well'": 0, "Language: Asian and Pacific Islander": 0, "Language: Asian and Pacific Islander – Speaks English 'less than well'": 0, "Language: Other": 0, "Language: Other – Speaks English 'less than well'": 0}

        # Collect data for each zipcode in neighborhood
        for z in neighborhood_to_zip[n]:
            # Filter data to zipcode
            z_df = y_df[y_df["Zipcode"] == z].iloc[0]

            # For all values but neighborhood and year...
            keys = list(row.keys())[2:]
            for k in keys:
                if not pd.isna(z_df[k]): # If value exists
                    if k in mean_keys or k == "Population": # If value is to be averaged or is population
                        row[k].append(float(z_df[k]))
                    else: # If value is to be summed
                        row[k] += int(z_df[k])
                else: # If value doesn't exist
                    if k in mean_keys or k == "Population": # If value is to be averaged or is population
                        row[k].append(None)
                    else: # If value is to be summed
                        row[k] += 0
        
        # Find total population
        total_population = sum([p for p in row["Population"] if not (p is None)])

        # Find weighted mean of each economic value
        for k in mean_keys:
            new_val = 0
            leftover_pop = 0
            for i in range(len(row[k])):
                if not(row[k][i] is None) and not(row["Population"][i] is None): 
                    # If there is a population and economic data, add economic value weighted by % of population
                    new_val += (row["Population"][i]/total_population)*row[k][i]
                elif (row[k][i] is None) and not (row["Population"][i] is None) and row["Population"][i] > 0:
                    # If there is no economic data but there is population data, use unweighted average of existing economic data
                        # Strange method of filling gap; could be changed
                    avg_val = [kv for kv in row[k] if not (kv is None)]
                    if avg_val:
                        avg_val = sum(avg_val)/len(avg_val)
                        new_val += (row["Population"][i]/total_population)*avg_val
            
            row[k] = new_val
        
        # Set population
        row["Population"] = total_population

        # Append neighborhood data
        neighborhood_rows.append(row)

# Save census data by year
neighborhood_df = pd.DataFrame(neighborhood_rows)
neighborhood_df.to_csv('census_data/census_data_neighborhood.csv', index=False)