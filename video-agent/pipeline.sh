#!/bin/bash
# pipeline.sh — суб-агентный оркестратор (Этап 3: гибрид).
#
# Phases 0-3 (init, scenarist, storyboarder, animator+sound) — монолитный Claude
#   с инструкцией STOP AFTER PHASE 3 (не запускает Editor / Phase 5 / Phase 6).
# Phase 4 (Editor) — отдельный Claude вызов с фокусированным промптом, опц. Sonnet.
# Phase 5 (upload + git) — Manager в монолитном вызове это уже не делает,
#   делегируем второму проходу монолита (минимальный) или явно через bash.
#   На этапе 3 для простоты — Editor sub-agent сам делает upload (если есть TASK_ID).
#
# Использование:
#   pipeline.sh GAME_TAG "idea" [format] [OUTPUT_DIR] [TASK_ID]
#
# ENV переменные:
#   PIPELINE_EDITOR_MODEL — модель для Editor (default: claude-sonnet-4-6)
#   PIPELINE_LOG          — путь к лог-файлу (default: $OUTPUT_DIR/pipeline.log)
#   PIPELINE_ORCHESTRATOR — codex (default) | claude
#
# Легаси (run.sh, монолитный worker.sh) не трогается. Pipeline опт-ин.

set -uo pipefail

# === Аргументы ===
GAME_TAG="${1:?Usage: pipeline.sh GAME_TAG \"idea\" [format] [OUTPUT_DIR] [TASK_ID]}"
IDEA="${2:?Usage: pipeline.sh GAME_TAG \"idea\" [format] [OUTPUT_DIR] [TASK_ID]}"
FORMAT="${3:-auto}"
OUTPUT_DIR_ARG="${4:-}"
TASK_ID="${5:-}"

# === Setup ===
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Загружаем .env
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

# Проверяем обязательные API ключи
if [ -z "${FAL_KEY:-}" ]; then
  echo "ERROR: FAL_KEY is not set" >&2
  echo "Add it to .env: FAL_KEY=your-key-here" >&2
  exit 1
fi

# === Format auto-detect (как в run.sh / worker.sh) ===
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
  elif echo "$IDEA_LOWER" | grep -qE 'motion dance|motion control|моушн|motion transfer'; then
    FORMAT="motion-dance"
  elif echo "$IDEA_LOWER" | grep -qE 'gameplay ai avatar|ai avatar|talking head|offerwall|оффер|бонус'; then
    FORMAT="gameplay-ai-avatar"
  elif echo "$IDEA_LOWER" | grep -qE 'dance battle|dance off|танцевальный батл'; then
    FORMAT="dance-battle"
  elif echo "$IDEA_LOWER" | grep -qE 'reddit story|storytime|narrated gameplay'; then
    FORMAT="reddit-story"
  elif echo "$IDEA_LOWER" | grep -qE 'character story|история персонажа|лор|lore|backstory'; then
    FORMAT="character-story"
  else
    FORMAT="standard"
  fi
fi

# === Output dir ===
DATE_DIR=$(date +%Y-%m-%d)
if [ -n "$OUTPUT_DIR_ARG" ]; then
  OUTPUT_DIR="$OUTPUT_DIR_ARG"
else
  OUTPUT_DIR="$SCRIPT_DIR/output/${DATE_DIR}/${GAME_TAG}/${FORMAT}"
fi
mkdir -p "$OUTPUT_DIR/scenes/refs"

# === Log ===
LOG_FILE="${PIPELINE_LOG:-$OUTPUT_DIR/pipeline.log}"
log() {
  local MSG="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
  echo "$MSG"
  echo "$MSG" >> "$LOG_FILE"
}

# === Helpers ===
# Default models per role tiering (см. план Этапа 4-5):
#   Scenarist  — Sonnet 4.6 (creative + RU/multilingual content; gap to Opus 1.2% on SWE-bench)
#   Sound      — Haiku 4.5 (mechanical: parse JSON → curl ElevenLabs → save MP3)
#   Storyboarder — Opus 4.7 (chain-ref strategy, expensive errors on NB2)
#   Animator   — Opus 4.7 (Kling errors are $0.28-1.40, judgment matters)
#   Editor     — Sonnet 4.6 (procedural FFmpeg по чек-листу)
PIPELINE_ORCHESTRATOR="${PIPELINE_ORCHESTRATOR:-codex}"
if [ "$PIPELINE_ORCHESTRATOR" = "claude" ]; then
  SCENARIST_MODEL="${PIPELINE_SCENARIST_MODEL:-claude-sonnet-4-6}"
  SOUND_MODEL="${PIPELINE_SOUND_MODEL:-claude-haiku-4-5-20251001}"
  STORYBOARDER_MODEL="${PIPELINE_STORYBOARDER_MODEL:-claude-opus-4-7}"
  ANIMATOR_MODEL="${PIPELINE_ANIMATOR_MODEL:-claude-opus-4-7}"
  EDITOR_MODEL="${PIPELINE_EDITOR_MODEL:-claude-sonnet-4-6}"
