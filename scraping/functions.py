from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import re

import random
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
def get_indicator_data_for_group_A(driver, urls):
    all_data = {}  # Dictionary to store data for each indicator
    
    for name, url in urls.items():
        print(f"Fetching data for: {name}")
        driver.get(url)  # Open the page for each indicator
        
        time.sleep(2)  # Wait for page to load (increase if needed)

        try:
            # Click to open the dropdown
            dropdown = driver.find_element(By.XPATH, '/html/body/main/section/div[2]/div[3]/div[1]/div[1]/div/div/div/div/div/div/div[1]/div[2]/div/div[2]/label/span[2]')
            dropdown.click()

            # Find all options in the dropdown
            options = dropdown.find_elements(By.CSS_SELECTOR, 'option')
            indicator_data = []  # To store the data for each option

            for option in options:
                option.click()  # Select the option
                print(f"Selected: {option.text}")
                
                time.sleep(1)  # Allow data to load after selection

                try:
                    # Extract the data point after selection
                    span_element = driver.find_element(By.CSS_SELECTOR, 'tr.border-bottom.svelte-193mdey.selected td[data-testid="dataDotViz-collapsibleTable-data-point"] span.svelte-193mdey')
                    data_point = span_element.text
                    print(f"Data Point: {data_point}")
                    indicator_data.append({option.text: data_point})  # Append option and data to list
                    
                except Exception as e:
                    print(f"Error fetching data for {option.text}: {str(e)}")
            
            all_data[name] = indicator_data  # Store the collected data for the current indicator

        except Exception as e:
            print(f"Error on URL {url}: {str(e)}")

    return all_data
def get_indicator_data_for_group_B(driver, urls):
    data = {}  # Dictionary to store data for each indicator
    print("Starting to fetch data...")

    for name, url in urls.items():  # Iterate over the dictionary
        open_page(driver, url)  # Open the page for each URL
        time.sleep(2)  # Wait for the page to load
        
        try:
            # Locate the parent element containing the chart data
            parent_css = '#data-visualization > div > div > div.col-lg-8 > div:nth-child(2) > div > div > div.dataDotViz-ChartRenderer-chartContainer > div > svg > g > g:nth-child(6)'
            parent_element = driver.find_element(By.CSS_SELECTOR, parent_css)
            
            # Find child elements with aria-labels
            child_css = '#data-visualization > div > div > div.col-lg-8 > div:nth-child(2) > div > div > div.dataDotViz-ChartRenderer-chartContainer > div > svg > g > g:nth-child(6) > use.border.svelte-oihrhl.selected'
            aria_pressed_elements = parent_element.find_elements(By.CSS_SELECTOR, child_css)
            time.sleep(1)  # Allow time for elements to be found
            
            # Collect aria-labels for the current indicator
            aria_labels = []
            for element in aria_pressed_elements:
                aria_label = element.get_attribute('aria-label')
                aria_labels.append(aria_label)

            # Store the collected data for the current indicator
            data[name] = aria_labels

        except Exception as e:
            print(f"An error occurred while fetching data for {name}: {e}")

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
def get_life_expectancy_data(driver):
    print("Getting life expectancy data...")
    life_expectancy_data = []

    try:
        # Attempt to find the element and extract the data
        driver.find_element(By.CSS_SELECTOR, '#tab-life-expectancy-section').click()
        chart_element = driver.find_element(By.CSS_SELECTOR, '#life-expectancy-section > div > div:nth-child(1) > div > div')
        row_elements = chart_element.find_elements(By.CSS_SELECTOR, 'g[role="row"]')
        
        for each in row_elements:
            row_data = {}
            each_row = each.find_elements(By.CSS_SELECTOR, 'text[role="cell"]')
            
            for row in each_row:
                time_dim = row.get_attribute("data-test-time-dim")
                value = row.text
                
                # Clean the value to ensure correct representation
                if "Male" in value:
                    value = "Male"
                elif "Female" in value:
                    value = "Female"
                elif "Total" in value:
                    value = "Total"
                
                # Store the time_dim and value in row_data
                row_data[time_dim] = value
            
            # Append the row data to the list
            life_expectancy_data.append(row_data)
    
    except Exception as e:
        # Fallback in case of any exception (element not found or other issues)
        print(f"An error occurred: {e}")
        # Provide dummy values
        dummy_data = {
            "time_dim": "Year",
            "Gender": "Unknown",
            "Life Expectancy": "N/A"
        }
        life_expectancy_data.append(dummy_data)

    # Return the list of dictionaries containing the data (or dummy data)
    return life_expectancy_data


