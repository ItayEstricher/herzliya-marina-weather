import streamlit as st
import requests
from datetime import datetime

# הגדרות הרצליה
LAT, LON = 32.1615, 34.7938

st.set_page_config(page_title="דשבורד מרינה הרצליה", layout="wide")

def get_data():
    # שימוש ב-API עם מפתח אישי מה-Secrets
    key = st.secrets["OPEN_METEO_KEY"]
    w_url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m,wind_speed_10m,wind_direction_10m&forecast_days=1&apikey={key}"
    m_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={LAT}&longitude={LON}&hourly=wave_height,swell_wave_height,swell_wave_period,wave_direction&cell_selection=sea&forecast_days=1&apikey={key}"
    
    try:
        w_data = requests.get(w_url).json()
        m_data = requests.get(m_url).json()
        return w_data.get('hourly'), m_data.get('hourly')
    except:
        return None, None

st.title("🌊 תחזית מרינה הרצליה")

if st.button("🔄 רענן נתונים"):
    w, m = get_data()
    if w and m:
        st.write("### תחזית ל-24 שעות הקרובות")
        table_data = []
        for i in range(0, 24, 3):
            table_data.append({
                "שעה": datetime.fromisoformat(w['time'][i]).strftime("%H:%M"),
                "גלים (מ')": m['wave_height'][i],
                "סוול (מ')": m['swell_wave_height'][i],
                "רוח (קמ\"ש)": int(w['wind_speed_10m'][i])
            })
        st.table(table_data)
    else:
        st.error("שגיאה במשיכת הנתונים. וודא שהמפתח ב-Secrets תקין.")
