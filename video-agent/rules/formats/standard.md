# Формат "Standard" — I2V / T2V

Стандартный формат видео. Используется по умолчанию, если идея не соответствует специальным форматам (news, serial-drama, object-character, dual-style, gameplay-ai-avatar, dance-battle).

> **Отладочный режим:** Если в задаче есть фраза «Отладочный режим» — после каждой фазы останавливайся и отправляй результат на согласование с пояснением (что сделано, почему, какие решения приняты). Не переходи к следующей фазе без одобрения. Подробнее — `rules/main/workflow.md`.

---

## Когда использовать

Формат "standard" активируется если IDEA НЕ содержит ключевых слов других форматов:
- Не "news/новости/patch recap" (→ news)
- Не "serial/episode/сериал" (→ serial-drama)
- Не "object character/talking object" (→ object-character)
- Не "dual-style/game vs reality" (→ dual-style)
- Не "gameplay ai avatar/offerwall/offer" (→ gameplay-ai-avatar)
- Не "dance battle/танцевальный батл" (→ dance-battle)

---

## Обзор формата

- **Концепт:** универсальный формат для экшена, стендапов, гайдов, рейтингов, трейлеров
- **Модель (без речи):** Kling 2.6 Pro I2V (`generate_audio: true`)
- **Модель (с речью):** Veo3 T2V (`generate_audio: true`)
- **Длительность:** 15-30 сек (3 клипа × 5-10s)
- **Бюджет:** $5 (I2V) / $10 (T2V)

---

## ФАЗА 0: ИНИЦИАЛИЗАЦИЯ

1. Загрузить `tools/fal-ai.md` — API reference
2. Загрузить `rules/main/fallback.md` — обработка ошибок
3. Загрузить `games/{GAME_TAG}/{GAME_TAG}.md` — конфиг игры
4. *(опционально)* Загрузить `music/tracks.json` — фоновая музыка
5. Определить наличие речи в идее → выбор модели (Kling I2V или Veo3 T2V)
6. Запросить `game_assets` из Supabase:
   ```
   GET /rest/v1/game_assets?game_tag=eq.{GAME_TAG}&select=*
   ```
7. Проверить наличие `reference_image` в результатах — если есть, использовать его URL в Фазе 2 вместо генерации нового

---

## ФАЗА 1: СЦЕНАРИЙ (storyboard.json)

**НИКОГДА не генерируй визуал без готового `storyboard.json`.**

### Подходы

| Тип контента | Подход | Модели |
|-------------|--------|--------|
| Динамичный контент, экшен, стендап, комбо | **Approach 2** (I2V/T2V) | Image → Kling 2.6 Pro I2V (без речи) / Veo3 T2V (с речью) |
| Кинематограф, трейлеры, атмосферные видео | **Approach 3** (T2V) | Veo3 T2V |
| Списки, рейтинги, советы, гайды, "Top N" | **Approach 2** (I2V) | Image → Kling 2.6 Pro I2V |

По умолчанию: Approach 2. Если пользователь указал подход — используй его.

### Выбор модели

Модель определяется наличием речи:
- `character_speech` ≠ null → **Veo3 T2V** (генерирует голос + липсинк)
- `character_speech` = null → **Kling 2.6 Pro I2V** (звуковые эффекты, без голоса)

### Клипы и длительности

| Подход | Клипов | Длительность каждого | Итого |
|--------|--------|---------------------|-------|
| Approach 2 (I2V/T2V) | **3** (по умолч.) | **5–10 сек** | **15–30 сек** |
| Approach 3 (T2V) | 2–3 | 5–8 сек | 16-24 сек |

**I2V правило:** По умолчанию 3 клипа. 4 клипа — ТОЛЬКО если каждый содержит достаточно действия и уникального движения.

---

### 1.1 Visual Identity (единый на всё видео)

Определи и зафикси визуальный стиль ДО генерации. Эти поля будут **дословно повторяться** в промптах каждой сцены.

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

**Prompt Consistency — главный механизм консистентности:**
1. `character_description` — **дословно одинаковый** во всех сценах (копируй из visual_identity)
2. `environment_description` (базовый) — **дословно одинаковый**
3. `style_tags` — **дословно одинаковые**
4. `lighting` и `color_palette` — **дословно одинаковые**

**Что МЕНЯЕТСЯ между сценами:** `character_state`, `environment_state`, `camera_style` (ракурс).

