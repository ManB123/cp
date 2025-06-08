import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.client import get

res = get("leagues")  # no filters to fetch all leagues
for entry in res["response"]:
    league = entry["league"]
    country = entry["country"]["name"]
    name = league["name"]

    if country.lower() == "japan" and "j1" in name.lower():
        print(f"🔍 Found: {name} — ID = {league['id']}")