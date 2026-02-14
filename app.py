import os
import streamlit as st 
import pandas as pd
import random 
import requests 
import time
import datetime
from collections import deque

st.markdown("""
<style>
html {
    scroll-behavior: smooth;
}

section {
    padding-top: 100px;
    padding-bottom: 100px;
}

.block-container {
    padding-top: 2rem;
}

.sidebar .sidebar-content {
    background-color: #0e1117;
}

.highlight {
    color: #00ffcc;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = {
        "time": deque(maxlen=50),
        "temperature": deque(maxlen=50),
        "speed": deque(maxlen=50),
        "acceleration": deque(maxlen=50),
        "pressure": deque(maxlen=50),
        "battery": deque(maxlen=50)
    }

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

st.set_page_config(
    page_title="Hyperloop System Dashboard",
    layout="wide"
)

st.sidebar.title("Navigation")
section = st.sidebar.radio(
    "Go to",
    ["Home","Overview", "Pod Status", "Performance Metrics", "System Alerts","Maintenance Logs"]
)

if "speed" not in st.session_state:
    st.session_state.speed = 820
    st.session_state.acceleration = 3.2
    st.session_state.pressure = 101325

speed = st.session_state.speed
acceleration = st.session_state.acceleration
pressure= st.session_state.pressure

# Simple thermal model (fake but logical)
base_temp = 25
temperature = base_temp + 0.02 * speed + 2 * acceleration
temperature = round(temperature, 1)

# Simple battery drain model (fake but logical)
battery = 100 - (0.03 * speed + 5 * acceleration)
battery = max(round(battery, 1), 0)

def get_status(value, min, max):
    if min <= value <= max:
        return "Normal"
    elif value < min or value > max:
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

def get_battery_status(battery):
    if battery > 50:
        return "Normal"
    elif battery > 20:
        return "Warning"
    else:
        return "Critical"
    battery_status = "Critical"

temp_status = get_status(temperature, 60, 80)
pressure_status = get_status(pressure, 95000, 105000)
acceleration_status = get_status(acceleration, 2, 5)
speed_status = get_status(speed, 600, 900)
battery_status = get_battery_status(battery)

if section== "Home":
    st.subheader("Avishkar – Pod Monitoring Interface")
    st.write("Welcome to the Hyperloop System Dashboard. Here you can monitor the performance and status of our Hyperloop pods in real-time.")
    st.write("This dashboard provides real-time data and insights into the performance of the Hyperloop pods.")
    st.write("Use the sidebar to navigate through different sections of the dashboard, including pod status, performance metrics, and system alerts.")

    API_KEY = "8802223f0fc8e6e31852d1bd5364e727"
    CITY = st.text_input("Enter city for weather data: ")

    @st.cache_data(ttl=60)
    def get_weather(city_name):
        if not city_name:
            return None, None, None

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data["weather"][0]["main"], data["wind"]["speed"], data["main"]["temp"]
            else:
                st.error(f"Weather API Error: {response.status_code}")
                return None, None, None
        except Exception as e:
            st.error(f"Connection Error: {e}")
            return None, None, None

    def suggest_safe_speed(weather, wind_speed):
        if weather in ["Thunderstorm", "Rain","Cloudy"]:
            return 500
        elif wind_speed > 11:
            return 800
        elif weather in ["Clear"]:
            return 1200
        else:
            return 1000

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

    if CITY:
        weather, wind_speed, temp = get_weather(CITY)
        if weather:
            safe_speed = suggest_safe_speed(weather, wind_speed)
            st.subheader("🌦 Route Optimization using Real time weather data")
            st.write(f"**Current Weather:** {weather}")
            st.write(f"**Wind Speed:** {wind_speed} m/s")
            st.write(f"**Temperature:** {temp} °C")
            st.success(f"Suggested Safe Pod Speed: **{safe_speed} km/h**")
        else:
            st.warning("Could not find weather data for that city. Please check the spelling.")
    else:
        st.info("Waiting for city input...")

    st.subheader("⚡ Energy Optimization Tip")
    st.info(get_energy_tip())

elif section == "Overview":
    st.header("Hyperloop System Overview")

    st.write(
        """
        This dashboard monitors key performance and safety parameters 
        of a Hyperloop pod in real time.
        
        The system models relationships between speed, acceleration, 
        temperature, battery health, and tube pressure to assess 
        operational safety.
        """
    )

    st.markdown("### Key Monitored Parameters")
    st.markdown(
        """
        - **Speed & Acceleration** – performance indicators  
        - **Temperature** – derived from operational load  
        - **Battery Level** – derived from power usage  
        - **Tube Pressure** – safety-critical environmental parameter  
        """
    )
    st.markdown("### Overall System Health")

    if (temp_status == "Normal"and battery_status == "Normal"and pressure_status == "Normal"):
        st.success("System operating within safe limits.")
    else:
        st.warning("System requires attention. Check Pod Status.")

elif section == "Pod Status":
    st.write("Live status of the pod subsystems.")
    pods = []
    for i in range(1, 6):
        pod = {
            "Pod ID": f"Pod-{i}",
            "Temperature (°C)": round(temperature + random.uniform(-5, 5), 1),
            "Battery (%)": max(round(battery + random.uniform(-10, 10), 1), 0),
            "Pressure (Pa)": pressure + random.randint(-5000, 5000),
            "Acceleration (m/s²)": round(acceleration + random.uniform(-1, 1), 2),
            "Speed (km/h)": speed + random.randint(-50, 50)
        }
        pods.append(pod)
    df = pd.DataFrame(pods)
    st.subheader("All Pods Overview")
    st.dataframe(df,hide_index=True,use_container_width=True)
    statuses = [
        temp_status,
        battery_status,
        pressure_status,
        acceleration_status,
        speed_status
    ]

    if "Critical" in statuses:
        overall_status = "Critical"
    elif "Warning" in statuses:
        overall_status = "Warning"
    else:
        overall_status = "Normal"

    if overall_status == "Normal":
        st.success("🟢 Pod Status: NORMAL")

    elif overall_status == "Warning":
        st.warning("🟡 Pod Status: WARNING – Check system parameters")

    else:
        st.error("🔴 Pod Status: CRITICAL – Immediate attention required")

    status_data = pd.DataFrame({
        "Parameter": ["Temperature", "Battery", "Pressure", "Acceleration", "Speed"],
        "Status": statuses
    })

    st.subheader("Parameter Status Breakdown")
    st.table(status_data)

elif section == "Performance Metrics":
    st.header("Performance Metrics")
    st.write("Real-time performance data and trends.")
    rt_mode = st.toggle("Enable RT Linux Mode (1ms Latency)")
    auto_mode = st.toggle("Auto-Run Simulation Mode")

    if rt_mode:
        latency = round(random.uniform(0.8, 1.5), 2)
    else:
        latency = round(random.uniform(5, 20), 2)


    if auto_mode:
        speed = random.randint(0, 1200)
        acceleration = round(random.uniform(0.0, 10.0), 2)
        pressure = random.randint(800000, 1200000)

    st.session_state.speed = st.slider("Speed (km/h)", 0, 1200, st.session_state.speed)
    st.session_state.acceleration = st.slider("Acceleration (m/s²)", 0.0, 10.0, st.session_state.acceleration)
    st.session_state.pressure = st.slider("Pressure (Pa)", 75000, 500000, st.session_state.pressure)

    speed = st.session_state.speed
    acceleration = st.session_state.acceleration
    pressure = st.session_state.pressure

    temperature = round(25 + 0.02 * speed + 2 * acceleration, 1)
    battery = max(round(100 - (0.03 * speed + 5 * acceleration), 1), 0)

    col1, col2, col3,col4,col5,col6 = st.columns(6) #KPIs for the Hyperloop pod performance

    if "display_speed" not in st.session_state:
        st.session_state.display_speed = 0
    placeholder = col1.empty()
    current = st.session_state.display_speed
    target = speed
    step = 5 if target > current else -5
    for val in range(current, target, step): #Animate speed change
        placeholder.metric("Speed (km/h)", val)
        time.sleep(0.005)

    placeholder.metric("Speed (km/h)", target,"-20")
    st.session_state.display_speed = target

   # col1.metric("Speed (km/h)", speed, "-20")
    col2.metric("Acceleration (m/s²)", acceleration, "-0.1")
    col3.metric("Pod Temperature (°C)", temperature, "+1")
    col4.metric("Pressure (Pa)", pressure, "+100")
    col5.metric("Battery (%)", battery, "-5")
    col6.metric("System Latency (ms)", latency, "-0.5 ms" if rt_mode else "+2 ms")

    if rt_mode:
        cpu_load = random.randint(60, 90)
    else:
        cpu_load = random.randint(20, 50)

    st.metric("CPU Load (%)", cpu_load)

    now = datetime.datetime.now().strftime("%H:%M:%S")

    st.session_state.history["time"].append(now)
    st.session_state.history["speed"].append(speed)
    st.session_state.history["temperature"].append(temperature)
    st.session_state.history["battery"].append(battery)
    st.session_state.history["pressure"].append(pressure)
    st.session_state.history["acceleration"].append(acceleration)
    history_df = pd.DataFrame(st.session_state.history)
    df = pd.DataFrame({
    "time": list(st.session_state.history["time"]),
    "Temperature": list(st.session_state.history["temperature"]),
    "Speed": list(st.session_state.history["speed"]),
    "Acceleration": list(st.session_state.history["acceleration"]),
    "Pressure": list(st.session_state.history["pressure"]),
    "Battery": list(st.session_state.history["battery"]),
})
    #df["time"] = df["time"] - df["time"].iloc[0]

    if st.button("Reset Simulation"):
        st.session_state.history = {
            "time": deque(maxlen=50),
            "temperature": deque(maxlen=50),
            "speed": deque(maxlen=50),
            "acceleration": deque(maxlen=50),
            "pressure": deque(maxlen=50),
            "battery": deque(maxlen=50)
        }
        st.session_state.display_speed = 0
        st.success("Simulation Reset")

    st.subheader("Performance Trends")
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
    metric_option = st.selectbox(
    "Select parameter to view trend",
    ["Temperature", "Speed", "Acceleration", "Pressure", "Battery"]
)
    st.line_chart(
    df.set_index("time")[metric_option]
)

    st.subheader("System Status")

    show_status("Temperature", temp_status)
    show_status("Battery", battery_status)
    show_status("Pressure", pressure_status)
    show_status("Acceleration", acceleration_status)
    show_status("Speed", speed_status)

    col1.metric("Speed Status", speed_status)
    col2.metric("Acceleration Status", acceleration_status)
    col3.metric("Temperature Status", temp_status)
    col4.metric("Pressure Status", pressure_status)
    col5.metric("Battery Status", battery_status)
    
    st.caption(f"Last updated: {time.strftime('%H:%M:%S')}")
    
    if auto_mode:
        if rt_mode:
            time.sleep(0.05)
        else:
            time.sleep(0.5)
        st.rerun()

elif section == "System Alerts":
    st.header("System Alerts")
    alerts = []

    if temp_status == "Critical":
        alerts.append("🔥 Temperature Critical – Immediate cooling required!")

    if battery_status == "Critical":
        alerts.append("🔋 Battery Critically Low – Emergency recharge needed!")

    if pressure_status == "Critical":
        alerts.append("⚠ Pressure Out of Safe Limits!")

    if speed_status == "Critical":
        alerts.append("🚀 Overspeed Condition Detected!")

    if acceleration_status == "Critical":
        alerts.append("⚡ High Acceleration Risk!")

    if len(alerts) == 0:
        st.success("All systems operating within safe limits.")
    else:
        for alert in alerts:
            st.error(alert)

elif section == "Maintenance Logs":
    st.header("Maintenance Logs")
    st.write("Record of inspections, repairs, and system servicing events.")
    with st.form("maintenance_form"):
        engineer = st.text_input("Engineer Name")
        issue = st.text_area("Issue Description")
        severity = st.selectbox("Severity Level", ["Low", "Medium", "High", "Critical"])
        submitted = st.form_submit_button("Add Log")

        if submitted:
            if "logs" not in st.session_state:
                st.session_state.logs = []

            log_entry = {
                "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Engineer": engineer,
                "Issue": issue,
                "Severity": severity
            }

            st.session_state.logs.append(log_entry)
            st.success("Log added successfully.")

    if "logs" in st.session_state and len(st.session_state.logs) > 0:
        logs_df = pd.DataFrame(st.session_state.logs)
        st.subheader("Maintenance History")
        st.dataframe(logs_df, use_container_width=True)
    else:
        st.info("No maintenance logs available.")
