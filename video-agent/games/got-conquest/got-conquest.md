# Game of Thrones: Conquest

## Posting status

- **ready_to_post:** no   <!-- yes only when the game is tested and cleared for posting -->

**Formats (linked to this game):**

- fake-ad — ready_to_post: no
- fun-news — ready_to_post: no


> TODO(style-refactor): character appearance must move to per-format story bibles `characters[]` (style-free); style → top-level `style_tags` in the bible, fallback = `prompt_prefix`. This game config not yet migrated (see star-trek-timelines / genshin-impact for the pattern).

## Метаданные

- **Жанр:** Strategy / MMO
- **Платформа:** iOS, Android
- **Разработчик:** Warner Bros. Games
- **Аудитория:** Global, фанаты GoT (25-45), стратегические игроки
- **Стиль арта:** Dark fantasy, cinematic medieval, fire-and-ice duality — Lannister gold vs Stark grey vs Targaryen fire
- **Premiere:** October 2017
- **youtube_channel:** _unmapped_ (нужен mapping перед public-загрузкой)

---

## Концепция игры

Игрок строит замок в Вестеросе, собирает великих лордов и королей, ведёт войны за Железный Трон. Лор напрямую взят из сериала HBO и книг Джорджа Мартина. Персонажи, дома, локации — канонические. Ресурсы: Gold, Food, Stone, Wood. Основной CTA: «Claim Resources — Tap > Link in Bio».

---

## Visual Style Guide

