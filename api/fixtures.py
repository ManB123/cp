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
    """
    Fetch all finished fixtures for a given league and season.
    """
    fixtures = []
    page = 1

    while True:
        params = {
            "league": league_id,
            "season": season,
            "status": "FT",
            "page": page
        }
        response = get("fixtures", params=params)
        data = response.get("response", [])

        if not data:
            break

        fixtures.extend(data)
        if response.get("paging", {}).get("current", 1) >= response.get("paging", {}).get("total", 1):
            break

        page += 1
    print(f"✅ Raw finished fixtures response for league {league_id} season {season}:")
    print(response["response"])

    return fixtures
