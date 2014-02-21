from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from collections import OrderedDict
import time
import csv
import re
import ConfigParser
import datetime
import sys
import os

CONFIG_FILE_NAME = os.path.dirname(os.path.realpath(__file__)) + '/census_data_scraper.cfg'
SYSCONFIG_FILE_NAME = os.path.dirname(os.path.realpath(__file__)) + '/census_data_scraper.syscfg'

## Parse the config file
config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE_NAME)

if config.get('SEARCH', 'RURAL') == '1':
    optionRural = True
else:
    optionRural = False
optionState = config.get('SEARCH', 'STATE')
optionDistrict = config.get('SEARCH', 'DISTRICT')
optionSubDistrictList = config.get('SEARCH', 'SUBDISTRICT').split(',')

## Parse the system config file
sysconfig = ConfigParser.ConfigParser()
sysconfig.read(SYSCONFIG_FILE_NAME)

PHANTOMJS_PATH = sysconfig.get('PHANTOMJS', 'PATH')

regex = re.compile('^(.+[0-9a-zA-Z)])\s*\(\s*([0-9]+)\s*\)\s*$', re.IGNORECASE)
regexSubstitute = '\\1|\\2'

## Function to parse a string of format: 'name_of_place (code_of_place)' into a list ['name_of_place', 'code_of_place']
def listCodeDescription(s):
    return regex.sub(regexSubstitute, s).split('|')

## Function to print timestamp with message on screen
def logWithDateTime(s):
    print datetime.datetime.now(), ': ', s

## Recursive function that walks across a list of dropdown ids
## First it starts looping though all instances of the first id
## Within this loop it starts another inner loop through all instances of the second id
## Whenever it reaches an end condition i.e. no ids further down the list, it gets ready to parse data
def SearchSelection(idList, currentSearchAt):
    if not idList:
        ParseHTML(currentSearchAt)
        return
    dictionary = OrderedDict()
    dropDownID = idList[0]
    searchByOption = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="%s"]/option[@value = "0"]' % dropDownID)))
    logWithDateTime("Got response...")
    for option in browser.find_elements_by_xpath('//*[@id="%s"]/option' % dropDownID)[1:]:
        dictionary[option.get_attribute('value')] = option.text
    for optionValue in dictionary:
        searchByElement = browser.find_element_by_id(dropDownID)
        selectByElement = Select(searchByElement)
        selectByElement.select_by_value(optionValue)
        logWithDateTime("Searching under " + dictionary[optionValue])
        SearchSelection(idList[1:], dictionary[optionValue])

## Function to submit the form and parse data into a list
def ParseHTML(currentSearchAt):
    submitButton = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="btn_submit"]')))
    submitButton.click()
    logWithDateTime("Submitted form, waiting for response...")
    ## Parse details
    checkSubmitted = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="lblvillage"][text() = "%s"]' % currentSearchAt)))
    populationData = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="gvPopulation"]/tbody')))
    logWithDateTime("Ready to parse...")
    row = []
    row.extend(listCodeDescription(browser.find_element_by_xpath('//*[@id="lblstatename"]').text))
    row.extend(listCodeDescription(browser.find_element_by_xpath('//*[@id="lbldistname"]').text))
    row.extend(listCodeDescription(browser.find_element_by_xpath('//*[@id="lblsubdist"]').text))
    if optionRural:
        row.extend(listCodeDescription(browser.find_element_by_xpath('//*[@id="lblvillage"]').text))
    else:
        row.extend(listCodeDescription(browser.find_element_by_xpath('//*[@id="lbltown"]').text))
        row.extend(listCodeDescription(browser.find_element_by_xpath('//*[@id="lblwardname"]').text))
    row.extend(listCodeDescription(browser.find_element_by_xpath('//*[@id = "Label5"]').text))
    for tr in populationData.find_elements_by_tag_name('tr')[1:]:
        for td in tr.find_elements_by_tag_name('td')[1:]:
            row.append(td.text)
    data.append(row)
    logWithDateTime("Parsing finished.")

