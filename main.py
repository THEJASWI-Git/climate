# app.py
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
# Helper: simulated datasets
# -----------------------
def generate_air_data(city: str, hours: int):
    ts = generate_timestamps(hours)
    data = []
    base_pm25 = {"Bangalore": 80, "Delhi": 140, "Mumbai": 90}.get(city, 80)
    for i, t in enumerate(ts):
        # add diurnal pattern and randomness
        pm25 = max(5, int(base_pm25 + 30 * np.sin(i/3.0) + random.randint(-25, 25)))
        pm10 = max(10, int(pm25 * (1.2 + random.uniform(-0.2, 0.3))))
        co = round(max(0.1, random.uniform(0.3, 2.5) + (pm25/200)), 2)
        no2 = int(20 + pm25 * 0.3 + random.randint(-10, 20))
        so2 = int(5 + random.randint(0, 30))
        o3 = int(20 + random.randint(0, 100))
        aqi = int(min(500, (pm25 / 12) * 50 * random.uniform(0.9, 1.1)))  # simple proxy
        data.append({
            "timestamp": t, "pm25": pm25, "pm10": pm10, "co": co,
            "no2": no2, "so2": so2, "o3": o3, "aqi": aqi
        })
    return pd.DataFrame(data)

def generate_water_data(city: str, hours: int):
    # we'll simulate daily-ish readings but keep hourly length for chart compatibility
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
        heavy_metals_ppm = round(random.uniform(0, 200), 2)  # composite indicator
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
# Sidebar: controls
# -----------------------
st.sidebar.title("Controls")
city = st.sidebar.selectbox("Select City", ["Bangalore", "Delhi", "Mumbai", "Other"])
category = st.sidebar.radio("Select Category", ["Air", "Water", "Soil", "Noise", "All"])
hours = st.sidebar.selectbox("Time window", [24, 48, 72], index=0)  # last n hours
download = st.sidebar.checkbox("Enable CSV download", value=True)
st.sidebar.markdown("---")
st.sidebar.markdown("Built for hackathon demo — currently using simulated data.")
st.sidebar.markdown("Team: Your Team Name")

# -----------------------
# Generate data based on selection
# -----------------------
air_df = generate_air_data(city, hours)
water_df = generate_water_data(city, hours)
soil_df = generate_soil_data(city, hours)
noise_df = generate_noise_data(city, hours)

# -----------------------
# Helper: CSV download
# -----------------------
def df_to_csv_bytes(dfs: dict):
    # Combine with sheet separators via CSVs in a single bytes buffer
    buffer = io.StringIO()
    for name, df in dfs.items():
        buffer.write(f"### {name} ###\n")
        df.to_csv(buffer, index=False)
        buffer.write("\n")
    return buffer.getvalue().encode()

# -----------------------
# Layout: Title
# -----------------------
st.title("🌱 Environmental Monitoring Dashboard")
st.subheader(f"{category} Monitoring — {city} — Last {hours} hours")

# -----------------------
# Display appropriate panels
# -----------------------
def show_air_panel(df):
    st.header("Air Quality")
    # Latest metrics
    latest = df.iloc[-1]
    cols = st.columns(4)
    cols[0].metric("AQI", latest["aqi"])
    cols[1].metric("PM2.5 (µg/m³)", latest["pm25"])
    cols[2].metric("PM10 (µg/m³)", latest["pm10"])
    cols[3].metric("CO (ppm)", latest["co"])
    # Secondary metrics row
    cols2 = st.columns(4)
    cols2[0].metric("NO₂ (ppb)", latest["no2"])
    cols2[1].metric("SO₂ (ppb)", latest["so2"])
    cols2[2].metric("O₃ (ppb)", latest["o3"])
    cols2[3].metric("Last Update", latest["timestamp"].strftime("%Y-%m-%d %H:%M"))

    # chart selector
    st.markdown("**Select pollutants to plot**")
    pollutants = st.multiselect("Pollutants", ["aqi", "pm25", "pm10", "co", "no2", "so2", "o3"],
                                default=["pm25", "pm10"])
    if len(pollutants) == 0:
        st.info("Select at least one pollutant to show the chart.")
    else:
        st.line_chart(df.set_index("timestamp")[pollutants])

    # Alerts
    alert_msg = []
    if latest["pm25"] > 150:
        alert_msg.append("PM2.5 is above 150 (Unhealthy).")
    if latest["pm10"] > 200:
        alert_msg.append("PM10 is above 200 (Unhealthy).")
    if latest["aqi"] > 150:
        alert_msg.append("AQI is above 150 (Unhealthy).")
    if alert_msg:
        st.error("⚠️ " + " ".join(alert_msg))
    else:
        st.success("✅ Air quality within safe thresholds (per demo thresholds).")

    # show raw table expandable
    with st.expander("Show air data table"):
        st.dataframe(df)

