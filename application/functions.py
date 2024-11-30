import pickle
import numpy as np
from urllib.request import urlopen
import os
import json
import pandas as pd
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.preprocessing import StandardScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
import concurrent.futures
from sklearn.metrics import r2_score
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from concurrent.futures import ThreadPoolExecutor

def load_model(indicator, cluster_id, model_dir='./models/pklFiles/'):
    model_filename = None
    model_name = None
    for file in os.listdir(model_dir):
        if f"{indicator}_cluster_{cluster_id}_model_" in file:
            model_filename = file
            model_name = file.split("_model_")[-1].replace(".pkl", "")  # Extract model name
            break

    if model_filename is None:
        return f"No model found for indicator '{indicator}' and cluster '{cluster_id}'."

    model_path = os.path.join(model_dir, model_filename)
    with open(model_path, 'rb') as file:
        model = pickle.load(file)


    result = {
        "name": model_name,
        "model": model,
        "scaler": None
    }

    if model_name == "LSTM":
        scaler_filename = f"{indicator}_cluster_{cluster_id}_scaler_{model_name}.pkl"
        scaler_path = os.path.join(model_dir, scaler_filename)
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as file:
                scaler = pickle.load(file)
                result["scaler"] = scaler
        else:
            print(f"Scaler file not found for LSTM model: {scaler_filename}")

    return result


def predict_value(year, country, indicator):
    df = pd.read_csv('./application/ClusterDataForTimeSeries.csv')
    
    try:
        cluster = df.loc[df['name'] == country, 'Assigned Cluster'].values[0]
    except IndexError:
        return f"Country {country} not found in the dataset."


    model = load_model(indicator, cluster)

    print(model)

    input_data = pd.DataFrame({'year': [year]})

    if model['name']=='LSTM':
        scaled_input = model['scaler'].transform(input_data.values)
        scaled_input = scaled_input.reshape((scaled_input.shape[0], 1, 1))
        prediction = model['model'].predict(scaled_input)
        prediction = model['scaler'].inverse_transform(prediction)
    if model['name']=='ARIMA':
        prediction = model['model'].predict(start=year,end=year)
        try:
            return abs (prediction['yhat'][0])%100
        except:
            return abs(float( prediction))%100
        
    if  model['name']=='Prophet':
        future=pd.DataFrame({'ds':pd.date_range(start=year,end=year)})
        prediction = model['model'].predict(future)
        try:
            return  abs(float(prediction['yhat'][0]))%100
        except:
            return abs(prediction)%100
        

    return abs(prediction[0][0]/10)%100

def get_all_predictions(indicators, country, year):

    predictions = {}
    with ThreadPoolExecutor() as executor:
        for indicator in indicators:
            predictions[indicator] = executor.submit(predict_value, year, country, indicator)

    return {indicator: prediction.result() for indicator, prediction in predictions.items()}




def predictions_table(predictions,population):
    for each in predictions:
        predictions[each]=predictions[each]
    df=pd.DataFrame(predictions.items(),columns=['Percentage','Population Effect%'])
    return df



def interactive_prediction_plot(predictions):
    df = pd.DataFrame(list(predictions.items()), columns=['Health Indicator', 'Population Effect%'])

    fig = px.bar(df, x='Health Indicator', y='Population Effect%', 
                 title="Health Indicator Predictions",
                 labels={'Population Effect%': 'Population Effect (%)', 'Health Indicator': 'Health Indicator'},
                 color='Population Effect%',  
                 color_continuous_scale='rainbow',  
                 hover_data={'Health Indicator': True, 'Population Effect%': True},  
                 template='plotly_dark')  

    fig.update_layout(
        hovermode="x unified",  
        xaxis_tickangle=-45,  
        showlegend=False  
    )

    st.plotly_chart(fig)

def get_risk_and_suggestion(indicator, value):
    thresholds = {
        "Adult obesity%": 15,
        "Tobacco use%": 15,
        "Alcohol consumption": 15,
        "Suicide deaths": 15,
        "Prevalence of hypertension%": 15,
        "Number of new HIV infections": 3
    }
    if value > thresholds.get(indicator, 0):
        return "High Risk", "red", "High!"
    else:
        return "Low Risk", "green", "Low."

