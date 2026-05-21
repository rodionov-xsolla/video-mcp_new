# Format "Character Story" — first-person lore monologue with visualization

A tightly-cut lore video: the character tells their story in first person while Kling I2V visualizes the key moments. TTS overlay on silent picture; subtitles via `add_subtitles.py` (whisper word-timestamps → ASS chunks of 3 words, burned in before audio mix).

This file is the **playbook**: when to use, concept, budget, role briefs. Craft rules — in `rules/roles/*.md`.

---

## When to use

Keywords: "character story", "история персонажа", "лор", "lore", "backstory", "origin story", "предыстория".

---

## Concept

- **Genre:** lore monologue, first-person visual storytelling
- **Style:** identical to the game (taken from `games/{GAME_TAG}/{GAME_TAG}.md`)
- **Duration:** 30–40s (6–8 clips × 5s)
- **Budget:** up to $6.00 per video. Stop if spend > $5.40.
- **Frame format:** 9:16 (608×1080) for all scenes

### Models

- **Image:** NB2 (`fal-ai/nano-banana-2/edit`) — character refs + scene images
- **Video:** Kling 2.6 Pro I2V (`fal-ai/kling-video/v2.6/pro/image-to-video`) — `generate_audio: false`
- **Audio:** ElevenLabs TTS overlay (`fal-ai/elevenlabs/tts/eleven-v3`) — first-person monologue
- **Music:** yes, mood per plot, `volume` per mood (0.10–0.20)

### Key mechanic

The character does NOT speak on camera (no lipsync). Video = visualization of what the voice tells. I2V shows actions, locations, key moments. TTS is overlaid as off-screen narration.

---

## Budget (rough estimates)

| Component | 5s clip |
|---|---|
| Image (NB2) | $0.04 |
| Kling I2V 5s (generate_audio=false) | $0.35 |
| **Per clip** | **~$0.39** |

| Component | Cost |
|---|---|
| ElevenLabs TTS (~40s monologue) | ~$0.20 |
| Music (local) | $0.00 |

| Variant | Clips | Cost |
|---|---|---|
| Base (recommended) | 6 × 5s = 30s | ~$2.50 |
| Extended | 8 × 5s = 40s | ~$3.30 |
| With extra refs/bg | 8 × 5s + 2–3 bg | ~$3.50 |

---

## Video structure

The structure is flexible — the scenarist adapts it to the specific character's story. Guides:

| Phase | Timing | Goal | Clips |
|---|---|---|---|
| **HOOK** | 0–5s | Dramatic moment from the middle/end. Stop the scroll | 1 clip (5s) |
| **ORIGIN** | 5–15s | Who the character is, where from, what shaped the path | 2 clips (5s) |
| **TURNING POINT** | 15–25s | Key event: battle, betrayal, loss, gaining power | 2 clips (5s) |
| **REVELATION** | 25–35s | Who they became, what they're known for, main trait | 1–2 clips (5s) |
| **CTA** | last ~5s | CTA clip | 1 clip |

### What works

- **In medias res.** Start with the brightest moment, then flashback to the beginning
- **Concrete visual images.** "The sword glowed white-hot" > "I became stronger"
- **Emotional contrasts.** Quiet moment → burst of action → silence
- **Each clip = a new visual image.** Change of location, angle, scale
- **Voice leads, video illustrates.** Don't duplicate — complement

### What does NOT work

- ❌ Chronological retelling without a hook (boring)
- ❌ Abstract emotions without visual stakes
- ❌ Monotonous footage (the same angle for 40 seconds)
- ❌ Monologue text literally describing what is on screen
- ❌ Philosophical monologues without action

### The monologue

- First-person, character voice
- ~80–120 words for 30–40s
- Short sentences, punchy phrases
- Voice picked from ElevenLabs by character traits
- Every 5s (1 clip) ≈ 10–15 words

---

## Role briefs

### Scenarist

- Write the first-person monologue (~80–120 words, 30–40s)
- Structure: HOOK (in medias res) → ORIGIN → TURNING POINT → REVELATION
- Split the monologue into 10–15 word fragments = one per clip (5s)
- `clip_type: "action"` for all clips (I2V, not Avatar)
- `character_speech: null` for all clips (voice via TTS overlay, not in video)
- `tts` field in storyboard.json — monologue text per clip
- `action_description` — what happens visually, NOT a repeat of the monologue text
- At least 2 different actions per clip (micro motion)
- camera_angle differs between adjacent clips
- Number of characters in frame — per plot (1–2, max 2 in frame)
- **No bg-reference generation** — environment goes into `image_prompt` as text only
- Voice: pick from ElevenLabs by character (Daniel — confident, George — neutral, Charlie — young, Charlotte — female)
- General script rules — `rules/roles/scenarist.md`

