---
subtitle_style: bold
subtitle_offset_s: 0
subtitle_mask: false
subtitle_highlight: false
subtitle_extras: []
---

# Format "TOP List" — countdown of top-5 characters / locations / items in a game

<!-- Графические оверлеи `#N` (Montserrat Black ~220px) и `{NAME}` (Bebas Neue ~96px) — это НЕ субтитры, а graphic overlays формата. Описаны в секции Editor ниже. Subtitle_style=bold относится только к narrator-сабам (если у сцены есть `tts`). -->


Stylized "TOP 5" countdown video: an animated title card in the game's visual language, then 5 items revealed in **5 → 1** order with the climax on #1. Narrator delivers one short, punchy line per item ("In third place: T'Pol from Enterprise — Vulcan grace and a logic-defying figure.").

This file is the **playbook**: when to use, concept, budget, role briefs. Craft rules — in `rules/roles/*.md`.

---

## When to use

Keywords: `"top-5"`, `"top 5"`, `"топ-5"`, `"топ 5"`, `"top list"`, `"топ"`, `"топ персонажей"`, `"top characters"`, `"top heroes"`, `"top locations"`, `"top items"`, `"best characters"`, `"ranking"`, `"рейтинг"`, `"countdown"`.

Typical themes: top-5 women characters, top-5 starfleet ships, top-5 villains, top-5 maps/locations, top-5 weapons/skins/items, top-5 ultimates.

Not for: news / patch recaps (use `news`), lore monologue (use `character-story`), single hero action scene (use `standard`).

---

## Concept

