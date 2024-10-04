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




def get_group_A_indicators(driver):
    group_A_links = []
    groupA_header = ["Number of new HIV infections", "Probability of dying from non-communicable diseases",
                     "Suicide deaths", "Prevalence of hypertension", "Adult obesity", "Tobacco use",
                     "Alcohol consumption", "Safely managed sanitation", "Fine particulate matter", "Financial hardship"]

    section = 1
    for i in range(1, 5):
        xpath = f"//*[@id='main']/section/div/div[9]/div/div/div/div/ul/li[{i}]"
        b1 = driver.find_element(By.XPATH, xpath)

        print("Button: ", b1.text)
        b1.click()
        time.sleep(1)

        indicators = driver.find_elements(By.XPATH, f"/html/body/div[5]/main/section/div/div[9]/div/div/div/div/section[{section}]/div")

        for i in indicators:
            links = i.find_elements(By.TAG_NAME, 'a')  # Get links
            headers = i.find_elements(By.TAG_NAME, 'h2')  # Get headers
            # print("headers successfully extracted.")

            h_count = 0
            for header in headers:
                header_text = header.text.strip()

                l_count = 0
                if header_text in groupA_header:
                    print("\nHeader: ", header_text)

                    for link in links:
                        if l_count == h_count:
                            href = link.get_attribute('href')
                            group_A_links.append(href)
                            print("Link: ", href)
                            l_count += 1
                        else:
                            l_count += 1
                else:
                    h_count += 1

        section += 1
        print("-----------------")
        continue

    return group_A_links





def get_group_B_indicators(driver):
    group_B_links = []
    groupB_header=["People living with tuberculosis (TB)","Malaria cases","Road traffic deaths","UHC index score",
                   "Births attended by skilled health personnel","Family planning","DTP3 immunization","MCV2 immunization",
                   "Interventions against NTDs","Density of doctors","Density of nurses","Density of pharmacists",
                   "Density of dentists","WASH development assistance"]

    section = 1
    for i in range(1, 5):
        xpath = f"//*[@id='main']/section/div/div[9]/div/div/div/div/ul/li[{i}]"
        b1 = driver.find_element(By.XPATH, xpath)

        print("Button: ", b1.text)
        b1.click()
        time.sleep(1)

        indicators = driver.find_elements(By.XPATH, f"/html/body/div[5]/main/section/div/div[9]/div/div/div/div/section[{section}]/div")

        for i in indicators:
            links = i.find_elements(By.TAG_NAME, 'a')  # Get links
            headers = i.find_elements(By.TAG_NAME, 'h2')  # Get headers
            # print("headers successfully extracted.")

            h_count = 0
            for header in headers:
                header_text = header.text.strip()

                l_count = 0
                if header_text in groupB_header:
                    print("\nHeader: ", header_text)
                    
                    for link in links:
                        if l_count == h_count:
                            href = link.get_attribute('href')
                            group_B_links.append(href)
                            print("Link: ", href)
                            l_count += 1
                        else:
                            l_count += 1
                else:
                    h_count += 1

        section += 1
        print("-----------------")
        continue

    return group_B_links




# def get_indicator_data_for_group_A(driver):
#     # group A example https://data.who.int/indicators/i/49AC786/77D059C?m49=004
#     pass
def get_indicator_data_for_group_A(driver, url):
    driver.get(url)
    
    data = []
    
    # Check the actual row class for the data.
    rows = driver.find_elements(By.CSS_SELECTOR, '.data-row')  # Update based on actual page structure
    
    for row in rows:
        try:
            year = row.find_element(By.CSS_SELECTOR, '.year').text  # Ensure the correct class is used
            count = row.find_element(By.CSS_SELECTOR, '.count').text  # Ensure the correct class is used
            data.append({'year': year, 'count': count})
        except Exception as e:
            print(f"Error extracting row: {e}")
    
    return data



# def get_indicator_data_for_group_B(driver):
#     # group B example https://data.who.int/indicators/i/CCCEBB2/217795A?m49=004
#     pass

def get_indicator_data_for_group_B(driver, url):
    driver.get(url)
    
    data = []
    
    # Check the correct classes for graph year and value.
    years = driver.find_elements(By.CSS_SELECTOR, '.graph-year')  # Update based on actual page
    values = driver.find_elements(By.CSS_SELECTOR, '.graph-value')  # Update based on actual page
    
    if len(years) == len(values):
        for i in range(len(years)):
            try:
                year = years[i].text
                value = values[i].text
                data.append({'year': year, 'value': value})
            except Exception as e:
                print(f"Error extracting graph data: {e}")
    else:
        print("Mismatch between years and values.")
    
    return data





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

def get_life_expentency_data(driver):
    pass

def get_health_life_expectancy_data(driver):
    pass