#!/bin/bash
# upload-asset.sh — загрузка ассета в Supabase (Storage + game_assets)
# Usage: ./upload-asset.sh "GAME_TAG" "CharacterName" "asset_type" ./file.png [--prompt-block "..."] [--tags "tag1,tag2"]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Загружаем .env
if [ -f "$AGENT_DIR/.env" ]; then
  set -a
  source "$AGENT_DIR/.env"
  set +a
fi

# Проверяем обязательные переменные
for VAR in SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY; do
  if [ -z "${!VAR:-}" ]; then
    echo "ERROR: $VAR is not set in .env"
    exit 1
  fi
done

GAME_TAG="${1:?Usage: ./upload-asset.sh GAME_TAG CharacterName asset_type ./file.png [--prompt-block '...'] [--tags 'tag1,tag2']}"
CHARACTER="${2:?Missing CharacterName}"
ASSET_TYPE="${3:?Missing asset_type (reference_image|character_card|screenshot|promo_art|generated_ref)}"
FILE_PATH="${4:?Missing file path}"

PROMPT_BLOCK=""
TAGS=""

# Parse optional flags
shift 4
while [[ $# -gt 0 ]]; do
  case $1 in
    --prompt-block) PROMPT_BLOCK="$2"; shift 2 ;;
    --tags) TAGS="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Validate asset_type
case "$ASSET_TYPE" in
  reference_image|character_card|screenshot|promo_art|generated_ref) ;;
  *) echo "ERROR: Invalid asset_type: $ASSET_TYPE"; exit 1 ;;
esac

# Validate file exists
if [ ! -f "$FILE_PATH" ]; then
  echo "ERROR: File not found: $FILE_PATH"
  exit 1
fi

# Determine file extension and content type
EXT="${FILE_PATH##*.}"
case "$EXT" in
  png) CONTENT_TYPE="image/png" ;;
  jpg|jpeg) CONTENT_TYPE="image/jpeg" ;;
  webp) CONTENT_TYPE="image/webp" ;;
  *) CONTENT_TYPE="application/octet-stream" ;;
esac

# Upload to Supabase Storage
STORAGE_PATH="assets/${GAME_TAG}/${CHARACTER}/${ASSET_TYPE}.${EXT}"
echo "Uploading to Storage: $STORAGE_PATH"

UPLOAD_RESULT=$(curl -s -w "\n%{http_code}" -X POST \
  "${SUPABASE_URL}/storage/v1/object/assets/${STORAGE_PATH}" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: $CONTENT_TYPE" \
  --data-binary "@${FILE_PATH}")

HTTP_CODE=$(echo "$UPLOAD_RESULT" | tail -1)
if [ "$HTTP_CODE" != "200" ]; then
  echo "WARNING: Storage upload returned $HTTP_CODE, trying upsert..."
  UPLOAD_RESULT=$(curl -s -w "\n%{http_code}" -X PUT \
    "${SUPABASE_URL}/storage/v1/object/assets/${STORAGE_PATH}" \
    -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
    -H "Content-Type: $CONTENT_TYPE" \
    -H "x-upsert: true" \
    --data-binary "@${FILE_PATH}")
  HTTP_CODE=$(echo "$UPLOAD_RESULT" | tail -1)
  if [ "$HTTP_CODE" != "200" ]; then
    echo "ERROR: Storage upload failed with $HTTP_CODE"
    echo "$UPLOAD_RESULT"
    exit 1
  fi
fi

PUBLIC_URL="${SUPABASE_URL}/storage/v1/object/public/assets/${STORAGE_PATH}"
echo "Public URL: $PUBLIC_URL"

# Build tags array for Postgres
TAGS_PG="{}"
if [ -n "$TAGS" ]; then
  TAGS_PG="{${TAGS}}"
fi

# Build JSON payload
PROMPT_JSON="null"
if [ -n "$PROMPT_BLOCK" ]; then
  PROMPT_JSON=$(python3 -c "import json; print(json.dumps('$PROMPT_BLOCK'))" 2>/dev/null || echo "\"$PROMPT_BLOCK\"")
fi

# Insert into game_assets table
echo "Inserting into game_assets..."
INSERT_RESULT=$(curl -s -w "\n%{http_code}" -X POST \
  "${SUPABASE_URL}/rest/v1/game_assets" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "{
    \"game_tag\": \"${GAME_TAG}\",
    \"character_name\": \"${CHARACTER}\",
    \"asset_type\": \"${ASSET_TYPE}\",
    \"url\": \"${PUBLIC_URL}\",
    \"prompt_block\": ${PROMPT_JSON},
    \"tags\": \"${TAGS_PG}\"
  }")

HTTP_CODE=$(echo "$INSERT_RESULT" | tail -1)
if [ "$HTTP_CODE" = "201" ]; then
  echo "Done! Asset uploaded and registered."
else
  echo "ERROR: Insert failed with $HTTP_CODE"
  echo "$INSERT_RESULT"
  exit 1
fi
