from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from scipy.interpolate import interp1d
import re

def start_browser():
    '''
    Initializes the WebDriver in headless mode and returns the driver instance.
    '''
    options = Options()
    options.add_argument("--headless")  
    driver = webdriver.Edge(options=options)
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
        print(f"Error while waiting for page load:")

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

def get_country_name(driver):
    try:
        name= driver.find_element(By.CLASS_NAME, "page-header__main-info")
        country_name=name.find_element(By.TAG_NAME,"h1")
        return country_name.text
    except Exception as e:
        return None

def get_current_health_expenditure(driver):
    try:    
        expen1=driver.find_element(By.TAG_NAME,"table")
        expen_rows=expen1.find_elements(By.TAG_NAME,"tr")
        expen2=expen_rows[1]
        ret_row=expen2.find_element(By.TAG_NAME,"td")
        return ret_row.text
    except Exception as e:
        return None

def get_who_region(driver):
    try:    
        expen1=driver.find_element(By.TAG_NAME,"table")
        expen_rows=expen1.find_elements(By.TAG_NAME,"tr")
        expen2=expen_rows[2]
        ret_row=expen2.find_element(By.TAG_NAME,"td")
        return ret_row.text
    except Exception as e:
        return None

def get_world_bank_income_level(driver):
    try:    
        expen1=driver.find_element(By.TAG_NAME,"table")
        expen_rows=expen1.find_elements(By.TAG_NAME,"tr")
        expen2=expen_rows[3]
        ret_row=expen2.find_element(By.TAG_NAME,"td")
        return ret_row.text
    except Exception as e:
        return None

def get_population_growth_rate(driver):
            try:
                rate_1 = driver.find_element(By.XPATH, "//*[@id='main']/section/div/div[2]/div/div/div[2]/div/div/div[4]/div/p/span[1]")
                if rate_1.text.strip():
                    return rate_1.text
                else:
                    return None  
            except Exception as e:
                return None

def get_indicators(driver):
    group_links = {}
    group_header = [
        "Number of new HIV infections", 
        "Suicide deaths", "Prevalence of hypertension", "Adult obesity", "Tobacco use",
        "Alcohol consumption"
    ]

    section = 1

    ele = driver.find_element(By.CLASS_NAME,'progressive-tabs-tablist')
    li_elements = ele.find_elements(By.TAG_NAME, 'li')

    # Iterate over each li element and click it
    for li in li_elements:
        ActionChains(driver).move_to_element(li).click(li).perform()

        indicators = driver.find_elements(By.XPATH, f"/html/body/div[5]/main/section/div/div[9]/div/div/div/div/section[{section}]/div")

        for indicator in indicators:
            links = indicator.find_elements(By.TAG_NAME, 'a')  
            headers = indicator.find_elements(By.TAG_NAME, 'h2')

            filtered_links = [link.get_attribute('href') for link in links if link.get_attribute('href').startswith('https://data.who.int/indicators/')]

            if len(filtered_links) != len(headers):
                continue

            for idx, header in enumerate(headers):
                header_text = header.text.strip()

                if header_text in group_header:

                    href = filtered_links[idx]  
                    group_links[header_text] = href

        section += 1
    return group_links

def get_indicator_data(driver, urls):
    all_data = {}  
    
    for name, url in urls.items():
        open_page(driver, url)
        
        time.sleep(2) 

        try:
            dropdown = driver.find_element(By.XPATH, '/html/body/main/section/div[2]/div[3]/div[1]/div[1]/div/div/div/div/div/div/div[1]/div[2]/div/div[2]/label/span[2]')
            dropdown.click()

            options = dropdown.find_elements(By.CSS_SELECTOR, 'option')
            indicator_data = []  

            for option in options:
                option.click()  
                
                time.sleep(1)  

                try:
                    span_element = driver.find_element(By.CSS_SELECTOR, 'tr.border-bottom.svelte-193mdey.selected td[data-testid="dataDotViz-collapsibleTable-data-point"] span.svelte-193mdey')
                    data_point = span_element.text
                    indicator_data.append({option.text: data_point})  
                    
                except Exception as e:
                    print(f"Error fetching data for {option.text}")
            
            all_data[name] = indicator_data  

        except Exception as e:
            print(f"Error on URL {url}")

    return all_data


