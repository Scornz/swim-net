from splinter import Browser
import time

file = open("names.txt", "w")

# Princeton: 477
# Harvard:   134
# Yale:      376
# Brown:     17
# Cornell:   258
# Columbia:  283
# Dartmouth: 272
# UPenn:     416
# Stanford:     112
# Northwestern: 401
# Duke:         280
# Notre Dame    53
# UC Berkeley   110
# Georgetown    252
# U Mich        89
# USC           102
# UVA           73
# UNC           60
# Georgia Tech  34
# UCSB          194
# UF            117

collegeNums = ["477", "134", "376", "17", "258", "283", "272", "416",
 "112", "401", "280", "53", "110", "252", "89", "102", "73", "60", "34", "194", "117"]
yearNums = ["12", "13", "14", "15", "16", "17", "18", "19", "20", "21"]

swimmers = []

with Browser() as browser:

    urlBeginning = "https://www.swimcloud.com/team/"
    # college num after beginning
    urlMiddle = "/roster/?page=1&gender=M&season_id="
    # year num after middle
    urlEnd = "&sort=name"
    
    for collegeNum in collegeNums:
        for yearNum in yearNums:
        
            url = urlBeginning + collegeNum + urlMiddle + yearNum + urlEnd
            browser.visit(url)

            personInfo = browser.find_by_css('td')
    
            # iterate over just the names (index increases by 5)
            i = 1
            while (i < len(personInfo)):
                nameArr = personInfo[i].text.split(" ")
                currName = nameArr[0] + nameArr[1]
                
                swimmers.append(currName)

                i += 5


final_swimmers = list(dict.fromkeys(swimmers)) # eliminate duplicates

print("complete")

for name in final_swimmers:
    file.write(name + "\n")    



