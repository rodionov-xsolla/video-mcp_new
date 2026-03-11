#!/bin/bash
# check-queue.sh — проверка pending задач в Supabase и atomic claim
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../.env" 2>/dev/null || true

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_ANON_KEY:-}" ]; then
  echo "ERROR: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env"
  exit 1
fi

# 1. Query oldest pending task (highest priority first, then oldest)
RESPONSE=$(curl -s \
  "${SUPABASE_URL}/rest/v1/video_tasks?status=eq.pending&order=priority.desc,created_at.asc&limit=1" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_ANON_KEY}")

# Check if empty array
if [ "$RESPONSE" = "[]" ] || [ -z "$RESPONSE" ]; then
  echo "NO_PENDING_TASKS"
  exit 0
fi

# 2. Extract task fields using grep (Supabase returns single-element array)
TASK_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
GAME_TAG=$(echo "$RESPONSE" | grep -o '"game_tag":"[^"]*"' | head -1 | cut -d'"' -f4)
IDEA=$(echo "$RESPONSE" | grep -o '"idea":"[^"]*"' | head -1 | cut -d'"' -f4)
PRIORITY=$(echo "$RESPONSE" | grep -o '"priority":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$TASK_ID" ]; then
  echo "NO_PENDING_TASKS"
  exit 0
fi

# 3. Atomic claim: set status=running, claimed_at=now
CLAIM_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X PATCH "${SUPABASE_URL}/rest/v1/video_tasks?id=eq.${TASK_ID}&status=eq.pending" \
  -H "apikey: ${SUPABASE_ANON_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=minimal" \
  -d "{\"status\":\"running\",\"claimed_at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}")

if [ "$CLAIM_RESPONSE" != "204" ]; then
  echo "CLAIM_FAILED (task may have been claimed by another worker)"
  exit 1
fi

# 4. Output task info
echo "TASK_FOUND"
echo "task_id=${TASK_ID}"
echo "game_tag=${GAME_TAG}"
echo "idea=${IDEA}"
echo "priority=${PRIORITY}"
