import streamlit as st
import requests
from datetime import datetime

# הגדרות הרצליה
LAT, LON = 32.1615, 34.7938

st.set_page_config(page_title="דשבורד מרינה", layout="wide")

def get_data():
    # הכתובות הרשמיות והיציבות ביותר
    w_url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m,wind_speed_10m,wind_direction_10m&forecast_days=1"
    m_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={LAT}&longitude={LON}&hourly=wave_height,swell_wave_height,swell_wave_period&cell_selection=sea&forecast_days=1"
    
    try:
        # הוספנו Headers כדי להיראות כמו דפדפן רגיל - זה מונע חסימות אוטומטיות!
        headers = {'User-Agent': 'Mozilla/5.0'}
        w_res = requests.get(w_url, headers=headers).json()
        m_res = requests.get(m_url, headers=headers).json()
        
        return w_res.get('hourly'), m_res.get('hourly')
    except:
        return None, None

st.title("🌊 תחזית מרינה הרצליה")

if st.button("🔄 רענן נתונים"):
    w, m = get_data()
    if w and m:
        st.write("תחזית ל-24 שעות:")
        # הצגת נתונים בסיסית ומהירה
        st.table(pd.DataFrame({
            "שעה": [datetime.fromisoformat(t).strftime("%H:%M") for t in w['time'][::3]],
            "גלים (מ)": m['wave_height'][::3],
            "סוול (מ)": m['swell_wave_height'][::3],
            "רוח (קמ\"ש)": [int(x) for x in w['wind_speed_10m'][::3]]
        }))
    else:
        st.error("השרת עדיין חוסם זמנית. נסה להוסיף 'Headers' לקוד (בוצע בקוד זה).")
