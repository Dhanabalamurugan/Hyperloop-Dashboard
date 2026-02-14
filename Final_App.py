import streamlit as st
import numpy as np
import pandas as pd
import random
import requests
import time
import os
from datetime import datetime
from collections import deque

st.set_page_config(page_title="Avishkar Hyperloop Dashboard", layout="wide")

# =========================================================
# ------------------- CSS -------------------------
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
# ---------------- CINEMATIC LANDING PAGE -----------------
# =========================================================

if "booted" not in st.session_state:
    st.session_state.booted = False

if not st.session_state["booted"]:

    st.markdown("""
    <h1 style='text-align:center;'>AVISHKAR HYPERLOOP CONTROL SYSTEM</h1>
    <h3 style='text-align:center;'>Year 2035 • Real-Time Pod Intelligence</h3>
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

section = st.sidebar.radio("Navigation", [
    "Overview",
    "Pod Tracker",
    "Performance Metrics",
    "Route Monitoring",
    "Pod Comparision",
    "Live Track Map",
    "System Alerts",
    "Maintenance Logs",
    "Did You Know"
])

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

def generate_pods():
    pods = []
    for i in range(1,6):
        pod = {
            "Pod ID": f"Pod-{i}",
            "Speed (km/h)": random.randint(500, 1000),
            "Battery (%)": random.randint(20,100),
            "Status": random.choice(["Operational","Maintenance","Docked"])
        }
        pods.append(pod)
    return pods

def log_to_csv(data):
    file = "hyperloop_logs.csv"
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

    st.session_state.pods = generate_pods()
    df = pd.DataFrame(st.session_state.pods)

    status_filter = st.selectbox("Filter by Status",
        ["All","Operational","Maintenance","Docked"])

    sort_by = st.selectbox("Sort by",
        ["Speed (km/h)", "Battery (%)"])

    if status_filter != "All":
        df = df[df["Status"] == status_filter]

    df = df.sort_values(by=sort_by, ascending=False)

    st.dataframe(df, use_container_width=True)

# =========================================================
# ---------------- PERFORMANCE METRICS --------------------
# =========================================================

elif section == "Performance Metrics":

    st.header("Performance Metrics")
    st.write("Real-time performance data and trends.")

    rt_mode = st.toggle("Enable RT Linux Mode (1ms Latency)", key="rt_mode")
    auto_mode = st.toggle("Auto-Run Simulation Mode", key="auto_mode")

    # --- Stop simulation if battery dead ---
    battery_dead = st.session_state.battery <= 0

    if battery_dead:
        st.error("Battery depleted. Simulation stopped.")

    # --- Auto Mode ---
    if auto_mode:
        st.session_state.speed = random.randint(0, 1200)
        st.session_state.acceleration = round(random.uniform(0.0, 10.0), 2)
        st.session_state.pressure = random.randint(90000, 110000)

    # --- Manual Controls ---
    st.slider("Speed", 0, 1200, key="speed")
    st.slider("Acceleration", 0.0, 10.0, key="acceleration")
    st.slider("Pressure", 90000, 110000, key="pressure")

    # --- Compute FIRST ---
    speed, acc, pressure, temp, battery = compute_values()

    # --- Log ---
    log_metrics()

    # --- Build chart ---
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

    # --- Reset Button ---
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

    # --- Auto Rerun ---
    if auto_mode and not battery_dead:
        time.sleep(0.05 if rt_mode else 0.5)
        st.rerun()

    st.markdown("""
    <style>
    button {
        cursor: pointer;
    }
    a {
        cursor: pointer;
    }
    .stselectbox, .stMultiSelect {
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

    # Logging
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

elif section == "Route Monitoring":

    st.header("Weather Monitoring")

    city = st.text_input("City", "Chengalpattu")
    API_KEY = "your_api_key_here"

    if st.button("Fetch Weather"):

        data = fetch_weather(city, API_KEY)

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

    pod1 = st.selectbox("Pod 1", df["Pod ID"])
    pod2 = st.selectbox("Pod 2", df["Pod ID"], index=1)

    st.dataframe(df[df["Pod ID"].isin([pod1,pod2])])

# =========================================================
# ---------------- LIVE TRACK MAP -------------------------
# =========================================================

elif section == "Live Track Map":

    st.header("Live Pod Position Tracking")

    pods = pd.DataFrame({
        "Pod": ["Pod 1", "Pod 2", "Pod 3", "Pod 4", "Pod 5", "Pod 6"],
        "Track Position": np.random.randint(0, 101, 6)
    })

    st.write("Track Length: 100 units")
    st.dataframe(pods, use_container_width=True)

    selected_pod = st.selectbox(
        "Select Pod to Track",
        pods["Pod"]
    )

    pod_position = pods.loc[
        pods["Pod"] == selected_pod,
        "Track Position"
    ].values[0]

    st.subheader(f"{selected_pod} Progress")

    st.progress(int(pod_position))

    st.write(f"Current Position: {pod_position} / 100 units")

    if pod_position >= 100:
        st.success(f"{selected_pod} has completed the track!")


# =========================================================
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
                "Time": datetime.datetime.now(),
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
        r = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
        if r.status_code == 200:
            st.info(r.json()["text"])
