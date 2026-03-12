# Video MCP — AI Video Production Agent

Автономный агент для создания коротких вертикальных видео (1080×1920, 9:16) для игровых каналов в соцсетях. Работает через Claude Code CLI + SJinn AI + FFmpeg.

## Как это работает

```
Идея → Сторибоард → Изображения → Анимация (I2V) → Сборка → Видео
```

Агент получает идею для ролика и игру, сам пишет сценарий, генерирует изображения через AI, анимирует их в видео через Image-to-Video модели, и собирает финальный ролик через FFmpeg.

## Быстрый старт

### 1. Настройка

```bash
cd video-agent
cp .env.example .env
# Заполни API-ключи в .env
```

**Необходимые ключи:**
| Ключ | Где взять | Для чего |
|------|-----------|----------|
| `SJINN_API_KEY` | [sjinn.ai](https://sjinn.ai) | Генерация изображений и видео |
| `FFMPEG_API_KEY` | [ffmpeg-api.com](https://api.ffmpeg-api.com) | Cloud FFmpeg (опционально) |
| `FAL_KEY` | [fal.ai](https://fal.ai) | Альтернативный провайдер (опционально) |

### 2. Supabase (для очереди задач)

```bash
# Выполни queue/setup.sql в Supabase SQL Editor
# Создай Storage bucket "videos" (public) через Dashboard
```

### 3. Запуск

**Автоматический воркер (рекомендуемый):**
```bash
cd video-agent/queue
./worker.sh          # Ctrl+C для остановки
# или в фоне:
nohup ./worker.sh > /dev/null 2>&1 &
```

Воркер сам проверяет очередь каждые 30 сек, подхватывает задачи и запускает `claude -p`.

**Добавление задач:**
- Через **Google Sheet** (настройка: `queue/google-sheets-setup.md`)
- Через **CLI**: `./queue/add-task.sh "Oxide" "История нуба на острове"`

**Разовый запуск (без очереди):**
```bash
./run.sh "Oxide" "История нуба на острове"
```

**Ручной (через Claude Code):**
```bash
cd video-agent
claude
# Затем описываешь задачу в чате
```

### 3. Результат

```
video-agent/output/2026-03-05_16-50_Kekele_game-vs-reality/
├── storyboard.json       # Сценарий
├── generate.sh           # Скрипт генерации (воспроизводимый)
├── scene-1.png           # Сгенерированные кадры
├── scene-1.mp4           # Анимированные клипы
├── scene-1-scaled.mp4    # Масштабированные к 1080x1920
└── final.mp4             # Финальное видео
```

## Структура проекта

```
video-agent/
├── video-production-agent.md   # Архитектура агента
├── run.sh                      # Точка входа (автоматический запуск)
├── providers.json              # Конфиг провайдеров AI (SJinn, fal.ai)
│
├── rules/                      # Правила для агента
│   ├── main.md                 # Workflow: 6 фаз pipeline
│   ├── storyboard.md           # Правила написания сценариев
│   ├── consistency.md          # Визуальная консистентность между сценами
│   └── fallback.md             # Обработка ошибок и таймаутов
│
├── games/                      # Конфиги игр
│   ├── oxide.md                # Oxide: Survival Island
│   ├── kekele.md               # Kakele Online MMORPG
│   └── mlbb.md                 # Mobile Legends: Bang Bang
│
├── tools/                      # API-документация провайдеров
│   ├── sjinn.md                # SJinn AI: Nano Banana, Veo3, Grok
│   ├── fal-ai.md               # fal.ai: FLUX, Kling, Veo, Kokoro TTS
│   └── ffmpeg-api.md           # FFmpeg Cloud API
│
├── queue/                      # Система очереди задач
│   ├── worker.sh               # Автономный воркер (бесконечный цикл)
│   ├── check-queue.sh          # Проверка и атомарный claim задачи
│   ├── update-task.sh          # Обновление статуса задачи
│   ├── add-task.sh             # Добавление задачи через CLI
│   ├── setup.sql               # DDL для таблицы video_tasks
│   └── google-sheets-setup.md  # Инструкция по интеграции с Google Sheets
│
├── music/                      # Фоновая музыка
│   └── tracks.json             # Royalty-free треки (Supabase Storage)
│
└── output/                     # Результаты генерации (gitignored media)
    ├── 2026-03-05_13-14_Oxide_noob-day-one/
    ├── 2026-03-05_15-35_Oxide_noob-success-v3/
    └── 2026-03-05_16-50_Kekele_game-vs-reality/
```

## Pipeline: 6 фаз

| Фаза | Что делает | Детали |
|------|-----------|--------|
| **0. Init** | Загрузка конфигов | `providers.json`, `games/*.md`, `rules/*.md` |
| **1. Storyboard** | Написание сценария | `storyboard.json` — narrative arc, промпты, камеры |
| **2. Character Ref** | Якорное изображение | Фиксирует внешность ГГ для всех сцен |
| **3. Image Gen** | Генерация кадров | Nano Banana Pro, chain reference для консистентности |
| **4. Animation** | I2V анимация | Veo3 / Grok, ~8 сек на клип, с голосом и липсинком |
| **5. Assembly** | Сборка видео | FFmpeg: scale → concat → `final.mp4` |
| **6. Upload** | Загрузка | Supabase Storage + лог в БД |

## Три подхода генерации

| Подход | Когда | Модели | Стоимость |
|--------|-------|--------|-----------|
| **1. Ken Burns** | Списки, рейтинги, гайды | Image → FFmpeg zoompan | ~500 кредитов |
| **2. I2V** | Экшен, истории, комедия | Image → Veo3/Grok I2V | ~1500 кредитов |
| **3. T2V** | Кинематограф, трейлеры | Veo3 Text-to-Video | ~2000 кредитов |

## Ключевые правила промптинга

Полные правила в `rules/storyboard.md`. Основные:

- **Действие + фраза вместе** — речь привязана к действию: `Character swings sword and shouts: "Who is the noob NOW?!"`
- **Максимум 2 фокусные точки** в одном 9:16 кадре
- **Камера разная** для каждого соседнего клипа (close-up → wide → low angle)
- **Минимум 2 действия** в каждом 8-сек клипе (нет зацикленных жестов)
- **gaze_direction** обязателен при 2+ персонажах в кадре
- **Живые описания** — кожа, шрамы, борода, грязь (не "armored man" → киборг)

## Добавление новой игры

Создай файл `games/{game-tag}.md` по шаблону:

```markdown
# Название Игры

## Visual Style Guide
- Цветовая палитра
- Освещение
- Prompt prefix

## Character Prompt Blocks
### Герой 1
`детальное описание внешности, минимум 8 визуальных деталей`

## Tone of Voice
- Настроение контента

## Идеи контента
- Список идей для роликов
```

Примеры: `games/oxide.md`, `games/kekele.md`, `games/mlbb.md`

## Примеры сгенерированных видео

| Видео | Игра | Концепт | Клипов | Длительность |
|-------|------|---------|--------|-------------|
| Oxide v0 | Oxide: Survival Island | День 1 нуба на острове | 3 | ~24 сек |
| Oxide v3 | Oxide: Survival Island | От нуба до короля (история успеха) | 5 | ~40 сек |
| Kekele | Kakele Online | Game vs Reality: cartoon + real human | 3 | ~24 сек |

## Лицензия

Private repository.
