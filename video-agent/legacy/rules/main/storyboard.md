# Правила сторибоарда

Перед любой генерацией изображений или видео ты ОБЯЗАН написать полный сторибоард. Без сторибоарда генерация запрещена.

---

## 1. Visual Identity (единый на всё видео)

Определи и зафиксируй визуальный стиль ДО генерации. Эти поля будут **дословно повторяться** в промптах каждой сцены.

```json
{
  "visual_identity": {
    "character_description": "конкретное описание персонажа — имя, одежда, оружие, причёска, телосложение, выражение лица",
    "environment_description": "конкретное описание окружения — локация, время суток, атмосфера, ключевые объекты",
    "style_tags": "из game config prompt_prefix",
    "color_palette": "из game config",
    "lighting": "из game config",
    "camera_style": "cinematic low angle / medium shot / etc"
  }
}
```

**Правила:**
- `character_description` берётся из `games/{GAME_TAG}/{GAME_TAG}.md` → секция "Character Prompt Blocks"
- Если блока нет — напиши сам, максимально детально (8+ визуальных деталей)
- `environment_description` — конкретная локация из игры, не абстрактная
- Не используй расплывчатые слова ("красивый", "крутой"). Только конкретика ("silver armor with blue engravings")

---

## 2. Narrative Arc (сюжетная арка)

Каждое видео имеет story beats (сюжетные биты):

| Beat | Цель | Пример |
|------|------|--------|
| **hook** | Зацепить внимание | Шокирующий факт, вопрос, провокация |
| **development** | Раскрыть тему, нарастить | Примеры, аргументы, нарастание |
| **climax** | Кульминация | Самый мощный момент, пик эмоции |
| **cta** | Призыв | "Подписывайся!", overlay на последнем клипе |

CTA — не отдельный клип, а overlay на последнем.

---

## 2.1 Пейсинг: beats → клипы

**КРИТИЧЕСКОЕ ПРАВИЛО:** Story beat ≠ клип. Beat — сюжетная единица, клип — техническая (5 или 10 сек: Kling 5s для hook/CTA, 10s для development/climax).

**Один клип = 5 или 10 сек (Kling: 5s для hook/CTA, 10s для development/climax).** Оценивай, сколько ДЕЙСТВИЯ в каждом beat:

| Действия на beat | Решение | Пример |
|-----------------|---------|--------|
| Мало (сидит, стоит, грустит) | **Объедини 2 beats в 1 клип** | "Грустный рейдер + к нему подходят буллеры" = 1 клип |
| Нормально (говорит реплику, жестикулирует) | **1 beat = 1 клип** | Стендап: одна шутка = один клип |
| Много (битва, погоня, взрыв + реакция) | **1 beat = 1 клип** | Находка легендарного лута = отдельный клип |

**Как объединить 2 beats в 1 клип:**
- В `motion_prompt` опиши два этапа: `"First 4 seconds: [действие 1]. Then: [действие 2]"`
- `image_prompt` показывает НАЧАЛЬНЫЙ кадр (первый beat)
- В `beats` перечисли оба бита: `["hook", "development"]`

**Таблица количества клипов (Approach 2 — I2V/T2V):**

| Тип контента | Story beats | Клипов | Итого |
|-------------|------------|------------|-------|
| Простая история / мораль | 4-5 beats | **3 клипа** | ~15-30 сек |
| Стендап / комедия | 3 beats | **3 клипа** | ~15-30 сек |
| Многопероснажный (1 герой = 1 часть) | по героям | **по 1 клипу на героя** | героев × 5-10 сек |
| Эпичная длинная история | 6+ beats | **4 клипа макс** | ~20-40 сек |

**По умолчанию: 3 клипа (15-30 сек).** 4 клипа — ТОЛЬКО если каждый клип НЕОБХОДИМ и содержит достаточно действия.

