import streamlit as st
import pandas as pd
import os
from datetime import datetime

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