**Storyboard.json — extra fields:**

```json
{
  "format": "character-story",
  "game_tag": "{GAME_TAG}",
  "character_name": "{name}",
  "tts": {
    "full_text": "{full monologue}",
    "voice": "{voice name}",
    "stability": 0.25,
    "style": 0.75,
    "language_code": "{ISO 639-1}"
  },
  "music": {
    "mood": "{mood}",
    "volume": 0.15
  },
  "clips": [
    {
      "index": 1,
      "beats": ["hook"],
      "duration_sec": 5,
      "clip_type": "action",
      "character_speech": null,
      "tts_segment": "{monologue fragment for this clip}",
      "character_state": "...",
      "facial_expression": "...",
      "action_description": "...",
      "camera_angle": "...",
      "image_prompt": "...",
      "negative_prompt": "..."
    }
  ]
}
```

### Storyboarder

- Style is taken from `games/{GAME_TAG}/{GAME_TAG}.md` (identical to the game)
- All frames 9:16 (608×1080)
- Character ref: create an anchor ref (neutral pose, dark background) from game config
- **No bg-reference generation.** Environment is baked into the scene prompt via `image_prompt`. Do NOT generate separate bg PNGs for character-story — use text description of the location in the prompt only.
- Chain: scene-N refs = `[character-ref]` only (no bg ref)
- If 2 characters in frame — both via refs, max 2 refs per image
- `image_prompt` describes the visual action from `action_description`, NOT the monologue text
- **Start frame only per clip. No end frames** — see storyboarder.md §14.8 and §16.
- General rules — `rules/roles/storyboarder.md`

### Animator

- All clips via **Kling 2.6 Pro I2V** (`generate_audio: false`)
- Micro motion only: gaze, gesture, head turn, wind, particles, camera
- Motion prompt = technical: positions, camera, physical actions
- Start ≈ end for I2V (one character, one bg, minimal difference)
- Duration: 5s for all clips
- Polling: base URL `fal-ai/kling-video`, every 15s, max 10 min
- Do NOT use: Kling Avatar, Veo3, generate_audio: true
- General rules — `rules/roles/animator.md`

### Sound

