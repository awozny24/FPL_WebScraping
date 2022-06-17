#### Import and Setup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException

import csv
import time

import pandas as pd

# read data
data=pd.read_csv("./sampledata-permits.csv")

# list of permits
data_dict=data.to_dict()
permit_list=data["PermitNumber"].to_list() #displays all permits
length=len(data.columns)

# relevant permits
# note that "Not Started "
relevant_permits = ["Not Started (NS)", "Slab", "Wall", "Roof", "Inspection (INSP)"]



#### Helper Functions
# This function takes in a webElement and gets relevant information from the text
# i.e. the permit type and its status
def GetStatAndPermText(webElement):
    # get the inner html code
    innerHTML = webElement.get_attribute("innerHTML").split('">')
    
    # get the status and permit from the text
    stat = innerHTML[1].split('<')[0]
    perm = innerHTML[2].split('<')[0]
    
    # return the information
    return stat, perm

# This functions takes in a string of text and gets the number of inspection entries
def GetNumRecords(parse):
    # eliminate the "Complete " and then the number of entries is next
    parse = parse.split('Completed ')
    
    # if there is no entry for the number of inspections, 0 are completed
    if (len(parse) == 1):
        return 0
      
    # get the number of entries from inside the parentheses
    else:
        parse = parse[1].split('\n')
        numPages = int(parse[0][1:-1])
        return numPages
    
# This function tries to move to the next page of inspections
# If it fails, it recursively calls itself to try again until success or the number of times tried reaches the "quit_count"
def RecursivePageTurn(p, browser, delay, permit_number, counter, quit_count=20):
    try:
        # CSS Selector for the given page
        cssSelStr = "#ctl00_PlaceHolderMain_InspectionList_gvListCompleted > tbody > tr.ACA_Table_Pages.ACA_Table_Pages_FontSize > td > table > tbody > tr > td:nth-child(" + str(p+2) + ")"
        
        # web element of the table of inspections
        table = browser.find_element(by=By.CSS_SELECTOR, value=cssSelStr)
        
        # click to the next page
        table.click()
        
        # delay to decrease the chance of exceptions
        time.sleep(delay)

    # if a failure occurs, try again
    # if this doesn't work, add another try and catch block inside this "except"
    # or play with the sleep time
    except (ElementClickInterceptedException, StaleElementReferenceException) as e:
        print("Exception {} {}! On page {} for permit #{}".format(e, counter, p, permit_number))
        
        # continue to try to turn the page
        if (counter < quit_count):
            # recursively call function to continue trying to turn the page
            RecursivePageTurn(p, browser, delay, permit_number, counter+1, quit_count) 
            
        # if too many tries for turning the page were reached, quit and return False for failure
        else:
            print("Page Turn Quit on {} time trying".format(counter))
            return False
          
    # This exception occurs when the format of the page changes due to the list of pages 
    # (i.e. for pages 1-10 there are 12 elements, but for 11 or more, there are only 4 web elements)
    except NoSuchElementException as nsee:
        print("Exception {} {}! No Such Element b/c of page formatting. Continue until found.".format(nsee, counter))
        RecursivePageTurn(p-1, browser, delay, permit_number, counter, quit_count)

    # at this point, success has occurred
    return True

# This function continually/recursively tries to click the search button
def RecursiveSearchButtonClick(browser, counter, quit_count=10):
    # try clicking the search button
    try:
        # find the search button and click it
        permitSearchBtn = browser.find_element(by=By.CLASS_NAME, value="gs_go_img")
        permitSearchBtn.click()
        
    # if it fails, try again    
    except (ElementClickInterceptedException, StaleElementReferenceException):
        print("Exception! Failed to click search button on try {}!".format(counter))
        
        # recursively call function to continue trying to click the search button
        if (counter < quit_count):
            RecursiveSearchButtonClick(browser, counter+1, quit_count)
        
        # if too many tries occur, quit and return False for failure
        else:
            print("Search Button quit on {} time trying".format(counter))
            return False
        
    # at this point, success has occurred    
    return True
  
  
  
#### Scrape Data
# percentage of permits to use
# set to 1 to run all of them
permits_frac = 1/15

# get start time
start_time = time.time()

# open file for data in write mode
OVERWRITE_CSV = True

# open files in write mode; this overwrites
if (OVERWRITE_CSV):
    # open files to write; overwrites
    file = open("./PermitStatuses.csv", mode='w')
    fileFailure = open("./UnknownPermits.csv", mode='w')
    
    # create csv writer for data
    writer = csv.writer(file)
    writerFailure = csv.writer(fileFailure)
    
    # add column names
    writer.writerow(["ID", "SLAB", "WALL", "ROOF"])    
    
