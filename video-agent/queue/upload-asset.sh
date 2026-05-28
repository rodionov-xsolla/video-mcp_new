#!/bin/bash
# upload-asset.sh — загрузка ассета в Supabase Storage (+ регистрация в game_assets).
#
# Новая раскладка хранилища (Phase 3, 2026-05-28):
#
#   assets/{GAME}/characters/{slug}/sheet.png            — canonical character ref
#   assets/{GAME}/characters/{slug}/variants/{var}.png   — variant ref (young/mature/borg/...)
#   assets/{GAME}/characters/{slug}/avatar.png           — Kling Avatar ref
#   assets/{GAME}/locations/{slug}.png                   — background / location
#   assets/{GAME}/branding/{name}.{png|mp4}              — CTA, opener, title-card
#   assets/{GAME}/gameplay/{name}.mp4                    — gameplay clip
#   episodes/{GAME}/{DATE}-{FORMAT}/scenes/{file}        — per-episode scene PNG/MP4
#   episodes/{GAME}/{DATE}-{FORMAT}/tts/{file}           — per-episode TTS
#
# Usage:
#   ./upload-asset.sh --kind character --game GAME --slug picard \
#                     [--variant prophet] ./file.png \
#                     [--prompt-block "..."] [--tags "tag1,tag2"]
#
#   ./upload-asset.sh --kind avatar   --game GAME --slug q ./file.png
#   ./upload-asset.sh --kind location --game GAME --slug ds9-ops ./file.png
#   ./upload-asset.sh --kind branding --game GAME --name cta ./file.mp4
#   ./upload-asset.sh --kind gameplay --game GAME ./file.mp4
#
#   ./upload-asset.sh --kind episode-scene --game GAME --episode 2026-05-28-redcon \
#                     --name scene-1.png ./file.png
#   ./upload-asset.sh --kind episode-tts --game GAME --episode 2026-05-28-redcon \
#                     --name clip-1.mp3 ./file.mp3
#
# Episode kinds: only upload to Storage, do NOT insert into game_assets
# (per-episode files are not reusable refs).

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

KIND=""; GAME=""; SLUG=""; VARIANT=""; NAME=""; EPISODE=""
PROMPT_BLOCK=""; TAGS=""; FILE_PATH=""

while [ $# -gt 0 ]; do
  case "$1" in
    --kind)         KIND="$2"; shift 2 ;;
    --game)         GAME="$2"; shift 2 ;;
    --slug)         SLUG="$2"; shift 2 ;;
    --variant)      VARIANT="$2"; shift 2 ;;
    --name)         NAME="$2"; shift 2 ;;
    --episode)      EPISODE="$2"; shift 2 ;;
    --prompt-block) PROMPT_BLOCK="$2"; shift 2 ;;
    --tags)         TAGS="$2"; shift 2 ;;
    --) shift; FILE_PATH="$1"; break ;;
    -h|--help) sed -n '1,40p' "$0"; exit 0 ;;
    -*) echo "ERROR: unknown flag $1" >&2; exit 1 ;;
    *) FILE_PATH="$1"; shift ;;
  esac
done

[ -n "$KIND" ] || { echo "ERROR: --kind required" >&2; exit 1; }
[ -n "$GAME" ] || { echo "ERROR: --game required" >&2; exit 1; }
[ -n "$FILE_PATH" ] || { echo "ERROR: file path required" >&2; exit 1; }
[ -f "$FILE_PATH" ] || { echo "ERROR: file not found: $FILE_PATH" >&2; exit 1; }

EXT="${FILE_PATH##*.}"
case "$(echo "$EXT" | tr A-Z a-z)" in
  png)         CONTENT_TYPE="image/png" ;;
  jpg|jpeg)    CONTENT_TYPE="image/jpeg" ;;
  webp)        CONTENT_TYPE="image/webp" ;;
  mp4|mov)     CONTENT_TYPE="video/mp4" ;;
  mp3)         CONTENT_TYPE="audio/mpeg" ;;
  wav)         CONTENT_TYPE="audio/wav" ;;
  *)           CONTENT_TYPE="application/octet-stream" ;;
