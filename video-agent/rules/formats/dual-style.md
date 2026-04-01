# Формат "Dual-Style" — Cartoon + Realistic

Концепт: в одном кадре — cartoon/chibi игровой персонаж рядом с его фотореалистичной человеческой "копией".

> **Отладочный режим:** Если в задаче есть фраза «Отладочный режим» — после каждой фазы останавливайся и отправляй результат на согласование с пояснением (что сделано, почему, какие решения приняты). Не переходи к следующей фазе без одобрения. Подробнее — `rules/main/workflow.md`.

---

## Когда использовать

- "Game vs Reality" / "Meet Your Character IRL"
- Сравнение игрового персонажа с реальным человеком
- Cosplay-контент
- "Which character are you?"

---

## Обзор формата

- **Концепт:** cartoon + realistic версия одного персонажа рядом в кадре
- **Модель:** Kling 2.6 Pro I2V (`generate_audio: true`)
- **Аудио:** Kling SFX (звуковые эффекты)
- **Речь:** нет (`character_speech: null`)
- **Длительность:** 15-30 сек (3 клипа × 5-10s)
- **Бюджет:** $5 максимум

---

## ФАЗА 0: ИНИЦИАЛИЗАЦИЯ

1. Загрузить `tools/fal-ai.md` — API reference
2. Загрузить `rules/main/fallback.md` — обработка ошибок
3. Загрузить `games/{GAME_TAG}/{GAME_TAG}.md` — конфиг игры
4. Проверить наличие dual-style Character Prompt Blocks в game config (cartoon + realistic версии)
5. Запросить game_assets из Supabase:
   ```
   GET /rest/v1/game_assets?game_tag=eq.{GAME_TAG}&select=*
   ```
   Найти ассеты с `asset_type` = `screenshot` или `character_card` для каждого персонажа.
6. Определить персонажей для каждого клипа

---

## ФАЗА 1: СЦЕНАРИЙ

### Visual Identity

```json
{
  "visual_identity": {
    "character_description": {
      "cartoon": "cartoon chibi [class] character with bold black outlines, bright flat saturated colors, exaggerated proportions, [8+ деталей внешности]",
      "realistic": "photorealistic [пол] [телосложение], [те же детали костюма что у cartoon], real skin textures, [живые детали: кожа, шрамы, грязь], [эмоция]"
    },
    "environment": "[ENVIRONMENT description]",
    "style_tags": "cartoon chibi with bold black outlines, photorealistic human counterpart, dual-style side by side, vertical composition",
    "color_palette": "[общая палитра для обеих версий]",
    "lighting": "[единое освещение для всех сцен]"
  }
}
```

- `style_tags` ОБЯЗАНЫ включать оба стиля (cartoon + realistic)
- `lighting` и `color_palette` одинаковые для всех сцен
- `character_description` содержит ДВЕ версии (cartoon и realistic)

### Narrative Arc

| Структура | Описание |
|-----------|----------|
| **Hook** | Яркий контраст — cartoon и realistic персонаж появляются рядом |
| **Development** | Оба демонстрируют характер через позу и действие |
| **Climax** | Кульминационный момент — синхронное действие или контрастная реакция |

### Пейсинг

- По умолчанию **3 клипа**, каждый 5-10s
- 1 клип = 1 персонажная пара (cartoon + realistic одного персонажа)
- Итого: 15-30 секунд

### Clip Schema

```json
{
  "index": 1,
  "beats": ["hook", "intro"],
  "duration_sec": 5,
  "character_state": "Cartoon chibi [NAME] stands confidently, realistic counterpart mirrors the stance",
  "camera_angle": "wide low-angle",
  "character_speech": null,
  "image_prompt": "[ENVIRONMENT], on the left a cartoon chibi [CHARACTER] with bold black outlines bright flat saturated colors exaggerated proportions [DETAILS], on the right a photorealistic human [MATCHING OUTFIT AND BUILD] real skin textures [DETAILS], both [ACTION/POSE], [LIGHTING], [CAMERA], vertical composition, 9:16 aspect ratio",
  "motion_prompt": "The cartoon [CHARACTER] on the left [ACTION with exaggerated movement]. The realistic [CHARACTER] on the right [MATCHING ACTION with grounded weight].",
  "negative_prompt": "blur, distort, merged characters, single character, text overlay, watermark"
}
```

