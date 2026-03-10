# Video Production Agent v5.1

Автономный видео-агент на базе Claude Code CLI + SJinn AI + FFmpeg. Создаёт короткие вертикальные видео (1080×1920, 9:16) для игровых каналов в соцсетях.

> **v5.1** — обновлённые правила промптинга: действие+фраза, покадровый план, dual-style генерация, gaze_direction.

---

## Архитектура

```
┌──────────────────────────────────────────────────────────┐
│                     ./run.sh "MLBB" "Top 5 героев"       │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                  Claude Code CLI (claude -p)              │
│                                                          │
│  Читает: rules/ tools/ games/                            │
│  MCP:    mcp-gsheets, Supabase                           │
│                                                          │
│  1. Читает конфиг игры (Google Sheets / games/*.md)      │
│  2. Выбирает подход (1/2/3) по типу контента + бюджету   │
│  3. Генерирует сцены через fal.ai                        │
│  4. Скачивает результаты (curl)                          │
│  5. Собирает видео через FFmpeg                          │
│  6. Загружает в Supabase Storage                         │
│  7. Пишет лог в video_agent_runs                         │
└──────────────────────────────────────────────────────────┘
```

### Стек

| Компонент | Назначение |
|-----------|-----------|
| Claude Code CLI | Ядро агента (`claude -p` non-interactive или interactive) |
| SJinn AI | Основной провайдер: Nano Banana Pro (images), Veo3/Grok (I2V, T2V) |
| fal.ai | Альтернативный провайдер: FLUX, Kling, Veo, Kokoro TTS |
| FFmpeg (локальный) | Масштабирование, concat, сборка финального видео |
| FFmpeg Cloud API | Cloud FFmpeg (опциональный, api.ffmpeg-api.com) |
| Supabase | Storage (видео, ассеты, музыка) |

---

## Файловая структура

```
video-agent/
├── video-production-agent.md    ← этот документ
├── run.sh                       ← точка входа
├── providers.json               ← конфиг активных провайдеров (переключение API)
├── .claude/
│   └── mcp.json                 ← MCP серверы
├── rules/
│   ├── main.md                  ← правила агента (выбор подхода, бюджет)
│   └── fallback.md              ← таймауты, retry, fallback
├── tools/
│   ├── fal-ai.md                ← API fal.ai: FLUX, Kling, Veo, Kokoro TTS
│   ├── ffmpeg-api.md            ← FFmpeg Cloud API (api.ffmpeg-api.com)
│   ├── kling-direct.md          ← (planned) Kling API напрямую
│   └── google-veo.md            ← (planned) Google Veo через Vertex AI
├── games/
│   └── {game-tag}.md            ← конфиг игры (стиль, герои, TOV)
├── music/
│   └── tracks.json              ← royalty-free треки в Supabase Storage
└── output/                      ← результаты (gitignored)
    └── 2026-03-02_14-30_mlbb_top-heroes/
        ├── scene-1.png
        ├── scene-1.mp4
        ├── voiceover.mp3
        └── final.mp4
```

---

## Три подхода генерации

### Approach 1 — Ken Burns (изображения + анимация)

**Когда:** списки, рейтинги, советы, гайды
**Стоимость:** ~$0.50/видео

```
FLUX.2 Pro (1080×1920) → скачать → FFmpeg zoompan → concat + audio → final.mp4
```

| Компонент | Расчёт | Стоимость |
|-----------|--------|-----------|
| 6 изображений FLUX.2 Pro | 6 × $0.045 (2.07 МП) | $0.27 |
| TTS voiceover | ~30 сек | $0.15 |
| FFmpeg | локально | $0.00 |
| **Итого** | | **~$0.42** |

### Approach 2 — Image-to-Video (Kling)

**Когда:** динамичный контент, геймплей, экшен
**Стоимость:** ~$1.70/видео

```
FLUX.2 Pro (9:16) → скачать → Kling 2.6 Pro I2V (generate_audio: false) → скачать → concat + audio → final.mp4
```

| Компонент | Расчёт | Стоимость |
|-----------|--------|-----------|
| 4 изображения FLUX.2 Pro | 4 × $0.045 | $0.18 |
| 4 клипа Kling 2.6 Pro (generate_audio: false) | 4 × 5 сек × $0.07/сек | $1.40 |
| TTS voiceover | ~20 сек | $0.10 |
| **Итого** | | **~$1.68** |