def get_health_life_expectancy_data(driver):
    print("Getting health life expectancy data...")
    health_life_expectancy_data = []

    try:
        # Attempt to find the element and extract the data
        driver.find_element(By.CSS_SELECTOR, '#tab-healthy-life-expectancy-section').click()
        chart_element = driver.find_element(By.CSS_SELECTOR, '#healthy-life-expectancy-section > div > div:nth-child(1) > div > div')
        row_elements = chart_element.find_elements(By.CSS_SELECTOR, 'g[role="row"]')
        
        for each in row_elements:
            row_data = {}
            each_row = each.find_elements(By.CSS_SELECTOR, 'text[role="cell"]')
            
            for row in each_row:
                time_dim = row.get_attribute("data-test-time-dim")
                value = row.text
                
                # Clean the value to ensure correct representation
                if "Male" in value:
                    value = "Male"
                elif "Female" in value:
                    value = "Female"
                elif "Total" in value:
                    value = "Total"
                
                # Store the time_dim and value in row_data
                row_data[time_dim] = value
            
            # Append the row data to the list
            health_life_expectancy_data.append(row_data)
    
    except Exception as e:
        # Fallback in case of any exception (element not found or other issues)
        print(f"An error occurred: {e}")
        # Provide dummy values
        dummy_data = {
            "time_dim": "Year",
            "Gender": "Unknown",
            "Life Expectancy": "N/A"
        }
        health_life_expectancy_data.append(dummy_data)

    # Return the list of dictionaries containing the data (or dummy data)
    return health_life_expectancy_data

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

def flatten_data(data):
    flat_data = []
    
    # Unpack country information
    country_info = {
        'Country': data['Country'],
        'Current Health Expenditure': data['Current Health Expenditure'],
        'WHO Region': data['WHO Region'],
        'World Bank Income Level': data['World Bank Income Level'],
        'Population Growth Rate': data['Population Growth Rate'],
        'Life Expectancy': {},
        'Health Expenditure': {},
        'Group A': {}
    }
    
    # Process Life Expectancy
    for record in data['Life Expectancy']:
        gender = record['None']
        for year, value in record.items():
            if year != 'None':
                country_info['Life Expectancy'][f"{gender}_{year}"] = value
    
    # Process Health Expenditure
    for record in data['Health Expenditure']:
        gender = record['None']
        for year, value in record.items():
            if year != 'None':
                country_info['Health Expenditure'][f"{gender}_{year}"] = value

    # Process Group A statistics
    for key, value in data['Group A'].items():
        for record in value:
            year = list(record.keys())[0]
            country_info['Group A'][f"{key}_{year}"] = record[year]
    
    flat_data.append(country_info)
    return pd.DataFrame(flat_data)

def extract_numerical(value):
    """Extract numerical values from a string, including commas and decimals."""
    num = re.findall(r"[\d,\.]+", value)
    if num:
        return ''.join(num).replace(',', '')  # Remove commas for numerical consistency
    return None

