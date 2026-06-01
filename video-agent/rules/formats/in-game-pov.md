---
subtitle_style: narrative
subtitle_offset_s: 0
subtitle_mask: false
subtitle_highlight: false
subtitle_extras: []
---

# Format "In-Game POV" — you are dropped into a lore/gameplay situation, first person, survive or die

<!-- HUD-оверлеи (`SURVIVAL: X%` счётчик, хук-плашка `ШАНС ВЫЖИВАНИЯ`, warning-плашки, outcome-плашка) — это НЕ субтитры, а graphic overlays формата. Их рисует Editor через drawtext (ffmpeg-full, libfreetype) per-scene ДО concat, значения берёт из полей storyboard. Они НЕ запекаются в NB2 — иначе AI рисует их непоследовательно и они "бьются" между кадрами. subtitle_style=narrative относится только к нарраторским сабам. -->

The viewer **is** the protagonist. A first-person camera (hands, weapon, cockpit glass, environment) drops them into a specific situation from the game's lore (a famous battle, a canon event) or from its gameplay (a clutch firefight, a raid wipe). A second-person narrator — a tense tactical instructor — opens with a hook (`"Вы оказались в битве WOLF 359, ваш корабль подбили. Шанс выживания: 2%."`), then walks through what to do to survive, step by step. It plays as a **survival manual**: situation → threats → moves → outcome. But following the manual does not guarantee life — the story can end in death. The signature gimmick is a **live survival-% HUD counter** that moves across the clips (up on a correct move, down on a new threat) and resolves on the final outcome plate.

This file is the **playbook**: when to use, concept, budget, role briefs. Craft rules (NB2 chain, Kling I2V, TTS, ffmpeg) — in `rules/roles/*.md`.

---

## When to use

Keywords: "in-game pov", "pov", "от первого лица", "first person", "ты оказался", "вы оказались", "тебя зажали", "survival guide", "survival manual", "как выжить", "how to survive", "survive the", "выживание", "shance of survival", "you wake up", "ты очнулся".

Best fit when the game has either (a) a **named canon event/battle** with high stakes (Wolf 359, a famous raid, a story climax) or (b) **tense gameplay scenarios** that read instantly in first person (a 1vX clutch, a boss enrage, a horde rush). Games with neither strong lore nor readable POV gameplay are a weak fit — pick `character-story` or `what-if-real-life` instead.

**Single-shot per video** — no story bible, no continuity between videos. Each video is one situation, one POV, one predetermined outcome.

### Manager asks ONE question before Scenarist runs

The outcome is a creative decision made **at creation time**, not by the scenarist alone. In Phase 0 the Manager asks the user:

> **«Эта история — про выживание или про гибель?»** (survive / death)

The answer is passed to Scenarist as `OUTCOME` and locked into `storyboard.json → outcome`. The whole script (which moves work, where the % lands, the final plate) is written to serve that predetermined ending. If the user does not specify and cannot be asked, default to a **50/50 author's choice**, leaning to `death` only when the situation is canonically lethal (e.g. a battle the faction historically lost).

---

## Concept

- **Genre:** first-person survival manual / immersive POV
- **Perspective:** pure POV. Second person ("ты"/"вы"). The protagonist is **never shown** — no face, no reflection, no over-the-shoulder. The camera IS their eyes. We see hands, weapon/tool, cockpit/HUD glass, and the world reacting to them.
- **Style:** identical to the game (taken from `games/{GAME_TAG}/{GAME_TAG}.md`).
- **Duration:** 35–45s (6–8 clips × 5s + CTA).
- **Budget:** up to $7.00 per video. Stop if spend > $6.30.
- **Frame format:** 9:16 (608×1080) for all scenes.

### Models

