# Формат "Object Character" — Антропоморфные объекты-персонажи

Формат коротких вертикальных видео (9:16) с антропоморфными бытовыми объектами: вилка с глазами, уставшая кружка, злой тапок и т.д.

> **Отладочный режим:** Если в задаче есть фраза «Отладочный режим» — после каждой фазы останавливайся и отправляй результат на согласование с пояснением (что сделано, почему, какие решения приняты). Не переходи к следующей фазе без одобрения. Подробнее — `rules/main/workflow.md`.

---

## Когда использовать

Идея содержит бытовой объект как персонаж, "object character", "антропоморф", "talking object", или описывает предмет с эмоциями/речью.

---

## Обзор формата

- **Концепт:** бытовой объект с эмоцией произносит 10-секундный монолог от первого лица
- **Модель:** строго Kling 2.6 Pro I2V (`generate_audio: true`)
- **Аудио:** Kokoro TTS (озвучка) + Kling SFX (фоновые звуки)
- **Речь:** через TTS overlay, `character_speech: null` в storyboard
- **Длительность:** 10 сек (single) / 5 × 10 сек (series)
- **Бюджет:** $1.50 (single) / $7.50 (series)
- **НЕ использовать Veo3 T2V.**

---

## ФАЗА 0: ИНИЦИАЛИЗАЦИЯ

1. Загрузить `tools/fal-ai.md` — API reference
2. Загрузить `rules/main/fallback.md` — обработка ошибок
3. Получить game_assets из Supabase: `GET /rest/v1/game_assets?game_tag=eq.{GAME_TAG}&select=*`
4. Определить из идеи: объект, эмоцию, контекст, конфликт
5. Написать `character_description` (8+ деталей) и скрипт (≤25 слов, от первого лица)
6. Определить формат: `single` (1 ролик) или `series` (5 роликов)

---

## Концепция формата

Каждый объект-персонаж — это бытовой предмет с выраженной эмоцией, который произносит 10-секундный монолог от первого лица. Объект должен быть узнаваем как предмет, но оживлён через:
- глаза и брови
- рот
- руки или жест (конечность-подобные выросты)
- поза / наклон
- взаимодействие с окружением

**Антропоморфизм усиливает личность, но НЕ убивает идентичность объекта.**

---

## Pipeline: Object Character

### Вход

Пользователь указывает:
- объект (обязательно) — например "вилка", "кружка", "тапок"
- эмоция (опционально) — "раздражение", "паника", "сарказм"
- сцена/контекст (опционально) — "на кухне после ужина"
- формат (опционально): `single` (1 ролик) или `series` (5 роликов: main + 4 related)

### Логика интерпретации

| Дано | Действие |
|------|----------|
| Только объект | Выведи эмоцию, сцену и конфликт |
| Объект + эмоция | Выведи самое сильное окружение для этой эмоции |
| Объект + сцена | Выведи самую читаемую эмоцию |
| Объект + эмоция + сцена | Сохрани всё, усиль кинематографичность |
| Несколько объектов | Выбери одного лида, остальные — related |

### Предпочтительные эмоции

- раздражённая правда
- усталый реализм
- тревожное предупреждение
- отвращение
- гордость
- паника
- сарказм
- защитная фрустрация
- изнурённая честность

**Избегай:** позитивная мотивация, абстрактный оптимизм, нейтральное повествование.

---

## ФАЗА 1: Сторибоард

### 1.1 Генерация персонажа

Для main объекта определи:

```json
{
  "object": "fork",
  "emotion": "defensive frustration",
  "context": "kitchen drawer after dinner party",
  "conflict": "always gets picked last, spoons get all the love",
  "character_description": "anthropomorphic silver dinner fork with expressive cartoon eyes with thick angry eyebrows, wide open mouth mid-rant, two small arm-like prongs gesturing wildly, slightly bent posture leaning forward aggressively, metallic silver surface with scratches and food residue, four sharp tines like spiky hair"
}
```

