---
subtitle_style: narrative
subtitle_offset_s: 0
subtitle_mask: true
subtitle_highlight: false
subtitle_extras: ["--marginv", "120", "--secondary-style", "Customer=lightgray,52,1,120"]
---

# Format "What If... Real Life" — game characters dropped into the mundane real world

<!-- Subtitle config:
  --mask (BorderStyle=4) — закрывает CJK-артефакты Kling Avatar v2 у низа кадра.
  --marginv 120 — опускает бокс прямо на артефакт (направление от низа: меньше=ниже).
  --secondary-style Customer=lightgray,52,1,120 — второй стиль для off-screen ребёнка
    в dialogue-offscreen сценах (легкосерый italic 52px, тот же MarginV=120).
-->


A recognizable game character is placed into a banal real-world situation or job — the contrast between who they ARE (their game persona, abilities, mannerisms, way of speaking) and who they have to BE in this context generates the comedy. Examples: Spock as a coffee barista, Kratos as a kindergarten teacher, a blocky Roblox guy trying to shop at a luxury boutique, Master Chief at a DMV counter, Geralt as a vet's receptionist.

This file is the **playbook**: when to use, concept, budget, role briefs. Craft rules (TTS, NB2 chain, Kling Avatar/I2V, ffmpeg) — in `rules/roles/*.md`.

---

## When to use

Keywords: "what if", "real life", "real world", "real-world", "что если", "в реальной жизни", "реальная жизнь", "fish out of water", "cameo", "mundane job", "ordinary life".

Best fit when the game has a strongly characterized hero (Spock, Kratos, Master Chief, Geralt, an iconic Roblox/MOBA/MMO avatar) whose persona is so specific that putting them in any ordinary context generates instant absurdity. **Single-shot per video** — no story bible, no continuity. Each video is one premise, one persona, one location.

---

## Concept

### The contrast rule

The character's reaction is **internally consistent with the game persona** (Spock is logical, Kratos is gruff/angry, a Roblox blocky guy is naively literal, Master Chief is military-formal) but **mismatched to the real-world context**. The contrast IS the joke; reactions don't have to be deadpan — they have to be in-character for a place where being in-character is wrong.

The chosen tone is fixed for the whole video in `visual_identity.reaction_mode` and applied to every character line. Mixing tones mid-video kills the bit ("Spock suddenly enthusiastic" = no).

### Locked across the format

- **Aspect ratio:** 9:16, 1080×1920, 30 fps
- **Style:** Photorealistic — even if the character is from a stylized source (Roblox block, low-poly MMO avatar). The character is rendered as if **physically present** in a real-world location: a Roblox guy is real cubic plastic in a real boutique, not a screenshot. Realism amplifies the absurd.
- **Subtitles:** ASS `BorderStyle=4` opaque box hugging text, Montserrat Bold 58–60, Alignment=2, MarginV=120 (low — also designed to mask any Kling Avatar v2 CJK bottom-strip artifact). See `rules/roles/sound.md` §10.
- **Speedup:** 1.18× at the end (snappier than the standard 1.15× — comedy timing). Applied BEFORE music mix. See `rules/roles/editor.md` §14.
- **Music:** From `video-agent/music/Fun/` only — upbeat, light. Volume 0.08. Tracks from `Dark/` or `Drama/` will tank the mood. See `rules/roles/sound.md` §10.5.
- **Negative prompt (all Avatar clips):** `extra characters facing camera, lipsync on background extras, CJK text, subtitle text in scene, watermark`

### Variable per video

- Character (must be visually recognizable in 1 second)
- Real-world location/role (barista / kindergarten teacher / DMV clerk / vet receptionist / wedding photographer / boutique shopper / dentist / Uber driver / yoga instructor)
- Outfit overlay anchoring the role (apron / lanyard / polo shirt / scrubs)
- `reaction_mode` (see Reaction Modes section)
- 3–6 vignette premises
- Bg-music track inside `music/Fun/`

---

## Reaction modes

Pick ONE and stick with it for all character lines in the video.

