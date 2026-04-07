#!/bin/bash

FFMPEG="/usr/local/bin/ffmpeg"
FFMPEG_FULL="/usr/local/bin/ffmpeg-full/ffmpeg"
FFPROBE="/usr/local/bin/ffprobe"
OUT="/Users/admin/conductor/workspaces/video-mcp-new/brasilia/video-agent/output/2026-04-06_star-trek-timelines_serial-drama-ep1"
SC="$OUT/scenes"

echo "=== Step 1: Scale I2V clips to 1080x1920, 30fps + add silent audio ==="

for i in 1 4 7 9; do
  echo "Scaling scene-$i (I2V)..."
  VID_DUR=$($FFPROBE -v error -show_entries format=duration -of csv=p=0 "$SC/scene-$i/scene-$i.mp4")
  echo "  video dur: ${VID_DUR}s"
  $FFMPEG -y -i "$SC/scene-$i/scene-$i.mp4" \
    -f lavfi -i "anullsrc=r=44100:cl=stereo" \
    -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
    -map 0:v -map 1:a -t "$VID_DUR" \
    -r 30 -c:v libx264 -crf 18 -preset fast \
    -ar 44100 -ac 2 -c:a aac -b:a 128k \
    "$SC/scene-$i/scene-$i-scaled.mp4"
  echo "  done"
done

echo ""
echo "=== Step 2: Prepare I2V finals ==="

# Scene 1: no TTS — just copy scaled (brainrot overlay added in step 4)
cp "$SC/scene-1/scene-1-scaled.mp4" "$SC/scene-1/scene-1-final.mp4"
echo "Scene-1: copied"

# Scene 4: Chekov TTS overlay (muffled behind glass), adelay 500ms
TTS_DUR=$($FFPROBE -v error -show_entries format=duration -of csv=p=0 "$SC/scene-4/tts-4.mp3")
CLIP_DUR=$(python3 -c "print(round(0.5 + $TTS_DUR + 1.0, 3))")
echo "Scene-4 TTS dur: ${TTS_DUR}s, clip target: ${CLIP_DUR}s"
$FFMPEG -y -i "$SC/scene-4/scene-4-scaled.mp4" -i "$SC/scene-4/tts-4.mp3" \
  -filter_complex "[1:a]adelay=500|500,aecho=0.8:0.9:10:0.3[tts];[0:a][tts]amix=inputs=2:duration=first,apad[a]" \
  -map 0:v -map "[a]" -t "$CLIP_DUR" \
  -c:v libx264 -crf 18 -preset fast \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  "$SC/scene-4/scene-4-final.mp4"
echo "Scene-4: done"

# Scene 7: pure silence
cp "$SC/scene-7/scene-7-scaled.mp4" "$SC/scene-7/scene-7-final.mp4"
echo "Scene-7: copied"

# Scene 9: pure silence (cliffhanger)
cp "$SC/scene-9/scene-9-scaled.mp4" "$SC/scene-9/scene-9-final.mp4"
echo "Scene-9: copied"

echo ""
echo "=== Step 3: Scale Avatar clips + trim to audio_dur+1s (fix Kling silent tail) ==="

for i in 2 3 5 6 8; do
  echo "Processing scene-$i (Avatar)..."
  AUDIO_DUR=$($FFPROBE -v error -show_entries stream=duration -select_streams a:0 -of csv=p=0 "$SC/scene-$i/scene-$i.mp4")
  VID_DUR=$($FFPROBE -v error -show_entries format=duration -of csv=p=0 "$SC/scene-$i/scene-$i.mp4")
  TARGET=$(python3 -c "print(round($AUDIO_DUR + 1.0, 3))")
  echo "  audio: ${AUDIO_DUR}s, video: ${VID_DUR}s → trimming to ${TARGET}s (audio+1s pause)"
  $FFMPEG -y -i "$SC/scene-$i/scene-$i.mp4" \
    -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,tpad=stop_mode=clone:stop_duration=1.0" \
    -af "apad=pad_dur=1.0" \
    -t "$TARGET" \
    -r 30 -c:v libx264 -crf 18 -preset fast \
    -ar 44100 -ac 2 -c:a aac -b:a 128k \
    "$SC/scene-$i/scene-$i-final.mp4"
  echo "  done → $($FFPROBE -v error -show_entries format=duration -of csv=p=0 "$SC/scene-$i/scene-$i-final.mp4")s"
done

echo ""
echo "=== Step 4: Brainrot overlay on Scene 1 (ffmpeg-full for drawtext) ==="
$FFMPEG_FULL -y -i "$SC/scene-1/scene-1-final.mp4" \
  -vf "drawtext=text='ЧЕХОВ. АГЕНТ ВРАГА.':fontsize=52:fontcolor=red:borderw=4:bordercolor=black:x=(w-text_w)/2:y=200:enable='between(t,0.5,4.5)',drawtext=text='AURA\: -9999':fontsize=46:fontcolor=yellow:borderw=4:bordercolor=black:x=(w-text_w)/2:y=280:enable='between(t,1.0,4.5)'" \
  -c:a copy "$SC/scene-1/scene-1-final-overlay.mp4"
