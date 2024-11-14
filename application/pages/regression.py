import streamlit as st
import pandas as pd



def show():
    st.title("Healthcare Regression Analysis")
    st.write("Select the country, WHO region, and year to get predictive insights on healthcare metrics.")
    df = pd.read_csv('../application/data.csv')
    countries=df['name'].unique()
    regions=df['who_region'].unique()
    region=st.selectbox('Select Region',regions)
    countries_in_region = list(set(df[df['who_region'] == region]['name'].tolist()))
    country=st.selectbox('Select Country',countries_in_region)
    available_income_levels = df[df['name'] == country]['world_bank_income_level'].unique()
    
    # Allow the user to select an income level from the available options
    income_level = st.selectbox("Select Income Level", available_income_levels)
    year=st.slider('Select Year',min_value=2000,max_value=2050)

    st.button('Predict')
    predictions=make_prediction(region,country,income_level,year)
    


    pass


def make_prediction(region,name,income_level,year):
    df_encoded=pd.read_csv('../application/dataNameEncoded.csv')
    df_non_encoded=pd.read_csv('../application/data.csv')
    feature_columns = ['health_expenditure', 'who_region', 'world_bank_income_level',
                   'population growth rate%', 'year', 'population', 'life_expectancy', 
                   'health_life_expectancy'] + list(df_encoded.columns[ df_encoded.columns.str.startswith('name_')])
    target_indicators = [ 'Adult obesity%',
                     'Tobacco use%', 'Alcohol consumption','Number of new HIV infections', 'Suicide deaths', 'Prevalence of hypertension%']
    input_data = {
    'name': name,
    'health_expenditure': df_non_encoded[df_non_encoded['name'] == name]['health_expenditure'].iloc[0],
    'who_region': df_non_encoded[df_non_encoded['name'] == name]['who_region'].iloc[0], 
    'world_bank_income_level': income_level,
    'population growth rate%': df_non_encoded[df_non_encoded['name'] == name]['population growth rate%'].iloc[0],
    'year': year,  # Assuming year is a variable
    'population': df_non_encoded[df_non_encoded['name'] == name]['population'].iloc[0],
    'life_expectancy': df_non_encoded[df_non_encoded['name'] == name]['life_expectancy'].iloc[0],
    'health_life_expectancy': df_non_encoded[df_non_encoded['name'] == name]['health_life_expectancy'].iloc[0]
}
    st.write("Input Data for Prediction:")
    st.write(input_data)
    pass



def inputs():

    pass


show()