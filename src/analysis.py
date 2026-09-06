import json
import os
import urllib.request

import matplotlib.pyplot as plt
import pandas as pd


# ============================================================
# Configuration
# ============================================================

COMPETITIONS_URL = (
    "https://raw.githubusercontent.com/statsbomb/open-data/"
    "master/data/competitions.json"
)

MATCHES_URL = (
    "https://raw.githubusercontent.com/statsbomb/open-data/"
    "master/data/matches/2/27.json"
)

EVENTS_URL = (
    "https://raw.githubusercontent.com/statsbomb/open-data/"
    "master/data/events/{match_id}.json"
)

EVENT_CACHE_DIR = "data/events"
PROCESSED_DATA_DIR = "data/processed"


# ============================================================
# Data Loading
# ============================================================

def load_json(url):
    """Download and return JSON data from a URL."""
    with urllib.request.urlopen(url) as response:
        return json.load(response)


def load_matches():
    """Load the 2015/16 Premier League match data."""
    return load_json(MATCHES_URL)


# ============================================================
# Match Analysis
# ============================================================

def load_match_events(match_id):
    """Load match events from cache or download them from StatsBomb."""

    os.makedirs(EVENT_CACHE_DIR, exist_ok=True)

    events_file = f"{EVENT_CACHE_DIR}/{match_id}.json"

    if os.path.exists(events_file):
        print(f"Loading cached events: {match_id}")

        with open(events_file, "r") as file:
            return json.load(file)

    print(f"Downloading events: {match_id}")

    events_url = EVENTS_URL.format(match_id=match_id)
    events = load_json(events_url)

    with open(events_file, "w") as file:
        json.dump(events, file)

    return events


def analyze_match(match):
    """Analyze shots, xG, and goals for a single match."""

    match_id = match["match_id"]

    print(f"Analyzing match ID: {match_id}")

    events = load_match_events(match_id)

    # Find all shots in the match
    shots = [
        event
        for event in events
        if event["type"]["name"] == "Shot"
    ]

    # Count shots by team
    shot_counts = {}

    for shot in shots:
        team = shot["team"]["name"]

        if team not in shot_counts:
            shot_counts[team] = 0

        shot_counts[team] += 1

    # Calculate xG by team
    xg_by_team = {}

    for shot in shots:
        team = shot["team"]["name"]
        xg = shot["shot"]["statsbomb_xg"]

        if team not in xg_by_team:
            xg_by_team[team] = 0

        xg_by_team[team] += xg

    # Get goals by team
    goals_by_team = {
        match["home_team"]["home_team_name"]: match["home_score"],
        match["away_team"]["away_team_name"]: match["away_score"]
    }

    # Build match analysis DataFrame
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


def build_season_shot_analysis(matches):
    """Analyze shots and xG across the entire season."""

    match_analyses = []

    for match in matches:
        match_analysis = analyze_match(match)
        match_analyses.append(match_analysis)

    print(f"\nAnalyzed {len(match_analyses)} matches.")

    return pd.concat(
        match_analyses,
        ignore_index=True
    )


def build_team_shot_analysis(season_shot_analysis):
    """Aggregate shot statistics by team."""

    team_shot_analysis = (
        season_shot_analysis
        .groupby("Team")[["Shots", "xG", "Goals"]]
        .sum()
    )

    team_shot_analysis["xG_per_shot"] = (
        team_shot_analysis["xG"]
        / team_shot_analysis["Shots"]
    )

    team_shot_analysis["Goals_minus_xG"] = (
        team_shot_analysis["Goals"]
        - team_shot_analysis["xG"]
    )

    return team_shot_analysis


# ============================================================
# League Table
# ============================================================

def calculate_team_stats(matches, team):
    """Calculate traditional league statistics for a team."""

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
        "points": points
    }


def get_teams(matches):
    """Return a set containing every team in the season."""

    teams = set()

    for match in matches:
        teams.add(
            match["home_team"]["home_team_name"]
        )

        teams.add(
            match["away_team"]["away_team_name"]
        )

    return teams


def build_league_table(matches):
    """Build the traditional Premier League table."""

    team_stats = []

    for team in get_teams(matches):
        stats = calculate_team_stats(matches, team)

        team_stats.append({
            "team": team,
            **stats
        })

    df = pd.DataFrame(team_stats)

    # Derived statistics
    df["goal_difference"] = (
        df["goals_for"] - df["goals_against"]
    )

    df["matches_played"] = (
        df["wins"]
        + df["draws"]
        + df["losses"]
    )

    df["points_per_match"] = (
        df["points"] / df["matches_played"]
    )

    df["goals_per_match"] = (
        df["goals_for"] / df["matches_played"]
    )

    df["goals_against_per_match"] = (
        df["goals_against"] / df["matches_played"]
    )

    # Sort into league-table order
    df = df.sort_values(
        ["points", "goal_difference"],
        ascending=[False, False]
    )

    df["Position"] = range(1, len(df) + 1)

    # Rename columns for final output
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

    # Organize columns
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

    return df.reset_index(drop=True)


# ============================================================
# Team Rankings & Scoring
# ============================================================

def normalize_metric(df, column, higher_is_better=True):
    """Normalize a metric to a 0–1 scale."""

    min_value = df[column].min()
    max_value = df[column].max()

    normalized = (
        (df[column] - min_value)
        / (max_value - min_value)
    )

    if not higher_is_better:
        normalized = 1 - normalized

    return normalized


def rank_teams(df, metric):
    """Rank teams by a selected metric."""

    return df.sort_values(
        metric,
        ascending=False
    )


