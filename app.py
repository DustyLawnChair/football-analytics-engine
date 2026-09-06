import streamlit as st
import pandas as pd


# -----------------------------
# Page setup
# -----------------------------

st.set_page_config(
    page_title="Football Analytics Engine",
    page_icon="⚽",
    layout="wide"
)

st.title("Football Analytics Engine")
st.write("2015/16 Premier League Analysis")


# -----------------------------
# Load data
# -----------------------------

league_table = pd.read_csv(
    "data/processed/league_table.csv"
)


# -----------------------------
# Team Explorer
# -----------------------------

st.sidebar.header("Team Explorer")

selected_team = st.sidebar.selectbox(
    "Select a team",
    league_table["Team"]
)

team_data = league_table[
    league_table["Team"] == selected_team
].iloc[0]


# -----------------------------
# Team Profile
# -----------------------------

st.header(f"{selected_team} — Team Profile")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Position",
    int(team_data["Position"])
)

col2.metric(
    "Points",
    int(team_data["Pts"])
)

col3.metric(
    "Goals",
    int(team_data["GF"])
)

col4.metric(
    "xG",
    f"{team_data['xG']:.2f}"
)


# -----------------------------
# League Overview
# -----------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "Teams",
    len(league_table)
)

col2.metric(
    "Matches",
    league_table["matches_played"].sum() // 2
)

col3.metric(
    "Top Team",
    league_table.iloc[0]["Team"]
)


# -----------------------------
# League Table
# -----------------------------

st.header("League Table")

st.dataframe(
    league_table[
        [
            "Position",
            "Team",
            "W",
            "D",
            "L",
            "GF",
            "GA",
            "GD",
            "Pts"
        ]
    ],
    hide_index=True,
    width="stretch"
)


# -----------------------------
# Goals Scored
# -----------------------------

st.header("Goals Scored")

goals_chart = league_table.sort_values(
    "GF",
    ascending=True
)

st.bar_chart(
    goals_chart,
    x="Team",
    y="GF",
    horizontal=True,
    width="stretch"
)


# -----------------------------
# Expected Goals vs Actual Goals
# -----------------------------

st.header("Expected Goals vs Actual Goals")

xg_chart = league_table.sort_values(
    "GF",
    ascending=True
)

st.bar_chart(
    xg_chart,
    x="Team",
    y=["GF", "xG"],
    horizontal=True,
    width="stretch"
)