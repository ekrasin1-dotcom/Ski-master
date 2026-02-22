import streamlit as st
import requests
from datetime import datetime
import urllib.parse
from thefuzz import process 

# --- Setup ---
st.set_page_config(page_title="SkiMaster Pro", page_icon="⛷️")

API_KEY = "3e830cd1e7024f7d1839481229012cfe"
MY_GEAR = "K2 Mindbender BOA (Size: 29.5)"

# רשימת "תרגום" מסיבית - מחברת בין שם האתר לעיירה שה-API מכיר
RESORT_DATABASE = {
    # צרפת
    "Val d'Isere": "Val-d'Isere,FR",
    "Avoriaz": "Morzine,FR",
    "Les Arcs": "Bourg-Saint-Maurice,FR",
    "Val Thorens": "Saint-Martin-de-Belleville,FR",
    "Tignes": "Tignes,FR",
    "Chamonix": "Chamonix,FR",
    "Meribel": "Les Allues,FR",
    # אוסטריה
    "St. Anton": "Sankt Anton am Arlberg,AT",
    "Ischgl": "Ischgl,AT",
    "Mayrhofen": "Mayrhofen,AT",
    "Solden": "Solden,AT",
    "Lech": "Lech,AT",
    # איטליה
    "Sella Ronda": "Canazei,IT",
    "Campitello": "Campitello di Fassa,IT",
    "Cervinia": "Breuil-Cervinia,IT",
    "Livigno": "Livigno,IT",
    # ארה"ב וקנדה
    "Vail": "Vail,US",
    "Breckenridge": "Breckenridge,US",
    "Beaver Creek": "Avon,US",
    "Big Sky": "Big Sky,US",
    "Whistler": "Whistler,CA",
    "Banff": "Banff,CA"
}

def get_weather(query):
    # 1. ניקוי ראשוני
    q = query.strip()
    
    # 2. חיפוש חכם ברשימה שלנו (מתקן שגיאות כתיב כמו 'val diser')
    best_match, score = process.extractOne(q, list(RESORT_DATABASE.keys()))
    
    if score > 60:
        api_target = RESORT_DATABASE[best_match]
        display_name = best_match
    else:
        # אם לא מצאנו ברשימה, ננסה לחפש גלובלית אבל נוסיף סיומת של מדינות סקי כדי לא להגיע לטקסס
        api_target = q
        display_name = q

    url = f"http://api.openweathermap.org/data/2.5/weather?q={api_target}&appid={API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        if res.get("cod") == 200:
            return res, display_name
        return None, None
    except:
        return None, None

# --- UI ---
st.title("⛷️ SkiMaster Pro")
st.write(f"📅 {datetime.now().strftime('%A, %d %B %Y')}")

search_input = st.text_input("Enter Resort Name:", placeholder="Try: Avoriaz, St. Anton, Val d'Isere...")

if st.button("Check Conditions & Guide"):
    if search_input:
        with st.spinner('Translating to mountain data...'):
            data, name = get_weather(search_input)
            if data:
                st.session_state.resort_data = data
                st.session_state.display_name = name
            else:
                st.error(f"Could not find '{search_input}'. Try the nearest big town.")

if 'resort_data' in st.session_state:
    res = st.session_state.resort_data
    name = st.session_state.display_name
    
    st.divider()
    st.header(f"📍 {name} ({res['sys'].get('country', '')})")
    
    # בדיקת בטיחות: אם חם מדי לסקי
    if res['main']['temp'] > 15:
        st.warning("⚠️ Note: High temperature detected. Make sure this is the correct mountain location.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Temp", f"{res['main']['temp']}°C")
    col2.metric("Feels Like", f"{res['main']['feels_like']}°C")
    col3.metric("Wind", f"{res['wind']['speed']} km/h")

    # --- המלצות אפרה-סקי ומסעדות ---
    st.subheader("🎿 SkiMaster Guide")
    q_enc = urllib.parse.quote(name)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"🍺 [**Best Après-Ski Bars**](https://www.google.com/search?q={q_enc}+best+apres+ski+bars)")
        st.markdown(f"🍽️ [**Top Restaurants**](https://www.google.com/search?q={q_enc}+top+rated+restaurants)")
    with c2:
        st.markdown(f"🎶 [**Events & Nightlife**](https://www.google.com/search?q={q_enc}+events+festivals+today)")
        st.markdown(f"🎥 [**Live Webcams**](https://www.google.com/search?q={q_enc}+live+webcams)")

st.sidebar.info(f"My Gear: {MY_GEAR}")
