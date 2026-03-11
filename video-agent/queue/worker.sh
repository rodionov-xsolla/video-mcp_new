#!/bin/bash
# worker.sh — автономный воркер для видео-очереди
# Запуск: ./worker.sh
# Остановка: Ctrl+C
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$SCRIPT_DIR/worker.log"
POLL_INTERVAL=30        # секунд между проверками очереди
TASK_TIMEOUT=900        # 15 минут максимум на одну задачу
COOLDOWN_AFTER_TASK=5   # секунд после завершения задачи

# Загружаем .env
if [ -f "$AGENT_DIR/.env" ]; then
  set -a
  source "$AGENT_DIR/.env"
  set +a
fi

# Проверяем обязательные переменные
for VAR in SJINN_API_KEY SUPABASE_URL SUPABASE_ANON_KEY; do
  if [ -z "${!VAR:-}" ]; then
    echo "ERROR: $VAR is not set in .env"
    exit 1
  fi
done

# Graceful shutdown
RUNNING=true
trap 'echo ""; log "Shutting down worker..."; RUNNING=false' INT TERM

log() {
  local MSG="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
  echo "$MSG"
  echo "$MSG" >> "$LOG_FILE"
}

log "=== Video Worker Started ==="
log "Agent dir: $AGENT_DIR"
log "Poll interval: ${POLL_INTERVAL}s"
log "Task timeout: ${TASK_TIMEOUT}s"

while $RUNNING; do
  # Проверяем очередь
  QUEUE_OUTPUT=$("$SCRIPT_DIR/check-queue.sh" 2>&1) || true

  if echo "$QUEUE_OUTPUT" | grep -q "NO_PENDING_TASKS"; then
    sleep "$POLL_INTERVAL"
    continue
  fi

  if ! echo "$QUEUE_OUTPUT" | grep -q "TASK_FOUND"; then
    log "WARNING: unexpected queue output: $QUEUE_OUTPUT"
    sleep "$POLL_INTERVAL"
    continue
  fi

  # Парсим задачу
  TASK_ID=$(echo "$QUEUE_OUTPUT" | grep '^task_id=' | cut -d'=' -f2)
  GAME_TAG=$(echo "$QUEUE_OUTPUT" | grep '^game_tag=' | cut -d'=' -f2)
  IDEA=$(echo "$QUEUE_OUTPUT" | grep '^idea=' | cut -d'=' -f2-)

  log ">>> TASK FOUND: $TASK_ID"
  log "    Game: $GAME_TAG"
  log "    Idea: $IDEA"

  # Создаём output директорию
  TIMESTAMP=$(date +%Y-%m-%d_%H-%M)
  SLUG=$(echo "$IDEA" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-' | head -c 30)
  OUTPUT_DIR="$AGENT_DIR/output/${TIMESTAMP}_${GAME_TAG}_${SLUG}"
  mkdir -p "$OUTPUT_DIR"

  log "    Output: $OUTPUT_DIR"

  # Запускаем Claude с полным промптом pipeline
  PROMPT="Ты — Video Production Agent. Выполни полный pipeline для создания видео.

ЗАДАЧА ИЗ ОЧЕРЕДИ:
- task_id: ${TASK_ID}
- game_tag: ${GAME_TAG}
- idea: ${IDEA}
- output_dir: ${OUTPUT_DIR}

ОБЯЗАТЕЛЬНЫЙ ПОРЯДОК:
1. Прочитай ВСЕ правила: rules/main.md, rules/storyboard.md, rules/consistency.md, rules/fallback.md
2. Прочитай providers.json
3. Прочитай games/${GAME_TAG}.md (если есть)
4. Если видео dual-style — прочитай rules/dual-style.md
5. Создай storyboard.json в ${OUTPUT_DIR}/
6. Выполни все 6 фаз pipeline (image gen → I2V → FFmpeg assembly)
7. Загрузи final.mp4 в Supabase Storage (bucket: videos, path: videos/${GAME_TAG}/${TIMESTAMP}_final.mp4)
8. Обнови статус задачи: bash ${SCRIPT_DIR}/update-task.sh ${TASK_ID} completed <VIDEO_URL>

ПРИ ОШИБКЕ:
- bash ${SCRIPT_DIR}/update-task.sh ${TASK_ID} failed \"описание ошибки\"

КРИТИЧЕСКИЕ ПРАВИЛА:
- СНАЧАЛА storyboard.json, ПОТОМ генерация
- В motion_prompt ОБЯЗАТЕЛЬНО включи ТОЧНЫЙ текст character_speech
- Используй ОДНУ I2V модель для ВСЕХ сцен
- camera_angle РАЗНЫЙ для соседних сцен
- Склейка через hard cut (concat), НЕ crossfade
- Минимум 2 действия в каждом 8-сек клипе
- Последовательная генерация I2V с валидацией размера файла"

  # Переходим в директорию агента (claude -p использует относительные пути)
  cd "$AGENT_DIR"

  # Запускаем Claude CLI с таймаутом
  log "    Launching Claude pipeline..."
  START_TIME=$(date +%s)

  if timeout "$TASK_TIMEOUT" claude -p "$PROMPT" --verbose 2>&1 | tee -a "$LOG_FILE"; then
    END_TIME=$(date +%s)
    DURATION=$(( END_TIME - START_TIME ))
    log "<<< TASK COMPLETED in ${DURATION}s: $TASK_ID"
  else
    EXIT_CODE=$?
    END_TIME=$(date +%s)
    DURATION=$(( END_TIME - START_TIME ))

    if [ "$EXIT_CODE" = "124" ]; then
      log "!!! TASK TIMEOUT after ${TASK_TIMEOUT}s: $TASK_ID"
      "$SCRIPT_DIR/update-task.sh" "$TASK_ID" failed "Worker timeout after ${TASK_TIMEOUT}s" 2>&1 | tee -a "$LOG_FILE"
    else
      log "!!! TASK FAILED (exit $EXIT_CODE) after ${DURATION}s: $TASK_ID"
      "$SCRIPT_DIR/update-task.sh" "$TASK_ID" failed "Claude process exited with code $EXIT_CODE" 2>&1 | tee -a "$LOG_FILE"
    fi
  fi

  log "--- Cooling down ${COOLDOWN_AFTER_TASK}s ---"
  sleep "$COOLDOWN_AFTER_TASK"
done

log "=== Video Worker Stopped ==="
