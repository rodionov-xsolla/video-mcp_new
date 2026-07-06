---
subtitles: true
overlays: true
---

# Format "In-Game POV" — you are dropped into a lore/gameplay situation, first person, survive or die

The viewer **is** the protagonist. A pure environmental first-person camera drops them into a specific situation from the game's lore (a famous battle, a canon event) or from its gameplay (a clutch firefight, a raid wipe). The video opens with a **game-styled title card** (situation name + survival %) that establishes the stakes before the first POV scene. A second-person narrator — a tense tactical instructor — then walks through what to do to survive. It plays as a **survival manual**: situation → threats → moves → outcome. But following the manual does not guarantee life — the story can end in death. The signature gimmick is a **live survival-% HUD counter** that moves across the clips and resolves on the final outcome plate.

This file is the **playbook**: when to use, concept, budget, role briefs. Craft rules (NB2 chain, Kling I2V, TTS, ffmpeg) — in `rules/roles/*.md`.

---

## When to use

Keywords: "in-game pov", "pov", "от первого лица", "first person", "ты оказался", "вы оказались", "тебя зажали", "survival guide", "survival manual", "как выжить", "how to survive", "survive the", "выживание", "shance of survival", "you wake up", "ты очнулся".

Best fit when the game has either (a) a **named canon event/battle** with high stakes (Wolf 359, a famous raid, a story climax) or (b) **tense gameplay scenarios** that read instantly in first person (a 1vX clutch, a boss enrage, a horde rush). Games with neither strong lore nor readable POV gameplay are a weak fit — pick `character-story` or `what-if-real-life` instead.

**Single-shot per video** — no story bible, no continuity between videos. Each video is one situation, one POV, one predetermined outcome.

### Manager asks before Scenarist runs

**Step 1 — Outcome question (mandatory):**
> **«Эта история — про выживание или про гибель?»** (survive / death)

The answer is passed to Scenarist as `OUTCOME` and locked into `storyboard.json → outcome`. The whole script (which moves work, where the % lands, the final plate) is written to serve that predetermined ending. If the user does not specify and cannot be asked, default to a **50/50 author's choice**, leaning to `death` only when the situation is canonically lethal (e.g. a battle the faction historically lost).

**Step 2 — Story bible check (mandatory, before Scenarist):**
Read `games/{GAME_TAG}/in-game-pov_story_bible.json` if it exists. Pass the full `used_situations[]` array and `anti_repetition` block to Scenarist in the prompt. Scenarist must not repeat any situation or threat type from that list. If the file does not exist — create it after the video is published (see Phase 5).

**Step 3 — After publishing (mandatory):**
Update `games/{GAME_TAG}/in-game-pov_story_bible.json` — add the new situation entry with date, outcome, threat_type, and published: true. Push to git with the episode commit.

---

## Concept

