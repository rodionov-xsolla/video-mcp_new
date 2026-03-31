#!/bin/bash
set -euo pipefail

export SJINN_API_KEY="ee0d1460-d8d6-4d11-97b3-7d814e8ce672"
CHAR_REF="https://edit.comfyonline.app/result/737c36d0-3c5f-427c-b519-6435ad9625e2.jpg"
cd "$(dirname "$0")"

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

# === PHASE 3: IMAGE GENERATION ===
echo "=== PHASE 3: IMAGE GENERATION (5 scenes) ==="

IMAGE_PROMPTS=(
  "Oxide Survival Island game style, semi-realistic 3D graphics, tropical island survival atmosphere, gritty post-apocalyptic aesthetic, warm natural lighting, young male survivor noob, torn gray t-shirt, worn khaki shorts, barefoot, messy brown hair, thin scrawny build, sunburned skin, standing next to tiny crooked wooden shack arms spread proudly presenting it, proud beaming grin, jungle clearing with palm trees and small crude wooden shelter with gaps in walls, warm golden hour sunlight volumetric rays through palms, jungle green and sand beige tones, close-up eye level shot, vertical composition, 9:16 aspect ratio"
  "Oxide Survival Island game style, semi-realistic 3D graphics, tropical island survival atmosphere, gritty post-apocalyptic aesthetic, warm natural lighting, young male survivor noob, torn gray t-shirt, worn khaki shorts, barefoot, messy brown hair, thin scrawny build, sunburned skin, kneeling on ground reaching out desperately with right hand, devastated heartbroken teary eyes, eyes locked on the girl ahead of him, in the background slightly blurred young woman in red tank top walking away with her back to camera long dark hair in ponytail, tropical jungle clearing with collapsed wooden debris, warm golden hour sunlight, jungle green and sand tones, wide shot slightly high angle, vertical composition, 9:16 aspect ratio"
  "Oxide Survival Island game style, semi-realistic 3D graphics, tropical island survival atmosphere, gritty post-apocalyptic aesthetic, warm natural lighting, young male survivor noob, torn gray t-shirt, worn khaki shorts, barefoot, messy brown hair, thin scrawny build, sunburned skin, swinging stone hatchet into tree trunk with force, fierce clenched jaw narrowed eyes gritted teeth sweat dripping down face, deep jungle clearing chopped stumps pile of wood and stone half-built wooden wall frame rising, golden light filtering through canopy, warm golden tones, medium shot low angle looking up heroically, vertical composition, 9:16 aspect ratio"
  "Oxide Survival Island game style, semi-realistic 3D graphics, tropical island survival atmosphere, gritty post-apocalyptic aesthetic, warm natural lighting, young male survivor now wearing crude metal chest plate and leather gear, messy brown hair, standing atop massive multi-story wooden and stone fortress as powerful silhouette against dramatic orange sunset, steely determined gaze, huge fortified base with walls towers and metal gates below, island panorama ocean jungle, dramatic golden sunset volumetric rays, warm orange and gold tones, dynamic high angle panoramic shot, vertical composition, 9:16 aspect ratio"
  "Oxide Survival Island game style, semi-realistic 3D graphics, tropical island survival atmosphere, gritty post-apocalyptic aesthetic, warm natural lighting, young male survivor in upgraded leather armor with crude gear, messy brown hair, standing confidently in center, calm dismissive half-smile one eyebrow raised, glancing toward the right side of frame, four armed clan members in mixed armor standing behind him in formation, massive fortress gate with hanging cloth banners behind, warm golden sunset light, earthy tones with metal accents, medium shot straight on balanced composition, vertical composition, 9:16 aspect ratio"
)

SCENE_URLS=()
PREV_URL=""

for i in 0 1 2 3 4; do
  SCENE_NUM=$((i + 1))
  PROMPT="${IMAGE_PROMPTS[$i]}"

  if [ -z "$PREV_URL" ]; then
    IMG_LIST="[\"$CHAR_REF\"]"
  else
    IMG_LIST="[\"$CHAR_REF\",\"$PREV_URL\"]"
  fi

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
  PREV_URL="$URL"
done

echo ""
echo "=== All 5 images generated ==="
ls -la scene-*.png
echo ""

# === PHASE 4: I2V ANIMATION (one at a time) ===
echo "=== PHASE 4: I2V ANIMATION (5 scenes) ==="

MOTION_PROMPTS=(
  'Camera holds steady at close-up eye level. Character smiles proudly, gestures at the tiny shack behind him, pats the wooden wall with his hand. The wall wobbles. His smile freezes. More planks crack and fall. The whole shack collapses into a pile of wood behind him. Character grabs his head with both hands, mouth wide open. The character proudly says: "Check it out! My first base! It is perf--" then screams: "oh no no no!" Steady shot, comedy timing.'
  'Camera slowly pulls back from slightly above. Character kneels near collapsed debris, reaching toward the girl walking away in the background. His eyes follow her as she moves further away. She does not look back. Character lowers his hand slowly. His teary expression shifts to clenched jaw. He balls his fist and stands up. The character desperately calls: "Wait! Where are you going?!" then quietly with resolve: "Fine. Fine!" Slow dolly back, heartbreak transitioning to determination.'
  'Camera holds at low angle looking up heroically. Character swings hatchet hard into tree, wood chips explode. He grunts, wipes sweat from forehead with arm. Bends down, grabs logs, hoists them onto shoulder. Carries them to the half-built wall frame. Sets them down, steps back, looks up at the rising wooden structure. Nods once with quiet satisfaction. The character speaks through gritted teeth: "They think I am done? I will show them ALL." Steady heroic low angle, golden backlight, training montage energy.'
  'Camera starts high showing the massive fortress from above. Character stands as silhouette on top, wind blowing hair, arms at sides, surveying the island. Then camera swoops down and pushes forward aggressively as character charges in crude armor. Explosions erupt around him, fire and debris. Enemy wooden walls crack and collapse. Smoke billows. The character screams with fury: "Who is the noob NOW?!" Epic panorama crashing into aggressive battle push.'
  'Camera holds steady at medium shot, balanced frame. Girl approaches slowly from the right side of frame, hopeful smile, reaching out hand. Character glances at her briefly with calm half-smile. He raises one hand flat to stop her. Shakes head once slowly. Turns his back and walks toward his fortress. Four armed clan members behind him nod and part to let him through. Gates creak open. The character calmly says: "Sorry. I got my crew now." Steady power shot, zero camera movement, letting the rejection land.'
)

PREV_MP4_SIZE=0

for i in 0 1 2 3 4; do
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
echo "=== All 5 I2V clips generated ==="
ls -la scene-*.mp4
echo ""
echo "DONE"
