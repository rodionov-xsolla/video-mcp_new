# Формат "Serial Drama" — Сериальные микро-драмы

Сериальные микро-драмы с brainrot эстетикой и бесконечным сюжетом. Каждый эпизод — 25-40 секунд, 3-5 клипов, cliffhanger в конце.

---

## Когда использовать

Идея содержит ключевые слова: "serial", "episode", "series", "ep1", "ep2", "сериал", или указан `series_id` существующего сериала.

---

## Обзор формата

- **Концепт:** бесконечные микро-драмы с brainrot эстетикой, cliffhanger-ы, петли сюжета
- **Модель:** Kling 2.6 Pro I2V (`generate_audio: false`)
- **Аудио:** Kokoro TTS (озвучка) + Kling Lipsync (опционально для крупных планов)
- **Речь:** через TTS overlay, `character_speech: null` в storyboard
- **Длительность:** 25-40 сек (3-5 клипов × 5-10s)
- **Бюджет:** $10 максимум на эпизод
- **Стиль:** Pixar/Disney 3D render

---

## ФАЗА 0: ИНИЦИАЛИЗАЦИЯ

1. Загрузить `tools/fal-ai.md` — API reference
2. Загрузить `rules/main/fallback.md` — обработка ошибок
3. Загрузить `games/{GAME_TAG}/{GAME_TAG}.md` — конфиг игры
4. Если есть `games/{GAME_TAG}/serial-drama_special.md` → загрузить
5. Получить `game_assets` из Supabase:
   ```
   GET /rest/v1/game_assets?game_tag=eq.{GAME_TAG}&select=*
   ```
6. **Episode 1 (новый сериал):**
   - Инициализируй `games/{GAME_TAG}/serial-drama_story_bible.json` (персонажи, петли, мир)
   - Сгенерируй character references для всех ключевых персонажей
7. **Episode N+1 (продолжение):**
   - Загрузи `games/{GAME_TAG}/serial-drama_story_bible.json`
   - Выполни State Analysis (статусы персонажей, активные петли, anti-repetition)
   - Выполни Loop Management (каждые 5 эпизодов: закрой 1 малую петлю, открой 2 новых)
8. Перейди к Фазе 1 с контекстом Story Bible
9. **После генерации:** обнови story_bible.json (State Transition)
   - Обнови characters status, aura_points, relationships
   - Обнови active_loops / closed_loops
   - Добавь episode_summary + cliffhanger
   - Обнови anti_repetition (фразы, хуки, клиффхэнгеры)

**story_bible.json** хранится в `games/{GAME_TAG}/serial-drama_story_bible.json` (персистентный, не в output).
Эпизоды сохраняются в стандартный output: `output/YYYY-MM-DD/{GAME_TAG}/serial-drama/`

---

## Art Direction

**Стиль: Pixar/Disney 3D — около-пиксар.**

- Все персонажи — стилизованные 3D, пластиковые текстуры, экспрессивные лица
- `style_tags` берутся из game config (для Roblox: blocky Pixar 3D; для MLBB: anime Pixar hybrid)
- Мягкое ambient освещение, cinematic depth of field
- Яркие насыщенные цвета, драматичные тени в эмоциональных моментах

---

## ФАЗА 1: СЦЕНАРИЙ

### Visual Identity

- `style_tags` берутся из game config
- Описания персонажей берутся из Story Bible (поле `character_description`)
- Все описания персонажей — живые, детализированные (кожа, текстуры, детали одежды, выражение лица)

### Структура эпизода (~25-40s, 3-5 clips)

| Фаза | Тайминг | Цель | Клипов |
|------|---------|------|--------|
| **HOOK** | 0-5s | Визуальный парадокс + хук-фраза. Остановка скролла | 1 clip (5s) |
| **CLIMAX** | 5-30s | Диалог, конфронтация, нарастающий темп | 2-3 clips (5-10s каждый) |
| **CLIFFHANGER** | Последние 5s | Обрыв на пике. Шок, reveal, mid-sentence stop | 1 clip (5s) |

