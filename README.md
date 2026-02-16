# 🚄 Avishkar Hyperloop -- GUI Subsystem

## Real-Time Control & Monitoring Dashboard

### IIT Madras \| Avishkar Hyperloop Team

**Solo Project -- GUI Subsystem Application**

------------------------------------------------------------------------

## 🔥 Project Overview

This project is a high-performance real-time monitoring dashboard built
for the Avishkar Hyperloop GUI Subsystem.

It simulates a futuristic Hyperloop Control Center (Year 2035) capable
of:

-   Real-time telemetry visualization\
-   Pod tracking and geolocation mapping\
-   Weather-aware operational decisions\
-   Maintenance logging\
-   MQTT live telemetry streaming\
-   Role-based authentication\
-   Performance analytics

This is not just a UI.\
It is a systems-oriented control interface designed with engineering
trade-offs in mind --- prioritizing:

-   ⚡ Speed\
-   🧠 Efficient data structures\
-   🔄 Real-time responsiveness\
-   🛠 Modular architecture\
-   🎯 Zero-lag interaction philosophy

------------------------------------------------------------------------

# 🧠 Design Philosophy

> Speed first. No lag. No unnecessary computation. No bloated state.

Core priorities:

-   Real-time responsiveness\
-   Efficient memory usage\
-   Clean modular design\
-   Hardware-communication readiness (MQTT)\
-   Asynchronous-safe data handling\
-   Professional UI aesthetics

------------------------------------------------------------------------

# 🏗 Architecture Overview

## 1️⃣ Streamlit Frontend

-   Wide layout\
-   Custom CSS-styled futuristic theme\
-   Sidebar-based modular navigation\
-   Session-based state management

## 2️⃣ Data Layer

-   `deque` for bounded telemetry history\
-   Queue-based MQTT ingestion\
-   Cached API calls\
-   Controlled re-rendering

## 3️⃣ Real-Time Engine

-   Auto simulation mode\
-   RT-Linux-inspired 1ms latency simulation\
-   Controlled reruns\
-   Battery + thermal modeling

## 4️⃣ Integration Layer

-   MQTT Broker (localhost)\
-   OpenWeather API\
-   CSV Logging\
-   Folium Geospatial Mapping

------------------------------------------------------------------------

# ⚡ Performance Engineering Decisions

## 🚀 Efficient Data Structures

Telemetry history uses:

-   `collections.deque(maxlen=50)`\
-   O(1) append operations\
-   Automatic memory bounding\
-   Prevents uncontrolled memory growth

Using deque instead of list avoids O(n) shifting operations and ensures
stable real-time performance.

------------------------------------------------------------------------

## 🔄 Smart State Management

`st.session_state` ensures:

-   No unnecessary re-initialization\
-   Stable simulation continuity\
-   Controlled UI refresh behavior\
-   Persistent MQTT client and logs

------------------------------------------------------------------------

## 📡 MQTT Integration

-   `paho-mqtt` client\
-   Background threaded loop\
-   Thread-safe `queue.Queue()` ingestion

This architecture is scalable to real hardware telemetry systems.

------------------------------------------------------------------------

## 🌦 Cached API Calls

-   `@st.cache_data(ttl=300)` for weather\
-   Prevents rate-limiting\
-   Reduces network overhead\
-   Improves responsiveness

------------------------------------------------------------------------

## 🗺 Geospatial Visualization

-   Folium-based dark themed map\
-   Dynamic color-coded markers\
-   Live coordinate updates\
-   Battery-aware simulation

------------------------------------------------------------------------

# 📊 Feature Modules

## Overview

System introduction and navigation.

## Pod Tracker

-   Dataframe filtering\
-   Operational status tracking

## Performance Metrics

-   Speed\
-   Acceleration\
-   Temperature\
-   Battery\
-   Pressure\
-   Real-time trend graphs\
-   CSV logging\
-   Reset functionality

## Weather Monitoring

-   Live OpenWeather API integration\
-   Dynamic speed recommendations

## Pod Comparison

-   Side-by-side diagnostic comparison

## Live Track Map

-   City-based pod initialization\
-   Real-time movement simulation

## System Alerts

-   Battery critical detection\
-   Temperature threshold alerts

## Maintenance Logs

-   Engineer issue logging\
-   Severity tagging\
-   Structured tabular view

## MQTT Live Data

-   Broker connection monitoring\
-   Auto-refresh telemetry panel\
-   Live JSON parsing

------------------------------------------------------------------------

# 📂 Technologies Used

-   Python\
-   Streamlit\
-   Pandas\
-   NumPy\
-   Folium\
-   Paho-MQTT\
-   dotenv\
-   Queue\
-   Deque\
-   OpenWeather API

------------------------------------------------------------------------

# 🛠 Setup Instructions

``` bash
pip install streamlit pandas numpy requests folium streamlit-folium paho-mqtt python-dotenv streamlit-autorefresh
```

Create `.env`:

    api_key=YOUR_OPENWEATHER_API_KEY
    USERS_JSON={...}

Run:

``` bash
streamlit run app.py
```

(Optional) Run local MQTT broker on localhost:1883

------------------------------------------------------------------------

# 🚀 Future Improvements

-   Database-backed logging\
-   Hashed authentication\
-   Async MQTT architecture\
-   Predictive failure analytics\
-   Deployment containerization

------------------------------------------------------------------------

# 👤 Author

Avishkar Hyperloop -- GUI Subsystem Application\
IIT Madras

This project demonstrates:

-   Systems-level thinking\
-   Performance-aware architecture\
-   Real-time dashboard engineering\
-   Hardware communication readiness\
-   Clean modular Python design

------------------------------------------------------------------------

Generated on: 2026-02-16 17:02:16
