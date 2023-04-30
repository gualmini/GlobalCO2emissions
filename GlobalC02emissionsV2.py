import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# list of changes I made:
# NOTE COUNTRY is fgor me also COUNTRY19, i guess a footnote was removed in trhe meantime from the wikipedia page
# I got rid of the graph inclusing the chnage in emissions for all countries, this was indeed meant for myself and not readable for the user
# I added a for loop to clean up the data and got rd of the part in which poorly entered data were hard-coded

available_tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_countries_by_carbon_dioxide_emissions")

def find_relevant_table(list_of_table):
    for available_table in available_tables:
        if "Fossil CO2 emissions (Mt CO2)" in available_table.columns:
            return available_table

target_table = find_relevant_table(available_tables)

# Eliminate multi -index
current_labels = target_table.columns.to_flat_index()

# Create new column labels by joining the first and second rows of the multi-index and assign new column labels
labels = []
for col in target_table.columns:
    if col[0] != col[1]:
        labels.append(f"{col[0]} {col[1]}")
    else:
        labels.append(col[0])
target_table.columns = labels

#eliminate non_countries
non_countries = ["World", "World – International Aviation", "World – International Shipping", "European Union"]
target_table_only_countries = target_table[~target_table["Country[19]"].isin(non_countries)]

#eliminates all wrongly entered data, why did you do this, really
target_table_only_countries = target_table_only_countries.replace("\,", "", regex=True)
for i in range(len(target_table_only_countries)):
    for j in range(len(target_table_only_countries.columns)):
        cell_value = str(target_table_only_countries.iloc[i,j])
        last_dot_index = cell_value.rfind('.')
        if last_dot_index != -1 and last_dot_index != len(cell_value) - 1:
            target_table_only_countries.iloc[i,j] = cell_value[:last_dot_index].replace('.', '') + cell_value[last_dot_index:]

# selects first 5 columns, and changes data to numeric
emission_df = target_table_only_countries.iloc[:,0:5]

def change_data_to_numeric(dataframe, first_column, last_column):
    for column in range (first_column, last_column +1):
        relevant_column = dataframe.columns[column]
        dataframe[relevant_column] = pd.to_numeric(dataframe[relevant_column], errors="coerce")
    return dataframe

emission_df = change_data_to_numeric(emission_df, 1, 4)


# selects 5 largest based on last measurement
most_recent_measurement_column = emission_df.columns[4]
top_emission_df = emission_df.nlargest(5, columns=most_recent_measurement_column)


# Graph 1 using top_emission_df
countries = top_emission_df["Country[19]"].tolist()
years = [1990, 2005, 2017, 2021]

emissions = []
for country in countries:
    row = top_emission_df[top_emission_df["Country[19]"] == country]
    country_emissions = [row[f"Fossil CO2 emissions (Mt CO2) {year}"].item() for year in years]
    emissions.append(country_emissions)

# Create the plot
for _ in range(5):
    plt.plot(years, emissions[_], label=countries[_])

# Labels, legend, title and show the plot
plt.xlabel("Year")
plt.ylabel("Fossil CO2 emissions (Mt CO2)")
plt.title("Top 5 CO2 Emission Countries")
plt.legend()
plt.xticks(years)
plt.show()



#this part creates the dataframe for worst and best changers
# it was not clear to me what counts as best or worst, I classified based on the change 1990-2021

#here we set up the dataframe
emission_and_relative_change_in_emission_df = emission_df
emission_and_relative_change_in_emission_df["Change in 1990"] = 0
emission_and_relative_change_in_emission_df["Change in 2005"] = ""
emission_and_relative_change_in_emission_df["Change in 2017"] = ""
emission_and_relative_change_in_emission_df["Change in 2021"] = ""

#now we fill the dataframe
for index, row in emission_and_relative_change_in_emission_df.iterrows():
    if row["Fossil CO2 emissions (Mt CO2) 1990"] == 0 or row["Fossil CO2 emissions (Mt CO2) 1990"] == 0:
        emission_and_relative_change_in_emission_df.at[index, "Change in 2005"] = 0
    else:
        percent_change = (row["Fossil CO2 emissions (Mt CO2) 2005"] - row["Fossil CO2 emissions (Mt CO2) 1990"])  * 100 / row[
            "Fossil CO2 emissions (Mt CO2) 1990"]
        emission_and_relative_change_in_emission_df.at[index, "Change in 2005"] = percent_change

    if row["Fossil CO2 emissions (Mt CO2) 2005"] == 0 or row["Fossil CO2 emissions (Mt CO2) 1990"] == 0:
        emission_and_relative_change_in_emission_df.at[index, "Change in 2017"] = 0
    else:
        percent_change = (row["Fossil CO2 emissions (Mt CO2) 2017"] - row["Fossil CO2 emissions (Mt CO2) 1990"])  * 100 / row[
            "Fossil CO2 emissions (Mt CO2) 1990"]
        emission_and_relative_change_in_emission_df.at[index, "Change in 2017"] = percent_change

    if row["Fossil CO2 emissions (Mt CO2) 2017"] == 0 or row["Fossil CO2 emissions (Mt CO2) 1990"] == 0:
        emission_and_relative_change_in_emission_df.at[index, "Change in 2021"] = 0
    else:
        percent_change = (row["Fossil CO2 emissions (Mt CO2) 2021"] - row["Fossil CO2 emissions (Mt CO2) 1990"])  * 100/ row[
            "Fossil CO2 emissions (Mt CO2) 1990"]
        emission_and_relative_change_in_emission_df.at[index, "Change in 2021"] = percent_change

