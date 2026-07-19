import streamlit as st
import requests
import math
from datetime import datetime

# הגדרות הרצליה
LAT, LON = 32.1615, 34.7938

st.set_page_config(page_title="דשבורד מרינה הרצליה", page_icon="🌊", layout="centered")

# עיצוב CSS המקצועי
st.markdown("""
<style>
    body { direction: rtl; font-family: 'Segoe UI', sans-serif; }
    .stApp { background-color: #f0f4f8; }
    .top-header { background: #1da1f2; color: white; padding: 20px; text-align: center; font-size: 28px; font-weight: 700; border-radius: 10px 10px 0 0; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); }
    .table-container { background: white; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); overflow: hidden; margin-top: 20px; }
    .t-header { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; background: #f8f9fa; padding: 15px; font-weight: bold; text-align: center; border-bottom: 2px solid #eee; }
    .t-row { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; align-items: center; text-align: center; padding: 15px; border-bottom: 1px solid #f1f1f1; }
    .wave-box { background-color: #0077bb; color: white; padding: 10px; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def get_marine_data():
    url = "https://marine-api.open-meteo.com/v1/marine"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "hourly": ["wave_height", "swell_wave_height", "swell_wave_period"],
        "timezone": "auto",
        "forecast_days": 1
    }
    response = requests.get(url, params=params)
    return response.json()

st.markdown('<div class="top-header">הרצליה - מרינה 🌊</div>', unsafe_allow_html=True)

if st.button("🔄 רענן נתונים ימיים"):
    with st.spinner("מושך נתונים..."):
        try:
            data = get_marine_data()
            hourly = data['hourly']
            
            # בניית הטבלה כ-String פשוט
            html = '<div class="table-container"><div class="t-header"><div>שעה</div><div>גלים</div><div>סוול</div><div>מחזור</div></div>'
            
            for i in range(0, 24, 3):
                time_val = datetime.fromisoformat(hourly['time'][i]).strftime("%H:%M")
                wave = hourly['wave_height'][i]
                swell = hourly['swell_wave_height'][i]
                period = hourly['swell_wave_period'][i]
                
                html += f'''
                <div class="t-row">
                    <div style="font-weight:bold;">{time_val}</div>
                    <div class="wave-box">{wave} מ'</div>
                    <div style="color:#0077bb; font-weight:bold;">{swell} מ'</div>
                    <div>{period} שנ'</div>
                </div>'''
            
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)
            st.success("הנתונים עודכנו!")
        except Exception as e:
            st.error(f"שגיאה: {e}")