### Правила нарратива

1. **HOOK (первый клип):**
   - Визуальный контраст: бедный нуб рядом с роскошным домом / спокойная сцена перед хаосом
   - Хук-фраза: провокация, вопрос, шокирующее заявление
   - Пример: *"Everybody laughed at the bacon hair... they had NO idea what was coming"*

2. **CLIMAX (середина):**
   - Плотный диалог, каждый клип содержит реплику
   - Нарастание конфликта: от разговора → к конфронтации → к reveal
   - Минимум 2 разных персонажа должны говорить за эпизод
   - Brainrot лексика в диалогах (rizz, sigma, cooked, negative aura)

3. **CLIFFHANGER (последний клип):**
   - Обрыв на самом интересном месте
   - Варианты: mid-sentence, reveal нового персонажа, неожиданный поворот
   - Последняя реплика ОБЯЗАТЕЛЬНО обрывается или заканчивается шоком
   - "TO BE CONTINUED..." overlay на последние 2 секунды

### Длительность клипа — адаптивная

Агент сам выбирает длину каждого клипа:

| Контент в клипе | Длительность | Когда |
|----------------|-------------|-------|
| Короткая реплика (≤10 слов) | **5s** | Реакция, хук, панчлайн |
| Длинная реплика (>10 слов) | **10s** | Диалог, монолог, развитие |
| Одно действие + реакция | **5s** | Шок, поворот, reveal |
| Развёрнутый момент, 2+ персонажа говорят | **10s** | Конфронтация, объяснение |

**Правило:** выбирай минимально достаточную длину. Если реплика укладывается в 5 секунд — не растягивай на 10.

### Схема клипа (JSON)

Каждый клип в storyboard.json содержит следующие поля (помимо стандартных):

```json
{
  "format": "serial-drama",
  "series_id": "roblox-noob-revenge",
  "episode_number": 1,
  "retention_strategy": "...",
  "active_loops": ["..."],
  "cliffhanger": "...",
  "character_speech": null,
  "tts": "Реплика персонажа идёт сюда (текст для Kokoro TTS)",
  "camera_angle": "close-up"
}
```

- `character_speech` = `null` — голос ТОЛЬКО через Kokoro TTS overlay
- `tts` — текст реплики, отдельное поле от storyboard (передаётся в Kokoro TTS в Фазе 5)
- `camera_angle` ОБЯЗАН отличаться от соседних клипов

### image_prompt

Шаблон: 40-80 слов, включает:
- `style_tags` из game config
- `character_description` из Story Bible
- состояние персонажа + выражение лица
- `camera_angle` (отличный от соседних клипов)
- 9:16 vertical composition

Правила 9:16:
- Максимум 2 фокусные точки в кадре
- Максимум 2 персонажа в кадре

**Пример image_prompt (1 персонаж):**
```
[style_tags], [character_description], standing in center frame, looking forward with wide innocent eyes and nervous expression, [environment], soft ambient lighting, cinematic depth of field, close-up shot, vertical composition, 9:16 aspect ratio
```

**Пример image_prompt (2 персонажа):**
```
[style_tags], [character_1_description], standing in foreground left, looking right at second character with angry expression,
[character_2_description], standing in background right slightly blurred, arms crossed, smug smirk looking down at first character,
[environment], [lighting], [camera_angle], vertical composition, 9:16 aspect ratio
```

### Anti-Repetition Check

Перед финализацией storyboard проверь `story_bible.json → anti_repetition`:

1. **Фразы:** Не повторяй фразы из последних 8 эпизодов
2. **Хуки:** Не используй тот же тип hook (если прошлый был "question hook" — используй "contrast hook" или "statement hook")
3. **Клиффхэнгеры:** Не повторяй тот же приём (если прошлый был "mid-sentence" — используй "reveal" или "unexpected entrance")
4. **Метафоры/сравнения:** Разнообразие обязательно

### Retention Strategy

Каждый эпизод ОБЯЗАН содержать в storyboard:

