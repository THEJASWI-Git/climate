import streamlit as st
import pandas as pd
import numpy as np
import datetime
import random
import io

st.set_page_config(page_title="Environmental Monitoring Dashboard", layout="wide")

# -----------------------
# Helper: generate timestamps
# -----------------------
def generate_timestamps(hours: int):
    now = datetime.datetime.now()
    return [(now - datetime.timedelta(hours=i)).replace(minute=0, second=0, microsecond=0)
            for i in range(hours-1, -1, -1)]

# -----------------------
# Simulated datasets
# -----------------------
def generate_air_data(city: str, hours: int):
    ts = generate_timestamps(hours)
    data = []
    base_pm25 = {"Bangalore": 80, "Delhi": 140, "Mumbai": 90}.get(city, 80)
    for i, t in enumerate(ts):
        pm25 = max(5, int(base_pm25 + 30 * np.sin(i/3.0) + random.randint(-25, 25)))
        pm10 = max(10, int(pm25 * (1.2 + random.uniform(-0.2, 0.3))))
        co = round(max(0.1, random.uniform(0.3, 2.5) + (pm25/200)), 2)
        no2 = int(20 + pm25 * 0.3 + random.randint(-10, 20))
        so2 = int(5 + random.randint(0, 30))
        o3 = int(20 + random.randint(0, 100))
        aqi = int(min(500, (pm25 / 12) * 50 * random.uniform(0.9, 1.1)))
        data.append({
            "timestamp": t, "pm25": pm25, "pm10": pm10, "co": co,
            "no2": no2, "so2": so2, "o3": o3, "aqi": aqi
        })
    return pd.DataFrame(data)

def generate_water_data(city: str, hours: int):
    ts = generate_timestamps(hours)
    data = []
    base_tds = {"Bangalore": 200, "Delhi": 400, "Mumbai": 350}.get(city, 250)
    for i, t in enumerate(ts):
        ph = round(7 + random.uniform(-0.5, 0.6), 2)
        tds = int(max(50, base_tds + random.randint(-80, 120)))
        turbidity = round(max(0.5, random.uniform(0.5, 10.0)), 2)
        do = round(max(2.0, random.uniform(4.0, 9.0)), 2)
        nitrates = round(random.uniform(0.1, 10.0), 2)
        lead_ppb = round(random.uniform(0.0, 50.0), 2)
        data.append({
            "timestamp": t, "ph": ph, "tds_mg_per_l": tds, "turbidity_NTU": turbidity,
            "do_mg_per_l": do, "nitrates_mg_per_l": nitrates, "lead_ppb": lead_ppb
        })
    return pd.DataFrame(data)

def generate_soil_data(city: str, hours: int):
    ts = generate_timestamps(hours)
    data = []
    for i, t in enumerate(ts):
        ph = round(6 + random.uniform(-1.0, 1.0), 2)
        heavy_metals_ppm = round(random.uniform(0, 200), 2)
        pesticides_ppm = round(random.uniform(0, 5), 3)
        organic_matter_percent = round(random.uniform(1, 8), 2)
        data.append({
            "timestamp": t, "ph": ph, "heavy_metals_ppm": heavy_metals_ppm,
            "pesticides_ppm": pesticides_ppm, "organic_matter_%": organic_matter_percent
        })
    return pd.DataFrame(data)

def generate_noise_data(city: str, hours: int):
    ts = generate_timestamps(hours)
    data = []
    base_db = {"Bangalore": 60, "Delhi": 70, "Mumbai": 65}.get(city, 60)
    for i, t in enumerate(ts):
        db = int(max(30, base_db + random.randint(-15, 20) + (5 * np.sin(i/2.0))))
        peak_db = db + random.randint(0, 20)
        exposure = round(max(30, db * random.uniform(0.8, 1.2)), 1)
        data.append({"timestamp": t, "db": db, "peak_db": peak_db, "exposure_index": exposure})
    return pd.DataFrame(data)

# -----------------------
# Sidebar Navigation
# -----------------------
st.sidebar.title("🌍 Navigation")
page = st.sidebar.radio("Go to:", ["Dashboard", "README"])

