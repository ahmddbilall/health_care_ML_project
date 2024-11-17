import pandas as pd

from functions import  *

st.header("Regression Analysis")

# Divide page into two columns
col1, col2 = st.columns([2, 3])


def predict_all_indicators():
    df1 = pd.read_csv('../models/pklFiles/ClusterDataForTimeSeries.csv')
    df2 = pd.read_csv('../application/data.csv')

    countries = df1['name'].unique()   
    regions = df2['who_region'].unique()

    selected_region = st.selectbox("Select Region", regions)
    countries = df2[df2['who_region'] == selected_region]['name'].unique()
    selected_country = st.selectbox("Select Country", countries)
    selected_year = st.slider("Select Year", 2024, 2050, 2024)

    # Fetch population for the selected country and year
    
    
    st.write(f"Selected Year: {selected_year}")

    target_indicators = ['Adult obesity%', 'Tobacco use%', 'Alcohol consumption',
                         'Number of new HIV infections', 'Suicide deaths', 'Prevalence of hypertension%']

    if "predictions" not in st.session_state:
        st.session_state["predictions"] = None

    # When button is clicked, call prediction function
    if st.button("Predict"):
        st.session_state["predictions"] = get_all_predictions(target_indicators, selected_country, selected_year)

    # Display the predictions if available
    if st.session_state["predictions"]:
        predictions = st.session_state["predictions"]
        st.write("Predictions:")
        # Assuming predictions_table function is defined to format the predictions in a table
        st.dataframe(predictions_table(predictions, 0))
    return  st.session_state["predictions"]

# Call the prediction section in the first column
predictions={}
with col1:
    predictions=predict_all_indicators()

# Decision-making section in the second column
with col2:
    if predictions:
        interactive_prediction_plot(predictions)
        create_risk_pie_chart(predictions)


if predictions:
    create_decision_making_plot(predictions)
   
   