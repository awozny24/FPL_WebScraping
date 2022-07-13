# FPL_WebScraping
For FPL engineers to scrape data (using selenium in python) about inspections for different projects and determine the project status.

Starts out at https://secureapps.charlottecountyfl.gov/CitizenAccess/Welcome.aspx?TabName=Home&TabList=Home and enters a given project permit ID, searches the website, finds the completed inspections, and determines the status of the project.

"FPL_WebScraping.py" contains all the functions that can be used by the user to scrape the web.
"main.py" is a sample file that shows the setup and the main function to be call, which is GetData(...)
"PermitStatus.csv" is the default filename for the results, and the one provided is a small example of what the outputted file looks like.
"sampledata-permits.csv" is a sample file of many ids to run the program on.
