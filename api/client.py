import requests
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

API_KEY = config["api_football"]["key"]
API_HOST = config["api_football"]["host"]

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

BASE_URL = f"https://{API_HOST}"

def get(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()
