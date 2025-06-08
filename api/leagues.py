"""League helpers."""

# A small curated list of popular leagues to limit API calls.
MAJOR_LEAGUES = [
    {"id": 39, "name": "Premier League", "season": 2024},
    {"id": 140, "name": "La Liga", "season": 2024},
    {"id": 135, "name": "Serie A", "season": 2024},
    {"id": 78, "name": "Bundesliga", "season": 2024},
    {"id": 61, "name": "Ligue 1", "season": 2024},
]

def get_supported_leagues():
    """Return a list of leagues used throughout the project."""
    return MAJOR_LEAGUES
