---
subtitle_style: narrative
subtitle_offset_s: 0
subtitle_mask: false
subtitle_highlight: false
subtitle_extras: []
---

# Format "In-Game POV" — you are dropped into a lore/gameplay situation, first person, survive or die

<!-- HUD-оверлеи (`SURVIVAL: X%` счётчик, title-card оверлей, outcome-плашка) — это НЕ субтитры, а graphic overlays формата. Их рисует Editor через drawtext (ffmpeg-full, libfreetype) per-scene ДО concat. Они НЕ запекаются в NB2. subtitle_style=narrative относится только к нарраторским сабам. SUBTITLE_OFFSET_S = duration_sec title-card клипа (выставляет Manager). -->

The viewer **is** the protagonist. A pure environmental first-person camera drops them into a specific situation from the game's lore (a famous battle, a canon event) or from its gameplay (a clutch firefight, a raid wipe). The video opens with a **game-styled title card** (situation name + survival %) that establishes the stakes before the first POV scene. A second-person narrator — a tense tactical instructor — then walks through what to do to survive. It plays as a **survival manual**: situation → threats → moves → outcome. But following the manual does not guarantee life — the story can end in death. The signature gimmick is a **live survival-% HUD counter** that moves across the clips and resolves on the final outcome plate.

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
- **Perspective:** pure environmental POV. Second person ("ты"/"вы"). The protagonist is **never shown** — no face, no reflection, no over-the-shoulder, **no hands**. The camera IS their eyes. We look at the world, we walk through it, we breathe.
- **Style:** identical to the game (taken from `games/{GAME_TAG}/{GAME_TAG}.md`).
- **Duration:** 35–45s (title card + 5–7 POV clips × 5s + CTA).
- **Budget:** up to $7.00 per video. Stop if spend > $6.30.
- **Frame format:** 9:16 (608×1080) for all scenes.

### Models

- **Image:** NB2 (`fal-ai/nano-banana-2/edit`) — title card (atmospheric establishing shot) + POV scene frames. No character-face ref. No prop refs unless a specific object needs continuity.
- **Video:** Kling v3 Standard I2V (`fal-ai/kling-video/v3/standard/image-to-video`) — `generate_audio: true` (POV combat SFX: explosions, alarms, gunfire, hull groan, heavy breathing). Fallback to v2.6 Pro only on v3 artifacts.
- **Audio:** ElevenLabs TTS — second-person narrator (one voice, clips 1–N) overlaid on the picture. TTS does NOT start on title card. Kling SFX kept underneath at low volume. Music bed under everything.
- **HUD overlays:** Editor drawtext (NOT baked into NB2). See "Survival HUD" below.

### Key mechanics

1. **Title card first.** Scene 0 is a game-styled title card (not POV) that names the situation and shows the starting survival %. It plays 3–5s with Kling ambient SFX but NO narrator TTS. The hook lives here visually.
2. **POV = environmental, never hands.** From clip 1 onward: pure look-around / walk-through / reaction POV. No hands gripping controls. No weapon barrels. Camera sees the world — corridors, consoles, windows, other crew, debris — as the viewer walks and breathes.
3. **Location variety mandatory.** Each POV clip is a different space aboard the ship (or outside it): bridge, corridor, engineering, escape pod bay, airlock, porthole exterior view. Never two consecutive clips in the same location.
4. **Live survival-% HUD.** A small persistent `SURVIVAL: X%` counter sits in the top-right corner and changes value per clip. It is a **programmatic drawtext overlay**, not an AI-rendered element.
5. **Predetermined outcome.** `survive` or `death`, decided by the Manager's question. Arc written backwards from it.

---

## Survival HUD (the signature element)

Two overlay layers, drawn by Editor via `drawtext` (ffmpeg-full) **per-scene before concat**, values read from storyboard fields. **None of these are ever baked into NB2** — NB2 `negative_prompt` must forbid on-screen text/HUD/numbers.

| Layer | Where | Source field | When |
|---|---|---|---|
| **Persistent counter** | Top-right corner, y≈80, right-aligned, small (fs~52), monospace look | `survival_pct` (int 0–100) per scene | every POV clip (scenes 1–N), full duration. NOT on title card. |
| **Outcome plate** | Center, large (fs~110) | `outcome_plate` (`ВЫ ВЫЖИЛИ` green / `ВЫ ПОГИБЛИ` red) | final POV clip, fade in over last 1.5s |

