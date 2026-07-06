# WWE Champions

> TODO(style-refactor): character appearance must move to per-format story bibles `characters[]` (style-free); style → top-level `style_tags` in the bible, fallback = `prompt_prefix`. This game config not yet migrated (see star-trek-timelines / genshin-impact for the pattern).

## Метаданные

- **Жанр:** Match-3 Puzzle RPG / Sports Brawler (Gacha)
- **Платформа:** iOS, Android
- **Разработчик:** Scopely
- **Аудитория:** Global, фанаты WWE (рестлинг 25-45), match-3 / gacha-игроки
- **Стиль арта:** Stylized semi-realistic 3D рестлеры, яркая арена-эстетика, неон + chrome, ring-side prop art
- **Премьера:** Декабрь 2017
- **youtube_channel:** _unmapped_ (нужен mapping в queue/youtube-upload.sh перед public-загрузкой)

---

## Концепция игры

Игрок собирает roster рестлеров WWE из всех эпох (Attitude Era, Ruthless Aggression, PG Era, Modern), прокачивает их и устраивает кейфейб-матчи в match-3 puzzle-формате. Roster: 250+ суперзвёзд от Hulk Hogan до Roman Reigns. Игроки строят фракции, участвуют в Showdown PvP, Faction Wars и сюжетных сториках с лицензированной WWE-лорой.

**Тон вселенной — кейфейб:** рестлеры подаются как реальные сверхчеловеки с каноничными приёмами, finishers, raldownвинами. Сатира должна играть с этим, не ломая.

---

## Visual Style Guide