## Construct the header row
header = ['State Name', 'State Code', 'District Name', 'District Code', 'Sub-District Name', 'Sub-District Code', 'Village Name', 'Village Code', 'No. Of HouseHold', 'Total Population', 'Male Population', 'Female Population',
          'In the age group 0-6 years', 'In the age group 0-6 years Male', 'In the age group 0-6 years Female', 'Scheduled Castes (SC)', 'Scheduled Castes (SC) Male', 'Scheduled Castes (SC) Female',
          'Scheduled Tribes (ST)', 'Scheduled Tribes (ST) Male', 'Scheduled Tribes (ST) Female', 'Literates', 'Literates Male', 'Literates Female', 'Illiterate', 'Illiterate Male', 'Illiterate Female',
          'Total Worker', 'Total Worker Male', 'Total Worker Female', 'Main Worker', 'Main Worker Male', 'Main Worker Female', 'Main Worker - Cultivator', 'Main Worker - Cultivator Male',
          'Main Worker - Cultivator Female', 'Main Worker - Agricultural Labourers', 'Main Worker - Agricultural Labourers Male', 'Main Worker - Agricultural Labourers Female', 'Main Worker - Household Industries',
          'Main Worker - Household Industries Male', 'Main Worker - Household Industries Female', 'Main Worker - Other', 'Main Worker - Other Male', 'Main Worker - Other Female', 'Marginal Worker',
          'Marginal Worker Male', 'Marginal Worker Female', 'Marginal Worker - Cultivator', 'Marginal Worker - Cultivator Male', 'Marginal Worker - Cultivator Female', 'Marginal Worker - Agriculture Labourers',
          'Marginal Worker - Agriculture Labourers Male', 'Marginal Worker - Agriculture Labourers Female', 'Marginal Worker - Household Industries', 'Marginal Worker - Household Industries Male',
          'Marginal Worker - Household Industries Female', 'Marginal Workers - Other', 'Marginal Workers - Other Male', 'Marginal Workers - Other Female', 'Marginal Worker (3-6 Months)',
          'Marginal Worker (3-6 Months) Male', 'Marginal Worker (3-6 Months) Female', 'Marginal Worker - Cultivator (3-6 Months)', 'Marginal Worker - Cultivator (3-6 Months) Male',
          'Marginal Worker - Cultivator (3-6 Months) Female', 'Marginal Worker - Cultivator (3-6 Months)', 'Marginal Worker - Cultivator (3-6 Months) Male', 'Marginal Worker - Cultivator (3-6 Months) Female',
          'Marginal Worker - Agriculture Labourers (3-6 Months)', 'Marginal Worker - Agriculture Labourers (3-6 Months) Male', 'Marginal Worker - Agriculture Labourers (3-6 Months) Female',
          'Marginal Worker - Household Industries (3-6 Months)', 'Marginal Worker - Household Industries (3-6 Months) Male', 'Marginal Worker - Household Industries (3-6 Months) Female',
          'Marginal Worker - Other (3-6 Months)', 'Marginal Worker - Other (3-6 Months) Male', 'Marginal Worker - Other (3-6 Months) Female', 'Marginal Worker - Cultivator (0-3 Months)',
          'Marginal Worker - Cultivator (0-3 Months) Male', 'Marginal Worker - Cultivator (0-3 Months) Female', 'Marginal Worker - Agriculture Labourers (0-3 Months)',
          'Marginal Worker - Agriculture Labourers (0-3 Months) Male', 'Marginal Worker - Agriculture Labourers (0-3 Months) Female', 'Marginal Worker - Household Industries (0-3 Months)',
          'Marginal Worker - Household Industries (0-3 Months) Male', 'Marginal Worker - Household Industries (0-3 Months) Female', 'Marginal Worker - Other Workers (0-3 Months)',
          'Marginal Worker - Other Workers (0-3 Months) Male', 'Marginal Worker - Other Workers (0-3 Months) Female', 'Non Worker', 'Non Worker Male', 'Non Worker Female']

if not optionRural:
    header = header[:6] + ['Town Name', 'Town Code', 'Ward Name', 'Ward Code'] + header[8:]

## Start browser
logWithDateTime("Instantiating browser...")
browser = webdriver.PhantomJS(executable_path=PHANTOMJS_PATH)
##browser = webdriver.Firefox()

## Get the search page
logWithDateTime("Navigating to the census results page...")
browser.get('http://www.censusindia.gov.in/pca/final_pca.aspx')

## Create generic wait object since the page loads dynamically
## If an element fails to load in 300 seconds, the script will error out
wait = WebDriverWait(browser, 300)

logWithDateTime("Setting search options...")

## Rural or Urban search?
if optionRural:
	rbRuralUrban = browser.find_element_by_id('rdb_Rural')
	sRuralUrban = 'Rural'
else:
	rbRuralUrban = browser.find_element_by_id('rdb_urban')
	sRuralUrban = 'Urban'

rbRuralUrban.click()

## Set state code from config file
searchStateOption = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="Drp_state"]/option[@value = "%s"]' % optionState)))
searchState = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Drp_state"]')))
selectState = Select(searchState)
selectState.select_by_value(optionState)

## Set district code from config file
searchDistrictOption = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="Drp_district"]/option[@value = "%s"]' % optionDistrict)))
searchByDistrict = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Drp_district"]')))
selectDistrict = Select(searchByDistrict)
selectDistrict.select_by_value(optionDistrict)

## For Rural search, search through villages
## For urban search, search through towns and for each town, search through wards
if optionRural:
    searchByList = ['Drp_Village']
else:
    searchByList = ['Drp_Town', 'Drp_Ward']

for optionSubDistrict in optionSubDistrictList:	
	## Set sub-district code from config file
	logWithDateTime("Selecting subdistrict " + optionSubDistrict)
	searchSubDistrictOption = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="Drp_subDistrict"]/option[@value = "%s"]' % optionSubDistrict)))
	searchBySubDistrict = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Drp_subDistrict"]')))
	selectBySubDistrict = Select(searchBySubDistrict)
	selectBySubDistrict.select_by_value(optionSubDistrict)
	
	## Initialize the main storage array
	data = []
	data.append(header)
	
	## Get cracking!
        try:
	    SearchSelection(searchByList, optionSubDistrict)
	except TimeoutException:
	    logWithDateTime("Timed out!")
	    sys.exit(1)
	
	if len(data)==1:
	    logWithDateTime("No data found!")
	    continue
	
	## Output file name will be of the format: "<State Name> <District Name> <Sub-District Name>.csv"
	logWithDateTime("Starting to write data into file...")
	fname = data[1][1] + ' ' + data[1][3] + ' ' + data[1][5] + ' ' + sRuralUrban + ' ' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.csv'
	
	## Write our data into a csv file
	with open(fname, 'w') as fp:
	    w = csv.writer(fp, delimiter=',')
	    w.writerows(data)
	
	logWithDateTime("Done for this subdistrict!")

logWithDateTime("All done!")