**Правила `character_description` (8+ деталей):**
1. Материал/текстура объекта (metallic, ceramic, rubber, wood)
2. Глаза — форма, размер, выражение (wide cartoon eyes, squinting suspicious eyes)
3. Брови — конкретная форма (thick angry eyebrows, raised worried eyebrows)
4. Рот — конкретное выражение (wide open mouth mid-rant, tight-lipped grimace)
5. Конечности — тип и действие (small arm-like handles gesturing, stubby legs stomping)
6. Поза — наклон, направление (leaning forward aggressively, slouched and defeated)
7. Износ/детали поверхности (scratches, stains, cracks, chips, dust)
8. Уникальная деталь объекта (four sharp tines, chipped rim, frayed laces)

### 1.2 Скрипт (монолог)

10-секундный монолог от первого лица. Правила:
- Говори как сам объект
- Естественно произносимый текст (записываемый без правок)
- Содержит: напряжение / фрустрацию / предупреждение / жалобу / инсайт / сарказм
- Эмоционально прямой, без филлеров
- **НЕ обращайся к аудитории** ("you guys", "подписывайтесь")
- **НЕ используй CTA-фразы**
- **НЕ используй мотивационный тон**
- Макс 25 слов (для 10 сек)

**Пример:**
```
"Every single dinner party — spoons in the spotlight, knives get respect, and me? I'm the one they drop on the floor."
```

### 1.3 Сторибоард (1 клип = 1 объект)

Формат Object Character — **1 клип на объект** (10 сек, Kling I2V).

```json
{
  "title": "Angry Fork — Kitchen Drawer Rant",
  "game_tag": "ObjectCharacter",
  "approach": 2,
  "format": "object-character",
  "duration_target_sec": 10,
  "visual_identity": {
    "character_description": "anthropomorphic silver dinner fork with expressive cartoon eyes with thick angry eyebrows, wide open mouth mid-rant, two small arm-like prongs gesturing wildly, slightly bent posture leaning forward aggressively, metallic silver surface with scratches and food residue, four sharp tines like spiky hair",
    "environment_description": "inside a dark kitchen drawer, surrounded by other cutlery silhouettes, warm light leaking through the drawer gap above, wooden interior with crumb debris",
    "style_tags": "stylized animated 3D render, Pixar-quality character design, expressive anthropomorphic object, vibrant colors, cinematic depth of field",
    "color_palette": "warm amber (#d4a574), cool silver (#c0c0c0), dark wood (#3e2723), soft gold light (#ffcc02)",
    "lighting": "warm volumetric light from above through drawer gap, soft ambient from below, dramatic rim light on character edges",
    "camera_style": "medium close-up, slightly below eye level"
  },
  "narrative_arc": {
    "hook": "Fork rants about being ignored",
    "climax": "Emotional peak — fork slams prong on drawer floor"
  },
  "tts": {
    "text": "Every single dinner party — spoons in the spotlight, knives get respect, and me? I'm the one they drop on the floor.",
    "voice": "am_adam",
    "speed": 1.1
  },
  "scenes": [
    {
      "index": 1,
      "beats": ["hook", "climax"],
      "duration_sec": 10,
      "character_state": "leaning forward aggressively, one prong-arm pointing outward accusingly, mouth wide open mid-rant",
      "facial_expression": "thick furrowed eyebrows, wide angry cartoon eyes, mouth open showing frustration",
      "character_speech": null,
      "environment_state": "dim drawer interior, other utensils as dark silhouettes, warm light shaft from above, crumbs scattered",
      "camera_angle": "medium close-up, slightly below eye level",
      "image_prompt": "stylized animated 3D render, Pixar-quality character design, expressive anthropomorphic object, vibrant colors, cinematic depth of field, anthropomorphic silver dinner fork with expressive cartoon eyes with thick angry eyebrows, wide open mouth mid-rant, two small arm-like prongs gesturing wildly, slightly bent posture leaning forward, metallic silver surface with scratches, leaning forward aggressively pointing one prong-arm outward accusingly, inside dark kitchen drawer surrounded by cutlery silhouettes, warm volumetric light from above through drawer gap, dramatic rim light, medium close-up, vertical composition, 9:16 aspect ratio",
      "motion_prompt": "Camera slowly pushes in toward the fork's face. The fork leans forward, gestures wildly with prong-arms, slams one prong on the drawer floor. Other utensils in background shift slightly. Warm light pulses gently from above. Preserve the character's appearance from the reference image. Expressive animated motion, building frustration energy."
    }
  ]
}
```

