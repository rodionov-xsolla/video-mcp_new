---
subtitles: true
overlays: true
---

# Format "Wild Documentary" — game creatures filmed as real wildlife, narrated by an elderly naturalist

A short-form nature documentary where iconic game creatures are portrayed as real animals discovered in their natural habitat. Hidden-camera footage aesthetic: shaky handheld, telephoto lens, found footage grain. An elderly male naturalist (David Attenborough register) provides hushed, awe-filled VO over each clip. No lipsync, no dialogue — just ambient sound, creature behavior, and the narrator quietly observing. Ends with the last creature holding a white sign in its mouth/paw (in-scene CTA hook).

This file is the **playbook**: when to use, concept, budget, role briefs. Craft rules (TTS, NB2, Kling I2V, ffmpeg) — in `rules/roles/*.md`.

---

## When to use

Keywords: "documentary", "wildlife", "дикая природа", "документалка", "натуралист", "naturalist", "nature doc", "hidden camera", "скрытая камера", "wild creatures", "wild pokémon", "wild pokemon", "дикие покемоны", "как выглядели бы в природе", "creatures in the wild".

Best fit for games with iconic, visually-recognizable creatures (Pokémon Go, Genshin monsters, WoW beasts, FF summons). Each video = 3–5 different creatures, each shown doing one characteristic behavior. **Single-episode format** — no serial continuity.

---

## Concept

- **Genre:** nature documentary, found footage, wildlife photography
- **Style:** ultra-realistic — creatures rendered as real animals in real biomes. NOT game-art style. "How would this creature actually look and move if it existed?"
- **Duration:** 20–30s (4–5 clips × 5s, no speedup)
- **Budget:** up to $5.00 per video. Stop if spend > $4.50.
- **Frame format:** 9:16 (608×1080)
- **Speedup:** NONE — documentary pacing is deliberate and slow

### Models

- **Image:** NB2 (`fal-ai/nano-banana-2/edit`) — ultra-realistic wildlife photography style
- **Video:** Kling v3 Standard I2V (`generate_audio: true`) — ambient creature/environment sounds baked in
- **Audio:** MiniMax TTS (naturalist narration) overlaid over Kling's embedded audio
- **Music:** none, or barely audible ambient underscore (vol 0.05)

### Key mechanic

Every clip: Kling generates the visual + ambient sound. MiniMax TTS generates the narration separately. Editor extracts Kling audio, attenuates it (vol 0.20), mixes with TTS at full volume. Viewers hear: rustling leaves, animal breathing, distant wildlife — underneath a calm elderly voice describing what they're seeing.

**CTA-in-scene:** the last creature clip has `cta_in_scene: true`. The NB2 image shows the creature approaching the camera holding a small white handwritten sign. The Kling animation shows it stopping and presenting the sign. The naturalist whispers something like *"...and it seems to be leaving us a message."* The standard CTA clip is appended after.

### Locked across the format

- **Aspect ratio:** 9:16, 608×1080
- **Style:** photorealistic wildlife photography — no game UI, no game art, no stylized look
- **Camera aesthetic:** grainy, telephoto compression, shallow depth of field, shaky handheld or fixed trail camera, partial occlusion by leaves/branches
- **Naturalist voice:** `Deep_Voice_Man`, speed 0.90, emotion `neutral` — one voice, same narrator across all clips. (`Patient_Man` 0.80 tested and rejected — too slow.)
- **Narration tone:** hushed, slightly breathless, factual but reverent. Short sentences. Never exclamatory. Never fourth-wall-breaking. Example: *"Notice how it adjusts its weight before the strike — remarkable."*
- **No speedup** (unlike comedy formats) — pace is contemplative
- **Negative prompt (all clips):** `text in frame, subtitles, watermark, game UI, game HUD, cartoon style, anime style, CJK characters`

### Variable per video

- Which creatures (3–5), their characteristic behavior, their real-world biome analogue
- CTA sign text: always `"follow for more"` (locked)
- Narration lines per creature (12–20 words each, 5s window)

---

## Budget (rough estimates)

| Component | Per unit | Typical count | Subtotal |
|---|---|---|---|
| NB2 creature ref | $0.08 | 1 per creature | $0.32–$0.40 |
| NB2 scene image | $0.08 | 1 per clip | $0.32–$0.40 |
| Kling v3 Standard I2V 5s (with audio) | $0.63 | 4–5 | $2.52–$3.15 |
| MiniMax TTS narration (~15 words/clip) | ~$0.01 | 4–5 | $0.04–$0.06 |
| **Typical total** | | | **$3.20–$4.01** |

