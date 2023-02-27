#!/bin/usr/python3

# import file with relevant functions
import FPL_WebScraper
import pandas as pd
from sys import platform
import sys

# path to webdriver
webDriverPath = sys.argv[1]

# read data (account for spaces)
inputFile = ""
ind = 2
while "csv" not in inputFile:
  inputFile += sys.argv[ind]
  ind += 1
  inputFile += ' '
inputFile = inputFile[:-1]

data = pd.read_csv(inputFile, names=["PermitNumber", "Name", "Num", "Loc"])

# output file name
outputFileName = sys.argv[ind]

# whether or not to overwrite output file and start from scratch
overwriteFile = True
if sys.argv[ind+1] == "true":
  overwriteFile = True
else:
  overwriteFile = False

# list of permits
data_dict=data.to_dict()
permit_list=data["PermitNumber"].to_list() #displays all permits
length=len(data.columns)

# relevant permits
relevant_inspections = ["Footer", "Slab", "Wall Sheathing", "Roof Sheathing", 
                        "Dry In", "Electric Rough", "Framing", "Insulation",
                        "Electric Temporary Service"]

# edge case: 20210519111
# "approved" & electric temp service test: 20210831265
# test failed permit: [2021083126, 1234]

# go to start url
start_url = 'https://aca-prod.accela.com/BOCC/Default.aspx'    

# initialize browser
browser = FPL_WebScraper.InitializeBrowser(start_url, webDriverPath)

# scrape data
# permit_use = [20210831265, 2021083126, 1234, 20210519111]
permit_use = permit_list[0::]
# permit_use = [20210829720]
FPL_WebScraper.GetData(browser, permit_use, relevant_inspections, webDriverPath, filenameResult=outputFileName, overwrite_csv=overwriteFile, numRetryPermit=5)

browser.close()