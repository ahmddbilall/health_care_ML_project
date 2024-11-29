
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import pandas as pd

st.set_page_config(page_title="Visulization", page_icon="📊",layout="wide")


def generate_income_level_chart(df):
    # Group by 'who_region' and 'world_bank_income_level', and count occurrences
    unique_countries = df[['who_region', 'world_bank_income_level', 'name']].drop_duplicates()

# Count the unique countries for each combination of WHO region and income level
    region_income_country_count = unique_countries.groupby(['who_region', 'world_bank_income_level']).size().unstack(fill_value=0)

     
    # Reset index for plotting with Plotly
    region_income_country_count.reset_index(inplace=True)

    # Create the stacked bar chart using Plotly
    fig = px.bar(region_income_country_count,
                 x='who_region',
                 y=region_income_country_count.columns[1:],  # all income levels columns
                 title='Income Levels Distribution Across WHO Regions',
                 labels={'who_region': 'WHO Region', 'value': 'Number of Countries'},
                 text_auto=True,
                 barmode='stack',  # Stack the bars
                 category_orders={'who_region': region_income_country_count['who_region'].unique()},
                 height=600)

    # Return the Plotly figure
    return fig

def plot_grouped_health_expenditure(df, group_by_column='world_bank_income_level'):
    # Group the dataframe by the specified column and calculate the mean of 'health_expenditure'
    group_data = df.groupby(group_by_column)['health_expenditure'].mean().reset_index()

    # Create a bar chart using Plotly
    fig = go.Figure()

    # Add traces (bars) for each unique group
    fig.add_trace(go.Bar(
        x=group_data[group_by_column],  # x-axis: the group names (income levels or regions)
        y=group_data['health_expenditure'],  # y-axis: the mean health expenditure
        name='Health Expenditure by ' + group_by_column,
        marker_color='rgb(26, 118, 255)'  # color for the bars
    ))

    # Update layout for the chart
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
        bargap=0.15,  # gap between bars of adjacent location coordinates.
        bargroupgap=0.1  # gap between bars of the same location coordinate.
    )

    return fig

df = pd.read_csv('./application/data.csv')  # Adjust path to your dataset


# Create 2 full-width columns per row (6 boxes total, 2 per row)
col1, col2 = st.columns([8, 3]) # Row 1 with 2 columns
col3, col4 = st.columns(2)  # Row 2 with 2 columns
col5, col6 = st.columns(2)  # Row 3 with 2 columns

# Display a graph in each column
with col1:
    st.write("**Graph 1**")
    fig1 = generate_income_level_chart(df)
    st.plotly_chart(fig1)

with col2:
    st.write("**Graph 2**")
    fig2 = plot_grouped_health_expenditure(df)
    st.plotly_chart(fig2)
    
with col3:
    st.write("**Graph 3**")
    st.write("This is a placeholder for Graph 3")
