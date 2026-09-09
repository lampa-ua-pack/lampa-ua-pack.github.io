import gzip
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

# ------------------ Конфігурація ------------------
# anibridge/anibridge-mappings — основне джерело. Мерджить 7 upstream'ів (anime-lists,
# AnimeAggregations, shinkro-mapping, QLever, живі API AniList/MAL/TMDB/TVDB) + ручні
# правки, тримає посезонні скоупи `tmdb_show:<id>:s<N>` та `tmdb_movie:<id>` окремо.
# Тег `v3` пінимо навмисне: мажор ламає схему, і ми хочемо впасти явно, а не тихо.
ANIBRIDGE_URL = "https://github.com/anibridge/anibridge-mappings/releases/download/v3/mappings.min.json"

# nattadasu/animeApi — заповнювач прогалин. Його upstream (manami-project) архівований
# з 2026-07-04, тож джерело поволі замирає, але ~800 tmdb id є тільки тут.
ANIMEAPI_URL = "https://raw.githubusercontent.com/nattadasu/animeApi/v3/database/animeapi.json"

SOURCES = (ANIBRIDGE_URL, ANIMEAPI_URL)

ANIME_DIR = Path("anime")
MAP_FILE = ANIME_DIR / "map.json"
HASH_FILE = ANIME_DIR / "map.json.hash"
ETAG_FILE = ANIME_DIR / "map.json.etag"

# Наскільки допустимо просісти по кількості tmdb id проти вже опублікованої карти.
# Файл лежить у GitHub Pages, тож «джерело віддало пів-файл» має бути червоним Action'ом,
# а не тихою регресією для клієнтів.
SHRINK_LIMIT = 0.05

UA = "lampa-ua-pack-anime-map"
# --------------------------------------------------


def _request(url: str, method: str):
    return urllib.request.Request(
        url, method=method, headers={"User-Agent": UA, "Accept-Encoding": "gzip"}
    )


def etag(url: str) -> str:
    """HEAD-запит: тег версії без завантаження тіла (~100 мс замість секунд)."""
    with urllib.request.urlopen(_request(url, "HEAD"), timeout=30) as resp:
        return resp.headers.get("ETag", "")


def fetch(url: str) -> bytes:
    """Завантажує URL, повертає байти (розпаковані, якщо прийшло gzip'ом).
    Байти, не str: json.loads їх їсть напряму, а sha256 по них вдвічі швидший."""
    with urllib.request.urlopen(_request(url, "GET"), timeout=60) as resp:
        body = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            body = gzip.decompress(body)
    return body


