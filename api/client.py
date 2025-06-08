import requests
import yaml
from requests.exceptions import RequestException

with open("config.yaml") as f:
    config = yaml.safe_load(f)

API_KEY = config["api_football"]["key"]
API_HOST = config["api_football"]["host"]

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

BASE_URL = f"https://{API_HOST}"

def get(endpoint, params=None, retries=3, timeout=30):
    """Perform a GET request with basic retry logic."""
    url = f"{BASE_URL}/{endpoint}"
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            if attempt == retries - 1:
                raise
            print(f"Request failed ({e}), retrying... ({attempt + 1}/{retries})")
