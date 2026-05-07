# Format "Motion Dance" — character dances to music via motion transfer from reference video

A single character (game skin, OC, meme) dances to music. Movements come from a real dance video via Kling Motion Control. Key feature — analyzing the reference video before image generation so the character's shot and pose match the reference.

This file is the **playbook**: when to use, concept, budget, role briefs.
Craft rules — in `rules/roles/*.md`.

---

## When to use

Keywords: "motion dance", "motion control", "моушн", "motion transfer", "танцует под видео".

Do NOT confuse with Dance Battle (two characters battle via Kling I2V). Motion Dance = one character + a real reference video.

---

## Concept

- **Genre:** dance video with motion transfer
- **Style:** Game-specific (Roblox 3D, Pixar, Anime — determined by the game)
- **Duration:** 10–30s (determined by the length of the reference video)
- **Clips:** 1 (= 1 dance from one reference video)
- **Budget:** up to $3.00 per video. Stop if spend > $2.70.
- **Frame format:** 9:16 (1080×1920)

### Models

- **Image:** Nano Banana 2 (character + background)
- **Video:** Kling Motion Control v2.6 Standard ($0.07/s)
- **Audio:** `keep_original_sound: true` (music from the reference video)

---

## Budget (rough estimates)

| Component | Cost |
|---|---|
| NB2 image (character) | ~$0.08 |
| Kling Motion Control v2.6 10s | $0.70 |
| Kling Motion Control v2.6 15s | $1.05 |
| Kling Motion Control v2.6 20s | $1.40 |
| Kling Motion Control v2.6 30s | $2.10 |

| Variant | Cost |
|---|---|
| Short dance (10s) | ~$0.78 |
| Medium dance (20s) | ~$1.48 |
| Long dance (30s) | ~$2.18 |

---

## Pipeline

| Phase | Action | Who |
|---|---|---|
| 0. Reference video analysis | Extract first frame + middle frame → determine shot, angle, pose | Storyboarder |
| 1. Image generation | NB2 — character in the same shot/angle as the reference video + background | Storyboarder |
| 2. Upload to Supabase | image + video → permanent URLs | Animator |
| 3. Motion Control | Kling v2.6 Standard → dancing character | Animator |
| 4. Finalization | Download, verify, optionally trim/scale | Editor |

### Phase 0 — Reference video analysis (CRITICAL)

Before generating the character image, **mandatory** extract frames from the reference video:

```bash
# First frame
ffmpeg -i ref-video.mp4 -vframes 1 -q:v 2 ref-frame-first.jpg

# Middle frame
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 ref-video.mp4)
MIDPOINT=$(echo "$DURATION / 2" | bc -l)
ffmpeg -i ref-video.mp4 -ss $MIDPOINT -vframes 1 -q:v 2 ref-frame-mid.jpg
```

Analyze the frames:
- **Shot:** full body / upper body / medium shot?
- **Angle:** frontal / slightly side / from below?
- **Proportions:** how much of the frame the person occupies?
- **Background:** flat / complex?

This data determines the NB2 prompt — the character must be in the **same shot and scale**, otherwise motion transfer will be incorrect.

---

## Kling Motion Control parameters

| Parameter | Value | Note |
|---|---|---|
| `image_url` | Supabase URL of the image | Permanent URL, NOT fal.media |
| `video_url` | Supabase URL of the reference video | Permanent URL, NOT fal.media |
| `character_orientation` | `"video"` | Movements from video (max 30s) |
| `keep_original_sound` | `true` | Keep music from the reference video |
| `prompt` | Brief description | "A cute Roblox girl dancing" |

### Polling

- Submit: `POST https://queue.fal.run/fal-ai/kling-video/v2.6/standard/motion-control`
- Polling base: `fal-ai/kling-video` (2-segment path)
- Interval: 15 seconds
- Timeout: 10 minutes

---

## Role briefs

### Scenarist
- SKIP — format does not use storyboard.json. All "directing" is in the reference video.
- The user provides: reference video + character description + background description.

### Storyboarder
- **Phase 0 mandatory:** extract frames from the reference video, determine shot/angle.
- Generate the character through NB2 in the same shot as the reference video.
- If there is a background ref (game map) — pass as `image_urls` for consistency.
- `image_urls`: `[bg-ref]` if there is a background reference, otherwise no `image_urls`.
- Character: full body, clear proportions, >5% of frame area (Kling requirement).
- Head must not be obscured (Motion Control requirement).
- General rules — `rules/roles/storyboarder.md`

### Animator
- **Model:** Kling Motion Control v2.6 Standard (`fal-ai/kling-video/v2.6/standard/motion-control`)
- **Before generation:** upload image + video to Supabase (permanent URLs).
- `character_orientation: "video"` (movements from video).
- `keep_original_sound: true` (music kept).
- Duration is determined by the reference video (max 30s in video mode).
- General rules — `rules/roles/animator.md`

### Sound
- SKIP — sound is taken from the reference video (`keep_original_sound: true`).
- TTS not needed, subtitles not needed.
- General rules — `rules/roles/sound.md`

### Editor
- Minimal processing: scale 1080×1920, 30fps if needed.
- Optional: trim start/end, fade out the last 1–2s.
- **Do NOT** re-encode audio if `keep_original_sound: true`.
- General rules — `rules/roles/editor.md`

---

## Output files

```
output/YYYY-MM-DD_motion-test/
├── ref-frame-first.jpg       # First frame of the reference video (analysis)
├── ref-frame-mid.jpg         # Middle frame of the reference video (analysis)
├── character.png             # Generated character image
├── dance-ref.mp4             # Reference video (original)
└── final.mp4                 # Motion control result
```

---

## Validation before publishing

- [ ] Phase 0 done: reference video frames extracted and analyzed
- [ ] Character in the same shot/scale as the reference video
- [ ] Character occupies >5% of the frame, head not obscured
- [ ] image + video uploaded to Supabase (permanent URLs)
- [ ] `character_orientation: "video"`
- [ ] Reference video ≤30s
- [ ] Result downloaded, size >10KB
- [ ] Budget ≤$3.00

---

## Anti-patterns

- ❌ Generating character image WITHOUT analyzing the reference video (shot won't match → broken motion transfer)
- ❌ Passing fal.media URL as `image_url` / `video_url` (will expire)
- ❌ `character_orientation: "image"` for dances (10s limit, worse for complex movements)
- ❌ Reference video >30s (Kling limit in video mode)
- ❌ Character with obscured head (Kling can't transfer expression)
- ❌ `-shortest` in FFmpeg (universal anti-pattern)
- ❌ Confusing with Dance Battle (that format = two characters via Kling I2V, no motion transfer)
