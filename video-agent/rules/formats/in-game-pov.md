---
ready_to_post: yes
subtitles: true
overlays: true
---

# Format "In-Game POV" — you are dropped into a lore/gameplay situation, first person, survive or die

The viewer **is** the protagonist. A pure environmental first-person camera drops them into a specific situation from the game's lore (a famous battle, a canon event) or from its gameplay (a clutch firefight, a raid wipe). The video opens with a **game-styled title card** (situation name + survival %) that establishes the stakes before the first POV scene. A second-person narrator — a tense tactical instructor — then walks through what to do to survive. It plays as a **survival manual**: situation → threats → moves → outcome. But following the manual does not guarantee life — the story can end in death. The signature gimmick is a **live survival-% HUD counter** that moves across the clips and resolves on the final outcome plate.

This file is the **playbook**: when to use, concept, budget, role briefs. Craft rules (NB2 chain, I2V, TTS, ffmpeg) — in `rules/roles/*.md`.

---

## When to use

Keywords: "in-game pov", "pov", "от первого лица", "first person", "ты оказался", "вы оказались", "тебя зажали", "survival guide", "survival manual", "как выжить", "how to survive", "survive the", "выживание", "shance of survival", "you wake up", "ты очнулся".

Best fit when the game has either (a) a **named canon event/battle** with high stakes (Wolf 359, a famous raid, a story climax) or (b) **tense gameplay scenarios** that read instantly in first person (a 1vX clutch, a boss enrage, a horde rush). Games with neither strong lore nor readable POV gameplay are a weak fit — pick `character-story` or `what-if-real-life` instead.

**Single-shot per video** — no narrative continuity between videos. Each video is one situation, one POV, one predetermined outcome. The exact-format story bible is still mandatory for style, owned assets, voice ownership, and anti-repetition.

### Manager asks before Scenarist runs

**Step 1 — Outcome question (mandatory):**
> **«Эта история — про выживание или про гибель?»** (survive / death)

The answer is passed to Scenarist as `OUTCOME` and locked into `storyboard.json → outcome`. The whole script (which moves work, where the % lands, the final plate) is written to serve that predetermined ending. If the user does not specify and cannot be asked, default to a **50/50 author's choice**, leaning to `death` only when the situation is canonically lethal (e.g. a battle the faction historically lost).

**Step 2 — Story bible check (mandatory, before Scenarist):**
Read `games/{GAME_TAG}/in-game-pov_story_bible.json`. Pass the full `used_situations[]` array and `anti_repetition` block to Scenarist in the prompt. Scenarist must not repeat any situation or threat type from that list. If the file is missing or lacks the required style/asset/voice ownership data, STOP and ask the user whether to create or complete it before generation. Never auto-create it.

**Step 3 — After publishing (mandatory):**
Update `games/{GAME_TAG}/in-game-pov_story_bible.json` — add the new situation entry with date, outcome, threat_type, and published: true. Push to git with the episode commit.

---

## Concept

- **Genre:** first-person survival manual / immersive POV
- **Perspective:** pure environmental POV. Second person ("ты"/"вы"). The protagonist is **never shown** — no face, no reflection, no over-the-shoulder, **no hands**. The camera IS their eyes. We look at the world, we walk through it, we breathe.
- **Style:** exact `in-game-pov` story bible `style_tags`, unless the user gives a live override. Game config and another format are not style/appearance fallbacks. Missing style data stops generation for user direction.
- **Duration:** 35–45s (title card + 5–6 POV clips × 5s + CTA).
- **Budget:** up to $7.00 per video. Stop if spend > $6.30.
- **Frame format:** 9:16 (608×1080) for all scenes.

### Models

