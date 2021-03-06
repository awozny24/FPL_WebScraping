#### Setup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException

import csv
import time
from pathlib import Path

import pandas as pd


# read data
data=pd.read_csv("./sampledata-permits.csv")

# list of permits
data_dict=data.to_dict()
permit_list=data["PermitNumber"].to_list() #displays all permits
length=len(data.columns)

# path to webdriver
webDriverPath = "/Users/alexanderwozny/Documents/chromedriver"


#### Helper Functions
# Initialize Browser
def InitializeBrowser(start_url, webDriverPath):
    # set up web driver
    s = Service(webDriverPath)
    browser = webdriver.Chrome(service=s)
    
    # intialize browser at specified start url
    browser.get(start_url)
    
    return browser



# This function takes in a webElement and gets relevant information from the text
# i.e. the permit type and its status
def GetStatAndPermText(webElement):
    # get the inner html code
    innerHTML = webElement.get_attribute("innerHTML").split('">')
    
    # get the status and permit from the text
    stat = innerHTML[1].split('<')[0]
    perm = innerHTML[2].split('<')[0].split(' (')[0]

    # return the information
    return stat, perm



# This functions takes in a string of text and gets the number of inspection entries
def GetNumRecords(browser):
    
    try:
        # get string containing the number of completed inspections
        completedText = WebDriverWait(browser, 60).until(EC.visibility_of_element_located((By.ID, "ctl00_PlaceHolderMain_InspectionList_lblInspectionCompleted"))).text

        # eliminate the "Complete " and then the number of entries is next
        completedInsp = completedText.split('Completed ')

        # if there is no entry for the number of inspections, 0 are completed
        if (len(completedInsp) == 1):
            return 0

        # get the number of entries from inside the parentheses
        else:
            completedInsp = completedInsp[1].split('\n')
            numRecords = int(completedInsp[0][1:-1])

            # return the number of records
            return numRecords
     
    # if the inspections table does not load, say table is empty
    except (TimeoutException, ElementNotVisibleException):
        return -1
    
    
    
# This function opens the specified files.
# filenameResult: Output files of the results. Each row has a permit id and the most recently completed inspection
# filenameSuccess: Output file of the raw results. Each row has a permit id and the result of each relevant inspection.
# overwrite_csv: Specifies whether to overwrite the csv when opening it.    
def OpenFiles(filenameResult="PermitStatus", filenameSuccess=None, overwrite_csv=False):

    if (filenameSuccess == None):
        keepRawInspectionStatus = False
    else:
        keepRawInspectionStatus = True
        if (".csv" not in filenameSuccess):
            filenameSuccess = filenameSuccess + ".csv"

    if ".csv" not in filenameResult:
        filenameResult = filenameResult + ".csv"


    createNewFile = not Path("./" + filenameResult).is_file()

    if (overwrite_csv | createNewFile):
        # open files to write; overwrites
        fileResult = open("./"+ filenameResult, mode='w')

        # create csv writer for data
        writerResult = csv.writer(fileResult)

        # add column names
        row = ["ID"]
        row = row + ["Most Recent"]
        writerResult.writerow(row)
        
        if (keepRawInspectionStatus):
            fileSuccess = open("./"+ filenameSuccess, mode='w')
            row = ["ID"]
            row = row + relevant_inspections
            writerSuccess = csv.writer(fileSuccess)
            writerSuccess.writerow(row)     
            
    # open files in append mode    
    else:
        # open files to write to using; does not overwrite, just appends
        fileResult = open("./"+ filenameResult, mode='a')

        # create csv writer for data
        writerResult  = csv.writer(fileResult)
        if (keepRawInspectionStatus):
            fileSuccess = open("./" + filenameSuccess, mode='a')
            writerSuccess = csv.writer(fileSuccess)
    
    
    # return the files and writers for the user
    if (keepRawInspectionStatus):
        files = [fileResult, fileSuccess]
        writers = [writerResult, writerSuccess]
        return files, writers
    else:
        files = [fileResult]
        writers = [writerResult]
        return files, writers    


# Close the specified files that were opened during scraping
def CloseFiles(files):
    # make sure the files is in list format
    if type(files) is not list:
        files = [files]
    
    # close each file
    for f in files:
        f.close()
    
    
