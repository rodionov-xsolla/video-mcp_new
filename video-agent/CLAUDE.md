# CLAUDE.md — Video Production Agent

## Что это

AI Video Production Agent — автономный pipeline для создания коротких вертикальных видео (1080×1920) для игровых каналов. Работает через SJinn AI API + FFmpeg.

## Обязательный порядок работы

**Перед любой генерацией** прочитай все правила:

1. `rules/main.md` — workflow, 6 фаз pipeline
2. `rules/storyboard.md` — правила сценария, промптинг, анти-паттерны
3. `rules/consistency.md` — визуальная консистентность, chain reference
4. `rules/fallback.md` — обработка ошибок
5. `providers.json` — активные провайдеры и модели
6. `games/{GAME_TAG}.md` — конфиг конкретной игры

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

## Добавление игры

Создай `games/{tag}.md` с секциями:
- Visual Style Guide (палитра, освещение, prompt prefix)
- Character Prompt Blocks (минимум 8 визуальных деталей на персонажа)
- Tone of Voice
- Идеи контента
- Референсные изображения (URL-ы)
