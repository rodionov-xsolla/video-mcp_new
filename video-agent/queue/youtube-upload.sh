#!/bin/bash
# Upload a video to YouTube via Data API v3 (resumable upload).
#
# Usage:
#   youtube-upload.sh [--channel NAME] [--publish-at ISO8601] [--thumbnail PATH] <video_path> <title> <description> <privacy> [<tags>]
#
#   --channel:    gamepulse | yellowguy | <name matching .env suffix>.
#                 Selects YOUTUBE_REFRESH_TOKEN_<NAME> / YOUTUBE_CHANNEL_ID_<NAME>.
#                 Omit to use the default YOUTUBE_REFRESH_TOKEN / YOUTUBE_CHANNEL_ID.
#   --publish-at: ISO 8601 UTC datetime, e.g. "2026-06-03T20:59:00Z".
#                 If omitted, auto-schedules at the nearest free date at 20:59 UTC (23:59 MSK).
#                 Pass "now" to publish immediately as public.
#   --thumbnail:  Path to thumbnail image (JPG/PNG). Uploaded after video.
#   privacy:      ignored when auto-scheduling (always private+publishAt).
#                 Honoured only when --publish-at=now.
#   tags:         comma-separated, e.g. "roblox,gaming,shorts"
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
PUBLISH_AT=""
THUMBNAIL=""
POSITIONAL=()
while [ $# -gt 0 ]; do
  case "$1" in
    --channel) CHANNEL="$2"; shift 2 ;;
    --channel=*) CHANNEL="${1#*=}"; shift ;;
    --publish-at) PUBLISH_AT="$2"; shift 2 ;;
    --publish-at=*) PUBLISH_AT="${1#*=}"; shift ;;
    --thumbnail) THUMBNAIL="$2"; shift 2 ;;
    --thumbnail=*) THUMBNAIL="${1#*=}"; shift ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done
set -- "${POSITIONAL[@]}"

VIDEO_PATH="${1:?Usage: youtube-upload.sh [--channel NAME] [--thumbnail PATH] <video_path> <title> <description> <privacy> [<tags>]}"
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

# ── handle --publish-at=now ───────────────────────────────────────────────────
PUBLISH_NOW=false
if [ "$PUBLISH_AT" = "now" ]; then
  PUBLISH_NOW=true
  PUBLISH_AT=""
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

# ── auto-schedule: find nearest free date at 20:59 UTC (23:59 MSK) ───────────
if [ "$PUBLISH_NOW" = false ] && [ -z "$PUBLISH_AT" ]; then
  echo "[youtube-upload] Auto-scheduling: finding nearest free date..."
  TAKEN_DATES=$(python3 - "$ACCESS_TOKEN" <<'PYEOF'
import sys, json, re, subprocess, datetime

token = sys.argv[1]

def yt_get(url):
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: Bearer {token}", url],
        capture_output=True, text=True
    )
    raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', result.stdout)
    return json.loads(raw)

# get uploads playlist
ch = yt_get("https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true")
playlist_id = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

# get last 50 video IDs
pl = yt_get(f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&maxResults=50")
ids = ",".join(it["contentDetails"]["videoId"] for it in pl.get("items", []))

if not ids:
    sys.exit(0)

# fetch statuses
vids = yt_get(f"https://www.googleapis.com/youtube/v3/videos?part=status&id={ids}")
taken = set()
for it in vids.get("items", []):
    pub = it["status"].get("publishAt", "")
    if pub:
        taken.add(pub[:10])  # YYYY-MM-DD

print(" ".join(sorted(taken)))
PYEOF
  )

  # Find nearest free date starting from today
  PUBLISH_AT=$(python3 - "$TAKEN_DATES" <<'PYEOF'
import sys, datetime

taken = set(sys.argv[1].split()) if sys.argv[1] else set()
today = datetime.date.today()
candidate = today
for _ in range(60):
    if candidate.isoformat() not in taken:
        print(f"{candidate.isoformat()}T20:59:00Z")
        sys.exit(0)
    candidate += datetime.timedelta(days=1)

# Fallback: 60 days out
print(f"{candidate.isoformat()}T20:59:00Z")
PYEOF
  )
  echo "[youtube-upload] Auto-scheduled for: ${PUBLISH_AT}"
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
publish_now = '${PUBLISH_NOW}' == 'true'
privacy = '${PRIVACY}' if publish_now else 'private'
publish_at = '' if publish_now else '${PUBLISH_AT}'
status = {
    'privacyStatus': privacy,
    'selfDeclaredMadeForKids': False
}
if publish_at:
    status['publishAt'] = publish_at
meta = {
  'snippet': {
    'title': '''${TITLE}''',
    'description': '''${DESCRIPTION}''',
    'tags': ${TAGS_JSON},
    'categoryId': '20'
  },
  'status': status
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
if [ "$PUBLISH_NOW" = true ]; then
  echo "[youtube-upload] SUCCESS (public now): ${YOUTUBE_URL}"
elif [ -n "$PUBLISH_AT" ]; then
  echo "[youtube-upload] SUCCESS (scheduled ${PUBLISH_AT}): ${YOUTUBE_URL}"
else
  echo "[youtube-upload] SUCCESS: ${YOUTUBE_URL}"
fi

# Machine-readable output for callers to capture scheduled date
[ -n "$PUBLISH_AT" ] && echo "SCHEDULED_FOR=${PUBLISH_AT}"

# ── upload thumbnail (optional) ───────────────────────────────────────────────
if [ -n "$THUMBNAIL" ]; then
  if [ ! -f "$THUMBNAIL" ]; then
    echo "[youtube-upload] WARNING: thumbnail file not found: $THUMBNAIL — skipping"
  else
    MIME="image/jpeg"
    case "${THUMBNAIL##*.}" in png|PNG) MIME="image/png" ;; esac
    echo "[youtube-upload] Uploading thumbnail: $(basename "$THUMBNAIL")"
    THUMB_RESPONSE=$(curl -s -X POST \
      "https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId=${VIDEO_ID}&uploadType=media" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Content-Type: ${MIME}" \
      --data-binary "@${THUMBNAIL}")
    THUMB_KIND=$(echo "$THUMB_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('kind',''))" 2>/dev/null || true)
    if [ "$THUMB_KIND" = "youtube#thumbnailSetResponse" ]; then
      echo "[youtube-upload] Thumbnail uploaded OK"
    else
      echo "[youtube-upload] WARNING: thumbnail upload may have failed"
      echo "$THUMB_RESPONSE"
    fi
  fi
fi

echo "$YOUTUBE_URL"
