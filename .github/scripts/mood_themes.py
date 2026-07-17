# -*- coding: utf-8 -*-
"""
Конфіг 14 тематичних підбірок («настроїв») для генератора mood.

Кожна тема містить:
  slug            — стабільний англ. ідентифікатор (ім'я файлів mood/{slug}.{uk,ru}.json)
  emoji           — іконка настрою (для маніфесту / майбутнього плагіна)
  title_uk/ru     — назва теми
  prompt          — опис теми для ІІ (англійською)
  genre_whitelist — множина TMDB genre_id (movie + tv), для фільтра «жанр б'ється з темою»
  discover_movie  — genre_id для /discover/movie (додатковий пул кандидатів). [] = пропустити кіно
  discover_tv     — genre_id для /discover/tv.                                 [] = пропустити ТВ
  max_year        — (опц.) верхня межа року релізу (для «Ретро»)

Жанрові якорі підібрані так, щоб discover-пули тем перетинались якомога менше
(див. таблицю нижче). Легітимні перетини добиває MAX_THEME_REUSE у генераторі.

Довідник TMDB genre_id:
  movie: 28 Action, 12 Adventure, 16 Animation, 35 Comedy, 80 Crime, 99 Documentary,
         18 Drama, 10751 Family, 14 Fantasy, 36 History, 27 Horror, 10402 Music,
         9648 Mystery, 10749 Romance, 878 Sci-Fi, 53 Thriller, 10752 War, 37 Western
  tv:    10759 Action&Adventure, 16 Animation, 35 Comedy, 80 Crime, 99 Documentary,
         18 Drama, 10751 Family, 10762 Kids, 9648 Mystery, 10765 Sci-Fi&Fantasy,
         10766 Soap, 10768 War&Politics, 37 Western
"""

