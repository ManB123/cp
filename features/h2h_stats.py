from api.client import get

def get_h2h_features(home_id, away_id, season, last_n=5):
    """
    Extract H2H features for the last N matches between home_id and away_id.
    Returns win/draw/loss record, avg corners, avg expected goals (xG).
    """
    params = {
        "h2h": f"{home_id}-{away_id}",
        "season": season,
        "status": "FT"
    }
    fixtures = get("fixtures", params=params).get("response", [])
    fixtures = sorted(fixtures, key=lambda x: x["fixture"]["date"], reverse=True)[:last_n]

    wins = draws = losses = 0
    total_home_corners = total_away_corners = 0
    total_home_xg = total_away_xg = 0
    count = 0

    for fixture in fixtures:
        fixture_id = fixture["fixture"]["id"]
        try:
            stats = get("fixtures/statistics", params={"fixture": fixture_id}).get("response", [])
            if not stats:
                continue

            goals = fixture["goals"]
            home_team = fixture["teams"]["home"]
            away_team = fixture["teams"]["away"]

            if home_team["id"] == home_id:
                home_goals = goals["home"]
                away_goals = goals["away"]
            else:
                home_goals = goals["away"]
                away_goals = goals["home"]

            if home_goals > away_goals:
                wins += 1
            elif home_goals < away_goals:
                losses += 1
            else:
                draws += 1

            for team_stats in stats:
                team_id = team_stats["team"]["id"]
                for s in team_stats["statistics"]:
                    if s["type"].lower() == "expected goals":
                        xg = float(s["value"] or 0)
                        if team_id == home_id:
                            total_home_xg += xg
                        elif team_id == away_id:
                            total_away_xg += xg
                    if s["type"] == "Corner Kicks":
                        val = s["value"] or 0
                        if team_id == home_id:
                            total_home_corners += val
                        elif team_id == away_id:
                            total_away_corners += val

            count += 1

        except Exception as e:
            print(f"⚠️ Failed to extract H2H stats for fixture {fixture_id}: {e}")

    return {
        "h2h_wins": wins,
        "h2h_draws": draws,
        "h2h_losses": losses,
        "h2h_avg_home_corners": total_home_corners / count if count else 0,
        "h2h_avg_away_corners": total_away_corners / count if count else 0,
        "h2h_avg_home_xg": total_home_xg / count if count else 0,
        "h2h_avg_away_xg": total_away_xg / count if count else 0,
    }