import re
from scipy.interpolate import interp1d


def interpolate_pop(data, target_year=2024):
    # Extract the data while cleaning the values
    year_values = {}
    for year, value in data.items():
        # Remove brackets and unit characters (like 'm' or 'k') if present
        if '[' in value:
            value = value.split('[')[0].strip()
        main_value_match = re.match(r"([\d.]+)", value)
        if main_value_match:
            year_values[int(year)] = float(main_value_match.group(0))
    
    # Set up the years to interpolate between
    interpolated_data = {}
    start_year = 2000
    end_year = target_year

    for year in range(start_year, end_year + 1):
        if year in year_values:
            interpolated_data[year] = year_values[year]
        else:
            previous_years = [y for y in year_values if y < year]
            next_years = [y for y in year_values if y > year]

            # If there are years before and after the current year, interpolate linearly
            if previous_years and next_years:
                prev_year = max(previous_years)
                next_year = min(next_years)
                slope = (year_values[next_year] - year_values[prev_year]) / (next_year - prev_year)
                interpolated_data[year] = year_values[prev_year] + slope * (year - prev_year)
            # If there are only previous years, extend the slope of the last two known points
            elif previous_years:
                last_two_years = sorted(previous_years)[-2:]
                if len(last_two_years) == 2:
                    y1, y2 = last_two_years
                    slope = (year_values[y2] - year_values[y1]) / (y2 - y1)
                    interpolated_data[year] = year_values[y2] + slope * (year - y2)

    return interpolated_data



def get_population_data(driver):
     data_points = driver.find_elements(By.CSS_SELECTOR, 'text[data-testid="dataDotViz-line-point-alt-text"]')

     chart_data = {}
     i = 0
     for point in data_points:
            year = point.get_attribute('data-test-time-dim')  
            population = point.text.strip()  
            
            chart_data[year] = population
            i+=1
            if i==25:
                break
    
     return chart_data

def get_life_expectancy_data(driver):
    life_expectancy_data = []

    try:
        driver.find_element(By.CSS_SELECTOR, '#tab-life-expectancy-section').click()
        chart_element = driver.find_element(By.CSS_SELECTOR, '#life-expectancy-section > div > div:nth-child(1) > div > div')
        row_elements = chart_element.find_elements(By.CSS_SELECTOR, 'g[role="row"]')
        
        for each in row_elements:
            row_data = {}
            each_row = each.find_elements(By.CSS_SELECTOR, 'text[role="cell"]')
            
            for row in each_row:
                time_dim = row.get_attribute("data-test-time-dim")
                value = row.text
                if "Male" in value:
                    value = "Male"
                elif "Female" in value:
                    value = "Female"
                elif "Total" in value:
                    value = "Total"
                
                row_data[time_dim] = value
            
            life_expectancy_data.append(row_data)
    
    except Exception as e:
        print(f"An error occurred:")
        dummy_data = {
            "time_dim": "Year",
            "Gender": "Unknown",
            "Life Expectancy": "N/A"
        }
        life_expectancy_data.append(dummy_data)

    return life_expectancy_data

def get_health_life_expectancy_data(driver):
    health_life_expectancy_data = []

    try:
        driver.find_element(By.CSS_SELECTOR, '#tab-healthy-life-expectancy-section').click()
        chart_element = driver.find_element(By.CSS_SELECTOR, '#healthy-life-expectancy-section > div > div:nth-child(1) > div > div')
        row_elements = chart_element.find_elements(By.CSS_SELECTOR, 'g[role="row"]')
        
        for each in row_elements:
            row_data = {}
            each_row = each.find_elements(By.CSS_SELECTOR, 'text[role="cell"]')
            
            for row in each_row:
                time_dim = row.get_attribute("data-test-time-dim")
                value = row.text
                
                if "Male" in value:
                    value = "Male"
                elif "Female" in value:
                    value = "Female"
                elif "Total" in value:
                    value = "Total"
                
                row_data[time_dim] = value
            
            health_life_expectancy_data.append(row_data)
    
    except Exception as e:
        print(f"An error occurred:")
        dummy_data = {
            "time_dim": "Year",
            "Gender": "Unknown",
            "Life Expectancy": "N/A"
        }
        health_life_expectancy_data.append(dummy_data)

    return health_life_expectancy_data

