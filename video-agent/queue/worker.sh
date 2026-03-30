#!/bin/bash
# worker.sh — автономный воркер для видео-очереди
# Запуск: ./worker.sh
# Остановка: Ctrl+C
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$SCRIPT_DIR/worker.log"
POLL_INTERVAL=30        # секунд между проверками очереди
TASK_TIMEOUT=2400       # 40 минут максимум на одну задачу
COOLDOWN_AFTER_TASK=5   # секунд после завершения задачи

# macOS не имеет timeout — используем gtimeout из coreutils
if command -v timeout &>/dev/null; then
  TIMEOUT_CMD="timeout"
elif command -v gtimeout &>/dev/null; then
  TIMEOUT_CMD="gtimeout"
else
  echo "ERROR: timeout/gtimeout not found. Install: brew install coreutils"
  exit 1
fi

# Загружаем .env
if [ -f "$AGENT_DIR/.env" ]; then
  set -a
  source "$AGENT_DIR/.env"
  set +a
fi

# Проверяем обязательные переменные
for VAR in FAL_KEY SUPABASE_URL SUPABASE_ANON_KEY; do
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

  # Определяем формат по ключевым словам
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

  # Создаём output директорию
  DATE_DIR=$(date +%Y-%m-%d)
  OUTPUT_DIR="$AGENT_DIR/output/${DATE_DIR}/${GAME_TAG}/${FORMAT}"
  mkdir -p "$OUTPUT_DIR/scenes/refs"

  log "    Output: $OUTPUT_DIR"

  # Запускаем Claude с полным промптом pipeline
  PROMPT="Ты — Video Production Agent. Выполни полный pipeline для создания видео.

ЗАДАЧА ИЗ ОЧЕРЕДИ:
- task_id: ${TASK_ID}
- game_tag: ${GAME_TAG}
- idea: ${IDEA}
- format: ${FORMAT}
- output_dir: ${OUTPUT_DIR}

ОБЯЗАТЕЛЬНЫЙ ПОРЯДОК:
1. Прочитай rules/main/workflow.md, rules/main/storyboard.md, rules/main/budgets.md, rules/main/fallback.md
2. Прочитай providers.json
3. Прочитай tools-файлы активных провайдеров (tools/fal-ai.md, tools/ffmpeg-api.md)
4. Прочитай games/${GAME_TAG}/${GAME_TAG}.md
5. Прочитай rules/formats/${FORMAT}.md — правила формата
6. Если есть games/${GAME_TAG}/${FORMAT}_special.md — прочитай его тоже
7. Создай storyboard.json в ${OUTPUT_DIR}/
8. Выполни все 6 фаз pipeline
9. Загрузи final.mp4 в Supabase Storage (bucket: videos, path: videos/${GAME_TAG}/${DATE_DIR}_final.mp4)
10. Обнови статус задачи: bash ${SCRIPT_DIR}/update-task.sh ${TASK_ID} completed <VIDEO_URL>

ПРИ ОШИБКЕ:
- bash ${SCRIPT_DIR}/update-task.sh ${TASK_ID} failed \"описание ошибки\"

КРИТИЧЕСКИЕ ПРАВИЛА:
- Модель генерации определяется файлом формата (rules/formats/${FORMAT}.md)
- СНАЧАЛА storyboard.json, ПОТОМ генерация
- Используй ОДНУ модель анимации для ВСЕХ сцен видео
- camera_angle РАЗНЫЙ для соседних сцен
- Склейка через hard cut (concat), НЕ crossfade
- Минимум 2 действия в каждом клипе
- Последовательная генерация с валидацией размера файла
- Сохрани все файлы в ${OUTPUT_DIR}/ (сцены в scenes/scene-N/, refs в scenes/refs/)
- Финальное видео: ${OUTPUT_DIR}/final.mp4
- ОБЯЗАТЕЛЬНО покажи отчёт о стоимости после генерации"

  # Переходим в директорию агента (claude -p использует относительные пути)
  cd "$AGENT_DIR"

  # Запускаем Claude CLI с таймаутом
  log "    Launching Claude pipeline..."
  START_TIME=$(date +%s)

  CLAUDE_LOG="$OUTPUT_DIR/claude.log"
  if env -u CLAUDECODE stdbuf -oL $TIMEOUT_CMD "$TASK_TIMEOUT" claude -p "$PROMPT" --allowedTools '*' --permission-mode bypassPermissions --verbose < /dev/null >> "$CLAUDE_LOG" 2>&1; then
    END_TIME=$(date +%s)
    DURATION=$(( END_TIME - START_TIME ))
    log "<<< TASK COMPLETED in ${DURATION}s: $TASK_ID"
    log "    Claude log: $CLAUDE_LOG"
  else
    EXIT_CODE=$?
    END_TIME=$(date +%s)
    DURATION=$(( END_TIME - START_TIME ))

    if [ "$EXIT_CODE" = "124" ]; then
      log "!!! TASK TIMEOUT after ${TASK_TIMEOUT}s: $TASK_ID"
      "$SCRIPT_DIR/update-task.sh" "$TASK_ID" failed "Worker timeout after ${TASK_TIMEOUT}s" >> "$LOG_FILE" 2>&1
    else
      log "!!! TASK FAILED (exit $EXIT_CODE) after ${DURATION}s: $TASK_ID"
      "$SCRIPT_DIR/update-task.sh" "$TASK_ID" failed "Claude process exited with code $EXIT_CODE" >> "$LOG_FILE" 2>&1
    fi
    log "    Claude log: $CLAUDE_LOG"
  fi

  log "--- Cooling down ${COOLDOWN_AFTER_TASK}s ---"
  sleep "$COOLDOWN_AFTER_TASK"
done

log "=== Video Worker Stopped ==="
