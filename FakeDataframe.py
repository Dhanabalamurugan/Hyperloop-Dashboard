import pandas as pd
import streamlit as st


pods = [
    {
        "name": "Avishkar-Alpha",
        "speed": 820,
        "battery": 78,
        "temperature": 62,
        "status": "Operational"
    },
    {
        "name": "Avishkar-Beta",
        "speed": 650,
        "battery": 45,
        "temperature": 70,
        "status": "Maintenance"
    },
    {
        "name": "Avishkar-Gamma",
        "speed": 900,
        "battery": 88,
        "temperature": 59,
        "status": "Operational"
    }
]

df = pd.DataFrame(pods)

st.subheader("All Pods Overview")
st.dataframe(df)