### Цветовая палитра
- Основные: arena black (#0a0a0a), WWE red (#d72027), ring-side white (#f5f5f5), chrome silver (#c0c0c0)
- Акценты: title-belt gold (#ffd700), spotlight blue (#1e90ff), pyrotechnic orange (#ff6a00)
- Рарити: bronze, silver, gold, platinum, diamond

### Освещение
- Spot-light от прожекторов арены сверху и сбоку
- Pyrotechnic вспышки (взрывной свет на entrance-сценах)
- Тёмный фон арены, яркие точечные источники
- Ringside cinematic — глубокие тени + контурный свет на мышцах

### Композиция
- Рестлеры: **semi-realistic photographic cinematic quality**, NOT cartoon, NOT illustration. Игра использует stylized 3D, но для Fun News (где идёт Avatar v2 lipsync) приоритет — semi-realistic, чтобы лицо хорошо синкалось.
- Фон: ringside, locker room, backstage corridor, parking lot (классические WWE backstage tropes)
- 9:16 vertical для mobile-first
- Title-belt props, ropes, ring posts — часть кадра, не центр

### Стилистические ограничения
- **НЕ cartoon, НЕ chibi, НЕ stylized 3D для лиц** — это ломает Avatar v2 lipsync
- Pat McAfee и репортёры должны выглядеть **как живые люди** в кадре, не как игровые модели
- Гипертрофированные мышцы — ОК для wrestlers, но черты лица photoreal
- НЕ использовать слова "WWE Champions style", "match-3 UI", "Scopely" в промптах — модель переопределит стиль

### Prompt prefix
```
WWE wrestling broadcast aesthetic, semi-realistic photographic cinematic quality, NOT cartoon NOT illustration NOT animation, dramatic ringside spotlight lighting, 9:16 vertical, broadcast TV studio framing, professional sports network composition
```

---

## Фракции / Эпохи

| Эра | Период | Key superstars |
|---|---|---|
| Golden Era | 1985-1993 | Hogan, Macho Man, Ultimate Warrior, Andre the Giant |
| New Generation | 1993-1997 | Bret Hart, Shawn Michaels, Undertaker (debut) |
| Attitude Era | 1997-2002 | Stone Cold, The Rock, Mankind, DX |
| Ruthless Aggression | 2002-2008 | John Cena (rise), Batista, Brock Lesnar, Edge |
| PG Era | 2008-2014 | Cena (peak), Punk, Daniel Bryan, Sheamus |
| Reality Era | 2014-2016 | Roman Reigns, Seth Rollins, Dean Ambrose (Shield) |
| New Era / Modern | 2016+ | Becky Lynch, Bray Wyatt, AJ Styles |
| Bloodline Era | 2020+ | Roman Reigns (Tribal Chief), Sami Zayn, Solo Sikoa, Jey Uso, Cody Rhodes |

---

## Reporter pool — fun-news / character roster

### Anchor (locked для WWE Champions)
**Pat McAfee** — реальный WWE-комментатор (RAW lead). Энергичный, орущий, sportsbook-vibes, бывший NFL-пунтер. На fun-news подаётся как stylized news-anchor с микрофоном за студийным столом WWE Network.

### Stage-1 reporters (в production)
- **The Undertaker** — мистические / потусторонние сюжеты
- **John Cena** — patriotic / комедийные / "невидимые" сюжеты
- **Becky Lynch** — feminist / empowerment-сатира
- **Roman Reigns** — power / corporate / Bloodline сюжеты

### Stage-2 reporters (на стадии stage-1 «примелькаются», ~эпизод 3+)
- **Rhea Ripley** — eternal goth / dark mami сюжеты
- **Cody Rhodes** — legacy / "finish the story" сюжеты
- **CM Punk** — straight-edge / "best in the world" / pipe bomb сюжеты
- **Brock Lesnar** — part-time / suplex city / "beast" сюжеты

---

## Character Prompt Blocks

### Pat McAfee (anchor, locked)
`semi-realistic male sports broadcaster, athletic build, short close-cropped sandy brown hair, clean-shaven, friendly energetic open-mouthed smile showing teeth, navy blazer over black t-shirt with sleeves rolled up, sitting at WWE Network news desk with red and chrome WWE branding behind, broadcast TV studio key light on face, holding microphone with WWE Champions logo, deep ringside-spotlight rim light, NOT cartoon NOT illustration`

### The Undertaker (reporter — mystical/dark themes)
`semi-realistic male professional wrestler, tall imposing 6'10 build, long straight black hair past shoulders, pale ghostly complexion, deep sunken eyes with dark eyeliner-like shadow, neatly trimmed dark goatee, long black duster trench coat over black tank top, black wide-brim hat held in one hand, weathered serious expression, dim funeral-parlor lighting with single overhead spotlight, NOT cartoon NOT illustration`

### John Cena (reporter — patriotic/comedy themes)
`semi-realistic male professional wrestler, athletic muscular build, very short buzz-cut brown hair, clean-shaven boyish face, bright wide grin showing teeth, fluorescent neon-green Cena t-shirt with logo, jean shorts, sweatband on wrist, holding microphone, bright daylight outdoor airport TSA checkpoint background visible behind, broadcast TV crew lighting, NOT cartoon NOT illustration`

### Becky Lynch (reporter — empowerment/feminist satire) — stage 1
`semi-realistic female professional wrestler, athletic build, long wavy bright red-orange hair past shoulders, piercing blue-green eyes with smudged dark eye makeup, mild smirk, leather steampunk-style jacket over black tank top, holding microphone, WWE women's locker room background, broadcast lighting, fierce confident posture, NOT cartoon NOT illustration`

### Roman Reigns (reporter — power/Bloodline themes) — stage 1
`semi-realistic male Samoan professional wrestler, athletic powerful build, long straight black hair past shoulders, neatly trimmed full black beard, intense piercing dark eyes, slight smirk, all-black vest over bare muscular chest, ornate gold chain necklace with Samoan tribal pendant, dim corporate office lighting with chrome accents, NOT cartoon NOT illustration`

---

## Tone of Voice

- Кейфейб-серьёзный с ironic-satire слоем поверх
- Sports broadcast энергия (Pat McAfee яркий пример) — короткие предложения, capital-letter intensity
- Mock-bureaucratic для шуток: реальные госагентства (OSHA, TSA, IRS, FAA) подаются на полном серьёзе в комплекте с кейфейбными приёмами
- Никакого "kayfabe vs reality breaking" внутри сюжета — даже сатира остаётся в-кейфейб
- Английский язык (для I2V / Avatar v2 моделей), субтитры английские

### Примеры фраз
- "Hey folks, Pat McAfee here with Kayfabe News — and tonight we are COOKED."
- "OSHA officials are still trying to figure out what 'tombstone piledriver' means."
- "DARPA confirms the Cena cloaking signature is real. The FAA is grounding all flights."
- "Acknowledge me. As your accredited HR trainer."

---

## Игровой сленг (для сценариев и кейфейб-сатиры)

| Термин | Значение |
|--------|----------|
| Kayfabe | The maintained illusion that wrestling is real |
| Heel | Bad guy (sometimes ironic) |
| Babyface / Face | Good guy |
| Heel turn | Good→Bad character flip |
| Face turn | Bad→Good character flip |
| Squash match | One-sided victory |
| Spot | Pre-planned move sequence |
| Finisher | Signature move that wins the match |
| Jobber | Wrestler whose role is to lose |
| Over | Crowd is invested in this wrestler |
| Heat | Crowd reaction (positive or negative) |
| Pop | Sudden loud crowd reaction |
| Selling | Acting like a move hurts |
| Botch | Move executed badly |
| Mark | Fan who believes kayfabe |
| Smark | Smart-mark; fan aware of kayfabe but still invested |
| Bloodline | Roman Reigns' Anoa'i family faction |
| Tribal Chief | Roman Reigns self-given honorific |
| Money in the Bank | Briefcase that grants championship contract |
| Hell in a Cell | Cage match inside a roofed steel structure |
| You can't see me | John Cena catchphrase / "invisibility" meme |

---

## Идеи для контента

### Fun News themes (satirical-kayfabe)
- Финишеры рестлеров — нарушение OSHA / safety code
- WWE Universe HR — корпоративные процедуры применённые к кейфейбу (harassment training, grief counseling)
- Реальные госагентства (TSA, DARPA, IRS, FAA, SEC) реагируют на кейфейб-явления как на реальные угрозы
- Patent / trademark abuse (Cena "you can't see me", Becky "The Man")
- Pyrotechnic / arena safety — реалистичное отношение к фантастическим элементам
- Bloodline family law / inheritance / tax claims

### Top-list / news (game-side контент)
- Top-5 rosters для PvP
- Best Finishers Tournament
- "Когда открыл MITB pack и достал jobber..."

---

## CTA

- **Источник:** пользовательский packshot (см. `.context/attachments/rIv2ln/wwe packshot.png`)
- **Контент:** WWE Champions logo + "CLAIM RESOURCES" + Coins / Cash / Keys / Shards + "TAP > LINK IN BIO"
- **Анимация:** Kling I2V 5s, лёгкий параллакс + свечение ресурсов, без аудио. После генерации залить в Supabase `assets/wwe-champions/branding/cta.mp4`.
- **Формат:** 1080×1920, 30fps, ~5s

---

## Opener

- **Контент:** title-card "KAYFABE NEWS" сверху + WWE Champions logo (вырезанный из packshot) по центру + ringside-style фон с red/chrome
- **Анимация:** Kling I2V 2s, лёгкая pyrotechnic вспышка + камера-pull-in. Без аудио (звук добавляет Editor через bg-music).
- **Формат:** 1080×1920, 30fps, ~2s
- **После генерации:** залить в Supabase `assets/wwe-champions/branding/opener.mp4`

---

## Music

- **Mood:** energetic / fun / sports broadcast intro
- **BPM:** 100-130
- **Стиль:** rock / percussion-driven, без резких vocals, под комедийный sports-вайб. Не использовать heavy metal (агрессивно), не использовать orchestral epic (слишком серьёзно для сатиры).
- **Volume:** 0.15 в Editor's amix
- **Поиск в `music/tracks.json`:** filter `use_for` includes `news` OR `mood ∈ {fun, energetic, comedic}`

---

## GLN Channel Branding

WWE Champions **не** входит в Galactic Lol Network (ST-Timelines own brand). Для WWE свой brand-bug опционален. **На пилот brand-bug отключён** — добавим позже, если будет смысл (пока контент сетки маленький).

---

## Anti-patterns

- ❌ Cartoon / stylized 3D refs для anchor / репортёров — ломает Avatar v2 lipsync
- ❌ Использовать реальные WWE logos / belts в качестве prop без disclaimer (это IP Endeavor). На сатиру kayfabe-news хватает abstract "wrestling broadcast" фона
- ❌ Реальный текст реальных WWE storylines — пишем fictional satirical headlines, как Onion
- ❌ Heavy metal / aggressive music — формат комедийный, музыка должна быть лёгкой
- ❌ Слишком долгие speeches от Pat McAfee — формат требует быстрого темпа (15-20 слов на anchor scene)
