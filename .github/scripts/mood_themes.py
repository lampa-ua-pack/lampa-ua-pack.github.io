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
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><rect x="134" y="96" width="78" height="320" rx="26" fill="currentColor"/><rect x="300" y="96" width="78" height="320" rx="26" fill="currentColor"/></svg>',
        "title_uk": "Мозок на паузі",
        "title_ru": "Мозг на паузе",
        "prompt": (
            "Brain-off popcorn, breezy and easy to follow. INCLUDE broad comedies, "
            "buddy/heist capers, light action-adventure. EXCLUDE dark, heavy, or twisty plots."
        ),
        "styles": [
            "buddy-cop & mismatched-duo action-comedy", "light-hearted heist & caper comedies",
            "fish-out-of-water comedies", "globe-trotting treasure-hunt adventures",
            "spy spoofs & breezy spy-action", "underdog sports crowd-pleasers",
            "fun non-scary creature & monster adventures", "martial-arts & kung-fu comedy romps",
            "car & racing action romps", "family adventure comedy movies", "road-trip comedies",
            "80s/90s action-comedy throwbacks", "comedy Westerns & adventure spoofs",
            "comedy remakes/reboots that actually work",
        ],
        "craft": (
            "Deep cuts here = fun, well-liked crowd-pleasers people forgot about, not "
            "critically-panned junk; keep it truly breezy and plot-light; movies over TV."
        ),
        "quality_min": 6.0,
        "genre_whitelist": {35, 12, 10751, 10759},
        "discover_movie": [12, 35],
        "discover_tv": [35],
    },
    {
        "slug": "blow-mind",
        "icon": '<svg viewBox="0 0 875 753" xmlns="http://www.w3.org/2000/svg"><g transform="scale(0.5,-0.5) translate(875,-875)"><path fill="none" stroke="currentColor" stroke-width="100" stroke-linecap="round" stroke-linejoin="round" d="M351.817,-129.806 C367.151,-88.2461,375,-44.2981,375,0 C375,207.107,207.107,375,0,375 C-207.107,375,-375,207.107,-375,0 C-375,-76.957,-351.323,-152.051,-307.182,-215.091 C-283.64,-248.712,-271.012,-288.762,-271.012,-329.806 C-271.012,-440.263,-360.555,-529.806,-471.012,-529.806 C-536.265,-529.806,-597.415,-497.974,-634.843,-444.522 C-726.067,-314.24,-775,-159.045,-775,0 C-775,428.021,-428.021,775,0,775 C428.021,775,775,428.021,775,0 C775,-91.5496,758.779,-182.375,727.089,-268.2655 C669.104,-425.425,519.332,-529.806,351.817,-529.806 C196.046,-529.806,54.4429,-439.376,-11.0774,-298.055 C-30.5166,-256.177,-86.6373,-160.72,-123.471,-124.015 C-156.457,-91.1748,-175,-46.5459,-175,0 C-175,96.6497,-96.6497,175,0,175 C96.6497,175,175,96.6497,175,0 C175,-20.6724,171.337,-41.1814,164.181,-60.5761 C156.003,-82.7417,151.817,-106.181,151.817,-129.806 C151.817,-240.263,241.36,-329.806,351.817,-329.806 C435.574,-329.806,510.46,-277.616,539.453,-199.036 C562.965,-135.311,575,-67.9238,575,0 C575,317.564,317.564,575,0,575 C-317.564,575,-575,317.564,-575,0 C-575,-118.001,-538.695,-233.146,-471.012,-329.806"/></g></svg>',
        "title_uk": "Зламаєш голову",
        "title_ru": "Голову сломаешь",
        "prompt": (
            "Puzzle-box: time loops, unreliable narrators, reality-bending, rewatch-worthy "
            "twists. EXCLUDE straightforward blockbusters and space operas even if sci-fi."
        ),
        "styles": [
            "time-loop films", "unreliable-narrator mind-benders",
            "fractured / nonlinear timelines", "reality- or simulation-questioning stories",
            "memory & identity puzzles", "rug-pull twist thrillers",
            "cerebral multiverse / parallel-worlds (not superhero)",
            "ambiguous 'what really happened' films",
            "clever low-budget high-concept sci-fi", "paranoia & conspiracy puzzle-boxes",
            "recursion & nested-structure narratives",
            "philosophical sci-fi that messes with your head",
            "con-artist rug-pull capers", "puzzle-box TV series",
        ],
        "craft": (
            "Favor films whose structure or twist is the whole point and rewards a rewatch; "
            "skip anything whose twist is now common knowledge; clever indie concepts welcome."
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
        "styles": [
            "terminal-illness & grief dramas", "parent-and-child bonds",
            "bittersweet lost-love romances", "coming-of-age heartbreak",
            "war-torn family separation", "loyal-animal companion tearjerkers",
            "losing-a-friend stories", "immigrant & family-sacrifice dramas",
            "dementia & memory-loss dramas", "long-distance / letters love stories",
            "based-on-a-true-story tragedies", "quiet dramas about goodbyes",
            "foreign-language emotional gut-punches", "redemption & reconciliation dramas",
        ],
        "craft": (
            "Must genuinely earn the tears through character, not cheap manipulation or "
            "TV-movie sap; foreign-language gut-punches very welcome."
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
        "styles": [
            "gentle slice-of-life dramas", "food & cooking comfort films",
            "small-town charm stories",
            "gentle Western/European stop-motion & hand-drawn animation (NO anime)",
            "warm friendship stories", "cozy period / British gentle dramas",
            "bookshop / cafe / quaint-setting films", "gentle seasonal & holiday comfort",
            "pastoral & nature calm", "cozy low-stakes rom-coms",
            "wholesome family gentle films", "quiet feel-good indie comedies",
            "cozy non-violent mysteries",
        ],
        "craft": (
            "Warm, soft, low-stakes above all — nothing tense, loud, or sad; quiet slice-of-life "
            "and gentle non-anime animation are gold. NO Japanese anime (including Ghibli)."
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
        "styles": [
            "single-location siege & survival", "car-chase & vehicular action",
            "heists under pressure", "ticking-clock thrillers",
            "martial-arts & fight-driven action", "real-time / one-shot intensity",
            "special-ops & military missions", "home-invasion survival",
            "natural-disaster survival", "hitman & assassin action",
            "prison-break & escape", "relentless action-horror",
            "revenge rampages", "manhunt & chase thrillers",
        ],
        "craft": (
            "Pace and tension are king — momentum must never sag; prefer lean, propulsive "
            "genre films over bloated blockbusters."
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
        "styles": [
            "underdog sports triumphs", "joyful musicals & dance films",
            "feel-good friendship comedies", "inspirational true stories",
            "optimistic coming-of-age", "unlikely-mentor & found-family",
            "chasing-the-dream stories", "heartwarming non-anime animation",
            "community-comes-together stories", "upbeat road-trip self-discovery",
            "rom-coms with a joyful ending", "fish-out-of-water heartwarmers",
            "second-chance & reinvention stories",
        ],
        "craft": (
            "Must leave the viewer lighter, with a clearly happy or hopeful ending; avoid "
            "bittersweet; earned uplift, not saccharine."
        ),
        "genre_whitelist": {10402, 10749, 35, 10751},
        "discover_movie": [10402, 10749],
        "discover_tv": [35],
    },
    {
        "slug": "dark",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><ellipse cx="256" cy="342" rx="216" ry="46" fill="currentColor"/><path fill="currentColor" d="M160 342C146 224 172 132 202 132c18 0 26 24 54 24s36-24 54-24c30 0 56 92 42 210z"/></svg>',
        "title_uk": "Нуар і тіні",
        "title_ru": "Нуар и тени",
        "prompt": (
            "Bleak, morally grey, oppressive — noir, psychological, disturbing. EXCLUDE merely "
            "'serious' prestige dramas that aren't actually dark. TV ok if genuinely bleak."
        ),
        "styles": [
            "neo-noir crime", "psychological character studies",
            "bleak revenge dramas", "slow-burn disturbing thrillers",
            "morally-grey crime sagas", "nihilistic downbeat dramas",
            "rural / small-town noir", "corruption & conspiracy noir",
            "grim serial-killer procedurals", "addiction & self-destruction dramas",
            "cold Nordic / European noir", "oppressive dystopian bleakness",
            "disturbing character-driven horror", "true-crime-inspired grimness",
        ],
        "craft": (
            "Genuinely bleak and oppressive in tone, not merely 'serious'; morally grey; "
            "acclaimed or cult, not exploitation schlock."
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
        "styles": [
            "classic Old-Hollywood romances (1930s-50s)",
            "sweeping historical / costume period romances", "romantic musicals",
            "charming foreign-language romances (French, Korean, Italian, etc.)",
            "epic romantic dramas", "screwball & witty-banter romances",
            "holiday & seasonal romances", "second-chance & later-in-life romances",
            "opposites-attract rom-coms", "friends-to-lovers stories",
            "dance & music-driven romances", "literary-adaptation romances (Austen & co.)",
            "road-trip & travel romances", "teen & coming-of-age romances",
        ],
        "craft": (
            "Charming, warm chemistry that plays for two; keep it swoony and light, never "
            "tragic; span eras and styles — do NOT default to recent indie rom-coms."
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
        "styles": [
            "80s teen coming-of-age classics", "90s action blockbusters",
            "beloved 80s/90s fantasy adventures", "family classics people rewatch",
            "90s rom-com favorites", "iconic sci-fi of the era",
            "classic 80s/90s comedy hits", "beloved non-anime animated classics",
            "80s/90s adventure quests", "cult classics of the era",
            "sports classics", "summer-blockbuster nostalgia",
        ],
        "craft": (
            "Shared-memory icons from ~1980s-2000s people rewatch; here the OBVIOUS beloved "
            "ones ARE the point — no obscure deep cuts, nothing after 2010."
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
        "styles": [
            "classic multi-cam sitcoms", "single-cam workplace comedies",
            "cozy crime procedurals", "feel-good ensemble comedies",
            "lighthearted mystery-of-the-week series", "adult animated sitcoms (non-anime)",
            "Britcoms & panel comfort shows", "easy medical / legal procedurals",
            "slice-of-life dramedy series", "family sitcoms",
            "cozy detective episodic series", "comfort rewatch series",
        ],
        "craft": (
            "Half-watchable, episodic, low-plot TV you can drop in and out of; comfort and "
            "rewatchability over prestige; TV only, no dense serialized dramas."
        ),
        "genre_whitelist": {35, 80, 18, 10759},
        "discover_movie": [],
        "discover_tv": [35, 80],
    },
    {
        "slug": "thrill-nerves",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" fill-rule="evenodd" d="M256 64C158 64 88 138 88 236c0 55 24 98 56 122v46c0 20 16 36 36 36h152c20 0 36-16 36-36v-46c32-24 56-67 56-122 0-98-70-172-168-172zM136 236a44 48 0 1 0 88 0 44 48 0 1 0-88 0zM288 236a44 48 0 1 0 88 0 44 48 0 1 0-88 0zM256 300l30 54h-60z"/></svg>',
        "title_uk": "Мурахи по шкірі",
        "title_ru": "Мурашки по коже",
        "prompt": (
            "Real horror and suspense — dread, tension, scares, from goosebumps to "
            "terrifying. EXCLUDE action movies with monsters that aren't actually scary."
        ),
        "styles": [
            "slow-burn atmospheric horror", "supernatural hauntings",
            "psychological horror", "folk horror",
            "home-invasion / survival horror", "genuinely scary creature horror",
            "possession & occult horror", "found-footage / mockumentary horror",
            "Hitchcockian suspense thrillers", "body horror",
            "cult & ritual horror", "isolation horror (cabin, remote, snowbound)",
            "monster-in-the-dark dread", "acclaimed foreign horror (Korean, Spanish, etc.)",
        ],
        "craft": (
            "Genuinely scary or suspenseful — dread and tension, not action; prefer acclaimed "
            "and cult horror over direct-to-video schlock; strong foreign horror welcome."
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
        "styles": [
            "historical war epics", "sweeping period sagas",
            "fantasy world-building epics", "sci-fi space spectacle",
            "ancient-world / sword-and-sandal epics", "survival-against-nature grandeur",
            "revolution & empire sagas", "seafaring & exploration epics",
            "sprawling crime sagas of epic scope", "mythic quests",
            "disaster-scale spectacle", "grand historical-figure biopics",
        ],
        "craft": (
            "Scale and spectacle must feel huge — vast worlds, sweeping scope, big-screen "
            "grandeur; skip intimate small-canvas films."
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
        "styles": [
            "buddy & mismatched-duo comedies", "raunchy gross-out comedies",
            "spoof & parody (Airplane! / Naked Gun lineage)", "slapstick & physical comedy",
            "workplace & ensemble comedies", "stoner & slacker comedies",
            "teen & coming-of-age comedies", "action-comedies",
            "comedy crime capers", "fish-out-of-water comedies",
            "holiday & party comedies", "family-friendly comedies",
            "rom-coms that are genuinely funny", "sports comedies",
        ],
        "craft": (
            "Goal is laugh-out-loud, quotable, rewatchable-for-the-jokes; NOT dry arthouse, "
            "bleak or political satire, or comedy-dramas that aren't actually funny."
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
        "styles": [
            "painterly period pieces", "contemplative nature cinema",
            "long-take auteur films", "minimalist mood pieces",
            "visually-lush foreign arthouse", "meditative journey / road films",
            "ravishing costume dramas", "atmospheric desert / landscape films",
            "quiet character portraits", "poetic memory & time films",
            "striking black-and-white cinematography", "dreamlike lyrical films",
            "seasons & pastoral beauty",
        ],
        "craft": (
            "Ravishing images and contemplative mood over plot; auteur/arthouse of exceptional "
            "visual beauty; patient pacing is a feature, not a flaw."
        ),
        "genre_whitelist": {18, 36, 10749, 14},
        "discover_movie": [36, 18],
        "discover_tv": [18],
    },
]
