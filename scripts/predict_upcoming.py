# scripts/predict_upcoming.py
import os
import sys
import pandas as pd
import joblib
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.fixtures import get_upcoming_fixtures
from features.team_form import get_team_form_features
from features.h2h_stats import get_h2h_features
from features.player_availability import get_missing_players_impact


def predict_upcoming_for_league(league_id, season, fixtures=None):
    """Predict upcoming fixtures for a league.

    If ``fixtures`` are provided they are used directly, otherwise the
    function fetches the upcoming fixtures via ``get_upcoming_fixtures``.
    The function attempts to load trained models from the ``models``
    directory.  When the models are missing, dummy predictions are
    generated so the frontend can still display results.
    """

    if fixtures is None:
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

    # Resolve model paths relative to repository root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    model_dir = os.path.join(base_dir, "models")

    use_dummy = False
    try:
        match_model = joblib.load(os.path.join(model_dir, "model_match_result.pkl"))
        home_corners_model = joblib.load(
            os.path.join(model_dir, "model_home_corners.pkl")
        )
        away_corners_model = joblib.load(
            os.path.join(model_dir, "model_away_corners.pkl")
        )
        expected_cols = joblib.load(os.path.join(model_dir, "training_columns.pkl"))
    except Exception as e:
        print(f"⚠️ Failed to load models: {e}. Using dummy predictions.")
        use_dummy = True
        expected_cols = []

    if not use_dummy:
        # Reindex with training columns, fill missing with 0
        df = df.reindex(columns=expected_cols, fill_value=0)

        # Predict using the trained models
        match_preds = match_model.predict(df)
        home_preds = home_corners_model.predict(df)
        away_preds = away_corners_model.predict(df)
    else:
        # Generate simple random predictions when models are unavailable
        match_preds = [random.choice(["home", "away", "draw"]) for _ in range(len(df))]
        home_preds = [random.randint(3, 10) for _ in range(len(df))]
        away_preds = [random.randint(3, 10) for _ in range(len(df))]

    # Combine results
    results = []
    for i in range(len(df)):
        results.append(
            {
                "home_team": display_data.iloc[i]["home_team"],
                "away_team": display_data.iloc[i]["away_team"],
                "result": match_preds[i],
                "home_corners": int(home_preds[i]),
                "away_corners": int(away_preds[i]),
            }
        )

    return results