else
  SCENARIST_MODEL="${PIPELINE_SCENARIST_MODEL:-}"
  SOUND_MODEL="${PIPELINE_SOUND_MODEL:-}"
  STORYBOARDER_MODEL="${PIPELINE_STORYBOARDER_MODEL:-}"
  ANIMATOR_MODEL="${PIPELINE_ANIMATOR_MODEL:-}"
  EDITOR_MODEL="${PIPELINE_EDITOR_MODEL:-}"
fi

fail_task() {
  local REASON="$1"
  log "!!! $REASON"
  if [ -n "$TASK_ID" ]; then
    "$SCRIPT_DIR/queue/update-task.sh" "$TASK_ID" failed "$REASON" >> "$LOG_FILE" 2>&1 || true
  fi
}

run_subagent() {
  # run_subagent <phase_name> <prompt_file> <model> <log_file> <env_var_assignments...>
  # Interpolates ${VARS} from current env into prompt_file, runs the configured orchestrator.
  local PHASE_NAME="$1"
  local PROMPT_FILE="$2"
  local MODEL="$3"
  local CLAUDE_LOG="$4"
  shift 4

  if [ ! -f "$PROMPT_FILE" ]; then
    fail_task "Prompt file not found: $PROMPT_FILE"
    return 10
  fi

  local PROMPT
  if command -v envsubst >/dev/null 2>&1; then
    PROMPT=$(GAME_TAG="$GAME_TAG" FORMAT="$FORMAT" IDEA="$IDEA" \
             OUTPUT_DIR="$OUTPUT_DIR" TASK_ID="$TASK_ID" \
             LANGUAGE="${LANGUAGE:-en}" \
             OPENER_PATH="${OPENER_PATH:-}" CTA_PATH="${CTA_PATH:-}" \
             MERGED_CONTEXT_PATH="${MERGED_CONTEXT_PATH:-}" \
             EXISTING_REFS_JSON="${EXISTING_REFS_JSON:-}" \
             SUPABASE_ASSETS_FILE="${SUPABASE_ASSETS_FILE:-}" \
             envsubst < "$PROMPT_FILE")
  else
    PROMPT=$(GAME_TAG="$GAME_TAG" FORMAT="$FORMAT" IDEA="$IDEA" \
             OUTPUT_DIR="$OUTPUT_DIR" TASK_ID="$TASK_ID" \
             LANGUAGE="${LANGUAGE:-en}" \
             OPENER_PATH="${OPENER_PATH:-}" CTA_PATH="${CTA_PATH:-}" \
             MERGED_CONTEXT_PATH="${MERGED_CONTEXT_PATH:-}" \
             EXISTING_REFS_JSON="${EXISTING_REFS_JSON:-}" \
             SUPABASE_ASSETS_FILE="${SUPABASE_ASSETS_FILE:-}" \
             python3 - "$PROMPT_FILE" <<'PY'
import os
import re
import sys

text = open(sys.argv[1], encoding="utf-8").read()
pattern = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-(.*?))?\}")

def repl(match):
    value = os.environ.get(match.group(1))
    if value:
        return value
    return match.group(2) or ""

sys.stdout.write(pattern.sub(repl, text))
PY
)
  fi

  local START_T END_T
  START_T=$(date +%s)
  log "    [$PHASE_NAME] launching (${PIPELINE_ORCHESTRATOR}, model: ${MODEL:-default})..."
  local EXIT_CODE
  if [ "$PIPELINE_ORCHESTRATOR" = "codex" ]; then
    local CODEX_CMD=(codex exec -C "$SCRIPT_DIR" --dangerously-bypass-approvals-and-sandbox)
    if [ -n "$MODEL" ]; then
      CODEX_CMD+=("--model" "$MODEL")
    fi
    "${CODEX_CMD[@]}" "$PROMPT" < /dev/null >> "$CLAUDE_LOG" 2>&1
    EXIT_CODE=$?
  else
    if command -v stdbuf >/dev/null 2>&1; then
      env -u CLAUDECODE stdbuf -oL claude -p "$PROMPT" \
         --model "$MODEL" \
         --permission-mode bypassPermissions --verbose \
         < /dev/null >> "$CLAUDE_LOG" 2>&1
      EXIT_CODE=$?
    else
      env -u CLAUDECODE claude -p "$PROMPT" \
         --model "$MODEL" \
         --permission-mode bypassPermissions --verbose \
         < /dev/null >> "$CLAUDE_LOG" 2>&1
      EXIT_CODE=$?
    fi
  fi

  if [ "$EXIT_CODE" -eq 0 ]; then
    END_T=$(date +%s)
    log "    [$PHASE_NAME] completed in $((END_T - START_T))s"
    return 0
  else
    END_T=$(date +%s)
    log "!!! [$PHASE_NAME] FAILED (exit $EXIT_CODE) after $((END_T - START_T))s — log: $CLAUDE_LOG"
    return "$EXIT_CODE"
  fi
}

