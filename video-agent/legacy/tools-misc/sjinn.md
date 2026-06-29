# SJinn API Reference

Справочник по API sjinn.ai — агрегатор моделей для генерации изображений и видео.

---

## Аутентификация

```
Authorization: Bearer $SJINN_API_KEY
```

**Base URL:** `https://sjinn.ai/api/un-api`

---

## Общий паттерн работы

Все модели работают одинаково:

1. **Создать задачу:** `POST /create_tool_task` → получить `task_id`
2. **Проверять статус:** `POST /query_tool_task_status` каждые 10-15 сек
3. **Получить результат:** из поля `output_urls` когда статус = 1

### Создание задачи

```bash
RESPONSE=$(curl -s -X POST "https://sjinn.ai/api/un-api/create_tool_task" \
  -H "Authorization: Bearer $SJINN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_type": "MODEL_ID",
    "input": {
      "prompt": "...",
      ...параметры модели...
    }
  }')

TASK_ID=$(echo "$RESPONSE" | jq -r '.data.task_id')
```

### Проверка статуса

```bash
STATUS_RESPONSE=$(curl -s -X POST "https://sjinn.ai/api/un-api/query_tool_task_status" \
  -H "Authorization: Bearer $SJINN_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"task_id\": \"$TASK_ID\"}")

STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.data.status')
# 0 = processing, 1 = completed, -1 = failed
```

### Получение результата

При `status = 1` результат в `output_urls`:
```bash
OUTPUT_URL=$(echo "$STATUS_RESPONSE" | jq -r '.data.output_urls[0]')
curl -s -o result.mp4 "$OUTPUT_URL"
```

---

## 1. Nano Banana — генерация изображений

**tool_type:** `nano-banana-image-api`
**Стоимость:** 50 кредитов
**Время:** 10-30 секунд

### Запрос

```bash
curl -s -X POST "https://sjinn.ai/api/un-api/create_tool_task" \
  -H "Authorization: Bearer $SJINN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_type": "nano-banana-image-api",
    "input": {
      "prompt": "MLBB hero Lancelot in dynamic sword pose, vertical composition, anime style, dramatic lighting",
      "aspect_ratio": "9:16"
    }
  }'
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Описание изображения |
| `aspect_ratio` | string | Нет | `"9:16"` для вертикального. Варианты: auto, 1:1, 16:9, 9:16, 4:3, 3:4, 2:3, 3:2 |
| `image_list` | string[] | Нет | URL-ы референсных изображений (макс 3) |

### Pro-версия

**tool_type:** `nano-banana-image-pro-api`
**Стоимость:** 150 кредитов (выше качество)

### Chain Reference — консистентность между сценами

Используй `image_list` для передачи референсных изображений. Это помогает сохранить стиль и персонажа.

**Паттерн:**

```bash
# Сцена 1 — только character reference
curl -s -X POST "https://sjinn.ai/api/un-api/create_tool_task" \
  -H "Authorization: Bearer $SJINN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_type": "nano-banana-image-api",
    "input": {
      "prompt": "ПОЛНЫЙ промпт сцены 1...",
      "aspect_ratio": "9:16",
      "image_list": ["https://edit.comfyonline.app/result/CHARACTER-REF-URL.png"]
    }
  }'

# Сцена 2 — character reference + предыдущая сцена
curl -s -X POST "https://sjinn.ai/api/un-api/create_tool_task" \
  -H "Authorization: Bearer $SJINN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_type": "nano-banana-image-api",
    "input": {
      "prompt": "ПОЛНЫЙ промпт сцены 2...",
      "aspect_ratio": "9:16",
      "image_list": [
        "https://edit.comfyonline.app/result/CHARACTER-REF-URL.png",
        "https://edit.comfyonline.app/result/SCENE-1-URL.png"
      ]
    }
  }'
```

**Правила:**
- `image_list[0]` — всегда character reference (якорь)
- `image_list[1]` — предыдущая сцена (для стилевой преемственности)
- Максимум 2 референса на сцену (не все предыдущие)
- `image_list` — слабая подсказка, основная консистентность через промпт

---

## 2. Veo3 — Text-to-Video

**tool_type:** `veo3-text-to-video-fast-api`
**Стоимость:** 420 кредитов
**Время:** 2-5 минут

### Запрос

```bash
curl -s -X POST "https://sjinn.ai/api/un-api/create_tool_task" \
  -H "Authorization: Bearer $SJINN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_type": "veo3-text-to-video-fast-api",
    "input": {
      "prompt": "Cinematic trailer of a fantasy MOBA battle, epic hero poses, vertical 9:16",
      "aspect_ratio": "9:16"
    }
  }'
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Описание видео |
| `aspect_ratio` | string | Нет | `"9:16"` или `"16:9"` (default) |

---

## 3. Veo3 — Image-to-Video

**tool_type:** `veo3-image-to-video-fast-api`
**Стоимость:** 420 кредитов
**Время:** 2-5 минут

