import pandas as pd

from functions import  *

st.set_page_config(page_title="Regression Analysis", page_icon="📊",layout="wide")

st.title("Regression Analysis of all indicators")

col1, col2 = st.columns([2, 3])


def predict_all_indicators():

    df1 = pd.read_csv(f'./application/ClusterDataForTimeSeries.csv')
    df2 = pd.read_csv('./application/data.csv')

    countries = df1['name'].unique()   
    regions = df2['who_region'].unique()

    selected_region = st.selectbox("Select Region", regions)
    countries = df2[df2['who_region'] == selected_region]['name'].unique()
    selected_country = st.selectbox("Select Country", countries)
    selected_year = st.slider("Select Year", 2024, 2050, 2024)

    st.write(f"Selected Year: {selected_year}")

    target_indicators = ['Adult obesity%', 'Tobacco use%', 'Alcohol consumption',
                         'Number of new HIV infections', 'Suicide deaths', 'Prevalence of hypertension%']

    if "predictions" not in st.session_state:
        st.session_state["predictions"] = None

    if st.button("Predict"):
        st.session_state["predictions"] = get_all_predictions(target_indicators, selected_country, selected_year)

    if st.session_state["predictions"]:
        predictions = st.session_state["predictions"]
        st.write("Predictions:")
        st.dataframe(predictions_table(predictions, 0))
    return  st.session_state["predictions"]

predictions={}
with col1:
    predictions=predict_all_indicators()

with col2:
    if predictions:
        interactive_prediction_plot(predictions)
        create_risk_pie_chart(predictions)


if predictions:
    create_decision_making_plot(predictions)
   
   