# === Header ===
log "=== Video Pipeline (full sub-agent mode) ==="
log "Game:         $GAME_TAG"
log "Idea:         $IDEA"
log "Format:       $FORMAT"
log "Output:       $OUTPUT_DIR"
log "Task ID:      ${TASK_ID:-<none>}"
log "Orchestrator: $PIPELINE_ORCHESTRATOR"
log "Scenarist:    $SCENARIST_MODEL"
log "Sound:        $SOUND_MODEL"
log "Storyboarder: $STORYBOARDER_MODEL"
log "Animator:     $ANIMATOR_MODEL"
log "Editor:       $EDITOR_MODEL"
log "============================================="

# === Phase 0: bash init (git pull + Supabase asset bank query) ===
log ">>> PHASE 0: Init (bash, no Claude)"

# git pull (best-effort, не критично если на ветке без upstream)
log "    git pull origin main..."
if git -C "$SCRIPT_DIR" pull --rebase --autostash origin main >> "$LOG_FILE" 2>&1; then
  log "    git pull: OK"
else
  log "    [warn] git pull failed or no upstream; continuing"
fi

MERGED_CONTEXT_PATH="$OUTPUT_DIR/merged-context.md"
log "    build_context.py (optional legacy gate)..."
BUILD_CONTEXT_SCRIPT="$SCRIPT_DIR/tools/build_context.py"
if [ -f "$BUILD_CONTEXT_SCRIPT" ]; then
  if python3 "$BUILD_CONTEXT_SCRIPT" "$GAME_TAG" "$FORMAT" "$OUTPUT_DIR" >> "$LOG_FILE" 2>&1; then
    log "    build_context: OK → $MERGED_CONTEXT_PATH"
  else
    fail_task "build_context.py failed"
    exit 1
  fi
else
  log "    build_context: skipped (script not present in current tool layout)"
fi
export MERGED_CONTEXT_PATH

