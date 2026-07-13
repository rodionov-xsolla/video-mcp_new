# fal.ai API Reference

Справочник по API fal.ai для генерации изображений, видео и озвучки.

---

## Аутентификация

Все запросы требуют заголовок:
```
Authorization: Key $FAL_KEY
```

Переменная `FAL_KEY` должна быть установлена в окружении перед запуском.

---

## 1. Nano Banana 2 — основная модель генерации изображений

**Стоимость:** ~$0.08 за изображение

> **Основная модель для всех сцен, character refs, bg-assets.**

### 1a. Text-to-Image (без референса — для character references)

**Endpoint:** `https://queue.fal.run/fal-ai/nano-banana-2`
**Метод:** POST (асинхронный — нужен polling)

> **Используй этот endpoint для генерации character references** (нет входного изображения). Поле `image_urls` НЕ передаётся.

### 1b. Image-to-Image / Edit (с референсом — для сцен)

**Endpoint:** `https://queue.fal.run/fal-ai/nano-banana-2/edit`
**Метод:** POST (асинхронный — нужен polling)

> **Используй этот endpoint для генерации сцен** с chain reference (image_urls обязателен).

### Запрос

```bash
curl -s -X POST "https://queue.fal.run/fal-ai/nano-banana-2/edit" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Star Trek cinematic 3D animation, Worf in dramatic pose, Klingon warrior armor, dark council chamber, 9:16 vertical",
    "image_urls": ["https://supabase.../character-ref.png"],
    "aspect_ratio": "9:16",
    "output_format": "png",
    "resolution": "1K",
    "safety_tolerance": "5"
  }'
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Текстовое описание (мин 3 символа, макс 50000) |
| `image_urls` | array of strings | Нет | URL-ы референсных изображений для chain reference консистентности. Сцена 1: [character-ref-url], Сцена N: [character-ref-url, scene-(N-1)-url]. **Не передавай поле вообще** если нет референса (пустой массив `[]` вызывает ошибку) |
| `aspect_ratio` | enum | Нет | `"9:16"` для вертикального видео. Варианты: "1:1", "16:9", "9:16", "4:3", "3:4" и др. По умолчанию: "auto" |
| `num_images` | integer | Нет | 1-4, по умолчанию 1 |
| `output_format` | enum | Нет | "jpeg", "png", "webp". По умолчанию "png" |
| `resolution` | enum | Нет | "0.5K", "1K", "2K", "4K". По умолчанию "1K" |
| `safety_tolerance` | enum | Нет | "1"-"6", по умолчанию "4". Для игрового контента ставь "5" |
| `seed` | integer | Нет | Для воспроизводимости результатов |

### Ответ

```json
{
  "images": [
    {
      "url": "https://fal.media/files/abc123/image.png",
      "width": 1080,
      "height": 1920,
      "content_type": "image/png"
    }
  ]
}
```

### Polling и скачивание (ОБЯЗАТЕЛЬНО)

Оба endpoint'а (с `/edit` и без) — **асинхронные**. Нужен polling.

```bash
# 1. Отправь запрос → получи request_id
REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')

# 2. Polling каждые 10 секунд
while true; do
  STATUS=$(curl -s "https://queue.fal.run/fal-ai/nano-banana-2/requests/$REQUEST_ID/status" \
    -H "Authorization: Key $FAL_KEY" | jq -r '.status')
  case "$STATUS" in
    "COMPLETED") break ;;
    "FAILED") echo "FAILED"; exit 1 ;;
    *) sleep 10 ;;
  esac
done

# 3. Получи результат
RESULT=$(curl -s "https://queue.fal.run/fal-ai/nano-banana-2/requests/$REQUEST_ID" \
  -H "Authorization: Key $FAL_KEY")
IMAGE_URL=$(echo "$RESULT" | jq -r '.images[0].url')
curl -s -o scene-1.png "$IMAGE_URL"

# 4. Проверь что файл скачался (>1000 bytes)
ls -la scene-1.png
```

> **ВАЖНО:** URL для polling/результата всегда `fal-ai/nano-banana-2/requests/{ID}` — без `/edit`, даже если запрос был на `/edit` endpoint.

### Chain Reference Usage

```bash
# Сцена 1 (только референс персонажа):
"image_urls": ["$CHARACTER_REF_URL"]

# Сцена 2+ (референс персонажа + предыдущая сцена):
"image_urls": ["$CHARACTER_REF_URL", "$PREV_SCENE_URL"]
```

---

## 1c. GPT Image 1 — fallback генерация изображений

**Endpoint:** `https://queue.fal.run/fal-ai/gpt-image-1/text-to-image`
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** ~$0.02 за изображение

