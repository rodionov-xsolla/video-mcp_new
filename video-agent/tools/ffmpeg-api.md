# FFmpeg Cloud API Reference

Справочник FFmpeg Cloud API (ffmpeg-api.com) для сборки видео.

> **ВАЖНО: Ограничения API**
> - Результаты (R2 presigned URLs) **нельзя** использовать как inputs обратно в API (403)
> - `filter_complex` с символами `[]` и `;` **не поддерживается** ("Invalid characters")
> - Для concat и сложных операций используй **локальный ffmpeg** (см. раздел 9)
> - AI endpoint `/ai/ffmpeg/process` **ненадёжен** для сложных задач (crashes)

---

## Аутентификация

```
Authorization: Basic $FFMPEG_API_KEY
```

**Base URL:** `https://api.ffmpeg-api.com`

---

## Основные эндпоинты

| Эндпоинт | Метод | Описание | Надёжность |
|----------|-------|----------|------------|
| `/ffmpeg/process` | POST | Синхронная обработка | Надёжный для простых операций |
| `/ffmpeg/process/async` | POST | Асинхронная обработка | Надёжный |
| `/ai/ffmpeg/process` | POST | AI-обработка | Ненадёжный, часто crashes |
| `/ffprobe/analyze` | POST | Анализ медиафайлов | Надёжный |
| `/job/{jobId}` | GET | Статус async задачи | Надёжный |

---

## 1. Ken Burns Effect (zoompan) — РАБОЧИЙ

Превращает изображение в видеоклип с эффектом зума. Входной файл — любой HTTPS URL.

### Формат запроса (ПРОВЕРЕННЫЙ)

```bash
curl -s -X POST "https://api.ffmpeg-api.com/ffmpeg/process" \
  -H "Authorization: Basic $FFMPEG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "inputs": [
        {
          "file_path": "https://example.com/scene-1.png",
          "options": ["-loop", "1"]
        }
      ],
      "outputs": [
        {
          "file": "scene-1.mp4",
          "options": [
            "-t", "5",
            "-vf", "scale=2000:-1,zoompan=z=zoom+0.004:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d=125:s=1080x1920:fps=25",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p"
          ]
        }
      ]
    }
  }'
```

> **ВАЖНО:**
> - Поле outputs — `"file"`, НЕ `"file_name"`
> - Поле inputs — `"file_path"` (объект, не строка)
> - Формула `zoom+0.004` без `min()` — за 125 кадров зум ≈ 1.5x
> - `scale=2000:-1` достаточно (3000 не нужно)

### Вариации зума

**Zoom-in (стандарт):** `z=zoom+0.004` — от 1.0x до 1.5x за 5 сек

**Zoom-out:** `z=1.5-on*0.004` — от 1.5x до 1.0x

**Без зума (pan only):** `z=1.3:x=on*4` — горизонтальный пан

### Формат ответа (РЕАЛЬНЫЙ)

```json
{
  "ok": true,
  "result": [
    {
      "size_bytes": 1299667,
      "download_url": "https://ffmpeg.xxx.eu.r2.cloudflarestorage.com/...",
      "file_name": "scene-1.mp4"
    }
  ],
  "usage": {
    "time_sec": 4.84,
    "input_size_gb": 0.001318,
    "output_size_gb": 0.0013,
    "gb_sec": 0.01267
  }
}
```

> **ВАЖНО:** Поле ответа — `"result"` (массив), НЕ `"results"`

### Параметры zoompan

| Параметр | Значение | Зачем |
|----------|----------|-------|
| `scale=2000:-1` | Масштаб | Достаточно для зума 1.5x |
| `d=125` | 125 кадров | 25fps × 5 сек |
| `zoom+0.004` | Скорость | +0.5 за 125 кадров (1.0→1.5) |
| `s=1080x1920` | Выходной размер | Вертикальное 9:16 |
| `fps=25` | Частота | Стандарт |

---

## 2. Concat (склейка) — ТОЛЬКО ЛОКАЛЬНО

> **НЕЛЬЗЯ** сделать concat через FFmpeg Cloud API:
> - `filter_complex` с `[0:v][1:v]concat=...` отклоняется ("Invalid characters")
> - R2 URLs от предыдущих операций возвращают 403 при использовании как inputs
> - AI endpoint часто crashes на concat задачах

### Решение: локальный ffmpeg

```bash
FFMPEG="/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg"

# 1. Скачай каждую сцену после Ken Burns
curl -s -o output/scene-1.mp4 "$DOWNLOAD_URL_1"
curl -s -o output/scene-2.mp4 "$DOWNLOAD_URL_2"
# ...

# 2. Создай concat list
cat > output/concat-list.txt << 'EOF'
file 'scene-1.mp4'
file 'scene-2.mp4'
file 'scene-3.mp4'
file 'scene-4.mp4'
file 'scene-5.mp4'
EOF

# 3. Склей без перекодирования
$FFMPEG -y -f concat -safe 0 -i output/concat-list.txt -c copy output/final.mp4
```