### Цветовая палитра
- Основные: castle stone (#2d2d2d), Lannister gold (#c9a84c), ice-white (#e8f4f8), dragon-fire orange (#e8621a)
- Акценты: blood red (#8b0000), Night's Watch black (#0f0f0f), wildfire green (#39ff14)
- Небо: perpetually overcast grey (Westeros) OR dramatic sunset/fire (Targaryen)
- Ice: The Wall — deep blue-white glacier, frozen blue sky

### Освещение
- Interior castle: torchlight from sconces, warm amber-orange key light, deep cold shadows
- The Wall / North: cold blueish overcast daylight, wind-blur particles, harsh rim light
- Dragon scenes: orange-red fire glow from below/behind, dramatic contrast
- News desk (anchor): single warm torch-bracket overhead + candelabra on table, deliberate cinematic key-light on face

### Композиция
- **Semi-realistic photographic cinematic quality** — NOT cartoon, NOT illustration, NOT animation
- 9:16 vertical, medium close-up for anchor/reporter faces (chin to top of head with 20% headroom)
- Mouth slightly open mid-speech for lipsync
- Professional broadcast key-light on face — dark BG keeps GoT vibe
- Props in frame but not centered (goblet, scroll, torch) — character is the focal point

### Prompt prefix
```
Game of Thrones cinematic aesthetic, semi-realistic photographic cinematic quality, NOT cartoon NOT illustration NOT animation NOT digital art, dramatic torchlight medieval atmosphere, 9:16 vertical, broadcast framing medium close-up, professional key-light on face
```

---

## Character Prompt Blocks

### Tyrion Lannister (anchor — locked)
```
semi-realistic male character, short stature dwarf lord, broad face with prominent forehead and wide jaw, short sandy-blonde tousled hair, pale skin, sardonic smirk with one eyebrow raised, mismatched eyes (one green, one darker scarred), richly embroidered crimson-and-gold doublet with Lannister lion clasp, seated at carved stone news-desk with parchment scrolls and gold goblet of red wine, warm amber torchlight from above-left, Lannister castle stone chamber background with lion banners dim behind, mouth slightly open mid-sentence for lipsync, broadcast key-light on face, NOT cartoon NOT illustration
```

### Varys (reporter — politics / King's Landing / intrigue)
```
semi-realistic male character, completely bald head smooth with slight sheen, heavy-set round face, no beard no eyebrows (very sparse barely visible), pale skin with slight heaviness under eyes, knowing slight smile — enigmatic not warm, rich embroidered deep-purple robes with silver embroidery at collar, standing in shadowy stone corridor of Red Keep, single torch sconce on wall behind casting orange rim-light and long shadows, holding a parchment scroll loosely in one hand, mouth slightly open mid-speech for lipsync, professional key-light on face, NOT cartoon NOT illustration
```

### Jon Snow (reporter — Night's Watch / The Wall / North)
```
semi-realistic young male character, athletic medium build, long curly dark-brown-black hair past jaw, short trimmed dark beard, brooding dark eyes with slight squint, stoic serious expression mouth slightly open mid-speech, heavy black wool Night's Watch cloak with fur trim at collar, standing at The Wall — massive ice cliff behind him, cold blue-white icy sky, blizzard particles in air, harsh cold rim-light from the ice behind, broadcast key-light on face, NOT cartoon NOT illustration
```

---

## Tone of Voice

- **Anchor (Tyrion):** dry wit, patrician sarcasm, delivers absurdity with complete sincerity — as if the news is obviously correct and the world is obviously broken. Short sentences. Wine-goblet energy.
- **Reporters:** tonally opposite to each other — Varys: conspiratorial whisper-to-normal, hints at knowing more than he says; Jon Snow: flat deadpan, monotone delivery that makes absurd content funnier
- **Universe tone:** kayfabe-straight — everything in Westeros is treated as real, serious, and fully documented by official institutions
- **Mock-institutional:** Maesters, Small Councils, Iron Throne Bureaus, Royal Inspectorates — applied with full bureaucratic gravity to GoT absurdities
- English language (for Avatar v2 lipsync), English subtitles

### Sample phrases
- "Good evening — Tyrion Lannister, Game of Thrones Daily, where every throne has a price and no one reads the contract."
- "The Small Council's Environmental Impact Assessment cited, quote, 'fire-based regulatory non-compliance.'"
- "The Night's Watch Annual Performance Review ends — and I will quote this exactly — with a hand-drawn question mark."
- "King's Landing Animal Control has declined to comment. Their clipboards were unavailable."

---

## Fun News — Reporter Pool

### Stage-1 (пилот)
- **Varys** — политика, интриги, Королевская Гавань, Малый Совет
- **Jon Snow** — Ночной Дозор, Стена, Север, Одичалые

### Stage-2 (эпизод 3+)
- **Cersei Lannister** — политика, дворец, вино, власть
- **Daenerys Targaryen** — драконы, Таргариены, Эссос
- **Bran Stark** — мистика, видения, Трёхглазый Ворон
- **Petyr Baelish (Мизинец)** — финансы, интриги, Вале

---

## CTA

- **Источник:** пользовательский packshot (`.context/attachments/xqGUq5/got packshot.png`)
- **Контент:** Game of Thrones Conquest logo + "CLAIM RESOURCES" + Gold / Food / Stone / Wood + "TAP > LINK IN BIO"
- **Анимация:** Kling I2V 5s — dramatic fire+ice zoom: fire-side (left) ignites inward, ice-side (right) crystallizes, packshot emerges from centre with camera pull-in; resource cards pulse with glow; no audio
- **Формат:** 1080×1920, 30fps, ~5s
- **После генерации:** залить в Supabase `assets/got-conquest/branding/cta.mp4`

---

## Opener

- **Название шоу:** Game of Thrones Daily
- **Контент:** Title card "GAME OF THRONES DAILY" — old-english serif font, gold on dark stone texture + Westeros map silhouette faint in BG + dragon silhouette flying across
- **Анимация:** Kling I2V 2s — torchlight flicker, slight camera push, dragon silhouette passes corner of frame; без аудио (тема добавляется Editor через bg-music)
- **Формат:** 1080×1920, 30fps, ~2s
- **После генерации:** залить в Supabase `assets/got-conquest/branding/opener-fun-news.mp4`

---

## Music

- **Mood:** dark epic medieval — orchestral, strings + low brass, stately but with ironic edge (NOT triumphant, NOT tragic — think "official ceremony that everyone knows is corrupt")
- **BPM:** 70-100
- **Стиль:** cinematic medieval orchestral; допускается light percussion
- **Volume:** 0.15 в Editor's amix
- **Поиск в `music/tracks.json`:** filter `use_for` includes `news` OR `mood ∈ {dark, dramatic, cinematic}`
- **Тема для опенера и пэкшота:** тот же трек — нарастание к финалу (crescendo на последних 2s перед CTA)

---

## Ambient / Интершум для сцен репортёра (fun-news specific)

- **Варис (King's Landing corridors):** ambient — distant castle echo, torch crackle, occasional stone step, whisper breath. Low volume, barely audible.
- **Джон Сноу (The Wall):** ambient — howling wind, ice creak, distant crow call. Layered under TTS.
- **Применение:** Sound role добавляет ambient track per-scene as a second audio layer; Editor миксует under TTS at volume 0.12–0.18.

---

## Anti-patterns

- ❌ Cartoon/stylized refs для anchor и репортёров — ломает Avatar v2 lipsync
- ❌ Real GoT show screenshots или official IP art в quality промптах без disclaimer
- ❌ Реальные сюжетные события из сериала как новости (используем канон как основу сатиры, не пересказываем)
- ❌ Слишком эпичный/трагичный тон музыки — формат комедийный, музыка фоновая
- ❌ Tyrion delivering 30+ word lines — формат требует тесноты (15-20 слов anchor scenes)
