#!/bin/bash
# log-video.sh — upsert строки в video_agent_runs (каталог сгенерированных видео).
#
# Первая генерация → INSERT. Регенерация в тот же путь (тот же output_video_url) → UPDATE
# (created_at сохраняется). Требует UNIQUE(output_video_url) — см. queue/setup.sql.
#
# title маппится на колонку input_idea (она NOT NULL).
#
# Usage:
#   log-video.sh --game GAME --title "..." --format FORMAT --video-url URL [--youtube-url URL]
#
# Требует в .env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

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

GAME=""; TITLE=""; FORMAT=""; VIDEO_URL=""; YOUTUBE_URL=""

while [ $# -gt 0 ]; do
  case "$1" in
    --game)        GAME="$2"; shift 2 ;;
    --title)       TITLE="$2"; shift 2 ;;
    --format)      FORMAT="$2"; shift 2 ;;
    --video-url)   VIDEO_URL="$2"; shift 2 ;;
    --youtube-url) YOUTUBE_URL="$2"; shift 2 ;;
    -h|--help) sed -n '1,17p' "$0"; exit 0 ;;
    *) echo "ERROR: unknown arg $1" >&2; exit 1 ;;
  esac
done

YT_TS=""
[ -n "$YOUTUBE_URL" ] && YT_TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

[ -n "$GAME" ]      || { echo "ERROR: --game required" >&2; exit 1; }
[ -n "$VIDEO_URL" ] || { echo "ERROR: --video-url required" >&2; exit 1; }

# Body: created_at НЕ шлём — на UPDATE он сохранится, на INSERT возьмётся DEFAULT now().
# input_idea (=title) NOT NULL — подстрахуемся идеей/URL, если title пуст.
# youtube_url/format шлём только если заданы — иначе на регенерации до YT-аплоада не затрём прошлое.
BODY=$(python3 -c '
import json, sys
game, title, fmt, url, yt, yt_ts = sys.argv[1:7]
row = {"game_tag": game, "output_video_url": url, "status": "completed",
       "input_idea": title or url}
if fmt:    row["format"] = fmt
if yt:     row["youtube_url"] = yt
if yt_ts:  row["yt_published"] = yt_ts
print(json.dumps(row))
' "$GAME" "$TITLE" "$FORMAT" "$VIDEO_URL" "$YOUTUBE_URL" "$YT_TS")

HTTP=$(/usr/bin/curl -sS -o /tmp/log-video-resp.$$ -w "%{http_code}" -X POST \
  "${SUPABASE_URL}/rest/v1/video_agent_runs?on_conflict=output_video_url" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: resolution=merge-duplicates,return=representation" \
  -d "$BODY")

if [ "$HTTP" = "200" ] || [ "$HTTP" = "201" ]; then
  echo "  video_agent_runs row upserted ($HTTP): $VIDEO_URL"
else
  echo "WARN: video_agent_runs upsert returned $HTTP" >&2
  cat /tmp/log-video-resp.$$ >&2
  rm -f /tmp/log-video-resp.$$
  exit 1
fi
rm -f /tmp/log-video-resp.$$
