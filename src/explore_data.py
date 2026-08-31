import json
import urllib.request

url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/competitions.json"
matches_url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/2/27.json"

with urllib.request.urlopen(url) as response:
    data = json.load(response)

with urllib.request.urlopen(matches_url) as response:
    matches = json.load(response)






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


arsenal = calculate_team_stats(matches, "Arsenal")
chelsea = calculate_team_stats(matches, "Chelsea")
liverpool = calculate_team_stats(matches, "Liverpool")

print("Arsenal:", arsenal)
print("Chelsea:", chelsea)
print("Liverpool:", liverpool)






        




