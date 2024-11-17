import streamlit as st
import pandas as pd
from functions  import *
# Page Header
import os
st.header("Clustering Analysis")

# Create Columns
col1, col2 = st.columns([1, 3])

target_indicators = [
   
    'Tobacco use%',
    'Alcohol consumption',
    'Number of new HIV infections',
    'Prevalence of hypertension%',
    'population'
]


    
st.subheader("Target Indicators")
selected_indicator = st.radio(
        "Choose an Indicator:", 
        target_indicators
    )




st.subheader(f"You have selected **{selected_indicator}**.")

create_3d_scatter_plot_single_indicator(selected_indicator)
create_2d_scatter_plot(selected_indicator)