- **Image:** NB2 (`fal-ai/nano-banana-2/edit`) — title card + one PNG per POV clip. Any optional continuity ref must be owned by this exact `in-game-pov` format/series or come from the same run. No character-face ref. No cross-format prop refs.
- **Video:** MiniMax H3 Max I2V (route `minimax.h3max.i2v`, `minimax/h3-max/image-to-video`) — one 5s call per animated clip, 768P, numeric `duration` = `duration_sec`, `prompt_expansion_mode: "disabled"`. The clip's own sound is kept (`scene_video_audio: "native"`: POV combat SFX — explosions, alarms, gunfire, hull groan, heavy breathing), and every prompt ends with the sound clause `No music, no voices.` The route is fixed for the run: retry the same serialized request once, then stop; Kling v3 Standard and Kling 2.6 are not automatic fallbacks.
- **Audio:** MiniMax TTS for the non-identity-critical second-person narrator. Use Chatterbox only when the exact `in-game-pov` story bible owns an approved voice sample. ElevenLabs TTS and cross-format voice samples are forbidden. TTS starts on the title card and voices its displayed situation title. The clips' own SFX stay underneath at low volume. Music bed under everything.
- **HUD overlays:** drawn by `tools/overlays.py` (NOT baked into NB2). See "## Overlays" below.

### Key mechanics

1. **Title card first and voiced.** Scene 0 is a game-styled title card (not POV) that names the situation and shows the starting survival %. Its `tts_segment` is mandatory: voice the displayed situation title, then the starting survival % (e.g. "Attack on the Akademiya. Survival chance — eight percent."). TTS starts at 0; `TTS_OFFSET = 0` in the Editor. The title card plays 3–5s with the clip's ambient SFX underneath (none when the title card is a still shot; narration and music still play from t=0).
2. **POV = environmental, never hands.** From clip 1 onward: pure look-around / walk-through / reaction POV. No hands gripping controls. No weapon barrels. Camera sees the world — corridors, consoles, windows, other crew, debris — as the viewer walks and breathes.
3. **Location variety mandatory.** Each POV clip is a different space aboard the ship (or outside it): bridge, corridor, engineering, escape pod bay, airlock, porthole exterior view. Never two consecutive clips in the same location.
4. **Each shot is a CUT, not a camera pan.** Shots do not flow into each other — there is a hard cut between them, and the viewer is instantly dropped into a new location. The cut IS the movement between places; it is invisible. Within a shot, only the environment moves (alarms strobe, doors slam, crew runs past). `tts_segment` opens by placing the viewer IN the new situation: `"Вы на мостике — объявлена эвакуация."` NOT: `"Вы поворачиваете голову к мостику."` — head-turn narration implies one continuous camera; here every shot is a fresh location drop.
5. **Live survival-% HUD.** A small persistent `SURVIVAL: X%` counter sits in the top-right corner and changes value per clip. It is a **programmatic drawtext overlay**, not an AI-rendered element.
6. **Predetermined outcome.** `survive` or `death`, decided by the Manager's question. Arc written backwards from it.

### Still shots: allowed

The scenarist may plan still shots (`motion: "still"`) under the rule, cap and fields in `rules/roles/scenarist.md` "Still shots" (§8). A still scene gets its start PNG as usual and is rendered free by the Animator (`tools/still_shot.py`, no paid clip), saving ~$0.41 per 5s scene.

- **Best candidate:** the title card (scene 0) — a wide cinematic establishing shot under a very slow push-in, with title and survival % drawn on top by `tools/overlays.py`. A still has no clip sound (`scene_video_audio: "none"`), so the title card then plays narration and music without its SFX bed.
- **POV clips (1–N) stay animated as a rule:** the moving first-person camera is the format. A POV clip qualifies only if nothing in it moves and it is not the outcome clip — rare. Zero stills is a normal result.
- HUD overlays, narration timing and `MAIN_DUR` are unchanged for a still scene.

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
| MiniMax H3 Max I2V 5s (own SFX kept; $0.08/s on the returned ~5.18s) | ~$0.41 |
| **Per clip** | **~$0.49** |
| Still-shot scene (NB2 image only; `tools/still_shot.py` render is free) | $0.08 |

| Component | Cost |
|---|---|
| External TTS (MiniMax, or Chatterbox with an approved exact-format sample) | see `providers.json` |
| MiniMax Music | see `providers.json` |
| HUD overlays (Editor drawtext) | $0.00 |