# Takes inspections scraped from the page and determines which inspections passed and which did not.
# Returns a row starting with the permit id and then 'Y' (Yes) or 'N' (No) for whether an inspection passed or not.
def GetInspectionStatus(status, inspections, permit_number, relevant_inspections):
    # put status and permit into a pandas dataframe
    data = {"status":status, "inspections": inspections}
    statusPanda = pd.DataFrame(data)

    # determine status of permit
    passed = statusPanda["status"] == "Pass"

    # begin row to write in csv with permit number
    row = [permit_number]

    # for each relevant permit
    for insp in relevant_inspections:
        # check if the permit type is in the list
        inspectionType = statusPanda["inspections"] == insp

        # if the specified permit type did not pass (resulting dataframe is empty) use "N" for no
        if (statusPanda.loc[((passed) & (inspectionType))].empty):
            row.append("N")
        # if the specified permit type passed use "Y" for yes
        else:
            row.append("Y")
                 
    return row   


# Finds the most recent inspection
# Takes in the "row" from GetInspectionStatus(...) and determines the most recent 'Y' (completed inspection)
def GetMostRecentInspection(row, permit_number, relevant_inspections):

    rowResult = [permit_number]

    # get the most recent permit
    found = False
    for i in range(1, len(row))[::-1]:
        if (row[i]=="Y"):
            rowResult = rowResult + [relevant_inspections[i-1]]
            found = True
            break;

    # if no relevant inspections have been completed
    if (found == False):
        rowResult = rowResult + ["None"]

    return rowResult


# Determines the permits that did not get recorded and written to a specified file
# Returns a list of permits that are not in the file
def GetUnusedPermits(filename, permit_list_use):

    # get the permits that were recorded from the csv
    if ".csv" in filename:
        recordedPermits = pd.read_csv("./" + filename)
    else:
        recordedPermits = pd.read_csv("./" + filename + ".csv")
    recordedPermits.drop(labels=recordedPermits.columns.difference(["ID"]), axis=1, inplace=True)
    
    if type(permit_list_use) is not list:
        permit_list_use = [permit_list_use]    

   # get the list of permits used
    triedPermitsList = {"permits": permit_list_use}
    triedPermits = pd.DataFrame(triedPermitsList)

    # get unused permits (due to failure)
    unusedPermits = triedPermits.loc[~triedPermits["permits"].isin(recordedPermits["ID"])]
    
    # turn unused permits pandas to list
    unusedPermits = unusedPermits["permits"].tolist()
    
    # return unused permits
    return unusedPermits


### Functions for Iteracting with the Webpage
# This function accesses the search box on the pages and searches for
# a given permit ID
# Returns True for success and False for failure
def SearchForPermit(browser, permit_number, quit_count=10):
    # enter permit id into search box
    searchbox = browser.find_element(by=By.ID, value="txtSearchCondition")

    # clear and then enter the permit number into the search bar
    searchbox.clear()
    searchbox.send_keys(str(permit_number))

    # find and click on button to search id
    counterSearch = 1
    searchSuccess = Recursive(ClickSearchButton, browser, permit_number, counterSearch, quit_count)
    
    # return whether or not the search was successful
    return searchSuccess


# Function to click the search button
def ClickSearchButton(browser):
    # find the search button and click it
    permitSearchBtn = browser.find_element(by=By.CLASS_NAME, value="gs_go_img")
    permitSearchBtn.click()
    
    

# This function goes to the inspections page/tab
# Returns True for success and False for failure
def GoToInspections(browser, permit_number, quit_count, first_call=True):
        
    # initialize try iteration
    counter = 1
        
    # go to inspections and return success or not
    result = Recursive(GoToInspectionsHelper, browser, permit_number, counter, quit_count)
    
    # if going to inspections was a success, exit the function
    if (result == True):
        return result
    # otherwise, try calling the function to click on the search result
    else:
        # if this is the first time this function is being called
        if (first_call == True):
            return ClickPermitNumber(browser, permit_number, quit_count)
        else: 
            return False
        

# Goes to the inspections tab on the page
def GoToInspectionsHelper(browser):
    # Go to Inspections for the searched for permit ID
    RecInfoDropdown = browser.find_element(by=By.CSS_SELECTOR, value="[title^='Record Info']")
    RecInfoDropdown.click()

    # keep dropdown open in order to click on inspections option
    browser.implicitly_wait(1)

    # click on "Inspection" option and go to inspections page for given permit id
    InspDropdownBtn = browser.find_element(by=By.CSS_SELECTOR, value="[title^='Inspections']")
    InspDropdownBtn.click()
    
    

# This function is called when searching or a permit takes the user to an unorthodox page.
# (Only called a few times)
# Clicks on the permit number when needed
def ClickPermitNumber(browser, permit_number, quit_count):
    # initialize try iteration
    counter = 1
        
    # call recursive function to try to click the permit number that was searched
    return Recursive(ClickPermitNumberHelper, browser, permit_number, counter, quit_count, extraVars=[permit_number, quit_count])
    
    
