import streamlit as st
import requests
import pandas as pd

# הגדרות הרצליה
API_KEY = st.secrets["WEATHER_API_KEY"]
LAT, LON = 32.1615, 34.7938

st.set_page_config(page_title="תחזית מרינה", layout="wide")

# עיצוב CSS כדי להיראות כמו האפליקציה שצילמת
st.markdown("""
<style>
    .forecast-table { width: 100%; border-collapse: collapse; text-align: center; font-family: sans-serif; }
    .header-row { background-color: #f0f0f0; font-weight: bold; padding: 10px; border-bottom: 2px solid #ccc; }
    .data-row { border-bottom: 1px solid #eee; height: 60px; }
    .wind-green { background-color: #27ae60; color: white; padding: 5px; border-radius: 4px; }
    .wind-orange { background-color: #f39c12; color: white; padding: 5px; border-radius: 4px; }
    .wave-cell { background-color: #0077bb; color: white; padding: 10px; }
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
    # יצירת הטבלה המעוצבת
    html = '<table class="forecast-table">'
    html += '<tr class="header-row"><th>שעה</th><th>גובה (ס"מ)</th><th>גלים</th><th>רוח</th><th>כיוון</th><th>סוואל</th><th>מחזור</th></tr>'
    
    for h in data[::3]:
        # לוגיקה לצבע רוח
        wind_class = "wind-green" if h['wind_kph'] < 10 else "wind-orange"
        
        html += f'''
        <tr class="data-row">
            <td>{h['time'].split(' ')[1]}</td>
            <td class="wave-cell">{int(h['swell_ht_mt']*100-10)} - {int(h['swell_ht_mt']*100+10)}</td>
            <td>קרסול</td>
            <td><span class="{wind_class}">{h['wind_kph']} קמ"ש</span></td>
            <td>{h['wind_dir']}</td>
            <td>{int(h['swell_ht_mt']*100)} ס"מ</td>
            <td>{h['swell_period_secs']} שנ'</td>
        </tr>
        '''
    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)
