import os
import streamlit as st 
import pandas as pd
import random 
import requests 
import time
import datetime
from collections import deque

st.set_page_config(
    page_title="Hyperloop System Dashboard",
    layout="wide"
)

# ---------------------- Styling ----------------------

st.markdown("""
<style>
html { scroll-behavior: smooth; }
.block-container { padding-top: 2rem; }
.sidebar .sidebar-content { background-color: #0e1117; }
.highlight { color: #00ffcc; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ---------------------- Session Init ----------------------

if "history" not in st.session_state:
    st.session_state.history = {
        "time": deque(maxlen=50),
        "temperature": deque(maxlen=50),
        "speed": deque(maxlen=50),
        "acceleration": deque(maxlen=50),
        "pressure": deque(maxlen=50),
        "battery": deque(maxlen=50)
    }

if "speed" not in st.session_state:
    st.session_state.speed = 820
    st.session_state.acceleration = 3.2
    st.session_state.pressure = 101325

# ---------------------- Status Logic ----------------------

def get_status(value, min_val, max_val):
    if min_val <= value <= max_val:
        return "Normal"
    else:
        return "Warning"

def get_battery_status(battery):
    if battery > 50:
        return "Normal"
    elif battery > 20:
        return "Warning"
    else:
        return "Critical"

def show_status(label, status):
    if status == "Normal":
        st.success(f"{label}: {status}")
    elif status == "Warning":
        st.warning(f"{label}: {status}")
    else:
        st.error(f"{label}: {status}")

# ---------------------- Login ----------------------

USERS = {
    "viewer": {"password": "viewer123", "role": "Viewer"},
    "controller": {"password": "control123", "role": "Controller"},
    "operator": {"password": "operate123", "role": "Operator"},
}

def login():
    st.sidebar.title("🔐 Secure Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = USERS[username]["role"]
            st.success(f"Welcome {username} ({st.session_state.role})")
        else:
            st.error("Invalid credentials")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

# ---------------------- Navigation ----------------------

st.sidebar.title("Navigation")
section = st.sidebar.radio(
    "Go to",
    ["Home","Overview", "Pod Status", "Performance Metrics", "System Alerts","Maintenance Logs"]
)

# ---------------------- Derived Values ----------------------

def compute_values():
    speed = st.session_state.speed
    acceleration = st.session_state.acceleration
    pressure = st.session_state.pressure

    temperature = round(25 + 0.02 * speed + 2 * acceleration, 1)
    battery = max(round(100 - (0.03 * speed + 5 * acceleration), 1), 0)

    temp_status = get_status(temperature, 60, 80)
    pressure_status = get_status(pressure, 90000, 110000)
    acceleration_status = get_status(acceleration, 2, 5)
    speed_status = get_status(speed, 600, 900)
    battery_status = get_battery_status(battery)

    return speed, acceleration, pressure, temperature, battery, \
           temp_status, pressure_status, acceleration_status, speed_status, battery_status

# ---------------------- HOME ----------------------

if section == "Home":
    st.subheader("Avishkar – Pod Monitoring Interface")
    st.write("Welcome to the Hyperloop System Dashboard.")

# ---------------------- OVERVIEW ----------------------

elif section == "Overview":

    speed, acceleration, pressure, temperature, battery, \
    temp_status, pressure_status, acceleration_status, speed_status, battery_status = compute_values()

    st.header("Hyperloop System Overview")

    if (temp_status == "Normal" and 
        battery_status == "Normal" and 
        pressure_status == "Normal"):
        st.success("System operating within safe limits.")
    else:
        st.warning("System requires attention.")

# ---------------------- POD STATUS ----------------------

elif section == "Pod Status":

    speed, acceleration, pressure, temperature, battery, \
    temp_status, pressure_status, acceleration_status, speed_status, battery_status = compute_values()

    pods = []
    for i in range(1, 6):
        pod = {
            "Pod ID": f"Pod-{i}",
            "Temperature (°C)": round(temperature + random.uniform(-5, 5), 1),
            "Battery (%)": max(round(battery + random.uniform(-10, 10), 1), 0),
            "Pressure (Pa)": pressure + random.randint(-2000, 2000),
            "Acceleration (m/s²)": round(acceleration + random.uniform(-1, 1), 2),
            "Speed (km/h)": speed + random.randint(-50, 50)
        }
        pods.append(pod)

    st.dataframe(pd.DataFrame(pods), hide_index=True, use_container_width=True)

# ---------------------- PERFORMANCE ----------------------

elif section == "Performance Metrics":

    st.header("Performance Metrics")

    rt_mode = st.toggle("Enable RT Linux Mode (1ms Latency)")
    auto_mode = st.toggle("Auto-Run Simulation Mode")

    if auto_mode:
        st.session_state.speed = random.randint(0, 1200)
        st.session_state.acceleration = round(random.uniform(0.0, 10.0), 2)
        st.session_state.pressure = random.randint(90000, 110000)

    st.session_state.speed = st.slider("Speed (km/h)", 0, 1200, st.session_state.speed)
    st.session_state.acceleration = st.slider("Acceleration (m/s²)", 0.0, 10.0, st.session_state.acceleration)
    st.session_state.pressure = st.slider("Pressure (Pa)", 90000, 110000, st.session_state.pressure)

    speed, acceleration, pressure, temperature, battery, \
    temp_status, pressure_status, acceleration_status, speed_status, battery_status = compute_values()

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Speed", speed)
    col2.metric("Acceleration", acceleration)
    col3.metric("Temperature", temperature)
    col4.metric("Pressure", pressure)
    col5.metric("Battery", battery)

    show_status("Temperature", temp_status)
    show_status("Battery", battery_status)
    show_status("Pressure", pressure_status)
    show_status("Acceleration", acceleration_status)
    show_status("Speed", speed_status)

# ---------------------- ALERTS ----------------------

elif section == "System Alerts":

    speed, acceleration, pressure, temperature, battery, \
    temp_status, pressure_status, acceleration_status, speed_status, battery_status = compute_values()

    alerts = []

    if battery_status == "Critical":
        alerts.append("Battery Critical")

    if len(alerts) == 0:
        st.success("All systems normal.")
    else:
        for a in alerts:
            st.error(a)

# ---------------------- LOGS ----------------------

elif section == "Maintenance Logs":

    with st.form("maintenance_form"):
        engineer = st.text_input("Engineer Name")
        issue = st.text_area("Issue Description")
        severity = st.selectbox("Severity Level", ["Low", "Medium", "High", "Critical"])
        submitted = st.form_submit_button("Add Log")

        if submitted:
            if "logs" not in st.session_state:
                st.session_state.logs = []
            st.session_state.logs.append({
                "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Engineer": engineer,
                "Issue": issue,
                "Severity": severity
            })
            st.success("Log added.")

    if "logs" in st.session_state:
        st.dataframe(pd.DataFrame(st.session_state.logs), use_container_width=True)
