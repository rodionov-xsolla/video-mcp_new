---
ready_to_post: yes
subtitles: true
overlays: false
---

# Format "Serial Drama" — serial micro-dramas

Serial micro-dramas with brainrot aesthetic and an endless plot. Each episode = 40–45 seconds, **max 6 clips**, cliffhanger at the end.

This file is the **playbook**: when to use, concept, budget, series state (story bible), role briefs. Craft rules — in `rules/roles/*.md`.

---

## When to use

Keywords: "serial", "episode", "series", "ep1", "ep2", "сериал", or `series_id` of an existing series is provided.

---

## Concept

- **Genre:** endless micro-dramas with brainrot aesthetic, cliffhangers, plot loops
- **Style:** read from the resolved style chain — story bible top-level `style_tags` (the series' canonical look), else game config `prompt_prefix`. This file does not hardcode a render medium; the scenarist resolves the chain into `visual_identity.style_tags` and the storyboarder applies it verbatim to every `image_prompt`. Preserve the exact proportions of locked character cards (cards carry appearance only — style comes solely from `style_tags`).
- **Duration:** 40–45s (**max 6 clips** × 5–10s). Hard cap — Scenarist must not exceed 6 scenes. EP2 had 8 scenes = $8.42, target is ≤$6 per episode.
- **Budget:** up to $7 per episode. Stop if spend > $6.50. Each dialogue I2V clip costs ~$0.63–1.26 — 6 clips max keeps you under budget.
- **Frame format:** 9:16 (608×1080) for all scenes. Square forbidden.

### Clip mix (balances)

- **ACTION/DIALOGUE ~ 50/50.** All-dialogue episode = monotonous; all-action = no plot.
- **I2V only.** Every serial-drama clip, including dialogue, is Kling v3 Standard I2V. Retry a technically failed request once with the same endpoint/settings; a second failure stops the video with an error. No v2.6, provider, or local fallback.
- **Dialogue I2V uses Kling voice support:** `generate_audio: true`, `voice_ids`, `shot_type: "customize"`, and `multi_prompt` with `<<<voice_1>>>` / `<<<voice_2>>>`.
- **Kling Avatar v2 is forbidden for serial-drama.** Do not create Avatar refs, do not call `fal-ai/kling-video/ai-avatar/*`, and do not render dialogue as a separate lipsync avatar clip.
- **Identity is physical, not nominal.** Kling/NB2 do not know character names. Every scene prompt and every `multi_prompt` shot must identify visible/speaking characters by their locked physical descriptors and attached refs.
- **When a scene chains 2+ character reference images, explicitly bind each reference to its position/role in the prompt** (e.g. "the reference image showing a male Fatui Harbinger is the figure standing center-left; the reference image showing a female Traveler is the smaller figure in the background"), in addition to the normal descriptive prose. This is a cheap, low-risk mitigation, not a confirmed fix: a controlled reproducibility test (genshin-dont-save-me-en EP7, 2026-07-21) re-ran a byte-identical prompt+refs twice and got a correct single-instance result once and a duplicated background character (two instances of the same secondary character) once — proving that this kind of duplication can be pure generation-to-generation randomness, not something the prompt structure alone fully controls. Tightening ref-to-role binding costs nothing and may lower the odds, but do not treat a recurrence as proof the binding was missing or wrong.
- **The story bible's `character_description` field itself must never lead with a name/rank+name** (e.g. "Captain James T. Kirk" or "Chief Engineer Montgomery Scott") — every sub-agent copies this field verbatim into prompts, so a name baked in here propagates into every episode's `image_prompt`/`motion_prompt` regardless of how careful Scenarist/Storyboarder/Animator are downstream. Write it as role/species + physical descriptors only (e.g. "Male Starfleet captain, athletic build..."). Burned in EP13 (2026-07-14, star-trek-airlock): both Kirk and Mirror Kirk's bible descriptions started with "James T. Kirk", which combined with a `multi_prompt` shot that dropped mid-frame characters from its text caused Kling to hallucinate a duplicate Kirk face in scene 6 — the two twin-faced characters gave the model an easy "safe" duplicate to fall back on. Spoken dialogue lines (`character_speech`) may still contain names naturally (characters address each other by name) — this rule is about the visual/descriptive identification text only.

---

## Budget (rough estimates)

| Component | 5s clip | 10s clip |
|---|---|---|
| Image (NB2) | $0.08 | $0.08 |
| Kling v3 Standard I2V, no audio ($0.084/s) | $0.42 | $0.84 |
| Kling v3 Standard I2V with generated dialogue/audio ($0.126/s) | $0.63 | $1.26 |
| MiniMax / local TTS | not used for serial-drama dialogue |
| Kling Avatar v2 | forbidden |
| **I2V action clip** | **~$0.50–0.63** | **~$0.92–1.26** |
| **I2V dialogue clip** | **~$0.63** | **~$1.26** |

| Variant | Clips | Cost |
|---|---|---|
| Base (recommended) | 5 × 5s | ~$2.00–3.00 |
| Extended | 6–7 × 5s | ~$2.50–4.00 |
| Exception (undividable monologue) | 4×5s + 1×10s | ~$2.80–3.80 |

⚠️ **Dynamics > savings.** 2×5s almost always beats 1×10s. Angle change / counterpart reaction matters more than $0.04 saved.

When reporting actual spend, calculate from rendered seconds, model rates, regenerations, and any burn tests; do not reuse the rough estimate after generation.

---

## Episode structure (narrative)

| Phase | Timing | Goal | Clips |
|---|---|---|---|
| **HOOK** | 0–5s | Spoken hook line / gag / engaging moment. Stop the scroll | 1 clip (5s, DIALOGUE/I2V) |
| **TITLE CARD** | after HOOK | Series overlay card | interstitial, not a scene |
| **CLIMAX** | 5–30s | Dialogue, confrontation, rising tempo | 2–3 clips (5–10s each) |
| **CLIFFHANGER** | last 5s | Cut at the peak. Shock, reveal, mid-sentence stop | 1 clip (5s, ACTION/I2V) |

**Scene 1 (HOOK) is always a dialogue clip carrying a spoken line/gag/engaging moment — never a silent action beat.** A silent hook (pure action, no line) reads as a slow establishing shot, not a scroll-stopper. This is Scenarist's job: write scene 1 as `clip_type: "dialogue"` with a punchy opening line, same convention as EP1–3's cold opens ("You're backup. Not competition." etc.).

**Two valid title-card TYPES — the exact type is a per-series choice, locked in that series' story bible (`production_rules` or a dedicated `title_card` field), not a format-wide default:**
1. **`png` type** — a locked branded overlay image at `games/{GAME_TAG}/overlay-series.png` (e.g. star-trek-airlock, ROOM 1701), composited via ffmpeg per the Storyboarder/Editor spec below.
2. **`text` type** — a dynamic drawtext card rendered fresh per episode from the episode's own number/title (e.g. "EPISODE 7" + "Golden House Again", Montserrat-Black, white text on a semi-transparent box, top of frame), no locked image asset needed. Confirmed convention for genshin-dont-save-me-en starting EP7 (2026-07-21): line 1 "EPISODE {N}" fontsize ~64 at y≈120, line 2 the episode title fontsize ~40 at y≈210, both centered horizontally with a black@0.45 box behind, via `ffmpeg-full` (`fontfile=`, not fontconfig) — see that series' story bible for the exact styling to reuse on every future episode once a series adopts this type.
A series' story bible must declare which type it uses; do not assume `png` by default just because that was the first-built convention — check the bible before generating anything.

**Title card placement — fixed convention, not an overlay-on-scene-2 default — applies to EITHER type above.** The order is always: **HOOK (scene 1) → TITLE CARD → rest of the episode (scene 2 onward)**. The title card must NEVER overlap a scene window that has active `character_speech` — it buries the dialogue and its subtitles (burned in ROOM 1701 EP4, 2026-07-10: title card window defaulted to `after_scene_1` starting exactly at scene 2's t=0, and scene 2 is dialogue from frame 1 — the "FREE DOWNLOAD / LINK IN BIO" card sat directly over Michael/Alex's faces and subtitle text for the first 5s of their conversation). Two valid placements, in order of preference:
1. **Within scene 1's own runtime**, if scene 1's hook line finishes with room to spare before the clip ends (e.g. line lands in the first 2–3s, last 2s is a silent reaction beat) — overlay the title card over that trailing silent portion only.
2. **As a short freeze-frame interstitial** immediately after scene 1's last frame (hold scene 1's final frame ~1.5–2s, title card fades in/out over the hold), inserted as its own beat before scene 2 starts. This adds to total runtime and is NOT counted against the 6-scene cap — it is not a scene, it is a title-card interstitial. Use this whenever scene 1's dialogue runs to the very end of the clip (no natural silent tail to overlay onto).
Never default the title card window to the start of scene 2 (or any other dialogue scene) just because scene 1 "ran out of room" — check the actual scene 1 audio/dialogue timing before picking the window.

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
- ❌ Static talking heads. Dialogue should be staged as two-shots, over-shoulders, reaction beats, or multi-shot I2V, not Avatar bust shots.

