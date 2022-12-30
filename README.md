# FPL_WebScraping
For FPL engineers to scrape data about inspections for different projects and determine the project status.


### Setup
Download or clone this Github repository to your local machine.  

In order to run the script, go to https://chromedriver.chromium.org/downloads and download the chromedriver version associated with your version of Chrome.
NOTE: Because Chrome might update to a different version automatically, the python scripts might fail due to conflicting versions of the chromedriver and Chrome.
To fix this, go the above website to download a new version of chrome.  

Open the RunWebScraper.sh file in a text editor and edit the parameters:
- WEBDRIVER - absolute path to the chrome webdriver on your local machine
- INPUTFILE - name of the .csv file to read the permit numbers from; this file must either be in the same folder as RunWebScraper.sh or a -relative path can be used
- OUTPUTFILE - name of the file to output the permit number, most recent inspection, and record status; this file must either be in the same folder as RunWebScraper.sh or a relative path can be used


### Running the Web Scraper
To run the file, open the Command Prompt or Terminal. Navigate to the folder that contains the RunWebScraper.sh file. In the Command Prompt or Terminal window, type:

./RunWebScraper

The web scraper will start running, and a Chrome window will open up controlled by the automation software. The specified output file will be created and will be updated as data is scraped for each permit for each permit's most recent inspection and record status. An "Error" will exist in the column for permits that have not been scraped yet or where failure to scrape data occurred.

Running the file as shown above overwrites the output file, and scrapes each permit from scratch. 
The flag -a can be optionally typed afterwards:

./RunWebScraper -a

If for some reason the program failed (e.g. from disrupted internet connection), this flag can be called to pick up from where the program left off. With this flag, the wep scraper just scrapes data for the permits that have "Error" in one of its columns.