Max with 1 retry per problem clip: **$5.00**. Stop at **$4.50**.

---

## Video structure

| Slot | Mandatory? | Dur. | Goal |
|---|---|---|---|
| Creature clip 1 | yes | 5s | First creature, signature behavior, biome establishing |
| Creature clip 2 | yes | 5s | Second creature, different biome |
| Creature clip 3 | yes | 5s | Third creature |
| Creature clip 4 | optional | 5s | Fourth creature |
| CTA-in-scene clip | yes | 5s | Last creature holds white handwritten sign, narrator reacts |
| Standard CTA | yes | ~5s | Channel CTA from Supabase, appended as-is |

Total pre-speed: 20–30s. No speedup applied. Hard cap 35s.

**Anti-repetition:** no two consecutive clips in the same biome (alternate between jungle, savanna, desert, forest, underwater, tundra, etc.).

---

## Narration structure

- **One continuous script** for the full video, split into `tts_segment` per clip
- Each segment: 12–20 words, past-tense or present-progressive, describes what the camera sees
- Clip 1: slightly louder (discovery framing): *"In the dense undergrowth of the Amazon basin, something extraordinary has been caught on camera..."*
- Clips 2–N: hushed observation: *"Its flower releases spores at precisely twelve degrees celsius. We do not yet know why."*
- CTA-in-scene clip: whispered reaction to the sign: *"...and it appears to be inviting us closer. Curious."*
- Total narration: ~70–100 words for 20–30s of video
- One TTS call, full text joined, clips get `tts_segment` timestamps aligned by Editor

---

## Manager — Phase 0: Creature Research (mandatory before Scenarist)

Before calling the Scenarist, the Manager must do a short web search for every creature in the request. The goal: correct biomes, real lore-accurate behaviors, canonical habitat. Never rely on training data alone — creature lore changes, wikis are authoritative.

**For each creature:**
1. Search `{creature name} {game name} habitat wiki` (Memory Alpha, Bulbapedia, Fandom, etc.)
2. Extract:
   - **Home planet / region / biome** — where they actually live in lore
   - **Diet / foraging behavior** — what they eat, how they hunt or graze
   - **Social behavior** — solitary, pack, colony, swarm, etc.
   - **Characteristic behaviors** — the one thing they're famous for (purring, multiplying, elemental attacks, etc.)
   - **Known environmental preferences** — temperature, humidity, terrain
3. Write a **1-paragraph habitat summary** per creature (3–5 sentences max)
4. Pass this summary to Scenarist in the prompt as `CREATURE_RESEARCH` block

**What to do with the research:**
- Use home biome as the primary biome for clip 1 (establishing shot)
- Use characteristic behaviors as the basis for clip 2+ actions
- If the canon habitat is a spaceship/interior (e.g. tribbles live on starbases, not planets) — use the closest real-world biome analogue that fits the creature's ecological niche (e.g. tribbles → warm granary, food storage, dense colony nest)
- If no canonical habitat exists — note this explicitly and use a plausible analogue based on creature biology

**Search tools:** use WebSearch. Two queries per creature is enough. If the wiki page is returned, read it.

**Do NOT skip this step for "well-known" creatures** — training data has errors and omissions. EP1 tribbles were placed in a "Federation grassland" with no lore basis because this step was skipped.

---

## Role briefs

### Scenarist

- Choose 3–5 creatures. Each creature gets: biome analogue, ONE characteristic behavior to film, 1–2 naturalist sentences.
- All narration is first-person plural ("we observe…", "notice how…") or impersonal ("the creature…"). Never second-person.
- Last creature clip: `cta_in_scene: true`, `sign_text: "follow for more"` — always this exact text.
- `clip_type: "action"` for all clips — no dialogue, no Avatar.
- `character_speech: null` for all clips — no lipsync anywhere.
- No title card scene — cold open on creature.
- Format fields in storyboard.json:

