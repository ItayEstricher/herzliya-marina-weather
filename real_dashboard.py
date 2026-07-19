import streamlit as st
import requests
import pandas as pd

API_KEY = st.secrets["WEATHER_API_KEY"]
LAT, LON = 32.1615, 34.7938

st.set_page_config(page_title="דשבורד מרינה", layout="wide")

# פונקציה לתיאור סוג הגלים לפי גובה
def get_wave_desc(h):
    if h < 0.5: return "קרסול"
    if h < 1.0: return "חזה"
    return "ראש"

st.markdown("""
<style>
    .t-header { display: grid; grid-template-columns: 0.5fr 1fr 1fr 1fr 1fr 1fr 1fr; background: #1da1f2; color: white; padding: 10px; font-weight: bold; text-align: center; font-size: 13px; }
    .t-row { display: grid; grid-template-columns: 0.5fr 1fr 1fr 1fr 1fr 1fr 1fr; align-items: center; text-align: center; padding: 10px; border-bottom: 1px solid #ddd; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def get_data():
    url = f"https://api.weatherapi.com/v1/marine.json?key={API_KEY}&q={LAT},{LON}&days=1"
    res = requests.get(url).json()
    return res['forecast']['forecastday'][0]['hour']

st.title("🌊 תחזית מרינה הרצליה המלאה")

data = get_data()
if data:
    # כותרות הטבלה
    st.markdown('''<div class="t-header">
        <div>שעה</div><div>טמפ'</div><div>רוח (קמ"ש)</div><div>כיוון רוח</div>
        <div>גלים</div><div>סוול</div><div>מחזור</div></div>''', unsafe_allow_html=True)
    
    for h in data[::3]: # כל 3 שעות
        wave_h = h['swell_ht_mt'] # גובה גלים משולב
        swell_h = h['swell_ht_mt'] # סוול
        period = h['swell_period_secs'] # מחזור
        
        st.markdown(f'''
        <div class="t-row">
            <div>{h['time'].split(' ')[1]}</div>
            <div>{h['temp_c']}°C</div>
            <div>{h['wind_kph']}</div>
            <div>{h['wind_dir']}</div>
            <div style="font-weight:bold;">{get_wave_desc(wave_h)}</div>
            <div>{swell_h} מ'</div>
            <div>{period} שנ'</div>
        </div>''', unsafe_allow_html=True)
else:
    st.error("לא ניתן למשוך נתונים.")
