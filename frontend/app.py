import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from api.leagues import get_supported_leagues
from api.fixtures import get_upcoming_fixtures

st.title("⚽ Corner Predictor - Select League")

# 1. Select League
leagues = get_supported_leagues()
league_names = [league["name"] for league in leagues]
selected_name = st.selectbox("Choose a League", league_names)

selected_league = next(league for league in leagues if league["name"] == selected_name)

# 2. Load Fixtures
if st.button("Load Fixtures"):
    fixtures = get_upcoming_fixtures(selected_league["id"], selected_league["season"])
    if fixtures:
        st.success(f"Found {len(fixtures)} upcoming fixtures!")
        for f in fixtures:
            home = f["teams"]["home"]["name"]
            away = f["teams"]["away"]["name"]
            date = f["fixture"]["date"]
            st.markdown(f"- **{home} vs {away}** on `{date}`")
    else:
        st.warning("No fixtures found.")
