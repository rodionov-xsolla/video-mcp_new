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
- **I2V only.** Every serial-drama clip, including dialogue, is Kling v3 Standard I2V. Fallback v2.6 Pro only on v3 artifacts.
- **Dialogue I2V uses Kling voice support:** `generate_audio: true`, `voice_ids`, `shot_type: "customize"`, and `multi_prompt` with `<<<voice_1>>>` / `<<<voice_2>>>`.
- **Kling Avatar v2 is forbidden for serial-drama.** Do not create Avatar refs, do not call `fal-ai/kling-video/ai-avatar/*`, and do not render dialogue as a separate lipsync avatar clip.
- **Identity is physical, not nominal.** Kling/NB2 do not know character names. Every scene prompt and every `multi_prompt` shot must identify visible/speaking characters by their locked physical descriptors and attached refs.

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
- Estimate spoken timing before generation: `speech_seconds = word_count / words_per_second`. ROOM 1701 default pace is ~2.4 words/sec; relaxed/sarcastic can be slower, tension/Michael mission-rant beats can be faster. Avoid accidental taratorка caused by too many words in a short shot.
- Add acting/pause padding when needed: +0.2s for a simple line, +0.4–0.7s for pause/comma/reaction, +0.8–1.2s for prop handoff or physical beat.
- One Kling dialogue request can use at most 2 `voice_ids`. The series/story bible may have 3+ reusable character voices, but each request remaps only the voices used in that clip to local `<<<voice_1>>>` / `<<<voice_2>>>` tags. If a scene needs 3 speaking characters in the same moment, split the scene into multiple clips.
- Prompt text per shot must stay ≤512 characters.
- The physical descriptor immediately before each `<<<voice_N>>>` must match `voice_ids[N-1]`.
- Any spoken line in a dialogue I2V clip must have `generate_audio: true`, `voice_ids`, and a matching `<<<voice_N>>>` tag. A dialogue clip rendered without voice is a failed request, not an acceptable silent beat.
- Never pad a clip with a frozen frame; the I2V duration is the duration.

---

## Story Bible — persistent series state

File `games/{GAME_TAG}/serial-drama_story_bible.json` stores the universe state between episodes. **Mandatory** for serial-drama.

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
- **Dialogue clips are I2V `multi_prompt`, not Avatar.** Stage them as medium two-shots, over-shoulders, group reactions, and insert beats. Avoid static frontal bust shots.
- Balance ACTION/DIALOGUE ~ 50/50; at least 2 different characters speak per episode
- Read the story bible: characters, voices (`voice` field), active loops, anti-repetition
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
- **Each scene is independent** — no ref chaining between scenes. Each NB2 call gets a fresh set of refs: location ref + relevant char sheets for that scene. Do not pass a previous scene's output as input to the next.
- **bg-ref must be a TIGHT MEDIUM SHOT** — not a wide establishing shot. Wide bg-refs make characters appear tiny and child-proportioned. EP2: wide coffee-spot refs caused this; regenerating as tight medium shots fixed it. If a new location has no saved bg-ref, generate it as a tight medium shot first.
- **No style-conflicting source refs.** An asset whose visual style differs from the resolved `style_tags` biases the render toward that other style; a text negative does NOT override a style-conflicting source image (e.g. a `photoreal` / `live-action` asset pulls toward realism regardless of `"not photorealistic"` in the prompt).

#### General storyboarder rules
- I2V clips: **start frame only** (`scene-K.png`). End frames are NEVER generated. `end_image_url` is FORBIDDEN with `multi_prompt` (Kling returns 422).
- Each clip = its own scene PNG (not the ref directly)
- General rules — `rules/roles/storyboarder.md`

### Animator

- I2V clips via Kling v3 Standard — micro motion only. Fallback to v2.6 Pro only on v3 artifacts.
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
  - **Второй персонаж входит в середине `multi_prompt`-клипа** → через Kling `elements` + `@Element1` в нужном шоте (`animator.md §5a`, burn-tested 2026-06-01). Работает, **если персонаж занимает заметную площадь кадра** (особенно крупный план лица — чинит дрейф финального шота). Для узнаваемости в мелком/перекрытом плане (лицо за стеклом и т.п.) element читается обобщённо → делай отдельный клип со своим start-frame.
