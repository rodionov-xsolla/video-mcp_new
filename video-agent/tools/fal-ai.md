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

## 1. FLUX.2 Pro — генерация изображений

**Endpoint:** `https://queue.fal.run/fal-ai/flux-pro/v1.1-ultra`
**Метод:** POST (синхронный — ответ приходит сразу)
**Стоимость:** ~$0.045 за изображение 9:16

### Запрос

```bash
curl -s -X POST "https://queue.fal.run/fal-ai/flux-pro/v1.1-ultra" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "MLBB hero Lancelot in dynamic sword pose, vertical composition, 9:16 aspect ratio, anime style, dramatic lighting",
    "aspect_ratio": "9:16",
    "num_images": 1,
    "output_format": "png",
    "safety_tolerance": "5"
  }'
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Текстовое описание изображения |
| `aspect_ratio` | enum | Нет | `"9:16"` для вертикального видео. Варианты: "1:1", "16:9", "9:16", "4:3", "3:4" |
| `num_images` | integer | Нет | 1-4, по умолчанию 1 |
| `output_format` | enum | Нет | "jpeg" или "png", по умолчанию "jpeg" |
| `safety_tolerance` | string | Нет | "1"-"6", по умолчанию "2". Для игрового контента ставь "5" |
| `seed` | integer | Нет | Для воспроизводимости результатов |
| `enhance_prompt` | boolean | Нет | Улучшает интерпретацию промпта |

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
  ],
  "seed": 12345,
  "prompt": "...",
  "has_nsfw_concepts": [false]
}
```

### Скачивание (ОБЯЗАТЕЛЬНО)

```bash
IMAGE_URL=$(echo "$RESPONSE" | jq -r '.images[0].url')
curl -s -o scene-1.png "$IMAGE_URL"

# Проверь что файл скачался
ls -la scene-1.png
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
| `generate_audio` | boolean | Нет | **Ставь `false`!** По умолчанию true. Аудио заменяется через FFmpeg |
| `negative_prompt` | string | Нет | Что исключить. По умолчанию "blur, distort, and low quality" |
| `end_image_url` | string | Нет | Изображение для концовки |

> **ВАЖНО:** Используй `"generate_audio": false` чтобы платить $0.07/сек вместо $0.14/сек.

### Polling статуса

```bash
# Проверяй каждые 15 секунд
while true; do
  STATUS_RESPONSE=$(curl -s "https://queue.fal.run/fal-ai/kling-video/v2.6/pro/image-to-video/requests/$REQUEST_ID/status" \
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
RESULT=$(curl -s "https://queue.fal.run/fal-ai/kling-video/v2.6/pro/image-to-video/requests/$REQUEST_ID" \
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
| `generate_audio` | boolean | Нет | **Ставь `false`!** По умолчанию true |
| `negative_prompt` | string | Нет | Что исключить |
| `seed` | integer | Нет | Для воспроизводимости |

> **ВАЖНО:** `generate_audio: false` снижает цену вдвое: $0.20/сек вместо $0.40/сек.

### Polling и получение результата

Аналогично Kling (см. выше), но endpoint:
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

## 4. Kokoro TTS — озвучка

**Endpoint:** `https://queue.fal.run/fal-ai/kokoro/american-english`
**Метод:** POST (синхронный)
**Стоимость:** $0.02 за 1000 символов

### Запрос

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/kokoro/american-english" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Top 5 heroes that will carry you to Mythic rank! Number five: Lancelot, the ultimate assassin!",
    "voice": "af_heart",
    "speed": 1.1
  }')

AUDIO_URL=$(echo "$RESPONSE" | jq -r '.audio.url')
curl -s -o voiceover.wav "$AUDIO_URL"
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Текст для озвучки |
| `voice` | enum | Нет | Голос. По умолчанию "af_heart" |
| `speed` | float | Нет | 0.1–5.0, по умолчанию 1.0. Для энергичного контента: 1.1–1.2 |

### Доступные голоса

**Женские:** af_heart, af_alloy, af_bella, af_jessica, af_nova, af_river, af_sarah, af_sky
**Мужские:** am_adam, am_echo, am_eric, am_liam, am_michael, am_onyx, am_puck

### Ответ

```json
{
  "audio": {
    "url": "https://fal.media/files/abc123/audio.wav"
  }
}
```

> Выходной формат: WAV. Если нужен MP3 для FFmpeg, конвертируй: `ffmpeg -i voiceover.wav -codec:a libmp3lame voiceover.mp3`

---

## Общий паттерн polling (для Kling и Veo)

```
1. POST запрос → получить request_id
2. Каждые 15 секунд: GET /requests/{request_id}/status
3. Проверить статус:
   - "IN_QUEUE" или "IN_PROGRESS" → продолжить polling
   - "COMPLETED" → GET /requests/{request_id} → скачать результат
   - "FAILED" → обработать ошибку (см. rules/fallback.md)
4. Таймаут: 10 минут максимум
5. При таймауте: fallback на Approach 1
```

---

## Важные правила

1. **Всегда скачивай файлы** после генерации. fal.ai URL-ы временные.
2. **Проверяй размер** скачанного файла (>1000 байт для изображений, >10000 для видео).
3. **`generate_audio: false`** для Kling и Veo — экономит 50% стоимости.
4. **Не отправляй больше 3 параллельных запросов** — rate limiting.
5. **Сохраняй request_id** — нужен для polling и отмены задач.