### Brainrot vocabulary

Appropriate in dialogue: `rizz`, `sigma`, `cooked`, `negative aura`, `bro`, `no cap`, `NPC behavior`, `delulu`. In moderation, not in every line. Not in the narrator.

### Duration — 5s by default

- Any line ≤15 words → **5s**
- Any action/reaction → **5s**
- 10s dialogue clip = **almost always a mistake** (a static head for 10 seconds = death of dynamics). Split into 2×5s with different angles.
- 10s clip requires `duration_reason` in storyboard.json.

#### Dialogue runtime planning

Serial-drama dialogue is I2V, so `duration_sec` is the actual rendered clip length. Plan runtime from the storyboard durations:

- Dialogue I2V target length is **6–10s**. Go longer only with explicit `duration_reason` and budget check.
- `multi_prompt` shot duration is not fixed. Default 2–3s per shot; 4s only when the phrase or acting beat genuinely needs it.
- Estimate spoken timing before generation: `speech_seconds = word_count / words_per_second`. Default pace is ~2.4 words/sec; relaxed/sarcastic lines can be slower, tension/mission-rant beats can be faster. Avoid accidentally cramming too many words into a short shot.
- Add acting/pause padding when needed: +0.2s for a simple line, +0.4–0.7s for pause/comma/reaction, +0.8–1.2s for prop handoff or physical beat.
- One Kling dialogue request can use at most 2 `voice_ids`. The series/story bible may have 3+ reusable character voices, but each request remaps only the voices used in that clip to local `<<<voice_1>>>` / `<<<voice_2>>>` tags. If a scene needs 3 speaking characters in the same moment, split the scene into multiple clips.
- Prompt text per shot must stay ≤512 characters.
- The physical descriptor immediately before each `<<<voice_N>>>` must match `voice_ids[N-1]`.
- Any spoken line in a dialogue I2V clip must have `generate_audio: true`, `voice_ids`, and a matching `<<<voice_N>>>` tag. A dialogue clip rendered without voice is a failed request, not an acceptable silent beat.
- Never pad a clip with a frozen frame; the I2V duration is the duration.

