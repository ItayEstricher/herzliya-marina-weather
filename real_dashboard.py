import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime

# ==== הגדרות ====
API_KEY = st.secrets["WEATHER_API_KEY"]
LAT, LON = 32.1615, 34.7938
MAX_FORECAST_DAYS = 7  # מגבלת ה-Marine API של weatherapi.com (עד 7 ימים, תלוי בתוכנית)

st.set_page_config(page_title="הרצליה - מרינה", layout="wide")

# מילון תרגום לכיווני רוח
WIND_DIRS = {
    "N": "צפונית", "NNE": "צפון-מזרחית", "NE": "צפון-מזרחית", "ENE": "צפון-מזרחית",
    "E": "מזרחית", "ESE": "דרום-מזרחית", "SE": "דרום-מזרחית", "SSE": "דרום-מזרחית",
    "S": "דרומית", "SSW": "דרום-מערבית", "SW": "דרום-מערבית", "WSW": "דרום-מערבית",
    "W": "מערבית", "WNW": "צפון-מערבית", "NW": "צפון-מערבית", "NNW": "צפון-מערבית"
}

WEEKDAYS_HE = ["שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת", "ראשון"]


@st.cache_data(ttl=3600)
def get_data(days: int):
    url = f"https://api.weatherapi.com/v1/marine.json?key={API_KEY}&q={LAT},{LON}&days={days}"
    res = requests.get(url).json()
    return res.get('forecast', {}).get('forecastday', [])


def arrow_svg(deg, color="white", size=16):
    """חץ שמסתובב לפי מעלות (0 = צפון)"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'style="transform:rotate({deg}deg)">'
        f'<path d="M12 2 L19 20 L12 16 L5 20 Z" fill="{color}"></path></svg>'
    )


# ==== CSS (מחרוזת רגילה, לא f-string) ====
CSS_STYLE = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Segoe UI', Arial, sans-serif;
    direction: rtl;
    background: #fff;
}
.app-shell { border-radius: 10px; overflow: hidden; border: 1px solid #e2e2e2; }

.top-bar {
    background: linear-gradient(180deg, #1a8fd1, #1179b8);
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    font-size: 22px;
    font-weight: 700;
}
.top-bar .icon { font-size: 20px; opacity: 0.9; }

.date-bar {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    padding: 14px 18px;
    background: white;
    border-bottom: 1px solid #eee;
    font-size: 16px;
    color: #333;
}
.date-bar b { font-size: 19px; margin-right: 6px; }

table { width: 100%; border-collapse: collapse; text-align: center; }
th {
    background: #f4f6f8; color: #555; font-weight: 600; font-size: 13px;
    padding: 10px 6px; border-bottom: 2px solid #e2e2e2;
}
td { padding: 6px 4px; font-size: 15px; color: #333; vertical-align: middle; }

.row-even td.plain { background: #eaf4fb; }
.row-odd td.plain { background: #ffffff; }

.height-cell { color: white; font-weight: 700; padding: 14px 4px; font-size: 14px; }
.height-high { background: #0d6cb0; }
.height-low  { background: #3ba9e0; }

.wind-cell { color: white; font-weight: 700; font-size: 13px; padding: 10px 4px; }
.wind-inner { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.wind-green  { background: #27ae60; }
.wind-orange { background: #f39c12; }

.swell-dir-icon { display: flex; flex-direction: column; align-items: center; gap: 2px; font-size: 12px; color: #333; }
"""

# ==== שורת בקרה: תאריך + רענון, מיושרים לימין ====
all_days = get_data(MAX_FORECAST_DAYS)

# בונים רשימת תאריכים זמינה בפועל (תלוי מה שהתוכנית שלכם מחזירה בפועל, עד 7)
date_options = [d['date'] for d in all_days] if all_days else []