**Пример упаковки beats (история с моралью):**
```
Story beats: грусть → буллинг → находка → помощь
Клипы:
  Клип 1 (beats: hook+development): "Герой сидит один грустный, потом входят буллеры и смеются"
  Клип 2 (beat: development):        "Герой находит легендарный лут, глаза горят"
  Клип 3 (beat: climax):             "Герой возвращается и делится лутом, бывшие буллеры в шоке"
= 3 клипа, 15-30 сек, динамичный пейсинг
```

---

## 2.2 Покадровый план клипа (обязательно)

Перед написанием `motion_prompt` разбей клип на 2-3 этапа. Это предотвращает зацикленные действия и даёт модели чёткие ориентиры.

**Формат для 5-сек клипа (hook/CTA):**
```
0-2 сек: [ДЕЙСТВИЕ 1] — [что делает ГГ] + [что делает камера]
2-5 сек: [ДЕЙСТВИЕ 2] — [что меняется] + [реакция]
```

**Формат для 10-сек клипа (development/climax):**
```
0-3 сек: [ДЕЙСТВИЕ 1] — [что делает ГГ] + [что делает камера]
3-7 сек: [ДЕЙСТВИЕ 2] — [что меняется] + [реакция]
7-10 сек: [ДЕЙСТВИЕ 3 / ФИНАЛ] — [завершающее действие / beat]
```

**КРИТИЧЕСКОЕ ПРАВИЛО:** Минимум 2 РАЗНЫХ действия в каждом клипе. Одно зацикленное действие (только рубит / только стоит / только бежит) = скучно и затянуто.

**Примеры (10-сек клип):**
- ❌ "Character swings hatchet for 10 seconds" — одно зацикленное
- ✅ "0-3s: swings hatchet, wood chips fly. 3-7s: wipes sweat, picks up logs. 7-10s: looks up at growing wall, nods" — 3 действия, прогрессия

**Примеры (5-сек клип):**
- ❌ "Character stands proudly for 5 seconds" — статика
- ✅ "0-2s: arms crossed, surveys fortress. 2-5s: notices girl approaching, expression shifts" — действие + реакция

**ВАЖНО:** "First/Then" в motion_prompt работает только для смены ДЕЙСТВИЯ в ОДНОЙ локации. НЕ пытайся сменить локацию, фон или состав персонажей через "First/Then" — модель не сможет это сделать.

---

## 3. Схема клипа

Каждый клип (= 1 генерация, 5 или 10 сек) в сторибоарде содержит:

```json
{
  "index": 1,
  "beats": ["hook"],
  "duration_sec": "5 or 10 (hook/CTA=5, development/climax=10)",
  "hero": "имя персонажа (опционально, для мульти-персонажных видео)",
  "image_prompt": "ПОЛНЫЙ промпт для генерации НАЧАЛЬНОГО КАДРА (см. шаблон ниже)",
  "motion_prompt": "для I2V (Kling) — описание движения БЕЗ текста речи; для T2V (Veo3) — движение + ТОЧНЫЙ текст речи",
  "character_state": "что делает персонаж В НАЧАЛЕ клипа",
  "facial_expression": "конкретное выражение лица: scared wide eyes, cocky smirk, tearful gaze (НЕ 'sad' или 'happy')",
  "gaze_direction": "looking at [КТО/ЧТО], body turned toward [КТО/ЧТО] (ОБЯЗАТЕЛЬНО при 2+ видимых персонажах)",
  "character_speech": "Hey guys, this hero is BROKEN!" или null если молчит,
  "environment_state": "что происходит с окружением",
  "camera_angle": "тип плана: close-up / medium shot / wide shot / low angle (ОБЯЗАТЕЛЬНО разный для каждого клипа)"
}
```

**Если в клипе 2 beats** (объединённые):
```json
{
  "index": 1,
  "beats": ["hook", "development"],
  "duration_sec": 8,
  "motion_prompt": "First 4 seconds: raider sits alone, head down. Then: three armed raiders enter and start pointing and laughing at him. Smooth cinematic motion.",
  "character_state": "sitting alone defeated (transitions to being mocked by others)"
}
```

