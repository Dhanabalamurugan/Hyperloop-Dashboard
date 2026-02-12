st.write("Live status of the pod subsystems.")
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
    }]
    df = pd.DataFrame(pods)
    st.subheader("All Pods Overview")
    st.dataframe(df)

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