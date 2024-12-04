
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import sys
sys.path.append('./') 
from functions import *
st.set_page_config(page_title="Visulization", page_icon="📊",layout="wide")
df = pd.read_csv('./application/data.csv') 
col1, col2 = st.columns([3, 3])
col3 = st.container()
col5 = st.container()
col7 = st.container()
col9 = st.container()
col11 = st.container()
selected_country = st.sidebar.selectbox("Select a Country", sorted(df['name'].unique()))
selected_columns = [ 'Number of new HIV infections', 'Suicide deaths', 
                    'Adult obesity%', 'Tobacco use%', 'Alcohol consumption', 
                    'Prevalence of hypertension%', 'life_expectancy', 'health_life_expectancy']
selected_indicator = st.sidebar.selectbox("Select an Indicator", selected_columns)
with col1:
    fig1 = generate_income_level_chart(df)
    st.plotly_chart(fig1)
with col2:
    fig2 = plot_grouped_health_expenditure(df)
    st.plotly_chart(fig2)
with col3:
    fig = plot_health_indicators(df)
    st.plotly_chart(fig)
with col5:
    plot_health_indicators_by_country(df, selected_country)
with col7:
    plot_health_life_hypertension_obesity(df, selected_country)
with col9:
    df_for_this_graph = pd.read_csv('visualization/output.csv')
    fig = plot_population_horizontal_bar_chart(df_for_this_graph)
    st.plotly_chart(fig)
with col11:
    fig = plot_choropleth_map(df, selected_indicator)
    st.plotly_chart(fig)
