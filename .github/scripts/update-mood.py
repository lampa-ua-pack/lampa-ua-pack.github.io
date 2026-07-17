# -*- coding: utf-8 -*-
"""
Генератор тематичних підбірок «MOOD».

Флоу для кожної з 14 тем (див. mood_themes.py):
  1. OpenCode API (OpenAI-сумісний chat/completions) → список назв тайтлів
  2. TMDB /search/{movie|tv} → резолв назв у реальні ID (fuzzy: звірка title + year)
     + /discover як додатковий пул кандидатів (змішаний пул)
  3. детерміновані фільтри анти-слопу (vote_count, збіг жанру, дедуп, ліміт очевидного)
  4. стабілізація (bounded churn відносно попереднього файлу)
  5. гідрація фінальних ~20 тайтлів мовами uk та ru
  6. запис mood/{slug}.uk.json та mood/{slug}.ru.json
Наприкінці — mood/index.json (маніфест). Збій однієї теми не рушить увесь ран:
її попередній файл лишається, у маніфесті ставиться "stale": true.

ENV:
  TMDB_API_KEY      — обов'язковий
  OPENCODE_URL      — базовий URL або повний endpoint chat/completions
  OPENCODE_MODEL    — ім'я моделі
  OPENCODE_TOKEN    — bearer-токен
  MOOD_ONLY         — (опц.) кома-список slug для локального прогону (напр. "laugh,cry")
"""

import os
import re
import json
import time
import math
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests

from mood_themes import THEMES

# ------------------ Конфігурація ------------------
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise ValueError("❌ TMDB_API_KEY environment variable not set")

OPENCODE_URL = os.environ.get("OPENCODE_URL", "").strip()
OPENCODE_MODEL = os.environ.get("OPENCODE_MODEL", "").strip()
OPENCODE_TOKEN = os.environ.get("OPENCODE_TOKEN", "").strip()

TMDB_BASE_URL = "https://api.themoviedb.org/3"
MOOD_DIR = Path("mood")
REQUEST_DELAY = 0.1          # пауза між запитами до TMDb
TIMEOUT = 15

TARGET_COUNT = 20            # тайтлів на тему
AI_REQUEST_COUNT = 30        # скільки назв просимо в ІІ (із запасом на фільтри)
VOTE_COUNT_MIN = 150         # поріг популярності (відсікає мотлох/неіснуюче)
OBVIOUS_VOTE_COUNT = 15000   # «занадто очевидні» блокбастери
OBVIOUS_MAX = 8              # не більше стількох «очевидних» на тему
MAX_CHANGE = 5               # скільки позицій дозволено міняти за ран (стабільність)

MOOD_ONLY = [s.strip() for s in os.environ.get("MOOD_ONLY", "").split(",") if s.strip()]

session = requests.Session()