```json
{
  "format": "wild-documentary",
  "game_tag": "{GAME_TAG}",
  "naturalist_voice": {
    "voice_id": "Deep_Voice_Man",
    "speed": 0.90,
    "emotion": "neutral"
  },
  "tts": {
    "full_text": "{joined narration — all tts_segments in order}",
    "language_code": "en"
  },
  "clips": [
    {
      "index": 1,
      "creature_name": "Venusaur",
      "biome": "Amazon rainforest",
      "behavior": "releasing spores from the flower",
      "clip_type": "action",
      "character_speech": null,
      "tts_segment": "In the dense undergrowth, something has been caught on camera. A creature not seen in decades.",
      "cta_in_scene": false,
      "action_description": "...",
      "camera_style": "handheld telephoto, leaves partially occlusing frame",
      "image_prompt": "...",
      "negative_prompt": "text in frame, subtitles, watermark, game UI, cartoon style, anime, CJK"
    },
    {
      "index": 4,
      "creature_name": "Pikachu",
      "biome": "Japanese mountain forest",
      "behavior": "approaching camera, holding sign",
      "clip_type": "action",
      "character_speech": null,
      "tts_segment": "It seems to be leaving us a message. Remarkable.",
      "cta_in_scene": true,
      "sign_text": "Comment PROMPT and I'll send you the workflow",
      "action_description": "...",
      "camera_style": "fixed trail camera, night vision tint, fisheye slight distortion",
      "image_prompt": "...",
      "negative_prompt": "..."
    }
  ]
}
```

- General script rules — `rules/roles/scenarist.md`

### Storyboarder

- **Style is ultra-realistic wildlife photography.** NOT game art. Imagine a BBC Nature camera crew secretly filmed this animal.
- **Game config style override:** if the game config specifies a cartoon or stylized art style (e.g. Pokémon GO cartoon 3D), IGNORE IT. Add `"style_override"` field to storyboard.json and state explicitly. The wildlife-photography style overrides ALL game config styles for this format.
- NB2 image_prompt must include: `ultra-realistic, hidden camera documentary footage, telephoto lens, shallow depth of field, naturalistic lighting, grainy texture, 4K photorealistic`

#### Creature ref workflow (mandatory — do this before generating any scene)

1. **Read the original game art ref** (`games/{GAME_TAG}/assets/`) or search for authoritative creature descriptions (wiki, in-game codex). Do NOT rely on memory or training data — the creature may look nothing like you expect.
2. **Write an exhaustive creature description** covering every anatomical feature: body shape, size proportions, armor/skin/fur texture, exact color with patches/gradients, horn shape (angle, length, curvature, attachment point), eye type, limb count and proportions, any distinctive features. The more specific the better — vague descriptions produce generic animals.
3. **Generate one photorealistic creature ref image** (NB2, `image_urls: [game_art_ref_url]`) — wide or 3/4 view showing full body. This is the canonical photorealistic render of the creature.
4. **Use this ref as the anchor for ALL subsequent scene images.** Do NOT chain refs scene-to-scene (chain degradation causes each scene to look like a different animal). Two anchor types:
   - **Body/wide shots:** `image_urls: [scene-1.png]` (first approved photorealistic scene)
   - **Face/close-up/CTA shots:** `image_urls: [scene with best horn/face profile]` (a profile or ridge shot showing correct features)

**Prompt detail rule:** every image_prompt must describe the creature's key distinguishing features explicitly (horn shape, armor texture, fur color). Never write "a Sumpter Beast" without also describing what it looks like — NB2 will invent its own interpretation. Include: exact horn description ("two short curved horns growing outward from sides of skull, curving slightly upward at tips like a yak"), armor type ("rough stone-textured armor plates"), fur ("thick coarse dark grey-brown bristly fur mane"). If the prompt is vague, the creature will be wrong.

**Scene visual contrast rule (mandatory):** adjacent clips must differ in at least TWO of the following — or the edit will look like a jump cut:
  - Camera distance (wide / medium / extreme close-up)
  - Lighting quality (dawn golden hour / hard midday / overcast / night/IR)
  - Micro-environment (riverbank vs dense ferns vs rocky clearing vs trail camera position)
  - Creature action type (static rest / moving / dramatic behavior / CTA)

Recommended rhythm for single-creature videos: **wide establishing → extreme close-up detail → dramatic behavior → CTA approach**. Never two consecutive wide shots or two consecutive medium shots. No two scenes with identical shot type in the entire video.

- **Camera style variety:** alternate between handheld telephoto, fixed trail camera, ground-level concealed, elevated wide. Set `camera_style` in each clip.
- **CTA-in-scene clip:** the `image_prompt` MUST include the exact sign text from `sign_text` field in the storyboard. Always phrase it as: `"a small white rectangular card with handwritten black marker text reading '{sign_text}'"`. NB2 is more reliable at rendering text than Kling I2V — the card must face the lens clearly. If NB2 renders the text illegible on the first attempt, retry once with the text phrase at the very start of the prompt. DO NOT attempt to fix via Kling prompt (Animator has no role in sign text) and DO NOT burn drawtext overlay (Editor has no role in sign text).
- **No bg-reference files** — environment goes into `image_prompt` inline.
- **One PNG per clip — start frame only.** No end frames.
- General rules — `rules/roles/storyboarder.md`