def ClickPermitNumberHelper(browser, extraVars):
    
    # get web element of table
    searchQueryTable = browser.find_element(by=By.CLASS_NAME, value="ACA_Grid_OverFlow")
    
    # get the web element of the table information
    searchQueryTable = searchQueryTable.find_element(by=By.CSS_SELECTOR, value="#ctl00_PlaceHolderMain_CapView_gdvPermitList")
    
    # get array of web elements of table information 
    searchQueryTable = searchQueryTable.find_elements(by=By.CLASS_NAME, value="ACA_AlignLeftOrRightTop")
    
    # find the element that references the desired permit number
    for sqt in searchQueryTable:
        if sqt.text == str(extraVars[0]):
            # # get element to click on using xpath and click on it
            txt = ".//div/strong/a[text()='" + str(extraVars[0]) + "']"
            clickOn = sqt.find_element(by=By.XPATH, value=txt)
            clickOn.click()
                        
            # Try going to the Inspections Table
            result = GoToInspections(browser, extraVars[0], extraVars[1], first_call=False)
       
            return result
    
    # at this point, failure has occurred
    return False
       
    

    
# Gets the information from an inspection table
def GetInspectionInfo(browser, permit_number, quit_count, status, inspections):
    
    # access the inspection table
    complete = browser.find_element(by=By.ID, value="divInspectionListCompleted")
    inspTable = complete.find_elements(by=By.CLASS_NAME, value="ACA_Width45em")
    
    # get the length of the table
    lengthTable = len(inspTable)
        
    # initialize counter for number of times tried
    counter = 1
    
    # for the completed inspection table, get each (of 5) inspections
    successTotal = True
    for i in range(0,lengthTable):
        # get information from inspection table
        successIter = Recursive(GetInspectionInfoHelper, browser, permit_number, counter, quit_count, [status, inspections, i])
    
        # if the inspection table could not be read on an iteration, return false
        if (successIter == False):
            successTotal = False
            
    return successTotal



def GetInspectionInfoHelper(browser, extraVars):
    
    # access the inspection table
    complete = browser.find_element(by=By.ID, value="divInspectionListCompleted")
    inspTable = complete.find_elements(by=By.CLASS_NAME, value="ACA_Width45em")
    
    try: 
        # get the inner html code
        i = extraVars[2]
        innerHTML = inspTable[i].get_attribute("innerHTML").split('">')
    except IndexError as e:
        print(f"\n\tIndex Error!", end="")
        return False

    # get the status and permit from the text
    statusText = innerHTML[1].split('<')[0]
    permitText = innerHTML[2].split('<')[0].split(' (')[0]

    # get the status and permit
    extraVars[0].append(statusText) # extraVars[0] = status
    extraVars[1].append(permitText) # extraVars[1] = inspection



# Function to turn the page to more of the information from the inspection table
def TurnPage(browser, permit_number, quit_count, p, delay):
    
    # initialize counter
    counter = 1
    
    # call recursive function to turn page
    return Recursive(TurnPageHelper, browser, permit_number, counter, quit_count, extraVars=[p, delay])
    
    
def TurnPageHelper(browser, extraVars):
    
    # unpack extraVars
    p = extraVars[0]
    delay = extraVars[1]
    
    # CSS Selector for the given page
    cssSelStr = "#ctl00_PlaceHolderMain_InspectionList_gvListCompleted > tbody > tr.ACA_Table_Pages.ACA_Table_Pages_FontSize > td > table > tbody > tr > td:nth-child(" + str(p+2) + ")"

    # web element of the table of inspections
    table = browser.find_element(by=By.CSS_SELECTOR, value=cssSelStr)

    # click to the next page
    table.click()

    # delay to decrease the chance of exceptions
    time.sleep(delay)



    

# Generic recursive formulation for trying to perform a function/action
def Recursive(function, browser, permit_number, counter, quit_count, extraVars=None):
    
    # try to perform function
    try:
        if (extraVars == None):
            result = function(browser)
            if result != None:
                return result

        else:
            result = function(browser, extraVars)
            if result != None:
                return result

        
    # failure to perform function     
    except (ElementClickInterceptedException, StaleElementReferenceException, NoSuchElementException,
            SessionNotCreatedException, ElementNotVisibleException, TimeoutException,
            ElementNotInteractableException) as e:
        # print error message