### Поле `character_speech`

Если персонаж **говорит** в сцене:
- Напиши конкретную реплику: `"This hero is absolutely BROKEN right now!"`
- В `image_prompt` добавь: `"mouth slightly open, speaking expression"`

**Veo3 T2V (character_speech ≠ null):**
- В `motion_prompt` ОБЯЗАТЕЛЬНО добавь точный текст: `The character speaks clearly and says: "This hero is absolutely BROKEN right now!"`
- Veo3 T2V сгенерирует голос и липсинк

**Kling I2V (character_speech = null):**
- В `motion_prompt` НЕ добавляй текст речи — Kling не генерирует голос

Если персонаж **молчит**:
- `character_speech`: `null`
- НЕ добавляй речь в `motion_prompt`

### Поле `camera_angle` (ОБЯЗАТЕЛЬНО)

Каждая сцена ОБЯЗАНА иметь **отличающийся** план камеры. Это делает каты между сценами осмысленными и профессиональными.

**Правило чередования планов:**
- Сцена 1 (hook): `close-up` или `medium close-up` — зацепить лицом/эмоцией
- Сцена 2 (development): `medium shot` или `wide shot` — показать контекст
- Сцена 3 (climax): `low angle` или `dynamic angle` — усилить эпичность

**ЗАПРЕЩЕНО** использовать одинаковый план для соседних сцен.

Значение `camera_angle` подставляется в `image_prompt` вместо `[CAMERA_STYLE]`.

---

## 4. Шаблон image_prompt

```
[STYLE_TAGS], [CHARACTER_DESCRIPTION], [CHARACTER_STATE], [FACIAL_EXPRESSION],
[GAZE_DIRECTION (если 2+ персонажей в кадре)],
[SECONDARY_CHARACTERS (если есть, с позицией: "in background, slightly blurred")],
[ENVIRONMENT_DESCRIPTION], [ENVIRONMENT_STATE],
[LIGHTING], [COLOR_PALETTE],
[CAMERA_STYLE], vertical composition, 9:16 aspect ratio, mobile-first framing
```

**Длина image_prompt:** 40–80 слов оптимально. Максимум 90 (допустимо при 2 персонажах). Если длиннее — сокращай `environment_state` (наименее приоритетные детали). Слишком длинные промпты размывают фокус модели.

### Пример для сцены 1 (hook):

```
MLBB Mobile Legends style, anime aesthetic, vibrant saturated colors, dramatic hero lighting, fantasy battle atmosphere, high detail character art,
male warrior assassin Lancelot, silver armor with intricate blue engravings, flowing royal blue cape, gleaming silver rapier, athletic build, spiky silver-blue hair, confident piercing gaze,
standing on a cliff edge overlooking the battlefield, cape billowing in the wind, sword at his side, looking directly at the viewer with a challenging smirk, mouth slightly open speaking expression,
ancient battlefield arena at twilight, crumbling stone pillars, purple-orange sky with magical aurora,
the arena is calm before battle, floating golden embers, distant towers on the horizon,
dramatic side-lighting with hero spotlight, purple-blue ambient glow, golden rim light from behind,
deep blue and gold color scheme with crimson accents,
cinematic low angle shot, vertical composition, 9:16 aspect ratio, mobile-first framing
```

### Пример для сцены 2 (development) — тот же персонаж:

```
MLBB Mobile Legends style, anime aesthetic, vibrant saturated colors, dramatic hero lighting, fantasy battle atmosphere, high detail character art,
male warrior assassin Lancelot, silver armor with intricate blue engravings, flowing royal blue cape, gleaming silver rapier, athletic build, spiky silver-blue hair, confident piercing gaze,
charging forward across the battlefield in mid-stride, rapier extended in attack position, cape streaming behind, intense focused expression,
ancient battlefield arena at twilight, crumbling stone pillars, purple-orange sky with magical aurora,
the arena alive with battle, explosions in background, dust and debris, energy crackling,
dramatic side-lighting with hero spotlight, purple-blue ambient glow, golden rim light from behind,
deep blue and gold color scheme with crimson accents,
dynamic medium shot with slight motion blur, vertical composition, 9:16 aspect ratio, mobile-first framing
```

