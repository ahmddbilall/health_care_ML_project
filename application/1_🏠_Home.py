import os
import warnings

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  

warnings.filterwarnings('ignore')

try:
    import tensorflow as tf
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
except ImportError:
    print("TensorFlow not installed.")
except AttributeError:
    pass  

try:
    import plotly.express as px
    print("Plotly is available for interactive plots.")
except ImportError:
    print("Plotly not installed. Run `pip install plotly` to enable interactive plots.")

import streamlit as st


st.set_page_config(page_title="Health Indicators Prediction", page_icon="🏠")

st.title("Welcome to the Health Indicators Prediction System")

# Description of the Project
st.markdown("""
This web application is designed to provide predictions and insights into various health indicators across different countries. By leveraging machine learning models and time series forecasting, this platform helps users to predict values such as:

- HIV Infections
- Tobacco Use
- Alcohol Consumption
- Hypertension Prevalence
- Population Growth

We aim to empower decision-makers, researchers, and public health officials with powerful tools to analyze and predict the trends that impact global health outcomes.
""")

st.header("Project Overview")
st.markdown("""
Our project uses time series forecasting models such as ARIMA, SARIMA, Prophet, and LSTM to predict health-related indicators based on historical data scraped from WHO. 
We have also clustered countries based on similarities in these indicators, allowing for better understanding and decision-making.

The application has five main sections:

1. **Clustering**: Visualize clusters of countries based on health-related indicators.
2. **Single Indicator**: Predict the value of a specific indicator for a given country.
3. **Combined Indicators**: Predict multiple health indicators at once.
4. **About**: Learn more about the team and the project.
""")

st.header("Our Goals")
st.markdown("""
- To provide accurate predictions on health indicators for individual countries.
- To allow easy comparison of countries based on their health metrics.
- To make health data more accessible and actionable for policy makers and researchers.
""")


