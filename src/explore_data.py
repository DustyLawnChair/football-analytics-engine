import json
import urllib.request
import pandas as pd
import os
import math
import matplotlib.pyplot as plt

url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/competitions.json"
matches_url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/2/27.json"

with urllib.request.urlopen(url) as response:
    data = json.load(response)

with urllib.request.urlopen(matches_url) as response:
    matches = json.load(response)

def analyze_match(match):
    match_id = match["match_id"]
    print(f"Analyzing match ID: {match_id}")

    events_file = f"data/events/{match_id}.json"

    if os.path.exists(events_file):
        print(f"Loading cached events: {match_id}")

        with open(events_file, "r") as file:
            events = json.load(file)

    else:
        print(f"Downloading events: {match_id}")

        events_url = (
            f"https://raw.githubusercontent.com/statsbomb/open-data/"
            f"master/data/events/{match_id}.json"
        )

        with urllib.request.urlopen(events_url) as response:
            events = json.load(response)

        with open(events_file, "w") as file:
            json.dump(events, file)

    shots = []
    shot_records = []

    for event in events:
        if event["type"]["name"] == "Shot":
            shots.append(event)

            x = event["location"][0]
            y = event["location"][1]

            left_goal_distance = math.sqrt(
                x ** 2 +
                (40 - y) ** 2
            )

            right_goal_distance = math.sqrt(
                (120 - x) ** 2 +
                (40 - y) ** 2
            )

            distance = min(left_goal_distance, right_goal_distance)

            event["shot_distance"] = distance

            shot_records.append({
                "Team": event["team"]["name"],
                "Player": event["player"]["name"],
                "x": x,
                "y": y,
                "xG": event["shot"]["statsbomb_xg"],
                "Distance": distance,
                "Outcome": event["shot"]["outcome"]["name"],
                "Body Part": event["shot"]["body_part"]["name"],
                "Shot Type": event["shot"]["type"]["name"]
            })
    shot_counts = {}

    for shot in shots:
        team = shot["team"]["name"]

        if team not in shot_counts:
            shot_counts[team] = 0

        shot_counts[team] += 1

    xg_by_team = {}

    for shot in shots:
        team = shot["team"]["name"]
        xg = shot["shot"]["statsbomb_xg"]

        if team not in xg_by_team:
            xg_by_team[team] = 0

        xg_by_team[team] += xg

    goals_by_team = {
        match["home_team"]["home_team_name"]: match["home_score"],
        match["away_team"]["away_team_name"]: match["away_score"]
    }

    shot_analysis = pd.DataFrame({
        "Team": list(shot_counts.keys()),
        "Shots": list(shot_counts.values()),
        "xG": [
            xg_by_team[team]
            for team in shot_counts.keys()
        ],
        "Goals": [
            goals_by_team[team]
            for team in shot_counts.keys()
        ]
    })

    shot_analysis["xG_per_shot"] = (
        shot_analysis["xG"] / shot_analysis["Shots"]
    )

    shot_analysis["Goals_minus_xG"] = (
        shot_analysis["Goals"] - shot_analysis["xG"]
    )

    return shot_analysis, shot_records

data_frames = []
all_shot_records = []

for match in matches:
    shot_analysis, shot_records = analyze_match(match)
    data_frames.append(shot_analysis)
    all_shot_records.extend(shot_records)

print(f"\nAnalyzed {len(data_frames)} matches.")

season_shot_analysis = pd.concat(data_frames, ignore_index=True)

team_shot_groups = season_shot_analysis.groupby("Team")

team_shot_analysis = team_shot_groups.sum()

team_shot_analysis["xG_per_shot"] = (
    team_shot_analysis["xG"] / team_shot_analysis["Shots"]
)

print(team_shot_analysis.loc["Leicester City"])

print("\nGROUPED SHOT DATA TEST 123:")
print(team_shot_analysis)

shot_data = pd.DataFrame(all_shot_records)

shot_data.to_csv(
    "data/processed/shot_data.csv",
    index=False
)

print("\nAnalyzed matches:", len(data_frames))
print("Total shots:", len(shot_data))

print("\nShot distance summary:")
print(shot_data["Distance"].describe())

