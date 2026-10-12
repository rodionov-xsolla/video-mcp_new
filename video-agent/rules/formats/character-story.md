---
ready_to_post: yes
subtitles: true
overlays: false
---

# Format "Character Story" — first-person lore monologue with visualization

A tightly-cut lore video: the character tells their story in first person while Kling I2V visualizes the key moments. TTS overlay on silent picture; subtitles use the universal whisper-timed ASS pipeline from `rules/roles/editor.md`.

This file is the **playbook**: when to use, concept, budget, role briefs. Craft rules — in `rules/roles/*.md`.

---

## When to use

Keywords: "character story", "история персонажа", "лор", "lore", "backstory", "origin story", "предыстория".

Before generation, resolve the exact `games/{GAME_TAG}/character-story_story_bible.json`. It must own this format's `style_tags`, character appearance data, eligible refs, and any approved voice sample. Missing or incomplete bible → STOP and ask the user whether to create or complete it. Never auto-create it or borrow another format's data.

---

## Concept

- **Genre:** lore monologue, first-person visual storytelling
- **Style:** exact `character-story` story bible `style_tags`, unless the user gives a live override. Game-wide and other-format style/appearance data are not fallbacks.
- **Duration:** 30–40s (6–8 clips × 5s)
- **Budget:** up to $6.00 per video. Stop if spend > $5.40.
- **Frame format:** 9:16 (608×1080) for all scenes

### Models

- **Image:** NB2 (`fal-ai/nano-banana-2/edit`) — character refs + scene images
- **Video:** Kling v3 Standard I2V (`fal-ai/kling-video/v3/standard/image-to-video`) — `generate_audio: false`. Keep the selected model/endpoint/route and serialized request fixed; retry once, then stop. Kling 2.6 is not an automatic fallback. v3 supports native `multi_prompt`.
- **Audio:** Chatterbox only when the exact `character-story` story bible owns an approved character sample. If no sample exists and voice identity is important, STOP and ask; use MiniMax only when the user accepts a non-identity-critical voice. ElevenLabs TTS and cross-format samples are forbidden.
- **Music:** yes, mood per plot, `volume` per mood (0.10–0.20)

### Key mechanic

The character does NOT speak on camera (no lipsync). Video = visualization of what the voice tells. I2V shows actions, locations, key moments. TTS is overlaid as off-screen narration.

### Still shots: allowed

The scenarist may plan still shots (`motion: "still"`) under the rule, cap and fields in `rules/roles/scenarist.md` "Still shots" (§8). A still scene gets its start PNG as usual and is rendered free by the Animator (`tools/still_shot.py`, no paid clip), saving that scene's Kling clip ($0.42 per 5s scene); narration plays over it as normal.

- **Best candidates:** a wide establishing or location shot with no character in focus (homeworld skyline, ship exterior, an empty room after a loss), a close-up of a meaningful object at rest (a medal, a letter, a memento), a quiet aftermath pause.
- **Never a still:** the HOOK, the TURNING POINT climax, or any clip whose point is the character's face, gesture or age-variant performance. Zero stills is a normal result.
- A still scene's camera move is its `still_effect`; the three-motion-layer and banned-phrase rules below apply to animated clips.

---

## Budget (rough estimates)

| Component | 5s clip |
|---|---|
| Image (NB2, start frame only — no end frame, no bg-ref) | $0.08 |
| Kling v3 Standard I2V 5s (generate_audio=false) | $0.42 |
| **Per clip** | **~$0.50** |
| Still-shot scene (NB2 image only; `tools/still_shot.py` render is free) | $0.08 |

| Component | Cost |
|---|---|
| External TTS (approved exact-format Chatterbox sample, or user-authorized MiniMax) | see `providers.json` |
| MiniMax Music | see `providers.json` |
| Character ref (one per age variant — typically 1 or 2) | $0.08 each |