---

## Diegetic product placement (in-scene banners/posters)

When the user asks for a native promo element (e.g. "free primogems banner", "poster in the background") worked into 2-3 scenes:

- **Never let the placement request override locked scene continuity/location.** State the banner/poster requirement as a PROP to fit into whatever location the locked beats/prior episode already put the characters in — do not describe it as belonging to a specific setting (e.g. "market banner", "street signage") if that setting isn't where the scene is actually happening. Burned in genshin-impact "Don't Save Me" EP5 (2026-07-10): the Manager's own brief to Scenarist said "market banner/flag... market stall signage", which combined with "pick whatever location fits" latitude, made Scenarist invent an entire market-street setting and move 4 scenes out of the locked teahouse continuity — an unforced, confusing location jump the viewer couldn't parse ("as in, they moved? how?"). The fix cost a full re-render of 4 scenes (~$3.20) that a correctly-scoped brief would have avoided.
- **When the locked location doesn't naturally fit the banner's real-world placement** (e.g. a promo banner is naturally an outdoor market fixture, but the scene is indoors), have it glimpsed through a window/open door frame from inside the locked location, rather than moving the characters outside. This satisfies "native in-world prop" without touching location/continuity.
- **Escalate legibility gradually across the 2-3 scenes**, not instantly large in scene 1 — e.g. small/distant in the first scene it appears, clearer in the second, largest/most legible in the third (the scene where the camera is naturally closest to it).
- **Banner text must fit fully in frame — verify against both crop AND occlusion.** NB2 can crop long banner text at the frame edges (state explicit width/positioning: "short banner, NOT spanning pole-to-pole, fully contained with margin on both sides") AND can let a character's raised arm/head cross in front of it (state explicit blocking: character's arms/head must stay below the banner's vertical band). Two different failure modes, both need explicit prompt language — fixing one does not fix the other.
- **Character costume lock reinforcement for dramatic close shots.** A close/dramatic framing instruction (e.g. "leaning in, urgent whisper") can make NB2 drift a locked character into an invented costume (armor/cape/accessories not in their card) even when the correct reference sheet is attached and the prompt text is otherwise correct — this is a generation-fidelity miss, not a prompt-writing bug. For any dramatic/intense close shot, add an explicit corrective clause naming what NOT to add (e.g. "standard uniform only — no armor, no cape, no pendant, no mask") in addition to the normal locked `prompt_descriptor`.

---

## Story Bible — persistent series state

The exact manager-resolved `STORY_BIBLE_PATH` stores the universe state between episodes. **Mandatory** for serial-drama. Never replace it with a hardcoded `games/{GAME_TAG}/serial-drama_story_bible.json`; this is especially important for Star Trek ROOM 1701, which must resolve to `games/star-trek-timelines/room1701_story_bible.json`.

### Structure

