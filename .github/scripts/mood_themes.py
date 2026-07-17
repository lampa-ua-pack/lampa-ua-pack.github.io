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
            "Light, undemanding movies and shows. Popcorn content: comedies and easy "
            "adventures. Watchable with zero effort, nothing to memorize or figure out."
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
            "Non-linear plots, unexpected twists, mind-bending puzzles. Movies and shows "
            "that make you think and beg for a rewatch to make everything click. "
            "Avoid the tired ever-present top-list cliches — favor the less obvious."
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
            "Tearjerker dramas. Moving, emotional stories about loss, love and family. "
            "The kind that has you reaching for the tissues."
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
            "Warm, calm, slow-paced comfort watches. A pleasant atmosphere with minimal "
            "stress. Perfect under a blanket on a rainy day."
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
            "Non-stop action, tense thrillers, chases and survival. Never lets you get "
            "bored for a second, keeps you on the edge of your seat."
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
            "Feel-good movies and shows. Bright, good-natured, with a happy ending. "
            "They leave you warmer inside after watching."
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
            "Bleak, oppressive, noir, psychological. A heavy atmosphere, uncomfortable "
            "subject matter and moral ambiguity."
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
            "Date night. Melodramas, romantic comedies and love stories. For two and a "
            "good mood."
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
            "Hits of past decades, the movies of childhood and youth (roughly before "
            "2010). Retro that everyone remembers and wants to revisit."
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
            "Something that doesn't need your full attention. Sitcoms, light procedurals, "
            "shows you put on while doing your own thing. TV series only."
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
            "Horror, suspense, something scary. From mild goosebumps to genuinely "
            "terrifying."
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
            "Epics, big cinema, sagas. Grand worlds, scope and spectacle. The kind you "
            "want to watch on a big screen."
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
            "Pure comedy. Humor, gags, easy laughs. For when you just need to cheer "
            "yourself up with a good laugh."
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
            "Slow cinema, visually refined. Beautiful cinematography, an unhurried pace, "
            "aesthetics over dynamics."
        ),
        "genre_whitelist": {18, 36, 10749, 14},
        "discover_movie": [36, 18],
        "discover_tv": [18],
    },
]
