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
    groupA_header = [
        "Number of new HIV infections", "Probability of dying from non-communicable diseases",
        "Suicide deaths", "Prevalence of hypertension", "Adult obesity", "Tobacco use",
        "Alcohol consumption", "Safely managed sanitation", "Fine particulate matter", "Financial hardship"
    ]

    section = 1
    for i in range(1, 5):
        xpath = f"//*[@id='main']/section/div/div[9]/div/div/div/div/ul/li[{i}]"
        b1 = driver.find_element(By.XPATH, xpath)

        print("Button: ", b1.text)
        b1.click()
        time.sleep(1)

        indicators = driver.find_elements(By.XPATH, f"/html/body/div[5]/main/section/div/div[9]/div/div/div/div/section[{section}]/div")

        for indicator in indicators:
            links = indicator.find_elements(By.TAG_NAME, 'a')  
            headers = indicator.find_elements(By.TAG_NAME, 'h2')

            filtered_links = [link.get_attribute('href') for link in links if link.get_attribute('href').startswith('https://data.who.int/indicators/')]

            if len(filtered_links) != len(headers):
                print("Warning: Mismatch between the number of links and headers!")
                continue

            for idx, header in enumerate(headers):
                header_text = header.text.strip()

                if header_text in groupA_header:
                    print("\nHeader Matched: ", header_text)

                    href = filtered_links[idx]  # Use idx to match the header and link
                    group_A_links.append(href)
                    print("Added Link: ", href)
                else:
                    print(f"Skipped Header: {header_text}")

        section += 1
        print("-----------------")

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

        for indicator in indicators:
            links = indicator.find_elements(By.TAG_NAME, 'a')  
            headers = indicator.find_elements(By.TAG_NAME, 'h2')

            filtered_links = [link.get_attribute('href') for link in links if link.get_attribute('href').startswith('https://data.who.int/indicators/')]

            if len(filtered_links) != len(headers):
                print("Warning: Mismatch between the number of links and headers!")
                continue

            for idx, header in enumerate(headers):
                header_text = header.text.strip()

                if header_text in groupB_header:
                    print("\nHeader Matched: ", header_text)

                    href = filtered_links[idx]  # Use idx to match the header and link
                    group_B_links.append(href)
                    print("Added Link: ", href)
                else:
                    print(f"Skipped Header: {header_text}")

        section += 1
        print("-----------------")

    return group_B_links






def get_indicator_data_for_group_A(driver, url): 
   data = []
   print("Starting to fetch")
   

   for i in url:
    open_page(driver,i) 
    
    
    
    b=driver.find_element(By.XPATH, '/html/body/main/section/div[2]/div[3]/div[1]/div[1]/div/div/div/div/div/div/div[1]/div[2]/div/div[2]/label/span[2]')
    b.click()
    
    options = b.find_elements(By.CSS_SELECTOR, 'option')  

    
    for option in options:
        option.click()
        print(f'Selected: {option.text}')

        span_element = driver.find_element(By.CSS_SELECTOR, 'tr.border-bottom.svelte-193mdey.selected td[data-testid="dataDotViz-collapsibleTable-data-point"] span.svelte-193mdey')

        print(span_element.text)
        data.append(span_element.text)
        #time.sleep(1)  

        b.click()
 

   return data




# def get_indicator_data_for_group_B(driver):
#     # group B example https://data.who.int/indicators/i/CCCEBB2/217795A?m49=004
#     pass


def get_indicator_data_for_group_B(driver, urls):
    data = []
    print("Starting to fetch")
    for url in urls:
        open_page(driver, url)
        time.sleep(2)
        
        try: 
            parent_css = '#data-visualization > div > div > div.col-lg-8 > div:nth-child(2) > div > div > div.dataDotViz-ChartRenderer-chartContainer > div > svg > g > g:nth-child(6)'
            parent_element = driver.find_element(By.CSS_SELECTOR, parent_css)
            
            child_css = '#data-visualization > div > div > div.col-lg-8 > div:nth-child(2) > div > div > div.dataDotViz-ChartRenderer-chartContainer > div > svg > g > g:nth-child(6) > use.border.svelte-oihrhl.selected'
            aria_pressed_elements = parent_element.find_elements(By.CSS_SELECTOR, child_css)
            time.sleep(1)
            
            for element in aria_pressed_elements:
                aria_label = element.get_attribute('aria-label')
                print(f'Aria-label: {aria_label}')
                data.append(aria_label)

        except Exception as e:
            print(f"An error occurred: {e}")

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