**ВАЖНО — `character_speech: null`:**
Kling I2V НЕ генерирует голос. Речь накладывается через Kokoro TTS в фазе сборки. Поэтому `character_speech` в storyboard = `null`, а текст монолога хранится в секции `tts`.

---

## ФАЗА 2: Character Reference

Генерация якорного изображения объекта-персонажа:

```
[STYLE_TAGS], [CHARACTER_DESCRIPTION],
full body character pose, front-facing view, neutral dark background,
clear detailed character design, vertical composition, 9:16 aspect ratio
```

Сохрани как `character-ref.png`. Стоимость: ~$0.04.

---

## ФАЗА 3: Генерация изображения

1 сцена = 1 изображение (Nano Banana 2).
- `image_urls`: `[character-ref-url]`
- `image_prompt` из storyboard

---

## ФАЗА 4: Анимация — Kling 2.6 Pro I2V

**Строго Kling.** Параметры:
- `start_image_url`: scene-1.png URL
- `prompt`: `motion_prompt` из storyboard (БЕЗ текста речи)
- `duration`: `"10"`
- `generate_audio`: `true` (звуковые эффекты: скрип ящика, стук, амбиент)
- `aspect_ratio`: `"9:16"`

Стоимость: $1.40 (10 сек с аудио).

---

## ФАЗА 5: Сборка — TTS + FFmpeg

### 5.1 Генерация озвучки (Kokoro TTS)

```bash
curl -s -X POST "https://queue.fal.run/fal-ai/kokoro/american-english" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Every single dinner party — spoons in the spotlight, knives get respect, and me? I am the one they drop on the floor.",
    "voice": "am_adam",
    "speed": 1.1
  }'
```

Параметры из `tts` секции storyboard. Стоимость: ~$0.02.

**Выбор голоса по эмоции:**

| Эмоция | Голос | Скорость |
|--------|-------|----------|
| Раздражение, сарказм | `am_adam` или `am_eric` | 1.1 |
| Паника, тревога | `af_bella` или `am_puck` | 1.2 |
| Усталость, грусть | `am_michael` или `af_river` | 0.95 |
| Гордость, самоуверенность | `am_onyx` или `af_heart` | 1.0 |
| Отвращение | `am_echo` | 1.05 |

### 5.2 Масштабирование видео

```bash
$FFMPEG -y -i scene-1.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -r 30 -c:v libx264 -preset slow -crf 10 -pix_fmt yuv420p \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  scene-1-scaled.mp4
```

### 5.3 Наложение озвучки на видео

```bash
# Скачай аудио
curl -s -o voiceover.wav "$AUDIO_URL"

# Определи длину TTS для обрезки клипа
TTS_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 voiceover.wav)
CLIP_DUR=$(echo "0.5 + $TTS_DUR + 1.0" | bc)

# Миксуй: Kling SFX тише, голос громче, обрежь по TTS
$FFMPEG -y -i scene-1-scaled.mp4 -i voiceover.wav \
  -filter_complex "[0:a]volume=0.4[sfx];[1:a]adelay=500|500,volume=1.0[voice];[sfx][voice]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -t $CLIP_DUR \
  -c:v copy -ar 44100 -ac 2 -c:a aac -b:a 128k final.mp4
```

**Логика миксования:**
- Kling SFX (звуковые эффекты) — `volume=0.4` (фоновые)
- Kokoro TTS (голос) — `volume=1.0` (основной), `adelay=500|500` (задержка 0.5s)
- `-t $CLIP_DUR` — обрезка: 0.5s + TTS + 1s пауза. **НИКАКИХ стоп-кадров после речи**
- **НИКОГДА не используй `-shortest`** — обрезает видео до длины аудио

---

## ФАЗА 6: UPLOAD & LOG

1. Загрузи `final.mp4` в Supabase Storage:
   - Путь: `videos/{GAME_TAG}/{YYYY-MM-DD}/object-character_final.mp4`
   - Получи публичный URL

2. Запиши лог в `video_agent_runs`:
   - game_tag, input_idea, approach_used, model_used, total_cost_usd, output_video_url, status, video_duration_seconds, scenes

3. Покажи отчёт о стоимости пользователю.

---

## Формат "Series" (5 роликов)

Если `format: "series"` — генерируй main + 4 related объекта-персонажа.

### Related characters — правила