- **Image:** NB2 (`fal-ai/nano-banana-2/edit`) — POV scene frames. No character-face ref (we never see the protagonist). A prop/vehicle ref (the ship, the signature weapon) is allowed ONLY when continuity of that object matters across clips.
- **Video:** Kling v3 Standard I2V (`fal-ai/kling-video/v3/standard/image-to-video`) — `generate_audio: true` (POV combat SFX: explosions, alarms, gunfire, hull groan). Fallback to v2.6 Pro only on v3 artifacts.
- **Audio:** ElevenLabs TTS — second-person narrator (one voice, whole video) overlaid on the picture. Kling SFX kept underneath at low volume. Music bed under everything.
- **HUD overlays:** Editor drawtext (NOT baked into NB2). See "Survival HUD" below.

### Key mechanics

1. **The camera does not speak.** No lipsync, no on-screen talking. Narrator is off-screen VO (TTS overlay) like `character-story`, but in **second person** ("ты делаешь", "у тебя 4 секунды") instead of first-person monologue.
2. **Live survival-% HUD.** A small persistent `SURVIVAL: X%` counter sits in the top-right corner and changes value per clip. It is a **programmatic drawtext overlay**, not an AI-rendered element — that is the only way to keep it consistent and legible.
3. **Predetermined outcome.** `survive` or `death`, decided by the Manager's question. The arc is written backwards from it.

---

## Survival HUD (the signature element)

Three overlay layers, all drawn by Editor via `drawtext` (ffmpeg-full) **per-scene before concat**, values read from storyboard fields. **None of these are ever baked into NB2** — NB2 `negative_prompt` must forbid on-screen text/HUD/numbers, otherwise the AI invents inconsistent counters that flicker between clips.

| Layer | Where | Source field | When |
|---|---|---|---|
| **Hook plate** | Center-upper, y≈h*0.22, large (fs~96) | `hook_plate` (e.g. `ШАНС ВЫЖИВАНИЯ: 2%`) | scene 1 only, fade in 0.0–0.4s, hold to clip end |
| **Persistent counter** | Top-right corner, y≈80, right-aligned, small (fs~52), monospace look | `survival_pct` (int 0–100) per scene | every scene, full duration |
| **Warning plate** | Center, y≈h*0.40, red, bold (fs~72) | `hud_warning` (e.g. `⚠ ВРАГ СЗАДИ`) — optional per scene | flash 0.2–2.2s when present |
| **Outcome plate** | Center, large (fs~110) | `outcome_plate` (`ВЫ ВЫЖИЛИ` green / `ВЫ ПОГИБЛИ` red) | final scene, fade in over last 1.5s |

Counter behaviour: starts at the hook value (low), and **moves with the narration** — up when the narrator's step succeeds, down when a new threat hits. It must reach a value consistent with the locked `outcome` on the last non-CTA scene (e.g. `survive` → ends high like 71%; `death` → ends at `0%`). Scenarist sets `survival_pct` per clip; Editor just renders it.

Layout safety: HUD lives in the **top half / center**, narrator subtitles in the **lower third** (narrative MarginV). No collision — do not move narrator subs up.

---

## Budget (rough estimates)

| Component | 5s clip |
|---|---|
| Image (NB2, start frame only — no end frame, no prop-ref unless needed) | $0.08 |
| Kling v3 I2V 5s (`generate_audio: true`) | $0.63 |
| **Per clip** | **~$0.71** |

| Component | Cost |
|---|---|
| ElevenLabs TTS (~40s second-person narration) | ~$0.20 |
| Music (local) | $0.00 |
| Prop/vehicle ref (only if continuity needed) | $0.08 |
| HUD overlays (Editor drawtext) | $0.00 |

| Variant | Clips | Cost |
|---|---|---|
| Base (recommended) | 6 × 5s = 30s + CTA | ~$4.50 |
| Extended | 8 × 5s = 40s + CTA | ~$5.90 |

Max with 1–2 retries: **$7.00**. Stop at **$6.30**.