def create_decision_making_plot(predictions):
    indicators = []
    values = []
    risks = []
    colors = []
    suggestions = []
    sizes = []

    size_factor = 5  

    for indicator, value in predictions.items():
        risk_status, color, suggestion = get_risk_and_suggestion(indicator, value)
        indicators.append(indicator)
        values.append(value)
        risks.append(risk_status)
        colors.append(color)
        suggestions.append(suggestion)
        sizes.append(value * size_factor)  

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=indicators,
        y=values,
        mode='markers+text',
        marker=dict(
            size=sizes,
            color=colors,
            opacity=0.8,
            line=dict(width=2, color='black')
        ),
        text=indicators,
        hoverinfo='text+name',  
    ))

    for i, indicator in enumerate(indicators):
        fig.add_annotation(
            x=indicators[i],
            y=values[i],
            text=suggestions[i],
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-40,
            font=dict(size=10, color=colors[i]),
            arrowcolor=colors[i]
        )

    fig.update_layout(
        title="Risk Level and Decision-Making Insights",
        xaxis_title="Health Indicators",
        yaxis_title="Predicted Value (%)",
        showlegend=False,
        hovermode='closest',
        template="plotly_dark",
        autosize=True
    )
    st.plotly_chart(fig)







def get_risk(indicator, value):
    thresholds = {
        "Adult obesity%": 15,
        "Tobacco use%": 15,
        "Alcohol consumption": 15,
        "Suicide deaths": 15,
        "Prevalence of hypertension%": 15,
        "Number of new HIV infections": 3
    }
    if value > thresholds.get(indicator, 0):
        return "High Risk", "red"
    else:
        return "Low Risk", "green"

def create_risk_pie_chart(predictions):
    high_risk_count = 0
    low_risk_count = 0
    
    for indicator, value in predictions.items():
        risk_status, _ = get_risk(indicator, value)
        if risk_status == "High Risk":
            high_risk_count += 1
        else:
            low_risk_count += 1
    
    risk_labels = ['High Risk', 'Low Risk']
    risk_values = [high_risk_count, low_risk_count]

    fig = go.Figure(data=[go.Pie(
        labels=risk_labels, 
        values=risk_values, 
        hole=0.2,
        hoverinfo='label+percent',  
        textinfo='label+value+percent',  
        textfont=dict(size=15, color='white'),  
        marker=dict(
            colors=['#FF4136', '#2ECC40'],  
            line=dict(color='black', width=2)  
        )
    )])

    fig.update_layout(
        title="Risk Level Distribution",
        template="plotly_dark",
        showlegend=True,
        legend=dict(x=0.85, y=1, font=dict(size=12)),  
        width=600,  
        height=300,  
        margin=dict(t=40, b=40, l=40, r=40),  
      
    )
    
    st.plotly_chart(fig)



def make_clustered_risk_graph(indicator):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.abspath(os.path.join(base_dir, f'../models/clusters_{indicator}.csv'))
    
    df = pd.read_csv(csv_path)
    
    if 'risk' not in df.columns or 'Assigned Cluster' not in df.columns or indicator not in df.columns:
        raise ValueError("CSV must contain 'risk', 'Assigned Cluster', and the selected indicator columns.")
    
    fig = px.scatter(
        df,
        x=indicator,
        y='risk',
        color='Assigned Cluster',
        title=f"Clusters and Risk for {indicator}",
        labels={'risk': 'Risk Level'},
        template="plotly_dark",
        hover_data=['Assigned Cluster']
    )
    st.plotly_chart(fig)
    return fig


def create_3d_scatter_plot_single_indicator(indicator):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.abspath(os.path.join(base_dir, f'../models/clusters_{indicator}.csv'))
    
    df = pd.read_csv(csv_path)
    fig = px.scatter_3d(df, 
                        x='name', 
                        y=indicator, 
                        z=indicator,  
                        color='risk', 
                        title=f'3D Scatter Plot of {indicator} across Countries')
    
    fig.update_layout(
        scene=dict(
            xaxis_title='Country',
            yaxis_title=indicator,
            zaxis_title=indicator
        ),
        template='plotly_dark',
             width=1500,  
        height=1000,
      
    )

    st.plotly_chart(fig)


def create_2d_scatter_plot(indicator):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.abspath(os.path.join(base_dir, f'../models/clusters_{indicator}.csv'))
    
    df = pd.read_csv(csv_path)
    
    if indicator not in df.columns or 'risk' not in df.columns or 'name' not in df.columns:
        raise ValueError(f"CSV must contain the '{indicator}', 'risk', and 'name' columns.")
    
    df_cleaned = df.dropna(subset=[indicator])  
    
    fig = px.scatter(
        df_cleaned, 
        x='name', 
        y=indicator, 
        color='risk',  
        labels={'name': 'Country', indicator: indicator, 'risk': 'Risk Level'},
        title=f'2D Scatter Plot of {indicator} by Country and Risk Level'
    )
    
    fig.update_layout(
        template='plotly',  
        xaxis_title='Country',
        yaxis_title=indicator,
        width=1500,  
        height=800,  
    )
    
    st.plotly_chart(fig)



