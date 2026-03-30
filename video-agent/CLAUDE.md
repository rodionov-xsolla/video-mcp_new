# CLAUDE.md — Video Production Agent

## Что это

AI Video Production Agent — автономный pipeline для создания коротких вертикальных видео (1080×1920) для игровых каналов. Работает через fal.ai API + FFmpeg.

## Обязательный порядок работы

### Всегда загружай (core rules):

1. `rules/main/workflow.md` — workflow, 6 фаз pipeline
2. `rules/main/storyboard.md` — правила сценария, промптинг, анти-паттерны, консистентность
3. `rules/main/budgets.md` — бюджеты и прайсинг
4. `rules/main/fallback.md` — обработка ошибок
5. `providers.json` — активные провайдеры и модели
6. `games/{GAME_TAG}/{GAME_TAG}.md` — конфиг конкретной игры

### Загрузка формата (ТОЛЬКО релевантный):

Определи формат по идее/промпту:

| Ключевые слова | Формат | Файл |
|---|---|---|
| "news", "новости", "game news", "patch recap", "обновление" | News | `rules/formats/news.md` |
| "serial", "episode", "series", "сериал" | Serial Drama | `rules/formats/serial-drama.md` |
| "object character", "talking object", "антропоморф" | Object Character | `rules/formats/object-character.md` |
| "dual-style", "game vs reality" | Dual-style | `rules/formats/dual-style.md` |
| "gameplay ai avatar", "ai avatar", "talking head", "offerwall", "offer", "оффер" | Gameplay AI Avatar | `rules/formats/gameplay-ai-avatar.md` |
| "dance battle", "dance", "танцевальный батл", "танец", "dance off" | Dance Battle | `rules/formats/dance-battle.md` |
| Всё остальное | Standard | `rules/formats/standard.md` |

Если есть game-specific файл для формата: `games/{GAME_TAG}/{format}_special.md` → загрузи его тоже.

**НЕ загружай файлы форматов, не относящихся к задаче.**

**Модель генерации определяется файлом формата.**

**НИКОГДА не генерируй визуал без готового `storyboard.json`.**

## Критические правила

- **Действие + фраза вместе** в motion_prompt: `[действие] and says: "[реплика]"` (только для моделей с генерацией голоса)
- **Максимум 2 фокусные точки** в одном 9:16 кадре
- **camera_angle РАЗНЫЙ** для каждого соседнего клипа
- **Минимум 2 действия** в каждом клипе (5 или 10 сек)
- **gaze_direction обязателен** при 2+ персонажах в кадре
- **Одна модель анимации** для всех сцен видео (не смешивай модели в одном ролике)
- **Живые описания персонажей** — кожа, шрамы, борода, грязь (не абстрактные "armored man")
- **Последовательная генерация** — по одному клипу, с валидацией размера файла
- **НЕТ активных действий в Kling I2V** — только микро-движения: поворот головы, жест рукой, смена выражения лица

## Текущий стек

- **Провайдер изображений:** fal.ai (Nano Banana 2) — ~$0.04/изображение
- **Провайдер видео I2V:** fal.ai (Kling 2.6 Pro) — $0.14/сек (с аудио)
- **Провайдер видео T2V:** fal.ai (Veo3) — $0.20-$0.40/сек
- **FFmpeg:** локальный `/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg`
- **TTS:** Kokoro TTS (fal.ai) — для форматов, использующих отдельную озвучку
- **Lipsync:** Kling Lipsync (fal.ai) — синхронизация речи с видео

### Форматы видео

