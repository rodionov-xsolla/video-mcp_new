#!/bin/bash
# Upload a video to YouTube via Data API v3 (resumable upload).
#
# Usage:
#   youtube-upload.sh [--channel NAME] <video_path> <title> <description> <privacy> [<tags>]
#
#   --channel: gamepulse | yellowguy | <name matching .env suffix>.
#              Selects YOUTUBE_REFRESH_TOKEN_<NAME> / YOUTUBE_CHANNEL_ID_<NAME>.
#              Omit to use the default YOUTUBE_REFRESH_TOKEN / YOUTUBE_CHANNEL_ID.
#   privacy:   public | unlisted | private (default: private)
#   tags:      comma-separated, e.g. "roblox,gaming,shorts"
#
# Requires in .env (shared OAuth client, per-channel refresh tokens):
#   YOUTUBE_CLIENT_ID
#   YOUTUBE_CLIENT_SECRET
#   YOUTUBE_REFRESH_TOKEN[_<CHANNEL>]
#   YOUTUBE_CHANNEL_ID[_<CHANNEL>]   (optional but recommended — verified post-upload)
#
# Returns: YouTube video URL on success, exits 1 on failure.

set -euo pipefail

# ── args ────────────────────────────────────────────────────────────────────
CHANNEL=""
POSITIONAL=()
while [ $# -gt 0 ]; do
  case "$1" in
    --channel) CHANNEL="$2"; shift 2 ;;
    --channel=*) CHANNEL="${1#*=}"; shift ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done
set -- "${POSITIONAL[@]}"

VIDEO_PATH="${1:?Usage: youtube-upload.sh [--channel NAME] <video_path> <title> <description> <privacy> [<tags>]}"
TITLE="${2:?title required}"
DESCRIPTION="${3:-}"
PRIVACY="${4:-private}"
TAGS="${5:-}"

# ── load env ─────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)/video-agent/.env"
if [ -f "$ENV_FILE" ]; then
  set -a; source "$ENV_FILE"; set +a
fi

: "${YOUTUBE_CLIENT_ID:?YOUTUBE_CLIENT_ID not set in .env}"
: "${YOUTUBE_CLIENT_SECRET:?YOUTUBE_CLIENT_SECRET not set in .env}"

# ── resolve per-channel refresh token + expected channel id ───────────────────
if [ -n "$CHANNEL" ]; then
  CHAN_UP=$(echo "$CHANNEL" | tr '[:lower:]' '[:upper:]')
  TOKEN_VAR="YOUTUBE_REFRESH_TOKEN_${CHAN_UP}"
  CHANID_VAR="YOUTUBE_CHANNEL_ID_${CHAN_UP}"
  REFRESH_TOKEN="${!TOKEN_VAR:-}"
  EXPECTED_CHANNEL_ID="${!CHANID_VAR:-}"
  if [ -z "$REFRESH_TOKEN" ]; then
    echo "[youtube-upload] ERROR: $TOKEN_VAR not set in .env (channel '$CHANNEL')"
    exit 1
  fi
  echo "[youtube-upload] Channel: $CHANNEL"
else
  REFRESH_TOKEN="${YOUTUBE_REFRESH_TOKEN:-}"
  EXPECTED_CHANNEL_ID="${YOUTUBE_CHANNEL_ID:-}"
  : "${REFRESH_TOKEN:?YOUTUBE_REFRESH_TOKEN not set in .env (and no --channel given)}"
fi

# ── get access token ──────────────────────────────────────────────────────────
echo "[youtube-upload] Refreshing access token..."
TOKEN_RESPONSE=$(curl -s -X POST https://oauth2.googleapis.com/token \
  -d "client_id=${YOUTUBE_CLIENT_ID}" \
  -d "client_secret=${YOUTUBE_CLIENT_SECRET}" \
  -d "refresh_token=${REFRESH_TOKEN}" \
  -d "grant_type=refresh_token")

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token',''))")
if [ -z "$ACCESS_TOKEN" ]; then
  echo "[youtube-upload] ERROR: failed to get access token"
  echo "$TOKEN_RESPONSE"
  exit 1
fi

# ── build metadata JSON ───────────────────────────────────────────────────────
FILE_SIZE=$(stat -f%z "$VIDEO_PATH" 2>/dev/null || stat -c%s "$VIDEO_PATH")

# Build tags array
TAGS_JSON="[]"
if [ -n "$TAGS" ]; then
  TAGS_JSON=$(python3 -c "
import json, sys
tags = [t.strip() for t in '${TAGS}'.split(',') if t.strip()]
print(json.dumps(tags))
")
fi

METADATA=$(python3 -c "
import json
meta = {
  'snippet': {
    'title': '''${TITLE}''',
    'description': '''${DESCRIPTION}''',
    'tags': ${TAGS_JSON},
    'categoryId': '20'
  },
  'status': {
    'privacyStatus': '${PRIVACY}',
    'selfDeclaredMadeForKids': False
  }
}
print(json.dumps(meta))
")

# ── initiate resumable upload ─────────────────────────────────────────────────
echo "[youtube-upload] Initiating upload: $(basename "$VIDEO_PATH") (${FILE_SIZE} bytes)"

INIT_RESPONSE=$(curl -s -D - -X POST \
  "https://www.googleapis.com/upload/youtube/v3/videos?part=snippet,status&uploadType=resumable" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Upload-Content-Type: video/mp4" \
  -H "X-Upload-Content-Length: ${FILE_SIZE}" \
  -d "$METADATA")

UPLOAD_URL=$(echo "$INIT_RESPONSE" | grep -i "^location:" | tr -d '\r' | awk '{print $2}')
if [ -z "$UPLOAD_URL" ]; then
  echo "[youtube-upload] ERROR: could not get upload URL"
  echo "$INIT_RESPONSE"
  exit 1
fi

# ── upload the file ───────────────────────────────────────────────────────────
echo "[youtube-upload] Uploading..."
UPLOAD_RESPONSE=$(curl -s -X PUT "$UPLOAD_URL" \
  -H "Content-Type: video/mp4" \
  -H "Content-Length: ${FILE_SIZE}" \
  --data-binary "@${VIDEO_PATH}")

VIDEO_ID=$(echo "$UPLOAD_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null || true)
if [ -z "$VIDEO_ID" ]; then
  echo "[youtube-upload] ERROR: upload failed"
  echo "$UPLOAD_RESPONSE"
  exit 1
fi

# ── verify the upload landed on the expected channel ──────────────────────────
if [ -n "$EXPECTED_CHANNEL_ID" ]; then
  ACTUAL_CHANNEL_ID=$(echo "$UPLOAD_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('snippet',{}).get('channelId',''))" 2>/dev/null || true)
  if [ -n "$ACTUAL_CHANNEL_ID" ] && [ "$ACTUAL_CHANNEL_ID" != "$EXPECTED_CHANNEL_ID" ]; then
    echo "[youtube-upload] WARNING: uploaded to channel '$ACTUAL_CHANNEL_ID' but expected '$EXPECTED_CHANNEL_ID'"
    echo "[youtube-upload] The video is live at https://www.youtube.com/watch?v=${VIDEO_ID} — review/delete if wrong channel."
  fi
fi

YOUTUBE_URL="https://www.youtube.com/watch?v=${VIDEO_ID}"
echo "[youtube-upload] SUCCESS: ${YOUTUBE_URL}"
echo "$YOUTUBE_URL"