def create_health_dataframe(diction):
    """Function to process the dictionary and return a DataFrame."""
    new_rows = []
    
    # Process 'Life Expectancy'
    for each in diction.get('Life Expectancy', []):
        if each:
            gender = each.get(None)  # Gender extraction
            for year, value in each.items():
                if year is not None:
                    new_row = {
                        'Country': diction['Country'],
                        'Current Health Expenditure': diction['Current Health Expenditure'],
                        'WHO Region': diction['WHO Region'],
                        'Population Growth Rate': diction['Population Growth Rate'],
                        'Gender': gender,
                        'Year': year,
                        'Life Expectancy': value
                    }
                    new_rows.append(new_row)

    # Process 'Health Expenditure'
    for each in diction.get('Health Expenditure', []):
        if each:
            gender = each.get(None)  # Gender extraction
            for year, value in each.items():
                if year is not None:
                    new_row = {
                        'Country': diction['Country'],
                        'Current Health Expenditure': diction['Current Health Expenditure'],
                        'WHO Region': diction['WHO Region'],
                        'Population Growth Rate': diction['Population Growth Rate'],
                        'Gender': gender,
                        'Year': year,
                        'Health Expenditure': value
                    }
                    new_rows.append(new_row)

    # Process 'Group A'
    for each, value in diction.get('Group A', {}).items():
        if each:
            for i in value:  # Assuming 'value' is a list of dictionaries
                for year, k in i.items():
                    new_row = {
                        'Country': diction['Country'],
                        'Current Health Expenditure': diction['Current Health Expenditure'],
                        'WHO Region': diction['WHO Region'],
                        'World Bank Income Level': diction['World Bank Income Level'],
                        'Population Growth Rate': diction['Population Growth Rate'],
                        'Year': year,
                        each: k  # Each key from Group A and its respective value
                    }
                    new_rows.append(new_row)

    # Process 'Group B'
    for each, value in diction.get('Group B', {}).items():
        if each:
            # Check if 'value' is a list or string
            if isinstance(value, list):
                numeric_values = [extract_numerical(v) for v in value if isinstance(v, str)]
            else:
                numeric_values = extract_numerical(value)

            # Create the new row
            new_row = {
                'Country': diction['Country'],
                'Current Health Expenditure': diction['Current Health Expenditure'],
                'WHO Region': diction['WHO Region'],
                'World Bank Income Level': diction['World Bank Income Level'],
                'Population Growth Rate': diction['Population Growth Rate'],
                each: numeric_values
            }
            new_rows.append(new_row)
    
    # Convert the list of rows to a DataFrame
    df = pd.DataFrame(new_rows)
    
    return df


def population_data_mapped(driver):
        data=get_population_data(driver)
        population_trend_mapped={}
        universal_health_trend_mapped={}
        for each in data:
            if '[' in each[1] and each[0]<='2024':
                universal_health_trend_mapped[each[0]]=each[1]
            elif each[0]<='2024':
                population_trend_mapped[each[0]]=each[1]
        target_years = list(map(str, range(2000, 2025)))
        for year in target_years:
            if year not in population_trend_mapped:
                population_trend_mapped[year] = None
            if year not in universal_health_trend_mapped:
                universal_health_trend_mapped[year]=None
        population_trend_mapped = dict(sorted(population_trend_mapped.items()))
        universal_health_trend_mapped=dict(sorted(universal_health_trend_mapped.items()))
        return population_trend_mapped,universal_health_trend_mapped

def life_expectency_mapped(driver):
        life_expectency_data = get_life_expectancy_data(driver)
        male_life_expectency={}
        female_life_expectency={}
        overall_life_expectency={}
        for each,value in life_expectency_data[1].items():
            if each is not None:
                male_life_expectency[each]=value
        for each,value in life_expectency_data[2].items():
            if each is not None:
                female_life_expectency[each]=value
        for each,value in life_expectency_data[3].items():
            if each is not None:
                overall_life_expectency[each]=value
        target_years = list(map(str, range(2000, 2025)))
        for year in target_years:
            if year not in male_life_expectency:
                male_life_expectency[year]=None
            if year not in female_life_expectency:
                female_life_expectency[year]=None
            if year not in overall_life_expectency:
                overall_life_expectency[each]=None
        male_life_expectency=dict(sorted(male_life_expectency.items()))
        female_life_expectency=dict(sorted(female_life_expectency.items()))
        overall_life_expectency=dict(sorted(overall_life_expectency.items()))
        return male_life_expectency,female_life_expectency,overall_life_expectency

