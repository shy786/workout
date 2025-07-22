import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Workout Tracker", layout="centered")
st.title("🏋️ Workout Tracker")

# In-memory user storage (reset on refresh)
if "users" not in st.session_state:
    st.session_state.users = {}
    st.session_state.data = {}

# Login form
st.sidebar.header("Login")
username = st.sidebar.text_input("Username").strip().lower()
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if username in st.session_state.users:
        if st.session_state.users[username] != password:
            st.sidebar.error("Incorrect password.")
        else:
            st.session_state.active_user = username
            st.sidebar.success("Logged in")
    else:
        st.session_state.users[username] = password
        st.session_state.data[username] = pd.DataFrame(columns=["Exercise", "Date", "Reps", "Weight"])
        st.session_state.active_user = username
        st.sidebar.success("Account created")

# Main app after login
if "active_user" in st.session_state:
    user = st.session_state.active_user
    df = st.session_state.data.get(user, pd.DataFrame(columns=["Exercise", "Date", "Reps", "Weight"]))

    st.subheader("➕ Log Workout")
    with st.form("log_form"):
        exercise = st.text_input("Exercise Name").strip()
        date = st.date_input("Date", datetime.today())
        reps = st.number_input("Reps", min_value=1)
        is_weighted = st.checkbox("Is this a weighted exercise?")
        weight = st.number_input("Weight (if any)", min_value=0.0) if is_weighted else None
        submitted = st.form_submit_button("Add Entry")

        if submitted and exercise:
            new = pd.DataFrame([[exercise, date, reps, weight]], columns=["Exercise", "Date", "Reps", "Weight"])
            df = pd.concat([df, new], ignore_index=True)
            st.session_state.data[user] = df
            st.success("Workout logged!")

    st.subheader("📈 Progress Charts")
    if df.empty:
        st.info("No data yet.")
    else:
        for ex in df["Exercise"].unique():
            subset = df[df["Exercise"] == ex].sort_values("Date")
            fig, ax = plt.subplots(figsize=(8, 4))
            if subset["Weight"].notnull().any():
                subset["E1RM"] = subset.apply(lambda row: row["Weight"] * (1 + row["Reps"] / 30), axis=1)
                ax.plot(subset["Date"], subset["E1RM"], marker="o", color="crimson")
                ax.set_ylabel("Estimated 1RM")
            else:
                ax.plot(subset["Date"], subset["Reps"], marker="o", color="royalblue")
                ax.set_ylabel("Total Reps")
            ax.set_xlabel("Date")
            ax.set_title(ex)
            st.pyplot(fig)

