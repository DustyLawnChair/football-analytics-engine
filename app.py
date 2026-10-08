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
# League Player Data
# -----------------------------

player_minutes_data = (
    shot_data[
        ["Team", "Player", "Match_ID", "Minutes"]
    ]
    .drop_duplicates()
    .groupby(["Team", "Player"], as_index=False)["Minutes"]
    .sum()
    .rename(columns={"Minutes": "Season_Minutes"})
)

player_stats = (
    shot_data
    .groupby(["Team", "Player"])
    .agg(
        Shots=("Player", "size"),
        Goals=("Outcome", lambda x: (x == "Goal").sum()),
        xG=("xG", "sum")
    )
    .reset_index()
)

player_stats = player_stats.merge(
    player_minutes_data,
    on=["Team", "Player"],
    how="left"
)

player_stats["Shots_per_90"] = (
    player_stats["Shots"]
    / player_stats["Season_Minutes"]
    * 90
)

player_stats["Goals_per_90"] = (
    player_stats["Goals"]
    / player_stats["Season_Minutes"]
    * 90
)

player_stats["xG_per_90"] = (
    player_stats["xG"]
    / player_stats["Season_Minutes"]
    * 90
)

player_stats["Goals_minus_xG_per_90"] = (
    (player_stats["Goals"] - player_stats["xG"])
    / player_stats["Season_Minutes"]
    * 90
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


# -----------------------------
# Player Selection
# -----------------------------

team_players = sorted(
    shot_data[
        shot_data["Team"] == selected_team
    ]["Player"].unique()
)

selected_player = st.sidebar.selectbox(
    "Select a player",
    team_players
)

selected_player_2 = st.sidebar.selectbox(
    "Compare with",
    team_players
)

player_shots = shot_data[
    shot_data["Player"] == selected_player
]

player_shots_2 = shot_data[
    shot_data["Player"] == selected_player_2
]

min_minutes = st.sidebar.slider(
    "Minimum minutes",
    min_value=0,
    max_value=3000,
    value=900,
    step=90
)

# -----------------------------
# Apply Minimum Minutes Filter
# -----------------------------

ranking_options = {
    "Goals per 90": "Goals_per_90",
    "xG per 90": "xG_per_90",
    "Shots per 90": "Shots_per_90",
    "Goals - xG per 90": "Goals_minus_xG_per_90"
}

ranking_label = st.selectbox(
    "Rank players by",
    ranking_options.keys()
)

ranking_metric = ranking_options[ranking_label]

qualified_players = player_stats[
    player_stats["Season_Minutes"] >= min_minutes
].copy()

top_players = qualified_players.sort_values(
    ranking_metric,
    ascending=False
).head(10)


# -----------------------------
# Player Rankings
# -----------------------------

st.subheader("League Player Rankings")

ranking_display = top_players[
    [
        "Player",
        "Team",
        "Season_Minutes",
        "Goals",
        "Goals_per_90",
        "xG_per_90",
        "Shots_per_90",
        "Goals_minus_xG_per_90"
    ]
].rename(
    columns={
        "Season_Minutes": "Minutes",
        "Goals_per_90": "Goals / 90",
        "xG_per_90": "xG / 90",
        "Shots_per_90": "Shots / 90",
        "Goals_minus_xG_per_90": "Goals − xG / 90"
    }
)

st.dataframe(
    ranking_display,
    hide_index=True,
    width="stretch"
)

# -----------------------------
# Second Player Metrics
# -----------------------------

player_2_minutes = (
    player_shots_2[["Match_ID", "Minutes"]]
    .drop_duplicates()["Minutes"]
    .sum()
)

player_2_goals = player_shots_2["Outcome"].eq("Goal").sum()
player_2_xg = player_shots_2["xG"].sum()

player_2_goals_minus_xg = player_2_goals - player_2_xg

player_2_shots_per_90 = (
    len(player_shots_2) / player_2_minutes * 90
    if player_2_minutes > 0
    else 0
)

player_2_goals_per_90 = (
    player_2_goals / player_2_minutes * 90
    if player_2_minutes > 0
    else 0
)

player_2_xg_per_90 = (
    player_2_xg / player_2_minutes * 90
    if player_2_minutes > 0
    else 0
)

player_2_goals_minus_xg_per_90 = (
    player_2_goals_minus_xg / player_2_minutes * 90
    if player_2_minutes > 0
    else 0
)

player_2_goals_per_shot = (
    player_2_goals / len(player_shots_2)
    if len(player_shots_2) > 0
    else 0
)

player_2_conversion_rate = (
    player_2_goals / len(player_shots_2) * 100
    if len(player_shots_2) > 0
    else 0
)

player_2_avg_shot_distance = player_shots_2["Distance"].mean()

player_2_shots_on_target = player_shots_2["Outcome"].isin(
    ["Goal", "Saved"]
).sum()

player_2_shot_accuracy = (
    player_2_shots_on_target / len(player_shots_2) * 100
    if len(player_shots_2) > 0
    else 0
)


# -----------------------------
# Player Minutes
# -----------------------------

player_minutes = (
    player_shots[["Match_ID", "Minutes"]]
    .drop_duplicates()["Minutes"]
    .sum()
)


# -----------------------------
# Player Core Metrics
# -----------------------------

player_goals = player_shots["Outcome"].eq("Goal").sum()
player_xg = player_shots["xG"].sum()

goals_minus_xg = player_goals - player_xg

conversion_rate = (
    player_goals / len(player_shots) * 100
)

goals_per_shot = (
    player_goals / len(player_shots)
    if len(player_shots) > 0
    else 0
)

avg_shot_distance = player_shots["Distance"].mean()

shots_on_target = player_shots["Outcome"].isin(
    ["Goal", "Saved"]
).sum()

shot_accuracy = (
    shots_on_target / len(player_shots) * 100
)


# -----------------------------
# Player Rate Metrics
# -----------------------------

shots_per_90 = (
    len(player_shots) / player_minutes * 90
    if player_minutes > 0
    else 0
)

goals_per_90 = (
    player_goals / player_minutes * 90
    if player_minutes > 0
    else 0
)

xg_per_90 = (
    player_xg / player_minutes * 90
    if player_minutes > 0
    else 0
)

goals_minus_xg_per_90 = (
    (player_goals - player_xg) / player_minutes * 90
    if player_minutes > 0
    else 0
)


# -----------------------------
# Player Comparison Display
# -----------------------------

st.subheader("Player Comparison")

comparison_data = {
    "Metric": [
        "Minutes",
        "Shots",
        "Goals",
        "xG",
        "Shots per 90",
        "Goals per 90",
        "xG per 90",
        "Goals − xG",
        "Goals − xG per 90",
        "Goals per Shot",
        "Conversion Rate",
        "Shot Accuracy",
        "Avg Shot Distance"
    ],
    selected_player: [
    f"{player_minutes}",
    f"{len(player_shots)}",
    f"{player_goals}",
    f"{player_xg:.2f}",
    f"{shots_per_90:.2f}",
    f"{goals_per_90:.2f}",
    f"{xg_per_90:.2f}",
    f"{goals_minus_xg:.2f}",
    f"{goals_minus_xg_per_90:.2f}",
    f"{goals_per_shot:.3f}",
    f"{conversion_rate:.2f}%",
    f"{shot_accuracy:.2f}%",
    f"{avg_shot_distance:.2f}m"
    ],

    selected_player_2: [
    f"{player_2_minutes}",
    f"{len(player_shots_2)}",
    f"{player_2_goals}",
    f"{player_2_xg:.2f}",
    f"{player_2_shots_per_90:.2f}",
    f"{player_2_goals_per_90:.2f}",
    f"{player_2_xg_per_90:.2f}",
    f"{player_2_goals_minus_xg:.2f}",
    f"{player_2_goals_minus_xg_per_90:.2f}",
    f"{player_2_goals_per_shot:.3f}",
    f"{player_2_conversion_rate:.2f}%",
    f"{player_2_shot_accuracy:.2f}%",
    f"{player_2_avg_shot_distance:.2f}m"
    ]
}

comparison_df = pd.DataFrame(comparison_data)

st.dataframe(
    comparison_df,
    hide_index=True,
    width="stretch"
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

player_col1, player_col2, player_col3, player_col4, player_col5, player_col6, player_col7, player_col8, player_col9, player_col10 = st.columns(10)

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

player_col7.metric(
    "Shots per 90",
    f"{shots_per_90:.2f}"
)

player_col8.metric(
    "Goals per 90",
    f"{goals_per_90:.2f}"
)

player_col9.metric(
    "xG per 90",
    f"{xg_per_90:.2f}"
)

player_col10.metric(
    "Goals − xG / 90",
    f"{goals_minus_xg_per_90:.2f}"
)

st.subheader("Player Efficiency")

eff_col1, eff_col2, eff_col3, eff_col4 = st.columns(4)

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

eff_col4.metric(
    "Goals per Shot",
    f"{goals_per_shot:.3f}"
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