| Mode | Voice direction | Example line in a barista scene |
|---|---|---|
| `deadpan-logical` | flat, slow, factual; no emotion | "This is not a beverage. This is a logical crime." |
| `gruff-angry` | gravelly, loud, impatient; treats trivial things as battles | "BOY! The almond milk is on the SHELF." |
| `naive-literal` | innocent, slow, questions obvious things | "Why does the cup have a HOLE on top? Will the coffee not fall out?" |
| `military-formal` | clipped, procedural, mission-style | "Order received. Latte engagement in five minutes. Confirm sugar payload." |
| `world-weary-monotone` | tired, low-pitch, treats every request as one more burden | "Of course you want oat milk. Everyone wants oat milk." |
| `over-the-top-heroic` | declarative, epic phrasing for trivial actions | "I shall pour the coffee. AND ALL WHO ORDER IT SHALL DRINK." |

Fix the mode in `storyboard.json → visual_identity.reaction_mode`. Sound uses it to choose ElevenLabs voice + stability + style; Scenarist uses it to write all character lines in one register; Animator picks Avatar v2 mouth-motion profile accordingly.

---

## Budget

| Component | Per unit | Typical count | Subtotal |
|---|---|---|---|
| NB2 character refs + scene images | $0.08 | 6–8 | $0.48–$0.64 |
| Kling Avatar v2 5s (single-talker scene) | $0.28 | 3–5 | $0.84–$1.40 |
| Kling Avatar v2 10s (on-screen dialogue, 2 talkers) | $0.56 each | 0–1 | $0–$0.56 |
| Kling I2V 5s with audio (physical gag) | $0.42–$0.63 | 0–1 | $0–$0.63 |
| Kling I2V 5s no audio (silent vignette) | $0.42 | 0–2 | $0–$0.84 |
| ElevenLabs TTS — character lines | ~$0.07 | 4–6 | $0.28–$0.42 |
| ElevenLabs TTS — off-screen customer / narrator | ~$0.05 | 0–5 | $0–$0.25 |
| Title card (NB2 still, optional minor I2V) | $0.08 (+$0.42 if I2V) | 1 | $0.08–$0.50 |
| **Typical total** | | | **$2.50–$4.50** |

Max with 1–2 retries: **$6.00**. Stop at **$5.40**.

---

## Episode / video structure (flexible 5–8 scenes)

| Slot | Mandatory? | Dur. (pre-speed) | Goal |
|---|---|---|---|
| Title card | yes | 3s | Hook — "What if... / [CHARACTER] / Becomes / [ROLE]" in 4 stacked lines |
| Vignette 1 | yes | 5s | First clash between persona and reality |
| Vignette 2 | yes | 5s | Different gag mechanic, different angle |
| Vignette 3 | yes | 5s | Different gag mechanic again |
| Vignette 4 | optional | 5s | — |
| Vignette 5 | optional | 5s | — |
| Vignette 6 | optional | 5s | — |
| CTA | yes | 3s | Channel CTA from Supabase |

Total target: 28–34s pre-speedup → ~24–29s after 1.18× speedup. Hard cap 32s post-speedup (short-form sweet spot).

