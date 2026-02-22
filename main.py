import streamlit as st
import requests
from datetime import datetime
import urllib.parse
from thefuzz import process 

# --- Setup ---
st.set_page_config(page_title="SkiMaster Pro", page_icon="⛷️")

API_KEY = "3e830cd1e7024f7d1839481229012cfe"
MY_GEAR = "K2 Mindbender BOA (Size: 29.5)"

# רשימה מורחבת מאוד לתיקון שגיאות
RESORTS_LIST = [
    "Val d'Isere", "Val Thorens", "Ischgl", "St. Anton am Arlberg", "Tignes", 
    "Zermatt", "Chamonix", "Courchevel", "Meribel", "Verbier", "Mayrhofen", 
    "Sölden", "Kitzbühel", "Vail", "Aspen", "Livigno", "Cervinia", "Saalbach", 
    "Zell am See", "Bansko", "Gudauri", "Mount Hermon", "Cortina d'Ampezzo",
    "Les Arcs", "La Plagne", "Avoriaz", "Flaine", "Morzine", "Sestriere",
    "Crans-Montana", "Davos", "St. Moritz", "Bad Gastein", "Jackson Hole",
    "Whistler Blackcomb", "Park City", "Breckenridge", "Mammoth Mountain"
]

if 'resort_data' not in st.session_state:
    st.session_state.resort_data = None

def get_weather(query):
    # מנסה למצוא התאמה ברשימה (Fuzzy Matching)
    best_match, score = process.extractOne(query, RESORTS_LIST)
    
    # אם רמת ההתאמה גבוהה (מעל 65), נשתמש בשם המתוקן. אם לא, נשתמש במקור.
    final_query = best_match if score > 65 else query
    
    # ניקוי תווים מיוחדים
    api_name = final_query.replace("'", "").replace("’", "")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={api_name}&appid={API_KEY}&units=metric"
    
    try:
        res = requests.get(url).json()
        if res.get("cod") == 200:
            return res, final_query
        return None, None
    except:
        return None, None

# --- UI ---
st.title("⛷️ SkiMaster Pro")
st.write(f"📅 {datetime.now().strftime('%A, %d %B %Y')}")

search_input = st.text_input("Enter Resort Name (e.g. val diser, ishgl, hermon):")

if st.button("Check Conditions & Guide"):
    if search_input:
        data, corrected_name = get_weather(search_input)
        if data:
            st.session_state.resort_data = data
            if corrected_name.lower() != search_input.lower():
                st.info(f"Checking: **{corrected_name}**")
        else:
            st.error(f"Could not find weather for '{search_input}'. Try a nearby city.")

if st.session_state.resort_data:
    res = st.session_state.resort_data
    st.divider()
    st.header(f"📍 {res['name']}, {res['sys'].get('country', '')}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Temp", f"{res['main']['temp']}°C")
    c2.metric("Feels Like", f"{res['main']['feels_like']}°C")
    c3.metric("Wind", f"{res['wind']['speed']} km/h")
    
    # המלצות אפרה סקי ובילויים
    st.subheader("🍴 Après-Ski & Food Guide")
    q_enc = urllib.parse.quote(res['name'])
    
    # כפתורים מעוצבים לבילויים
    rec_col1, rec_col2 = st.columns(2)
    with rec_col1:
        st.markdown(f"🍺 [**Top Après-Ski Bars**](https://www.google.com/search?q={q_enc}+best+apres+ski+bars)")
        st.markdown(f"🥩 [**Best Dinner Spots**](https://www.google.com/search?q={q_enc}+top+restaurants)")
    with rec_col2:
        st.markdown(f"🎶 [**Events & Parties**](https://www.google.com/search?q={q_enc}+events+this+week)")
        st.markdown(f"🎥 [**Live Webcams**](https://www.google.com/search?q={q_enc}+live+webcams)")

st.sidebar.info(f"My Gear: {MY_GEAR}")
