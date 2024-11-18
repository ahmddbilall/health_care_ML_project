import streamlit as st
import pandas as pd
import numpy as np
from functions import  *
st.set_page_config(layout="wide")

st.header("Regression Analysis")
df1 = pd.read_csv('../models/pklFiles/ClusterDataForTimeSeries.csv')
df2 = pd.read_csv('../application/data.csv')

def predict_all_indicators():
    countries = df1['name'].unique()   
    regions = df2['who_region'].unique()
    selected_region = st.selectbox("Select Region", regions)
    countries = df2[df2['who_region'] == selected_region]['name'].unique()
    selected_country = st.selectbox("Select Country", countries)
    target_indicators = ['Adult obesity%', 'Tobacco use%', 'Alcohol consumption',
                     'Number of new HIV infections', 'Suicide deaths', 'Prevalence of hypertension%']
    select_indicator=st.selectbox("Select Indicator",target_indicators)
    selected_year = st.slider("Select Year", 2024, 2050, 2024)

    st.write(f"Selected Year: {selected_year}")
    if st.button("Predict"):
        predictions=make_predictions(select_indicator,selected_country,selected_year)
        plot_predictions(predictions)
        plot_predictions_2(predictions)
        




predict_all_indicators()