> **ВАЖНО:** Используем Kling 2.6 Pro с параметром `generate_audio: false`. Аудио всё равно заменяется на voiceover + музыку через FFmpeg, платить за генерацию аудио ($0.14/сек) не нужно.

### Approach 3 — Text-to-Video (Veo 3)

**Когда:** кинематографичный контент, трейлеры, атмосферные видео
**Стоимость:** ~$3.28/видео без аудио (потолок $10)

```
Veo 3 T2V (generate_audio: false) → скачать → concat + audio → final.mp4
```

| Компонент | Расчёт | Стоимость |
|-----------|--------|-----------|
| 2 клипа Veo 3 (без аудио) | 2 × 8 сек × $0.20/сек | $3.20 |
| TTS voiceover | ~16 сек | $0.08 |
| **Итого** | | **~$3.28** |

> **Цены Veo 3:** $0.20/сек без аудио, $0.40/сек с аудио. Мы используем `generate_audio: false` — аудио заменяется через FFmpeg. Максимум 2 клипа × 8 сек. Потолок расходов на Approach 3: **$10**.

---

## MCP конфигурация

### .claude/mcp.json

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "npx",
      "args": ["-y", "mcp-gsheets@latest"],
      "env": {
        "GOOGLE_SERVICE_ACCOUNT_KEY": "/path/to/service-account.json"
      }
    },
    "supabase": {
      "transport": "http",
      "url": "https://mcp.supabase.com/mcp?project_ref=txckerrkubbvmzlionjf&features=docs%2Caccount%2Cdatabase%2Cdebugging%2Cdevelopment%2Cfunctions%2Cbranching%2Cstorage"
    }
  }
}
```

> **Fix #1:** Пакет `@anthropic/google-sheets-mcp` не существует. Используем `mcp-gsheets` — самый популярный TypeScript MCP-коннектор для Google Sheets.

> **Fix #8:** Supabase MCP использует HTTP transport с полным набором features (8 штук).

---

## FFmpeg команды

### Ken Burns (zoompan)

```bash
ffmpeg -loop 1 -i scene-1.png -t 5 \
  -vf "scale=3000:-1,zoompan=z='min(zoom+0.004,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125:s=1080x1920:fps=25" \
  -c:v libx264 -pix_fmt yuv420p scene-1.mp4
```

| Параметр | Значение | Почему |
|----------|----------|--------|
| `scale=3000:-1` | Масштаб до 3000px ширины | 8000px = ~1.5 ГБ RAM на кадр, 3000px достаточно для зума |
| `d=125` | 125 кадров | При 25fps = 5 сек, согласовано с `-t 5` |
| `zoom+0.004` | Скорость зума | За 125 кадров: +0.5 (от 1.0 до 1.5) — видимый эффект |
| `s=1080x1920` | Выходной размер | Вертикальное видео 9:16 |

### Concat

```bash
# Создать список
for f in scene-*.mp4; do echo "file '$f'" >> concat.txt; done

# Склеить
ffmpeg -f concat -safe 0 -i concat.txt -c copy joined.mp4
```

### Audio overlay

```bash
ffmpeg -i joined.mp4 -i voiceover.mp3 -i music.mp3 \
  -filter_complex "[1:a]volume=1.0[vo];[2:a]volume=0.3[bg];[vo][bg]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -shortest final.mp4
```

---

## Pipeline с fal.ai

### Шаг скачивания (обязательный)

fal.ai возвращает URL к сгенерированным файлам. **Каждый pipeline должен включать явный шаг скачивания:**

```bash
# После генерации изображения
curl -s -o scene-1.png "https://fal.run/cdn/result/..."