**Обрати внимание:** строки 1-2 (style + character) и строка 4 (environment core) **идентичны** в обеих сценах. Меняются только строки 3 (character_state), 5 (environment_state), 8 (camera).

---

## 4.1 Правило вертикального кадра 9:16

Вертикальный формат 9:16 — узкий. Это ОГРАНИЧИВАЕТ количество объектов в кадре.

**Максимум 2 фокусные точки в одном кадре:**
- Передний план: 1 персонаж (крупно, в фокусе)
- Задний план: 1 объект ИЛИ 1 персонаж (мельче, может быть слегка размыт)

**ЗАПРЕЩЕНО:**
- 3+ персонажа крупно в одном кадре (все станут мелкими, потеряют детали)
- Персонаж + здание + другой персонаж + ещё объект = визуальный мусор
- Сложные пространственные отношения между 3+ объектами

**Если в сюжете 3 персонажа в одной сцене:**
- Разбей на 2 клипа: один с ГГ + персонаж A, другой с ГГ + персонаж B
- ИЛИ покажи третьего как `"distant blurred silhouette in background"`

**Планировка глубины кадра:**

| Плоскость | Что может быть | Детализация |
|-----------|---------------|-------------|
| Foreground (25%) | Руки ГГ, оружие, объект | Высокая |
| Mid-ground (50%) | Персонаж(и), 1-2 макс | Высокая |
| Background (25%) | Среда, постройки, 1 силуэт | Низкая, размыто допустимо |

---

## 5. Шаблон motion_prompt (для I2V)

Описывает движение + диалог. Начальное изображение задаёт основу, но **ОБЯЗАТЕЛЬНО дублируй описание внешности и одежды** персонажа в motion_prompt — это помогает модели сохранить узнаваемость. Добавляй фразу: "Preserve the character's appearance from the reference image."

**КРИТИЧЕСКИ ВАЖНО:** Если персонаж говорит (`character_speech` ≠ null), ОБЯЗАТЕЛЬНО включи точный текст реплики в motion_prompt. Veo3 T2V генерирует аудио и липсинк на основе промпта. Kling I2V НЕ генерирует голос — используется только для сцен без речи.

### Формат: действие + фраза вместе

**ГЛАВНОЕ ПРАВИЛО:** Каждая реплика привязана к действию, которое её сопровождает. НЕ выноси речь в отдельный блок в конце.

```
[CAMERA_MOVEMENT].
[ДЕЙСТВИЕ 1] and says: "[ФРАЗА 1]".
[ДЕЙСТВИЕ 2] and says: "[ФРАЗА 2]".
[MOTION_STYLE]
```

**Формат связки действие+речь:**
- `[действие] and says: "[реплика]"` — для спокойной речи
- `[действие] and shouts: "[реплика]"` — для крика
- `[действие] and whispers: "[реплика]"` — для шёпота
- `[действие] and screams: "[реплика]"` — для отчаяния/ярости

**Примеры:**
- ✅ `Character pats the wooden wall proudly and says: "Check it out! My first base!" The wall collapses, he grabs his head and screams: "Oh no no no!"`
- ❌ `Character pats wall. Wall collapses. Character grabs head. The character says: "Check it out! My first base! Oh no no no!"` — речь оторвана от действий, модель не знает когда какую фразу произносить

### Вариации camera movement по типу beat

**НЕ используй** одну и ту же фразу "Smooth cinematic motion" в каждом клипе. Подбирай движение камеры под настроение:

