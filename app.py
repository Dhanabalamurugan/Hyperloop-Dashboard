import streamlit as st
import numpy as np
import pandas as pd
import random
import requests
import folium
import queue
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from streamlit_folium import st_folium
from datetime import datetime
from collections import deque
from streamlit_autorefresh import st_autorefresh
import json
import os
import time
import folium
load_dotenv()  
api_key = os.getenv("api_key")
mqtt_queue = queue.Queue()

st.set_page_config(page_title="Avishkar Hyperloop Dashboard", layout="wide")


# =========================================================
# ---------------------- FUNCTIONS ------------------------
# =========================================================

def compute_values():
    speed = st.session_state.speed
    acc = st.session_state.acceleration
    pressure = st.session_state.pressure

    temp = 0.005 * speed + 0.5 * acc
    st.session_state.temperature = round(
        st.session_state.temperature + temp * 0.01,
        2
    )

    if speed < 450:
        st.session_state.temperature = max(
            25,
            st.session_state.temperature - 0.1
        )

    if "battery" not in st.session_state:
        st.session_state.battery = 100.0
    drain = 0.02 * speed + 1.5 * acc
    st.session_state.battery = max(
        round(st.session_state.battery - drain * 0.01, 2),
        0
    )
    battery = st.session_state.battery

    return speed, acc, pressure, st.session_state.temperature, st.session_state.battery

def generate_pods(base_lat=None, base_lon=None):
    statuses = ["Operational", "Maintenance", "Docked"]
    pods = []
    for i in range(1, 6):
        pod = {
            "id": f"Pod-{i}",
            "speed": random.randint(500, 1000),
            "battery": random.randint(20, 100),
            "status": random.choice(statuses),
            "latitude": base_lat + random.uniform(-0.003, 0.003) if base_lat else None,
            "longitude": base_lon + random.uniform(-0.003, 0.003) if base_lon else None
        }
        pods.append(pod)
    return pods

def log_to_csv(data):
    file = "data/hyperloop_logs.csv"
    df = pd.DataFrame([data])
    if os.path.exists(file):
        df.to_csv(file, mode="a", header=False, index=False)
    else:
        df.to_csv(file, index=False)

def log_metrics():
    st.session_state.history["time"].append(datetime.now())
    st.session_state.history["speed"].append(st.session_state.speed)
    st.session_state.history["pressure"].append(st.session_state.pressure)
    st.session_state.history["battery"].append(st.session_state.battery)
    st.session_state.history["acceleration"].append(st.session_state.acceleration)
    st.session_state.history["temperature"].append(st.session_state.temperature)

