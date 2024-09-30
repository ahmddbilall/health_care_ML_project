# Scraping Folder

This folder contains the scripts and functions used for scraping healthcare data from WHO. The scraping functionality is split into two main files: `functions.py` and `scraping.ipynb`.

## Files Overview

1. **functions.py**:  
   This file contains all the reusable functions for scraping data. The functions here are modular and can be imported and used across different scripts and notebooks.

2. **scraping.ipynb**:  
   A Jupyter notebook where the scraping process is executed. This notebook imports the functions from `functions.py` and calls them to scrape data and display the output.

---

## Table of Contents
- [Prerequisites](#prerequisites)
- [Structure of functions.py](#structure-of-functionspy)
- [How to Use scraping.ipynb](#how-to-use-scrapingipynb)
- [Getting Started](#getting-started)

---

## Prerequisites
Before running the scripts in this folder, make sure you have the following installed:

- **Python 3.8+**
- **Jupyter Notebook** (for running the notebook file)
- **Selenium** (for web scraping)

Install dependencies by running:
```bash
pip install -r requirements.txt
```

## Structure of `functions.py`
The `functions.py` file contains the core scraping functions that:
- Initialize and configure Selenium WebDriver.
- Parse web pages for extracting relevant healthcare data (e.g., disease cases, recovery rates).
- Store the data in a structured format (CSV, JSON, etc.).

You can modify or add functions as needed to support additional scraping workflows. 

## How to Use `scraping.ipynb`
The `scraping.ipynb` notebook is where the functions defined in `functions.py` are called. Here's an overview of the steps:

1. **Import the Functions**:
   At the beginning of the notebook, you'll import the necessary functions from `functions.py`:
   ```python
   from functions import *
   ```

2. **Call Functions**:
   You can then call the functions to perform the scraping tasks. For example:

3. **View Output**:
   Once the functions are called, the notebook will display the scraped data or store it in a file for further use.

