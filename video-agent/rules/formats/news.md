# Формат "Новости игры" (Game News)

Формат новостного выпуска: игровой персонаж ведёт новости из студии, оформленной в стилистике игры. Второй персонаж — репортёр с места событий.

> **Отладочный режим:** Если в задаче есть фраза «Отладочный режим» — после каждой фазы останавливайся и отправляй результат на согласование с пояснением (что сделано, почему, какие решения приняты). Не переходи к следующей фазе без одобрения. Подробнее — `rules/main/workflow.md`.

---

## Когда использовать

Идея содержит ключевые слова: "новости", "news", "game news", "weekly news", "patch recap", "обновление", "что нового".

---

## Обзор формата

- **Ведущий (anchor):** игровой персонаж за новостным столом в тематической студии
- **Репортёр (field reporter):** другой игровой персонаж, докладывает "с места событий" из игровой локации
- **3 новости** за выпуск
- **Все персонажи говорят** → `character_speech` ≠ null → **Veo3 T2V** (обязательно)
- **Бюджет:** $10 (Veo3 с аудио = $0.40/сек)

---

## ФАЗА 0: ИНИЦИАЛИЗАЦИЯ

1. Загрузить `tools/fal-ai.md` — API reference
2. Загрузить `rules/main/fallback.md` — обработка ошибок
3. Загрузить `games/{GAME_TAG}/{GAME_TAG}.md` — конфиг игры
4. Если есть `games/{GAME_TAG}/news_special.md` → загрузить
5. Запросить game_assets из Supabase:
   ```
   GET /rest/v1/game_assets?game_tag=eq.{GAME_TAG}&select=*
   ```
   Сохранить результат — использовать для ссылок на character refs, существующие ассеты.
6. Перейти к ФАЗЕ 0.5 (Исследование)

---

## ФАЗА 0.5: ИССЛЕДОВАНИЕ (Research)

**Выполняется ПЕРЕД написанием сторибоарда.**

### Шаг 1: Поиск новостей

Используй веб-поиск для нахождения 3 актуальных новостей об игре:

**Поисковые запросы:**
1. `"{game_name}" patch notes {month} {year}` — патч-ноты
2. `"{game_name}" update news {month} {year}` — обновления
3. `"{game_name}" new hero OR new character OR event {year}` — контент

**Приоритет источников:**
1. Официальные патч-ноты / сайт разработчика
2. Официальные соцсети (Twitter/X, Facebook, YouTube)
3. Крупные игровые медиа
4. Сообщества (Reddit, Discord)

### Шаг 2: Выбор 3 новостей

Критерии отбора:
- **Актуальность** — за последние 7-14 дней
- **Значимость** — влияет на игровой процесс (новый герой, баланс, событие)
- **Разнообразие** — разные типы новостей (не 3 нерфа подряд)

**Fallback:** если <3 реальных новостей — используй community highlight (популярный клип, мем, фан-арт, мета-сдвиг).

### Шаг 3: Написание скриптов

Для каждой новости напиши anchor_script (текст ведущего):
- **Максимум 20-25 слов на сцену** (должно уместиться в 8 секунд)
- Стиль: энергичный новостной ведущий
- Используй Tone of Voice из конфига игры

### Шаг 4: Сохранение

Сохрани `research.json` в OUTPUT_DIR:

```json
{
  "game_tag": "MLBB",
  "research_date": "2026-03-24",
  "news_items": [
    {
      "index": 1,
      "headline": "Aurora Rework в патче 1.9.12",
      "summary": "Aurora получила полную переработку скиллов: новый ульт замораживает область, пассивка даёт щит.",
      "source_url": "https://...",
      "type": "patch"
    },
    {
      "index": 2,
      "headline": "Новая карта для рангов",
      "summary": "Добавлена альтернативная карта для ранговых матчей с изменённой jungle зоной.",
      "source_url": "https://...",
      "type": "update"
    },
    {
      "index": 3,
      "headline": "Призовой фонд Mythic Tournament удвоен",
      "summary": "Призовой фонд турнира Mythic увеличен вдвое, регистрация до конца месяца.",
      "source_url": "https://...",
      "type": "event"
    }
  ],
  "sources_consulted": ["url1", "url2", "url3"]
}
```

---

## ФАЗА 1: СЦЕНАРИЙ

### 1.1 Visual Identity

Определи двух персонажей и два окружения на весь выпуск:

