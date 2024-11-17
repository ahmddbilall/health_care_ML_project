import pickle
import numpy as np
import os
import pandas as pd
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.preprocessing import StandardScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.metrics import r2_score
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from concurrent.futures import ThreadPoolExecutor


def load_model(indicator, cluster_id, model_dir='../models/pklFiles/'):
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
    df = pd.read_csv('../models/pklFiles/ClusterDataForTimeSeries.csv')
    
    try:
        cluster = df.loc[df['name'] == country, 'Assigned Cluster'].values[0]
    except IndexError:
        return f"Country {country} not found in the dataset."


    model = load_model(indicator, cluster)

    print(model)

    # Prepare input data
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
    # Fetch predictions (replace this with actual session state if needed)
    # Convert the predictions to a DataFrame
    df = pd.DataFrame(list(predictions.items()), columns=['Health Indicator', 'Population Effect%'])

    # Create an interactive bar chart using Plotly
    fig = px.bar(df, x='Health Indicator', y='Population Effect%', 
                 title="Health Indicator Predictions",
                 labels={'Population Effect%': 'Population Effect (%)', 'Health Indicator': 'Health Indicator'},
                 color='Population Effect%',  # Color bars based on effect
                 color_continuous_scale='rainbow',  # Choose a color scale
                 hover_data={'Health Indicator': True, 'Population Effect%': True},  # Show details on hover
                 template='plotly_dark')  # Optional: Use a dark theme

    # Add hover effects, zoom, and interactivity
    fig.update_layout(
        hovermode="x unified",  # Unified hover for better comparison
        xaxis_tickangle=-45,  # Rotate x-axis labels for better readability
        showlegend=False  # Optional: Hide legend if not needed
    )

    # Display the Plotly chart in Streamlit
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

    size_factor = 5  # Size scaling factor for circles

    for indicator, value in predictions.items():
        risk_status, color, suggestion = get_risk_and_suggestion(indicator, value)
        indicators.append(indicator)
        values.append(value)
        risks.append(risk_status)
        colors.append(color)
        suggestions.append(suggestion)
        sizes.append(value * size_factor)  # Proportional size of circles based on prediction

    fig = go.Figure()

    # Add circles with decision-making suggestions
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
        hoverinfo='text+name',  # Display indicator name and value
    ))

    # Add suggestions as annotations
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
    
    # Classify the predictions into High and Low Risk
    for indicator, value in predictions.items():
        risk_status, _ = get_risk(indicator, value)
        if risk_status == "High Risk":
            high_risk_count += 1
        else:
            low_risk_count += 1
    
    # Prepare data for pie chart
    risk_labels = ['High Risk', 'Low Risk']
    risk_values = [high_risk_count, low_risk_count]

    # Create enhanced pie chart
    fig = go.Figure(data=[go.Pie(
        labels=risk_labels, 
        values=risk_values, 
        hole=0.2,
        hoverinfo='label+percent',  # Show percentage on hover
        textinfo='label+value+percent',  # Display label, value, and percentage inside the pie
        textfont=dict(size=15, color='white'),  # Customize text style inside the chart
        marker=dict(
            colors=['#FF4136', '#2ECC40'],  # Set custom colors for High and Low risk
            line=dict(color='black', width=2)  # Add border around the pie segments
        )
    )])

    # Update layout with enhanced visual features
    fig.update_layout(
        title="Risk Level Distribution",
        template="plotly_dark",
        showlegend=True,
        legend=dict(x=0.85, y=1, font=dict(size=12)),  # Position and size of legend
        width=600,  # Keep the width as per the requirement
        height=300,  # Keep the height as per the requirement
        margin=dict(t=40, b=40, l=40, r=40),  # Set margin for better spacing
      
    )
    
    st.plotly_chart(fig)



def make_clustered_risk_graph(indicator):
    # Get the current file's directory and form the absolute path for the CSV
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.abspath(os.path.join(base_dir, f'../models/clusters_{indicator}.csv'))
    
    # Load CSV data into a DataFrame
    df = pd.read_csv(csv_path)
    
    # Ensure the necessary columns are present
    if 'risk' not in df.columns or 'Assigned Cluster' not in df.columns or indicator not in df.columns:
        raise ValueError("CSV must contain 'risk', 'Assigned Cluster', and the selected indicator columns.")
    
    # Plot the clusters with the 'risk' values
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
    # Get the current file's directory and form the absolute path for the CSV
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.abspath(os.path.join(base_dir, f'../models/clusters_{indicator}.csv'))
    
    # Load CSV data into a DataFrame
    df = pd.read_csv(csv_path)
    # 3D Scatter Plot using Plotly
    fig = px.scatter_3d(df, 
                        x='name', 
                        y=indicator, 
                        z=indicator,  # Same indicator for Y and Z axis
                        color='risk',  # Optional: Color by country
                        title=f'3D Scatter Plot of {indicator} across Countries')
    
    # Update Layout for better aesthetics
    fig.update_layout(
        scene=dict(
            xaxis_title='Country',
            yaxis_title=indicator,
            zaxis_title=indicator
        ),
        template='plotly_dark',
             width=1500,  # Increase width
        height=1000,  # Increase height
      
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig)


def create_2d_scatter_plot(indicator):
    # Get the current file's directory and form the absolute path for the CSV
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.abspath(os.path.join(base_dir, f'../models/clusters_{indicator}.csv'))
    
    # Load CSV data into a DataFrame
    df = pd.read_csv(csv_path)
    
    # Check if necessary columns exist
    if indicator not in df.columns or 'risk' not in df.columns or 'name' not in df.columns:
        raise ValueError(f"CSV must contain the '{indicator}', 'risk', and 'name' columns.")
    
    # Ensure country and indicator columns are cleaned up (remove NaNs)
    df_cleaned = df.dropna(subset=[indicator])  # Drop rows where indicator is NaN
    
    # Create a scatter plot using Plotly Express
    fig = px.scatter(
        df_cleaned, 
        x='name', 
        y=indicator, 
        color='risk',  # Color by the risk column
        labels={'name': 'Country', indicator: indicator, 'risk': 'Risk Level'},
        title=f'2D Scatter Plot of {indicator} by Country and Risk Level'
    )
    
    # Update layout for aesthetics with a white background and a custom theme
    fig.update_layout(
        template='plotly',  # White background theme
        xaxis_title='Country',
        yaxis_title=indicator,
        width=1500,  # Increase width
        height=800,  # Increase height
    )
    
    # Display the plot in Streamlit
    st.plotly_chart(fig)