# ------------------ Утиліти ------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_title(s: str) -> str:
    """Нормалізація назви для fuzzy-звірки: нижній регістр, без пунктуації/діакритики."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return s.strip()


def year_of(item: dict) -> int:
    date = item.get("release_date") or item.get("first_air_date") or ""
    if len(date) >= 4 and date[:4].isdigit():
        return int(date[:4])
    return 0


def item_title(item: dict) -> str:
    return item.get("title") or item.get("name") or ""


def item_original_title(item: dict) -> str:
    return item.get("original_title") or item.get("original_name") or ""


# ------------------ OpenCode (ІІ) ------------------
def opencode_endpoint() -> str:
    """Дозволяє задавати або базовий URL, або повний endpoint chat/completions."""
    url = OPENCODE_URL.rstrip("/")
    if url.endswith("/chat/completions") or url.endswith("/completions"):
        return url
    return url + "/chat/completions"


def ai_suggest_titles(theme: dict) -> list:
    """
    Повертає список кандидатів [{title, year, media_type}] від ІІ.
    Якщо OpenCode не налаштований або відповів помилкою — повертає [] (спрацює discover-пул).
    """
    if not (OPENCODE_URL and OPENCODE_MODEL and OPENCODE_TOKEN):
        print("⚠️ OpenCode not configured — relying on TMDB discover pool only")
        return []

    system_prompt = (
        "You are a seasoned film and TV curator with broad, non-mainstream taste. "
        "You return ONLY a JSON array, no prose, no markdown fences. "
        "Each element is an object with keys: "
        '"title" (original English or international title), '
        '"year" (release year as integer), '
        '"media_type" ("movie" or "tv"). '
        "Favor diversity across decades and countries. Avoid the same tired top-list "
        "picks everyone names first; include lesser-known gems that still fit the mood."
    )
    user_prompt = (
        f"Theme: {theme['title_ru']}\n"
        f"Description: {theme['prompt']}\n\n"
        f"Return exactly {AI_REQUEST_COUNT} titles that genuinely fit this mood. "
        f"Mix movies and TV series where appropriate. JSON array only."
    )

    payload = {
        "model": OPENCODE_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "seed": 42,
    }
    headers = {
        "Authorization": f"Bearer {OPENCODE_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        resp = session.post(opencode_endpoint(), json=payload, headers=headers, timeout=60)
        if resp.status_code != 200:
            print(f"⚠️ OpenCode {resp.status_code}: {resp.text[:200]}")
            return []
        content = resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"⚠️ OpenCode request error: {e}")
        return []

    return parse_ai_titles(content)


def parse_ai_titles(content: str) -> list:
    """Витягує JSON-масив із відповіді ІІ, толерантно до ```json fences та зайвого тексту."""
    if not content:
        return []
    text = content.strip()
    # прибрати markdown-fences
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    # взяти першу [...] групу, якщо навколо є зайвий текст
    if not text.startswith("["):
        m = re.search(r"\[.*\]", text, re.DOTALL)
        if m:
            text = m.group(0)
    try:
        data = json.loads(text)
    except Exception as e:
        print(f"⚠️ Failed to parse AI JSON: {e}")
        return []

    out = []
    for el in data if isinstance(data, list) else []:
        if not isinstance(el, dict):
            continue
        title = str(el.get("title", "")).strip()
        if not title:
            continue
        mt = str(el.get("media_type", "movie")).strip().lower()
        if mt not in ("movie", "tv"):
            mt = "movie"
        year = el.get("year")
        try:
            year = int(year)
        except (TypeError, ValueError):
            year = 0
        out.append({"title": title, "year": year, "media_type": mt})
    return out


# ------------------ TMDB ------------------
def tmdb_get(path: str, params: dict):
    params = dict(params or {})
    params["api_key"] = TMDB_API_KEY
    try:
        resp = session.get(f"{TMDB_BASE_URL}/{path}", params=params, timeout=TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
        print(f"⚠️ TMDb {path}: {resp.status_code}")
    except Exception as e:
        print(f"⚠️ TMDb request error ({path}): {e}")
    return None


def tmdb_search(name: str, year: int, media_type: str):
    """Резолв назви у TMDB-кандидата з fuzzy-звіркою. Повертає нормалізований candidate або None."""
    params = {"query": name, "include_adult": "false", "language": "en-US"}
    if year:
        params["year" if media_type == "movie" else "first_air_date_year"] = year
    data = tmdb_get(f"search/{media_type}", params)
    time.sleep(REQUEST_DELAY)
    if not data or not data.get("results"):
        return None

    want = normalize_title(name)
    best = None
    for res in data["results"][:5]:
        cand_title = normalize_title(item_title(res))
        cand_orig = normalize_title(item_original_title(res))
        title_match = want and (want == cand_title or want == cand_orig
                                or want in cand_title or cand_title in want)
        if not title_match:
            continue
        if year:
            ry = year_of(res)
            if ry and abs(ry - year) > 1:
                continue
        best = res
        break

    if best is None:
        return None
    return to_candidate(best, media_type)


def to_candidate(res: dict, media_type: str) -> dict:
    return {
        "id": res.get("id"),
        "media_type": media_type,
        "genre_ids": res.get("genre_ids") or [],
        "vote_average": res.get("vote_average") or 0,
        "vote_count": res.get("vote_count") or 0,
        "year": year_of(res),
    }


def tmdb_discover(theme: dict) -> list:
    """Fallback/додатковий пул кандидатів через /discover для movie і tv."""
    candidates = []
    common = {
        "sort_by": "vote_count.desc",
        "vote_count.gte": VOTE_COUNT_MIN,
        "include_adult": "false",
        "language": "en-US",
        "page": 1,
    }
    max_year = theme.get("max_year")

    if theme.get("discover_movie"):
        params = dict(common)
        params["with_genres"] = "|".join(str(g) for g in theme["discover_movie"])
        if max_year:
            params["primary_release_date.lte"] = f"{max_year}-12-31"
        data = tmdb_get("discover/movie", params)
        time.sleep(REQUEST_DELAY)
        for res in (data or {}).get("results", []):
            candidates.append(to_candidate(res, "movie"))

    if theme.get("discover_tv"):
        params = dict(common)
        params["with_genres"] = "|".join(str(g) for g in theme["discover_tv"])
        if max_year:
            params["first_air_date.lte"] = f"{max_year}-12-31"
        data = tmdb_get("discover/tv", params)
        time.sleep(REQUEST_DELAY)
        for res in (data or {}).get("results", []):
            candidates.append(to_candidate(res, "tv"))

    return candidates


def tmdb_detail(tmdb_id: int, media_type: str, language: str):
    """Локалізована картка для фінальної гідрації."""
    data = tmdb_get(f"{media_type}/{tmdb_id}", {"language": language})
    time.sleep(REQUEST_DELAY)
    return data


def build_item(tmdb_id: int, media_type: str, language: str):
    """Гідрує один тайтл у форматі discovery-респонсу для заданої мови."""
    d = tmdb_detail(tmdb_id, media_type, language)
    if not d:
        return None
    genre_ids = [g["id"] for g in d.get("genres", []) if "id" in g]
    return {
        "id": d.get("id"),
        "media_type": media_type,
        "title": item_title(d),
        "original_title": item_original_title(d),
        "overview": d.get("overview") or "",
        "poster_path": d.get("poster_path"),
        "backdrop_path": d.get("backdrop_path"),
        "genre_ids": genre_ids,
        "vote_average": d.get("vote_average") or 0,
        "vote_count": d.get("vote_count") or 0,
        "release_date": d.get("release_date") or d.get("first_air_date") or "",
    }


# ------------------ Фільтри / ранжування / стабільність ------------------
def passes_filters(cand: dict, theme: dict) -> bool:
    if cand.get("id") is None:
        return False
    if (cand.get("vote_count") or 0) < VOTE_COUNT_MIN:
        return False
    genre_ids = set(cand.get("genre_ids") or [])
    if not genre_ids & theme["genre_whitelist"]:
        return False
    max_year = theme.get("max_year")
    if max_year and cand.get("year") and cand["year"] > max_year:
        return False
    return True


def rank_key(cand: dict) -> float:
    """Скор: якість × log(популярність) — тягне добротне, але не порожнє."""
    va = cand.get("vote_average") or 0
    vc = cand.get("vote_count") or 1
    return va * math.log10(vc + 10)


def cap_obvious(ranked: list) -> list:
    """Обмежує частку ультра-популярних блокбастерів заради різноманіття."""
    result, obvious = [], 0
    for c in ranked:
        if (c.get("vote_count") or 0) >= OBVIOUS_VOTE_COUNT:
            if obvious >= OBVIOUS_MAX:
                continue
            obvious += 1
        result.append(c)
    return result


def stabilize(prev_keys: list, new_ranked_keys: list, target: int, max_change: int) -> list:
    """Bounded churn: тримаємо попередні валідні позиції, міняємо не більше max_change за ран."""
    if not prev_keys:
        return new_ranked_keys[:target]
    new_set = set(new_ranked_keys)
    prev_set = set(prev_keys)
    kept = [k for k in prev_keys if k in new_set]          # попередні, що досі валідні
    fresh = [k for k in new_ranked_keys if k not in prev_set]
    n_add = min(max_change, len(fresh), target)
    result = kept[: target - n_add] + fresh[:n_add]
    for k in new_ranked_keys:                               # добір, якщо коротко
        if len(result) >= target:
            break
        if k not in result:
            result.append(k)
    return result[:target]


# ------------------ Файли ------------------
def read_prev_keys(slug: str) -> list:
    """Ключі (media_type, id) із попереднього uk-файлу теми, у збереженому порядку."""
    path = MOOD_DIR / f"{slug}.uk.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [(it.get("media_type"), it.get("id")) for it in data.get("items", [])
                if it.get("id") is not None]
    except Exception:
        return []


def write_theme_file(theme: dict, language: str, items: list):
    lang_short = "uk" if language.startswith("uk") else "ru"
    path = MOOD_DIR / f"{theme['slug']}.{lang_short}.json"
    payload = {
        "slug": theme["slug"],
        "title": theme["title_uk"] if lang_short == "uk" else theme["title_ru"],
        "lang": lang_short,
        "updated_at": now_iso(),
        "items": items,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# ------------------ Обробка однієї теми ------------------
def process_theme(theme: dict, global_used: set) -> dict:
    """
    Повертає dict для index.json. Кидає виняток → викликаюча сторона позначить stale.
    global_used — множина (media_type, id), вже зайнятих іншими темами (дедуп між темами).
    """
    slug = theme["slug"]
    print(f"\n=== {slug} ({theme['title_ru']}) ===")

    # 1. кандидати: ІІ-назви + discover-пул + попередні валідні
    candidates = {}   # key (media_type, id) -> cand

    for suggestion in ai_suggest_titles(theme):
        cand = tmdb_search(suggestion["title"], suggestion["year"], suggestion["media_type"])
        if cand and cand.get("id") is not None:
            candidates[(cand["media_type"], cand["id"])] = cand

    for cand in tmdb_discover(theme):
        if cand.get("id") is not None:
            candidates.setdefault((cand["media_type"], cand["id"]), cand)

    # попередні тайтли — щоб працювала стабілізація (перевіряємо їх заново)
    for (mt, tid) in read_prev_keys(slug):
        if (mt, tid) in candidates:
            continue
        d = tmdb_detail(tid, mt, "en-US")
        if d:
            cand = to_candidate(d, mt)
            cand["genre_ids"] = [g["id"] for g in d.get("genres", []) if "id" in g]
            cand["id"] = d.get("id")
            candidates[(mt, tid)] = cand

    print(f"  candidates: {len(candidates)}")

    # 2. фільтри + дедуп між темами
    filtered = [c for k, c in candidates.items()
                if passes_filters(c, theme) and k not in global_used]

    # 3. ранжування + ліміт очевидного
    ranked = cap_obvious(sorted(filtered, key=rank_key, reverse=True))
    ranked_keys = [(c["media_type"], c["id"]) for c in ranked]
    print(f"  after filters: {len(ranked_keys)}")

    if not ranked_keys:
        raise RuntimeError(f"no candidates survived filters for '{slug}'")

    # 4. стабілізація
    prev_keys = read_prev_keys(slug)
    final_keys = stabilize(prev_keys, ranked_keys, TARGET_COUNT, MAX_CHANGE)

    # 5. гідрація uk + ru
    uk_items, ru_items = [], []
    for (mt, tid) in final_keys:
        uk = build_item(tid, mt, "uk")
        ru = build_item(tid, mt, "ru")
        if uk and ru:
            uk_items.append(uk)
            ru_items.append(ru)
        global_used.add((mt, tid))

    if not uk_items:
        raise RuntimeError(f"hydration produced no items for '{slug}'")

    # 6. запис
    write_theme_file(theme, "uk", uk_items)
    write_theme_file(theme, "ru", ru_items)
    print(f"  written: {len(uk_items)} items")

    return {
        "slug": slug,
        "title_uk": theme["title_uk"],
        "title_ru": theme["title_ru"],
        "count": len(uk_items),
        "updated_at": now_iso(),
        "uk_url": f"mood/{slug}.uk.json",
        "ru_url": f"mood/{slug}.ru.json",
        "stale": False,
    }


def stale_entry(theme: dict) -> dict:
    """Запис у маніфест для теми, яку не вдалося перегенерувати (файл лишається старий)."""
    slug = theme["slug"]
    count = len(read_prev_keys(slug))
    return {
        "slug": slug,
        "title_uk": theme["title_uk"],
        "title_ru": theme["title_ru"],
        "count": count,
        "updated_at": now_iso(),
        "uk_url": f"mood/{slug}.uk.json",
        "ru_url": f"mood/{slug}.ru.json",
        "stale": True,
    }


# ------------------ main ------------------
def main():
    MOOD_DIR.mkdir(exist_ok=True)

    themes = THEMES
    if MOOD_ONLY:
        themes = [t for t in THEMES if t["slug"] in MOOD_ONLY]
        print(f"MOOD_ONLY active → {[t['slug'] for t in themes]}")

    global_used = set()
    index_themes = []

    for theme in themes:
        try:
            index_themes.append(process_theme(theme, global_used))
        except Exception as e:
            print(f"❌ theme '{theme['slug']}' failed: {e} — keeping previous file, marking stale")
            index_themes.append(stale_entry(theme))

    # index.json — для стабільного порядку слідуємо порядку THEMES
    index = {"updated_at": now_iso(), "themes": index_themes}
    with open(MOOD_DIR / "index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    ok = sum(1 for t in index_themes if not t["stale"])
    print(f"\n✅ Done. {ok}/{len(index_themes)} themes regenerated.")


if __name__ == "__main__":
    main()
