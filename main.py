import streamlit as st
import requests
from datetime import datetime
import urllib.parse
from thefuzz import process 

# --- Setup ---
st.set_page_config(page_title="SkiMaster Pro", page_icon="⛷️")

API_KEY = "3e830cd1e7024f7d1839481229012cfe"
MY_GEAR = "K2 Mindbender BOA (Size: 29.5)"

# מפה חכמה שמתקנת שמות לפורמט שה-API חייב לקבל
# הוספתי כאן את המדינות (AT, FR) כדי שלא ייתן לך תוצאות מהמדבר
RESORT_MAPPING = {
    "val d isere": "Val-d'Isere,FR",
    "val disere": "Val-d'Isere,FR",
    "ischgl": "Ischgl,AT",
    "ischgle": "Ischgl,AT",
    "st anton": "Sankt Anton am Arlberg,AT",
    "saint anton": "Sankt Anton am Arlberg,AT",
    "les arcs": "Bourg-Saint-Maurice,FR",
    "les arc": "Bourg-Saint-Maurice,FR",
    "tignes": "Tignes,FR",
    "zermatt": "Zermatt,CH",
    "kicking horse": "Golden,CA",
    "hermon": "Majdal Shams,IL"
}

def get_weather(query):
    q_clean = query.lower().strip()
    
    # 1. בדיקה במפה החכמה
    target = RESORT_MAPPING.get(q_clean)
    
    # 2. אם לא מצא במפה, ננסה ניקוי כללי
    if not target:
        target = q_clean.replace("ski", "").replace("resort", "").strip()

    url = f"http://api.openweathermap.org/data/2.5/weather?q={target}&appid={API_KEY}&units=metric"
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

search_input = st.text_input("Search Resort (e.g. ischgl, st anton, val d isere):")

if st.button("Check Conditions"):
    if search_input:
        data, found_name = get_weather(search_input)
        if data:
            st.session_state.resort_data = data
            # בדיקת הגיון - אם הטמפרטורה גבוהה מדי לאתר סקי, ניתן אזהרה
            if data['main']['temp'] > 20:
                st.warning("⚠️ This seems too warm for skiing! Are we in the right place?")
            else:
                st.success(f"📍 Found: {found_name}")
        else:
            st.error(f"Could not find '{search_input}'. Try nearby village name.")

if 'resort_data' in st.session_state and st.session_state.resort_data:
    res = st.session_state.resort_data
    st.divider()
    
    # תצוגה מעוצבת יותר
    st.header(f"Live: {res['name']}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Temp", f"{res['main']['temp']}°C")
    col2.metric("Wind", f"{res['wind']['speed']} km/h")
    col3.metric("Humidity", f"{res['main']['humidity']}%")
    
    # המלצות
    st.subheader("🎿 SkiMaster Guide")
    q_enc = urllib.parse.quote(res['name'])
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"🍺 [**Best Après-Ski**](https://www.google.com/search?q={q_enc}+best+apres+ski+bars)")
        st.markdown(f"🍽️ [**Top Restaurants**](https://www.google.com/search?q={q_enc}+top+rated+restaurants)")
    with c2:
        st.markdown(f"🎶 [**Events Today**](https://www.google.com/search?q={q_enc}+events+festivals)")
        st.markdown(f"🎥 [**Live Webcams**](https://www.google.com/search?q={q_enc}+ski+webcams)")

st.sidebar.info(f"My Gear: {MY_GEAR}")
