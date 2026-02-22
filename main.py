import streamlit as st
import requests
from datetime import datetime
import urllib.parse
from streamlit_js_eval import get_geolocation

# --- Configuration ---
st.set_page_config(page_title="SkiMaster Pro", page_icon="⛷️")

API_KEY = "3e830cd1e7024f7d1839481229012cfe"
MY_GEAR = "K2 Mindbender BOA (Size: 29.5)"

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

def get_weather(city=None, lat=None, lon=None):
    if lat and lon:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    else:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    
    try:
        res = requests.get(url).json()
        return res if res.get("cod") == 200 else None
    except:
        return None

# --- UI ---
st.title("⛷️ SkiMaster Pro")

# 1. GPS Location Button
st.subheader("📍 Smart Location")
loc = get_geolocation()
if loc:
    lat = loc['coords']['latitude']
    lon = loc['coords']['longitude']
    if st.button("Check Weather at My Current Location"):
        data = get_weather(lat=lat, lon=lon)
        if data:
            st.session_state.selected_resort = data['name']

# 2. Search Input
resort = st.text_input("Search Resort Name:", placeholder="e.g. Val Thorens, Ischgl")

if resort:
    if resort not in st.session_state.history:
        st.session_state.history.insert(0, resort)
        st.session_state.history = st.session_state.history[:3] # Keep last 3

# 3. Recent Searches
if st.session_state.history:
    st.write("🕒 Recent:", " | ".join(st.session_state.history))

# 4. Main Display
target = resort if resort else st.session_state.get('selected_resort')

if target:
    data = get_weather(target)
    if data:
        st.header(f"Results for {data['name']}")
        col1, col2 = st.columns(2)
        col1.metric("Temperature", f"{data['main']['temp']}°C")
        col2.metric("Wind Speed", f"{data['wind']['speed']} km/h")
        
        # 5. Events Section
        st.divider()
        st.subheader("📅 Local Events & Après-Ski")
        res_enc = urllib.parse.quote(data['name'])
        
        st.info(f"Check out what's happening in {data['name']} today:")
        st.markdown(f"🔗 [Live Music & Festivals](https://www.google.com/search?q={res_enc}+events+festivals+this+week)")
        st.markdown(f"🔗 [Après-Ski Parties](https://www.google.com/search?q={res_enc}+apres+ski+parties)")
        
    else:
        st.error("Location not found. Try a nearby city name.")

st.sidebar.header("🎿 My Gear")
st.sidebar.info(MY_GEAR)
