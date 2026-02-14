import streamlit as st
import pandas as pd
import random
import requests
import datetime
import time
from collections import deque
import os

st.set_page_config(page_title="Avishkar Hyperloop Dashboard", layout="wide")

# =========================================================
# -------------------- SESSION INIT -----------------------
# =========================================================

if "history" not in st.session_state:
    st.session_state.history = {
        "time": deque(maxlen=50),
        "speed": deque(maxlen=50),
        "temperature": deque(maxlen=50),
        "battery": deque(maxlen=50)
    }

if "speed" not in st.session_state:
    st.session_state.speed = 800
    st.session_state.acceleration = 3.0
    st.session_state.pressure = 101325

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
    "viewer": {"password": "viewer123", "role": "Viewer"},
    "controller": {"password": "control123", "role": "Controller"},
    "operator": {"password": "operate123", "role": "Operator"},
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
    "Pod Health Insights",
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

    temp = round(25 + 0.02*speed + 2*acc, 1)
    battery = max(round(100 - (0.03*speed + 5*acc),1), 0)

    return speed, acc, pressure, temp, battery


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

# =========================================================
# ---------------------- OVERVIEW -------------------------
# =========================================================

if section == "Overview":
    st.title("Avishkar Hyperloop Control Center")

    speed, acc, pressure, temp, battery = compute_values()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Speed", speed, delta=random.randint(-10,10))
    col2.metric("Temperature", temp, delta=random.randint(-3,3))
    col3.metric("Battery", battery, delta=random.randint(-5,5))
    col4.metric("Pressure", pressure)

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

    st.session_state.speed = st.slider("Speed",0,1200,st.session_state.speed)
    st.session_state.acceleration = st.slider("Acceleration",0.0,10.0,st.session_state.acceleration)
    st.session_state.pressure = st.slider("Pressure",90000,110000,st.session_state.pressure)

    speed, acc, pressure, temp, battery = compute_values()

    # Live chart history
    now = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.history["time"].append(now)
    st.session_state.history["speed"].append(speed)
    st.session_state.history["temperature"].append(temp)
    st.session_state.history["battery"].append(battery)

    chart_df = pd.DataFrame({
        "Time": st.session_state.history["time"],
        "Speed": st.session_state.history["speed"],
        "Temperature": st.session_state.history["temperature"],
        "Battery": st.session_state.history["battery"],
    })

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
    chart_df.set_index("Time")[metric_option]
)

    # Logging
    if st.button("Log Current Metrics"):
        log_data = {
            "Time": now,
            "Speed": speed,
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

    city = st.text_input("City", "Mumbai")
    API_KEY = "8802223f0fc8e6e31852d1bd5364e727"

    if st.button("Fetch Weather"):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        r = requests.get(url)

        if r.status_code == 200:
            data = r.json()
            temp = data["main"]["temp"]
            weather = data["weather"][0]["description"]

            st.metric("Temperature (°C)", temp)
            st.write("Condition:", weather)

            if "rain" in weather.lower():
                st.warning("Suggested Speed Limit: 700 km/h")
            else:
                st.success("Suggested Speed Limit: 900 km/h")
        else:
            st.error("Weather fetch failed")

# =========================================================
# ---------------- POD HEALTH INSIGHTS --------------------
# =========================================================

elif section == "Pod Health Insights":

    st.header("Compare Pods")

    df = pd.DataFrame(generate_pods())

    pod1 = st.selectbox("Pod 1", df["Pod ID"])
    pod2 = st.selectbox("Pod 2", df["Pod ID"], index=1)

    st.dataframe(df[df["Pod ID"].isin([pod1,pod2])])

# =========================================================
# ---------------- LIVE TRACK MAP -------------------------
# =========================================================

elif section == "Live Track Map":

    st.header("Live Pod Track Visualization")

    track_length = 100

    for pod in st.session_state.positions:
        st.session_state.positions[pod] += random.randint(1,5)
        if st.session_state.positions[pod] > track_length:
            st.session_state.positions[pod] = 0

    pos_df = pd.DataFrame({
        "Pod": list(st.session_state.positions.keys()),
        "Position": list(st.session_state.positions.values())
    })

    st.bar_chart(pos_df.set_index("Pod"))

    st.write("Track Length = 100 units")

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

    st.header("Fun Fact")

    if st.button("Generate Fact"):
        r = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
        if r.status_code == 200:
            st.info(r.json()["text"])
        else:
            st.error("Failed to fetch fact")
