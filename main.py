import streamlit as st
import requests
from datetime import datetime
import urllib.parse
from thefuzz import process # ספרייה לתיקון טעויות כתיב

# --- Configuration ---
st.set_page_config(page_title="SkiMaster Pro", page_icon="⛷️")

API_KEY = "3e830cd1e7024f7d1839481229012cfe"
MY_GEAR = "K2 Mindbender BOA (Size: 29.5)"

# רשימת אתרים לתיקון טעויות - אפשר להוסיף כאן עוד ועוד
RESORT_DATABASE = [
    "Val d'Isere", "Val Thorens", "Ischgl", "St. Anton am Arlberg", 
    "Tignes", "Zermatt", "Chamonix", "Courchevel", "Meribel", 
    "Verbier", "Mayrhofen", "Sölden", "Kitzbühel", "Vail", "Aspen"
]

if 'resort_data' not in st.session_state:
    st.session_state.resort_data = None

def get_weather(query):
    # תיקון טעויות חכם: מחפש את השם הכי קרוב ברשימה
    best_match, score = process.extractOne(query, RESORT_DATABASE)
    
    # אם רמת הביטחון מעל 60%, נשתמש בתיקון. אם לא, ננסה את מה שהמשתמש כתב
    final_name = best_match if score > 60 else query
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={final_name}&appid={API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        if res.get("cod") == 200:
            return res, final_name
        return None, None
    except:
        return None, None

# --- UI ---
st.title("⛷️ SkiMaster Pro")
st.write(f"📅 {datetime.now().strftime('%A, %d %B %Y')}")

search_term = st.text_input("Enter Resort Name (Free text):", placeholder="e.g. val diser, ishgl, st anton")

if st.button("Search & Analyze"):
    if search_term:
        data, corrected_name = get_weather(search_term)
        if data:
            st.session_state.resort_data = data
            if corrected_name != search_term:
                st.info(f"Showing results for: **{corrected_name}** (corrected from '{search_term}')")
        else:
            st.error("Could not find a matching resort. Try another name.")

if st.session_state.resort_data:
    res = st.session_state.resort_data
    st.divider()
    st.header(f"📍 {res['name']}")
    
    col1, col2 = st.columns(2)
    col1.metric("Temp", f"{res['main']['temp']}°C")
    col2.metric("Wind", f"{res['wind']['speed']} km/h")
    
    # המלצות אפרה סקי ומסעדות
    st.subheader("🎿 SkiMaster Guide")
    q_enc = urllib.parse.quote(res['name'])
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"[🍺 Après-Ski](https://www.google.com/search?q={q_enc}+best+apres+ski)")
    c2.markdown(f"[🍽️ Restaurants](https://www.google.com/search?q={q_enc}+best+restaurants)")
    c3.markdown(f"[🎉 Events](https://www.google.com/search?q={q_enc}+events+today)")

st.sidebar.info(f"My Gear: {MY_GEAR}")