| Beat тип | Camera motion | Зачем |
|----------|--------------|-------|
| hook | `Camera slowly pushes in` или `Camera holds static` | Интрига, фокус на лице/объекте |
| development | `Camera tracks sideways` или `Slight handheld drift` | Следим за действием, динамика |
| climax | `Camera pushes in dramatically` или `Camera pulls back to reveal` | Эпичность, раскрытие масштаба |
| комедия/стендап | `Camera holds steady` | Дать актёру играть, не отвлекать |
| грусть/эмоция | `Camera drifts slowly` или `Gentle dolly back` | Интимность, дистанция |

Каждый клип должен иметь **уникальное** описание движения камеры.

### Пример без речи (hook — интрига):

```
Camera slowly pushes in toward the hero's face. The hero's cape billows in the wind, he turns his head slightly to the right. Floating embers drift upward, magical particles pulse softly.
Slow deliberate motion, building tension.
```

### Пример С речью — действие+фраза (development — стендап):

```
Camera holds steady on medium shot. Character leans forward, gestures with free hand and says: "Hey what's up guys! So I just came back from ranked..." He shifts weight, waves hand dismissively and continues: "...and let me tell you, these teammates were something else."
Stage lights pulse gently. Static camera, letting the performance breathe.
```

### Пример С речью — мульти-действие+фраза (hook — комедия):

```
Camera holds steady at eye level. Character pats the crooked wooden wall proudly and says: "Check it out! My first base! It is perf—" The wall wobbles, planks crack and fall. The whole shack collapses. Character grabs his head with both hands and screams: "Oh no no no!"
Steady shot, comedy timing.
```

### Пример (climax — эпичный момент):

```
Camera pushes in dramatically from low angle. Character charges through explosions, raises weapon and screams: "Who is the noob NOW?!" Enemy walls crack and collapse, fire erupts, debris flies.
Aggressive forward push through chaos.
```

### Правила включения речи в motion_prompt:

**Эти правила применяются ТОЛЬКО при использовании Veo3 T2V (сцены с `character_speech` ≠ null). Для Kling I2V (без речи) — НЕ включай текст реплики в motion_prompt.**

1. **Действие + фраза вместе** — каждая реплика привязана к конкретному действию: `[делает X] and says: "[реплика]"`
2. **Точный текст** — копируй `character_speech` дословно, разбивая на части по действиям
3. **Язык** — реплика на том же языке, что в `character_speech`
4. **Не пересказывай** — не пиши "character talks about bots", пиши точную фразу
5. **Глагол речи = эмоция** — `says` (спокойно), `shouts` (крик), `screams` (ярость/ужас), `whispers` (тихо), `laughs and says` (смех)
6. **НЕ выноси речь в конец** — ❌ "...actions... The character says: 'all speech here'" ✅ "...action 1 and says: 'part 1'. Action 2 and screams: 'part 2'"

---

## 5.1 Анти-паттерны промптинга

**НЕ делай:**
- ❌ "high quality, masterpiece, best quality, 4K, ultra HD" — мусорные теги, не влияют на результат
- ❌ "no watermark, no text, no artifacts" — модели плохо обрабатывают отрицания, часто добавляют то, что просишь НЕ делать
- ❌ "beautiful", "amazing", "epic", "cool" — абстрактные прилагательные без визуального смысла
- ❌ Дублирование style_tags в character_state (если в style_tags есть "dramatic lighting", не повторяй в state)
- ❌ Одинаковый motion_prompt суффикс во всех клипах ("Smooth cinematic motion, maintain vertical composition")
- ❌ Три+ персонажа крупно в одном 9:16 кадре (все мелкие, нет фокуса)
- ❌ Два соседних клипа с одинаковым типом camera_angle (low angle → low angle)
- ❌ Одно зацикленное действие на весь клип (только рубит / только стоит / только бежит) — минимум 2 разных действия
- ❌ Описание позы без gaze_direction при 2+ видимых персонажах в кадре
- ❌ Абстрактные описания вторичных персонажей: "armored man" (→ робот/киборг). Описывай ЖИВЫЕ детали: кожа, шрамы, борода, грязь, пот
- ❌ "First/Then" в motion_prompt со сменой локации, фона или состава персонажей — модель не сменит обстановку. "First/Then" работает ТОЛЬКО для смены ДЕЙСТВИЯ в ОДНОЙ локации
- ❌ Вся речь в конце motion_prompt одним блоком: `"...actions... The character says: 'вся речь здесь'"` — модель не знает когда какую фразу произносить. Привязывай каждую реплику к действию: `"[действие] and says: '[фраза]'"`
- ❌ **Активные/резкие действия персонажей** — Kling I2V плохо генерирует: размахивание оружием, удары, прыжки, бег, броски, взмахи руками, борьбу. Результат: смазанные конечности, деформация тела, артефакты. Вместо этого используй **статичные позы с минимальным движением**: поворот головы, смена выражения лица, жест рукой, наклон корпуса, перевод взгляда, лёгкое покачивание