def make_predictions(indicator, country, year):
    current_year = year
    
    years_to_predict = [current_year + i for i in range(1, 10 + 1)]
    
    predictions = {}
    
    def get_prediction_for_year(year):
        return year, get_all_predictions([indicator], country, year)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(get_prediction_for_year, years_to_predict)
        
        for year, prediction in results:
            predictions[year] = prediction
    
    return predictions


def plot_predictions(predictions):
    """
    This function takes a dictionary of predictions and plots the trend over time in a line chart, 
    adding small fluctuations to the values.
    
    :param predictions: Dictionary with years as keys and prediction values as sub-dictionaries
    :return: None
    """
    df = pd.DataFrame.from_dict(predictions, orient='index')
    df.reset_index(inplace=True)
    df.columns = ['Year', 'Prevalence of hypertension%']
    
    noise = np.random.normal(0, 0.1, size=df.shape[0])  
    df['Prevalence of hypertension%'] += noise  
    
    fig = px.line(df, x='Year', y='Prevalence of hypertension%', title='Prevalence of Hypertension Over Time' ,
                  
                   markers=True,)
    
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_yaxes(range=[df['Prevalence of hypertension%'].min() - 1, df['Prevalence of hypertension%'].max() + 1])  
    fig.update_layout(template='plotly_dark', height=900)  
    st.plotly_chart(fig)
def plot_predictions_2(predictions):
    """
    This function takes a dictionary of predictions and plots a histogram on the Date axes 
    with daily markers and average value bars, adding noise to show fluctuations.
    
    :param predictions: Dictionary with years as keys and prediction values as sub-dictionaries.
    :return: None
    """
    years = list(predictions.keys())
    values = [list(prediction.values())[0] for prediction in predictions.values()]
    
    df = pd.DataFrame({
        'Year': years,
        'Prediction': values
    })
    
    noise = np.random.normal(0, 0.2, size=df.shape[0])  
    df['Prediction'] += noise  
    
    fig = px.histogram(df, x="Year", y="Prediction", histfunc="avg", title="Prediction over Time")
    
    fig.update_traces(xbins_size=1)  
    fig.update_xaxes(showgrid=True, ticklabelmode="period", tickformat="%Y")
    
    fig.update_layout(
        bargap=0.2,  
        font=dict(color='black'),   
        title_font=dict(size=22), 
        title_x=0.5,  
        margin={"r": 20, "t": 40, "l": 40, "b": 40}, 
    )
    
    fig.add_trace(go.Scatter(mode="markers", x=df["Year"], y=df["Prediction"], name="Predictions", marker=dict(color='blue')))
    
    st.plotly_chart(fig)


def plot_population_horizontal_bar_chart(df):  
    filtered_df = df[df['year'] == 2024]
    filtered_df = filtered_df.sort_values(by='pop2024', ascending=False)
    filtered_df = filtered_df.head(10)
    fig = px.bar(
        filtered_df,
        y='name',
        x='pop2024',
        title='Population of All Countries in 2024',
        labels={'name': 'Country', 'pop2024': 'Population'},
        color='pop2024',
        orientation='h',
        color_continuous_scale='viridis',
        template='plotly_dark'
    )
    fig.update_layout(
        yaxis_title='Country',
        xaxis_title='Population',
        height=900, 
        width=1000
    )
    return fig



def generate_income_level_chart(df):
    unique_countries = df[['who_region', 'world_bank_income_level', 'name']].drop_duplicates()
    region_income_country_count = unique_countries.groupby(['who_region', 'world_bank_income_level']).size().unstack(fill_value=0)
    region_income_country_count.reset_index(inplace=True)
    fig = px.bar(region_income_country_count,
                 x='who_region',
                 y=region_income_country_count.columns[1:],
                 title='Income Levels Distribution Across WHO Regions',
                 labels={'who_region': 'WHO Region', 'value': 'Number of Countries'},
                 text_auto=True,
                 barmode='stack',  
                 category_orders={'who_region': region_income_country_count['who_region'].unique()},
                 height=600)
    return fig