- **Genre:** first-person survival manual / immersive POV
- **Perspective:** pure environmental POV. Second person ("ты"/"вы"). The protagonist is **never shown** — no face, no reflection, no over-the-shoulder, **no hands**. The camera IS their eyes. We look at the world, we walk through it, we breathe.
- **Style:** resolved from the style chain — story bible `style_tags` if present, else game config `prompt_prefix` (which for this format is the game's house style).
- **Duration:** 35–45s (title card + 5–6 POV clips × 5s + CTA).
- **Budget:** up to $7.00 per video. Stop if spend > $6.30.
- **Frame format:** 9:16 (608×1080) for all scenes.

### Models

- **Image:** NB2 (`fal-ai/nano-banana-2/edit`) — title card + one PNG per POV clip. No character-face ref. No prop refs unless a specific object needs continuity.
- **Video:** Kling v3 Standard I2V (`fal-ai/kling-video/v3/standard/image-to-video`) — one 5s call per clip, `generate_audio: true` (POV combat SFX: explosions, alarms, gunfire, hull groan, heavy breathing). Fallback to v2.6 Pro only on v3 artifacts.
- **Audio:** ElevenLabs TTS — second-person narrator (one voice, clips 1–N) overlaid on the picture. TTS does NOT start on title card. Kling SFX kept underneath at low volume. Music bed under everything.
- **HUD overlays:** drawn by `tools/overlays.py` (NOT baked into NB2). See "## Overlays" below.

### Key mechanics

1. **Title card first.** Scene 0 is a game-styled title card (not POV) that names the situation and shows the starting survival %. It plays 3–5s with Kling ambient SFX. **Optional title card TTS:** a brief 1–2 sentence situational intro (e.g. "Attack on the Akademiya. Survival chance — eight percent.") is allowed when the Manager decides the viewer needs verbal context to land the hook. If clip 0 has a `tts_segment`, TTS_OFFSET = 0 in the Editor (no adelay). If absent, TTS_OFFSET = 5s (default). The hook lives here visually — title card TTS is ambient framing, not POV narration.
2. **POV = environmental, never hands.** From clip 1 onward: pure look-around / walk-through / reaction POV. No hands gripping controls. No weapon barrels. Camera sees the world — corridors, consoles, windows, other crew, debris — as the viewer walks and breathes.
3. **Location variety mandatory.** Each POV clip is a different space aboard the ship (or outside it): bridge, corridor, engineering, escape pod bay, airlock, porthole exterior view. Never two consecutive clips in the same location.
4. **Each shot is a CUT, not a camera pan.** Shots do not flow into each other — there is a hard cut between them, and the viewer is instantly dropped into a new location. The cut IS the movement between places; it is invisible. Within a shot, only the environment moves (alarms strobe, doors slam, crew runs past). `tts_segment` opens by placing the viewer IN the new situation: `"Вы на мостике — объявлена эвакуация."` NOT: `"Вы поворачиваете голову к мостику."` — head-turn narration implies one continuous camera; here every shot is a fresh location drop.
5. **Live survival-% HUD.** A small persistent `SURVIVAL: X%` counter sits in the top-right corner and changes value per clip. It is a **programmatic drawtext overlay**, not an AI-rendered element.
6. **Predetermined outcome.** `survive` or `death`, decided by the Manager's question. Arc written backwards from it.

---

## Overlays

Graphic overlays (NOT subtitles) — rendered by `tools/overlays.py` from `clips[].overlays[]`,
per-scene before concat. **LAYOUT (type/position/size/timing) is defined here; font/color/stroke come
from `games/{tag}/{tag}.md` → `## Overlay brand` (font role → brand font).** Never bake into NB2 —
`negative_prompt` must forbid on-screen text/HUD/numbers. Schema: `rules/roles/scenarist.md`.

| # | type | position | size | enable | font role | text source |
|---|------|----------|------|--------|-----------|-------------|
| 1 | `title` | `(w-text_w)/2,680` (+`\n` → y840) | 130 | whole title-card clip | display | situation name (2 lines) |
| 2 | `title` (hook) | `(w-text_w)/2,1030` | 60 | whole title-card clip | label (accent color) | `"SURVIVAL CHANCE: N%"` |
| 3 | `hud_counter` | `top-right` | 52 | shot window `[t0,t1]` | label | `"SURVIVAL N%"`, N = shot `survival_pct` |
| 4 | `outcome_plate` | `center` | 110 | `["gte", clip_dur-1.5]`, fade_in 0.4 | display | `YOU SURVIVED`/`YOU DIED` (always EN) |

- The counter **moves with the narration**: starts at the title-card value, up on a successful step,
  down on a new threat, lands on the locked `outcome` on the last scene (`survive`→71%, `death`→0%).
  One `hud_counter` per clip with enable window `[0,5]` (full 5s clip duration).
- Subtitle band (universal MarginV 520, y≈1256–1400) stays clear: HUD top-right, outcome center.

---

## Budget (rough estimates)

| Component | 5s clip |
|---|---|
| Image (NB2, start frame only) | $0.08 |
| Kling v3 I2V 5s (`generate_audio: true`) | $0.63 |
| **Per clip** | **~$0.71** |

| Component | Cost |
|---|---|
| ElevenLabs TTS (~30s second-person narration over POV clips) | ~$0.18 |
| Music (local) | $0.00 |
| HUD overlays (Editor drawtext) | $0.00 |

| Variant | Clips | Cost |
|---|---|---|
| Base (recommended) | title card + 5 POV × 5s + CTA | ~$4.44 |
| Extended | title card + 6 POV × 5s + CTA | ~$5.15 |

Max with 1–2 retries: **$7.00**. Stop at **$6.30**.

> SFX note: `generate_audio: true` is **experimental** for this format (combat ambience boosts immersion). Because the camera shows no faces and no one talks on screen, Kling has nothing to lip-sync and rarely produces the "bad voice" problem. Still, push `voices, speech, dialogue, vocals, music` into the Kling `negative_prompt` so it stays pure SFX. If a clip comes back with garbled speech, re-run that single clip with `generate_audio: false` (saves $0.21).

---

## Video structure (title card + 5–6 POV clips, written backwards from the outcome)

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
- **Each clip = a new location (hard cut).** Bridge → corridor → engine room → escape pod bay. Never the same space twice. The journey through the ship *is* the narrative — each shot drops the viewer into a new place. `tts_segment` opens with where they ARE now, not how they got there: `"Вы на мостике — объявлена эвакуация."` / `"Вы бежите по коридору, но дверь закрывается."` / `"Вы нашли выход через вентиляцию."` Each sentence is a new world, new stakes.
- **Environmental immersion.** Camera sees what the protagonist sees as they move: alarms strobing in a corridor, emergency doors slamming, other crew running past, smoke. No hands, no controls — just the world reacting.
- **Honest stakes.** If the outcome is `death`, the manual should look almost-right — the viewer should feel they nearly made it.

### What does NOT work

- ❌ Showing the protagonist (defeats POV)
- ❌ Hands, weapon barrels, or cockpit controls in frame — pure environmental look/walk/breathe POV
- ❌ Two consecutive clips in the same location — must show location variety
- ❌ `tts_segment` describing HOW the viewer moves between locations ("вы поворачиваете голову вправо", "вы идёте к двери", "вы оглядываетесь") — each shot is a hard CUT; the viewer is already IN the new location when the segment starts. Narrate the new situation, not the transit.
- ❌ Third-person or first-person-past narration ("I was in the battle") — second-person present ("ты в бою")
- ❌ Narrator describing the picture ("на экране взрыв" — bad; "уклоняйся, слева ракета" — good)
- ❌ A static % (the counter must move — that's the retention hook)
- ❌ `tts.full_text` over 67 words — TTS will run over the 30s video window, forcing aggressive atempo or freeze-extend
- ❌ Last POV clip `tts_segment` not ending with `"You died."` / `"You survived."` — verbal and visual outcomes must be synchronised
- ❌ Outcome that contradicts the locked `outcome` field
- ❌ Baking the HUD/% into NB2 images

### The narration

- Second person, present tense, imperative. One voice for the whole video.
- **Word cap: `tts.full_text` ≤ 67 words total** (all clips combined, including clip 0 if it has tts_segment). At ~0.5s/word ElevenLabs pace, 67 words ≈ 33s — fits the 30s video window with headroom for the 1.4× atempo cap. Per-clip guideline: title card ≤ 8 words; each POV clip ≤ 12 words.
- **Last POV clip rule: the final POV clip's `tts_segment` MUST end with `"You died."` (outcome = death) or `"You survived."` (outcome = survive), always EN, always the final two words of the segment.** This synchronises the verbal narration with the outcome plate visual. The scenarist writes this as the closing beat of the last segment — it is NOT an afterthought append.
- Short, clipped, urgent. Each clip ≈ 10–12 words (strict cap).
- Normally starts on clip 1 (after the title card); see Key Mechanics item 1 for the optional clip 0 TTS exception.
- Does NOT repeat the title card text verbatim — the visual established it; narration moves the story forward.
- **Each `tts_segment` opens by placing the viewer IN the new location** — not describing how they arrived. The cut is the transport. Pattern: `"[Where you are] — [what is happening / immediate threat or action]."` Examples: `"Вы на мостике — объявлена эвакуация."` / `"Вы бежите по коридору — дверь закрывается."` / `"Вы нашли выход через вентиляцию."` / `"Вы выбрались — но это реакторный отсек. Он взрывается."` Each sentence = a new world.

---

## Story Bible

`games/{GAME_TAG}/in-game-pov_story_bible.json` — tracks every situation ever used for this game in this format. Prevents repetition of threats, locations, and core premises.

**Schema:**
```json
{
  "format": "in-game-pov",
  "game_tag": "{GAME_TAG}",
  "last_updated": "YYYY-MM-DD",
  "used_situations": [
    {
      "situation": "Human-readable description of the situation",
      "date": "YYYY-MM-DD",
      "outcome": "death",
      "threat_type": "Borg",
      "published": false,
      "status": "completed",
      "comment": ""
    }
  ],
  "anti_repetition": {
    "threat_types_used": ["Borg", "Dominion"],
    "note": "Free-text reminder for Scenarist about what to avoid"
  }
}
```

**Rules:**
- Scenarist reads this file before choosing a situation. Never reuse a `threat_type` from the last 3 entries. Never reuse the same core premise (even if the title differs).
- Manager updates this file after the video is published (`published: true`, `status: "completed"`). If the video had errors and was never published, still log it with `published: false` and `status: "error"`.
- If the file does not exist for a game, create it after the first in-game-pov for that game.

---

## Role briefs

### Scenarist

- Receive `OUTCOME` (`survive`/`death`) from Manager. Lock it in `storyboard.json → outcome`. Write the whole arc backwards from it.
- **Read the story bible** passed by Manager (`used_situations[]` + `anti_repetition`). Choose a situation that has NOT been used before — different threat type, different setting, different core premise. If all obvious candidates are taken, escalate to Manager.
- Pick the situation: lore event OR gameplay scenario, per the game (`games/{GAME_TAG}/{GAME_TAG}.md`). If the game has no usable lore, use a gameplay scenario; if neither reads well in POV, tell Manager this format is a weak fit.
- **Video structure: 1 title-card clip + 5–6 POV clips, each 5s, independent.** Total ~30–35s before CTA. Each clip = one Kling I2V call.
- **Write flat clips, not nested shots.** Each entry in `clips[]` is one clip:
  - `index` — integer, 0 = title card, 1–N = POV clips
  - `clip_type` — `"title_card"` (index 0) | `"pov"` (index 1+)
  - `type` — (pov only) `"hook"` | `"threat"` | `"moves"` | `"outcome"`
  - `duration` — `"5"` (string)
  - `location` — human-readable location name. **MUST differ between adjacent clips** (location variety is the immersion engine).
  - `survival_pct` — (pov only) integer 0–100. Starts at the hook value matching `hook_plate`, moves per narration step, lands at 0 (`death`) or 60–85 (`survive`) on the final clip.
  - `tts_segment` — (pov only) **10–12 word** narration fragment (hard cap — see word cap rule). Second person, present tense, imperative. Opens by placing the viewer IN the new location. **Final POV clip only:** segment MUST end with `"You died."` or `"You survived."` (always EN).
  - `action_description` — what the viewer sees and feels from first person. Three layers: camera movement + environment reaction + atmospheric element. No hands, no body, no weapon barrels.
- **Graphic overlays → `clips[].overlays[]`** (rendered by `tools/overlays.py`, NOT subtitles — layout in the `## Overlays` section above, schema in `rules/roles/scenarist.md`; font/color/stroke from game `## Overlay brand`):
  - **Title card (clip 0):** two `title` overlays — situation name (size 130, 2 lines via `\n`, y680/840) + hook plate `"SURVIVAL CHANCE: N%"` (size 60, label role, y1030). `action_description` = wide cinematic, NOT POV. No `tts_segment`.
  - **Each POV clip:** one `hud_counter` overlay — `text:"SURVIVAL N%"`, top-right, `enable:[0,5]` (whole 5s clip). N = that clip's `survival_pct`.
  - **Last POV clip (outcome):** add `outcome_plate` (`"YOU SURVIVED"` green / `"YOU DIED"` red — always EN), center, `enable:["gte", clip_dur-1.5]`, fade_in 0.4.
- **Narrator normally starts on clip 1** (after title card). Exception: if the Manager authorizes title card TTS, add a `tts_segment` to clip 0 (situation + survival %, not POV voice). In that case TTS_OFFSET = 0 in Editor. First POV tts_segment (clip 1) still opens: "You are in…" / "Ты оказался…". All `tts_segment` values concatenated in index order → `tts.full_text`.
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
    "full_text": "{all tts_segments from clips index 1–N, in order, space-joined}",
    "voice": "George",
    "stability": 0.30,
    "style": 0.65,
    "language_code": "ru"
  },
  "music": { "mood": "tense", "volume": 0.12 },
  "clips": [
    {
      "index": 0,
      "clip_type": "title_card",
      "duration": "5",
      "location": "Liyue Harbor — sea exterior",
      "overlays": [
        {"type":"title","text":"OSIAL\nRISES","position":"(w-text_w)/2,680","font":"ULT","size":130,"color":"white","stroke":{"color":"black","width":4},"line_gap":160},
        {"type":"title","text":"SURVIVAL CHANCE: 5%","position":"(w-text_w)/2,1030","font":"MED","size":60,"color":"red"}
      ],
      "action_description": "Wide cinematic: Osial tentacles towering over Liyue Harbor, ships capsizing, distant explosions, massive wave forming"
    },
    {
      "index": 1,
      "clip_type": "pov",
      "type": "hook",
      "duration": "5",
      "location": "Liyue Harbor — main dock",
      "survival_pct": 5,
      "tts_segment": "Ты на доках Ли Юэ. Осиал пробудился. Беги.",
      "action_description": "First-person dock level: tentacles rise from sea ahead, ships explode mid-distance, Millelith soldiers sprint past",
      "overlays": [
        {"type":"hud_counter","text":"SURVIVAL 5%","position":"top-right","font":"ARI","size":52,"color":"white","stroke":{"color":"black","width":4}}
      ]
    },
    {
      "index": 2,
      "clip_type": "pov",
      "type": "threat",
      "duration": "5",
      "location": "burning dock planks",
      "survival_pct": 5,
      "tts_segment": "Уходи от края. Щупальце идёт справа.",
      "action_description": "Camera stumbles forward over burning dock planks, tentacle slams warehouse to the right, smoke and splinters burst",
      "overlays": [
        {"type":"hud_counter","text":"SURVIVAL 5%","position":"top-right","font":"ARI","size":52,"color":"white","stroke":{"color":"black","width":4}}
      ]
    },
    {
      "index": 3,
      "clip_type": "pov",
      "type": "moves",
      "duration": "5",
      "location": "flooding market street",
      "survival_pct": 15,
      "tts_segment": "В переулок. Вода поднимается.",
      "action_description": "Camera in narrow market street, knee-deep water surges toward viewer, market stalls collapse",
      "overlays": [
        {"type":"hud_counter","text":"SURVIVAL 15%","position":"top-right","font":"ARI","size":52,"color":"white","stroke":{"color":"black","width":4}}
      ]
    },
    {
      "index": 4,
      "clip_type": "pov",
      "type": "moves",
      "duration": "5",
      "location": "warehouse — elevated crates",
      "survival_pct": 25,
      "tts_segment": "Вверх. На ящики. Держись.",
      "action_description": "Camera scrambles up stacked cargo crates, floodwater rising below, rafters shaking",
      "overlays": [
        {"type":"hud_counter","text":"SURVIVAL 25%","position":"top-right","font":"ARI","size":52,"color":"white","stroke":{"color":"black","width":4}}
      ]
    },
    {
      "index": 5,
      "clip_type": "pov",
      "type": "outcome",
      "duration": "5",
      "location": "seawall — wave impact",
      "survival_pct": 0,
      "tts_segment": "Ты не успел.",
      "action_description": "Massive wave crashes over seawall, camera tumbles in churning whitewater, vision darkens to black",
      "overlays": [
        {"type":"hud_counter","text":"SURVIVAL 0%","position":"top-right","font":"ARI","size":52,"color":"white","stroke":{"color":"black","width":4}},
        {"type":"outcome_plate","text":"YOU DIED","position":"center","font":"TRJ","size":110,"color":"red","stroke":{"color":"black","width":5},"enable":["gte",3.5],"fade_in":0.4}
      ]
    }
  ]
}
```

### Storyboarder

- Style resolved from the style chain — story bible `style_tags` if present, else game config `prompt_prefix` (the game's house style for this format). Apply it verbatim.
- All frames 9:16 (608×1080).
- **Generate ONE PNG per clip** — title card + every POV clip. N clips → N PNGs.
  - `clip 0` (title card) → `scene-0.png` — wide **cinematic establishing shot**, NOT first-person POV. Atmospheric crisis from a dramatic angle. NB2 `negative_prompt` must include `text, captions, ui, hud, hands, person pov, first person view`.
  - `clip 1` → `scene-1.png` — **first-person environmental view** of that clip's location. NEVER show protagonist face, body, or hands.
  - `clip 2+` → `scene-K.png` — same rules. Chain the previous clip's PNG as an `image_url` ref for visual consistency (environment lighting/tone carryover). Max 2 refs (bg-ref + prev-scene).
- POV `image_prompt` cues: emergency lighting, smoke, debris, other characters (fleeing), environmental chaos — but **NO numbers/text/UI** (Editor overlays only).

- **Camera height — STRICT:** camera is ALWAYS at standing human eye level (~160–170 cm). NEVER elevated, overhead, bird's-eye, or from tiered seating height. Describe explicitly: `"camera at standing human eye level"`. If the action_description says "from elevated seating" — ignore it; plant the camera at floor level among the people.

- **NPC direction — STRICT:** when NPCs are present in frame (scholars, guards, researchers), they MUST be fleeing AWAY from the camera — backs visible, running toward exits, moving in the SAME direction as the viewer. NEVER facing the camera or running toward it. Describe explicitly: `"backs to the camera, running ahead toward [exit/door/staircase]"`. NPCs running toward camera looks like they're charging the viewer and breaks the POV illusion completely.

- **Populate crowd scenes:** any scene where the action_description mentions "scholars flee", "guards run", "researchers scatter" — include 2–4 NPCs explicitly in the image_prompt with backs to camera. An empty scene in a mass-evacuation context looks wrong. Exception: undercroft stairwell and sealed-off dead-end scenes may be empty (isolation = horror).

- **Every POV `image_prompt` MUST end with:** `". Clean environmental first-person POV. NO hands, NO weapon barrels, NO controls in frame. NO on-screen text, NO HUD numbers, NO captions, NO UI labels, NO crosshair text, NO percentage counters."`
- General rules — `rules/roles/storyboarder.md`.

### Animator

**Architecture: one Kling v3 Standard I2V call per clip (5s each).** N clips → N Kling calls. Simple, controllable, no chaining artifacts.

- All calls via **Kling v3 Standard I2V** (`fal-ai/kling-video/v3/standard/image-to-video`), `generate_audio: true`. Fallback v2.6 Pro only on v3 artifacts.

**Call structure per clip:**
- `start_image_url` — Supabase URL of `scene-K.png` (Storyboarder uploaded it)
- `duration: "5"` (string)
- `generate_audio: true`
- `prompt` — motion description derived from `action_description`
- `negative_prompt` — see below
- **No `multi_prompt`**, no `end_image_url`, no `shot_type`

**Title card motion (clip 0):**
- Very slow camera push-in toward the crisis. Atmospheric debris drifts and settles. Distant explosion flares and holds. Continuous verb tense throughout.

**POV clip motion (clips 1–N):**
- Every prompt starts with: `"Environmental first-person POV."` (style anchor)
- Every prompt ends with an explicit endpoint verb: `dissipates`, `settles`, `clears`, `holds`, `pushes forward`
- No names, no moods, no hands, no weapon barrels, no protagonist body
- Prompt ≤ 512 chars (count before submitting)

**`negative_prompt` on every call** (functional core — always include):
`voices, speech, dialogue, vocals, singing, music, on-screen text, HUD numbers, percentage counter, captions, watermark, person facing camera, protagonist body, hands, arms, weapon, controls, cockpit controls, talking`
Then append style anti-drift terms **derived from the resolved `style_tags`** (the opposite render medium) so the POV stays on the game's house style — e.g. `photorealistic, film grain, realistic skin` when the game style is stylized/illustrated. Do not hardcode anti-realism terms when the game's own style is photoreal.

**Banned phrases in prompts** (Kling reads as freeze): `then settles`, `then steady`, `then holds`, `camera holds steady`, `hold position`, `no morphing`. Use continuous verbs + endpoint cues.

**Debug mode — full scenario table before ANY Kling call (MANDATORY):**
```
=== ANIMATOR DEBUG: {SITUATION} — per-clip I2V ===

