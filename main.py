import streamlit as st
import requests
from datetime import datetime
import urllib.parse
from thefuzz import process 

# --- Setup ---
st.set_page_config(page_title="SkiMaster Pro", page_icon="⛷️")

API_KEY = "3e830cd1e7024f7d1839481229012cfe"
MY_GEAR = "K2 Mindbender BOA (Size: 29.5)"

# רשימת אתרים עם שמות מפורשים כדי למנוע בלבול עם Vail
RESORTS_DATABASE = {
    "Val d'Isere": "Val-d'Isere",
    "Val Thorens": "Val Thorens",
    "Ischgl": "Ischgl",
    "St. Anton": "Sankt Anton am Arlberg",
    "Tignes": "Tignes",
    "Zermatt": "Zermatt",
    "Chamonix": "Chamonix-Mont-Blanc",
    "Courchevel": "Courchevel",
    "Vail": "Vail",
    "Mount Hermon": "Majdal Shams" # החרמון מזוהה דרך מג'דל שמס ב-API
}

if 'resort_data' not in st.session_state:
    st.session_state.resort_data = None

def get_weather(query):
    # ניקוי בסיסי של הקלט
    q = query.lower().strip()
    
    # טיפול ספציפי ב"ואל דיזר" - הבעיה העיקרית שלך
    if "val" in q and ("diser" in q or "d'isere" in q or "diz" in q):
        target_name = "Val-d'Isere"
    else:
        # חיפוש חכם בשאר הרשימה
        best_match, score = process.extractOne(query, list(RESORTS_DATABASE.keys()))
        target_name = RESORTS_DATABASE[best_match] if score > 70 else query

    url = f"http://api.openweathermap.org/data/2.5/weather?q={target_name}&appid={API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        if res.get("cod") == 200:
            return res, target_name
        return None, None
    except:
        return None, None

# --- UI ---
st.title("⛷️ SkiMaster Pro")
st.write(f"📅 {datetime.now().strftime('%A, %d %B %Y')}")

search_input = st.text_input("Enter Resort Name:", placeholder="Try 'val diser' or 'ishgl'...")

if st.button("Check Conditions"):
    if search_input:
        data, corrected_name = get_weather(search_input)
        if data:
            st.session_state.resort_data = data
            st.success(f"Found: {corrected_name}")
        else:
            st.error(f"Could not find weather for '{search_input}'.")

if st.session_state.resort_data:
    res = st.session_state.resort_data
    st.divider()
    st.header(f"📍 {res['name']}, {res['sys'].get('country', '')}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Temp", f"{res['main']['temp']}°C")
    c2.metric("Feels Like", f"{res['main']['feels_like']}°C")
    c3.metric("Wind", f"{res['wind']['speed']} km/h")
    
    # המלצות אפרה סקי ובילויים
    st.subheader("🍴 Après-Ski & Lifestyle")
    q_enc = urllib.parse.quote(res['name'])
    
    col_links1, col_links2 = st.columns(2)
    with col_links1:
        st.markdown(f"🍺 [**Best Après-Ski**](https://www.google.com/search?q={q_enc}+best+apres+ski+bars)")
        st.markdown(f"🥩 [**Dinner Spots**](https://www.google.com/search?q={q_enc}+top+restaurants)")
    with col_links2:
        st.markdown(f"🎶 [**Events**](https://www.google.com/search?q={q_enc}+events+today)")
        st.markdown(f"🎥 [**Live Webcams**](https://www.google.com/search?q={q_enc}+live+webcams)")

st.sidebar.info(f"My Gear: {MY_GEAR}")
