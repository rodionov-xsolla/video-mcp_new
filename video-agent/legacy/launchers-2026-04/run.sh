#!/bin/bash
set -euo pipefail

# Определяем директорию скрипта
cd "$(dirname "$0")"

# Загружаем .env если есть
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

GAME_TAG="${1:?Usage: ./run.sh GAME_TAG \"idea\" [format]}"
IDEA="${2:?Usage: ./run.sh GAME_TAG \"idea\" [format]}"
FORMAT="${3:-auto}"

# Проверяем API ключи (обязательные)
if [ -z "${FAL_KEY:-}" ]; then
  echo "ERROR: FAL_KEY is not set"
  echo "Add it to .env: FAL_KEY=your-key-here"
  exit 1
fi

# Auto-detect формата по ключевым словам
if [ "$FORMAT" = "auto" ]; then
  IDEA_LOWER=$(echo "$IDEA" | tr '[:upper:]' '[:lower:]')
  if echo "$IDEA_LOWER" | grep -qE 'news|новости|game news|patch recap|обновление'; then
    FORMAT="news"
  elif echo "$IDEA_LOWER" | grep -qE 'serial|episode|series|сериал|ep[0-9]'; then
    FORMAT="serial-drama"
  elif echo "$IDEA_LOWER" | grep -qE 'object character|talking object|антропоморф'; then
    FORMAT="object-character"
  elif echo "$IDEA_LOWER" | grep -qE 'dual-style|game vs reality|cartoon.*realistic'; then
    FORMAT="dual-style"
  else
    FORMAT="standard"
  fi
fi

# Output: output/YYYY-MM-DD/GAME_TAG/format/
DATE_DIR=$(date +%Y-%m-%d)
OUTPUT_DIR="output/${DATE_DIR}/${GAME_TAG}/${FORMAT}"
mkdir -p "$OUTPUT_DIR/scenes/refs"

echo "=== Video Production Agent ==="
echo "Game:   $GAME_TAG"
echo "Idea:   $IDEA"
echo "Format: $FORMAT"
echo "Output: $OUTPUT_DIR"
echo "=============================="

claude --permission-mode bypassPermissions -p "
Ты — Video Production Agent. Создай вертикальное видео (1080×1920) для игры ${GAME_TAG}.

Идея: ${IDEA}
Формат: ${FORMAT}

Правила:
- Прочитай rules/main/workflow.md, rules/main/storyboard.md, rules/main/budgets.md и rules/main/fallback.md
- Прочитай providers.json чтобы определить активных провайдеров
- Прочитай tools-файлы активных провайдеров (tools/fal-ai.md, tools/ffmpeg-api.md и т.д.)
- Прочитай games/${GAME_TAG}/${GAME_TAG}.md
- Прочитай rules/formats/${FORMAT}.md — правила формата
- Если есть games/${GAME_TAG}/${FORMAT}_special.md — прочитай его тоже
- ОБЯЗАТЕЛЬНО: сначала напиши полный сторибоард (storyboard.json), потом генерируй

КРИТИЧЕСКИЕ ПРАВИЛА:
- Модель генерации определяется файлом формата (rules/formats/${FORMAT}.md)
- Используй ОДНУ модель анимации для ВСЕХ сцен видео
- camera_angle РАЗНЫЙ для каждой соседней сцены (close-up → wide → low angle)
- Склейка через hard cut (concat), НЕ crossfade
- Изображения через Nano Banana 2 (fal-ai/nano-banana-2/edit) с image_urls для chain reference

- Сохрани все файлы в ${OUTPUT_DIR}/ (сцены в scenes/scene-N/, refs в scenes/refs/)
- Финальное видео: ${OUTPUT_DIR}/final.mp4
- Залей финальное видео в Supabase Storage
- ОБЯЗАТЕЛЬНО покажи отчёт о стоимости после генерации
"