mv "$SC/scene-1/scene-1-final-overlay.mp4" "$SC/scene-1/scene-1-final.mp4"
echo "Scene-1 brainrot overlay done"

echo ""
echo "=== Step 5: Verify clip durations before concat ==="
for i in 1 2 3 4 5 6 7 8 9; do
  DUR=$($FFPROBE -v error -show_entries format=duration -of csv=p=0 "$SC/scene-$i/scene-$i-final.mp4" 2>/dev/null || echo "MISSING")
  echo "  scene-$i: ${DUR}s"
done

echo ""
echo "=== Step 6: Concat all 9 clips ==="
cat > /tmp/concat_st.txt << 'EOF'
file '/Users/admin/conductor/workspaces/video-mcp-new/brasilia/video-agent/output/2026-04-06_star-trek-timelines_serial-drama-ep1/scenes/scene-1/scene-1-final.mp4'
file '/Users/admin/conductor/workspaces/video-mcp-new/brasilia/video-agent/output/2026-04-06_star-trek-timelines_serial-drama-ep1/scenes/scene-2/scene-2-final.mp4'
file '/Users/admin/conductor/workspaces/video-mcp-new/brasilia/video-agent/output/2026-04-06_star-trek-timelines_serial-drama-ep1/scenes/scene-3/scene-3-final.mp4'
file '/Users/admin/conductor/workspaces/video-mcp-new/brasilia/video-agent/output/2026-04-06_star-trek-timelines_serial-drama-ep1/scenes/scene-4/scene-4-final.mp4'
file '/Users/admin/conductor/workspaces/video-mcp-new/brasilia/video-agent/output/2026-04-06_star-trek-timelines_serial-drama-ep1/scenes/scene-5/scene-5-final.mp4'
file '/Users/admin/conductor/workspaces/video-mcp-new/brasilia/video-agent/output/2026-04-06_star-trek-timelines_serial-drama-ep1/scenes/scene-6/scene-6-final.mp4'
file '/Users/admin/conductor/workspaces/video-mcp-new/brasilia/video-agent/output/2026-04-06_star-trek-timelines_serial-drama-ep1/scenes/scene-7/scene-7-final.mp4'
file '/Users/admin/conductor/workspaces/video-mcp-new/brasilia/video-agent/output/2026-04-06_star-trek-timelines_serial-drama-ep1/scenes/scene-8/scene-8-final.mp4'
file '/Users/admin/conductor/workspaces/video-mcp-new/brasilia/video-agent/output/2026-04-06_star-trek-timelines_serial-drama-ep1/scenes/scene-9/scene-9-final.mp4'
EOF

$FFMPEG -y -f concat -safe 0 -i /tmp/concat_st.txt \
  -c:v libx264 -crf 18 -preset fast \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  "$OUT/assembled.mp4"
echo "assembled.mp4 done: $($FFPROBE -v error -show_entries format=duration -of csv=p=0 "$OUT/assembled.mp4")s"

echo ""
echo "=== Step 7: TO BE CONTINUED overlay on last 2s (ffmpeg-full) ==="
TOTAL_DUR=$($FFPROBE -v error -show_entries format=duration -of csv=p=0 "$OUT/assembled.mp4")
SHOW_AT=$(python3 -c "print(round($TOTAL_DUR - 2.0, 3))")
echo "Total dur: ${TOTAL_DUR}s, overlay starts at: ${SHOW_AT}s"

$FFMPEG_FULL -y -i "$OUT/assembled.mp4" \
  -vf "drawtext=text='TO BE CONTINUED...':fontsize=54:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h-160:enable='gte(t,${SHOW_AT})'" \
  -c:a copy "$OUT/with-overlay.mp4"
echo "with-overlay.mp4 done"

echo ""
echo "=== Step 8: Add dark music at 12% volume ==="
MUSIC=$(find /Users/admin/conductor/workspaces/video-mcp-new/brasilia/video-agent/music/Dark -name "*.mp3" 2>/dev/null | head -1)
if [ -z "$MUSIC" ]; then
  MUSIC=$(find /Users/admin/conductor/workspaces/video-mcp-new/brasilia/video-agent/music -name "*.mp3" 2>/dev/null | head -1)
fi
echo "Music: $MUSIC"

VIDEO_DUR=$($FFPROBE -v error -show_entries format=duration -of csv=p=0 "$OUT/with-overlay.mp4")
FADE_ST=$(python3 -c "print(round($VIDEO_DUR - 1.5, 3))")

$FFMPEG -y -i "$OUT/with-overlay.mp4" -stream_loop -1 -i "$MUSIC" \
  -filter_complex "[1:a]volume=0.12,atrim=0:${VIDEO_DUR},afade=t=out:st=${FADE_ST}:d=1.5[music];[0:a][music]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" \
  -c:v copy -ar 44100 -ac 2 -c:a aac -b:a 128k \
  "$OUT/final.mp4"

echo ""
echo "=== ASSEMBLY COMPLETE ==="
$FFPROBE -v error -show_entries format=duration,size -of default "$OUT/final.mp4"
