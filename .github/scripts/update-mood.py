# -*- coding: utf-8 -*-
"""
Генератор тематичних підбірок «MOOD».

Флоу:
  A. OpenCode API (OpenAI-сумісний chat/completions) → назви тайтлів для ВСІХ тем ПАРАЛЕЛЬНО
  B. по кожній темі (послідовно — заради детермінованого дедупу між темами):
     1. TMDB /search резолвить назви у реальні ID (паралельно, fuzzy: title + year)
        + /discover як додатковий пул кандидатів (змішаний пул)
     2. детерміновані фільтри анти-слопу (vote_count, збіг жанру, дедуп, ліміт очевидного)
     3. ротація: спершу тайтли, яких не було минулого прогону (заради свіжості)
     4. гідрація фінальних тайтлів мовами uk та ru (паралельно)
     5. запис mood/{slug}.uk.json та mood/{slug}.ru.json
Наприкінці — mood/index.json (маніфест). Збій однієї теми не рушить увесь ран:
її попередній файл лишається, у маніфесті ставиться "stale": true.

Паралелізм: пул потоків (MAX_WORKERS) обмежує одночасні запити до TMDb замість пауз sleep.

ENV:
  TMDB_API_KEY      — обов'язковий
  OPENCODE_URL      — базовий URL або повний endpoint chat/completions
  OPENCODE_MODELS   — кома-список моделей (фолбэк-ланцюг), напр. "hy3-free,big-pickle,deepseek-v4-flash-free"
  OPENCODE_MODEL    — одна модель (якщо OPENCODE_MODELS не задано; стане першою в ланцюгу + дефолтні фолбэки)
  OPENCODE_TOKEN    — bearer-токен
  MOOD_ONLY         — (опц.) кома-список slug для локального прогону (напр. "laugh,cry")
  MAX_WORKERS       — (опц.) пул потоків для TMDb (дефолт 16)
  AI_WORKERS        — (опц.) скільки батч-запитів до ІІ одночасно (дефолт 2)
  AI_BATCH_SIZE     — (опц.) скільки тем в одному запиті до ІІ (дефолт 2; 14 = один запит)
  OPENCODE_RETRIES  — (опц.) додаткові спроби ІІ-запиту на таймаут/помилку (дефолт 2)
  DISCOVER_PAGES    — (опц.) сторінок /discover на кожен тип (дефолт 2)
  MAX_THEME_REUSE   — (опц.) у скількох темах може зустрічатись один тайтл (дефолт 2)
  TARGET_COUNT      — (опц.) фінальних тайтлів на тему (дефолт 10)
  AI_REQUEST_COUNT  — (опц.) скільки назв просити в ІІ (дефолт 24)
  OPENCODE_TEMPERATURE — (опц.) температура ІІ; вище = різноманітніше (дефолт 0.9)
  OPENCODE_SEED     — (опц.) seed ІІ; порожньо = без seed, свіжа вибірка щоразу
"""

import os
import re
import json
import math
import time
import random
import unicodedata
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter

from mood_themes import THEMES

# ------------------ Конфігурація ------------------
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise ValueError("[fail] TMDB_API_KEY environment variable not set")

OPENCODE_URL = os.environ.get("OPENCODE_URL", "").strip()
OPENCODE_MODEL = os.environ.get("OPENCODE_MODEL", "").strip()
OPENCODE_MODELS = os.environ.get("OPENCODE_MODELS", "").strip()  # кома-список моделей (фолбэк-ланцюг)
OPENCODE_TOKEN = os.environ.get("OPENCODE_TOKEN", "").strip()

# Ланцюг моделей: пробуємо по черзі, перша, що відповіла валідним — виграє. Так швидко
# (hy3-free/big-pickle ~3-4с) і стійко до зникнення будь-якої однієї free-моделі.
_DEFAULT_CHAIN = ["big-pickle", "hy3-free", "deepseek-v4-flash-free"]
if OPENCODE_MODELS:
    MODEL_CHAIN = [m.strip() for m in OPENCODE_MODELS.split(",") if m.strip()]
elif OPENCODE_MODEL:
    MODEL_CHAIN = [OPENCODE_MODEL] + [m for m in _DEFAULT_CHAIN if m != OPENCODE_MODEL]
else:
    MODEL_CHAIN = _DEFAULT_CHAIN