# Supabase asset bank query — список существующих refs/avatars/openers/CTAs/prompts
SUPABASE_ASSETS_FILE="$OUTPUT_DIR/_supabase-assets.json"
if [ -n "${SUPABASE_URL:-}" ] && [ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  log "    Querying Supabase game_assets for tag=$GAME_TAG..."
  if curl -sf -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
        -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
        "${SUPABASE_URL}/rest/v1/game_assets?game_tag=eq.${GAME_TAG}&select=*" \
        -o "$SUPABASE_ASSETS_FILE" 2>>"$LOG_FILE"; then
    ASSET_COUNT=$(jq 'length' "$SUPABASE_ASSETS_FILE" 2>/dev/null || echo "?")
    log "    Supabase: $ASSET_COUNT assets cached → $SUPABASE_ASSETS_FILE"
  else
    log "    [warn] Supabase query failed; sub-agents will see empty asset bank"
    echo "[]" > "$SUPABASE_ASSETS_FILE"
  fi
else
  log "    [warn] SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing; skipping asset bank query"
  echo "[]" > "$SUPABASE_ASSETS_FILE"
fi
export SUPABASE_ASSETS_FILE

# === Phase 1: Scenarist sub-agent (Sonnet) ===
log ">>> PHASE 1: Scenarist sub-agent"

CLAUDE_LOG_SCEN="$OUTPUT_DIR/claude-scenarist.log"
if ! run_subagent "Scenarist" "$SCRIPT_DIR/prompts/scenarist.txt" "$SCENARIST_MODEL" "$CLAUDE_LOG_SCEN"; then
  fail_task "Scenarist failed"
  exit 1
fi

# Validate storyboard.json
if [ ! -s "$OUTPUT_DIR/storyboard.json" ]; then
  fail_task "storyboard.json missing after Scenarist"
  exit 2
fi
EXPECTED_CLIPS=$(jq '(.clips // .scenes // []) | length' "$OUTPUT_DIR/storyboard.json" 2>/dev/null || echo 0)
if [ "$EXPECTED_CLIPS" = "0" ] || [ -z "$EXPECTED_CLIPS" ]; then
  fail_task "storyboard.json has no clips/scenes array"
  exit 2
fi
DIALOGUE_CLIPS=$(jq '[(.clips // .scenes // [])[] | select(.clip_type == "dialogue" or ((.tts // null) != null and (.tts | type) == "string") or (.tts_segment // null) != null)] | length' "$OUTPUT_DIR/storyboard.json" 2>/dev/null || echo 0)
log "    storyboard.json: $EXPECTED_CLIPS clips ($DIALOGUE_CLIPS dialogue)"

# === Phase 2: Sound sub-agent (Haiku) — TTS BEFORE Animator (Avatar needs audio_url) ===
if [ "$DIALOGUE_CLIPS" -gt 0 ]; then
  log ">>> PHASE 2: Sound sub-agent (TTS for $DIALOGUE_CLIPS dialogue clips)"
  CLAUDE_LOG_SOUND="$OUTPUT_DIR/claude-sound.log"
  if ! run_subagent "Sound" "$SCRIPT_DIR/prompts/sound.txt" "$SOUND_MODEL" "$CLAUDE_LOG_SOUND"; then
    fail_task "Sound failed"
    exit 1
  fi

  # Validate that each dialogue clip has scene-K.mp3
  SOUND_MISSING=0
  for K in $(jq -r '[(.clips // .scenes // []) | to_entries[] | select(.value.clip_type == "dialogue" or ((.value.tts // null) | type) == "string" or (.value.tts_segment // null) != null) | (.key + 1)] | .[]' "$OUTPUT_DIR/storyboard.json" 2>/dev/null); do
    MP3="$OUTPUT_DIR/scenes/scene-$K/scene-$K.mp3"
    if [ ! -s "$MP3" ] || [ "$(stat -f%z "$MP3" 2>/dev/null || echo 0)" -lt 5000 ]; then
      log "    [warn] missing/undersized TTS: $MP3"
      SOUND_MISSING=$((SOUND_MISSING + 1))
    fi
  done
  if [ "$SOUND_MISSING" -gt 0 ]; then
    fail_task "Sound incomplete: $SOUND_MISSING TTS files missing"
    exit 2
  fi
  log "    All TTS files present, all clips have tts_url in storyboard.json"
else
  log ">>> PHASE 2: Sound — SKIPPED (no dialogue clips)"
fi

# === Phase 3a: Storyboarder sub-agent (Opus 4.7) ===
log ">>> PHASE 3a: Storyboarder sub-agent"

CLAUDE_LOG_STORY="$OUTPUT_DIR/claude-storyboarder.log"
START_STORY=$(date +%s)
if ! run_subagent "Storyboarder" "$SCRIPT_DIR/prompts/storyboarder.txt" "$STORYBOARDER_MODEL" "$CLAUDE_LOG_STORY"; then
  fail_task "Storyboarder failed"
  exit 1
fi

# Validate scene PNGs exist
PNG_MISSING=0
for K in $(seq 1 "$EXPECTED_CLIPS"); do
  PNG="$OUTPUT_DIR/scenes/scene-$K/scene-$K.png"
  if [ ! -s "$PNG" ] || [ "$(stat -f%z "$PNG" 2>/dev/null || echo 0)" -lt 1000 ]; then
    log "    [warn] missing or undersized PNG: $PNG"
    PNG_MISSING=$((PNG_MISSING + 1))
  fi
done
if [ "$PNG_MISSING" -gt 0 ]; then
  fail_task "Storyboarder incomplete: $PNG_MISSING/$EXPECTED_CLIPS scene PNGs missing"
  exit 2
fi
log "    All $EXPECTED_CLIPS scene PNGs present (>1KB)"

# === Phase 3b: Animator sub-agent (Opus 4.7) ===
log ">>> PHASE 3b: Animator sub-agent"

CLAUDE_LOG_ANIM="$OUTPUT_DIR/claude-animator.log"
if ! run_subagent "Animator" "$SCRIPT_DIR/prompts/animator.txt" "$ANIMATOR_MODEL" "$CLAUDE_LOG_ANIM"; then
  fail_task "Animator failed"
  exit 1
fi

# Validate scene MP4s exist
log ">>> Validating Phase 3 output (programmatic)"
MISSING=0
for K in $(seq 1 "$EXPECTED_CLIPS"); do
  MP4="$OUTPUT_DIR/scenes/scene-$K/scene-$K.mp4"
  if [ ! -s "$MP4" ] || [ "$(stat -f%z "$MP4" 2>/dev/null || echo 0)" -lt 100000 ]; then
    log "    [warn] missing or undersized: $MP4"
    MISSING=$((MISSING + 1))
  fi
done
if [ "$MISSING" -gt 0 ]; then
  fail_task "Animator incomplete: $MISSING/$EXPECTED_CLIPS scene MP4s missing"
  exit 2
fi
log "    All $EXPECTED_CLIPS scene MP4s present (>100KB)"

# === Phase 4: Editor sub-agent ===
log ">>> PHASE 4: Editor sub-agent"

# Discover opener / CTA paths if Phase 0 (in monolith) downloaded them somewhere predictable
OPENER_PATH=""
CTA_PATH=""
for candidate in "$OUTPUT_DIR/opener.mp4" "$OUTPUT_DIR/scenes/refs/opener.mp4"; do
  [ -s "$candidate" ] && OPENER_PATH="$candidate" && break
done
for candidate in "$OUTPUT_DIR/cta.mp4" "$OUTPUT_DIR/scenes/refs/cta.mp4"; do
  [ -s "$candidate" ] && CTA_PATH="$candidate" && break
done
export OPENER_PATH CTA_PATH

CLAUDE_LOG_04="$OUTPUT_DIR/claude-editor.log"
if ! run_subagent "Editor" "$SCRIPT_DIR/prompts/editor.txt" "$EDITOR_MODEL" "$CLAUDE_LOG_04"; then
  fail_task "Editor failed"
  exit 1
fi

# === Validate final.mp4 ===
log ">>> Validating final.mp4"
FINAL="$OUTPUT_DIR/final.mp4"
if [ ! -s "$FINAL" ] || [ "$(stat -f%z "$FINAL" 2>/dev/null || echo 0)" -lt 100000 ]; then
  log "!!! Validation failed: final.mp4 missing or <100KB"
  if [ -n "$TASK_ID" ]; then
    "$SCRIPT_DIR/queue/update-task.sh" "$TASK_ID" failed "final.mp4 missing or undersized" >> "$LOG_FILE" 2>&1 || true
  fi
  exit 4
fi

FINAL_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FINAL" 2>/dev/null || echo "?")
FINAL_SIZE_KB=$(( $(stat -f%z "$FINAL") / 1024 ))
log "    final.mp4: OK, ${FINAL_DUR}s, ${FINAL_SIZE_KB}KB"

# === Phase 5: Upload + status update ===
# Editor sub-agent должен залить final.mp4 в Supabase (это в editor.md / format brief).
# Здесь только обновляем статус задачи если есть TASK_ID и Editor залил URL куда-то.
if [ -n "$TASK_ID" ]; then
  log ">>> Updating task status to completed"
  # Попытка вытащить Supabase URL из лога Editor'а (нестрогая)
  VIDEO_URL=$(grep -oE 'https://[a-z0-9.-]+supabase[^[:space:]\"]*\.mp4' "$CLAUDE_LOG_04" | tail -1 || true)
  if [ -n "$VIDEO_URL" ]; then
    log "    Detected Supabase URL: $VIDEO_URL"
    "$SCRIPT_DIR/queue/update-task.sh" "$TASK_ID" completed "$VIDEO_URL" >> "$LOG_FILE" 2>&1 || \
      log "!!! update-task.sh failed (non-fatal)"
  else
    log "    No Supabase URL detected in editor log; marking completed without URL"
    "$SCRIPT_DIR/queue/update-task.sh" "$TASK_ID" completed "" >> "$LOG_FILE" 2>&1 || true
  fi
fi

# === Done ===
TOTAL_DUR=$(($(date +%s) - START_STORY))
log "=== Pipeline finished in ${TOTAL_DUR}s ==="
log "    Output:           $FINAL"
log "    Scenarist log:    $CLAUDE_LOG_SCEN"
[ "$DIALOGUE_CLIPS" -gt 0 ] && log "    Sound log:        $CLAUDE_LOG_SOUND"
log "    Storyboarder log: $CLAUDE_LOG_STORY"
log "    Animator log:     $CLAUDE_LOG_ANIM"
log "    Editor log:       $CLAUDE_LOG_04"
log "    Pipeline log:     $LOG_FILE"

exit 0