**Персонажи:**
- **Anchor (ведущий):** игровой персонаж из конфига игры; сидит за новостным столом; профессиональная, авторитетная поза
- **Field Reporter (репортёр):** другой игровой персонаж из конфига; держит микрофон; репортёрская стойка

**Окружения:**
- **Студия:** тематика соответствует игре (берётся из `games/{GAME_TAG}.md` → News Format → Studio Description). Обязательные элементы: новостной стол, экран/баннер с логотипом игры за спиной, освещение. Стол современный с элементами дизайна игры (неоновые полоски, магические руны, технологические панели — в зависимости от стиля). Экран за ведущим показывает визуал, относящийся к текущей новости.
- **Field Location (сцена 2):** локация соответствует содержанию новости #2:
  - Новость про новую карту → репортёр на новой карте
  - Новость про нового героя → репортёр на арене / тренировочном полигоне
  - Новость про ивент → репортёр на площадке ивента
  - Окружение за репортёром **активное** (частицы, движение, атмосфера)

### 1.2 Структура сцен (ФИКСИРОВАННАЯ — 4 элемента)

| Сцена | Роль | Локация | Контент | Длительность | Модель |
|-------|------|---------|---------|-------------|--------|
| 0 | **Title Card** (заставка) | — | Логотип шоу, название | 3 сек | Image + Ken Burns |
| 1 | **Anchor** (ведущий) | Студия | Приветствие + Новость #1 | 8 сек | Veo3 T2V |
| 2 | **Field Reporter** (репортёр) | Игровая локация | Новость #2 ("с места событий") | 8 сек | Veo3 T2V |
| 3 | **Anchor** (ведущий) | Студия | Новость #3 + прощание | 8 сек | Veo3 T2V |

**Итого:** ~27 секунд (3 сек заставка + 24 сек новости).

### 1.3 Правила написания скриптов

#### Сцена 1 — Ведущий в студии: приветствие + новость #1

```
"Welcome to [Show Name]! I'm [character name]. Big news — [новость #1 в 15-18 слов]!"
```

Пример:
```
"Welcome to MLBB News Flash! I'm Lancelot. Big news — Aurora just got a MASSIVE rework with a brand new ultimate!"
```

#### Сцена 2 — Репортёр с места событий: новость #2

```
"Thanks [anchor name]! I'm here at [location] where [новость #2 в 15-18 слов]!"
```

Пример:
```
"Thanks Lancelot! I'm here at the new jungle where major map changes are shaking up ranked play completely!"
```

#### Сцена 3 — Ведущий в студии: новость #3 + прощание

```
"[Новость #3 в 12-15 слов]. That's all for this week — like and subscribe!"
```

Пример:
```
"And the Mythic Tournament prize pool just got DOUBLED! That's all for this week — smash that subscribe!"
```

### 1.4 Правила промптинга

- `character_speech` ≠ null для ВСЕХ сцен (1, 2, 3) → обязательно Veo3 T2V
- `motion_prompt` ОБЯЗАН включать точный текст речи в формате: `[действие] and says: "[реплика]"`
- `camera_angle` — разный для каждого соседнего клипа
- `image_prompt`: 40-80 слов, включает описание персонажа + окружения + ракурса + `"vertical composition, 9:16"`

### 1.5 Расширения стоибоарда

Стандартный стоибоард дополняется полями:

```json
{
  "format": "news",
  "show_name": "MLBB News Flash",
  "research": {
    "file": "research.json",
    "news_items": [
      {"index": 1, "headline": "...", "type": "patch"},
      {"index": 2, "headline": "...", "type": "update"},
      {"index": 3, "headline": "...", "type": "event"}
    ]
  },
  "visual_identity": {
    "characters": {
      "anchor": {
        "name": "Lancelot",
        "character_description": "..."
      },
      "field_reporter": {
        "name": "Fanny",
        "character_description": "..."
      }
    },
    "environments": {
      "studio": "описание новостной студии...",
      "field_location": "описание локации для репортажа (зависит от новости #2)..."
    }
  },
  "scenes": [
    {
      "index": 1,
      "role": "anchor",
      "news_item_index": 1
    }
  ]
}
```

Дополнительные поля для каждой сцены:
- `role` — `"anchor"` или `"field_reporter"`
- `news_item_index` — индекс новости из `research.news_items`

### 1.6 Сохранение

Сохранить `storyboard.json` в OUTPUT_DIR.

### 1.7 Пример полного сторибоарда (MLBB)

