import streamlit as st
import pandas as pd
import random
import requests
import folium
import queue
import hashlib
import paho.mqtt.client as mqtt
from dotenv import load_dotenv, find_dotenv
from streamlit_folium import st_folium
from datetime import datetime
from collections import deque
from streamlit_autorefresh import st_autorefresh
import json
import os
import time

load_dotenv(find_dotenv())
api_key = os.getenv("api_key")

# =========================================================
# ---------------------- USERS & ROLES --------------------
# =========================================================

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

USERS = {
    "ch25b033":   {"password": hash_pw("bala"),          "role": "Viewer"},
    "controller": {"password": hash_pw("controller123"), "role": "Controller"},
}

ROLE_PAGES = {
    "Viewer":     ["Overview", "Pod Tracker", "Weather Monitoring",
                   "Live Track Map", "Did You Know", "MQTT Live Data"],
    "Controller": ["Overview", "Pod Tracker", "Performance Metrics",
                   "Weather Monitoring", "Pod Comparison", "Live Track Map",
                   "System Alerts", "Maintenance Logs", "Did You Know", "MQTT Live Data"],
}

ALL_PAGES = [
    "Overview", "Pod Tracker", "Performance Metrics", "Weather Monitoring",
    "Pod Comparison", "Live Track Map", "System Alerts",
    "Maintenance Logs", "Did You Know", "MQTT Live Data",
]

st.set_page_config(page_title="Avishkar Hyperloop Dashboard", layout="wide")

# =========================================================
# ---------------------- FUNCTIONS ------------------------
# =========================================================

def compute_values():
    speed    = st.session_state.speed
    acc      = st.session_state.acceleration
    pressure = st.session_state.pressure
    temp_delta = 0.005 * speed + 0.5 * acc
    st.session_state.temperature = round(st.session_state.temperature + temp_delta * 0.01, 2)
    if speed < 450:
        st.session_state.temperature = max(25, st.session_state.temperature - 0.1)
    drain = 0.02 * speed + 1.5 * acc
    st.session_state.battery = max(round(st.session_state.battery - drain * 0.01, 2), 0)
    return speed, acc, pressure, st.session_state.temperature, st.session_state.battery


def generate_pods(base_lat=None, base_lon=None):
    statuses = ["Operational", "Maintenance", "Docked"]
    return [
        {
            "id":        f"Pod-{i}",
            "speed":     random.randint(500, 1000),
            "battery":   random.randint(20, 100),
            "status":    random.choice(statuses),
            "latitude":  base_lat + random.uniform(-0.003, 0.003) if base_lat else None,
            "longitude": base_lon + random.uniform(-0.003, 0.003) if base_lon else None,
        }
        for i in range(1, 6)
    ]


def log_to_csv(data, filename="hyperloop_logs.csv"):
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df = pd.DataFrame([data])
    if os.path.exists(file_path):
        df.to_csv(file_path, mode="a", header=False, index=False, quoting=1)
    else:
        df.to_csv(file_path, index=False, quoting=1)


def log_metrics():
    for key in ["time", "speed", "pressure", "battery", "acceleration", "temperature"]:
        val = datetime.now() if key == "time" else st.session_state[key]
        st.session_state.history[key].append(val)


def require_role(page_name):
    role          = st.session_state.get("role", "Viewer")
    allowed_pages = ROLE_PAGES.get(role, [])
    if page_name not in allowed_pages:
        st.markdown(
            f"<div class='locked-msg'>⛔ ACCESS DENIED<br><br>"
            f"<span style='font-size:0.8rem;color:#664444;'>"
            f"This section requires Controller privileges.<br>Current role: {role}</span></div>",
            unsafe_allow_html=True,
        )
        return False
    return True


@st.cache_data(ttl=300)
def fetch_weather(city, api_key):
    url      = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None


@st.cache_data(ttl=60)
def get_pod_data(city, api_key):
    url      = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    return {"latitude": data["coord"]["lat"], "longitude": data["coord"]["lon"], "name": city}