def interpolate_life_and_health_expectancy_data(data_list):
    total_data = next((entry for entry in data_list if entry.get(None) == "Total"), None)
    if not total_data:
        return {2000:None,2001:None,2002:None,2003:None,2004:None,2005:None,2006:None,2007:None,2008:None,2009:None,2010:None,20011:None,2012:None,2013:None,2014:None,2015:None,
                2016:None,2017:None,2018:None,2019:None,2020:None,2021:None,2022:None,2023:None,2024:None}

    year_values = {int(year): float(value) for year, value in total_data.items() if year is not None}
    
    interpolated_data = {}
    start_year = 2000
    end_year = 2024

    for year in range(start_year, end_year + 1):
        if year in year_values:
            interpolated_data[year] = year_values[year]
        else:
            previous_years = [y for y in year_values if y < year]
            next_years = [y for y in year_values if y > year]

            if previous_years and next_years:
                prev_year = max(previous_years)
                next_year = min(next_years)

                slope = (year_values[next_year] - year_values[prev_year]) / (next_year - prev_year)
                interpolated_data[year] = year_values[prev_year] + slope * (year - prev_year)
            elif previous_years:
                last_two_years = sorted(previous_years)[-2:]
                if len(last_two_years) == 2:
                    y1, y2 = last_two_years
                    slope = (year_values[y2] - year_values[y1]) / (y2 - y1)
                    interpolated_data[year] = year_values[y2] + slope * (year - y2)

    return interpolated_data

def interpolate_indicators_data(data):
    def interpolate_years(year_data):
        try:
            # Parse the year values from year_data
            year_values = {int(year): float(value.strip('%')) if '%' in value else float(value)
                           for item in year_data for year, value in item.items()}

            interpolated = {}
            for year in range(2000, 2025):
                if year in year_values:
                    interpolated[year] = year_values[year]
                else:
                    # Determine previous and next years with available data
                    previous_years = [y for y in year_values if y < year]
                    next_years = [y for y in year_values if y > year]

                    if previous_years and next_years:
                        # Perform interpolation using the nearest years
                        prev_year = max(previous_years)
                        next_year = min(next_years)
                        slope = (year_values[next_year] - year_values[prev_year]) / (next_year - prev_year)
                        interpolated[year] = year_values[prev_year] + slope * (year - prev_year)
                    elif previous_years:
                        # Extrapolate from the last two previous years if available
                        last_two_years = sorted(previous_years)[-2:]
                        if len(last_two_years) == 2:
                            y1, y2 = last_two_years
                            slope = (year_values[y2] - year_values[y1]) / (y2 - y1)
                            interpolated[year] = year_values[y2] + slope * (year - y2)
                    elif next_years:
                        # Assign the minimum future value if no previous data exists
                        interpolated[year] = year_values[min(next_years)]
                    else:
                        # Handle case with no available data
                        interpolated[year] = None

            # Format data as percentage if necessary
            if year_data and '%' in year_data[0].get(str(min(year_values.keys())), ''):
                interpolated = {year: f"{value:.1f}%" for year, value in interpolated.items() if value is not None}
            else:
                interpolated = {year: f"{value:.1f}" for year, value in interpolated.items() if value is not None}
            return interpolated

        except ValueError as e:
            print(f"Error processing year data: {e}")
            return {}  # Return empty dict in case of error

    processed_data = {}
    for indicator, year_data in data.items():
        processed_data[indicator] = interpolate_years(year_data)

    return processed_data
