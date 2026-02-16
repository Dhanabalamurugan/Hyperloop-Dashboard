import streamlit as st

USERS = {
    "ch25b033": {"password": "bala", "role": "Viewer"},
    "controller": {"password": "controller123", "role": "Controller"}
}

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