```json
{
  "retention_strategy": "Reveal that the noob has a secret golden item triggers curiosity — viewer MUST see next episode to learn what it does",
  "active_loops": ["noob's secret identity", "slender's revenge plan"],
  "cliffhanger": "Noob opens inventory and golden light illuminates his face — cut to black"
}
```

### Сохранение storyboard.json

Сохранить в `output/YYYY-MM-DD/{GAME_TAG}/serial-drama/storyboard.json` до начала генерации.

---

## ФАЗА 2: CHARACTER REFERENCE

Сгенерировать character reference для каждого ключевого персонажа из Story Bible.

- Один ref на персонажа (один раз на весь сериал, переиспользуется в каждом эпизоде)
- Стиль: Pixar/Disney 3D, совпадает с `style_tags` из game config
- Если в `game_assets` есть `reference_image` для персонажа → использовать его вместо генерации
- Для multi-character сцен: `image_urls` включает refs обоих персонажей

**Сохранение:** `scenes/refs/character-ref-{name}.png`

---

## ФАЗА 3: ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ

Генерировать изображения последовательно, по одному клипу за раз.

### Chain reference (стандартный паттерн):

- `image_urls`: [character-ref.png] — для первой сцены
- `image_urls`: [character-ref.png, предыдущая-сцена.png] — для последующих сцен (chain)
- Для multi-character сцен: `image_urls` включает refs обоих персонажей

### Параметры:

- Модель: Nano Banana 2 (`fal-ai/nano-banana-2/edit`)
- Стоимость: $0.04 за изображение

**Сохранение:** `scenes/scene-{N}/scene-{N}.png`

---

## ФАЗА 4: АНИМАЦИЯ

Анимировать каждое изображение через Kling 2.6 Pro I2V.

### Параметры:

- Модель: `fal-ai/kling-video/v2.6/pro/image-to-video`
- `generate_audio` = `false` — **ВСЕГДА**. Kling НЕ генерирует звук. Вся озвучка через TTS
- `character_speech` = `null`
- `duration`: `"5"` или `"10"` (адаптивно, согласно стoryboard)
- Polling: каждые 15 секунд
- Валидация: файл > 1000 байт

### Разрешённые действия (ТОЛЬКО микродвижения):

- ✅ Поворот головы (медленный)
- ✅ Подъём/опускание бровей
- ✅ Смена выражения лица (улыбка → шок → злость)
- ✅ Жест рукой (указать, помахать, сжать кулак)
- ✅ Лёгкий наклон корпуса вперёд/назад
- ✅ Покачивание, перенос веса с ноги на ногу
- ✅ Моргание
- ✅ Движение окружения: ветер, частицы, свет пульсирует
- ✅ Движение камеры: push in, pull back, drift

### ЗАПРЕЩЁННЫЕ действия:

- ❌ Ходьба, бег, прыжки
- ❌ Удары, замахи, броски
- ❌ Резкие повороты всего тела
- ❌ Перемещение из точки A в точку B
- ❌ Падения, полёты
- ❌ Любые активные физические действия
- ❌ **Kling генерирует голос/слова** — generate_audio ВСЕГДА false

**Все сцены — статичные позиции персонажей с мягкой анимацией лица и жестов.**

### Несколько персонажей в кадре

Для динамики допускается **2 персонажа в одном кадре** (максимум, из-за 9:16):
- Один на переднем плане (крупно), второй на среднем плане или сбоку
- Оба в статичных позах с микродвижениями (один поворачивает голову к другому, второй жестикулирует)
- `gaze_direction` ОБЯЗАТЕЛЕН — кто на кого смотрит
- В image_prompt: опиши позицию каждого ("foreground left", "background right, slightly blurred")
- В motion_prompt: опиши микродвижения КАЖДОГО персонажа отдельно
- Используй chain reference обоих персонажей: `image_urls: [ref-char1, ref-char2]`

**Пример motion_prompt с 2 персонажами:**
```
Camera holds steady at medium shot. Foreground character turns head slowly toward the other, expression shifts to anger, fists clench. Background character raises eyebrow, slight lean back with amused smirk. Ambient particles drift. Tense confrontation energy.
```