# После генерации видео
curl -s -o scene-1.mp4 "https://fal.run/cdn/result/..."
```

### Async handling (для видео)

Генерация видео через Kling/Veo занимает 1-5 минут.

```
1. Отправить запрос → получить request_id
2. Polling каждые 15 секунд: GET /status/{request_id}
3. Статусы: QUEUED → IN_PROGRESS → COMPLETED / FAILED
4. Таймаут: 10 минут максимум
5. При таймауте: отменить задачу, fallback на Approach 1
```

| Событие | Действие |
|---------|----------|
| COMPLETED | Скачать результат, продолжить pipeline |
| FAILED | Retry 1 раз. Если снова FAILED → fallback на Approach 1 |
| Таймаут 10 мин | Отменить, fallback на Approach 1 |
| Зависшая задача | Если нет обновлений 3 мин → считать зависшей, fallback |

---

## Схема БД

### Таблица `video_agent_runs`

```sql
CREATE TABLE video_agent_runs (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at timestamptz DEFAULT now(),
  game_tag text NOT NULL,
  input_idea text NOT NULL,
  agent_plan text,
  approach_used integer,               -- 1, 2 или 3
  model_used text,                      -- NEW: kling-2.6-pro / veo3.1 / flux.2-pro
  total_cost_usd numeric(8,4),
  output_video_url text,
  status text DEFAULT 'running',        -- running / completed / failed
  error_message text,
  video_duration_seconds integer,       -- NEW: длительность готового видео
  run_duration_seconds integer,         -- RENAMED: время работы агента (было duration_seconds)
  scenes jsonb                          -- NEW: [{prompt, model, cost, duration_sec}]
);
```

> **Fix #10:** Добавлены 4 поля для аналитики. `duration_seconds` переименован в `run_duration_seconds` чтобы не путать с длительностью видео.

### Пример `scenes` jsonb

```json
[
  {
    "index": 1,
    "prompt": "MLBB hero Lancelot in dynamic pose, 9:16 vertical",
    "model": "flux.2-pro",
    "type": "image",
    "cost": 0.045,
    "duration_sec": null
  },
  {
    "index": 1,
    "prompt": "Animate hero with sword slash motion",
    "model": "kling-2.6-pro",
    "type": "i2v",
    "cost": 0.35,
    "duration_sec": 5
  }
]
```

---

## Музыка

### Стратегия

Заготовленные **royalty-free** треки в Supabase Storage.

| Источник | Лицензия | Примечание |
|----------|----------|------------|
| Pixabay Music | Pixabay License (free for commercial) | Основной источник |
| Uppbeat | Free tier (attribution) | Альтернатива |

> **Fix #11:** YouTube/TikTok автоматически детектят копирайт. Только royalty-free треки с подтверждённой лицензией.

### music/tracks.json

```json
{
  "tracks": [
    {
      "name": "epic-gaming-beat",
      "url": "https://YOUR_PROJECT.supabase.co/storage/v1/object/public/music/epic-gaming-beat.mp3",
      "duration_sec": 120,
      "mood": "epic",
      "bpm": 140,
      "license": "pixabay",
      "games": ["MLBB", "PUBG Mobile", "DELTA FORCE"]
    },
    {
      "name": "chill-strategy",
      "url": "https://YOUR_PROJECT.supabase.co/storage/v1/object/public/music/chill-strategy.mp3",
      "duration_sec": 90,
      "mood": "chill",
      "bpm": 100,
      "license": "pixabay",
      "games": ["POKEMON GO", "MTG ARENA", "MONOPOLY"]
    }
  ]
}
```

---

## run.sh

```bash
#!/bin/bash
set -euo pipefail

# Определяем директорию скрипта (Fix #5)
cd "$(dirname "$0")"

GAME_TAG="${1:?Usage: ./run.sh GAME_TAG \"idea\"}"
IDEA="${2:?Usage: ./run.sh GAME_TAG \"idea\"}"

