---
subtitle_style: bold
subtitle_offset_s: 0
subtitle_mask: false
subtitle_highlight: false
subtitle_extras: []
---

# Format "Serial Drama" — serial micro-dramas

Serial micro-dramas with brainrot aesthetic and an endless plot. Each episode = 25–40 seconds, 3–5 clips, cliffhanger at the end.

This file is the **playbook**: when to use, concept, budget, series state (story bible), role briefs. Craft rules — in `rules/roles/*.md`.

---

## When to use

Keywords: "serial", "episode", "series", "ep1", "ep2", "сериал", or `series_id` of an existing series is provided.

---

## Concept

- **Genre:** endless micro-dramas with brainrot aesthetic, cliffhangers, plot loops
- **Style:** Pixar/Disney 3D — stylized 3D characters, plastic textures, expressive faces, soft ambient lighting, cinematic depth of field
- **Duration:** 25–40s (3–5 clips × 5–10s)
- **Budget:** up to $10 per episode. Stop if spend > $9.00.
- **Frame format:** 9:16 (608×1080) for all scenes. Square forbidden.

### Clip mix (balances)

- **ACTION/DIALOGUE ~ 50/50.** All-dialogue episode = monotonous and expensive; all-action = no plot.
- **I2V (Kling v3 Standard)** — action/reaction clips (silent); fallback v2.6 Pro only on v3 artifacts
- **Avatar (Kling Avatar v2)** — dialogue clips with lipsync (TTS from ElevenLabs)
- **TTS overlay with aecho** — only for "behind glass/door" scenes (character is visible through a barrier, face not visible)

---

## Budget (rough estimates)

| Component | 5s clip | 10s clip |
|---|---|---|
| Image (NB2) | $0.04 | $0.04 |
| Kling I2V (generate_audio=false, $0.07/s) | $0.35 | $0.70 |
| ElevenLabs TTS (line 5–15s) | ~$0.05 | ~$0.07 |
| Kling Avatar v2 (dialogue) | ~$0.28 | ~$0.56 |
| **I2V action clip** | **~$0.39** | **~$0.74** |
| **Avatar dialogue clip** | **~$0.32** | **~$0.63** |

| Variant | Clips | Cost |
|---|---|---|
| Base (recommended) | 5 × 5s | ~$2.00–3.00 |
| Extended | 6–7 × 5s | ~$2.50–4.00 |
| Exception (undividable monologue) | 4×5s + 1×10s | ~$2.80–3.80 |

⚠️ **Dynamics > savings.** 2×5s almost always beats 1×10s. Angle change / counterpart reaction matters more than $0.04 saved.

---

## Episode structure (narrative)

| Phase | Timing | Goal | Clips |
|---|---|---|---|
| **HOOK** | 0–5s | Visual paradox + hook line. Stop the scroll | 1 clip (5s, ACTION/I2V) |
| **CLIMAX** | 5–30s | Dialogue, confrontation, rising tempo | 2–3 clips (5–10s each) |
| **CLIFFHANGER** | last 5s | Cut at the peak. Shock, reveal, mid-sentence stop | 1 clip (5s, ACTION/I2V) |

### What works (TikTok/Reels audience)

- **Conflict from the first second.** Not "once upon a time", but "Worf is leading Chekov to the airlock". Viewer drops into the middle of the action.
- **Concrete visual stakes.** Someone will die, be betrayed, lose everything. Not abstract emotions.
- **Short punchy lines.** 2–5s per phrase. Not monologues.
- **Every scene moves the plot.** Zero filler.
- **Drama through action, not words.** "Worf lowers his eyes" > a 10-second monologue.

### What does NOT work

- ❌ Philosophical/sentimental plots ("What Spock would never say")
- ❌ Theatrical speeches, long monologues
- ❌ Slow buildup without conflict in the first 5 seconds
- ❌ All clips dialogue (monotonous, expensive, boring)
- ❌ Two consecutive Avatar clips of different characters on the SAME background, frontal (copy-paste)

### Brainrot vocabulary

Appropriate in dialogue: `rizz`, `sigma`, `cooked`, `negative aura`, `bro`, `no cap`, `NPC behavior`, `delulu`. In moderation, not in every line. Not in the narrator.

### Duration — 5s by default

