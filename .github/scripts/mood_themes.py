# -*- coding: utf-8 -*-
"""
Конфіг 14 тематичних підбірок («настроїв») для генератора mood.

Кожна тема містить:
  slug            — стабільний англ. ідентифікатор (ім'я файлів mood/{slug}.{uk,ru}.json)
  icon            — SVG-іконка настрою (viewBox 0 0 512 512, fill/stroke=currentColor)
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
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M168 96h64c17.7 0 32 14.3 32 32v256c0 17.7-14.3 32-32 32h-64c-17.7 0-32-14.3-32-32V128c0-17.7 14.3-32 32-32zm112 0h64c17.7 0 32 14.3 32 32v256c0 17.7-14.3 32-32 32h-64c-17.7 0-32-14.3-32-32V128c0-17.7 14.3-32 32-32z"/></svg>',
        "title_uk": "Мозок на паузі",
        "title_ru": "Мозг на паузе",
        "prompt": (
            "Brain-off popcorn, breezy and easy to follow. INCLUDE broad comedies, "
            "buddy/heist capers, light action-adventure. EXCLUDE dark, heavy, or twisty plots."
        ),
        "genre_whitelist": {35, 12, 10751, 10759},
        "discover_movie": [12, 35],
        "discover_tv": [35],
    },
    {
        "slug": "blow-mind",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><polygon fill="currentColor" points="256,40 305,207 472,256 305,305 256,472 207,305 40,256 207,207"/></svg>',
        "title_uk": "Зламаєш голову",
        "title_ru": "Голову сломаешь",
        "prompt": (
            "Puzzle-box: time loops, unreliable narrators, reality-bending, rewatch-worthy "
            "twists. EXCLUDE straightforward blockbusters and space operas even if sci-fi."
        ),
        "genre_whitelist": {9648, 878, 53, 10765},
        "discover_movie": [878, 9648],
        "discover_tv": [10765],
    },
    {
        "slug": "cry",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M256 64C190 180 128 250 128 320a128 128 0 1 0 256 0C384 250 322 180 256 64z"/></svg>',
        "title_uk": "До сліз",
        "title_ru": "В слёзы",
        "prompt": (
            "Tearjerkers about love, loss, family, sacrifice that genuinely make you cry. "
            "EXCLUDE crime sagas or war epics that are merely 'serious'. TV ok if truly moving."
        ),
        "genre_whitelist": {18, 10749},
        "discover_movie": [18],
        "discover_tv": [18],
    },
    {
        "slug": "cozy-rain",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><rect x="104" y="176" width="216" height="208" rx="28" fill="currentColor"/><path fill="none" stroke="currentColor" stroke-width="28" d="M320 224h28a52 52 0 0 1 0 104h-28"/><path fill="none" stroke="currentColor" stroke-width="20" stroke-linecap="round" d="M168 92c-18 22 18 40 0 60M248 92c-18 22 18 40 0 60"/></svg>',
        "title_uk": "Плед і какао",
        "title_ru": "Плед и какао",
        "prompt": (
            "Gentle low-stakes comfort with a warm, soothing feel. INCLUDE calm films, "
            "slice-of-life, gentle animation. EXCLUDE tension, violence, loud spectacle."
        ),
        "genre_whitelist": {16, 10751, 10402, 35},
        "discover_movie": [16, 10751],
        "discover_tv": [10751],
    },
    {
        "slug": "adrenaline",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><polygon fill="currentColor" points="300,32 116,296 236,296 212,480 396,216 276,216"/></svg>',
        "title_uk": "Адреналін",
        "title_ru": "Адреналин",
        "prompt": (
            "Relentless action and tension — chases, heists, survival, ticking-clock "
            "thrillers. EXCLUDE slow burns and talky dramas."
        ),
        "genre_whitelist": {28, 53, 12, 10759},
        "discover_movie": [28],
        "discover_tv": [10759],
    },
    {
        "slug": "mood-up",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><circle cx="256" cy="256" r="104" fill="currentColor"/><path fill="none" stroke="currentColor" stroke-width="32" stroke-linecap="round" d="M256 40v48M256 424v48M40 256h48M424 256h48M107 107l34 34M371 371l34 34M405 107l-34 34M141 371l-34 34"/></svg>',
        "title_uk": "Заряд позитиву",
        "title_ru": "Заряд позитива",
        "prompt": (
            "Feel-good, uplifting, life-affirming with a happy ending. INCLUDE warmth, hope, "
            "underdog wins, good-hearted humor. EXCLUDE bittersweet or downer endings."
        ),
        "genre_whitelist": {10402, 10749, 35, 10751},
        "discover_movie": [10402, 10749],
        "discover_tv": [35],
    },
    {
        "slug": "dark",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M352 96a176 176 0 1 0 96 288A208 208 0 0 1 352 96z"/></svg>',
        "title_uk": "Нуар і тіні",
        "title_ru": "Нуар и тени",
        "prompt": (
            "Bleak, morally grey, oppressive — noir, psychological, disturbing. EXCLUDE merely "
            "'serious' prestige dramas that aren't actually dark. TV ok if genuinely bleak."
        ),
        "genre_whitelist": {80, 53, 18, 9648},
        "discover_movie": [80],
        "discover_tv": [80],
    },
    {
        "slug": "date-night",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M256 464C120 360 48 288 48 200c0-60 48-104 104-104 40 0 76 24 104 64 28-40 64-64 104-64 56 0 104 44 104 104 0 88-72 160-208 264z"/></svg>',
        "title_uk": "Для двох",
        "title_ru": "Для двоих",
        "prompt": (
            "Romantic films for two — chemistry, longing, charming rom-coms, swoony love "
            "stories. EXCLUDE bleak or tragic romances that would kill the mood."
        ),
        "genre_whitelist": {10749, 35, 18},
        "discover_movie": [10749],
        "discover_tv": [10766],
    },
    {
        "slug": "nostalgia",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><rect x="56" y="120" width="400" height="272" rx="28" fill="none" stroke="currentColor" stroke-width="28"/><circle cx="192" cy="248" r="40" fill="currentColor"/><circle cx="320" cy="248" r="40" fill="currentColor"/><path stroke="currentColor" stroke-width="24" stroke-linecap="round" d="M168 340h176"/></svg>',
        "title_uk": "Ретро",
        "title_ru": "Ретро",
        "prompt": (
            "Beloved iconic classics (~1980s-2000s) people grew up with and rewatch. "
            "EXCLUDE recent films and obscure deep cuts — this mood is shared memory."
        ),
        "genre_whitelist": {12, 14, 10751, 878, 28, 35, 18},
        "discover_movie": [12, 14],
        "discover_tv": [10759],
        "max_year": 2010,
    },
    {
        "slug": "background",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="none" stroke="currentColor" stroke-width="32" d="M104 288v-24a152 152 0 0 1 304 0v24"/><rect x="80" y="280" width="72" height="128" rx="28" fill="currentColor"/><rect x="360" y="280" width="72" height="128" rx="28" fill="currentColor"/></svg>',
        "title_uk": "Під справи",
        "title_ru": "Под дела",
        "prompt": (
            "Easy low-attention TV to half-watch while doing chores — sitcoms, cozy "
            "procedurals, episodic comfort shows. EXCLUDE dense serialized dramas. TV only."
        ),
        "genre_whitelist": {35, 80, 18, 10759},
        "discover_movie": [],
        "discover_tv": [35, 80],
    },
    {
        "slug": "thrill-nerves",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="none" stroke="currentColor" stroke-width="28" stroke-linejoin="round" d="M112 248a144 144 0 0 1 288 0v192l-40-32-40 32-48-36-48 36-40-32-24 20z"/><circle cx="204" cy="236" r="22" fill="currentColor"/><circle cx="308" cy="236" r="22" fill="currentColor"/></svg>',
        "title_uk": "Мурахи по шкірі",
        "title_ru": "Мурашки по коже",
        "prompt": (
            "Real horror and suspense — dread, tension, scares, from goosebumps to "
            "terrifying. EXCLUDE action movies with monsters that aren't actually scary."
        ),
        "genre_whitelist": {27, 53, 9648, 10765},
        "discover_movie": [27],
        "discover_tv": [9648],
    },
    {
        "slug": "epic",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><polygon fill="currentColor" points="16,436 176,140 288,340 344,248 496,436"/></svg>',
        "title_uk": "Великий екран",
        "title_ru": "Большой экран",
        "prompt": (
            "Grand-scale spectacle — sweeping sagas, vast worlds, war and history on a huge "
            "canvas, for the big screen. EXCLUDE small, intimate chamber pieces."
        ),
        "genre_whitelist": {12, 14, 878, 10752, 36, 28, 10759, 10765, 10768},
        "discover_movie": [36, 10752, 14],
        "discover_tv": [10768],
    },
    {
        "slug": "laugh",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M256,0C114.833,0,0,114.833,0,256s114.833,256,256,256s256-114.833,256-256S397.167,0,256,0z M256,472.341c-119.275,0-216.341-97.066-216.341-216.341S136.725,39.659,256,39.659c119.295,0,216.341,97.066,216.341,216.341S375.275,472.341,256,472.341z"/><circle cx="176" cy="200" r="28" fill="currentColor"/><circle cx="336" cy="200" r="28" fill="currentColor"/><path fill="none" stroke="currentColor" stroke-width="28" stroke-linecap="round" d="M160 300a112 112 0 0 0 192 0"/></svg>',
        "title_uk": "Сміхота",
        "title_ru": "Умора",
        "prompt": (
            "Broadly funny, laugh-out-loud crowd-pleasers people quote and rewatch for the "
            "laughs — mainstream and cult comedies, spoofs, slapstick, feel-good farces. "
            "EXCLUDE dry arthouse comedy, bleak/political satire, and comedy-dramas that aren't "
            "actually funny (no Fleabag / The Lobster / The Death of Stalin)."
        ),
        "genre_whitelist": {35},
        "discover_movie": [35],
        "discover_tv": [],
    },
    {
        "slug": "slow-beauty",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><rect x="88" y="96" width="336" height="320" rx="16" fill="none" stroke="currentColor" stroke-width="26"/><g fill="currentColor"><rect x="120" y="128" width="36" height="36" rx="6"/><rect x="120" y="238" width="36" height="36" rx="6"/><rect x="120" y="348" width="36" height="36" rx="6"/><rect x="356" y="128" width="36" height="36" rx="6"/><rect x="356" y="238" width="36" height="36" rx="6"/><rect x="356" y="348" width="36" height="36" rx="6"/></g></svg>',
        "title_uk": "Естетика кадру",
        "title_ru": "Эстетика кадра",
        "prompt": (
            "Visually ravishing slow cinema — painterly, contemplative, mood over plot. "
            "INCLUDE auteur/arthouse of exceptional beauty. EXCLUDE fast, plot-driven films."
        ),
        "genre_whitelist": {18, 36, 10749, 14},
        "discover_movie": [36, 18],
        "discover_tv": [18],
    },
]
