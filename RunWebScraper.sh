#!/bin/sh

# WEBDRIVER="C:\webdrivers\chromedriver.exe"
WEBDRIVER="/Users/alexanderwozny/Documents/chromedriver"
INPUTFILE="SAMPLE DATA.csv"
OUTPUTFILE="PermitStatus.csv"

python3 ./utils/main.py $WEBDRIVER $INPUTFILE $OUTPUTFILE