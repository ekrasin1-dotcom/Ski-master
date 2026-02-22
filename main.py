import streamlit as st
import requests
from datetime import datetime
import urllib.parse
from thefuzz import process 

# --- Setup ---
st.set_page_config(page_title="SkiMaster Pro", page_icon="⛷️")

API_KEY = "3e830cd1e7024f7d1839481229012cfe"
MY_GEAR = "K2 Mindbender BOA (Size: 29.5)"

# מפת "תרגום" - מקשרת בין השם שאתה מכיר לשם שה-API צריך (עיר ומדינה)
# הוספתי כאן את האתרים הגדולים בצרפת, אוסטריה, איטליה, ארה"ב, קנדה ויפן
RESORT_TRANSLATION_MAP = {
    # ארה"ב - קולורדו ומונטנה
    "Breckenridge": "Breckenridge,US",
    "Beaver Creek": "Avon,US",
    "Vail": "Vail,US",
    "Aspen": "Aspen,US",
    "Steamboat": "Steamboat Springs,US",
    "Big Sky": "Big Sky,US",
    "Telluride": "Telluride,US",
    "Keystone": "Keystone,US",
    
    # קנדה
    "Whistler": "Whistler,CA",
    "Kicking Horse": "Golden,CA",
    "Lake Louise": "Lake Louise,CA",
    "Revelstoke": "Revelstoke,CA",
    "Banff": "Banff,CA",
    
    # צרפת
    "Val d'Isere": "Val-d'Isere,FR",
    "Val Thorens": "Val Thorens,FR",
    "Les Arcs": "Bourg-Saint-Maurice,FR",
    "Tignes": "Tignes,FR",
    
    # איטליה
    "Sella Ronda": "Canazei,IT",
    "Campitello": "Campitello di Fassa,IT",
    "Val di Fassa": "Canazei,IT",
    "Cervinia": "Breuil-Cervinia,IT",
    
    # אוסטריה
    "Ischgl": "Ischgl,AT",
    "St. Anton": "Sankt Anton am Arlberg,AT",
    "Mayrhofen": "Mayrhofen,AT",
    
    # יפן
    "Niseko": "Niseko,JP",
    "Hakuba": "Hakuba,JP"
}

def get_weather(user_query):
    # 1. תיקון שגיאות כתיב חכם (Fuzzy Search) מול המפה שלנו
    # מחזיר את השם הכי קרוב ואת רמת הביטחון (score)
    all_known_names = list(RESORT_TRANSLATION_MAP.keys())
    best_match, score = process.extractOne(user_query, all_known_names)
    
    # אם רמת ההתאמה גבוהה מ-60%, נשתמש בתרגום שלנו
    if score > 60:
        api_target = RESORT_TRANSLATION_MAP[best_match]
        display_name = best_match
    else:
        # אם אין התאמה, ננסה לשלוח את מה שהמשתמש כתב כמו שהוא
        api_target = user_query
        display_name = user_query

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

# שורת החיפוש החופשית שלך
search_input = st.text_input("Enter Ski Resort:", placeholder="e.g. brecking ridge, val diser, kick horse...")

if st.button("Analyze & Get Weather"):
    if search_input:
        data, corrected_name = get_weather(search_input)
        if data:
            st.session_state.resort_data = data
            st.success(f"✅ Interpreted as: **{corrected_name}**")
        else:
            st.error(f"Sorry, couldn't translate '{search_input}' to a known resort. Try a different spelling.")

if 'resort_data' in st.session_state and st.session_state.resort_data:
    res = st.session_state.resort_data
    st.divider()
    
    st.header(f"📍 {res['name']}, {res['sys'].get('country', '')}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Temp", f"{res['main']['temp']}°C")
    col2.metric("Feels Like", f"{res['main']['feels_like']}°C")
    col3.metric("Wind", f"{res['wind']['speed']} km/h")

    # המלצות גמישות
    st.subheader("🌟 SkiMaster Recommendations")
    q_enc = urllib.parse.quote(res['name'])
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"🍺 [**Après-Ski Guide**](https://www.google.com/search?q={q_enc}+best+apres+ski+bars)")
        st.markdown(f"🍽️ [**Best Food**](https://www.google.com/search?q={q_enc}+top+restaurants)")
    with c2:
        st.markdown(f"🎶 [**What's On?**](https://www.google.com/search?q={q_enc}+events+festivals)")
        st.markdown(f"🎥 [**Live Webcams**](https://www.google.com/search?q={q_enc}+webcams+live)")

st.sidebar.info(f"Gear: {MY_GEAR}")