Clip 0  title-card  /  PNG: scene-0.png  /  5s = $0.63
  prompt: "Slow camera push toward {crisis}, {debris} drifts and settles, distant explosion flares then holds."

Clip 1  pov/hook    /  PNG: scene-1.png  /  5s = $0.63  /  {pct}%
  prompt: "Environmental first-person POV. {≤512 chars, endpoint verb}"

Clip 2  pov/threat  /  PNG: scene-2.png  /  5s = $0.63  /  {pct}%
  prompt: "Environmental first-person POV. {≤512 chars, endpoint verb}"

...

Clip N  pov/outcome /  PNG: scene-N.png  /  5s = $0.63  /  {pct}%
  prompt: "Environmental first-person POV. {≤512 chars, endpoint verb}"

Total: {N+1} × $0.63 = ${total}  (cap $6.30)
Proceed? (y/n)
```

**Per-clip output:** download to `scenes/scene-K.mp4`, validate (filesize > 100KB, ffprobe duration ~5s). On garbled speech: re-run that single clip with `generate_audio: false`.

Polling: base `fal-ai/kling-video`, every 15s, max 10 min per clip.

**Pricing:** (N+1) clips × $0.63 per clip. Base (6 clips total) = $3.78 + title card $0.63 = **$4.41** (well within $6.30 cap). If garbled speech on a clip: re-run with `generate_audio: false` (saves $0.21 per clip).

### Sound

- **TTS:** ElevenLabs via fal.ai (`fal-ai/elevenlabs/tts/eleven-v3`).
  - `voice` = name string (Daniel/George/Adam), NOT voice_id. One voice for the whole video.
  - Generate narration from `tts.full_text` (covers clips 1–N, and clip 0 if it has a `tts_segment`). One request, one mp3.
  - Save → upload to Supabase.
- **Subtitles:** NOT Sound's job. One universal style, generated by Editor via whisper from `build/voice-final.wav` (see `rules/roles/editor.md` §6). No `--style`/`--chunk`/`--text`/`--offset`/`--atempo`.
- **Speed control:** if TTS duration > POV-clips timeline, Editor applies `atempo` (cap 1.4×). Subtitles are computed from the already sped-up speech — nothing to recompute. If mismatch > 40% → back to Scenarist to shorten.
- **Music:** mood `tense`/`drama` from `music/tracks.json`, `volume` from storyboard (default 0.12). Never `Fun/`. Music starts from t=0 (over the title card and through the whole video).
- General rules — `rules/roles/sound.md`.

### Editor

Three-stage assembly (HUD drawtext per-clip before concat, then subtitles, then final audio mix).

**Stage 0 — graphic overlays (per-clip, BEFORE concat):** drawn by `tools/overlays.py` from
`clips[].overlays[]` (NOT manual drawtext, do NOT bake into NB2). For each clip K:
```bash
FRAG=$(python3 tools/overlays.py storyboard.json --scene-index $K --workdir build \
         --input-label "[v${K}pre]" --output-label "[v${K}]")
