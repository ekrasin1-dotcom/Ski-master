import streamlit as st
import requests
from datetime import datetime
import urllib.parse
from streamlit_js_eval import get_geolocation

# --- Configuration ---
st.set_page_config(page_title="SkiMaster Pro", page_icon="⛷️")

API_KEY = "3e830cd1e7024f7d1839481229012cfe"
MY_GEAR = "K2 Mindbender BOA (Size: 29.5)"

# Popular Ski Resorts List for Autocomplete
POPULAR_RESORTS = [
    "Val Thorens", "Ischgl", "St. Anton am Arlberg", "Zermatt", "Chamonix", 
    "Courchevel", "Meribel", "Tignes", "Val d'Isere", "Verbier", "Mayrhofen", 
    "Sölden", "Kitzbühel", "Lech", "Avoriaz", "Les Arcs", "La Plagne", 
    "Livigno", "Cervinia", "Sestriere", "Cortina d'Ampezzo", "Bad Gastein",
    "Saalbach", "Zell am See", "Flaine", "Crans-Montana", "Vail", "Aspen", 
    "Whistler", "Bansko", "Gudauri", "Poiana Brasov"
]

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

# --- UI ---
st.title("⛷️ SkiMaster Pro")
st.write(f"{datetime.now().strftime('%A, %d %B %Y')}")

# --- Sidebar ---
st.sidebar.header("🎿 My Gear")
st.sidebar.info(f"Boots: {MY_GEAR}")
if st.session_state.history:
    st.sidebar.write("---")
    st.sidebar.subheader("🕒 Recent")
    for item in st.session_state.history:
        if st.sidebar.button(item):
            st.session_state.resort_data = get_weather(item)

# --- Main Logic ---
tab1, tab2 = st.tabs(["🔍 Find Resort", "📍 GPS Location"])

with tab1:
    # Use selectbox with search capability
    selected_resort = st.selectbox(
        "Start typing resort name:", 
        options=[""] + sorted(list(set(POPULAR_RESORTS + st.session_state.history))),
        format_func=lambda x: "Select a resort..." if x == "" else x
    )
    
    manual_input = st.text_input("Or type full name manually:")
    
    if st.button("Get Weather"):
        final_query = manual_input if manual_input else selected_resort
        if final_query:
            data = get_weather(final_query)
            if data:
                st.session_state.resort_data = data
                if data['name'] not in st.session_state.history:
                    st.session_state.history.insert(0, data['name'])
                    st.session_state.history = st.session_state.history[:5]
            else:
                st.error("Could not find weather for this location. Try a nearby city.")

with tab2:
    loc = get_geolocation()
    if st.button("Locate Me"):
        if loc and 'coords' in loc:
            data = get_weather(lat=loc['coords']['latitude'], lon=loc['coords']['longitude'])
            if data:
                st.session_state.resort_data = data
        else:
            st.warning("Please wait for GPS signal or enable location permissions.")

# --- Results ---
if st.session_state.resort_data:
    data = st.session_state.resort_data
    st.divider()
    st.header(f"Live: {data['name']}")
    
    c1, c2 = st.columns(2)
    c1.metric("Temperature", f"{data['main']['temp']}°C")
    c2.metric("Wind Speed", f"{data['wind']['speed']} m/h")
    
    st.subheader("📅 Plan Your Day")
    res_enc = urllib.parse.quote(data['name'])
    st.markdown(f"🔗 [Events in {data['name']}](https://www.google.com/search?q={res_enc}+ski+events+2026)")
    st.markdown(f"🔗 [Best Restaurants](https://www.google.com/search?q={res_enc}+top+restaurants+ski)")
