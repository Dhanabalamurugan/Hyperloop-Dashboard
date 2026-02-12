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
