
import streamlit as st

st.set_page_config(page_title="Environmental Dashboard", layout="wide")

# Sidebar navigation
page = st.sidebar.radio("Navigate", ["Dashboard", "README"])

if page == "Dashboard":
    st.title("🌱 Environmental Monitoring Dashboard")
    st.write("Select a category from the sidebar to view data.")
    # 👉 (Here goes your existing Air, Water, Soil, Noise code)

elif page == "README":
    st.title("📖 Project README")
    st.markdown("""
    ## 🌱 Environmental Monitoring Dashboard
    This app monitors **Air, Water, Soil, and Noise Pollution**.

    ### 🚀 Features
    - Real-time (simulated) environmental data.
    - Trend charts, alerts, and metrics.
    - CSV data download for further analysis.
    - Eco-friendly UI for awareness campaigns.

    ### 🛠️ How to Run
    ```bash
    pip install -r requirements.txt
    streamlit run app.py
    ```

    ### 👨‍💻 Team
    - THEJASWI
    - CHIRANTH
    - MADHUSUDHAN
    - LIKHITH
    """)