```json
{
  "series_id": "roblox-noob-revenge",
  "game_tag": "Roblox",
  "title": "The Noob Who Was a Secret Millionaire",
  "style_tags": "the series' canonical look, resolved once and applied verbatim to every image_prompt...",
  "created_at": "2026-03-27",
  "last_episode": 0,

  "characters": [
    {
      "name": "Noob Dave",
      "role": "protagonist",
      "character_description": "Roblox-style blocky humanoid, bright yellow smooth plastic skin, simple blue torso shirt, bright green pants, round head with wide innocent eyes, small curved mouth, matte plastic texture",
      "voice": "Casual_Guy",
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

1. Load the story bible from the exact `STORY_BIBLE_PATH` passed by Manager. If it is absent, invalid, or ambiguous, STOP and ask the user whether to create/select one; never silently use the generic default.
2. Analyze: who is in what status, which loops are active, what is the aura level
3. Run Anti-Repetition Check (see below)
4. Decide what happens in this episode (Loop Management)

### State Transition (only after explicit final user approval, Manager updates)

Do not mutate series state when generation or Editor finishes. Present the final video first; apply the following transition only after the user explicitly approves it.

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
- **Dialogue clips are I2V `multi_prompt`, not Avatar.** Stage them as medium two-shots, over-shoulders, group reactions, and insert beats. Avoid static frontal bust shots.
- Balance ACTION/DIALOGUE ~ 50/50; at least 2 different characters speak per episode
- Read the exact resolved series bible: characters, format-owned native voice refs/IDs (`voice_ref_url` / `voice_id_kling`), active loops, anti-repetition
- **`retention_strategy` mandatory** in storyboard — why the cliffhanger pulls the next episode
- Brainrot vocabulary in moderation, dialogue only
- camera_angle differs for every adjacent clip
- **NO title cards / brainrot tags / character names overlays** — only dialogue subtitles + TBC
- General script rules — `rules/roles/scenarist.md`

**MANDATORY YouTube metadata** — Scenarist MUST write these top-level fields in storyboard.json (Manager cannot publish without them):

```json
"title":        "{series_title} — EP {N}: {episode_title} | {Game Name}",
"description":  "{1-2 sentence hook describing the episode cliffhanger}\n\n{series_title} — EP {N} of {total}\n\n#{GameTag} #{Character1} #{Character2} #Shorts",
"youtube_tags": ["{Game Name}", "{Character1}", "{Character2}", "serial drama", "{series_title}", "Shorts", "anime", "{game} shorts", "{episode_title}"],
"thumbnail_url": ""
```

Convention examples (series "Don't Save Me", Genshin Impact):
- `title`: `"Don't Save Me — EP 2: Leave Liyue | Genshin Impact"`
- `description`: first line = cliffhanger hook (≤120 chars), then blank line, then series credit, then hashtags
- `youtube_tags`: 8–12 tags, mix broad (`Genshin Impact`, `Shorts`) + specific (`Childe`, `Leave Liyue`, `Fatui`)
- `thumbnail_url`: leave empty string — Manager fills it after extracting frame from the cliffhanger scene

### Storyboarder

- Style comes from the resolved style chain (story bible top-level `style_tags` → game config `prompt_prefix`) and is applied verbatim to every `image_prompt`. Do not introduce any render-medium terms that are not already in the locked `style_tags` string.
- All frames 9:16 (608×1080) — square forbidden

#### image_prompt template (EP1 gold standard — follow this structure for every scene)

```
[STYLE PREFIX — the exact resolved `style_tags` string from the story bible, copied verbatim],
[PRIMARY CHAR — full physical description + SPECIFIC POSE/ACTION in this scene],
[SECONDARY CHAR — full physical description, shown shoulders-up only, facing direction, action],
[TERTIARY CHAR if present — shown shoulders-up only, STRONGLY out of focus blurred background [position], action],
[ENVIRONMENT — tight, specific relevant details matching the bg-ref],
[SHOT TYPE — close medium two-shot / medium three-shot / etc.],
vertical 9:16 frame, no text overlays, keep facial features exactly matching the uploaded reference images
```

**Critical rules for this template:**
- **Primary char** = the speaker or hero of this beat. Full description + what they are physically DOING (pose, gesture, expression). Not just appearance — specific action: `"leaning in toward Michael with urgent whisper expression, shoulders raised, chin tucked"` not `"nervous energy"`.
- **Secondary chars** = always `"shown shoulders-up only [left/right of frame]"`. Never describe their full body unless they are equally prominent. Describe their specific action too.
- **Background/blurred chars** = add `"STRONGLY out of focus blurred background [far left/right]"` in CAPS so NB2 treats it as instruction, not description. Include their char sheet in `image_urls` anyway — the sheet anchors their face even when blurred.
- **Color specificity** = use emphatic exact names for distinctive costume items: `"bright YELLOW-GOLD hoodie"` not `"yellow hoodie"`. Ambiguous color = wrong render.
- **Environment** = describe tightly — what is immediately around the characters, not the whole room. Match the bg-ref depth: if the bg-ref shows a tight medium shot of the coffee bar, describe `"coffee bar edge and espresso machine visible close in background"`, not `"coffee shop interior"`.

#### image_urls order and rules

```json
"image_urls": [
  "<location-bg-ref>",       // ALWAYS first — environment anchor
  "<primary-char-sheet>",    // speaking/hero character
  "<secondary-char-sheet>",  // second visible character
  "<tertiary-char-sheet>"    // third visible character (if any, max 4 total)
]
```

- **ALL visible/speaking character sheets are mandatory** — even for chars who are blurred background. Their sheet anchors the face even at low prominence. Missing a sheet = face drifts or character looks generic.
- **NEVER include a cross-episode scene image as a ref.** A previous episode's room photo (e.g. `room1701-ep1-last-scene.png`) will bleed its location (bedroom furniture, colors) into the new scene. EP2 attempt 2 used the EP1 last scene as anchor → bedroom elements appeared in the coffee shop. Only use character sheets + location bg-ref.
- **Reusing the same location bg-ref across two DIFFERENT scenes in the same episode (not a `continues_from_scene` pair) risks Kling hallucinating an extra background person during I2V motion**, especially near a door/threshold/off-frame edge. Burned in EP13 star-trek-airlock (2026-07-14): scene 3 and scene 4 both chained off `bridge-tactical-ep13.png` with similar framing — across two separate render attempts, Kling invented a random extra character near the turbolift door during the I2V camera motion, not present in either scene's static start-frame prompt. This is distinct from the cross-episode bleed rule above (same episode, same format, still wrong): when two scenes in one episode are NOT declared continuations of each other (no `continues_from_scene` link) but would otherwise reuse the identical location bg-ref and near-identical camera framing, generate a genuinely fresh location bg-ref for one of them instead — a different angle/composition is not sufficient on its own to fix this once it's happened, a fresh underlying location asset is the reliable fix.
- **Each scene is independent by default** — no ref chaining between scenes. Each NB2 call gets a fresh set of refs: location ref + relevant char sheets for that scene. Do not pass a previous scene's output as input to the next.
- **EXCEPTION — blocking continuity for a continuous physical sequence within ONE episode.** When 2+ consecutive scenes are staged as one continuous physical moment in the same location (characters moving/repositioning across scenes — someone crosses the room, a third character enters and walks toward the others, etc.), generating each scene's start frame independently from text alone causes characters to visually "teleport" between clips — position, distance, and even who's still in frame can jump discontinuously. Burned in genshin-impact "Don't Save Me" EP4 (2026-07-07, scenes 4→5→6): a wound-tending exchange, a doorway confrontation, and a cliffhanger stand-off across 3 consecutive scenes in the same teahouse produced 3 unrelated spatial arrangements — caught only on user review. Room 1701's sitcom blocking (characters mostly seated, small movements) doesn't trigger this as visibly; any format/series with continuous cross-scene action will. **Fix:** Scenarist sets `"continues_from_scene": N` on a clip when it's staged as a direct spatial continuation of clip N (same location, same continuous moment, characters mid-repositioning) — omit/null when a scene is a clean new beat. Storyboarder reads this field: when set, it adds the immediately-preceding scene's PNG (same episode, one scene back only — never cross-episode, never more than one scene back) as an EXTRA chain-ref alongside the location bg-ref, and explicitly describes the new scene's blocking as a continuation of the previous scene's declared end-state/blocking metadata. Never inspect the rendered MP4 or extract its last frame automatically; generated media receives technical validation only. This still respects the bg-ref-first / no-cross-episode-bleed rules — it only adds a positional anchor, not a new location source.
  - For a tight `continues_from_scene` link, use the immediately preceding same-episode start PNG plus the declared end-state/blocking metadata. Do not extract or inspect frames from the rendered MP4 automatically; any visual continuity judgment is the user's during debug.
  - **⚠️ The extra chain-ref does NOT substitute for a fresh location bg-ref when the text describes REAL spatial repositioning (walking to a different wall, turning a corner, advancing down a corridor/dock).** Burned in genshin-impact "Don't Save Me" EP6 (2026-07-14): scenes 1→2 (running further down a dock) and scenes 3→4→5 (character steps to a side wall, then the other closes the distance) all reused the SAME location bg-ref file across the whole chain, with only the text and the continuation-PNG anchor describing the movement. Result: every cut looked like teleportation — running scene 2 showed the exact same framing as scene 1 (no sense of having covered distance), and the alcove scenes never actually showed a side wall despite the text repeatedly saying characters moved to one, because the underlying bg-ref photo was identical every time and NB2/Kling anchor heavily on the literal pixels of the location image, not just the text describing where people now stand in it. **Rule: if the blocking description says a character reaches a new vantage point (turns a corner, crosses to a different wall/landmark, advances a visible distance), generate a genuinely NEW location bg-ref for that vantage point** — a fresh NB2 generation (can be an `/edit` chained off the original bg-ref for style/architecture consistency, e.g. "same corridor, seen from further down / rotated to show the side wall") — not just a text instruction layered on the identical unchanged photo. Reserve the "text + continuation-PNG only" version of this exception for blocking that stays in essentially the same framing (a small step, a turn of the head, a hand reaching out) — anything that covers visible ground needs its own generated background.
  - **⚠️ Even a genuinely fresh bg-ref per vantage point can still fail — two independently-generated "same room, different angle" images rarely read as connected, and characters can flip left/right across the cut (crossing the 180-degree line), which looks like a place-swap, not dynamism.** This is what actually happened in the EP6 retry: a purpose-built "side wall" bg-ref for scenes 4-5 didn't visually connect to scene 3's door, and the characters' screen-left/right positions weren't held constant across the three scenes. **When a multi-beat exchange needs to happen in ONE location across several key_lines, prefer merging it into a SINGLE `multi_prompt` I2V clip (one start frame, several sequential shots) over splitting it into separate independently-generated scenes** — this sidesteps the whole problem, since there is no cut between independently-generated backgrounds, just continuous camera motion from one anchor. Kling's multi_prompt hard cap (≤15s, ≤6 shots per call) is usually enough for a 3-4 line exchange. Only fall back to separate scenes with fresh bg-refs when the exchange genuinely can't fit those caps, and if you do, fix each character's screen-left/right position for the ENTIRE sequence and never let it flip.
  - **⚠️ When a scene shows a character running/approaching TOWARD a destination visible in-frame, they must be oriented toward it (e.g. back-to-camera, angled toward the landmark) — not sprinting toward the camera with the destination as passive backdrop.** Burned in the same EP6 pursuit scene: the characters were composed running straight at the viewer while the door they were supposedly fleeing toward sat behind them, unrelated to their direction of motion — visually incoherent once cut against the arrival scene. Also: **that destination landmark's bg-ref must be generated as an `/edit` descendant of the SAME bg-ref asset used in the scene where they actually arrive there**, not independently re-generated as a "similar-looking" building — two separate NB2 calls describing "a Golden House entrance" will not produce the same door, and cutting between them reads as two different buildings.
- **bg-ref must be a TIGHT MEDIUM SHOT** — not a wide establishing shot. Wide bg-refs make characters appear tiny and child-proportioned. EP2: wide coffee-spot refs caused this; regenerating as tight medium shots fixed it. If a new location has no saved bg-ref, generate it as a tight medium shot first.
- **No style-conflicting source refs.** An asset whose visual style differs from the resolved `style_tags` biases the render toward that other style; a text negative does NOT override a style-conflicting source image (e.g. a `photoreal` / `live-action` asset pulls toward realism regardless of `"not photorealistic"` in the prompt).
- **`nb2.edit` inherits the base image's existing geometry/scale — it does not recompute the scene.** Chaining `nb2.edit` off a location bg-ref that itself has broken proportions (e.g. a console-only shot with no chair, no person, filling most of the frame) forces the model to fit any newly-requested object (a chair, standing/seated characters) into that already-wrong geometry rather than generating correct scale from scratch — no amount of text description fixes this, the same way a style-conflicting source image beats a text negative (rule above). Burned in star-trek-airlock EP14 (2026-07-21): scenes 1/2/4 were all generated via `nb2.edit` chained directly off `bridge-weapons-ep13.png`/`bridge-tactical-ep13.png` (console filling the frame, no chair, no human), and the console rendered torso-height in every one of them. **Fix:** when a scene needs an object or amount of open floor space that the existing bg-ref doesn't already show at correct scale (e.g. adding a chair to a console-only shot), generate the scene via `nb2.text` (fresh generation from character refs + text, no broken base to inherit from) instead of editing onto the flawed asset. Reserve `nb2.edit` for cases where the base image's own geometry is already correct and only a smaller local change is needed.

#### General storyboarder rules
- I2V clips: **start frame only** (`scene-K.png`). End frames are NEVER generated. `end_image_url` is FORBIDDEN with `multi_prompt` (Kling returns 422).
- Each clip = its own scene PNG (not the ref directly)
- General rules — `rules/roles/storyboarder.md`

### Animator

- I2V clips via Kling v3 Standard — micro motion only. Retry one technically failed request once with the same endpoint/settings, then STOP; never switch to v2.6 or another provider.
  - **Dialogue I2V:** `generate_audio: true`, `shot_type: "customize"`, `voice_ids`, `multi_prompt`. No external TTS, no Avatar.
  - **Action I2V:** `generate_audio: true` when room tone/ambient helps; `false` only for purely visual shots.
- Motion prompt = technical (positions, camera, physical actions), without names/moods
- One I2V model for the whole episode — do not mix Kling I2V versions within one episode
- Start frame only for I2V; Kling animates from the start frame via `motion_prompt`
- **Style-hold for this format (not universal — lives here, not in `animator.md`):**
  - **Anti-drift negative in EVERY I2V clip**, not selectively. DERIVE the negative from the resolved `style_tags`: it must push away from whatever the locked style is NOT (e.g. if `style_tags` is a stylized/animated look, the negative pushes away from photoreal — `photorealistic, film grain, realistic skin, live action, photograph`). Do not hardcode a fixed medium here; build the negative from the style the bible actually declares. EP6 scene 2 omitted it and the close-up drifted; scenes 7/8 that had it held better.
  - **Carry the style anchor into EVERY shot of a `multi_prompt`**, not just shot 1 — each shot's prompt opens with the resolved `style_tags` + current location lighting. The anchor is LOCATION-SPECIFIC, not a boilerplate: prepend the exact `style_tags` string, then the per-location lighting (e.g. `"..., warm Edison bulb interior light"` for a coffee shop interior; `"..., soft warm morning light, exterior"` for exterior; `"..., warm lamp light, bedroom"` for an interior bedroom). The style string itself is never hardcoded here — it is copied from `style_tags`. Late shots without an anchor drift to the model's prior.
  - **Carry physical descriptors into EVERY shot of a `multi_prompt`**, especially immediately before each `<<<voice_N>>>` tag. Do not rely on names: the model will assign lines to the wrong visible person. Full physical description = at least hair color/style, glasses if any, hoodie/top color, and one distinctive item (headphones, badge, necklace).
  - **Do not end a `multi_prompt` on a tight close-up of a face that is not present in the start frame.** This was the real "problem is always in the third shot": both EP6 multi-prompts ended on an invented face close-up; by the last shot Kling has left the start frame and re-renders that face with its own (realistic) prior. Keep the final shot within the framing the start frame supports, or split the close-up into its own clip.
  - **A second character enters mid-`multi_prompt` clip** → via Kling `elements` + `@Element1` in the relevant shot (`animator.md §5a`, burn-tested 2026-06-01). Works well **when the character occupies a noticeable share of the frame** (especially a face close-up — this fixes final-shot drift). For recognizability in a small/occluded shot (face behind glass, etc.) an element reads as generic → use a separate clip with its own start-frame instead.
- **Do NOT use Avatar** in serial-drama. If a storyboard contains `clip_type: "avatar"` or an Avatar endpoint, return it to Scenarist before generation.
- General rules — `rules/roles/animator.md`

### Sound

- **No per-scene TTS for serial-drama dialogue.** Dialogue voices come from Kling I2V `voice_ids` in Animator. Sound only generates external audio for explicit narrator/off-screen VO tracks.
- For serial-drama dialogue I2V, one character = one reusable voice across the series. Use supplied voice refs / existing Kling voice IDs from the exact bible. If Kling requires `fal-ai/kling-video/create-voice`, call it once from the supplied format-owned ref and keep the returned ID in run-local state / `proposed_bible_updates`; Manager writes it to the exact bible only after explicit final user approval.
- If a speaking character has no approved native voice ref/ID owned by the resolved series bible, STOP and report the missing requirement. Never substitute an ElevenLabs ID or borrow a voice from another format.
- For explicit narrator/off-screen VO only: intentional native audio → approved sample owned by this resolved series bible through Chatterbox → otherwise MiniMax. Retry the same route once, then STOP; do not switch provider.
- **Music is mandatory and generated:** Sound always generates `bg-music.mp3` through `fal-ai/minimax-music/v2.6`; never skip it or replace it with a local library track. For sitcom tone: instrumental low-density comedy underscore, no vocals/lyrics, no dramatic swell.
- **Narrator VO (optional):** off-screen series intro voice over I2V action clips. Store as `narrator_vo` top-level field in storyboard.json: `{text, voice, tts_url, duration_sec, overlay_clips, volume}`. Sound generates the MP3; Editor overlays it via amix starting at t=0. Generate with `faster-whisper` for timing (offset=0 per clip, then +cumulative_start for ASS timecodes).
- **Subtitles:** ASS via `ffmpeg-full` (`/usr/local/bin/ffmpeg-full/ffmpeg`) — libass is required; stock Homebrew ffmpeg silently errors on `ass=` filter. Use sentence-level Whisper timing — NOT word-by-word. Dialogue style: Bold=1, Outline=6, Fontsize=70, white, MarginV=520. Narrator style: Bold=1, Outline=4, italic, warm color `#EDE0C8`, Fontsize=65, MarginV=540.
- **Whisper source = individual scene MP4s, NOT voice-final.wav and NOT storyboard JSON text.** Extract 16kHz mono WAV from each dialogue scene MP4 (`ffmpeg -vn -ar 16000 -ac 1`), run Whisper on each separately, then offset timecodes by cumulative scene start. Running Whisper on voice-final.wav or storyboard text produces subtitles with speaker names and JSON metadata instead of dialogue. Burned in EP2.
- **Subtitle timing cap (mandatory):** After `add_subtitles.py` generates `build/subs.ass`, clamp every Dialogue event to the dialogue clip window it overlaps most. Events must never bleed into action/I2V-without-speech clips, CTA, or the next dialogue scene. If Whisper merges words across a scene boundary, split the subtitle text manually at the boundary.
- ONLY dialogue subs + narrator + TBC. No title cards, brainrot tags, character names.
- Background music: drama/cinematic, `volume=0.45`; duck under narrator VO only as required by the mix.
- General rules — `rules/roles/sound.md`