> **Используй ТОЛЬКО как fallback**, если Nano Banana 2 не работает. GPT Image 1 не поддерживает `image_urls` (нет chain reference), поэтому консистентность персонажа хуже.

### Запрос

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/gpt-image-1/text-to-image" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Star Trek cinematic 3D animation, Worf in dramatic pose, Klingon warrior armor, dark council chamber, 9:16 vertical",
    "image_size": "1024x1536"
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Текстовое описание |
| `image_size` | enum | Нет | `"auto"`, `"1024x1024"`, `"1536x1024"`, `"1024x1536"`. Для 9:16 используй `"1024x1536"` |

### Polling и получение результата

```bash
STATUS=$(curl -s "https://queue.fal.run/fal-ai/gpt-image-1/requests/$REQUEST_ID/status" \
  -H "Authorization: Key $FAL_KEY" | jq -r '.status')

RESULT=$(curl -s "https://queue.fal.run/fal-ai/gpt-image-1/requests/$REQUEST_ID" \
  -H "Authorization: Key $FAL_KEY")

IMAGE_URL=$(echo "$RESULT" | jq -r '.images[0].url')
curl -s -o scene-1.png "$IMAGE_URL"
```

### Ответ

```json
{
  "images": [
    {
      "url": "https://v3b.fal.media/files/...",
      "content_type": "image/png",
      "width": 1024,
      "height": 1536
    }
  ]
}
```

---

## 2. Kling v3 Standard — основная I2V модель

**Endpoint:** `https://queue.fal.run/fal-ai/kling-video/v3/standard/image-to-video`
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** $0.084/сек без аудио (5s = $0.42, 10s = $0.84) | $0.126/сек с аудио (5s = $0.63, 10s = $1.26)

> **Основная модель для I2V.** Всегда используй `generate_audio: false` — звук генерируется отдельно через TTS/anullsrc.

### Отправка запроса

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/kling-video/v3/standard/image-to-video" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Worf stands at the bridge console, turns slowly toward camera, jaw set with determination, low-angle push-in, dramatic lighting",
    "start_image_url": "https://supabase.../scene-1-start.png",
    "end_image_url": "https://supabase.../scene-1-end.png",
    "duration": "5",
    "generate_audio": false,
    "negative_prompt": "blur, distort, low quality, static, morphing faces"
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Описание анимации: камера, позиции, действия. Технический, не литературный |
| `start_image_url` | string | Да | URL начального кадра (постоянный Supabase URL) |
| `end_image_url` | string | Нет | URL конечного кадра (почти идентичен start, с минимальным сдвигом). ⚠️ ЗАПРЕЩЁН вместе с `multi_prompt` (Kling 422) |
| `multi_prompt` | list | Нет | Массив шотов для одного непрерывного клипа из одного `start_image_url`. См. §2d и `animator.md §5a`. Передавать ЛИБО `prompt`, ЛИБО `multi_prompt`, не оба |
| `duration` | enum | Нет | `"3"`–`"15"` секунд, по умолчанию "5" |
| `generate_audio` | boolean | Нет | **Всегда `false`** — anullsrc правило. I2V без аудио |
| `cfg_scale` | float | Нет | Сила следования промпту, 0.0–1.0, по умолчанию 0.5 |
| `negative_prompt` | string | Нет | Что исключить |
| `elements` | list | Нет | Кастомные персонажи/объекты, которые можно ввести в кадр и звать из промпта (`@Element1`, `@Element2`). Каждый элемент: `frontal_image_url` + `reference_image_urls` (**обязателен, ≥1 URL**) ЛИБО `video_url` (только 1 video-элемент на запрос). Все URL — постоянные Supabase. ✅ burn-tested 2026-06-01, работает с `multi_prompt` — см. §2c |

### Polling статуса

> ⚠️ **КРИТИЧНО:** Polling и результат — по **базовому 2-сегментному пути** `fal-ai/kling-video`, НЕ по полному пути submit endpoint.

```bash
while true; do
  STATUS_RESPONSE=$(curl -s "https://queue.fal.run/fal-ai/kling-video/requests/$REQUEST_ID/status" \
    -H "Authorization: Key $FAL_KEY")

  STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')

  case "$STATUS" in
    "COMPLETED") break ;;
    "FAILED") echo "FAILED"; exit 1 ;;
    *) sleep 15 ;;
  esac
done
```

### Получение результата

```bash
RESULT=$(curl -s "https://queue.fal.run/fal-ai/kling-video/requests/$REQUEST_ID" \
  -H "Authorization: Key $FAL_KEY")

VIDEO_URL=$(echo "$RESULT" | jq -r '.video.url')
curl -s -o scene-1.mp4 "$VIDEO_URL"
```

### Ответ

```json
{
  "video": {
    "url": "https://fal.media/files/abc123/output.mp4",
    "content_type": "video/mp4",
    "file_name": "output.mp4",
    "file_size": 1234567
  }
}
```