### Motion prompt шаблон

```
Camera [slight push-in / holds steady / drifts slowly].
[Character] [micro-action: turns head slowly, raises eyebrow, clenches fist].
[Second micro-action: glances sideways, smirks, eyes widen].
[Environment: ambient particles drift, neon signs pulse, light shifts].
Preserve character appearance from reference image.
```

Примеры:
- ✅ `Camera holds steady at medium shot. Character turns head slowly to face the viewer, eyebrows raise in surprise, mouth drops slightly open. Background neon signs flicker. Tense stillness.`
- ❌ `Character walks up to the other player and pushes him` — перемещение + физический контакт

### Hard cut:

- Без `end_image_url`
- Хард-кат между клипами (нет freeze frame на последнем кадре)

**Сохранение:** `scenes/scene-{N}/scene-{N}.mp4`

---

## ФАЗА 5: СБОРКА

### 5.1 TTS

Сгенерировать озвучку для каждого клипа через Kokoro TTS.

- Текст берётся из поля `tts` в storyboard (не из `character_speech`)
- Голос выбирается по типу персонажа и зафиксирован в story_bible.json

#### Выбор голоса Kokoro TTS

| Тип персонажа | Голос | Когда |
|---------------|-------|-------|
| Уверенный мужской (sigma, chad) | `am_adam` или `am_eric` | Сарказм, уверенность, угрозы |
| Паника / страх | `af_bella` или `am_puck` | Шок, испуг, отчаяние |
| Усталость / грусть | `am_michael` или `af_river` | Разочарование, усталость |
| Гордость / хвастовство | `am_onyx` или `af_heart` | Флекс, победа |
| Женский (preppy, девочки) | `af_bella` или `af_jessica` | Любой женский персонаж |
| Нуб / невинный | `am_puck` или `af_nova` | Наивность, непонимание |

**Фиксируй голос для каждого персонажа в story_bible.json** — один персонаж = один голос на весь сериал.

**Сохранение:** `scenes/scene-{N}/tts-{N}.wav`

### 5.2 Lipsync (опционально)

Применять Kling Lipsync только для клипов с крупным планом (close-up, medium close-up).

- На wide shot / low angle — TTS overlay без lipsync (губы не видны)
- Стоимость: $0.50/5s или $1.00/10s

**Сохранение:** `scenes/scene-{N}/scene-{N}-lipsync.mp4`

### 5.3 Масштабирование

Все клипы привести к единому формату перед склейкой:
- Разрешение: 1080×1920
- FPS: 30
- CRF: 10
- Аудио: AAC 44100 Hz stereo

**Сохранение:** `scenes/scene-{N}/scene-{N}-scaled.mp4`

### 5.4 TTS overlay per clip

```bash
TTS_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 tts.wav)
CLIP_DUR=$(echo "0.5 + $TTS_DUR + 1.0" | bc)
ffmpeg -y -i scene.mp4 -i tts.wav \
  -filter_complex "[1:a]adelay=500|500[tts];[0:a][tts]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" -t $CLIP_DUR \
  -ar 44100 -ac 2 -c:a aac -b:a 128k scene-final.mp4
```

#### Правило обрезки по TTS:

```
clip_duration = 0.5 (pre-delay) + TTS_duration + 1.0 (post-silence)
```

- 0.5s — пауза перед речью (зритель успевает увидеть кадр)
- TTS_duration — длина озвучки
- 1.0s — пауза после речи (зритель осмысляет)
- Если clip_duration > video_duration → обрезать по видео

#### Для lipsync клипов (аудио уже в видео):

```bash
ffmpeg -y -i scene-lipsync.mp4 -t $CLIP_DUR \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  scene-final.mp4
```

**КРИТИЧНО: НИКОГДА не используй `-shortest`** — это обрежет видео до длины аудио.

### 5.5 Склейка клипов

Concat всех клипов с re-encode (не stream copy):

