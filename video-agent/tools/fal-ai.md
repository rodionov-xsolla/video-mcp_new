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

## 1. GPT Image 2 — основная модель генерации изображений

**Endpoint:** `https://queue.fal.run/fal-ai/gpt-image-2` *(уточни через Context7 перед использованием)*
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** ~$0.04 за изображение (medium quality)

> **Основная модель для всех сцен, character refs, bg-assets.** Заменяет Nano Banana 2.

### Запрос

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/gpt-image-2" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Star Trek cinematic 3D animation, Captain Kirk medium close-up, gold tunic, dramatic lighting, 9:16 vertical",
    "image_url": "https://supabase.../character-ref.png",
    "quality": "medium",
    "image_size": "1024x1536"
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Текстовое описание |
| `quality` | enum | Нет | `"low"`, `"medium"`, `"high"`. Используй `"medium"` |
| `image_size` | enum | Нет | `"1024x1536"` для 9:16 вертикального |
| `image_url` | string | Нет | URL reference image для chain consistency (уточни через Context7) |

> ⚠️ Перед первым вызовом сверься с Context7: `resolve-library-id gpt-image-2` → `get-library-docs`. Параметры (особенно `image_url` vs `image_urls`, polling path) могут отличаться.

### Polling

```bash
# Polling base path — уточнить через Context7
STATUS=$(curl -s "https://queue.fal.run/fal-ai/gpt-image-2/requests/$REQUEST_ID/status" \
  -H "Authorization: Key $FAL_KEY" | jq -r '.status')
```

---

## 1b. Nano Banana 2 — LEGACY (не использовать для новых проектов)

### Text-to-Image (без референса — для character references)

**Endpoint:** `https://queue.fal.run/fal-ai/nano-banana-2`
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** ~$0.04 за изображение

> **Используй этот endpoint для генерации character references** (нет входного изображения). Поле `image_urls` НЕ передаётся.

### Image-to-Image / Edit (с референсом — для сцен)

**Endpoint:** `https://queue.fal.run/fal-ai/nano-banana-2/edit`
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** ~$0.04 за изображение

> **Используй этот endpoint для генерации сцен** с chain reference (image_urls обязателен).

### Запрос

```bash
curl -s -X POST "https://queue.fal.run/fal-ai/nano-banana-2/edit" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "MLBB hero Lancelot in dynamic sword pose, vertical composition, 9:16 aspect ratio, anime style, dramatic lighting",
    "image_urls": ["https://fal.media/files/abc123/character-ref.png"],
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

## 1b. GPT Image 1 — fallback генерация изображений

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
    "prompt": "MLBB hero Lancelot in dynamic sword pose, vertical composition, detailed character design, dramatic lighting",
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
# Проверяй каждые 10 секунд
STATUS=$(curl -s "https://queue.fal.run/fal-ai/gpt-image-1/requests/$REQUEST_ID/status" \
  -H "Authorization: Key $FAL_KEY" | jq -r '.status')

# Результат:
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

## 2. Kling 2.6 Pro — Image-to-Video

**Endpoint:** `https://queue.fal.run/fal-ai/kling-video/v2.6/pro/image-to-video`
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** $0.07/сек (без аудио), $0.14/сек (с аудио)

### Отправка запроса

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/kling-video/v2.6/pro/image-to-video" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "The hero swings his sword with dynamic motion, camera follows the action",
    "start_image_url": "https://fal.media/files/abc123/scene-1.png",
    "duration": "5",
    "generate_audio": true,
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
| `generate_audio` | boolean | Нет | **Ставь `true`** (по умолчанию). Kling генерирует звуковые эффекты (шаги, звон, амбиент). $0.14/сек с аудио, $0.07/сек без |
| `negative_prompt` | string | Нет | Что исключить. По умолчанию "blur, distort, and low quality" |
| `end_image_url` | string | Нет | Изображение для концовки |

> **По умолчанию:** `"generate_audio": true` — Kling генерирует звуковые эффекты (шаги, удары, амбиент). Стоимость $0.14/сек. Если нужно сэкономить — `false` ($0.07/сек).