esac

# Resolve target bucket + path + DB asset_type
TARGET_BUCKET="assets"
TARGET_PATH=""
DB_ASSET_TYPE=""
DB_CHARACTER_NAME=""   # what we put in game_assets.character_name
INSERT_DB="yes"

case "$KIND" in
  character)
    [ -n "$SLUG" ] || { echo "ERROR: --slug required for character" >&2; exit 1; }
    if [ -n "$VARIANT" ]; then
      TARGET_PATH="${GAME}/characters/${SLUG}/variants/${VARIANT}.${EXT}"
      DB_CHARACTER_NAME="${SLUG}-${VARIANT}"
    else
      TARGET_PATH="${GAME}/characters/${SLUG}/sheet.${EXT}"
      DB_CHARACTER_NAME="${SLUG}"
    fi
    DB_ASSET_TYPE="reference_image"
    ;;

  avatar)
    [ -n "$SLUG" ] || { echo "ERROR: --slug required for avatar" >&2; exit 1; }
    if [ -n "$VARIANT" ]; then
      TARGET_PATH="${GAME}/characters/${SLUG}/avatar-${VARIANT}.${EXT}"
      DB_CHARACTER_NAME="${SLUG}-${VARIANT}"
    else
      TARGET_PATH="${GAME}/characters/${SLUG}/avatar.${EXT}"
      DB_CHARACTER_NAME="${SLUG}"
    fi
    DB_ASSET_TYPE="avatar_ref"
    ;;

  location)
    [ -n "$SLUG" ] || { echo "ERROR: --slug required for location" >&2; exit 1; }
    TARGET_PATH="${GAME}/locations/${SLUG}.${EXT}"
    DB_CHARACTER_NAME="location:${SLUG}"
    DB_ASSET_TYPE="generated_ref"
    [ -z "$TAGS" ] && TAGS="location" || TAGS="${TAGS},location"
    ;;

  branding)
    [ -n "$NAME" ] || { echo "ERROR: --name required for branding (e.g. cta, opener)" >&2; exit 1; }
    # name may include extension; if not, append
    case "$NAME" in
      *.*) FILENAME="$NAME" ;;
      *)   FILENAME="${NAME}.${EXT}" ;;
    esac
    TARGET_PATH="${GAME}/branding/${FILENAME}"
    DB_CHARACTER_NAME="branding:${NAME%.*}"
    DB_ASSET_TYPE="generated_ref"
    [ -z "$TAGS" ] && TAGS="branding" || TAGS="${TAGS},branding"
    ;;

  gameplay)
    BN="$(basename "$FILE_PATH")"
    # Normalize: lowercase, spaces/underscores → hyphens
    NORM="$(echo "$BN" | tr 'A-Z ' 'a-z-' | tr '_' '-')"
    TARGET_PATH="${GAME}/gameplay/${NORM}"
    DB_CHARACTER_NAME="${NAME:-$(echo "$NORM" | sed 's/\.[^.]*$//')}"
    DB_ASSET_TYPE="gameplay_clip"
    ;;

  episode-scene)
    [ -n "$EPISODE" ] || { echo "ERROR: --episode required (format: YYYY-MM-DD-format-slug)" >&2; exit 1; }
    [ -n "$NAME" ]    || { echo "ERROR: --name required (e.g. scene-1.png)" >&2; exit 1; }
    TARGET_BUCKET="episodes"
    TARGET_PATH="${GAME}/${EPISODE}/scenes/${NAME}"
    INSERT_DB="no"
    ;;

  episode-tts)
    [ -n "$EPISODE" ] || { echo "ERROR: --episode required" >&2; exit 1; }
    [ -n "$NAME" ]    || { echo "ERROR: --name required (e.g. clip-1.mp3)" >&2; exit 1; }
    TARGET_BUCKET="episodes"
    TARGET_PATH="${GAME}/${EPISODE}/tts/${NAME}"
    INSERT_DB="no"
    ;;

  *)
    echo "ERROR: unknown --kind '$KIND' (use: character|avatar|location|branding|gameplay|episode-scene|episode-tts)" >&2
    exit 1 ;;