**Anti-repetition:** no two vignettes may use the same gag mechanic (e.g. don't have two "customer asks for absurd order" gags in a row).

---

## Vignette scene types

Each vignette picks ONE of these. Sound, Animator, Editor read `scene.scene_type` and dispatch accordingly.

| `scene_type` | Audio source | Animation model | Notes |
|---|---|---|---|
| `dialogue-offscreen` (default) | `customer.mp3` (off-screen voice) + silence-padded Avatar TTS | Kling Avatar v2 — only the character is on screen | Cheapest dialogue option. Customer face never to camera (back-of-head, off-frame, or blurred bg). See "Recommended dialogue pattern" below. |
| `dialogue-on-screen` | Two TTS tracks; both characters lipsynced | 2× Kling Avatar v2 (or HeyGen for second) — both faces visible | Doubles cost. Use sparingly, max 1 per video. |
| `monologue` | Narrator VO TTS over silent visuals | Kling I2V `generate_audio: false` + TTS overlay by Editor | Voice-of-god narration over the character doing something silly silently. |
| `inner-thought` | Character TTS over silent I2V (the persona THINKS, doesn't speak — face stays still) | Kling I2V `generate_audio: false` + TTS overlay | "Subtitled internal monologue" — character on screen, eyes communicate, voice is internal. |
| `physical-gag` | SFX only, no speech | Kling I2V `generate_audio: true` | Kratos crushes a juice box trying to open it. Sound = SFX from Kling. |

---

## Recommended dialogue pattern (`dialogue-offscreen` scenes)

This is the signature mechanic of the format — it's cheaper than two on-screen Avatars and it works.

For a scene where the customer/extra speaks first and the character reacts:

```
character_avatar_audio_mp3 = silence(customer_dur + 0.6s) + actual_tts(character_line)
```

This silence-padded mp3 is what Kling Avatar v2 ingests. **Kling Avatar v2 holds the mouth still during leading silence segments** (empirically validated). Editor then mixes `customer.mp3` over the silence portion via `amix`, producing the natural rhythm "customer speaks → character pauses → character replies" with only ONE Avatar v2 call per scene.

References:
- Off-screen voice mix protocol: `rules/roles/sound.md` §9
- Audio amix + RMS sanity check: `rules/roles/editor.md` §12
- ASS subtitle invariants (anti-overlap, MarginV direction, BorderStyle=4 box, last-sub-to-clip-end): `rules/roles/sound.md` §10

---

## Storyboard extension

```json
{
  "format": "what-if-real-life",
  "visual_identity": {
    "character": {
      "name": "Spock",
      "source_game": "Star Trek Timelines",
      "outfit_overlay": "green barista apron over charcoal t-shirt",
      "style": "photorealistic"
    },
    "real_world_role": "coffee barista",
    "location_description": "third-wave specialty coffee shop, warm wood, exposed bulbs, modern espresso machine",
    "reaction_mode": "deadpan-logical"
  },
  "scenes": [
    {
      "index": 1,
      "scene_type": "title-card",
      "title_lines": ["What if...", "SPOCK", "Becomes", "BARISTA"]
    },
    {
      "index": 2,
      "scene_type": "dialogue-offscreen",
      "customer_line": "Can I get a latte with no almonds, no milk, no caffeine — but make it energizing?",
      "character_line": "This is not a beverage. This is a logical crime.",
      "customer_voice": "Charlotte",
      "character_voice": "Daniel",
      "negative_prompt": "..."
    }
  ]
}
```

---

## Role briefs

### Scenarist

- Pick the character (must be visually unmistakable) + real-world role + ONE `reaction_mode` from the table above. Lock it in `visual_identity`.
- Write all character lines in the chosen `reaction_mode`. No mode-flips. Sarcasm is forbidden for `deadpan-logical` and `world-weary-monotone` — those modes work because the character is sincere.
- For each vignette, pick `scene_type` from the table. Default to `dialogue-offscreen`. Allow at most one `dialogue-on-screen` per video (cost).
- Each vignette = one specific real-world element that conflicts with the persona (the espresso machine for Spock, snack-time for Kratos, the boutique price-tag system for Roblox guy). No two vignettes with the same conflict mechanic.
- General script rules — `rules/roles/scenarist.md`.

### Storyboarder

- Photorealistic NB2 across all scenes — even when the character originates from a stylized source. Render the character as a tangible physical presence in the real-world location.
- Character outfit must include a clearly visible role-overlay (apron, lanyard, scrubs) — viewers register the role in <1s.
- For `dialogue-offscreen` scenes: customers are back-to-camera, edge-of-frame, or blurred in the background. Prompt this explicitly (e.g. "customer in foreground, BACK to camera, head turned away, only shoulders visible"). Otherwise NB2 invents inconsistent faces.
- For `dialogue-on-screen` scenes: both characters in frame, framed for 2× Avatar v2 lipsync (clean view of both mouths).
- Chain-reference using the character sheet as `anchor`, prev-scene as second ref. Location stays consistent across all vignettes of the same video.
- General rules — `rules/roles/storyboarder.md`.

### Animator

- Dispatch per `scene_type`:
  - `dialogue-offscreen` → Kling Avatar v2 with silence-padded mp3 (do NOT trim leading silence — it's the pause that makes the bit work).
  - `dialogue-on-screen` → 2× Kling Avatar v2 (or HeyGen for the second face if Avatar can't do dual). Coordinate timings via two padded mp3s so the two voices don't talk over each other.
  - `monologue`, `inner-thought` → Kling I2V with `generate_audio: false`.
  - `physical-gag` → Kling I2V with `generate_audio: true` for SFX.
- Watch for Kling Avatar v2 CJK text artifacts in the bottom strip (y ≈ 1700–1850). Subtitles are designed to mask them — don't try to prompt them away, you'll only waste Avatar calls.
- **Debug mode:** before launching the Avatar batch, list planned clips with per-clip cost and get user OK (see `rules/roles/manager.md` Debug-mode safety rules).
- General rules — `rules/roles/animator.md`.

### Sound

- TTS for the character (one voice, one stability profile chosen by `reaction_mode`) and for any off-screen customers / narrator (varying voices per scene to feel like different people).
- Voice picks by `reaction_mode`:
  - `deadpan-logical` → `Daniel` stability 0.10 or `George` stability 0.30
  - `gruff-angry` → `Adam` stability 0.10 style 0.9
  - `naive-literal` → `Bill` (or any youthful clear voice) stability 0.50
  - `military-formal` → `Daniel` stability 0.40
  - `world-weary-monotone` → `George` stability 0.40
  - `over-the-top-heroic` → `Adam` stability 0.15 style 0.7
- For each `dialogue-offscreen` scene: produce `customer.mp3` AND the silence-padded `scene-K.mp3` for Avatar.
- For each `monologue` / `inner-thought` scene: produce a single TTS track for Editor to overlay.
- ASS subtitles: per-scene, BorderStyle=4, MarginV=120, no event overlap, last event to clip end. See `rules/roles/sound.md` §10.
- Music: from `video-agent/music/Fun/`, volume 0.08. Never `Dark/` or `Drama/`.
- General rules — `rules/roles/sound.md` (especially §9 off-screen voices, §10 ASS invariants).

### Editor

- Per-scene burn-in pipeline:
  - `title-card`: scale → burn **title_lines** from storyboard.json as 4-stacked-line centered ASS text (Alignment=5). Style: line 1 "What if..." small italic (fs36), line 2 character name large bold (fs80), line 3 "Becomes a" small (fs36), line 4 role name large bold (fs52). No audio → add anullsrc. This overlay is MANDATORY — without it the title card is a blank shot.
  - `dialogue-offscreen`: scale → amix(Avatar audio, customer.mp3) → burn ASS via **ffmpeg-full** (libass required). ASS MUST contain TWO styles: **Default** (Worf lines, white bold 58, BorderStyle=4, MarginV=120) AND **Customer** (off-screen child lines, light-gray italic 52, BorderStyle=4, MarginV=120). Customer events are timed 0:00:00.30 → `duration(customer.mp3)`. Default events start after the silence gap (= `duration(customer.mp3)` + 0.6s). Text from `customer_line` and `character_line` in storyboard.json — verbatim, no re-transcription.
  - `dialogue-on-screen`: assemble shot-reverse-shot cuts → burn ASS.
  - `monologue` / `inner-thought`: silent I2V → overlay TTS (scene-K.mp3) via amix → burn ASS with Default style timed from 0:00:00.00.
  - `physical-gag`: I2V with Kling SFX baked → keep audio → no subtitles.
- bg-music.mp3 lookup: check `OUTPUT_DIR/bg-music.mp3` first (Sound writes it here), then `OUTPUT_DIR/build/bg-music.mp3`. Fail loudly if neither exists.
- Concat all scenes + CTA → `build/concat.mp4`.
- Apply **1.18× speedup** (`setpts=PTS/1.18` + `atempo=1.18`) BEFORE music mix. Self-check: `duration(final) ≈ sum(scene_durations) / 1.18`.
- Mix bg-music at volume 0.08.
- RMS sanity check on every `dialogue-offscreen` scene interval: > -30 dB. -40 dB = customer VO dropped.
- General rules — `rules/roles/editor.md` (especially §11 ffmpeg-full, §12 off-screen VO mix + customer subtitles, §13 artifact masking, §14 speedup).

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/what-if-real-life/
├── storyboard.json
├── bg-music.mp3
├── scenes/
│   ├── refs/
│   │   └── {char-slug}-sheet.png
│   ├── scene-1/                       # title card
│   │   ├── scene-1.png
│   │   └── scene-1.mp4
│   ├── scene-2/ ... scene-N/          # vignettes (dispatched by scene_type)
│   │   ├── scene-K.png
│   │   ├── scene-K.mp3                # character TTS (silence-padded for dialogue-offscreen)
│   │   ├── customer.mp3               # off-screen voice (if dialogue-offscreen)
│   │   ├── narrator.mp3               # if monologue
│   │   ├── inner.mp3                  # if inner-thought
│   │   └── scene-K.mp4
├── build/                             # all intermediate work (ASS, scaled mp4s, concat lists)
└── final.mp4                          # 1080×1920, ≤ 32s after 1.18× speedup
```

---

## Validation before publishing

- [ ] 5–8 scenes total (incl. title card), CTA appended
- [ ] Total duration after 1.18× speedup ≤ 32s
- [ ] Photorealistic style preserved across all scenes — character rendered as tangibly present in the real-world setting (no leaked stylized-source look)
- [ ] `reaction_mode` consistent across all character lines — no tonal flip mid-video
- [ ] No two vignettes share the same gag mechanic
- [ ] For every `dialogue-offscreen` scene: off-screen voice audible (RMS > -30 dB on the dialogue interval)
- [ ] For every `dialogue-offscreen` scene: customer's face is NOT turned to camera
- [ ] Subtitles BorderStyle=4 box (no full-width black bar), MarginV=120, no event overlap within a Style, last event in each scene reaches clip end
- [ ] No visible Kling Avatar v2 CJK artifact in any sampled frame (check at 1s and `clip_end − 0.3s` of each Avatar scene)
- [ ] Music is from `Fun/`, volume 0.08, audible but not overpowering
- [ ] 1.18× speedup applied (NOT 1.15×)
- [ ] CTA appended

---

## Anti-patterns

- ❌ Mixing game style with real world (Roblox-shaped Roblox guy in a Roblox-screenshot store) — defeats the realism contrast
- ❌ `reaction_mode` flips mid-video (Spock suddenly enthusiastic, Kratos suddenly gentle) — breaks the bit
- ❌ Customers facing camera in `dialogue-offscreen` scenes — they'd need lipsync, defeating the cost economy
- ❌ Two vignettes with the same gag mechanic (two "absurd customer order" gags, two "boss screams at toddlers" gags)
- ❌ Calling Avatar v2 with non-padded audio when the gag needs customer-first rhythm
- ❌ Forgetting to mix off-screen / narrator VO into the final audio (RMS check catches it)
- ❌ Full-width drawbox to hide CJK artifact (cuts the picture — use ASS `BorderStyle=4` box only)
- ❌ MarginV=480 thinking "raise subtitle higher" — Alignment=2 MarginV grows UP from bottom, so big MarginV moves text AWAY from a bottom-strip artifact
- ❌ Music from `Dark/` or `Drama/` — mood mismatch
- ❌ Skipping the 1.18× speedup step
- ❌ Burning ASS subtitles with stock ffmpeg (lacks libass — subtitles silently dropped)
- ❌ Two ASS Dialogue events with overlapping time ranges within the same Style (text scrambles, word order looks broken)
- ❌ `-shortest` in any ffmpeg call (universal anti-pattern — use `apad`)
