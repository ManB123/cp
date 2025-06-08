import sys
import os
import streamlit as st
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.leagues import get_supported_leagues
from api.fixtures import get_upcoming_fixtures
from scripts.predict_upcoming import predict_upcoming_for_league

st.set_page_config(page_title="Corner Predictor", layout="centered")
st.title("⚽ Corner Predictor")

# 1. Select League
leagues = get_supported_leagues()
league_names = [league["name"] for league in leagues]
selected_name = st.selectbox("Choose a League", league_names)
selected_league = next(league for league in leagues if league["name"] == selected_name)

# Track loaded fixtures across runs
if "loaded_fixtures" not in st.session_state:
    st.session_state.loaded_fixtures = []

# 2. Load Fixtures
if st.button("🔄Load Fixtures"):
    fixtures = get_upcoming_fixtures(selected_league["id"], selected_league["season"])
    st.session_state.loaded_fixtures = fixtures  # Save in session state
    if fixtures:
        st.success(f"✅ Found {len(fixtures)} upcoming fixtures")
        for f in fixtures:
            home = f["teams"]["home"]["name"]
            away = f["teams"]["away"]["name"]
            date = f["fixture"]["date"][:10]
            st.markdown(f"- 📅 `{date}` — **{home} vs {away}**")
    else:
        st.warning("⚠️ No fixtures found.")

# 3. Predict Results and Corners
if st.session_state.loaded_fixtures and st.button("🔮 Predict Results"):
    with st.spinner("Predicting results and corners..."):
        results = predict_upcoming_for_league(selected_league["id"], selected_league["season"])
        if results:
            st.success("✅ Predictions complete")
            st.subheader("📊 Match Predictions")
            for r in results:
                st.markdown(f"**{r['home_team']} vs {r['away_team']}**")
                st.markdown(f"- 🏁 Result: `{r['result']}`")
                st.markdown(f"- 🥅 Corners: `{r['home_corners']} - {r['away_corners']}`")
                st.markdown("---")
        else:
            st.warning("⚠️ No predictions available. Possibly missing data.")