- Any line ≤15 words → **5s**
- Any action/reaction → **5s**
- 10s dialogue clip = **almost always a mistake** (a static head for 10 seconds = death of dynamics). Split into 2×5s with different angles.
- 10s clip requires `duration_reason` in storyboard.json.

---

## Story Bible — persistent series state

File `games/{GAME_TAG}/serial-drama_story_bible.json` stores the universe state between episodes. **Mandatory** for serial-drama.

### Structure

```json
{
  "series_id": "roblox-noob-revenge",
  "game_tag": "Roblox",
  "title": "The Noob Who Was a Secret Millionaire",
  "style_tags": "Roblox-inspired Pixar-style 3D...",
  "created_at": "2026-03-27",
  "last_episode": 0,

  "characters": [
    {
      "name": "Noob Dave",
      "role": "protagonist",
      "character_description": "Roblox-style blocky humanoid, bright yellow smooth plastic skin, simple blue torso shirt, bright green pants, round head with wide innocent eyes, small curved mouth, matte plastic texture",
      "voice": "Charlie",
      "status": "just joined the server, secretly rich",
      "aura_points": 0,
      "relationships": {}
    }
  ],

  "active_loops": [],
  "closed_loops": [],

  "world_state": {
    "location": "Roblox server lobby",
    "important_items": [],
    "key_events": []
  },

  "anti_repetition": {
    "recent_phrases": [],
    "recent_hooks": [],
    "recent_cliffhangers": []
  },

  "episode_summaries": []
}
```

### State Analysis (before generation)

1. Load story bible from `games/{GAME_TAG}/serial-drama_story_bible.json`
2. Analyze: who is in what status, which loops are active, what is the aura level
3. Run Anti-Repetition Check (see below)
4. Decide what happens in this episode (Loop Management)

### State Transition (after generation, Manager updates)

1. Update `characters[].status` and `aura_points`
2. Update `relationships` if changed
3. Update `active_loops` / `closed_loops`
4. Add `episode_summaries[]` with a brief summary + cliffhanger
5. Update `anti_repetition` — add used phrases, hooks, cliffhangers
6. Update `world_state`
7. Increment `last_episode`

---

## Loop Management (Recursive Continuity)

Intrigue loops — unresolved conflicts that keep viewers engaged.

| Type | Duration | Example |
|---|---|---|
| **Minor** | 2–5 episodes | "Who stole the item?" |
| **Major** | 10–20 episodes | "The hero's hidden identity" |
| **Eternal** | Never closed | "The server war" |

### Rules

- Every 5 episodes **close 1 minor loop**, but **open 2 new larger ones**
- At least 2 active loops at all times
- **No Finality:** any victory begins a new disaster; any reveal generates a new mystery
- The series NEVER ends

---

## Retention Strategy (mandatory in storyboard)

Each episode contains in storyboard:

```json
{
  "retention_strategy": "Reveal that the noob has a secret golden item triggers curiosity — viewer MUST see next episode to learn what it does",
  "active_loops": ["noob's secret identity", "slender's revenge plan"],
  "cliffhanger": "Noob opens inventory and golden light illuminates his face — cut to black"
}
```

---

## Anti-Repetition Check

Before writing the storyboard, check `anti_repetition` in story bible:

1. **Phrases:** do not repeat from the last 8 episodes
2. **Hooks:** do not use the same type (if last was a "question hook" — use "contrast" or "statement")
3. **Cliffhangers:** do not repeat the device (mid-sentence / reveal / unexpected entrance)
4. **Metaphors/similes:** diversity is mandatory

---

## Role briefs

### Scenarist

- Episode structure: HOOK → CLIMAX (2–3 clips) → CLIFFHANGER
- **5s default**, 10s dialogue = almost always a mistake (split into 2×5s)
- Balance ACTION/DIALOGUE ~ 50/50; at least 2 different characters speak per episode
- Read the story bible: characters, voices (`voice` field), active loops, anti-repetition
- **`retention_strategy` mandatory** in storyboard — why the cliffhanger pulls the next episode
- Brainrot vocabulary in moderation, dialogue only
- camera_angle differs for every adjacent clip
- **NO title cards / brainrot tags / character names overlays** — only dialogue subtitles + TBC
- General script rules — `rules/roles/scenarist.md`

### Storyboarder

