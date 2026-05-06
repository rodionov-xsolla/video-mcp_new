#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
GAMES_DIR="$BASE_DIR/games"

source "$BASE_DIR/.env"

SB_URL="$SUPABASE_URL"
SB_KEY="$SUPABASE_SERVICE_ROLE_KEY"
BUCKET="assets"

NB2_ENDPOINT="https://queue.fal.run/fal-ai/nano-banana-2"
GPT2_SUBMIT="https://queue.fal.run/fal-ai/gpt-image-2/edit"
GPT2_POLL="https://queue.fal.run/fal-ai/gpt-image-2"
POLL_INTERVAL=5
MAX_POLLS=60
GPT2_MAX_RETRIES=5
GPT2_RETRY_DELAY=15

FORCE=false
TARGET_CHARACTER=""
ALL_GAMES=false
GAME_TAG=""
ENGINE="nb2"
STYLE_REF_URL=""

usage() {
  cat <<'USAGE'
Usage:
  gen-character-cards.sh <game-tag>                          # NB2, all characters
  gen-character-cards.sh <game-tag> --engine gpt2            # GPT Image 2 low
  gen-character-cards.sh <game-tag> --engine gpt2 --ref-url URL  # GPT2 + style ref
  gen-character-cards.sh <game-tag> --character "Kirk"        # single character
  gen-character-cards.sh <game-tag> --force                   # regenerate existing
  gen-character-cards.sh --all                                # all games
  gen-character-cards.sh --all --force                        # regenerate everything

Engines:
  nb2   — Nano Banana 2 (Gemini), $0.04/img, good style control (default)
  gpt2  — GPT Image 2 low via edit endpoint, $0.01/img, needs ref for style
          Auto-detects *-ref.png in game refs/ dir as style anchor.
          Use --ref-url to override.

Output: games/{game-tag}/assets/refs/{slug}-sheet.png
Also uploads to Supabase: assets/{game-tag}/refs/{slug}-sheet.png
USAGE
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) FORCE=true; shift ;;
    --all) ALL_GAMES=true; shift ;;
    --character) TARGET_CHARACTER="$2"; shift 2 ;;
    --engine) ENGINE="$2"; shift 2 ;;
    --ref-url) STYLE_REF_URL="$2"; shift 2 ;;
    --help|-h) usage ;;
    -*) echo "Unknown flag: $1" >&2; usage ;;
    *) GAME_TAG="$1"; shift ;;
  esac
done

if [[ "$ALL_GAMES" = false && -z "$GAME_TAG" ]]; then
  echo "Error: specify <game-tag> or --all" >&2
  usage
fi

slugify() {
  echo "$1" | python3 -c "
import sys, re
name = sys.stdin.read().strip()
slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
print(slug)
"
}

parse_game_config() {
  local MD_FILE="$1"
  python3 -c "
import re, json, sys

text = open(sys.argv[1], encoding='utf-8').read()

# Extract prompt prefix from code block
prefix_match = re.search(r'### Prompt prefix\n\`\`\`\n(.+?)\n\`\`\`', text, re.DOTALL)
prefix = prefix_match.group(1).strip() if prefix_match else ''

# Extract Character Prompt Blocks section
blocks_section = re.split(r'^## Character Prompt Blocks', text, flags=re.MULTILINE)
if len(blocks_section) < 2:
    print(json.dumps({'prefix': prefix, 'characters': {}}))
    sys.exit(0)

section_text = blocks_section[1]
end_match = re.search(r'^## ', section_text, re.MULTILINE)
if end_match:
    section_text = section_text[:end_match.start()]

characters = {}
raw_names = []
for m in re.finditer(r'###\s+(.+?)\n\`([^\`]+)\`', section_text):
    raw_names.append((m.group(1).strip(), m.group(2).strip()))

# Detect base name collisions to decide whether to keep parenthetical
base_counts = {}
for raw_name, _ in raw_names:
    base = re.sub(r'\s*\(.*?\)\s*$', '', raw_name).strip()
    base_counts[base] = base_counts.get(base, 0) + 1

for raw_name, desc in raw_names:
    base = re.sub(r'\s*\(.*?\)\s*$', '', raw_name).strip()
    # Keep parenthetical only if base name has duplicates (e.g. Pirate cartoon vs realistic)
    if base_counts.get(base, 1) > 1:
        name = raw_name
    else:
        name = base
    characters[name] = desc

print(json.dumps({'prefix': prefix, 'characters': characters}, ensure_ascii=False))
" "$MD_FILE"
}

