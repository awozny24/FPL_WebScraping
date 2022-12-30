# FPL_WebScraping
For FPL engineers to scrape data about inspections for different projects and determine the project status.


### Setup
Download or clone this Github repository to your local machine.  

In order to run the script, go to https://chromedriver.chromium.org/downloads and download the chromedriver version associated with your version of Chrome.
NOTE: Because Chrome might update to a different version automatically, the python scripts might fail due to conflicting versions of the chromedriver and Chrome.
To fix this, go the above website to download a new version of chrome.  

Open the RunWebScraper.sh file in a text editor and edit the parameters:
Markup :  *WEBDRIVER
          *INPUTFILE="SAMPLE DATA.csv"
          *OUTPUTFILE="PermitStatus.csv"