**Правила camera_angle:** ОБЯЗАН отличаться от соседнего клипа.

| Клип | Рекомендуемый ракурс |
|------|----------------------|
| 1 | wide low-angle |
| 2 | medium eye-level |
| 3 | wide pull-back |

### Структура image_prompt

```
[ENVIRONMENT],
on the left a cartoon chibi [CHARACTER] with bold black outlines bright flat colors exaggerated proportions [DETAILS],
on the right a photorealistic human [MATCHING OUTFIT AND BUILD] real skin textures [DETAILS],
both [ACTION/POSE],
[LIGHTING], [CAMERA], vertical composition, 9:16 aspect ratio
```

- **40-80 слов** оптимально
- Максимум **2 фокусные точки** в 9:16 кадре
- Cartoon **всегда** слева, realistic **всегда** справа (фиксировано на всё видео)

### Ключевые правила промптинга

#### 1. Чёткое разделение стилей

Cartoon-версия ОБЯЗАНА содержать маркеры стиля, иначе AI сделает обоих реалистичными:

**Cartoon маркеры:**
- `bold black outlines` — жирные контуры
- `bright flat saturated colors` — плоская яркая заливка
- `exaggerated chibi proportions` — преувеличенные пропорции
- `large head, small body` — большая голова (если chibi)

**Realistic маркеры:**
- `photorealistic` — фотореализм
- `real skin textures` — реальная текстура кожи
- `natural proportions` — естественные пропорции
- `weathered / sun-darkened / tanned` — реалистичные детали кожи

#### 2. Связь между версиями

Обе версии одного персонажа должны быть очевидно связаны:
- **Одинаковый костюм** — цвета, тип одежды, аксессуары
- **Одинаковая поза** — `matching pose`, `mirrored stance`
- **Одинаковые ключевые детали** — если у cartoon розовая бандана, у realistic тоже

#### 3. Позиционирование

- Cartoon **всегда** на одной стороне (обычно left), realistic **всегда** на другой (right)
- `side by side` — рядом, не один за другим

#### 4. Размеры в кадре

- Cartoon может быть **меньше** (chibi = маленький), realistic — крупнее
- Это нормально и даже желательно — подчёркивает контраст стилей
- Не пытайся выровнять их по высоте в промпте

### Motion Prompt

- Описывай действия **обоих** персонажей отдельно:
  ```
  The cartoon pirate on the left bounces with exaggerated steps.
  The realistic pirate on the right walks with heavy confident swagger.
  ```
- Можно добавлять взаимодействие:
  ```
  Real pirate strokes his beard, cartoon pirate copies the gesture with oversized hand.
  ```
- `character_speech: null` для ВСЕХ клипов (Kling I2V, нет речи)

### Мульти-персонажное видео

Если показываем несколько персонажей (каждому свой клип):

| Аспект | Правило |
|--------|---------|
| Клипы | 1 клип = 1 пара (cartoon + realistic одного персонажа) |
| Reference | Каждый клип получает свой image_urls с ассетом текущего персонажа |
| Chain reference | НЕ используется между клипами разных персонажей |
| style_tags | Единые для всех клипов |
| lighting | Единое или подобранное под среду клипа |
| camera_angle | Разный для каждого соседнего клипа |

### Character Prompt Blocks

В `games/{GAME_TAG}/{GAME_TAG}.md` описывай ДВЕ версии каждого персонажа:

```markdown
### Hero Name (cartoon)
`cartoon chibi [class] character with bold black outlines, bright flat saturated colors, exaggerated proportions, [8+ деталей внешности]`

### Hero Name (realistic counterpart)
`photorealistic [пол] [телосложение], [те же детали костюма что у cartoon], real skin textures, [живые детали: кожа, шрамы, грязь], [эмоция]`
```

