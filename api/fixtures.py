from api.client import get

def get_upcoming_fixtures(league_id, season_year):
    params = {
        "league": league_id,
        "season": season_year,
        "next": 10
    }
    data = get("fixtures", params=params)
    return data["response"]