def top_teams(df, metric, n=5):
    """Return the top N teams for a metric."""

    return (
        df.sort_values(metric, ascending=False)
        .head(n)
    )


def get_best_defenses(df, n=5):
    """Return the teams with the best defensive record."""

    return (
        df.sort_values(
            "goals_against_per_match",
            ascending=True
        )
        .head(n)
    )


def calculate_team_scores(df):
    """Calculate normalized attack, defense, results, and overall scores."""

    df["attack_score"] = normalize_metric(
        df,
        "goals_per_match"
    )

    df["defense_score"] = normalize_metric(
        df,
        "goals_against_per_match",
        higher_is_better=False
    )

    df["results_score"] = normalize_metric(
        df,
        "points_per_match"
    )

    df["overall_score"] = (
        df["attack_score"] * 0.30
        + df["defense_score"] * 0.30
        + df["results_score"] * 0.40
    )

    return df


# ============================================================
# Reporting
# ============================================================

def print_analysis_report(df, team_shot_analysis):
    """Print major analytical findings."""

    print("\nTop teams by xG:")
    print(
        team_shot_analysis
        .sort_values("xG", ascending=False)
        [["xG"]]
        .head(5)
    )

    print("\nBest finishing relative to xG:")
    print(
        team_shot_analysis
        .sort_values(
            "Goals_minus_xG",
            ascending=False
        )
        [["Goals", "xG", "Goals_minus_xG"]]
        .head(5)
    )

    print("\nWorst finishing relative to xG:")
    print(
        team_shot_analysis
        .sort_values(
            "Goals_minus_xG",
            ascending=True
        )
        [["Goals", "xG", "Goals_minus_xG"]]
        .head(5)
    )

    print("\nTop teams by points per match:")
    print(
        rank_teams(
            df,
            "points_per_match"
        )
        .head(5)
        [["Team", "points_per_match"]]
    )

    print("\nTop teams by goal difference:")
    print(
        rank_teams(df, "GD")
        .head(5)
        [["Team", "GD"]]
    )

    print("\nTop teams by goals per match:")
    print(
        rank_teams(
            df,
            "goals_per_match"
        )
        .head(5)
        [["Team", "goals_per_match"]]
    )

    print("\nBest defenses:")
    print(
        get_best_defenses(df)
        [["Team", "goals_against_per_match"]]
    )

    print("\nNormalized team scores:")
    print(
        df[
            [
                "Team",
                "attack_score",
                "defense_score",
                "results_score"
            ]
        ]
        .sort_values(
            "results_score",
            ascending=False
        )
    )

    print("\nOverall team performance:")
    print(
        df.sort_values(
            "overall_score",
            ascending=False
        )
        .head(5)
        [
            [
                "Team",
                "attack_score",
                "defense_score",
                "results_score",
                "overall_score"
            ]
        ]
    )

    print("\nBest shot quality:")
    print(
        team_shot_analysis
        .sort_values(
            "xG_per_shot",
            ascending=False
        )
        [["Shots", "xG", "xG_per_shot"]]
        .head(5)
    )

    correlation = team_shot_analysis["Shots"].corr(
        team_shot_analysis["Goals"]
    )

    print(
        f"\nShots vs Goals correlation: "
        f"{correlation:.3f}"
    )


# ============================================================
# Visualization
# ============================================================

def plot_shots_vs_goals(team_shot_analysis):
    """Plot team shots against goals scored."""

    plt.figure()

    plt.scatter(
        team_shot_analysis["Shots"],
        team_shot_analysis["Goals"]
    )

    for team, row in team_shot_analysis.iterrows():
        plt.annotate(
            team,
            (row["Shots"], row["Goals"])
        )

    plt.xlabel("Shots")
    plt.ylabel("Goals")
    plt.title(
        "Shots vs Goals — 2015/16 Premier League"
    )

    plt.show()


def plot_shots_vs_xg(team_shot_analysis):
    """Plot team shots against expected goals."""

    plt.figure()

    plt.scatter(
        team_shot_analysis["Shots"],
        team_shot_analysis["xG"]
    )

    plt.xlabel("Shots")
    plt.ylabel("xG")
    plt.title(
        "Shots vs Expected Goals — 2015/16 Premier League"
    )

    plt.show()


# ============================================================
# Export
# ============================================================

def save_processed_data(df, team_shot_analysis):
    """Save processed datasets for the Streamlit dashboard."""

    os.makedirs(
        PROCESSED_DATA_DIR,
        exist_ok=True
    )

    team_shot_analysis.to_csv(
        f"{PROCESSED_DATA_DIR}/team_shot_analysis.csv"
    )

    df.to_csv(
        f"{PROCESSED_DATA_DIR}/league_table.csv",
        index=False
    )


# ============================================================
# Main Pipeline
# ============================================================

def main():

    print("Loading StatsBomb data...")

    matches = load_matches()

    # Shot analysis
    season_shot_analysis = build_season_shot_analysis(
        matches
    )

    team_shot_analysis = build_team_shot_analysis(
        season_shot_analysis
    )

    # League table
    df = build_league_table(matches)

    # Add shot/xG statistics to league table
    df = df.merge(
        team_shot_analysis,
        on="Team",
        how="left"
    )

    # Calculate team performance scores
    df = calculate_team_scores(df)

    # Reporting
    print_analysis_report(
        df,
        team_shot_analysis
    )

    # Visualizations
    plot_shots_vs_goals(
        team_shot_analysis
    )

    plot_shots_vs_xg(
        team_shot_analysis
    )

    # Save processed data
    save_processed_data(
        df,
        team_shot_analysis
    )

    print("\nAnalysis complete.")
    print("Processed data saved successfully.")


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()