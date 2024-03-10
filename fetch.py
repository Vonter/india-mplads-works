from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import logging
import os
import tempfile
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("fetch.log"),
        logging.StreamHandler()
    ]
)

# Reset all dropdowns to default value
def reset_dropdowns():
    try:
        for dropdown_id in range(0, len(driver.find_elements(By.TAG_NAME, 'select'))):
            time.sleep(1)
            dropdown_element = driver.find_elements(By.TAG_NAME, 'select')[dropdown_id]
            select = Select(dropdown_element)
            select.select_by_index(0)
    except:
        logging.error("Failed to reset dropdowns")

    return True

# Restore dropdowns from selections
def restore_dropdowns(selections={}):
    try:
        for dropdown_id in selections.keys():
            time.sleep(1)
            dropdown_element = driver.find_element(By.ID, dropdown_id)
            select = Select(dropdown_element)
            select.select_by_visible_text(selections[dropdown_id])
    except:
        logging.error("Failed to restore dropdowns for selections {}".format(', '.join(selections.values())))

    return True

# Restore page state from selections
def restore_selections(selections={}):
    try:
        # Navigate to the URL
        driver.get(url)
        # Reset dropdowns
        reset_dropdowns()
        # Restore dropdowns
        restore_dropdowns(selections)
    except:
        logging.error("Failed to page state for selections {}".format(', '.join(selections.values())))

    return True

# Check if a selection has already been fetched
def is_fetched(selections={}):
    try:
        matching_files = [file for file in os.listdir("raw") if all(string in file for string in selections.values())]
        # If exact match has been found only
        if len(matching_files) == 1 and len(selections) <= 4:
            return True
        if len(matching_files) > 2 and len(selections) > 4:
            return True
    except:
        logging.error("Failed to check fetched status for selections {}".format(', '.join(selections.values())))

    return False

# Click a button and wait for page load
def click_button(button_id, wait_element_id):
    try:
        old_wait_element_text = driver.find_element(By.ID, wait_element_id).text
    except:
        old_wait_element_text = None

    # Click the button
    try:
        button = driver.find_element(By.ID, button_id)
        button.click()
        time.sleep(15)
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, wait_element_id))
        )
    except:
        logging.error("Failed to click button {}".format(button_id))

    # Wait for changes to reflect, after button click page reload
    try:
        if not "Excel" in button_id:
            while old_wait_element_text == driver.find_element(By.ID, wait_element_id).text:
                logging.info("Waiting for DOM element {} to change".format(wait_element_id))
                time.sleep(5)
            logging.info("DOM element {} changed to {}".format(wait_element_id, driver.find_element(By.ID, wait_element_id).text))
    except:
        logging.error("Failure while waiting for DOM element {} to change".format(wait_element_id))

    return True

# Fetch XLS for current selections
def fetch_page(selections={}, errorLevel=0):
    try:
        logging.info("Fetching XLS for {}".format(', '.join(selections.values())))
        # Search
        click_button("body_btnSearch", "body_lblFileName")
        # Fetch
        click_button("body_btnExcel", "body_lblDataDate")
        # Check if fetched
        if not is_fetched(selections):
            raise
    except:
        logging.error("Failed to fetch {}".format(', '.join(selections.values())))
        raise

    return True

# Check which options for given dropdown have already been fetched
def check_dropdown_options(dropdown_id, selections={}):
    try:
        # Locate relevant dropdown element
        element = driver.find_element(By.ID, dropdown_id)
        select = Select(element)
        options = select.options[1:]

        fetchedCheck = selections
        pendingOptions = []

        # Check each possible option for the dropdown
        for option in options:
            try:
                fetchedCheck[dropdown_id] = option.text
                if is_fetched(fetchedCheck):
                    logging.info("Already fetched, skipping {}".format(', '.join(fetchedCheck.values())))
                else:
                    pendingOptions.append(option.text)
            except:
                logging.error("Failed to check if already fetched: {}".format(', '.join(selections.values())))
        return pendingOptions
    except:
        logging.error("Failed to check dropdown options: {}".format(dropdown_id))

# Recursively loop over required dropdowns
def loop_over_dropdowns(dropdown_ids=None, selections={}, errorLevel=0):

    # Check if any dropdowns are remaining
    if dropdown_ids[0]:
        dropdown_id = dropdown_ids[0]
        dropdown_ids = dropdown_ids[1:]
    else:
        try:
            fetch_page(selections, errorLevel)
        except:
            restore_selections(selections)
            loop_over_dropdowns([additionalDropdownList[errorLevel]] + dropdown_ids, selections, errorLevel + 1)
        return True

    # Wait for selections to settle
    time.sleep(5)

    # Check which dropdown options are remaining for fetch
    pendingOptions = check_dropdown_options(dropdown_id, selections)

    # Iterate over options for given dropdown which are pending to check
    for option in pendingOptions:
        try:
            time.sleep(1)
            element = driver.find_element(By.ID, dropdown_id)
            select = Select(element)
            select.select_by_visible_text(option)

            selections[dropdown_id] = option
            logging.info("Selections: {}".format(', '.join(selections.values())))

            loop_over_dropdowns(dropdown_ids, selections, errorLevel)
            time.sleep(1)
        except:
            logging.error("Failed option select for dropdown {} and value {} (current selections: {})".format(dropdown_id, option, ', '.join(selections.values())))

    # Reset given dropdown to default value
    try:
        dropdown_element = driver.find_element(By.ID, dropdown_id)
        select = Select(dropdown_element)
        select.select_by_index(0)
        del(selections[dropdown_id])
        time.sleep(1)
    except:
        logging.error("Failed to reset dropdown {} to default value".format(dropdown_id))

# Define required variables
url = 'http://164.100.68.116/mpladssbi/MembersOfParlament/Reports/WorkByLocation.aspx'
baseDropdownList = ['body_ddlHouse', 'body_ddlTenure', None]
additionalDropdownList = ['body_ddlState', 'body_ddlLocation', 'body_ddlStatus', None]

# Create a temporary directory for the user data
temp_dir = tempfile.TemporaryDirectory()
# Initialize the service
service = Service(executable_path='/usr/bin/geckodriver')
# Set the download preferences
options = Options()
options.set_preference("browser.download.folderList",  2)  # Use custom download directory
options.set_preference("browser.download.manager.showWhenStarting", False)  # Don't show download manager
options.set_preference("browser.download.dir", os.path.join(os.getcwd(), "raw"))  # Set custom download directory
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream,application/vnd.ms-excel")  # Set MIME types to download automatically
# Initialize the WebDriver with the specified options
driver = webdriver.Firefox(service=service, options=options)

# Load main URL
driver.get(url)
# Recursively loop over dropdowns and fetch results
loop_over_dropdowns(baseDropdownList)
# Log on completion
logging.info("Completed fetching")

# Close the WebDriver
driver.quit()
# Clean up the temporary directory
temp_dir.cleanup()
