from api.client import get

def get_missing_players_impact(team_id):
    """
    Calculate a basic player impact score based on injured/suspended players.
    Uses rating (if available) and goals + assists as a proxy for impact.
    """
    players = get("players/squads", params={"team": team_id})["response"]
    player_ids = [p["id"] for p in players[0]["players"]] if players else []

    impact_score = 0
    for pid in player_ids:
        player_data = get("players", params={"id": pid, "season": 2024}).get("response", [])
        if not player_data:
            continue

        player = player_data[0]["statistics"][0]
        injured = player.get("games", {}).get("injured", False)

        if injured:
            rating = float(player.get("games", {}).get("rating") or 6.0)
            goals = player.get("goals", {}).get("total", 0)
            assists = player.get("goals", {}).get("assists", 0) or 0
            impact_score += rating + goals + assists

    return impact_score