### 2c. `elements` — ввод персонажей/объектов в кадр

> ✅ **Burn-tested 2026-06-01 (v3 Standard, `elements` + `multi_prompt` вместе, $0.50).** Подтверждено: комбинация принимается и рендерит. Выводы теста — в конце секции.

`multi_prompt` тянет всё из одного `start_image_url` → новые сущности в кадре сами не появляются. Чтобы ввести персонажа/объект, которого нет на стартовом кадре, передай его как `element` и сошлись из промпта через `@Element1`.

Схема одного элемента (`KlingV3ComboElementInput`):

```json
"elements": [
  {
    "frontal_image_url": "https://supabase.../worf-front.png",
    "reference_image_urls": [
      "https://supabase.../worf-side.png",
      "https://supabase.../worf-3q.png"
    ]
  }
]
```

В `prompt` (или в промпте конкретного шота `multi_prompt`): `"@Element1 enters through the airlock door"`.

| Поле | Тип | Описание |
|------|-----|----------|
| `frontal_image_url` | string | Главный (фронтальный) вид элемента |
| `reference_image_urls` | array | **ОБЯЗАТЕЛЕН при `frontal_image_url`: ≥1 URL.** 1–3 доп. ракурса. Если чистый ракурс только один — допустимо передать тот же URL повторно (fal.ai принимает дубликат), но идентичность будет слабее |
| `video_url` | string | Видео-референс элемента. **Только 1 video-элемент на запрос** |
| `voice_id` | string | Привязка голоса (только для video-элементов) |