esac

echo "Uploading → ${TARGET_BUCKET}/${TARGET_PATH}"

UPLOAD_HTTP=$(/usr/bin/curl -sS -o /tmp/upload-resp.$$ -w "%{http_code}" -X POST \
  "${SUPABASE_URL}/storage/v1/object/${TARGET_BUCKET}/${TARGET_PATH}" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: $CONTENT_TYPE" \
  --data-binary "@${FILE_PATH}")

if [ "$UPLOAD_HTTP" != "200" ]; then
  echo "  POST returned $UPLOAD_HTTP — retrying with x-upsert..."
  UPLOAD_HTTP=$(/usr/bin/curl -sS -o /tmp/upload-resp.$$ -w "%{http_code}" -X PUT \
    "${SUPABASE_URL}/storage/v1/object/${TARGET_BUCKET}/${TARGET_PATH}" \
    -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
    -H "Content-Type: $CONTENT_TYPE" \
    -H "x-upsert: true" \
    --data-binary "@${FILE_PATH}")
  if [ "$UPLOAD_HTTP" != "200" ]; then
    echo "ERROR: upload failed with $UPLOAD_HTTP" >&2
    cat /tmp/upload-resp.$$ >&2
    rm -f /tmp/upload-resp.$$
    exit 1
  fi
fi
rm -f /tmp/upload-resp.$$

PUBLIC_URL="${SUPABASE_URL}/storage/v1/object/public/${TARGET_BUCKET}/${TARGET_PATH}"
echo "  url: $PUBLIC_URL"

if [ "$INSERT_DB" != "yes" ]; then
  echo "  (no DB row — episode-* kinds are not registered in game_assets)"
  echo "$PUBLIC_URL"
  exit 0
fi

# Build tags array literal for Postgres
if [ -n "$TAGS" ]; then
  TAGS_PG="{$(echo "$TAGS" | sed 's/[[:space:]]//g')}"
else
  TAGS_PG="{}"
fi

# Build prompt_block JSON
if [ -n "$PROMPT_BLOCK" ]; then
  PROMPT_JSON=$(python3 -c "import json,sys; print(json.dumps(sys.argv[1]))" "$PROMPT_BLOCK")
else
  PROMPT_JSON="null"
fi

INSERT_BODY=$(python3 -c '
import json, sys
print(json.dumps({
  "game_tag": sys.argv[1],
  "character_name": sys.argv[2],
  "asset_type": sys.argv[3],
  "url": sys.argv[4],
  "prompt_block": json.loads(sys.argv[5]) if sys.argv[5] != "null" else None,
  "tags": sys.argv[6],
}))
' "$GAME" "$DB_CHARACTER_NAME" "$DB_ASSET_TYPE" "$PUBLIC_URL" "$PROMPT_JSON" "$TAGS_PG")

INSERT_HTTP=$(/usr/bin/curl -sS -o /tmp/insert-resp.$$ -w "%{http_code}" -X POST \
  "${SUPABASE_URL}/rest/v1/game_assets" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "$INSERT_BODY")

if [ "$INSERT_HTTP" = "201" ]; then
  echo "  game_assets row inserted"
elif [ "$INSERT_HTTP" = "409" ]; then
  echo "  game_assets row already exists (UNIQUE), skipping insert"
else
  echo "WARN: insert returned $INSERT_HTTP" >&2
  cat /tmp/insert-resp.$$ >&2
fi
rm -f /tmp/insert-resp.$$

echo "$PUBLIC_URL"