| Variant | Clips | Cost |
|---|---|---|
| Base (recommended) | 6 × 5s = 30s + 1–2 char-refs (NO separate bg-refs) | ~$2.80 |
| Extended | 8 × 5s = 40s + 1–2 char-refs (NO separate bg-refs) | ~$3.60 |

A still scene saves its Kling clip ($0.42 per 5s, no audio).

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
- Voice route follows exact-format ownership: approved Character Story sample → Chatterbox; user-authorized non-identity-critical voice → MiniMax
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
- **HOOK self-introduction is MANDATORY.** The first clip's `tts_segment` must name the character with their full canonical designation so unfamiliar viewers (most of the audience) immediately know who they're watching. Include four elements when applicable: **rank + full name + role + ship/affiliation**. Examples: "I am Captain Benjamin Lafayette Sisko", "I am Seven of Nine, Tertiary Adjunct of Unimatrix Zero One", "I am Lieutenant Nyota Uhura, Communications Officer, Starship Enterprise". One line, ≤18 words, hard requirement. Without this the video reads as art-piece monologue rather than a character story.
- **Show visual age progression where canon supports it.** If the character has clearly distinct age variants in their canon (child / young adult / cadet / mature), the arc MUST visualize AT LEAST 2 of them across the clips — ideally 3 (child → young → mature). ORIGIN clips usually carry the youngest variant; HOOK and REVELATION the most mature. Mark each clip's image_prompt with the specific age variant ("child X at ~8 years old", "young cadet X at ~20", "Captain X at ~50"). A flat single-age character story loses the "growing-up arc" that defines the format.
- **Three motion layers per animated clip** (mandatory): camera move + environment motion + character action. Each layer continues throughout the full 5s — do NOT write "then settles / then steady / then dissipates" (Kling reads those as freeze cues).
- camera_angle differs between adjacent clips, AND every clip specifies an active camera move (push-in / pull-back / lateral dolly / low boom / crane up / handheld drift; for a still scene, its `still_effect`). No "camera holds steady" clips.
- Still shots: optional, per "Still shots: allowed" above and `rules/roles/scenarist.md` "Still shots"; zero is a normal result.
- Number of characters in frame — per plot (1–2, max 2 in frame)
- **No bg-reference generation** — environment goes into `image_prompt` as text only
- Voice intent comes from the character and exact Character Story bible. Record intent, not an ElevenLabs voice name; Sound resolves the permitted Chatterbox/MiniMax route.
- General script rules — `rules/roles/scenarist.md`

**Storyboard.json — extra fields:**

