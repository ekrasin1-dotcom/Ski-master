import streamlit as st
import requests
from datetime import datetime
import urllib.parse
from streamlit_js_eval import get_geolocation

# --- Configuration ---
st.set_page_config(page_title="SkiMaster Pro", page_icon="⛷️")

API_KEY = "3e830cd1e7024f7d1839481229012cfe"
MY_GEAR = "K2 Mindbender BOA (Size: 29.5)"

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'resort_data' not in st.session_state:
    st.session_state.resort_data = None

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

# --- UI Header ---
st.title("⛷️ SkiMaster Pro")
st.write(f"{datetime.now().strftime('%A, %d %B %Y')}")

# --- Sidebar ---
st.sidebar.header("🎿 My Gear")
st.sidebar.info(f"Boots: {MY_GEAR}")
if st.session_state.history:
    st.sidebar.write("---")
    st.sidebar.subheader("🕒 Recent Searches")
    for item in st.session_state.history:
        if st.sidebar.button(item):
            st.session_state.resort_data = get_weather(item)

# --- Selection Logic ---
st.subheader("Choose your method:")
tab1, tab2 = st.tabs(["🔍 Search by Name", "📍 Use My Location"])

with tab1:
    resort_input = st.text_input("Enter Resort Name:", placeholder="e.g. Ischgl")
    if st.button("Search"):
        if resort_input:
            data = get_weather(resort_input)
            if data:
                st.session_state.resort_data = data
                if data['name'] not in st.session_state.history:
                    st.session_state.history.insert(0, data['name'])
                    st.session_state.history = st.session_state.history[:5]
            else:
                st.error("Resort not found. Try 'Val Thorens' or 'Zermatt'.")

with tab2:
    st.write("Click the button to find the resort you are currently in.")
    loc = get_geolocation()
    if st.button("Get Weather from GPS"):
        if loc and 'coords' in loc:
            data = get_weather(lat=loc['coords']['latitude'], lon=loc['coords']['longitude'])
            if data:
                st.session_state.resort_data = data
        else:
            st.warning("Please wait a second for GPS signal or allow location access.")

# --- Results Display ---
if st.session_state.resort_data:
    data = st.session_state.resort_data
    st.divider()
    st.header(f"Results for {data['name']}")
    
    col1, col2 = st.columns(2)
    col1.metric("Temperature", f"{data['main']['temp']}°C")
    col2.metric("Wind Speed", f"{data['wind']['speed']} km/h")
    
    # Events & Links Section
    st.subheader("📅 Events & Local Info")
    res_enc = urllib.parse.quote(data['name'])
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"🔗 [Music & Parties](https://www.google.com/search?q={res_enc}+ski+events+today)")
    with col_b:
        st.markdown(f"🔗 [Best Après-Ski](https://www.google.com/search?q={res_enc}+best+apres+ski)")