# FRAG is spliced into filter_complex between scale/pad/fps and concat (editor.md §6.5)
```
- Positions/style come from `overlays[]` written by the scenarist (see the `## Overlays` table):
  title card — two lines fs130 white (y680/840) + hook_plate fs60 red (y1030); HUD counter —
  top-right fs52 white with outline (no time-range `enable` needed — each clip is 5s); outcome plate —
  center fs110 green/red, `enable:["gte",3.5]`.
- overlays.py resolves fonts (FONTS map, fallbacks) — no hardcoded paths. `%` is handled
  via `expansion=none` (automatically). Before the encode — `overlays.py storyboard.json --check`.
- Overlays — ONLY via overlays.py; never ask NB2/Kling to draw HUD/numbers/text.

**Stage 1 — Picture-only concat:**
- Normalize each HUD'd clip: scale 1080×1920, 30fps, `preset slow`, `crf 20`. Kling I2V is 24fps → normalize to 30fps before concat.
- Hard cuts, no crossfade.
- Concat-list entries: `scene-0-hud.mp4` + `scene-1-hud.mp4` + … + `scene-N-hud.mp4`. No duplicates.
- Output: `build/concat-noaudio.mp4` (silent; CTA NOT yet appended).
- `MAIN_DUR` = (N+1) × 5s. `TTS_OFFSET` = 5s (title card duration).

