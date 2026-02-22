import streamlit as st
import requests
from datetime import datetime
import urllib.parse
from streamlit_js_eval import get_geolocation

# --- Setup & Config ---
st.set_page_config(page_title="SkiMaster Pro", page_icon="⛷️", layout="centered")

API_KEY = "3e830cd1e7024f7d1839481229012cfe"
MY_GEAR = "K2 Mindbender BOA (Size: 29.5)"

# Extended Resort List
RESORTS_DB = sorted([
    "Val Thorens", "Ischgl", "St. Anton am Arlberg", "Zermatt", "Chamonix", 
    "Courchevel", "Meribel", "Tignes", "Val d'Isere", "Verbier", "Mayrhofen", 
    "Sölden", "Kitzbühel", "Lech", "Avoriaz", "Les Arcs", "La Plagne", 
    "Livigno", "Cervinia", "Sestriere", "Cortina d'Ampezzo", "Bad Gastein",
    "Saalbach", "Zell am See", "Flaine", "Crans-Montana", "Vail", "Aspen", 
    "Whistler", "Bansko", "Gudauri", "Poiana Brasov", "Bormio", "Morzine", 
    "Madonna di Campiglio", "Obertauern", "Serre Chevalier", "Les Menuires"
])

if 'history' not in st.session_state:
    st.session_state.history = []
if 'resort_data' not in st.session_state:
    st.session_state.resort_data = None

def get_weather(query):
    # Clean query for API (removes special characters like ' that break search)
    clean_query = query.replace("'", "").replace("’", "")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={clean_query}&appid={API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        return res if res.get("cod") == 200 else None
    except:
        return None

def get_weather_by_coords(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        return res if res.get("cod") == 200 else None
    except:
        return None

# --- App UI ---
st.title("⛷️ SkiMaster Pro")
st.write(f"📅 {datetime.now().strftime('%A, %d %B %Y')}")

# Sidebar for Gear & History
st.sidebar.header("🎿 My Equipment")
st.sidebar.info(MY_GEAR)
if st.session_state.history:
    st.sidebar.divider()
    st.sidebar.subheader("🕒 Recent Searches")
    for h in st.session_state.history:
        if st.sidebar.button(f"Go to {h}"):
            st.session_state.resort_data = get_weather(h)

# Selection Tabs
tab1, tab2 = st.tabs(["🔍 Find My Resort", "📍 GPS Sync"])

with tab1:
    search_choice = st.selectbox("Select from list or type below:", [""] + RESORTS_DB)
    manual_name = st.text_input("Can't find it? Type name manually:")
    
    if st.button("Check Conditions"):
        query = manual_name if manual_name else search_choice
        if query:
            data = get_weather(query)
            if data:
                st.session_state.resort_data = data
                if data['name'] not in st.session_state.history:
                    st.session_state.history.insert(0, data['name'])
                    st.session_state.history = st.session_state.history[:5]
            else:
                st.error(f"Sorry, couldn't find '{query}'. Try the nearest big town or check spelling.")

with tab2:
    st.write("Automatically detect your resort:")
    loc = get_geolocation()
    if st.button("Identify My Location"):
        if loc and 'coords' in loc:
            data = get_weather_by_coords(loc['coords']['latitude'], loc['coords']['longitude'])
            if data:
                st.session_state.resort_data = data
        else:
            st.warning("Still waiting for GPS... Make sure location access is 'Always' or 'While Using'.")

# --- Results Area ---
if st.session_state.resort_data:
    res = st.session_state.resort_data
    st.divider()
    st.header(f"📍 {res['name']}, {res['sys']['country']}")
    
    # Weather Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Temp", f"{res['main']['temp']}°C")
    m2.metric("Feels Like", f"{res['main']['feels_like']}°C")
    m3.metric("Wind", f"{res['wind']['speed']} km/h")
    
    # Recommendations Section
    st.subheader("🌟 SkiMaster Recommendations")
    st.write(f"Best spots in {res['name']} for today:")
    
    q_enc = urllib.parse.quote(res['name'])
    
    rec_col1, rec_col2 = st.columns(2)
    with rec_col1:
        st.markdown(f"🍺 [**Best Après-Ski Bars**](https://www.google.com/search?q={q_enc}+best+apres+ski+bars+party)")
        st.markdown(f"🍽️ [**Top-Rated Restaurants**](https://www.google.com/search?q={q_enc}+best+restaurants+for+dinner)")
    with rec_col2:
        st.markdown(f"🎶 [**Events & Nightlife**](https://www.google.com/search?q={q_enc}+events+festivals+today)")
        st.markdown(f"🚠 [**Live Webcams**](https://www.google.com/search?q={q_enc}+ski+webcams+live)")

    st.success(f"Enjoy your session with your {MY_GEAR}!")
