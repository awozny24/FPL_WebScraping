#!/bin/usr/python3

# import file with relevant functions
import FPL_WebScraper
import pandas as pd

# read data
# data=pd.read_csv("./sampledata-permits.csv")
data = pd.read_csv("./SAMPLE DATA.csv", names=["PermitNumber", "Name", "Num", "Loc"])

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
permit_use = permit_list[0::]
FPL_WebScraper.GetData(browser, permit_use, relevant_inspections, webDriverPath, filenameResult="PermitStatus", keepRawInspectionStatus=False, overwrite_csv=False, numRetryPermit=3)