# choosing best and worst 3
relative_change_in_emission_in_decending_order = emission_and_relative_change_in_emission_df.sort_values(by="Change in 2021", ascending=False)
worst_3_relative_change_in_emission_df =relative_change_in_emission_in_decending_order.head(3)
best_3_relative_change_in_emission_df =relative_change_in_emission_in_decending_order.tail(3)
best_3_and_worst_3_relative_change_in_emission_df = pd.concat([best_3_relative_change_in_emission_df, worst_3_relative_change_in_emission_df])
best_3_and_worst_3_relative_change_in_emission_df = best_3_and_worst_3_relative_change_in_emission_df.sort_values(by="Change in 2021", ascending=False)

# Graph 2 (emissions of best and worst reducers) and 3 (percentage change of best and worst reducers)
# Select data and columns of interest
years = ["1990", "2005", "2017", "2021"]
emission_columns = [f"Fossil CO2 emissions (Mt CO2) {year}" for year in years]
countries = best_3_and_worst_3_relative_change_in_emission_df["Country[19]"].tolist()
data = best_3_and_worst_3_relative_change_in_emission_df[emission_columns]

# Plot the lines
plt.figure(figsize=(10, 6))
for i, country in enumerate(countries):
    plt.plot(years, data.iloc[i], label=country)

# Add titles, labels, legend and show plot
plt.title("Fossil CO2 Emissions (Mt CO2) of three best and worst reducers")
plt.xlabel("Year")
plt.ylabel("Fossil CO2 Emissions (Mt CO2)")
plt.legend()
plt.show()

#Graph 3
# update data of interest
change_columns = [f"Change in {year}" for year in years]
data = best_3_and_worst_3_relative_change_in_emission_df[change_columns]

# Plot the lines
plt.figure(figsize=(10, 6))
for i, country in enumerate(countries):
    plt.plot(years, data.iloc[i], label=country)

# Add titles, labels, legend and show plot
plt.title("Change in Fossil CO2 Emissions of three best and worst reducers since 1990")
plt.xlabel("Year")
plt.ylabel("Change in CO2 Emissions")
plt.legend()
plt.show()


# now we create the dataframe of sizable changers and we get the tree extremes on each side
sizeable_relative_change_in_emission_df = emission_and_relative_change_in_emission_df[emission_and_relative_change_in_emission_df.iloc[:, 1] >= 5]
sizeable_relative_change_in_emission_in_decending_order = sizeable_relative_change_in_emission_df.sort_values(by="Change in 2021", ascending=False)
worst_3_sizeable_relative_change_in_emission_df = sizeable_relative_change_in_emission_in_decending_order.head(3)
best_3_sizeable_relative_change_in_emission_df = sizeable_relative_change_in_emission_in_decending_order.tail(3)
best_3_and_worst_3_sizeable_relative_change_in_emission_df = pd.concat([best_3_sizeable_relative_change_in_emission_df, worst_3_sizeable_relative_change_in_emission_df])
best_3_and_worst_3_sizeable_relative_change_in_emission_df = best_3_and_worst_3_sizeable_relative_change_in_emission_df.sort_values(by="Change in 2021", ascending=False)


# Graph 4 (emissions of best and worst reducers) and 3 (percentage change of best and worst reducers)
#update data of interest
data = best_3_and_worst_3_sizeable_relative_change_in_emission_df[emission_columns]

# Plot the lines
plt.figure(figsize=(10, 6))
for i, country in enumerate(countries):
    plt.plot(years, data.iloc[i], label=country)

# Add titles, labels, legend and show plot
plt.title("Fossil CO2 Emissions (Mt CO2) of three best and worst sizeable reducers")
plt.xlabel("Year")
plt.ylabel("Fossil CO2 Emissions (Mt CO2)")
plt.legend()
plt.show()

#Graph 5
#update the data of interest
data = best_3_and_worst_3_sizeable_relative_change_in_emission_df[change_columns]

# Plot the lines
plt.figure(figsize=(10, 6))
for i, country in enumerate(countries):
    plt.plot(years, data.iloc[i], label=country)

# Add titles, labels, legend and show plot
plt.title("Change in Fossil CO2 Emissions of three best and worst sizeable reducers since 1990")
plt.xlabel("Year")
plt.ylabel("Change in CO2 Emissions")
plt.legend()
plt.show()
