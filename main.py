import streamlit as st
import requests
from datetime import datetime
import urllib.parse

# --- Configuration ---
st.set_page_config(page_title="SkiMaster Pro", page_icon="⛷️")

API_KEY = "3e830cd1e7024f7d1839481229012cfe"
MY_GEAR = "K2 Mindbender BOA (Size: 29.5)"

# רשימת המדינות המורשות שלך
ALLOWED_COUNTRIES = ["FR", "AT", "IT", "JP", "US", "CA"]

# מפה חכמה לאתרים "בעייתיים" שביקשת
CORE_MAPPING = {
    "val d isere": "Val-d'Isere,FR",
    "val disere": "Val-d'Isere,FR",
    "val d'isere": "Val-d'Isere,FR",
    "les arcs": "Bourg-Saint-Maurice,FR",
    "les arc": "Bourg-Saint-Maurice,FR",
    "sella ronda": "Canazei,IT",
    "val di fassa": "Canazei,IT",
    "campitello": "Campitello di Fassa,IT",
    "ischgl": "Ischgl,AT",
    "st anton": "Sankt Anton am Arlberg,AT",
    "niseko": "Niseko,JP",
    "kicking horse": "Golden,CA"
}

def get_weather(query):
    q_clean = query.lower().strip()
    
    # 1. בדיקה במפה המהירה (מדינות שלך בלבד)
    if q_clean in CORE_MAPPING:
        target = CORE_MAPPING[q_clean]
        url = f"http://api.openweathermap.org/data/2.5/weather?q={target}&appid={API_KEY}&units=metric"
        res = requests.get(url).json()
        if res.get("cod") == 200:
            return res, res['name']

    # 2. חיפוש חכם במדינות שבחרת
    for country in ALLOWED_COUNTRIES:
        target = f"{q_clean},{country}"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={target}&appid={API_KEY}&units=metric"
        try:
            res = requests.get(url).json()
            # אנחנו מוודאים שזה באמת במדינה הנכונה ושזו טמפרטורה הגיונית לסקי (מתחת ל-20 מעלות)
            if res.get("cod") == 200 and res['sys']['country'] in ALLOWED_COUNTRIES:
                if res['main']['temp'] < 22:
                    return res, res['name']
        except:
            continue
            
    return None, None

# --- UI ---
st.title("⛷️ SkiMaster Pro")
st.write(f"📅 {datetime.now().strftime('%A, %d %B %Y')}")

# שורת חיפוש ממוקדת
search_input = st.text_input("Search (France, Austria, Italy, Japan, USA, Canada):", placeholder="e.g. Sella Ronda, Whistler, Niseko")

if st.button("Check Conditions"):
    if search_input:
        data, found_name = get_weather(search_input)
        if data:
            st.session_state.resort_data = data
            st.success(f"📍 Found in {data['sys']['country']}: {found_name}")
        else:
            st.error(f"Could not find '{search_input}' in your selected countries. Please check spelling.")

if 'resort_data' in st.session_state and st.session_state.resort_data:
    res = st.session_state.resort_data
    st.divider()
    
    st.header(f"Live Status: {res['name']} ({res['sys']['country']})")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Temp", f"{res['main']['temp']}°C")
    col2.metric("Feels Like", f"{res['main']['feels_like']}°C")
    col3.metric("Wind", f"{res['wind']['speed']} km/h")

    # המלצות מותאמות אישית
    st.subheader("🌟 SkiMaster Recommendations")
    q_enc = urllib.parse.quote(res['name'])
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"🍺 [**Best Après-Ski Bars**](https://www.google.com/search?q={q_enc}+best+apres+ski+bars)")
        st.markdown(f"🥩 [**Top Restaurants**](https://www.google.com/search?q={q_enc}+best+restaurants)")
    with c2:
        st.markdown(f"🎶 [**Events & Nightlife**](https://www.google.com/search?q={q_enc}+events+festivals)")
        st.markdown(f"🎥 [**Live Webcams**](https://www.google.com/search?q={q_enc}+ski+webcams)")

st.sidebar.info(f"My Gear: {MY_GEAR}")
