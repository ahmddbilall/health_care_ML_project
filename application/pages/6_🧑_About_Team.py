import streamlit as st
from PIL import Image

st.set_page_config(page_title="About the Team", page_icon=":guardsman:", layout="wide")

st.title("About the Team")

st.markdown("""
    We are a team of four students from FAST NUCES Lahore. 
    This project is our final project for the course Data Analytics and Visualization (DAV), and we have worked collaboratively to develop this. 
    Each of us contributed equally to the development, research, and implementation of various aspects of the project.
""")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.image("./application/bilal.jpg", width=150)  
    st.markdown("**Bilal Ahmad**")
    st.markdown("[GitHub](https://github.com/ahmddbilall) | [LinkedIn](https://www.linkedin.com/in/ahmddbilall/)") 

with col2:
    st.image("./application/umair.jpeg", width=150)  # Replace with the image path of team member 2
    st.markdown("**Umair Imran**")
    st.markdown("[GitHub](https://github.com/umairimran) | [LinkedIn](https://www.linkedin.com/in/muhammad-umair-imran-7919361b0/)")  # Replace with actual URLs

with col3:
    st.image("./application/najam.jpeg", width=150)  # Replace with the image path of team member 3
    st.markdown("**Najam Ul Islam Saeed**")
    st.markdown("[GitHub](https://github.com/Najam266) | [LinkedIn](https://www.linkedin.com/in/najamulislam-saeed-4a38762a4/)")  # Replace with actual URLs

with col4:
    st.image("./application/shahzad.jpeg", width=150)  # Replace with the image path of team member 4
    st.markdown("**Shahzad Waris**")
    st.markdown("[GitHub](https://github.com/meshahzad92) | [LinkedIn](https://www.linkedin.com/in/shahzad-waris-74ab8b2a8/)")  # Replace with actual URLs

# Footer (Optional)
st.markdown("---")
st.markdown("""
    This project was developed as part of our final year course in Data Analytics and Visualization (DAV) at FAST NUCES Lahore. 
    The project demonstrates our collective efforts in utilizing advanced data analytics and machine learning techniques.
""")