- **TTS:** ElevenLabs via fal.ai (`fal-ai/elevenlabs/tts/eleven-v3`)
  - `voice` = name string (Daniel, George, Charlie, Charlotte), NOT voice_id
  - One voice for the whole video (single character)
  - `stability` and `style` per character traits
  - Generate the full monologue in **one request** (it's a single continuous voice; one request keeps prosody coherent and gets a single mp3 the subtitle pipeline can whisper-align in one pass)
  - Save full mp3 → upload to Supabase. Editor mixes it over the concatenated picture.
- **Subtitles: ASS via `tools/add_subtitles.py` (Pipeline 8B in `sound.md`)**
  - **NEVER** generate one PIL PNG per `tts_segment` — produces unreadable 13-word slabs glued to 5s clip duration. Banned.
  - Run `add_subtitles.py` ONCE on the full `tts-output.mp3` against the picture-only concat (Editor produces it before audio mix).
  - Args: `--chunk 3 --fontsize 72 --marginv 200 --lang en --no-scale`. Pass `--emphasis "phrase1,phrase2"` if scenarist marked beats.
  - Output: `build/concat-subbed.mp4` → Editor then overlays TTS + music on it.
- **Speed control:** if TTS duration > timeline (7×5 = 35s for 6-clip; 8×5 = 40s for 8-clip), Editor applies `atempo` (cap 1.4×). Pass `--atempo` to the subtitle script so ASS timestamps scale. If mismatch > 40% — return to Scenarist to shorten text, don't paper over.
- **Music:** by mood from storyboard (`music.mood`)
  - Pick a track from `music/tracks.json` by mood
  - `volume` from storyboard (default 0.15)
- General rules — `rules/roles/sound.md`

### Editor

Two-stage assembly because subtitles need a picture-only concat to whisper-align against:

**Stage 1 — Picture-only concat:**
- Normalize each clip: scale 1080×1920, 30fps, `preset slow`, `crf 20`. Kling I2V is 24fps → normalize to 30fps mandatory before concat.
- Hard cuts, no crossfade.
- Output: `build/concat-noaudio.mp4` (silent, full main duration; CTA NOT yet appended).

**Stage 2 — Subtitle burn-in (delegated to Sound, see `sound.md` § 8B):**
- `add_subtitles.py build/concat-noaudio.mp4 tts-output.mp3 build/concat-subbed.mp4 --chunk 3 --fontsize 72 --marginv 200 --lang en --no-scale [--atempo N]`
- Output: `build/concat-subbed.mp4` (still silent picture, but with burned ASS).

**Stage 3 — Final audio mix (one ffmpeg pass):**
- Inputs: `build/concat-subbed.mp4` + `tts-output.mp3` (atempo-adjusted if needed) + music + `cta-scaled.mp4`
- Concat picture = `concat-subbed.mp4` + `cta-scaled.mp4`
- TTS overlay: `apad=whole_dur=${MAIN_DUR}` (not `-shortest`), TTS volume=1.0
- Music: `amix` with TTS, volume from storyboard, duration = MAIN_DUR, fade out 1.0s before CTA
- `-t TOTAL_DUR` where `TOTAL_DUR = MAIN_DUR + CTA_DUR`

**Speed control:**
- If `dur(tts) > MAIN_DUR` → apply `atempo` (cap 1.4×). Pass same `--atempo` to `add_subtitles.py` so ASS times scale.
- If `dur(tts) < MAIN_DUR` → freeze-frame extend the last (or lowest-motion) clip; do NOT pad TTS with leading silence.
- If mismatch > 40% → reject, ask Manager to send Scenarist back.

General rules — `rules/roles/editor.md`

---

## CTA (Call to Action)

CTA video is taken from Supabase `game_assets` (tag `cta` + `video`). Manager downloads it in Phase 0 and hands it to Editor. Normalize (1080×1920, 30fps, AAC 128k), insert into concat-list as the last clip.

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/character-story/
├── storyboard.json
├── scenes/
│   ├── refs/
│   │   └── character-ref.png
│   ├── scene-1/
│   │   ├── scene-1.png
│   │   ├── scene-1.mp4
│   │   └── scene-1-scaled.mp4
│   └── scene-N/...
├── tts-output.mp3
├── build/
│   ├── concat-noaudio.mp4   (picture-only concat for whisper align)
│   └── concat-subbed.mp4    (after add_subtitles.py burn-in)
├── concat-list.txt
└── final.mp4
```

---

## Validation before publishing

- [ ] `format: "character-story"` in storyboard.json
- [ ] `character_speech: null` for all clips (voice via TTS, not in video)
- [ ] `tts_segment` filled for each clip
- [ ] Full monologue = sum of all `tts_segment`
- [ ] All images 608×1080 (9:16)
- [ ] No bg-reference files (environment in image_prompt only)
- [ ] I2V start frame only — no end frames (§14.8)
- [ ] camera_angle differs between adjacent clips
- [ ] TTS via fal.ai ElevenLabs (`voice` name, not `voice_id`)
- [ ] Subtitles via `add_subtitles.py` (ASS, chunk 3, fontsize 72, marginv 200) — NOT PIL PNG by `tts_segment`
- [ ] If TTS longer than picture timeline: `--atempo` ≤ 1.4× applied in BOTH the script and Editor's audio mix (same value)
- [ ] fps normalized to 30 before concat
- [ ] One ffmpeg pipeline, not layered
- [ ] Music fade out before CTA
- [ ] CTA included in concat-list
- [ ] `-shortest` NOT used

---

## Anti-patterns

- ❌ `generate_audio: true` in Kling I2V (voice is bad, use TTS overlay)
- ❌ Kling Avatar / Veo3 (format does not use lipsync)
- ❌ `character_speech ≠ null` (voice only via TTS overlay)
- ❌ `voice_id` hash instead of `voice` name in ElevenLabs
- ❌ TTS by fragments (generate the whole monologue in one request)
- ❌ Monologue text = description of footage (voice complements, doesn't duplicate)
- ❌ character ref directly as scene image (each clip = its own PNG)
- ❌ Different character on start/end I2V (Kling will morph)
- ❌ `-shortest` in FFmpeg (use `apad`)
- ❌ Layered assembly (breaks music and timing)
- ❌ Monotonous footage (one angle for the whole 40 seconds)
- ❌ Title cards, brainrot tags, character name overlays
