---
subtitles: true
overlays: true
---

# Format "In-Game POV" — you are dropped into a lore/gameplay situation, first person, survive or die

<!-- HUD-оверлеи (`SURVIVAL: X%` счётчик, title-card оверлей, outcome-плашка) — это НЕ субтитры, а graphic overlays. Их рисует `tools/overlays.py` из `scenes[].overlays[]` (типы `title`, `hud_counter`, `outcome_plate`) per-scene ДО concat (editor.md §6.5). НЕ запекаются в NB2. Субтитры — единый универсальный стиль (editor.md §6). -->

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

Two overlay layers, отрисовываются `tools/overlays.py` из `clips[].overlays[]` (сценарист заполняет) **per-scene before concat**. **None of these are ever baked into NB2** — NB2 `negative_prompt` must forbid on-screen text/HUD/numbers.

| Layer | Where | Source field | When |
|---|---|---|---|
| **Persistent counter** | Top-right corner, y≈80, right-aligned, small (fs~52), monospace look | `survival_pct` (int 0–100) per shot → `hud_counter.text` | every POV clip (scenes 1–N), full duration. NOT on title card. |
| **Outcome plate** | Center, large (fs~110) | `outcome_plate` (`YOU SURVIVED` green / `YOU DIED` red) — always EN | final POV clip, fade in over last 1.5s |