print("\nAverage xG by shot distance:")
distance_bins = pd.cut(
    shot_data["Distance"],
    bins=[0, 10, 15, 20, 25, 30, 40, 100]
)

print(
    shot_data.groupby(
        distance_bins,
        observed=True
    )["xG"].mean()
)

print("\nTeam shot profile:")
team_shot_profile = (
    shot_data
    .groupby("Team")
    .agg(
        Shots=("xG", "count"),
        Avg_Distance=("Distance", "mean"),
        Avg_xG=("xG", "mean"),
        Total_xG=("xG", "sum")
    )
    .sort_values("Avg_xG", ascending=False)
)

print(team_shot_profile)

# Create shot zones based on lateral position
shot_data["Shot_Zone"] = pd.cut(
    shot_data["y"],
    bins=[0, 20, 30, 50, 60, 80],
    labels=[
        "Wide Left",
        "Left-Centre",
        "Centre",
        "Right-Centre",
        "Wide Right"
    ]
)

print("\nPercentage of shots from inside 15 meters:")

close_shot_percentage = (
    shot_data["Distance"]
    .le(15)
    .groupby(shot_data["Team"])
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

print(close_shot_percentage)

print("\nPercentage of xG from shots inside 15 meters:")

close_xg_percentage = (
    shot_data[shot_data["Distance"] <= 15]
    .groupby("Team")["xG"]
    .sum()
    .div(
        shot_data.groupby("Team")["xG"].sum()
    )
    .mul(100)
    .sort_values(ascending=False)
)

print(close_xg_percentage)

print("\nIndividual shot data:")
print(shot_data.head())
print("\nSeason shot analysis:")
print(season_shot_analysis.head())

print("\nFinishing efficiency:")

finishing = (
    shot_data
    .groupby("Team")
    .agg(
        Shots=("xG", "count"),
        xG=("xG", "sum")
    )
)

goals = (
    shot_data[shot_data["Outcome"] == "Goal"]
    .groupby("Team")
    .size()
    .rename("Goals")
)

finishing = finishing.join(goals, how="left")

finishing["Goals"] = finishing["Goals"].fillna(0)

finishing["Goals_minus_xG"] = (
    finishing["Goals"] - finishing["xG"]
)

finishing["Conversion_Rate"] = (
    finishing["Goals"] / finishing["Shots"] * 100
)

print(
    finishing
    .sort_values("Goals_minus_xG", ascending=False)
)

plt.scatter(
    finishing["Shots"],
    finishing["Goals"]
)

for team in finishing.index:
    plt.annotate(
        team,
        (
            finishing.loc[team, "Shots"],
            finishing.loc[team, "Goals"]
        )
    )

plt.xlabel("Shots")
plt.ylabel("Goals")
plt.title("Team Shots vs Goals — 2015/16 Premier League")

plt.show()

plt.scatter(
    finishing["xG"],
    finishing["Goals"]
)

for team in finishing.index:
    plt.annotate(
        team,
        (
            finishing.loc[team, "xG"],
            finishing.loc[team, "Goals"]
        )
    )

plt.plot(
    [finishing["xG"].min(), finishing["xG"].max()],
    [finishing["xG"].min(), finishing["xG"].max()]
)

plt.xlabel("Expected Goals (xG)")
plt.ylabel("Actual Goals")
plt.title("Team xG vs Actual Goals — 2015/16 Premier League")

plt.show()


print("\nPlayer shooting analysis:")

player_shooting = (
    shot_data
    .groupby("Player")
    .agg(
        Shots=("xG", "count"),
        xG=("xG", "sum")
    )
)

player_goals = (
    shot_data[shot_data["Outcome"] == "Goal"]
    .groupby("Player")
    .size()
    .rename("Goals")
)

player_shooting = player_shooting.join(
    player_goals,
    how="left"
)

player_shooting["Goals"] = player_shooting["Goals"].fillna(0)

player_shooting["xG_per_shot"] = (
    player_shooting["xG"] /
    player_shooting["Shots"]
)

player_shooting["Goals_minus_xG"] = (
    player_shooting["Goals"] -
    player_shooting["xG"]
)

player_shooting["Conversion_Rate"] = (
    player_shooting["Goals"] /
    player_shooting["Shots"] * 100
)

qualified_players = player_shooting[
    player_shooting["Shots"] >= 50
]

print("\nTop players by finishing above xG:")

print(
    qualified_players
    .sort_values("Goals_minus_xG", ascending=False)
    .head(15)
    .to_string()
)

print(
    player_shooting
    .sort_values("xG", ascending=False)
    .head(20)
)

top_players = qualified_players.sort_values(
    "xG",
    ascending=False
).head(10)

plt.scatter(
    qualified_players["xG"],
    qualified_players["Goals"]
)

for player in top_players.index:
    plt.annotate(
        player,
        (
            top_players.loc[player, "xG"],
            top_players.loc[player, "Goals"]
        )
    )

plt.plot(
    [qualified_players["xG"].min(), qualified_players["xG"].max()],
    [qualified_players["xG"].min(), qualified_players["xG"].max()]
)

plt.xlabel("Expected Goals (xG)")
plt.ylabel("Actual Goals")
plt.title("Player xG vs Actual Goals — 2015/16 Premier League")

plt.show()

finishing_sorted = finishing.sort_values(
    "Goals_minus_xG"
)

plt.barh(
    finishing_sorted.index,
    finishing_sorted["Goals_minus_xG"]
)

plt.xlabel("Goals − xG")
plt.ylabel("Team")
plt.title("Finishing Performance — 2015/16 Premier League")

plt.tight_layout()
plt.show()

def calculate_team_stats(matches, team):
    wins = 0
    draws = 0
    losses = 0
    goals_for = 0
    goals_against = 0
    points = 0

    for match in matches:
        home_team = match["home_team"]["home_team_name"]
        away_team = match["away_team"]["away_team_name"]

        if home_team == team or away_team == team:
            if home_team == team:
                team_goals = match["home_score"]
                opponent_goals = match["away_score"]
            else:
                team_goals = match["away_score"]
                opponent_goals = match["home_score"]

            goals_for += team_goals
            goals_against += opponent_goals

            if team_goals > opponent_goals:
                wins += 1
                points += 3
            elif team_goals == opponent_goals:
                draws += 1
                points += 1
            else:
                losses += 1

    return {
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "points": points,
    }

teams = set()

for match in matches:
    home_team = match["home_team"]["home_team_name"]
    away_team = match["away_team"]["away_team_name"]

    teams.add(home_team)
    teams.add(away_team)

team_stats = []

for team in teams:
    stats = calculate_team_stats(matches, team)
    team_stats.append({
        "team": team,
        **stats
    })


df = pd.DataFrame(team_stats)

df["goal_difference"] = df["goals_for"] - df["goals_against"]

df["matches_played"] = df["wins"] + df["draws"] + df["losses"]

df["points_per_match"] = df["points"] / df["matches_played"]
df["points_per_match"] = df["points_per_match"].round(2)

df["goals_per_match"] = df["goals_for"] / df["matches_played"]
df["goals_per_match"] = df["goals_per_match"].round(2)

df["goals_against_per_match"] = df["goals_against"] / df["matches_played"]
df["goals_against_per_match"] = df["goals_against_per_match"].round(2)

df = df.sort_values(
    ["points", "goal_difference"],
    ascending=[False, False]
)

df["Position"] = range(1, len(df) + 1)

df = df.rename(columns={
    "team": "Team",
    "wins": "W",
    "draws": "D",
    "losses": "L",
    "goals_for": "GF",
    "goals_against": "GA",
    "goal_difference": "GD",
    "points": "Pts"
})

best_attack =df.sort_values(
    "goals_per_match",
    ascending=False
)

print(best_attack[["Team", "goals_per_match"]])


df = df[
    [
        "Position",
        "Team",
        "W",
        "D",
        "L",
        "GF",
        "GA",
        "GD",
        "Pts",
        "matches_played",
        "points_per_match",
        "goals_per_match",
        "goals_against_per_match"
    ]
]

df = df.reset_index(drop=True)

def rank_teams(df, metric):
    sorted_df = df.sort_values(metric, ascending=False)
    return sorted_df

print(rank_teams(df, "goals_per_match"))
rank_teams(df, "points_per_match")
rank_teams(df, "GD")
rank_teams(df, "goals_per_match")










        




