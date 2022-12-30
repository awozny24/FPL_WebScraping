# FPL_WebScraping
For FPL engineers to scrape data (using selenium in python) about inspections for different projects and determine the project status.

Starts out at https://secureapps.charlottecountyfl.gov/CitizenAccess/Welcome.aspx?TabName=Home&TabList=Home and enters a given project permit ID, searches the website, finds the completed inspections, and determines the status of the project.

"FPL_WebScraping.py" contains all the functions that can be used by the user to scrape the web.
"main.py" is a sample file that shows the setup and the main function to be call, which is GetData(...)
"PermitStatus.csv" is the default filename for the results, and the one provided is a small example of what the outputted file looks like.
"sampledata-permits.csv" is a sample file of many ids to run the program on.

For the main function that needs to be called, GetData(...):
  - permit_use: list of integer permits to scrape data on; can also insert a single value
  - relevant_inspections: list of relevant inspection titles; those provided by John are "Footer", "Slab", "Wall Sheathing", "Roof Sheathing", etc.
  - overwrite_csv: specifies whether to overwrite the .csv files that result from previous runs
  - filenameResult: name of the .csv file to output the results
  - filenameSuccess: name of the .csv file to output the raw data to
  - keepRawInspectionStatus: determines whether or not to record the raw data by storing it in filenameSuccess.csv
  - numTryClick: specifies how many times that the program should try to perform a function on a web page before quitting
  - numRetryPermit: specifies how many times to retry searching for a permit if failure occurred during the intial scraping

