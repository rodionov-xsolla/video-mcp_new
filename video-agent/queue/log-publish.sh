#!/bin/bash
# log-publish.sh — mark a video as published/scheduled.
#
# Usage:
#   # TikTok / Instagram (post-now — sets timestamp to now):
#   log-publish.sh --platform tt|inst --video-url <supabase_video_url>
#
#   # YouTube (scheduled — sets yt_published to the planned open date):
#   log-publish.sh --platform yt --video-url <supabase_video_url> \
#                  --publish-at <ISO8601_UTC> --youtube-url <yt_url>
#
#   --publish-at: required for --platform yt. Scheduled open date on YouTube,
#                 e.g. "2026-06-13T20:59:00Z". Stored in yt_published.
#   --youtube-url: optional. Stored in youtube_url column.
#
# Requires in .env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

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

PLATFORM=""; VIDEO_URL=""; PUBLISH_AT=""; YOUTUBE_URL=""

while [ $# -gt 0 ]; do
  case "$1" in
    --platform)    PLATFORM="$2";    shift 2 ;;
    --video-url)   VIDEO_URL="$2";   shift 2 ;;
    --publish-at)  PUBLISH_AT="$2";  shift 2 ;;
    --youtube-url) YOUTUBE_URL="$2"; shift 2 ;;
    *) echo "ERROR: unknown arg $1" >&2; exit 1 ;;
  esac
done

[ -n "$PLATFORM" ]  || { echo "ERROR: --platform tt|inst|yt required" >&2; exit 1; }
[ -n "$VIDEO_URL" ] || { echo "ERROR: --video-url required" >&2; exit 1; }

case "$PLATFORM" in
  yt)   FIELD="yt_published" ;;
  tt)   FIELD="tt_published" ;;
  inst) FIELD="inst_published" ;;
  *) echo "ERROR: --platform must be tt|inst|yt" >&2; exit 1 ;;
esac

# YouTube requires explicit --publish-at (the planned open date, not upload time)
if [ "$PLATFORM" = "yt" ]; then
  [ -n "$PUBLISH_AT" ] || { echo "ERROR: --publish-at ISO8601 required for --platform yt" >&2; exit 1; }
  TS="$PUBLISH_AT"
else
  TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
fi

BODY=$(python3 -c "
import json
d = {'${FIELD}': '${TS}'}
if '${YOUTUBE_URL}':
    d['youtube_url'] = '${YOUTUBE_URL}'
print(json.dumps(d))
")

FILTER="output_video_url=eq.$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1],safe=''))" "$VIDEO_URL")"

HTTP=$(/usr/bin/curl -sS -o /tmp/log-publish-resp.$$ -w "%{http_code}" -X PATCH \
  "${SUPABASE_URL}/rest/v1/video_agent_runs?${FILTER}" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=minimal" \
  -d "$BODY")

if [ "$HTTP" = "200" ] || [ "$HTTP" = "204" ]; then
  echo "  ${FIELD} set to ${TS} for: $VIDEO_URL"
else
  echo "WARN: log-publish returned $HTTP" >&2
  cat /tmp/log-publish-resp.$$ >&2
  rm -f /tmp/log-publish-resp.$$
  exit 1
fi
rm -f /tmp/log-publish-resp.$$
