import os
import warnings

# Suppress TensorFlow and oneDNN logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Only critical TensorFlow errors
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN optimization messages

# Suppress Python warnings
warnings.filterwarnings('ignore')

try:
    import tensorflow as tf
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
except ImportError:
    print("TensorFlow not installed.")
except AttributeError:
    pass  # Ignore for newer TensorFlow versions

# Import Plotly
try:
    import plotly.express as px
    print("Plotly is available for interactive plots.")
except ImportError:
    print("Plotly not installed. Run `pip install plotly` to enable interactive plots.")

import streamlit as st
from pages import Home, About, Ai_chat, Clustering, Collective_Regression, Single_Regression

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to", ["Home", "AI Chat", "Regression", "Clustering", "Regression Analysis", "About"])

if page == "Home":
    Home.show()
elif page == "About":
    About.show()
elif page == "AI Chat":
    Ai_chat.show()
elif page == "Regression":
    Single_Regression.show()
elif page == "Clustering":  # Corrected this line
    Clustering.show()
elif page == "Regression Analysis":
    Collective_Regression.show()
