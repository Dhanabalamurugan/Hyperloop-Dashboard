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
