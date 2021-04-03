import time

import os
import pandas as pd
from collections import defaultdict

# Get list of events and ages
from swimnet import events, ages, metrics

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
    datum = {"Name": name}
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
        if column not in datum and column in columns:
            datum[column] = time

    print(f"Finished processing {name}.")
    data = data.append(datum, ignore_index=True)

# All non-existent times should be 0 (instead of NaN)
data = data.fillna(0)
print(data)