import streamlit as st
from pages import home, about, ai_chat, regression, clustering

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to", ["Home", "About", "AI Chat", "Regression", "Clustering"])

# Load selected page
if page == "Home":
    home.show()
elif page == "About":
    about.show()
elif page == "AI Chat":
    ai_chat.show()
elif page == "Regression":
    regression.show()
elif page == "Classification":
    clustering.show()