### Polling статуса

> ⚠️ **КРИТИЧНО:** Polling и результат — по **базовому 2-сегментному пути** `fal-ai/kling-video`, НЕ по полному пути submit endpoint.

```bash
# Base для polling = первые 2 сегмента endpoint
# Submit: fal-ai/kling-video/v2.6/pro/image-to-video
# Polling: fal-ai/kling-video

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
# Тот же базовый путь fal-ai/kling-video
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

## 3. Veo 3 — Text-to-Video

**Endpoint:** `https://queue.fal.run/fal-ai/veo3`
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** $0.20/сек (без аудио), $0.40/сек (с аудио)

> **ОГРАНИЧЕНИЕ:** Максимум 2 клипа × 8 секунд = $3.20 без аудио. Потолок $10.

### Отправка запроса

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/veo3" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Cinematic trailer of a fantasy MOBA battle, epic hero poses, dramatic lighting, vertical 9:16 composition, high quality",
    "aspect_ratio": "9:16",
    "duration": "8s",
    "resolution": "720p",
    "generate_audio": false,
    "safety_tolerance": "4"
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Описание видео (макс 20000 символов) |
| `aspect_ratio` | enum | Нет | `"9:16"` или `"16:9"`, по умолчанию "16:9" |
| `duration` | enum | Нет | `"4s"`, `"6s"` или `"8s"`, по умолчанию "8s" |
| `resolution` | enum | Нет | `"720p"` или `"1080p"`, по умолчанию "720p" |
| `generate_audio` | boolean | Нет | По умолчанию true. `true` = голос + звук ($0.40/сек), `false` = только видео ($0.20/сек). Решение определяется файлом формата |
| `negative_prompt` | string | Нет | Что исключить |
| `seed` | integer | Нет | Для воспроизводимости |

> **generate_audio:** `true` — когда в промпте есть речь (Veo3 генерит голос + липсинк из текста). `false` — чисто визуальный T2V без диалога (экономия 50%). Решение определяется файлом формата.

### Polling и получение результата

Аналогично Kling — базовый 2-сегментный путь `fal-ai/veo3`:
```
Status: https://queue.fal.run/fal-ai/veo3/requests/{REQUEST_ID}/status
Result: https://queue.fal.run/fal-ai/veo3/requests/{REQUEST_ID}
```

### Ответ

```json
{
  "video": {
    "url": "https://fal.media/files/abc123/output.mp4",
    "content_type": "video/mp4",
    "file_name": "output.mp4",
    "file_size": 9876543
  }
}
```

---

## 4. ElevenLabs TTS (через fal.ai) — основной TTS для ВСЕХ форматов

**Endpoint:** `https://queue.fal.run/fal-ai/elevenlabs/tts/eleven-v3`
**Метод:** POST (async, polling через `fal-ai/elevenlabs`)
**Стоимость:** ~$0.30/мин (~$0.05–0.10 за фразу 2–6 сек)

⚠️ **Это fal.ai wrapper, НЕ прямой ElevenLabs API.** Параметры отличаются от `elevenlabs.md`!

### Запрос

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/elevenlabs/tts/eleven-v3" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Stand down, Worf. That is an order.",
    "voice": "Daniel",
    "language_code": "en",
    "stability": 0.10,
    "style": 0.8
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `text` | string | Да | Текст для озвучки |
| `voice` | string | Да | **Имя голоса** (строка): `Daniel`, `George`, `Charlie`, `Charlotte`, `Rachel`. **НЕ voice_id хеш!** |
| `language_code` | string | Нет | Код языка: `en`, `ru`, `es`, `de`, `fr` и др. (29 языков) |
| `stability` | float | Нет | 0.0–1.0. Низкое = экспрессивнее (0.10 для Captain Kirk), высокое = стабильнее |
| `style` | float | Нет | 0.0–1.0. Стиль подачи (0.8 для выразительной речи) |

### Голоса для Serial Drama