### Запрос

```bash
curl -s -X POST "https://sjinn.ai/api/un-api/create_tool_task" \
  -H "Authorization: Bearer $SJINN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_type": "veo3-image-to-video-fast-api",
    "input": {
      "prompt": "The hero swings his sword with dynamic motion",
      "image": "https://cdn.example.com/scene-1.png",
      "aspect_ratio": "9:16"
    }
  }'
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Описание анимации |
| `image` | string | Да | URL исходного изображения (HTTP/HTTPS) |
| `aspect_ratio` | string | Нет | `"9:16"` или `"16:9"` |
| `end_image_url` | string | Нет | URL финального кадра (для контроля концовки) |

---

## 4. Grok — Text-to-Video

**tool_type:** `grok-text-to-video-api`
**Стоимость:** duration × 50 кредитов (5 сек = 250 кредитов)
**Время:** 2-8 минут

### Запрос

```bash
curl -s -X POST "https://sjinn.ai/api/un-api/create_tool_task" \
  -H "Authorization: Bearer $SJINN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_type": "grok-text-to-video-api",
    "input": {
      "prompt": "Epic battle scene in a fantasy MOBA game",
      "duration": 5,
      "aspect_ratio": "9:16"
    }
  }'
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Описание видео |
| `duration` | number | Нет | 3-15 секунд, default 5 |
| `aspect_ratio` | string | Нет | `"9:16"`, `"16:9"`, `"1:1"` |

---

## 5. Grok — Image-to-Video

**tool_type:** `grok-image-to-video-api`
**Стоимость:** duration × 50 кредитов
**Время:** 2-8 минут

### Запрос

```bash
curl -s -X POST "https://sjinn.ai/api/un-api/create_tool_task" \
  -H "Authorization: Bearer $SJINN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_type": "grok-image-to-video-api",
    "input": {
      "prompt": "The hero leaps forward with a powerful attack",
      "image": "https://cdn.example.com/scene-1.png",
      "duration": 5,
      "aspect_ratio": "9:16"
    }
  }'
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Описание движения (фокус на действии, не на изображении) |
| `image` | string | Да | URL исходного изображения |
| `duration` | number | Нет | 3-15 секунд, default 5 |
| `aspect_ratio` | string | Нет | `"9:16"`, `"16:9"`, `"1:1"` |

---

## 6. Sora2 — Text-to-Video / Image-to-Video

**tool_type (T2V):** `sora2-text-to-video-api`
**tool_type (I2V):** `sora2-image-to-video-api`
**Стоимость:** 420 кредитов (std) / 2100 кредитов (pro)
**Время:** 2-5 минут

> Sora2 — премиум модель. Используй только для высокобюджетного контента.

---

## 7. Seedream — генерация изображений (альтернатива Nano Banana)

**tool_type:** `seedream-v4-5-api` или `seedream-v5-lite-api`
**Стоимость:** 50 кредитов
**Время:** 10-30 секунд

---

## Polling (шаблон)

```bash
TIMEOUT=600  # 10 минут
ELAPSED=0

while [ $ELAPSED -lt $TIMEOUT ]; do
  STATUS_RESPONSE=$(curl -s -X POST "https://sjinn.ai/api/un-api/query_tool_task_status" \
    -H "Authorization: Bearer $SJINN_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"task_id\": \"$TASK_ID\"}")

  STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.data.status')

  case "$STATUS" in
    1) echo "COMPLETED"; break ;;
    -1) echo "FAILED"; exit 1 ;;
    0) sleep 15; ELAPSED=$((ELAPSED + 15)) ;;
  esac
done
```

---

## Стоимость по моделям (в кредитах)

| Модель | tool_type | Кредиты |
|--------|-----------|---------|
| Nano Banana (image) | nano-banana-image-api | 50 |
| Nano Banana Pro (image) | nano-banana-image-pro-api | 150 |
| Seedream v4.5 (image) | seedream-v4-5-api | 50 |
| Seedream v5 Lite (image) | seedream-v5-lite-api | 50 |
| Veo3 T2V | veo3-text-to-video-fast-api | 420 |
| Veo3 I2V | veo3-image-to-video-fast-api | 420 |
| Grok T2V | grok-text-to-video-api | duration × 50 |
| Grok I2V | grok-image-to-video-api | duration × 50 |
| Sora2 T2V | sora2-text-to-video-api | 420 |
| Sora2 I2V | sora2-image-to-video-api | 420 |

---

## Важные правила

1. **Скачивай результат** сразу — URL-ы могут истекать.
2. **Polling:** каждые 10-15 сек для видео, 5-10 сек для изображений.
3. **Таймаут:** 10 минут максимум.
4. **Кредиты возвращаются** при ошибке генерации.
5. **Изображения для I2V** должны быть доступны по полному HTTPS URL.
6. **TTS не доступен** через SJinn — используй ElevenLabs через fal.ai (`fal-ai/elevenlabs/tts/eleven-v3`).