- **Do NOT use Avatar** in serial-drama. If a storyboard contains `clip_type: "avatar"` or an Avatar endpoint, return it to Scenarist before generation.
- General rules — `rules/roles/animator.md`

### Sound

- **No per-scene TTS for serial-drama dialogue.** Dialogue voices come from Kling I2V `voice_ids` in Animator. Sound only generates external audio for explicit narrator/off-screen VO tracks.
- For serial-drama dialogue I2V, one character = one reusable voice across the series. Use the supplied voice refs / existing Kling voice IDs from the story bible. If Kling requires `fal-ai/kling-video/create-voice`, call it once from the supplied Supabase voice ref, store the returned reusable ID in the story bible, and reuse it for the series. This does not disable required TTS/VO generation for narrator/off-screen tracks or other formats.
- **Music is generated, not silently selected locally:** for serial-drama, generate `bg-music.mp3` through `fal-ai/minimax-music/v2.6` unless the user explicitly asks for a local library track. For sitcom tone: instrumental low-density comedy underscore, no vocals/lyrics, no dramatic swell.
- **Narrator VO (optional):** off-screen series intro voice over I2V action clips. Store as `narrator_vo` top-level field in storyboard.json: `{text, voice, tts_url, duration_sec, overlay_clips, volume}`. Sound generates the MP3; Editor overlays it via amix starting at t=0. Generate with `faster-whisper` for timing (offset=0 per clip, then +cumulative_start for ASS timecodes).
- **Subtitles:** ASS via `ffmpeg-full` (`/usr/local/bin/ffmpeg-full/ffmpeg`) — libass is required; stock Homebrew ffmpeg silently errors on `ass=` filter. Use sentence-level Whisper timing — NOT word-by-word. Dialogue style: Bold=1, Outline=6, Fontsize=70, white, MarginV=520. Narrator style: Bold=1, Outline=4, italic, warm color `#EDE0C8`, Fontsize=65, MarginV=540.
- **Whisper source = individual scene MP4s, NOT voice-final.wav and NOT storyboard JSON text.** Extract 16kHz mono WAV from each dialogue scene MP4 (`ffmpeg -vn -ar 16000 -ac 1`), run Whisper on each separately, then offset timecodes by cumulative scene start. Running Whisper on voice-final.wav or storyboard text produces subtitles with speaker names and JSON metadata instead of dialogue. Burned in EP2.
- **Subtitle timing cap (mandatory):** After `add_subtitles.py` generates `build/subs.ass`, clamp every Dialogue event to the dialogue clip window it overlaps most. Events must never bleed into action/I2V-without-speech clips, CTA, or the next dialogue scene. If Whisper merges words across a scene boundary, split the subtitle text manually at the boundary.
- ONLY dialogue subs + narrator + TBC. No title cards, brainrot tags, character names.
- Background music: drama/cinematic, `volume=0.15`; duck to `0.08–0.10` under narrator VO.
- General rules — `rules/roles/sound.md`

### Editor