TMDB_BASE_URL = "https://api.themoviedb.org/3"
MOOD_DIR = Path("mood")
TIMEOUT = 15
OPENCODE_TIMEOUT = int(os.environ.get("OPENCODE_TIMEOUT", "120"))  # даємо повільним запитам добігти
OPENCODE_RETRIES = int(os.environ.get("OPENCODE_RETRIES", "0"))  # без негайного повтору (повтор повільної
                                                                # моделі лише палить час); 2й шанс — у salvage
OPENCODE_TEMPERATURE = float(os.environ.get("OPENCODE_TEMPERATURE", "0.9"))  # вище = різноманітніше
OPENCODE_SEED = os.environ.get("OPENCODE_SEED", "").strip()  # порожньо = без seed (свіжа вибірка щоразу)
AI_BUDGET_SEC = int(os.environ.get("AI_BUDGET_SEC", "540"))  # ліміт часу на ВСЮ ІІ-фазу; після нього
                                                            # нові ІІ-запити не робляться (теми -> stale)
_AI_START = time.monotonic()  # старт відліку бюджету ІІ (звичайний скрипт — time доступний)

MAX_WORKERS = int(os.environ.get("MAX_WORKERS", "16"))   # паралелізм TMDb
AI_WORKERS = int(os.environ.get("AI_WORKERS", "1"))      # ПОСЛІДОВНО: free-модель під паралельними
                                                         # запитами ділить пропускну здатність і таймаутить;
                                                         # один запит за раз відповідає за ~15-20с
AI_BATCH_SIZE = int(os.environ.get("AI_BATCH_SIZE", "1"))  # тем на запит. 1 = легкий надійний запит
                                                           # (single-key fallback є). (14 = один запит на всі)

TARGET_COUNT = int(os.environ.get("TARGET_COUNT", "15"))        # фінальних тайтлів на тему
AI_REQUEST_COUNT = int(os.environ.get("AI_REQUEST_COUNT", "24"))  # назв просимо в ІІ (запас на резолв/
                                                                 # дедуп/відсів без перекладу; ІІ — єдине джерело)
# країни виробництва під блок (СРСР + РФ/СНД) — жорсткий бекстоп до промт-виключення (ISO 3166-1)
BLOCK_COUNTRIES = {"SU", "RU", "BY", "KZ", "AM", "AZ", "KG", "MD", "TJ", "UZ", "TM"}
DISCOVER_PAGES = int(os.environ.get("DISCOVER_PAGES", "0"))  # 0 = discover вимкнено (контент лише від ІІ)
VOTE_COUNT_MIN = 150         # поріг популярності для discover-кандидатів (відсікає мотлох)
AI_VOTE_COUNT_MIN = int(os.environ.get("AI_VOTE_COUNT_MIN", "50"))  # м'якший поріг для ІІ-пиків
                                                                    # (пускає артхаус-рідкості, ловить хибні матчі)
OBVIOUS_VOTE_COUNT = 15000   # «занадто очевидні» блокбастери
OBVIOUS_MAX = 4              # скільки «очевидних» брати ПЕРШИМИ (решта — у хвіст, не викидаються)
QUALITY_MIN = float(os.environ.get("QUALITY_MIN", "6.5"))  # м'який поріг у КОДІ: спершу вибираємо
                                                           # РІВНОМІРНО зі свіжих >=порогу (відсікає дуди
                                                           # ~5.x, але лишає пул широким → рандом цілий),
                                                           # нижче — лише на послаблення. Планку 7+ тягне
                                                           # промт; код 6.5 — компроміс якість/різноманіття
MAX_THEME_REUSE = int(os.environ.get("MAX_THEME_REUSE", "2"))  # у скількох темах може бути один тайтл
                                                               # (жанри мудів реально перетинаються)

MOOD_ONLY = [s.strip() for s in os.environ.get("MOOD_ONLY", "").split(",") if s.strip()]

# Спільна сесія: пул з'єднань під розмір пулу потоків (щоб воркери не блокувались на конекшенах).
session = requests.Session()
_adapter = HTTPAdapter(pool_connections=MAX_WORKERS, pool_maxsize=MAX_WORKERS, max_retries=2)
session.mount("https://", _adapter)
session.mount("http://", _adapter)


def parallel_map(fn, items, workers=None):
    """Паралельний map зі збереженням порядку. Порожній вхід → []."""
    items = list(items)
    if not items:
        return []
    workers = min(workers or MAX_WORKERS, len(items))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))


# ------------------ Утиліти ------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_str() -> str:
    """Дата дня (UTC). Можна перекрити MOOD_DAY для тестів/відтворюваності."""
    return os.environ.get("MOOD_DAY") or datetime.now(timezone.utc).strftime("%Y-%m-%d")


