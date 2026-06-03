# Pokémon GO

## Метаданные

- **Жанр:** AR Mobile Game, Creature Collector
- **Платформа:** iOS, Android
- **Разработчик:** Niantic
- **Аудитория:** Global, ностальгирующие по Pokemon 90х/2000х, casual gamers, семьи 18-40
- **Стиль арта:** Playful 3D semi-realistic — яркие насыщенные цвета, мультяшные пропорции у покемонов, реалистичные тренеры
- **Концепция:** Покемоны в реальном мире (AR), тренеры выходят на улицы ловить покемонов, рейды, торговля, командные войны
- **youtube_channel:** (не назначен)

---

## Концепция игры

Pokémon GO переносит покемонов в реальный мир через дополненную реальность. Тренеры присоединяются к одной из трёх команд (Mystic, Valor, Instinct) и соревнуются за контроль над покестопами и тренажёрными залами. Ловля покемонов, рейды, эволюции, торговля — в реальных городах и локациях.

**Ключевые механики:** Ловля AR, Рейды, PvP-сражения, Командные битвы за гимы, Мегаэволюция, Легендарные рейды.

---

## Visual Style Guide

### Цветовая палитра
- Основные: Pokéball red (#EE1515), cream white (#F8F8F8), sky blue (#3DB8EE)
- Team Mystic: icy blue (#00BCD4), deep blue (#1565C0), white
- Team Valor: fiery red (#D32F2F), black, white flame accents
- Team Instinct: electric yellow (#FDD835), black lightning accents
- Природа/AR-среда: живые яркие уличные сцены, парки, городские пейзажи

### Освещение
- Яркий дневной свет — игра про выход на улицу
- Магическое свечение при появлении покемона (AR-эффект)
- Электрические искры (Pikachu), огненный свет (Charizard/Charmander), зловещие тени (Gengar)
- Рейды: драматическое освещение гимназий с лиловым/золотым свечением

### Композиция
- Покемоны: мультяшные 3D существа с cartoon proportions, яркие и cute
- Тренеры: реалистичные/стилизованные в официальных командных костюмах
- Фон: реальные городские локации, парки, улицы — концепция "покемоны среди нас"
- Вертикальная 9:16, mobile-first

### Стилистические ограничения
- Покемоны НЕ реалистичные животные — cartoon 3D, мультяшные пропорции
- Тренеры — стильные, молодые, энергичные (не anime-style)
- AR-эффект: покемоны "материализуются" в реальном мире, лёгкий glow вокруг них

### Prompt prefix (для сцен с покемонами)
```
Pokémon GO style, vibrant cartoon 3D Pokémon character, bright saturated colors, playful round proportions, cute expressive face, magical AR glow, real-world environment backdrop, dynamic energetic pose
```

### Prompt prefix (для тренеров)
```
Pokémon GO trainer, stylized semi-realistic young adult, team costume with logo, energetic confident pose, outdoor real-world setting, bright natural lighting
```

---

## Команды тренеров

| Команда | Лидер | Цвета | Характер |
|---------|-------|-------|----------|
| **Team Mystic** | Blanche | Icy blue + white | Спокойная, аналитическая, мудрая |
| **Team Valor** | Candela | Red + black + white | Страстная, сильная, боевая |
| **Team Instinct** | Spark | Yellow + black | Весёлая, интуитивная, раздолбай |

---

## Character Prompt Blocks

### Покемоны

#### Bulbasaur (#001)
`cartoon 3D Bulbasaur Pokémon, small quadruped, turquoise-green skin with darker irregular patches, large green plant bulb growing on back glowing softly with life energy, bright curious eyes, stubby legs, friendly expression, vibrant magical aura`

#### Charmander (#004)
`cartoon 3D Charmander Pokémon, small orange bipedal lizard, bright round eyes, flickering orange flame burning at the tip of its tail reflecting warm light, cheerful eager expression, small claws, upright stance, warm fiery glow`

#### Squirtle (#007)
`cartoon 3D Squirtle Pokémon, small light-blue bipedal turtle, smooth brown rounded shell on back, large round eyes, cheeky grin, tiny arms and legs, water-type freshness, playful confident pose`

#### Charizard (#006)
`cartoon 3D Charizard Pokémon, large powerful orange dragon, muscular arms, blue-tinged inner wings spread wide, blazing orange flame at tail tip, fierce roaring expression, imposing majestic stance, fire and smoke effects, mid-flight or rearing up`

#### Pikachu (#025)
`cartoon 3D Pikachu Pokémon, chubby yellow electric mouse, long black-tipped ears, small red circle cheeks glowing faintly with electricity, bright energetic eyes, tiny arms, cute stubby tail with lightning bolt tip, surrounded by sparks`

#### Jigglypuff (#039)
`cartoon 3D Jigglypuff Pokémon, round soft pale pink body, oversized round blue eyes with dramatic flair, tiny stubby arms, small curl on forehead, holding a microphone, ready to sing, adorable and theatrical expression`

#### Meowth (#052)
`cartoon 3D Meowth Pokémon, cream-colored bipedal cat, standing upright, round gold coin on forehead, expressive face with sly mischievous grin, whiskers, small paws with tiny claws, greedy playful personality`

#### Psyduck (#054)
`cartoon 3D Psyduck Pokémon, round pink-yellow body, cream muzzle, dazed dreamy eyes with perpetual headache expression, small arms, long tail, spaced-out confused look, gentle peaceful pose`

#### Gengar (#094)
`cartoon 3D Gengar Pokémon, round dark purple ghost body, glowing red eyes, wide wicked grin with spiky teeth, stubby arms, stepping out from shadows, eerie yet playful laugh, ghostly aura with dark wisps`

#### Snorlax (#143)
`cartoon 3D Snorlax Pokémon, massive round blue-green body, cream-colored belly, tiny eyes half-closed, small ears, enormous girth, peacefully sitting or sleeping, calm heavy comforting presence, lazy contented expression`

#### Eevee (#133)
`cartoon 3D Eevee Pokémon, small fox-like creature, soft brown fur, fluffy oversized cream-white collar ruff, large bright curious brown eyes, fluffy tail, gentle warm expression, elegant yet playful, sitting or ready to leap`

#### Beedrill (#015)
`cartoon 3D Beedrill Pokémon, yellow and black striped wasp, large wings, drill-like stingers on forearms and tail, intense fierce expression, mid-flight attack pose, fast aggressive energy, sharp dangerous`

#### Pidgey (#016)
`cartoon 3D Pidgey Pokémon, small round bird, beige underside with brown back and wings, tiny beak, gentle curious round eyes, natural earthy tones, perched calmly or mid-flutter, soft feathers`

#### Mew (#151)
`cartoon 3D Mew Pokémon, tiny floating pink creature, large innocent round blue eyes, thin graceful tail curling behind, translucent pink ears, ethereal glowing aura, childlike dreamlike expression, hovering lightly in air`

#### Mewtwo (#150)
`cartoon 3D Mewtwo Pokémon, tall sleek humanoid build, pale gray smooth skin, long thick purple tail, large elongated head, cold intelligent glowing eyes, powerful psychic aura emanating, imposing regal posture, arms slightly raised`

> ⚠️ В ассетах Supabase файл `079.png` содержит референс для Mewtwo (строка с описанием "tall sleek humanoid, pale gray skin, long purple tail"). Файл `079.png` используется как Mewtwo-референс, несмотря на номер. Для Slowpoke используй только текстовый промпт.

---

## Тренеры (Character Prompt Blocks)

#### Team Mystic Trainer (Blanche-style)
`Pokémon GO Team Mystic female trainer, cool composed style, sleek white jacket with light-blue and magenta accents, modern athletic cut pants, minimalist futuristic accessories, hair tied back neatly, calm strategic expression, confident analytical aura`

#### Team Valor Trainer (Candela-style)
`Pokémon GO Team Valor female trainer, fiery energetic design, red hoodie-jacket with flame accent details, sporty shorts or leggings, bold confident posing, flame motif accessories, passionate intense expression, strong athletic build`

#### Team Instinct Trainer (Spark-style)
`Pokémon GO Team Instinct female trainer, casual electric vibe, bright yellow hoodie with black leather jacket layered, fingerless gloves, lightning-bolt pendant accessory, sneakers, playful carefree expression, fun spontaneous energy`

---

## Референсные изображения (Supabase)

> Base URL: `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/`

| Персонаж | Supabase URL |
|----------|-------------|
| Bulbasaur | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/001.png` |
| Charmander | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/004.png` |
| Jigglypuff | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/039.png` |
| Charizard | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/006.png` |
| Squirtle | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/007.png` |
| Pikachu | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/025.png` |
| Meowth | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/052.png` |
| Eevee | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/133.png` |
| Gengar | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/094.png` |
| Snorlax | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/143.png` |
| Mewtwo (ref: 079.png) | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/079.png` |
| Mew | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/151.png` |
| Beedrill | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/015.png` |
| Pidgey | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/016.png` |
| Psyduck | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/054.png` |
| Team Mystic Trainer | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/female-pokemon-go-team-mystic-trainer-costume.webp` |
| Team Valor Trainer | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/female-pokemon-go-team-valor-trainer-costume.webp` |
| Team Instinct Trainer | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/pokemon-go-trainer-female-costume.webp` |

---

## Tone of Voice

- Ностальгический + современный: «помнишь этого покемона?»
- Энергичный, дружелюбный, для всех возрастов
- AR-hook: «а вдруг этот покемон живёт за углом?»
- Командное соперничество (Mystic vs Valor vs Instinct)
- Язык: English (основной), Russian

### Примеры фраз
- "Which starter would YOU choose?"
- "What if Pikachu was your actual neighbor?"
- "Team Mystic, Valor, or Instinct — which one are you?"
- "The rarest Pokémon just appeared downtown..."
- "Pokémon GO: where the game never really ends"

---

## Форматы для этой игры

- **`what-if-real-life`** — покемоны в реальных городских локациях (AR-вайб)
- **`character-story`** — история конкретного покемона (Pikachu, Gengar, Snorlax)
- **`top-list`** — топ-5 покемонов для рейдов, топ-3 стартера и т.д.
- **`dual-style`** — игровой покемон vs реальный мир
- **`fun-news`** — новости: новый рейд, ивент, редкий покемон пойман

---

## Музыка

- **Mood:** nostalgic, playful, energetic, adventure
- **BPM:** 110-140
- **Рекомендуемые треки:** upbeat adventure, nostalgic game OST vibes, playful electronic

---

## Игровой сленг

| Термин | Значение |
|--------|----------|
| CP | Combat Power — боевая мощь покемона, общий показатель силы |
| IV | Individual Values — скрытые характеристики (0-15 по Atk/Def/HP), макс = 100% |
| Stardust | Звёздная пыль — основная валюта для усиления покемонов |
| Candy | Конфеты — специфичны для вида, нужны для эволюции и прокачки |
| Shiny | Блестящий покемон — редкий цветовой вариант, охота за ним = главная страсть |
| Lucky Pokémon | Особый покемон после обмена с другом — дешевле в прокачке, светится |
| Shadow Pokémon | Покемон Team Rocket — усиленный урон, но слабая защита; можно очистить |
| Purified Pokémon | Очищенный Shadow — теряет агрессию, получает бонус к IV |
| Raid | Рейд — совместная битва с мощным боссом у гимназии |
| Legendary Raid | Рейд 5-звёздочного легендарного покемона (Mewtwo, Lugia и т.д.) |
| Mega Evolution | Мегаэволюция — временное усиление, даёт бонус к команде в рейде |
| Buddy Pokémon | Напарник — ходит с тренером, приносит конфеты и Special moves |
| PokéStop | Голубой диск на карте — источник предметов и яиц |
| Gym | Гимназия — захватываемая точка для командных сражений |
| Egg Hatching | Вылупление яйца — ходьба 2/5/7/10/12 км для получения покемона |
| Wild Spawn | Дикий покемон на карте — базовая механика ловли |
| Lure Module | Приманка — усиливает спавн покемонов у PokéStop на 30 мин |
| Incense | Благовоние — привлекает покемонов к тренеру на 1 час |
| Great / Ultra / Master League | PvP лиги по ограничению CP: ≤1500 / ≤2500 / без ограничений |
| GBL | GO Battle League — рейтинговый PvP |
| XL Candy | Конфеты XL — для прокачки покемонов выше 40 уровня |
| Spotlight Hour | Час особого покемона — 1 час повышенного спавна каждый вторник |
| Community Day | Комьюнити-день — ежемесячный ивент с особым покемоном и эксклюзивным муувом |
| 100 IV / Hundo | Покемон с идеальными IVs (15/15/15) — редкость, предмет гордости |
| 0 IV / Nundo | Покемон с нулевыми IVs — мем, тоже редкость по-своему |
| TM | Technical Machine — смена атаки покемона |
| Lucky Trade | Обмен с гарантированным Lucky-результатом (при достаточной дружбе) |

---

## CTA

- **Статус:** TODO — ассеты не загружены
- **Контент (план):** Pokémon GO логотип + Pokéball анимация + "CATCH THEM ALL" / "LINK IN BIO"
- **После генерации:** залить в Supabase `assets/pokemon-go/branding/cta.mp4`
- **Формат:** 1080×1920, 30fps, ~5s

---

## Opener

- **Статус:** TODO — ассеты не загружены
- **Контент (план):** AR-эффект появления покемона + логотип Pokemon GO
- **После генерации:** залить в Supabase `assets/pokemon-go/branding/opener.mp4`
- **Формат:** 1080×1920, 30fps, ~2s