> SFX note: `generate_audio: true` is **experimental** for this format (combat ambience boosts immersion). Because the camera shows no faces and no one talks on screen, Kling has nothing to lip-sync and rarely produces the "bad voice" problem that forces `character-story` to silence. Still, push `voices, speech, dialogue, vocals, music` into the Kling `negative_prompt` so it stays pure SFX. If a clip comes back with garbled speech, re-run that single clip with `generate_audio: false` (saves $0.21) and lean on TTS+music for that scene.

---

## Video structure (flexible 6–8 clips, written backwards from the outcome)

| Phase | Timing | Goal | Clips |
|---|---|---|---|
| **HOOK** | 0–5s | Drop them in. Situation named + `hook_plate` survival %. Narrator: "Вы оказались в…" | 1 clip (5s) |
| **THREAT** | 5–15s | What is killing you right now. Counter drops. | 1–2 clips (5s) |
| **MOVES** | 15–30s | The survival manual — concrete steps. Counter moves per step. | 2–4 clips (5s) |
| **OUTCOME** | 30–40s | Resolve to the locked `outcome`. `outcome_plate` over last 1.5s. | 1 clip (5s) |
| **CTA** | last | CTA clip | 1 clip |

### What works

- **Second-person imperative.** "Уводи нос вправо. Глуши реактор. У тебя три секунды." — direct orders to the viewer.
- **A ticking clock.** Concrete time/resource pressure ("4 секунды до перегрева", "один заряд щита").
- **The counter as a story beat.** A correct move visibly bumps the %; a new threat slashes it. The number tells the story alongside the voice.
- **Each clip = a new POV moment.** New threat, new angle, new action of the hands. Never the same shot twice.
- **Honest stakes.** If the outcome is `death`, the manual should look almost-right — the viewer should feel they nearly made it.

### What does NOT work

