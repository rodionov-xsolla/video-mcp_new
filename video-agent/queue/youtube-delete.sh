#!/bin/bash
# Delete a YouTube video via Data API v3.
#
# Usage:
#   youtube-delete.sh [--channel NAME] <video_id> [<video_id> ...]
#
#   --channel: gamepulse | yellowguy | <name matching .env suffix>.
#              Selects YOUTUBE_REFRESH_TOKEN_<NAME>.
#              Omit to use the default YOUTUBE_REFRESH_TOKEN.
#   video_id:  YouTube video ID (e.g. dQw4w9WgXcQ), or full URL.
#
# Requires in .env:
#   YOUTUBE_CLIENT_ID
#   YOUTUBE_CLIENT_SECRET
#   YOUTUBE_REFRESH_TOKEN[_<CHANNEL>]

set -euo pipefail

# ── args ────────────────────────────────────────────────────────────────────
CHANNEL=""
VIDEO_IDS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --channel) CHANNEL="$2"; shift 2 ;;
    --channel=*) CHANNEL="${1#*=}"; shift ;;
    *) VIDEO_IDS+=("$1"); shift ;;
  esac
done

if [ ${#VIDEO_IDS[@]} -eq 0 ]; then
  echo "Usage: youtube-delete.sh [--channel NAME] <video_id> [<video_id> ...]"
  exit 1
fi

# ── load env ─────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)/video-agent/.env"
if [ -f "$ENV_FILE" ]; then
  set -a; source "$ENV_FILE"; set +a
fi

: "${YOUTUBE_CLIENT_ID:?YOUTUBE_CLIENT_ID not set in .env}"
: "${YOUTUBE_CLIENT_SECRET:?YOUTUBE_CLIENT_SECRET not set in .env}"

# ── resolve per-channel refresh token ────────────────────────────────────────
if [ -n "$CHANNEL" ]; then
  CHAN_UP=$(echo "$CHANNEL" | tr '[:lower:]' '[:upper:]')
  TOKEN_VAR="YOUTUBE_REFRESH_TOKEN_${CHAN_UP}"
  REFRESH_TOKEN="${!TOKEN_VAR:-}"
  if [ -z "$REFRESH_TOKEN" ]; then
    echo "[youtube-delete] ERROR: $TOKEN_VAR not set in .env (channel '$CHANNEL')"
    exit 1
  fi
  echo "[youtube-delete] Channel: $CHANNEL"
else
  REFRESH_TOKEN="${YOUTUBE_REFRESH_TOKEN:-}"
  : "${REFRESH_TOKEN:?YOUTUBE_REFRESH_TOKEN not set in .env (and no --channel given)}"
fi

# ── get access token ──────────────────────────────────────────────────────────
echo "[youtube-delete] Refreshing access token..."
TOKEN_RESPONSE=$(curl -s -X POST https://oauth2.googleapis.com/token \
  -d "client_id=${YOUTUBE_CLIENT_ID}" \
  -d "client_secret=${YOUTUBE_CLIENT_SECRET}" \
  -d "refresh_token=${REFRESH_TOKEN}" \
  -d "grant_type=refresh_token")

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token',''))")
if [ -z "$ACCESS_TOKEN" ]; then
  echo "[youtube-delete] ERROR: failed to get access token"
  echo "$TOKEN_RESPONSE"
  exit 1
fi

# ── delete each video ─────────────────────────────────────────────────────────
FAIL=0
for RAW_ID in "${VIDEO_IDS[@]}"; do
  # Accept full URLs too: extract the ID from ?v=... or youtu.be/...
  VIDEO_ID=$(echo "$RAW_ID" | python3 -c "
import sys, re
raw = sys.stdin.read().strip()
m = re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})', raw)
print(m.group(1) if m else raw)
")

  echo "[youtube-delete] Deleting video: $VIDEO_ID"
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
    "https://www.googleapis.com/youtube/v3/videos?id=${VIDEO_ID}" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}")

  if [ "$HTTP_STATUS" = "204" ]; then
    echo "[youtube-delete] SUCCESS: $VIDEO_ID deleted (204 No Content)"
  elif [ "$HTTP_STATUS" = "404" ]; then
    echo "[youtube-delete] WARNING: $VIDEO_ID not found (404) — already deleted or wrong ID"
    FAIL=1
  else
    echo "[youtube-delete] ERROR: $VIDEO_ID — HTTP $HTTP_STATUS"
    FAIL=1
  fi
done

exit $FAIL