### Animator

- All clips: **Kling v3 Standard I2V, `generate_audio: true`** — let Kling generate ambient nature sounds.
- Fallback to v2.6 Pro only if v3 produces visible artifacts (anatomical distortion).
- **Start frame only.** No `tail_image_url`.
- **Kling prompt hard limit: 512 characters.** Count before submitting. Truncate by removing secondary details (dragonfly, specific leaf movement etc.) — keep creature motion + camera motion + grain/texture as the core.
- **Polling URL:** status at `https://queue.fal.run/fal-ai/kling-video/requests/{REQUEST_ID}/status` — NOT the model path. Using the model path (`.../v3/standard/image-to-video/requests/...`) returns 405.
- **multi_prompt via fal.ai wrapper is unreliable.** Do NOT send multi-segment prompts as a combined string like `"multi_prompt[0]: ... multi_prompt[1]: ..."` — Kling ignores the format. Write ONE well-crafted single prompt covering the full 5s arc.

#### Anti-morphing rules (mandatory for every clip)

Face and body morphing is the most common failure mode in this format. Every motion prompt MUST include an explicit negative constraint: `"no face morphing, no facial deformation, no body distortion, anatomy stable throughout"`. Add this to the end of every Kling prompt.

**For wide/medium shots with creature face visible:** put motion budget into BODY, not face. Motion prompt should explicitly lock the head: `"head stays still and low, no head raise, no facial movement"`. Motion goes into: body sway, breathing, ear rotation, tail flick, environment (grass, leaves, water).

**For extreme close-up clips (armor, fur, texture):** head and face must be OUT of frame in the source image (NB2 handles this). Motion prompt: `"stone plates shift imperceptibly with slow breathing, fur bristles move in faint breeze, camera locked"`.

**For face/portrait close-ups:** use multi-prompting for more naturalistic motion — two motion stages within the 5s clip: e.g. `"first 2s: creature holds perfectly still, nostrils flaring. next 3s: slow deliberate turn of the head, ears angle toward camera"`. This avoids the static→morph failure pattern.

Motion prompts must have three concurrent motion layers:
  1. Creature motion (breathing, moving, blinking — never face deformation)
  2. Environment motion (leaves swaying, water rippling, grass moving)
  3. Camera motion ("shaky handheld telephoto", "slight handheld drift", "fixed trail cam with minimal jitter")

**No repeated shot types across the episode.** If clip 1 is a wide telephoto, clip 2 cannot also be a wide telephoto. Check the full clip list before writing each motion prompt — vary distance, angle, and creature behavior.

- **Avoid fast motion** — documentary wildlife is slow, heavy, deliberate. Use: "moves slowly", "breathes deeply", "turns its head gradually".
- **CTA-in-scene clip:** do NOT attempt to generate sign text via Kling prompt — Kling cannot reliably render readable text. Just describe the creature approaching and stopping with "a white card visible". Text on the card comes from NB2 (if legible) — Animator has no role in sign text.
- After generation: audio is embedded in the MP4. Pass local paths to Editor.
- General rules — `rules/roles/animator.md`

### Sound

- **TTS:** one MiniMax call with the joined full narration text (`tts.full_text` from storyboard.json).
  - `voice_id: "Deep_Voice_Man"`, `speed: 0.90`, `emotion: "neutral"`
  - Upload to Supabase as `tts-narration.mp3`
- **Segmentation for Editor:** provide a `tts_segments.json` with per-clip word counts and estimated timestamps so Editor can align narration to clips. Rough formula: ~0.45s per word at speed 0.90.
- **No background music** (default). If the user explicitly requests it: ambient nature underscore from `music/Ambient/` at vol 0.05 maximum.
- General rules — `rules/roles/sound.md`

### Editor

**Two-pass single-filter pipeline** (do NOT cut TTS per-clip — it severs words at clip boundaries):