- **Genre:** stylized listicle countdown (Buzzfeed-meets-MTV-countdown, in game style)
- **Style:** game-specific — pulled from `games/{GAME_TAG}/{GAME_TAG}.md` (`prompt_prefix`, `palette`, `lighting`)
- **Style consistency rule (HARD):** the visual style is described ONCE at the video level in `visual_identity.style_tags` and applied VERBATIM to every scene's `image_prompt`. All 7 scenes must look like the same artist/render pipeline made them. Mixing 3D-render with illustration in the same video looks broken — even a single off-style scene wrecks the countdown rhythm. Per-scene style overrides are FORBIDDEN.
- **Style confirmation at video start (MANDATORY).** Before kicking off Scenarist, Manager MUST confirm the target visual style with the user. The game config (`games/{TAG}/{TAG}.md`) declares a default house style (e.g. Star Trek Timelines = "semi-realistic Pixar-quality 3D"). For top-list videos the default is to MATCH the game's house style so the video reads as on-brand. If the user wants something different (illustration, comic, retro), they must say so at the start — drift discovered mid-pipeline costs an additional NB2 regen pass and may sink the budget. The chosen style is then frozen in `visual_identity.style_tags` and applied verbatim per the previous rule.
- **Anchor-ref style trap:** Supabase character refs from other formats may have been generated in a different style (e.g. character-story uses 3D Pixar look). When you pull them as `/edit` anchor refs, NB2 copies that style and breaks consistency for THIS video. **If an existing Supabase ref is in a different visual style than the locked `style_tags`, do NOT use it as a ref — generate the scene text-to-image with detailed character_description + style tags instead.** Pay $0.08 of NB2 to keep the video coherent; do not save pennies and ship a broken-looking ad.
- **N:** fixed **5 items**
- **Order:** **5 → 1** (climax at #1)
- **Rank #1 is ALWAYS rendered as 2 clips × 5s = 10s total** — split visually (wide hero shot → close-up payoff) with narrator carrying across both halves. This gives the climax breathing room and a cinematic match-cut moment that no other rank gets.
- **Duration:** ~35s total (1× title 5s + 4× item 5s + 2× rank-1 climax 5s = 35s; CTA overlay only on the SECOND part of rank-1)
- **Total scenes in storyboard.json: 7** (indices 0..6). Rank-1 occupies indices 5 and 6, both with `rank: 1`, distinguished by `part: 1` and `part: 2`.
- **Budget:** up to **$5.00** per video. Stop if spend > **$4.50**.
- **Frame format:** 9:16 (1080×1920)

### Models

- **Image:** Nano Banana 2 (title card + 5 item illustrations, 6 generations total)
- **Video:** Kling I2V v3 Standard (`generate_audio: false`) — primary; Kling 2.6 Pro fallback
- **Audio:** ElevenLabs TTS narrator overlay (1 short line per item + optional title intro line); music bed under everything
- **Pre-built assets:** title card is generated inline. CTA is a **pack-shot from Supabase if the game has one** (query `game_assets` for `tags @> ["cta"]` and `asset_type` containing "video"); otherwise fall back to a drawtext CTA overlay on the rank-1 part-2 clip. Star Trek Timelines, for example, has `assets/star-trek-timelines/refs/cta.mp4` ready.

---

## Budget (rough estimates)

| Component | 5s clip | 7× total |
|---|---|---|
| NB2 image | $0.08 | $0.56 |
| Kling v3 Standard I2V 5s (no audio) | $0.42 | $2.94 |
| Kling 2.6 Pro I2V 5s (no audio, fallback) | $0.35 | $2.45 |
| ElevenLabs TTS (~6–8 short lines, ≤10 words) | ~$0.05 | ~$0.30 |
| NB2 anchor refs (per new character — when not in Supabase) | $0.08 | varies |

| Variant | Total |
|---|---|
| Typical (v3 Standard, all anchors in Supabase) | **~$3.80** |
| Worst case (2 new anchor refs to generate) | ~$3.96 |
| Fallback (2.6 Pro) | ~$3.31 |

Slightly more than the previous 6-clip layout because rank-1 is split into 2 clips for the climax. Still cheaper than `standard` ($5).

---

## Video structure

| Index | Beat | Duration | Visual | Narrator (TTS) |
|---|---|---|---|---|
| 0 (title) | Hook / theme reveal | 5s | Title-card NB2 + Kling I2V: sparkles, lens-flare, slow push-in, baked "TOP 5 {THEME}" text | Optional: 1-line teaser, e.g. `"Five Starfleet women who broke the warp drive — who tops the list?"` |
| 1 (`#5`) | Lowest entry | 5s | Item NB2 + Kling I2V: subtle motion (camera arc, breath, magical aura) | `"In fifth place: {NAME} — {one-line reason}."` |
| 2 (`#4`) | Rising | 5s | Item NB2 + Kling I2V | `"Number four: {NAME} — {one-line reason}."` |
| 3 (`#3`) | Mid | 5s | Item NB2 + Kling I2V (slightly more intense motion) | `"At three: {NAME} — {one-line reason}."` |
| 4 (`#2`) | Penultimate, tease #1 | 5s | Item NB2 + Kling I2V (energy step up) | `"And the runner-up: {NAME} — {one-line reason}."` |
| 5 (`#1`, part 1) | **Climax** — wide hero reveal | 5s | Item NB2 + Kling I2V (large motion: pull-back, dramatic lighting, particles, banner reveal) | `"Topping the list: {NAME}. {one-line reason A — pacing setup}."` |
| 6 (`#1`, part 2) | **Climax payoff** + CTA overlay last 1.5s | 5s | Item NB2 (chain from scene 5) + Kling I2V (closer angle: emotional push-in, slow-motion hair drift, screen flash) | `"{one-line reason B — emotional/legacy beat}. Follow for more tops."` |

- `camera_angle` MUST be different for adjacent clips (close-up → medium → low-angle → wide → hero shot)
- Energy / motion intensity escalates from #5 → #1
- Numbers count DOWN (5, 4, 3, 2, 1) — never up
- **Rank-1 split rule (HARD):** the climax is ALWAYS rendered as 2× 5s clips. Part 1 = wide / hero / establishing reveal of the character. Part 2 = closer / emotional payoff (push-in, slow-mo hair drift, eye contact). Both clips share the same `rank: 1`, `name`, `character_description`, and Janeway anchor ref. They differ in `part` (1 vs 2), `camera_angle` (wide → close), `motion_prompt` (reveal → payoff), and `tts` (split sentence).
- Narrator TTS for rank-1 is split into 2 separate ≤10-word lines, one per clip. Part-2's TTS MUST end with literal `"Follow for more tops."`
- `cta_overlay: true` ONLY on part 2 (scene 6) — never on part 1.

---

## Title card (clip 0) — special construction

Two-stage build, the same as a regular scene but with text baked into the NB2 image:

1. **NB2 image** (608×1080):
   - Composition: hero collage / silhouette montage of the 5 items behind a big foreground title plate
   - Text baked into the image: `"TOP 5"` (huge) and `"{THEME}"` (e.g. `"STARFLEET WOMEN"`)
   - Style: from `games/{GAME_TAG}/{GAME_TAG}.md` — `prompt_prefix`, `palette`, `lighting`
   - Font: read `top_font` from `games/{GAME_TAG}/top-list_special.md` if present, otherwise default **"Montserrat Black"** or **"Bebas Neue"** (bold, sans-serif, high stroke), accent color from game `palette`
   - Add: lens-flare, sparkles, magical particles, embers — whatever fits the game's tone

2. **Kling I2V**, `generate_audio: false`, `duration: 5`:
   - `motion_prompt`: short, multi-action — sparkles drift, light rays sweep across the title, slow camera push-in, particles swirl. Two distinct movements minimum.
   - Title plate must stay readable: no warp, no rotation past 5°, no obscuring particles in the center 60% of the frame
   - `negative_prompt`: `"warped text, illegible letters, garbled text, distorted typography, blurred title, missing letters, extra letters"`

3. **No text-overlay pass needed** in Editor for the title card — text is baked into NB2. Editor only handles the optional narrator subtitle.

---

## Per-item clip (clips 1–5) — visual structure

NB2 image of the character / location / item, **no number-text baked in** (numbers are added by Editor as a drawtext/PIL overlay, so we can iterate fast without re-rendering NB2):

- Composition: hero pose / iconic shot of the item. Character/object occupies center 50–70% of frame, leaves room top-left or top-right for the number overlay
- Style: from game config (`prompt_prefix`, `palette`, `lighting`)
- For locations: wide establishing shot, optional foreground silhouette for depth
- For items/weapons: 3/4 hero-product angle on a stylized background (smoke, sparks, energy)

Kling I2V `motion_prompt`: ≥2 distinct micro-motions, e.g. `"hair drifts in low gravity AND camera arcs slowly to the right; particles drift across the lens"`. Escalate motion intensity #5 → #1.

---

## Text overlays (Editor)

Two overlays per item clip (drawtext or PIL), applied **per-scene before concat**:

| Overlay | Position | Style | Timing |
|---|---|---|---|
| Number `"#5"` (huge) | top-left @ x=80, y=200 | game font (or Montserrat Black), ~220px, accent color stroke 4px, black drop-shadow | 0.0s–5.0s (whole clip) |
| Name `"T'POL"` (uppercase) | bottom third @ y=1400 (above subtitle area) | game font (or Bebas Neue), ~96px, white with 6px black stroke | 0.3s–5.0s (slide-in from left 0.0–0.3s) |

### CTA — pack-shot from Supabase (preferred)

If `game_assets` has a CTA video (`tags @> ["cta"]`, `asset_type` like "%video%" OR file extension `.mp4`):
- Download once at Phase 0 (Manager), pass URL/path to Editor as `CTA_PATH`
- Editor normalizes (scale 1080×1920, fps=30, AAC 128k) and **concatenates after scene 6** as the final clip
- Apply fade-to-black ONLY on the CTA tail (last 0.5–1.0s), NOT on scene 6
- No drawtext CTA on scene 6 in this path
- Music: fade out music 0.5s before the CTA clip starts so the pack-shot's own audio (if any) breathes; if pack-shot is silent, music continues at volume 0.10 under the pack shot

### CTA — fallback drawtext (only if no Supabase pack-shot)

If no Supabase CTA video exists for the game: drawtext on the rank-1 part-2 clip (scene 6), last 1.5s: `"Follow for more tops →"` lower-center, white on translucent black box. Fade out final 1.0s of scene 6.

---

## Subtitles

Narrator subtitles per-scene (drawtext on each `-scaled.mp4` BEFORE concat — never on the concatenated final, whisper misses voices on concat).

- Method: drawtext ffmpeg (single-line, may auto-wrap to 2)
- Font: **Montserrat Bold 44px** (or game-specified)
- Position: lower third, `y=1550`, centered
- Color: white, stroke 4px black
- Timing: matches TTS line, with `adelay=200ms` (TTS starts 0.2s into clip so visual lands first)

Title card subtitle is optional (skip if title intro line is empty).

---

## Prompting rules (NB2 + Kling)

### NB2 chain

- **Anchor ref:** for each item, if the character already exists in Supabase `game_assets` (`character_name=eq.{name}`), **check the ref's visual style BEFORE using it**. If it matches the locked `visual_identity.style_tags` for this video → pull and use as `image_urls[0]`. If it's in a different style (e.g. 3D Pixar ref while this video is locked to painted illustration) → **DO NOT USE IT**. Generate text-to-image with `image_urls: []` + the full character_description + locked style_tags. The $0.08 NB2 spend is worth far more than a broken-looking scene.
- **Chain strategy:** `[anchor_ref?, prev_scene?]` (max 2 refs). Title card has no prev_scene — pure text-to-image with style refs only. For ranks 5–2 each character is different, so chaining on prev_scene would bleed the previous character's identity into the next — usually anchor-only is safer. **The rank-1 climax pair IS the exception**: scene 6 ALWAYS chains on scene 5 (same character, style continuity guaranteed by the pair).
- **Identity:** `visual_identity.character_description` is verbatim across the brief; per-item `character_description` overrides for that specific entry only.
- **Style verbatim:** the EXACT `visual_identity.style_tags` string is appended to every `image_prompt` (every scene, no exceptions). Storyboarder MUST copy-paste it; rewording or paraphrasing loses style fidelity.

### Rank-1 climax pair — visual differentiation (HARD RULE)

Scene 5 (part 1) and scene 6 (part 2) feature the SAME character. To prevent NB2 from copying scene-5 verbatim when chained, scene 6's `image_prompt` MUST add a **"winner beat"** that visually distinguishes it as the victory shot — choose one or combine:

- **Crown / laurel wreath** (gold laurel above the head)
- **Fireworks / golden sparks bursting** around the character
- **Pedestal / podium / raised platform** lifting the character
- **#1 banner unfurling** behind them
- **Golden spotlight from above** + soft confetti
- **Trophy / medal** held or floating beside them

Combined with a tighter crop (close-up vs scene 5's wide hero), the second image must read clearly as the "this is the winner" moment — not a static rerun of part 1.

### Kling I2V

- `generate_audio: false` (always — TTS overlay handles sound, music bed handles ambience)
- `duration: 5` (locked for every clip including title)
- `motion_prompt`: minimum 2 different actions, escalating from #5 → #1
- Title card extra: `negative_prompt` mandatory for text legibility
- Polling base: `fal-ai/kling-video` (2-segment path)

---

## Music

- **Per-game mood** — pulled from `games/{GAME_TAG}/{GAME_TAG}.md` (e.g., MLBB → anime-epic, Star Trek → orchestral-sci-fi, Marvel Snap → comic-burst). If game config doesn't specify, default to **"hype / epic countdown"**.
- Volume: `0.15`
- Apply via `amix` on the concatenated video with `apad` on music side. **NEVER `-shortest`.**
- Optional: small `volume` boost (×1.5) on clip 5 (`#1`) for the climax. Implement via timeline crossfade if used.

---

## Voice (ElevenLabs TTS)

| Role | Voice | stability | Notes |
|---|---|---|---|
| Narrator | `George` (energetic male) or `Charlotte` (energetic female) | 0.30 | Use `voice` name string, NOT `voice_id` hash. Per-game override allowed via `games/{TAG}/top-list_special.md` |

Lines are **short** (8–15 words). Style direction in TTS prompt: `"energetic countdown host, building excitement toward number one"`.

---

## Game-specific overrides (optional)

`games/{GAME_TAG}/top-list_special.md` (create only if needed):

```markdown
# TOP List — settings for {Game Name}

## Title card
- `top_font`: e.g. "Eurostile Bold Extended" (Star Trek), "Anime FX" (MLBB)
- `title_card_style`: extra style line for NB2 prompt
- `accent_color`: hex for text stroke / glow

## Numbers / names
- `number_font`: defaults to top_font
- `name_font`: defaults to "Bebas Neue"
- `name_uppercase`: true (default)

## Narrator
- `narrator_voice`: "George" / "Charlotte" / etc.
- `tone_directive`: extra direction for TTS

## Music
- `music_mood`: e.g. "orchestral-sci-fi", "anime-epic", "comic-burst"
```

If file absent → defaults from this playbook.

---

## Storyboard JSON (template)

```json
{
  "format": "top-list",
  "theme": "STARFLEET WOMEN",
  "game_tag": "star-trek",
  "visual_identity": {
    "style_tags": "from game config",
    "palette": "from game config",
    "lighting": "from game config",
    "top_font": "Eurostile Bold Extended",
    "accent_color": "#F5A623"
  },
  "music": {"mood": "orchestral-sci-fi", "volume": 0.15},
  "voices": {
    "narrator": {"voice": "Charlotte", "stability": 0.30, "language_code": "en"}
  },
  "scenes": [
    {
      "index": 0,
      "role": "title_card",
      "clip_type": "title",
      "duration_sec": 5,
      "title_text": "TOP 5",
      "subtitle_text": "STARFLEET WOMEN",
      "tts": "Five Starfleet women who broke the warp drive — who tops the list?",
      "image_prompt": "...",
      "motion_prompt": "sparkles drift across title, lens flare sweeps left to right, slow camera push-in"
    },
    {
      "index": 1,
      "rank": 5,
      "name": "T'Pol",
      "clip_type": "item",
      "duration_sec": 5,
      "camera_angle": "medium close-up, three-quarter",
      "character_description": "Vulcan woman, dark hair, blue Enterprise NX-01 uniform...",
      "tts": "In fifth place: T'Pol from Enterprise — Vulcan grace and a logic-defying figure.",
      "image_prompt": "...",
      "motion_prompt": "eyes blink subtly, hair drifts, camera arcs slowly to the right"
    },
    {"index": 2, "rank": 4, "name": "...", "...": "..."},
    {"index": 3, "rank": 3, "name": "...", "...": "..."},
    {"index": 4, "rank": 2, "name": "...", "...": "..."},
    {
      "index": 5,
      "rank": 1,
      "name": "Seven of Nine",
      "clip_type": "item_climax",
      "duration_sec": 5,
      "camera_angle": "low-angle hero shot",
      "tts": "Topping the list: Seven of Nine. The queen of Borg-meets-bombshell. Follow for more tops.",
      "image_prompt": "...",
      "motion_prompt": "camera zooms in, screen flash, particles burst from behind, hair drifts",
      "cta_overlay": true
    }
  ]
}
```

---

## Role briefs

### Scenarist

- Exactly **7 scenes**: 1 title + 4 items (ranks 5..2) + 2 climax clips (both rank 1, `part` 1 and 2).
- Title scene fields: `role: "title_card"`, `clip_type: "title"`, `title_text`, `subtitle_text`, optional `tts`.
- Item scene fields: `rank` (int), `name`, `character_description` (8+ visual details), `camera_angle`, `motion_hint`, `tts`.
- Rank-1 climax: TWO scenes (indices 5 and 6) BOTH with `rank: 1`. Index 5 = `part: 1`, `clip_type: "item_climax"`. Index 6 = `part: 2`, `clip_type: "item_climax"`. Same `name` and `character_description`. Different `camera_angle` (wide → close), `motion_hint`, and `tts` text.
- `tts` for ranks 5..2: **8–15 words**, must START with the rank phrase ("In fifth place: / Number four: / At three: / And the runner-up:"). Include name + one-line reason.
- `tts` for rank 1: **two short lines (≤10 words each)**. Part 1 starts with `"Topping the list:"` + name + a pacing-setup beat. Part 2 = emotional/legacy beat + literal closing `"Follow for more tops."`
- `camera_angle` different for adjacent scenes (including across the rank-1 pair: e.g. wide hero → close-up push-in).
- `motion_hint` ≥2 different actions; intensity escalates 5→1; rank-1 part 2 is the most intense.
- `cta_overlay: true` ONLY on the rank-1 part-2 scene (index 6). NOT on part 1.
- Read `games/{GAME_TAG}/{GAME_TAG}.md` for style, palette, lighting. If `games/{GAME_TAG}/top-list_special.md` exists, override accordingly.
- General rules — `rules/roles/scenarist.md`

### Storyboarder

- **7 NB2 generations** (title + 4 items + 2 climax clips for rank-1). All 608×1080 (9:16).
- **Title card NB2**: bake `"TOP 5"` + `"{theme}"` text into the image using `top_font` from `visual_identity` (defaults Montserrat Black / Bebas Neue). Style refs only, no prior-scene ref. Add sparkles/lens-flare/particles aligned with game palette.
- **Item NB2**: do NOT bake numbers — numbers are an Editor overlay. Compose with center 50–70% subject + clear space top-left for the `#N` overlay.
- **No on-screen text on character images (HARD RULE).** Per-item NB2 outputs must be CLEAN illustrations — no character-card layout, no game UI labels, no nameplate banners, no era/series logos ("STAR TREK: DEEP SPACE NINE", "VOYAGER" etc.), no #N number, no caption strip, no rarity stars/borders. All text and number callouts come from Editor drawtext overlays. Every per-item `image_prompt` MUST end with `". Clean illustration with NO on-screen text, NO captions, NO labels, NO logos, NO nameplate banners, NO game UI of any kind."` Push the same intent into NB2 `negative_prompt` and into the per-clip Kling `negative_prompt` so any drift is caught: `"on-screen text, character card layout, trading card, nameplate, banner text, game UI labels, captions, watermark, rarity stars, series logo, era label, subtitle"`.
- **Rank-1 climax pair (scenes 5 + 6):** generate part 1 first (wide hero shot, ≥7-detail backdrop, dramatic establishing composition). Then generate part 2 using part 1 as `[anchor_ref?, scene-5_image]` chain — same character, closer angle, same lighting/palette. Part 2 = closer crop, more intimate; show eyes/face cleanly for the emotional payoff.
- Chain refs: `[anchor_ref?, prev_scene]` for items; title card uses no prev_scene; rank-1 part 2 ALWAYS chains on part 1.
- If a character already has a Supabase `game_assets` ref (`character_name=eq.{name}`) — pull and use it as anchor. Otherwise generate a new anchor ref (sheet style, 16:9 neutral bg, ~$0.08) FIRST, save to `games/{GAME_TAG}/assets/refs/`, upload to Supabase, then use it for all scenes featuring that character.
- Character description verbatim from `visual_identity` + per-scene additions.
- General rules — `rules/roles/storyboarder.md`

### Animator

- **Model:** Kling I2V v3 Standard (primary), Kling 2.6 Pro (fallback).
- **All 7 scenes:** `duration: 5`, `generate_audio: false`, **NO end frame** (start frame only — end frames make Kling interpolate-then-freeze).
- **Three motion layers per clip (MANDATORY).** Every clip's `motion_prompt` must specify three concurrent layers, each continuing throughout the full 5s — no "then settles" / "then steady" / "then dies" cues (Kling reads those as freeze):
  1. **Camera move** — pick one per clip: slow push-in, slow pull-back, lateral dolly, low boom up, crane up, parallax handheld drift, slow arc. Distribute variety across the 7 clips. NEVER "camera holds steady".
  2. **Environment motion** — wind, smoke, sparks, particles, light flicker, distant figures, holographic UI motion, console glow pulses, viewscreen shimmer, starfield drift. Continuous throughout the 5s.
  3. **Character action** — one gesture or expression beat sustained through the clip (slow head turn, eyes lifting, half-smile forming, jaw tightening, hand drifting). Sustained, NOT completed mid-clip.
- **Phrasing rules for `motion_prompt`:**
  - Continuous-tense verbs (`is drifting`, `tightens`, `lifts gently`) and explicit duration cues (`throughout the shot`, `held for the full 5 seconds`, `continues across the frame`).
  - **Banned phrases (read as freeze by Kling):** `"then settles"`, `"then steady"`, `"then holds"`, `"then dissipates"`, `"then dies"`, `"camera holds steady"`, `"hold position"`, `"no morphing"`, `"maintain exact character appearance"`. NEVER use.
  - **Avoid stacked negative listings.** Do not pile `No walking, no running, no fighting, no impact`. Replace with positive grounded instructions ("character remains rooted at the console", "feet planted, weight shifts gently").
  - Trust Kling to hold identity from the start frame — do not write defensive identity-lock phrases.
- **Micro vs. macro motion.** Avoid full-body locomotion (walking, running, combat hits) — identity drift becomes visible. Motion WITHIN the frame (head, hands, torso, breath, sustained gestures, environment) MUST be alive.
- **Rank-1 climax pair (scenes 5 + 6):** generate independently as two separate Kling I2V calls (no end frame; two distinct shots). Part 1 motion: pull-back reveal + viewscreen flare + golden particles bursting outward + still-sustained character pose. Part 2 motion: slow push-in + laurel wreath shimmer + golden sparks rising + character eyes lifting to camera in the final third. Strongest motion intensity of the whole video.
- **Universal `negative_prompt` (every clip):** `"on-screen text, captions, character card, trading card layout, nameplate, banner text, game UI labels, watermark, rarity stars, series logo, era label, talking, mouth open, lip sync, blurry face, text deformation, garbled letters"`. Title-card scene 0 adds the text-legibility set already specified in its section.
- Title card: `negative_prompt` mandatory (`"warped text, illegible letters, garbled text, distorted typography, blurred title, missing letters, extra letters"`).
- Items: standard negative-prompt set + game-specific anti-style.
- Polling base = first 2 segments of endpoint (`fal-ai/kling-video`).
- Validate after each clip: filesize > 100KB, ffprobe duration ≈ 5.0s ±0.2s.
- General rules — `rules/roles/animator.md`

### Sound

- **ElevenLabs TTS** for each scene that has non-empty `tts` (title card may skip).
- Voice from `voices.narrator` in storyboard. Use `voice` name, NOT `voice_id`.
- Upload each `.mp3` to Supabase → write `audio_url` back into the scene.
- **Subtitles per-scene** via drawtext on `-scaled.mp4` BEFORE concat (font: Montserrat Bold 44px, lower third, white + 4px black stroke).
- **Music bed**: pull mood from `visual_identity` (or game config), `volume=0.15`, mix via `amix` + `apad` on the concatenated video. Never `-shortest`.
- General rules — `rules/roles/sound.md`

### Editor

- For each item clip with a `rank` (scenes 1–6), apply **two drawtext overlays** before concat:
  - `#{N}` huge top-left (game/Montserrat Black ~220px, accent stroke 4px, drop shadow), full duration
  - `{NAME}` uppercase bottom-third (game/Bebas Neue ~96px, white + 6px black stroke), 0.3s slide-in
- Rank-1 pair (scenes 5 + 6) both show `#1` + `{NAME}` overlays. They are visually continuous (same number, same name), but distinct shots.
- Title card (scene 0): NO number/name overlay (text is in NB2). Only subtitle if `tts` present.
- Per-scene pipeline: subtitles → number+name overlay → normalize (1080×1920, 30fps, `-c:v libx264 -preset slow -crf 20`, AAC 128k).
- Concat with re-encode (NOT `-c copy`); hard cuts, NO crossfade between items (countdown rhythm). Hard cut also between rank-1 part 1 and part 2 — the match-cut is the moment, not a dissolve.
- **CTA pack-shot from Supabase (preferred):** query `game_assets` for `tags @> ["cta"]` + video asset. If present, normalize (1080×1920, 30fps, AAC 128k) and concatenate AFTER scene 6 as the final clip. Apply fade-to-black on the pack-shot tail (last 0.5–1.0s), NOT on scene 6. Music fades 0.5s before the pack-shot starts.
- **CTA fallback (only if no Supabase pack-shot):** drawtext `"Follow for more tops →"` lower-center on translucent black box on scene 6, last 1.5s. Fade-to-black final 1.0s of scene 6.
- Music: `amix` with TTS, music `volume=0.15`, music `apad`. **NEVER `-shortest`.**
- General rules — `rules/roles/editor.md`

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/top-list/
├── storyboard.json
├── scenes/
│   ├── scene-0/                # title card
│   │   ├── scene-0.png         # NB2 with baked title text
│   │   ├── scene-0.mp4         # Kling I2V raw
│   │   ├── scene-0.mp3         # TTS (optional)
│   │   └── scene-0-sub.mp4     # with subtitle (if tts)
│   ├── scene-1/                # rank #5
│   │   ├── scene-1.png         # NB2 (no number)
│   │   ├── scene-1.mp4         # Kling I2V raw
│   │   ├── scene-1.mp3         # narrator TTS
│   │   ├── scene-1-overlay.mp4 # with #5 + name overlay
│   │   └── scene-1-sub.mp4     # + subtitle
│   ├── scene-2/  # rank #4
│   ├── scene-3/  # rank #3
│   ├── scene-4/  # rank #2
│   ├── scene-5/  # rank #1 part 1 (wide hero reveal)
│   └── scene-6/  # rank #1 part 2 (close payoff + CTA + fade)
├── concat-list.txt
└── final.mp4
```

---

## Validation before publishing

- [ ] `format: "top-list"`, `theme` set, exactly **7 scenes** (1 title + 4 items + 2 rank-1 climax clips)
- [ ] Ranks present: 5, 4, 3, 2, 1, 1 (rank 1 appears twice with `part: 1` and `part: 2`); no other duplicates / gaps
- [ ] Title-card NB2 contains legible `"TOP 5"` + `"{theme}"` (visual check during Storyboarder — programmatic only: filesize > 50KB)
- [ ] Item NB2s have NO number baked in (numbers come from Editor overlay)
- [ ] All 7 Kling clips `generate_audio: false`, duration 5s ±0.2s
- [ ] `camera_angle` different for adjacent scenes (including across rank-1 pair: part 1 wide → part 2 close)
- [ ] `motion_hint` ≥2 different actions per scene; intensity escalates 5→1
- [ ] Each item TTS begins with the correct rank phrase ("In fifth place / Number four / At three / Runner-up / Topping the list")
- [ ] Rank-1 TTS split across two parts: part 1 ≤10w; part 2 ≤10w and ends with literal "Follow for more tops."
- [ ] Per-scene drawtext applied BEFORE concat (subtitles + number/name overlays)
- [ ] CTA: if game has Supabase pack-shot video → concatenated after scene 6 (no drawtext CTA on scene 6, no fade-to-black on scene 6 — fade goes on pack-shot tail). If no pack-shot → drawtext CTA on scene 6 last 1.5s + fade-to-black on scene 6 last 1.0s.
- [ ] Per-item NB2 outputs are CLEAN illustrations — no on-screen text, no character-card layout, no game UI labels, no era logos, no nameplate banners (visual check during regression review; programmatic only checks filesize/dims)
- [ ] Visual style was confirmed with the user at video start; `visual_identity.style_tags` matches that decision and is applied verbatim to every `image_prompt`
- [ ] Every `motion_prompt` includes three concurrent layers (camera move + environment motion + character action) and contains NONE of the banned freeze phrases (`then settles`, `then steady`, `camera holds steady`, `hold position`, `no morphing`, `maintain exact character appearance`)
- [ ] Every Kling clip has the universal anti-text `negative_prompt` set
- [ ] Music `volume=0.15`, mixed via `amix` + `apad`, NO `-shortest`. Music fades 0.5s before pack-shot starts (if pack-shot path used).
- [ ] `final.mp4`: 1080×1920, 30fps. Duration = ~35s without pack-shot or ~35s + pack-shot length. Budget ≤ $5.00

---

## Anti-patterns

- ❌ Baking numbers (`"#5"`, `"#4"`...) into NB2 — locks the rendering, can't iterate. Always overlay in Editor.
- ❌ Counting UP (1→5). Always 5→1 with climax on #1.
- ❌ Same `camera_angle` on adjacent items (kills rhythm).
- ❌ `generate_audio: true` on Kling I2V — wastes ~$1.20/video, TTS+music bed already cover sound.
- ❌ Subtitles applied AFTER concat — whisper misses voices on concatenated tracks.
- ❌ Crossfade between item clips — countdown needs hard cuts for snap rhythm.
- ❌ `-shortest` in FFmpeg (universal). Always `apad` on music side.
- ❌ `voice_id` hash in ElevenLabs — use `voice` name string.
- ❌ Title card NB2 without `negative_prompt` for text legibility — Kling warps text without it.
- ❌ Generating a CTA video — top-list uses a text overlay on the rank-1 clip, no separate CTA clip from Supabase.
- ❌ TTS lines longer than 15 words on rank 5–2, or longer than 10 words on rank-1 parts — eats into the 5s clip, narration runs over the next clip's overlay.
- ❌ Rendering rank-1 as a single 5s or 10s clip. RULE: rank-1 is ALWAYS 2× 5s clips with a hard match-cut. No exceptions.
- ❌ Identical `camera_angle` between rank-1 part 1 and part 2 — the climax pair must visually contrast (wide → close).
- ❌ CTA overlay on rank-1 part 1 — only part 2 carries the CTA and the fade-to-black.
- ❌ Mixing visual styles between scenes (e.g. 3D Pixar render in one scene, painted illustration in the next). Style is locked at the VIDEO level in `visual_identity.style_tags` and applied verbatim to every `image_prompt`. Even one off-style scene breaks the countdown rhythm.
- ❌ Pulling a Supabase anchor ref without checking its style. Refs generated for other formats (e.g. character-story's polished 3D look) will hijack the style of THIS video. If style doesn't match → generate text-to-image instead.
- ❌ Scene 6 looking identical to scene 5. The chain reference makes NB2 reproduce part 1 unless the prompt explicitly demands a NEW visual element (crown / laurel wreath / fireworks / pedestal / #1 banner) plus a tighter crop. No winner beat = broken climax cut.
- ❌ Per-item NB2 outputs containing baked text — character-card layouts, game UI labels, era/series logos ("STAR TREK: DEEP SPACE NINE"), nameplate banners, rarity stars. Per-item images must be CLEAN; all callouts come from Editor drawtext overlays.
- ❌ Generating a top-list video without first confirming the visual style with the user. Style drift discovered mid-pipeline costs an extra NB2 regen pass and risks busting the budget.
- ❌ `motion_prompt` with "camera holds steady" / "then settles" / "then steady" / "hold position" / "no morphing" / "maintain exact character appearance" — Kling reads these as freeze cues and produces static clips. Every clip needs three concurrent motion layers (camera + environment + character).
- ❌ Using a drawtext CTA overlay when the game already has a Supabase pack-shot video. The pack-shot is the on-brand, branded ending; drawtext is the fallback.
