import requests
import yaml

# Load config from config.yaml
with open("config.yaml") as f:
    config = yaml.safe_load(f)

API_KEY = config["api_football"]["key"]

HEADERS = {
    "x-apisports-key": API_KEY  # ✅ Official header for API-Football (not RapidAPI)
}

BASE_URL = "https://v3.football.api-sports.io"

def get(endpoint, params=None):
    print(f"🛠️ Loaded API key: {API_KEY}")

    url = f"{BASE_URL}/{endpoint}"
    print(f"📡 GET {url} with params={params}")  # Optional: debug line
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()
