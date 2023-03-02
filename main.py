#!/bin/usr/python3

######################################################
# USER PARAMETERS #
# Only change these parameters.
#######################################################
webDriverPath = "/Users/alexanderwozny/Documents/chromedriver"
# webDriverPath ="C:\webdrivers\chromedriver.exe"
inputFile = "SAMPLE DATA.csv"
outputFileName = "PermitStatus.csv"
start_url = 'https://aca-prod.accela.com/BOCC/Default.aspx' 
overwriteFile = True
########################################################

# import file with relevant functions
import FPL_WebScraper
import pandas as pd
from sys import platform
import sys

# read data from inputFile csv
data = pd.read_csv(inputFile, names=["PermitNumber", "Name", "Num", "Loc"])

# whether or not to overwrite output file and start from scratch
# This can be defined above by the user, but if the -o flag is used in the command line, then ovewriteFile is set to True.
# And if the -a flag (append) is used in the command line, then overwriteFile is set to False
if len(sys.argv) > 1:
    if sys.argv[1] == "-o":
        overwriteFile = True
    elif sys.argv[1] == "-a":
        overwrite = False

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
   

# initialize browser
browser = FPL_WebScraper.InitializeBrowser(start_url, webDriverPath)

# scrape data
# permit_use = [20210831265, 2021083126, 1234, 20210519111]
permit_use = permit_list[0::]
# permit_use = [20210829720]
FPL_WebScraper.GetData(browser, permit_use, relevant_inspections, webDriverPath, start_url, filenameResult=outputFileName, overwrite_csv=overwriteFile, numRetryPermit=5)

browser.close()