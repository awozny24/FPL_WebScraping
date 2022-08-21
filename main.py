#!/bin/usr/python3

# import file with relevant functions
import FPL_WebScraper
import pandas as pd

# read data
data=pd.read_csv("./sampledata-permits.csv")

# list of permits
data_dict=data.to_dict()
permit_list=data["PermitNumber"].to_list() #displays all permits
length=len(data.columns)

# relevant permits
relevant_inspections = ["Footer", "Slab", "Wall Sheathing", "Roof Sheathing", 
                        "Dry In", "Electric Rough", "Framing", "Insulation",
                        "Electric Temporary Service"]

# path to webdriver
webDriverPath = "/Users/alexanderwozny/Documents/chromedriver"

# edge case: 20210519111
# "approved" & electric temp service test: 20210831265
# test failed permit: [2021083126, 1234]

# go to start url
start_url = 'https://secureapps.charlottecountyfl.gov/CitizenAccess/Welcome.aspx?TabName=Home&TabList=Home'    

# initialize browser
browser = FPL_WebScraper.InitializeBrowser(start_url, webDriverPath)

# scrape data
# permit_use = [20210831265, 2021083126, 1234, 20210519111]
for i in range(1, len(permit_list[0:253])):
  permit_use = permit_list[0:i]
  FPL_WebScraper.GetData(browser, permit_use, relevant_inspections, webDriverPath, filenameResult="PermitStatus", keepRawInspectionStatus=False, overwrite_csv=False, numRetryPermit=1)


# print the list of permits that were unsuccessfully scraped
# print(FPL_WebScraper.GetUnusedPermits("PermitStatus.csv", permit_use))
# start_url = 'https://secureapps.charlottecountyfl.gov/CitizenAccess/Welcome.aspx?TabName=Home&TabList=Home'    
