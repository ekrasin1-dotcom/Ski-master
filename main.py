import streamlit as st
import requests
from datetime import datetime
import urllib.parse

# --- Page Configuration ---
st.set_page_config(page_title="SkiMaster Pro", page_icon="⛷️", layout="centered")

# --- Custom Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Your API Key & Gear Info ---
API_KEY = "3e830cd1e7024f7d1839481229012cfe"
MY_GEAR = "K2 Mindbender BOA (Size: 29.5)"

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        return res if res.get("cod") == 200 else None
    except:
        return None

# --- App Interface ---
st.title("⛷️ SkiMaster Pro")
st.write(f"{datetime.now().strftime('%A, %d %B %Y')}")

# Sidebar - Gear & Stats
with st.sidebar:
    st.header("🎿 My Gear")
    st.info(f"**Boots:** {MY_GEAR}")
    st.write("---")
    st.write("❄️ *Have a great session on the slopes!*")

# Input for Resort
resort = st.text_input("Enter Ski Resort Name:", placeholder="e.g. Val Thorens, Ischgl, St. Anton")

if resort:
    data = get_weather(resort)
    
    if data:
        # Weather Display
        st.subheader(f"Current Status in {resort.capitalize()}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Temp", f"{data['main']['temp']}°C")
        with col2:
            st.metric("Wind", f"{data['wind']['speed']} km/h")
        with col3:
            st.metric("Humidity", f"{data['main']['humidity']}%")
            
        st.write(f"**Condition:** {data['weather'][0]['description'].capitalize()}")
        st.image(f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png")

        st.divider()

        # Action Buttons (Smart Links)
        st.subheader("📍 Explore the Resort")
        resort_encoded = urllib.parse.quote(resort)
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown(f"[🍴 Top Restaurants](https://www.google.com/search?q=best+restaurants+in+{resort_encoded}+open+now)")
            st.markdown(f"[🎉 Events & Festivals](https://www.google.com/search?q=events+and+festivals+in+{resort_encoded}+this+week)")

        with col_b:
            st.markdown(f"[🗺️ Piste Map](https://www.google.com/search?q={resort_encoded}+ski+piste+map+high+resolution)")
            st.markdown(f"[🍻 Best Après-Ski](https://www.google.com/search?q=best+apres+ski+bars+in+{resort_encoded})")

        # Dynamic Tip
        st.divider()
        if data['main']['temp'] < -5:
            st.warning("It's cold! Perfect weather for a hot Fondue or a fresh Carpaccio inside a cozy hut.")
        else:
            st.success("Great weather! Enjoy a fresh Beef Carpaccio on a sunny terrace.")
            
    else:
        st.error("Resort not found. Please check your spelling (use English names).")

else:
    st.info("Enter a resort name to get live weather, food recommendations, and events.")

st.caption("Data provided by OpenWeather API")
