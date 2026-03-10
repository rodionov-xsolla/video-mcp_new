#!/bin/bash
set -euo pipefail

# Определяем директорию скрипта (Fix #5)
cd "$(dirname "$0")"

# Загружаем .env если есть
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

GAME_TAG="${1:?Usage: ./run.sh GAME_TAG \"idea\"}"
IDEA="${2:?Usage: ./run.sh GAME_TAG \"idea\"}"

# Проверяем API ключи (обязательные)
if [ -z "${SJINN_API_KEY:-}" ]; then
  echo "ERROR: SJINN_API_KEY is not set"
  echo "Add it to .env: SJINN_API_KEY=your-key-here"
  exit 1
fi

if [ -z "${FFMPEG_API_KEY:-}" ]; then
  echo "ERROR: FFMPEG_API_KEY is not set"
  echo "Add it to .env: FFMPEG_API_KEY=your-base64-key-here"
  exit 1
fi

# FAL_KEY опционален (на будущее)
# if [ -z "${FAL_KEY:-}" ]; then
#   echo "WARNING: FAL_KEY is not set"
# fi

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
- Прочитай rules/main.md, rules/storyboard.md, rules/consistency.md и rules/fallback.md
- Прочитай providers.json чтобы определить активных провайдеров
- Прочитай tools-файлы активных провайдеров (tools/sjinn.md, tools/fal-ai.md, tools/ffmpeg-api.md и т.д.)
- Прочитай games/${GAME_TAG}.md (если есть) или возьми данные из Google Sheets
- ОБЯЗАТЕЛЬНО: сначала напиши полный сторибоард (storyboard.json), потом генерируй

КРИТИЧЕСКИЕ ПРАВИЛА:
- В motion_prompt для I2V ОБЯЗАТЕЛЬНО включи ТОЧНЫЙ текст character_speech (модель сама сделает голос и липсинк)
- Используй ОДНУ I2V модель для ВСЕХ сцен (не смешивай Grok и Veo3)
- camera_angle РАЗНЫЙ для каждой соседней сцены (close-up → wide → low angle)
- Склейка через hard cut (concat), НЕ crossfade
- TTS НЕ используется — голос генерится I2V моделью

- Сохрани все файлы в ${OUTPUT_DIR}/
- Залей финальное видео в Supabase Storage
- Запиши лог в таблицу video_agent_runs

Бюджет:
- Approach 1 (Ken Burns): до \$2
- Approach 2 (I2V): до \$5
- Approach 3 (T2V): до \$10
"
