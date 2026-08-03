# Growtopia

## Posting status

- **ready_to_post:** yes   <!-- yes only when the game is tested and cleared for posting -->

**Formats (linked to this game):**

- character-story — ready_to_post: yes (tested 2026-07-17, final.mp4 produced)
- top-list — ready_to_post: yes (untested — first run pending)
- fun-news — ready_to_post: yes (untested — first run pending)
- what-if-real-life — ready_to_post: yes (untested — first run pending)
- reddit-story — ready_to_post: yes (tested 2026-07-22, final.mp4 produced and approved)
- dual-style — ready_to_post: yes (tested 2026-07-22, final.mp4 produced)

> ⚠️ **No YouTube channel mapped yet** (`youtube_channel: none`). Per Phase 6 routing rule, YT upload is skipped until a channel is mapped — deliverable stays Supabase-only. Also no opener asset yet (CTA + pop-up are ready).


> TODO(style-refactor): character appearance must move to per-format story bibles `characters[]` (style-free); style → top-level `style_tags` in the bible, fallback = `prompt_prefix`. This game config not yet migrated (see star-trek-timelines / genshin-impact for the pattern).

> DONE (2026-07-16): 39 NPC/character reference sprites uploaded to Supabase, incl. the canonical default-skin Growtopian avatar. Full list and URLs in `## Референсные изображения (Supabase)` below.

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

### Approved generated-video treatment — pseudo-isometric 2.5D (user-locked 2026-07-24)

For newly generated vertical videos, use a **bright pseudo-isometric 2.5D pixel-art diorama** unless the exact format/series story bible or a live user instruction explicitly requires the legacy side-view treatment:

- Native edge-to-edge 9:16 with a large foreground, readable midground action platform and receding background tiles.
- Front-facing or three-quarter Growtopians and products share one coherent projected grid with the blocks and shadows.
- Crisp illustrated pixel art with thick outlines and a cheerful cyan/green/gold palette.
- Preserve Growtopia identity without becoming Minecraft, voxel sculpture, smooth CGI or photoreal 3D.
- Do not paste flat side-view sprites into a perspective environment.

Suggested prompt block:
```
Growtopia-inspired crisp 2D pixel art, pseudo-isometric 2.5D diorama, blocky pixelated proportions, thick clean black outlines, bright cheerful cyan green and gold palette, coherent three-quarter projection, layered foreground midground and receding tile platforms, native edge-to-edge vertical 9:16, illustrated perspective rather than volumetric 3D, no Minecraft, no voxel CGI
```

### ⚠️ Kling I2V — no Elements by default (user-locked 2026-07-24)

**Do not attach separate Kling Elements for Growtopia by default.** The approved pseudo-isometric test showed excessive character/product geometry morphing when Elements were attached. Animate the complete approved scene PNG directly; an Element is allowed only after an explicit live user request.

- The start frame must already contain the final coherent character, product, Gems, text and perspective.
- Prefer near-locked shots, tiny character actions, restrained particles and subtle differential parallax.
- Avoid camera orbits, perspective flips, large body turns and object reconstruction.
- For timers or exact diegetic text, bake the exact value into the start frame and keep the shot nearly static.
- Never ask Kling to redraw, count down or rotate text-bearing objects.

### Legacy flat side-view Kling branch — "Minecraft morph" (burned 2026-07-17)

The guidance below applies only when the exact format/series bible or the user explicitly selects the legacy flat side-view treatment.

The blocky Growtopia skin **very easily morphs into a 3D Minecraft look** under I2V. `NOT Minecraft` negatives do NOT fix it — it is fixed by start-frame composition and camera motion (full write-up in `rules/roles/animator.md §3.2`). In short, for growtopia pixel scenes:
- **Grounded composition is mandatory:** the character stands inside a full flat tiled Growtopia world (platforms, blocks, World Lock — reading like a "2D game screenshot"). Do NOT isolate the sprite on empty sky and do NOT place it in a perspective 3D "cave" — in both cases Kling reconstructs voxel 3D.
- **Camera:** a gentle push-in toward the character, or near-locked. No pull-backs / fly-overs "above the block world" and no orbits "toward frontal" — those trigger 3D reconstruction.
- **Do not rotate the sprite:** no head/body turns to frontal (a side-view sprite has no valid 3D frontal view).
- Liveliness comes from 2D particles and environment, not from camera motion.

