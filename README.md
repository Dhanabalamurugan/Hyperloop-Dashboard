# 🚄 Avishkar Hyperloop -- GUI Subsystem

## Real-Time Control & Monitoring Dashboard

### IIT Madras \| Avishkar Hyperloop Team

**GUI Subsystem Control Interface**

------------------------------------------------------------------------

## Project Overview

This project is a high-performance real-time monitoring dashboard built
for the Avishkar Hyperloop GUI Subsystem.

It simulates a futuristic Hyperloop Control Center (Year 2035) capable
of:

-   Real-time telemetry visualization
-   Pod tracking and geolocation mapping
-   Weather-aware operational decisions
-   Maintenance logging
-   MQTT live telemetry streaming
-   Performance analytics

It is a systems-oriented control interface designed with engineering
trade-offs in mind prioritizing:

-    Speed
-    Efficient data structures
-    Real-time responsiveness
-    Modular architecture

------------------------------------------------------------------------

Core priorities:

-   Real-time responsiveness
-   Efficient memory usage
-   Clean modular design
-   Hardware-communication readiness (MQTT)
-   Asynchronous-safe data handling
-   Professional UI aesthetics

------------------------------------------------------------------------

# Architecture Overview

## Streamlit Frontend

-   Wide layout
-   Custom CSS-styled futuristic theme
-   Sidebar-based modular navigation
-   Session-based state management

## Data Layer

-   `deque` for bounded telemetry history
-   Queue-based MQTT ingestion
-   Cached API calls
-   Controlled re-rendering

## Real-Time Engine

-   Auto simulation mode
-   RT-Linux-inspired 1ms latency simulation
-   Controlled reruns
-   Battery + thermal modeling

## Integration Layer

-   MQTT Broker (localhost)
-   OpenWeather API
-   Useless Facts REST API
-   CSV Logging
-   Folium Geospatial Mapping

------------------------------------------------------------------------

# Performance Engineering 

## Efficient Data Structures

Telemetry history uses:

-   `collections.deque(maxlen=50)`
-   O(1) append operations
-   Automatic memory bounding
-   Prevents uncontrolled memory growth

Using deque instead of list avoids O(n) shifting operations and ensures
stable real-time performance.

------------------------------------------------------------------------

## State Management

`st.session_state` ensures:

-   No unnecessary re-initialization
-   Stable simulation continuity
-   Controlled UI refresh behavior
-   Persistent MQTT client and logs

------------------------------------------------------------------------

## MQTT Integration

-   `paho-mqtt` client
-   Background threaded loop
-   Thread-safe `queue.Queue()` ingestion

This architecture is scalable to real hardware telemetry systems.

------------------------------------------------------------------------

## Cached API Calls

-   `@st.cache_data(ttl=300)` for weather
-   Prevents rate-limiting
-   Reduces network overhead
-   Improves responsiveness

------------------------------------------------------------------------

## Geospatial Visualization

-   Folium-based dark themed map
-   Dynamic color-coded markers
-   Live coordinate updates
-   Battery-aware simulation

------------------------------------------------------------------------

# Feature Modules

## Overview

System introduction and navigation.

## Pod Tracker

-   Dataframe filtering
-   Operational status tracking

## Performance Metrics

-   Speed
-   Acceleration
-   Temperature
-   Battery
-   Pressure
-   Real-time trend graphs
-   CSV logging
-   Reset functionality

## Weather Monitoring

-   Live OpenWeather API integration
-   Dynamic speed recommendations

## Pod Comparison

-   Side-by-side diagnostic comparison

## Live Track Map

-   City-based pod initialization
-   Real-time movement simulation

## System Alerts

-   Battery critical detection\
-   Temperature threshold alerts

## Maintenance Logs

-   Engineer issue logging
-   Severity tagging
-   Structured tabular view

## MQTT Live Data

-   Broker connection monitoring\
-   Auto-refresh telemetry panel\
-   Live JSON parsing

------------------------------------------------------------------------

# Setup Instructions

``` bash
pip install streamlit pandas numpy requests folium streamlit-folium paho-mqtt python-dotenv streamlit-autorefresh
```

Create `.env`:

    api_key=YOUR_OPENWEATHER_API_KEY

Run:

``` bash
streamlit run app.py
```

------------------------------------------------------------------------

# Future Improvements

-   Database-backed logging
-   Hashed authentication
-   Async MQTT architecture
-   Predictive failure analytics
-   Deployment containerization

------------------------------------------------------------------------

# 👤 Author

Dhanabala Murugan M
CH25B033

This project demonstrates:

-   Systems-level thinking
-   Performance-aware architecture
-   Real-time dashboard engineering
-   Hardware communication readiness
-   Clean modular Python design

------------------------------------------------------------------------
## Authentication Note

For demonstration purposes and ease of testing the source code , user credentials are currently defined directly within the application code.
In a production deployment, credentials would be securely stored using environment variables and hashed authentication mechanisms.
