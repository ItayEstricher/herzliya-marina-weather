import streamlit as st
import requests
from datetime import datetime

# הגדרות הרצליה
LAT, LON = 32.1615, 34.7938

st.set_page_config(page_title="דשבורד מרינה הרצליה", page_icon="🌊", layout="wide")

# CSS לעיצוב
st.markdown("""
<style>
    body { direction: rtl; font-family: 'Segoe UI', sans-serif; }
    .t-header { display: grid; grid-template-columns: 0.5fr 1fr 1fr 1fr 1fr 1fr 1fr; background: #f8f9fa; padding: 12px; font-weight: bold; text-align: center; border-bottom: 2px solid #ddd; }
    .t-row { display: grid; grid-template-columns: 0.5fr 1fr 1fr 1fr 1fr 1fr 1fr; align-items: center; text-align: center; padding: 12px; border-bottom: 1px solid #eee; }
    .wind-box { padding: 5px; border-radius: 5px; color: white; font-weight: bold; background: #27ae60; }
</style>
""", unsafe_allow_html=True)

def get_wave_desc(h):
    if h < 0.5: return "קרסול"
    if h < 1.0: return "חזה"
    return "ראש"

def get_dir(deg):
    if deg is None: return "-"
    dirs = ["צפונית", "צפון-מזרחית", "מזרחית", "דרום-מזרחית", "דרומית", "דרום-מערבית", "מערבית", "צפון-מערבית"]
    return dirs[int((deg + 22.5) % 360 / 45)]

def get_data():
    try:
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m,wind_speed_10m,wind_direction_10m&forecast_days=1"
        m_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={LAT}&longitude={LON}&hourly=wave_height,swell_wave_height,swell_wave_period&forecast_days=1"
        
        w_data = requests.get(w_url).json()
        m_data = requests.get(m_url).json()
        
        if 'hourly' not in w_data or 'hourly' not in m_data:
            return None, None
        return w_data['hourly'], m_data['hourly']
    except:
        return None, None

st.title("🌊 תחזית מרינה הרצליה")

if st.button("🔄 רענן נתונים"):
    with st.spinner("מושך נתונים..."):
        w, m = get_data()
        
        if w and m:
            html = '<div class="t-header"><div>שעה</div><div>גובה (ס"מ)</div><div>סוג גלים</div><div>סוול (מ')</div><div>מחזור</div><div>רוח (קמ"ש)</div><div>כיוון</div></div>'
            
            for i in range(6, 20, 3):
                time = datetime.fromisoformat(w['time'][i]).strftime("%H:%M")
                wave_m = m['wave_height'][i] or 0
                wave_cm = int(wave_m * 100)
                swell = m['swell_wave_height'][i] or 0
                period = m['swell_wave_period'][i] or 0
                wind = int(w['wind_speed_10m'][i] or 0)
                wind_dir = get_dir(w['wind_direction_10m'][i])
                
                html += f'''
                <div class="t-row">
                    <div>{time}</div>
                    <div style="color:#0077bb; font-weight:bold;">{max(0, wave_cm-10)}-{wave_cm+10}</div>
                    <div>{get_wave_desc(wave_m)}</div>
                    <div>{swell} מ'</div>
                    <div>{period} שנ'</div>
                    <div class="wind-box">{wind}</div>
                    <div>{wind_dir}</div>
                </div>'''
            
            st.markdown(html + '</div>', unsafe_allow_html=True)
        else:
            st.error("לא ניתן למשוך נתונים מהשרת. נסה שוב מאוחר יותר.")