**Правило motion_prompt для Kling I2V:**
- ✅ Микро-движения: "turns head slowly", "shifts weight", "raises eyebrow", "leans forward slightly", "crosses arms", "nods"
- ✅ Окружение двигается: "wind blows cape", "particles drift", "light pulses", "mist swirls"
- ✅ Камера двигается: "camera slowly pushes in", "camera drifts sideways"
- ❌ Макро-движения: "swings sword", "charges forward", "jumps", "throws daggers", "punches", "runs", "slams fist"
- ❌ Сложные взаимодействия: "grabs object and throws it", "catches weapon mid-air", "flips backward"

**ДЕЛАЙ:**
- ✅ Конкретные визуальные детали: "silver armor with blue engravings" вместо "cool armor"
- ✅ Конкретные эмоции на лице: "cocky smirk with raised eyebrow" вместо "confident expression"
- ✅ Конкретные действия: "reaches for microphone with left hand" вместо "interacts with environment"
- ✅ Уникальное движение камеры для каждого клипа

---

## 6. Полный пример сторибоарда

```json
{
  "title": "Lancelot Stand-up Comedy",
  "game_tag": "MLBB",
  "approach": 2,
  "duration_target_sec": 24,
  "visual_identity": {
    "character_description": "male warrior assassin Lancelot from MLBB, silver armor with intricate blue engravings, flowing royal blue cape, gleaming silver rapier at his side, athletic build, spiky silver-blue hair, confident piercing gaze",
    "environment_description": "comedy club stage with a single microphone stand, dark background with purple and blue neon lights, spotlight from above, audience silhouettes in foreground",
    "style_tags": "MLBB Mobile Legends style, anime aesthetic, vibrant saturated colors, dramatic hero lighting, high detail character art",
    "color_palette": "deep blue (#1a237e), gold (#ffd700), purple neon (#9c27b0), electric blue (#00bcd4)",
    "lighting": "single spotlight from above on the character, purple-blue ambient neon glow from the sides, dark shadows",
    "camera_style": "medium shot, slightly below eye level"
  },
  "narrative_arc": {
    "hook": "Lancelot выходит на сцену и обращается к зрителям",
    "development": "Рассказывает шутки про игру, жестикулирует",
    "climax": "Финальная шутка + mic drop"
  },
  "scenes": [
    {
      "index": 1,
      "beats": ["hook"],
      "duration_sec": 8,
      "character_state": "walking onto the stage toward the microphone, reaching for it, confident smirk",
      "character_speech": "Hey what's up guys! So I just came back from ranked...",
      "environment_state": "spotlight turns on as character walks in, audience silhouettes visible",
      "camera_angle": "medium close-up, slightly below eye level",
      "image_prompt": "... (assembled from template)",
      "motion_prompt": "Camera holds at medium shot. Character walks forward confidently, grabs the microphone stand and says: \"Hey what's up guys!\" He adjusts the mic, leans in and continues: \"So I just came back from ranked...\" Cape sways gently, spotlight intensifies. Smooth entrance energy."
    },
    {
      "index": 2,
      "beats": ["development"],
      "duration_sec": 8,
      "character_state": "holding microphone, gesturing dramatically with free hand, animated expression, leaning forward",
      "character_speech": "And this Fanny thinks she can 1v5 the whole team... she flies in and BOOM — instant delete!",
      "environment_state": "stage lights pulse with the punchline, audience shadows react",
      "camera_angle": "wide shot, straight on, showing full stage",
      "image_prompt": "...",
      "motion_prompt": "Camera holds steady wide shot. Character waves hand dismissively and says: \"And this Fanny thinks she can 1v5 the whole team...\" He leans forward, slaps his knee and shouts: \"She flies in and BOOM — instant delete!\" Neon lights pulse with the punchline. Comedy timing, let the delivery land."
    },
    {
      "index": 3,
      "beats": ["climax"],
      "duration_sec": 8,
      "character_state": "dropping the microphone, arms spread wide in victory pose, triumphant grin",
      "character_speech": "That's what I call a SAVAGE! Goodnight everybody!",
      "environment_state": "stage lights flash, audience shadows go wild",
      "camera_angle": "dynamic low angle, looking up at triumphant character",
      "image_prompt": "...",
      "motion_prompt": "Camera pushes in from low angle. Character drops the microphone, spreads arms wide and shouts: \"That's what I call a SAVAGE!\" He points at the audience and says: \"Goodnight everybody!\" Stage lights flash and pulse. Triumphant energy, mic drop moment."
    }
  ]
}
```