| Variant | Clips | Cost |
|---|---|---|
| Base (recommended) | title card + 5 POV × 5s + CTA | ~$3.10 approx. (~$2.70 with a still title card) |
| Extended | title card + 6 POV × 5s + CTA | ~$3.60 approx. (~$3.20 with a still title card) |

Budget ceiling including permitted retries: **$7.00**. Each failed request gets at most one retry; stop spending at **$6.30**.

> SFX note: this format keeps each clip's own sound (`scene_video_audio: "native"`; combat ambience boosts immersion). H3 always returns a soundtrack. Because the camera shows no faces and no one talks on screen, the model has nothing to lip-sync and rarely produces the "bad voice" problem. H3 has no `negative_prompt`, so every prompt ends with the sound clause `No music, no voices.` to keep it pure SFX. A failed generation gets one identical retry; never switch automatically to a silent configuration (`scene_video_audio: "none"`) or another model/route. A different configuration requires a stopped run and explicit user authorization.

---

## Video structure (title card + 5–6 POV clips, written backwards from the outcome)

| Phase | Timing | Goal | Clips |
|---|---|---|---|
| **TITLE CARD** | 0–5s | Visual hook — situation name + starting survival %. Narrator voices both from t=0; atmospheric SFX stays underneath (animated title card only). | scene 0 (5s) |
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
- **Word cap: `tts.full_text` ≤ 67 words total** (all clips combined, including the mandatory clip-0 `tts_segment`). At the target narrator pace, 67 words ≈ 33s — fits the full story timeline with headroom for the 1.4× atempo cap. Per-clip guideline: title card ≤ 8 words; each POV clip ≤ 12 words.
- **Last POV clip rule: the final POV clip's `tts_segment` MUST end with `"You died."` (outcome = death) or `"You survived."` (outcome = survive), always EN, always the final two words of the segment.** This synchronises the verbal narration with the outcome plate visual. The scenarist writes this as the closing beat of the last segment — it is NOT an afterthought append.
- Short, clipped, urgent. Each clip ≈ 10–12 words (strict cap).
- Starts on clip 0. The title-card segment speaks the displayed situation title verbatim, followed by the starting survival %.
- From clip 1 onward, narration does not repeat the title; it moves the story forward.
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
- If the file does not exist or is incomplete, stop before generation and ask the user whether to create or complete it.

---

## Role briefs

### Scenarist

- Receive `OUTCOME` (`survive`/`death`) from Manager. Lock it in `storyboard.json → outcome`. Write the whole arc backwards from it.
- **Read the story bible** passed by Manager (`used_situations[]` + `anti_repetition`). Choose a situation that has NOT been used before — different threat type, different setting, different core premise. If all obvious candidates are taken, escalate to Manager.
- Pick the situation: lore event OR gameplay scenario, per the game (`games/{GAME_TAG}/{GAME_TAG}.md`). If the game has no usable lore, use a gameplay scenario; if neither reads well in POV, tell Manager this format is a weak fit.
- **Video structure: 1 title-card clip + 5–6 POV clips, each 5s, independent.** Total ~30–35s before CTA. Each animated clip = one H3 I2V call; a still scene needs none.
- **Write flat clips, not nested shots.** Each entry in `clips[]` is one clip:
  - `index` — integer, 0 = title card, 1–N = POV clips
  - `clip_type` — `"title_card"` (index 0) | `"pov"` (index 1+)
  - `type` — (pov only) `"hook"` | `"threat"` | `"moves"` | `"outcome"`
  - `duration_sec` — `5` (number). The H3 job's `duration` is this number (not a string); a still renders exactly this length.
  - `location` — human-readable location name. **MUST differ between adjacent clips** (location variety is the immersion engine).
  - `survival_pct` — (pov only) integer 0–100. Starts at the hook value matching `hook_plate`, moves per narration step, lands at 0 (`death`) or 60–85 (`survive`) on the final clip.
  - `tts_segment` — mandatory on every clip. On the title card: the displayed situation title + starting survival %, ≤8 words. On POV clips: **10–12 word** narration fragment (hard cap — see word cap rule), second person, present tense, imperative, opening by placing the viewer IN the new location. **Final POV clip only:** segment MUST end with `"You died."` or `"You survived."` (always EN).
  - `action_description` — what the viewer sees and feels from first person. Three layers: camera movement + environment reaction + atmospheric element. No hands, no body, no weapon barrels.