---

### 1.2 Narrative Arc (сюжетная арка)

| Beat | Цель | Пример |
|------|------|--------|
| **hook** | Зацепить внимание | Шокирующий факт, вопрос, провокация |
| **development** | Раскрыть тему, нарастить | Примеры, аргументы, нарастание |
| **climax** | Кульминация | Самый мощный момент, пик эмоции |
| **cta** | Призыв | "Подписывайся!", overlay на последнем клипе |

CTA — не отдельный клип, а overlay на последнем.

---

### 1.3 Пейсинг: beats → клипы

**КРИТИЧЕСКОЕ ПРАВИЛО:** Story beat ≠ клип. Beat — сюжетная единица, клип — техническая (5 или 10 сек: Kling 5s для hook/CTA, 10s для development/climax).

| Действия на beat | Решение | Пример |
|-----------------|---------|--------|
| Мало (сидит, стоит, грустит) | **Объедини 2 beats в 1 клип** | "Грустный рейдер + к нему подходят буллеры" = 1 клип |
| Нормально (говорит реплику, жестикулирует) | **1 beat = 1 клип** | Стендап: одна шутка = один клип |
| Много (битва, погоня, взрыв + реакция) | **1 beat = 1 клип** | Находка легендарного лута = отдельный клип |

**Как объединить 2 beats в 1 клип:**
- В `motion_prompt` опиши два этапа: `"First 4 seconds: [действие 1]. Then: [действие 2]"`
- `image_prompt` показывает НАЧАЛЬНЫЙ кадр (первый beat)
- В `beats` перечисли оба бита: `["hook", "development"]`

**Таблица количества клипов (Approach 2):**

| Тип контента | Story beats | Клипов | Итого |
|-------------|------------|--------|-------|
| Простая история / мораль | 4-5 beats | **3 клипа** | ~15-30 сек |
| Стендап / комедия | 3 beats | **3 клипа** | ~15-30 сек |
| Многоперсонажный (1 герой = 1 часть) | по героям | **по 1 клипу на героя** | героев × 5-10 сек |
| Эпичная длинная история | 6+ beats | **4 клипа макс** | ~20-40 сек |

**По умолчанию: 3 клипа.** 4 клипа — ТОЛЬКО если каждый НЕОБХОДИМ.

---

### 1.4 Покадровый план клипа (обязательно)

Перед написанием `motion_prompt` разбей клип на 2-3 этапа.

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

**КРИТИЧЕСКОЕ ПРАВИЛО:** Минимум 2 РАЗНЫХ действия в каждом клипе. Одно зацикленное действие = скучно и затянуто.

- ❌ "Character swings hatchet for 10 seconds" — одно зацикленное
- ✅ "0-3s: swings hatchet, wood chips fly. 3-7s: wipes sweat, picks up logs. 7-10s: looks up at growing wall, nods" — 3 действия, прогрессия

**ВАЖНО:** "First/Then" работает только для смены ДЕЙСТВИЯ в ОДНОЙ локации. НЕ пытайся сменить локацию, фон или состав персонажей — модель не сможет это сделать.

---

