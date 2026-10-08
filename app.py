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

shot_data = pd.read_csv(
    "data/processed/shot_data.csv"
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

team_shots = shot_data[
    shot_data["Team"] == selected_team
]

players = sorted(shot_data["Player"].unique())

selected_player = st.sidebar.selectbox(
    "Select a player",
    players
)

player_shots = shot_data[
    shot_data["Player"] == selected_player
]

player_goals = player_shots["Outcome"].eq("Goal").sum()

player_xg = player_shots["xG"].sum()

goals_minus_xg = player_goals - player_xg

conversion_rate = (
    player_goals /
    len(player_shots) *
    100
)

avg_shot_distance = player_shots["Distance"].mean()

shots_on_target = player_shots["Outcome"].isin(
    ["Goal", "Saved"]
).sum()

shot_accuracy = (
    shots_on_target /
    len(player_shots) *
    100
)


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

st.header(f"{selected_team} — Shot Profile")

shot_col1, shot_col2, shot_col3, shot_col4 = st.columns(4)

shot_col1.metric(
    "Shots",
    len(team_shots)
)

shot_col2.metric(
    "Avg Shot Distance",
    f"{team_shots['Distance'].mean():.2f}"
)

shot_col3.metric(
    "xG per Shot",
    f"{team_shots['xG'].mean():.3f}"
)

shot_col4.metric(
    "Goals − xG",
    f"{team_shots['Outcome'].eq('Goal').sum() - team_shots['xG'].sum():.2f}"
)

st.subheader("Shot Quality by Distance")

distance_bins = [0, 10, 15, 20, 25, 30, 40, 100]

team_shots["Distance_Bin"] = pd.cut(
    team_shots["Distance"],
    bins=distance_bins
)

distance_xg = (
    team_shots
    .groupby("Distance_Bin", observed=False)["xG"]
    .mean()
    .reset_index()
)

distance_xg["Distance_Bin"] = distance_xg["Distance_Bin"].astype(str)

st.bar_chart(
    distance_xg,
    x="Distance_Bin",
    y="xG",
    width="stretch"
)

st.subheader("Shot Distribution by Zone")

zone_shots = (
    team_shots
    .groupby("Shot_Zone", observed=False)
    .size()
    .reset_index(name="Shots")
)

st.bar_chart(
    zone_shots,
    x="Shot_Zone",
    y="Shots",
    width="stretch"
)

st.header(f"{selected_player} — Player Profile")

player_col1, player_col2, player_col3, player_col4, player_col5, player_col6 = st.columns(6)

player_col1.metric(
    "Shots",
    len(player_shots)
)

player_col2.metric(
    "Goals",
    int(player_shots["Outcome"].eq("Goal").sum())
)

player_col3.metric(
    "xG",
    f"{player_shots['xG'].sum():.2f}"
)

player_col4.metric(
    "xG per Shot",
    f"{player_shots['xG'].mean():.3f}"
)

player_col5.metric(
    "Shots on Target",
    int(shots_on_target)
)

player_col6.metric(
    "Shot Accuracy",
    f"{shot_accuracy:.2f}%"
)

st.subheader("Player Efficiency")

eff_col1, eff_col2, eff_col3 = st.columns(3)

eff_col1.metric(
    "Goals − xG",
    f"{goals_minus_xg:.2f}"
)

eff_col2.metric(
    "Conversion Rate",
    f"{conversion_rate:.2f}%"
)

eff_col3.metric(
    "Avg Shot Distance",
    f"{avg_shot_distance:.2f}"
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