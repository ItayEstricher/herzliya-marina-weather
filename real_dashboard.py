import streamlit as st
import requests
import pandas as pd

# הגדרות
API_KEY = st.secrets["WEATHER_API_KEY"]
LAT, LON = 32.1615, 34.7938

st.set_page_config(page_title="הרצליה - מרינה", layout="wide")

# כפתור רענון
if st.button("🔄 רענן נתונים"):
    st.cache_data.clear()

st.title("הרצליה - מרינה")

@st.cache_data(ttl=3600)
def get_data():
    url = f"https://api.weatherapi.com/v1/marine.json?key={API_KEY}&q={LAT},{LON}&days=1"
    res = requests.get(url).json()
    return res['forecast']['forecastday'][0]['hour']

data = get_data()

if data:
    # הכנת הנתונים ל-DataFrame (זה יציג טבלה נקייה ומעוצבת אוטומטית)
    table_data = []
    for h in data[::3]:
        table_data.append({
            "שעה": h['time'].split(' ')[1],
            "גובה (ס\"מ)": f"{int(h['swell_ht_mt']*100)} - {max(0, int(h['swell_ht_mt']*100)-20)}",
            "גלים": "חזה" if h['swell_ht_mt'] >= 0.5 else "קרסול",
            "רוח": f"{int(h['wind_kph'])} קמ\"ש",
            "כיוון": h['wind_dir'],
            "סוואל": f"{int(h['swell_ht_mt']*100)} ס\"מ",
            "מחזור": f"{h['swell_period_secs']} שנ'"
        })
    
    df = pd.DataFrame(table_data)
    
    # הצגת הטבלה
    st.table(df)
else:
    st.error("לא ניתן למשוך נתונים.")