**ВСЕ клипы** перед склейкой должны иметь одинаковый аудио формат:
- Sample rate: 44100 Hz
- Channels: stereo (2)
- Codec: AAC 128kbps

Без нормализации concat даёт глитчи/тишину при смене формата между клипами.

### 5.6 "TO BE CONTINUED..." Overlay

На последний клип финального видео — FFmpeg drawtext:

```bash
$FFMPEG -y -i final.mp4 \
  -vf "drawtext=text='TO BE CONTINUED...':fontsize=48:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-120:enable='between(t,duration-2,duration)'" \
  -c:a copy final-overlay.mp4
```

- Текст: белый с чёрной обводкой
- Позиция: по центру, нижняя часть экрана
- Появляется: за 2 секунды до конца видео
- Заменить `duration` на реальную длительность видео (получить через `ffprobe`)

### 5.7 Фоновая музыка (опционально)

Наложить фоновую музыку с `volume=0.15`.

**NEVER `-shortest`.**

---

## ФАЗА 6: UPLOAD & LOG

1. Загрузить `final.mp4` в Supabase Storage:
   ```
   videos/{GAME_TAG}/{YYYY-MM-DD}/serial-drama_final.mp4
   ```
2. Записать лог в таблицу `video_agent_runs`
3. Обновить Story Bible (State Transition — см. Фазу 0, шаг 9)
4. Показать cost report (разбивка по компонентам: image, video, TTS, lipsync, итого)

---

## Story Bible — persistent state

Файл `games/{GAME_TAG}/serial-drama_story_bible.json` хранит состояние вселенной между эпизодами.

### Структура:

```json
{
  "series_id": "roblox-noob-revenge",
  "game_tag": "Roblox",
  "title": "The Noob Who Was a Secret Millionaire",
  "style_tags": "Roblox-inspired Pixar-style 3D...",
  "created_at": "2026-03-27",
  "last_episode": 0,

  "characters": [
    {
      "name": "Noob Dave",
      "role": "protagonist",
      "character_description": "Roblox-style blocky humanoid...",
      "voice": "am_puck",
      "status": "new to the server, secretly rich",
      "aura_points": 0,
      "relationships": {}
    }
  ],

  "active_loops": [],
  "closed_loops": [],

  "world_state": {
    "location": "Roblox server lobby",
    "important_items": [],
    "key_events": []
  },

  "anti_repetition": {
    "recent_phrases": [],
    "recent_hooks": [],
    "recent_cliffhangers": []
  },

  "episode_summaries": []
}
```

### Правила обновления Story Bible:

**Перед генерацией (State Analysis):**
1. Загрузи `serial-drama_story_bible.json` из `games/{GAME_TAG}/`
2. Проанализируй: кто в каком статусе, какие петли активны, какой level ауры
3. Определи что должно произойти в этом эпизоде (Loop Management)

**После генерации (State Transition):**
1. Обнови `characters[].status` и `aura_points`
2. Обнови `relationships` если изменились
3. Обнови `active_loops` / `closed_loops`
4. Добавь `episode_summaries[]` с кратким содержанием + cliffhanger
5. Обнови `anti_repetition` — добавь использованные фразы, хуки, клиффхэнгеры
6. Обнови `world_state` — локация, важные предметы, события
7. Инкрементируй `last_episode`

---

## Loop Management (Recursive Continuity)

Петли интриги — нерешённые конфликты, которые удерживают зрителя.

### Правило 5 эпизодов:
- Каждые 5 эпизодов **закрой 1 малую петлю** (minor loop)
- Но **открой 2 новых** более масштабных
- Никогда не закрывай ВСЕ петли — минимум 2 активных всегда

### Типы петель:

| Тип | Длительность | Пример |
|-----|-------------|--------|
| **Minor** | 2-5 эпизодов | "Кто украл предмет?" |
| **Major** | 10-20 эпизодов | "Скрытая личность главного героя" |
| **Eternal** | Никогда не закрывается | "Война серверов" |

### Правило "No Finality":
- Любая победа — начало новой беды
- Любое раскрытие — порождает новую тайну
- Сериал НИКОГДА не заканчивается