```json
{
  "format": "character-story",
  "game_tag": "{GAME_TAG}",
  "character_name": "{name}",
  "tts": {
    "full_text": "{full monologue}",
    "voice_intent": "{character-specific delivery intent}",
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

- Style: use the exact `character-story` story bible `style_tags` (or live user override) verbatim for every clip. Never fall back to game-wide or another format's style/appearance data.
- All frames 9:16 (608×1080)
- Character ref: use only an anchor recorded by the exact Character Story bible and owned by the exact game/format/series. If missing, generate a fresh Character Story-bound anchor from that bible's appearance text; never copy another format's ref or appearance description.
- **No bg-reference generation.** Environment is baked into the scene prompt via `image_prompt`. Do NOT generate separate bg PNGs for character-story — use text description of the location in the prompt only.
- Chain: `scene-1` refs = `[exact-character-story-ref]`; `scene-N` (N≥2) refs = `[exact-character-story-ref, same-run scene-(N-1).png]`. No bg ref (background comes through text in `image_prompt`), but the same-run prev-scene chain is mandatory for continuity between frames. See storyboarder.md §10.
- If 2 characters in frame — both via refs, max 2 refs per image
- `image_prompt` describes the visual action from `action_description`, NOT the monologue text
- **One PNG per clip — start frame only.** Do NOT generate `scene-K-end.png`. End frames waste $0.08/clip and are FORBIDDEN with `multi_prompt`. See storyboarder.md §14.8.
- General rules — `rules/roles/storyboarder.md`

### Animator

- All animated clips via **Kling v3 Standard I2V** (`generate_audio: false`; still scenes are rendered locally, no paid clip). Retry the same serialized request once on the same route, then stop the whole video; Kling 2.6 requires separate explicit authorization after the stopped run. Never replace a failed clip with a still.
- **Still scenes** (`motion: "still"`): no Kling call; render with `tools/still_shot.py` as `rules/roles/animator.md` §2b describes.
- **Start frame only.** Do NOT pass `tail_image_url` / end frame. Identity is held by `image_url` (start frame, chain-ref'd by Storyboarder) + the chain consistency Kling already enforces between adjacent frames. End frames make Kling interpolate-then-freeze and produce static clips.
- **Motion is mandatory, not optional.** Every animated clip must specify three concurrent layers:
  1. **Camera move** — pick one per clip: slow push-in, slow pull-back, lateral dolly, low boom up, crane up, parallax handheld drift. Distribute variety across the 6–8 clips. NEVER "camera holds steady".
  2. **Environment motion** — wind, smoke, sparks, particles, light flicker, distant figures, water/dust, holographic UI motion. Continuous throughout the 5s.
  3. **Character action** — one gesture or expression beat sustained through the clip (a slow head turn, a hand rising to the brow, a sip, a jaw clenching, a half-smile forming). Sustained, NOT completed mid-clip.
- **Phrasing rules for `motion_prompt`:**
  - Use continuous-tense verbs (`is lifting`, `tightens`, `drifts past`) and explicit duration cues (`throughout the shot`, `held for the full 5 seconds`, `continues across the frame`).
  - **Banned phrases:** `"then settles"`, `"then steady"`, `"then holds"`, `"then dissipates"`, `"then dies"`, `"camera holds steady"`, `"hold position"`, `"no morphing"`, `"maintain exact character appearance"`. These all read to Kling as "freeze".
  - **Avoid negative listings.** Do not stack `No walking, no running, no fighting, no impact`. Replace with positive instructions ("character remains rooted at the console", "feet planted, weight shifts gently").
  - Trust Kling to hold identity from the start frame — do not write defensive phrases.
- Micro vs. macro motion: avoid full-body locomotion (walking across the frame, running, combat hits) because identity drift is visible. BUT motion within the frame (head, hands, torso, breath, sustained gestures, props in motion, environment) MUST be alive.
- Duration: 5s for all clips
- Polling: base URL `fal-ai/kling-video`, every 15s, max 10 min
- Do NOT use: Kling Avatar, generate_audio: true
- General rules — `rules/roles/animator.md`

### Sound

- **TTS route:** follow `rules/roles/sound.md`.
  - Approved sample owned by the exact `character-story` bible → Chatterbox.
  - No approved sample and identity-critical character voice → STOP and ask the user.
  - MiniMax is allowed only when the user accepts a non-identity-critical voice.
  - ElevenLabs TTS and cross-format voice lookup are forbidden. Keep one voice intent for the whole video.
  - Chatterbox monologues are split into safe chunks of at most 35 words; never send an 80+ word monologue in one request. Concatenate the validated chunks into the single final narration track used for alignment.
  - Save locally and upload only when a downstream API needs a permanent run-scoped URL. Editor mixes the final narration over the concatenated picture.
- **Subtitles: one universal style (editor.md §6)**
  - **NEVER** generate one PIL PNG per `tts_segment` — produces unreadable 13-word slabs glued to 5s clip duration. Banned.
  - Run `add_subtitles.py` ONCE on the full `tts-output.mp3` against the picture-only concat (Editor produces it before audio mix).
  - One universal style (editor.md §6): `add_subtitles.py build/voice-final.wav build/subs.ass --storyboard storyboard.json --lang en --main-dur {MAIN_DUR}`. No `--chunk`/`--fontsize`/`--marginv`/`--no-scale`/`--emphasis`.
- **Speed control:** if TTS duration > timeline (7×5 = 35s for 6-clip; 8×5 = 40s for 8-clip), Editor applies `atempo` (cap 1.4×). Subtitles are computed from the already sped-up speech (`voice-final.wav`) — no recompute. If mismatch > 40% — return to Scenarist to shorten text.
- **Music:** by mood from storyboard (`music.mood`)
  - Generate the track with MiniMax by mood (see sound.md §6)
  - `volume` from storyboard (default 0.15)
- General rules — `rules/roles/sound.md`

### Editor

Two-stage assembly because subtitles need a picture-only concat to whisper-align against:

**Stage 1 — Picture-only concat:**
- Normalize each clip: scale 1080×1920, 30fps, `preset slow`, `crf 20`. Kling I2V is 24fps → normalize to 30fps mandatory before concat.
- Hard cuts, no crossfade.
- Output: `build/concat-noaudio.mp4` (silent, full main duration; CTA NOT yet appended).

**Stage 2 — Subtitle burn-in (delegated to Sound, see `sound.md` § 8B):**
- `add_subtitles.py build/voice-final.wav build/subs.ass --storyboard storyboard.json --lang en --main-dur {MAIN_DUR}` → burn `ass=build/subs.ass` as the last video filter (editor.md §6). Universal style, no legacy flags.

**Stage 3 — Final audio mix (one ffmpeg pass):**
- Inputs: `build/concat-subbed.mp4` + `tts-output.mp3` (atempo-adjusted if needed) + music + `cta-scaled.mp4`
- Concat picture = `concat-subbed.mp4` + `cta-scaled.mp4`
- TTS overlay: `apad=whole_dur=${MAIN_DUR}` (not `-shortest`), TTS volume=1.0
- Music: `amix` with TTS, volume from storyboard, duration = MAIN_DUR, fade out 1.0s before CTA
- `-t TOTAL_DUR` where `TOTAL_DUR = MAIN_DUR + CTA_DUR`

**Speed control:**
- If `dur(tts) > MAIN_DUR` → apply `atempo` (cap 1.4×). Subtitles are computed from the already sped-up `voice-final.wav` — no recompute.
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
│   │   ├── scene-1.png           (start frame only — no end frame; background painted inline by NB2)
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

Generated PNG/MP4/audio receives technical validation only (path, size, hash, dimensions, codec, duration, schema). Visual continuity/style/age-progression items below are prompt/schema requirements and user-review criteria; they do not authorize AI Vision, frame sampling, or machine semantic inspection.

- [ ] `format: "character-story"` in storyboard.json
- [ ] `character_speech: null` for all clips (voice via TTS, not in video)
- [ ] `tts_segment` filled for each clip
- [ ] Full monologue = sum of all `tts_segment`
- [ ] **HOOK clip's `tts_segment` contains the character's name + rank/role + ship/affiliation** (self-introduction for unfamiliar viewers)
- [ ] **If character has canonical age variants, arc visualizes ≥2 of them** (separate clips for young/mature, each with the matching character-ref); single-age stories rejected for characters with multi-age canon
- [ ] All images 608×1080 (9:16)
- [ ] No bg-reference files (environment in image_prompt only)
- [ ] One PNG per scene (start frame only) — NO end-frame PNGs generated (§14.8)
- [ ] All Supabase uploads use date-suffix paths (`<slug>-<YYYY-MM-DD>.png` for refs, `scene-K-<slug>-<YYYY-MM-DD>.png` for scenes) — no bare `scene-K.png` paths that would collide with prior episodes
- [ ] camera_angle differs between adjacent clips, and every clip has an active camera move (no "holds steady"; a still scene's `still_effect` counts)
- [ ] Every animated clip's motion_prompt has three concurrent layers (camera + environment + character) and uses continuous-tense verbs
- [ ] Still scenes (if any) were planned in Phase 1, have `scene_video_kind: "still"` and stay within the `rules/roles/scenarist.md` "Still shots" cap; every other scene is a Kling v3 Standard clip
- [ ] motion_prompt contains NONE of the banned freeze phrases (then settles / then steady / then holds / hold position / no morphing / camera holds steady)
- [ ] TTS uses approved exact-character-story Chatterbox, or user-authorized MiniMax; no ElevenLabs TTS or cross-format sample
- [ ] Subtitles use the universal `add_subtitles.py` contract from `rules/roles/editor.md` — no format-local chunk/font/margin overrides and no PIL PNG by `tts_segment`
- [ ] If TTS longer than picture timeline: `atempo` ≤ 1.4× in audio mix; subtitles via whisper from voice-final.wav (no manual --atempo)
- [ ] fps normalized to 30 before concat
- [ ] One ffmpeg pipeline, not layered
- [ ] Music fade out before CTA
- [ ] CTA included in concat-list
- [ ] `-shortest` NOT used

---

## Visual style consistency — HARD RULE

**All clips in an episode must share the same visual style.** The target style comes from the exact Character Story bible's top-level `style_tags` (or a live user override) and must be applied identically to every clip, including clips with child characters or scenes that trigger NB2 safety filters. Missing style data stops generation; never fall back to game-wide or another format.

**If NB2 rejects a prompt:** rewrite the `image_prompt` and `negative_prompt` using neutral language (avoid: occupation, refugee, soldier, war, violence, terrified, attack, battle, enemy). Do NOT change the image style, do NOT drop the character ref from `image_urls`. The character ref anchors the visual style — removing it causes NB2 to lose the style anchor and produce inconsistent output.

**Style drift = episode failure.** An episode where clips differ in art style must be marked `status: "error"` and rejected at the Phase 6 review gate. Rerun storyboarder with corrected prompts.

---

## Anti-patterns

- ❌ `generate_audio: true` in Kling I2V (voice is bad, use TTS overlay)
- ❌ Kling Avatar (format does not use lipsync)
- ❌ `character_speech ≠ null` (voice only via TTS overlay)
- ❌ ElevenLabs TTS, a cross-format voice sample, or Chatterbox without an approved exact-character-story sample
- ❌ Sending an 80+ word monologue in one Chatterbox request, or changing route/voice intent between chunks
- ❌ Monologue text = description of footage (voice complements, doesn't duplicate)
- ❌ character ref directly as scene image (each clip = its own PNG)
- ❌ Generating scene-K-end.png and/or passing `tail_image_url` to Kling — wastes $0.08/clip and biases Kling toward static interpolation
- ❌ `-shortest` in FFmpeg (use `apad`)
- ❌ Layered assembly (breaks music and timing)
- ❌ Monotonous footage (one angle for the whole 40 seconds)
- ❌ "Camera holds steady" / "then settles" / "then steady" / "hold position" / "no morphing" / "maintain exact character appearance" anywhere in `motion_prompt` (Kling reads these as freeze cues — produces static clips)
- ❌ Stacked negative listings (`No walking, no running, no fighting, no impact`) — replace with positive grounded actions
- ❌ Title cards, brainrot tags, character name overlays
- ❌ Separate `bg-{location}.png` references generated as a phase before scene PNGs — NB2 paints the background inline with the character; chaining `[bg-ref, character-ref]` produces stiff composite-feel results with mismatched lighting/perspective. Describe the location verbosely in `image_prompt` instead.
- ❌ HOOK clip without character name self-introduction — viewers who don't know the character are lost in the first 5 seconds. The name + rank/role + ship/affiliation must be in clip 1's `tts_segment`.
- ❌ Single-age character story when the character has clearly different canonical age variants (child / young / mature). The arc must visualize ≥2 of them; otherwise the "growing-up" beat collapses and the video reads as a moment-in-time portrait rather than a lore arc. Generate one character-ref per age variant used.
- ❌ Supabase scene PNG uploads at bare `scene-K.png` paths (without date+character suffix) — collides with prior episodes' scene assets and silently clobbers them. Always upload to `scene-K-<character-slug>-<YYYY-MM-DD>.png`.
