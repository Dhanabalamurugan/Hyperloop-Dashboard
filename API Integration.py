
from turtle import st
import requests

API_KEY = "3715427ce9fcd3049ac5297cdeebe7ed"
CITY = "Chennai"

@st.cache_data(ttl=60)
def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        weather_main = data["weather"][0]["main"]
        wind_speed = data["wind"]["speed"]
        temperature = data["main"]["temp"]
        return weather_main, wind_speed, temperature
    else:
        return None, None, None
    
def suggest_safe_speed(weather, wind_speed):
    if weather in ["Thunderstorm", "Rain"]:
        return 300
    elif wind_speed > 15:
        return 400
    elif weather in ["Clear"]:
        return 800
    else:
        return 600

weather, wind_speed, temp = get_weather()

if weather:
    safe_speed = suggest_safe_speed(weather, wind_speed)

    st.subheader("🌦 Weather-Based Operational Advisory")
    st.write(f"Current Weather: {weather}")
    st.write(f"Wind Speed: {wind_speed} m/s")
    st.write(f"Temperature: {temp} °C")
    st.success(f"Suggested Safe Pod Speed: {safe_speed} km/h")
else:
    st.error("Weather API unavailable.")

def get_energy_tip():
    url = "https://jsonplaceholder.typicode.com/posts"
    response = requests.get(url)

    if response.status_code == 200:
        posts = response.json()
        import random
        tip = random.choice(posts)
        return tip["title"]
    else:
        return "Energy tip unavailable."

st.subheader("⚡ Energy Optimization Tip")
st.info(get_energy_tip())
