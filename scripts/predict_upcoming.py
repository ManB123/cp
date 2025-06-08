# scripts/predict_upcoming.py
import os
import sys
import pandas as pd
import joblib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.fixtures import get_upcoming_fixtures
from features.team_form import get_team_form_features
from features.h2h_stats import get_h2h_features
from features.player_availability import get_missing_players_impact

def predict_upcoming_for_league(league_id, season):
    fixtures = get_upcoming_fixtures(league_id, season)
    all_features = []

    for fixture in fixtures:
        fixture_id = fixture["fixture"]["id"]
        home = fixture["teams"]["home"]
        away = fixture["teams"]["away"]

        try:
            # Skip fixture_stats (not available pre-match)
            home_form = get_team_form_features(home["id"], season)
            away_form = get_team_form_features(away["id"], season)
            h2h_stats = get_h2h_features(home["id"], away["id"], season)
            home_impact = get_missing_players_impact(home["id"])
            away_impact = get_missing_players_impact(away["id"])

            features = {}
            features.update({f"home_{k}": v for k, v in home_form.items()})
            features.update({f"away_{k}": v for k, v in away_form.items()})
            features.update(h2h_stats)
            features["home_missing_impact"] = home_impact
            features["away_missing_impact"] = away_impact
            features["home_team"] = home["name"]
            features["away_team"] = away["name"]

            all_features.append(features)

        except Exception as e:
            print(f"⚠️ Skipping fixture {fixture_id} due to error: {e}")

    if not all_features:
        return []

    df = pd.DataFrame(all_features).fillna(0)
    df.columns = df.columns.str.replace(" ", "_")

    # Extract and preserve names for display
    display_data = df[["home_team", "away_team"]]
    df = df.drop(columns=["home_team", "away_team"])

    # Load models
    match_model = joblib.load("models/model_match_result.pkl")
    home_corners_model = joblib.load("models/model_home_corners.pkl")
    away_corners_model = joblib.load("models/model_away_corners.pkl")

    # Load expected columns from training (stored separately)
    expected_cols = joblib.load("models/training_columns.pkl")  # This must be saved during training

    # Reindex with training columns, fill missing with 0
    df = df.reindex(columns=expected_cols, fill_value=0)

    # Predict
    match_preds = match_model.predict(df)
    home_preds = home_corners_model.predict(df)
    away_preds = away_corners_model.predict(df)

    # Combine results
    results = []
    for i in range(len(df)):
        results.append({
            "home_team": display_data.iloc[i]["home_team"],
            "away_team": display_data.iloc[i]["away_team"],
            "result": match_preds[i],
            "home_corners": int(home_preds[i]),
            "away_corners": int(away_preds[i])
        })

    return results
