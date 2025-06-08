from api.client import get

def get_fixture_stats(fixture_id, home_id, away_id):
    """
    Fetch and structure per-team fixture stats like xG, corners, possession, etc.
    """
    data = get("fixtures/statistics", params={"fixture": fixture_id})
    stats = {"fixture_id": fixture_id, "home_corners": None, "away_corners": None}

    if not data.get("response") or len(data["response"]) != 2:
        print(f"⚠️ Skipping fixture {fixture_id} — no valid stats")
        return None

    for team_data in data["response"]:
        team_id = team_data["team"]["id"]
        team_name = team_data["team"]["name"]

        for stat in team_data["statistics"]:
            stat_type = stat["type"]
            value = stat["value"]
            stats[f"{team_name}_{stat_type}"] = value

            if stat_type == "Corner Kicks":
                if team_id == home_id:
                    stats["home_corners"] = value
                elif team_id == away_id:
                    stats["away_corners"] = value

    return stats if stats["home_corners"] is not None and stats["away_corners"] is not None else None
