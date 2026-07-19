import streamlit as st
import requests

# הגדרות
API_KEY = st.secrets["WEATHER_API_KEY"]
LAT, LON = 32.1615, 34.7938

st.set_page_config(page_title="הרצליה - מרינה", layout="wide")

# כפתור רענון
if st.button("🔄 רענן נתונים"):
    st.cache_data.clear()

st.title("הרצליה - מרינה")

# מילון כיווני רוח
WIND_DIRS = {
    "N": "צפונית", "NNE": "צפון-מזרחית", "NE": "צפון-מזרחית", "ENE": "צפון-מזרחית",
    "E": "מזרחית", "ESE": "דרום-מזרחית", "SE": "דרום-מזרחית", "SSE": "דרום-מזרחית",
    "S": "דרומית", "SSW": "דרום-מערבית", "SW": "דרום-מערבית", "WSW": "דרום-מערבית",
    "W": "מערבית", "WNW": "צפון-מערבית", "NW": "צפון-מערבית", "NNW": "צפון-מערבית"
}

@st.cache_data(ttl=3600)
def get_data():
    url = f"https://api.weatherapi.com/v1/marine.json?key={API_KEY}&q={LAT},{LON}&days=1"
    res = requests.get(url).json()
    return res['forecast']['forecastday'][0]['hour']

data = get_data()

if data:
    # כאן אנחנו בונים את כל העיצוב (CSS) והטבלה כבלוק אחד
    html_output = """
    <style>
        .forecast-table { width: 100%; border-collapse: collapse; text-align: center; font-family: sans-serif; direction: rtl; }
        .header-row { background-color: #f0f0f0; font-weight: bold; padding: 15px; border-bottom: 2px solid #ccc; }
        .data-row { border-bottom: 1px solid #eee; height: 65px; }
        .wave-cell { background-color: #0088cc; color: white; padding: 8px; font-weight: bold; border-radius: 5px; }
        .wind-badge { color: white; padding: 6px 10px; border-radius: 4px; display: inline-block; font-weight: bold; }
    </style>
    <table class="forecast-table">
        <tr class="header-row">
            <th>שעה</th><th>גובה</th><th>גלים</th><th>רוח</th><th>כיוון</th><th>סוואל</th><th>מחזור</th>
        </tr>
    """

    for h in data[::3]:
        # חישובים לנתונים
        wave_max = int(h['swell_ht_mt']*100)
        wave_min = max(0, wave_max - 20)
        wave_desc = "חזה" if wave_max > 40 else "קרסול"
        wind_color = "#27ae60" if h['wind_kph'] < 14 else "#f39c12" # ירוק או כתום
        wind_dir = WIND_DIRS.get(h['wind_dir'], h['wind_dir'])
        
        # בניית השורה
        html_output += f'''
        <tr class="data-row">
            <td>{h['time'].split(' ')[1]}</td>
            <td><div class="wave-cell">{wave_max} - {wave_min} ס"מ</div></td>
            <td>{wave_desc}</td>
            <td><span class="wind-badge" style="background-color: {wind_color};">{int(h['wind_kph'])} קמ"ש</span></td>
            <td>{wind_dir}</td>
            <td>{wave_max} ס"מ</td>
            <td>{h['swell_period_secs']} שנ'</td>
        </tr>
        '''
    
    html_output += "</table>"
    
    # הצגה אחת בלבד
    st.markdown(html_output, unsafe_allow_html=True)
else:
    st.error("לא ניתן למשוך נתונים.")