### Editor

- **One ffmpeg pipeline for the entire final assembly** (concat + overlays + music + fade + CTA). NOT layered.
- I2V clips: fps normalization 24 → 30 mandatory before concat. **NEVER trim I2V clips** — their declared duration is intentional and exact.
- I2V clips: **never trim**; their declared duration is intentional. Preserve each clip's embedded audio stream when `generate_audio:true`.
- **A/V sync — joint concat mandatory:** use a single `concat=n=N:v=1:a=1` with interleaved `[sv_i][sa_i]` pairs. CTA (no audio) gets `anullsrc` paired with its video.
- **I2V `generate_audio:true` audio must be preserved.** Dialogue voices are inside the I2V MP4. Never replace final audio with `voice-final.wav`; that file is for Whisper timing only.
- **`voice-final.wav` is NOT an audio source for the final encode.** It is a whisper-alignment artifact (TTS only, 16kHz mono). Final audio = scene `[k:a]` streams + mandatory `bg-music.mp3`. Passing `voice-final.wav` to the encode discards all I2V atmospheric sounds. Burned in EP3 — cost 3 re-renders.
- **amix for overlay tracks:** narrator VO + bg-music overlay on top of joint concat via `amix=inputs=3:duration=first:normalize=0`. `normalize=0` is mandatory (prevents volume division by N). `duration=first` anchors output length to the scene audio, avoiding music bleed-through.
- Off-screen narrator VO: overlay as separate amix input starting at t=0; music ducked during VO. See storyboard.json `narrator_vo` field.
- TTS overlay "behind glass" (rare): `aecho=0.8:0.9:10:0.3`, `adelay=500`
- Subtitles: ASS via ffmpeg-full (has libass); sentence-level Whisper timing. Two styles: `Default` (Bold=1, Outline=6, white, MarginV=520) for dialogue; `Narrator` (Bold=1, Outline=4, italic, warm color, MarginV=540) for off-screen VO.
- **CTA included in concat list** as the last clip (not a separate re-encode)
- TBC overlay 2s before the end (before fade)
- Fade out 1.0s on MAIN_DUR (before CTA); CTA goes after fade in silence
- **Episode title card — check the series' story bible for its declared type (`png` or `text`) before generating anything; do not assume `png` by default.**
  - **`png` type** — use the series overlay PNG, not a Pillow-generated strip. The series has a locked `overlay-series.png` in `games/{GAME_TAG}/`. Load it as an ffmpeg input, scale to fit 1080px wide (`scale=1080:-1`), overlay centered on the frame (`x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2`) during the title-card window defined in `storyboard.json episode_metadata.title_card_position`. Visible 5 seconds with fade-in 0.5s + fade-out 0.5s (starting at t=4.5s relative to overlay start). **PNG overlay input MUST be given a real timeline — `-loop 1 -t <total_duration>` — or `enable='between(t,...)'` silently never fires.** A plain `-i overlay-series.png` produces a single-frame stream whose PTS never advances past ~0, so the filter gate never evaluates true.
  - **`text` type** — burn two `drawtext` lines directly onto the title-card window (scene 1's trailing silent portion or a freeze-frame interstitial, same placement rules as `png`): line 1 the episode number ("EPISODE {N}"), line 2 the episode title, using that series' locked font/size/position convention from its story bible (e.g. genshin-dont-save-me-en: Montserrat-Black, line 1 fontsize ~64 at y≈120, line 2 fontsize ~40 at y≈210, both centered with a `boxcolor=black@0.45` behind). Requires `ffmpeg-full` (`fontfile=`, libfreetype) — plain Homebrew ffmpeg silently fails to render `drawtext`. Verify the window does not overlap any scene's subtitle burn-in (drawtext near top, subtitles near bottom — check both timing AND position).
  - Technical validation checks the input timeline, filtergraph, timestamps, encode success, and output decodability only. Do not extract/pixel-diff frames or run AI Vision; the user performs any visual review during debug.
- General rules — `rules/roles/editor.md`

---

## CTA (Call to Action)

The CTA video is taken from Supabase `game_assets` (tag `cta` + `video`), resolved by `GAME_TAG` — see `editor.md §5.1` for the lookup order. Manager downloads it in Phase 0 and hands it to Editor. If the CTA has no embedded audio, inject `anullsrc`.

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
${OUTPUT_DIR}/
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

Also: exact `STORY_BIBLE_PATH` — persistent, updated only after explicit final user approval.

After explicit user approval, Manager uploads through its canonical run-scoped path.

---

## Validation before publishing

- [ ] `format: "serial-drama"`, `series_id`, `episode_number` = story_bible.last_episode + 1
- [ ] `retention_strategy`, `active_loops`, `cliffhanger` filled
- [ ] First clip — HOOK, last — CLIFFHANGER
- [ ] Scene 1 (HOOK) is a dialogue clip with a spoken line/gag, not a silent action beat
- [ ] Title card window sits after HOOK and before scene 2, and does NOT overlap any scene's `character_speech` window (own trailing silent portion of scene 1, or a freeze-frame interstitial — never defaulted onto scene 2's start)
- [ ] ACTION/DIALOGUE ~ 50/50; at least 2 characters speak
- [ ] Dialogue clips = 5s (10s only with `duration_reason`)
- [ ] All images 608×1080 (9:16)
- [ ] bg-reference per location created
- [ ] I2V: start frame only (`scene-K.png`), no end frames generated
- [ ] Cross-asset pre-flight passed (all URLs 200, distinct audio per clip, filename=index, scene_image_url↔hero) — `validation.md`
- [ ] Each character from ONE locked ref; no photoreal-tagged refs; every `image_prompt` has full style prefix
- [ ] Each I2V has an anti-drift negative derived from the resolved `style_tags`; each multi_prompt shot has a style anchor copied from `style_tags`; no multi_prompt ends on an invented face close-up
- [ ] For every `<<<voice_N>>>` tag in every multi_prompt shot: the physical descriptor IMMEDIATELY preceding it belongs to `voice_ids[N-1]`'s character — check who actually SPEAKS the line, not just who is mentioned last in the sentence. Burned EP4 (genshin, 2026-07-07): a shot described character A then tagged `<<<voice_1>>>` for character B's line, sitting right after A's descriptor — Kling rendered both characters off-model/identity-confused.
- [ ] Dialogue clips use I2V `multi_prompt + voice_ids`; no Avatar endpoint and no `clip_type: "avatar"`
- [ ] Subtitles ASS events are clamped to dialogue scene windows; no bleed into action scenes or silence
- [ ] fps normalized to 30 before concat
- [ ] One ffmpeg pipeline, not layered
- [ ] CTA included in concat-list (not a separate re-encode)
- [ ] TBC overlay 2s before the end; fade out 1.0s
- [ ] Anti-repetition check passed
- [ ] Story bible still unchanged before review; updated only after explicit final user approval

