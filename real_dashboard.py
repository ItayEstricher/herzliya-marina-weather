import streamlit as st
import requests
from datetime import datetime

LAT, LON = 32.1615, 34.7938

st.set_page_config(page_title="דשבורד מרינה הרצליה", layout="wide")

def get_data():
    # הוספנו &cell_selection=sea כדי להבטיח נתוני ים
    w_url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m,wind_speed_10m,wind_direction_10m&forecast_days=1"
    m_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={LAT}&longitude={LON}&hourly=wave_height,swell_wave_height,swell_wave_period,wave_direction&cell_selection=sea&forecast_days=1"
    
    try:
        w_res = requests.get(w_url).json()
        m_res = requests.get(m_url).json()
        
        if 'hourly' not in w_res or 'hourly' not in m_res:
            st.error(f"שגיאת שרת: {w_res.get('reason', 'Unknown')} / {m_res.get('reason', 'Unknown')}")
            return None, None
        return w_res['hourly'], m_res['hourly']
    except Exception as e:
        st.error(f"שגיאת תקשורת: {e}")
        return None, None

st.title("🌊 תחזית מרינה הרצליה")

if st.button("🔄 רענן נתונים"):
    w, m = get_data()
    if w and m:
        # טבלה נקייה
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
        st.warning("לא הצלחנו למשוך נתונים. השרת של Open-Meteo ייתכן ועמוס.")