Counter behaviour: starts at the value stated in the title card, and **moves with the narration** — up when the narrator's step succeeds, down when a new threat hits. It must reach a value consistent with the locked `outcome` on the last non-CTA scene (`survive` → ends high like 71%; `death` → ends at `0%`). Scenarist sets `survival_pct` per clip; Editor just renders it.

Layout safety: HUD counter lives in the **top-right**, outcome plate in the **center**, narrator subtitles in the **lower third** (narrative MarginV 420). No collision.

**Title card HUD (scene 0 only):** Editor draws the situation title + survival % via drawtext directly on the title card image (see Editor brief for exact spec). These are separate from the per-scene counter.

---

## Budget (rough estimates)

| Component | 5s clip |
|---|---|
| Image (NB2, start frame only) | $0.08 |
| Kling v3 I2V 5s (`generate_audio: true`) | $0.63 |
| **Per clip** | **~$0.71** |

| Component | Cost |
|---|---|
| ElevenLabs TTS (~35s second-person narration over POV clips) | ~$0.18 |
| Music (local) | $0.00 |
| HUD overlays (Editor drawtext) | $0.00 |

| Variant | Clips | Cost |
|---|---|---|
| Base (recommended) | title card + 5 POV × 5s + CTA | ~$4.50 |
| Extended | title card + 7 POV × 5s + CTA | ~$5.80 |

Max with 1–2 retries: **$7.00**. Stop at **$6.30**.

> SFX note: `generate_audio: true` is **experimental** for this format (combat ambience boosts immersion). Because the camera shows no faces and no one talks on screen, Kling has nothing to lip-sync and rarely produces the "bad voice" problem. Still, push `voices, speech, dialogue, vocals, music` into the Kling `negative_prompt` so it stays pure SFX. If a clip comes back with garbled speech, re-run that single clip with `generate_audio: false` (saves $0.21).

---

## Video structure (title card + 5–7 POV clips, written backwards from the outcome)

| Phase | Timing | Goal | Clips |
|---|---|---|---|
| **TITLE CARD** | 0–5s | Visual hook — situation name + starting survival %. No narrator TTS. Atmospheric SFX only. | scene 0 (5s) |
| **HOOK** | 5–10s | Drop them in. Narrator opens: "Ты оказался…" POV clip 1. | scene 1 (5s) |
| **THREAT** | 10–20s | What is killing you right now. Counter drops. Different location per clip. | scenes 2–3 (5s each) |
| **MOVES** | 20–35s | The survival manual — concrete steps. Counter moves per step. Each clip = new location. | scenes 3–5 (5s each) |
| **OUTCOME** | 35–40s | Resolve to the locked `outcome`. `outcome_plate` over last 1.5s. | scene N (5s) |
| **CTA** | last | CTA clip | 1 clip |

### What works

- **Second-person imperative.** "Уводи нос вправо. Глуши реактор. У тебя три секунды." — direct orders to the viewer.
- **A ticking clock.** Concrete time/resource pressure ("4 секунды до перегрева", "один заряд щита").
- **The counter as a story beat.** A correct move visibly bumps the %; a new threat slashes it. The number tells the story alongside the voice.
- **Each clip = a new location.** Bridge → corridor → engine room → escape pod bay. Never the same space twice. The journey through the ship *is* the narrative.
- **Environmental immersion.** Camera sees what the protagonist sees as they move: alarms strobing in a corridor, emergency doors slamming, other crew running past, smoke. No hands, no controls — just the world reacting.
- **Honest stakes.** If the outcome is `death`, the manual should look almost-right — the viewer should feel they nearly made it.

### What does NOT work

