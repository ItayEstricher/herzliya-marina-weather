import streamlit as st
import requests
import math
from datetime import datetime

# =========================
# הגדרות משתמש
# =========================
API_KEY = st.secrets["WINDY_API_KEY"] 
LAT = 32.1615
LON = 34.7938

# =========================
# הגדרות תצוגה ו-CSS
# =========================
st.set_page_config(page_title="דשבורד מרינה הרצליה", page_icon="🌊", layout="centered")

st.markdown("""
<style>
    body { direction: rtl; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stApp { background-color: #f0f4f8; }
    .top-header { background: #1da1f2; color: white; padding: 20px; text-align: center; font-size: 28px; font-weight: 700; border-radius: 10px 10px 0 0; margin-bottom: 0px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); }
    .sub-header { background: #1181c6; color: white; display: flex; justify-content: center; padding: 10px; border-radius: 0 0 10px 10px; font-size: 16px; margin-bottom: 20px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); }
    .sub-header span.active { font-weight: bold; border-bottom: 3px solid white; padding-bottom: 2px; }
    .table-container { background: white; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); overflow: hidden; margin-bottom: 20px; }
    .t-header, .t-row { display: grid; grid-template-columns: 1.2fr 1fr 1fr 1fr 1.5fr; align-items: center; text-align: center; font-size: 14px; }
    .t-header { background: #f8f9fa; color: #555; font-weight: bold; padding: 15px 10px; border-bottom: 2px solid #eee; }
    .t-row { padding: 12px 10px; border-bottom: 1px solid #f1f1f1; color: #333; font-size: 15px; }
    .t-row:hover { background: #fdfdfd; }
    .time-block { display: flex; flex-direction: column; align-items: center; font-weight: bold; }
    .time-text { font-size: 16px; color: #111; }
    .temp-text { font-size: 18px; color: #1da1f2; margin-top: 5px; }
    .wind-container { display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 10px; }
    .wind-box { display: flex; flex-direction: column; align-items: center; justify-content: center; width: 65px; height: 65px; border-radius: 8px; color: white; font-weight: bold; line-height: 1.2; }
    .wind-dir-text { font-size: 12px; color: #555; width: 60px; }
    .wind-arrow { font-size: 18px; margin-bottom: 2px; display: inline-block; }
    .wind-speed { font-size: 16px; }
    .wind-unit { font-size: 11px; font-weight: normal; }
    .bg-green { background-color: #27ae60; }
    .bg-yellow { background-color: #f39c12; }
    .bg-orange { background-color: #d35400; }
    .bg-red { background-color: #c0392b; }
</style>
""", unsafe_allow_html=True)

# =========================
# פונקציות
# =========================
def get_weather():
    url = "https://api.windy.com/api/point-forecast/v2"
    payload = {
        "lat": LAT,
        "lon": LON,
        "model": "gfs",
        "parameters": ["temp", "wind", "windGust", "waves_height", "swell1_height"],
        "levels": ["surface"],
        "key": API_KEY
    } 
    r = requests.post(url, json=payload)
    if r.status_code != 200:
        raise Exception(f"{r.status_code} Error: {r.text}")
    return r.json()

def calculate_wind(u, v):
    speed = math.sqrt(u*u + v*v) * 3.6
    direction = (270 - math.degrees(math.atan2(v, u))) % 360 
    return round(speed), round(direction)

def get_wind_color(speed):
    if speed < 12: return "bg-green"
    if speed < 22: return "bg-yellow"
    if speed < 32: return "bg-orange"
    return "bg-red"

def get_hebrew_direction(deg):
    val = int((deg / 45) + 0.5)
    directions = ["צפונית", "צפון מזרחית", "מזרחית", "דרום מזרחית", "דרומית", "דרום מערבית", "מערבית", "צפון מערבית"]
    return directions[val % 8]

# =========================
# ממשק המשתמש (UI)
# =========================
st.markdown("""
<div class="top-header">הרצליה - מרינה 🌊</div>
<div class="sub-header">
    <span class="active">תחזית ימית</span>
</div>
""", unsafe_allow_html=True)

if st.button("🔄 רענן נתונים עדכניים"):
    with st.spinner("מושך נתונים מ-Windy..."):
        try:
            data = get_weather()
            
            html_table = f"""
            <div style="margin-bottom:10px; font-weight:bold; font-size:18px; text-align: right; padding-right: 5px;">
                היום {datetime.now().strftime('%d/%m/%Y')}
            </div>
            <div class="table-container">
                <div class="t-header">
                    <div>שעה וטמפ'</div>
                    <div>גלים (מטר)</div>
                    <div>סוול (ס"מ)</div>
                    <div>משבים (קמ"ש)</div>
                    <div>רוח וכיוון</div>
                </div>
            """
            
            rows_data = []
            count = 0
            
            for i, timestamp in enumerate(data["ts"]):
                dt = datetime.fromtimestamp(timestamp / 1000)
                
                if dt.hour % 3 == 0:
                    hour_str = dt.strftime("%H:%M")
                    icon = "☀️" if 6 <= dt.hour <= 18 else "🌙"
                    
                    # שליפת נתונים עם הגנה
                    temp = round(data.get("temp-surface", [0]*20)[i] - 273.15) if "temp-surface" in data else "-"
                    
                    u = data.get("wind_u-surface", [0]*20)[i]
                    v = data.get("wind_v-surface", [0]*20)[i]
                    speed, deg = calculate_wind(u, v)
                    
                    gust_raw = data.get("gust-surface", [0]*20)[i]
                    gust = round(gust_raw * 3.6)
                    
                    # נתוני ים עם בדיקת null
                    wave_raw = data.get("waves_height-surface", [None]*20)[i]
                    wave_m = round(wave_raw, 1) if wave_raw is not None else "-"
                    
                    swell_raw = data.get("swell1_height-surface", [None]*20)[i]
                    swell_cm = int(swell_raw * 100) if swell_raw is not None else "-"
                    
                    color_class = get_wind_color(speed)
                    heb_dir = get_hebrew_direction(deg)
                    arrow_rotation = deg + 180
                    sort_key = (dt.hour - 6) % 24
                    
                    row_html = f"""
                    <div class="t-row">
                        <div class="time-block">
                            <span class="time-text">{hour_str}</span>
                            <span class="temp-text">{icon} {temp}°C</span>
                        </div>
                        <div style="font-weight:bold; font-size:18px;">{wave_m}</div>
                        <div style="font-weight:bold; font-size:16px;">{swell_cm} ס"מ</div>
                        <div>{gust}</div>
                        <div class="wind-container">
                            <div class="wind-dir-text">{heb_dir}</div>
                            <div class="wind-box {color_class}">
                                <span class="wind-arrow" style="transform: rotate({arrow_rotation}deg);">↑</span>
                                <span class="wind-speed">{speed}</span>
                                <span class="wind-unit">קמ"ש</span>
                            </div>
                        </div>
                    </div>
                    """
                    rows_data.append((sort_key, row_html))
                    count += 1
                    if count >= 6: break
                    
            rows_data.sort(key=lambda x: x[0])
            for key, row in rows_data: html_table += row
            html_table += "</div>"
            st.markdown(html_table.replace('\n', ''), unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"אירעה שגיאה: {e}")
