---
ready_to_post: yes
subtitles: false
overlays: false
---

# Format "Dual-Style" — cartoon + realistic

In one frame: cartoon/chibi game character next to its photorealistic human "twin". Style contrast is the main device.

This file is the **playbook**. Craft rules (NB2, Kling I2V, ffmpeg) — in `rules/roles/*.md`.

---

## When to use

Keywords: "dual-style", "game vs reality", "meet your character IRL", cosplay content, "which character are you".

---

## Concept

- **Cartoon left + realistic right** (positioning fixed for the whole video)
- **3 clips × 5–10s** → 15–30s total
- **Model:** Kling v3 Standard I2V, `generate_audio: true` (Kling's built-in audio — ambient SFX baked directly into the clip)
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
- Cartoon may be **smaller** (chibi = small), realistic larger
- This enhances the contrast, do not try to align by height

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
- The actor's costume must identically match the game-style version (same colors, accessories, weapon)
- Do NOT alter the actor's face (no heavy makeup or distortion in the prompt)
- `style_tags`: add `live-action cast, [Actor Name] as [Character]`

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
      "cartoon": "cartoon chibi [class] with bold black outlines, bright flat saturated colors, exaggerated proportions, [8+ details]",
      "realistic": "photorealistic [gender] [build], [same costume], real skin textures, [vivid details], [emotion]"
    },
    "environment_description": "[concrete location]",
    "style_tags": "cartoon chibi with bold black outlines, photorealistic human counterpart, dual-style side by side",
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
`cartoon chibi [class] with bold black outlines, bright flat saturated colors, exaggerated proportions, [8+ details]`

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
- General rules — `rules/roles/storyboarder.md`

### Animator
- **Kling v3 Standard I2V**, `generate_audio: true` (built-in ambient SFX), `aspect_ratio: "9:16"`
- `duration`: "5" or "10"; without `end_image_url`
- `character_speech: null` → Kling does not receive speech text
- One model for the whole video
- **⚠️ NO HEAD/FACE MOVEMENT for the photorealistic figure — MANDATORY.** Any head turn, chin lift, eye shift, or facial expression change causes face distortion in Kling I2V. motion_prompt must explicitly state: "photorealistic figure on the right: NO head movement, NO neck rotation, NO chin lift, NO eye movement — face remains completely locked forward throughout entire clip." Only body, costume, hair, and elemental effects may move.
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

- [ ] Cartoon markers in image_prompt (`bold black outlines`, `bright flat saturated colors`, `exaggerated proportions`)
- [ ] Realistic markers in image_prompt (`photorealistic`, `real skin textures`)
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
- ❌ Trying to align cartoon and realistic by height — let chibi stay smaller
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