4 объекта из той же тематической вселенной через:
- комнату (кухня: вилка, кружка, губка, тёрка)
- рутину (утро: будильник, зубная щётка, тапок, кофеварка)
- категорию (канцелярия: степлер, ножницы, скотч, карандаш)
- эмоциональную тему (выгорание: лампочка, батарейка, зажигалка, свеча)
- бытовую проблему (беспорядок: носок, пульт, зарядка, ключи)

**Каждый related character ОБЯЗАН иметь:**
- Уникальный объект (не повторять основной)
- Уникальную эмоцию или вариацию
- Уникальный конфликт
- Уникальный скрипт (НЕ повторять структуру с заменами)
- Уникальный голос (чередуй male/female, разные voice ID)

**НЕ делай:**
- 4 near-дубликата
- Одинаковые эмоциональные фразы
- Один шаблон скрипта с подстановками

### Пример series storyboard

```json
{
  "series_title": "Kitchen Drawer Chronicles",
  "format": "series",
  "episodes": [
    {
      "object": "Fork",
      "emotion": "defensive frustration",
      "context": "always picked last",
      "tts": { "text": "...", "voice": "am_adam", "speed": 1.1 }
    },
    {
      "object": "Sponge",
      "emotion": "exhausted honesty",
      "context": "used for everything, never thanked",
      "tts": { "text": "...", "voice": "af_river", "speed": 0.95 }
    },
    {
      "object": "Cheese Grater",
      "emotion": "anxious warning",
      "context": "everyone uses her wrong",
      "tts": { "text": "...", "voice": "af_bella", "speed": 1.15 }
    },
    {
      "object": "Wooden Spoon",
      "emotion": "tired pride",
      "context": "oldest tool, seen everything",
      "tts": { "text": "...", "voice": "am_michael", "speed": 0.95 }
    },
    {
      "object": "Microwave",
      "emotion": "sarcasm",
      "context": "judges everyone's food choices",
      "tts": { "text": "...", "voice": "am_eric", "speed": 1.1 }
    }
  ]
}
```

Каждый эпизод → отдельный storyboard.json → отдельный `final.mp4`.

---

## Бюджет

| Компонент | Стоимость |
|-----------|-----------|
| Character reference (Nano Banana 2) | $0.04 |
| Scene image (Nano Banana 2) | $0.04 |
| Animation 10s (Kling 2.6 Pro + audio) | $1.40 |
| TTS (Kokoro) | $0.02 |
| **Итого 1 ролик** | **~$1.50** |
| **Итого series (5 роликов)** | **~$7.50** |

Лимит: $2.00 на single, $10.00 на series.

---

## Валидация

- [ ] Объект узнаваем как предмет (не абстрактное существо)
- [ ] `character_description` содержит 8+ визуальных деталей
- [ ] Глаза, брови, рот, конечности, поза — все описаны
- [ ] Скрипт — от первого лица, ≤25 слов, без CTA, без обращения к зрителю
- [ ] Скрипт содержит конфликт/напряжение/эмоцию (не нейтральный)
- [ ] `character_speech: null` (Kling не генерит голос)
- [ ] `tts` секция заполнена (text, voice, speed)
- [ ] `motion_prompt` НЕ содержит текст речи
- [ ] `motion_prompt` содержит минимум 2 действия
- [ ] `image_prompt` содержит "vertical composition, 9:16 aspect ratio"
- [ ] `style_tags` включает "stylized animated 3D render"
- [ ] Environment привязан к реальному использованию объекта
- [ ] Для series: все 5 объектов уникальны по эмоции, конфликту, скрипту, голосу
- [ ] Бюджет не превышен

---

## Анти-паттерны

- ❌ Абстрактный объект без идентичности ("cute blob with face")
- ❌ Объект = просто человек с текстурой предмета
- ❌ Скрипт обращается к зрителю ("Hey guys!", "Subscribe!")
- ❌ Мотивационный тон ("You can do it!", "Never give up!")
- ❌ Текст речи в `motion_prompt` (Kling не генерит голос)
- ❌ `character_speech` ≠ null (должен быть null для Kling)
- ❌ Одинаковые скрипты с подстановками в series
- ❌ "nice background", "good lighting", "cool vibe" — только конкретика
- ❌ Veo3 для этого формата

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
│   └── voiceover.wav
└── final.mp4
```

Для series: каждый эпизод в отдельной OUTPUT_DIR.

