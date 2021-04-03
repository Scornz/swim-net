from splinter import Browser
from selenium import webdriver
import time

import os
import pandas as pd


# Let's get 100 values
n = 100 

names_location = "data/test_names.csv"
# Path needs to have backslashes (chrome driver doesn't like forward slashes)
xlsx_location = os.path.abspath('data\\raw_xlsx\\')
names = pd.read_csv(names_location, na_values='?', delimiter=',', skipinitialspace=True)


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

# Wait 20 seconds while we get some data!
time.sleep(20)

for index, row in names.iterrows():
    # Get the names of the swimmers
    first_name = row['First Name']
    last_name = row['Last Name']

    # Grab the first name and last name and throw them into the form
    browser.fill('Times_TimesSearchDetail_Index_Div-1-FirstName', first_name)
    browser.fill('Times_TimesSearchDetail_Index_Div-1-LastName', last_name)
    # Search!
    search_button.click()
    # Wait 2.5 seconds for this data to load
    time.sleep(2.5)

    if browser.is_element_not_present_by_id("Times_TimesSearchDetail_Index_Div-1-DownloadButton"):
        print(f"No results for {first_name} {last_name}!")
        continue

    # Grab the download button, find it by id, and click it!
    download_button = browser.find_by_id("Times_TimesSearchDetail_Index_Div-1-DownloadButton")
    download_button.click()

    file_name = f"Times For {first_name} {last_name}.xlsx"
    file_path = os.path.join(xlsx_location, file_name)

    check_limit = 20
    i = 0
    print(f"Waiting for download...")
    while not os.path.exists(file_path) and i < check_limit:
        time.sleep(0.15)
        i += 1
    
    # Skip this item if we haven't found the file yet (something happened...)
    if i >= check_limit:
        print("Download not successful!")
        continue

    # Download successful
    print("Download successful!")