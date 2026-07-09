---
ready_to_post: yes
subtitles: false
overlays: false
---

# Format "Dual-Style" — cartoon + realistic

In one frame: cel-shaded anime-style game character (accurate in-game proportions by default, chibi only if explicitly requested) next to its photorealistic human "twin". Style contrast is the main device.

This file is the **playbook**. Craft rules (NB2, Kling I2V, ffmpeg) — in `rules/roles/*.md`.

---

## When to use

Keywords: "dual-style", "game vs reality", "meet your character IRL", cosplay content, "which character are you".

---

## Concept

- **Cartoon left + realistic right** (positioning fixed for the whole video)
- **3 clips × 5–10s** → 15–30s total
- **Model:** Kling v3 Standard I2V, `generate_audio: true` (Kling's built-in audio — ambient SFX baked directly into the clip; can also add unwanted music on energetic prompts, see Animator brief below)
- **Speech:** NO, `character_speech: null` everywhere
- **Budget:** $5 max

---

## Structure

| Clip | Beat | Dur. | camera_angle |
|---|---|---|---|
| 1 | hook — both appear together | 5s | wide low-angle |
| 2 | development — character through pose | 5–10s | medium eye-level |
| 3 | climax — synchronized action or contrasting reaction | 5–10s | wide pull-back |

`camera_angle` different for adjacent clips (mandatory).

Multi-character video: 1 clip = 1 pair (cartoon + realistic of one character), chain reference does **not** cross between different characters.

---

## Key prompting rules

### 1. Style isolation markers (mandatory, 2026-06-09)

The character sheet chain-ref is anime-style — without explicit style isolation, NB2 applies anime style to BOTH figures.

**Left figure (game-style) markers:**
- `anime cel-shaded style`
- `bold black outlines`
- `bright flat saturated colors`
- `vibrant flat anime colors`

**Right figure (realistic) markers — must be explicit and strong:**
- `photorealistic photograph`
- `live-action movie still`
- `real human being`
- `real skin textures, natural skin pores`
- `cinema quality lighting`
- `NOT anime, NOT cartoon, NOT illustrated`

**Style isolation in image_prompt (mandatory):**
Explicitly bind each style to its side using the phrase:
> `anime cel-shaded style on the LEFT figure only, photorealistic live-action style on the RIGHT figure only`

**Negative prompt must include:**
> `anime style on right figure, cartoon right side, cel-shaded right side, illustrated right figure, anime on both sides`

### 2. Connection between versions
- Same costume (colors, type of clothing, accessories)
- Same pose (`matching pose`, `mirrored stance`)
- Same key details (pink bandana on cartoon → pink on realistic)

### 3. Positioning
- Anime/cartoon version **always** on the left, realistic **always** on the right (or fixed the other way around — one decision for the whole video)
- `side by side`, not one behind the other

### 4. Sizes in frame
- **Default: accurate in-game body proportions on the cartoon side — NOT chibi.** Burned on genshin-impact EP5 (2026-07-09): default chibi/exaggerated-proportions template drifted far enough from the real character design that the user rejected the whole batch and forced a full Storyboarder re-run. Chibi/deformed proportions are opt-in only, on explicit user request — never the default.
- Cartoon and realistic are the same height/build (matching the character's real in-game proportions); contrast comes from render style (cel-shaded vs photorealistic), not from shrinking one figure.
- `character_description` (cartoon) and `image_prompt` must state explicitly: "accurate to in-game proportions, NOT chibi, NOT deformed, NOT exaggerated head-to-body ratio." Add `chibi, deformed proportions, exaggerated head size` to `negative_prompt`.
- Anchor cartoon fidelity to the character's chain-ref `sheet.png` (face/costume/silhouette) rather than letting the prompt override what the reference image shows.

### 6. Actor-as-realistic counterpart (optional, 2026-06-09)

Instead of a generic photorealistic human, the realistic side can depict a **specific real-world actor** who resembles the character and could play them in a live-action film. This dramatically increases virality ("Raiden Shogun = real-life Wonder Woman").

**Game config:** the `(realistic counterpart)` block must then describe the actor's real appearance + the character's costume:
```
### Hero Name (realistic counterpart)
`photorealistic [ACTOR NAME], [actor's real physical features: ethnicity, build, eye color, face structure], wearing [CHARACTER COSTUME matching game-style version exactly], [emotion matching game-style pose]`
```

**Scenarist:** `action_description` must name the actor explicitly: "…her photorealistic counterpart, played by [Actor Name], stands…"

**Rules:**
- Only use publicly known actors — no private individuals
- **Prefer widely recognized, A-list/globally famous actors over lesser-known ones** — virality scales with name/face recognition; when choosing between two plausible look-alikes, pick the more famous one.
- The actor's costume must identically match the game-style version (same colors, accessories, weapon)
- Do NOT alter the actor's face (no heavy makeup or distortion in the prompt)
- `style_tags`: add `live-action cast, [Actor Name] as [Character]`
- **Actor names are for Scenarist/Storyboarder prompts only (image generation) — never pass a real person's name into Animator/Kling-facing text** (motion_prompt, elements prompt reference). Kling doesn't parse identity from names; describe the photorealistic figure only by role/position ("the photorealistic figure on the right") and let the image itself (start frame + `elements` face-lock) carry the likeness.

### 5. Single shared space — no panel divide (mandatory, 2026-06-09)

Both versions must occupy **one continuous environment**. A visible dividing line or split-panel effect means the prompt used positional language ("on the left half / on the right half") that forced the AI into a diptych layout.

**WRONG — causes split panels:**
> "on the left [anime character] …, on the right [realistic character] …"

**CORRECT — shared space:**
> "[anime-style character] stands side by side with their photorealistic counterpart in [unified environment], both sharing the same continuous space, no dividing line"

The environment description, lighting, and ground plane must be written as **one scene** that both figures inhabit together. The positioning words `left` / `right` may still appear to anchor each figure within the description, but the scene framing must never imply two separate panels or halves.

---

## Storyboard extensions

```json
{
  "format": "dual-style",
  "visual_identity": {
    "character_description": {
      "cartoon": "cartoon [class] with bold black outlines, bright flat saturated colors, accurate in-game body proportions (NOT chibi, NOT deformed) unless chibi explicitly requested, [8+ details]",
      "realistic": "photorealistic [gender] [build], [same costume], real skin textures, [vivid details], [emotion]"
    },
    "environment_description": "[concrete location]",
    "style_tags": "cartoon cel-shaded with bold black outlines, photorealistic human counterpart, dual-style side by side",
    "color_palette": "[one palette for both versions]",
    "lighting": "[unified lighting across all scenes]"
  },
  "sfx": true,
  "scenes": [
    {
      "index": 1,
      "character_speech": null,
      "negative_prompt": "blur, distort, merged characters, single character, text overlay, watermark",
      "sfx_description": "[ambient environment sound + character action sound, e.g. 'howling wind and rustling fabric, bow string tension release']",
      "image_prompt": "[ENV, one continuous background], anime cel-shaded style on the LEFT figure only — [CHAR] [DETAILS bold black outlines vibrant flat anime colors], photorealistic live-action style on the RIGHT figure only — [ACTOR/PERSON NAME real skin textures natural skin pores cinema lighting NOT anime NOT cartoon], both sharing the same continuous space no dividing line, [MATCHING POSE], [UNIFIED LIGHTING], [CAMERA], vertical composition, 9:16 aspect ratio",
      "motion_prompt": "The anime-style [CHAR] on the left [SUBTLE ACTION]. The photorealistic [CHAR] on the right [MATCHING GROUNDED ACTION]. Both in the same continuous environment."
    }
  ]
}
```

- `style_tags` must include **both** styles
- `lighting` / `color_palette` identical across all scenes
- `image_prompt` 40–80 words, max 2 focal points

---

## Game config requirement

`games/{GAME_TAG}/{GAME_TAG}.md` must contain **TWO** versions of each character:

```markdown
### Hero Name (cartoon)
`cartoon [class] with bold black outlines, bright flat saturated colors, accurate in-game body proportions (NOT chibi, NOT deformed) unless chibi explicitly requested, [8+ details]`

### Hero Name (realistic counterpart)
`photorealistic [gender] [build], [same costume as cartoon], real skin textures, [skin/scars/dirt], [emotion]`
```

If these blocks are missing — Manager must flag and stop until they are added.

---

## Role briefs

### Scenarist
- 3 clips × 5–10s; `character_speech: null` everywhere
- Cartoon and realistic markers mandatory in image_prompt (see above)
- Same costume/pose/details between versions
- `motion_prompt` describes actions of **both** characters separately
- `negative_prompt`: `blur, distort, merged characters, single character, text overlay, watermark`
- General rules — `rules/roles/scenarist.md`

### Storyboarder
- Source ref: game asset (screenshot / character_card) from `game_assets` Supabase or `games/{GAME_TAG}/assets/refs/`
- If none — generate the cartoon version through NB2 as anchor
- **Multi-character:** every new character starts the chain anew (do NOT pass the previous character's scene)
- For one character: scene 1 = `[asset]`; scene 2+ = `[asset, scene-(K-1)]`
- **Face-lock headshot (optional side-asset, only when Animator needs `elements` binding for macro motion — see Animator brief below):** after the scene PNG is accepted, generate ONE additional frontal headshot crop of the photorealistic figure via NB2 edit, using the already-rendered scene PNG as the image reference (not a fresh text-only generation) — the headshot must match the exact identity already locked in that scene, not a new likeness. Plain neutral background, head+shoulders, facing camera, neutral expression. Upload as a per-episode asset (`episode-scene` kind), not `game_assets`. Cost ≈$0.04–0.08.
- General rules — `rules/roles/storyboarder.md`

### Animator
- **Kling v3 Standard I2V**, `aspect_ratio: "9:16"`
- `duration`: "5" or "10"; without `end_image_url`
- `character_speech: null` → Kling does not receive speech text
- One model for the whole video
- **`generate_audio: true` risk — unwanted music.** Kling's native audio can add background music/score on top of ambient SFX when the motion_prompt reads "cinematic"/energetic (see `rules/roles/animator.md` generate_audio note). If the episode has a separately-generated `bg-music.mp3` (the dual-style default via Sound), either add an explicit anti-music clause to every motion_prompt (`"ambient environmental sound only, no music, no score, no soundtrack"`) or have Editor strip the baked-in clip audio entirely at concat time and rely solely on `bg-music.mp3`.
- **Face stability — two supported patterns, pick one per episode:**
  1. **Micro-motion only (original, lowest risk):** NO HEAD/FACE MOVEMENT for the photorealistic figure — any head turn, chin lift, eye shift, or facial expression change causes face distortion in Kling I2V. motion_prompt: "photorealistic figure on the right: NO head movement, NO neck rotation, NO chin lift, NO eye movement — face remains completely locked forward throughout entire clip." Only body, costume, hair, and elemental effects may move. Camera can be any angle since the figure doesn't need to face it continuously.
  2. **Macro-motion (e.g. walking) with `elements` face-lock (validated on genshin-impact EP5, 2026-07-09):** requires the Storyboarder-generated frontal headshot (see above) passed as `elements[0].frontal_image_url`, with the scene PNG as `reference_image_urls`. **`elements` is mandatory-paired with `multi_prompt: true`** — passing `elements` with a bare top-level `prompt` causes a deferred 500 at result-fetch (`rules/roles/animator.md` §4). Reference the bound face as `@Element1` in the shot prompt; still state the explicit face-lock clause (no head turn/no morphing) even with `elements` — the binding reduces drift, it does not by itself guarantee zero motion.
  - **Camera direction for walking shots — camera must be IN FRONT of the figures (receding/dolly-back tracking, retreating at their walking pace), never behind.** The whole point of dual-style is comparing the two faces side by side; a behind-the-figures tracking shot shows only backs/backs-of-heads and defeats the format. Burned on EP5: first attempt used camera-behind per a literal reading of "camera follows them," had to be redone.
- General rules — `rules/roles/animator.md`

### Sound
- TTS **not needed** (no speech)
- **SFX per scene via CassetteAI on fal.ai** (optional, enabled when `sfx: true` in storyboard.json):
  - Endpoint: `https://queue.fal.run/cassetteai/sound-effects-generator` (async, polling base = `cassetteai/sound-effects-generator`)
  - Auth: `Authorization: Key $FAL_KEY`
  - Body (JSON file): `{"prompt": "[sfx_description from scene]", "duration": 5}`
  - Poll every 15s until COMPLETED; download WAV from `audio_file.url`
  - Save to: `OUTPUT_DIR/scenes/scene-K/scene-K-sfx.wav`; convert to mp3 via ffmpeg if needed
  - One SFX file per scene; write `sfx_url` (local path) back into storyboard.json
  - Cost: **$0.01 per generation** (4 scenes = $0.04)
- Music: **must be generated via MiniMax Music v2.6** (`fal-ai/minimax-music/v2.6`, $0.03/track). Tracks from `music/tracks.json` are forbidden — the rights holder files strikes and videos get shadow-banned. Parameters: `is_instrumental: true`, mood energetic/upbeat, BPM 120–150. Duration: at least as long as the final video (≥25s). Save as `OUTPUT_DIR/bg-music.mp3`.
- Subtitles do not apply
- General rules — `rules/roles/sound.md`

### Editor
- Scale 1080×1920, 30fps, concat with re-encode, hard cuts (no crossfade)
- **Animated CTA mandatory at the end** — fetch from `game_assets` where `tags` contains `cta` and `video`. Append after the last scene clip. If CTA is missing in Supabase — STOP and notify the Manager.
- **SFX mixing** (when `scene-K-sfx.mp3` files present): mix each SFX file aligned to its scene start time using `amix` or per-stream `adelay`. SFX volume: `0.15`. Music volume: `0.40`. NEVER `-shortest`.
- **Music plays through the full video including CTA** — do not cut music before the CTA clip. Apply `afade=t=out` only at the very end of the last clip.
- General rules — `rules/roles/editor.md`

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/dual-style/
├── storyboard.json
├── scenes/
│   ├── refs/character-ref.png
│   ├── scene-1/{scene-1.png, scene-1.mp4, scene-1-scaled.mp4}
│   ├── scene-2/...
│   └── scene-3/...
├── concat-list.txt
└── final.mp4
```

---

## Validation

- [ ] Cartoon markers in image_prompt (`bold black outlines`, `bright flat saturated colors`, accurate in-game proportions — NOT chibi/exaggerated unless explicitly requested)
- [ ] Realistic markers in image_prompt (`photorealistic`, `real skin textures`)
- [ ] If macro-motion (walking) is used: camera is in front (dolly-back), not behind; `elements` + `multi_prompt: true` used for face-lock; no real actor name in motion_prompt
- [ ] If `generate_audio: true` + separate `bg-music.mp3` exists: anti-music clause in motion_prompt, or Editor strips baked-in clip audio at concat
- [ ] Costume/pose/details match between versions
- [ ] Cartoon and realistic on fixed sides (for the whole video)
- [ ] `character_speech: null` in all clips
- [ ] `camera_angle` different for adjacent clips
- [ ] `style_tags` include both styles; `lighting`/`color_palette` unified
- [ ] For multi-character: chain reference does not cross between different characters
- [ ] `negative_prompt` filled
- [ ] Animated CTA appended at the end (from Supabase `tags: cta + video`)
- [ ] If `sfx: true`: `scene-K-sfx.mp3` present for every scene; `sfx_url` written to storyboard.json
- [ ] If actor-as-realistic: actor name in `action_description` and `style_tags`
- [ ] Budget ≤$5

---

## Anti-patterns

- ❌ "cartoon style" without concrete markers (bold outlines, flat colors) — AI will make semi-realistic
- ❌ Framing as "on the left half / on the right half" of the image — AI renders a split-panel diptych with a visible dividing line. Use shared-space language: both figures in one continuous environment.
- ❌ Missing style isolation — without "anime cel-shaded style on LEFT figure only, photorealistic on RIGHT figure only", the character sheet chain-ref bleeds anime style onto both sides. Always add explicit per-side style binding and negative_prompt entries.
- ❌ Realistic without "live" details (skin, textures) — you get a 3D render, not a human
- ❌ Chain reference between different characters — breaks appearance
- ❌ Trying to align cartoon and realistic by height — they should match (see §4, default is NOT chibi)
- ❌ Defaulting to chibi/exaggerated proportions without an explicit user request — drifts from the real character design; state "accurate to in-game proportions, NOT chibi" in every cartoon `character_description`/`image_prompt`
- ❌ Camera positioned BEHIND the figures for a walking/macro-motion shot — hides both faces, defeats the format's core comparison device. Camera goes in front (dolly-back) for any shot where the figures move toward it.
- ❌ Passing Kling `elements` with a bare top-level `prompt` (no `multi_prompt: true`) — causes a deferred 500 at result-fetch, not an immediate error
- ❌ Real actor name in Animator/Kling-facing motion_prompt text — Kling doesn't parse identity from names; use `elements`/the image for likeness, describe the figure only by role/position in motion_prompt
- ❌ `generate_audio: true` with an energetic/cinematic motion_prompt and no anti-music clause, when a separate `bg-music.mp3` already exists — Kling may bake in its own unwanted score on top
- ❌ `character_speech ≠ null` (Kling I2V does not generate voice)
- ❌ `-shortest` in ffmpeg

---

## Story Bible

Create on first run: `games/{GAME_TAG}/dual-style_story_bible.json`

```json
{
  "series_id": "dual-style-{GAME_TAG}",
  "game_tag": "{GAME_TAG}",
  "title": "{Game} Dual Style",
  "created_at": "{TODAY}",
  "last_episode": 0,
  "character_pool": [
    {
      "character_name": "slug",
      "display_name": "Name",
      "has_actor_counterpart": false,
      "actor_name": null,
      "last_seen_episode": null
    }
  ],
  "character_rotation": {
    "recent_characters": [],
    "recent_actors": [],
    "recent_environments": [],
    "recent_action_types": [],
    "cooldown_episodes": 10
  },
  "episode_summaries": [],
  "cta_url": ""
}
```

**`character_pool`** — mirrors the characters defined in `games/{GAME_TAG}/{GAME_TAG}.md` with dual-style blocks. Populate on first run; add new characters as they are added to the game config. `last_seen_episode: null` means the character has never been featured.

**`episode_summary`** structure (FIFO 5):

```json
{
  "episode": 1,
  "date": "YYYY-MM-DD",
  "characters": ["Venti", "Hu Tao"],
  "environments": ["Mondstadt cliff", "Wuwang Hill graveyard"],
  "actors": ["(none)", "(none)"],
  "action_types": ["wide-introduction-pose", "dynamic-element-release"],
  "final_url": "...",
  "duration_sec": 20.0,
  "cost_usd": 2.00
}
```

**`action_types`** slugs — describe the VISUAL HOOK TYPE, not just the beat name. Examples: `wide-introduction-pose`, `weapon-draw-stance`, `element-burst-release`, `idle-confident-stance`, `sitting-meditate`, `walking-approach`, `dynamic-jump-landing`.

**Story Bible update (Manager, after editor confirms `final.mp4`):**

1. Characters used → append each to `recent_characters`; trim to last **10 episodes' worth** (FIFO).
2. Actors used (if any named actor) → append to `recent_actors`; trim to last **10** items (FIFO).
3. Environments used → append each to `recent_environments`; trim to last **6 episodes' worth** (FIFO).
4. Action types used → append each to `recent_action_types`; trim to last **6** items (FIFO).
5. For each character featured: set `character_pool[].last_seen_episode = current episode number`.
6. Append `episode_summary`; FIFO keep last **5**.
7. Increment `last_episode`.

---

## Anti-repetition check

Before Phase 1 (scenarist), manager validates proposed character/environment selection:

- [ ] None of the selected characters appear in `recent_characters` (last 10 episodes).
- [ ] None of the selected environments appear in `recent_environments` (last 6 episodes).
- [ ] None of the selected actors appear in `recent_actors` (last 10 items).
- [ ] Proposed `action_types` do not repeat the same type 2+ times consecutively in `recent_action_types` tail.
- [ ] Prefer characters with the lowest (or null) `last_seen_episode` when choosing from the pool.

If a collision is found — scenarist picks different characters / environments before writing storyboard.json.