extract_equipment() {
  local DESC="$1"
  python3 -c "
import re, sys
desc = sys.argv[1]

# Split description into comma-separated phrases, find ones with equipment keywords
equipment_keywords = [
    'sword', 'rapier', 'dagger', 'knife', 'blade',
    'bow', 'crossbow', 'rifle', 'gun', 'phaser', 'pistol',
    'shield', 'armor', 'helmet', 'gauntlet', 'vest',
    'badge', 'combadge', 'necklace', 'chain', 'pendant',
    'cape', 'cloak', 'sash', 'baldric', 'belt',
    'staff', 'wand', 'umbrella', 'torch', 'tool',
    'crown', 'hat', 'bandana', 'headband', 'sunglasses',
    'implant', 'eye-piece', 'tubes', 'circuitry',
    'catsuit', 'uniform', 'tunic', 'outfit', 'bodysuit'
]
phrases = [p.strip() for p in desc.split(',')]
items = []
for phrase in phrases:
    phrase_lower = phrase.lower()
    for kw in equipment_keywords:
        if kw in phrase_lower:
            clean = phrase.strip().rstrip('.')
            if clean and clean not in items:
                items.append(clean)
            break

if items:
    print(', '.join(items[:6]))
else:
    print('character accessories and signature items')
" "$DESC"
}