---

## 7. Валидация сторибоарда

Перед переходом к генерации проверь:

- [ ] `visual_identity.character_description` — минимум 8 визуальных деталей
- [ ] `visual_identity.environment_description` — конкретная локация, не абстрактная
- [ ] Каждый клип имеет `beats` (массив: hook/development/climax)
- [ ] Narrative arc полный (все beats покрывают hook → development → climax)
- [ ] **Пейсинг:** каждый клип содержит достаточно действия на 5-10 сек. Нет "пустых" клипов
- [ ] **Пейсинг:** beats с малым действием объединены в один клип
- [ ] По умолчанию 3 клипа (~15-30 сек). 4 клипа — только если каждый НЕОБХОДИМ
- [ ] `character_speech` заполнен там где персонаж говорит
- [ ] `motion_prompt` содержит ТОЧНЫЙ текст из `character_speech` (формат: `The character says: "..."`) (только для Veo3 T2V сцен; для Kling I2V — motion_prompt БЕЗ текста речи)
- [ ] `facial_expression` — конкретное выражение лица в каждом клипе (не абстрактное)
- [ ] `camera_angle` РАЗНЫЙ для каждого соседнего клипа (close-up ≠ wide ≠ low angle)
- [ ] Camera movement в `motion_prompt` УНИКАЛЬНЫЙ для каждого клипа (не шаблонный)
- [ ] `image_prompt` длина: 40–70 слов (макс 80)
- [ ] Нет анти-паттернов (мусорных тегов, абстрактных прилагательных, отрицаний)
- [ ] `gaze_direction` указан для ВСЕХ сцен с 2+ видимыми персонажами
- [ ] `gaze_direction` совпадает с адресатом `character_speech` (если ГГ говорит кому-то)
- [ ] В каждом `image_prompt` максимум 2 фокусные точки (1 передний + 1 задний план)
- [ ] Для каждого клипа есть покадровый план: минимум 2 разных действия в 5-10 сек
- [ ] Вторичные персонажи описаны конкретно (кожа, шрамы, одежда), не абстрактно ("armored man")
- [ ] "First/Then" в motion_prompt — только смена действия, НЕ смена локации/персонажей
- [ ] Бюджет не превышен (посчитай: N изображений + 1 ref + N анимаций)
- [ ] `image_prompt` собран по шаблону для каждого клипа

---

