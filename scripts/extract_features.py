import pandas as pd
from features.fixture_stats import get_fixture_stats
from features.team_form import get_team_form_features
from features.h2h_stats import get_h2h_features
from features.player_availability import get_missing_players_impact

def build_feature_set(fixtures):
    all_features = []

    for fixture in fixtures:
        fixture_id = fixture["fixture"]["id"]
        home_id = fixture["teams"]["home"]["id"]
        away_id = fixture["teams"]["away"]["id"]
        season = fixture["league"]["season"]

        try:
            # Base fixture stats
            stats = get_fixture_stats(fixture_id, home_id, away_id)
            if not stats:
                continue

            # Team form stats
            home_form = get_team_form_features(home_id, season)
            away_form = get_team_form_features(away_id, season)
            for k, v in home_form.items():
                stats[f"home_{k}"] = v
            for k, v in away_form.items():
                stats[f"away_{k}"] = v

            # H2H stats
            h2h = get_h2h_features(home_id, away_id, season)
            stats.update(h2h)

            # Player availability (injuries/suspensions)
            stats["home_missing_impact"] = get_missing_players_impact(home_id)
            stats["away_missing_impact"] = get_missing_players_impact(away_id)

            all_features.append(stats)

        except Exception as e:
            print(f"❌ Error processing fixture {fixture_id}: {e}")

    return pd.DataFrame(all_features)
