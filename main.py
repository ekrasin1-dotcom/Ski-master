import streamlit as st
import requests
from datetime import datetime
import urllib.parse

# --- Setup ---
st.set_page_config(page_title="SkiMaster Pro", page_icon="⛷️")

API_KEY = "3e830cd1e7024f7d1839481229012cfe"
MY_GEAR = "K2 Mindbender BOA (Size: 29.5)"

# מפה מורחבת הכוללת את איטליה והדולומיטים
RESORT_MAPPING = {
    # צרפת
    "val d isere": "Val-d'Isere,FR",
    "val disere": "Val-d'Isere,FR",
    "les arcs": "Bourg-Saint-Maurice,FR",
    "les arc": "Bourg-Saint-Maurice,FR",
    "tignes": "Tignes,FR",
    # אוסטריה
    "ischgl": "Ischgl,AT",
    "ischgle": "Ischgl,AT",
    "st anton": "Sankt Anton am Arlberg,AT",
    # איטליה - דולומיטים
    "sella ronda": "Canazei,IT",
    "sela ronda": "Canazei,IT",
    "campitello": "Campitello di Fassa,IT",
    "val di fassa": "Canazei,IT",
    "canazei": "Canazei,IT",
    "selva": "Selva di Val Gardena,IT",
    "val gardena": "Selva di Val Gardena,IT",
    "livigno": "Livigno,IT",
    # שונות
    "kicking horse": "Golden,CA",
    "hermon": "Majdal Shams,IL"
}

def get_weather(query):
    q_clean = query.lower().strip()
    
    # חיפוש חכם במיפוי - בודק אם המילה שכתבת נמצאת בתוך אחד המפתחות
    target = None
    for key, value in RESORT_MAPPING.items():
        if key in q_clean:
            target = value
            break
    
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

search_input = st.text_input("Search Resort (e.g. Sella Ronda, Campitello, Ischgl):")

if st.button("Check Conditions"):
    if search_input:
        data, found_name = get_weather(search_input)
        if data:
            st.session_state.resort_data = data
            if data['main']['temp'] > 18:
                st.warning("⚠️ High temp detected! Make sure this is the right ski resort.")
            else:
                st.success(f"📍 Found: {found_name}")
        else:
            st.error(f"Could not find '{search_input}'. Try nearby village name.")

if 'resort_data' in st.session_state and st.session_state.resort_data:
    res = st.session_state.resort_data
    st.divider()
    
    st.header(f"Live Weather: {res['name']}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Temp", f"{res['main']['temp']}°C")
    col2.metric("Wind", f"{res['wind']['speed']} km/h")
    col3.metric("Status", res['weather'][0]['main'])
    
    # המלצות מותאמות
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
