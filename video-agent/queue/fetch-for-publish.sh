#!/bin/bash
# fetch-for-publish.sh — pick the next un-published video and stage it on the phone.
#
# Usage:
#   fetch-for-publish.sh --platform tt|inst --game <game_tag> [--limit 1]
#
# 1. Queries video_agent_runs for the oldest completed run whose {tt|inst}_published
#    IS NULL and which has an output_video_url. --game filters by game_tag so the
#    clip lands on the matching phone account (see rules/roles/publisher.md):
#       star-trek-timelines -> "starfleet archives" account
#       genshin-impact      -> "genshin snap" account
# 2. Downloads the mp4 from Supabase Storage to a temp file.
# 3. Pushes it to the phone (/sdcard/Movies/) via adb and triggers a media scan
#    so it shows up in the gallery for the TikTok / Instagram picker.
# 4. Prints machine-readable metadata for the posting agent (publisher.md):
#       VIDEO_URL=...      (pass back to log-publish.sh after a successful post)
#       LOCAL_PATH=...     (path on the Mac)
#       DEVICE_PATH=...    (path on the phone)
#       CAPTION_SOURCE=... (input_idea — basis for the generated caption)
#       GAME_TAG=...
#       FORMAT=...
#       YOUTUBE_URL=...
#
# Requires in .env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
# Requires adb (resolved via $ADB, then $ANDROID_HOME, then ~/Library/Android).

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

# --- resolve adb -------------------------------------------------------------
resolve_adb() {
  if [ -n "${ADB:-}" ] && [ -x "$ADB" ]; then echo "$ADB"; return; fi
  if [ -n "${ANDROID_HOME:-}" ] && [ -x "$ANDROID_HOME/platform-tools/adb" ]; then
    echo "$ANDROID_HOME/platform-tools/adb"; return
  fi
  if [ -x "$HOME/Library/Android/platform-tools/adb" ]; then
    echo "$HOME/Library/Android/platform-tools/adb"; return
  fi
  if [ -x "$HOME/Library/Android/sdk/platform-tools/adb" ]; then
    echo "$HOME/Library/Android/sdk/platform-tools/adb"; return
  fi
  command -v adb 2>/dev/null || true
}
ADB_BIN="$(resolve_adb)"
[ -n "$ADB_BIN" ] || { echo "ERROR: adb not found (set \$ADB or \$ANDROID_HOME)" >&2; exit 1; }

# --- args --------------------------------------------------------------------
PLATFORM=""; GAME=""; LIMIT=1
while [ $# -gt 0 ]; do
  case "$1" in
    --platform) PLATFORM="$2"; shift 2 ;;
    --game)     GAME="$2";     shift 2 ;;
    --limit)    LIMIT="$2";    shift 2 ;;
    *) echo "ERROR: unknown arg $1" >&2; exit 1 ;;
  esac
done

case "$PLATFORM" in
  tt)   FIELD="tt_published" ;;
  inst) FIELD="inst_published" ;;
  *) echo "ERROR: --platform must be tt or inst" >&2; exit 1 ;;
esac

if [ -z "$GAME" ]; then
  echo "ERROR: --game <game_tag> is required (e.g. star-trek-timelines, genshin-impact)." >&2
  echo "       It selects which phone account the clip is meant for; see publisher.md." >&2
  exit 1
fi

# --- check a device is attached ----------------------------------------------
DEVICE_LINE="$("$ADB_BIN" devices | awk 'NR>1 && $2=="device"{print $1}' | head -1)"
if [ -z "$DEVICE_LINE" ]; then
  echo "ERROR: no authorized Android device (adb devices is empty/unauthorized)." >&2
  echo "       Enable USB debugging and accept the RSA prompt on the phone." >&2
  exit 1
fi

# --- query the next un-published run -----------------------------------------
QUERY="${SUPABASE_URL}/rest/v1/video_agent_runs"
QUERY="${QUERY}?${FIELD}=is.null"
QUERY="${QUERY}&status=eq.completed"
QUERY="${QUERY}&output_video_url=not.is.null"
QUERY="${QUERY}&game_tag=eq.${GAME}"
QUERY="${QUERY}&order=created_at.asc&limit=${LIMIT}"
QUERY="${QUERY}&select=output_video_url,input_idea,format,game_tag,youtube_url,created_at"

RESP="$(/usr/bin/curl -sS \
  "$QUERY" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY")"

# Parse the first row with python3 (matches the style used elsewhere in queue/).
ROW_JSON="$(python3 - "$RESP" <<'PY'
import json, sys
rows = json.loads(sys.argv[1]) if sys.argv[1].strip() else []
if not rows:
    print("")
else:
    print(json.dumps(rows[0]))
PY
)"

if [ -z "$ROW_JSON" ]; then
  echo "NOTHING_TO_PUBLISH=1"
  echo "  No completed runs with ${FIELD} IS NULL." >&2
  exit 0
fi

VIDEO_URL="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1]).get("output_video_url",""))' "$ROW_JSON")"
CAPTION_SOURCE="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1]).get("input_idea") or "")' "$ROW_JSON")"
GAME_TAG="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1]).get("game_tag") or "")' "$ROW_JSON")"
FORMAT="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1]).get("format") or "")' "$ROW_JSON")"
YOUTUBE_URL="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1]).get("youtube_url") or "")' "$ROW_JSON")"

[ -n "$VIDEO_URL" ] || { echo "ERROR: row has empty output_video_url" >&2; exit 1; }

# --- download ----------------------------------------------------------------
BASENAME="$(basename "${VIDEO_URL%%\?*}")"
case "$BASENAME" in *.mp4) ;; *) BASENAME="${BASENAME}.mp4" ;; esac
SAFE_NAME="$(printf '%s_%s' "${GAME_TAG:-video}" "$BASENAME" | tr ' /' '__')"
LOCAL_PATH="$(mktemp -d)/${SAFE_NAME}"

HTTP="$(/usr/bin/curl -sS -L -o "$LOCAL_PATH" -w "%{http_code}" "$VIDEO_URL")"
if [ "$HTTP" != "200" ] || [ ! -s "$LOCAL_PATH" ]; then
  echo "ERROR: download failed (HTTP $HTTP) from $VIDEO_URL" >&2
  exit 1
fi

# --- push to phone + media scan ----------------------------------------------
DEVICE_PATH="/sdcard/Movies/${SAFE_NAME}"
"$ADB_BIN" push "$LOCAL_PATH" "$DEVICE_PATH" >&2
"$ADB_BIN" shell am broadcast \
  -a android.intent.action.MEDIA_SCANNER_SCAN_FILE \
  -d "file://${DEVICE_PATH}" >/dev/null 2>&1 || true

# --- emit metadata -----------------------------------------------------------
echo "VIDEO_URL=${VIDEO_URL}"
echo "LOCAL_PATH=${LOCAL_PATH}"
echo "DEVICE_PATH=${DEVICE_PATH}"
echo "CAPTION_SOURCE=${CAPTION_SOURCE}"
echo "GAME_TAG=${GAME_TAG}"
echo "FORMAT=${FORMAT}"
echo "YOUTUBE_URL=${YOUTUBE_URL}"
