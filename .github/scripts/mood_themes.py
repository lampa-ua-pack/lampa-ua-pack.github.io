# -*- coding: utf-8 -*-
"""
Конфіг 14 тематичних підбірок («настроїв») для генератора mood.

Кожна тема містить:
  slug            — стабільний англ. ідентифікатор (ім'я файлів mood/{slug}.{uk,ru}.json)
  title_uk/ru     — назва теми для маніфесту index.json
  prompt          — опис теми для ІІ (англійською)
  genre_whitelist — множина TMDB genre_id (movie + tv), для фільтра «жанр б'ється з темою»
  discover_movie  — genre_id для /discover/movie (fallback-пул кандидатів)
  discover_tv     — genre_id для /discover/tv
  max_year        — (опц.) верхня межа року релізу (для «Ностальгії»)

Довідник TMDB genre_id:
  movie: 28 Action, 12 Adventure, 16 Animation, 35 Comedy, 80 Crime, 99 Documentary,
         18 Drama, 10751 Family, 14 Fantasy, 36 History, 27 Horror, 10402 Music,
         9648 Mystery, 10749 Romance, 878 Sci-Fi, 53 Thriller, 10752 War, 37 Western
  tv:    10759 Action&Adventure, 16 Animation, 35 Comedy, 80 Crime, 99 Documentary,
         18 Drama, 10751 Family, 10762 Kids, 9648 Mystery, 10764 Reality,
         10765 Sci-Fi&Fantasy, 10766 Soap, 10768 War&Politics, 37 Western
"""

