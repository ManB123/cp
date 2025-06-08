from api.client import get

def get_team_form_features(team_id, season, last_n=5):
    """
    Computes average goals, corners, xG, and win/draw/loss rate from recent matches.
    """
    params = {
        "team": team_id,
        "season": season,
        "status": "FT"
    }
    matches = get("fixtures", params=params)["response"]
    matches = sorted(matches, key=lambda m: m["fixture"]["date"], reverse=True)[:last_n]

    stats = {
        "avg_goals": 0,
        "avg_corners": 0,
        "avg_xg": 0,
        "win_rate": 0,
        "draw_rate": 0,
        "loss_rate": 0
    }

    wins = draws = losses = total_goals = total_corners = total_xg = 0

    for m in matches:
        team_side = "home" if m["teams"]["home"]["id"] == team_id else "away"
        goals_for = m["goals"][team_side]
        goals_against = m["goals"]["away" if team_side == "home" else "home"]

        if goals_for > goals_against:
            wins += 1
        elif goals_for == goals_against:
            draws += 1
        else:
            losses += 1

        total_goals += goals_for or 0

        stats_data = get("fixtures/statistics", params={"fixture": m["fixture"]["id"]}).get("response", [])
        for team_data in stats_data:
            if team_data["team"]["id"] != team_id:
                continue
            for s in team_data["statistics"]:
                if s["type"] == "Expected Goals":
                    total_xg += float(s["value"] or 0)
                if s["type"] == "Corner Kicks":
                    total_corners += s["value"] or 0

    n = len(matches)
    if n > 0:
        stats["avg_goals"] = total_goals / n
        stats["avg_corners"] = total_corners / n
        stats["avg_xg"] = total_xg / n
        stats["win_rate"] = wins / n
        stats["draw_rate"] = draws / n
        stats["loss_rate"] = losses / n

    return stats