**Pass 1 — concat video + continuous audio mix:**
```bash
FF=/usr/local/bin/ffmpeg   # no libfreetype needed for pass 1

$FF -y \
  -i scene-1.mp4 -i scene-2.mp4 ... -i scene-N.mp4 \
  -i build/tts-fast.mp3 \
  -filter_complex "
    [0:v]scale=608:1080,setsar=1,fps=30[v0]; ... [vN-1];
    [v0]...[vN-1]concat=n=N:v=1:a=0[vconcat];
    [0:a]volume=0.20[a0]; ... [N-1:a]volume=0.20[aN-1];
    [a0]...[aN-1]concat=n=N:v=0:a=1[kling_mix];
    [Na]volume=1.0,apad[narration];
    [kling_mix][narration]amix=inputs=2:duration=first[audio]
  " \
  -map "[vconcat]" -map "[audio]" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ar 44100 \
  build/concat_audio.mp4
```

**atempo normalization (mandatory before Pass 1):**
```bash
TTS_DUR=$(ffprobe -i tts-narration.mp3 -show_entries format=duration -v quiet -of csv=p=0)
VID_DUR=$(python3 -c "import subprocess,json; ...")  # sum of scene durations
ATEMPO=$(python3 -c "print(round($TTS_DUR/$VID_DUR, 3))")
# Acceptable range: 0.95–1.10. Outside → re-examine narration length.
ffmpeg -y -i tts-narration.mp3 -af "atempo=$ATEMPO" build/tts-fast.mp3
```

**Pass 2 — subtitles:** the one universal path, see `rules/roles/editor.md` §6. Editor builds
`build/voice-final.wav` from the continuous narration (already after `atempo`), runs whisper, burns
the universal ASS. No `--style`/`--text`/`--atempo` — timings are correct by construction.

**Key rules:**
- **No speedup** on video (`setpts` NOT applied) — documentary pace is deliberate.
- **No drawtext sign text overlay** — the sign exists only in the visual (NB2/Kling). Never burn "follow for more" or any CTA text as a drawtext/subtitle overlay.
- **Subtitles — universal style**, generated by Editor via whisper (editor.md §6). Single-voice: `voice-final.wav` = TTS after atempo.
- **Concat order:** creature clips in storyboard index order, then standard CTA clip appended from Supabase (`assets/{GAME_TAG}/branding/cta.mp4`).
- bg-music: SKIP unless `music` block present in storyboard.json.

#### Title overlay (mandatory — overlays: true)

Burn a two-line title card at the start of every episode:
- **Line 1:** `"{GAME_WORLD} DOCUMENTARY"` — use the in-universe world name, not "Wildlife Documentary". Examples: `TEYVAT DOCUMENTARY`, `KANTO DOCUMENTARY`, `AZEROTH DOCUMENTARY`. Read the game config for the world name.
- **Line 2:** `"{creature name}"` — exact creature name as in `creature_name` field of clip 1.
- **Position:** upper third (~15% from top), centered.
- **Timing:** fade in over 0.5s at t=0, hold, fade out over 0.5s, gone by t=4s.
- **Render method:** Pillow PNG (RGBA, match video resolution) → ffmpeg overlay composite. Do NOT use drawtext with `.ttc` font paths — causes squares on some builds. Use system fonts: `Arial`, `Liberation Sans`, or `DejaVu Sans`.
- **Style:** Line 1 — large uppercase bold white; Line 2 — smaller regular weight white. No background box, no drop shadow (film grain provides contrast).

#### CTA sign text rule

The in-scene CTA sign text is **always `"follow for more"`** for this format. Scenarist sets `sign_text: "follow for more"` on the CTA clip — no exceptions, no channel-specific overrides unless the user explicitly instructs otherwise in the session.

