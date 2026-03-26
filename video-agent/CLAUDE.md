# CLAUDE.md — Video Production Agent

## Что это

AI Video Production Agent — автономный pipeline для создания коротких вертикальных видео (1080×1920) для игровых каналов. Работает через fal.ai API + FFmpeg.

## Обязательный порядок работы

**Перед любой генерацией** прочитай все правила:

1. `rules/main.md` — workflow, 6 фаз pipeline
2. `rules/storyboard.md` — правила сценария, промптинг, анти-паттерны
3. `rules/consistency.md` — визуальная консистентность, chain reference
4. `rules/fallback.md` — обработка ошибок
5. `rules/dual-style.md` — правила dual-style видео (если применимо)
5b. `rules/news.md` — правила новостного формата (если идея — новости)
6. `providers.json` — активные провайдеры и модели
7. `games/{GAME_TAG}.md` — конфиг конкретной игры

**НИКОГДА не генерируй визуал без готового `storyboard.json`.**

## Критические правила

- **Действие + фраза вместе** в motion_prompt: `[действие] and says: "[реплика]"` — НЕ выноси речь в конец отдельным блоком (только для Veo3 T2V)
- **Максимум 2 фокусные точки** в одном 9:16 кадре
- **camera_angle РАЗНЫЙ** для каждого соседнего клипа
- **Минимум 2 действия** в каждом клипе (5 или 10 сек)
- **gaze_direction обязателен** при 2+ персонажах в кадре
- **Одна модель анимации** для всех сцен видео (не смешивай Kling и Veo3 в одном ролике)
- **Живые описания персонажей** — кожа, шрамы, борода, грязь (не абстрактные "armored man")
- **Последовательная генерация** — по одному клипу, с валидацией размера файла на дубли
- **Речь → Veo3 T2V**, без речи → Kling I2V

## Текущий стек

- **Провайдер изображений:** fal.ai (Nano Banana 2) — ~$0.04/изображение
- **Провайдер видео I2V (без речи):** fal.ai (Kling 2.6 Pro) — $0.14/сек (с аудио, generate_audio=true по умолчанию)
- **Провайдер видео T2V (с речью):** fal.ai (Veo3) — $0.20/сек — модель сама генерит голос и липсинк
- **FFmpeg:** локальный `/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg`
- **TTS:** не используется отдельно — Veo3 T2V генерирует голос из текста в промпте
- **Fallback:** SJinn сохранён в providers.json, но не используется по умолчанию

### Форматы видео

| Формат | Описание | Модель | Бюджет |
|--------|----------|--------|--------|
| Стандартный | Списки, экшен, стендап | Approach 1/2/3 | $2-$10 |
| Dual-style | Cartoon + realistic рядом | Approach 2 | $5 |
| **News** | Новости игры: ведущий в студии + репортёр с места событий | Veo3 T2V (3 × 8s) | $10 |

## API

### fal.ai (основной)
- Auth: `Authorization: Key $FAL_KEY`
- Base URL: `https://queue.fal.run/`
- Изображения: `POST /fal-ai/nano-banana-2/edit` (синхронный, `image_urls` для референсов)
- Видео I2V: `POST /fal-ai/kling-video/v2.6/pro/image-to-video` (асинхронный, polling)
- Видео T2V: `POST /fal-ai/veo3` (асинхронный, polling)
- fal.ai возвращает валидный JSON — используй jq для парсинга

### Модели
| Модель | Endpoint | Стоимость |
|--------|----------|-----------|
| Nano Banana 2 (image) | `fal-ai/nano-banana-2/edit` | ~$0.04 |
| Kling 2.6 Pro I2V (video+audio) | `fal-ai/kling-video/v2.6/pro/image-to-video` | $0.14/сек |
| Veo3 T2V (video + voice) | `fal-ai/veo3` | $0.20/сек |

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
- [x] **fal.ai + Kling:** переход с SJinn на fal.ai как основной провайдер (изображения + видео)
- [ ] **Game configs:** создать `games/ark.md` и `games/pubg.md`
- [ ] **Dual-style для MLBB:** добавить cartoon + realistic блоки персонажей
- [x] **News format:** правила, сторибоард, MLBB конфиг (anchor: Lancelot, reporter: Fanny)
- [x] **SUPABASE_SERVICE_ROLE_KEY:** добавлен в `.env`
- [ ] **Cost tracking:** персистентный подсчёт стоимости генераций
