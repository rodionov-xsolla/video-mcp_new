# Growtopia

## Posting status

- **ready_to_post:** no   <!-- yes only when the game is tested and cleared for posting -->

**Formats (linked to this game):**

- (none configured yet)


> TODO(style-refactor): character appearance must move to per-format story bibles `characters[]` (style-free); style → top-level `style_tags` in the bible, fallback = `prompt_prefix`. This game config not yet migrated (see star-trek-timelines / genshin-impact for the pattern).

> TODO(assets): нет референсов в Supabase. Нужно спарсить спрайты предметов/сетов с вики (см. `tools/growtopia_parser.py`) и загрузить как `reference_image` с тегом `growtopia`.

> TODO(assets): забрать **стандартный (дефолтный) скин Growtopian** (базовый аватар игрока) как отдельный реф. Источник — канонический спрайт с вики (не Google-кэш-превью). Референс от юзера: `https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQSXtwW37bC4G4wtckNqCSpqg00fmo40PHlVLYd9lupAGRdJdQAUcy5JryV&s=10` (низкое качество, только как ориентир).

## Метаданные

- **Жанр:** 2D Sandbox MMO, Crafting / Trading
- **Платформа:** iOS, Android, PC (Steam)
- **Разработчик:** Ubisoft (изначально Robinson Technologies — Seth "Hamumu" Able & Mike Hommel)
- **Аудитория:** Global, 10–25, casual + core sandbox/trading игроки, ностальгия по ретро-пикселю
- **Стиль арта:** 2D pixel-art sandbox — плоские ретро-спрайты, side-view, блочные пропорции, яркая насыщенная палитра
- **Премьера:** January 2013 (active live service)
- **youtube_channel:** none

---

## Концепция игры

Growtopia — 2D песочница-MMO, где мир состоит из блоков, которые можно ломать, крафтить и строить. Каждый игрок создаёт собственные «миры» (worlds), фармит и торгует предметами, собирает культовые сеты (Legendary Wizard, Zeus, Angelic, Dragon) и копит валюту в виде замков (World Lock → Diamond Lock → Blue Gem Lock). Ядро игры — крафт, коллекционирование редких предметов, сезонные ивенты и живая экономика, построенная целиком на торговле между игроками.

**Ключевые механики:** блочный крафт и строительство, кастомные миры, торговля/экономика на World Lock'ах, сезонные ивенты (Growmas, Startopia, Harvest Festival), рейд-боссы (Growganoth), коллекционные легендарные сеты.

---

## Visual Style Guide

