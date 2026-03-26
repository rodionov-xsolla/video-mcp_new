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
if [ -z "${FAL_KEY:-}" ]; then
  echo "ERROR: FAL_KEY is not set"
  echo "Add it to .env: FAL_KEY=your-key-here"
  exit 1
fi

# SJINN_API_KEY опционален (fallback)
# FFMPEG_API_KEY опционален (используем локальный ffmpeg по умолчанию)

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

claude --permission-mode bypassPermissions -p "
Ты — Video Production Agent. Создай вертикальное видео (1080×1920) для игры ${GAME_TAG}.

Идея: ${IDEA}

Правила:
- Прочитай rules/main.md, rules/storyboard.md, rules/consistency.md и rules/fallback.md
- Прочитай providers.json чтобы определить активных провайдеров
- Прочитай tools-файлы активных провайдеров (tools/fal-ai.md, tools/ffmpeg-api.md и т.д.)
- Прочитай games/${GAME_TAG}.md (если есть) или возьми данные из Google Sheets
- ОБЯЗАТЕЛЬНО: сначала напиши полный сторибоард (storyboard.json), потом генерируй

ФОРМАТ НОВОСТЕЙ:
- Если идея содержит 'новости', 'news', 'game news', 'weekly news', 'patch recap' — это формат News
- Прочитай rules/news.md — правила новостного формата
- ФАЗА 0.5: Используй WebSearch для поиска 3 актуальных новостей об игре. Сохрани research.json
- 3 сцены: студия (ведущий) → поле (репортёр) → студия (ведущий). Все 8s Veo3 T2V
- Два character reference: anchor + reporter. Бюджет: \$10

КРИТИЧЕСКИЕ ПРАВИЛА:
- Речь → Veo3 T2V (включи ТОЧНЫЙ текст character_speech в prompt — модель генерирует голос + липсинк)
- Без речи → Kling 2.6 Pro I2V (НЕ включай текст речи в prompt)
- Используй ОДНУ модель анимации для ВСЕХ сцен одного типа
- camera_angle РАЗНЫЙ для каждой соседней сцены (close-up → wide → low angle)
- Склейка через hard cut (concat), НЕ crossfade
- Изображения через Nano Banana 2 (fal-ai/nano-banana-2/edit) с image_urls для chain reference

- Сохрани все файлы в ${OUTPUT_DIR}/
- Залей финальное видео в Supabase Storage
- Запиши лог в таблицу video_agent_runs

Бюджет:
- Approach 1 (Ken Burns): до \$2
- Approach 2 (I2V): до \$5
- Approach 3 (T2V): до \$10
"