# open files in append mode    
else:
    # open files to write to using; does not overwrite, just appends
    file = open("./PermitStatuses.csv", mode='a')
    fileFailure = open("./UnknownPermits.csv", mode='a')

    # create csv writer for data
    writer = csv.writer(file)
    writerFailure = csv.writer(fileFailure)

# set up web driver
webDriverPath = "/Users/alexanderwozny/Documents/chromedriver"
s = Service(webDriverPath)
browser = webdriver.Chrome(service=s)

# go to to start url
start_url = 'https://secureapps.charlottecountyfl.gov/CitizenAccess/Welcome.aspx?TabName=Home&TabList=Home'
browser.get(start_url)

# number of times to try turning the page before quitting
quit_count=10
success = True

# for each permit id
for numIter, permit_number in enumerate(permit_list[10:int(len(permit_list)*permits_frac)]):

    # enter permit id into search box
    searchbox = browser.find_element(by=By.ID, value="txtSearchCondition")

    # clear and then enter the permit number into the search bar
    searchbox.clear()
    searchbox.send_keys(str(permit_number))

    # find and click on button to search id
    counterSearch = 1
    searchSuccess = RecursiveSearchButtonClick(browser, counterSearch, quit_count)

    # if clicking the search button was a success
    if (searchSuccess == True):
        # Go to Inspections for the searched for permit ID
        RecInfoDropdown = browser.find_element(by=By.CSS_SELECTOR, value="[title^='Record Info']")
        RecInfoDropdown.click()

        # keep dropdown open in order to click on inspections option
        browser.implicitly_wait(1)

        # click on "Inspection" option and go to inspections page for given permit id
        InspDropdownBtn = browser.find_element(by=By.CSS_SELECTOR, value="[title^='Inspections']")
        InspDropdownBtn.click()

        # get number of records and number of pages
        completedText = WebDriverWait(browser, 60).until(EC.visibility_of_element_located((By.ID, "ctl00_PlaceHolderMain_InspectionList_lblInspectionCompleted")))
        numRecords = GetNumRecords(completedText.text)
        numPages = int(numRecords/5) + 1

        # time delay for preventing stale reference
        delay = 1.5

        # store each completed permit and status
        status = list()
        permit = list()

        # for each page   
        for p in range(1, numPages+1):

            # stop at 10 pages
            if (p > 10):
                break;
            
            #### Do for loop to read through each inspection and determine status ####
            # read status and of permit inspections (this is used to get the number on each page)
            completed = browser.find_element(by=By.ID, value="divInspectionListCompleted")

            # get the table of completed inspections
            inspTable = completed.find_elements(by=By.CLASS_NAME, value="ACA_Width45em")

            # for each completed inspection, get the permit and status
            # done in groups of 5
            for i in range(0,len(inspTable)):

                # get string of text relating to status and permit
                statusText, permitText = GetStatAndPermText(inspTable[i])

                # get the status and permit
                status.append(statusText.split(' ')[0])
                permit.append(permitText.split(' ')[0])


            # initialize counter for counting the number of tries to turn the page
            counter = 1
            
            # set success equal to True for if the if statement conditions are not met
            success = True
            
            # if there is only one page (numRecords > 5) and the current page is not the last, turn the page
            if ((numRecords > 5) & (p != numPages)):
                success = RecursivePageTurn(p, browser, delay, permit_number, counter, quit_count)
                

        # if the permit information was successfully retrieved
        if (success == True):
            # put status and permit into a pandas dataframe
            data = {"status":status, "permit":permit}
            statusPanda = pd.DataFrame(data)

            # determine status of permit
            passed = statusPanda["status"] == "Pass"
            # approved = statusPanda["status"] == "Approved"

            # begin row to write in csv with permit number
            row = [permit_number]

            # for each relevant permit
            for per in relevant_permits[1:-1]:
                # check if the permit type is in the list
                permitType = statusPanda["permit"] == per

                # if the specified permit type did not pass (resulting dataframe is empty) use "N" for no
                if (statusPanda.loc[((passed) & (permitType))].empty):
                    row.append("N")
                # if the specified permit type passed use "Y" for yes
                else:
                    row.append("Y")

            # write a row to the csv
            writer.writerow(row)
        # if the permit information was not successfully retrieved
        else:
            writerFailure.writerow(permit_number)
    else:
        writerFailure.writerow(permit_number)
        
    
    
# close the csv file
file.close()
fileFailure.close()

# get ending time
end_time = time.time()
        