- Pixar/Disney 3D style (`style_tags` from story bible)
- All frames 9:16 (608×1080) — square forbidden
- **bg-reference per location** mandatory — without it the background drifts between clips (see `storyboarder.md` section 2)
- Character refs: characters from story bible, mouth with teeth for lipsync clips
- I2V clips: **start frame only** (`scene-K.png`). End frames are NEVER generated — see `storyboarder.md` §14.8/§16. `end_image_url` is FORBIDDEN with `multi_prompt` (Kling returns 422).
- Each clip = its own scene PNG (not the ref directly)
- **No photoreal source refs in this stylized format.** Before using a character ref, check its tags — an asset tagged `photoreal` / `comedy-sketch` / `live-action` is FORBIDDEN here. A photoreal reference image biases the whole render toward realism; a text "NOT photorealistic, strictly Pixar 3D" does NOT override a photoreal *source image* (proven by EP6 scene 8, which used `spock/variants/canonical.png` — a photoreal sheet — and drifted realistic). Use the Pixar/3D-styled sheet, or generate one.
- General rules — `rules/roles/storyboarder.md`

### Animator

- I2V clips via Kling v3 Standard (`generate_audio: false`, always) — micro motion only. Fallback to v2.6 Pro only on v3 artifacts.
- Avatar clips via Kling Avatar v2 Standard (with TTS audio_url)
- Motion prompt = technical (positions, camera, physical actions), without names/moods
- One I2V model for the whole episode — do not mix Kling I2V versions within one episode
- Start frame only for I2V; Kling animates from the start frame via `motion_prompt`
- **Style-hold for this Pixar-styled format (not universal — lives here, not in `animator.md`):**
  - **Anti-photoreal negative in EVERY I2V clip**, not selectively: `photorealistic, film grain, realistic skin, live action, photograph`. EP6 scene 2 omitted it and the close-up drifted realistic; scenes 7/8 that had it held better.
  - **Carry the style anchor into EVERY shot of a `multi_prompt`**, not just shot 1 — each shot's prompt restates the style ("Pixar 3D animated …"). Late shots without an anchor drift to the model's realistic prior.
  - **Do not end a `multi_prompt` on a tight close-up of a face that is not present in the start frame.** This was the real "problem is always in the third shot": both EP6 multi-prompts ended on an invented face close-up; by the last shot Kling has left the start frame and re-renders that face with its own (realistic) prior. Keep the final shot within the framing the start frame supports, or split the close-up into its own clip.
- **Do NOT speed up Avatar** in serial-drama (1.3x — only for gameplay-ai-avatar)
- Avatar = bust shot (head fills upper 55–75% of frame, no feet / full body) — full-body framing produces face artifacts (EP6 Kirk scenes 3/5)
- General rules — `rules/roles/animator.md`

### Sound

