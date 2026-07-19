import streamlit as st
import requests

# הגדרות
API_KEY = st.secrets["WEATHER_API_KEY"]
LAT, LON = 32.1615, 34.7938

st.set_page_config(page_title="הרצליה - מרינה", layout="wide")

# כפתור רענון נתונים
if st.button("🔄 רענן נתונים"):
    st.cache_data.clear()

st.title("הרצליה - מרינה")

# עיצוב CSS - הכל מרוכז כאן
st.markdown("""
<style>
    .forecast-table { width: 100%; border-collapse: collapse; text-align: center; font-family: sans-serif; direction: rtl; }
    .header-row { background-color: #f0f0f0; font-weight: bold; padding: 15px; border-bottom: 2px solid #ccc; }
    .data-row { border-bottom: 1px solid #eee; height: 60px; }
    .wave-cell { background-color: #0077bb; color: white; padding: 8px; font-weight: bold; border-radius: 5px; }
    .wind-green { background-color: #27ae60; color: white; padding: 4px 8px; border-radius: 4px; }
    .wind-orange { background-color: #f39c12; color: white; padding: 4px 8px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def get_data():
    url = f"https://api.weatherapi.com/v1/marine.json?key={API_KEY}&q={LAT},{LON}&days=1"
    res = requests.get(url).json()
    return res['forecast']['forecastday'][0]['hour']

# מילון תרגום לכיווני רוח
WIND_DIRS = {
    "N": "צפונית", "NNE": "צפון-מזרחית", "NE": "צפון-מזרחית", "ENE": "צפון-מזרחית",
    "E": "מזרחית", "ESE": "דרום-מזרחית", "SE": "דרום-מזרחית", "SSE": "דרום-מזרחית",
    "S": "דרומית", "SSW": "דרום-מערבית", "SW": "דרום-מערבית", "WSW": "דרום-מערבית",
    "W": "מערבית", "WNW": "צפון-מערבית", "NW": "צפון-מערבית", "NNW": "צפון-מערבית"
}

data = get_data()

if data:
    # בניית מחרוזת ה-HTML כולה במשתנה אחד (זה המפתח!)
    html_table = '<table class="forecast-table">'
    html_table += '<tr class="header-row"><th>שעה</th><th>גובה</th><th>גלים</th><th>רוח</th><th>כיוון</th><th>סוואל</th><th>מחזור</th></tr>'
    
    for h in data[::3]:
        wave_max = int(h['swell_ht_mt']*100)
        wave_min = max(0, wave_max - 20)
        wave_desc = "חזה" if wave_max > 40 else "קרסול"
        wind_class = "wind-green" if h['wind_kph'] < 14 else "wind-orange"
        
        # שים לב שאין פה שום הדפסה של Streamlit - רק בניית מחרוזת
        html_table += f'''
        <tr class="data-row">
            <td>{h['time'].split(' ')[1]}</td>
            <td><div class="wave-cell">{wave_max} - {wave_min} ס"מ</div></td>
            <td>{wave_desc}</td>
            <td><span class="{wind_class}">{int(h['wind_kph'])} קמ"ש</span></td>
            <td>{WIND_DIRS.get(h['wind_dir'], h['wind_dir'])}</td>
            <td>{wave_max} ס"מ</td>
            <td>{h['swell_period_secs']} שנ'</td>
        </tr>
        '''
    html_table += '</table>'
    
    # רינדור הכל בפקודה אחת בלבד!
    st.markdown(html_table, unsafe_allow_html=True)
else:
    st.error("לא ניתן למשוך נתונים.")
