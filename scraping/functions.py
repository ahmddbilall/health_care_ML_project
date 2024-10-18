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

def wait_for_page_load(driver, timeout=4):
    '''
    Wait for the page to load within the given timeout period.
    If the page does not load in the specified time, an exception is raised.
    '''
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except Exception as e:
        print(f"Error while waiting for page load: {e}")

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


# ------------------------------        COUNTRY SPECIFIC FUNCTIONS        ------------------------------




def get_group_A_indicators(driver):
    group_A_links = {}
    groupA_header = [
        "Number of new HIV infections", "Probability of dying from non-communicable diseases",
        "Suicide deaths", "Prevalence of hypertension", "Adult obesity", "Tobacco use",
        "Alcohol consumption", "Safely managed sanitation", "Fine particulate matter", "Financial hardship"
    ]

    section = 1
    for i in range(1, 5):
        xpath = f"//*[@id='main']/section/div/div[9]/div/div/div/div/ul/li[{i}]"
        b1 = driver.find_element(By.XPATH, xpath)

        b1.click()

        indicators = driver.find_elements(By.XPATH, f"/html/body/div[5]/main/section/div/div[9]/div/div/div/div/section[{section}]/div")

        for indicator in indicators:
            links = indicator.find_elements(By.TAG_NAME, 'a')  
            headers = indicator.find_elements(By.TAG_NAME, 'h2')

            filtered_links = [link.get_attribute('href') for link in links if link.get_attribute('href').startswith('https://data.who.int/indicators/')]

            if len(filtered_links) != len(headers):
                continue

            for idx, header in enumerate(headers):
                header_text = header.text.strip()

                if header_text in groupA_header:

                    href = filtered_links[idx]  
                    group_A_links[header_text] = href

        section += 1
    return group_A_links

def get_group_B_indicators(driver):
    group_B_links = {}
    groupB_header=["People living with tuberculosis (TB)","Malaria cases","Road traffic deaths","UHC index score",
                   "Births attended by skilled health personnel","Family planning","DTP3 immunization","MCV2 immunization",
                   "Interventions against NTDs","Density of doctors","Density of nurses","Density of pharmacists",
                   "Density of dentists","WASH development assistance"]

    section = 1
    for i in range(1, 5):
        xpath = f"//*[@id='main']/section/div/div[9]/div/div/div/div/ul/li[{i}]"
        b1 = driver.find_element(By.XPATH, xpath)

        b1.click()

        indicators = driver.find_elements(By.XPATH, f"/html/body/div[5]/main/section/div/div[9]/div/div/div/div/section[{section}]/div")

        for indicator in indicators:
            links = indicator.find_elements(By.TAG_NAME, 'a')  
            headers = indicator.find_elements(By.TAG_NAME, 'h2')

            filtered_links = [link.get_attribute('href') for link in links if link.get_attribute('href').startswith('https://data.who.int/indicators/')]

            if len(filtered_links) != len(headers):
                continue

            for idx, header in enumerate(headers):
                header_text = header.text.strip()

                if header_text in groupB_header:

                    href = filtered_links[idx]  
                    group_B_links[header_text] = href

        section += 1

    return group_B_links


# -- for following two functions only, return the a dictionary with the year as key and value as value. 
# return 24 values for each year          
def get_indicator_data_for_group_A(driver, url): 
   data = []
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

        b.click()
 

   return data

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

# ----------------------------------------------


def get_country_name(driver):
    name= driver.find_element(By.CLASS_NAME, "page-header__main-info")
    country_name=name.find_element(By.TAG_NAME,"h1")
    return country_name.text

def get_current_health_expenditure(driver):
    expen1=driver.find_element(By.TAG_NAME,"table")
    expen_rows=expen1.find_elements(By.TAG_NAME,"tr")
    expen2=expen_rows[1]
    ret_row=expen2.find_element(By.TAG_NAME,"td")
    return ret_row.text

def get_who_region(driver):
    expen1=driver.find_element(By.TAG_NAME,"table")
    expen_rows=expen1.find_elements(By.TAG_NAME,"tr")
    expen2=expen_rows[2]
    ret_row=expen2.find_element(By.TAG_NAME,"td")
    return ret_row.text


def get_world_bank_income_level(driver):
    expen1=driver.find_element(By.TAG_NAME,"table")
    expen_rows=expen1.find_elements(By.TAG_NAME,"tr")
    expen2=expen_rows[3]
    ret_row=expen2.find_element(By.TAG_NAME,"td")
    return ret_row.text

def get_population_growth_rate(driver):
            try:
                rate_1 = driver.find_element(By.XPATH, "//*[@id='main']/section/div/div[2]/div/div/div[2]/div/div/div[4]/div/p/span[1]")
                if rate_1.text.strip():
                    return rate_1.text
                else:
                    return None  
            except NoSuchElementException:
                return None

