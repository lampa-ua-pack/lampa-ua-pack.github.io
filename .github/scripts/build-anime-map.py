import json
import hashlib
import requests
from pathlib import Path

# ------------------ Конфігурація ------------------
# nattadasu/animeApi — пласка база (~40k записів). На відміну від Fribb, тримає
# themoviedb + themoviedb_type ("movie"/"tv") окремими полями, тож фільми більше
# не змішуються з TV-серіалами під одним tmdb id.
SRC_URL = "https://raw.githubusercontent.com/nattadasu/animeApi/v3/database/animeapi.json"

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

    print("📡 Fetching animeApi database...")
    src_text, records = fetch(SRC_URL)

    # Хеш від вмісту вихідного файлу — щоб не робити зайву роботу,
    # коли дані в джерелі не змінилися.
    new_hash = hashlib.sha256(src_text.encode("utf-8")).hexdigest()
    if HASH_FILE.exists() and MAP_FILE.exists():
        if HASH_FILE.read_text().strip() == new_hash:
            print("✅ Source unchanged – map.json is already up to date.")
            return

    print("🔄 Building tmdb → mal map...")

    # Кожен запис уже містить themoviedb + themoviedb_type + myanimelist.
    # Один прохід: групуємо mal id за (тип, tmdb id). Кілька mal на один tmdb
    # (напр. сезони серіалу) складаються в set — так само, як робив Fribb-білд.
    out = {"movie": {}, "tv": {}}  # { "movie" | "tv": { "<tmdb_id>": {mal_id, ...} } }
    for rec in records:
        tid = rec.get("themoviedb")
        mtype = rec.get("themoviedb_type")  # "movie" | "tv" | None
        mal = rec.get("myanimelist")
        if tid is None or mal is None or mtype not in ("movie", "tv"):
            continue
        out[mtype].setdefault(str(tid), set()).add(int(mal))

    # set -> відсортований список; порожні секції прибираємо.
    out = {
        mtype: {tid: sorted(mals) for tid, mals in buckets.items()}
        for mtype, buckets in out.items()
        if buckets
    }

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
