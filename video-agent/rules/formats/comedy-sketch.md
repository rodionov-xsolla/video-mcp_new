# Format "Comedy Sketch" — deadpan vertical comedy sketches

A recurring deadpan straight-man character is placed in a mundane "fish out of water" job/situation (e.g. Spock as a barista). Comedy comes from the contrast between the character's emotionless logic and an over-the-top human customer/world reacting to them. 6 gags + 1 title card, ~30s after speedup.

This file is the **playbook**: when to use, concept, budget, role briefs. Craft rules — in `rules/roles/*.md`.

---

## When to use

Keywords: "comedy sketch", "sketch", "deadpan", "barista", "fish out of water", "комедийный скетч", "скетч", "дедпан".

Best fit when the game has a strong serious/iconic character (Spock, a tactical commander, a stoic dragon) that can be dropped into a banal civilian job for absurd contrast. Format is **single-shot per video** — no story bible, no continuity, each video is its own gag set.

---

## Concept

- **One recurring straight-man** (game character, photorealistic, locked outfit suited to the new job — e.g. green apron + dark t-shirt over the character's natural look)
- **6 gags + 1 title card** — title card opens, then each gag is one self-contained micro-scene
- **Off-screen / back-to-camera customers** — extras whose faces are NEVER turned to camera, so they don't need Avatar lipsync. Their voice is a separate TTS overlay (see role briefs below)
- **Style:** Photorealistic, **overrides game default** (Pixar/3D/anime). Comedy works better on a believable surface.
- **Frame:** 9:16 vertical (1080×1920)
- **Duration:** 30–38s pre-speedup → ~26–32s after 1.18× speedup
- **Budget:** $6.00 max, stop at $5.40

### Models

- **Title card (scene 1):** NB2 still with baked title text, or short Kling I2V 3s for subtle motion
- **Gag scenes (Avatar reactions, 5 clips):** Kling Avatar v2 Standard ($0.056/s) — straight-man's deadpan response to an off-screen customer line
- **Transition scene (1 clip, optional):** Kling I2V 5s with start+end frames — used when the gag requires a visible expression change (e.g. deadpan → forced smile)
- **Audio:**
  - Straight-man speech via ElevenLabs TTS → Avatar v2 lipsync
  - Off-screen customer/extras speech via separate ElevenLabs TTS → mixed by Editor (see Sound brief)

---

## Budget (rough estimates)

| Component | Per unit | Count | Subtotal |
|---|---|---|---|
| NB2 character refs + scene images | $0.08 | 8 | $0.64 |
| Kling Avatar v2 (5s gag) | $0.28 | 5 | $1.40 |
| Kling I2V (5s transition, start+end frames) | $0.42 + 2×$0.04 | 1 | $0.50 |
| ElevenLabs TTS (straight-man lines) | ~$0.07 | 6 | $0.42 |
| ElevenLabs TTS (off-screen customer lines) | ~$0.05 | 4 | $0.20 |
| Title card (NB2 still + minor) | $0.08 | 1 | $0.08 |
| **Typical total** | | | **~$3.24** |

Max with 1–2 retries: **$6.00**. Stop at **$5.40**.

---

## Episode / video structure

| # | Type | Dur. (pre-speed) | Goal |
|---|---|---|---|
| 1 | Title card | 3s | Hook — "What if... / [CHARACTER] / Becomes / [JOB]" in 4 stacked lines |
| 2 | Gag (Avatar) | 5s | Setup → straight-man's deadpan line. Off-screen customer speaks first (face turned away or fully off-screen) |
| 3 | Gag (Avatar) | 5s | Different angle, different customer (or same), different gag mechanic |
| 4 | Gag (Avatar) | 5s | — |
| 5 | Gag (Avatar) | 5s | — |
| 6 | Gag (Avatar) | 5s | — |
| 7a | I2V transition | 3–4s | Deadpan → forced smile (start frame = deadpan, end frame = smile) — silent, sets up the punchline |
| 7b | Avatar punchline | 2–3s | Straight-man delivers the closing line over the held smile |
| 8 | CTA | 3s | Standard channel CTA from Supabase |

Cadence after 1.18× speedup: ~26–32s. Keep total ≤ 32s — TikTok/Reels short-form sweet spot.

---

## The off-screen voice pattern (signature mechanic of this format)

The straight-man is the only character whose face is lipsynced. Customers/extras either stand with their back to camera, are fully out-of-frame, or are blurred in the background. Their voice arrives at Editor as a separate mp3 per scene (`scenes/scene-K/customer.mp3`).

**Silence-padding trick for the Avatar audio:**

For a scene where customer speaks first, then the straight-man deadpan-replies:

```
straight_man_tts_mp3 = silence(customer_dur + 0.6s) + actual_tts(straight_man_line)
```

This is what Avatar v2 ingests. The model holds the mouth still during the leading silence (validated empirically — Kling Avatar v2 does NOT animate during silent audio segments). Editor then mixes `customer.mp3` over the silence portion via `amix`, producing the natural rhythm "customer speaks → straight-man pauses → straight-man replies" with only ONE Avatar v2 call per scene.

**See:** `rules/roles/sound.md` §9 (off-screen / non-animated voices) and `rules/roles/editor.md` §12 (off-screen VO mix sanity check).

---

## Locked parameters (identical across episodes of the format)

- **Aspect ratio:** 9:16, 1080×1920, 30 fps
- **Style:** Photorealistic, cinematic — overrides game style guide
- **Subtitles:** ASS BorderStyle=4 (opaque box hugs text width), Montserrat Bold 58–60 px, Alignment=2, MarginV=120 (low — designed to also mask Kling Avatar v2 CJK text artifacts in the bottom strip)
- **Speedup:** 1.18× at the end (vs the standard 1.15×) — comedy needs slightly snappier pacing
- **Music:** From `video-agent/music/Fun/` only — upbeat, light. Volume 0.08 (lower than standard because Avatar's lipsynced audio is the comedic centerpiece)
- **Negative prompt (all Avatar clips):** `extra characters facing camera, lipsync on background extras, CJK text, subtitle text in scene, watermark`

---

## Variable parameters (change per video)

- Job/setting (barista / IT helpdesk / DMV / dating coach / yoga instructor / kindergarten teacher)
- Outfit overlay (apron / lanyard / polo / tracksuit)
- The 6 gag premises (customer requests)
- The 6 straight-man punchlines (always logical, deadpan, never sarcastic — sarcasm breaks the bit)
- Music track within `music/Fun/`

---

## Role briefs

### Scenarist

- Output `storyboard.json` with 7 scenes (title + 5 Avatar gags + 1 split Avatar/I2V scene 7) + CTA reference.
- For each gag scene: `dialogue` block with `customer_line` (off-screen) AND `character_line` (straight-man). Customer line must be the SETUP, character line the deadpan REACTION — never reverse.
- Gag premises must be diverse mechanics: misinterpret literal vs figurative ("smile more!" → confused face), unreasonable customization, customer name absurdity, etc. **No two gags with the same mechanic.**
- `visual_identity.character` overrides game style with `style: "photorealistic"`. Outfit field locks the job costume.
- Scene 7 split: 7a is silent I2V transition (start_frame=deadpan, end_frame=forced smile), 7b is Avatar with the closing line over the held smile.
- General script rules — `rules/roles/scenarist.md`.

### Storyboarder

- Photorealistic NB2 images. Chain-reference using the straight-man character sheet as `anchor`, prev-scene as second ref.
- For each gag scene where the customer appears: customer must be back-to-camera OR fully off-screen OR blurred far background. Prompt this **explicitly** (e.g. `customer in foreground, BACK to camera, head turned away, only shoulders and back of head visible`). Otherwise NB2 will draw a face that mismatches between scenes.
- Title card image: straight-man centered, neutral background, leave bottom 60% of frame clear for the 4-line title overlay (or bake the title text directly into the NB2 prompt — both work).
- Scene 7a needs TWO NB2 images: start (deadpan, identical pose to scene 6) and end (forced smile, same outfit, same framing).
- General rules — `rules/roles/storyboarder.md`.

### Animator

- 5 Avatar v2 gag clips + 1 I2V transition (scene 7a) + optionally 1 short I2V for title card subtle motion.
- Avatar v2 input audio MUST be the silence-padded mp3 produced by Sound (silence(customer_dur + 0.6s) + straight_man_line). Do not trim the leading silence — that silence is the bit.
- I2V scene 7a: pass start_frame=deadpan png, end_frame=smile png, motion_prompt = "subtle facial transition, lips press together, micro-smile blooms slowly, otherwise still". Generate without audio (`generate_audio: false`).
- **Debug mode:** before launching the Avatar batch (5 clips × ~$0.28 = ~$1.40), list planned clips and get user OK — Avatar regenerations are the most expensive failure mode for this format.
- Watch for CJK text artifacts in Avatar output near the bottom of the frame (y ≈ 1700–1850). These cannot be fully prevented by negative prompt; Sound's subtitles are designed to mask them.
- General rules — `rules/roles/animator.md`.

### Sound

- TTS for the straight-man (6 lines) + off-screen customers (4 lines, fewer than gags because some gags are reactions to a non-verbal cue).
- Straight-man voice: deep, deadpan male — `George` (stability 0.30) or `Daniel` (stability 0.15) depending on character. Lock the choice in storyboard.
- Customer voices: vary per scene — `Rachel`, `Charlotte`, `Adam` — to feel like different customers.
- For each gag with a customer line: produce `scenes/scene-K/customer.mp3` (off-screen voice) AND the silence-padded `scenes/scene-K/scene-K.mp3` for Avatar.
- ASS subtitles: write per-scene ASS with **BorderStyle=4, MarginV=120** so the box sits low enough to mask the Kling CJK artifact AND is opaque enough to hide it. NO full-frame drawbox. No overlapping events within the same Style. Last subtitle must end at clip end (≥ duration − 0.05s) to keep the artifact masked during trailing silence.
- Music: from `video-agent/music/Fun/`, volume 0.08. NOT from Dark/ or Drama/ — wrong mood will kill the comedy.
- General rules — `rules/roles/sound.md` (especially §9 off-screen voices and §10 ASS invariants).

### Editor

- Per-scene burn-in pipeline: take Avatar mp4, scale to 1080×1920 if needed, mix in `customer.mp3` via amix (during the leading silence portion), then burn the per-scene ASS subtitles using **ffmpeg-full** (libass required — stock ffmpeg silently skips ASS).
- Concat all 7 scenes + CTA → `build/concat.mp4`.
- Apply **1.18× speedup** (`setpts=PTS/1.18` + `atempo=1.18`) BEFORE mixing music. If you skip speedup, `final.mp4` will be too long — check duration vs sum(scene_durations) / 1.18.
- Mix `bg-music.mp3` from Fun/ at volume 0.08.
- RMS sanity check: on intervals where customer VO should be heard, RMS must be > -30 dB. -40 dB means VO didn't make it into the mix.
- General rules — `rules/roles/editor.md` (especially §11 ffmpeg-full, §12 off-screen VO mix, §13 artifact masking, §14 speedup).

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/comedy-sketch/
├── storyboard.json
├── bg-music.mp3                       # picked from music/Fun/
├── scenes/
│   ├── refs/
│   │   └── {char-slug}-sheet.png      # straight-man character sheet
│   ├── scene-1/                       # title card
│   │   ├── scene-1.png
│   │   └── scene-1.mp4                # NB2 still or 3s I2V
│   ├── scene-2/ ... scene-6/          # gag Avatar clips
│   │   ├── scene-K.png
│   │   ├── scene-K.mp3                # silence-padded Avatar audio
│   │   ├── customer.mp3               # off-screen VO (when applicable)
│   │   └── scene-K.mp4                # Avatar v2 output
│   └── scene-7/                       # split 7a I2V + 7b Avatar
│       ├── scene-7a-start.png
│       ├── scene-7a-end.png
│       ├── scene-7a.mp4
│       ├── scene-7b.png
│       ├── scene-7b.mp3
│       └── scene-7b.mp4
├── build/                             # all intermediate work — ASS, scaled mp4s, concat lists, mixed audio
└── final.mp4                          # 1080×1920, ~28s after 1.18× speedup
```

---

## Validation before publishing

- [ ] 7 scenes + CTA concatenated
- [ ] Total duration after 1.18× speedup ≤ 32s
- [ ] Photorealistic style preserved (not slipped into game default 3D)
- [ ] Customer faces NEVER directly to camera in any scene
- [ ] Off-screen customer VO audible (RMS > -30 dB on dialogue intervals)
- [ ] Subtitles BorderStyle=4 box, no full-width black bar, MarginV=120
- [ ] Last subtitle in each scene reaches clip end (artifact masked through trailing silence)
- [ ] No CJK text artifact visible in any scene (sample frames at 1s and clip_end−0.3s of each Avatar clip)
- [ ] Music is from Fun/, volume 0.08, audible but not overpowering
- [ ] 1.18× speedup applied (NOT 1.15×)
- [ ] CTA appended

---

## Anti-patterns

- ❌ Game default style (Pixar/3D) — comedy needs photorealism here
- ❌ Customers facing camera — they'd need lipsync, defeating the off-screen-VO economy
- ❌ Sarcastic straight-man lines — deadpan logic only; sarcasm breaks the bit
- ❌ Avatar v2 called with non-padded audio when the gag needs customer-first rhythm
- ❌ Forgetting to mix `customer.mp3` into the final audio (RMS check catches it)
- ❌ Full-width drawbox to hide CJK artifact (cuts the picture — use BorderStyle=4 box)
- ❌ MarginV=480 thinking "raise subtitle higher" — Alignment=2 MarginV grows UP from bottom, so big MarginV moves text AWAY from the artifact at the bottom
- ❌ Music from Dark/ or Drama/ — mood mismatch
- ❌ Skipping the 1.18× speedup step
- ❌ Burning ASS subtitles with stock ffmpeg (lacks libass — subtitles silently dropped)
- ❌ Two ASS Dialogue events with overlapping time ranges in the same Style (text scrambles)
- ❌ `-shortest` in any ffmpeg call (universal anti-pattern — use `apad`)
