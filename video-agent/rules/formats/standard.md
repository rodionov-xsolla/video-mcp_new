# Format "Standard" — universal I2V

Universal default format: action, standup, guides, ratings, trailers. Picked when the idea doesn't fit specialized formats.

This file is the **playbook**. Craft rules (motion_prompt style, NB2 chain, ffmpeg pipeline) — in `rules/roles/*.md`.

---

## When to use

Keywords: any, **except** "news", "serial/сериал", "object character", "dual-style", "gameplay ai avatar / offerwall", "dance battle", "reddit story", "character story".

Typical cases: action scenes, standup jokes, top-N ratings, guides, atmospheric trailers.

---

## Concept

- **3 clips × 5–10s** → 15–30s total (4 clips — only if each contains a unique action)
- **Model: Kling I2V** (v3 Standard or 2.6 Pro fallback) — `generate_audio: true` (SFX)
- **Speech:** `character_speech: null` in all scenes — voice via TTS overlay if needed
- **One model for the whole video**
- **Budget:** $5

---

## Structure (default)

| Clip | Beat | Duration | camera_angle |
|---|---|---|---|
| 1 | hook | 5s | close-up / medium close-up |
| 2 | development | 10s | medium / wide |
| 3 | climax + CTA overlay | 5–10s | low angle / dynamic |

- CTA — from Supabase `game_assets` (tag `cta`), normalized, last clip in concat list
- camera_angle **different** for adjacent clips (mandatory)
- 4th clip — only if each of 4 carries a unique action

---

## Storyboard extensions

```json
{
  "format": "standard",
  "visual_identity": {
    "character_description": "8+ visual details (skin, scars, clothing, weapon)",
    "environment_description": "concrete location from the game",
    "style_tags": "from game config prompt_prefix",
    "color_palette": "from game config",
    "lighting": "from game config"
  },
  "scenes": [
    {"index": 1, "beats": ["hook"], "duration_sec": 5, "camera_angle": "close-up", ...}
  ]
}
```

Common scene fields (camera_angle, character_state, facial_expression, gaze_direction, character_speech, motion_prompt) — in `rules/roles/scenarist.md`.

---

## Role briefs

### Scenarist
- 3 clips × 5–10s; 4 only when fully loaded with unique action
- Narrative arc: hook → development → climax
- `character_speech: null` in all scenes
- At least 2 DIFFERENT actions in every motion_prompt (not looped)
- `character_state` / `camera_angle` change between scenes; `character_description` verbatim identical
- General rules — `rules/roles/scenarist.md`

### Storyboarder
- Anchor ref + chain on previous scene (max 2 refs)
- Style — from `games/{GAME_TAG}/{GAME_TAG}.md` (prompt_prefix, palette, lighting)
- Characters from Supabase `game_assets` — if present, reuse the ref
- General rules — `rules/roles/storyboarder.md`

### Animator
- **Kling I2V** (v3 Standard primary, 2.6 Pro fallback): `generate_audio: true` (SFX), micro motion, start≈end
- Polling base path = first 2 segments of the endpoint
- General rules — `rules/roles/animator.md`

### Sound
- TTS overlay (ElevenLabs via fal.ai) if voice over the video is needed
- Optional bg music (volume=0.15)
- Dialogue subtitles — optional; title/brainrot overlays forbidden
- General rules — `rules/roles/sound.md`

### Editor
- Scale every scene to 1080×1920, fps=30, `-preset slow -crf 20`
- Concat with re-encode (`libx264`), NOT `-c copy`; hard cuts, NO crossfade
- CTA from Supabase, normalized, last clip in concat list
- Music via `amix`; **NEVER `-shortest`** — use `apad`
- General rules — `rules/roles/editor.md`

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/standard/
├── storyboard.json
├── scenes/
│   ├── refs/character-ref.png
│   ├── scene-1/{scene-1.png, scene-1.mp4, scene-1-scaled.mp4}
│   ├── scene-2/...
│   └── scene-3/...
├── concat-list.txt
└── final.mp4
```

---

## Validation

- [ ] `format: "standard"`
- [ ] `character_speech: null` in all scenes — Kling I2V, not T2V
- [ ] 3 clips (or 4 with justification for each)
- [ ] `camera_angle` different for adjacent clips
- [ ] `motion_prompt` ≥2 different actions
- [ ] `visual_identity.character_description` ≥8 visual details
- [ ] `gaze_direction` with 2+ characters in frame
- [ ] CTA from Supabase `game_assets`
- [ ] Budget ≤$5
- [ ] `final.mp4` 1080×1920, 30fps; hard cuts; no `-shortest`

---

## FORBIDDEN

- Any T2V model (expensive, no control)
- `character_speech ≠ null` — voice only via TTS overlay
- `-shortest` in ffmpeg
- CTA generation — taken from Supabase