### Сохранение storyboard.json

После составления сценария сохрани `storyboard.json` в `OUTPUT_DIR/` до начала генерации.

---

## ФАЗА 2: CHARACTER REFERENCE

- Используй **игровой ассет** (скриншот, character card) как `image_urls[0]` при генерации изображений
- Ассет должен соответствовать cartoon-стилю персонажа — помогает AI "увидеть" стиль
- **НЕ используй chain reference** между клипами разных персонажей
- Для мульти-персонажного видео: отдельный ref для каждой персонажной пары

**Источники ассетов (приоритет):**
1. `game_assets` из Supabase (`asset_type = screenshot` или `character_card`)
2. Локальный файл из `games/{GAME_TAG}/assets/refs/`
3. Если ассет отсутствует — сгенерируй через Nano Banana 2:
   ```
   [STYLE_TAGS], [CHARACTER_DESCRIPTION cartoon version],
   full body character pose, standing confident, [ENVIRONMENT BACKGROUND],
   clear detailed character design, vertical composition, 9:16 aspect ratio
   ```
   Сохрани как `scenes/refs/character-ref.png`.

---

## ФАЗА 3: ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ

Генерируй сцены **последовательно** через Nano Banana 2 (`fal-ai/nano-banana-2/edit`).

### Chain Reference

- **Сцена 1:** `image_urls: [character-asset-url]`
- **Сцена 2+:** `image_urls: [character-asset-url, scene-(K-1)-url]`

### Правила для мульти-персонажного видео

- Каждый клип разного персонажа начинает chain **заново**
- Сцена 1 персонажа B: `image_urls: [character-B-asset-url]` (НЕ передавай сцену персонажа A)
- Chain reference НЕ пересекается между разными персонажами

### Параметры запроса

```json
{
  "prompt": "[image_prompt из storyboard]",
  "image_urls": ["[character-asset-url]"],
  "aspect_ratio": "9:16"
}
```

### Валидация результата

- Проверить размер файла > 1000 байт
- Сохранить как `scenes/scene-K/scene-K.png`

---

## ФАЗА 4: АНИМАЦИЯ (Kling 2.6 Pro I2V)

Модель: `fal-ai/kling-video/v2.6/pro/image-to-video`

Для каждой сцены K:

```json
{
  "start_image_url": "scene-K.png URL",
  "prompt": "[motion_prompt из storyboard]",
  "duration": "5",
  "generate_audio": true,
  "aspect_ratio": "9:16"
}
```

**Правила:**
- `generate_audio: true` — Kling генерирует SFX
- `character_speech: null` — речь отсутствует во всех клипах
- `duration`: `"5"` или `"10"` согласно storyboard
- **Одна модель** для всех сцен — не смешивай модели внутри одного видео
- Без `end_image_url` — только hard cut
- `negative_prompt`: `"blur, distort, merged characters, text overlay, watermark"`

**Polling:** каждые 15 секунд до получения результата. Проверить размер файла > 1000 байт.

Сохранить как `scenes/scene-K/scene-K.mp4`.

---

## ФАЗА 5: СБОРКА (FFmpeg)

```bash
FFMPEG=/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg
```

### 5.1 Масштабирование

Масштабировать каждый клип до 1080×1920, 30fps, CRF 10, AAC 44100Hz stereo:

```bash
$FFMPEG -y -i scenes/scene-K/scene-K.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -r 30 -c:v libx264 -preset slow -crf 10 -pix_fmt yuv420p \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  scenes/scene-K/scene-K-scaled.mp4
```

### 5.2 Склейка (hard cut, re-encode)

```bash
cat > concat-list.txt << EOF
file 'scenes/scene-1/scene-1-scaled.mp4'
file 'scenes/scene-2/scene-2-scaled.mp4'
file 'scenes/scene-3/scene-3-scaled.mp4'
EOF

$FFMPEG -y -f concat -safe 0 -i concat-list.txt \
  -r 30 -c:v libx264 -preset slow -crf 10 \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  assembled.mp4
```

