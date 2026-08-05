# Структура проекта Video Production Agent

Правила организации файлов и директорий.

---

## Директории

| Директория | Назначение |
|---|---|
| `rules/main/` | Основные правила pipeline: budgets, fallback, скилл создания формата. Универсальные для ВСЕХ форматов. |
| `rules/formats/` | Правила форматов видео. Каждый формат — отдельный самодостаточный файл. |
| `games/{tag}/` | Конфиги игр. Каждая игра — отдельная папка. |
| `tools/` | Скрипты пайплайна (gate-скрипты, FFmpeg-хелперы) и API-документация внешних сервисов. Справочник — `SCRIPTS.md`. |
| `music/` | Фоновая музыка (tracks.json). |
| `queue/` | Система очередей задач (worker, scripts, Supabase интеграция). |
| `output/` | Сгенерированные видео (вложенная структура). |

---

## Принципы организации

### 1. Один файл — одна зона ответственности

- **Main rules** содержат ТОЛЬКО универсальную логику pipeline (фазы 0-6)
- **Format files** содержат ВСЁ специфичное для формата: детекцию, модели, фазы, консистентность, валидацию
- **Game configs** содержат ТОЛЬКО идентичность игры: стиль, персонажи, tone of voice, музыка

### 2. Нет дублирования

- Consistency rules живут ВНУТРИ format files (не в отдельном документе)
- Main rules НИКОГДА не содержат format-specific логику
- Game configs НИКОГДА не содержат workflow/format логику

### 3. Модель определяется форматом

Workflow.md не диктует модель генерации. Каждый format file сам указывает какие модели использовать.

---

## Как добавить новый формат

1. Прочитай `rules/main/new-format-skill.md` — пошаговый скилл-опросник
2. Пройди 8 шагов скилла: сбор данных → дерево моделей → условные вопросы → расчёт бюджета → генерация playbook → обновление cross-cutting файлов → auxiliary → валидация
3. Скилл автоматически указывает какие файлы создать и обновить

---

## Как добавить новую игру

1. Создай `games/{tag}/{tag}.md` с секциями:
   - Метаданные (жанр, платформа, аудитория)
   - Visual Style Guide (палитра, освещение, prompt prefix)
   - Герои для промптов (таблица)
   - Tone of Voice
   - Character Prompt Blocks (готовые описания для промптов)
   - Музыка

2. **НЕ добавляй** в game config: идеи контента, workflow правила, format-specific логику

---

## Как добавить game-specific format override

Если для конкретной игры нужны особые настройки формата:

1. Создай `games/{tag}/{format}_special.md`
   - Например: `games/mlbb/news_special.md` — настройки News для MLBB
   - Например: `games/roblox/serial-drama_special.md` — настройки Serial Drama для Roblox

2. Этот файл загружается АВТОМАТИЧЕСКИ в Phase 0, если существует

---

## Структура output

```
output/
└── YYYY-MM-DD/                  # Дата генерации
    └── {GAME_TAG}/              # Тег игры (MLBB, Roblox, Oxide...)
        └── {format_slug}/       # Формат (standard, news, serial-drama...)
            ├── storyboard.json  # Сценарий
            ├── research.json    # (только news формат)
            ├── scenes/
            │   ├── refs/        # Character references
            │   │   └── character-ref.png
            │   ├── scene-1/     # Артефакты сцены 1
            │   │   ├── scene-1.png
            │   │   ├── scene-1.mp4
            │   │   └── scene-1-scaled.mp4
            │   └── scene-2/
            │       └── ...
            └── final.mp4        # Финальное видео (ТОЛЬКО финал в корне)
```

**Правила:**
- Каждая сцена — в своей подпапке внутри `scenes/`
- Character references — в `scenes/refs/`
- Только `final.mp4` лежит в корне output-директории формата
- `storyboard.json` — в корне (нужен для воспроизводимости)

---

## Файлы проекта