- **Максимум 3 элемента на запрос** (лимит Kling 3.0 для video; fal.ai-схема `maxItems` не enforce'ит, но Kling отвалит на отложенной валидации). На элемент: 1 фронталь + до 3 ракурсов (макс 4 картинки). Видео-элемент — только 1.
- `elements` задаётся **на уровне запроса**, не на уровне шота. Каждый шот `multi_prompt` может звать любой `@ElementN` в своём `prompt`.
- Референсы элемента (фронталь + ракурсы) генерит Storyboarder как character-sheet-набор и грузит в Supabase — см. `storyboarder.md §15.2`.
- Все URL — постоянные Supabase, НЕ fal.media.

**⚠️ Валидация `elements` отложенная (deferred):** ошибки схемы возвращаются НЕ на submit (там 200/IN_QUEUE), а при fetch результата — в поле `detail`, и джоба «завершается» за ~16с без `video.url`. Всегда проверяй `video.url` в результате; если его нет — смотри `detail`. (Это иначе, чем `prompt`+`multi_prompt` вместе → там немедленный 422.)

**Выводы burn-test 2026-06-01 (Spock/Kirk, 3 шота × 2с):**
- ✅ **Element для крупного плана лица в финальном шоте работает отлично** — чинит EP6-баг «третий шот дрейфует в реализм»: заякоренное элементом лицо держит Pixar-стиль и on-model.
- ⚠️ **Идентичность элемента в маленькой/перекрытой области кадра слабая** (лицо Кирка в иллюминаторе под красным светом прочиталось обобщённо). Для надёжной узнаваемости element должен занимать заметную площадь кадра; для мелких/затенённых появлений идентичность не гарантируется.
- `reference_image_urls` обязателен (≥1). Дубликат фронтали как ракурс принимается, но это stopgap — для identity-critical планов давай реальный второй ракурс.

### 2d. `multi_prompt` — несколько шотов в одном вызове

Один непрерывный MP4 из N последовательных шотов от одного `start_image_url`. Полные правила, лимиты (≤15s/вызов, ≤6 шотов) и chaining для >15s — в `animator.md §5a`. Здесь — только напоминание схемы:

```json
{
  "start_image_url": "https://supabase.../scene-2.png",
  "multi_prompt": [
    {"prompt": "шот 1 …", "duration": "3"},
    {"prompt": "шот 2 …", "duration": "3"}
  ],
  "shot_type": "customize",
  "duration": "6",
  "generate_audio": false
}
```

- Передавать **ЛИБО `prompt`, ЛИБО `multi_prompt`**, не оба (иначе 422).
- `end_image_url` ЗАПРЕЩЁН вместе с `multi_prompt` (422).
- Каждый шот: `prompt` (обяз.) + `duration` (enum `"1"`–`"15"`). Сумма длительностей шотов = верхнему `duration`.
- **Промпт каждого шота ≤ 512 символов (хард-лимит Kling).** Валидация отложенная: over-length шот проходит submit, но падает 422 в `detail` при fetch — теряешь round-trip. Режь до ≤512 ДО отправки (били на EP7 многократно).

---

## 2a. Kling Motion Control — motion transfer с реф-видео

Переносит движения из референсного видео на статичное изображение персонажа.

### Endpoints

| Вариант | Endpoint | Стоимость |
|---------|----------|-----------|
| **v2.6 Standard (основной)** | `fal-ai/kling-video/v2.6/standard/motion-control` | $0.07/сек |
| v3 Standard | `fal-ai/kling-video/v3/standard/motion-control` | $0.126/сек |
| v3 Pro | `fal-ai/kling-video/v3/pro/motion-control` | $0.168/сек |

### Запрос (v2.6 Standard)

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/kling-video/v2.6/standard/motion-control" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cute Roblox girl dancing energetically",
    "image_url": "https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/motion-test/character.png",
    "video_url": "https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/motion-test/dance-ref.mp4",
    "character_orientation": "video",
    "keep_original_sound": true
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|:---:|----------|
| `image_url` | string | Да | URL изображения персонажа (постоянный Supabase URL). Персонаж: чёткие пропорции, >5% площади, голова открыта |
| `video_url` | string | Да | URL референсного видео с движением (постоянный Supabase URL). Макс 10с (image mode) / 30с (video mode) |
| `character_orientation` | enum | Да | `"video"` = ориентация по видео (макс 30с, лучше для танцев). `"image"` = по картинке (макс 10с) |
| `prompt` | string | Нет | Описание |
| `keep_original_sound` | boolean | Нет | Сохранить звук из реф-видео (default: true) |
| `elements` | list | Нет | Привязка лица для консистентности (макс 1, только video mode) |

### Polling

```bash
# Base = fal-ai/kling-video (НЕ полный путь v2.6/standard/motion-control)
while true; do
  STATUS=$(curl -s "https://queue.fal.run/fal-ai/kling-video/requests/$REQUEST_ID/status" \
    -H "Authorization: Key $FAL_KEY" | jq -r '.status')
  case "$STATUS" in
    "COMPLETED") break ;;
    "FAILED") echo "FAILED"; exit 1 ;;
    *) sleep 15 ;;
  esac
done

RESULT=$(curl -s "https://queue.fal.run/fal-ai/kling-video/requests/$REQUEST_ID" \
  -H "Authorization: Key $FAL_KEY")
VIDEO_URL=$(echo "$RESULT" | jq -r '.video.url')
curl -s -o output.mp4 "$VIDEO_URL"
```

### Ответ

```json
{
  "video": {
    "url": "https://fal.media/files/abc123/output.mp4",
    "content_type": "video/mp4",
    "file_name": "output.mp4",
    "file_size": 19489104
  }
}
```

### Требования к входным файлам

- **Изображение:** персонаж с чёткими пропорциями тела, голова не закрыта, занимает >5% кадра
- **Видео:** реальные движения человека, макс 30с (video mode) / 10с (image mode)
- **Оба файла** — постоянные Supabase URL (НЕ fal.media)

---

## 2b. Kling 2.6 Pro — fallback I2V модель

**Endpoint:** `https://queue.fal.run/fal-ai/kling-video/v2.6/pro/image-to-video`
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** $0.07/сек без аудио (5s = $0.35, 10s = $0.70) | $0.14/сек с аудио (5s = $0.70, 10s = $1.40)

> **Используй ТОЛЬКО как fallback**, если Kling v3 Standard не работает или возвращает ошибки.

### Отправка запроса

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/kling-video/v2.6/pro/image-to-video" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "The hero swings his sword with dynamic motion, camera follows the action",
    "start_image_url": "https://fal.media/files/abc123/scene-1.png",
    "duration": "5",
    "generate_audio": false,
    "negative_prompt": "blur, distort, low quality, static"
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Описание анимации |
| `start_image_url` | string | Да | URL исходного изображения |
| `duration` | enum | Нет | `"5"` или `"10"` секунд, по умолчанию "5" |
| `generate_audio` | boolean | Нет | **Всегда `false`** — anullsrc правило |
| `negative_prompt` | string | Нет | Что исключить |
| `end_image_url` | string | Нет | Изображение для концовки |

### Polling статуса

```bash
# Base для polling = fal-ai/kling-video (первые 2 сегмента)
while true; do
  STATUS_RESPONSE=$(curl -s "https://queue.fal.run/fal-ai/kling-video/requests/$REQUEST_ID/status" \
    -H "Authorization: Key $FAL_KEY")

  STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')

  case "$STATUS" in
    "COMPLETED") break ;;
    "FAILED") echo "FAILED"; exit 1 ;;
    *) sleep 15 ;;
  esac
done
```

### Получение результата

```bash
RESULT=$(curl -s "https://queue.fal.run/fal-ai/kling-video/requests/$REQUEST_ID" \
  -H "Authorization: Key $FAL_KEY")

VIDEO_URL=$(echo "$RESULT" | jq -r '.video.url')
curl -s -o scene-1.mp4 "$VIDEO_URL"
```

### Ответ

```json
{
  "video": {
    "url": "https://fal.media/files/abc123/output.mp4",
    "content_type": "video/mp4",
    "file_name": "output.mp4",
    "file_size": 1234567
  }
}
```

---

## 4. MiniMax TTS — основной TTS для ВСЕХ форматов

**Endpoint:** `https://queue.fal.run/fal-ai/minimax/speech-2.8-hd`
**Метод:** POST (async, polling через `fal-ai/minimax`)
**Стоимость:** ~$0.10/1k chars (~$0.001–0.005 за фразу)

### Запрос

```bash
cat > /tmp/tts-body.json <<'EOF'
{
  "prompt": "Stand down, Worf. That is an order.",
  "voice_setting": {
    "voice_id": "Deep_Voice_Man",
    "speed": 0.9,
    "emotion": "angry"
  },
  "audio_setting": { "format": "mp3" }
}
EOF

RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/minimax/speech-2.8-hd" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/tts-body.json)

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

⚠️ **КРИТИЧНО:** поле называется `prompt`, НЕ `text`. Голос — `voice_setting.voice_id`, НЕ `voice`.

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Текст для озвучки. Поддерживает теги и паузы. |
| `voice_setting.voice_id` | string | Нет | ID голоса. Default: `Wise_Woman` |
| `voice_setting.speed` | float | Нет | 0.5–2.0. Темп речи. Default: 1.0 |
| `voice_setting.emotion` | string | Нет | `angry`, `happy`, `sad`, `fearful`, `disgusted`, `surprised`, `neutral` |
| `voice_setting.vol` | float | Нет | 0–10. Громкость. Default: 5 |
| `audio_setting.format` | string | Нет | `mp3`, `pcm`, `flac`. Default: mp3 |

### Теги в тексте

| Тег | Звук |
|-----|------|
| `(laughs)` | смех |
| `(groans)` | рёв/стон |
| `(sighs)` | вздох |
| `(coughs)` | кашель |
| `(gasps)` | резкий вдох |
| `(sniffs)` | шмыганье |
| `(yawns)` | зевок |
| `(clears throat)` | прочистка горла |
| `<#0.5#>` | пауза 0.5 сек |

### Голоса (все доступные)

| voice_id | Характер |
|----------|---------|
| `Deep_Voice_Man` | глубокий мужской |
| `Determined_Man` | решительный мужской |
| `Imposing_Manner` | властный мужской |
| `Young_Knight` | молодой мужской |
| `Casual_Guy` | разговорный мужской |
| `Patient_Man` | спокойный мужской |
| `Elegant_Man` | формальный мужской |
| `Decent_Boy` | нейтральный мужской |
| `Wise_Woman` | мудрая женская |
| `Calm_Woman` | спокойная женская |
| `Friendly_Person` | дружелюбная |
| `Inspirational_girl` | воодушевляющая женская |
| `Lively_Girl` | живая женская |
| `Lovely_Girl` | мягкая женская |
| `Sweet_Girl_2` | сладкая женская |
| `Exuberant_Girl` | экспрессивная женская |
| `Abbess` | строгая женская |

### Polling

```bash
# Base path для polling = fal-ai/minimax (первые 2 сегмента)
STATUS_URL="https://queue.fal.run/fal-ai/minimax/requests/${REQUEST_ID}/status"
RESULT_URL="https://queue.fal.run/fal-ai/minimax/requests/${REQUEST_ID}"
```

### Ответ

```json
{
  "audio": {
    "url": "https://fal.media/files/abc123/speech.mp3",
    "content_type": "audio/mpeg"
  }
}
```

Выходной формат: MP3 (готов для FFmpeg, конвертация не нужна).

---

## 4a. ElevenLabs TTS — через fal.ai (override MiniMax по запросу юзера)

**Endpoint:** `https://queue.fal.run/fal-ai/elevenlabs/tts/eleven-v3`
**Polling base:** `fal-ai/elevenlabs`
**Стоимость:** ~$0.03–0.05 за фразу

> Используется когда юзер явно просит ElevenLabs вместо MiniMax. ELEVENLABS_API_KEY в .env не нужен — fal.ai использует свой аккаунт.

### Запрос

```bash
cat > /tmp/el-body.json << 'EOF'
{
  "text": "Enterprise. You are under quarantine.",
  "voice": "Liam"
}
EOF

RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/elevenlabs/tts/eleven-v3" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/el-body.json)

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### ⚠️ КРИТИЧНО: правильные параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `text` | string | Да | Текст для озвучки |
| `voice` | string | Да | **Имя голоса** (не UUID, не `voice_id`!) |

**Правильно:** `{"text": "...", "voice": "Liam"}`
**Неправильно:** `{"text": "...", "voice_id": "Liam"}` — игнорируется, fallback на дефолтный голос
**Неправильно:** `{"text": "...", "voice_id": "TX3LPaxmHKxFdv7VOQHJ"}` — UUID не работает

### Голоса (соответствие персонажей)

| Персонаж | `voice` |
|----------|---------|
| Kirk, Mirror Kirk | `Daniel` |
| Chekov | `Charlie` |
| Fleet Admiral | `Liam` |
| Worf, Scotty | `George` |
| Spock | `Brian` |

### Polling и ответ

```bash
# Polling base = fal-ai/elevenlabs (2 сегмента)
STATUS_URL="https://queue.fal.run/fal-ai/elevenlabs/requests/${REQUEST_ID}/status"
RESULT_URL="https://queue.fal.run/fal-ai/elevenlabs/requests/${REQUEST_ID}"

# Ответ
{
  "audio": {
    "url": "https://v3b.fal.media/files/abc123/output.mp3",
    "content_type": "audio/mpeg"
  }
}
```

---

## Общий паттерн polling (для ВСЕХ fal.ai endpoints)

> ⚠️ **КРИТИЧНО:** Polling ВСЕГДА по **базовому 2-сегментному пути**, НЕ по полному submit endpoint.

| Submit endpoint | Polling base |
|-----------------|-------------|
| `fal-ai/nano-banana-2` | `fal-ai/nano-banana-2` |
| `fal-ai/nano-banana-2/edit` | `fal-ai/nano-banana-2` |
| `fal-ai/kling-video/v3/standard/image-to-video` | `fal-ai/kling-video` |
| `fal-ai/kling-video/v2.6/pro/image-to-video` | `fal-ai/kling-video` |
| `fal-ai/kling-video/ai-avatar/v2/standard` | `fal-ai/kling-video` |
| `fal-ai/kling-video/lipsync/audio-to-video` | `fal-ai/kling-video` |
| `fal-ai/kling-video/v2.6/standard/motion-control` | `fal-ai/kling-video` |
| `fal-ai/kling-video/v3/standard/motion-control` | `fal-ai/kling-video` |
| `fal-ai/kling-video/v3/pro/motion-control` | `fal-ai/kling-video` |
| `fal-ai/elevenlabs/tts/eleven-v3` | `fal-ai/elevenlabs` |
| `fal-ai/minimax-music/v2.6` | `fal-ai/minimax-music` |
| `fal-ai/gpt-image-1/text-to-image` | `fal-ai/gpt-image-1` |
| `fal-ai/heygen/avatar4/image-to-video` | `fal-ai/heygen` |

**Правило:** `base = "/".join(endpoint.split("/")[:2])`

```
1. POST запрос на полный endpoint → получить request_id
2. Каждые 15 секунд: GET https://queue.fal.run/{BASE}/requests/{request_id}/status
3. Проверить статус:
   - "IN_QUEUE" / "IN_PROGRESS" → продолжить polling
   - "COMPLETED" → GET https://queue.fal.run/{BASE}/requests/{request_id} → скачать результат
   - "FAILED" → обработать ошибку (см. rules/fallback.md)
4. Таймаут: 10 минут максимум
5. При таймауте: fallback
```

**Если использовать полный путь вместо base — fal.ai вернёт пустой body, 404 или 405. Деньги за генерацию будут потрачены, результат не скачается.**

---

## 5. Kling Lipsync — Audio-to-Video (липсинк)

**Endpoint:** `https://queue.fal.run/fal-ai/kling-video/lipsync/audio-to-video`
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** ~$0.10/сек

> Принимает видео + аудио, генерирует липсинк (движение губ синхронно с речью).

### Запрос

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/kling-video/lipsync/audio-to-video" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://fal.media/files/abc123/scene-1.mp4",
    "audio_url": "https://fal.media/files/abc123/voiceover.wav"
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `video_url` | string | Да | URL исходного видео (из Kling I2V) |
| `audio_url` | string | Да | URL аудиофайла с речью (из ElevenLabs TTS через fal.ai) |

### Polling и получение результата

```
# Base = fal-ai/kling-video (НЕ полный путь lipsync/audio-to-video)
Status: https://queue.fal.run/fal-ai/kling-video/requests/{REQUEST_ID}/status
Result: https://queue.fal.run/fal-ai/kling-video/requests/{REQUEST_ID}
```

### Ответ

```json
{
  "video": {
    "url": "https://fal.media/files/abc123/output.mp4",
    "content_type": "video/mp4"
  }
}
```

### Пайплайн с липсинком

```
Image → Kling I2V (анимация) → ElevenLabs TTS (голос, через fal.ai) → Kling Lipsync (видео + аудио → липсинк) → FFmpeg (склейка)
```

**ВАЖНО:** `audio_url` должен быть публичным URL. ElevenLabs TTS через fal.ai возвращает URL с fal.media — скачай локально и залей в Supabase для стабильного URL.

---

## 6. HeyGen Avatar IV — Text-to-Avatar Video (голос + видео в одном)

**Endpoint:** `https://queue.fal.run/fal-ai/heygen/avatar4/image-to-video`
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** $0.10/сек

> Принимает изображение + текст скрипта → генерирует talking head видео с голосом, lipsync, мимикой и жестами рук. Голос генерируется внутри модели — отдельный TTS не нужен.

### Запрос

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/heygen/avatar4/image-to-video" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://fal.media/files/abc123/avatar-ref.png",
    "script": "Yo, why is nobody talking about this? They are literally giving away 500 free diamonds right now! All you gotta do is download the game through the link in my bio and reach level 10.",
    "voice_id": "...",
    "custom_motion_prompt": "energetic gaming blogger speaking to camera, natural hand gestures, nodding"
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `image_url` | string | Да | URL изображения аватара (portrait, upper body, смотрит в камеру) |
| `script` | string | Да | Текст, который аватар произнесёт. Модель сама генерирует голос и lipsync |
| `voice_id` | string | Нет | Имя голоса из списка HeyGen (300+ голосов, 175+ языков). EN рекомендации: `Chill Brian`, `Bold Blake`, `Ivy`, `Cute Chloe - Friendly` |
| `custom_motion_prompt` | string | Нет | Описание жестов и движений ("energetic blogger, hand gestures"). **Именно `custom_motion_prompt`**, НЕ `motion_prompt` |

### Polling и получение результата

```bash
# Проверяй каждые 15 секунд
while true; do
  STATUS=$(curl -s "https://queue.fal.run/fal-ai/heygen/avatar4/image-to-video/requests/$REQUEST_ID/status" \
    -H "Authorization: Key $FAL_KEY" | jq -r '.status')
  case "$STATUS" in
    "COMPLETED") break ;;
    "FAILED") echo "FAILED"; exit 1 ;;
    *) sleep 15 ;;
  esac
done

RESULT=$(curl -s "https://queue.fal.run/fal-ai/heygen/avatar4/image-to-video/requests/$REQUEST_ID" \
  -H "Authorization: Key $FAL_KEY")
VIDEO_URL=$(echo "$RESULT" | jq -r '.video.url')
curl -s -o avatar.mp4 "$VIDEO_URL"
```

### Ответ

```json
{
  "video": {
    "url": "https://fal.media/files/abc123/output.mp4",
    "content_type": "video/mp4"
  }
}
```

### Доступные голоса (примеры)

300+ голосов на 175+ языках. Популярные для gaming-контента:

**EN мужские:** `Chill Brian`, `Andrew Rizz`, `Bold Blake`, `Jack Sterling - Broadcaster`, `Expressive Evan`, `Mellow Marcus`
**EN женские:** `Ivy`, `Cute Chloe - Friendly`, `Feisty Fiona - Excited`, `Ellie Faye - Excited`, `Willow`
**Универсальные:** `Warm Pro Narrator`, `Professor Dean`, `Radio Rick`

> Полный список голосов: проверь через fal.ai playground на странице модели.

> **Используется для формата Gameplay AI Avatar.** Один вызов = голос + lipsync + мимика + жесты. Отдельный TTS не нужен.

---

## 7. Kling Avatar v2 — Image + Audio to Avatar Video (fallback)

**Endpoint (Standard):** `https://queue.fal.run/fal-ai/kling-video/ai-avatar/v2/standard`
**Endpoint (Pro):** `https://queue.fal.run/fal-ai/kling-video/ai-avatar/v2/pro`
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** $0.056/сек (Standard), $0.115/сек (Pro)

> Принимает изображение + аудио → генерирует talking head с lipsync. В отличие от HeyGen, требует отдельный TTS для генерации аудио.

### Запрос

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/kling-video/ai-avatar/v2/standard" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://fal.media/files/abc123/avatar-ref.png",
    "audio_url": "https://fal.media/files/abc123/speech.wav"
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `image_url` | string | Да | URL изображения аватара |
| `audio_url` | string | Да | URL аудиофайла (WAV/MP3) — из ElevenLabs TTS через fal.ai |

### Polling

Аналогично другим Kling endpoints — base `fal-ai/kling-video`:
```
# Base = fal-ai/kling-video (НЕ полный путь ai-avatar/v2/standard)
Status: https://queue.fal.run/fal-ai/kling-video/requests/{REQUEST_ID}/status
Result: https://queue.fal.run/fal-ai/kling-video/requests/{REQUEST_ID}
```

### Пайплайн с Kling Avatar v2 (fallback для Gameplay AI Avatar)

```
Nano Banana 2 (avatar ref) → ElevenLabs TTS (speech.wav, через fal.ai) → Kling Avatar v2 (image + audio → avatar.mp4) → FFmpeg split-screen
```

> **Используй как fallback**, если HeyGen Avatar IV не работает. Дешевле ($0.056/сек vs $0.10/сек), но требует отдельный TTS.

---

## 8. MiniMax Music v2.6 — AI-generated background music

**Endpoint:** `https://queue.fal.run/fal-ai/minimax-music/v2.6`
**Polling base:** `fal-ai/minimax-music`
**Стоимость:** $0.03 за трек

> Генерирует инструментальную музыку по текстовому описанию. Используется для форматов, где треки из библиотеки запрещены (авторские права → страйки). `is_instrumental: true` — обязательно для фоновой музыки без вокала.

### Запрос

```bash
cat > /tmp/music-body.json << 'EOF'
{
  "style": "energetic upbeat anime action music, driving beat 140bpm, orchestral synth blend, heroic bold melody, suitable for vertical short video, cinematic hype",
  "is_instrumental": true,
  "duration": 30
}
EOF

RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/minimax-music/v2.6" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/music-body.json)

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `style` | string | Да | Описание стиля (до 2000 символов) |
| `is_instrumental` | boolean | Нет | `true` = без вокала. **Всегда `true` для фоновой музыки** |
| `duration` | integer | Нет | Длительность в секундах (рекомендуется 30–60) |

### Polling

```bash
while true; do
  STATUS=$(curl -s "https://queue.fal.run/fal-ai/minimax-music/requests/$REQUEST_ID/status" \
    -H "Authorization: Key $FAL_KEY" | jq -r '.status')
  case "$STATUS" in
    "COMPLETED") break ;;
    "FAILED") echo "FAILED"; exit 1 ;;
    *) sleep 15 ;;
  esac
