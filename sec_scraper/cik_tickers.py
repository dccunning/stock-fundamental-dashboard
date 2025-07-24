import os
import json
import requests
from pathlib import Path


def update_ticker_mapping(cache_filename=os.getenv("TICKER_CIK_CACHE"), user_agent=os.getenv("WEB_USER_AGENT")):
    """
    Fetch the latest ticker–CIK mapping from the SEC and save it to a local JSON file.

    :param cache_filename: Filename of the local json
    :param user_agent: User Agent to access the SEC website
    :return: Dict of updated ticker–CIK mappings
    """
    if not cache_filename:
        raise ValueError("cache_filename env variable is not set")

    if not user_agent:
        raise ValueError("WEB_USER_AGENT env variable is not set")

    current_dir = Path(__file__).resolve().parent.parent
    cache_path = current_dir / cache_filename

    url = "https://www.sec.gov/files/company_tickers_exchange.json"
    headers = {
        "User-Agent": user_agent,
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


def load_ticker_mapping(cache_filename=os.getenv("TICKER_CIK_CACHE")):
    """
    Load the ticker–CIK mapping from a local JSON cache file.

    :param cache_filename: Filename of the local JSON cache
    :return: Dict of ticker–CIK mappings
    """
    if not cache_filename:
        raise ValueError("TICKER_CIK_CACHE env variable is not set")

    current_dir = Path(__file__).resolve().parent.parent
    cache_path = current_dir / cache_filename

    with open(cache_path, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    update_ticker_mapping("data/ticker_cik_cache.json")
    print("Ticker mappings updated")
