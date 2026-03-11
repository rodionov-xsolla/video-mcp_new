#!/bin/bash
# update-task.sh — обновление статуса задачи в Supabase
# Usage:
#   ./update-task.sh <task_id> completed <video_url>
#   ./update-task.sh <task_id> failed "error message"
#   ./update-task.sh <task_id> running
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../.env" 2>/dev/null || true

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_ANON_KEY:-}" ]; then
  echo "ERROR: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env"
  exit 1
fi

TASK_ID="${1:?Usage: update-task.sh <task_id> <status> [url_or_error]}"
STATUS="${2:?Usage: update-task.sh <task_id> <status> [url_or_error]}"
EXTRA="${3:-}"

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

case "$STATUS" in
  completed)
    DATA="{\"status\":\"completed\",\"completed_at\":\"${NOW}\",\"output_video_url\":\"${EXTRA}\",\"updated_at\":\"${NOW}\"}"
    ;;
  failed)
    DATA="{\"status\":\"failed\",\"error_message\":\"${EXTRA}\",\"updated_at\":\"${NOW}\"}"
    ;;
  running)
    DATA="{\"status\":\"running\",\"claimed_at\":\"${NOW}\",\"updated_at\":\"${NOW}\"}"
    ;;
  *)
    echo "ERROR: status must be completed, failed, or running"
    exit 1
    ;;
esac

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X PATCH "${SUPABASE_URL}/rest/v1/video_tasks?id=eq.${TASK_ID}" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=minimal" \
  -d "$DATA")

if [ "$HTTP_CODE" = "204" ]; then
  echo "OK: task ${TASK_ID} → ${STATUS}"
else
  echo "ERROR: HTTP ${HTTP_CODE} updating task ${TASK_ID}"
  exit 1
fi