#         print(f"\n\tException in {function.__name__}: {e.__class__.__name__}", end="")
        
        # continue trying
        if (counter < quit_count):
            return Recursive(function, browser, permit_number, counter+1, quit_count, extraVars)
        
        # stop if recursive formulation has been tried too many times
        else: 
            return False           
    
    # at this point, success has occurred
    return True


    
#### Scrape Data
def ScrapeData(permits, relevant_inspections, webDriverPath, overwrite_csv=False, filenameResult="PermitStatus", filenameSuccess="GetStatusSuccess", keepRawInspectionStatus=True, numTryClick=20):
    # get start time
    start_time = time.time()

    # make sure permit_list is in list format
    if type(permits) is not list:
        permits = [permits]

    # open files 
    if (keepRawInspectionStatus):
        # open files and initialize writers; use raw data file
        [fileResult, fileSuccess], [writerResult, writerSuccess] = OpenFiles(filenameResult=filenameResult, filenameSuccess=filenameSuccess, overwrite_csv=False)
        fileResult.close(); fileSuccess.close();
    else:
        # open files and initialize writers; don't use raw data file
        [fileResult], [writerResult] = OpenFiles(filenameResult=filenameResult, overwrite_csv=False)
        fileResult.close();

    # go to start url
    start_url = 'https://secureapps.charlottecountyfl.gov/CitizenAccess/Welcome.aspx?TabName=Home&TabList=Home'    

    # initialize browser
    browser = InitializeBrowser(start_url, webDriverPath)

    success = True

    # for each permit
    for numIter, permit_number in enumerate(permits):
        
        print(f"{numIter}.) Permit #{permit_number}", end="")
        
        # open the csv files to write to 
        if (keepRawInspectionStatus):
            # open files and initialize writers; use raw data file
            [fileResult, fileSuccess], [writerResult, writerSuccess] = OpenFiles(filenameResult=filenameResult, filenameSuccess=filenameSuccess, overwrite_csv=False)
        else:
            # open files and initialize writers; don't use raw data file
            [fileResult], [writerResult] = OpenFiles(filenameResult=filenameResult, overwrite_csv=False)
        
        try:
            # number of times to try to access web element for a certain permit
            quit_count=20

            # search for the permit; continue if successful
            if (SearchForPermit(browser, permit_number, quit_count)):

                # go to inspection table; continue if successful, otherwise move to next permit
                if (GoToInspections(browser, permit_number, quit_count)):
                    pass
                else:
                    # close the files for writing
                    if (keepRawInspectionStatus):
                        CloseFiles([fileResult, fileSuccess])
                    else:
                        CloseFiles([fileResult])
                    
                    # print failure message
                    print("\n\tFailure!")
                    
                    # move to next loop
                    continue
                    
                # get number of records in the inspection table
                numRecords = GetNumRecords(browser)
                
                # if numRecords==-1, the inspection table did not load and couldn't be read
                if (numRecords == -1):
                    # move to the next permit
                    continue;

                # get number of pages
                numPages = int(numRecords/5) + 1

                # store each completed inspection and its status
                status = list()
                inspections = list()

                # relative page number in html
                p = 1

                # initialize the success of turning the page and getting info as a success
                pageTurnSuccess = True
                getInfoSuccess = True
                
                # for each page
                while ((p < numPages+1) & (p < 11) & (pageTurnSuccess) & (getInfoSuccess)):
                    # get the completed inspections from the inspection table on each page
                    getInfoSuccess = GetInspectionInfo(browser, permit_number, quit_count, status, inspections)

                    # set delay for waiting for turning the page
                    delay = 1.5

                    # set to True, if there are no pages to turn, then success technically
                    pageTurnSuccess = True

                    # if there are pages to turn, turn the page
                    if ((numRecords > 5) & (p != numPages)):
                        pageTurnSuccess = TurnPage(browser, permit_number, quit_count, p, delay)
                       
                    # set p to next page
                    p = p + 1
                    
                   
                # move to next permit, if the page turn was unsuccessful
                if (pageTurnSuccess == False):
                    getInfoSuccess = False
                    browser.get(start_url)
                    print(f"\n\tFailure!")
                    continue
                
                # move to next permit, if getting info was unsuccessful
                if (getInfoSuccess == False):
                    getTurnSuccess = False
                    browser.get(start_url)
                    print(f"\n\tFailure!")
                    continue
                    

                # if the permit information was successfully retrieved
                if ((pageTurnSuccess) & (getInfoSuccess)):

                    # get the status of the relevant inspections
                    row = GetInspectionStatus(status, inspections, permit_number, relevant_inspections)

                    # get the most recent inspection
                    mostRecentInspection = GetMostRecentInspection(row, permit_number, relevant_inspections)

                    # write to the csv files
                    writerResult.writerow(mostRecentInspection)

                    if (keepRawInspectionStatus):
                        writerSuccess.writerow(row)
                        
                    print(f"\n\tSuccess!")
            
            # if failed to search, restart at home page and move to next iteration
            else:
                browser.get(start_url)
                print(f"\n\tFailure!")
                continue
        
        # if an error occurs
        except (ElementClickInterceptedException, StaleElementReferenceException, NoSuchElementException,
            SessionNotCreatedException, ElementNotVisibleException, TimeoutException,
            ElementNotInteractableException) as e:
            # print error message
            print(f"\n\tPermit Overall Exception {e.__class__.__name__}", end="")
            print(f"\n\tFailure!")
                        
            # close the files for writing
            if (keepRawInspectionStatus):
                CloseFiles([fileResult, fileSuccess])
            else:
                CloseFiles([fileResult])
        
            # move to next iteration
            continue
            
        # close the files for writing
        if (keepRawInspectionStatus):
            CloseFiles([fileResult, fileSuccess])
        else:
            CloseFiles([fileResult])
                