def plot_choropleth_map(df, selected_indicator, geojson_url='https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json'):
    with urlopen(geojson_url) as response:
        countries_geojson = json.load(response)
    selected_columns = [ 'Number of new HIV infections', 'Suicide deaths', 
                        'Adult obesity%', 'Tobacco use%', 'Alcohol consumption', 
                        'Prevalence of hypertension%', 'life_expectancy', 'health_life_expectancy']
    numeric_df = df[selected_columns + ['name']].dropna()
    grouped_df = numeric_df.groupby('name').mean()
    if selected_indicator not in grouped_df.columns:
        raise ValueError(f"{selected_indicator} is not a valid column in the dataset")
    fig = px.choropleth(
        grouped_df.reset_index(), 
        geojson=countries_geojson,
        locations='name',
        featureidkey='properties.name', 
        color=selected_indicator,
        color_continuous_scale="Viridis",
        range_color=(grouped_df[selected_indicator].min(), grouped_df[selected_indicator].max()),
        labels={selected_indicator: selected_indicator.replace('_', ' ').title()},
        title=f'{selected_indicator.replace("_", " ").title()} by Country'
    )
    fig.update_geos(
        fitbounds="locations", 
        visible=False,
        projection_scale=1.2
    )
    fig.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},  # Minimize margins
        width=1200,  
        height=400   
    )
    return fig



def plot_health_indicators_by_country(df,selected_country):
    country_list = df['name'].unique()
    filtered_df = df[df['name'] == selected_country]
    indicators = {
        'Life Expectancy': 'life_expectancy',
        'Alcohol Consumption': 'Alcohol consumption',
        'Tobacco Use': 'Tobacco use%'
    }
    fig = go.Figure()
    for indicator_name, column in indicators.items():
        fig.add_trace(go.Scatter(
            x=filtered_df['year'],
            y=filtered_df[column],
            mode='lines+markers',
            name=indicator_name
        ))
    fig.update_layout(
        title=f'Health Indicators Over Time for {selected_country}',
        xaxis_title='Year',
        yaxis_title='Normalized Value',
        hovermode='x unified',
        legend_title='Indicators',
        template='plotly_dark',
        width=1000,
        height=600
    )
    st.plotly_chart(fig)
def plot_health_life_hypertension_obesity(df, selected_country):
    filtered_df = df[df['name'] == selected_country]
    indicators = {
        'Health Life Expectancy': 'health_life_expectancy',
        'Prevalence of Hypertension': 'Prevalence of hypertension%',
        'Adult Obesity': 'Adult obesity%'
    }
    fig = go.Figure()
    for indicator_name, column in indicators.items():
        fig.add_trace(go.Scatter(
            x=filtered_df['year'],
            y=filtered_df[column],
            mode='lines+markers',
            name=indicator_name
        ))
    fig.update_layout(
        title=f'Health Life Expectancy, Hypertension, and Obesity Over Time for {selected_country}',
        xaxis_title='Year',
        yaxis_title='Normalized Value',
        hovermode='x unified',
        legend_title='Indicators',
        template='plotly_dark',
        width=1000,
        height=600
    )
    st.plotly_chart(fig)





def plot_health_indicators(df):
    selected_columns = ['population', 'Number of new HIV infections', 'Suicide deaths', 
                        'Adult obesity%', 'Tobacco use%', 'Alcohol consumption', 
                        'Prevalence of hypertension%', 'life_expectancy', 'health_life_expectancy']
    numeric_df = df[selected_columns]
    grouped_df = df.groupby('year')[selected_columns].mean()
    df_normalized=grouped_df
    fig = go.Figure()
    for col in df_normalized.columns:
        fig.add_trace(go.Scatter(
            x=df_normalized.index,  
            y=df_normalized[col],   
            mode='lines+markers',
            name=col 
        ))
    fig.update_layout(
        title='Normalized Interactive Line Chart of Health Indicators by Year',
        xaxis_title='Year',
        yaxis_title='Normalized Values (0-1)',
        hovermode='x unified', 
        legend_title='Indicators',
        template='plotly_dark', 
        width=1000,
        height=600
    )
    return fig






def plot_grouped_health_expenditure(df, group_by_column='world_bank_income_level'):

    group_data = df.groupby(group_by_column)['health_expenditure'].mean().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=group_data['health_expenditure'], 
        y=group_data[group_by_column],
        name='Health Expenditure by ' + group_by_column,
        marker_color='rgb(26, 118, 255)'
    ))
    fig.update_layout(
        title=f'Average Health Expenditure by {group_by_column.capitalize()}',
        xaxis_tickfont_size=14,
        yaxis=dict(
            title=dict(
                text="Health Expenditure (USD)",
                font=dict(size=16)
            ),
            tickfont_size=14,
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1  
    )
    return fig