- **Graphic overlays → `clips[].overlays[]`** (rendered by `tools/overlays.py`, NOT subtitles — layout in the `## Overlays` section above, schema in `rules/roles/scenarist.md`; font/color/stroke from game `## Overlay brand`):
  - **Title card (clip 0):** two `title` overlays — situation name (size 130, 2 lines via `\n`, y680/840) + hook plate `"SURVIVAL CHANCE: N%"` (size 60, label role, y1030). `action_description` = wide cinematic, NOT POV. `tts_segment` is mandatory and voices the displayed situation title + starting survival %.
  - **Each POV clip:** one `hud_counter` overlay — `text:"SURVIVAL N%"`, top-right, `enable:[0,5]` (whole 5s clip). N = that clip's `survival_pct`.
  - **Last POV clip (outcome):** add `outcome_plate` (`"YOU SURVIVED"` green / `"YOU DIED"` red — always EN), center, `enable:["gte", clip_dur-1.5]`, fade_in 0.4.
- **Narrator starts on clip 0.** Its mandatory `tts_segment` voices the displayed situation title + starting survival %. `TTS_OFFSET = 0` in Editor. First POV `tts_segment` (clip 1) still opens: "You are in…" / "Ты оказался…". All `tts_segment` values concatenate in index order → `tts.full_text`.
- **No character-face ref. No prop/vehicle ref** unless absolutely required for continuity. Any allowed ref must be owned by this exact format/series or generated inside the current run.
- Voice intent: tense tactical instructor. Sound resolves it to MiniMax unless the exact `in-game-pov` story bible owns an approved Chatterbox sample; never encode an ElevenLabs voice name in the storyboard.
- General script rules — `rules/roles/scenarist.md`.

**Storyboard.json — schema:**