**Stage 2 — Subtitle burn-in:** the canonical path, editor.md §6 — `python3 tools/add_subtitles.py build/voice-final.wav build/subs.ass --storyboard storyboard.json --lang {lang} --main-dur {MAIN_DUR}`, then `ass=build/subs.ass` as the last video filter. The title-card lead silence is already in `voice-final.wav` (adelay), so `--offset` is not needed.

**Stage 3 — Final audio mix (one ffmpeg pass):**
- Inputs: `build/concat-subbed.mp4` + `tts-output.mp3` + Kling SFX (baked in each clip's audio — preserve) + music + `cta-scaled.mp4`.
- **Audio levels:** narrator TTS = 1.0 (front), Kling combat SFX = ~0.30 (bed), music = `music.volume` (~0.12). Mix all three over MAIN_DUR.
- TTS delayed by `TTS_OFFSET` in the mix: `adelay={TTS_OFFSET_MS}|{TTS_OFFSET_MS}` on the TTS input. **TTS_OFFSET = 0** if `clips[0].tts_segment` exists (narrator starts with title card); **TTS_OFFSET = 5000ms** (default) if clip 0 has no tts_segment (title card plays with SFX + music only).
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
│   ├── scene-0.png              (title card — cinematic establishing shot, NOT POV)
│   ├── scene-0.mp4              (Kling I2V title card, 5s, generate_audio: true)
│   ├── scene-0-hud.mp4          (after Stage 0 drawtext)
│   ├── scene-1.png              (POV clip 1 start frame — environment, NO hands)
│   ├── scene-1.mp4
│   ├── scene-1-hud.mp4
│   ├── ...
│   ├── scene-N.png
│   ├── scene-N.mp4              (final POV clip — outcome plate burned in)
│   └── scene-N-hud.mp4
├── tts-output.mp3
├── build/
│   ├── concat-noaudio.mp4       (N+1 clips concat, HUD burned)
│   └── concat-subbed.mp4        (after add_subtitles.py burn-in)
├── concat-list.txt
└── final.mp4
```

---

## Validation before publishing

- [ ] `format: "in-game-pov"` in storyboard.json
- [ ] `outcome` set to `survive` or `death` (the value the Manager asked the user for)
- [ ] Story bible checked — situation is NOT a repeat of any `used_situations[]` entry (different threat type, premise, core scenario)
- [ ] All narration is **second person, present tense** — no first-person, no past tense
- [ ] `tts.full_text` ≤ 67 words total (count before passing to Sound)
- [ ] Last POV clip `tts_segment` ends with `"You died."` (death) or `"You survived."` (survive) — always EN
- [ ] `clips[0].clip_type: "title_card"` — no `tts_segment`, wide cinematic `action_description`
- [ ] All other clips are `clip_type: "pov"`, each with `type`, `location`, `survival_pct`, `tts_segment`, `action_description`
- [ ] First `tts_segment` (clip 1) opens: "Ты оказался…" (does NOT repeat title card verbatim)
- [ ] No `tts_segment` describes head turns or movement TOWARD a location — each opens by placing viewer IN the new situation
- [ ] `survival_pct` set on every pov clip; moves with narration; final clip consistent with `outcome` (`death` → 0, `survive` → 60–85)
- [ ] `location` set on every clip; no two consecutive clips share the same location
- [ ] **Protagonist never shown** — no face, no body, **no hands**, no weapon barrel in any PNG
- [ ] No on-screen text/HUD/numbers baked into any NB2 image
- [ ] HUD rendered by Editor: title card has situation name + survival %; each POV clip has its own `hud_counter` (always-on, no time range); last POV clip has `outcome_plate` at t≥3.5s
- [ ] **No warning plates** (removed from this format — center overlays are confusing and out-of-style)
- [ ] HUD (top-right) and subtitles (bottom, universal MarginV 520) do not overlap
- [ ] All images 608×1080 (9:16); one PNG per clip (start frame only)
- [ ] No character-face ref; no prop-ref unless explicitly needed
- [ ] Kling I2V `generate_audio: true`; `negative_prompt` forbids voices/speech/music/on-screen-text/hands/protagonist
- [ ] No garbled speech in any clip (if found → re-run that clip with `generate_audio: false`)
- [ ] Audio mix: narrator 1.0, Kling SFX ~0.30, music ~0.12; TTS delayed by title card duration
- [ ] Every clip has an active camera move in the motion_prompt (no "holds steady") — endpoint verb present
- [ ] Every motion_prompt starts with `"Environmental first-person POV."` for clips 1–N; title card uses slow push-in
- [ ] TTS via fal.ai ElevenLabs (`voice` name, not `voice_id`), one request for the whole narration
- [ ] Subtitles — universal whisper style (editor.md §6); if clip 0 has tts_segment: TTS_OFFSET = 0 (no silence gap before narration); if clip 0 has no tts_segment: 5s title-card lead silence via adelay in Editor
- [ ] fps normalized to 30 before concat; concat-list has exactly N+1 story clips + CTA; single-pass audio mix; music fade before CTA
- [ ] `-shortest` NOT used (use `apad`)
- [ ] After publishing: story bible updated in `games/{GAME_TAG}/in-game-pov_story_bible.json`

---

## Anti-patterns

- ❌ Showing the protagonist's face/body/hands/reflection — kills POV
- ❌ **Hands or weapon barrels in any POV clip** — this is a look/walk/breathe format, not a first-person shooter HUD format
- ❌ Two consecutive POV clips in the same location — kills momentum and immersion
- ❌ **NPCs facing or running toward the camera** — they must always be fleeing AWAY (backs to camera, same direction as viewer). NPCs running at the camera look like they're attacking the viewer.
- ❌ **Camera at elevated/overhead height** — must be standing human eye level (~160–170 cm). "Elevated tiered seating" means the camera sits at the top; it should be on the floor among the people.
- ❌ **Empty crowd scenes** — if the situation involves mass evacuation (lecture hall, archive, Great Hall), include 2–4 fleeing NPCs with backs to camera. An empty room during a catastrophe reads as a mistake, not atmosphere.
- ❌ `tts_segment` describing a head turn or movement TOWARD a location ("вы поворачиваете голову вправо", "вы замечаете", "вы идёте к") — shots are hard cuts, the viewer is instantly IN the new location; narrate situation-on-arrival, not mid-transit
- ❌ First-person-past or third-person narration — must be second-person present imperative
- ❌ Narrator just describing the picture ("на экране взрыв") instead of giving survival orders
- ❌ Baking the `SURVIVAL %`, outcome plate, or any HUD into NB2/Kling — Editor drawtext ONLY
- ❌ Static survival % (must move per clip — it's the retention hook)
- ❌ Final % / outcome plate contradicting the locked `outcome` field
- ❌ **Warning plates** (center-screen overlays like `⚠ HULL BREACH`) — they look artificial and are removed from this format
- ❌ `generate_audio: true` left on a clip that came back with garbled speech (re-run with `false`)
- ❌ Dropping the Kling SFX track in the mix (it's the immersion bed — keep at ~0.30)
- ❌ Moving narrator subtitles up into the HUD zone (HUD top-right, subs lower third)
- ❌ TTS starting over the title card without Manager authorization — default TTS_OFFSET = 5s (title card plays silent); only use TTS_OFFSET = 0 when clip 0 explicitly has a `tts_segment`
- ❌ **Duplicate scene in concat-list** — a freeze-extended scene REPLACES its entry; never append it as a second entry
- ❌ Character-face ref or prop-ref without explicit Scenarist justification
- ❌ End-frame PNGs or `tail_image_url` in Kling (causes freeze artifacts)
- ❌ "Camera holds steady" / "then settles" / "then steady" / "hold position" / "no morphing" in any prompt (Kling reads as freeze)
- ❌ **multi_prompt / pov_multi_prompt / shot chaining** — this format uses one 5s Kling call per clip; multi_prompt produces uncontrolled transitions and location drift across shots
- ❌ Bridge frame extraction or start_image_url chaining between clips — each clip uses its own independently generated NB2 PNG as start frame
- ❌ Missing style anchor `"Environmental first-person POV."` in any clip 1–N prompt — shots drift to Kling's generic realistic prior
- ❌ Prompt > 512 chars — validated post-submit, costs the round-trip before failing
- ❌ Skipping debug-mode scenario table — launch without it = no user visibility on per-clip timing/cost before spending $4.41+
- ❌ Music from `Fun/` (wrong mood — use tense/drama)
- ❌ Burning ASS subtitles with stock ffmpeg (lacks libass — use ffmpeg-full)
- ❌ `-shortest` in any ffmpeg call (use `apad`)
- ❌ **Choosing a situation already in the story bible** — always read `in-game-pov_story_bible.json` first; repeating threat type or core premise counts as a violation even if the title differs (e.g. "Borg cube" and "Borg boarding" are the same threat type)
- ❌ Not updating the story bible after publishing — every completed (or errored) run must be logged so the next Scenarist has accurate anti_repetition data
