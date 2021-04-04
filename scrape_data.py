from splinter import Browser
from selenium import webdriver
import time

import os
import pandas as pd
import sys

names_location = "data/names.csv"
# Path needs to have backslashes (chrome driver doesn't like forward slashes)
xlsx_location = os.path.abspath('data\\raw_xlsx\\')
names = pd.read_csv(names_location, na_values='?', delimiter=',', skipinitialspace=True)

names = names.fillna('')

options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": xlsx_location,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}

options.add_experimental_option("prefs", prefs)
browser = Browser('chrome', options=options)

# Visit URL
url = "https://www.usaswimming.org/times/individual-times-search"
browser.visit(url)

search_button = browser.find_by_id("Times_TimesSearchDetail_Index_Div-1-Search")

advanced_search = browser.find_by_id("Times_TimesSearchDetail_Index_Div-1-Advanced-Search")
advanced_search.click()

# Get the starting index
start_index = int(sys.argv[1])

# Wait 20 seconds while we get some data!
time.sleep(13)

for index, row in names.iterrows():

    # Skip forward to get to the start index
    if index < start_index:
        continue

    # Get the names of the swimmers
    first_name = row['First Name']
    last_name = row['Last Name']

    if not first_name or not last_name or len(first_name) == 0 or len(last_name) == 0:
        print(f"Invalid name at row {index}")
        continue

    # Grab the first name and last name and throw them into the form
    browser.fill('Times_TimesSearchDetail_Index_Div-1-FirstName', first_name)
    browser.fill('Times_TimesSearchDetail_Index_Div-1-LastName', last_name)
    # Search!
    search_button.click()
    # Wait 1.5 seconds for this data to load
    time.sleep(1.67)

    if browser.is_element_not_present_by_id("Times_TimesSearchDetail_Index_Div-1-DownloadButton"):
        print(f"No results for {first_name} {last_name}!")
        continue

    # Grab the download button, find it by id, and click it!
    download_button = browser.find_by_id("Times_TimesSearchDetail_Index_Div-1-DownloadButton")
    download_button.click()
    # Download successful
    print(f"Download successful for {first_name} {last_name}!")