```json
{
  "format": "in-game-pov",
  "game_tag": "{GAME_TAG}",
  "outcome": "death",
  "situation": "Osial rises — you are a Millelith soldier at Liyue Harbor",
  "tts": {
    "full_text": "{all tts_segments from clips index 0–N, in order, space-joined}",
    "voice_intent": "tense tactical instructor",
    "language_code": "ru"
  },
  "music": { "mood": "tense", "volume": 0.12 },
  "clips": [
    {
      "index": 0,
      "clip_type": "title_card",
      "duration_sec": 5,
      "location": "Liyue Harbor — sea exterior",
      "tts_segment": "Osial rises. Survival chance — five percent.",
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
      "duration_sec": 5,
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
      "duration_sec": 5,
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
      "duration_sec": 5,
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
      "duration_sec": 5,
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
      "duration_sec": 5,
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

- Style comes from the exact `in-game-pov` story bible `style_tags` (or a live user override) and is applied verbatim. Never fall back to another format or game-wide appearance/style data.
- All frames 9:16 (608×1080).
- **Generate ONE PNG per clip** — title card + every POV clip. N clips → N PNGs.
  - `clip 0` (title card) → `scene-0.png` — wide **cinematic establishing shot**, NOT first-person POV. Atmospheric crisis from a dramatic angle. NB2 `negative_prompt` must include `text, captions, ui, hud, hands, person pov, first person view`.
  - `clip 1` → `scene-1.png` — **first-person environmental view** of that clip's location. NEVER show protagonist face, body, or hands.
  - `clip 2+` → `scene-K.png` — same rules. Chain only the previous clip's PNG from this same run as an `image_url` ref for visual consistency (environment lighting/tone carryover). Any additional ref must be owned by this exact format/series. Max 2 refs.
- POV `image_prompt` cues: emergency lighting, smoke, debris, other characters (fleeing), environmental chaos — but **NO numbers/text/UI** (Editor overlays only).

- **Camera height — STRICT:** camera is ALWAYS at standing human eye level (~160–170 cm). NEVER elevated, overhead, bird's-eye, or from tiered seating height. Describe explicitly: `"camera at standing human eye level"`. If the action_description says "from elevated seating" — ignore it; plant the camera at floor level among the people.

- **NPC direction — STRICT:** when NPCs are present in frame (scholars, guards, researchers), they MUST be fleeing AWAY from the camera — backs visible, running toward exits, moving in the SAME direction as the viewer. NEVER facing the camera or running toward it. Describe explicitly: `"backs to the camera, running ahead toward [exit/door/staircase]"`. NPCs running toward camera looks like they're charging the viewer and breaks the POV illusion completely.

- **Populate crowd scenes:** any scene where the action_description mentions "scholars flee", "guards run", "researchers scatter" — include 2–4 NPCs explicitly in the image_prompt with backs to camera. An empty scene in a mass-evacuation context looks wrong. Exception: undercroft stairwell and sealed-off dead-end scenes may be empty (isolation = horror).

- **Every POV `image_prompt` MUST end with:** `". Clean environmental first-person POV. NO hands, NO weapon barrels, NO controls in frame. NO on-screen text, NO HUD numbers, NO captions, NO UI labels, NO crosshair text, NO percentage counters."`
- General rules — `rules/roles/storyboarder.md`.

### Animator

**Architecture: one H3 Max I2V call per animated clip (5s each).** N animated clips → N calls; a still scene needs none. Simple, controllable, no chaining artifacts.

- All animated clips via the format's route, **MiniMax H3 Max I2V** (`minimax.h3max.i2v`), through `tools/kling_runner.py` (see `tools/examples/minimax-h3-max-scene-video.job.json`), with `expect.audio: "required"` and `scene_video_audio: "native"` written on every animated scene. Keep the model, endpoint, route, and serialized request fixed; retry once on failure, then stop the whole video. Never switch automatically to Kling v3 Standard, Kling 2.6 or a silent configuration.
- **Still scenes** (`motion: "still"`, normally only the title card): no paid job; render with `tools/still_shot.py` as `rules/roles/animator.md` describes (`scene_video_audio: "none"`).

**Call structure per animated clip (payload, exact field set):**
- `image_url` — Supabase URL of `scene-K.png` (Storyboarder uploaded it)
- `duration: 5` (number = `duration_sec`; H3 returns ~5.18s, which the Editor trims to plan)
- `resolution: "768P"`, `prompt_expansion_mode: "disabled"`
- `prompt` — motion description derived from `action_description`, ending with the closing clauses below
- Nothing else: H3 has no `negative_prompt`, `generate_audio`, `multi_prompt`, end frame or `shot_type`

**Title card motion (clip 0):**
- Very slow camera push-in toward the crisis. Atmospheric debris drifts and settles. Distant explosion flares and holds. Continuous verb tense throughout. As a still shot, the push-in is rendered by `tools/still_shot.py` instead (no SFX under it).

**POV clip motion (clips 1–N):**
- Every prompt starts with: `"Environmental first-person POV."` (style anchor)
- The motion text ends with an explicit endpoint verb: `dissipates`, `settles`, `clears`, `holds`, `pushes forward`; the closing clauses follow it
- No names, no moods, no hands, no weapon barrels, no protagonist body
- Prompt ≤512 serialized UTF-8 bytes (measure before submitting)

**Closing clauses on every call** (H3 has no `negative_prompt`; at most two short plain sentences at the end of `prompt`):
1. The sound clause, always: `No music, no voices.`
2. Optionally one more for the most important exclusion or style lock, e.g. `No hands or on-screen text.`, or one derived from the resolved `style_tags` (e.g. `Keeps the illustrated game style.` when the game is stylized). Do not hardcode anti-realism wording when the game's own style is photoreal.

**Banned phrases in prompts** (I2V models read them as freeze cues): `then settles`, `then steady`, `then holds`, `camera holds steady`, `hold position`, `no morphing`. Use continuous verbs + endpoint cues.

**Debug mode — full scenario table before ANY paid I2V call (MANDATORY):**
```
=== ANIMATOR DEBUG: {SITUATION} — per-clip I2V ===

