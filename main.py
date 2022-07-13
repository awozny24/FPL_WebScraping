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
                        "Dry In", "Electric Rough", "Framing", "Electric Temporary Service",
                        "Insulation"]

# path to webdriver
webDriverPath = "/Users/alexanderwozny/Documents/chromedriver"

# edge case: 20210519111

# scrape data
permit_use = permit_list[0:120]
FPL_WebScraper.GetData(permit_use, relevant_inspections, webDriverPath, filenameResult="PermitStatus", keepRawInspectionStatus=False, overwrite_csv=False)