**Concat с re-encode** (не `-c copy`). Hard cut — без crossfade.

### 5.3 Фоновая музыка (опционально)

```bash
$FFMPEG -y -i assembled.mp4 -i bg-music.mp3 \
  -filter_complex "[0:a]volume=0.6[sfx];[1:a]volume=0.15[music];[sfx][music]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 128k \
  final.mp4
```

- Kling SFX: `volume=0.6`
- Фоновая музыка: `volume=0.15`
- **НИКОГДА не используй `-shortest`** — обрежет видео до длины аудио

---

## ФАЗА 6: UPLOAD & LOG

1. Загрузи `final.mp4` в Supabase Storage:
   ```
   videos/{GAME_TAG}/{YYYY-MM-DD}/dual-style_final.mp4
   ```

2. Залогируй в таблицу `video_agent_runs`:
   - `game_tag`, `format`, `output_path`, `cost_total`, `duration_sec`, `created_at`

3. Покажи отчёт о стоимости:
   ```
   Character ref:     $X.XX
   Scene images (N):  $X.XX
   Kling I2V (Xs):    $X.XX
   FFmpeg:            $0.00
   ─────────────────────────
   Итого:             $X.XX / $5.00
   ```

---

## Бюджет

| Компонент | Стоимость |
|-----------|-----------|
| Character reference (game asset или Nano Banana 2) | $0.04/шт |
| Scene images (3 × Nano Banana 2) | $0.12 |
| Kling I2V (3 × 5-10s, с аудио) | 15-30s × $0.14 = $2.10-$4.20 |
| FFmpeg (локальный) | $0.00 |
| **Итого** | **~$2.50-$4.50** |

**Лимит:** $5.00. Остановись если расход > $4.50.

---

## Валидация

- [ ] Cartoon маркеры присутствуют в image_prompt (`bold black outlines`, `bright flat saturated colors`, `exaggerated proportions`)
- [ ] Realistic маркеры присутствуют в image_prompt (`photorealistic`, `real skin textures`)
- [ ] Костюм/поза/детали совпадают между cartoon и realistic версиями
- [ ] Позиционирование: cartoon на одной стороне, realistic на другой (фиксировано на всё видео)
- [ ] `character_speech: null` для всех клипов
- [ ] `camera_angle` разный для каждого соседнего клипа
- [ ] `style_tags` включают оба стиля (cartoon + realistic)
- [ ] `lighting` и `color_palette` одинаковые для всех сцен
- [ ] Chain reference между клипами разных персонажей НЕ используется
- [ ] `storyboard.json` сохранён до начала генерации
- [ ] Все файлы > 1000 байт (изображения и видео)
- [ ] Бюджет не превышен ($5.00)
- [ ] `final.mp4` загружен в `videos/{GAME_TAG}/{YYYY-MM-DD}/dual-style_final.mp4`

---

## Анти-паттерны

- ❌ Только "cartoon style" без конкретных маркеров (`bold outlines`, `flat colors`) — AI сделает semi-realistic
- ❌ Один промпт без разделения "on the left / on the right" — AI объединит в одного персонажа
- ❌ Реалистичная версия без "живых" деталей (кожа, текстуры) — получится 3D рендер, не человек
- ❌ Chain reference между клипами разных персонажей — сломает внешность
- ❌ Попытка сделать cartoon и realistic одинакового размера в промпте — пусть chibi будет меньше
- ❌ `character_speech` не null — Kling I2V не генерирует голос
- ❌ `-shortest` в FFmpeg — обрежет видео

---

## Выходные файлы

```
OUTPUT_DIR/
├── storyboard.json
├── concat-list.txt
├── assembled.mp4
├── final.mp4
└── scenes/
    ├── refs/
    │   └── character-ref.png      # Game asset или сгенерированный ref
    ├── scene-1/
    │   ├── scene-1.png
    │   ├── scene-1.mp4
    │   └── scene-1-scaled.mp4
    ├── scene-2/
    │   └── ...
    └── scene-3/
        └── ...
```
