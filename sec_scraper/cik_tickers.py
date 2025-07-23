import os
import json
import requests
from pathlib import Path


def update_ticker_mapping(cache_path=None):
    """
    Fetch the latest ticker–CIK mapping from the SEC and save it to a local JSON file.
    """
    if cache_path is None:
        cache_path = os.getenv("TICKER_CIK_CACHE")

    cache_path = Path(cache_path)

    url = "https://www.sec.gov/files/company_tickers_exchange.json"
    headers = {
        "User-Agent": os.getenv("WEB_USER_AGENT"),
        "Accept": "application/json",
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    mapping = {
        f"{item[3].upper() if item[3] else 'None'}:{item[2]}": item[0]
        for item in data["data"]
    }

    cache_path.parent.mkdir(parents=True, exist_ok=True)

    with open(cache_path, "w") as f:
        json.dump(mapping, f)

    return mapping


def load_ticker_mapping(cache_path=os.getenv("TICKER_CIK_CACHE")):
    """
    Load the ticker–CIK mapping from a local JSON cache file.
    """
    if cache_path is None:
        cache_path = os.getenv("TICKER_CIK_CACHE", "ticker_cik.json")

    if not os.path.isabs(cache_path):
        parent_dir = os.path.dirname(os.getcwd())
        cache_path = os.path.join(parent_dir, cache_path)

    with open(cache_path, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    print(load_ticker_mapping())