- TTS via fal.ai ElevenLabs — `voice` (name string) from story bible, `language_code` ISO 639-1, `stability` per mood
- One character = one voice across the whole series (locked in story bible)
- **Subtitles: PIL PNG overlay** (ffmpeg 8.1 without libfreetype can't drawtext)
  - Font Arial/Helvetica Bold 38–48px, white + 3px stroke, lower third
  - ONLY dialogue subs + TBC. No title cards, brainrot tags, character names.
- Background music: drama/cinematic, `volume=0.15`
- General rules — `rules/roles/sound.md`

### Editor

- **One ffmpeg pipeline for the entire final assembly** (concat + overlays + music + fade + CTA). NOT layered.
- I2V clips: fps normalization 24 → 30 mandatory before concat
- Avatar clips: trim to TTS_dur + 0.3s, `apad=whole_dur=${TARGET}` (not `pad_dur`)
- TTS overlay "behind glass" (rare): `aecho=0.8:0.9:10:0.3`, `adelay=500`
- Subtitles via PNG overlay chain (filter_complex)
- **CTA included in concat list** as the last clip (not a separate re-encode)
- TBC overlay 2s before the end (before fade)
- Fade out 1.0s on MAIN_DUR (before CTA); CTA goes after fade in silence
- General rules — `rules/roles/editor.md`

---

## CTA (Call to Action)

The CTA video is taken from Supabase `game_assets` (tag `cta` + `video`). Manager downloads it in Phase 0 and hands it to Editor.

### Assembly

CTA is added to concat-list.txt **as the last clip** BEFORE final assembly. Timings:

- `MAIN_DUR` = main content without CTA
- `CTA_DUR` = CTA duration
- `TOTAL_DUR` = MAIN_DUR + CTA_DUR
- Music `amix` on MAIN_DUR, fade ends before CTA
- `-t TOTAL_DUR` includes CTA

**Result:** one ffmpeg pass instead of three.

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/serial-drama/
├── storyboard.json
├── scenes/
│   ├── refs/
│   │   ├── character-ref-{name}.png
│   │   └── bg-{location}.png
│   ├── scene-1/
│   │   ├── scene-1.png
│   │   ├── scene-1.mp4
│   │   ├── scene-1-scaled.mp4
│   │   └── tts-1.mp3 (for dialogue only)
│   └── scene-N/...
├── subs/sub-N.png
└── final.mp4
```

Also: `games/{GAME_TAG}/serial-drama_story_bible.json` — persistent, updated after every episode.

After upload: `videos/{GAME_TAG}/{YYYY-MM-DD}/serial-drama_final.mp4` in Supabase.

---

## Validation before publishing

- [ ] `format: "serial-drama"`, `series_id`, `episode_number` = story_bible.last_episode + 1
- [ ] `retention_strategy`, `active_loops`, `cliffhanger` filled
- [ ] First clip — HOOK, last — CLIFFHANGER
- [ ] ACTION/DIALOGUE ~ 50/50; at least 2 characters speak
- [ ] Dialogue clips = 5s (10s only with `duration_reason`)
- [ ] All images 608×1080 (9:16)
- [ ] bg-reference per location created
- [ ] I2V: start frame only (`scene-K.png`), no end frames generated
- [ ] Cross-asset pre-flight passed (all URLs 200, distinct audio per clip, filename=index, scene_image_url↔hero) — `validation.md`
- [ ] Each character from ONE locked ref; no photoreal-tagged refs; every `image_prompt` has full style prefix
- [ ] Each I2V has anti-photoreal negative; each multi_prompt shot has a style anchor; no multi_prompt ends on an invented face close-up
- [ ] TTS via fal.ai ElevenLabs (`voice` name, not `voice_id`)
- [ ] Subtitles PIL PNG; dialogue + TBC only
- [ ] fps normalized to 30 before concat
- [ ] One ffmpeg pipeline, not layered
- [ ] CTA included in concat-list (not a separate re-encode)
- [ ] TBC overlay 2s before the end; fade out 1.0s
- [ ] Anti-repetition check passed
- [ ] Story bible updated after generation

---

## Anti-patterns

- ❌ `generate_audio: true` in Kling (voice is bad)
- ❌ Kokoro TTS, Kling Lipsync, direct ElevenLabs API
- ❌ `voice_id` hash instead of `voice` name
- ❌ 1:1 square for Avatar (only 9:16)
- ❌ character ref directly as scene image (each clip = its own PNG)
- ❌ Generating `scene-K-end.png` for I2V — end frames forbidden (storyboarder.md §14.8); `end_image_url` + `multi_prompt` = Kling 422
- ❌ `-shortest` in FFmpeg
- ❌ Closing all loops (at least 2 active)
- ❌ Repeating hooks/cliffhangers from the last 8 episodes
- ❌ Redoing clips that already work (each extra generation = $0.35+)
- ❌ Layered assembly (breaks music and timing)
- ❌ Title cards, brainrot tags, character name overlays
- ❌ Long 10s dialogue clips for $0.04 savings (kills dynamics)
- ❌ Re-rendering one line into a parallel `-new`/`-v2` audio file (drops locked voice → same character, two voices — EP6 Admiral)
- ❌ Referencing one character from two different ref asset paths across clips (face differs between adjacent clips)
- ❌ Photoreal-tagged source ref in this Pixar format (text "NOT photorealistic" does not override a photoreal source image)
- ❌ `image_prompt` without the full `style_tags` prefix (off-style clip)
- ❌ I2V clip without an anti-photoreal negative; `multi_prompt` shot without a style anchor
- ❌ Ending a `multi_prompt` on a tight invented face close-up not present in the start frame (drifts realistic)
- ❌ Launching Kling before the cross-asset pre-flight gate passes (dead ref / duplicate audio / wrong PNG — see `validation.md`)