### 1.5 Схема клипа

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
  "character_speech": "Hey guys, this hero is BROKEN! или null если молчит",
  "environment_state": "что происходит с окружением",
  "camera_angle": "тип плана: close-up / medium shot / wide shot / low angle (ОБЯЗАТЕЛЬНО разный для каждого клипа)"
}
```

**Если в клипе 2 beats (объединённые):**
```json
{
  "index": 1,
  "beats": ["hook", "development"],
  "duration_sec": 8,
  "motion_prompt": "First 4 seconds: raider sits alone, head down. Then: three armed raiders enter and start pointing and laughing at him. Smooth cinematic motion.",
  "character_state": "sitting alone defeated (transitions to being mocked by others)"
}
```

**Поле `character_speech`:**
- Напиши конкретную реплику: `"This hero is absolutely BROKEN right now!"`
- В `image_prompt` добавь: `"mouth slightly open, speaking expression"`
- **Veo3 T2V:** в `motion_prompt` ОБЯЗАТЕЛЬНО включи точный текст: `The character speaks clearly and says: "..."`
- **Kling I2V:** в `motion_prompt` НЕ добавляй текст речи — Kling не генерирует голос

**Поле `camera_angle` — правило чередования планов:**
- Сцена 1 (hook): `close-up` или `medium close-up` — зацепить лицом/эмоцией
- Сцена 2 (development): `medium shot` или `wide shot` — показать контекст
- Сцена 3 (climax): `low angle` или `dynamic angle` — усилить эпичность
- **ЗАПРЕЩЕНО** использовать одинаковый план для соседних сцен

---

### 1.6 Шаблон image_prompt

```
[STYLE_TAGS], [CHARACTER_DESC], [STATE], [EXPRESSION],
[GAZE_DIRECTION (если 2+ персонажей в кадре)],
[SECONDARY_CHARS (если есть, с позицией: "in background, slightly blurred")],
[ENVIRONMENT], [ENV_STATE],
[LIGHTING], [PALETTE],
[CAMERA], vertical composition, 9:16 aspect ratio, mobile-first framing
```

**Длина:** 40–80 слов оптимально. Максимум 90 при 2 персонажах. Слишком длинные промпты размывают фокус модели.

**Правило вертикального кадра 9:16 — максимум 2 фокусные точки:**
- Передний план: 1 персонаж (крупно, в фокусе)
- Задний план: 1 объект ИЛИ 1 персонаж (мельче, может быть слегка размыт)
- Если 3 персонажа — разбей на 2 клипа или покажи третьего как `"distant blurred silhouette in background"`

| Плоскость | Что может быть | Детализация |
|-----------|---------------|-------------|
| Foreground (25%) | Руки ГГ, оружие, объект | Высокая |
| Mid-ground (50%) | Персонаж(и), 1-2 макс | Высокая |
| Background (25%) | Среда, постройки, 1 силуэт | Низкая, размыто допустимо |

**Консистентность image_prompt:** строки style_tags + character_description + environment_description (базовые) — **идентичны** во всех сценах. Меняются только character_state, environment_state, camera.

---

### 1.7 Шаблон motion_prompt (для I2V)

**ОБЯЗАТЕЛЬНО дублируй описание внешности персонажа** и добавляй: `"Preserve the character's appearance from the reference image."`

**Формат: действие + фраза вместе (только для Veo3 T2V):**
```
[CAMERA_MOVEMENT].
[ДЕЙСТВИЕ 1] and says: "[ФРАЗА 1]".
[ДЕЙСТВИЕ 2] and says: "[ФРАЗА 2]".
[MOTION_STYLE]
```

- `[действие] and says: "[реплика]"` — спокойная речь
- `[действие] and shouts: "[реплика]"` — крик
- `[действие] and whispers: "[реплика]"` — шёпот
- `[действие] and screams: "[реплика]"` — ярость/отчаяние

**Вариации camera movement по типу beat:**

| Beat тип | Camera motion | Зачем |
|----------|--------------|-------|
| hook | `Camera slowly pushes in` или `Camera holds static` | Интрига, фокус на лице |
| development | `Camera tracks sideways` или `Slight handheld drift` | Следим за действием |
| climax | `Camera pushes in dramatically` или `Camera pulls back to reveal` | Эпичность |
| комедия/стендап | `Camera holds steady` | Дать актёру играть |
| грусть/эмоция | `Camera drifts slowly` или `Gentle dolly back` | Интимность |

Каждый клип должен иметь **уникальное** описание движения камеры.

**Kling I2V — только микро-движения:**
- ✅ "turns head slowly", "shifts weight", "raises eyebrow", "leans forward slightly", "crosses arms", "nods"
- ✅ Окружение двигается: "wind blows cape", "particles drift", "light pulses"
- ✅ Камера двигается: "camera slowly pushes in", "camera drifts sideways"
- ❌ Макро-движения: "swings sword", "charges forward", "jumps", "throws daggers", "runs"

---

### 1.8 Сохранение storyboard.json

Сохрани `storyboard.json` в `OUTPUT_DIR/` перед переходом к Фазе 2.

---

## ФАЗА 2: CHARACTER REFERENCE

Генерируй один anchor image для консистентности персонажа.

**Если `reference_image` найден в `game_assets` (Фаза 0) → использовать его URL. Генерацию не выполнять.**

**Промпт генерации:**
```
[STYLE_TAGS], [CHARACTER_DESCRIPTION],
full body character pose, front-facing view, neutral dark background,
clear detailed character design, vertical composition, 9:16 aspect ratio
```

**API call:**
- Endpoint: `fal-ai/nano-banana-2/edit`
- `aspect_ratio: "9:16"`
- Не передавай `image_urls: []` — если нет референсных URL, **omit the field entirely**
- Стиль ref ОБЯЗАН совпадать со стилем видео (photorealistic → photorealistic, anime → anime)

**Сохранить:** `scenes/refs/character-ref.png`

**Стоимость:** ~$0.04

---

## ФАЗА 3: ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ

Последовательная генерация с chain reference:

| Сцена | image_urls |
|-------|-----------|
| 1 | `[character-ref-url]` |
| 2 | `[character-ref-url, scene-1-url]` |
| N | `[character-ref-url, scene-(N-1)-url]` |

**Правила:**
- Всегда 2 референса: anchor + предыдущая сцена
- Сцена 1 — только anchor (character-ref)
- Скачивай файлы немедленно — URL fal.ai временные
- Endpoint: `fal-ai/nano-banana-2/edit` с `aspect_ratio: "9:16"`
- Сохранять как `scenes/scene-K/scene-K.png`

---

## ФАЗА 4: АНИМАЦИЯ

### Approach 2 — Kling 2.6 Pro (без речи) / Veo3 T2V (с речью)

**ONE model for ALL scenes.** Разные модели = разная пластика и цветовая температура, ломает консистентность.

**Если модель падает → retry той же модели (до 3 раз), затем fallback (`rules/main/fallback.md`).**

##### Без речи — Kling 2.6 Pro I2V

Для каждой сцены K (где `character_speech` = null):
- `start_image_url` = scene-K.png URL
- `prompt` = `motion_prompt` из storyboard (НЕ включай `character_speech`)
- `duration` = `"5"` или `"10"` (согласно storyboard)
- `generate_audio` = `true` (Kling генерирует звуковые эффекты)
- `aspect_ratio` = `"9:16"`
- Без `end_image_url` — hard cut, NO crossfade

##### С речью — Veo3 T2V

Для каждой сцены K (где `character_speech` ≠ null):
- `prompt` = `image_prompt` + `motion_prompt` объединённые (ОБЯЗАТЕЛЬНО включи текст `character_speech`)
- `generate_audio` = `true`
- `duration` = `"8s"`
- `aspect_ratio` = `"9:16"`

### Approach 3 — T2V

Используй Veo3 T2V. `prompt` = полный `image_prompt` + `motion_prompt` объединённые.

### Polling и загрузка

- Проверяй статус каждые 15 сек
- Скачивай каждый `scene-K.mp4` сразу после готовности
- Верифицируй: файл > 1000 байт

---

## ФАЗА 5: СБОРКА (FFmpeg)

**Локальный FFmpeg:** `/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg`

Задай переменную: `FFMPEG=/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg`

### 5.1 Масштабирование (каждая сцена)

```bash
$FFMPEG -y -i scenes/scene-K/scene-K.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -r 30 -c:v libx264 -preset slow -crf 10 -pix_fmt yuv420p \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  scenes/scene-K/scene-K-scaled.mp4
```

Обязательные параметры: `-r 30`, `-preset slow -crf 10`, `-ar 44100 -ac 2`

### 5.2 Склейка (hard cut only)

```bash
cat > concat-list.txt << EOF
file 'scenes/scene-1/scene-1-scaled.mp4'
file 'scenes/scene-2/scene-2-scaled.mp4'
file 'scenes/scene-3/scene-3-scaled.mp4'
EOF

