# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 21:04:38 2025

@author: jeshu
"""
import random
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Garmin Wrapped", layout="wide")

st.title("Garmin Wrapped 🎉")
st.write("Upload your Garmin activity CSV to see your 2025 stats and join the leaderboard!")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload Garmin CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # --- Normalize Activity Types ---
    def normalize_activity(activity):
        activity = str(activity)
        if "Run" in activity:
            return "Running"
        elif "Cycl" in activity:
            return "Cycling"
        elif "Swim" in activity:
            return "Swimming"
        else:
            return "Other"

    df["Activity Category"] = df["Activity Type"].apply(normalize_activity)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    active_days = df["Date"].dt.date.nunique()

    # Compute longest streak of consecutive days
    dates = sorted(df["Date"].dt.date.dropna().unique())
    longest_streak = 0
    current_streak = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days == 1:
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
        else:
            current_streak = 1
            longest_streak = max(longest_streak, current_streak)

    # --- Convert Track Running distances (meters → miles) ---
    df["Distance"] = pd.to_numeric(df["Distance"], errors="coerce")

    # Track Running rows are in meters → convert to miles
    track_mask = df["Activity Type"].str.contains("Track Running", na=False)
    df.loc[track_mask, "Distance"] = df.loc[track_mask, "Distance"] / 1609.34  # meters → miles
    swim_masc = df["Activity Type"].str.contains("Swim", na=False)
    df.loc[swim_masc, "Distance"] = df.loc[swim_masc, "Distance"] / 1760




    # --- Counts ---
    focus_categories = ["Running", "Cycling", "Swimming", "Other"]
    counts = df["Activity Category"].value_counts().reindex(focus_categories, fill_value=0)

    # --- Distances ---
    df["Distance"] = pd.to_numeric(df["Distance"], errors="coerce")
    distance_sums = df.groupby("Activity Category")["Distance"].sum().reindex(focus_categories, fill_value=0)

    st.subheader("Yearly Summary")

    col_dist, col_time, col_days = st.columns(3)

   # --- Helper functions ---
    def boxed_dual_metric(col, title, val1, subtitle1, val2, subtitle2, emoji, color):
       col.markdown(
        f"""
        <div style="border:2px solid #ddd; border-radius:10px; padding:15px; background-color:{color};">
            <h3 style="margin:0; color:black; text-align:center;">{emoji} {title}</h3>
            <div style="display:flex; justify-content:space-around; margin-top:10px;">
                <div style="text-align:center;">
                    <p style="font-size:22px; margin:0; color:black;"><b>{val1}</b></p>
                    <p style="color:black; margin:0;">{subtitle1}</p>
                </div>
                <div style="text-align:center;">
                    <p style="font-size:22px; margin:0; color:black;"><b>{val2}</b></p>
                    <p style="color:black; margin:0;">{subtitle2}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    def boxed_metric(col, title, value, subtitle, emoji, color):
        col.markdown(
        f"""
        <div style="border:2px solid #ddd; border-radius:10px; padding:15px; text-align:center; background-color:{color};">
            <h3 style="margin:0; color:black;">{emoji} {title}</h3>
            <p style="font-size:24px; margin:5px 0; color:black;"><b>{value}</b></p>
            <p style="color:black; margin:0;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
   
    def parse_duration_to_seconds(t):
        try:
            h, m, s = map(int, str(t).split(":"))
            return h*3600 + m*60 + s
        except:
            return 0
    
    # --- Total Distance ---
    total_distance = df["Distance"].sum()
    boxed_dual_metric(
    col_days,
    "Activity Days",
    active_days, "Total Days",
    longest_streak, "Longest Streak",
    "📅", "#f1c40f"  # yellow background
)

    # --- Total Time ---
    # Assuming Garmin CSV has a "Duration" column in seconds
    df["DurationSeconds"] = df["Time"].apply(parse_duration_to_seconds)
    total_seconds = df["DurationSeconds"].sum()
    total_days = total_seconds / (24*3600)
    #print(f"Total time: {total_days:.2f} days")

    # --- Total Distance ---
    total_distance = df["Distance"].sum()
    boxed_metric(col_dist, "Total Distance", f"{total_distance:.1f} mi", "Yearly total", "📏", "#9b59b6")  # purple

    # --- Total Time (hh:mm:ss → days) ---
    df["DurationSeconds"] = df["Time"].apply(parse_duration_to_seconds)
    total_seconds = df["DurationSeconds"].sum()
    total_days = total_seconds / (24*3600)
    boxed_metric(col_time, "Total Time", f"{total_days:.1f} days", "Yearly total", "⏱️", "#e74c3c")  # red



    # --- Charts ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Activity Distribution (Counts)")
        fig_counts = px.pie(values=counts.values, names=counts.index,
                            color=counts.index,
                            color_discrete_map={"Running":"green","Cycling":"orange","Swimming":"blue","Other":"gray"})
        st.plotly_chart(fig_counts, use_container_width=True)

    with col2:
        st.subheader("Total Distance by Activity Type")
        fig_distances = px.bar(x=distance_sums.index, y=distance_sums.values,
                               labels={"x":"Activity Type","y":"Total Distance (mi)"},
                               color=distance_sums.index,
                               color_discrete_map={"Running":"green","Cycling":"orange","Swimming":"blue","Other":"gray"})
        st.plotly_chart(fig_distances, use_container_width=True)

    # --- Longest Activities with Boxes ---
    st.subheader("Your Longest Activities")
    col_run, col_swim, col_bike = st.columns(3)

    def boxed_metric(col, title, value, subtitle, emoji, color):
        col.markdown(
        f"""
        <div style="border:2px solid #ddd; border-radius:10px; padding:15px; text-align:center; background-color:{color};">
            <h3 style="margin:0; color:white;">{emoji} {title}</h3>
            <p style="font-size:24px; margin:5px 0; color:white;"><b>{value}</b></p>
            <p style="color:white; margin:0;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Longest Run
    longest_run = df[df["Activity Category"]=="Running"].sort_values("Distance", ascending=False).head(1)
    if not longest_run.empty:
        distance_str = f"{longest_run['Distance'].values[0]:.2f} miles"
        title_str = longest_run['Title'].values[0]
    else:
        distance_str = "N/A"
        title_str = "No running logged"
    boxed_metric(col_run, "Longest Run", distance_str, title_str, "🏃", "#2ecc71")  # green
            
    # Longest Swim
    longest_swim = df[df["Activity Category"]=="Swimming"].sort_values("Distance", ascending=False).head(1)
    if not longest_swim.empty:
        distance_str = f"{longest_swim['Distance'].values[0]:.2f} miles"
        title_str = longest_swim['Title'].values[0]
    else:
        distance_str = "N/A"
        title_str = "No swimming logged"
    boxed_metric(col_swim, "Longest Swim", distance_str, title_str, "🏊", "#3498db")  # blue
                    
    # Longest Bike
    longest_bike = df[df["Activity Category"]=="Cycling"].sort_values("Distance", ascending=False).head(1)
    if not longest_bike.empty:
        distance_str = f"{longest_bike['Distance'].values[0]:.2f} miles"
        title_str = longest_bike['Title'].values[0]
    else:
        distance_str = "N/A"
        title_str = "No cycling logged"
    boxed_metric(col_bike, "Longest Bike", distance_str, title_str, "🚴", "#e74c3c")  # red

        
        
    # --- Monthly Distance Line Graph ---
    st.subheader("Monthly Distance by Activity")
    left_col, right_col = st.columns([2, 1])  # left is 2x width of right

    # Extract Year-Month for grouping
    df["Month"] = df["Date"].dt.strftime("%b")
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    df["Month"] = pd.Categorical(df["Month"], categories=month_order, ordered=True)

    
    # Group by Activity Category + Month, sum distances
    monthly_distances = (
        df[df["Activity Category"].isin(["Running", "Cycling", "Swimming"])]
        .groupby(["Month", "Activity Category"])["Distance"]
        .sum()
    .reset_index()
    )

    with left_col:
        # Line graph spanning "2 widgets long"
        fig_monthly = px.line(
            monthly_distances,
            x="Month",
            y="Distance",
            color="Activity Category",
            markers=True,
            labels={"Month": "Month", "Distance": "Total Distance (mi)", "Activity Category": "Activity"},
            color_discrete_map={
                "Running": "green",
                "Cycling": "red",
                "Swimming": "blue"
                }
            )
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with right_col:
        st.subheader("📊 Extra Stats")

        # --- Favorite Activity (most frequent) ---
        fav_activity = df["Activity Category"].mode()[0] if not df["Activity Category"].empty else "N/A"
        boxed_metric(right_col, "Favorite Activity", fav_activity, "Most frequent activity type", "⭐", "#9b59b6")

        # --- Total Elevation Climbed ---
        if "Total Ascent" in df.columns:
            total_ascent = pd.to_numeric(df["Total Ascent"], errors="coerce").sum()
            boxed_metric(right_col, "Total Elevation", f"{total_ascent:.0f} ft", "Yearly total ascent", "⛰️", "#e74c3c")
            
            # --- Max Elevation ---
        if "Max Elevation" in df.columns:
            df["Max Elevation Clean"] = (
                df["Max Elevation"]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.strip()
                )
            df["Max Elevation Clean"] = pd.to_numeric(df["Max Elevation Clean"], errors="coerce")
            max_elev = df["Max Elevation Clean"].max()
            boxed_metric(right_col, "Max Elevation", f"{max_elev:.0f} ft", "Highest elevation reached", "🏔️", "#3498db")


    def generate_active_name(stats):
    # Base words depending on favorite activity
     activity_map = {
        "Running": ["Vlogger", "Boujee", "Male Manipulator", "Goblin Mode"],
        "Cycling": ["Mandolin Fairycore", "Emo Ukulele", "Goth RoadWarrior", "Abstract Folding Arts"],
        "Swimming": ["Empathy", "Warlock", "Loosey Goosey", "Coastal Grandmother"]
    }
     base = random.choice(activity_map.get(stats["favorite_activity"], ["Mover"]))

     # Collect all matching flairs
     flairs = []
     if stats["total_distance_mi"] > 1000:
        flairs.append("Ultra")
     if stats["total_ascent_ft"] > 40000:
        flairs.append("Golden Goat of")
     if stats["longest_streak"] > 14:
        flairs.append("24/7")

     # If no conditions matched, give a default
     if not flairs:
        flairs.append("Typical")

     # Join all flairs together before the base
     return " ".join(flairs) + " " + base


    year_stats = {
        #"user": nickname,
        "total_distance_mi": round(total_distance, 1),
        "total_time_days": round(total_days, 1),
        "active_days": active_days,
        "longest_streak": longest_streak,
        "favorite_activity": fav_activity,
        "total_ascent_ft": int(total_ascent),
        "max_elevation_ft": int(max_elev)
        }   

    active_name = generate_active_name(year_stats)
  
    #st.subheader("✨ Your Year in Workout Vibes ✨")
    #st.write(f"**{active_name}** — based on your yearly stats!")
    with st.container():
        st.markdown(
            f"""
            <style>
            .vibe-box {{
                background: linear-gradient(135deg, #ff9a9e, #fad0c4);
                                            border-radius: 15px;
                                            padding: 30px;
            text-align: center;
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }}
        .vibe-sub {{
            font-size: 18px;
            font-weight: normal;
            color: #34495e;
            margin-top: 10px;
        }}
        </style>
        <div class="vibe-box">
            ✨ Workout Vibe ✨
            <div class="vibe-sub">Your energy for 2025: {active_name}!</div>
        </div>
        """,
        unsafe_allow_html=True
    )
                                            
                                            
#reset
    # --- Leaderboard (community) ---
    if "leaderboard" not in st.session_state:
        st.session_state["leaderboard"] = []
        
    nickname = st.text_input("Enter a nickname:", "Anonymous")

    # Build a stats row for this user
    stats_entry = {
        "user": nickname,
        "workout vibe": active_name,
        "total_distance_mi": round(total_distance, 1),
        "total_time_days": round(total_days, 1),
        "active_days": active_days,
        "longest_streak": longest_streak,
        "favorite_activity": fav_activity,
        "total_ascent_ft": int(total_ascent),
        "max_elevation_ft": int(max_elev)
        }   


    # Append to leaderboard
    st.session_state["leaderboard"].append(stats_entry)

    # Convert to DataFrame
    leaderboard_df = pd.DataFrame(st.session_state["leaderboard"])
        
    # Display sorted by total_distance
    st.subheader("Community Leaderboard")
    st.dataframe(
        leaderboard_df.sort_values("total_distance_mi", ascending=False),
            use_container_width=True
            ) 
