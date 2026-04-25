import os
import json
import hashlib
import copy
import requests
import time
from pathlib import Path

# ------------------ Конфігурація ------------------
CUB_URL = "https://cub.rip/api/feed/all"
NEWS_DIR = Path("news")
DATA_FILE = NEWS_DIR / "data.json"
DATA_UK_FILE = NEWS_DIR / "data.uk.json"
HASH_FILE = NEWS_DIR / "data.hash"
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise ValueError("❌ TMDB_API_KEY environment variable not set")

TMDB_BASE_URL = "https://api.themoviedb.org/3"
LANGUAGE_UK = "uk"
REQUEST_DELAY = 0.1
# --------------------------------------------------

def get_tmdb_data(tmdb_id: int, media_type: str):
    endpoint = f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}"
    params = {"api_key": TMDB_API_KEY, "language": LANGUAGE_UK}
    try:
        resp = requests.get(endpoint, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"⚠️ TMDb {media_type} {tmdb_id}: {resp.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ TMDb request error: {e}")
        return None

def get_tmdb_episode(tmdb_id: int, season: int, episode: int):
    endpoint = f"{TMDB_BASE_URL}/tv/{tmdb_id}/season/{season}/episode/{episode}"
    params = {"api_key": TMDB_API_KEY, "language": LANGUAGE_UK}
    try:
        resp = requests.get(endpoint, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"⚠️ Episode S{season}E{episode}: {resp.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Episode request error: {e}")
        return None

def localize_item(item: dict) -> dict:
    """Повертає копію item з українськими текстовими полями (замінює data)"""
    new_item = copy.deepcopy(item)
    tmdb_id = new_item.get("card_id")
    if not tmdb_id:
        return new_item

    card_type = new_item.get("card_type")
    media_type = "tv" if card_type == "tv" else "movie"

    # Локалізація основного об'єкта data
    if "data" in new_item:
        data_obj = new_item["data"]
        tmdb_info = get_tmdb_data(tmdb_id, media_type)
        if tmdb_info:
            if media_type == "movie":
                if tmdb_info.get("title"):
                    data_obj["title"] = tmdb_info["title"]
                if tmdb_info.get("original_title"):
                    data_obj["original_title"] = tmdb_info["original_title"]
                if tmdb_info.get("overview"):
                    data_obj["overview"] = tmdb_info["overview"]
                # Для сумісності, якщо є поле name
                if "name" in data_obj and tmdb_info.get("title"):
                    data_obj["name"] = tmdb_info["title"]
                # Оновлюємо назву в масиві names, якщо він є
                if "names" in data_obj and isinstance(data_obj["names"], list) and tmdb_info.get("title"):
                    if tmdb_info["title"] not in data_obj["names"]:
                        data_obj["names"].insert(0, tmdb_info["title"])
            else:  # tv
                if tmdb_info.get("name"):
                    data_obj["name"] = tmdb_info["name"]
                if tmdb_info.get("original_name"):
                    data_obj["original_name"] = tmdb_info["original_name"]
                if tmdb_info.get("overview"):
                    data_obj["overview"] = tmdb_info["overview"]
                if "names" in data_obj and isinstance(data_obj["names"], list) and tmdb_info.get("name"):
                    if tmdb_info["name"] not in data_obj["names"]:
                        data_obj["names"].insert(0, tmdb_info["name"])

            # --- Локалізація жанрів ---
            if "genres" in tmdb_info and isinstance(tmdb_info["genres"], list):
                genre_names = [g["name"] for g in tmdb_info["genres"] if "name" in g]
                if genre_names:
                    data_obj["genres"] = genre_names

            # --- Локалізація країн виробництва ---
            if "production_countries" in tmdb_info and isinstance(tmdb_info["production_countries"], list):
                country_names = [c["name"] for c in tmdb_info["production_countries"] if "name" in c]
                if country_names:
                    data_obj["countries"] = country_names

        # Локалізація епізоду, якщо є
        if new_item.get("type") == "episode" and "episode" in data_obj:
            ep_data = data_obj["episode"]
            season = ep_data.get("season_number")
            episode_num = ep_data.get("episode_number")
            if season and episode_num:
                tmdb_ep = get_tmdb_episode(tmdb_id, season, episode_num)
                if tmdb_ep:
                    if tmdb_ep.get("name"):
                        ep_data["name"] = tmdb_ep["name"]
                    if tmdb_ep.get("overview"):
                        ep_data["overview"] = tmdb_ep["overview"]
                    if tmdb_ep.get("runtime"):
                        ep_data["runtime"] = tmdb_ep["runtime"]
                    if tmdb_ep.get("still_path"):
                        ep_data["still_path"] = tmdb_ep["still_path"]
                    if tmdb_ep.get("air_date"):
                        ep_data["air_date"] = tmdb_ep["air_date"]
                    if tmdb_ep.get("vote_average") is not None:
                        ep_data["vote_average"] = tmdb_ep["vote_average"]

    return new_item

def main():
    NEWS_DIR.mkdir(exist_ok=True)

    print("📡 Fetching from cub.rip...")
    try:
        resp = requests.get(CUB_URL, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to fetch cub.rip: {e}")
        return

    original_text = resp.text
    original_data = resp.json()

    new_hash = hashlib.sha256(original_text.encode('utf-8')).hexdigest()

    old_hash = None
    if HASH_FILE.exists():
        old_hash = HASH_FILE.read_text().strip()

    # Завжди зберігаємо оригінальний data.json (без змін)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(original_data, f, ensure_ascii=False, indent=2)

    # Якщо хеш не змінився, не оновлюємо data.uk.json (економимо запити до TMDb)
    if old_hash == new_hash and DATA_UK_FILE.exists():
        print("✅ Hash unchanged – Ukrainian file already up to date.")
        # Оновимо хеш-файл (він міг бути втрачений)
        with open(HASH_FILE, "w", encoding="utf-8") as f:
            f.write(new_hash)
        return

    print("🔄 Hash changed – generating Ukrainian version...")

    # Створюємо українську версію
    uk_data = copy.deepcopy(original_data)
    if "result" in uk_data:
        new_results = []
        total = len(uk_data["result"])
        for idx, item in enumerate(uk_data["result"], 1):
            print(f"🔄 Processing {idx}/{total} (card_id: {item.get('card_id')})")
            localized_item = localize_item(item)
            new_results.append(localized_item)
            time.sleep(REQUEST_DELAY)  # дотримуємось лімітів TMDb
        uk_data["result"] = new_results

    # Зберігаємо українську версію
    with open(DATA_UK_FILE, "w", encoding="utf-8") as f:
        json.dump(uk_data, f, ensure_ascii=False, indent=2)

    # Зберігаємо новий хеш
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        f.write(new_hash)

    print("✅ Done. Original data saved to data.json, Ukrainian version to data.uk.json")

if __name__ == "__main__":
    main()