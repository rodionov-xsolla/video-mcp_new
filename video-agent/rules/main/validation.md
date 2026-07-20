# Validation Policy

Central policy for validating generated binary assets (PNG/MP4/MP3). Applied by all roles (Storyboarder, Animator, Editor).

## Rule: programmatic-only. No Read on binaries.

**Never use the Read tool, AI Vision, sampled-frame inspection, pixel-diff, or semantic media QA on generated PNG/MP4/MP3.** The only exceptions are source material explicitly declared by the format: a Wild Documentary research/source image when genuinely necessary, and Motion Dance source-video frames. These exceptions never apply to generated outputs or `final.mp4`.

Validation is done via bash.

### For PNG (images)

For Storyboarder NB2 outputs, `tools/fal_runner.py` is the validation authority: it checks PNG signature/chunks/CRC, decompresses image data, requires full ffmpeg decode, minimum dimensions, and portrait 9:16 (documented 2:3 fallback). Do not repeat generation because a valid 2:3 fallback is not exactly 1080×1920.

```bash
# File downloaded
[ -s "scene-1.png" ] && [ $(stat -f%z scene-1.png) -gt 1000 ]

# Dimensions correct (1080×1920 for vertical)
identify -format "%wx%h" scene-1.png   # → "1080x1920"
# or via ffprobe
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 scene-1.png
```

### Storyboarder Phase 3 handoff — runner state + permanent URL

Manager may accept a scene only when all four facts agree:

1. `storyboard.json` has a local `scene_image` for that clip, and the PNG exists/is >1 KB.
2. The matching `${OUTPUT_DIR}/build/fal/{job_id}/state.json` has `phase: "DONE"` and `output_path == scene_image`.
3. Storyboard has a non-empty HTTPS `scene_image_url`, and it equals that state's `supabase_url`.
4. Neither `scene_image_url` nor any downstream `image_urls[]` contains a temporary fal/fal.media host.

Example read-only gate (adapt `.clips` to `.scenes` when required by the schema):

```bash
while IFS=$'\t' read -r idx local_path permanent_url; do
  [ -s "$local_path" ] || { echo "scene-$idx local PNG missing"; exit 1; }
  [ "$(stat -f%z "$local_path" 2>/dev/null || stat -c%s "$local_path")" -gt 1000 ] || exit 1
  case "$permanent_url" in https://*) ;; *) echo "scene-$idx permanent URL missing"; exit 1 ;; esac
  case "$permanent_url" in *fal.media*|*queue.fal.run*) echo "scene-$idx temporary URL"; exit 1 ;; esac
  jq -se --arg p "$local_path" --arg u "$permanent_url" \
    '[.[] | select(.phase == "DONE" and .output_path == $p and .supabase_url == $u)] | length == 1' \
    "$OUTPUT_DIR"/build/fal/*/state.json >/dev/null || {
      echo "scene-$idx has no matching DONE runner state"; exit 1;
    }
done < <(jq -r '(.clips // .scenes)[] | [.index, .scene_image, .scene_image_url] | @tsv' "$OUTPUT_DIR/storyboard.json")
```

Missing state/URL is a Phase 3 failure. Do not launch Animator and do not manually upload or substitute a URL.

### For MP4 (video)

For schema-v3 fal video jobs, Scenarist/Manager/Animator own the semantic plan and exact provider payload. `tools/kling_runner.py` validates only execution safety: registered route descriptor, immutable canonical payload, permanent URLs at any payload depth, saved request ID, and the caller-supplied technical `expect` (duration/tolerance, audio required/optional/forbidden, minimum bytes/dimensions, orientation). It fully decodes the MP4, uploads it and byte-verifies the permanent public copy. Animator handoff requires runner `phase: "DONE"`, local `scene_video == output_path`, and permanent `scene_video_url == supabase_url`.

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

TTS and canonical scene files are named strictly from `clips[].index`: `scene-{index}.png/.mp4/.mp3`, `tts` keyed to the same index. **No `-new`, `-v2`, `-fixed` parallel files in canonical handoff.** A runner-claimed canonical PNG cannot be overwritten or reset manually. The runner has no safe reset command: preserve its output, state, request, and claim, then STOP for an explicit recovery decision. Drifting names (`ep6-scene-2.mp3` actually belonging to clip 3) are what let the wrong audio/PNG reach the wrong clip.

### 4. scene_image_url ↔ index — the PNG under a clip is that clip's own PNG

```bash
# basename of scene_image_url must contain scene-{index}
jq -r '.clips[] | "\(.index) \(.scene_image_url)"' storyboard.json
```

For dialogue clips, the face ref must match `clip.hero`. (EP6: the Admiral clip briefly pointed at Kirk's bust PNG → Kirk's face lipsynced to the Admiral's voice.)

**Print the mapping table** (`clip# → image_url → audio_url → expected text → hero`) and confirm all four checks pass before launching Kling. This is the single highest-ROI gate in the pipeline — it catches 4 of the 5 most expensive EP6 bugs with zero vision tokens.

## Time-gated PNG overlays — technical validation only

`overlay=...:enable='between(t,START,END)'` on a plain `-i overlay.png` input is a silent no-op: a single still image has a PTS that never advances, so `between(t,...)` never evaluates true and the overlay never appears — ffmpeg exits 0, no warning. Feed the PNG a real timeline first: `-loop 1 -t <total_duration> -i overlay.png`.

Validate the PNG input timeline, `enable=between(...)` expression, filtergraph construction, encode exit status, output streams and duration. Do not extract or compare frames to prove visual presence; the user performs visual review.

## Asset selection: by path, not by visual inspection

Where the right asset depends on game/format/series — resolve by exact ownership metadata or by the URL recorded in the exact resolved story bible. Images, appearance text, voice samples, openers and title assets require exact game + format + series ownership. CTA wording and asset must be read from that same exact story bible; there is no automatic cross-format/global lookup.

Examples:
- CTA → both wording and asset come from the exact resolved current format/series story bible. If missing or invalid, STOP; never synthesize, guess, or copy a global/cross-game fallback.
- Character refs → `games/{GAME_TAG}/{format}_story_bible.json → supabase_assets.char_refs`. Never re-derive from a wide-shot scene render.