def mqtt_on_message(client, userdata, msg):
    try:
        userdata.put({
            "data": msg.payload.decode(),
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    except Exception:
        pass


# =========================================================
# ---------------------- CSS ------------------------------
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    background-color: #04080f !important;
    color: #a8d8ff !important;
    font-family: 'Exo 2', sans-serif !important;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060d1a 0%, #04080f 100%) !important;
    border-right: 1px solid rgba(0,170,255,0.15) !important;
}
div[data-testid="metric-container"] {
    background: rgba(0,120,255,0.07) !important;
    border: 1px solid rgba(0,170,255,0.2) !important;
    border-radius: 10px !important;
    padding: 14px !important;
}
.stButton > button {
    background: transparent !important;
    color: #00aaff !important;
    border: 1px solid #00aaff !important;
    border-radius: 6px !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 1px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(0,170,255,0.12) !important;
    box-shadow: 0 0 12px rgba(0,170,255,0.3) !important;
}
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > div > textarea {
    background: rgba(0,20,50,0.8) !important;
    border: 1px solid rgba(0,170,255,0.25) !important;
    color: #a8d8ff !important;
    border-radius: 6px !important;
}
h1, h2, h3 {
    font-family: 'Share Tech Mono', monospace !important;
    color: #00aaff !important;
    letter-spacing: 2px !important;
}
.stDataFrame { border: 1px solid rgba(0,170,255,0.15) !important; border-radius: 8px !important; }
div[role="radiogroup"] label { color: #7ab8e8 !important; font-size: 0.88rem !important; }
.stSlider > div > div > div { background: rgba(0,170,255,0.3) !important; }
.page-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.5rem;
    color: #00aaff;
    text-shadow: 0 0 20px rgba(0,170,255,0.5);
    letter-spacing: 3px;
    border-bottom: 1px solid rgba(0,170,255,0.2);
    padding-bottom: 0.5rem;
    margin-bottom: 1.2rem;
}
.role-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 1px;
    margin-top: 4px;
}
.role-controller { background: rgba(0,255,136,0.12); border: 1px solid #00ff88; color: #00ff88; }
.role-viewer     { background: rgba(0,170,255,0.12); border: 1px solid #00aaff; color: #00aaff; }
.locked-msg {
    text-align: center;
    padding: 3rem 2rem;
    border: 1px solid rgba(255,100,100,0.2);
    border-radius: 12px;
    background: rgba(255,50,50,0.04);
    color: #ff6666;
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 2px;
    margin-top: 2rem;
}
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #04080f; }
::-webkit-scrollbar-thumb { background: rgba(0,170,255,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# -------------------- LANDING PAGE ----------------------
# =========================================================

if "booted" not in st.session_state:
    st.session_state.booted = False

if not st.session_state.booted:
    st.markdown("""
    <div style='text-align:center; padding:4rem 0 2rem;'>
      <h1 style='font-family:Share Tech Mono,monospace;font-size:2rem;color:#00aaff;
                 text-shadow:0 0 30px rgba(0,170,255,0.6);letter-spacing:4px;'>
        AVISHKAR HYPERLOOP
      </h1>
      <p style='color:#3a6080;font-family:Share Tech Mono,monospace;letter-spacing:3px;'>
        CONTROL SYSTEM — YEAR 2035
      </p>
    </div>
    """, unsafe_allow_html=True)
    progress = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress.progress(i + 1)
    st.success("System Boot Complete")
    if st.button("⚡  Enter Control Center"):
        st.session_state.booted = True
        st.rerun()
    st.stop()

# =========================================================
# -------------------- SESSION INIT -----------------------
# =========================================================

if "history" not in st.session_state:
    st.session_state.history = {
        k: deque(maxlen=50)
        for k in ["time", "pressure", "speed", "acceleration", "temperature", "battery"]
    }

for key, value in {"speed": 800, "acceleration": 3.0, "pressure": 101325,
                   "temperature": 25.0, "battery": 100.0}.items():
    if key not in st.session_state:
        st.session_state[key] = value

for key, default in [("pods", []), ("logs", []), ("mqtt_data", []), ("alerts", [])]:
    if key not in st.session_state:
        st.session_state[key] = default

if "positions" not in st.session_state:
    st.session_state.positions = {f"Pod-{i}": random.randint(0, 100) for i in range(1, 6)}

if "mqtt_queue" not in st.session_state:
    st.session_state.mqtt_queue = queue.Queue()

if "mqtt_client" not in st.session_state:
    client = mqtt.Client(
        client_id="streamlit_client",
        protocol=mqtt.MQTTv311,
        transport="tcp",
        userdata=st.session_state.mqtt_queue 
    )

    def on_connect(c, userdata, flags, rc, properties=None):
        c.subscribe("hyperloop/pods/demo")

    client.on_connect = on_connect
    client.on_message = mqtt_on_message
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_start()
    st.session_state.mqtt_client = client

# =========================================================
# ---------------------- LOGIN ----------------------------
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def login():
    st.markdown("""
    <div style='
        position:fixed; top:0; left:240px; right:0; bottom:0;
        display:flex; align-items:center; justify-content:center;
    '>
        <div style='text-align:center;'>
            <p style='font-family:Share Tech Mono,monospace; font-size:4rem;
                      color:#00aaff; text-shadow:0 0 60px rgba(0,170,255,0.8),
                      0 0 120px rgba(0,170,255,0.3);
                      letter-spacing:10px; margin:0; line-height:1;'>AVISHKAR</p>
            <p style='font-family:Share Tech Mono,monospace; font-size:1.1rem;
                      color:#4a8aab; letter-spacing:6px; margin:8px 0 0;'>
                      HYPERLOOP CONTROL SYSTEM</p>
            <p style='font-family:Share Tech Mono,monospace; font-size:0.75rem;
                      color:#2a5a6a; letter-spacing:3px; margin-top:6px;'>
                      YEAR 2035 • IIT MADRAS</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<div class='page-title' style='font-size:1rem;'>🔐 LOGIN</div>",
                        unsafe_allow_html=True)
    u = st.sidebar.text_input("Username")
    p = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if u in USERS and USERS[u]["password"] == hash_pw(p):
            st.session_state.logged_in = True
            st.session_state.role      = USERS[u]["role"]
            st.session_state.username  = u
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials")


if not st.session_state.logged_in:
    login()
    st.stop()

# =========================================================
# ---------------------- NAVIGATION -----------------------
# =========================================================

role = st.session_state.get("role", "Viewer")

with st.sidebar:
    BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(BASE_DIR, "assets", "club_logo.png")
    st.markdown(
        "<div style='padding-left:28px;'>",
        unsafe_allow_html=True
    )
    if os.path.exists(logo_path):
        st.image(logo_path, width=140)
    st.markdown("</div>", unsafe_allow_html=True)

    badge_class = "role-controller" if role == "Controller" else "role-viewer"
    st.markdown(
        f"<div style='text-align:center;margin-bottom:0.8rem;'>"
        f"<span style='color:#4a7a9b;font-size:0.8rem;'>👤 {st.session_state.get('username','')}</span><br>"
        f"<span class='role-badge {badge_class}'>{role.upper()}</span></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<hr style='border:1px solid rgba(0,170,255,0.15);margin:8px 0 14px;'>",
                unsafe_allow_html=True)

    section = st.radio("Navigation", ALL_PAGES)

    st.markdown("<hr style='border:1px solid rgba(0,170,255,0.1);margin:14px 0 8px;'>",
                unsafe_allow_html=True)
    if st.button("Logout"):
        for k in ["logged_in", "role", "username"]:
            st.session_state.pop(k, None)
        st.rerun()

# =========================================================
# ---------------------- OVERVIEW -------------------------
# =========================================================

if section == "Overview":
    st.markdown("<div class='page-title'>◈ SYSTEM OVERVIEW</div>", unsafe_allow_html=True)
    st.markdown("""
    Welcome to the **Avishkar Hyperloop Monitoring Dashboard**.

    This system provides real-time monitoring and control insights
    for all operational pods across the test track.

    Use the navigation panel to access:

    • **Pod Tracker** — View individual pod details  
    • **Performance Metrics** — System telemetry & analytics *(Controller only)*  
    • **Weather Monitoring** — Track conditions along the route  
    • **Pod Comparison** — Compare pods side-by-side *(Controller only)*  
    • **Live Track Map** — Real-time GPS visualization  
    • **System Alerts** — Critical warnings *(Controller only)*  
    • **Maintenance Logs** — Service history *(Controller only)*  
    """)

# =========================================================
# ---------------------- POD TRACKER ----------------------
# =========================================================

elif section == "Pod Tracker":
    if not require_role("Pod Tracker"): st.stop()
    st.markdown("<div class='page-title'>◈ POD TRACKER</div>", unsafe_allow_html=True)

    if not st.session_state.pods:
        st.warning("Pods not initialized. Visit Live Track Map first.")
        st.stop()

    df            = pd.DataFrame(st.session_state.pods)
    status_filter = st.selectbox("Filter by Status", ["All", "Operational", "Maintenance", "Docked"])
    if status_filter != "All":
        df = df[df["status"] == status_filter]
    st.dataframe(df, use_container_width=True)

# =========================================================
# ---------------- PERFORMANCE METRICS --------------------
# =========================================================

elif section == "Performance Metrics":
    if not require_role("Performance Metrics"): st.stop()
    st.markdown("<div class='page-title'>◈ PERFORMANCE METRICS</div>", unsafe_allow_html=True)

    rt_mode   = st.toggle("Enable RT Linux Mode (1ms Latency)", key="rt_mode")
    auto_mode = st.toggle("Auto-Run Simulation Mode",           key="auto_mode")

    battery_dead = st.session_state.battery <= 0
    if battery_dead:
        st.error("⚠ Battery depleted. Simulation stopped.")

    if auto_mode:
        st.session_state.speed        = random.randint(0, 1200)
        st.session_state.acceleration = round(random.uniform(0.0, 10.0), 2)
        st.session_state.pressure     = random.randint(90000, 110000)

    st.slider("Speed (km/h)",        0,     1200,   key="speed")
    st.slider("Acceleration (m/s²)", 0.0,   10.0,   key="acceleration")
    st.slider("Pressure (Pa)",       90000, 110000, key="pressure")

    speed, acc, pressure, temp, battery = compute_values()
    log_metrics()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Speed",       f"{speed} km/h")
    c2.metric("Temperature", f"{temp} °C")
    c3.metric("Battery",     f"{battery} %")
    c4.metric("Pressure",    f"{pressure} Pa")

    chart_df = pd.DataFrame(st.session_state.history)
    chart_df["time"] = pd.to_datetime(chart_df["time"])
    chart_df = chart_df.sort_values("time").set_index("time")

    st.subheader("Performance Trends")
    metric_option = st.selectbox("Select Parameter",
                                 ["speed", "acceleration", "temperature", "battery", "pressure"])
    st.line_chart(chart_df[metric_option])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Reset Simulation"):
            st.session_state.battery     = 100.0
            st.session_state.temperature = 25.0
            st.session_state.history     = {
                k: deque(maxlen=50)
                for k in ["time", "pressure", "speed", "acceleration", "temperature", "battery"]
            }
            st.success("Simulation reset.")
            st.rerun()
    with col2:
        if st.button("Log Current Metrics"):
            log_to_csv({"Time": datetime.now(), "Speed": speed, "Acceleration": acc,
                        "Temperature": temp, "Battery": battery, "Pressure": pressure})
            st.success("Logged to CSV.")

    if auto_mode and not battery_dead:
        time.sleep(0.05 if rt_mode else 0.5)
        st.rerun()

# =========================================================
# ---------------- WEATHER MONITORING ---------------------
# =========================================================

elif section == "Weather Monitoring":
    if not require_role("Weather Monitoring"): st.stop()
    st.markdown("<div class='page-title'>◈ WEATHER MONITORING</div>", unsafe_allow_html=True)

    city = st.text_input("City", "Chengalpattu")
    if st.button("Fetch Weather"):
        data = fetch_weather(city, api_key)
        if data:
            temp    = data["main"]["temp"]
            weather = data["weather"][0]["description"]
            st.metric("Temperature (°C)", temp)
            st.write("Condition:", weather)
            if any(w in weather.lower() for w in ["rain", "overcast", "haze"]):
                st.warning("Suggested Speed Limit: 700 km/h")
            else:
                st.success("Suggested Speed Limit: 900 km/h")
        else:
            st.error("Weather fetch failed.")

# =========================================================
# ---------------- POD COMPARISON -------------------------
# =========================================================

elif section == "Pod Comparison":
    if not require_role("Pod Comparison"): st.stop()
    st.markdown("<div class='page-title'>◈ POD COMPARISON</div>", unsafe_allow_html=True)

    df  = pd.DataFrame(generate_pods())
    ids = df["id"].tolist()

    col1, col2 = st.columns(2)
    pod1 = col1.selectbox("Pod A", ids, index=0)
    pod2 = col2.selectbox("Pod B", ids, index=1)

    selected = (df[df["id"].isin([pod1, pod2])]
                .set_index("id")
                .drop(columns=["latitude", "longitude"]))

    st.subheader("Raw Data")
    st.dataframe(selected, use_container_width=True)

    st.subheader("Speed Comparison")
    st.bar_chart(selected[["speed"]])

    st.subheader("Battery Comparison")
    st.bar_chart(selected[["battery"]])

    st.subheader("Head-to-Head")
    compare_df = selected[["speed", "battery"]].T
    compare_df.columns = [pod1, pod2]
    compare_df["Winner"] = compare_df.apply(
        lambda row: pod1 if row[pod1] > row[pod2] else pod2, axis=1)
    st.dataframe(compare_df, use_container_width=True)

# =========================================================
# ---------------- LIVE TRACK MAP -------------------------
# =========================================================

elif section == "Live Track Map":
    if not require_role("Live Track Map"): st.stop()
    st.markdown("<div class='page-title'>◈ LIVE TRACK MAP</div>", unsafe_allow_html=True)

    city     = st.text_input("City", "Chengalpattu")
    pod_info = get_pod_data(city, api_key)

    if "current_city" not in st.session_state:
        st.session_state.current_city = city

    if st.session_state.current_city != city and pod_info:
        st.session_state.pods         = generate_pods(pod_info["latitude"], pod_info["longitude"])
        st.session_state.current_city = city

    if not pod_info:
        st.error("City not found or API error.")
        st.stop()

    if not st.session_state.pods:
        st.session_state.pods        = generate_pods(pod_info["latitude"], pod_info["longitude"])
        st.session_state.last_update = time.time()

    if st.button("⟳ Update Pod Positions"):
        for pod in st.session_state.pods:
            pod["latitude"]  += random.uniform(-0.005, 0.005)
            pod["longitude"] += random.uniform(-0.005, 0.005)
            pod["battery"]    = max(pod["battery"] - random.uniform(1, 3), 0)
        st.session_state.last_update = time.time()

    m = folium.Map(location=[pod_info["latitude"], pod_info["longitude"]],
                   zoom_start=14, tiles="CartoDB dark_matter")

    for pod in st.session_state.pods:
        if pod["latitude"] is None:
            continue
        color = {"Operational": "green", "Maintenance": "orange"}.get(pod["status"], "gray")
        folium.CircleMarker(
            location=[pod["latitude"], pod["longitude"]],
            radius=9, color=color, fill=True, fill_color=color, fill_opacity=0.8,
            tooltip=f"{pod['id']} | {pod['status']}",
            popup=(f"<b>{pod['id']}</b><br>Speed: {pod['speed']} km/h<br>"
                   f"Battery: {round(pod['battery'],1)}%<br>Status: {pod['status']}"),
        ).add_to(m)

    st_folium(m, width=900, height=550)

# =========================================================
# ---------------- SYSTEM ALERTS --------------------------
# =========================================================

elif section == "System Alerts":
    if not require_role("System Alerts"): st.stop()
    st.markdown("<div class='page-title'>◈ SYSTEM ALERTS</div>", unsafe_allow_html=True)

    speed    = st.session_state.speed
    temp     = st.session_state.temperature
    battery  = st.session_state.battery
    pressure = st.session_state.pressure

    now = datetime.now().strftime("%H:%M:%S")
    if battery < 20:
        st.session_state.alerts.append({"Time": now, "Level": "CRITICAL", "Message": f"Battery at {battery}%"})
    if temp > 80:
        st.session_state.alerts.append({"Time": now, "Level": "WARNING",  "Message": f"Temperature at {temp}°C"})
    if pressure < 92000 or pressure > 108000:
        st.session_state.alerts.append({"Time": now, "Level": "WARNING",  "Message": f"Pressure out of range: {pressure} Pa"})

    if battery < 20:
        st.error("⚠ Battery Critical!")
    elif temp > 80:
        st.warning("⚠ High Temperature Warning")
    elif pressure < 92000 or pressure > 108000:
        st.warning("⚠ Pressure Anomaly Detected")
    else:
        st.success("✓ All systems operational")

    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Speed",       f"{speed} km/h")
    c2.metric("Temperature", f"{temp} °C")
    c3.metric("Battery",     f"{battery} %")
    c4.metric("Pressure",    f"{pressure} Pa")

    st.divider()
    st.subheader("Alert History")

    if st.session_state.alerts:
        alert_df = pd.DataFrame(st.session_state.alerts[-50:])
        st.dataframe(alert_df[::-1], use_container_width=True)
    else:
        st.info("No alerts recorded this session.")

    if st.button("Clear Alert History"):
        st.session_state.alerts = []
        st.rerun()

# =========================================================
# ---------------- MAINTENANCE LOGS -----------------------
# =========================================================

elif section == "Maintenance Logs":
    if not require_role("Maintenance Logs"): st.stop()
    st.markdown("<div class='page-title'>◈ MAINTENANCE LOGS</div>", unsafe_allow_html=True)

    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "maintenance_logs.csv")
    if os.path.exists(log_file):
        try:
            st.dataframe(pd.read_csv(log_file, quoting=1), use_container_width=True)
        except Exception as e:
            st.warning(f"Could not load log file: {e}")

    with st.form("log_form"):
        engineer  = st.text_input("Engineer Name")
        issue     = st.text_area("Issue")
        severity  = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        submitted = st.form_submit_button("Submit Log")
        if submitted:
            if not engineer.strip() or not issue.strip():
                st.error("Engineer name and issue cannot be blank.")
            else:
                entry = {
                    "Time":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Engineer": engineer.strip(),
                    "Issue":    issue.strip(),
                    "Severity": severity,
                }
                log_to_csv(entry, filename="maintenance_logs.csv")
                st.success("Log saved.")
                st.rerun()

# =========================================================
# ---------------- DID YOU KNOW ---------------------------
# =========================================================

elif section == "Did You Know":
    if not require_role("Did You Know"): st.stop()
    st.markdown("<div class='page-title'>◈ DID YOU KNOW</div>", unsafe_allow_html=True)

    if st.button("Generate Hyperloop Fact"):
        response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
        if response.status_code == 200:
            st.info(response.json()["text"])
        else:
            st.error("Failed to fetch fact.")

# =========================================================
# ---------------- MQTT LIVE DATA -------------------------
# =========================================================

elif section == "MQTT Live Data":
    if not require_role("MQTT Live Data"): st.stop()
    st.markdown("<div class='page-title'>◈ MQTT LIVE CONTROL PANEL</div>", unsafe_allow_html=True)

    st_autorefresh(interval=1000, key="mqtt_refresh")

    if "mqtt_logging" not in st.session_state:
        st.session_state.mqtt_logging = True

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.session_state.mqtt_logging:
            if st.button("⏸ Pause Logging"):
                st.session_state.mqtt_logging = False
        else:
            if st.button("▶ Resume Logging"):
                st.session_state.mqtt_logging = True
    with col2:
        if st.button("🗑 Clear Messages"):
            st.session_state.mqtt_data = []
            st.rerun()
    with col3:
        if st.button("🗑 Clear CSV Log"):
            log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "mqtt_logs.csv")
            if os.path.exists(log_file):
                os.remove(log_file)
                st.success("CSV cleared.")
            else:
                st.info("No CSV file found.")

    while not st.session_state.mqtt_queue.empty():
        data = st.session_state.mqtt_queue.get()
        if st.session_state.mqtt_logging:
            # Cap in-memory list at 100 messages
            if len(st.session_state.mqtt_data) >= 100:
                st.session_state.mqtt_data.pop(0)
            st.session_state.mqtt_data.append(data)
            try:
                parsed = json.loads(data["data"])
                parsed["received_at"] = data["timestamp"]
                log_to_csv(parsed, filename="mqtt_logs.csv")
            except Exception:
                pass

    message_count = len(st.session_state.mqtt_data)
    client = st.session_state.get("mqtt_client", None)

    connected = client is not None and (client.is_connected() or message_count > 0)
    status_color = "#00ff88" if connected else "#ff4466"
    status_text  = "BROKER CONNECTED — broker.hivemq.com:1883" if connected else "BROKER NOT CONNECTED"
    logging_badge = (
        "<span style='color:#00ff88;font-size:0.8rem;'> ● LOGGING</span>"
        if st.session_state.mqtt_logging else
        "<span style='color:#ff4466;font-size:0.8rem;'> ● PAUSED</span>"
    )
    st.markdown(
        f"<p style='color:{status_color};font-family:Share Tech Mono,monospace;'>"
        f"{'🟢' if connected else '🔴'} {status_text} {logging_badge}</p>",
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("📡 Total Messages", message_count)
    c2.metric("🕒 Last Update",
              st.session_state.mqtt_data[-1]["timestamp"] if message_count > 0 else "No Data")
    c3.metric("💾 Memory Cap", f"{message_count}/100")

    st.divider()

    if message_count > 0:
        latest = st.session_state.mqtt_data[-1]
        try:
            st.json(json.loads(latest["data"]))
        except Exception:
            st.code(latest)

        with st.expander("📋 Message History (last 10)"):
            for msg in reversed(st.session_state.mqtt_data[-10:]):
                try:
                    parsed = json.loads(msg["data"])
                    st.markdown(
                        f"<code style='color:#00aaff;'>{msg['timestamp']}</code> — "
                        f"<code style='color:#a8d8ff;'>{msg['data']}</code>",
                        unsafe_allow_html=True
                    )
                except Exception:
                    pass
    else:
        st.warning("Waiting for incoming MQTT telemetry data...")
