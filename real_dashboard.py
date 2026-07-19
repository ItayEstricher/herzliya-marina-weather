import streamlit as st
import requests

# הגדרות
API_KEY = st.secrets["WEATHER_API_KEY"]
LAT, LON = 32.1615, 34.7938

# מילון תרגום לכיווני רוח
WIND_DIRS = {
    "N": "צפונית", "NNE": "צפון-מזרחית", "NE": "צפון-מזרחית", "ENE": "צפון-מזרחית",
    "E": "מזרחית", "ESE": "דרום-מזרחית", "SE": "דרום-מזרחית", "SSE": "דרום-מזרחית",
    "S": "דרומית", "SSW": "דרום-מערבית", "SW": "דרום-מערבית", "WSW": "דרום-מערבית",
    "W": "מערבית", "WNW": "צפון-מערבית", "NW": "צפון-מערבית", "NNW": "צפון-מערבית"
}

def get_wave_desc(h):
    if h < 0.5: return "קרסול"
    if h < 0.9: return "חזה"
    return "ראש"

st.set_page_config(page_title="הרצליה - מרינה", layout="wide")

# CSS לעיצוב בסגנון האפליקציה
st.markdown("""
<style>
    .forecast-table { width: 100%; border-collapse: collapse; text-align: center; font-family: sans-serif; direction: rtl; }
    .header-row { background-color: #f8f9fa; font-weight: bold; padding: 15px; border-bottom: 2px solid #ddd; }
    .data-row { border-bottom: 1px solid #eee; height: 70px; }
    .wind-green { background-color: #27ae60; color: white; padding: 6px; border-radius: 4px; display: inline-block; width: 80px;}
    .wind-orange { background-color: #f39c12; color: white; padding: 6px; border-radius: 4px; display: inline-block; width: 80px;}
    .wave-cell { background-color: #0077bb; color: white; padding: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def get_data():
    url = f"https://api.weatherapi.com/v1/marine.json?key={API_KEY}&q={LAT},{LON}&days=1"
    res = requests.get(url).json()
    return res['forecast']['forecastday'][0]['hour']

st.title("הרצליה - מרינה")

data = get_data()
if data:
    html = '<table class="forecast-table">'
    html += '<tr class="header-row"><th>שעה</th><th>גובה (ס"מ)</th><th>גלים</th><th>רוח</th><th>כיוון</th><th>סוואל</th><th>מחזור</th></tr>'
    
    for h in data[::3]:
        dir_he = WIND_DIRS.get(h['wind_dir'], h['wind_dir'])
        wave_max = int(h['swell_ht_mt']*100)
        wave_min = max(0, wave_max - 20)
        wind_class = "wind-green" if h['wind_kph'] < 14 else "wind-orange"
        
        html += f'''
        <tr class="data-row">
            <td>{h['time'].split(' ')[1]}</td>
            <td class="wave-cell">{wave_max} - {wave_min}</td>
            <td>{get_wave_desc(h['swell_ht_mt'])}</td>
            <td><span class="{wind_class}">{int(h['wind_kph'])} קמ"ש</span></td>
            <td>{dir_he}</td>
            <td>{wave_max} ס"מ</td>
            <td>{h['swell_period_secs']} שנ'</td>
        </tr>
        '''
    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)
else:
    st.error("לא ניתן למשוך נתונים.")