$FFMPEG -y -f concat -safe 0 -i concat-list.txt \
  -r 30 -c:v libx264 -preset slow -crf 10 \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  final.mp4
```

**ВАЖНО:** Concat с re-encode (`-c:v libx264`), NOT stream copy. NO crossfade/xfade.

### 5.3 Фоновая музыка (опционально)

```bash
$FFMPEG -y -i final.mp4 -i bg-music.mp3 \
  -filter_complex "[1:a]volume=0.15[music];[0:a][music]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 128k final-with-music.mp4
```

**НИКОГДА не используй `-shortest`** — обрезает видео до длины аудио. Используй `apad` если нужно.

---

## ФАЗА 6: UPLOAD & LOG

1. Загрузить `final.mp4` в Supabase Storage:
   ```
   videos/{GAME_TAG}/{YYYY-MM-DD}/standard_final.mp4
   ```
2. Записать в таблицу `video_agent_runs` (game_tag, format, date, cost, output_path)
3. Показать пользователю отчёт о стоимости:
   - N изображений × $0.04
   - 1 character ref × $0.04
   - N анимаций × $0.14/сек (Kling) или $0.20-$0.40/сек (Veo3)
   - Итого

---

## Бюджет

| Подход | Максимум |
|--------|----------|
| Approach 2 (I2V) | **$5.00** |
| Approach 3 (T2V) | **$10.00** |

---

## Валидация

- [ ] `format: "standard"` присутствует в storyboard
- [ ] Подход (approach) соответствует типу контента
- [ ] `character_speech` ≠ null → модель Veo3 T2V; `character_speech` = null → Kling I2V
- [ ] Одна модель на все сцены (не миксовать Kling + Veo3)
- [ ] `camera_angle` разный для каждого соседнего клипа
- [ ] `motion_prompt` содержит минимум 2 действия
- [ ] `image_prompt` содержит "vertical composition, 9:16 aspect ratio"
- [ ] Если речь → текст включён в `motion_prompt` (Veo3)
- [ ] Если без речи → `motion_prompt` НЕ содержит текст речи
- [ ] Бюджет не превышен ($5 I2V / $10 T2V)
- [ ] `visual_identity.character_description` — минимум 8 визуальных деталей
- [ ] `visual_identity.environment_description` — конкретная локация, не абстрактная
- [ ] Narrative arc полный (hook → development → climax)
- [ ] `facial_expression` — конкретное выражение лица в каждом клипе (не абстрактное)
- [ ] `gaze_direction` указан для ВСЕХ сцен с 2+ видимыми персонажами
- [ ] Camera movement в `motion_prompt` УНИКАЛЬНЫЙ для каждого клипа
- [ ] `image_prompt` длина: 40–80 слов
- [ ] Для каждого клипа есть покадровый план: минимум 2 разных действия
- [ ] "First/Then" в motion_prompt — только смена действия, НЕ смена локации
- [ ] Character Reference сгенерирован (или взят из game_assets)
- [ ] Chain reference использован при генерации изображений (Фаза 3)

---

## Анти-паттерны

**НЕ делай:**
- Не миксуй Kling I2V и Veo3 T2V в одном видео — разная пластика и цветовая температура
- Не передавай `character_speech` в Kling I2V — модель не генерирует голос
- Не делай больше 4 клипов без обоснования — каждый клип должен нести уникальное действие
- Не используй `end_image_url` — только hard cut между разными планами камеры
- Не используй `-shortest` в FFmpeg — обрезает видео до длины аудио
- ❌ "high quality, masterpiece, best quality, 4K, ultra HD" — мусорные теги
- ❌ "no watermark, no text, no artifacts" — модели плохо обрабатывают отрицания
- ❌ "beautiful", "amazing", "epic", "cool" — абстрактные прилагательные без визуального смысла
- ❌ Дублирование style_tags в character_state
- ❌ Одинаковый motion_prompt суффикс во всех клипах ("Smooth cinematic motion, maintain vertical composition")
- ❌ Три+ персонажа крупно в одном 9:16 кадре
- ❌ Два соседних клипа с одинаковым типом camera_angle
- ❌ Одно зацикленное действие на весь клип — минимум 2 разных действия
- ❌ Описание позы без gaze_direction при 2+ видимых персонажах в кадре
- ❌ Абстрактные описания персонажей: "armored man" → описывай живые детали: кожа, шрамы, борода, грязь, пот
- ❌ "First/Then" в motion_prompt со сменой локации, фона или состава персонажей
- ❌ Вся речь в конце motion_prompt одним блоком — привязывай каждую реплику к действию
- ❌ Активные/резкие действия в Kling I2V (размахивание оружием, удары, прыжки, бег) — только микро-движения
- ❌ Не передавай `image_urls: []` (пустой массив) в fal-ai — omit the field entirely

---

## Выходные файлы

```
OUTPUT_DIR/
├── storyboard.json
├── scenes/
│   ├── refs/
│   │   └── character-ref.png
│   ├── scene-1/
│   │   ├── scene-1.png
│   │   ├── scene-1.mp4
│   │   └── scene-1-scaled.mp4
│   ├── scene-2/
│   │   └── ...
│   └── scene-3/
│       └── ...
├── concat-list.txt
└── final.mp4
```
