# Fallback и обработка ошибок

Правила поведения при таймаутах, ошибках генерации и сбоях FFmpeg.

---

## Async polling (fal.ai)

Генерация видео/изображений через fal.ai — асинхронная. После отправки запроса:

1. Получи `request_id` из ответа
2. Каждые **15 секунд** проверяй статус
3. Максимальное время ожидания одной генерации: **10 минут**

### ⚠️ КРИТИЧНО: Base URL для status/result

Submit идёт на **полный** endpoint, но status и result — только по **2-сегментному base path**.

```python
# Правило: base = первые 2 сегмента endpoint
base = "/".join(endpoint.split("/")[:2])

# Status:  https://queue.fal.run/{base}/requests/{request_id}/status
# Result:  https://queue.fal.run/{base}/requests/{request_id}
```

| Модель | Submit endpoint | Status/Result base |
|--------|-----------------|-------------------|
| NB2 edit | `fal-ai/nano-banana-2/edit` | `fal-ai/nano-banana-2` |
| Kling I2V | `fal-ai/kling-video/v2.6/pro/image-to-video` | `fal-ai/kling-video` |
| Kling Avatar v2 | `fal-ai/kling-video/ai-avatar/v2/standard` | `fal-ai/kling-video` |
| ElevenLabs TTS | `fal-ai/elevenlabs/tts/eleven-v3` | `fal-ai/elevenlabs` |
| Kokoro TTS | `fal-ai/kokoro/american-english` | `fal-ai/kokoro` |

**Если использовать полный путь** → fal.ai возвращает пустой body или 404, задача «теряется».

### Статусы и действия

| Статус | Действие |
|--------|----------|
| `IN_QUEUE` / `IN_PROGRESS` | Продолжай polling |
| `COMPLETED` | Забери результат через GET /requests/{REQUEST_ID}, продолжи pipeline |
| `FAILED` | Retry 1 раз. Если снова FAILED → fallback |
| Таймаут 10 мин | Отменить задачу, fallback |

---

## Каскад fallback

### Изображения

```
Nano Banana 2 ──FAIL──→ retry 1 раз ──FAIL──→ GPT Image 1 (fal-ai/gpt-image-1/text-to-image) ──FAIL──→ статус 'failed'
```

**Nano Banana 2 — основная модель.** Для первой сцены (нет референса) — сначала сгенерируй character-ref через Nano Banana 2 с нейтральным промптом, используй его URL как `image_urls[0]`. НЕ переключайся на flux-pro или другие модели без явной ошибки.

**GPT Image 1 — fallback.** Доступен через fal.ai (тот же FAL_KEY). Endpoint: `fal-ai/gpt-image-1/text-to-image`. Размеры: `1024x1536` (вертикальный). Не поддерживает `image_urls` — используй подробный промпт с описанием персонажа для консистентности.

**Если `fal.run` sync endpoint не отвечает** — используй `queue.fal.run` async endpoint с polling.

### Видео

При ошибке генерации — спускайся по каскаду:

```
Kling I2V ──FAIL──→ retry 1 раз ──FAIL──→ Ken Burns (FFmpeg zoompan)
Veo3 T2V  ──FAIL──→ retry 1 раз ──FAIL──→ Kling I2V (без речи) ──FAIL──→ Ken Burns
Ken Burns  ──FAIL──→ retry 1 раз ──FAIL──→ статус 'failed', записать ошибку
```

При fallback:
- Перепланируй сцены под новый подход
- Сохрани уже сгенерированные файлы (не удаляй)
- В логе укажи исходный и финальный подход

---

## Ошибки fal.ai API

| Ошибка | Действие |
|--------|----------|
| **Rate limited (429)** | Подожди 30 секунд, retry |
| **Invalid input (400/422)** | Проверь промпт и параметры, retry |
| **Server error (500)** | Подожди 60 секунд, retry 1 раз |
| **Model unavailable (503)** | Fallback на следующую модель |
| **Timeout** | Fallback на следующую модель |

Максимум **1 retry** на каждую генерацию. Не зацикливайся.

---

## Ошибки FFmpeg Cloud API

| Ошибка | Действие |
|--------|----------|
| HTTP 400 | Проверь JSON и параметры запроса |
| HTTP 401 | Проверь FFMPEG_API_KEY |
| HTTP 403 (квота) | Подожди или используй AI endpoint вместо стандартного |
| HTTP 500 (обработка) | Retry 1 раз через 30 сек |
| Concat fails | Проверь что все URL клипов доступны. Используй AI endpoint с описанием задачи |
| Audio overlay fails | Попробуй без музыки. Если и это не работает — выдай видео без аудио |
| Ken Burns fails | Проверь размеры изображения через `/ffprobe/analyze`. Убедись что ширина ≥ 1080px |
| Файл 0 байт | Перегенерируй |

---

## Ошибки скачивания

| Ошибка | Действие |
|--------|----------|
| curl вернул ошибку | Retry через 10 секунд, максимум 3 попытки |
| Файл 0 байт | Удали и перегенерируй |
| URL истёк | fal.ai URLs are temporary — always download immediately after generation |
| Повторный запрос URL | **НИКОГДА** не перезапрашивать fal.ai result URL для передачи между этапами. Скачать локально → загрузить в Supabase → использовать постоянный URL |

После каждого скачивания проверяй размер файла:
```bash
filesize=$(stat -f%z "scene-1.png" 2>/dev/null || stat -c%s "scene-1.png" 2>/dev/null)
if [ "$filesize" -lt 1000 ]; then
  echo "ERROR: Downloaded file is too small"
fi
```

---

## Логирование ошибок

При любой ошибке, которая приводит к `status='failed'`:

<!-- TODO: реализовать INSERT в video_agent_runs -->
1. Запиши в `video_agent_runs`:
   - `status`: 'failed'
   - `error_message`: описание ошибки (какой подход, какой шаг, что пошло не так)
   - `total_cost_usd`: расходы до момента ошибки
   - `scenes`: все сцены, включая неуспешные

2. Не удаляй промежуточные файлы — они нужны для диагностики.

---

## Таймауты по операциям

| Операция | Таймаут |
|----------|---------|
| Генерация изображения (Nano Banana 2) | 120 секунд |
| Генерация видео (Kling 2.6 Pro I2V) | 10 минут |
| Генерация видео (Veo3 T2V) | 10 минут |
| Скачивание файла (curl) | 120 секунд |
| FFmpeg операция | 5 минут |
| **Весь pipeline (worker.sh)** | **40 минут** |