def day_rng(slug: str) -> random.Random:
    """Детермінований генератор на (день, тема): у межах дня стабільно, між днями різне."""
    return random.Random(f"{today_str()}|{slug}")


# Ротирующий САБ-ЖАНР дня (константний розмір промту). У кожної теми власний курований
# список `styles` (mood_themes.py). Модель без цього тяжіє до «greatest hits» (ті самі якорі
# щодня); сильний КОНКРЕТНИЙ саб-жанр щодня заганяє її в інший кут теми → різні глибокі
# добірки, менше повторів. Настрій — головний, саб-жанр — вторинна лінза (див. RULES).
def daily_style(theme: dict) -> str:
    """Один сильний ротирующий саб-жанр на день, підпорядкований настрою теми.
    Порожньо, якщо у теми немає `styles`.

    Вибір НЕ випадковий незалежно щодня (тоді сусідні дні можуть збігтися — день1==день3),
    а перебір ПЕРЕМІШАНОЇ перестановки за порядковим номером дня: у межах циклу з len(styles)
    днів кожен стиль трапляється рівно раз → сусідні дні й день1/день3 НІКОЛИ не повторюють
    стиль. Кожен новий цикл перемішується інакше (сид від номера циклу)."""
    styles = theme.get("styles") or []
    if not styles:
        return ""
    n = len(styles)
    try:
        ordinal = datetime.strptime(today_str(), "%Y-%m-%d").toordinal()
    except Exception:
        ordinal = 0
    # СТАБІЛЬНА перестановка на тему + крок +1 щодня: 3 підряд дні дають ordinal%n, (o+1)%n,
    # (o+2)%n — при n>=3 завжди РІЗНІ індекси, тож сусідні дні й день1/день3 НІКОЛИ не збігаються
    # (без reshuffle на границі циклу, який раніше давав повтори). Період повного циклу = n днів.
    order = list(range(n))
    random.Random("styleorder|" + theme["slug"]).shuffle(order)
    style = styles[order[ordinal % n]]
    return (
        f" THIS RUN, lean hard into ONE specific sub-style: {style}. "
        f"RULES: (1) COMMIT to this sub-style — MOST of the list must clearly BE this sub-style, "
        f"not generic go-to picks for the mood; do NOT retreat to the usual crowd-pleasers. "
        f"(2) Still keep the core mood above — if a specific sub-style title breaks the mood, drop "
        f"THAT title (but do NOT abandon the sub-style). "
        f"(3) MIX the sub-style's mainstream pillars with lesser-known gems — not only obscure picks."
    )


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


def _opencode_chat(system_prompt: str, user_prompt: str, label: str):
    """
    chat/completions по ЛАНЦЮГУ моделей: пробуємо MODEL_CHAIN по черзі, перша валідна відповідь
    виграє. `reasoning.enabled=false` вимикає «розмисли» там, де вони є (big-pickle/mimo -> ~4с),
    інші моделі його ігнорують. Повертає content або None.
    """
    def make_payload(model):
        p = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": OPENCODE_TEMPERATURE,
            "reasoning": {"enabled": False},   # вимкнути reasoning (де підтримується) -> швидше
        }
        if OPENCODE_SEED:
            p["seed"] = int(OPENCODE_SEED)
        return p

    headers = {
        "Authorization": f"Bearer {OPENCODE_TOKEN}",
        "Content-Type": "application/json",
    }
    endpoint = opencode_endpoint()

    for model in MODEL_CHAIN:
        for attempt in range(1, OPENCODE_RETRIES + 2):
            if time.monotonic() - _AI_START > AI_BUDGET_SEC:
                print(f"[warn] OpenCode {label}: AI time budget ({AI_BUDGET_SEC}s) exhausted, skipping")
                return None
            try:
                resp = session.post(endpoint, json=make_payload(model), headers=headers,
                                    timeout=OPENCODE_TIMEOUT)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
                last_err = f"HTTP {resp.status_code}: {resp.text[:120]}"
            except Exception as e:
                last_err = repr(e)
            print(f"[warn] OpenCode {label} [{model}] try {attempt} failed: {last_err}")
            if attempt <= OPENCODE_RETRIES:
                time.sleep(2 * attempt)
        # ця модель не спрацювала — переходимо до наступної в ланцюгу
    return None


