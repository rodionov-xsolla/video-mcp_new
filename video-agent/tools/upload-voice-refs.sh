#!/bin/bash
# upload-voice-refs.sh — загрузка голосовых референсов Genshin Impact в Supabase Storage
#
# Storage path: assets/genshin-impact/characters/{slug}/voice-{N}.mp3
# Slug = lowercase, spaces → hyphens
#
# Usage: ./tools/upload-voice-refs.sh [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -f "$AGENT_DIR/.env" ]; then
  set -a; . "$AGENT_DIR/.env"; set +a
fi

for VAR in SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY; do
  if [ -z "${!VAR:-}" ]; then
    echo "ERROR: $VAR not set in .env" >&2; exit 1
  fi
done

VOICES_DIR="$AGENT_DIR/games/genshin impact/characters"
DRY_RUN="${1:-}"
GAME_SLUG="genshin-impact"
OK=0; FAIL=0; SKIP=0

echo "=== Uploading Genshin Impact voice refs to Supabase ==="
echo "Source: $VOICES_DIR"
echo ""

for char_dir in "$VOICES_DIR"/*/; do
  CHAR_NAME="$(basename "$char_dir")"
  # Normalize: lowercase, spaces → hyphens
  CHAR_SLUG="$(echo "$CHAR_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"

  for N in 1 2 3; do
    LOCAL_FILE="$char_dir/${CHAR_NAME}_${N}.mp3"
    [ -f "$LOCAL_FILE" ] || { echo "  SKIP (missing): $LOCAL_FILE" >&2; ((SKIP++)); continue; }

    TARGET_PATH="${GAME_SLUG}/characters/${CHAR_SLUG}/voice-${N}.mp3"
    PUBLIC_URL="${SUPABASE_URL}/storage/v1/object/public/assets/${TARGET_PATH}"

    if [ "$DRY_RUN" = "--dry-run" ]; then
      echo "  [dry-run] $CHAR_NAME → assets/$TARGET_PATH"
      ((OK++))
      continue
    fi

    UPLOADED=0
    for ATTEMPT in 1 2 3; do
      HTTP=$(/usr/bin/curl -sS -o /tmp/vup-resp.$$ -w "%{http_code}" \
        --retry 0 --max-time 30 \
        -X PUT "${SUPABASE_URL}/storage/v1/object/assets/${TARGET_PATH}" \
        -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
        -H "Content-Type: audio/mpeg" \
        -H "x-upsert: true" \
        --data-binary "@${LOCAL_FILE}" 2>/dev/null) || true
      if [ "$HTTP" = "200" ]; then
        UPLOADED=1; break
      fi
      echo "  retry $ATTEMPT/$CHAR_NAME[$N] (HTTP=$HTTP)" >&2
      sleep 2
    done
    rm -f /tmp/vup-resp.$$

    if [ "$UPLOADED" = "1" ]; then
      echo "  OK  $CHAR_NAME[$N] → $PUBLIC_URL"
      ((OK++))
    else
      echo "  FAIL $CHAR_NAME[$N]" >&2
      ((FAIL++))
    fi
  done
done

echo ""
echo "=== Done: $OK uploaded, $FAIL failed, $SKIP skipped ==="
