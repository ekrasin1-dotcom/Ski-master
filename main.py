import streamlit as st
import requests
from datetime import datetime
import urllib.parse
from thefuzz import process 

# --- Setup ---
st.set_page_config(page_title="SkiMaster Pro", page_icon="⛷️")

API_KEY = "3e830cd1e7024f7d1839481229012cfe"
MY_GEAR = "K2 Mindbender BOA (Size: 29.5)"

# מפת תרגום משודרגת - פותרת את בעיית קנדה וארה"ב
RESORT_DATABASE = {
    # קנדה (הוספתי שמות ספציפיים כדי שלא יברח לארה"ב)
    "Lake Louise": "Lake Louise,CA",
    "Jasper": "Jasper,CA",
    "Marmot Basin": "Jasper,CA",
    "Whistler": "Whistler,CA",
    "Banff": "Banff,CA",
    "Revelstoke": "Revelstoke,CA",
    "Kicking Horse": "Golden,CA",
    
    # ארה"ב - קולורדו ומונטנה
    "Breckenridge": "Breckenridge,US",
    "Beaver Creek": "Avon,US",
    "Vail": "Vail,US",
    "Aspen": "Aspen,US",
    "Big Sky": "Big Sky,US",
    "Steamboat": "Steamboat Springs,US",
    
    # אירופה (צרפת, אוסטריה, איטליה)
    "Val d'Isere": "Val-d'Isere,FR",
    "Avoriaz": "Morzine,FR",
    "St. Anton": "Sankt Anton am Arlberg,AT",
    "Ischgl": "Ischgl,AT",
    "Sella Ronda": "Canazei,IT",
    "Cervinia": "Breuil-Cervinia,IT"
}

def get_weather(query):
    q = query.strip()
    
    # 1. חיפוש חכם במאגר שלנו
    best_match, score = process.extractOne(q, list(RESORT_DATABASE.keys()))
    
    if score > 70:
        api_target = RESORT_DATABASE[best_match]
        display_name = f"{best_match} (via {api_target})"
    else:
        # אם לא מצאנו, נחפש רגיל
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

search_input = st.text_input("Search (e.g., Jasper, Lake Louise, Beaver Creek):")

if st.button("Check Conditions"):
    if search_input:
        data, name = get_weather(search_input)
        if data:
            st.session_state.resort_data = data
            st.session_state.display_name = name
        else:
            st.error(f"Could not find '{search_input}'. Please try another spelling.")

if 'resort_data' in st.session_state:
    res = st.session_state.resort_data
    st.divider()
    st.header(f"📍 {st.session_state.display_name}")
    
    # הצגת נתונים
    c1, c2, c3 = st.columns(3)
    c1.metric("Temp", f"{res['main']['temp']}°C")
    c2.metric("Feels Like", f"{res['main']['feels_like']}°C")
    c3.metric("Wind", f"{res['wind']['speed']} km/h")

    # לינקים חכמים לחיפוש
    st.subheader("🌟 Local Guide")
    q_enc = urllib.parse.quote(res['name'])
    st.markdown(f"🔗 [Best Après-Ski in {res['name']}](https://www.google.com/search?q={q_enc}+best+apres+ski)")
    st.markdown(f"🍽️ [Top Restaurants in {res['name']}](https://www.google.com/search?q={q_enc}+top+restaurants)")

st.sidebar.info(f"My Gear: {MY_GEAR}")