> Если ffmpeg не в PATH, используй полный путь: `/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg`

---

## 3. Audio Overlay — ТОЛЬКО ЛОКАЛЬНО

Аналогично concat, audio overlay требует filter_complex и должен выполняться локально.

```bash
FFMPEG="/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg"

$FFMPEG -y \
  -i output/joined.mp4 \
  -i voiceover.wav \
  -i music.mp3 \
  -filter_complex "[1:a]volume=1.0[vo];[2:a]volume=0.3[bg];[vo][bg]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" \
  -c:v copy -c:a aac -shortest \
  output/final.mp4
```

---

## 4. Конвертация аудио — РАБОЧИЙ через API

Простые операции без filter_complex работают.

```bash
curl -s -X POST "https://api.ffmpeg-api.com/ffmpeg/process" \
  -H "Authorization: Basic $FFMPEG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "inputs": [
        {"file_path": "https://example.com/voiceover.wav"}
      ],
      "outputs": [
        {
          "file": "voiceover.mp3",
          "options": ["-codec:a", "libmp3lame", "-b:a", "192k"]
        }
      ]
    }
  }'
```

---

## 5. Анализ медиафайлов (ffprobe)

```bash
curl -s -X POST "https://api.ffmpeg-api.com/ffprobe/analyze" \
  -H "Authorization: Basic $FFMPEG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "https://example.com/scene-1.mp4",
    "probe": {
      "streams": ["codec_name", "width", "height", "duration"]
    },
    "select_streams": "v:0"
  }'
```

---

## 6. Асинхронная обработка

Для операций >30 секунд.

### Отправка

```bash
RESPONSE=$(curl -s -X POST "https://api.ffmpeg-api.com/ffmpeg/process/async" \
  -H "Authorization: Basic $FFMPEG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "inputs": [{"file_path": "..."}],
      "outputs": [{"file": "...", "options": [...]}]
    }
  }')

JOB_ID=$(echo "$RESPONSE" | jq -r '.job_id')
```

### Polling

```bash
curl -s "https://api.ffmpeg-api.com/job/$JOB_ID" \
  -H "Authorization: Basic $FFMPEG_API_KEY"
```

Статусы: `pending` → `processing` → `completed` / `failed`

---

## 7. Загрузка локальных файлов

```bash
# 1. Получить presigned URL
UPLOAD=$(curl -s -X POST "https://api.ffmpeg-api.com/file" \
  -H "Authorization: Basic $FFMPEG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"file_name": "scene-1.png"}')

UPLOAD_URL=$(echo "$UPLOAD" | jq -r '.upload_url')

# 2. Загрузить файл
curl -s -X PUT "$UPLOAD_URL" --data-binary @scene-1.png
```

---

## 8. Обработка ошибок

| HTTP код | Значение | Действие |
|----------|----------|----------|
| 200 | Успех | `result[0].download_url` |
| 400 | Неверный запрос | Проверить формат (file vs file_name) |
| 401 | Неверный ключ | Проверить FFMPEG_API_KEY |
| 403 | Доступ запрещён / R2 URL | Нельзя использовать output URLs как inputs |
| 500 | Ошибка обработки | Retry 1 раз |

---

## 9. Рабочий pipeline (ПРОВЕРЕННЫЙ)

```
Шаг 1: Для каждого scene-N.png:
        POST /ffmpeg/process → Ken Burns → скачать scene-N.mp4 локально

Шаг 2: Локальный ffmpeg:
        -f concat → joined.mp4

Шаг 3: Локальный ffmpeg:
        filter_complex audio overlay → final.mp4

Шаг 4: Загрузить final.mp4 в Supabase Storage
```

> **Ключевой момент:** FFmpeg Cloud API используется ТОЛЬКО для Ken Burns (одиночные операции).
> Все операции с filter_complex (concat, audio mix) делаются локально.

---

## 10. Известные баги API

1. **`file` vs `file_name`**: outputs требуют поле `"file"`, не `"file_name"`
2. **`result` vs `results`**: ответ содержит `"result"`, не `"results"`
3. **Inputs — объекты**: `{"file_path": "url"}`, не просто `"url"`
4. **R2 URLs одноразовые**: download_url нельзя передать обратно как input (403)
5. **filter_complex запрещён**: символы `[]` и `;` считаются "Invalid characters"
6. **AI endpoint ненадёжен**: часто exit code 234 или SIGABRT на сложных задачах
