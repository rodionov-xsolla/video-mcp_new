# Validation Policy

Central policy for validating generated binary assets (PNG/MP4/MP3). Applied by all roles (Storyboarder, Animator, Editor).

## Default: Programmatic only — DO NOT read binaries

**By default DO NOT use the Read tool on PNG/MP4/MP3.** Each Read of a binary consumes vision tokens, which are expensive and bloat the context.

Validation is done via bash:

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

## Visual validation: opt-in per format

Visual validation (Read tool on a binary) is enabled **ONLY** if the format playbook explicitly declares:

```yaml
visual_validation: required        # Full visual check of all assets
visual_validation: first-scene     # Only first scene + character refs
```

**Default (if the field is missing): visual_validation: off** — Read of binaries forbidden.

### Current formats

All default formats are `visual_validation: off`. If a format requires working with frames as part of **generation** (e.g. motion-dance analyzes reference video frames in Phase 0 — that is part of the pipeline, not post-validation), it is described in the format playbook itself and is NOT covered by this policy.

This policy regulates only **post-generation** verification of NB2/Kling/FFmpeg results.

## What replaces visual validation

Previously the agent read PNGs visually and checked 9 items (storyboarder.md section 19):
- Character = the one ordered
- Style consistent
- Figure count = requested
- Composition start ≈ end (for I2V)
- No extra characters
- Proportions in constrained frames
- Mouth correct for lipsync
- Background matches bg ref
- No color artifacts on skin

**Current approach:** these checks are handled at the **prompt engineering** level, not as post-hoc validation:
- Precise character_description (8+ details) in JSON
- Stable `image_urls` for chain reference
- Negative prompts against artifacts
- Constraint frames for proportions
- Programmatic check of filesize/dimensions

If NB2 produces garbage — it is visible in the final video, caught during content review (outside the pipeline).

## When to enable visual_validation in a format

Enable only if:
1. The format has unique visual requirements (dance, pose, specific object)
2. The cost of "broken final video" is higher than the cost of vision tokens
3. Programmatic validation fundamentally cannot cover the requirement

Otherwise — leave the default (off).
