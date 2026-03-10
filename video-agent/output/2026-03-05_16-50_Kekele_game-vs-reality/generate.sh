#!/bin/bash
set -euo pipefail

export SJINN_API_KEY="ee0d1460-d8d6-4d11-97b3-7d814e8ce672"
cd "$(dirname "$0")"

# Character reference images (provided assets)
PIRATE_REF="https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/img_2.png"
DEMON_REF="https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/img_3.png"
KNIGHT_REF="https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/Cosplay%20sources/img_4.png"

CHAR_REFS=("$PIRATE_REF" "$DEMON_REF" "$KNIGHT_REF")

# --- HELPER: create task and poll until done ---
create_and_poll() {
  local PAYLOAD="$1"
  local LABEL="$2"

  echo "[$LABEL] Creating task..."
  RESP=$(curl -s -X POST "https://sjinn.ai/api/un-api/create_tool_task" \
    -H "Authorization: Bearer $SJINN_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

  TASK_ID=$(echo "$RESP" | grep -o '"task_id":"[^"]*"' | sed 's/"task_id":"//;s/"//')
  if [ -z "$TASK_ID" ] || [ "$TASK_ID" = "null" ]; then
    echo "[$LABEL] FAILED to create task: $RESP"
    return 1
  fi
  echo "[$LABEL] Task: $TASK_ID"

  for i in $(seq 1 60); do
    sleep 10
    SR=$(curl -s -X POST "https://sjinn.ai/api/un-api/query_tool_task_status" \
      -H "Authorization: Bearer $SJINN_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"task_id\":\"$TASK_ID\"}")
    STATUS=$(echo "$SR" | grep -o '"status":[0-9-]*' | head -1 | grep -o '[0-9-]*$')
    if [ "$STATUS" = "1" ]; then
      URL=$(echo "$SR" | grep -o '"output_urls":\["[^"]*"' | sed 's/.*\["//' | sed 's/"$//')
      echo "[$LABEL] DONE: $URL"
      echo "$URL"
      return 0
    elif [ "$STATUS" = "-1" ] || [ "$STATUS" = "2" ]; then
      echo "[$LABEL] FAILED (status=$STATUS)"
      return 1
    fi
    echo "[$LABEL] polling... ${i}0s"
  done
  echo "[$LABEL] TIMEOUT"
  return 1
}

# === PHASE 3: IMAGE GENERATION (3 scenes) ===
echo "=== PHASE 3: IMAGE GENERATION (3 scenes) ==="

IMAGE_PROMPTS=(
  "Medieval fantasy village cobblestone street with wooden tavern in background, on the left side a cartoon chibi pirate character with bold black outlines bright flat saturated colors exaggerated large head muscular stocky build pink bandana massive thick ginger beard bare hairy chest blue baggy pants confident cocky grin, on the right side a photorealistic muscular stocky man pink bandana thick ginger beard bare tanned hairy chest blue linen pants brown leather belt weathered sun-darkened skin cocky grin, both standing side by side facing forward matching pose, warm golden afternoon sunlight, medium shot eye level, vertical composition, 9:16 aspect ratio"
  "Dark mystical forest with glowing red magical orbs floating between twisted trees eerie fog, on the left a cartoon chibi demon character with bold black outlines bright flat saturated colors exaggerated very large head tiny body wild spiky crimson red hair pointed ears sharp fangs angry scowling face reddish skin gold chain necklace dark vest clenched fists, on the right a photorealistic young man with wild spiky crimson dyed hair pointed ear tips sharp canine teeth snarl reddish face paint gold thick chain necklace dark leather vest bare chest fierce red eyes lean wiry build, both standing back to back arms crossed menacing pose, crimson red mystical lighting from below, close-up slightly low angle, vertical composition, 9:16 aspect ratio"
  "Stone road leading up green hill toward medieval castle silhouette dramatic orange gold sunset sky banners fluttering, on the left a cartoon chibi knight character with bold black outlines bright flat saturated colors exaggerated large head full gray steel plate armor helmet with orange messy hair sticking out holding large sword marching determined, on the right a photorealistic tall man in full medieval gray steel plate armor with scratches and dents open-faced helmet orange messy hair strong jaw determined grin gauntleted hands gripping steel longsword marching, both side by side marching forward, dramatic golden sunset backlighting, wide shot low angle looking up heroically, vertical composition, 9:16 aspect ratio"
)

SCENE_URLS=()

for i in 0 1 2; do
  SCENE_NUM=$((i + 1))
  PROMPT="${IMAGE_PROMPTS[$i]}"
  REF="${CHAR_REFS[$i]}"

  IMG_LIST="[\"$REF\"]"

  PAYLOAD=$(jq -n --arg prompt "$PROMPT" --argjson img_list "$IMG_LIST" '{
    "tool_type": "nano-banana-image-pro-api",
    "input": {"prompt": $prompt, "aspect_ratio": "9:16", "image_list": $img_list}
  }')

  RESULT=$(create_and_poll "$PAYLOAD" "IMG-$SCENE_NUM")
  URL=$(echo "$RESULT" | tail -1)

  curl -s -o "scene-${SCENE_NUM}.png" "$URL"
  SIZE=$(stat -f%z "scene-${SCENE_NUM}.png" 2>/dev/null || stat -c%s "scene-${SCENE_NUM}.png")
  echo "[IMG-$SCENE_NUM] Downloaded: ${SIZE} bytes"

  SCENE_URLS+=("$URL")
done

echo ""
echo "=== All 3 images generated ==="
ls -la scene-*.png
echo ""

# === PHASE 4: I2V ANIMATION (one at a time) ===
echo "=== PHASE 4: I2V ANIMATION (3 scenes) ==="

MOTION_PROMPTS=(
  'Camera tracks backward smoothly at eye level as both characters walk forward in sync. The cartoon pirate on the left bounces with exaggerated chibi steps, arms swinging wide. The realistic pirate on the right walks with heavy confident swagger. Real pirate strokes his thick beard thoughtfully, cartoon pirate copies the gesture with oversized cartoon hand. Both glance at each other and grin. Cartoon pirate flexes muscles in an exaggerated pose. Warm village atmosphere, dust particles in sunlight.'
  'Camera slowly pushes in from slightly low angle. Both characters stand back to back with arms crossed, perfectly still, menacing. Then both spin around to face the camera simultaneously. Cartoon demon on the left bares tiny sharp fangs with an exaggerated snarl. Real demon on the right leans toward camera with an intense fierce snarl. Cartoon demon jumps up behind him with fists raised in tiny rage. Red magical orbs pulse brighter. Eerie fog swirls at their feet. Intense dark energy.'
  'Camera holds at low angle looking up heroically as both characters march forward side by side. Heavy armor clanks with each step. Cartoon knight on the left marches with bouncy exaggerated steps, then points forward at the castle with oversized gauntlet. Real knight on the right nods firmly. Both slow their march, then raise their swords high above their heads in triumphant salute. Sunset blazes behind them, golden light silhouettes their raised weapons. Wind catches hair and banners. Epic heroic finale energy.'
)

PREV_MP4_SIZE=0

for i in 0 1 2; do
  SCENE_NUM=$((i + 1))
  IMAGE_URL="${SCENE_URLS[$i]}"
  MOTION="${MOTION_PROMPTS[$i]}"

  PAYLOAD=$(jq -n --arg prompt "$MOTION" --arg image "$IMAGE_URL" '{
    "tool_type": "veo3-image-to-video-fast-api",
    "input": {"prompt": $prompt, "image": $image, "aspect_ratio": "9:16"}
  }')

  RESULT=$(create_and_poll "$PAYLOAD" "I2V-$SCENE_NUM")
  URL=$(echo "$RESULT" | tail -1)

  curl -s -o "scene-${SCENE_NUM}.mp4" "$URL"
  SIZE=$(stat -f%z "scene-${SCENE_NUM}.mp4" 2>/dev/null || stat -c%s "scene-${SCENE_NUM}.mp4")
  echo "[I2V-$SCENE_NUM] Downloaded: ${SIZE} bytes"

  # VALIDATION: check not duplicate
  if [ "$SIZE" -eq "$PREV_MP4_SIZE" ] && [ "$SCENE_NUM" -gt 1 ]; then
    echo "[I2V-$SCENE_NUM] WARNING: Same size as previous ($SIZE bytes)! Retrying..."
    RESULT2=$(create_and_poll "$PAYLOAD" "I2V-$SCENE_NUM-RETRY")
    URL2=$(echo "$RESULT2" | tail -1)
    curl -s -o "scene-${SCENE_NUM}.mp4" "$URL2"
    SIZE=$(stat -f%z "scene-${SCENE_NUM}.mp4" 2>/dev/null || stat -c%s "scene-${SCENE_NUM}.mp4")
    echo "[I2V-$SCENE_NUM-RETRY] Downloaded: ${SIZE} bytes"
  fi

  if [ "$SIZE" -lt 1000 ]; then
    echo "[I2V-$SCENE_NUM] ERROR: File too small ($SIZE bytes)! Generation may have failed."
  fi

  PREV_MP4_SIZE=$SIZE
done

echo ""
echo "=== All 3 I2V clips generated ==="
ls -la scene-*.mp4
echo ""
echo "DONE"