THEMES = [
    {
        "slug": "no-think",
        "title_uk": "Щоб не думати",
        "title_ru": "Чтобы не думать",
        "prompt": (
            "Light, undemanding movies and shows. Popcorn content: comedies and easy "
            "adventures. Watchable with zero effort, nothing to memorize or figure out."
        ),
        "genre_whitelist": {35, 12, 10751, 10759, 16},
        "discover_movie": [35, 12, 10751],
        "discover_tv": [35, 10759, 10751],
    },
    {
        "slug": "blow-mind",
        "title_uk": "Підірвати мозок",
        "title_ru": "Взорвать мозг",
        "prompt": (
            "Non-linear plots, unexpected twists, mind-bending puzzles. Movies and shows "
            "that make you think and beg for a rewatch to make everything click. "
            "Avoid the tired ever-present top-list cliches — favor the less obvious."
        ),
        "genre_whitelist": {9648, 878, 53, 10765},
        "discover_movie": [9648, 878, 53],
        "discover_tv": [9648, 10765],
    },
    {
        "slug": "cry",
        "title_uk": "Поплакати",
        "title_ru": "Поплакать",
        "prompt": (
            "Tearjerker dramas. Moving, emotional stories about loss, love and family. "
            "The kind that has you reaching for the tissues."
        ),
        "genre_whitelist": {18, 10749},
        "discover_movie": [18, 10749],
        "discover_tv": [18],
    },
    {
        "slug": "cozy-rain",
        "title_uk": "Затишне під дощ",
        "title_ru": "Уютное под дождь",
        "prompt": (
            "Warm, calm, slow-paced comfort watches. A pleasant atmosphere with minimal "
            "stress. Perfect under a blanket on a rainy day."
        ),
        "genre_whitelist": {10751, 10749, 35, 18, 16},
        "discover_movie": [10751, 10749, 35, 18],
        "discover_tv": [10751, 35, 18],
    },
    {
        "slug": "adrenaline",
        "title_uk": "На адреналіні",
        "title_ru": "На адреналине",
        "prompt": (
            "Non-stop action, tense thrillers, chases and survival. Never lets you get "
            "bored for a second, keeps you on the edge of your seat."
        ),
        "genre_whitelist": {28, 53, 80, 10759, 12},
        "discover_movie": [28, 53, 80],
        "discover_tv": [10759, 80],
    },
    {
        "slug": "mood-up",
        "title_uk": "Підняти настрій",
        "title_ru": "Поднять настроение",
        "prompt": (
            "Feel-good movies and shows. Bright, good-natured, with a happy ending. "
            "They leave you warmer inside after watching."
        ),
        "genre_whitelist": {35, 10751, 10402, 10749, 16},
        "discover_movie": [35, 10751, 10402],
        "discover_tv": [35, 10751],
    },
    {
        "slug": "dark",
        "title_uk": "Темне і тривожне",
        "title_ru": "Тёмное и тревожное",
        "prompt": (
            "Bleak, oppressive, noir, psychological. A heavy atmosphere, uncomfortable "
            "subject matter and moral ambiguity."
        ),
        "genre_whitelist": {53, 80, 27, 9648, 18},
        "discover_movie": [53, 80, 27, 9648],
        "discover_tv": [80, 9648, 18],
    },
    {
        "slug": "date-night",
        "title_uk": "Для романтичного вечора",
        "title_ru": "Для романтического вечера",
        "prompt": (
            "Date night. Melodramas, romantic comedies and love stories. For two and a "
            "good mood."
        ),
        "genre_whitelist": {10749, 35, 18},
        "discover_movie": [10749, 35],
        "discover_tv": [18, 35],
    },
    {
        "slug": "nostalgia",
        "title_uk": "Ностальгія",
        "title_ru": "Ностальгия",
        "prompt": (
            "Hits of past decades, the movies of childhood and youth (roughly before "
            "2010). Retro that everyone remembers and wants to revisit."
        ),
        "genre_whitelist": {28, 12, 35, 18, 878, 14, 10751, 10749, 53, 10759, 10765},
        "discover_movie": [28, 12, 35, 18, 878, 14, 10751],
        "discover_tv": [35, 18, 10759],
        "max_year": 2010,
    },
    {
        "slug": "background",
        "title_uk": "Фоном під справи",
        "title_ru": "Фоном под дела",
        "prompt": (
            "Something that doesn't need your full attention. Sitcoms, light procedurals, "
            "shows you put on while doing your own thing. Prefer TV series."
        ),
        "genre_whitelist": {35, 80, 18, 10759},
        "discover_movie": [35],
        "discover_tv": [35, 80, 18, 10759],
    },
    {
        "slug": "thrill-nerves",
        "title_uk": "Полоскотати нерви",
        "title_ru": "Пощекотать нервы",
        "prompt": (
            "Horror, suspense, something scary. From mild goosebumps to genuinely "
            "terrifying."
        ),
        "genre_whitelist": {27, 53, 9648, 10765},
        "discover_movie": [27, 53, 9648],
        "discover_tv": [9648, 10765],
    },
    {
        "slug": "epic",
        "title_uk": "Масштабне",
        "title_ru": "Масштабное",
        "prompt": (
            "Epics, big cinema, sagas. Grand worlds, scope and spectacle. The kind you "
            "want to watch on a big screen."
        ),
        "genre_whitelist": {12, 14, 878, 10752, 36, 28, 10759, 10765, 10768},
        "discover_movie": [12, 14, 878, 10752, 36, 28],
        "discover_tv": [10759, 10765, 10768],
    },
    {
        "slug": "laugh",
        "title_uk": "Щоб посміятися",
        "title_ru": "Чтобы посмеяться",
        "prompt": (
            "Pure comedy. Humor, gags, easy laughs. For when you just need to cheer "
            "yourself up with a good laugh."
        ),
        "genre_whitelist": {35},
        "discover_movie": [35],
        "discover_tv": [35],
    },
    {
        "slug": "slow-beauty",
        "title_uk": "Повільне і красиве",
        "title_ru": "Медленное и красивое",
        "prompt": (
            "Slow cinema, visually refined. Beautiful cinematography, an unhurried pace, "
            "aesthetics over dynamics."
        ),
        "genre_whitelist": {18, 36, 10749, 14},
        "discover_movie": [18, 36, 10749, 14],
        "discover_tv": [18],
    },
]