- General rules — `rules/roles/editor.md`

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/wild-documentary/
├── storyboard.json
├── tts-narration.mp3
├── tts_segments.json             # per-clip word counts + estimated timestamps
├── scenes/
│   ├── refs/
│   │   ├── {creature1}-ref.png
│   │   └── {creatureN}-ref.png
│   ├── scene-1/
│   │   ├── scene-1.png           # start frame only
│   │   ├── scene-1.mp4           # Kling output (audio embedded)
│   │   ├── scene-1-kling.wav     # extracted Kling audio
│   │   └── scene-1-final.mp4    # Kling video + mixed audio
│   └── scene-N/ ...
├── build/
│   ├── concat-list.txt
│   └── concat.mp4
└── final.mp4                    # 608×1080, ≤35s, ambient+narration mixed
```

---

## Validation before publishing

- [ ] `format: "wild-documentary"` in storyboard.json
- [ ] Creature ref generated from original game asset / wiki, NOT from memory — all anatomical features verified
- [ ] All scene image_prompts include explicit creature feature description (horns, armor, fur, color)
- [ ] All body/wide scene images use scene-1 anchor ref; all face/CTA scenes use profile-scene anchor ref
- [ ] `character_speech: null` for ALL clips (no lipsync anywhere)
- [ ] All images 9:16, photorealistic wildlife style (NOT game art, NOT cartoon)
- [ ] No two clips with identical shot type (camera distance + creature pose)
- [ ] All Kling clips generated with `generate_audio: true`
- [ ] Every Kling motion prompt includes `"no face morphing, no facial deformation, anatomy stable throughout"`
- [ ] Wide/medium shots: head locked in motion prompt, motion on body + environment
- [ ] Kling ambient audio attenuated to vol 0.20 in final mix
- [ ] TTS narration continuous (not cut per-clip), audible — RMS > -30 dB
- [ ] `atempo` applied to TTS: `TTS_DUR / VID_DUR` in range 0.95–1.10
- [ ] ASS subtitles — universal whisper style (editor.md §6), text matches the narration
- [ ] No drawtext "follow for more" or any sign text overlay burned on video
- [ ] No speedup on video — `ffprobe duration` ≈ sum of clip durations
- [ ] No two adjacent clips with same camera distance AND same lighting
- [ ] Last creature clip has `cta_in_scene: true`, creature approaching/holding card
- [ ] Title overlay present: Line 1 = `"{GAME_WORLD} DOCUMENTARY"`, Line 2 = creature name; visible 0–4s
- [ ] Standard CTA clip from Supabase appended after creature clips
- [ ] No game UI, no stylized art, no CJK text in any frame

---

## Anti-patterns

- ❌ Game-art style NB2 images (cartoon proportions, smooth skin, bright colors) — requires photorealism
- ❌ Not overriding game config style — for stylized games (Pokémon GO etc.) MUST add `style_override` to storyboard
- ❌ Vague creature description in image_prompt — write every feature explicitly (horn shape, armor texture, fur color, body proportions). "A Sumpter Beast" without description = NB2 invents a random animal
- ❌ Skipping creature ref research — always read the original game asset or wiki before writing prompts. Never rely on training data for creature appearance
- ❌ Chain refs scene-to-scene — causes visual drift, each scene looks like a different animal. Use ONE approved anchor ref for all body shots, ONE profile/ridge scene for all face/CTA shots
- ❌ Face morphing in Kling — must add `"no face morphing, no facial deformation, anatomy stable throughout"` to EVERY motion prompt
- ❌ Putting motion budget on the face in wide/medium shots — lock the head, animate the body and environment
- ❌ Same shot type repeated — no two clips with identical camera distance + creature pose. Vary: wide telephoto → extreme close-up → dramatic action → CTA trail cam
- ❌ Generic title overlay ("Wildlife Documentary") — use in-universe world name: "TEYVAT DOCUMENTARY", "KANTO DOCUMENTARY" etc.
- ❌ `generate_audio: false` — ambient sounds are the atmosphere; silence kills the format
- ❌ Cutting TTS per-clip — severs words at clip boundaries; use ONE continuous TTS over full concat
- ❌ Skipping atempo normalization — TTS duration ≠ video duration; without atempo the narration is cut or runs long
- ❌ Manual ASS generation with `--text`/`--atempo`/`--style` — those flags are removed; Editor does it universally via whisper
- ❌ Using local ffmpeg (`/usr/local/bin/ffmpeg`) for subtitle burn — it lacks libfreetype; use `ffmpeg-full`
- ❌ Burning "follow for more" or any sign text as drawtext/subtitle overlay — breaks documentary immersion
- ❌ Trying to get Kling to render readable sign text — unreliable; text belongs in NB2 image_prompt
- ❌ Sending multi-prompt as `"multi_prompt[0]: ... multi_prompt[1]: ..."` string to Kling — not parsed; write one unified prompt
- ❌ Kling prompt over 512 chars — silently truncated or rejected with 422
- ❌ Polling Kling at `.../v3/standard/image-to-video/requests/{ID}/status` — returns 405; use `.../kling-video/requests/{ID}/status`
- ❌ Two adjacent clips with same camera distance + same lighting — causes jump cut
- ❌ All scenes in same micro-environment — visual monotony; vary distance, light, specific location
- ❌ Speedup applied to video — documentary pace is deliberate
- ❌ Narrator exclamatory or excited — hushed, factual, reverent only
- ❌ `-shortest` in FFmpeg (always use `apad`)
- ❌ Character ref directly as scene image