def ai_suggest_batch(batch: list) -> dict:
    """
    ІІ-пропозиції для групи тем одним запитом. Повертає {slug: [{title, year, media_type}, ...]}.
    Теми, для яких ІІ недоступний/не відповів, отримують [] (спрацює discover-пул).
    """
    slugs = [t["slug"] for t in batch]
    if not (OPENCODE_URL and MODEL_CHAIN and OPENCODE_TOKEN):
        print("[warn] OpenCode not configured - theme will stay stale")
        return {s: [] for s in slugs}

    system_prompt = (
        "Film/TV curator with broad, deep taste. "
        "Return ONLY a JSON object (no prose, no fences): keys = the exact theme ids in "
        'brackets, each value = array of {"title","year"(int),"media_type":"movie"|"tv"}. '
        "Match the MOOD, not shared genre tags; drop famous titles whose real mood is wrong. "
        "Obey each theme's own description, craft note, sub-style and EXCLUDE rules STRICTLY — "
        "they override any default instinct. "
        "EXCLUDE anything produced in the USSR or in Russia and other post-Soviet CIS countries "
        "(Russia, Belarus, Kazakhstan, etc.). EXCLUDE Japanese anime (animated films/series). "
        "BALANCE recognizability: within the given sub-style, MIX the genuine mainstream pillars "
        "everyone loves with lesser-known gems — aim for roughly half and half. Do NOT return "
        "only obscure no-names, and do NOT return only the same few blockbusters every run (the "
        "daily sub-style already keeps runs varied). A theme's craft note can shift this balance "
        "(e.g. nostalgia = mostly iconic). If a sub-style is hard to fill, pad with OTHER titles "
        "that fit the SUB-STYLE — not random off-style famous names. "
        "QUALITY: favor well-reviewed titles — aim for roughly a 7+/10 audience rating; a "
        "lower-rated pick is OK only if it truly nails the mood. Less-obvious must still mean "
        "well-made, not bad-and-forgotten. "
        "Fresh: vary picks run to run, never repeat a theme's AVOID list, never list the same "
        "title twice within a list; <=1 per franchise; vary eras and countries; "
        "add TV where episodic fits; order by strongest mood-fit first."
    )

    def block(t):
        line = f"[{t['slug']}] {t['title_ru']}: {t['prompt']}"
        craft = t.get("craft")
        if craft:
            line += " " + craft              # деталі під специфіку жанру
        avoid = read_prev_titles(t["slug"])
        if avoid:
            line += " AVOID (already shown, do not repeat): " + ", ".join(avoid)
        line += daily_style(t)               # сильний ротирующий саб-жанр дня (константний розмір)
        return line

    theme_blocks = "\n".join(block(t) for t in batch)
    user_prompt = (
        f"Themes:\n{theme_blocks}\n\n"
        f"For EACH theme id return {AI_REQUEST_COUNT} titles that fit THAT mood. "
        f"JSON object keyed by the exact ids."
    )

    content = _opencode_chat(system_prompt, user_prompt, "batch:" + ",".join(slugs))
    if not content:
        return {s: [] for s in slugs}

    obj = parse_ai_object(content)
    # толерантне сопоставлення: модель інколи віддає ключі інакше (no_think / "No Think" / рос. назва)
    norm_obj = {_norm_key(k): v for k, v in obj.items()}
    result = {}
    for s in slugs:
        titles = obj.get(s) or norm_obj.get(_norm_key(s), [])
        result[s] = titles
    # single-theme fallback: одна тема, один ключ у відповіді — беремо його попри розбіжність назви
    if len(slugs) == 1 and not result[slugs[0]] and len(obj) == 1:
        result[slugs[0]] = next(iter(obj.values()))
    # дедуп повторів усередині відповіді: деякі моделі зациклюються і повторюють один тайтл
    # десятки разів — прибираємо дублі за нормалізованою назвою, зберігаючи порядок
    for s in slugs:
        seen, dd = set(), []
        for it in result[s]:
            if not isinstance(it, dict):
                continue
            key = normalize_title(it.get("title") or "")
            if key and key not in seen:
                seen.add(key)
                dd.append(it)
        result[s] = dd
    for s in slugs:
        print(f"  ai[{s}]: {len(result[s])} titles")
    return result