---

## Retention Strategy (обязательный блок)

Каждый эпизод ОБЯЗАН содержать в storyboard:

```json
{
  "retention_strategy": "Reveal that the noob has a secret golden item triggers curiosity — viewer MUST see next episode to learn what it does",
  "active_loops": ["noob's secret identity", "slender's revenge plan"],
  "cliffhanger": "Noob opens inventory and golden light illuminates his face — cut to black"
}
```

---

## Anti-Repetition Check

Перед написанием storyboard проверь `serial-drama_story_bible.json → anti_repetition`:

1. **Фразы:** Не повторяй фразы из последних 8 эпизодов
2. **Хуки:** Не используй тот же тип hook (если прошлый был "question hook" — используй "contrast hook" или "statement hook")
3. **Клиффхэнгеры:** Не повторяй тот же приём (если прошлый был "mid-sentence" — используй "reveal" или "unexpected entrance")
4. **Метафоры/сравнения:** Разнообразие обязательно

---

## Бюджетные лимиты

### Стоимость с generate_audio=false

| Компонент | 5s клип | 10s клип |
|-----------|---------|----------|
| Image (Nano Banana 2) | $0.04 | $0.04 |
| Kling I2V (no audio) | $0.35 | $0.70 |
| Kokoro TTS | $0.02 | $0.02 |
| Lipsync (если face detected) | $0.50 | $1.00 |
| **Итого с lipsync** | **$0.91** | **$1.76** |
| **Итого без lipsync** | **$0.41** | **$0.76** |

> **1×10s выгоднее чем 2×5s** — та же цена за Kling, но 1 image вместо 2, 1 lipsync вместо 2.

| Вариант | Клипов | Стоимость | Когда |
|---------|--------|-----------|-------|
| Минимальный | 3 × 5s | ~$1.75-2.75 | Короткий эпизод |
| Типичный | 2×10s + 1×5s | ~$3-4.50 | Стандартный эпизод |
| Максимальный | 3×10s | ~$4-5.30 | Длинный эпизод |

**Лимит:** $10.00 на эпизод. Остановись если расход > $9.00.

**Оптимизация:**
- `generate_audio = false` — экономит 50% на Kling ($0.07/s вместо $0.14/s)
- Lipsync только на крупных планах с выраженными чертами лица
- Предпочитай 10s клипы вместо 2×5s

---

## Пример: Episode 1 — "The Noob Who Was a Secret Millionaire"

### Story Bible (инициализация):
```json
{
  "series_id": "roblox-noob-revenge",
  "game_tag": "Roblox",
  "title": "The Noob Who Was a Secret Millionaire",
  "last_episode": 0,
  "characters": [
    {
      "name": "Noob Dave",
      "role": "protagonist",
      "character_description": "Roblox-style blocky humanoid character, bright yellow smooth plastic skin, simple blue torso shirt with no details, bright green pants, round head with wide innocent eyes, small curved mouth, stubby short limbs, toy-like proportions with oversized head, matte plastic texture",
      "voice": "am_puck",
      "status": "just joined the server",
      "aura_points": 0,
      "relationships": {}
    },
    {
      "name": "King Rex",
      "role": "antagonist",
      "character_description": "Roblox-style blocky humanoid with oversized golden crown with embedded jewels, thick diamond chain necklace with dollar pendant, white fluffy fur coat over gold vest, designer sunglasses pushed up on forehead, smug arrogant expression with raised eyebrow, glossy shiny plastic texture",
      "voice": "am_onyx",
      "status": "self-proclaimed server king",
      "aura_points": 500,
      "relationships": {}
    }
  ],
  "active_loops": [],
  "closed_loops": [],
  "world_state": {
    "location": "Roblox Adopt Me server lobby",
    "important_items": [],
    "key_events": []
  },
  "anti_repetition": {"recent_phrases": [], "recent_hooks": [], "recent_cliffhangers": []},
  "episode_summaries": []
}
```

### Storyboard sketch:

**Clip 1 (HOOK, 5s, close-up):**
- Noob Dave стоит в лобби, смотрит вокруг с широко открытыми глазами
- TTS: *"So uh... this is my first day on this server..."*
- Motion: Camera slight push-in. Character turns head slowly, eyes widen. Ambient neon signs glow.

**Clip 2 (CLIMAX, 10s, medium shot):**
- King Rex стоит перед Noob Dave, смотрит сверху вниз, презрительная ухмылка
- TTS (Rex): *"Bro really showed up with ZERO drip. Negative aura detected. You don't belong here."*
- TTS (Dave): *"I... I just wanted to play..."*
- Motion: Camera holds steady. Rex leans forward slightly, raises hand dismissively. Dave shrinks back, expression shifts to sad.

**Clip 3 (CLIMAX, 5s, wide shot):**
- Другие игроки вокруг смеются, указывают на Dave
- TTS: *"Even the NPCs got more style than this bacon hair lookin—"*
- Motion: Camera drifts slightly. Background characters' heads turn. Dave clenches fists, jaw tightens.

**Clip 4 (CLIFFHANGER, 5s, close-up):**
- Dave открывает инвентарь, золотой свет озаряет его лицо
- TTS: *"You know what... let me show you something..."*
- Motion: Camera pushes in on face. Golden light illuminates from below. Eyes narrow, slight smirk appears. Cut to black.
- **"TO BE CONTINUED..."** overlay последние 2 секунды

---

## Валидация serial-drama

- [ ] `format: "serial-drama"` присутствует
- [ ] `series_id` заполнен
- [ ] `episode_number` корректен (= story_bible.last_episode + 1)
- [ ] `retention_strategy` заполнен и конкретен
- [ ] `active_loops` актуальны
- [ ] `cliffhanger` описан
- [ ] Первый клип — HOOK (визуальный парадокс + хук-фраза)
- [ ] Последний клип — CLIFFHANGER (обрыв на пике)
- [ ] Каждый клип содержит реплику (TTS через Kokoro, `character_speech: null` в storyboard)
- [ ] Brainrot лексика присутствует в диалогах
- [ ] Анимация — ТОЛЬКО микродвижения (нет ходьбы, бега, ударов, прыжков)
- [ ] Длительность клипов адаптивная: 5s (≤10 слов реплики) или 10s (>10 слов)
- [ ] `camera_angle` отличается для каждого соседнего клипа
- [ ] Story bible загружена (если episode > 1) и будет обновлена после генерации
- [ ] Anti-repetition check пройден (нет повторов из последних 8 эпизодов)
- [ ] "TO BE CONTINUED..." overlay запланирован на последние 2 секунды
- [ ] Chain reference использован для всех изображений (Фаза 3)
- [ ] `generate_audio: false` во всех Kling запросах

---

## Анти-паттерны

**НЕ делай:**
- Не используй `generate_audio: true` — Kling-генерированный голос плохого качества, речь только через Kokoro TTS
- Не используй Veo3 T2V для этого формата — только Kling I2V
- Не давай персонажам активных действий (ходьба, бег, прыжки, удары) — только микро-движения
- Не превышай 25 слов на реплику TTS — не уложится в 10 сек
- Не используй `-shortest` в FFmpeg — обрезает видео до длины аудио
- Не закрывай все сюжетные петли — всегда должен оставаться открытый cliffhanger
- Не повторяй хуки/клиффхэнгеры из последних 8 эпизодов (anti-repetition)

---

## Выходные файлы

```
OUTPUT_DIR/
├── storyboard.json
├── scenes/
│   ├── refs/
│   │   ├── character-ref-{name}.png
│   │   └── ...
│   ├── scene-1/
│   │   ├── scene-1.png
│   │   ├── scene-1.mp4
│   │   ├── scene-1-scaled.mp4
│   │   └── tts-1.wav
│   ├── scene-2/
│   │   └── ...
│   └── scene-N/
│       └── ...
└── final.mp4
```

**Также:** `games/{GAME_TAG}/serial-drama_story_bible.json` — персистентный, обновляется после каждого эпизода.