nb2_generate() {
  local PROMPT="$1"
  local ASPECT="$2"
  local OUT_FILE="$3"

  local BODY
  BODY=$(python3 -c "
import json, sys
print(json.dumps({
    'prompt': sys.argv[1],
    'aspect_ratio': sys.argv[2],
    'output_format': 'png',
    'safety_tolerance': '5'
}))
" "$PROMPT" "$ASPECT")

  local REQ_ID
  REQ_ID=$(curl -s -X POST "$NB2_ENDPOINT" \
    -H "Authorization: Key $FAL_KEY" \
    -H "Content-Type: application/json" \
    -d "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('request_id','FAIL'))")

  if [[ "$REQ_ID" = "FAIL" || -z "$REQ_ID" ]]; then
    echo "  ERROR: Failed to submit NB2 request" >&2
    return 1
  fi
  echo "  Submitted: $REQ_ID" >&2

  for i in $(seq 1 $MAX_POLLS); do
    local ST
    ST=$(curl -s "$NB2_ENDPOINT/requests/$REQ_ID/status" \
      -H "Authorization: Key $FAL_KEY" \
      | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','?'))" 2>/dev/null)

    if [[ "$ST" = "COMPLETED" ]]; then
      local IMG_URL
      IMG_URL=$(curl -s "$NB2_ENDPOINT/requests/$REQ_ID" \
        -H "Authorization: Key $FAL_KEY" \
        | python3 -c "import sys,json; print(json.load(sys.stdin)['images'][0]['url'])")
      curl -s -o "$OUT_FILE" "$IMG_URL"
      local SZ
      SZ=$(wc -c < "$OUT_FILE" | tr -d ' ')
      if [[ "$SZ" -lt 1000 ]]; then
        echo "  ERROR: Downloaded file too small (${SZ} bytes)" >&2
        return 1
      fi
      echo "  Downloaded: ${SZ} bytes → $OUT_FILE" >&2
      return 0
    elif [[ "$ST" = "FAILED" ]]; then
      echo "  FAILED!" >&2
      return 1
    fi
    sleep $POLL_INTERVAL
  done
  echo "  TIMEOUT after $((MAX_POLLS * POLL_INTERVAL))s" >&2
  return 1
}

find_style_ref() {
  local REFS_DIR="$1"
  if [[ -n "$STYLE_REF_URL" ]]; then
    echo "$STYLE_REF_URL"
    return 0
  fi
  local REF_FILE
  REF_FILE=$(ls "$REFS_DIR"/*-ref.png 2>/dev/null | head -1)
  if [[ -n "$REF_FILE" ]]; then
    local REF_NAME
    REF_NAME=$(basename "$REF_FILE")
    local GAME_DIR_NAME
    GAME_DIR_NAME=$(basename "$(dirname "$(dirname "$REFS_DIR")")")
    local SB_PATH="${GAME_DIR_NAME}/refs/${REF_NAME}"
    upload_sb "$REF_FILE" "$SB_PATH" 2>/dev/null
    return 0
  fi
  echo ""
}

gpt2_generate() {
  local PROMPT="$1"
  local OUT_FILE="$2"
  local REF_URLS_JSON="$3"

  local BODY
  BODY=$(python3 -c "
import json, sys
refs = json.loads(sys.argv[2]) if sys.argv[2] else []
d = {
    'prompt': sys.argv[1],
    'image_size': {'width': 1920, 'height': 1080},
    'quality': 'low',
    'output_format': 'png'
}
if refs:
    d['image_urls'] = refs
print(json.dumps(d))
" "$PROMPT" "$REF_URLS_JSON")

  local ENDPOINT
  if [[ "$REF_URLS_JSON" != "[]" && -n "$REF_URLS_JSON" ]]; then
    ENDPOINT="$GPT2_SUBMIT"
  else
    ENDPOINT="${GPT2_POLL}"
  fi

  for attempt in $(seq 1 $GPT2_MAX_RETRIES); do
    if [[ $attempt -gt 1 ]]; then
      echo "    retry $attempt/$GPT2_MAX_RETRIES..." >&2
      sleep $GPT2_RETRY_DELAY
    fi

    local REQ_ID
    REQ_ID=$(curl -s -X POST "$ENDPOINT" \
      -H "Authorization: Key $FAL_KEY" \
      -H "Content-Type: application/json" \
      -d "$BODY" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('request_id','FAIL'))")

    if [[ "$REQ_ID" = "FAIL" || -z "$REQ_ID" ]]; then
      echo "    submit failed" >&2
      continue
    fi

    for i in $(seq 1 $MAX_POLLS); do
      local ST
      ST=$(curl -s "$GPT2_POLL/requests/$REQ_ID/status" \
        -H "Authorization: Key $FAL_KEY" \
        | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','?'))" 2>/dev/null)

      if [[ "$ST" = "COMPLETED" ]]; then
        local RESULT
        RESULT=$(curl -s "$GPT2_POLL/requests/$REQ_ID" \
          -H "Authorization: Key $FAL_KEY")
        local IMG_URL
        IMG_URL=$(echo "$RESULT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'images' in d and len(d.get('images',[])) > 0:
    print(d['images'][0]['url'])
else:
    print('FAIL')
")
        if [[ "$IMG_URL" = "FAIL" ]]; then
          echo "    completed but no images" >&2
          break
        fi
        curl -s -o "$OUT_FILE" "$IMG_URL"
        local SZ
        SZ=$(wc -c < "$OUT_FILE" | tr -d ' ')
        if [[ "$SZ" -lt 1000 ]]; then
          echo "    file too small (${SZ} bytes)" >&2
          break
        fi
        echo "  Downloaded: ${SZ} bytes → $OUT_FILE" >&2
        return 0
      elif [[ "$ST" = "FAILED" ]]; then
        echo "    generation failed" >&2
        break
      fi
      sleep $POLL_INTERVAL
    done
  done

  echo "  GAVE UP after $GPT2_MAX_RETRIES attempts" >&2
  return 1
}

upload_sb() {
  local FILE="$1"
  local REMOTE_PATH="$2"
  curl -s -X POST "${SB_URL}/storage/v1/object/${BUCKET}/${REMOTE_PATH}" \
    -H "Authorization: Bearer ${SB_KEY}" \
    -H "Content-Type: image/png" \
    -H "x-upsert: true" \
    --data-binary "@${FILE}" > /dev/null
  echo "${SB_URL}/storage/v1/object/public/${BUCKET}/${REMOTE_PATH}"
}

generate_for_game() {
  local GAME="$1"
  local MD_FILE="$GAMES_DIR/$GAME/$GAME.md"

  if [[ ! -f "$MD_FILE" ]]; then
    echo "SKIP: $MD_FILE not found" >&2
    return 0
  fi

  local REFS_DIR="$GAMES_DIR/$GAME/assets/refs"
  mkdir -p "$REFS_DIR"

  echo "=== $GAME (engine: $ENGINE) ===" >&2

  local STYLE_REF_FOR_GAME=""
  if [[ "$ENGINE" = "gpt2" ]]; then
    STYLE_REF_FOR_GAME=$(find_style_ref "$REFS_DIR")
    if [[ -n "$STYLE_REF_FOR_GAME" ]]; then
      echo "  Style ref: $STYLE_REF_FOR_GAME" >&2
    else
      echo "  No style ref found, GPT2 will use text-to-image only" >&2
    fi
  fi

  local CONFIG
  CONFIG=$(parse_game_config "$MD_FILE")

  local PREFIX
  PREFIX=$(echo "$CONFIG" | python3 -c "import sys,json; print(json.load(sys.stdin)['prefix'])")

  local CHAR_NAMES
  CHAR_NAMES=$(echo "$CONFIG" | python3 -c "
import sys, json
cfg = json.load(sys.stdin)
for name in cfg['characters']:
    print(name)
")

  local GENERATED=0
  local SKIPPED=0
  local FAILED=0

  while IFS= read -r CHAR_NAME; do
    [[ -z "$CHAR_NAME" ]] && continue

    if [[ -n "$TARGET_CHARACTER" && "$CHAR_NAME" != *"$TARGET_CHARACTER"* ]]; then
      continue
    fi

    local SLUG
    SLUG=$(slugify "$CHAR_NAME")
    local OUT_FILE="$REFS_DIR/${SLUG}-sheet.png"

    if [[ -f "$OUT_FILE" && "$FORCE" = false ]]; then
      echo "  SKIP: $CHAR_NAME (exists: $OUT_FILE)" >&2
      SKIPPED=$((SKIPPED + 1))
      continue
    fi

    local CHAR_DESC
    CHAR_DESC=$(echo "$CONFIG" | python3 -c "
import sys, json
cfg = json.load(sys.stdin)
print(cfg['characters'].get(sys.argv[1], ''))
" "$CHAR_NAME")

    if [[ -z "$CHAR_DESC" ]]; then
      echo "  SKIP: $CHAR_NAME (no description)" >&2
      SKIPPED=$((SKIPPED + 1))
      continue
    fi

    local EQUIPMENT
    EQUIPMENT=$(extract_equipment "$CHAR_DESC")

    echo "  Generating: $CHAR_NAME → $OUT_FILE" >&2
    echo "  Equipment: $EQUIPMENT" >&2

    local GEN_OK=false
    if [[ "$ENGINE" = "gpt2" ]]; then
      local GPT2_STYLE="3D animated character in Pixar-quality CGI render style exactly matching the uploaded reference images. Smooth matte plastic-like skin with subtle subsurface scattering, large expressive cartoon eyes, slightly oversized head proportions, rounded stylized facial features, soft diffused studio lighting with warm fill light. This is a 3D animated character like from a Pixar or DreamWorks movie, absolutely not photorealistic, not live-action photography."
      local PROMPT="character reference sheet, concept art turnaround, professional game art layout, ${GPT2_STYLE}, ${PREFIX}, ${CHAR_DESC}, large full body front-facing view in the right half of the image, full body back view on the left side slightly smaller, isolated key equipment items shown separately around the figures: ${EQUIPMENT}, clean pure white background, soft even diffused lighting, no text labels no watermarks, horizontal composition, 16:9 aspect ratio"
      local REF_JSON="[]"
      if [[ -n "$STYLE_REF_FOR_GAME" ]]; then
        REF_JSON="[\"${STYLE_REF_FOR_GAME}\"]"
      fi
      gpt2_generate "$PROMPT" "$OUT_FILE" "$REF_JSON" && GEN_OK=true
    else
      local PROMPT="character reference sheet, concept art, professional game art layout, ${PREFIX}, ${CHAR_DESC}, large full body front-facing view in the right half of the image, full body back view on the left side slightly smaller, isolated key equipment items shown separately around the figures: ${EQUIPMENT}, clean white background, soft even lighting, no text labels no watermarks, horizontal composition, 16:9 aspect ratio"
      nb2_generate "$PROMPT" "16:9" "$OUT_FILE" && GEN_OK=true
    fi

    if [[ "$GEN_OK" = true ]]; then
      local SB_PATH="${GAME}/refs/${SLUG}-sheet.png"
      local PUBLIC_URL
      PUBLIC_URL=$(upload_sb "$OUT_FILE" "$SB_PATH")
      echo "  Uploaded: $PUBLIC_URL" >&2
      GENERATED=$((GENERATED + 1))
    else
      echo "  FAILED: $CHAR_NAME" >&2
      FAILED=$((FAILED + 1))
    fi

    echo "" >&2
  done <<< "$CHAR_NAMES"

  local UNIT_COST="0.04"
  [[ "$ENGINE" = "gpt2" ]] && UNIT_COST="0.01"
  echo "--- $GAME: generated=$GENERATED skipped=$SKIPPED failed=$FAILED cost=\$$(echo "$GENERATED * $UNIT_COST" | bc) ($ENGINE) ---" >&2
}

# Main
TOTAL_START=$(date +%s)

if [[ "$ALL_GAMES" = true ]]; then
  for GAME_DIR in "$GAMES_DIR"/*/; do
    GAME=$(basename "$GAME_DIR")
    [[ -f "$GAMES_DIR/$GAME/$GAME.md" ]] && generate_for_game "$GAME"
  done
else
  generate_for_game "$GAME_TAG"
fi

TOTAL_END=$(date +%s)
echo "" >&2
echo "=== DONE in $((TOTAL_END - TOTAL_START))s ===" >&2