```json
{
  "title": "MLBB News Flash - Week of March 24",
  "game_tag": "MLBB",
  "format": "news",
  "show_name": "MLBB News Flash",
  "approach": 2,
  "duration_target_sec": 24,
  "research": {
    "file": "research.json",
    "news_items": [
      {"index": 1, "headline": "Aurora Rework в патче 1.9.12", "type": "patch"},
      {"index": 2, "headline": "Новая jungle карта для рангов", "type": "update"},
      {"index": 3, "headline": "Mythic Tournament призовой фонд x2", "type": "event"}
    ]
  },
  "visual_identity": {
    "characters": {
      "anchor": {
        "name": "Lancelot",
        "character_description": "male warrior assassin Lancelot, silver armor with intricate blue engravings, flowing royal blue cape, athletic build, spiky silver-blue hair, confident piercing gaze, seated behind modern news desk"
      },
      "field_reporter": {
        "name": "Fanny",
        "character_description": "female assassin Fanny, dark purple and silver battle suit, short dark hair with purple streaks, athletic agile build, fierce determined expression, holding a microphone"
      }
    },
    "environments": {
      "studio": "modern gaming news studio with holographic screen behind desk showing MLBB logo, purple and blue neon lighting, sleek black desk with glowing blue trim, floating magical particles, professional broadcast setup",
      "field_location": "newly redesigned jungle map at golden hour, towering ancient trees with glowing vines, new buff monster visible in background, magical fog rolling through"
    },
    "style_tags": "MLBB Mobile Legends style, anime aesthetic, vibrant saturated colors, dramatic hero lighting, high detail character art",
    "color_palette": "deep blue (#1a237e), gold (#ffd700), purple neon (#9c27b0), electric blue (#00bcd4)",
    "lighting": "professional studio broadcast lighting with dramatic accents"
  },
  "narrative_arc": {
    "hook": "Ведущий открывает выпуск, сразу в главную новость",
    "development": "Репортёр на месте событий раскрывает вторую новость",
    "climax": "Ведущий завершает третьей новостью и прощается"
  },
  "scenes": [
    {
      "index": 1,
      "role": "anchor",
      "news_item_index": 1,
      "beats": ["hook", "news_1"],
      "duration_sec": 8,
      "hero": "Lancelot",
      "character_state": "seated behind news desk, turns to camera, professional authoritative posture, slight smile",
      "facial_expression": "confident professional smile with raised eyebrows for emphasis",
      "character_speech": "Welcome to MLBB News Flash! I'm Lancelot. Big news — Aurora just got a MASSIVE rework with a brand new ultimate!",
      "environment_state": "studio lights activate, holographic screen behind shows Aurora gameplay footage, neon trim pulses",
      "camera_angle": "medium close-up, slightly below eye level",
      "image_prompt": "MLBB Mobile Legends style, anime aesthetic, vibrant saturated colors, dramatic hero lighting, high detail character art, male warrior assassin Lancelot, silver armor with intricate blue engravings, flowing royal blue cape, athletic build, spiky silver-blue hair, confident piercing gaze, seated behind modern news desk, professional smile, mouth slightly open speaking expression, modern gaming news studio with holographic screen showing MLBB logo, purple and blue neon lighting, sleek black desk with glowing blue trim, professional studio broadcast lighting, medium close-up, vertical composition, 9:16 aspect ratio",
      "motion_prompt": "Camera holds steady at medium close-up. Lancelot turns to camera, gestures with hand and says: \"Welcome to MLBB News Flash! I'm Lancelot.\" He leans forward slightly, eyes widen with excitement and says: \"Big news — Aurora just got a MASSIVE rework with a brand new ultimate!\" Holographic screen behind glows and shifts. Professional news anchor energy."
    },
    {
      "index": 2,
      "role": "field_reporter",
      "news_item_index": 2,
      "beats": ["news_2_field"],
      "duration_sec": 8,
      "hero": "Fanny",
      "character_state": "standing in jungle clearing, holding microphone, wind in hair, alert reporter stance",
      "facial_expression": "enthusiastic wide eyes, energetic reporting expression",
      "character_speech": "Thanks Lancelot! I'm here at the new jungle where major map changes are shaking up ranked play completely!",
      "environment_state": "jungle environment with new glowing vines, buff monster prowling in background, magical fog, leaves rustling",
      "camera_angle": "wide shot, showing environment behind reporter",
      "image_prompt": "MLBB Mobile Legends style, anime aesthetic, vibrant saturated colors, dramatic hero lighting, high detail character art, female assassin Fanny, dark purple and silver battle suit, short dark hair with purple streaks, athletic agile build, fierce determined expression, holding microphone, reporter stance, newly redesigned jungle map at golden hour, towering ancient trees with glowing vines, new buff monster in background, magical fog, dramatic natural lighting with golden rim light, wide shot, vertical composition, 9:16 aspect ratio",
      "motion_prompt": "Camera holds wide showing the jungle behind. Fanny holds microphone, looks at camera and says: \"Thanks Lancelot! I'm here at the new jungle where major map changes are shaking up ranked play completely!\" She gestures toward the new jungle features behind her. Wind whips her hair, leaves drift past. On-location reporter energy."
    },
    {
      "index": 3,
      "role": "anchor",
      "news_item_index": 3,
      "beats": ["news_3", "cta"],
      "duration_sec": 8,
      "hero": "Lancelot",
      "character_state": "behind desk, energetic, leaning forward for emphasis, wrapping up the show",
      "facial_expression": "excited grin, eyebrows raised, high energy sign-off expression",
      "character_speech": "And the Mythic Tournament prize pool just got DOUBLED! That's all for this week — smash that subscribe!",
      "environment_state": "studio screen shows tournament bracket with gold confetti, lights flash and pulse with excitement",
      "camera_angle": "dynamic low angle, looking up at anchor",
      "image_prompt": "MLBB Mobile Legends style, anime aesthetic, vibrant saturated colors, dramatic hero lighting, high detail character art, male warrior assassin Lancelot, silver armor with intricate blue engravings, flowing royal blue cape, athletic build, spiky silver-blue hair, excited grin, leaning forward behind modern news desk, studio screen showing tournament bracket, purple and blue neon lighting, sleek black desk, gold confetti particles, professional studio broadcast lighting, dynamic low angle shot, vertical composition, 9:16 aspect ratio",
      "motion_prompt": "Camera pushes in from low angle. Lancelot leans forward excitedly and says: \"And the Mythic Tournament prize pool just got DOUBLED!\" He points at camera, studio lights flash and says: \"That's all for this week — smash that subscribe!\" Gold confetti drifts across frame. High energy sign-off."
    }
  ]
}
```

