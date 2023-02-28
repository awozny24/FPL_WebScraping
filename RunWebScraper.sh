#!/bin/sh

# WEBDRIVER="C:\webdrivers\chromedriver.exe"
WEBDRIVER="/Users/alexanderwozny/Documents/chromedriver"
INPUTFILE="SAMPLE DATA.csv"
OUTPUTFILE="PermitStatus.csv"

OVERWRITE="true"
while getopts 'a' OPTION; do
  case "$OPTION" in 
    a)
      OVERWRITE="false"
      ;;
  esac
done

# run the program
python3 ./utils/main.py $WEBDRIVER $INPUTFILE $OUTPUTFILE $OVERWRITE

# run the program again in case it fails, but do not overwrite
python3 ./utils/main.py $WEBDRIVER $INPUTFILE $OUTPUTFILE "false"
