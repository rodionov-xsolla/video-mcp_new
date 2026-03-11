#!/bin/bash
# add-task.sh — добавление задачи в очередь
# Usage: ./add-task.sh "GameTag" "Video idea description" [priority]
# Example: ./add-task.sh "Oxide" "Noob builds a castle and it explodes" 1
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../.env" 2>/dev/null || true

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_ANON_KEY:-}" ]; then
  echo "ERROR: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env"
  exit 1
fi

GAME_TAG="${1:?Usage: add-task.sh <game_tag> <idea> [priority]}"
IDEA="${2:?Usage: add-task.sh <game_tag> <idea> [priority]}"
PRIORITY="${3:-0}"

RESPONSE=$(curl -s \
  -X POST "${SUPABASE_URL}/rest/v1/video_tasks" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "{\"game_tag\":\"${GAME_TAG}\",\"idea\":\"${IDEA}\",\"priority\":${PRIORITY},\"source\":\"manual\"}")

TASK_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -n "$TASK_ID" ]; then
  echo "Task added: ${TASK_ID}"
  echo "  game: ${GAME_TAG}"
  echo "  idea: ${IDEA}"
  echo "  priority: ${PRIORITY}"
else
  echo "ERROR adding task:"
  echo "$RESPONSE"
  exit 1
fi
