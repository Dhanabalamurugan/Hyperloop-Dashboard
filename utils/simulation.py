import streamlit as st

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