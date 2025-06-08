
from api.client import get

def get_upcoming_fixtures(league_id, season_year):
    params = {
        "league": league_id,
        "season": season_year,
        "next": 10
    }
    data = get("fixtures", params=params)
    return data["response"]

def get_finished_fixtures(league_id, season):
    params = {
        "league": league_id,
        "season": season,
        "status": "FT"
    }

    response = get("fixtures", params=params)
    fixtures = response.get("response", [])
    print(f"✅ Total fixtures retrieved for league {league_id}: {len(fixtures)}")
    return fixtures