Clip 0  title-card  /  PNG: scene-0.png  /  5s ≈ $0.41  (as a still: $0.00, {still_effect})
  prompt: "Slow camera push toward {crisis}, {debris} drifts and settles, distant explosion flares and holds. No music, no voices."

Clip 1  pov/hook    /  PNG: scene-1.png  /  5s ≈ $0.41  /  {pct}%
  prompt: "Environmental first-person POV. {endpoint verb}. No music, no voices."   (≤512 UTF-8 bytes)

Clip 2  pov/threat  /  PNG: scene-2.png  /  5s ≈ $0.41  /  {pct}%
  prompt: "Environmental first-person POV. {endpoint verb}. No music, no voices."   (≤512 UTF-8 bytes)

...

Clip N  pov/outcome /  PNG: scene-N.png  /  5s ≈ $0.41  /  {pct}%
  prompt: "Environmental first-person POV. {endpoint verb}. No music, no voices."   (≤512 UTF-8 bytes)

Total: {animated clips} × ~$0.41 + {still clips} × $0.00 = ${total}  (cap $6.30)
Proceed? (y/n)
```

**Per-clip output:** the runner downloads to `scenes/scene-K.mp4`; validate technically (filesize > 100KB, codec, audio stream present, ffprobe duration ~5s; H3 runs up to ~0.7s long). Do not inspect generated media semantically. A failed request gets one identical retry; a second failure stops the whole video.

Polling: done by `tools/kling_runner.py` against the route's poll base in `tools/video_routes.json` (H3 Max: `https://queue.fal.run/minimax/h3-max`); never poll by hand.

**Pricing:** ~$0.41 per animated 5s clip ($0.08/s on the returned length); a still scene costs $0.00. Base (title card + 5 POV = 6 clips) ≈ **$2.46** of video, ~$2.05 with a still title card (well within $6.30 cap). A separately authorized silent configuration is a new stopped-run decision, never an automatic fallback.

### Sound

- **TTS route:** follow `rules/roles/sound.md`.
  - Default narrator route: MiniMax (`fal-ai/minimax/speech-2.8-hd`).
  - Chatterbox is allowed only with an approved sample owned by the exact `in-game-pov` story bible; split long Chatterbox narration into safe chunks as required by Sound.
  - ElevenLabs TTS and cross-format voice lookup are forbidden. Keep one voice intent for the whole video.
  - Save locally and upload only when a downstream stage needs a permanent run-scoped URL.
- **Subtitles:** NOT Sound's job. One universal style, generated by Editor via whisper from `build/voice-final.wav` (see `rules/roles/editor.md` §6). No `--style`/`--chunk`/`--text`/`--offset`/`--atempo`.
- **Speed control:** if TTS duration > POV-clips timeline, Editor applies `atempo` (cap 1.4×). Subtitles are computed from the already sped-up speech — nothing to recompute. If mismatch > 40% → back to Scenarist to shorten.
- **Music:** generated via MiniMax with a `tense`/`drama` `style` prompt (instrumental, see `rules/roles/sound.md` §6), `volume` from storyboard (default 0.12). Never fun/upbeat. Music starts from t=0 (over the title card and through the whole video).
- General rules — `rules/roles/sound.md`.

### Editor

Three-stage assembly (HUD drawtext per-clip before concat, then subtitles, then final audio mix).