def suggestions_for_all(themes: list) -> dict:
    """Розбиває теми на батчі й тягне ІІ-пропозиції паралельно (AI_WORKERS батчів одночасно)."""
    batches = [themes[i:i + AI_BATCH_SIZE] for i in range(0, len(themes), AI_BATCH_SIZE)]
    print(f"[ai] {len(themes)} themes -> {len(batches)} batch(es) of up to {AI_BATCH_SIZE}")
    merged = {}
    for d in parallel_map(ai_suggest_batch, batches, workers=AI_WORKERS):
        merged.update(d)

    # salvage: теми, що лишились порожні (збій батчу/розбіжність ключів) — перезапит поодинці,
    # перш ніж відкотитись на discover-пул (одиночний запит легший і надійніший)
    configured = bool(OPENCODE_URL and OPENCODE_MODEL and OPENCODE_TOKEN)
    empty = [t for t in themes if not merged.get(t["slug"])]
    if configured and empty:
        print(f"[ai] salvage {len(empty)} empty theme(s): {[t['slug'] for t in empty]}")
        for d in parallel_map(lambda t: ai_suggest_batch([t]), empty, workers=AI_WORKERS):
            merged.update({k: v for k, v in d.items() if v})
    return merged


def _coerce_titles(data) -> list:
    """Нормалізує список елементів ІІ у [{title, year:int, media_type}]."""
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


def _norm_key(k) -> str:
    """Нормалізація ключа теми для толерантного сопоставлення (no-think == no_think == 'No Think')."""
    return re.sub(r"[^a-z0-9]", "", str(k).lower())


def _strip_fences(content: str) -> str:
    text = content.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def parse_ai_object(content: str) -> dict:
    """Витягує JSON-об'єкт {slug: [...]} із відповіді ІІ, толерантно до fences/зайвого тексту."""
    if not content:
        return {}
    text = _strip_fences(content)
    if not text.startswith("{"):
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            text = m.group(0)
    try:
        data = json.loads(text)
    except Exception as e:
        print(f"[warn] Failed to parse AI JSON object: {e}")
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(k): _coerce_titles(v) for k, v in data.items()}


def parse_ai_titles(content: str) -> list:
    """Витягує JSON-масив [{title, year, media_type}] (толерантно до fences). Для одиночних відповідей/тестів."""
    if not content:
        return []
    text = _strip_fences(content)
    if not text.startswith("["):
        m = re.search(r"\[.*\]", text, re.DOTALL)
        if m:
            text = m.group(0)
    try:
        data = json.loads(text)
    except Exception as e:
        print(f"[warn] Failed to parse AI JSON: {e}")
        return []
    return _coerce_titles(data)