---

## ФАЗА 2: CHARACTER REFERENCE

Генерируй **ДВА** отдельных референса (по одному на персонажа):

### 2.1 Anchor Reference — `character-ref-anchor.png`

Промпт:
```
[STYLE_TAGS], [ANCHOR_CHARACTER_DESCRIPTION], seated behind news desk, professional authoritative posture,
full body, front-facing view, [STUDIO_ENVIRONMENT], vertical composition, 9:16
```

- Поза: сидит за столом, смотрит в камеру, авторитетная осанка
- Стиль должен **точно совпадать** со стилем видео (фотореал → фотореал, аниме → аниме)
- Стоимость: ~$0.04

### 2.2 Reporter Reference — `character-ref-reporter.png`

Промпт:
```
[STYLE_TAGS], [REPORTER_CHARACTER_DESCRIPTION], holding microphone, reporter stance,
full body, front-facing view, neutral dark background, vertical composition, 9:16
```

- Поза: стоит, держит микрофон, репортёрская стойка
- Стиль должен **точно совпадать** со стилем видео
- Стоимость: ~$0.04

### 2.3 Правила консистентности персонажей

- `style_tags`, `color_palette` — **идентичны** в обоих референсах и во всех 3 сценах
- `character_description` — **разный** для ведущего и репортёра
- `lighting` — может отличаться: студийное (сцены 1, 3) vs. игровое окружение (сцена 2)
- В каждом video prompt описывай внешность и одежду персонажа полностью

### 2.4 Сохранение

Сохранить оба файла в `OUTPUT_DIR/scenes/refs/`:
- `character-ref-anchor.png`
- `character-ref-reporter.png`

---

## ФАЗА 3: ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ

### 3.1 Title Card (заставка) — `title-card.png`

Сгенерируй изображение-заставку с названием шоу:

**Промпт:**
```
[STYLE_TAGS], [GAME] news broadcast title card, bold stylized text "[SHOW_NAME]" centered,
[GAME]-themed background with [GAME_ELEMENTS], dramatic lighting, broadcast graphics style,
vertical composition, 9:16 aspect ratio
```