| Тип персонажа | Голос | stability | style |
|---------------|-------|-----------|-------|
| Мужской (уверенный, авторитетный) | `Daniel` | 0.10 | 0.8 |
| Мужской (нейтральный, рассказчик) | `George` | 0.30 | — |
| Мужской (молодой, энергичный) | `Charlie` | 0.20 | — |
| Женский (уверенный) | `Charlotte` | 0.25 | — |
| Женский (нейтральный) | `Rachel` | 0.35 | — |

### Polling

```bash
# Base path для polling = fal-ai/elevenlabs (первые 2 сегмента, НЕ полный endpoint)
STATUS_URL="https://queue.fal.run/fal-ai/elevenlabs/requests/${REQUEST_ID}/status"
RESULT_URL="https://queue.fal.run/fal-ai/elevenlabs/requests/${REQUEST_ID}"
```

### Ответ

```json
{
  "audio": {
    "url": "https://fal.media/files/abc123/audio.mp3",
    "content_type": "audio/mpeg"
  }
}
```

Выходной формат: MP3 (готов для FFmpeg, конвертация не нужна).

⚠️ **КРИТИЧНО:** Параметр `voice` = **имя** (`"Daniel"`), НЕ `voice_id` хеш (`"pNInz6obpgDQGcFmaJgB"`). Если передать хеш — fal.ai wrapper откатится на дефолтный голос (женский), и все персонажи будут говорить одним голосом.

---

## Общий паттерн polling (для ВСЕХ fal.ai endpoints)

> ⚠️ **КРИТИЧНО:** Polling ВСЕГДА по **базовому 2-сегментному пути**, НЕ по полному submit endpoint.

| Submit endpoint | Polling base |
|-----------------|-------------|
| `fal-ai/nano-banana-2/edit` | `fal-ai/nano-banana-2` |
| `fal-ai/kling-video/v2.6/pro/image-to-video` | `fal-ai/kling-video` |
| `fal-ai/kling-video/ai-avatar/v2/standard` | `fal-ai/kling-video` |
| `fal-ai/kling-video/lipsync/audio-to-video` | `fal-ai/kling-video` |
| `fal-ai/elevenlabs/tts/eleven-v3` | `fal-ai/elevenlabs` |
| `fal-ai/veo3` | `fal-ai/veo3` |
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
Image → Kling I2V (анимация + SFX) → ElevenLabs TTS (голос, через fal.ai) → Kling Lipsync (видео + аудио → липсинк) → FFmpeg (склейка)
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

## Важные правила

1. **fal.ai URL-ы ВРЕМЕННЫЕ.** Скачивай файлы сразу после генерации. Не рассчитывай на повторный доступ.
2. **Перед дорогой генерацией (Kling I2V, Avatar, Veo3) — загрузи ВСЕ входные файлы в Supabase Storage.** Используй ТОЛЬКО постоянные Supabase URL как `start_image_url`, `end_image_url`, `audio_url`. Временные fal.ai URL протухают → генерация стоимостью $0.35–$3.20 пропадает.
3. **Polling — по 2-сегментному base пути.** НЕ по полному submit endpoint. См. таблицу в "Общий паттерн polling".
4. **Проверяй размер** скачанного файла (>1000 байт для изображений, >10000 для видео).
5. **`generate_audio: true`** для Kling (SFX по умолчанию), решение по `false` определяется файлом формата.
6. **Не отправляй больше 3 параллельных запросов** — rate limiting.
7. **Сохраняй request_id** — нужен для polling и отмены задач.

### Пайплайн загрузки в Supabase перед дорогой генерацией

```bash
# 1. Генерируй изображение через NB2 → скачай локально
# 2. Загрузи в Supabase Storage
curl -s -X POST "https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/assets/${GAME_TAG}/scenes/${FILENAME}" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: image/png" \
  --data-binary @"$LOCAL_FILE"

# 3. Получи постоянный URL
PERMANENT_URL="https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/${GAME_TAG}/scenes/${FILENAME}"

# 4. Используй PERMANENT_URL как start_image_url в Kling I2V
```

**Никогда не передавай `fal.media` URL в `start_image_url` / `end_image_url` / `audio_url`.**
