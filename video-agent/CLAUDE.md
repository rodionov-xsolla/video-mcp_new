# CLAUDE.md — Video Production Agent

## Что это

AI Video Production Agent — автономный pipeline для создания коротких вертикальных видео (1080×1920) для игровых каналов. Работает через SJinn AI API + FFmpeg.

## Обязательный порядок работы

**Перед любой генерацией** прочитай все правила:

1. `rules/main.md` — workflow, 6 фаз pipeline
2. `rules/storyboard.md` — правила сценария, промптинг, анти-паттерны
3. `rules/consistency.md` — визуальная консистентность, chain reference
4. `rules/fallback.md` — обработка ошибок
5. `rules/dual-style.md` — правила dual-style видео (если применимо)
6. `providers.json` — активные провайдеры и модели
7. `games/{GAME_TAG}.md` — конфиг конкретной игры

**НИКОГДА не генерируй визуал без готового `storyboard.json`.**

## Критические правила

- **Действие + фраза вместе** в motion_prompt: `[действие] and says: "[реплика]"` — НЕ выноси речь в конец отдельным блоком
- **Максимум 2 фокусные точки** в одном 9:16 кадре
- **camera_angle РАЗНЫЙ** для каждого соседнего клипа
- **Минимум 2 действия** в каждом 8-сек клипе
- **gaze_direction обязателен** при 2+ персонажах в кадре
- **Одна I2V модель** для всех сцен видео (не смешивай Grok и Veo3)
- **Живые описания персонажей** — кожа, шрамы, борода, грязь (не абстрактные "armored man")
- **Последовательная генерация I2V** — по одному клипу, с валидацией размера файла на дубли

## Текущий стек (MVP)

- **Провайдер изображений:** SJinn (Nano Banana Pro) — 150 кредитов/изображение
- **Провайдер видео:** SJinn (Veo3 I2V → Grok I2V fallback)
- **FFmpeg:** локальный `/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg`
- **TTS:** не используется — голос генерируется I2V моделью через motion_prompt

## API

### SJinn AI (основной)
- Создание: `POST https://sjinn.ai/api/un-api/create_tool_task`
- Статус: `POST https://sjinn.ai/api/un-api/query_tool_task_status`
- Auth: `Authorization: Bearer $SJINN_API_KEY`
- **Внимание:** SJinn возвращает невалидный JSON с `\!` и `\?` — используй grep вместо jq для парсинга

### Модели
| Модель | tool_type | Кредиты |
|--------|-----------|---------|
| Nano Banana Pro (image) | `nano-banana-image-pro-api` | 150 |
| Veo3 I2V (video) | `veo3-image-to-video-fast-api` | 420 |
| Grok I2V (video) | `grok-image-to-video-api` | duration × 50 |

### FFmpeg
- Локальный: `/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg`
- Масштабирование: `scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2`
- Склейка: hard cut через `concat`, без crossfade

## Структура output

```
output/{TIMESTAMP}_{Game}_{slug}/
├── storyboard.json       # Сценарий (ОБЯЗАТЕЛЬНО первым)
├── generate.sh           # Воспроизводимый скрипт генерации
├── scene-{K}.png         # Сгенерированные кадры
├── scene-{K}.mp4         # I2V анимация
├── scene-{K}-scaled.mp4  # 1080×1920
└── final.mp4             # Финальное видео
```

## Очередь задач

Система автоматической обработки задач через Supabase.

**Таблица:** `video_tasks` (Supabase) — статусы: pending → running → completed/failed

**Скрипты:**
- `queue/worker.sh` — автоворкер, проверяет очередь каждые 30 сек, таймаут 25 мин, вызывает `claude -p`
- `queue/check-queue.sh` — проверка + атомарный claim задачи
- `queue/update-task.sh` — обновление статуса: `./update-task.sh <task_id> completed <url>`
- `queue/add-task.sh` — добавление задачи: `./add-task.sh "Game" "Idea" [priority]`

**Google Sheets:** задачи добавляются через таблицу, Apps Script отправляет в Supabase. Инструкция в `queue/google-sheets-setup.md`.

**Supabase Storage:** bucket `videos` (public), путь: `videos/{GAME_TAG}/{TIMESTAMP}_final.mp4`

## Ассеты персонажей (game_assets)

Централизованный каталог персонажей, prompt blocks и референсных изображений.

**Таблица:** `game_assets` (Supabase)
- `game_tag` — игра (MLBB, Oxide, Kekele)
- `character_name` — имя персонажа (nullable — для скриншотов/промо без привязки к персонажу)
- `asset_type` — тип: `reference_image`, `character_card`, `screenshot`, `promo_art`, `generated_ref`
- `url` — публичный URL изображения (nullable — для записей только с prompt_block)
- `prompt_block` — готовый промпт для вставки в visual_identity
- `tags` — теги для фильтрации (role, gender, style)
- **UNIQUE constraint:** `(game_tag, character_name, asset_type)` — дубли невозможны

**Использование в pipeline (Фаза 0):**
```
GET /rest/v1/game_assets?game_tag=eq.{GAME_TAG}&select=*
```
- Если есть `reference_image` → пропустить Фазу 2 (Character Reference)
- Если есть `prompt_block` → использовать как `character_description`

**Скрипты:**
- `queue/upload-asset.sh` — загрузка файла + регистрация в БД (требует SUPABASE_SERVICE_ROLE_KEY)
- Google Sheets интеграция: `queue/google-sheets-assets-setup.md`

## Добавление игры

Создай `games/{tag}.md` с секциями:
- Visual Style Guide (палитра, освещение, prompt prefix)
- Character Prompt Blocks (минимум 8 визуальных деталей на персонажа)
- Tone of Voice
- Идеи контента
- Референсные изображения (URL-ы)

## TODO (требует доработки)

- [ ] **Фаза 0:** автоматический запрос game_assets в pipeline (сейчас описан в rules, но не реализован в worker)
- [ ] **Фаза 6:** логирование в `video_agent_runs` (таблица создана, INSERT не реализован)
- [ ] **fal.ai + Kling:** переход с SJinn на fal.ai как основной I2V провайдер
- [ ] **Game configs:** создать `games/ark.md` и `games/pubg.md`
- [ ] **Dual-style для MLBB:** добавить cartoon + realistic блоки персонажей
- [ ] **SUPABASE_SERVICE_ROLE_KEY:** добавить в `.env` для `upload-asset.sh`
- [ ] **Cost tracking:** персистентный подсчёт стоимости генераций
