import streamlit as st
import requests
from datetime import datetime, timedelta
import urllib.parse
from thefuzz import process 

# --- Setup ---
st.set_page_config(page_title="SkiMaster Pro", page_icon="⛷️", layout="wide")

API_KEY = "3e830cd1e7024f7d1839481229012cfe"
MY_GEAR = "K2 Mindbender BOA (Size: 29.5)"

# מפת תרגום (השארתי את העיקריים, המנגנון החכם יטפל בשאר)
RESORT_DATABASE = {
    "Lake Louise": "Lake Louise,CA", "Jasper": "Jasper,CA",
    "Val d'Isere": "Val-d'Isere,FR", "Avoriaz": "Morzine,FR",
    "St. Anton": "Sankt Anton am Arlberg,AT", "Ischgl": "Ischgl,AT",
    "Sella Ronda": "Canazei,IT", "Breckenridge": "Breckenridge,US",
    "Beaver Creek": "Avon,US", "Big Sky": "Big Sky,US"
}

def get_weather_and_forecast(query):
    # 1. תרגום שם האתר למיקום מדויק
    best_match, score = process.extractOne(query, list(RESORT_DATABASE.keys()))
    target = RESORT_DATABASE[best_match] if score > 70 else query

    # 2. קריאה למזג אוויר נוכחי
    current_url = f"http://api.openweathermap.org/data/2.5/weather?q={target}&appid={API_KEY}&units=metric"
    # 3. קריאה לתחזית (Forecast)
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={target}&appid={API_KEY}&units=metric"
    
    try:
        curr_res = requests.get(current_url).json()
        fore_res = requests.get(forecast_url).json()
        
        if curr_res.get("cod") == 200 and fore_res.get("cod") == "200":
            return curr_res, fore_res, best_match if score > 70 else curr_res['name']
        return None, None, None
    except:
        return None, None, None

# --- UI ---
st.title("⛷️ SkiMaster Pro: Ultimate Edition")

search_input = st.text_input("Enter Resort Name:", placeholder="Try 'brecking ridge' or 'avoriaz'...")

if st.button("Analyze Mountain Stats"):
    if search_input:
        curr, fore, name = get_weather_and_forecast(search_input)
        if curr:
            st.divider()
            st.header(f"📍 {name} ({curr['sys'].get('country', '')})")
            
            # --- חישוב שלג ב-24 שעות האחרונות (מתוך התחזית/היסטוריה קרובה) ---
            # הערה: ה-API החינמי נותן שלג שהצטבר ב-3 שעות האחרונות ב-Current
            snow_now = curr.get('snow', {}).get('1h', curr.get('snow', {}).get('3h', 0))
            
            # --- נתוני תחזית ל-24 שעות הבאות ---
            # ה-API נותן תחזית במרווחים של 3 שעות. האינדקס ה-8 הוא בדיוק עוד 24 שעות.
            next_24h = fore['list'][8] 
            
            # תצוגה ב-Columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🌡️ Current Conditions")
                st.metric("Temperature", f"{curr['main']['temp']}°C", f"Feels {curr['main']['feels_like']}°C")
                st.metric("Wind Speed", f"{curr['wind']['speed']} km/h")
                st.write(f"**Current Sky:** {curr['weather'][0]['description'].capitalize()}")
                if snow_now > 0:
                    st.info(f"❄️ Fresh Snow (Recent): {snow_now}mm")
                else:
                    st.write("❄️ No recent snowfall recorded.")

            with col2:
                st.subheader("📅 Next 24 Hours Forecast")
                st.metric("Expected Temp", f"{next_24h['main']['temp']}°C")
                st.metric("Expected Wind", f"{next_24h['wind']['speed']} km/h")
                st.write(f"**Forecast:** {next_24h['weather'][0]['description'].capitalize()}")
                
                # בדיקת שלג בתחזית ל-24 שעות
                forecast_snow = next_24h.get('snow', {}).get('3h', 0)
                if forecast_snow > 0:
                    st.success(f"❄️ Snow incoming! Approx {forecast_snow}mm expected.")

            # --- קישורים מהירים ---
            st.subheader("🔗 Mountain Links")
            q_enc = urllib.parse.quote(name)
            l1, l2, l3 = st.columns(3)
            l1.markdown(f"[🍺 Best Après-Ski](https://www.google.com/search?q={q_enc}+best+apres+ski)")
            l2.markdown(f"[🥩 Top Restaurants](https://www.google.com/search?q={q_enc}+top+restaurants)")
            l3.markdown(f"[🎥 Live Webcams](https://www.google.com/search?q={q_enc}+live+webcams)")
            
        else:
            st.error("Could not find data. Try a different resort name.")

st.sidebar.info(f"My Gear: {MY_GEAR}")
