import json
import hashlib
import requests
from pathlib import Path

# ------------------ Конфігурація ------------------
MAL_URL = "https://raw.githubusercontent.com/Fribb/anime-lists/master/indices/mal_index.json"
TMDB_URL = "https://raw.githubusercontent.com/Fribb/anime-lists/master/indices/themoviedb_index.json"

ANIME_DIR = Path("anime")
MAP_FILE = ANIME_DIR / "map.json"
HASH_FILE = ANIME_DIR / "map.json.hash"
# --------------------------------------------------


def fetch(url: str):
    """Завантажує URL, повертає (текст, розпарсений JSON)."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text, resp.json()


def main():
    ANIME_DIR.mkdir(exist_ok=True)

    print("📡 Fetching Fribb indices...")
    mal_text, mal_index = fetch(MAL_URL)
    tmdb_text, tmdb_index = fetch(TMDB_URL)

    # Хеш від вмісту обох вихідних файлів — щоб не робити зайву роботу,
    # коли дані в джерелі не змінилися.
    new_hash = hashlib.sha256((mal_text + tmdb_text).encode("utf-8")).hexdigest()
    if HASH_FILE.exists() and MAP_FILE.exists():
        if HASH_FILE.read_text().strip() == new_hash:
            print("✅ Source unchanged – map.json is already up to date.")
            return

    print("🔄 Building tmdb → mal map...")

    # Обидва індекси посилаються на позиції в одному й тому ж anime-list-full.json.
    # Будуємо pos → mal_id, потім через нього резолвимо mal для кожного tmdb.
    pos2mal = {}
    for mal_id, obj in mal_index.items():
        for pos in obj.get("anime-list", []):
            pos2mal[pos] = int(mal_id)

    out = {}  # { "movie" | "tv": { "<tmdb_id>": [mal_id, ...] } }
    for key, obj in tmdb_index.items():
        mtype, _, tid = key.partition(":")  # напр. "tv:26209" -> ("tv", "26209")
        if not tid:
            continue
        mal_ids = sorted({pos2mal[p] for p in obj.get("anime-list", []) if p in pos2mal})
        if mal_ids:
            out.setdefault(mtype, {})[tid] = mal_ids

    # Впорядковуємо ключі за зростанням числового tmdb id — стабільні diff'и та кращий gzip.
    ordered = {
        mtype: {tid: out[mtype][tid] for tid in sorted(out[mtype], key=int)}
        for mtype in sorted(out)
    }

    # Мініфікований JSON (без пробілів) — мінімальний розмір файлу.
    with open(MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(ordered, f, ensure_ascii=False, separators=(",", ":"))

    with open(HASH_FILE, "w", encoding="utf-8") as f:
        f.write(new_hash)

    total_pairs = sum(len(mals) for m in ordered.values() for mals in m.values())
    counts = ", ".join(f"{mtype}: {len(ids)}" for mtype, ids in ordered.items())
    print(f"✅ Done. {counts}; total tmdb→mal pairs: {total_pairs}")
    print(f"📦 {MAP_FILE} size: {MAP_FILE.stat().st_size} bytes")


if __name__ == "__main__":
    main()
