import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.leagues import get_supported_leagues
from api.fixtures import get_finished_fixtures
from features.fixture_stats import get_fixture_stats
from features.team_form import get_team_form_features
from features.h2h_stats import get_h2h_features
from features.player_availability import get_missing_players_impact

OUTPUT_DIR = "data/training"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_features_from_fixture(fixture):
    fixture_id = fixture["fixture"]["id"]
    home = fixture["teams"]["home"]
    away = fixture["teams"]["away"]
    season = fixture["league"]["season"]

    try:
        stats = get_fixture_stats(fixture_id, home["id"], away["id"])
        if not stats:
            print(f"⚠️ No stats for fixture {fixture_id}")
            return None

        home_form = get_team_form_features(home["id"], season)
        away_form = get_team_form_features(away["id"], season)
        h2h = get_h2h_features(home["id"], away["id"], season)
        home_impact = get_missing_players_impact(home["id"])
        away_impact = get_missing_players_impact(away["id"])

        stats.update({f"home_{k}": v for k, v in home_form.items()})
        stats.update({f"away_{k}": v for k, v in away_form.items()})
        stats.update(h2h)
        stats["home_missing_impact"] = home_impact
        stats["away_missing_impact"] = away_impact
        stats["home_team"] = home["name"]
        stats["away_team"] = away["name"]

        return stats

    except Exception as e:
        print(f"❌ Skipping fixture {fixture_id} due to error: {e}")
        return None

def main():
    all_data = []

    for league in get_supported_leagues():
        league_id = league["id"]
        season = league["season"]

        assert isinstance(season, int), f"Season must be int! Got {season} ({type(season)})"

        print(f"\n🔍 Processing {league['name']} (ID: {league_id}, Season: {season})...")
        fixtures = get_finished_fixtures(league_id, season)
        print(f"✅ Fixtures returned: {len(fixtures)}")

        rows = []
        for f in fixtures:
            result = extract_features_from_fixture(f)
            if result:
                rows.append(result)
            else:
                print(f"⚠️ Skipped fixture {f['fixture']['id']}")

        if rows:
            df = pd.DataFrame(rows)
            league_file = os.path.join(OUTPUT_DIR, f"{league['name'].replace(' ', '_')}_features.csv")
            df.to_csv(league_file, index=False)
            print(f"✅ Saved {len(df)} rows to {league_file}")
            all_data.append(df)
        else:
            print(f"⚠️ No valid data for {league['name']}")

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        combined.to_csv(os.path.join(OUTPUT_DIR, "training_data.csv"), index=False)
        print("📦 Full training data saved to data/training/training_data.csv")

if __name__ == "__main__":
    main()
