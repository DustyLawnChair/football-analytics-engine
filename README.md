# Football Analytics Engine

A Python-based football analytics dashboard built with StatsBomb Open Data and Streamlit.

This project analyzes the 2015/16 Premier League season using event-level match data to explore team performance, shooting, expected goals (xG), and player efficiency.

## Features

### Team Analysis

- Premier League league table
- Team-specific performance statistics
- Team shot analysis
- Shot and goal data

### Player Analysis

- Player profiles
- Player comparison
- Minutes played
- Goals and xG
- Goals per shot
- Shot accuracy
- Average shot distance
- Per-90 statistics

### League Player Rankings

Players can be ranked using a minimum playing-time threshold by:

- Goals per 90
- xG per 90
- Shots per 90
- Goals − xG per 90

The minimum-minutes filter helps reduce the effect of very small sample sizes when comparing players.

## Data

This project uses [StatsBomb Open Data](https://github.com/statsbomb/open-data).

**Current version:** Premier League, 2015/16 season

The current release intentionally focuses on a single competition and season. Support for additional seasons and competitions is planned for future versions.

## Tech Stack

- Python
- pandas
- Streamlit
- StatsBomb Open Data
- Git / GitHub

## Project Structure

```text
football-analytics-engine/
│
├── app.py
├── src/
│   └── explore_data.py
├── data/
│   ├── raw/
│   └── processed/
├── tests/
├── requirements.txt
└── README.md
```

## Running Locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd football-analytics-engine
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Streamlit application

```bash
streamlit run app.py
```

The application will open in your browser.

## Analytics

### Expected Goals (xG)

Expected goals estimates the probability that a shot results in a goal based on characteristics of the chance.

The application uses xG to compare a player's actual scoring output with the quality of chances they received.

### Per-90 Metrics

Per-90 statistics normalize player output based on playing time:

```text
Metric per 90 = Metric / Minutes Played × 90
```

This allows players with different amounts of playing time to be compared more fairly.

### Goals − xG

Goals minus expected goals measures the difference between a player's actual goals and the goals their chances were expected to produce.

```text
Goals − xG = Goals − xG
```

A positive value indicates a player scored more goals than expected based on their recorded chances, while a negative value indicates they scored fewer.

## Version

**v1.0 — 2015/16 Premier League**

This release establishes the core analytics pipeline and dashboard functionality.

## Future Development

Planned future versions may include:

- Additional Premier League seasons
- Additional domestic leagues and competitions
- Cross-season player analysis
- Player shot maps and heatmaps
- Expected assists (xA)
- Advanced player profiles
- Team style analysis
- Additional visualization and scouting tools

## Author

Hunter Dornblaser