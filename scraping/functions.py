from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.common.action_chains import ActionChains




# ------------------------------        GENERAL FUNCTIONS        ------------------------------
def start_browser():
    '''
    Initializes the WebDriver and returns the driver instance.
    '''
    driver = webdriver.Edge()  
    return driver


def open_page(driver ,link):
    '''
    Load the given URL and wait until the page is fully loaded.
    If the page does not load within 10 seconds, an exception will be raised.
    '''
    driver.get(link)
    wait_for_page_load(driver)
    assert "No results found." not in driver.page_source


def wait_for_page_load(driver, timeout=10):
    '''
    Wait for the page to load within the given timeout period.
    If the page does not load in the specified time, an exception is raised.
    '''
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except Exception as e:
        print(f"Error while waiting for page load: {e}")



# ------------------------------        COUNTRY SPECIFIC FUNCTIONS        ------------------------------


def get_list_of_countries(driver):
    """Extracts all the links from the 'alphabetical-box' divs on the page."""
    countries_links = []
    
    try:
        alphabetical_boxes = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "alphabetical-box"))
        )
        
        for box in alphabetical_boxes:
            try:
                ul_element = box.find_element(By.TAG_NAME, "ul")
                
                li_elements = ul_element.find_elements(By.TAG_NAME, "li")
                
                for li in li_elements:
                    a_tag = li.find_element(By.TAG_NAME, "a")
                    link = a_tag.get_attribute("href")  
                    countries_links.append(link)  
                
            except NoSuchElementException:
                print("Warning: <ul> or <li> not found in an 'alphabetical-box', skipping...")
                continue
    
    except TimeoutException:
        print("Error: Timed out waiting for the alphabetical-box divs to appear.")
    
    return countries_links




# --------------------------------- SHAHZAD ------------------------------------

def get_life_expentency_data(driver):
    pass

def get_health_life_expectancy_data(driver):
    pass

def get_all_indicators(driver):
    pass


def get_indicator_data_for_group_A(driver):
    # group A example https://data.who.int/indicators/i/49AC786/77D059C?m49=004
    pass

def get_indicator_data_for_group_B(driver):
    # group B example https://data.who.int/indicators/i/CCCEBB2/217795A?m49=004
    pass






# --------------------------------- NAJAM ------------------------------------

def get_country_name(driver):
    pass

def get_current_health_expenditure(driver):
    pass

def get_who_region(driver):
    pass

def get_world_bank_income_level(driver):
    pass

def get_population_growth_rate(driver):
    pass

def get_leading_cause_of_death(driver):
    pass

def get_leading_cause_of_death(driver):
    pass

def get_leading_cause_of_under_5_mortality(driver):
    pass

def get_population_data(driver):
    pass