def show_water_panel(df):
    st.header("Water Quality")
    latest = df.iloc[-1]
    cols = st.columns(4)
    cols[0].metric("pH", latest["ph"])
    cols[1].metric("TDS (mg/L)", latest["tds_mg_per_l"])
    cols[2].metric("Turbidity (NTU)", latest["turbidity_NTU"])
    cols[3].metric("Dissolved O₂ (mg/L)", latest["do_mg_per_l"])

    cols2 = st.columns(3)
    cols2[0].metric("Nitrates (mg/L)", latest["nitrates_mg_per_l"])
    cols2[1].metric("Lead (ppb)", latest["lead_ppb"])
    cols2[2].metric("Last Update", latest["timestamp"].strftime("%Y-%m-%d %H:%M"))

    # Chart selector
    st.markdown("**Select water parameters to plot**")
    params = st.multiselect("Water params", ["ph", "tds_mg_per_l", "turbidity_NTU", "do_mg_per_l", "nitrates_mg_per_l", "lead_ppb"],
                            default=["tds_mg_per_l", "turbidity_NTU"])
    if len(params) == 0:
        st.info("Select at least one parameter to show the chart.")
    else:
        st.line_chart(df.set_index("timestamp")[params])

    # Alerts (demo thresholds)
    alert_msg = []
    if latest["ph"] < 6.5 or latest["ph"] > 8.5:
        alert_msg.append("pH outside safe range (6.5-8.5).")
    if latest["tds_mg_per_l"] > 1000:
        alert_msg.append("TDS is very high (>1000 mg/L).")
    if latest["lead_ppb"] > 10:
        alert_msg.append("Lead concentration > 10 ppb (unsafe).")
    if alert_msg:
        st.error("⚠️ " + " ".join(alert_msg))
    else:
        st.success("✅ Water parameters within demo safe thresholds.")

    with st.expander("Show water data table"):
        st.dataframe(df)

def show_soil_panel(df):
    st.header("Soil Monitoring")
    latest = df.iloc[-1]
    cols = st.columns(4)
    cols[0].metric("pH", latest["ph"])
    cols[1].metric("Heavy metals (ppm)", latest["heavy_metals_ppm"])
    cols[2].metric("Pesticides (ppm)", latest["pesticides_ppm"])
    cols[3].metric("Organic matter (%)", latest["organic_matter_%"])

    st.markdown("**Select soil parameters to plot**")
    params = st.multiselect("Soil params", ["ph", "heavy_metals_ppm", "pesticides_ppm", "organic_matter_%"],
                            default=["heavy_metals_ppm", "organic_matter_%"])
    if len(params) == 0:
        st.info("Select at least one parameter to show the chart.")
    else:
        st.line_chart(df.set_index("timestamp")[params])

    alert_msg = []
    if latest["heavy_metals_ppm"] > 100:
        alert_msg.append("High heavy metals in soil (>100 ppm).")
    if latest["pesticides_ppm"] > 1:
        alert_msg.append("Pesticide residue high (>1 ppm).")
    if alert_msg:
        st.error("⚠️ " + " ".join(alert_msg))
    else:
        st.success("✅ Soil parameters look OK for demo thresholds.")

    with st.expander("Show soil data table"):
        st.dataframe(df)

def show_noise_panel(df):
    st.header("Noise Monitoring")
    latest = df.iloc[-1]
    cols = st.columns(3)
    cols[0].metric("Current dB", latest["db"])
    cols[1].metric("Peak dB (last hour)", latest["peak_db"])
    cols[2].metric("Exposure index", latest["exposure_index"])

    st.markdown("**Noise trend**")
    st.line_chart(df.set_index("timestamp")[["db", "peak_db"]])

    alert_msg = []
    if latest["db"] > 70 or latest["peak_db"] > 90:
        alert_msg.append("Noise level high (dB > 70).")
    if latest["exposure_index"] > 85:
        alert_msg.append("Exposure index high.")
    if alert_msg:
        st.error("⚠️ " + " ".join(alert_msg))
    else:
        st.success("✅ Noise levels within demo thresholds.")

    with st.expander("Show noise data table"):
        st.dataframe(df)

# -----------------------
# Render based on selection
# -----------------------
if category == "Air":
    show_air_panel(air_df)
elif category == "Water":
    show_water_panel(water_df)
elif category == "Soil":
    show_soil_panel(soil_df)
elif category == "Noise":
    show_noise_panel(noise_df)
else:  # All
    # show in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Air", "Water", "Soil", "Noise"])
    with tab1:
        show_air_panel(air_df)
    with tab2:
        show_water_panel(water_df)
    with tab3:
        show_soil_panel(soil_df)
    with tab4:
        show_noise_panel(noise_df)

# -----------------------
# CSV Download (combined or per category)
# -----------------------
if download:
    st.markdown("---")
    st.subheader("Export Data")
    if category == "All":
        combined = {"Air": air_df, "Water": water_df, "Soil": soil_df, "Noise": noise_df}
        csv_bytes = df_to_csv_bytes(combined)
        st.download_button("Download all data (CSV)", data=csv_bytes, file_name=f"{city}_env_data_last_{hours}h.csv", mime="text/csv")
    else:
        single_map = {"Air": air_df, "Water": water_df, "Soil": soil_df, "Noise": noise_df}
        df_sel = single_map[category]
        csv = df_sel.to_csv(index=False).encode()
        st.download_button(f"Download {category} data (CSV)", data=csv, file_name=f"{city}_{category.lower()}_last_{hours}h.csv", mime="text/csv")

# -----------------------
# Footer
# -----------------------
st.markdown("---")
st.caption("Demo app: data simulated for hackathon. Replace data generators with real API/IoT ingestion when ready.")