Сохранить в `OUTPUT_DIR/scenes/title-card/title-card.png`.
Стоимость: ~$0.04

### 3.2 Изображения сцен (Veo3 T2V — изображения не нужны)

Veo3 T2V генерирует видео напрямую из текстового промпта — предварительно генерировать изображения для сцен 1-3 **не требуется**.

Однако если используются image refs для консистентности персонажей, передавай `image_urls` в запрос Veo3:

**Chain Reference для новостного формата:**

| Сцена | Роль | `image_urls` |
|-------|------|-------------|
| 1 | Anchor | `[anchor-ref-url]` |
| 2 | Field Reporter | `[reporter-ref-url]` |
| 3 | Anchor | `[anchor-ref-url, scene-1-url]` |

**ВАЖНО:**
- Сцена 2 **НЕ** цепляется к сцене 1 (другой персонаж!)
- Сцена 3 цепляется к **сцене 1** (тот же персонаж — ведущий), **не к сцене 2**
- `image_urls` не передавать как пустой массив — либо с URL, либо поле не передавать вообще

---

## ФАЗА 4: АНИМАЦИЯ

### 4.1 Title Card — Ken Burns (FFmpeg)

```bash
/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg -y \
  -loop 1 -i title-card.png \
  -vf "zoompan=z=zoom+0.003:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d=75:s=1080x1920:fps=25" \
  -t 3 -c:v libx264 -pix_fmt yuv420p title-card.mp4
```

Длительность: 3 секунды. Сохранить в `OUTPUT_DIR/scenes/title-card/title-card.mp4`.

### 4.2 Сцены 1-3 — Veo3 T2V

**Параметры запроса:**

```json
{
  "prompt": "[image_prompt]. [motion_prompt]",
  "duration": "8s",
  "aspect_ratio": "9:16",
  "generate_audio": true
}
```

- `prompt` = `image_prompt` + `motion_prompt` объединённые; **ОБЯЗАН включать точный текст `character_speech`**
- `generate_audio: true` — обязательно (персонажи говорят)
- `duration: "8s"` — для всех трёх сцен
- `aspect_ratio: "9:16"` — для всех трёх сцен
- **Одна модель** для всех сцен — не смешивать модели в одном ролике

**Endpoint:** `fal-ai/veo3`

**Polling:** каждые 15 секунд до готовности. После получения URL — проверить размер файла (>1000 байт).

**Сохранение:**
- `OUTPUT_DIR/scenes/scene-1/scene-1.mp4`
- `OUTPUT_DIR/scenes/scene-2/scene-2.mp4`
- `OUTPUT_DIR/scenes/scene-3/scene-3.mp4`

---

## ФАЗА 5: СБОРКА (FFmpeg)

FFmpeg: `/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg`

### 5.1 Масштабирование клипов

Масштабировать все клипы (включая title card) к 1080×1920, 30fps, CRF 10, AAC 44100Hz стерео:

```bash
/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg -y \
  -i INPUT.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -r 30 -c:v libx264 -crf 10 \
  -c:a aac -ar 44100 -ac 2 \
  OUTPUT-scaled.mp4
```

Применить ко всем клипам: `title-card.mp4`, `scene-1.mp4`, `scene-2.mp4`, `scene-3.mp4`.

### 5.2 Конкатенация

Объединить `title-card-scaled.mp4` + `scene-1-scaled.mp4` + `scene-2-scaled.mp4` + `scene-3-scaled.mp4`:

```bash
# Создать список файлов
echo "file 'title-card-scaled.mp4'
file 'scene-1-scaled.mp4'
file 'scene-2-scaled.mp4'
file 'scene-3-scaled.mp4'" > concat_list.txt

/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg -y \
  -f concat -safe 0 -i concat_list.txt \
  -c:v libx264 -crf 10 -r 30 \
  -c:a aac -ar 44100 -ac 2 \
  news_concat.mp4
```

### 5.3 Фоновая музыка (опционально)

Если требуется фоновая музыка (volume=0.15):

```bash
/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg -y \
  -i news_concat.mp4 \
  -i MUSIC_TRACK.mp3 \
  -filter_complex "[1:a]volume=0.15[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -ar 44100 -ac 2 \
  news_final.mp4
```

**НИКОГДА не использовать `-shortest`** — использовать `duration=first` для amix.

Без музыки: переименовать `news_concat.mp4` → `news_final.mp4`.

---

## ФАЗА 6: UPLOAD & LOG

