import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# הגדרות הרצליה
LAT, LON = 32.1615, 34.7938

st.set_page_config(page_title="דשבורד מרינה - OpenMeteo", layout="centered")

def get_marine_data():
    # כתובת ה-API של Open-Meteo לתחזית ימית
    url = "https://marine-api.open-meteo.com/v1/marine"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "hourly": ["wave_height", "swell_wave_height", "swell_wave_period", "wave_direction"],
        "daily": ["wave_height_max"],
        "timezone": "auto",
        "forecast_days": 7
    }
    response = requests.get(url, params=params)
    return response.json()

st.title("🌊 מרינה הרצליה - תחזית ימית")

if st.button("🔄 טען נתוני ים"):
    data = get_marine_data()
    hourly = data['hourly']
    
    # בניית טבלה נוחה
    df = pd.DataFrame({
        "שעה": [datetime.fromisoformat(t).strftime("%H:%M") for t in hourly['time'][:12]],
        "גובה גלים (מ')": hourly['wave_height'][:12],
        "גובה סוול (מ')": hourly['swell_wave_height'][:12],
        "זמן סוול (שניות)": hourly['swell_wave_period'][:12]
    })
    
    st.dataframe(df, use_container_width=True)
    st.success("הנתונים נמשכו בהצלחה מ-Open-Meteo!")