| Формат | Описание | Файл правил |
|--------|----------|-------------|
| Standard | I2V/T2V для экшена, стендапов, гайдов | `rules/formats/standard.md` |
| Dual-style | Cartoon + realistic рядом | `rules/formats/dual-style.md` |
| News | Новости: ведущий в студии + репортёр | `rules/formats/news.md` |
| Object Character | Антропоморфные объекты с монологом | `rules/formats/object-character.md` |
| Serial Drama | Сериальные микро-драмы с brainrot | `rules/formats/serial-drama.md` |
| Gameplay AI Avatar | Говорящая голова + геймплей, продвижение офферов | `rules/formats/gameplay-ai-avatar.md` |
| Dance Battle | Комедийные танцевальные батлы двух персонажей | `rules/formats/dance-battle.md` |

## API

### fal.ai (основной)
- Auth: `Authorization: Key $FAL_KEY`
- Base URL: `https://queue.fal.run/`
- Подробности: `tools/fal-ai.md`

### Модели
| Модель | Endpoint | Стоимость |
|--------|----------|-----------|
| Nano Banana 2 (image) | `fal-ai/nano-banana-2/edit` | ~$0.04 |
| Kling 2.6 Pro I2V (video+audio) | `fal-ai/kling-video/v2.6/pro/image-to-video` | $0.14/сек |
| Veo3 T2V (video + voice) | `fal-ai/veo3` | $0.20-$0.40/сек |
| Kokoro TTS (voice) | `fal-ai/kokoro/american-english` | ~$0.02/запрос |
| Kling Lipsync (lip sync) | `fal-ai/kling-video/lipsync/audio-to-video` | ~$0.10/сек |
| HeyGen Avatar IV (avatar+voice) | `fal-ai/heygen/avatar4/image-to-video` | $0.10/сек |
| Kling Avatar v2 Standard (avatar) | `fal-ai/kling-video/ai-avatar/v2/standard` | $0.056/сек |

### FFmpeg
- Локальный: `/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg`
- Подробности: `tools/ffmpeg-api.md`

## Структура output

```
output/YYYY-MM-DD/{GAME_TAG}/{format_slug}/
├── storyboard.json       # Сценарий (ОБЯЗАТЕЛЬНО первым)
├── scenes/
│   ├── refs/
│   │   └── character-ref.png
│   ├── scene-1/
│   │   ├── scene-1.png
│   │   ├── scene-1.mp4
│   │   └── scene-1-scaled.mp4
│   └── scene-2/ ...
└── final.mp4             # Финальное видео
```

## Очередь задач

Система автоматической обработки задач через Supabase.

**Таблица:** `video_tasks` (Supabase) — статусы: pending → running → completed/failed

**Скрипты:**
- `queue/worker.sh` — автоворкер, проверяет очередь каждые 30 сек
- `queue/check-queue.sh` — проверка + атомарный claim задачи
- `queue/update-task.sh` — обновление статуса
- `queue/add-task.sh` — добавление задачи

**Supabase Storage:** bucket `videos` (public), путь: `videos/{GAME_TAG}/{TIMESTAMP}_final.mp4`

## Ассеты персонажей (game_assets)

**Таблица:** `game_assets` (Supabase)
- `game_tag`, `character_name`, `asset_type`, `url`, `prompt_block`, `tags`
- **UNIQUE constraint:** `(game_tag, character_name, asset_type)`

**Использование в pipeline (Фаза 0):**
```
GET /rest/v1/game_assets?game_tag=eq.{GAME_TAG}&select=*
```

## Добавление игры

Создай `games/{tag}/{tag}.md` с секциями:
- Visual Style Guide (палитра, освещение, prompt prefix)
- Character Prompt Blocks (минимум 8 визуальных деталей на персонажа)
- Tone of Voice
- Музыка

Если нужны специальные настройки формата — создай `games/{tag}/{format}_special.md`.

## TODO

- [ ] **Фаза 0:** автоматический запрос game_assets в pipeline
- [ ] **Фаза 6:** логирование в `video_agent_runs`
- [ ] **Game configs:** создать `games/ark/ark.md` и `games/pubg/pubg.md`
- [ ] **Cost tracking:** персистентный подсчёт стоимости генераций