THEMES = [
    {
        "slug": "no-think",
        "emoji": "🍿",
        "title_uk": "Мозок на паузі",
        "title_ru": "Мозг на паузе",
        "prompt": (
            "Brain-off popcorn: broad comedies, buddy/heist capers, easy action-adventure, "
            "crowd-pleasers. INCLUDE fun, breezy, easy-to-follow films. EXCLUDE anything "
            "dark, heavy, emotionally draining, or with twisty/complex plots that demand attention."
        ),
        "genre_whitelist": {35, 12, 10751, 10759},
        "discover_movie": [12, 35],
        "discover_tv": [35],
    },
    {
        "slug": "blow-mind",
        "emoji": "🌀",
        "title_uk": "Зламаєш голову",
        "title_ru": "Голову сломаешь",
        "prompt": (
            "Puzzle-box cinema: time loops, unreliable narrators, reality-bending premises, "
            "non-linear structure that rewards a rewatch. INCLUDE clever, twist-driven, "
            "mind-bending stories. EXCLUDE straightforward blockbusters and space operas "
            "even if they are sci-fi/action."
        ),
        "genre_whitelist": {9648, 878, 53, 10765},
        "discover_movie": [878, 9648],
        "discover_tv": [10765],
    },
    {
        "slug": "cry",
        "emoji": "😢",
        "title_uk": "До сліз",
        "title_ru": "В слёзы",
        "prompt": (
            "Tearjerkers and emotional gut-punches about love, loss, family and sacrifice — "
            "films that genuinely make people cry. INCLUDE deeply moving, heartfelt dramas. "
            "EXCLUDE crime sagas or war epics that are merely 'serious' rather than "
            "tear-inducing. TV series welcome if truly moving."
        ),
        "genre_whitelist": {18, 10749},
        "discover_movie": [18],
        "discover_tv": [18],
    },
    {
        "slug": "cozy-rain",
        "emoji": "☕",
        "title_uk": "Плед і какао",
        "title_ru": "Плед и какао",
        "prompt": (
            "Gentle, low-stakes comfort watches with a warm, soft, soothing atmosphere. "
            "INCLUDE calm feel-cozy films, gentle animation, slice-of-life. EXCLUDE tension, "
            "violence, loud spectacle or anything stressful. Perfect under a blanket on a rainy day."
        ),
        "genre_whitelist": {16, 10751, 10402, 35},
        "discover_movie": [16, 10751],
        "discover_tv": [10751],
    },
    {
        "slug": "adrenaline",
        "emoji": "💥",
        "title_uk": "Повний газ",
        "title_ru": "Полный газ",
        "prompt": (
            "Relentless action and tension: chases, heists, survival, ticking-clock "
            "thrillers that keep the pulse up from start to finish. INCLUDE fast, intense, "
            "high-stakes films. EXCLUDE slow burns and talky dramas."
        ),
        "genre_whitelist": {28, 53, 12, 10759},
        "discover_movie": [28],
        "discover_tv": [10759],
    },
    {
        "slug": "mood-up",
        "emoji": "✨",
        "title_uk": "Заряд позитиву",
        "title_ru": "Заряд позитива",
        "prompt": (
            "Feel-good films that leave you smiling — warmth, hope, underdog triumphs, "
            "good-hearted humor. INCLUDE uplifting, life-affirming stories with a satisfying, "
            "happy ending. EXCLUDE bittersweet or downer endings."
        ),
        "genre_whitelist": {10402, 10749, 35, 10751},
        "discover_movie": [10402, 10749],
        "discover_tv": [35],
    },
    {
        "slug": "dark",
        "emoji": "🌑",
        "title_uk": "Нуар і тіні",
        "title_ru": "Нуар и тени",
        "prompt": (
            "Bleak, morally grey, oppressive cinema — noir, psychological, disturbing, heavy "
            "by design. INCLUDE unsettling, ambiguous, atmospheric films. EXCLUDE merely "
            "'serious' prestige dramas that aren't actually dark. TV series welcome if genuinely bleak."
        ),
        "genre_whitelist": {80, 53, 18, 9648},
        "discover_movie": [80],
        "discover_tv": [80],
    },
    {
        "slug": "date-night",
        "emoji": "❤️",
        "title_uk": "Для двох",
        "title_ru": "Для двоих",
        "prompt": (
            "Romantic films made for two: chemistry, longing, charming rom-coms and swooning "
            "love stories. INCLUDE warm, crowd-pleasing romances. EXCLUDE bleak or tragic "
            "romances that would kill the mood."
        ),
        "genre_whitelist": {10749, 35, 18},
        "discover_movie": [10749],
        "discover_tv": [10766],
    },
    {
        "slug": "nostalgia",
        "emoji": "📼",
        "title_uk": "Ретро",
        "title_ru": "Ретро",
        "prompt": (
            "Beloved classics from roughly the 1980s-2000s that people grew up with and love "
            "to revisit. INCLUDE iconic, warmly familiar, endlessly rewatchable titles. "
            "EXCLUDE recent films and obscure deep cuts — this mood is about shared memory."
        ),
        "genre_whitelist": {12, 14, 10751, 878, 28, 35, 18},
        "discover_movie": [12, 14],
        "discover_tv": [10759],
        "max_year": 2010,
    },
    {
        "slug": "background",
        "emoji": "🎧",
        "title_uk": "Під справи",
        "title_ru": "Под дела",
        "prompt": (
            "Easy, low-attention TV you can half-watch while doing chores: sitcoms, cozy "
            "procedurals, episodic comfort shows. INCLUDE light, self-contained, always-on "
            "series. EXCLUDE dense serialized dramas that demand full attention. TV series only."
        ),
        "genre_whitelist": {35, 80, 18, 10759},
        "discover_movie": [],
        "discover_tv": [35, 80],
    },
    {
        "slug": "thrill-nerves",
        "emoji": "👻",
        "title_uk": "Мурахи по шкірі",
        "title_ru": "Мурашки по коже",
        "prompt": (
            "Real horror and suspense — dread, tension, jump scares, creeping unease, from "
            "goosebumps to genuinely terrifying. INCLUDE scary films built to unnerve. "
            "EXCLUDE action movies with monsters that aren't actually scary."
        ),
        "genre_whitelist": {27, 53, 9648, 10765},
        "discover_movie": [27],
        "discover_tv": [9648],
    },
    {
        "slug": "epic",
        "emoji": "🏔️",
        "title_uk": "Великий екран",
        "title_ru": "Большой экран",
        "prompt": (
            "Grand-scale spectacle: sweeping sagas, vast worlds, war and history on a huge "
            "canvas, made for the big screen. INCLUDE ambitious, large-scope, visually massive "
            "films. EXCLUDE small, intimate, chamber pieces."
        ),
        "genre_whitelist": {12, 14, 878, 10752, 36, 28, 10759, 10765, 10768},
        "discover_movie": [36, 10752, 14],
        "discover_tv": [10768],
    },
    {
        "slug": "laugh",
        "emoji": "😂",
        "title_uk": "Сміхота",
        "title_ru": "Умора",
        "prompt": (
            "Films that make you laugh out loud — sharp comedies, gags, satire, absurdist and "
            "deadpan humor. INCLUDE films where comedy is the whole point. EXCLUDE dramas with "
            "a few funny moments."
        ),
        "genre_whitelist": {35},
        "discover_movie": [35],
        "discover_tv": [],
    },
    {
        "slug": "slow-beauty",
        "emoji": "🎞️",
        "title_uk": "Естетика кадру",
        "title_ru": "Эстетика кадра",
        "prompt": (
            "Visually ravishing slow cinema — painterly cinematography, contemplative pace, "
            "atmosphere and mood over plot. INCLUDE auteur/arthouse films of exceptional "
            "beauty. EXCLUDE fast-paced or plot-driven films."
        ),
        "genre_whitelist": {18, 36, 10749, 14},
        "discover_movie": [36, 18],
        "discover_tv": [18],
    },
]
