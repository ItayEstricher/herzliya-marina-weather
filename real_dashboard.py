import streamlit as st
import requests
import pandas as pd

# הגדרות הרצליה
API_KEY = st.secrets["WEATHER_API_KEY"]
LAT, LON = 32.1615, 34.7938

st.set_page_config(page_title="דשבורד מרינה", layout="wide")

# CSS לעיצוב הטבלה
st.markdown("""
<style>
    .t-header { display: grid; grid-template-columns: repeat(4, 1fr); background: #1da1f2; color: white; padding: 10px; font-weight: bold; text-align: center; border-radius: 5px; }
    .t-row { display: grid; grid-template-columns: repeat(4, 1fr); align-items: center; text-align: center; padding: 10px; border-bottom: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def get_data():
    url = f"https://api.weatherapi.com/v1/marine.json?key={API_KEY}&q={LAT},{LON}&days=1"
    res = requests.get(url).json()
    return res['forecast']['forecastday'][0]['hour']

st.title("🌊 תחזית מרינה הרצליה")

data = get_data()
if data:
    # הצגת הטבלה
    st.markdown('<div class="t-header"><div>שעה</div><div>טמפ\'</div><div>רוח (קמ"ש)</div><div>גלים (מ\')</div></div>', unsafe_allow_html=True)
    
    for h in data[::3]: # כל 3 שעות
        st.markdown(f'''
        <div class="t-row">
            <div>{h['time'].split(' ')[1]}</div>
            <div>{h['temp_c']}°C</div>
            <div>{h['wind_kph']}</div>
            <div style="font-weight:bold; color:#0077bb;">{h['swell_ht_mt']} מ'</div>
        </div>''', unsafe_allow_html=True)
else:
    st.error("לא הצלחנו למשוך נתונים. בדוק את ה-API Key ב-Secrets.")
