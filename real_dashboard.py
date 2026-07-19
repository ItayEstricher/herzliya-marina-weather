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
# הגדרות תצוגה
# =========================
st.set_page_config(
    page_title="דשבורד מרינה הרצליה",
    page_icon="⛵",
    layout="centered"
)

# =========================
# עיצוב CSS
# =========================
st.markdown("""
<style>
    body { direction: rtl; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stApp { background-color: #f0f4f8; }

    .top-header {
        background: #1da1f2;
        color: white;
        padding: 20px;
        text-align: center;
        font-size: 28px;
        font-weight: 700;
        border-radius: 10px 10px 0 0;
        margin-bottom: 0px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }

    .sub-header {
        background: #1181c6;
        color: white;
        display: flex;
        justify-content: center;
        padding: 10px;
        border-radius: 0 0 10px 10px;
        font-size: 16px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    .sub-header span.active { font-weight: bold; border-bottom: 3px solid white; padding-bottom: 2px; }

    .table-container {
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        overflow: hidden;
        margin-bottom: 20px;
    }
    .t-header {
        display: grid;
        grid-template-columns: 1.5fr 1fr 1fr 1fr 1.5fr;
        background: #f8f9fa;
        color: #555;
        font-weight: bold;
        text-align: center;
        padding: 15px 10px;
        border-bottom: 2px solid #eee;
        font-size: 14px;
    }
    .t-row {
        display: grid;
        grid-template-columns: 1.5fr 1fr 1fr 1fr 1.5fr;
        align-items: center;
        text-align: center;
        padding: 12px 10px;
        border-bottom: 1px solid #f1f1f1;
        font-size: 15px;
        color: #333;
    }
    .t-row:last-child { border-bottom: none; }
    .t-row:hover { background: #fdfdfd; }

    .time-block { display: flex; flex-direction: column; align-items: center; font-weight: bold; }
    .time-text { font-size: 16px; color: #111; }
    .temp-text { font-size: 18px; color: #1da1f2; margin-top: 5px; }

    .wind-container {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    .wind-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 65px;
        height: 65px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        line-height: 1.2;
    }
    .wind-dir-text {
        font-size: 12px;
        color: #555;
        width: 60px;
    }
    .wind-arrow {
        font-size: 18px;
        margin-bottom: 2px;
        display: inline-block;
    }
    .wind-speed { font-size: 16px; }
    .wind-unit { font-size: 11px; font-weight: normal; }

    .bg-green { background-color: #27ae60; }
    .bg-yellow { background-color: #f39c12; }
    .bg-orange { background-color: #d35400; }
    .bg-red { background-color: #c0392b; }

</style>
""", unsafe_allow_html=True)


# =========================
# פונקציות וחישובים
# =========================
def get_weather():
    url = "https://api.windy.com/api/point-forecast/v2"
    payload = {
        "lat": LAT,
        "lon": LON,
        "model": "gfs",
        "parameters": ["temp", "wind", "windGust", "rh", "pressure"],
        "levels": ["surface"],
        "key": API_KEY
    }

    r = requests.post(url, json=payload)
    r.raise_for_status()
    return r.json()


def calculate_wind(u, v):
    speed = math.sqrt(u * u + v * v) * 3.6
    direction = (270 - math.degrees(math.atan2(v, u))) % 360
    return round(speed), round(direction)


def get_wind_color(speed):
    if speed < 12: return "bg-green"
    if speed < 22: return "bg-yellow"
    if speed < 32: return "bg-orange"
    return "bg-red"


def get_hebrew_direction(deg):
    val = int((deg / 45) + 0.5)
    directions = ["צפונית", "צפון מזרחית", "מזרחית", "דרום מזרחית",
                  "דרומית", "דרום מערבית", "מערבית", "צפון מערבית"]
    return directions[val % 8]


# =========================
# בניית הממשק (UI)
# =========================

# שינויים בסרגל: החלפת נקודה בגל והשארת "תחזית ימית" בלבד
st.markdown("""
<div class="top-header">הרצליה - מרינה 🌊</div>
<div class="sub-header">
    <span class="active">תחזית ימית</span>
</div>
""", unsafe_allow_html=True)

# שינוי כפתור: כפתור רגיל (ללא חלוקה לעמודות וללא תפיסת רוחב מלא)
refresh_clicked = st.button("🔄 רענן נתונים עדכניים")

if refresh_clicked:
    with st.spinner("מושך נתונים מ-Windy..."):
        try:
            data = get_weather()

            # תאריך בצד ימין
            html_table = f"""
            <div style="margin-bottom:10px; font-weight:bold; font-size:18px; text-align: right; padding-right: 5px;">
                היום {datetime.now().strftime('%d/%m/%Y')}
            </div>
            <div class="table-container">
                <div class="t-header">
                    <div>שעה</div>
                    <div>לחות</div>
                    <div>לחץ (hPa)</div>
                    <div>משבים</div>
                    <div>רוח וכיוון</div>
                </div>
            """

            # מערך לאחסון השורות לפני המיון
            rows_data = []

            for i in range(0, 18, 3):
                timestamp = data["ts"][i] / 1000
                dt = datetime.fromtimestamp(timestamp)
                hour_str = dt.strftime("%H:%M")

                icon = "☀️" if 6 <= dt.hour <= 18 else "🌙"

                temp = round(data["temp-surface"][i] - 273.15)
                rh = round(data["rh-surface"][i])
                pressure = round(data["pressure-surface"][i] / 100)

                u = data["wind_u-surface"][i]
                v = data["wind_v-surface"][i]
                speed, deg = calculate_wind(u, v)
                gust = round(data["gust-surface"][i] * 3.6)

                color_class = get_wind_color(speed)
                heb_dir = get_hebrew_direction(deg)

                arrow_rotation = deg + 180

                # מפתח למיון: מבטיח שהשעה 06:00 תקבל את הערך הנמוך ביותר ו-00:00 את הערך הגבוה ביותר
                sort_key = (dt.hour - 6) % 24

                row_html = f"""
                <div class="t-row">
                    <div class="time-block">
                        <span class="time-text">{hour_str}</span>
                        <span class="temp-text">{icon} {temp}°C</span>
                    </div>
                    <div>{rh}%</div>
                    <div>{pressure}</div>
                    <div>{gust} <span style="font-size:12px;">קמ"ש</span></div>
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

            # מיון השורות לפי המפתח שהגדרנו (החל מ-06:00)
            rows_data.sort(key=lambda x: x[0])

            # חיבור השורות הממוינות לטבלה
            for key, row in rows_data:
                html_table += row

            html_table += "</div>"

            # ניקוי שורות כדי למנוע את באג התצוגה של Streamlit
            clean_html = html_table.replace('\n', '')

            # הדפסת הטבלה
            st.markdown(clean_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"אירעה שגיאה: {e}")
else:
    st.info("👆 לחץ על כפתור הרענון כדי לטעון את התחזית המעוצבת.")