# Формат имени: единый (Fix #12)
TIMESTAMP=$(date +%Y-%m-%d_%H-%M)
SLUG=$(echo "$IDEA" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-' | head -c 30)
OUTPUT_DIR="output/${TIMESTAMP}_${GAME_TAG}_${SLUG}"
mkdir -p "$OUTPUT_DIR"

echo "=== Video Production Agent ==="
echo "Game:   $GAME_TAG"
echo "Idea:   $IDEA"
echo "Output: $OUTPUT_DIR"
echo "=============================="

claude -p "
Ты — Video Production Agent. Создай вертикальное видео (1080×1920) для игры ${GAME_TAG}.

Идея: ${IDEA}

Правила:
- Прочитай rules/main.md и rules/fallback.md
- Прочитай tools/fal-ai.md и tools/ffmpeg.md
- Прочитай games/${GAME_TAG}.md (если есть) или возьми данные из Google Sheets
- Прочитай music/tracks.json для выбора фоновой музыки
- Сохрани все файлы в ${OUTPUT_DIR}/
- Залей финальное видео в Supabase Storage
- Запиши лог в таблицу video_agent_runs

Бюджет:
- Approach 1 (Ken Burns): до \$2
- Approach 2 (I2V Kling): до \$3
- Approach 3 (T2V Veo): до \$10
"
```

---

## Бюджеты

### Стоимость за единицу (актуальные цены fal.ai)

| Ресурс | Цена | Примечание |
|--------|------|------------|
| FLUX.2 Pro изображение (1080×1920) | $0.045/шт | 2.07 МП: $0.03 за 1 МП + $0.015/доп. МП |
| Kling 2.6 Pro I2V (generate_audio: false) | $0.07/сек | БЕЗ аудио — аудио заменяется |
| Kling 2.6 Pro I2V (с аудио) | $0.14/сек | НЕ ИСПОЛЬЗУЕМ |
| Veo 3 T2V (generate_audio: false) | $0.20/сек | Без аудио — вдвое дешевле |
| Veo 3 T2V (с аудио) | $0.40/сек | НЕ ИСПОЛЬЗУЕМ |
| Kokoro TTS | $0.02/1000 символов | fal.ai, ~$0.01 за 30 сек озвучки |

### Стоимость за видео

| Approach | Средняя | Максимум |
|----------|---------|----------|
| 1. Ken Burns | $0.50 | $2.00 |
| 2. I2V Kling | $1.70 | $3.00 |
| 3. T2V Veo | $6.50 | $10.00 |

### Месячные расходы (Fix #13)

| Сценарий | Расчёт | Итого |
|----------|--------|-------|
| 60 видео (80% Approach 1+2, 20% Approach 3) | 48 × $2 + 12 × $10 | **$216/мес** |
| 60 видео (100% Approach 1+2) | 60 × $1.50 | **$90/мес** |
| 60 видео (по плану v3.2) | 60 × $3 | ~~$180/мес~~ (занижено) |

---

## Claude Code CLI чеклист (Fix #14)

Перед первым запуском проверить:

```bash
# 1. MCP серверы загружаются
claude -p "Перечисли доступные MCP серверы" --allowedTools mcp__*

# 2. Google Sheets доступны
claude -p "Прочитай данные из Google Sheets Control Center"

# 3. Supabase доступен
claude -p "Выполни SELECT 1 через Supabase MCP"

# 4. Чтение файлов работает
claude -p "Прочитай rules/main.md и выведи первую строку"

# 5. FFmpeg установлен
ffmpeg -version

# 6. fal.ai ключ
echo $FAL_KEY | head -c 10
```

---

## Таблица исправлений v3.2 → v4.0

| # | Проблема | Критичность | Исправление |
|---|----------|-------------|-------------|
| 1 | `@anthropic/google-sheets-mcp` не существует | CRITICAL | Заменён на `mcp-gsheets` (npx, TypeScript) |
| 2 | Veo 3.1 = $0.40/сек, Approach 3 стоит $12+ | CRITICAL | Ограничено: макс 2 клипа × 8 сек ($6.40), потолок $10 |
| 3 | Kling с ненужным аудио ($0.14/сек) | MEDIUM | `generate_audio: false`, $0.07/сек |
| 4 | Стоимость изображений 1080×1920 занижена | LOW | $0.045/шт (2.07 МП по FLUX.2 Pro) |
| 5 | run.sh — hardcoded path | MEDIUM | `cd "$(dirname "$0")"` |
| 6 | FFmpeg Ken Burns — RAM + timing | MEDIUM | scale=3000, d=125 (25fps×5сек), zoom+0.004 |
| 7 | Нет шага скачивания с fal.ai | MEDIUM | Явный `curl -o` в каждом pipeline |
| 8 | Supabase MCP URL урезан | LOW | Полный URL с 8 features |
| 9 | Нет async timeout handling | MEDIUM | 10 мин таймаут, polling 15 сек, fallback |
| 10 | БД — мало полей для аналитики | LOW | +4 поля: video_duration, scenes, model_used, run_duration |
| 11 | Лицензирование музыки | MEDIUM | Royalty-free треки в Supabase Storage |
| 12 | Output naming конфликт | LOW | Единый формат `%Y-%m-%d_%H-%M_{game}_{slug}` |
| 13 | Месячные расходы занижены | LOW | $216/мес (пересчёт с реальными ценами) |
| 14 | claude -p + MCP не протестировано | MEDIUM | Чеклист верификации перед запуском |