def get_population_data(driver):
     data_points = driver.find_elements(By.CSS_SELECTOR, 'text[data-testid="dataDotViz-line-point-alt-text"]')
     chart_data = []
     for point in data_points:
            year = point.get_attribute('data-test-time-dim')  # The year
            population = point.text.strip()  # The population value (e.g., "74.1m (projected)")
            chart_data.append((year, population))
        
     return chart_data


# -- for following two functions only, return the a dictionary with the year as key and value as value. 
# Only return values of total not for male and female          
def get_life_expentency_data(driver):
    print("Getting life expectancy data...")
    chart_element = driver.find_element(By.CSS_SELECTOR, '#life-expectancy-section > div > div:nth-child(1) > div > div')
    row_elements = chart_element.find_elements(By.CSS_SELECTOR, 'g[role="row"]')
    for each in row_elements:
        each_row = each.find_elements(By.CSS_SELECTOR, 'text[role="cell"]')
        for row in each_row:
            time_dim = row.get_attribute("data-test-time-dim")
            value = row.text
            if "Male" in value:
                value = "Male"
            elif "Female" in value:
                value = "Female"
            if "Total" in value:
                value = "Total"
            print(time_dim, value)
        print("_______________________________")

def get_health_life_expectancy_data(driver):
    print("Getting  health life expectancy data...")
    chart_element = driver.find_element(By.CSS_SELECTOR, '#healthy-life-expectancy-section > div > div:nth-child(1) > div > div')
    row_elements = chart_element.find_elements(By.CSS_SELECTOR, 'g[role="row"]')
    for each in row_elements:
        each_row = each.find_elements(By.CSS_SELECTOR, 'text[role="cell"]')
        for row in each_row:
            time_dim = row.get_attribute("data-test-time-dim")
            value = row.text
            if "Male" in value:
                value = "Male"
            elif "Female" in value:
                value = "Female"
            if "Total" in value:
                value = "Total"
            print(time_dim, value)
        print("_______________________________")
























# ----------- indicators

def HIV_infections(driver):
            try:
                rate_1 = driver.find_element(By.XPATH, "//*[@id='health-status-section']/div/div[1]/div/div/div[4]/div/p/span[1]")
                if rate_1.text.strip():
                    return rate_1.text
                else:
                    return None  
            except NoSuchElementException:
                return None
       

def TB_infections(driver):
            try:
                rate_1 = driver.find_element(By.XPATH, "//*[@id='health-status-section']/div/div[2]/div/div/div[4]/div/p/span[1]")
                if rate_1.text.strip():
                    return rate_1.text
                else:
                    return None  
            except NoSuchElementException:
                return None

def Malaria_cases(driver):
        try:
            rate_1 = driver.find_element(By.XPATH, "//*[@id='health-status-section']/div/div[3]/div/div/div[4]/div/p/span[1]")
            if rate_1.text.strip():
                return rate_1.text
            else:
                return None  
        except NoSuchElementException:
            return None

def N_com(driver):
        try:
            rate_1 = driver.find_element(By.XPATH, "//*[@id='health-status-section']/div/div[4]/div/div/div[4]/div/p/span[1]")
            if rate_1.text.strip():
                return rate_1.text
            else:
                return None  
        except NoSuchElementException:
            return None

def t_deaths(driver):
        try:
            rate_1 = driver.find_element(By.XPATH, "//*[@id='health-status-section']/div/div[5]/div/div/div[4]/div/p/span[1]")
            if rate_1.text.strip():
                return rate_1.text
            else:
                return None  
        except NoSuchElementException:
            return None
        
def s_deaths(driver):
        try:
            rate_1 = driver.find_element(By.XPATH, "//*[@id='health-status-section']/div/div[6]/div/div/div[4]/div/p/span[1]")
            if rate_1.text.strip():
                return rate_1.text
            else:
                return None  
        except NoSuchElementException:
            return None
        
def p_deaths(driver):
        try:
            rate_1 = driver.find_element(By.XPATH, "//*[@id='risk-factors-section']/div/div[1]/div/div/div[4]/div/p/span[1]")
            if rate_1.text.strip():
                return rate_1.text
            else:
                return None  
        except NoSuchElementException:
            return None    

def adult_obs(driver):
        try:
            rate_1 = driver.find_element(By.XPATH, "//*[@id='risk-factors-section']/div/div[2]/div/div/div[4]/div/p/span[1]")
            if rate_1.text.strip():
                return rate_1.text
            else:
                return None  
        except NoSuchElementException:
            return None 
                        
def tobaco_use(driver):
        try:
            rate_1 = driver.find_element(By.XPATH, "//*[@id='risk-factors-section']/div/div[3]/div/div/div[4]/div/p/span[1]")
            if rate_1.text.strip():
                return rate_1.text
            else:
                return None  
        except NoSuchElementException:
            return None 

def Alcohol_con(driver):
        try:
            rate_1 = driver.find_element(By.XPATH, "//*[@id='risk-factors-section']/div/div[4]/div/div/div[4]/div/p/span[1]")
            if rate_1.text.strip():
                return rate_1.text
            else:
                return None  
        except NoSuchElementException:
            return None    

