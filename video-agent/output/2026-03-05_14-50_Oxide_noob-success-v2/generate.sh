#!/bin/bash
set -euo pipefail

export SJINN_API_KEY="ee0d1460-d8d6-4d11-97b3-7d814e8ce672"
CHAR_REF="https://edit.comfyonline.app/result/737c36d0-3c5f-427c-b519-6435ad9625e2.jpg"
OUTPUT_DIR="$(dirname "$0")"
cd "$OUTPUT_DIR"

# --- HELPER: create task and poll until done ---
create_and_poll() {
  local TOOL_TYPE="$1"
  local PAYLOAD="$2"
  local LABEL="$3"

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

# === PHASE 3: IMAGE GENERATION (sequential with chain ref) ===
echo "=== PHASE 3: IMAGE GENERATION ==="

IMAGE_PROMPTS=(
  "Oxide Survival Island game style, semi-realistic 3D graphics, tropical island survival atmosphere, gritty post-apocalyptic aesthetic, warm natural lighting, young male survivor noob, torn gray t-shirt, worn khaki shorts, barefoot, messy brown hair, thin scrawny build, sunburned skin, standing next to tiny crooked wooden shack presenting it proudly, proud beaming grin, jungle clearing with palm trees and small crude wooden shelter, young woman in red tank top visible walking away in background, warm golden hour sunlight volumetric rays, jungle green and sand beige tones, close-up eye level, vertical composition, 9:16 aspect ratio"
  "Oxide Survival Island game style, semi-realistic 3D graphics, tropical island survival atmosphere, gritty post-apocalyptic aesthetic, warm natural lighting, young male survivor noob, torn gray t-shirt, worn khaki shorts, barefoot, messy brown hair, thin scrawny build, sunburned skin, swinging stone hatchet into tree trunk with force, fierce clenched jaw narrowed vengeful eyes gritted teeth sweat dripping, deep jungle clearing chopped stumps growing pile of wood and stone half-built walls rising, golden light filtering through canopy, warm golden tones, medium shot low angle looking up heroically, vertical composition, 9:16 aspect ratio"
  "Oxide Survival Island game style, semi-realistic 3D graphics, tropical island survival atmosphere, gritty post-apocalyptic aesthetic, warm natural lighting, young male survivor now wearing crude metal chest armor holding rifle, messy brown hair, standing atop massive multi-story wooden and stone fortress silhouette against dramatic orange sunset, steely determined gaze arms crossed, huge fortified base with walls towers metal gates, island panorama ocean jungle below, dramatic golden sunset light volumetric rays, warm orange gold tones, wide dramatic low angle from below, vertical composition, 9:16 aspect ratio"
  "Oxide Survival Island game style, semi-realistic 3D graphics, tropical island survival atmosphere, gritty post-apocalyptic aesthetic, warm natural lighting, young male survivor in upgraded leather armor with gear, messy brown hair, standing confidently in center, calm dismissive half-smile one eyebrow raised, four armed clan members in metal armor standing behind in formation, young woman in red tank top approaching from side with pleading face, massive fortress gate with hanging clan banners, warm golden sunset light, earthy tones metal accents, medium shot straight on, vertical composition, 9:16 aspect ratio"
)

SCENE_URLS=()
PREV_URL=""

for i in 0 1 2 3; do
  SCENE_NUM=$((i + 1))
  PROMPT="${IMAGE_PROMPTS[$i]}"

  # Build image_list JSON
  if [ -z "$PREV_URL" ]; then
    IMG_LIST="[\"$CHAR_REF\"]"
  else
    IMG_LIST="[\"$CHAR_REF\",\"$PREV_URL\"]"
  fi

  PAYLOAD=$(jq -n --arg prompt "$PROMPT" --argjson img_list "$IMG_LIST" '{
    "tool_type": "nano-banana-image-pro-api",
    "input": {"prompt": $prompt, "aspect_ratio": "9:16", "image_list": $img_list}
  }')

  RESULT=$(create_and_poll "nano-banana-image-pro-api" "$PAYLOAD" "IMG-$SCENE_NUM")
  URL=$(echo "$RESULT" | tail -1)

  # Download
  curl -s -o "scene-${SCENE_NUM}.png" "$URL"
  SIZE=$(stat -f%z "scene-${SCENE_NUM}.png" 2>/dev/null || stat -c%s "scene-${SCENE_NUM}.png")
  echo "[IMG-$SCENE_NUM] Downloaded: ${SIZE} bytes"

  SCENE_URLS+=("$URL")
  PREV_URL="$URL"
done

echo ""
echo "=== All 4 images generated ==="
ls -la scene-*.png
echo ""

# === PHASE 4: I2V ANIMATION (one at a time with validation) ===
echo "=== PHASE 4: I2V ANIMATION ==="

MOTION_PROMPTS=(
  'Camera starts close on the characters proud face as he gestures at his tiny shack. First 4 seconds: the shack wobbles, planks fall, whole thing collapses. Characters grin freezes into shock. Then: camera pulls back to reveal the girl in red walking away toward a tall armored figure by a huge metal base. Character drops to knees, reaching out. The character proudly says: "Check it out! My first base!" then desperately yells: "Wait, babe, where are you going?!" Close-up comedy shifting to wide dolly-back heartbreak.'
  'Camera holds at low angle looking up, making the character look larger than life. Character swings hatchet hard into tree, wood chips explode outward. Wipes forehead with arm, grabs logs, carries them. Behind him wooden walls are rising. He works with fury and purpose. The character speaks through gritted teeth: "They think I am done? I will show them ALL." Steady heroic low angle, training montage intensity, golden backlight through trees.'
  'Camera tilts up slowly revealing the massive fortress scale. First 3 seconds: character stands silhouetted on top against sunset, wind in hair, arms crossed. Then hard cut to action: camera pushes forward aggressively as character charges in armor through explosions and smoke. Enemy base walls crack and collapse. Fire erupts. Armored raider falls backward. The character screams: "Who is the noob NOW?!" Dramatic reveal transitioning to aggressive battle push.'
  'Camera holds steady at medium shot, balanced frame. Girl approaches slowly from the right, hopeful smile, reaching out her hand. Character glances at her briefly with a calm half-smile. He raises one hand flat to stop her. Shakes his head once. Turns his back and walks toward his fortress. Behind him four armed clan members nod and follow. Gates creak open. The character calmly says: "Sorry. I got my crew now." Steady power shot, no camera movement, letting the rejection land.'
)

PREV_MP4_SIZE=0

for i in 0 1 2 3; do
  SCENE_NUM=$((i + 1))
  IMAGE_URL="${SCENE_URLS[$i]}"
  MOTION="${MOTION_PROMPTS[$i]}"

  PAYLOAD=$(jq -n --arg prompt "$MOTION" --arg image "$IMAGE_URL" '{
    "tool_type": "veo3-image-to-video-fast-api",
    "input": {"prompt": $prompt, "image": $image, "aspect_ratio": "9:16"}
  }')

  RESULT=$(create_and_poll "veo3-image-to-video-fast-api" "$PAYLOAD" "I2V-$SCENE_NUM")
  URL=$(echo "$RESULT" | tail -1)

  # Download
  curl -s -o "scene-${SCENE_NUM}.mp4" "$URL"
  SIZE=$(stat -f%z "scene-${SCENE_NUM}.mp4" 2>/dev/null || stat -c%s "scene-${SCENE_NUM}.mp4")
  echo "[I2V-$SCENE_NUM] Downloaded: ${SIZE} bytes"

  # VALIDATION: check not duplicate of previous
  if [ "$SIZE" -eq "$PREV_MP4_SIZE" ] && [ "$SCENE_NUM" -gt 1 ]; then
    echo "[I2V-$SCENE_NUM] WARNING: Same size as previous! Possible duplicate. Retrying..."
    # Retry once
    RESULT2=$(create_and_poll "veo3-image-to-video-fast-api" "$PAYLOAD" "I2V-$SCENE_NUM-RETRY")
    URL2=$(echo "$RESULT2" | tail -1)
    curl -s -o "scene-${SCENE_NUM}.mp4" "$URL2"
    SIZE=$(stat -f%z "scene-${SCENE_NUM}.mp4" 2>/dev/null || stat -c%s "scene-${SCENE_NUM}.mp4")
    echo "[I2V-$SCENE_NUM-RETRY] Downloaded: ${SIZE} bytes"
  fi

  PREV_MP4_SIZE=$SIZE
done

echo ""
echo "=== All 4 I2V clips generated ==="
ls -la scene-*.mp4
echo ""
echo "DONE"