**Stage 0 — graphic overlays (per-clip, BEFORE concat):** drawn by `tools/overlays.py` from
`clips[].overlays[]` (NOT manual drawtext, do NOT bake into NB2). For each clip K:
```bash
FRAG=$(python3 tools/overlays.py storyboard.json --scene-index $K --workdir build \
         --input-label "[v${K}pre]" --output-label "[v${K}]")
# FRAG is spliced into filter_complex between scale/crop/setsar/fps and concat (editor.md §6.5)
# portrait scene clips (H3, still): scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1
```
- Positions/style come from `overlays[]` written by the scenarist (see the `## Overlays` table):
  title card — two lines fs130 white (y680/840) + hook_plate fs60 red (y1030); HUD counter —
  top-right fs52 white with outline (no time-range `enable` needed — each clip is 5s); outcome plate —
  center fs110 green/red, `enable:["gte",3.5]`.
- overlays.py resolves fonts (FONTS map, fallbacks) — no hardcoded paths. `%` is handled
  via `expansion=none` (automatically). Before the encode — `overlays.py storyboard.json --check`.
- Overlays — ONLY via overlays.py; never ask NB2 or the I2V model to draw HUD/numbers/text.

**Stage 1 — Picture-only concat:**
- Normalize each HUD'd clip: fill-and-crop to 1080×1920 ending in `,setsar=1` (as above), 30fps, `preset slow`, `crf 20`. I2V clips arrive at 24fps (H3 and Kling) → normalize to 30fps before concat. H3 clips (`scene_video_route` starting with `minimax.`) are trimmed to `duration_sec`; still clips are already exact (`rules/roles/editor.md`).
- Hard cuts, no crossfade.
- Concat-list entries: `scene-0-hud.mp4` + `scene-1-hud.mp4` + … + `scene-N-hud.mp4`. No duplicates.
- Output: `build/concat-noaudio.mp4` (silent; CTA NOT yet appended).
- `MAIN_DUR` = (N+1) × 5s (played lengths: H3 clips trimmed to plan, stills exact). `TTS_OFFSET = 0` because title-card narration is mandatory.

**Stage 2 — Subtitle burn-in:** the canonical path, editor.md §6 — `python3 tools/add_subtitles.py build/voice-final.wav build/subs.ass --storyboard storyboard.json --lang {lang} --main-dur {MAIN_DUR}`, then `ass=build/subs.ass` as the last video filter. TTS starts at 0, so `--offset` is not needed.