## 8. Prompt Consistency (визуальная консистентность через промпты)

**Это главный механизм консистентности.** `image_urls` — слабая подсказка. Промпт — главный инструмент.

**Правила:**
1. `character_description` — **дословно одинаковый** во всех сценах (копируй из visual_identity)
2. `environment_description` (базовый) — **дословно одинаковый** (копируй из visual_identity)
3. `style_tags` — **дословно одинаковые** (копируй из visual_identity)
4. `lighting` и `color_palette` — **дословно одинаковые**

**Что МЕНЯЕТСЯ между сценами:**
- `character_state` — действие персонажа (стоит → бежит → атакует)
- `environment_state` — состояние окружения (спокойно → битва → взрыв)
- `camera_style` — ракурс камеры (low angle → medium shot → close-up)

---

## 9. Мульти-персонажные видео

Если в видео несколько героев (каждый герой = отдельная сцена):

**Reference images:**
- Генерируй (или используй предоставленный) отдельный reference для КАЖДОГО героя
- `image_urls` в каждой сцене содержит reference ТОЛЬКО текущего героя сцены

**Visual identity:**
```json
{
  "visual_identity": {
    "characters": {
      "Saber": "futuristic cyber warrior, blue-black mech armor...",
      "Nana": "cute small cat-girl, pink hair, fox ears...",
      "Alice": "demon queen, crimson bat wings, dark horns..."
    },
    "style_tags": "единые для всех",
    "color_palette": "единые для всех",
    "lighting": "единые для всех"
  }
}
```

**Правила:**
- `style_tags`, `lighting`, `color_palette` — **одинаковые** для всех сцен (единство стиля)
- `character_description` — **разный** для каждой сцены (разные герои)
- В storyboard каждый клип имеет поле `hero` с именем текущего персонажа
- Chain reference НЕ используется между сценами разных героев (нет смысла)

### Второстепенные персонажи (на заднем плане)

Когда в кадре видны другие персонажи кроме ГГ:

1. **Всегда** включай их описание из `visual_identity.characters` в `image_prompt`
2. Описание должно быть **КОНКРЕТНЫМ и ЖИВЫМ** — человеческие детали:
   - ✅ "weathered leather vest, scarred bearded face, sun-darkened skin, tribal tattoos"
   - ❌ "metal armor, helmet" (модель интерпретирует как робота/киборга)
3. Минимум 3 "живые" детали: кожа, шрамы, грязь, пот, борода, татуировки
4. Указывай **их действие:** "stands with arms crossed, smirking menacingly"
5. Указывай **позицию в кадре:** "in the background, slightly blurred" / "in mid-ground"

### Визуальная логика кадра

При мульти-персонажных сценах:

**В image_prompt:**

| Указание | Зачем | Пример |
|----------|-------|--------|
| Позиция персонажа | Модель знает масштаб | "in foreground" / "in background" |
| Направление тела ГГ | Модель знает ориентацию | "body turned toward the girl, back to the raider" |
| Действие вторичного | Модель знает что рисовать | "girl walks away with her back to camera" |

**В motion_prompt:**

| Указание | Пример |
|----------|--------|
| Направление взгляда | "character's eyes follow the girl leaving" |
| Кого НЕ смотрит (при неоднозначности) | "ignoring the raider behind" |
| Направление жеста/руки | "reaches toward the girl with right hand" |

---

## 10. Чеклист перед генерацией

- [ ] Character reference изображение сгенерировано и URL сохранён
- [ ] Каждая сцена имеет `image_urls` с character-ref + предыдущей сценой
- [ ] `character_description` идентичен во всех промптах (проверь копипастом)
- [ ] `environment_description` базовый идентичен во всех промптах
- [ ] `style_tags`, `lighting`, `color_palette` идентичны
- [ ] ОДНА модель анимации для всех сцен (не смешивай модели в одном ролике)
- [ ] `camera_angle` РАЗНЫЙ для каждой соседней сцены