### 6.1 Загрузка в Supabase Storage

Загрузить `news_final.mp4` в бакет `videos`:

```
videos/{GAME_TAG}/{YYYY-MM-DD}/news_final.mp4
```

Пример: `videos/MLBB/2026-03-24/news_final.mp4`

Использовать `queue/upload-asset.sh` или прямой запрос к Supabase Storage API.

### 6.2 Логирование в video_agent_runs

Записать строку в таблицу `video_agent_runs`:

```json
{
  "game_tag": "MLBB",
  "format": "news",
  "title": "MLBB News Flash - Week of March 24",
  "output_url": "videos/MLBB/2026-03-24/news_final.mp4",
  "duration_sec": 27,
  "total_cost_usd": 9.84,
  "storyboard_path": "OUTPUT_DIR/storyboard.json",
  "created_at": "2026-03-24T..."
}
```

### 6.3 Отчёт о стоимости

Вывести итоговый cost report:

```
=== COST REPORT ===
Character ref (anchor):   $0.04
Character ref (reporter): $0.04
Title card:               $0.04
Scene 1 (Veo3 T2V 8s):   $3.20
Scene 2 (Veo3 T2V 8s):   $3.20
Scene 3 (Veo3 T2V 8s):   $3.20
──────────────────────────────
TOTAL:                    ~$9.72
```

---

## Бюджет

| Компонент | Количество | Стоимость |
|-----------|------------|-----------|
| Character ref (anchor) | 1 | ~$0.04 |
| Character ref (reporter) | 1 | ~$0.04 |
| Title card (заставка) | 1 | ~$0.04 |
| Veo3 T2V 8s (с аудио) | 3 | 3 × $3.20 = $9.60 |
| **ИТОГО** | | **~$9.72** |

---

## Валидация

- [ ] `format: "news"` присутствует в storyboard.json
- [ ] `research.json` сохранён с 3 новостями
- [ ] Title card (сцена 0) — заставка с названием шоу
- [ ] 3 основные сцены (+ заставка = 4 элемента)
- [ ] Сцена 1: `role: "anchor"`, сцена 2: `role: "field_reporter"`, сцена 3: `role: "anchor"`
- [ ] Каждая сцена имеет `news_item_index`
- [ ] `character_speech` ≠ null во ВСЕХ сценах (1, 2, 3)
- [ ] Речь ≤ 25 слов на сцену (чтобы уместиться в 8 секунд)
- [ ] `motion_prompt` включает точный текст речи
- [ ] Сцена 2 использует ДРУГОГО персонажа (не ведущего)
- [ ] Два character reference сгенерированы (anchor + reporter)
- [ ] Chain reference: сцена 3 → сцена 1 (не сцена 2)
- [ ] Локация сцены 2 соответствует содержанию новости #2
- [ ] Стилистика character ref совпадает со стилистикой видео (фотореал → фотореал, аниме → аниме)
- [ ] `camera_angle` разный для каждого соседнего клипа
- [ ] `image_urls` не передаётся как пустой массив (либо с URL, либо без поля)
- [ ] `show_name` из конфига игры
- [ ] `news_final.mp4` загружен в Supabase Storage
- [ ] Запись добавлена в `video_agent_runs`

---

## Анти-паттерны

**НЕ делай:**
- Не используй Kling I2V для этого формата — только Veo3 T2V (персонажи говорят)
- Не превышай 25 слов на сцену — Veo3 не уложит длинную речь в 8 секунд
- Не используй chain reference между сценами anchor и reporter — это разные персонажи
- Не делай локацию репортажа (сцена 2) generic ("game world") — привязывай к конкретной новости
- Не используй одинаковый `camera_angle` для соседних сцен
- Не пропускай фазу исследования (ФАЗА 0.5) — новости должны быть реальными и актуальными
- Не используй `-shortest` в FFmpeg с TTS/аудио — используй `duration=first` или `apad`

---

## Выходные файлы

```
OUTPUT_DIR/
├── storyboard.json
├── research.json
├── scenes/
│   ├── refs/
│   │   ├── character-ref-anchor.png
│   │   └── character-ref-reporter.png
│   ├── title-card/
│   │   ├── title-card.png
│   │   └── title-card.mp4
│   ├── scene-1/
│   │   └── scene-1.mp4
│   ├── scene-2/
│   │   └── scene-2.mp4
│   └── scene-3/
│       └── scene-3.mp4
└── news_final.mp4
```
