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
        "icon": '<svg viewBox="0 0 100.5 122.9" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="m4.4 62.4-1.8-2a15 15 0 0 1-2.6-8 20 20 0 0 1 1.3-8.1q1.3-3.1 3.4-5.7-1.5-4-1-8.2a19.4 19.4 0 0 1 18-17.5c1.7-4.7 5-8 8.9-10.2q3.7-2 7.8-2.5 4.2-.4 8.1.3 6.5 1.3 10.6 6a22 22 0 0 1 20.3 4q3 2.4 4.7 5.7a16 16 0 0 1 1.8 9.5q4.4 1.2 7.8 4.2 4.2 3.6 6.5 8.8 2.4 5.3 2.3 11.1-.2 7.5-5.3 14.1l-12.1 59H66.6l2.7-64.5h21.3q2.8-4.2 2.9-8.8A19 19 0 0 0 87 35.2q-3.3-2.8-7.6-3l-4.8-.2 1.6-4.6A10 10 0 0 0 72.9 16q-2-1.5-4.4-2.4a14 14 0 0 0-11 .4l-3.1 1.6-1.7-3a11 11 0 0 0-7.6-5A18 18 0 0 0 34 8.8a12 12 0 0 0-6.2 8.2l-.6 3.1L24 20a12 12 0 0 0-11.5 5.7Q11 28 10.6 31q-.4 3.4 1.5 6.6l1.6 2.8-2.7 1.9a9 9 0 0 0-3 4.5A13 13 0 0 0 7 52q.2 2.4 1.4 4.4a6 6 0 0 0 2.4 2H30l5.3 64.5H16.8zM62 26.2a4.6 4.6 0 1 1 0 9.1 4.6 4.6 0 0 1 0-9M48 40.4a4.6 4.6 0 1 1 0 9.1 4.6 4.6 0 0 1 0-9m-19.6-8.6a4.6 4.6 0 1 1 0 9.1 4.6 4.6 0 0 1 0-9.1m31.6 91H42l-5.3-64.6h26z"/></svg>',
        "title_uk": "Розвантаження",
        "title_ru": "Разгрузка",
        "prompt": (
            "Brain-off popcorn, breezy and easy to follow. INCLUDE broad comedies, "
            "buddy/heist capers, light action-adventure. EXCLUDE dark, heavy, or twisty plots."
        ),
        "styles": [
            "buddy-cop & mismatched-duo action-comedy", "light-hearted heist & caper comedies",
            "fish-out-of-water comedies", "globe-trotting treasure-hunt adventures",
            "spy spoofs & breezy spy-action", "underdog sports crowd-pleasers",
            "fun non-scary creature & monster adventures", "martial-arts & kung-fu comedy romps",
            "car & racing action romps", "family adventure comedy movies", "party & vacation comedies (pure laughs, no somber journeys)",
            "80s/90s action-comedy throwbacks", "comedy Westerns & adventure spoofs",
            "comedy remakes/reboots that actually work",
            "goofy superhero & comic-book romps", "toy & video-game adaptations played for fun",
            "dance & music feel-good comedies", "talking-animal & creature comedies",
            "light casino & con-artist caper romps", "goofy sci-fi & alien comedies",
        ],
        "craft": (
            "Deep cuts here = fun, well-liked crowd-pleasers people forgot about, not "
            "critically-panned junk; keep it truly breezy and plot-light — nothing heavy, sad or "
            "serious, pure light fun; movies over TV."
        ),
        "quality_min": 6.0,
        "require_genre": {35, 12, 10751, 10759, 28, 14, 878, 9648},
        "genre_whitelist": {35, 12, 10751, 10759},
        "discover_movie": [12, 35],
        "discover_tv": [35],
    },
    {
        "slug": "blow-mind",
        "icon": '<svg viewBox="0 0 875 753" xmlns="http://www.w3.org/2000/svg"><g transform="scale(0.5,-0.5) translate(875,-875)"><path fill="none" stroke="currentColor" stroke-width="100" stroke-linecap="round" stroke-linejoin="round" d="M351.817,-129.806 C367.151,-88.2461,375,-44.2981,375,0 C375,207.107,207.107,375,0,375 C-207.107,375,-375,207.107,-375,0 C-375,-76.957,-351.323,-152.051,-307.182,-215.091 C-283.64,-248.712,-271.012,-288.762,-271.012,-329.806 C-271.012,-440.263,-360.555,-529.806,-471.012,-529.806 C-536.265,-529.806,-597.415,-497.974,-634.843,-444.522 C-726.067,-314.24,-775,-159.045,-775,0 C-775,428.021,-428.021,775,0,775 C428.021,775,775,428.021,775,0 C775,-91.5496,758.779,-182.375,727.089,-268.2655 C669.104,-425.425,519.332,-529.806,351.817,-529.806 C196.046,-529.806,54.4429,-439.376,-11.0774,-298.055 C-30.5166,-256.177,-86.6373,-160.72,-123.471,-124.015 C-156.457,-91.1748,-175,-46.5459,-175,0 C-175,96.6497,-96.6497,175,0,175 C96.6497,175,175,96.6497,175,0 C175,-20.6724,171.337,-41.1814,164.181,-60.5761 C156.003,-82.7417,151.817,-106.181,151.817,-129.806 C151.817,-240.263,241.36,-329.806,351.817,-329.806 C435.574,-329.806,510.46,-277.616,539.453,-199.036 C562.965,-135.311,575,-67.9238,575,0 C575,317.564,317.564,575,0,575 C-317.564,575,-575,317.564,-575,0 C-575,-118.001,-538.695,-233.146,-471.012,-329.806"/></g></svg>',
        "title_uk": "Головоломка",
        "title_ru": "Головоломка",
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
            "rug-pull heist structures", "closed-room whodunit puzzles",
            "AI & consciousness mind-benders", "doppelganger & double-identity puzzles",
            "time-travel paradox films", "Rashomon-style perspective-shifters",
        ],
        "craft": (
            "Favor films whose structure or twist is the whole point and rewards a rewatch; "
            "skip anything whose twist is now common knowledge; clever indie concepts welcome."
        ),
        "require_genre": {9648, 878, 53, 10765, 18, 14, 27},
        "genre_whitelist": {9648, 878, 53, 10765},
        "discover_movie": [878, 9648],
        "discover_tv": [10765],
    },
    {
        "slug": "cry",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M256 64C190 180 128 250 128 320a128 128 0 1 0 256 0C384 250 322 180 256 64z"/></svg>',
        "title_uk": "До сліз",
        "title_ru": "До слёз",
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
            "single-parent & adoption tearjerkers", "sibling-bond dramas",
            "disability & resilience dramas", "found-family & orphan stories",
            "old-age & end-of-life dramas", "reunions after long separation",
        ],
        "craft": (
            "Must genuinely earn the tears through character, not cheap manipulation or "
            "TV-movie sap; foreign-language gut-punches very welcome."
        ),
        "require_genre": {18, 10749},
        "genre_whitelist": {18, 10749},
        "discover_movie": [18],
        "discover_tv": [18],
    },
    {
        "slug": "cozy-rain",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><rect x="104" y="176" width="216" height="208" rx="28" fill="currentColor"/><path fill="none" stroke="currentColor" stroke-width="28" d="M320 224h28a52 52 0 0 1 0 104h-28"/><path fill="none" stroke="currentColor" stroke-width="20" stroke-linecap="round" d="M168 92c-18 22 18 40 0 60M248 92c-18 22 18 40 0 60"/></svg>',
        "title_uk": "Затишок",
        "title_ru": "Уют",
        "prompt": (
            "Gentle low-stakes comfort with a warm, soothing feel. INCLUDE calm films, "
            "slice-of-life, gentle animation. EXCLUDE tension, violence, loud spectacle."
        ),
        "styles": [
            "gentle live-action slice-of-life (real people, NOT anime/animation)", "food & cooking comfort films",
            "small-town charm stories",
            "gentle Western/European stop-motion & hand-drawn animation (NO anime)",
            "warm friendship stories", "cozy period / British gentle dramas",
            "bookshop / cafe / quaint-setting films", "gentle seasonal & holiday comfort",
            "cozy village & countryside life (gentle live-action, warm — no war, action or peril)", "cozy low-stakes rom-coms",
            "wholesome family gentle films", "quiet feel-good indie comedies",
            "light cozy whodunits (Agatha Christie / Knives Out tone — no gore, no grim crime or horror)",
            "gentle pet & animal comfort (warm, never sad)", "bakery, craft & garden slice-of-life",
            "warm intergenerational friendships", "cozy library & bookshop mysteries (no grim crime)",
            "gentle armchair-travel & scenic comfort", "cozy Christmas-market & seasonal warmth",
        ],
        "craft": (
            "Warm, soft, low-stakes above all — nothing tense, loud, sad or heavy; no war, trauma "
            "or grief (no The Breadwinner, Persepolis, Grave of the Fireflies). Quiet slice-of-life "
            "and gentle non-anime animation are gold. NO Japanese anime (including Ghibli)."
        ),
        "tone_strict": True,   # затишок = теплий тон понад усе → лише безпечні run-модифікатори
        "require_genre": {16, 10751, 10402, 35, 18, 10749, 99, 14},
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
            "spy & espionage action", "vehicular mayhem (bike, boat, train)",
            "wilderness pursuit & survival chase", "protect-the-target / bodyguard thrillers",
            "kidnap-rescue ticking-clock", "sieges on transport (plane, train, ship)",
        ],
        "craft": (
            "Pace and tension are king — momentum must never sag; prefer lean, propulsive "
            "genre films over bloated blockbusters."
        ),
        "require_genre": {28, 53, 12, 10759, 80, 27, 878},
        "genre_whitelist": {28, 53, 12, 10759},
        "discover_movie": [28],
        "discover_tv": [10759],
    },
    {
        "slug": "mood-up",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><circle cx="256" cy="256" r="104" fill="currentColor"/><path fill="none" stroke="currentColor" stroke-width="32" stroke-linecap="round" d="M256 40v48M256 424v48M40 256h48M424 256h48M107 107l34 34M371 371l34 34M405 107l-34 34M141 371l-34 34"/></svg>',
        "title_uk": "Позитив",
        "title_ru": "Позитив",
        "prompt": (
            "Feel-good, uplifting, life-affirming with a happy ending. INCLUDE warmth, hope, "
            "underdog wins, good-hearted humor. EXCLUDE bittersweet or downer endings."
        ),
        "styles": [
            "underdog sports triumphs", "joyful, upbeat musicals (nothing tragic — no Dancer in the Dark / Les Miserables)",
            "feel-good friendship comedies", "uplifting inspirational true stories (triumphant, not tragic)",
            "feel-good, funny coming-of-age (happy ending, not bittersweet dramas)", "warm mentor & found-family stories (no abusive-mentor dramas)",
            "feel-good dream-chasers that end in triumph",
            "cheerful, upbeat non-anime animation (nothing sad or heavy)",
            "community-comes-together stories", "feel-good holiday & Christmas movies",
            "rom-coms with a joyful ending", "fish-out-of-water heartwarmers",
            "hopeful comeback & second-chance stories (uplifting, not tragic)",
            "feel-good pet & animal triumphs (happy ending)", "small-business & workplace success comedies",
            "uplifting dance & performance crowd-pleasers (triumphant)", "found-family holiday heartwarmers",
            "underdog competition winners (spelling bee, cook-off, talent)",
            "kids-and-grownups feel-good adventures (uplifting)",
        ],
        "craft": (
            "OVERRIDING GATE (beats the sub-style): EVERY pick must FEEL uplifting and end happily. "
            "Before adding a title, judge its overall tone and ending — if it is sad, heavy, bleak, "
            "tragic or bittersweet, DROP it however acclaimed or well-fitting (NO Whiplash, "
            "The Wrestler, Black Swan, Requiem for a Dream, Dancer in the Dark, Mary and Max, "
            "The Breadwinner, Persepolis, Grave of the Fireflies, Manchester by the Sea, Blue "
            "Valentine, Into the Wild, Wild). Earned uplift, not saccharine."
        ),
        "tone_strict": True,   # overriding tone-gate → лише безпечні run-модифікатори (STRICT_LENSES)
        "genre_whitelist": {10402, 10749, 35, 10751},
        "discover_movie": [10402, 10749],
        "discover_tv": [35],
    },
    {
        "slug": "dark",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><ellipse cx="256" cy="342" rx="216" ry="46" fill="currentColor"/><path fill="currentColor" d="M160 342C146 224 172 132 202 132c18 0 26 24 54 24s36-24 54-24c30 0 56 92 42 210z"/></svg>',
        "title_uk": "Нуар",
        "title_ru": "Нуар",
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
            "hitman & underworld character studies", "bleak prison & incarceration dramas",
            "morally-grey legal & political noir", "cold-war espionage paranoia",
            "domestic-thriller dread (marriages gone dark)", "gangland rise-and-fall tragedies",
        ],
        "craft": (
            "Genuinely bleak and oppressive in tone, not merely 'serious'; morally grey; "
            "acclaimed or cult, not exploitation schlock."
        ),
        "require_genre": {80, 53, 18, 9648, 27, 10768},
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
            "charming foreign-language romances (live-action — French, Korean, Italian; NO anime)",
            "epic romantic dramas", "screwball & witty-banter romances",
            "holiday & seasonal romances", "second-chance & later-in-life romances",
            "opposites-attract rom-coms", "friends-to-lovers stories",
            "enemies-to-lovers romances",
            "literary-adaptation romances (Austen & co.)",
            "summer & vacation romances",
            "sweet teen & high-school romances (fun and warm, not tragic — no Romeo + Juliet / A Walk to Remember)",
            "royalty & fairy-tale romances (charming)", "workplace & rivals-to-lovers rom-coms",
            "dance & music romances (swoony)", "reunited-lovers & letters-across-time (warm ending)",
            "cross-cultural & travel romances", "witty modern rom-coms with real chemistry",
        ],
        "craft": (
            "Charming, warm chemistry that plays for two; keep it swoony and light, never tragic "
            "(no Romeo + Juliet, A Walk to Remember, Blue Valentine); span eras and styles — do "
            "NOT default to recent indie rom-coms."
        ),
        "require_genre": {10749, 35, 18},
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
            "90s/2000s teen comedies", "iconic 80s/90s horror classics",
            "classic Disney & animated-era favorites (non-anime)", "beloved buddy-cop & action-duo classics",
            "90s/2000s rom-com staples", "classic creature-feature blockbusters",
        ],
        "craft": (
            "Shared-memory icons from ~1980s-2000s people rewatch; here the OBVIOUS beloved "
            "ones ARE the point — no obscure deep cuts, nothing after 2010."
        ),
        "require_genre": {12, 14, 10751, 878, 28, 35, 18, 27, 10749, 53, 80, 10759, 10765},
        "genre_whitelist": {12, 14, 10751, 878, 28, 35, 18},
        "discover_movie": [12, 14],
        "discover_tv": [10759],
        "max_year": 2010,
    },
    {
        "slug": "background",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="none" stroke="currentColor" stroke-width="32" d="M104 288v-24a152 152 0 0 1 304 0v24"/><rect x="80" y="280" width="72" height="128" rx="28" fill="currentColor"/><rect x="360" y="280" width="72" height="128" rx="28" fill="currentColor"/></svg>',
        "title_uk": "Фоном",
        "title_ru": "Фоном",
        "prompt": (
            "Easy, low-attention comfort to half-watch while doing chores — sitcoms, cozy "
            "procedurals, light comedies and feel-good movies alike (TV OR film). EXCLUDE dense "
            "serialized dramas and anything that demands full attention."
        ),
        "styles": [
            "classic multi-cam sitcoms", "single-cam workplace sitcoms",
            "cozy crime & detective procedurals", "feel-good ensemble comedy series",
            "lighthearted mystery-of-the-week", "adult animated sitcoms (non-anime)",
            "Britcoms & comfort panel shows", "easy feel-good comfort movies",
            "light comedy movies you can half-watch", "cozy rom-com movies",
            "family sitcoms & light family movies", "comfort rewatch favorites (TV or film)",
            "light medical & legal comfort procedurals", "cooking & baking competition shows",
            "gentle cozy period comfort series", "half-watchable animated sitcoms (non-anime)",
            "light feel-good docu-comfort", "easy rewatch action-comedy movies",
        ],
        "craft": (
            "Half-watchable, low-plot comfort you can drop in and out of — sitcoms, procedurals "
            "and easy light movies alike; comfort and rewatchability over prestige. Everything "
            "must be genuinely LIGHT and low-attention: no dense serialized dramas, no heavy or "
            "demanding films."
        ),
        "require_genre": {35, 80, 18, 10759, 10766, 10765, 9648, 10751},
        "genre_whitelist": {35, 80, 18, 10759},
        "discover_movie": [],
        "discover_tv": [35, 80],
    },
    {
        "slug": "thrill-nerves",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="none" stroke="currentColor" stroke-width="30" stroke-linejoin="round" d="M48 256s86-132 208-132 208 132 208 132-86 132-208 132S48 256 48 256z"/><circle cx="256" cy="256" r="64" fill="currentColor"/></svg>',
        "title_uk": "Саспенс",
        "title_ru": "Саспенс",
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
            "slasher & masked-killer horror", "vampire & werewolf horror",
            "zombie & outbreak horror", "haunted-house & haunted-object horror",
            "witch & folk-occult horror", "techno, screen & AI horror",
        ],
        "craft": (
            "Genuinely scary or suspenseful — dread and tension, not action; prefer acclaimed "
            "and cult horror over direct-to-video schlock; strong foreign horror welcome."
        ),
        "require_genre": {27, 53, 9648, 10765},
        "genre_whitelist": {27, 53, 9648, 10765},
        "discover_movie": [27],
        "discover_tv": [9648],
    },
    {
        "slug": "epic",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><polygon fill="currentColor" points="16,436 176,140 288,340 344,248 496,436"/></svg>',
        "title_uk": "Епос",
        "title_ru": "Эпос",
        "prompt": (
            "Grand-scale spectacle — sweeping sagas, vast worlds, war and history on a huge "
            "canvas, for the big screen. EXCLUDE small, intimate chamber pieces."
        ),
        "styles": [
            "historical war epics", "sweeping period sagas",
            "fantasy world-building epics (LOTR / GoT scale)", "sci-fi space spectacle (Dune / Star Wars scale)",
            "ancient-world / sword-and-sandal epics", "epic wilderness & survival spectacle (huge scale)",
            "revolution & empire sagas", "seafaring & swashbuckling adventure epics",
            "sprawling crime sagas of epic scope", "grand mythic & fantasy quests (Conan / Willow scale)",
            "disaster-scale spectacle", "grand historical-figure biopics",
            "medieval siege & castle-war epics", "naval & age-of-sail battle epics",
            "samurai & Asian historical epics (live-action, non-anime)", "biblical & mythological spectacle",
            "frontier & western epics (huge scale)", "dynastic & royal-court sagas",
        ],
        "craft": (
            "Scale and spectacle must feel huge — vast worlds, sweeping scope, big-screen "
            "grandeur; skip intimate small-canvas films. Lean MAINSTREAM here: the big beloved "
            "epics belong, mixed with a few lesser-seen ones."
        ),
        "require_genre": {12, 14, 878, 10752, 36, 28, 10759, 10765, 10768, 37, 18},
        "genre_whitelist": {12, 14, 878, 10752, 36, 28, 10759, 10765, 10768},
        "discover_movie": [36, 10752, 14],
        "discover_tv": [10768],
    },
    {
        "slug": "laugh",
        "icon": '<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M256,0C114.833,0,0,114.833,0,256s114.833,256,256,256s256-114.833,256-256S397.167,0,256,0z M256,472.341c-119.275,0-216.341-97.066-216.341-216.341S136.725,39.659,256,39.659c119.295,0,216.341,97.066,216.341,216.341S375.275,472.341,256,472.341z"/><circle cx="176" cy="200" r="28" fill="currentColor"/><circle cx="336" cy="200" r="28" fill="currentColor"/><path fill="none" stroke="currentColor" stroke-width="28" stroke-linecap="round" d="M160 300a112 112 0 0 0 192 0"/></svg>',
        "title_uk": "Сміх",
        "title_ru": "Смех",
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
            "teen & high-school comedies — laugh-out-loud only (NOT coming-of-age dramas)", "action-comedies",
            "comedy crime capers", "fish-out-of-water comedies",
            "holiday & party comedies", "family-friendly comedies",
            "rom-coms that are genuinely funny", "sports comedies",
            "mockumentary & improv comedies", "musical & song comedies (funny first)",
            "goofy horror-comedies (laugh-first)", "buddy road-trip comedies (laugh-out-loud, not soul-searching)",
            "wedding & party-disaster comedies", "British & Aussie broad comedies",
        ],
        "craft": (
            "Every pick must be a film you'd call a COMEDY first — its main job is to make you "
            "laugh. TEST: if a reasonable viewer would describe it as a drama (even a funny, "
            "touching or bittersweet one), EXCLUDE it. INCLUDE laugh-first films even if a little "
            "heartfelt (Mean Girls, Superbad, 10 Things I Hate About You, Booksmart); EXCLUDE "
            "drama-first coming-of-age / bittersweet indies (no Perks of Being a Wallflower, "
            "Moonlight, Lady Bird, Eighth Grade, Boyhood, Mean Creek, The Way Way Back, Little "
            "Miss Sunshine). Also not dry arthouse or bleak/political satire."
        ),
        "require_genre": {35},
        "genre_whitelist": {35},
        "discover_movie": [35],
        "discover_tv": [],
    },
    {
        "slug": "slow-beauty",
        "icon": '<svg viewBox="0 0 18 18" xmlns="http://www.w3.org/2000/svg"><path d="M9 0L11.4308 6.56918L18 9L11.4308 11.4308L9 18L6.56918 11.4308L0 9L6.56918 6.56918L9 0Z" fill="currentColor"/></svg>',
        "title_uk": "Естетика",
        "title_ru": "Эстетика",
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
            "painterly food & still-life cinema", "architectural & urban-mood films",
            "aquatic & underwater visual poems", "winter & snowscape contemplation",
            "folk-ritual & festival visual tapestries", "colour-drenched melodrama (Wong Kar-wai / Almodovar tone)",
        ],
        "craft": (
            "Ravishing images and contemplative mood over plot; auteur/arthouse of exceptional "
            "visual beauty; patient pacing is a feature, not a flaw."
        ),
        "require_genre": {18, 36, 10749, 14, 99, 10402},
        "genre_whitelist": {18, 36, 10749, 14},
        "discover_movie": [36, 18],
        "discover_tv": [18],
    },
]
