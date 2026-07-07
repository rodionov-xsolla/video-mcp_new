# Validation Policy

Central policy for validating generated binary assets (PNG/MP4/MP3). Applied by all roles (Storyboarder, Animator, Editor).

## Rule: programmatic-only. No Read on binaries.

**Never use the Read tool on PNG/MP4/MP3.** Vision tokens are expensive, bloat the context, and don't pay off — broken output is caught at the next stage (Kling artifacts in MP4, weird Editor output in final.mp4) and at the human review of the final video.

Validation is done via bash.

### For PNG (images)

```bash
# File downloaded
[ -s "scene-1.png" ] && [ $(stat -f%z scene-1.png) -gt 1000 ]

# Dimensions correct (1080×1920 for vertical)
identify -format "%wx%h" scene-1.png   # → "1080x1920"
# or via ffprobe
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 scene-1.png
```

### For MP4 (video)

```bash
# File downloaded (Kling returns <1KB JSON on error)
[ -s "scene-1.mp4" ] && [ $(stat -f%z scene-1.mp4) -gt 100000 ]

# Duration close to expected (±0.1s)
ffprobe -v error -show_entries format=duration -of csv=p=0 scene-1.mp4

# Video stream present
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of csv=p=0 scene-1.mp4
```

### For MP3 (audio)

```bash
[ -s "scene-1.mp3" ] && [ $(stat -f%z scene-1.mp3) -gt 1000 ]

# Duration
ffprobe -v error -show_entries format=duration -of csv=p=0 scene-1.mp3
```

## Why no visual checks

- Precise `character_description` (8+ details) in `storyboard.json` + chain `image_urls` + negative prompts cover what a post-hoc visual check used to catch.
- If the prompt-engineering is wrong, a Read on the result tells you "the prompt was wrong" — but you already shipped one expensive generation. Fix at the prompt level, not at validation.
- Programmatic checks (filesize / dimensions / duration / codec) catch the only failure modes that are silent at the API layer (truncated download, dimension mismatch, corrupted MP4).

## Cross-asset pre-flight (Manager, before any expensive generation)

Most of the costly failures in EP6 «11 Seconds» were not creative — they were file/URL bookkeeping: a dead ref URL, a cascaded `cp` that gave 4 clips the same audio, a TTS filename that drifted out of sync with the clip index, a scene PNG pointed at the wrong character. All four are caught programmatically, before paying Kling. Run these in Phase 2 (before NB2) and Phase 3 (before Avatar/I2V):

### 1. URL reachability — every input URL returns 200

Before handing any `image_urls[]`, `scene_image_url`, or `tts_url` to NB2/Kling:

```bash
for u in $URLS; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$u")
  [ "$code" = "200" ] || echo "DEAD REF ($code): $u"
done
```

Any non-200 → STOP, do not spend on the clip. (EP6 scene-9 Spock ref was HTTP 400 → the clip was generated with no valid character ref → wrong face.)

### 2. Distinct-audio — no two dialogue clips share an audio track

After Sound, before Avatar:

```bash
# md5 of every dialogue clip's audio must be unique
for f in scenes/scene-*/scene-*.mp3; do md5 -q "$f"; done | sort | uniq -d
```

Any duplicate md5 → a cascade-copy bug (one line overwrote several). STOP and re-resolve sources. (EP6: scenes 3–6 all carried the Admiral's line at 35153 B.)

### 3. Filename = f(index) — names are derived from the clip index, never a free counter

TTS and scene files are named strictly from `clips[].index`: `scene-{index}.png/.mp4/.mp3`, `tts` keyed to the same index. **No `-new`, `-v2`, `-fixed` parallel files** — a regeneration overwrites the same name (archive the old one first, see storyboarder §17). Drifting names (`ep6-scene-2.mp3` actually belonging to clip 3) are what let the wrong audio/PNG reach the wrong clip.

### 4. scene_image_url ↔ index — the PNG under a clip is that clip's own PNG

```bash
# basename of scene_image_url must contain scene-{index}
jq -r '.clips[] | "\(.index) \(.scene_image_url)"' storyboard.json
```

For dialogue clips, the face ref must match `clip.hero`. (EP6: the Admiral clip briefly pointed at Kirk's bust PNG → Kirk's face lipsynced to the Admiral's voice.)

**Print the mapping table** (`clip# → image_url → audio_url → expected text → hero`) and confirm all four checks pass before launching Kling. This is the single highest-ROI gate in the pipeline — it catches 4 of the 5 most expensive EP6 bugs with zero vision tokens.

## Time-gated PNG overlays — prove the composite, don't sample variance

`overlay=...:enable='between(t,START,END)'` on a plain `-i overlay.png` input is a silent no-op: a single still image has a PTS that never advances, so `between(t,...)` never evaluates true and the overlay never appears — ffmpeg exits 0, no warning. Feed the PNG a real timeline first: `-loop 1 -t <total_duration> -i overlay.png`.

Frame-variance/stddev sampling on the output is NOT sufficient proof the overlay rendered — ordinary scene content already produces high variance, so a broken (missing) overlay and a working one can both pass a variance threshold. To actually verify: extract a frame from inside the overlay window and one from outside it (or from a version rendered without the overlay filter), and diff them (pixel mean/stddev delta, or eyeball via Read — this specific check is worth the vision tokens, unlike routine PNG/MP4 validation). Burned in ROOM 1701 EP3 (2026-07-07, `serial-drama.md`): Editor reported the title card as burned in based on variance sampling; it was actually absent from the delivered final.mp4, caught only on user review.

## Asset selection: by path, not by visual inspection

Where the right asset depends on game/format (CTA, openers, character refs, bg refs) — **resolve by `GAME_TAG`-scoped path or by Supabase URL recorded in the story bible / game config.** Never pick from a generic location and then visually verify the branding — the path is the validation.

Examples:
- CTA → `games/{GAME_TAG}/assets/cta/cta.mp4` or previous-episode `output/.../{GAME_TAG}/.../cta-fallback.mp4`. Never `video-agent/cta-star-trek-timelines.mp4` (star-trek-timelines branded, wrong for any other game).
- Character refs → `games/{GAME_TAG}/{format}_story_bible.json → supabase_assets.char_refs`. Never re-derive from a wide-shot scene render.