**"2D side-scroller" style-anchor phrasing — pick by static vs. dynamic (tested 2026-07-20, scene-6, both variants passed):**
- **Static shot** (character idle/holding pose, no traversal): add the side-scroller/platformer framing (e.g. "2D side-scrolling platformer game scene, flat side-view like Mario or Terraria") purely as a **style-anchor phrase**, paired with the grounded-composition + locked/push-in camera rules above — NO lateral camera track, NO background scroll. This is the "safe" branch — default here.
- **Dynamic shot** (character explicitly traversing/running/jumping across the world): the side-scroller framing may drive an actual **horizontal camera track or background tile-scroll** (camera follows the character sideways, or the world scrolls past) — this is the "risky" branch and is more likely to trip the 3D/voxel reconstruction than the safe branch, so treat it as a deliberate trade for traversal motion, not a default. Keep "flat 2D sprite, no rotation, no 3D volume" in the prompt and negatives regardless.

### Default-skin costume — locked
Canon is fixed (see the LOCKED block in `## Character Prompt Blocks` → Growtopian Avatar, and `games/growtopia/character-story_story_bible.json.characters[].canonical_costume`): tan skin, **cyan/turquoise shirt (~#3FC1D6)**, **medium-blue pants (~#5B6DC8)**. Otherwise NB2 drifts the colors from scene to scene (seen: nude / red / cyan within one video) — always spell out the exact colors in every scene prompt.

---

## Character Prompt Blocks

> Growtopia не имеет фиксированных героев — есть кастомный аватар игрока (Growtopian), культовые сеты и знаковые предметы/существа. Блоки ниже покрывают типовые аватары + иконические сеты + предметы-символы.

### Аватары и сеты

#### Growtopian Avatar (base player) — LOCKED default-skin costume
> The default-skin canon is fixed so NB2 stops producing different colors from scene to scene. Skin tan/beige (~#C9A67C), shirt bright cyan/turquoise (~#3FC1D6), pants medium-blue (~#5B6DC8), white eyes with black pupils, thick outline, no hats/sets.

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

**Status: ✅ READY (uploaded 2026-07-16, PR #90 merged).** 39 NPC/character reference sprites live in Supabase (`game_assets`, `asset_type=reference_image`, `game_tag=growtopia`, path `assets/growtopia/characters/{slug}/sheet.png`). Full manifest with names/slugs/URLs: `games/growtopia/assets/refs/npcs.json`.

| Персонаж / предмет | Supabase URL |
|--------------------|--------------|
| A Burglar | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/a-burglar/sheet.png |
| Alan, The Alien | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/alan-the-alien/sheet.png |
| Alien Computer | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/alien-computer/sheet.png |
| Alien Menace | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/alien-menace/sheet.png |
| Alien Ship | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/alien-ship/sheet.png |
| Boss Ghost | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/boss-ghost/sheet.png |
| Box of Supplies | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/box-of-supplies/sheet.png |
| Crazy Jim | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/crazy-jim/sheet.png |
| Crime In Progress | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/crime-in-progress/sheet.png |
| Criminal Mastermind | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/criminal-mastermind/sheet.png |
| Dummy Alien Computer | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/dummy-alien-computer/sheet.png |
| Dungeons Cryptkeeper | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/dungeons-cryptkeeper/sheet.png |
| Dungeons Shopkeeper | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/dungeons-shopkeeper/sheet.png |
| Fashion Show Bouncer | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/fashion-show-bouncer/sheet.png |
| Founder of the Fancy Gentleman Club | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/founder-of-the-fancy-gentleman-club/sheet.png |
| Geoff, The Guard | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/geoff-the-guard/sheet.png |
| Growtopian (default skin) | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/growtopian-default-skin/sheet.png |
| Legendary Wizard | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/legendary-wizard/sheet.png |
| Lincoln, The Leprechaun | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/lincoln-the-leprechaun/sheet.png |
| Lock-Bot | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/lock-bot/sheet.png |
| Locke The Salesman | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/locke-the-salesman/sheet.png |
| Mark, The Mechanic | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/mark-the-mechanic/sheet.png |
| Master Peng | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/master-peng/sheet.png |
| Nutcracker | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/nutcracker/sheet.png |
| Pet Battle Gym Healer | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/pet-battle-gym-healer/sheet.png |
| Pet Battle Gym Leader | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/pet-battle-gym-leader/sheet.png |
| Pet Battle Gym Trainer | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/pet-battle-gym-trainer/sheet.png |
| Pet Trainer | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/pet-trainer/sheet.png |
| Robert, The Robot | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/robert-the-robot/sheet.png |
| Shady Salesman | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/shady-salesman/sheet.png |
| ShockBot (disambiguation) | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/shockbot-disambiguation/sheet.png |
| ShooterBot (disambiguation) | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/shooterbot-disambiguation/sheet.png |
| SpikeBot (disambiguation) | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/spikebot-disambiguation/sheet.png |
| The Bartender | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/the-bartender/sheet.png |
| The Bouncer | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/the-bouncer/sheet.png |
| The Monster Nian | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/the-monster-nian/sheet.png |
| The Ringmaster | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/the-ringmaster/sheet.png |
| Tomb Robber | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/tomb-robber/sheet.png |
| Walter, The Manager | https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/characters/walter-the-manager/sheet.png |

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

- **Status:** ✅ READY (2026-07-17)
- **Video:** `assets/growtopia/branding/cta.mp4` — `game_assets` (`asset_type=generated_ref`, `character_name=branding:cta`, tags `cta,video,branding`). Editor finds it by the required `cta` + `video` tags.
  - `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/branding/cta.mp4`
- **Content:** a Growtopia pixel scene, text "Get free gems" / "Link in bio" + a down-arrow, gems, sun. 3s, ~9:16 (720×1280 from Kling; Editor scales to 1080×1920).
- **Source frame:** `assets/growtopia/branding/cta-source.png` (ChatGPT art). Animated with Kling v3 I2V (idle-v2): camera locked, only the arrow (bob) + sun shimmer move, everything else static.
- **⚠️ Lesson (2026-07-17):** Kling I2V **morphs text even on a minimal idle** — tested on v1 (lots of motion) AND v2 (only arrow+sun moving, text explicitly frozen via negatives) → the text still "jumped". Conclusion: **a text-heavy CTA cannot be animated cleanly through I2V.** The right approach for text CTAs is **compositing** (animate the background in Kling WITHOUT text, overlay the text as a static ffmpeg layer), or a static CTA. The arrow bounce also comes out too harsh. The current `cta.mp4` (v2) was accepted as "good enough" but carries this text defect. Full write-up in `rules/roles/animator.md §3.2`.

## Reddit Story production assets

- **Status:** ✅ TESTED (2026-07-22). The first approved episode is recorded in `games/growtopia/reddit-story_bible.json`.
- **Game-specific rules:** `games/growtopia/reddit-story_special.md`.
- **Background:** `game_assets` (`asset_type=generated_ref`, `character_name=location:reddit-story`, tags `reddit-story-bg,bg-ref,location`).
  - `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/locations/reddit-story.png`
- **Gameplay clip 01:** `game_assets` (`asset_type=gameplay_clip`, `character_name=growtopia-gameplay-01`, tags `gameplay,reddit-story,vertical`).
  - Local mirror: `games/growtopia/assets/Growtopia 1.mp4`
  - `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/gameplay/growtopia-01.mp4`
- **Gameplay clip 02:** `game_assets` (`asset_type=gameplay_clip`, `character_name=growtopia-gameplay-02`, tags `gameplay,reddit-story,vertical`).
  - Local mirror: `games/growtopia/assets/growtopia 2.mp4`
  - `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/gameplay/growtopia-02.mp4`
- **Approved episode:** `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/videos/growtopia/2026-07-22/reddit-story/20260722-173047-reddit-cousin-world/final.mp4`

## Pop-up (overlay banner)

- **Status:** ✅ READY (2026-07-17)
- **Image:** `assets/growtopia/branding/popup.png` — `game_assets` (`asset_type=generated_ref`, `character_name=branding:popup`, tags `popup,overlay,branding`).
  - `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/branding/popup.png`
- **Content:** a horizontal banner "Get FREE GEMS! / Link in Bio!" with gems, a miner character, and a chest. For overlaying on videos (not a full-screen CTA).

---

## Opener

- **Статус:** TODO — ассет не загружен
- **Контент (план):** пиксельная анимация появления блочного мира + логотип Growtopia
- **После генерации:** залить в Supabase `assets/growtopia/branding/opener.mp4`
- **Формат:** 1080×1920, 30fps, ~2s