def sources_unchanged() -> bool:
    """True, якщо обидва джерела віддають ті самі ETag'и, що й на минулій збірці.
    Тоді качати 12 МБ немає сенсу."""
    # Всі три файли мусять бути на місці: якщо якийсь загубився, треба пройти
    # повний шлях і відновити його, а не зрізати по ETag'у назавжди.
    if not all(f.exists() for f in (MAP_FILE, HASH_FILE, ETAG_FILE)):
        return False
    try:
        seen = json.loads(ETAG_FILE.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return False
    if not all(seen.get(url) for url in SOURCES):
        return False
    return all(etag(url) == seen[url] for url in SOURCES)


def parse_anibridge(mappings, out):
    """tmdb_movie:<id> / tmdb_show:<id>:s<N> -> mal:<id>. Спешли (s0) пропускаємо:
    у плоскому масиві вони домішують OVA до сезонів і ламають позиційне вгадування."""
    for key, targets in mappings.items():
        parts = key.split(":")
        if parts[0] == "tmdb_movie":
            sect, tid = "movie", parts[1]
        elif parts[0] == "tmdb_show":
            if parts[2] == "s0":
                continue
            sect, tid = "tv", parts[1]
        else:
            continue  # інші провайдери і "$meta"

        for tgt, ranges in targets.items():
            if not tgt.startswith("mal:"):
                continue
            # Схема допускає null як «явно не мапиться».
            if ranges and all(v is None for v in ranges.values()):
                continue
            out[sect].setdefault(tid, set()).add(int(tgt.split(":")[1]))


def parse_animeapi(records, out):
    """Додає тільки ті tmdb id, яких anibridge не дав — щоб не забруднювати
    валідовані набори mal. Повертає кількість дозаповнених пар."""
    primary = {sect: set(ids) for sect, ids in out.items()}
    added = 0
    for rec in records:
        tid = rec.get("themoviedb")
        mtype = rec.get("themoviedb_type")  # "movie" | "tv" | None
        mal = rec.get("myanimelist")
        if tid is None or mal is None or mtype not in ("movie", "tv"):
            continue
        if str(tid) in primary[mtype]:
            continue
        out[mtype].setdefault(str(tid), set()).add(int(mal))
        added += 1
    return added


def main():
    ANIME_DIR.mkdir(exist_ok=True)

    if sources_unchanged():
        print("✅ Sources unchanged (ETag) – map.json is already up to date.")
        return

    print("📡 Fetching anibridge mappings...")
    ab_etag = etag(ANIBRIDGE_URL)
    ab_body = fetch(ANIBRIDGE_URL)
    ab_data = json.loads(ab_body)
    meta = ab_data.get("$meta", {})
    print(f"   schema {meta.get('schema_version')}, generated {meta.get('generated_on')}")

    print("📡 Fetching animeApi database...")
    api_etag = etag(ANIMEAPI_URL)
    api_body = fetch(ANIMEAPI_URL)
    api_records = json.loads(api_body)

    # ETag змінюється і при перезаливці ідентичного вмісту (anibridge перебудовується
    # щодня), тож хеш вмісту — друга лінія захисту від зайвого коміту.
    new_hash = hashlib.sha256(ab_body + api_body).hexdigest()
    etags = {ANIBRIDGE_URL: ab_etag, ANIMEAPI_URL: api_etag}
    if HASH_FILE.exists() and MAP_FILE.exists():
        if HASH_FILE.read_text().strip() == new_hash:
            print("✅ Source content unchanged – refreshing ETags only.")
            ETAG_FILE.write_text(json.dumps(etags, indent=1), encoding="utf-8")
            return

    print("🔄 Building tmdb → mal map...")

    out = {"movie": {}, "tv": {}}  # { "movie" | "tv": { "<tmdb_id>": {mal_id, ...} } }
    parse_anibridge(ab_data, out)
    primary_counts = {sect: len(ids) for sect, ids in out.items()}
    filled = parse_animeapi(api_records, out)

    # set -> відсортований список; ключі за зростанням числового tmdb id
    # (стабільні diff'и та кращий gzip). Порожні секції прибираємо.
    ordered = {
        sect: {tid: sorted(out[sect][tid]) for tid in sorted(out[sect], key=int)}
        for sect in sorted(out)
        if out[sect]
    }

    # Санітарна перевірка: не перезаписувати опубліковану карту, якщо вона різко просіла.
    if MAP_FILE.exists():
        prev = json.loads(MAP_FILE.read_text(encoding="utf-8"))
        for sect, prev_ids in prev.items():
            now = len(ordered.get(sect, {}))
            if prev_ids and now < len(prev_ids) * (1 - SHRINK_LIMIT):
                sys.exit(f"❌ Refusing to write: {sect} shrank {len(prev_ids)} → {now} "
                         f"(> {SHRINK_LIMIT:.0%}). Source likely broken or schema changed.")

    # Мініфікований JSON (без пробілів) — мінімальний розмір файлу.
    with open(MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(ordered, f, ensure_ascii=False, separators=(",", ":"))

    HASH_FILE.write_text(new_hash, encoding="utf-8")
    ETAG_FILE.write_text(json.dumps(etags, indent=1), encoding="utf-8")

    total_pairs = sum(len(mals) for sect in ordered.values() for mals in sect.values())
    counts = ", ".join(
        f"{sect}: {len(ids)} (anibridge {primary_counts[sect]})"
        for sect, ids in ordered.items()
    )
    print(f"✅ Done. {counts}; total tmdb→mal pairs: {total_pairs}")
    print(f"🩹 Filled from animeApi fallback: {filled} pairs")
    print(f"📦 {MAP_FILE} size: {MAP_FILE.stat().st_size} bytes")


if __name__ == "__main__":
    main()