### Цветовая палитра
- Основные: Growtopia green (#5FB53C), sky blue (#5BC0EB), dirt brown (#8B5A2B)
- Акценты валюты: World Lock brown (#A0682E), Diamond Lock cyan (#3EE0E0), Blue Gem Lock deep blue (#1E4FE0)
- Яркие «леденцовые» цвета предметов и сетов, чистый плоский фон блочных миров

### Освещение
- Плоское, равномерное — как в ретро-2D-спрайтах, без объёмных теней
- Лёгкое свечение (glow) только у редких/легендарных предметов и валюты-замков
- Магическое сияние у сетов (Zeus — молнии, Angelic — золотой ореол, Dragon — огонь)

### Композиция
- Строго side-view (вид сбоку), 2D-плоскость, блочный мир из тайлов
- Персонажи — блочные пиксельные аватары с крупной квадратной головой
- Вертикальная 9:16, mobile-first; сцена «читается» как кадр из 2D-песочницы

### Стилистические ограничения
- НЕ 3D, НЕ realistic, НЕ cel-shaded anime — только плоский пиксель-арт / ретро-спрайт
- Толстые чёткие контуры, ограниченная палитра, «пикселизованные» края
- Никакого объёмного рендера персонажей — держим блочность и плоскость Growtopia

### Prompt prefix
```
Growtopia style, 2D pixel-art sprite, retro flat side-view design, blocky pixelated proportions, thick clean black outlines, bright saturated candy colors, simple tile-based sandbox world backdrop, no 3D rendering
```

### ⚠️ Анимация спрайта через Kling I2V — «Minecraft morph» (burned 2026-07-17)
Блочный Growtopia-скин **очень легко уезжает в 3D-майнкрафт** при I2V. Негативы `NOT Minecraft` НЕ спасают — лечится композицией стартового кадра и движением камеры (полный разбор — `rules/roles/animator.md §3.2`). Кратко для growtopia-пиксельных сцен:
- **Grounded-композиция обязательна:** персонаж стоит внутри полноценного плоского тайлового мира Growtopia (платформы, блоки, World Lock — как «читаемый скриншот 2D-игры»). НЕ изолировать спрайт на пустом небе и НЕ ставить в перспективную 3D-«пещеру» — в обоих случаях Kling достраивает воксельный 3D.
- **Камера:** мягкий push-in к персонажу или почти залочена. Никаких pull-back/пролётов «над блочным миром» и орбит «во фронт» — это триггерит 3D-реконструкцию.
- **Спрайт не вращать:** без разворотов головы/тела во фронт (side-view спрайт не имеет валидного 3D-фаса).
- Живость — из 2D-партиклов и среды, не из движения камеры.

### Костюм дефолт-скина — залочен
Канон зафиксирован (см. LOCKED-блок в `## Character Prompt Blocks` → Growtopian Avatar и `games/growtopia/character-story_story_bible.json.characters[].canonical_costume`): tan-кожа, **cyan/turquoise футболка (~#3FC1D6)**, **medium-blue штаны (~#5B6DC8)**. NB2 иначе плодит разные цвета от сцены к сцене (было: голый / красный / голубой в одном ролике) — всегда прописывать точные цвета в промпт каждой сцены.

---

## Character Prompt Blocks

> Growtopia не имеет фиксированных героев — есть кастомный аватар игрока (Growtopian), культовые сеты и знаковые предметы/существа. Блоки ниже покрывают типовые аватары + иконические сеты + предметы-символы.

### Аватары и сеты

#### Growtopian Avatar (базовый игрок) — LOCKED default-skin costume
> Канон дефолт-скина зафиксирован, чтобы NB2 не плодил разные цвета от сцены к сцене. Кожа tan/beige (~#C9A67C), футболка bright cyan/turquoise (~#3FC1D6), штаны medium-blue (~#5B6DC8), белые глаза с чёрными зрачками, толстый контур, без головных уборов/сетов.

`2D pixel-art Growtopian avatar, blocky humanoid, tan/beige blocky skin, large square head, two white dot eyes with black pupils and a small flat mouth, thick clean black outline, bright cyan/turquoise short-sleeve t-shirt, medium-blue pants, tiny blocky hands, no hat, no cosmetic set, canonical unmodified default skin, side-view stance, retro sprite look`

#### Legendary Wizard set
`2D pixel-art Growtopian in Legendary Wizard set, long flowing purple robe, tall pointed wizard hat with yellow stars, big white pixel beard, glowing magic staff with sparkling orb, faint arcane glow, side-view heroic pose`

#### Zeus set
`2D pixel-art Growtopian in Zeus set, golden greek-style armor, laurel crown, crackling yellow lightning bolts around the body, glowing storm aura, powerful side-view stance, electric sparks`

#### Angelic set
`2D pixel-art Growtopian in Angelic set, large white feathered wings, glowing golden halo above head, flowing white robe, soft heavenly golden glow, serene floating side-view pose`

#### Dragon set (Baby Dragon)
`2D pixel-art Growtopian in Dragon set, green scaled dragon hood and tail, small folded wings, tiny pixel flame breath from mouth, spiky scaled details, fierce playful side-view pose`

#### Devil / Demonic set
`2D pixel-art Growtopian in Demonic set, dark red skin, black bat wings, curved horns, glowing red eyes, mischievous sharp-toothed grin, dark smoky aura, menacing side-view stance`

#### Chef set
`2D pixel-art Growtopian in Chef set, tall white chef hat, white apron over striped shirt, holding a frying pan, cheerful expression, cooking pose, side-view`

#### Adventurer / Explorer set
`2D pixel-art Growtopian in Adventurer set, brown explorer fedora, leather satchel across chest, coiled whip on belt, rugged khaki outfit, confident treasure-hunter side-view pose`

### Предметы-символы (валюта и коллекционные)

#### World Lock (WL)
`2D pixel-art World Lock item, small brown wooden lock block with a yellow keyhole and metal band, subtle warm glow, iconic Growtopia currency icon, flat sprite on transparent-style backdrop`

#### Diamond Lock (DL)
`2D pixel-art Diamond Lock item, cyan crystalline lock block with sparkling faceted surface and keyhole, bright cyan glow, premium Growtopia currency icon, flat sprite`

#### Blue Gem Lock (BGL)
`2D pixel-art Blue Gem Lock item, deep radiant blue crystal lock block, intense glowing facets and keyhole, rare high-value currency icon, strong blue aura, flat sprite`

#### Gems / Growtoken
`2D pixel-art Growtopia gems, small cyan diamond-shaped currency crystals with soft sparkle, scattered pile, bright cheerful glow, flat sprite icon`

### Существа / боссы

#### Growganoth (world boss)
`2D pixel-art Growganoth, massive dark purple tentacled world-boss creature, multiple glowing yellow eyes, ominous shadowy body filling the frame, dripping dark energy, menacing side-view raid-boss presence`

#### Growmoji
`2D pixel-art Growmoji, small round yellow smiley pixel creature, big simple eyes and grin, tiny stub arms, bouncy cheerful expression, mascot-like flat sprite`

---

## Референсные изображения (Supabase)

> **TODO** — референсов пока нет. Спрайты будут спарсены с вики (`tools/growtopia_parser.py`) и загружены в Supabase с `game_tag=growtopia`, `asset_type=reference_image`. До этого storyboarder работает по текстовым промптам выше.

| Персонаж / предмет | Supabase URL |
|--------------------|--------------|
| (parser pending)   | —            |

---

## Tone of Voice

- Игривый, ностальгически-пиксельный, ламповый community-вайб
- Экономика/торговля в центре: «сколько это в World Lock'ах?», «сколько DL у тебя в банке?»
- Kid-friendly, но с уличной смекалкой (осторожно со скамами)
- Хайп вокруг редких сетов и дропа с ивентов
- Язык: English (основной), Russian

### Примеры фраз
- "How many World Locks is THIS worth?"
- "I turned 1 WL into a Diamond Lock — here's how"
- "The rarest set in Growtopia just dropped..."
- "Don't get scammed: the oldest trick in Growtopia"
- "Building the craziest world with 100 DLs"

---

## Форматы для этой игры

- **`top-list`** — топ самых дорогих/редких предметов и сетов (тир-листы в WL/DL)
- **`fun-news`** — новости: новый ивент (Growmas, Startopia), апдейт, редкий дроп
- **`what-if-real-life`** — «а если бы Growtopia-предметы существовали в реальном мире»
- **`character-story`** — лор культового сета (Legendary Wizard, Zeus, Growganoth)
- **`reddit-story`** — житейские истории про торговлю/скамы/дружбу в игре (игра — фон)
- **`dual-style`** — пиксельный предмет vs его «реалистичная» версия

> Пиксель-стиль будет уточняться пер-формат (user override): в некоторых форматах допускается «Growtopia-inspired» более отрисованный вид.

---

## Музыка

- **Mood:** playful, nostalgic, upbeat, chiptune / 8-bit
- **BPM:** 110–140
- **Рекомендуемые треки:** retro chiptune adventure, upbeat sandbox loop, nostalgic 8-bit theme

---

## Игровой сленг

| Термин | Значение |
|--------|----------|
| WL | World Lock — базовая валюта; замок, защищающий/маркирующий мир |
| DL | Diamond Lock — 100 WL, средняя валюта |
| BGL | Blue Gem Lock — 100 DL (10 000 WL), крупная валюта |
| Gems | Гемы — внутриигровая валюта, фармится с блоков, тратится на крафт |
| Growtoken | Токены с ивентов, тратятся на эксклюзивные предметы |
| Farmable | Предмет/блок, который можно фармить ради гемов или профита |
| BFG | Break For Gems — ломать блоки ради гемов |
| GrowID | Аккаунт/никнейм игрока |
| World | Персональный мир игрока — площадка для стройки/фарма/торговли |
| Vend / Display Box | Витрина/торговый ящик для продажи предметов за WL |
| Legendary set | Культовый дорогой сет (Wizard, Zeus, Angelic и т.п.) |
| Scam | Обман при сделке — бич игры; «anti-scam» = правила безопасной торговли |
| Providence | Механика создания редких Growtoken-предметов |
| Focused Eyes | Знаковый косметический предмет (светящиеся глаза) |
| Growmas | Рождественский ивент Growtopia |
| Startopia | Космический сезонный ивент |
| Harvest Festival | Осенний ивент со сбором урожая |
| Growganoth | Рейд-босс, мировой ивент-монстр |
| Surg / Surgery | Мини-игра «хирургия» на ивентах ради предметов |
| Punch / Wrench | Основные действия: удар (ломать/строить) и гаечный ключ (настройки блока) |
| Doorbell | Механика приглашения игроков в мир |

---

## CTA

- **Статус:** ✅ ГОТОВ (2026-07-17)
- **Видео:** `assets/growtopia/branding/cta.mp4` — `game_assets` (`asset_type=generated_ref`, `character_name=branding:cta`, tags `cta,branding`). Editor находит по тегу `cta`.
  - `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/branding/cta.mp4`
- **Контент:** пиксельная Growtopia-сцена, текст «Get free gems» / «Link in bio» + стрелка вниз, гемы, солнце. 3s, ~9:16 (720×1280 из Kling; Editor масштабирует в 1080×1920).
- **Источник кадра:** `assets/growtopia/branding/cta-source.png` (ChatGPT-арт). Анимирован Kling v3 I2V (idle-v2): камера залочена, двигаются только стрелка (боб) + шиммер солнца, всё остальное статикой.
- **⚠️ Урок (2026-07-17):** Kling I2V **морфит текст даже на минимальном idle** — проверено на v1 (много движения) И v2 (двигались только стрелка+солнце, текст явно заморожен негативами) → текст всё равно «прыгал». Вывод: **текстовый CTA через I2V чисто не сделать.** Правильный путь для текстовых CTA — **композитинг** (анимировать фон в Kling БЕЗ текста, текст накладывать статик-оверлеем через ffmpeg), либо статичный CTA. Баунс стрелки к тому же выходит резким. Текущий `cta.mp4` (v2) принят как «сойдёт», но с этим дефектом текста. Полный разбор — `rules/roles/animator.md §3.2`.

## Pop-up (overlay-плашка)

- **Статус:** ✅ ГОТОВ (2026-07-17)
- **Картинка:** `assets/growtopia/branding/popup.png` — `game_assets` (`asset_type=generated_ref`, `character_name=branding:popup`, tags `popup,overlay,branding`).
  - `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/branding/popup.png`
- **Контент:** горизонтальный баннер «Get FREE GEMS! / Link in Bio!» с гемами, майнером-персонажем, сундуком. Для наложения оверлеем на видео (не фуллскрин-CTA).

---

## Opener

- **Статус:** TODO — ассет не загружен
- **Контент (план):** пиксельная анимация появления блочного мира + логотип Growtopia
- **После генерации:** залить в Supabase `assets/growtopia/branding/opener.mp4`
- **Формат:** 1080×1920, 30fps, ~2s