spacer_col, date_col, refresh_col = st.columns([4, 2, 1])
with date_col:
    if date_options:
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        default_index = date_options.index(today_str) if today_str in date_options else 0
        selected_date = st.selectbox(
            "תאריך", date_options, index=default_index, label_visibility="collapsed"
        )
    else:
        selected_date = None
with refresh_col:
    if st.button("🔄 רענן"):
        st.cache_data.clear()
        st.rerun()

if not all_days:
    st.error("לא ניתן למשוך נתונים.")
else:
    day_data = next((d for d in all_days if d['date'] == selected_date), all_days[0])
    hours = day_data['hour']

    # תווית "היום" / "מחר" / שם יום בשבוע
    today = datetime.date.today()
    picked = datetime.datetime.strptime(day_data['date'], "%Y-%m-%d").date()
    delta = (picked - today).days
    if delta == 0:
        day_label = "היום"
    elif delta == 1:
        day_label = "מחר"
    else:
        day_label = f"יום {WEEKDAYS_HE[picked.weekday()]}"

    date_display = picked.strftime("%d/%m/%Y")

    rows_html = ""
    for i, h in enumerate(hours[::3]):
        wave_max = int(h['swell_ht_mt'] * 100)
        wave_min = max(0, wave_max - 20)
        wave_desc = "חזה" if wave_max > 40 else "קרסול"

        wind_kph = int(h['wind_kph'])
        wind_class = "wind-green" if wind_kph < 10 else "wind-orange"
        wind_deg = h.get('wind_degree', 0)

        height_class = "height-high" if wave_max >= 65 else "height-low"
        row_class = "row-even" if i % 2 == 0 else "row-odd"

        # swell_dir הוא מעלות (float), swell_dir_16_point הוא הטקסט המצפני
        swell_deg = h.get('swell_dir', wind_deg)

        rows_html += (
            f"<tr class='{row_class}'>"
            f"<td class='plain'>{h['time'].split(' ')[1]}</td>"
            f"<td class='height-cell {height_class}'>{wave_max} - {wave_min} ס\"מ</td>"
            f"<td class='plain'>{wave_desc}</td>"
            f"<td class='wind-cell {wind_class}'>"
            f"<div class='wind-inner'>{arrow_svg(wind_deg)}<span>{wind_kph} קמ\"ש</span></div>"
            f"</td>"
            f"<td class='plain'>{WIND_DIRS.get(h['wind_dir'], h['wind_dir'])}</td>"
            f"<td class='plain'>{wave_max} ס\"מ</td>"
            f"<td class='plain'>{h['swell_period_secs']} שנ'</td>"
            f"<td class='plain'><div class='swell-dir-icon'>{arrow_svg(swell_deg, color='#333', size=14)}</div></td>"
            f"</tr>"
        )

    table_html = (
        "<table>"
        "<tr><th>שעה</th><th>גובה</th><th>גלים</th><th>רוח</th>"
        "<th>כיוון</th><th>סוואל</th><th>מחזור</th><th>כיוון</th></tr>"
        f"{rows_html}"
        "</table>"
    )

    full_html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<style>{CSS_STYLE}</style>
</head>
<body>
<div class="app-shell">
  <div class="top-bar">
    <span class="icon">⚙️</span>
    <span>הרצליה - מרינה</span>
    <span class="icon">🌊</span>
  </div>
  <div class="date-bar">
    <span class="date-text">{date_display}</span>
    <b>{day_label}</b>
  </div>
  {table_html}
</div>
</body>
</html>"""

    components.html(full_html, height=420 + 46 * len(hours[::3]), scrolling=False)

    if len(all_days) < MAX_FORECAST_DAYS:
        st.caption(
            f"התוכנית שלכם ב-weatherapi.com מחזירה כרגע {len(all_days)} ימי תחזית ימית. "
            f"המקסימום האפשרי במסלול Marine API הוא 7 ימים (לא 14) — תלוי בתוכנית המנוי שלכם."
        )
