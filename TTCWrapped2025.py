import streamlit as st
import pandas as pd


# --- App Title ---
st.title("Tucson Track Club Wrapped 🎉")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your Garmin CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # --- Basic Stats ---
    df["Distance"] = pd.to_numeric(df["Distance"], errors="coerce")
    total_distance = df["Distance"].sum()
    longest_run = df.loc[df["Distance"].idxmax()]

    st.subheader("Your Wrapped Summary")
    st.write(f"**Total Distance:** {total_distance:.2f} km")
    st.write(f"**Longest Activity:** {longest_run['Title']} ({longest_run['Distance']} km)")
    st.write("**Activity Breakdown:**")
    st.bar_chart(df["Activity Type"].value_counts())

    # --- Leaderboard (mocked) ---
    if "leaderboard" not in st.session_state:
        st.session_state["leaderboard"] = []

    st.session_state["leaderboard"].append({
        "user": st.text_input("Enter a nickname:", "Anonymous"),
        "distance": total_distance
    })

    leaderboard_df = pd.DataFrame(st.session_state["leaderboard"])
    st.subheader("Community Leaderboard")
    st.dataframe(leaderboard_df.sort_values("distance", ascending=False))