- ❌ Showing the protagonist (defeats POV)
- ❌ Third-person or first-person-past narration ("I was in the battle") — this format is second-person present ("ты в битве")
- ❌ Narrator describing the picture instead of giving orders ("на экране взрыв" — bad; "уклоняйся, слева ракета" — good)
- ❌ A static % (the counter must move — that's the retention hook)
- ❌ Outcome that contradicts the locked `outcome` field
- ❌ Baking the HUD/% into NB2 images

### The narration

- Second person, present tense, imperative. One voice for the whole video.
- ~80–120 words for 35–45s. Short, clipped, urgent.
- HOOK line is MANDATORY and must (a) name the situation and (b) state the starting survival chance, matching `hook_plate`. ≤20 words. Example: "Вы оказались в битве при Wolf 359. Ваш корабль подбит. Шанс выжить — два процента."
- Each clip ≈ 10–15 words.

---

## Role briefs

### Scenarist

- Receive `OUTCOME` (`survive`/`death`) from Manager. Lock it in `storyboard.json → outcome`. Write the whole arc backwards from it.
- Pick the situation: lore event OR gameplay scenario, per the game (`games/{GAME_TAG}/{GAME_TAG}.md`). If the game has no usable lore, use a gameplay scenario; if neither reads well in POV, tell Manager this format is a weak fit.
- Write the **second-person, present-tense, imperative** narration (~80–120 words). One voice. No first person, no past tense.
- **HOOK is MANDATORY:** clip 1 `tts_segment` names the situation + the starting survival chance, matching `hook_plate`. ≤20 words.
- Split narration into 10–15 word fragments → one `tts_segment` per clip.
- Set `survival_pct` (int 0–100) for **every** clip. It must start at the hook value, move with the narration (up on a successful step, down on a new threat), and land on a value consistent with `outcome` (`death` → final non-CTA clip = `0`; `survive` → ends high, 60–85).
- Set `hook_plate` on clip 1, `outcome_plate` on the final non-CTA clip (`ВЫ ВЫЖИЛИ` / `ВЫ ПОГИБЛИ` or game-localised equivalent), and `hud_warning` on threat clips (short, ≤18 chars, e.g. `⚠ ВРАГ СЗАДИ`, `ПЕРЕГРЕВ`). Leave `hud_warning: null` on non-threat clips.
- `clip_type: "action"` for all clips. `character_speech: null` for all (voice via TTS overlay).
- `action_description` = what happens visually from first person, NOT a repeat of the narration.
- **Three motion layers per clip** (mandatory): camera move + environment motion + hands/weapon action. Each sustained the full 5s — never "then settles / then steady" (Kling reads those as freeze cues).
- POV-specific framing: every `image_prompt` is first person. No protagonist body/face. Hands, weapon, cockpit/visor framing allowed.
- **No character-face ref.** A prop/vehicle ref only if its continuity matters across clips (then note it for Storyboarder).
- Voice: pick from ElevenLabs by tone (tense tactical instructor — `Daniel` confident, `George` neutral-grave, `Adam` urgent). Lock in `tts.voice`.
- General script rules — `rules/roles/scenarist.md`.

**Storyboard.json — extra fields:**

```json
{
  "format": "in-game-pov",
  "game_tag": "{GAME_TAG}",
  "outcome": "survive",
  "situation": "Battle of Wolf 359 — your ship is crippled",
  "tts": {
    "full_text": "{full second-person narration}",
    "voice": "Daniel",
    "stability": 0.30,
    "style": 0.65,
    "language_code": "{ISO 639-1}"
  },
  "music": { "mood": "tense", "volume": 0.12 },
  "clips": [
    {
      "index": 1,
      "beats": ["hook"],
      "duration_sec": 5,
      "clip_type": "action",
      "character_speech": null,
      "tts_segment": "Вы оказались в битве при Wolf 359. Ваш корабль подбит. Шанс выжить — два процента.",
      "survival_pct": 2,
      "hook_plate": "ШАНС ВЫЖИВАНИЯ: 2%",
      "hud_warning": "КОРПУС ПРОБИТ",
      "outcome_plate": null,
      "action_description": "POV from a damaged cockpit, sparks, a Borg cube filling the canopy, hands gripping the controls",
      "camera_angle": "first-person cockpit, slight handheld shake",
      "image_prompt": "...",
      "negative_prompt": "..."
    }
  ]
}
```

### Storyboarder

- Style taken from `games/{GAME_TAG}/{GAME_TAG}.md` (identical to the game).
- All frames 9:16 (608×1080), **first person**. NEVER show the protagonist's face or body beyond hands/arms. No mirror/visor reflection of their face.
- POV cues to bake into `image_prompt`: cockpit canopy frame, weapon barrel/sights in lower frame, gloved hands, HUD glass — but **NO numbers/text/UI labels** (those are Editor overlays).
- **No character-face ref.** Generate a prop/vehicle ref ONLY if Scenarist flagged that object's continuity matters; otherwise no refs at all (environment painted inline by NB2).
- Chain: `scene-1` no ref (or `[prop-ref]` if one exists); `scene-N` (N≥2) refs = `[scene-(N-1).png]` (+ `[prop-ref]` if used) for continuity. See storyboarder.md §10.
- **One PNG per clip — start frame only.** Do NOT generate end frames (forbidden with `multi_prompt`, wastes $0.08). See storyboarder.md §14.8.
- **Every `image_prompt` MUST end with** `". Clean first-person POV frame with NO on-screen text, NO HUD numbers, NO captions, NO UI labels, NO crosshair text, NO percentage counters."` Push the same into NB2 `negative_prompt` AND the per-clip Kling `negative_prompt`.
- General rules — `rules/roles/storyboarder.md`.

### Animator

- All clips via **Kling v3 Standard I2V** with **`generate_audio: true`** (combat SFX). Fallback v2.6 Pro only on v3 artifacts.
- **Start frame only.** Do NOT pass `tail_image_url` / end frame (causes interpolate-then-freeze static clips).
- Kling `negative_prompt` MUST include: `voices, speech, dialogue, vocals, singing, music, on-screen text, HUD numbers, percentage counter, captions, watermark, person facing camera, protagonist body, talking`.
- **Three concurrent motion layers per clip** (mandatory), each sustained the full 5s:
  1. **Camera move** — first-person: push-in, handheld combat shake, fast pan to a threat, dive, roll. Vary across clips. NEVER "camera holds steady".
  2. **Environment motion** — explosions, tracer fire, alarms strobing, smoke, debris, water/dust, energy.
  3. **Hands/weapon action** — reload, grip tightening on the stick, hand slamming a console, weapon recoil. Sustained, not completed mid-clip.
- **Banned phrases in `motion_prompt`** (Kling reads as freeze): `then settles`, `then steady`, `then holds`, `then dissipates`, `camera holds steady`, `hold position`, `no morphing`, `maintain exact appearance`. Use continuous-tense verbs + duration cues (`throughout the shot`, `held for the full 5 seconds`).
- Avoid full-body locomotion of the protagonist (there is none — it's POV). Motion = camera + world + hands.
- Duration: 5s all clips. Polling: base `fal-ai/kling-video`, every 15s, max 10 min.
- **If a clip returns garbled speech/vocals despite the negative prompt:** re-run that single clip with `generate_audio: false` (saves $0.21); the scene then relies on TTS + music + (optional) library SFX.
- **Debug mode:** before the Kling batch, list planned clips with per-clip cost and get user OK.
- Do NOT use: Kling Avatar, Veo3, lipsync.
- General rules — `rules/roles/animator.md`.

### Sound

- **TTS:** ElevenLabs via fal.ai (`fal-ai/elevenlabs/tts/eleven-v3`).
  - `voice` = name string (Daniel/George/Adam), NOT voice_id. One voice for the whole video.
  - `stability`/`style` for an urgent tactical-instructor read (lower stability = more intensity).
  - Generate the full narration in **one request** (coherent prosody, one mp3 for the subtitle pass).
  - Save → upload to Supabase. Editor mixes over the concatenated picture.
- **Subtitles:** ASS via `tools/add_subtitles.py` (Pipeline 8B in `sound.md`), run ONCE on the full `tts-output.mp3` against the picture-only concat.
  - Args: `--style narrative --chunk 4 --marginv 420 --lang {lang} --no-scale`. Pass `--text` with the known TTS text (proportional timing, no whisper). Add `--atempo N` if Editor sped up the narration.
  - NEVER one PIL PNG per `tts_segment`.
- **Speed control:** if TTS duration > timeline, Editor applies `atempo` (cap 1.4×); pass the same `--atempo` to the subtitle script. If mismatch > 40% → back to Scenarist to shorten.
- **Music:** mood `tense`/`drama` from `music/tracks.json`, `volume` from storyboard (default 0.12). Never `Fun/`.
- General rules — `rules/roles/sound.md`.

### Editor

Three-stage assembly (subtitles need a picture-only concat to align against), **plus a per-scene HUD drawtext pass before concat.**

**Stage 0 — HUD overlays (per-scene, BEFORE concat, ffmpeg-full / libfreetype):**
- Use `$FFMPEG = /usr/local/bin/ffmpeg-full/ffmpeg` (drawtext needs libfreetype; the Homebrew ffmpeg lacks it).
- On each `scene-K-scaled.mp4`, chain drawtext filters from storyboard fields:
  - **Persistent counter** (every scene): `drawtext=text='SURVIVAL ${survival_pct}%%':fontsize=52:fontcolor=white:borderw=4:bordercolor=black:x=w-text_w-40:y=80` (top-right, full duration).
  - **Hook plate** (scene 1 only): big centered, `fontsize=96`, white + black stroke, `enable='gte(t,0)'`, fade in via `alpha='if(lt(t,0.4),t/0.4,1)'`, y≈h*0.22.
  - **Warning plate** (scenes with non-null `hud_warning`): `fontsize=72`, `fontcolor=red`, center y≈h*0.40, `enable='between(t,0.2,2.2)'`.
  - **Outcome plate** (final non-CTA scene): `fontsize=110`, green (`ВЫ ВЫЖИЛИ`) or red (`ВЫ ПОГИБЛИ`) per `outcome`, center, `enable='gte(t,3.5)'`, fade in over the last 1.5s.
- Escape `%` as `%%` and any `:`/`'` in drawtext text. These overlays render on the picture; they survive into the subtitle and audio stages because the burned subs come AFTER (lower third) and audio is separate.
- HUD goes ONLY here — never ask NB2/Kling to draw it.

**Stage 1 — Picture-only concat:**
- Normalize each HUD'd clip: scale 1080×1920, 30fps, `preset slow`, `crf 20`. Kling I2V is 24fps → normalize to 30fps before concat.
- Hard cuts, no crossfade. Output: `build/concat-noaudio.mp4` (silent, full main duration; CTA NOT yet appended).

**Stage 2 — Subtitle burn-in (delegated to Sound, `sound.md` §8B):**
- `add_subtitles.py build/concat-noaudio.mp4 tts-output.mp3 build/concat-subbed.mp4 --style narrative --chunk 4 --marginv 420 --lang {lang} --no-scale --text "..." [--atempo N]`
- Narrator subs sit in the lower third (MarginV 420) — clear of the top/center HUD. Output: `build/concat-subbed.mp4`.

**Stage 3 — Final audio mix (one ffmpeg pass):**
- Inputs: `build/concat-subbed.mp4` + `tts-output.mp3` + Kling SFX (already baked in each clip's audio — preserve it) + music + `cta-scaled.mp4`.
- **Audio levels:** narrator TTS = 1.0 (front), Kling combat SFX = ~0.30 (bed), music = `music.volume` (~0.12). `amix` all three over MAIN_DUR; do NOT drop the Kling SFX track.
- Concat picture = `concat-subbed.mp4` + `cta-scaled.mp4`.
- TTS overlay: `apad=whole_dur=${MAIN_DUR}` (NOT `-shortest`).
- Music fade out 1.0s before CTA. `-t TOTAL_DUR` where `TOTAL_DUR = MAIN_DUR + CTA_DUR`.

**Speed control:** if `dur(tts) > MAIN_DUR` → `atempo` (cap 1.4×), same value to `add_subtitles.py`. If `dur(tts) < MAIN_DUR` → freeze-extend the lowest-motion clip; never pad TTS with leading silence. Mismatch > 40% → reject to Scenarist.

- General rules — `rules/roles/editor.md` (especially §1 single-pass, drawtext font/`$FFMPEG` notes, §6 subtitle burn order — `ass=` must be the LAST video token).

---

## CTA (Call to Action)

CTA video from Supabase `game_assets` (tag `cta` + `video`). Manager downloads it in Phase 0 and hands it to Editor. Normalize (1080×1920, 30fps, AAC 128k), append as the last concat clip. No HUD on the CTA clip.

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/in-game-pov/
├── storyboard.json
├── scenes/
│   ├── refs/
│   │   └── prop-ref.png            (optional — only if a vehicle/weapon needs continuity)
│   ├── scene-1/
│   │   ├── scene-1.png             (start frame only — POV, NO HUD baked in)
│   │   ├── scene-1.mp4             (Kling I2V, generate_audio: true)
│   │   ├── scene-1-hud.mp4         (after Stage 0 drawtext HUD pass)
│   │   └── scene-1-scaled.mp4
│   └── scene-N/...
├── tts-output.mp3
├── build/
│   ├── concat-noaudio.mp4          (picture-only concat, HUD already burned)
│   └── concat-subbed.mp4           (after add_subtitles.py burn-in)
├── concat-list.txt
└── final.mp4
```

---

## Validation before publishing

- [ ] `format: "in-game-pov"` in storyboard.json
- [ ] `outcome` set to `survive` or `death` (the value the Manager asked the user for)
- [ ] `character_speech: null` for all clips; narration via TTS overlay only
- [ ] All narration is **second person, present tense** — no first-person, no past tense
- [ ] HOOK clip `tts_segment` names the situation + starting survival % and matches `hook_plate`
- [ ] `survival_pct` set on every clip; moves with the narration; final non-CTA value consistent with `outcome` (`death` → 0)
- [ ] **Protagonist never shown** — no face/body/reflection in any frame (pure POV)
- [ ] No on-screen text/HUD/numbers baked into any NB2 image (HUD is Editor drawtext only)
- [ ] HUD rendered by Editor: persistent counter (top-right) every scene, hook plate (scene 1), warning plates on threat scenes, outcome plate on final scene
- [ ] HUD (top/center) and narrator subtitles (lower third, MarginV 420) do not overlap
- [ ] All images 608×1080 (9:16); one PNG per scene (start frame only, no end frames)
- [ ] No character-face ref; prop-ref only if continuity needed
- [ ] Kling I2V `generate_audio: true`; `negative_prompt` forbids voices/speech/music/on-screen-text/protagonist
- [ ] No garbled speech in any clip's Kling SFX (if found → that clip re-run with `generate_audio: false`)
- [ ] Audio mix: narrator 1.0, Kling SFX ~0.30, music ~0.12 — SFX track NOT dropped
- [ ] camera_angle differs between adjacent clips; every clip has an active camera move (no "holds steady")
- [ ] motion_prompt = three concurrent layers (camera + environment + hands), continuous-tense, none of the banned freeze phrases
- [ ] TTS via fal.ai ElevenLabs (`voice` name, not `voice_id`), one request for the whole narration
- [ ] Subtitles via `add_subtitles.py --style narrative` (NOT PIL PNG per segment)
- [ ] fps normalized to 30 before concat; single-pass audio mix; music fade before CTA
- [ ] CTA included in concat-list (no HUD on CTA)
- [ ] `-shortest` NOT used (use `apad`)

---

## Anti-patterns

- ❌ Showing the protagonist's face/body/reflection — kills POV. The camera IS their eyes.
- ❌ First-person-past or third-person narration ("I was there" / "he fought") — must be second-person present imperative ("ты в бою, уводи нос вправо")
- ❌ Baking the `SURVIVAL %`, warning plates, or any HUD into NB2/Kling — AI renders them inconsistently and they flicker between clips. HUD is Editor drawtext ONLY.
- ❌ Static survival % (must move per clip — it's the retention hook)
- ❌ Final % / outcome plate contradicting the locked `outcome` field
- ❌ Narrator describing the picture instead of giving survival orders
- ❌ `generate_audio: true` left on a clip that came back with garbled speech (re-run that clip with `false`)
- ❌ Dropping the Kling SFX track in the mix (it's the immersion bed — keep at ~0.30 under narrator)
- ❌ Moving narrator subtitles up into the HUD zone (HUD top/center, subs lower third)
- ❌ Character-face ref (we never see the protagonist) — at most a prop/vehicle ref for continuity
- ❌ Generating end-frame PNGs / passing `tail_image_url` to Kling (interpolate-then-freeze static clips)
- ❌ "Camera holds steady" / "then settles" / "then steady" / "hold position" / "no morphing" anywhere in motion_prompt (Kling reads as freeze)
- ❌ Music from `Fun/` (wrong mood — use tense/drama)
- ❌ Burning ASS subtitles with stock ffmpeg (lacks libass / libfreetype — subtitles & drawtext silently dropped; use ffmpeg-full)
- ❌ `-shortest` in any ffmpeg call (universal anti-pattern — use `apad`)
