#!/bin/bash
# log-publish.sh — mark a video as published to TikTok or Instagram.
#
# Usage:
#   log-publish.sh --platform tt|inst --video-url <supabase_video_url>
#
# Sets tt_published or inst_published to now() in video_agent_runs.
# Intended for use by the mobile-mcp posting agent after a successful upload.
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

PLATFORM=""; VIDEO_URL=""

while [ $# -gt 0 ]; do
  case "$1" in
    --platform)  PLATFORM="$2"; shift 2 ;;
    --video-url) VIDEO_URL="$2"; shift 2 ;;
    *) echo "ERROR: unknown arg $1" >&2; exit 1 ;;
  esac
done

[ -n "$PLATFORM" ]  || { echo "ERROR: --platform tt|inst required" >&2; exit 1; }
[ -n "$VIDEO_URL" ] || { echo "ERROR: --video-url required" >&2; exit 1; }

case "$PLATFORM" in
  tt)   FIELD="tt_published" ;;
  inst) FIELD="inst_published" ;;
  *) echo "ERROR: --platform must be tt or inst" >&2; exit 1 ;;
esac

TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
BODY="{\"${FIELD}\": \"${TS}\"}"
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