**Stage 3 — Final audio mix (one ffmpeg pass):**
- Inputs: `build/concat-subbed.mp4` + `tts-output.mp3` + clip SFX (each clip's own audio — preserve it for scenes with `scene_video_audio: "native"`, trimmed like its picture: `atrim=end=<duration_sec>,asetpts=PTS-STARTPTS` for H3 clips, so the bed stays in sync; a `"none"` or still scene gets an `anullsrc` slot of its played length) + music + `cta-scaled.mp4`.
- **Audio levels:** narrator TTS = 1.0 (front), clip combat SFX = ~0.30 (bed), music = `music.volume` (~0.12). Mix all three over MAIN_DUR.
- TTS starts at the beginning of the mix with `TTS_OFFSET = 0`; do not add title-card lead silence.
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
│   ├── scene-0.mp4              (H3 I2V title card, 5s, own SFX — or a silent still-shot clip)
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

Generated PNG/MP4/audio receives technical validation only (path, size, hash, dimensions, codec, duration, schema). The semantic checklist items below are prompt/schema requirements and user-review criteria, not authorization for AI Vision, frame sampling, or machine visual/audio interpretation.

- [ ] `format: "in-game-pov"` in storyboard.json
- [ ] `outcome` set to `survive` or `death` (the value the Manager asked the user for)
- [ ] Story bible checked — situation is NOT a repeat of any `used_situations[]` entry (different threat type, premise, core scenario)
- [ ] All narration is **second person, present tense** — no first-person, no past tense
- [ ] `tts.full_text` ≤ 67 words total (count before passing to Sound)
- [ ] Last POV clip `tts_segment` ends with `"You died."` (death) or `"You survived."` (survive) — always EN
- [ ] `clips[0].clip_type: "title_card"` — mandatory `tts_segment` voices the displayed situation title + starting survival %, with a wide cinematic `action_description`
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
- [ ] Animated clips use `minimax.h3max.i2v` with `scene_video_audio: "native"`; every prompt ends with `No music, no voices.` (H3 has no `negative_prompt`); at most one further closing clause
- [ ] Every animated clip has an audio stream (`expect.audio: "required"`); validate it technically. If the user rejects its content, stop for an explicitly authorized rerun configuration.
- [ ] Still scenes (if any, normally only the title card): `scene_video_kind: "still"`, `scene_video_audio: "none"`, within the `rules/roles/scenarist.md` "Still shots" cap
- [ ] Audio mix: narrator 1.0, clip SFX ~0.30, music ~0.12; TTS starts at 0 on the title card
- [ ] Every animated clip has an active camera move in the motion_prompt (no "holds steady") — endpoint verb present; a still's `still_effect` counts as its camera move
- [ ] Every motion_prompt starts with `"Environmental first-person POV."` for clips 1–N; title card uses slow push-in
- [ ] TTS via MiniMax, or Chatterbox only with an approved exact-format sample; no ElevenLabs TTS or cross-format sample
- [ ] Subtitles — universal whisper style (editor.md §6); clip 0 has mandatory `tts_segment`; `TTS_OFFSET = 0`
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
- ❌ Baking the `SURVIVAL %`, outcome plate, or any HUD into NB2 or the I2V clip — Editor drawtext ONLY
- ❌ Static survival % (must move per clip — it's the retention hook)
- ❌ Final % / outcome plate contradicting the locked `outcome` field
- ❌ **Warning plates** (center-screen overlays like `⚠ HULL BREACH`) — they look artificial and are removed from this format
- ❌ Automatically switching a POV clip from clip sound (`scene_video_audio: "native"`) to silent, or to another route, after failure or semantic rejection
- ❌ Dropping the clips' own SFX track in the mix (it's the immersion bed — keep at ~0.30)
- ❌ A prompt without the closing sound clause `No music, no voices.`
- ❌ Moving narrator subtitles up into the HUD zone (HUD top-right, subs lower third)
- ❌ Silent title card or a missing clip-0 `tts_segment` — the displayed situation title and starting survival % must be voiced from t=0
- ❌ **Duplicate scene in concat-list** — a freeze-extended scene REPLACES its entry; never append it as a second entry
- ❌ Character-face ref or prop-ref without explicit Scenarist justification
- ❌ End-frame PNGs or any end frame (`tail_image_url` on Kling; H3 takes none) — causes freeze artifacts
- ❌ "Camera holds steady" / "then settles" / "then steady" / "hold position" / "no morphing" in any prompt (read as freeze cues)
- ❌ **multi_prompt / pov_multi_prompt / shot chaining** — this format uses one 5s I2V call per clip (H3 has no `multi_prompt`); multi-shot prompting produces uncontrolled transitions and location drift across shots
- ❌ Bridge frame extraction or start-image chaining between clips — each clip uses its own independently generated NB2 PNG as start frame
- ❌ Missing style anchor `"Environmental first-person POV."` in any clip 1–N prompt — shots drift to the model's generic realistic prior
- ❌ Prompt >512 serialized UTF-8 bytes — the format's limit (on Kling it fails only after the submit round-trip)
- ❌ Skipping debug-mode scenario table — launch without it = no user visibility on per-clip timing/cost before spending ~$1.26+
- ❌ Music from `Fun/` (wrong mood — use tense/drama)
- ❌ Burning ASS subtitles with stock ffmpeg (lacks libass — use ffmpeg-full)
- ❌ `-shortest` in any ffmpeg call (use `apad`)
- ❌ **Choosing a situation already in the story bible** — always read `in-game-pov_story_bible.json` first; repeating threat type or core premise counts as a violation even if the title differs (e.g. "Borg cube" and "Borg boarding" are the same threat type)
- ❌ Not updating the story bible after publishing — every completed (or errored) run must be logged so the next Scenarist has accurate anti_repetition data