- **One ffmpeg pipeline for the entire final assembly** (concat + overlays + music + fade + CTA). NOT layered.
- I2V clips: fps normalization 24 → 30 mandatory before concat. **NEVER trim I2V clips** — their declared duration is intentional and exact.
- I2V clips: **never trim**; their declared duration is intentional. Preserve each clip's embedded audio stream when `generate_audio:true`.
- **A/V sync — joint concat mandatory:** use a single `concat=n=N:v=1:a=1` with interleaved `[sv_i][sa_i]` pairs. CTA (no audio) gets `anullsrc` paired with its video.
- **I2V `generate_audio:true` audio must be preserved.** Dialogue voices are inside the I2V MP4. Never replace final audio with `voice-final.wav`; that file is for Whisper timing only.
- **`voice-final.wav` is NOT an audio source for the final encode.** It is a whisper-alignment artifact (TTS only, 16kHz mono). Final audio = scene `[k:a]` streams + `bg-music.m4a`. Passing `voice-final.wav` to the encode discards all I2V atmospheric sounds. Burned in EP3 — cost 3 re-renders.
- **amix for overlay tracks:** narrator VO + bg-music overlay on top of joint concat via `amix=inputs=3:duration=first:normalize=0`. `normalize=0` is mandatory (prevents volume division by N). `duration=first` anchors output length to the scene audio, avoiding music bleed-through.
- Off-screen narrator VO: overlay as separate amix input starting at t=0; music ducked during VO. See storyboard.json `narrator_vo` field.
- TTS overlay "behind glass" (rare): `aecho=0.8:0.9:10:0.3`, `adelay=500`
- Subtitles: ASS via ffmpeg-full (has libass); sentence-level Whisper timing. Two styles: `Default` (Bold=1, Outline=6, white, MarginV=520) for dialogue; `Narrator` (Bold=1, Outline=4, italic, warm color, MarginV=540) for off-screen VO.
- **CTA included in concat list** as the last clip (not a separate re-encode)
- TBC overlay 2s before the end (before fade)
- Fade out 1.0s on MAIN_DUR (before CTA); CTA goes after fade in silence
- **Episode title card — use the series overlay PNG, not a Pillow-generated strip.** Each series has a locked `overlay-series.png` in `games/{GAME_TAG}/`. Load it as an ffmpeg input, scale to fit 1080px wide (`scale=1080:-1`), overlay centered on the frame (`x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2`) during the title-card window defined in `storyboard.json episode_metadata.title_card_position`. Visible 5 seconds with fade-in 0.5s + fade-out 0.5s (starting at t=4.5s relative to overlay start). For ROOM 1701: `games/star-trek-timelines/overlay-series.png`.
- **PNG overlay input MUST be given a real timeline — `-loop 1 -t <total_duration>` — or `enable='between(t,...)'` silently never fires.** A plain `-i overlay-series.png` produces a single-frame stream whose PTS never advances past ~0, so the `overlay` filter's `enable=between(t,START,END)` gate never evaluates true — ffmpeg exits 0, no error, and the title card is simply absent from every frame. This is a silent no-op, not a crash. Burned in ROOM 1701 EP3 (2026-07-07): the first Editor pass reported the title card as burned in (based on frame-variance sampling, which false-positived on the underlying scene content), but the overlay was missing from the delivered final.mp4 — caught only when the user manually reviewed the video. **Verification must extract actual frames inside the overlay window and pixel-diff them against a frame outside the window** (or against a version rendered without the overlay filter) — variance/stddev sampling on a single frame is not sufficient proof, since normal scene content can also produce high variance.
- General rules — `rules/roles/editor.md`

---

## CTA (Call to Action)

The CTA video is taken from Supabase `game_assets` (tag `cta` + `video`). Manager downloads it in Phase 0 and hands it to Editor. For star-trek-timelines: `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/star-trek-timelines/branding/cta.mp4` (5s, no embedded audio — inject anullsrc).

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
- [ ] Each I2V has an anti-drift negative derived from the resolved `style_tags`; each multi_prompt shot has a style anchor copied from `style_tags`; no multi_prompt ends on an invented face close-up
- [ ] Dialogue clips use I2V `multi_prompt + voice_ids`; no Avatar endpoint and no `clip_type: "avatar"`
- [ ] Subtitles ASS events are clamped to dialogue scene windows; no bleed into action scenes or silence
- [ ] fps normalized to 30 before concat
- [ ] One ffmpeg pipeline, not layered
- [ ] CTA included in concat-list (not a separate re-encode)
- [ ] TBC overlay 2s before the end; fade out 1.0s
- [ ] Anti-repetition check passed
- [ ] Story bible updated after generation

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
- ❌ Padding dialogue clips with `tpad=stop_mode=clone` / freeze-last-frame. Runtime comes from I2V durations.
- ❌ Title cards, brainrot tags, character name overlays
- ❌ Long 10s dialogue clips for $0.04 savings (kills dynamics)
- ❌ Re-rendering one line into a parallel `-new`/`-v2` audio file (drops locked voice → same character, two voices — EP6 Admiral)
- ❌ Referencing one character from two different ref asset paths across clips (face differs between adjacent clips)
- ❌ Source ref whose visual style conflicts with the resolved `style_tags` (a mismatched-style source image is not overridden by text negatives — e.g. a photoreal ref will not be un-realistified by "NOT photorealistic")
- ❌ `image_prompt` without the full `style_tags` prefix (off-style clip)
- ❌ I2V clip without an anti-drift negative derived from `style_tags`; `multi_prompt` shot without a style anchor copied from `style_tags`
- ❌ Ending a `multi_prompt` on a tight invented face close-up not present in the start frame (drifts realistic)
- ❌ Launching Kling before the cross-asset pre-flight gate passes (dead ref / duplicate audio / wrong PNG — see `validation.md`)