- ❌ Showing the protagonist (defeats POV)
- ❌ Hands, weapon barrels, or cockpit controls in frame — pure environmental look/walk/breathe POV
- ❌ Two consecutive clips in the same location — must show location variety
- ❌ Third-person or first-person-past narration ("I was in the battle") — second-person present ("ты в бою")
- ❌ Narrator describing the picture ("на экране взрыв" — bad; "уклоняйся, слева ракета" — good)
- ❌ A static % (the counter must move — that's the retention hook)
- ❌ Outcome that contradicts the locked `outcome` field
- ❌ Baking the HUD/% into NB2 images

### The narration

- Second person, present tense, imperative. One voice for the whole video.
- ~70–100 words for 25–35s of POV clips. Short, clipped, urgent.
- Starts on clip 1 (after the title card): "Ты оказался в битве при Wolf 359. Ваш корабль разрезает лазер. Бежишь по мостику."
- Does NOT repeat the title card text verbatim — the visual established it; narration moves the story forward.
- Each clip ≈ 10–15 words.

---

## Role briefs

### Scenarist

- Receive `OUTCOME` (`survive`/`death`) from Manager. Lock it in `storyboard.json → outcome`. Write the whole arc backwards from it.
- Pick the situation: lore event OR gameplay scenario, per the game (`games/{GAME_TAG}/{GAME_TAG}.md`). If the game has no usable lore, use a gameplay scenario; if neither reads well in POV, tell Manager this format is a weak fit.
- **Clip 0 = title card.** `clip_type: "title_card"`, `tts_segment: null` (no narration here), `duration_sec: 5`. Set `title_card_text` (the situation name, e.g. `"BATTLE OF WOLF 359"`) and `hook_plate` (e.g. `"SURVIVAL CHANCE: 2%"`). The `action_description` = establishing shot of the crisis (atmosphere, NOT first-person). `survival_pct: null` on the title card.
- **Clips 1–N = POV scenes.** `clip_type: "action"`, `character_speech: null` for all.
- Write the **second-person, present-tense, imperative** narration (~70–100 words over POV clips). One voice. No first person, no past tense.
- **Narrator starts on clip 1** (after title card). Clip 1 `tts_segment` opens: "Ты оказался…" and names the situation fresh, as if the viewer just woke up in it (not repeating the title card literally).
- Split narration into 10–15 word fragments → one `tts_segment` per POV clip (clips 1–N). `tts_segment: null` on title card.
- Set `survival_pct` (int 0–100) for **every POV clip** (1–N). Start at the hook value (must match `hook_plate`), move with narration, land consistent with `outcome` (`death` → 0; `survive` → 60–85). `survival_pct: null` on title card.
- Set `outcome_plate` on the final non-CTA clip (`ВЫ ВЫЖИЛИ` / `ВЫ ПОГИБЛИ` or game-localised equivalent). No `hud_warning` field — warning plates are removed.
- **Location variety is MANDATORY.** Each POV clip must be in a different space: bridge, corridor, engineering bay, escape pod bay, airlock, porthole, exterior view. Write `location` per clip (e.g. `"starship bridge"`, `"burning corridor"`). Never two consecutive clips in the same location.
- `action_description` = what the viewer sees and feels from first person, NOT a repeat of the narration. Focus on environment, not hands or controls.
- **Three motion layers per clip** (mandatory): camera move + environment motion + atmospheric response. Each sustained the full 5s — never "then settles / then steady". **No hands or weapon action** — camera moves through the world, the world reacts (explosions, crew running, alarms, doors slamming, smoke, debris).
- POV-specific framing: every `image_prompt` for clips 1–N is first person view of the **environment**. No protagonist body/face, **no hands**, no weapon barrel. Camera sees the room/corridor/window as if the viewer is standing/walking there.
- Title card image (`action_description` for clip 0): cinematic establishing shot of the crisis — Borg cube looming over a burning Starfleet vessel, an explosion in space, armies massing — atmospheric, NOT first-person.
- **No character-face ref.** No prop/vehicle ref unless absolutely required for continuity.
- Voice: pick from ElevenLabs by tone (tense tactical instructor — `Daniel` confident, `George` neutral-grave, `Adam` urgent). Lock in `tts.voice`.
- General script rules — `rules/roles/scenarist.md`.

**Storyboard.json — extra fields:**

```json
{
  "format": "in-game-pov",
  "game_tag": "{GAME_TAG}",
  "outcome": "death",
  "situation": "Battle of Wolf 359 — your ship is crippled",
  "tts": {
    "full_text": "{full second-person narration — clips 1-N only, not title card}",
    "voice": "Daniel",
    "stability": 0.30,
    "style": 0.65,
    "language_code": "{ISO 639-1}"
  },
  "music": { "mood": "tense", "volume": 0.12 },
  "clips": [
    {
      "index": 0,
      "beats": ["title_card"],
      "duration_sec": 5,
      "clip_type": "title_card",
      "character_speech": null,
      "tts_segment": null,
      "survival_pct": null,
      "title_card_text": "BATTLE OF WOLF 359",
      "hook_plate": "SURVIVAL CHANCE: 2%",
      "outcome_plate": null,
      "location": "space exterior",
      "action_description": "Borg cube filling the frame, a Starfleet vessel cut in half, debris field, silent explosion"
    },
    {
      "index": 1,
      "beats": ["hook"],
      "duration_sec": 5,
      "clip_type": "action",
      "character_speech": null,
      "tts_segment": "You are on the bridge. A Borg cutting beam just split the ship in two. The captain's last word: abandon ship.",
      "survival_pct": 2,
      "title_card_text": null,
      "hook_plate": null,
      "outcome_plate": null,
      "location": "starship bridge",
      "action_description": "POV on the bridge — consoles sparking, viewscreen cracked, smoke filling the air, red alert lights strobing, crew running past"
    }
  ]
}
```

### Storyboarder

- Style taken from `games/{GAME_TAG}/{GAME_TAG}.md` (identical to the game).
- All frames 9:16 (608×1080).
- **Clip 0 (title card):** `clip_type = "title_card"` — generate a **cinematic atmospheric shot**, NOT first-person POV. Wide establishing: the crisis from a dramatic angle (e.g. Borg cube from space, a burning ship exterior, an army advancing). This image will have text overlaid by Editor. NB2 `negative_prompt` must include `text, captions, ui, hud, hands, person pov, first person view`.
- **Clips 1–N (POV):** pure first-person environmental view. NEVER show protagonist face, body, **or hands**. Camera sees the location — the room, the corridor, the view through the window. No weapon barrels, no cockpit controls.
- POV cues to bake into `image_prompt`: emergency lighting, smoke, debris, other crew (running or dead), sparking consoles, alarm strobes, blast doors — but **NO numbers/text/UI labels** (those are Editor overlays).
- **No character-face ref. No prop/vehicle ref** unless Scenarist explicitly flagged continuity need.
- Chain: `scene-0` no ref; `scene-N` (N≥1) refs = `[scene-(N-1).png]` for continuity. See storyboarder.md §10.
- **One PNG per clip — start frame only.** No end frames.
- **Every POV `image_prompt` MUST end with:** `". Clean environmental first-person POV. NO hands, NO weapon barrels, NO controls in frame. NO on-screen text, NO HUD numbers, NO captions, NO UI labels, NO crosshair text, NO percentage counters."`
- General rules — `rules/roles/storyboarder.md`.

### Animator

- All clips (including title card) via **Kling v3 Standard I2V** with **`generate_audio: true`**. Fallback v2.6 Pro only on v3 artifacts.
- **Title card motion (scene 0):** very slow dramatic movement — slow zoom in toward the crisis, slight drift. Motion layers: slow camera push-in toward crisis / atmospheric debris floating / distant explosions flaring. 5s. `generate_audio: true` for distant SFX rumble and space ambience.
- **POV clips (scenes 1–N) motion layers (mandatory), each sustained full 5s:**
  1. **Camera move** — walking bob, quick turn to a new threat, stagger from an impact, ducking under debris. Vary per clip. NEVER "camera holds steady".
  2. **Environment motion** — explosions, tracer fire, alarms strobing, smoke rolling, blast doors slamming, emergency lights flickering, crew running past.
  3. **Atmospheric reaction** — dust particles, sparks falling, screen-space shake from explosion, gravity shift. Sustained, not completed mid-clip.
- **No hand/weapon motion** — the POV never shows hands; replace hand-action layer with atmospheric/world-reaction layer.
- **Start frame only.** Do NOT pass `tail_image_url` / end frame.
- Kling `negative_prompt` MUST include: `voices, speech, dialogue, vocals, singing, music, on-screen text, HUD numbers, percentage counter, captions, watermark, person facing camera, protagonist body, hands, arms, weapon, controls, cockpit controls, talking`.
- **Banned phrases in `motion_prompt`** (Kling reads as freeze): `then settles`, `then steady`, `then holds`, `camera holds steady`, `hold position`, `no morphing`. Use continuous-tense verbs + duration cues (`throughout the shot`, `held for the full 5 seconds`).
- Duration: 5s all clips. Polling: base `fal-ai/kling-video`, every 15s, max 10 min.
- **If garbled speech:** re-run single clip with `generate_audio: false`.
- **Debug mode:** before Kling batch, list planned clips with per-clip cost and get user OK.
- General rules — `rules/roles/animator.md`.

### Sound

- **TTS:** ElevenLabs via fal.ai (`fal-ai/elevenlabs/tts/eleven-v3`).
  - `voice` = name string (Daniel/George/Adam), NOT voice_id. One voice for the whole video.
  - Generate narration from `tts.full_text` (which covers clips 1–N only — title card has no TTS). One request, one mp3.
  - Save → upload to Supabase.
- **Subtitles:** ASS via `tools/add_subtitles.py`, run ONCE on the full `tts-output.mp3` against the picture-only concat.
  - Args: `--style narrative --chunk 4 --marginv 420 --lang {lang} --no-scale`. Pass `--text` with the narration text.
  - `--offset` = title card duration in seconds (so subs align to when TTS actually starts in the concat).
  - Add `--atempo N` if Editor sped up the narration.
- **Speed control:** if TTS duration > POV-clips timeline, Editor applies `atempo` (cap 1.4×); pass the same `--atempo` to the subtitle script. If mismatch > 40% → back to Scenarist to shorten.
- **Music:** mood `tense`/`drama` from `music/tracks.json`, `volume` from storyboard (default 0.12). Never `Fun/`. Music starts from t=0 (over the title card and through the whole video).
- General rules — `rules/roles/sound.md`.

### Editor

Three-stage assembly (HUD drawtext per-scene before concat, then subtitles, then final audio mix).

**Stage 0 — HUD overlays (per-scene, BEFORE concat, ffmpeg-full / libfreetype):**
- Use `$FFMPEG = /usr/local/bin/ffmpeg-full/ffmpeg` (drawtext needs libfreetype).
- **Title card (scene-0-scaled.mp4):** draw two text layers centered:
  - Line 1 — `title_card_text` (situation name): `fontsize=80:fontcolor=white:borderw=5:bordercolor=black:x=(w-text_w)/2:y=h*0.35`, fade in from t=0.0–0.6s.
  - Line 2 — `hook_plate` (survival %): `fontsize=96:fontcolor=red:borderw=6:bordercolor=black:x=(w-text_w)/2:y=h*0.52`, fade in from t=0.6–1.2s, stay through end.
  - No `survival_pct` counter on the title card.
- **POV clips (scene-1 through scene-N):** per-scene, two drawtext layers:
  - **Persistent counter** (every POV scene): `drawtext=text='SURVIVAL ${survival_pct}%%':fontsize=52:fontcolor=white:borderw=4:bordercolor=black:x=w-text_w-40:y=80`, full duration.
  - **Outcome plate** (final non-CTA POV scene only): `fontsize=110`, green (`ВЫ ВЫЖИЛИ`) or red (`ВЫ ПОГИБЛИ`) per `outcome`, center `x=(w-text_w)/2:y=(h-text_h)/2`, `enable='gte(t,3.5)'`, fade in alpha over last 1.5s.
- **MANDATORY drawtext rules (macOS ffmpeg 8.x):**
  1. Use `textfile=` not `text=` — inline `text=` breaks on `:` (colon is treated as option separator even inside single quotes).
  2. Use `fontfile='/System/Library/Fonts/Supplemental/Arial Unicode.ttf'` — without fontfile, text renders invisible.
  3. The `%` character is special in drawtext format strings — use the **fullwidth percent sign `％` (U+FF05)** instead. It renders identically but is not interpreted as a format specifier. Write it as UTF-8 bytes `\xef\xbc\x85`:
  ```bash
  PCT="\xef\xbc\x85"   # ％ U+FF05 — looks like % but safe in drawtext
  FONT="/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
  printf "BATTLE OF WOLF 359" > /tmp/ing_title.txt
  printf "SURVIVAL CHANCE: 2${PCT}" > /tmp/ing_hook.txt
  printf "SURVIVAL ${pct}${PCT}" > /tmp/ing_counter.txt
  printf "YOU DIED" > /tmp/ing_outcome.txt
  # drawtext=textfile='/tmp/ing_title.txt':fontfile='$FONT':...
  ```
- HUD goes ONLY here — never ask NB2/Kling to draw it.

**Stage 1 — Picture-only concat:**
- Normalize each HUD'd clip: scale 1080×1920, 30fps, `preset slow`, `crf 20`. Kling I2V is 24fps → normalize to 30fps before concat.
- Hard cuts, no crossfade.
- **Dedup check (MANDATORY):** before writing concat-list, verify it contains exactly N+1 entries (one per clip index 0 through N), each filename unique. If a clip was freeze-extended, its entry REPLACES the original — never append a second entry for the same scene. A duplicate scene entry causes the clip to play twice, which is a production error.
- Output: `build/concat-noaudio.mp4` (silent, full main duration; CTA NOT yet appended).
- `MAIN_DUR` = sum of all clip durations (title card + POV clips).
- TTS offset: `TTS_OFFSET = clips[0].duration_sec` (title card duration). TTS starts at this offset in the final mix.

**Stage 2 — Subtitle burn-in:**
- `add_subtitles.py build/concat-noaudio.mp4 tts-output.mp3 build/concat-subbed.mp4 --style narrative --chunk 4 --marginv 420 --lang {lang} --no-scale --offset {TTS_OFFSET} --text "..." [--atempo N]`
- `--offset {TTS_OFFSET}` delays subtitles past the title card. Output: `build/concat-subbed.mp4`.

**Stage 3 — Final audio mix (one ffmpeg pass):**
- Inputs: `build/concat-subbed.mp4` + `tts-output.mp3` + Kling SFX (baked in each clip's audio — preserve) + music + `cta-scaled.mp4`.
- **Audio levels:** narrator TTS = 1.0 (front), Kling combat SFX = ~0.30 (bed), music = `music.volume` (~0.12). Mix all three over MAIN_DUR.
- TTS delayed by `TTS_OFFSET` in the mix: `adelay={TTS_OFFSET_MS}|{TTS_OFFSET_MS}` on the TTS input (title card plays with SFX + music only, no narrator).
- `apad=whole_dur=${MAIN_DUR}` on TTS. NOT `-shortest`.
- Music fade out 1.0s before CTA. `-t TOTAL_DUR`.

**Speed control:** if `dur(tts) > (MAIN_DUR - TTS_OFFSET)` → `atempo` (cap 1.4×), same value to `add_subtitles.py`. If mismatch > 40% → freeze-extend the lowest-motion clip; REPLACE (not append) in concat-list. Mismatch > 40% without freeze-extend possible → reject to Scenarist.

- General rules — `rules/roles/editor.md` (especially §1 single-pass, drawtext font/`$FFMPEG`, §6 subtitle burn order — `ass=` must be the LAST video token).

---

## CTA (Call to Action)

CTA video from Supabase `game_assets` (tag `cta` + `video`). Manager downloads it in Phase 0 and hands it to Editor. Normalize (1080×1920, 30fps, AAC 128k), append as the last concat clip. No HUD on the CTA clip.

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/in-game-pov/
├── storyboard.json
├── scenes/
│   ├── scene-0/
│   │   ├── scene-0.png             (title card — cinematic establishing shot, NOT POV)
│   │   ├── scene-0.mp4             (Kling I2V, generate_audio: true, slow zoom-in)
│   │   ├── scene-0-hud.mp4         (after Stage 0 drawtext — situation name + survival %)
│   │   └── scene-0-scaled.mp4
│   ├── scene-1/
│   │   ├── scene-1.png             (POV frame — environment, NO hands)
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
- [ ] **Clip 0 = title card** (`clip_type: "title_card"`, `tts_segment: null`, `survival_pct: null`)
- [ ] Title card has `title_card_text` and `hook_plate`
- [ ] Clip 1 narration opens: "Ты оказался…" (or equivalent) and does NOT just repeat the title card verbatim
- [ ] `survival_pct` set on every POV clip (1–N); moves with narration; final non-CTA value consistent with `outcome` (`death` → 0)
- [ ] `location` field set on every clip; no two consecutive clips share the same location
- [ ] **Protagonist never shown** — no face, no body, **no hands**, no weapon barrel in any POV frame
- [ ] No on-screen text/HUD/numbers baked into any NB2 image
- [ ] HUD rendered by Editor: title card has situation name + survival %; POV clips have persistent counter (top-right); final clip has outcome plate
- [ ] **No warning plates** (removed from this format — center overlays are confusing and out-of-style)
- [ ] HUD (top-right) and narrator subtitles (lower third, MarginV 420) do not overlap
- [ ] All images 608×1080 (9:16); one PNG per scene (start frame only)
- [ ] No character-face ref; no prop-ref unless explicitly needed
- [ ] Kling I2V `generate_audio: true`; `negative_prompt` forbids voices/speech/music/on-screen-text/hands/protagonist
- [ ] No garbled speech in any clip (if found → re-run that clip with `generate_audio: false`)
- [ ] Audio mix: narrator 1.0, Kling SFX ~0.30, music ~0.12; TTS delayed by title card duration
- [ ] camera_angle differs between adjacent clips; every clip has an active camera move (no "holds steady")
- [ ] motion_prompt = three concurrent layers (camera + environment + atmosphere), continuous-tense, none of the banned freeze phrases
- [ ] TTS via fal.ai ElevenLabs (`voice` name, not `voice_id`), one request for the whole narration
- [ ] Subtitles via `add_subtitles.py --style narrative --offset {title_card_dur}` — subs skip the title card
- [ ] fps normalized to 30 before concat; single-pass audio mix; music fade before CTA
- [ ] **Concat-list dedup:** exactly N+1 entries (clips 0–N), each unique. No scene appears twice. Freeze-extend REPLACES (not appends).
- [ ] CTA included in concat-list (no HUD on CTA)
- [ ] `-shortest` NOT used (use `apad`)

---

## Anti-patterns

- ❌ Showing the protagonist's face/body/hands/reflection — kills POV
- ❌ **Hands or weapon barrels in any POV clip** — this is a look/walk/breathe format, not a first-person shooter HUD format
- ❌ Two consecutive POV clips in the same location — kills momentum and immersion
- ❌ First-person-past or third-person narration — must be second-person present imperative
- ❌ Narrator just describing the picture ("на экране взрыв") instead of giving survival orders
- ❌ Baking the `SURVIVAL %`, outcome plate, or any HUD into NB2/Kling — Editor drawtext ONLY
- ❌ Static survival % (must move per clip — it's the retention hook)
- ❌ Final % / outcome plate contradicting the locked `outcome` field
- ❌ **Warning plates** (center-screen overlays like `⚠ HULL BREACH`) — they look artificial and are removed from this format
- ❌ `generate_audio: true` left on a clip that came back with garbled speech (re-run with `false`)
- ❌ Dropping the Kling SFX track in the mix (it's the immersion bed — keep at ~0.30)
- ❌ Moving narrator subtitles up into the HUD zone (HUD top-right, subs lower third)
- ❌ TTS starting over the title card — TTS is `adelay`'d by the title card duration
- ❌ Subtitles without `--offset` — they'll appear during the title card
- ❌ **Duplicate scene in concat-list** — a freeze-extended scene REPLACES its entry; never append it as a second entry
- ❌ Character-face ref or prop-ref without explicit Scenarist justification
- ❌ End-frame PNGs or `tail_image_url` in Kling (causes freeze artifacts)
- ❌ "Camera holds steady" / "then settles" / "then steady" / "hold position" / "no morphing" in motion_prompt (Kling reads as freeze)
- ❌ Music from `Fun/` (wrong mood — use tense/drama)
- ❌ Burning ASS subtitles with stock ffmpeg (lacks libass — use ffmpeg-full)
- ❌ `-shortest` in any ffmpeg call (use `apad`)
