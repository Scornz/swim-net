import time

import os
import pandas as pd
from collections import defaultdict

# Get list of events and ages
from swimnet import events, ages, metrics
from metrics import *

names_location = "data/test_names.csv"
# Path needs to have backslashes (chrome driver doesn't like forward slashes)
xlsx_location = os.path.abspath('data\\raw_xlsx\\')

# All possible columns
columns = ['Name']
for age in ages:
    for event in events:
        columns.append(f"{event} {age}")

columns.extend(metrics)

def dateTimeToSec(datTimStr):
    tt = pd.to_datetime(datTimStr).time()
    return float((tt.hour * 3600 + tt.minute * 60 + tt.second + 10**-6 * tt.microsecond) - (43200))

data = pd.DataFrame(columns=columns)
# Go through every excel sheet in here
for file in os.listdir(xlsx_location):
    # Extract the name (lazily) from the file name
    names = file.replace("Times For ","").replace(".xlsx","").split(' ')
    name = f"{names[0]} {names[1]}"
    file_path = os.path.join(xlsx_location, file)
    # Read the data in from the excel sheet
    # This is the data object to be added to the data frame 
    # (will only contain name, highschool times, and output metrics)
    datum = {"Name": name}
    # This contains all events throughout all ages (used to prevent duplicates)
    # Highschool and college
    all_times = {}

    swimmer = pd.read_excel(file_path, engine='openpyxl')
    
    # These two dictionaries will contain all events swam
    # Key is the event, and the value is a list of times (maximum of 4 for 4 years)
    highschool_times = defaultdict(list)
    college_times = defaultdict(list)
    # Iterate through each row of the excel file
    for index, row in swimmer.iterrows():
        event = row['Event']
        time = round(dateTimeToSec(row['Alt. Adj. Time']), 2)
        age = int(row['Age'])
        power_points = int(row['Power Points'])
        column = f"{event} {age}"
        
        # Only add this time IF IT IS NOT ALREADY ADDED
        # This will account for LCM times at the same age
        # Make sure the event is in the events list (we don't want 800 FR)
        if column not in all_times and event in events:
            all_times[column] = time
            # If this is something we should be adding to the CSV file
            # Equivalent to checking if the age is under 18
            if column in columns:
                datum[column] = time
                highschool_times[event].append((time, power_points))
            else:
                # We must be in college then
                college_times[event].append((time, power_points))

    
    # Get an average percentage improved
    datum['Top 3 Ratio'] = average_ratio_top_n(3, highschool_times, college_times)
    datum['Top 3 Power Points'] = average_power_points_top_n(3, highschool_times, college_times)
    datum['Top 3 Improvement'] = average_improvement_top_n(3, highschool_times, college_times)
    datum['Top 5 Improvement'] = average_improvement_top_n(5, highschool_times, college_times)

    if (datum['Top 3 Ratio'] == -1 or datum['Top 5 Improvement'] == -1):
        print("Non-value, something went wrong here. Skipping...")
        continue

    print(f"Finished processing {name}.")
    data = data.append(datum, ignore_index=True)

# All non-existent times should be 0 (instead of NaN)
data = data.fillna(0)
data.to_csv('data/swimmers.csv', sep=',', header=True, columns=columns, index = False)