# ------------------ TMDB ------------------
def tmdb_get(path: str, params: dict):
    params = dict(params or {})
    params["api_key"] = TMDB_API_KEY
    try:
        resp = session.get(f"{TMDB_BASE_URL}/{path}", params=params, timeout=TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
        print(f"[warn] TMDb {path}: {resp.status_code}")
    except Exception as e:
        print(f"[warn] TMDb request error ({path}): {e}")
    return None


def tmdb_search(name: str, year: int, media_type: str):
    """Резолв назви у TMDB-кандидата з fuzzy-звіркою. Повертає нормалізований candidate або None."""
    params = {"query": name, "include_adult": "false", "language": "en-US"}
    if year:
        params["year" if media_type == "movie" else "first_air_date_year"] = year
    data = tmdb_get(f"search/{media_type}", params)
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
    return to_candidate(best, media_type, "ai")


def to_candidate(res: dict, media_type: str, source: str = "discover") -> dict:
    return {
        "id": res.get("id"),
        "media_type": media_type,
        "genre_ids": res.get("genre_ids") or [],
        "vote_average": res.get("vote_average") or 0,
        "vote_count": res.get("vote_count") or 0,
        "year": year_of(res),
        "source": source,   # "ai" | "discover" | "prev" — визначає пріоритет у ранжуванні
    }


def tmdb_discover(theme: dict) -> list:
    """
    Додатковий пул кандидатів через /discover для movie і tv, кілька сторінок (DISCOVER_PAGES).
    Кілька сторінок дають не лише топ-блокбастери, а й середняків — потрібно, щоб набрати
    TARGET навіть у вузьких/перетинних темах.
    """
    common = {
        "sort_by": "vote_count.desc",
        "vote_count.gte": VOTE_COUNT_MIN,
        "include_adult": "false",
        "language": "en-US",
    }
    max_year = theme.get("max_year")
    reqs = []

    def add_reqs(path, genres, mt, year_key):
        base = dict(common)
        base["with_genres"] = "|".join(str(g) for g in genres)
        if max_year:
            base[year_key] = f"{max_year}-12-31"
        for page in range(1, DISCOVER_PAGES + 1):
            params = dict(base)
            params["page"] = page
            reqs.append((path, params, mt))

    if theme.get("discover_movie"):
        add_reqs("discover/movie", theme["discover_movie"], "movie", "primary_release_date.lte")
    if theme.get("discover_tv"):
        add_reqs("discover/tv", theme["discover_tv"], "tv", "first_air_date.lte")

    def run(req):
        path, params, mt = req
        data = tmdb_get(path, params)
        return [to_candidate(r, mt) for r in (data or {}).get("results", [])]

    candidates = []
    for chunk in parallel_map(run, reqs):
        candidates.extend(chunk)
    return candidates


def tmdb_detail(tmdb_id: int, media_type: str, language: str):
    return tmdb_get(f"{media_type}/{tmdb_id}", {"language": language})


def _item_from_detail(d: dict, media_type: str) -> dict:
    """Формує елемент підбірки з TMDB-деталі (для однієї мови)."""
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


def hydrate_and_validate(key):
    """
    Гідрує тайтл мовами uk та ru і валідує:
      - країна виробництва НЕ в блок-листі (СРСР/РФ/СНД);
      - НЕ японське аніме (жанр Animation + оригінал ja / країна JP);
      - є переклад на ОБИДВІ мови (непорожній overview і uk, і ru).
    Повертає (key, uk_item, ru_item) або None, якщо тайтл не проходить.
    """
    mt, tid = key
    uk = tmdb_detail(tid, mt, "uk")
    ru = tmdb_detail(tid, mt, "ru")
    if not uk or not ru:
        return None
    countries = {c.get("iso_3166_1") for c in uk.get("production_countries", [])}
    countries |= set(uk.get("origin_country") or [])   # для ТВ
    if countries & BLOCK_COUNTRIES:
        return None
    # японське аніме: анімація + японське походження
    genre_ids = {g.get("id") for g in uk.get("genres", [])}
    if 16 in genre_ids and (uk.get("original_language") == "ja" or "JP" in countries):
        return None
    if not (uk.get("overview", "").strip() and ru.get("overview", "").strip()):
        return None
    return key, _item_from_detail(uk, mt), _item_from_detail(ru, mt)


# ------------------ Фільтри / ранжування / стабільність ------------------
def passes_filters(cand: dict, theme: dict) -> bool:
    if cand.get("id") is None:
        return False
    is_ai = cand.get("source") in ("ai", "prev")  # ІІ-курованим темам довіряємо настрій
    vote_floor = AI_VOTE_COUNT_MIN if is_ai else VOTE_COUNT_MIN
    if (cand.get("vote_count") or 0) < vote_floor:
        return False
    # whitelist жанрів — лише для discover (санітар попси); ІІ обирає за настроєм, не за тегом
    if not is_ai:
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


def prioritize_obvious(ranked: list) -> list:
    """
    Soft-cap заради різноманіття: перші OBVIOUS_MAX ультра-популярних лишаються попереду,
    решту «очевидних» НЕ викидаємо, а зсуваємо в хвіст. Так не-очевидні у пріоритеті,
    але список все одно набирає TARGET, якщо середняків бракує.
    """
    head, tail, obvious = [], [], 0
    for c in ranked:
        if (c.get("vote_count") or 0) >= OBVIOUS_VOTE_COUNT:
            if obvious < OBVIOUS_MAX:
                head.append(c)
                obvious += 1
            else:
                tail.append(c)
        else:
            head.append(c)
    return head + tail


def rotate_order(prev_keys: list, ranked_keys: list) -> list:
    """
    Ротація заради свіжості (БЕЗ обрізки): спершу кандидати, яких НЕ було минулого прогону,
    потім торішні (на добивання). Обрізку до target робить пізніше hydrate_valid, бо частина
    кандидатів відсіється на валідації перекладів/країни.
    """
    prev_set = set(prev_keys)
    fresh = [k for k in ranked_keys if k not in prev_set]
    seen = [k for k in ranked_keys if k in prev_set]
    return fresh + seen


# ------------------ Файли ------------------
def _read_prev_items(slug: str) -> list:
    path = MOOD_DIR / f"{slug}.uk.json"
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("items", [])
    except Exception:
        return []


def read_prev_keys(slug: str) -> list:
    """Ключі (media_type, id) із попереднього uk-файлу теми, у збереженому порядку."""
    return [(it.get("media_type"), it.get("id")) for it in _read_prev_items(slug)
            if it.get("id") is not None]


def read_prev_titles(slug: str) -> list:
    """
    Оригінальні назви з попередньої версії файлу теми (усі, не лише частина) — щоб просити ІІ
    не повторювати саме те, що вже показано зараз у майстері. Історію НЕ накопичуємо.
    """
    out = []
    for it in _read_prev_items(slug):
        name = it.get("original_title") or it.get("title")
        if name:
            out.append(name)
    return out


def write_theme_file(theme: dict, lang_short: str, items: list):
    path = MOOD_DIR / f"{theme['slug']}.{lang_short}.json"
    payload = {
        "slug": theme["slug"],
        "icon": theme.get("icon", ""),
        "title": theme["title_uk"] if lang_short == "uk" else theme["title_ru"],
        "lang": lang_short,
        "updated_at": now_iso(),
        "items": items,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# ------------------ Обробка однієї теми ------------------
def collect_candidates(theme: dict, suggestions: list) -> dict:
    """Кандидати: ІІ-назви (паралельний резолв) + discover-пул + попередні валідні (паралельно)."""
    candidates = {}   # key (media_type, id) -> cand

    # 1. резолв ІІ-назв паралельно
    resolved = parallel_map(
        lambda s: tmdb_search(s["title"], s["year"], s["media_type"]),
        suggestions,
    )
    for i, cand in enumerate(resolved):
        if cand and cand.get("id") is not None:
            cand["ai_order"] = i   # кураторський порядок ІІ (менше = вище пріоритет)
            candidates.setdefault((cand["media_type"], cand["id"]), cand)

    # 2. discover-пул
    for cand in tmdb_discover(theme):
        if cand.get("id") is not None:
            candidates.setdefault((cand["media_type"], cand["id"]), cand)

    # 3. попередні тайтли (щоб працювала стабілізація) — паралельний детейл
    missing = [(mt, tid) for (mt, tid) in read_prev_keys(theme["slug"])
               if (mt, tid) not in candidates]
    prev_details = parallel_map(lambda k: (k, tmdb_detail(k[1], k[0], "en-US")), missing)
    for (mt, tid), d in prev_details:
        if d:
            cand = to_candidate(d, mt, "prev")
            cand["id"] = d.get("id")
            cand["genre_ids"] = [g["id"] for g in d.get("genres", []) if "id" in g]
            candidates[(mt, tid)] = cand

    return candidates


def hydrate_pool(ordered_keys: list, cap: int) -> list:
    """
    Гідрує uk+ru та валідує (країна / аніме / переклад) капнутий пул кандидатів паралельно.
    Повертає ВСІ валідні (key, uk_item, ru_item) у порядку пулу — з них потім випадково беремо
    TARGET. Cap фіксований → вартість не росте з часом.
    """
    pool = ordered_keys[:cap]
    results = parallel_map(hydrate_and_validate, pool)
    return [r for r in results if r is not None]


def process_theme(theme: dict, suggestions: list, global_used) -> dict:
    """
    Повертає dict для index.json. Кидає виняток → викликаюча сторона позначить stale.
    global_used — Counter (media_type, id) -> у скількох темах уже використано (м'який дедуп).
    """
    slug = theme["slug"]
    print(f"\n=== {slug} ({theme['title_ru']}) ===")

    candidates = collect_candidates(theme, suggestions)
    print(f"  candidates: {len(candidates)}")

    # фільтри + м'який дедуп між темами (тайтл дозволено у MAX_THEME_REUSE темах)
    filtered = [c for k, c in candidates.items()
                if passes_filters(c, theme) and global_used[k] < MAX_THEME_REUSE]

    # ранжування: ІІ-добірка попереду, prev — лише на добір.
    # ІІ-кандидати: раніше суворо за ai_order (топ моделі ≈ найвідоміше) — cap завжди різав
    # той самий верх, звідси цикл повторів. Тепер день-сеяний shuffle зсуває вікно cap
    # день-у-день (анти-повтор); ai_order лишається для ФІНАЛЬНОГО порядку виводу нижче.
    ai_cands = [c for c in filtered if c["source"] == "ai"]
    day_rng("pool|" + slug).shuffle(ai_cands)
    other_cands = sorted((c for c in filtered if c["source"] != "ai"),
                         key=rank_key, reverse=True)
    ranked_keys = [(c["media_type"], c["id"]) for c in ai_cands + other_cands]
    print(f"  after filters: {len(ranked_keys)} (ai={len(ai_cands)}, other={len(other_cands)})")

    # контент лише від ІІ: якщо ІІ нічого не дав — лишаємо попередній файл (stale)
    if not ai_cands:
        raise RuntimeError(f"AI returned no usable candidates for '{slug}' - keeping previous file")

    # ротація (свіжі вперед) → валідація пулу → ВИПАДКОВА вибірка TARGET (свіжість день-у-день)
    prev_keys = read_prev_keys(slug)
    prev_set = set(prev_keys)
    ordered = rotate_order(prev_keys, ranked_keys)
    cap = min(len(ordered), max(TARGET_COUNT * 2 + 6, AI_REQUEST_COUNT))
    valid = hydrate_pool(ordered, cap)   # [(key, uk, ru)]
    if not valid:
        raise RuntimeError(f"no valid (uk/ru, non-SU/CIS, non-anime) titles for '{slug}' - keeping previous file")

    fresh = [v for v in valid if v[0] not in prev_set]   # яких не було в минулій версії
    seen = [v for v in valid if v[0] in prev_set]         # торішні — лише на добір

    # М'який жанровий гард + якісний тир + РІВНОМІРНА вибірка в межах тиру.
    # Черговість відер: свіжі перед торішніми; у межах — спершу ЖАНР-збіг, тоді якість (>=qmin).
    # М'який гард (theme.require_genre, напр. laugh->Comedy): не-жанрові тайтли беруться ЛИШЕ
    # коли жанрових бракує на TARGET — не хард-дроп, а пріоритет. Рандомізація в тирі — той
    # самий rng.sample. Теми без require_genre поводяться як раніше (не-жанрові відра порожні).
    def _va(v):
        return v[1].get("vote_average") or 0
    qmin = float(theme.get("quality_min", QUALITY_MIN))  # тема може мати свій поріг (напр. попкорн)
    req_genre = set(theme.get("require_genre") or ())
    def _gmatch(v):
        return (not req_genre) or bool(set(v[1].get("genre_ids") or ()) & req_genre)

    def _tier(pool):
        gm = [v for v in pool if _gmatch(v)]
        ng = [v for v in pool if not _gmatch(v)]
        return ([v for v in gm if _va(v) >= qmin], [v for v in gm if _va(v) < qmin],
                [v for v in ng if _va(v) >= qmin], [v for v in ng if _va(v) < qmin])

    rng = day_rng(slug)
    picked = []
    for bucket in (*_tier(fresh), *_tier(seen)):
        if len(picked) >= TARGET_COUNT:
            break
        need = TARGET_COUNT - len(picked)
        picked += bucket if len(bucket) <= need else rng.sample(bucket, need)

    # порядок виводу — за кураторським ai_order
    ai_order_of = {(c["media_type"], c["id"]): c.get("ai_order", 10**6) for c in ai_cands}
    picked.sort(key=lambda v: ai_order_of.get(v[0], 10**6))

    chosen_keys = [v[0] for v in picked]
    uk_items = [v[1] for v in picked]
    ru_items = [v[2] for v in picked]
    if len(chosen_keys) < TARGET_COUNT:
        print(f"  [note] only {len(chosen_keys)}/{TARGET_COUNT} valid for '{slug}'")

    for key in chosen_keys:
        global_used[key] += 1

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

    # статус конфігурації ІІ (без витоку значень) — щоб одразу було видно, чи працює OpenCode
    ai_ready = bool(OPENCODE_URL and MODEL_CHAIN and OPENCODE_TOKEN)
    print(f"[cfg] OpenCode: url={bool(OPENCODE_URL)} token={bool(OPENCODE_TOKEN)} "
          f"models={MODEL_CHAIN} -> {'READY' if ai_ready else 'DISABLED'}")
    if not ai_ready:
        print("[cfg] WARNING: AI is OFF; themes will stay stale. "
              "Set OPENCODE_URL / OPENCODE_TOKEN (and OPENCODE_MODELS or OPENCODE_MODEL).")

    themes = THEMES
    if MOOD_ONLY:
        themes = [t for t in THEMES if t["slug"] in MOOD_ONLY]
        print(f"MOOD_ONLY active -> {[t['slug'] for t in themes]}")

    # A. ІІ-пропозиції для всіх тем: батчами, паралельно, з ретраями на таймаут
    suggestions_by_slug = suggestions_for_all(themes)

    # B. теми послідовно — заради детермінованого м'якого дедупу між темами
    global_used = Counter()
    index_themes = []
    for theme in themes:
        try:
            index_themes.append(
                process_theme(theme, suggestions_by_slug.get(theme["slug"], []), global_used))
        except Exception as e:
            print(f"[fail] theme '{theme['slug']}': {e} - keeping previous file, marking stale")
            index_themes.append(stale_entry(theme))

    index = {"updated_at": now_iso(), "themes": index_themes}
    with open(MOOD_DIR / "index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    ok = sum(1 for t in index_themes if not t["stale"])
    print(f"\n[ok] Done. {ok}/{len(index_themes)} themes regenerated.")


if __name__ == "__main__":
    main()
