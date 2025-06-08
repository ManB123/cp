from api.client import get

def get_supported_leagues():
    data = get("leagues")
    leagues = []
    for item in data["response"]:
        league = item["league"]
        country = item["country"]
        leagues.append({
            "id": league["id"],
            "name": f"{league['name']} ({country['name']})",
            "season": item["seasons"][-1]["year"]  # Get most recent season
        })
    return leagues