@st.cache_data(ttl=300)
def fetch_weather(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    return None

@st.cache_data(ttl=60) 
def get_pod_data(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Error fetching data from OpenWeather API")
        return None
    data = response.json()
    latitude = data["coord"]["lat"]
    longitude = data["coord"]["lon"]
    return {"latitude": latitude, "longitude": longitude, "name": city}

def mqtt_on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print("MESSAGE ARRIVED:", payload)

    mqtt_queue.put({
        "data": payload,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
  

# =========================================================
# ------------------- CSS Layout-------------------------
# =========================================================

st.markdown("""
<style>
html, body, [class*="css"]  {
    background-color: #050a05;
    color: #00ff88;
}

.stButton>button {
    background-color: #003d1f;
    color: #00ff88;
    border: 1px solid #00ff88;
}

.stMetric {
    background-color: #001a0d;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #00ff88;
}

.sidebar .sidebar-content {
    background-color: #001a0d;
}

h1, h2, h3 {
    color: #00ff88;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# -------------------- LANDING PAGE ----------------------
# =========================================================

if "booted" not in st.session_state:
    st.session_state.booted = False

if not st.session_state["booted"]:

    st.markdown("""
    <h1 style='text-align:center;'>AVISHKAR HYPERLOOP CONTROL SYSTEM</h1>
    <h3 style='text-align:center;'>Year 2035 • Real-Time Pod Interface</h3>
    """, unsafe_allow_html=True)

    progress = st.progress(0)

    for i in range(100):
        time.sleep(0.01)
        progress.progress(i + 1)

    st.success("System Boot Complete")

    if st.button("Enter Control Center"):
        st.session_state["booted"] = True
        st.rerun()

    st.stop()

# =========================================================
# -------------------- SESSION INIT -----------------------
# =========================================================

if "history" not in st.session_state:
    st.session_state.history = {
        "time": deque(maxlen=50),
        "pressure": deque(maxlen=50),
        "speed": deque(maxlen=50),
        "acceleration": deque(maxlen=50),
        "temperature": deque(maxlen=50),
        "battery": deque(maxlen=50)
    }

defaults = {
    "speed": 800,
    "acceleration": 3.0,
    "pressure": 101325,
    "temperature": 25.0,
    "battery": 100
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

if "pods" not in st.session_state:
    st.session_state.pods = []

if "positions" not in st.session_state:
    st.session_state.positions = {f"Pod-{i}": random.randint(0, 100) for i in range(1,6)}

if "logs" not in st.session_state:
    st.session_state.logs = []

if "mqtt_data" not in st.session_state:
    st.session_state.mqtt_data = []

if "mqtt_queue" not in st.session_state:
    st.session_state.mqtt_queue = queue.Queue()

mqtt_queue = st.session_state.mqtt_queue

if "mqtt_client" not in st.session_state:

    client = mqtt.Client(
        client_id="streamlit_client",
        protocol=mqtt.MQTTv311,
        transport="tcp"
    )

    def on_connect(client, userdata, flags, rc, properties=None):
        print("Connected with result code:", rc)
        client.subscribe("hyperloop/pods/demo")
        print("Subscribed to hyperloop/pods/demo")

    client.on_connect = on_connect
    client.on_message = mqtt_on_message

    client.connect("127.0.0.1", 1883, 60)
    client.loop_start()

    st.session_state.mqtt_client = client

# =========================================================
# ---------------------- LOGIN ----------------------------
# =========================================================

USERS = {
    "ch25b033": {"password": "bala", "role": "Viewer"},
    "controller": {"password": "controller123", "role": "Controller"}
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.sidebar.title("🔐 Login")
    u = st.sidebar.text_input("Username")
    p = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if u in USERS and USERS[u]["password"] == p:
            st.session_state.logged_in = True
            st.session_state.role = USERS[u]["role"]
            st.success(f"Welcome {u}")
            st.rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# =========================================================
# ---------------------- NAVIGATION -----------------------
# =========================================================

with st.sidebar:

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(BASE_DIR, "assets", "club_logo.png")

    st.image(logo_path, width=140)

    st.markdown(
        """
        <p style='text-align:center; font-size:13px; color:gray;'>
            IIT Madras Tech Team
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "<hr style='border:1px solid #00FFAA; margin-top:10px; margin-bottom:15px;'>",
        unsafe_allow_html=True
    )

    section = st.radio(
        "Navigation",
        [
            "Overview",
            "Pod Tracker",
            "Performance Metrics",
            "Weather Monitoring",
            "Pod Comparison",
            "Live Track Map",
            "System Alerts",
            "Maintenance Logs",
            "Did You Know",
            "MQTT Live Data"
        ]
    )


# =========================================================
# ---------------------- OVERVIEW -------------------------
# =========================================================

if section == "Overview":
    st.title("Avishkar Hyperloop Control Center")

    st.markdown("""
    Welcome to the Avishkar Hyperloop Monitoring Dashboard.

    This system provides real-time monitoring and control insights
    for all operational pods across the test track.

    Use the navigation panel to access:

    • Pod Tracker – View individual pod details  
    • Performance Metrics – System telemetry & analytics  
    • Route Monitoring – Track movement across the track  
    • Pod Comparision – Diagnostics & alerts  
    • Live Track Map – Real-time GPS visualization  
    • System Alerts – Critical warnings  
    • Maintenance Logs – Service history  

    This dashboard simulates a live Hyperloop control environment.
    """)

# =========================================================
# ---------------------- POD TRACKER ----------------------
# =========================================================

elif section == "Pod Tracker":
    st.header("Pod Tracker")

    if not st.session_state.pods:
        st.warning("Pods not initialized yet. Visit Live Track Map first.")
        st.stop()

    df = pd.DataFrame(st.session_state.pods)

    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "Operational", "Maintenance", "Docked"]
    )

    if status_filter != "All":
        df = df[df["status"] == status_filter]

    st.dataframe(df, use_container_width=True)

# =========================================================
# ---------------- PERFORMANCE METRICS --------------------
# =========================================================

elif section == "Performance Metrics":

    st.header("Performance Metrics")
    st.write("Real-time performance data and trends.")

    rt_mode = st.toggle("Enable RT Linux Mode (1ms Latency)", key="rt_mode")
    auto_mode = st.toggle("Auto-Run Simulation Mode", key="auto_mode")

    battery_dead = st.session_state.battery <= 0

    if battery_dead:
        st.error("Battery depleted. Simulation stopped.")

    if auto_mode:
        st.session_state.speed = random.randint(0, 1200)
        st.session_state.acceleration = round(random.uniform(0.0, 10.0), 2)
        st.session_state.pressure = random.randint(90000, 110000)

    st.slider("Speed", 0, 1200, key="speed")
    st.slider("Acceleration", 0.0, 10.0, key="acceleration")
    st.slider("Pressure", 90000, 110000, key="pressure")

    speed, acc, pressure, temp, battery = compute_values()

    log_metrics()

    chart_df = pd.DataFrame(st.session_state.history)
    chart_df["time"] = pd.to_datetime(chart_df["time"])
    chart_df = chart_df.sort_values("time")
    chart_df = chart_df.set_index("time")

    st.subheader("Performance Trends")

    metric_option = st.selectbox(
        "Select Parameter",
        ["speed", "acceleration", "temperature", "battery", "pressure"]
    )

    st.line_chart(chart_df[metric_option])

    if st.button("Reset Simulation"):
        st.session_state.battery = 100.0
        st.session_state.temperature = 25.0
        st.session_state.history = {
            "time": deque(maxlen=50),
            "speed": deque(maxlen=50),
            "acceleration": deque(maxlen=50),
            "pressure": deque(maxlen=50),
            "temperature": deque(maxlen=50),
            "battery": deque(maxlen=50),
        }
        st.success("Simulation Reset.")
        st.rerun()

    if auto_mode and not battery_dead:
        time.sleep(0.05 if rt_mode else 0.5)
        st.rerun()

    st.markdown("""
    <style>
    button {
        cursor: pointer;
    }
    .stselectbox, .stMultiSelect {
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button("Log Current Metrics"):
        log_data = {
            "Time": datetime.now(),
            "Speed": speed,
            "Acceleration": acc,
            "Temperature": temp,
            "Battery": battery,
            "Pressure": pressure
        }

        log_to_csv(log_data)
        st.success("Logged to CSV")

# =========================================================
# ---------------- ROUTE MONITORING -----------------------
# =========================================================

elif section == "Weather Monitoring":

    st.header("Weather Monitoring")
    city = st.text_input("City", "Chengalpattu")

    if st.button("Fetch Weather"):
        data = fetch_weather(city, api_key)
        if data:
            temp = data["main"]["temp"]
            weather = data["weather"][0]["description"]

            st.metric("Temperature (°C)", temp)
            st.write("Condition:", weather)

            if "rain" in weather.lower() or "overcast clouds" in weather.lower() or "haze" in weather.lower():
                st.warning("Suggested Speed Limit: 700 km/h")
            else:
                st.success("Suggested Speed Limit: 900 km/h")
        else:
            st.error("Weather fetch failed")

# =========================================================
# ---------------- POD HEALTH INSIGHTS --------------------
# =========================================================

elif section == "Pod Comparision":

    st.header("Compare Pods")

    df = pd.DataFrame(generate_pods())

    pod1 = st.selectbox("Pod 1", df["id"], index=0)
    pod2 = st.selectbox("Pod 2", df["id"], index=1)

    st.dataframe(df[df["id"].isin([pod1,pod2])])

# =========================================================
# ---------------- LIVE TRACK MAP -------------------------
# =========================================================

elif section == "Live Track Map":

    st.header("Live Pod Position Tracking")

    city = st.text_input("City", "Chengalpattu")
    pod_info = get_pod_data(city)

    if "current_city" not in st.session_state:
        st.session_state.current_city = city

    if st.session_state.current_city != city:
        st.session_state.pods = generate_pods(
            base_lat=pod_info["latitude"],
            base_lon=pod_info["longitude"]
        )
        st.session_state.current_city = city

    if not pod_info:
        st.error("City not found or API error.")
        st.stop()

    if not st.session_state.pods:

        st.session_state.pods = generate_pods(
            base_lat=pod_info["latitude"],
            base_lon=pod_info["longitude"]
        )

        st.session_state.last_update = time.time()

    if st.button(" Update Pod Positions"):

        for pod in st.session_state.pods:
            pod["latitude"] += random.uniform(-0.005, 0.005)
            pod["longitude"] += random.uniform(-0.005, 0.005)
            pod["battery"] = max(pod["battery"] - random.uniform(1, 3), 0)
            
        st.session_state.last_update = time.time()

    m = folium.Map(
        location=[pod_info["latitude"], pod_info["longitude"]],
        zoom_start=14,
        tiles="CartoDB dark_matter"
    )

    for pod in st.session_state.pods:

        if pod["latitude"] is None or pod["longitude"] is None:
            continue

        if pod["status"] == "Operational":
            color = "green"
        elif pod["status"] == "Maintenance":
            color = "orange"
        else:
            color = "gray"

        folium.CircleMarker(
            location=[pod["latitude"], pod["longitude"]],
            radius=9,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            tooltip=f"{pod['id']} | {pod['status']}",
            popup=f"""
            <b>{pod['id']}</b><br>
            Speed: {pod['speed']} km/h<br>
            Battery: {round(pod['battery'],1)}%<br>
            Status: {pod['status']}
            """
        ).add_to(m)

    st_folium(m, width=900, height=550)

# ---------------- SYSTEM ALERTS --------------------------
# =========================================================

elif section == "System Alerts":

    speed, acc, pressure, temp, battery = compute_values()

    if battery < 20:
        st.error("Battery Critical!")
    elif temp > 80:
        st.warning("High Temperature Warning")
    else:
        st.success("All systems operational")

# =========================================================
# ---------------- MAINTENANCE LOGS -----------------------
# =========================================================

elif section == "Maintenance Logs":

    with st.form("log_form"):
        engineer = st.text_input("Engineer Name")
        issue = st.text_area("Issue")
        severity = st.selectbox("Severity",["Low","Medium","High","Critical"])
        submitted = st.form_submit_button("Submit")

        if submitted:
            entry = {
                "Time": datetime.now(),
                "Engineer": engineer,
                "Issue": issue,
                "Severity": severity
            }
            st.session_state.logs.append(entry)
            st.success("Log Added")

    if st.session_state.logs:
        st.dataframe(pd.DataFrame(st.session_state.logs))

# =========================================================
# ---------------- DID YOU KNOW ---------------------------
# =========================================================

elif section == "Did You Know":

    st.header("Hyperloop Fun Fact")

    if st.button("Generate Fact"):
        url="https://uselessfacts.jsph.pl/random.json?language=en"
        response= requests.get(url)
        if response.status_code == 200:
            st.info(response.json()["text"])

# =========================================================
# ---------------- MQTT LIVE DATA -------------------------
# ========================================================= 

elif section == "MQTT Live Data":

    st.title("🚄 Hyperloop MQTT Live Control Panel")
    st_autorefresh(interval=1000, key="mqtt_refresh")
    client = st.session_state.get("mqtt_client", None)

    while not mqtt_queue.empty():
        data = mqtt_queue.get()
        st.session_state.mqtt_data.append(data)


    if client is not None and client.is_connected():
        st.markdown(
            "<h3 style='color:lime;'>🟢 MQTT Broker Connected (localhost:1883)</h3>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<h3 style='color:red;'>🔴 MQTT Broker NOT Connected</h3>",
            unsafe_allow_html=True
        )

    message_count = len(st.session_state.mqtt_data)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("📡 Total Messages Received", message_count)

    with col2:
        if message_count > 0:
            st.metric("🕒 Last Update",
                      datetime.now().strftime("%H:%M:%S"))
        else:
            st.metric("🕒 Last Update", "No Data")

    st.divider()

    if message_count > 0:
        latest = st.session_state.mqtt_data[-1]

        st.markdown(
            """
            <div style='
                background-color:#111;
                padding:20px;
                border-radius:12px;
                border:1px solid #00FFAA;
                box-shadow: 0 0 15px #00FFAA;
            '>
            <h4 style='color:#00FFAA;'> Latest Pod Data</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        try:
            st.json(json.loads(latest))
        except:
            st.code(latest)

    else:
        st.warning("Waiting for incoming MQTT telemetry data...")