# Main function to call
# permit_use: list of integer permits to scrape data on; can also insert a single value
# relevant_inspections: list of relevant inspection titles; those provided by John are "Footer", "Slab", "Wall Sheathing", "Roof Sheathing", etc.
# overwrite_csv: specifies whether to overwrite the .csv files that result from previous runs
# filenameResult: name of the .csv file to output the results
# filenameSuccess: name of the .csv file to output the raw data to
# keepRawInspectionStatus: determines whether or not to record the raw data by storing it in filenameSuccess.csv
# numTryClick: specifies how many times that the program should try to perform a function on a web page before quitting
# numRetryPermit: specifies how many times to retry searching for a permit if failure occurred during the intial scraping
def GetData(permit_use, relevant_inspections, webDriverPath, overwrite_csv=False, filenameResult="PermitStatus", filenameSuccess="GetStatusSuccess", keepRawInspectionStatus=False, numTryClick=20, numRetryPermit=5): 
    
    # open files 
    if (keepRawInspectionStatus):
        # open files and initialize writers; use raw data file
        [fileResult, fileSuccess], [writerResult, writerSuccess] = OpenFiles(filenameResult=filenameResult, filenameSuccess=filenameSuccess, overwrite_csv=overwrite_csv)
        fileResult.close(); fileSuccess.close();
    else:
        # open files and initialize writers; don't use raw data file
        [fileResult], [writerResult] = OpenFiles(filenameResult=filenameResult, overwrite_csv=overwrite_csv)
        fileResult.close();

    
    
    # make sure specified filename contains .csv; otherwise add it
    if ".csv" not in filenameResult:
        filenameResult = filenameResult + ".csv"

    # get unused permits
    unused = GetUnusedPermits(filenameResult, permit_use)

    # create dict with keys as unused permits and value as number of times tried
    timesUnused = {}
    for per in unused:
        timesUnused[per] = 1
       
    # variable to keep track of start of web scraping permits
    start = True
    
    # initialize variable to store iteration
    it = 1

    # while there are still unused permits
    while ((len(timesUnused) > 0) & (len(unused) > 0) & (it <= numRetryPermit)):

        # on start, let user choose whether or not to overwrite the csv
        if (start == True):
            # try getting data for each permit
            ScrapeData(unused, relevant_inspections, webDriverPath, overwrite_csv, filenameResult, filenameSuccess, keepRawInspectionStatus, numTryClick)
            start = False
        # if not on start, then do not overwrite
        else:
            ScrapeData(unused, relevant_inspections, webDriverPath, False, filenameResult, filenameSuccess, keepRawInspectionStatus, numTryClick)

        # get the unused/unsuccessful permits to try to search for again
        unused = GetUnusedPermits(filenameResult, permit_use)

        # get rid of used permits from unused dictionary
        for per in timesUnused.keys():
            # get list of permits to remove from timesUnused
            listRemove = set()
            
            # add to times tried if the permit is still unused or has not yet failed 5 times to search
            if ((per in unused) & (timesUnused[per] < numRetryPermit)):
                timesUnused[per] = timesUnused[per] + 1
                
            # if the permit search is successful or has failed 5 times to search, 
            # remove it from the unused dictionary 
            else: 
                listRemove.add(per)
                
        # remove permits from timesUnused dict
        for per in listRemove.intersection(timesUnused.keys()):
            timesUnused.pop(per)
            
        # increase iteration
        it = it + 1

                