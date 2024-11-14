import streamlit as st
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler

def show():
    st.title("Healthcare Regression Analysis")
    st.write("Select the country, WHO region, and year to get predictive insights on healthcare metrics.")
    
    # Load the data
    df = pd.read_csv('../application/data.csv')
    
    # Dropdowns and slider for user inputs
    regions = df['who_region'].unique()
    region = st.selectbox('Select Region', regions)
    
    # Filter countries based on selected region
    countries_in_region = list(set(df[df['who_region'] == region]['name'].tolist()))
    country = st.selectbox('Select Country', countries_in_region)

    available_income_levels = df[df['name'] == country]['world_bank_income_level'].unique()
    income_level = st.selectbox("Select Income Level", available_income_levels)

    year = st.slider('Select Year', min_value=2000, max_value=2050)
    
    # Trigger to calculate predictions on button click
    if st.button("Predict Healthcare Metrics"):
        predictions = make_prediction(region, country, income_level, year)
        
        # Display predictions
        st.write("Predicted Healthcare Metrics:")
        st.write(predictions)  # Assuming `make_prediction` returns a dictionary or DataFrame
        


def make_prediction(region, name, income_level, year):
    # Load the data
    df = pd.read_csv('../application/data.csv')
    
    # Define feature columns and target indicators
    feature_columns = [
        'health_expenditure', 'who_region', 'world_bank_income_level',
        'population growth rate%', 'year', 'population', 
        'life_expectancy', 'health_life_expectancy'
    ] + list(df.columns[df.columns.str.startswith('name_')])
    
    target_indicators = [
        'Adult obesity%', 'Tobacco use%', 'Alcohol consumption', 
        'Number of new HIV infections', 'Suicide deaths', 
        'Prevalence of hypertension%'
    ]

    input_data = {
        'name_0': int(df[df['name'] == name]['name_0'].iloc[0] if 'name_0' in df.columns else None),
        'name_1': int(df[df['name'] == name]['name_1'].iloc[0] if 'name_1' in df.columns else None),
        'name_2': int(df[df['name'] == name]['name_2'].iloc[0] if 'name_2' in df.columns else None),
        'name_3': int(df[df['name'] == name]['name_3'].iloc[0] if 'name_3' in df.columns else None),
        'name_4': int(df[df['name'] == name]['name_4'].iloc[0] if 'name_4' in df.columns else None),
        'name_5': int(df[df['name'] == name]['name_5'].iloc[0] if 'name_5' in df.columns else None),
        'name_6': int(df[df['name'] == name]['name_6'].iloc[0] if 'name_6' in df.columns else None),
        'name_7': int(df[df['name'] == name]['name_7'].iloc[0] if 'name_7' in df.columns else None),
        'health_expenditure': df[df['name'] == name]['health_expenditure'].iloc[0],
        'who_region': int(df[df['name'] == name]['who_region_encoded'].iloc[0]),
        'world_bank_income_level': int(df[df['name'] == name]['world_bank_income_level_encoded'].iloc[0]),
        'population growth rate%': df[df['name'] == name]['population growth rate%'].iloc[0],
        'year': year,
        'population': df[df['name'] == name]['population'].iloc[0],
        'life_expectancy': df[df['name'] == name]['life_expectancy'].iloc[0],
        'health_life_expectancy': df[df['name'] == name]['health_life_expectancy'].iloc[0]
    }
    
  

    predictions = {}
    for indicator in target_indicators:
        predictions[indicator] = predict(indicator, input_data)
    st.write(input_data)
    return predictions

def scale_data(input_data,indicator):
    with open(f'../models/pklFiles/scaler_{indicator}.pkl', 'rb') as file:
        scaler = pickle.load(file)
    input_df_scaled = pd.DataFrame([input_data])
    feature_columns = [
        'health_expenditure', 'who_region', 'world_bank_income_level',
        'population growth rate%', 'year', 'population', 'life_expectancy', 
        'health_life_expectancy'
    ] + [col for col in input_df_scaled.columns if col.startswith('name_')]


    input_scaled = scaler.fit_transform(input_df_scaled[feature_columns])
    
    return input_scaled


def predict(indicator, input_data):

    with open(f'../models/pklFiles/best_model_{indicator}.pkl', 'rb') as file:
        model = pickle.load(file)
    # input_scaled=scale_data(input_data,indicator)
    import numpy as np
    input_data_scaled = np.array(list(input_data.values())).reshape(1, -1)
    print(f"Scaled Input for {indicator}: {input_data_scaled}")
    prediction = model.predict(input_data_scaled)
    print(f"Prediction for {indicator}: {prediction}")
    
    return prediction[0]



if __name__ == "__main__":
    show()