```
video-agent/
├── CLAUDE.md                    # Entry point агента
├── STRUCTURE.md                 # Этот файл
├── providers.json               # Активные API-провайдеры
│
├── rules/
│   ├── main/
│   │   ├── workflow.md          # 6 фаз pipeline
│   │   ├── storyboard.md       # Правила сторибоарда + консистентность
│   │   ├── budgets.md          # Бюджеты и прайсинг
│   │   ├── fallback.md         # Обработка ошибок
│   │   └── new-format-skill.md # Скилл создания нового формата
│   └── formats/
│       ├── news.md              # Новости (ведущий + репортёр)
│       ├── serial-drama.md      # Сериальные микро-драмы
│       ├── dual-style.md        # Cartoon + realistic
│       ├── gameplay-ai-avatar.md # Говорящая голова + геймплей
│       ├── character-story.md   # Лор-монолог персонажа
│       ├── item-story.md        # Лор-история внутриигрового предмета от внешнего рассказчика
│       ├── motion-dance.md     # Motion transfer танец с реф-видео
│       ├── what-if-real-life.md # «Что если бы персонаж попал в реальную жизнь» (Spock-бариста, Kratos-воспитатель, ...)
│       ├── top-list.md          # TOP-5 countdown персонажей / локаций / предметов
│       ├── fun-news.md          # Выдуманные ироничные новости из лора игры (anchor + 1-2 reporters, Avatar v2)
│       ├── streettalk.md        # Vox-pop уличное интервью: 1 репортёр + 3 интервьюируемых, без студии, channel-bug branding (Avatar v2)
│       ├── in-game-pov.md       # POV от первого лица: «ты оказался в ситуации», survival-мануал + живой HUD-счётчик %, исход — выжил/погиб
│       ├── redcon.md            # Alternate-universe divergence: персонаж в точке расхождения лора, нарративный монолог
│       ├── wild-documentary.md  # Дикая природа: существа из игры как реальные животные, закадровый голос натуралиста, hidden-camera стиль
│       ├── special-report.md   # Спецрепортаж: 1 репортёр, 3 локации, единая история — репортёр сбоку кадра показывает улики
│       └── fake-ad.md          # Фейковая реклама: абсурдный рекламный ролик с обязательным твистом в конце
│
├── games/
│   ├── mlbb/
│   │   ├── mlbb.md             # Конфиг игры
│   │   └── news_special.md     # News overrides для MLBB
│   ├── roblox/
│   │   ├── roblox.md
│   │   └── serial-drama_special.md
│   ├── oxide/
│   │   └── oxide.md
│   ├── kekele/
│   │   └── kekele.md
│   ├── growtopia/
│   │   └── growtopia.md         # Конфиг игры (pixel-art sandbox; рефы — TODO, парсер)
│   ├── marvel-snap/
│   │   ├── gameplay/
│   │   └── reddit-story_bible.json
│   ├── genshin-impact/
│   │   ├── genshin-impact.md
│   │   └── assets/
│   ├── wwe-champions/
│   │   ├── wwe-champions.md
│   │   └── fun-news_story_bible.json
│   └── star-trek-timelines/
│       ├── star-trek-timelines.md
│       ├── streettalk_story_bible.json
│       ├── serial-drama_special.md
│       └── top-list_special.md
│
├── tools/
│   ├── SCRIPTS.md              # Справочник всех скриптов пайплайна (назначение, аргументы, подводные камни)
│   ├── add_subtitles.py        # ASS субтитры через Whisper (вызывается editor-агентом)
│   ├── overlays.py             # drawtext фильтры для FFmpeg (вызывается editor-агентом)
│   ├── gen-character-cards.sh  # Батч-генерация character sheets (NB2)
│   ├── upload-voice-refs.sh    # Загрузка ElevenLabs voice refs в Supabase
│   ├── fal-ai.md               # fal.ai API reference
│   └── ffmpeg-api.md           # FFmpeg Cloud API reference
│
├── music/
│   └── tracks.json
│
└── queue/
    ├── add-task.sh
    ├── check-queue.sh
    ├── update-task.sh
    └── upload-asset.sh
```