if page == "Dashboard":
    # Dashboard Sidebar Controls
    city = st.sidebar.selectbox("Select City", ["Bangalore", "Delhi", "Mumbai", "Other"])
    category = st.sidebar.radio("Select Category", ["Air", "Water", "Soil", "Noise", "All"])
    hours = st.sidebar.selectbox("Time window", [24, 48, 72], index=0)
    download = st.sidebar.checkbox("Enable CSV download", value=True)
    st.sidebar.markdown("---")
    st.sidebar.caption("Demo app — using simulated data.\nTeam: Your Team Name")

    # Generate datasets
    air_df = generate_air_data(city, hours)
    water_df = generate_water_data(city, hours)
    soil_df = generate_soil_data(city, hours)
    noise_df = generate_noise_data(city, hours)

    # -----------------------
    # Dashboard Layout
    # -----------------------
    st.title("🌱 Environmental Monitoring Dashboard")
    st.subheader(f"{category} Monitoring — {city} — Last {hours} hours")

    # Define functions to display each panel
    def show_air_panel(df):
        st.header("Air Quality")
        latest = df.iloc[-1]
        cols = st.columns(4)
        cols[0].metric("AQI", latest["aqi"])
        cols[1].metric("PM2.5 (µg/m³)", latest["pm25"])
        cols[2].metric("PM10 (µg/m³)", latest["pm10"])
        cols[3].metric("CO (ppm)", latest["co"])
        with st.expander("Air Data Table"):
            st.dataframe(df)

    def show_water_panel(df):
        st.header("Water Quality")
        latest = df.iloc[-1]
        cols = st.columns(4)
        cols[0].metric("pH", latest["ph"])
        cols[1].metric("TDS (mg/L)", latest["tds_mg_per_l"])
        cols[2].metric("Turbidity (NTU)", latest["turbidity_NTU"])
        cols[3].metric("DO (mg/L)", latest["do_mg_per_l"])
        with st.expander("Water Data Table"):
            st.dataframe(df)

    def show_soil_panel(df):
        st.header("Soil Monitoring")
        latest = df.iloc[-1]
        cols = st.columns(4)
        cols[0].metric("pH", latest["ph"])
        cols[1].metric("Heavy Metals (ppm)", latest["heavy_metals_ppm"])
        cols[2].metric("Pesticides (ppm)", latest["pesticides_ppm"])
        cols[3].metric("Organic Matter (%)", latest["organic_matter_%"])
        with st.expander("Soil Data Table"):
            st.dataframe(df)

    def show_noise_panel(df):
        st.header("Noise Monitoring")
        latest = df.iloc[-1]
        cols = st.columns(3)
        cols[0].metric("Current dB", latest["db"])
        cols[1].metric("Peak dB", latest["peak_db"])
        cols[2].metric("Exposure Index", latest["exposure_index"])
        with st.expander("Noise Data Table"):
            st.dataframe(df)

    # Render based on category
    if category == "Air":
        show_air_panel(air_df)
    elif category == "Water":
        show_water_panel(water_df)
    elif category == "Soil":
        show_soil_panel(soil_df)
    elif category == "Noise":
        show_noise_panel(noise_df)
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["Air", "Water", "Soil", "Noise"])
        with tab1: show_air_panel(air_df)
        with tab2: show_water_panel(water_df)
        with tab3: show_soil_panel(soil_df)
        with tab4: show_noise_panel(noise_df)

elif page == "README":
    st.title("📖 Project README")
    st.markdown("""
    ## 🌱 Environmental Monitoring Dashboard

    A Streamlit-based app to monitor **Air, Water, Soil, and Noise Pollution** for different cities.

    ### 🚀 Features
    - Real-time (simulated) environmental data
    - Trend charts, alerts, and metrics
    - CSV data download
    - Eco-friendly UI for awareness

    ### 🛠️ How to Run
    ```bash
    pip install -r requirements.txt
    streamlit run app.py
    ```

    ### 👨‍💻 Team
    - Member 1  
    - Member 2  
    - Member 3  
    - Member 4  

    """)
