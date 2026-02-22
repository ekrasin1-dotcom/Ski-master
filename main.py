import streamlit as st
import requests
from datetime import datetime
import urllib.parse
from thefuzz import process 

# --- Setup ---
st.set_page_config(page_title="SkiMaster Pro", page_icon="⛷️")

API_KEY = "3e830cd1e7024f7d1839481229012cfe"
MY_GEAR = "K2 Mindbender BOA (Size: 29.5)"

# רשימת "קיצורי דרך" לאתרים מורכבים במיוחד
RESORT_MAPPING = {
    "val d isere": "Val-d'Isere",
    "val disere": "Val-d'Isere",
    "les arcs": "Bourg-Saint-Maurice",
    "les arc": "Bourg-Saint-Maurice",
    "kicking horse": "Golden",
    "kick horse": "Golden",
    "mount hermon": "Majdal Shams",
    "hermon": "Majdal Shams"
}

def clean_query(query):
    # מנקה מילים שעלולות לבלבל את ה-API
    q = query.lower().strip()
    for word in ["ski", "resort", "station", "area", "village"]:
        q = q.replace(word, "")
    return q.strip()

def get_weather(query):
    q_clean = clean_query(query)
    
    # 1. בדיקה אם זה אחד מהקיצורים שהגדרנו
    target_name = RESORT_MAPPING.get(q_clean, query)
    
    # 2. פנייה ל-API
    url = f"http://api.openweathermap.org/data/2.5/weather?q={target_name}&appid={API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        if res.get("cod") == 200:
            return res, res['name']
        return None, None
    except:
        return None, None

# --- UI ---
st.title("⛷️ SkiMaster Pro")
st.write(f"📅 {datetime.now().strftime('%A, %d %B %Y')}")

search_input = st.text_input("Enter ANY Ski Resort Name:", placeholder="Try 'les arc', 'kick horse' or 'st moritz'...")

if st.button("Check Conditions"):
    if search_input:
        data, found_name = get_weather(search_input)
        if data:
            st.session_state.resort_data = data
            st.success(f"📍 Found: {found_name}")
        else:
            st.error(f"Could not find '{search_input}'. Tip: Try the name of the nearest village.")

if 'resort_data' in st.session_state and st.session_state.resort_data:
    res = st.session_state.resort_data
    st.divider()
    st.header(f"Live Weather: {res['name']}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Temp", f"{res['main']['temp']}°C")
    c2.metric("Feels Like", f"{res['main']['feels_like']}°C")
    c3.metric("Wind", f"{res['wind']['speed']} km/h")
    
    # המלצות שוות
    st.subheader("🎿 SkiMaster Guide")
    q_enc = urllib.parse.quote(res['name'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"🍺 [**Best Après-Ski**](https://www.google.com/search?q={q_enc}+best+apres+ski+bars)")
        st.markdown(f"🍽️ [**Top Restaurants**](https://www.google.com/search?q={q_enc}+top+rated+restaurants)")
    with col2:
        st.markdown(f"🎶 [**Events Today**](https://www.google.com/search?q={q_enc}+events+festivals)")
        st.markdown(f"🎥 [**Live Webcams**](https://www.google.com/search?q={q_enc}+ski+webcams)")

st.sidebar.info(f"My Gear: {MY_GEAR}")