done

RESULT=$(curl -s "https://queue.fal.run/fal-ai/minimax-music/requests/$REQUEST_ID" \
  -H "Authorization: Key $FAL_KEY")
AUDIO_URL=$(echo "$RESULT" | jq -r '.audio.url // .audio_file.url')
curl -s -o bg-music.mp3 "$AUDIO_URL"
```

### Ответ

```json
{
  "audio": {
    "url": "https://fal.media/files/abc123/music.mp3",
    "content_type": "audio/mpeg"
  }
}
```

---

## Важные правила

1. **fal.ai URL-ы ВРЕМЕННЫЕ.** Скачивай файлы сразу после генерации. Не рассчитывай на повторный доступ.
2. **Перед дорогой генерацией (Kling I2V, Avatar) — загрузи ВСЕ входные файлы в Supabase Storage.** Используй ТОЛЬКО постоянные Supabase URL как `start_image_url`, `end_image_url`, `audio_url`. Временные fal.ai URL протухают → генерация стоимостью $0.42–$1.40 пропадает.
3. **Polling — по 2-сегментному base пути.** НЕ по полному submit endpoint. См. таблицу в "Общий паттерн polling".
4. **Проверяй размер** скачанного файла (>1000 байт для изображений, >10000 для видео).
5. **`generate_audio: false`** для всех I2V (anullsrc правило) — звук добавляется на этапе сборки.
6. **Не отправляй больше 3 параллельных запросов** — rate limiting.
7. **Сохраняй request_id** — нужен для polling и отмены задач.

### Пайплайн загрузки в Supabase перед дорогой генерацией

```bash
# 1. Генерируй изображение через NB2 → скачай локально
# 2. Загрузи в Supabase Storage
#    Путь ОБЯЗАН содержать дату и формат для scene PNG, иначе следующий эпизод
#    того же game_tag затрёт предыдущий. См. storyboarder.md §15.1.
#    scene PNG:  ${GAME_TAG}/scenes/${YYYY-MM-DD}/${FORMAT_SLUG}/scene-K.png
#    bg/char ref: ${GAME_TAG}/refs/${name}.png  (без даты — шарится между эпизодами)
STORAGE_PATH="${GAME_TAG}/scenes/${DATE}/${FORMAT_SLUG}/${FILENAME}"
curl -s -X POST "https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/assets/${STORAGE_PATH}" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: image/png" \
  --data-binary @"$LOCAL_FILE"

# 3. Получи постоянный URL
PERMANENT_URL="https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/${STORAGE_PATH}"

# 4. Используй PERMANENT_URL как start_image_url в Kling I2V
```

**Никогда не передавай `fal.media` URL в `start_image_url` / `end_image_url` / `audio_url`.**
