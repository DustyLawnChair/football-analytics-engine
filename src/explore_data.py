import json
import urllib.request
import pandas as pd
import os

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

    for event in events:
        if event["type"]["name"] == "Shot":
            shots.append(event)

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

    return shot_analysis

data_frames = []

for match in matches:
    shot_analysis = analyze_match(match)
    data_frames.append(shot_analysis)

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
print("\nSeason shot analysis:")
print(season_shot_analysis)

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
df = df.sort_values(
    ["points", "goal_difference"],
    ascending=[False, False])


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










        