def health_expectancy_mapped(driver):
    health_expectancy_data = get_health_life_expectancy_data(driver)
    
    male_health_expectancy = {}
    female_health_expectancy = {}
    overall_health_expectancy = {}
    
    # Map male health expectancy data
    for each, value in health_expectancy_data[1].items():
        if each is not None:
            male_health_expectancy[each] = value
    
    # Map female health expectancy data
    for each, value in health_expectancy_data[2].items():
        if each is not None:
            female_health_expectancy[each] = value
    
    # Map overall health expectancy data
    for each, value in health_expectancy_data[3].items():
        if each is not None:
            overall_health_expectancy[each] = value
    
    # Fill missing years with None for all categories (2000 to 2024)
    target_years = list(map(str, range(2000, 2025)))
    
    for year in target_years:
        if year not in male_health_expectancy:
            male_health_expectancy[year] = None
        if year not in female_health_expectancy:
            female_health_expectancy[year] = None
        if year not in overall_health_expectancy:
            overall_health_expectancy[year] = None
    
    # Sort dictionaries by year for consistency
    male_health_expectancy = dict(sorted(male_health_expectancy.items()))
    female_health_expectancy = dict(sorted(female_health_expectancy.items()))
    overall_health_expectancy = dict(sorted(overall_health_expectancy.items()))
    
    return male_health_expectancy, female_health_expectancy, overall_health_expectancy



def process_group_A_data(group_A_data):
    hiv_data = {}
    non_commencial_diseases = {}
    suicide_deaths = {}
    hypertension_data = {}
    adult_obesity = {}
    tobaco_use = {}
    alcohol_assumption = {}
    safely_managed_sanitation = {}
    fine_particulate_matter = {}
    financial_hardship = {}

    list_of_indicators_a = [hiv_data, non_commencial_diseases, suicide_deaths,
                            hypertension_data, adult_obesity, tobaco_use,
                            alcohol_assumption, safely_managed_sanitation,
                            fine_particulate_matter, financial_hardship]

    for key, array in zip(group_A_data.keys(), list_of_indicators_a):
        for each in group_A_data[key]:
            for i in each.keys():
                array[i] = each[i]  # Assuming `array` is a dictionary-like structure

    target_years = list(map(str, range(2000, 2025)))
    for each in list_of_indicators_a:
        # Remove years outside 2000-2024
        keys_to_remove = [year for year in each.keys() if int(year) < 2000 or int(year) > 2024]
        for key in keys_to_remove:
            del each[key]

        # Ensure all years between 2000-2024 are present, add None if missing
        for year in target_years:
            if year not in each:
                each[year] = None
    hiv_data = dict(sorted(hiv_data.items()))
    non_commencial_diseases = dict(sorted(non_commencial_diseases.items()))
    suicide_deaths = dict(sorted(suicide_deaths.items()))
    hypertension_data = dict(sorted(hypertension_data.items()))
    adult_obesity = dict(sorted(adult_obesity.items()))
    tobaco_use = dict(sorted(tobaco_use.items()))
    alcohol_assumption = dict(sorted(alcohol_assumption.items()))
    safely_managed_sanitation = dict(sorted(safely_managed_sanitation.items()))
    fine_particulate_matter = dict(sorted(fine_particulate_matter.items()))
    financial_hardship = dict(sorted(financial_hardship.items()))

    return (hiv_data, non_commencial_diseases, suicide_deaths, hypertension_data,
            adult_obesity, tobaco_use, alcohol_assumption, safely_managed_sanitation,
            fine_particulate_matter, financial_hardship)


def extract_number(data_point):
    # Check if data_point is empty or not a valid string
    if not data_point or not isinstance(data_point[0], str):
        return None  # Return None if the input is invalid

    # Use regex to find the first occurrence of a number in the string
    match = re.search(r"[-+]?\d*\.\d+|\d+", data_point[0])
    if match:
        return float(match.group(0))  # Convert the extracted number to a float
    return None  # Return None if no number is found

def generate_nearby_values(data_point, indicator_name):
    year_data = {}
    base_value = extract_number(data_point)  # Extract the number from the first element of the list

    for year in range(2000, 2025):
        if base_value is not None:  # Check if a valid base value is available
            # Generate a random value around the base value with a small variance (e.g., ±10%)
            variance = random.uniform(-0.1 * base_value, 0.1 * base_value)  # 10% variance
            random_value = round(base_value + variance, 2)
            year_data[str(year)] = random_value
        else:
            # Assign the indicator name if base value is not found
            year_data[str(year)] = indicator_name  # or a meaningful placeholder
    return year_data