---

## Anti-patterns

- ❌ Kling Avatar v2 for serial-drama.
- ❌ External TTS as the primary serial-drama dialogue source. Dialogue voice comes from Kling I2V `voice_ids`.
- ❌ Kokoro TTS, Kling Lipsync, ElevenLabs
- ❌ `voice_id` hash instead of `voice` name
- ❌ 1:1 square scenes (all serial-drama frames are 9:16)
- ❌ character ref directly as scene image (each clip = its own PNG)
- ❌ Generating `scene-K-end.png` for I2V — end frames forbidden (storyboarder.md §14.8); `end_image_url` + `multi_prompt` = Kling 422
- ❌ `-shortest` in FFmpeg
- ❌ Closing all loops (at least 2 active)
- ❌ Repeating hooks/cliffhangers from the last 8 episodes
- ❌ Redoing clips that already work (each extra generation = $0.42+)
- ❌ Layered assembly (breaks music and timing)
- ❌ Padding dialogue clips with `tpad=stop_mode=clone` / freeze-last-frame to fake extra runtime inside a scene. Runtime comes from I2V durations. (This does NOT forbid the title-card freeze-frame interstitial between scene 1 and scene 2 — that's a distinct beat, not padding a clip's own duration.)
- ❌ Title-card overlay window defaulted onto scene 2 (or any scene with `character_speech`) — always place it on scene 1's silent tail or as its own freeze-frame interstitial (see "Episode structure" above). Burned ROOM 1701 EP4 (2026-07-10).
- ❌ Mid-episode title cards, brainrot tags, character name overlays (the episode-open title card is the one exception — see "Episode structure")
- ❌ Long 10s dialogue clips for $0.04 savings (kills dynamics)
- ❌ Re-rendering one line into a parallel `-new`/`-v2` audio file (drops locked voice → same character, two voices — EP6 Admiral)
- ❌ Referencing one character from two different ref asset paths across clips (face differs between adjacent clips)
- ❌ Source ref whose visual style conflicts with the resolved `style_tags` (a mismatched-style source image is not overridden by text negatives — e.g. a photoreal ref will not be un-realistified by "NOT photorealistic")
- ❌ `image_prompt` without the full `style_tags` prefix (off-style clip)
- ❌ I2V clip without an anti-drift negative derived from `style_tags`; `multi_prompt` shot without a style anchor copied from `style_tags`
- ❌ Ending a `multi_prompt` on a tight invented face close-up not present in the start frame (drifts realistic)
- ❌ Launching Kling before the cross-asset pre-flight gate passes (dead ref / duplicate audio / wrong PNG — see `validation.md`)