Counter behaviour: starts at the value stated in the title card, and **moves with the narration** — up when the narrator's step succeeds, down when a new threat hits. It must reach a value consistent with the locked `outcome` on the last non-CTA scene (`survive` → ends high like 71%; `death` → ends at `0%`). Scenarist кладёт значения в `hud_counter` overlay'и (с enable-окнами по shot'ам); overlays.py рендерит.

Layout safety: HUD counter lives in the **top-right**, outcome plate in the **center**, narrator subtitles — единый универсальный стиль внизу (MarginV 520, editor.md §6). No collision (HUD top-right, outcome center, subs bottom).

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
- **Video structure: 1 title-card call + 2 POV multi_prompt calls.** Total ~35s before CTA:
  - `call_index: 0` — `call_type: "title_card"` — 5s single I2V. Wide cinematic shot (NOT POV). Sets situation name + starting survival %.
  - `call_index: 1` — `call_type: "pov_multi_prompt"` — 15s, 3 POV shots × 5s. Covers HOOK → first THREAT locations.
  - `call_index: 2` — `call_type: "pov_multi_prompt"` — 15s, 3 POV shots × 5s. Covers MOVES → OUTCOME.
- **Write shots, not clips.** Each POV call has a `shots[]` sub-array. Fill per shot:
  - `index` — global shot number (0 = first shot of call 1, continues across calls)
  - `duration` — `"5"` (string; all shot durations in a call must sum to `duration_total`)
  - `type` — `"hook"` | `"threat"` | `"moves"` | `"outcome"`
  - `location` — human-readable location name. **MUST differ between adjacent shots** (location variety is the immersion engine).
  - `survival_pct` — integer 0–100. Starts at the hook value matching `hook_plate`, moves per narration step, lands at 0 (`death`) or 60–85 (`survive`) on the final shot.
  - `tts_segment` — 10–15 word narration fragment. Second person, present tense, imperative.
  - `action_description` — what the viewer sees and feels from first person. Three layers: camera movement + environment reaction + atmospheric element. No hands, no body, no weapon barrels.
- **Графические оверлеи → `clips[].overlays[]`** (рисует `tools/overlays.py`, НЕ субтитры — см. схему overlays[] в `rules/roles/scenarist.md`):
  - **Title card (call 0):** два `title`-оверлея — название ситуации (fs130, 2 строки через `\n`, y680/840) + hook_plate `"SURVIVAL CHANCE: N%"` (fs60 red, y1030). `action_description` — wide cinematic, NOT POV. Нет `tts_segment`.
  - **POV call:** по одному `hud_counter` на каждый shot — `text:"SURVIVAL N%"`, top-right, `enable:[t0,t1]` (5-сек окно shot'а внутри call-файла: shot 0 → [0,5], shot 1 → [5,10], shot 2 → [10,15]). N = `survival_pct` этого shot'а.
  - **Final POV call:** добавь `outcome_plate` (`"YOU SURVIVED"` green / `"YOU DIED"` red — всегда EN), center, `enable:["gte", call_dur-1.5]`, fade_in 0.4.
  - `survival_pct` в shots оставляешь (нарративная логика арки); значения дублируешь в `hud_counter.text`.
- **`elements[]` per POV call:** if a significant entity (boss, monster part, enemy group) enters a specific shot, list it in the call's `elements[]` array with a `slug` and `description`. Storyboarder will generate refs; Animator wires them via `@Element1` in the shot prompt.
- **Narrator starts on shot 0 of call 1** (after title card). First `tts_segment` opens: "Ты оказался…". All `tts_segment` values concatenated in index order → `tts.full_text`.
- **No character-face ref. No prop/vehicle ref** unless absolutely required for continuity.
- Voice: pick from ElevenLabs by tone (tense tactical instructor — `Daniel` confident, `George` neutral-grave, `Adam` urgent). Lock in `tts.voice`.
- General script rules — `rules/roles/scenarist.md`.

**Storyboard.json — schema:**

```json
{
  "format": "in-game-pov",
  "game_tag": "{GAME_TAG}",
  "outcome": "death",
  "situation": "Osial rises — you are a Millelith soldier at Liyue Harbor",
  "tts": {
    "full_text": "{all tts_segments from shots index 0–N, in order, space-joined}",
    "voice": "George",
    "stability": 0.30,
    "style": 0.65,
    "language_code": "ru"
  },
  "music": { "mood": "tense", "volume": 0.12 },
  "clips": [
    {
      "call_index": 0,
      "call_type": "title_card",
      "duration_total": "5",
      "anchor_image": "scene-anchor-0.png",
      "location": "Liyue Harbor — sea exterior",
      "overlays": [
        {"type":"title","text":"OSIAL\nRISES","position":"(w-text_w)/2,680","font":"ULT","size":130,"color":"white","stroke":{"color":"black","width":4},"line_gap":160},
        {"type":"title","text":"SURVIVAL CHANCE: 5%","position":"(w-text_w)/2,1030","font":"MED","size":60,"color":"red"}
      ],
      "action_description": "Wide cinematic: Osial tentacles towering over Liyue Harbor, ships capsizing, distant explosions, massive wave forming"
    },
    {
      "call_index": 1,
      "call_type": "pov_multi_prompt",
      "duration_total": "15",
      "anchor_image": "scene-anchor-1.png",
      "elements": [
        {
          "slug": "osial_tentacle",
          "description": "massive black Geo-scarred sea tentacle, colossal scale, dripping dark seawater, ancient stone texture",
          "frontal_image_url": "{supabase url — filled by Storyboarder}",
          "reference_image_urls": ["{supabase url side angle}"]
        }
      ],
      "overlays": [
        {"type":"hud_counter","text":"SURVIVAL 5%","position":"top-right","font":"ARI","size":52,"color":"white","stroke":{"color":"black","width":4},"enable":[0,5]},
        {"type":"hud_counter","text":"SURVIVAL 5%","position":"top-right","font":"ARI","size":52,"color":"white","stroke":{"color":"black","width":4},"enable":[5,10]},
        {"type":"hud_counter","text":"SURVIVAL 15%","position":"top-right","font":"ARI","size":52,"color":"white","stroke":{"color":"black","width":4},"enable":[10,15]}
      ],
      "shots": [
        {
          "index": 0, "duration": "5",
          "type": "hook",
          "location": "Liyue Harbor — main dock",
          "survival_pct": 5,
          "tts_segment": "Ты на доках Ли Юэ. Осиал пробудился. Беги.",
          "action_description": "First-person dock level: tentacles rise from sea ahead, ships explode mid-distance, Millelith soldiers sprint past"
        },
        {
          "index": 1, "duration": "5",
          "type": "threat",
          "location": "burning dock planks",
          "survival_pct": 5,
          "tts_segment": "Уходи от края. Щупальце идёт справа.",
          "action_description": "Camera stumbles forward over burning dock planks, @Element1 tentacle slams warehouse to the right, smoke and splinters burst"
        },
        {
          "index": 2, "duration": "5",
          "type": "moves",
          "location": "flooding market street",
          "survival_pct": 15,
          "tts_segment": "В переулок. Вода поднимается.",
          "action_description": "Camera turns left into narrow market street, knee-deep water surges toward viewer, market stalls collapse under wave pressure"
        }
      ]
    },
    {
      "call_index": 2,
      "call_type": "pov_multi_prompt",
      "duration_total": "15",
      "anchor_image": "bridge-frame-1.png",
      "elements": [],
      "overlays": [
        {"type":"hud_counter","text":"SURVIVAL 25%","position":"top-right","font":"ARI","size":52,"color":"white","stroke":{"color":"black","width":4},"enable":[0,5]},
        {"type":"hud_counter","text":"SURVIVAL 10%","position":"top-right","font":"ARI","size":52,"color":"white","stroke":{"color":"black","width":4},"enable":[5,10]},
        {"type":"hud_counter","text":"SURVIVAL 0%","position":"top-right","font":"ARI","size":52,"color":"white","stroke":{"color":"black","width":4},"enable":[10,15]},
        {"type":"outcome_plate","text":"YOU DIED","position":"center","font":"TRJ","size":110,"color":"red","stroke":{"color":"black","width":5},"enable":["gte",13.5],"fade_in":0.4}
      ],
      "shots": [
        {
          "index": 3, "duration": "5",
          "type": "moves",
          "location": "warehouse — elevated crates",
          "survival_pct": 25,
          "tts_segment": "Вверх. На ящики. Держись.",
          "action_description": "Camera scrambles up stacked cargo crates, warehouse interior opens above, floodwater rising below, rafters shaking"
        },
        {
          "index": 4, "duration": "5",
          "type": "moves",
          "location": "harbor seawall top",
          "survival_pct": 10,
          "tts_segment": "До стены. Только до стены.",
          "action_description": "Camera sprints along seawall top, massive tidal wave builds on the horizon, Millelith bodies floating in water far below"
        },
        {
          "index": 5, "duration": "5",
          "type": "outcome",
          "location": "seawall — wave impact",
          "survival_pct": 0,
          "tts_segment": "Ты не успел.",
          "action_description": "Massive wave crashes over seawall, camera tumbles in churning whitewater, vision darkens to black"
        }
      ]
    }
  ]
}
```

### Storyboarder

- Style taken from `games/{GAME_TAG}/{GAME_TAG}.md` (identical to the game).
- All frames 9:16 (608×1080).
- **Generate anchor PNGs per call, not per shot** (fewer images than before):
  - `call_index: 0` (title card) → `scene-anchor-0.png` — wide **cinematic establishing shot**, NOT first-person POV. Atmospheric crisis from a dramatic angle. Text will be overlaid by Editor. NB2 `negative_prompt` must include `text, captions, ui, hud, hands, person pov, first person view`.
  - `call_index: 1` → `scene-anchor-1.png` — **first-person environmental view** of the first POV shot's starting location. This single anchor frame carries the whole 15s multi_prompt call; Kling transitions locations via motion prompts. NEVER show protagonist face, body, or hands.
  - `call_index: 2+` — anchor = bridge frame extracted by Animator from the end of the previous call. **Do NOT generate a PNG for these calls.** Storyboarder's job ends at call 1.
- **Elements:** for each `elements[]` entry in a call, generate a frontal reference PNG + at least one secondary-angle PNG. Upload both to Supabase. Write URLs into `elements[].frontal_image_url` and `elements[].reference_image_urls[]`. See `storyboarder.md §15.2`.
- POV anchor `image_prompt` cues: emergency lighting, smoke, debris, other characters (running), environmental chaos — but **NO numbers/text/UI** (Editor overlays only).
- **Every POV anchor `image_prompt` MUST end with:** `". Clean environmental first-person POV. NO hands, NO weapon barrels, NO controls in frame. NO on-screen text, NO HUD numbers, NO captions, NO UI labels, NO crosshair text, NO percentage counters."`
- General rules — `rules/roles/storyboarder.md`.

### Animator

**Architecture: whole-video `multi_prompt` chaining.** The entire video is produced by **3 Kling API calls** (1 title-card + 2 POV multi_prompt), not by one call per scene. Each POV call outputs a single 15s MP4 covering 3 shots; Editor concats 3 files total.

- All calls via **Kling v3 Standard I2V** (`generate_audio: true`). Fallback v2.6 Pro only on v3 artifacts.

**Call 0 — title card (single `motion_prompt`, 5s):**
- Body: standard I2V (`prompt`, `start_image_url`, `duration: "5"`, `generate_audio: true`). **No `multi_prompt`.**
- Derive `motion_prompt` from `action_description`: very slow camera push-in toward the crisis, atmospheric debris drifts and settles, distant explosions flare and hold.

**Calls 1–2 — POV sequence (`multi_prompt`, 15s each):**
- `start_image_url` = anchor PNG for call 1; bridge frame for call 2 (see chaining below).
- `duration: "15"`, `shot_type: "customize"`, `generate_audio: true`.
- `shots[]` — 3 shots × 5s each, built from storyboard `shots[]` of that call:
  - Read each shot's `action_description`, translate to Kling technical language
  - Every shot prompt starts with: `"Environmental first-person POV."` (style anchor — prevents late shots drifting to Kling's generic prior)
  - Every shot prompt has an explicit endpoint verb: `dissipates`, `settles`, `clears`, `holds`, `pushes forward`
  - Each shot prompt ≤ 512 chars — count before submitting (validated post-submit, fails with 422 costing the round-trip)
  - No names, no moods, no hands, no weapon barrels, no protagonist body
- **`elements[]`** — if the call's storyboard has `elements[]`, add to API body. Summon in the correct shot prompt via `@Element1`. See `animator.md §5a` for full schema.
- **Body rules (strict):**
  - **Pass ONLY `multi_prompt`. No top-level `prompt`** (fal.ai 422 pre-compute).
  - **No `end_image_url`** (Kling 422 with multi_prompt).
  - Shot durations (strings) must sum exactly to top-level `duration: "15"`.

**Chaining between calls:**
```bash
# After call 1 completes and call-1.mp4 is downloaded:
ffmpeg -sseof -0.1 -i call-1.mp4 -frames:v 1 bridge-frame-1.png
# Upload bridge-frame-1.png to Supabase
# Use that URL as start_image_url for call 2
```

**`negative_prompt` on every call:**
`voices, speech, dialogue, vocals, singing, music, on-screen text, HUD numbers, percentage counter, captions, watermark, person facing camera, protagonist body, hands, arms, weapon, controls, cockpit controls, talking, photorealistic, film grain, realistic skin`

**Banned phrases in shot prompts** (Kling reads as freeze): `then settles`, `then steady`, `then holds`, `camera holds steady`, `hold position`, `no morphing`. Use continuous verbs + endpoint cues.

**Pricing:** call 0 = $0.63 (5s × $0.126) + call 1 = $1.89 (15s × $0.126) + call 2 = $1.89 = **$4.41 total** (well within $6.30 cap). If garbled speech on a call: re-run with `generate_audio: false` (saves $0.63 per call).

**Debug mode — full shot scenario before ANY Kling call (MANDATORY):**
```
=== ANIMATOR DEBUG: {SITUATION} — whole-video multi_prompt ===

Call 0  title-card  /  anchor: scene-anchor-0.png  /  5s = $0.63
  motion_prompt: "Slow camera push toward {crisis}, {debris} drifts and settles, distant explosion flares then holds."

Call 1  pov-multi_prompt  /  anchor: scene-anchor-1.png  /  15s = $1.89
  Shot 0 (0–5s,   {location}, {pct}%) "Environmental first-person POV. {≤512 chars, endpoint verb}"
  Shot 1 (5–10s,  {location}, {pct}%) "Environmental first-person POV. {≤512 chars, endpoint verb}"
  Shot 2 (10–15s, {location}, {pct}%) "Environmental first-person POV. {≤512 chars, endpoint verb}"
  → extract bridge-frame-1.png at t=14.9s → upload to Supabase

Call 2  pov-multi_prompt  /  anchor: bridge-frame-1.png  /  15s = $1.89
  Shot 3 (0–5s,   {location}, {pct}%) "Environmental first-person POV. {≤512 chars, endpoint verb}"
  Shot 4 (5–10s,  {location}, {pct}%) "Environmental first-person POV. {≤512 chars, endpoint verb}"
  Shot 5 (10–15s, {location},   0%)   "Environmental first-person POV. {≤512 chars, endpoint verb}"

elements (call 1): {slug} → @Element1 in shot {index}
Total: $0.63 + $1.89 + $1.89 = $4.41  (cap $6.30)
Proceed? (y/n)
```

Polling: base `fal-ai/kling-video`, every 15s, max 10 min. General rules — `rules/roles/animator.md §5a` (multi_prompt limits, elements, chaining).

### Sound

- **TTS:** ElevenLabs via fal.ai (`fal-ai/elevenlabs/tts/eleven-v3`).
  - `voice` = name string (Daniel/George/Adam), NOT voice_id. One voice for the whole video.
  - Generate narration from `tts.full_text` (which covers clips 1–N only — title card has no TTS). One request, one mp3.
  - Save → upload to Supabase.
- **Subtitles:** НЕ задача Sound. Единый универсальный стиль, генерит Editor по whisper из `build/voice-final.wav` (см. `rules/roles/editor.md` §6). Никаких `--style`/`--chunk`/`--text`/`--offset`/`--atempo`.
- **Speed control:** if TTS duration > POV-clips timeline, Editor applies `atempo` (cap 1.4×). Субтитры считаются по уже ускоренной речи — пересчитывать ничего не надо. If mismatch > 40% → back to Scenarist to shorten.
- **Music:** mood `tense`/`drama` from `music/tracks.json`, `volume` from storyboard (default 0.12). Never `Fun/`. Music starts from t=0 (over the title card and through the whole video).
- General rules — `rules/roles/sound.md`.

### Editor

Three-stage assembly (HUD drawtext per-call-file before concat, then subtitles, then final audio mix).

**Stage 0 — графические оверлеи (per-call-file, BEFORE concat):** рисует `tools/overlays.py` из
`clips[].overlays[]` (НЕ ручной drawtext, НЕ запекать в NB2). Для каждого call'а:
```bash
FRAG=$(python3 tools/overlays.py storyboard.json --scene-index $CALL_INDEX --workdir build \
         --input-label "[v${CALL_INDEX}pre]" --output-label "[v${CALL_INDEX}]")
# FRAG вплетается в filter_complex между scale/pad/fps и concat (editor.md §6.5)
```
- Позиции/стиль заданы в `overlays[]` сценаристом (см. «Survival HUD» и схему storyboard):
  title card — две строки fs130 white (y680/840) + hook_plate fs60 red (y1030); HUD-счётчик —
  top-right fs52 white с обводкой, по одному `hud_counter` на каждый shot с `enable:[t0,t1]`
  (5-секундные окна внутри call-файла); outcome plate — center fs110 green/red, `enable:["gte",13.5]`.
- Шрифты резолвит overlays.py (FONTS-map, фолбэки) — никаких захардкоженных путей. `%` обрабатывается
  через `expansion=none` (автоматически). Перед encode — `overlays.py storyboard.json --check`.
- Оверлеи — ТОЛЬКО через overlays.py; никогда не проси NB2/Kling рисовать HUD/числа/текст.

**Stage 1 — Picture-only concat:**
- Normalize each HUD'd file: scale 1080×1920, 30fps, `preset slow`, `crf 20`. Kling I2V is 24fps → normalize to 30fps before concat.
- Hard cuts, no crossfade.
- **Exactly 3 entries in concat-list:** `call-0-hud.mp4` (5s) + `call-1-hud.mp4` (15s) + `call-2-hud.mp4` (15s). No duplicates.
- Output: `build/concat-noaudio.mp4` (silent, 35s; CTA NOT yet appended).
- `MAIN_DUR` = 35s (5 + 15 + 15). `TTS_OFFSET` = 5s (title card duration).

**Stage 2 — Subtitle burn-in:** канонический путь editor.md §6 — `python3 tools/add_subtitles.py build/voice-final.wav build/subs.ass --storyboard storyboard.json --lang {lang} --main-dur {MAIN_DUR}`, затем `ass=build/subs.ass` последним видеофильтром. Лид-тишина title card уже в `voice-final.wav` (adelay), поэтому `--offset` не нужен.

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
│   ├── scene-anchor-0.png          (title card — cinematic establishing shot, NOT POV)
│   ├── scene-anchor-1.png          (POV anchor for call 1 — environment, NO hands)
│   ├── bridge-frame-1.png          (extracted by Animator from last frame of call-1.mp4)
│   ├── elements/
│   │   ├── {slug}-front.png        (frontal ref for Kling elements)
│   │   └── {slug}-side.png
│   ├── call-0.mp4                  (Kling I2V title card, 5s, generate_audio: true)
│   ├── call-0-hud.mp4              (after Stage 0 drawtext)
│   ├── call-0-scaled.mp4
│   ├── call-1.mp4                  (Kling multi_prompt POV shots 0–2, 15s)
│   ├── call-1-hud.mp4              (after Stage 0 time-range drawtext)
│   ├── call-1-scaled.mp4
│   ├── call-2.mp4                  (Kling multi_prompt POV shots 3–5, 15s)
│   ├── call-2-hud.mp4
│   └── call-2-scaled.mp4
├── tts-output.mp3
├── build/
│   ├── concat-noaudio.mp4          (3 files concat, HUD burned, 35s)
│   └── concat-subbed.mp4           (after add_subtitles.py burn-in)
├── concat-list.txt
└── final.mp4
```

---

## Validation before publishing

- [ ] `format: "in-game-pov"` in storyboard.json
- [ ] `outcome` set to `survive` or `death` (the value the Manager asked the user for)
- [ ] All narration is **second person, present tense** — no first-person, no past tense
- [ ] `clips[0].call_type: "title_card"` — no `shots[]`, has `title_card_text` and `hook_plate`
- [ ] `clips[1]` and `clips[2]` are `call_type: "pov_multi_prompt"`, each has `shots[]` × 3
- [ ] First shot of call 1 `tts_segment` opens: "Ты оказался…" (does NOT repeat title card verbatim)
- [ ] `survival_pct` set on every shot; moves with narration; final shot consistent with `outcome` (`death` → 0)
- [ ] `location` set on every shot; no two consecutive shots share the same location
- [ ] **Protagonist never shown** — no face, no body, **no hands**, no weapon barrel in any anchor PNG
- [ ] No on-screen text/HUD/numbers baked into any NB2 image
- [ ] HUD rendered by Editor: title card has situation name + survival %; POV call files have time-range counter (top-right); final call has outcome plate at t≥13.5s
- [ ] **No warning plates** (removed from this format — center overlays are confusing and out-of-style)
- [ ] HUD (top-right) и субтитры (низ, универсальный MarginV 520) не пересекаются
- [ ] All images 608×1080 (9:16); one PNG per scene (start frame only)
- [ ] No character-face ref; no prop-ref unless explicitly needed
- [ ] Kling I2V `generate_audio: true`; `negative_prompt` forbids voices/speech/music/on-screen-text/hands/protagonist
- [ ] No garbled speech in any clip (if found → re-run that clip with `generate_audio: false`)
- [ ] Audio mix: narrator 1.0, Kling SFX ~0.30, music ~0.12; TTS delayed by title card duration
- [ ] camera_angle differs between adjacent clips; every clip has an active camera move (no "holds steady")
- [ ] Call 0: single `motion_prompt` (no `multi_prompt`), slow push-in, continuous-tense, none of the banned freeze phrases
- [ ] Calls 1–2: `multi_prompt` 3 shots × 5s, top-level `duration: "15"`, no top-level `prompt`, no `end_image_url`
- [ ] Every shot prompt starts with `"Environmental first-person POV."` style anchor; every shot has an explicit endpoint verb; every shot ≤ 512 chars
- [ ] Bridge frame extracted from last frame of call-1.mp4 and used as `start_image_url` for call 2
- [ ] HUD drawtext: call-1/call-2 MP4s use `enable='between(t,T1,T2)'` per shot for time-varying survival_pct
- [ ] TTS via fal.ai ElevenLabs (`voice` name, not `voice_id`), one request for the whole narration
- [ ] Subtitles — универсальный стиль по whisper (editor.md §6); лид-тишина title card в voice-final.wav, отдельный offset не нужен
- [ ] fps normalized to 30 before concat; exactly 3 entries in concat-list (call-0/1/2 + CTA); single-pass audio mix; music fade before CTA
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
- ❌ "Camera holds steady" / "then settles" / "then steady" / "hold position" / "no morphing" in any shot prompt (Kling reads as freeze)
- ❌ One Kling call per scene (old architecture) — must use whole-video multi_prompt chaining (3 calls total)
- ❌ Generating anchor PNGs for call 2+ — bridge frame is extracted from call-1.mp4 by Animator, NOT generated by Storyboarder
- ❌ Single flat `motion_prompt` for POV calls — must use `multi_prompt` with `shots[]`
- ❌ Top-level `prompt` alongside `multi_prompt` — fal.ai returns 422 pre-compute
- ❌ `end_image_url` with `multi_prompt` — Kling returns 422
- ❌ Missing style anchor `"Environmental first-person POV."` in any shot prompt — late shots drift to Kling's generic realistic prior
- ❌ Shot prompt > 512 chars — validated post-submit, costs the round-trip before failing
- ❌ Per-scene drawtext (old approach) — must use time-range `enable='between(t,T1,T2)'` on the 15s call-level MP4s
- ❌ Skipping debug-mode multi-prompt scenario table — launch without it = no user visibility on timing/cost before spending $4.41
- ❌ Music from `Fun/` (wrong mood — use tense/drama)
- ❌ Burning ASS subtitles with stock ffmpeg (lacks libass — use ffmpeg-full)
- ❌ `-shortest` in any ffmpeg call (use `apad`)
