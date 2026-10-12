---
ready_to_post: yes
subtitles: true
overlays: true
---

# Format "Wild Documentary" — game creatures filmed as real wildlife, narrated by an elderly naturalist

A short-form nature documentary where iconic game creatures are portrayed as real animals discovered in their natural habitat. Hidden-camera footage aesthetic: shaky handheld, telephoto lens, found footage grain. An elderly male naturalist (David Attenborough register) provides hushed, awe-filled VO over each clip. No lipsync, no dialogue — just ambient sound, creature behavior, and the narrator quietly observing. The final generated creature clip is an in-scene CTA hook: the animal approaches the camera holding a small white handwritten sign. The standard game CTA asset is appended after it.

This file is the **playbook**: when to use, concept, budget, role briefs. Craft rules (TTS, NB2, Kling I2V, ffmpeg) — in `rules/roles/*.md`.

---

## When to use

Keywords: "documentary", "wildlife", "дикая природа", "документалка", "натуралист", "naturalist", "nature doc", "hidden camera", "скрытая камера", "wild creatures", "wild pokémon", "wild pokemon", "дикие покемоны", "как выглядели бы в природе", "creatures in the wild".

Best fit for games with iconic, visually-recognizable creatures (Pokémon Go, Genshin monsters, WoW beasts, FF summons). **Each video features exactly ONE creature per episode**, shown across 4–5 clips capturing different characteristic behaviors, camera angles, and moments in its habitat — not a roster of different species. A resolved format-local story bible is mandatory even though episodes are self-contained; its `covered_creatures` list is also the source of truth for which species is not yet used, so a new episode always picks an unused creature. If it is missing, ask the user whether to create it and stop until they confirm. Update its state only after the user explicitly approves the presented final video.

---

## Concept

- **Genre:** nature documentary, found footage, wildlife photography
- **Style:** ultra-realistic — creatures rendered as real animals in real biomes. NOT game-art style. "How would this creature actually look and move if it existed?"
- **Duration:** 20–30s (4–5 clips × 5s, no speedup)
- **Budget:** up to $5.00 per video. Stop if spend > $4.50.
- **Frame format:** 9:16 (1080×1920)
- **Speedup:** NONE — documentary pacing is deliberate and slow

### Models

- **Image:** NB2 (`fal-ai/nano-banana-2/edit`) — ultra-realistic wildlife photography style
- **Video:** Kling v3 Standard I2V (`generate_audio: true`) — ambient creature/environment sounds baked in
- **Audio:** intentional native speech when supported → approved sample owned by this `wild-documentary` bible through Chatterbox → otherwise MiniMax, over Kling's embedded ambient audio
- **Music:** none, or barely audible ambient underscore (vol 0.05)

### Key mechanic

Every clip: Kling generates the visual + ambient sound. MiniMax TTS generates the narration separately. Editor extracts Kling audio, attenuates it (vol 0.20), mixes with TTS at full volume. Viewers hear: rustling leaves, animal breathing, distant wildlife — underneath a calm elderly voice describing what they're seeing.

**CTA-in-scene:** the last generated creature clip has `cta_in_scene: true`. Resolve both the exact sign wording and the standard CTA asset exclusively from the exact current `STORY_BIBLE_PATH` at `cta.sign_text` and `cta.standard_asset_url`; never use a global or cross-game fallback. Its NB2 start frame shows the creature approaching the camera with the story-bible sign facing the lens; Kling animates the approach and presentation without regenerating the text. The narrator reacts quietly to the message. Append the story-bible standard CTA asset after this generated CTA scene. If either CTA field is missing or empty, STOP before generation and ask to complete the exact bible.

### Still shots: allowed

The scenarist may plan still shots (`motion: "still"`) under the rule, cap and fields in `rules/roles/scenarist.md` "Still shots" (§8). A still scene gets its start PNG as usual and is rendered free by the Animator (`tools/still_shot.py`, no paid clip), saving that scene's Kling clip ($0.63 per 5s scene with `generate_audio: true`); narration plays over it as normal.

- **Best candidates:** the establishing shot (clip 1) when it is a wide biome view with the creature small and at rest; a habitat or landscape shot where no creature motion matters (an empty clearing, a nest, tracks in mud).
- **Never a still:** the CTA-in-scene clip (the approach is the point), a dramatic-behavior clip, or a face/portrait close-up. Zero stills is a normal result.
- A still has no clip sound: the Kling ambience drops out for that scene and the narration plays over silence. Count that loss in the impact score and prefer at most one still per episode.
- A still scene carries `duration_sec: 5` (a number): the Phase 1 still gate and `tools/still_shot.py` read it. Its `still_effect` counts as the clip's camera move.

### Locked across the format

- **Aspect ratio:** 9:16, 1080×1920
- **Style:** photorealistic wildlife photography — no game UI, no game art, no stylized look
- **Camera aesthetic:** grainy, telephoto compression, shallow depth of field, shaky handheld or fixed trail camera, partial occlusion by leaves/branches
- **Naturalist voice:** `Deep_Voice_Man`, speed 0.90, emotion `neutral` — one voice, same narrator across all clips. (`Patient_Man` 0.80 tested and rejected — too slow.)
- **Narration tone:** hushed, slightly breathless, factual but reverent. Short sentences. Never exclamatory. Never fourth-wall-breaking. Example: *"Notice how it adjusts its weight before the strike — remarkable."*
- **No speedup** (unlike comedy formats) — pace is contemplative
- **Negative prompt (non-CTA clips):** `text in frame, subtitles, watermark, game UI, game HUD, cartoon style, anime style, CJK characters`
- **CTA sign exception:** the last clip permits only the exact `sign_text` on the white card; reject extra text, misspellings, printed typography, UI, and watermarks.

### Variable per video

- Which single creature (an unused entry not yet in the exact story bible's `covered_creatures`), its real-world biome analogue, and 4–5 distinct characteristic behaviors/camera treatments to film across clips
- CTA sign text and standard CTA asset: mandatory values from the exact story bible's top-level `cta` object; no global, game-config, special-file, or cross-game fallback
- Narration lines per clip/behavior (12–20 words each, 5s window)

---

## Budget (rough estimates)

| Component | Per unit | Typical count | Subtotal |
|---|---|---|---|
| NB2 creature ref | $0.08 | 1 per episode (one creature, reused across all clips) | $0.08 |
| NB2 scene image | $0.08 | 1 per clip | $0.32–$0.40 |
| Kling v3 Standard I2V 5s (with audio) | $0.63 | 4–5 | $2.52–$3.15 |
| MiniMax TTS narration (~15 words/clip) | ~$0.01 | 4–5 | $0.04–$0.06 |
| **Typical total** | | | **$2.96–$3.69** |

A still scene saves its Kling clip ($0.63 per 5s with audio); its NB2 image is still generated.

Max with 1 technical retry per failed request: **$5.00**. Retry once with the same provider/settings; a second failure stops the video with an error. No provider/model/local fallback. Stop at **$4.50**.

---

## Video structure

| Slot | Mandatory? | Dur. | Goal |
|---|---|---|---|
| Creature clip 1 | yes | 5s | Establishing shot — signature behavior, biome establishing |
| Creature clip 2 | yes | 5s | Different behavior/camera angle, same creature, same biome |
| Creature clip 3 | yes | 5s | Different behavior/camera angle |
| Creature clip 4 | optional | 5s | Different behavior/camera angle |
| CTA-in-scene clip | yes | 5s | Same creature approaches with a white handwritten sign; narrator reacts |
| Standard CTA | yes | ~5s | Channel CTA from Supabase, appended as-is |

Total pre-speed: 20–30s. No speedup applied. Hard cap 35s.

**Anti-repetition (within episode):** the creature and biome stay the same across all clips — vary behavior, camera distance/angle, and lighting instead (see Storyboarder "Scene visual contrast rule"); no two adjacent clips may share the same shot type (camera distance + creature pose). **Anti-repetition (across episodes):** the exact story bible's `covered_creatures` list is mandatory — never re-pick a creature or its exact biome that's already logged there.

---

## Narration structure

- **One continuous script** for the full video, split into `tts_segment` per clip
- Each segment: 12–20 words, past-tense or present-progressive, describes what the camera sees
- Clip 1: slightly louder (discovery framing): *"In the dense undergrowth of the Amazon basin, something extraordinary has been caught on camera..."*
- Clips 2–N: hushed observation: *"Its flower releases spores at precisely twelve degrees celsius. We do not yet know why."*
- CTA-in-scene clip: a short, hushed reaction to the sign, such as *"...and it seems to be leaving us a message. Curious."*
- Total narration: ~70–100 words for 20–30s of video
- One TTS call, full text joined, clips get `tts_segment` timestamps aligned by Editor

---

## Manager — Phase 0: Creature Research

Before calling the Scenarist, Manager performs the format's existing Phase 0 creature research. Keep the declared phase ownership and order unchanged.

**For each creature:**
1. Search `{creature name} {game name} habitat wiki` (Memory Alpha, Bulbapedia, Fandom, etc.)
2. Extract:
   - **Home planet / region / biome** — where they actually live in lore
   - **Diet / foraging behavior** — what they eat, how they hunt or graze
   - **Social behavior** — solitary, pack, colony, swarm, etc.
   - **Characteristic behaviors** — the one thing they're famous for (purring, multiplying, elemental attacks, etc.)
   - **Known environmental preferences** — temperature, humidity, terrain
3. Write a **1-paragraph habitat summary** per creature (3–5 sentences max) into `research.json`
4. Include structured `CREATURE_RESEARCH` and, only when necessary, `CREATURE_ANATOMY` blocks in that artifact for the later script/storyboard phases

**What to do with the research:**
- Use home biome as the primary biome for clip 1 (establishing shot)
- Use characteristic behaviors as the basis for clip 2+ actions
- If the canon habitat is a spaceship/interior (e.g. tribbles live on starbases, not planets) — use the closest real-world biome analogue that fits the creature's ecological niche (e.g. tribbles → warm granary, food storage, dense colony nest)
- If no canonical habitat exists — note this explicitly and use a plausible analogue based on creature biology

**Search tools (existing Manager Phase 0 research scope):** use WebSearch. Two queries per creature is enough. If the wiki page is returned, read it.

**Do NOT skip this step for "well-known" creatures** — training data has errors and omissions. EP1 tribbles were placed in a "Federation grassland" with no lore basis because this step was skipped.

### Visual ref inspection (existing Manager Phase 0 scope, only when genuinely necessary)

After web research, Scenarist may inspect an authoritative source image only when the textual sources leave a genuine anatomy ambiguity or the user explicitly points to a source asset. This is the sole image-inspection exception and applies only to the source reference, never generated media. If necessary, Scenarist opens the local game art ref (`games/{GAME_TAG}/assets/` or the user-provided path) and writes an **anatomy checklist** into `research.json` covering the relevant visible features:

- Eyes: present / absent / partially hidden / how many
- Limbs: visible / count / type (paws, fins, tentacles)
- Mouth / beak / snout: shape and visibility
- Skin / fur / scales: texture, color patches, gradients
- Horns / spines / wings / tail: shape, length, attachment point
- Body proportions: relative head-to-body size, stance
- Any distinctive markings

Pass `CREATURE_ANATOMY` only when source inspection was actually necessary. It overrides training-data assumptions. Otherwise use authoritative textual research and do not run image inspection as a routine gate. In debug mode, stop at the existing Phase 0 boundary.

Example error (EP1 tribbles): manager described "no visible eyes" from memory — original ref clearly shows small eyes. Anatomy was wrong in all 5 generated scenes as a result.

---

## Role briefs

### Scenarist
- Choose ONE creature for the whole episode — a species not yet listed in the exact story bible's `covered_creatures`. Establish its biome analogue once; give it 4–5 distinct characteristic behaviors/camera treatments across clips, each with 1–2 naturalist sentences.
- All narration is first-person plural ("we observe…", "notice how…") or impersonal ("the creature…"). Never second-person.
- Last generated creature clip: `cta_in_scene: true`, with `sign_text` copied verbatim from the exact story bible's `cta.sign_text`. Missing value is a blocking configuration error.
- `clip_type: "action"` for all clips — no dialogue, no Avatar.
- `character_speech: null` for all clips — no lipsync anywhere.
- No title card scene — cold open on creature.
- Still shots: optional, per "Still shots: allowed" above and `rules/roles/scenarist.md` "Still shots"; at most one is preferred, zero is a normal result.
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
      "creature_name": "Venusaur",
      "biome": "Amazon rainforest",
      "behavior": "approaching camera, holding sign",
      "clip_type": "action",
      "character_speech": null,
      "tts_segment": "It seems to be leaving us a message. Remarkable.",
      "cta_in_scene": true,
      "sign_text": "{exact STORY_BIBLE_PATH -> cta.sign_text}",
      "action_description": "...",
      "camera_style": "fixed trail camera, night vision tint, slight fisheye distortion",
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

#### Ultra-realistic prompting (mandatory technique — learned from EP1 Seelie retry)

The most common failure mode: the creature looks like a CGI asset pasted into a background — a clean glowing sphere or cartoon character floating in a realistic environment. This is wrong. The creature must feel physically present in nature, as if it were a real bioluminescent/biological organism photographed by a hidden camera.

**Prompt structure — lead with camera/technical specs FIRST:**
```
RAW wildlife photography, Canon 5D Mark IV, [focal length], ISO 3200, heavy film grain and digital noise, natural light only — [creature anatomy + behavior] — [environment] — atmospheric haze, chromatic aberration at edges, no studio lighting, no post-processing
```

**Key elements that force photorealism:**
1. **Film grain and noise** — always include: `"heavy film grain, digital noise, ISO 3200 grain texture"`. This is the single most effective realism signal.
2. **Imperfect lighting** — `"natural ambient light only, no studio lighting, uneven exposure, underexposed background"`. Perfect lighting = CGI. The creature's glow should cast realistic light on nearby surfaces (grass, stone, leaves).
3. **Environmental integration** — the creature must feel embedded in the scene, not pasted on top. Its glow should interact with the surroundings: `"bioluminescent glow casting soft light on surrounding grass/stone, atmospheric haze catching the light"`. A spirit or orb can still be smooth and glowing — the failure mode is when it looks like a flat cartoon asset with no environmental interaction.
4. **Camera imperfections** — `"handheld camera shake, partial occlusion by foreground grass/branches, lens flare, chromatic aberration"`.
5. **Strong negative prompt** — every scene must include: `"no cartoon shading, no cel shading, no flat colors, no anime outline, no game UI, no studio lighting, no video game render"`. Do NOT add "no smooth sphere" — the creature can legitimately be a smooth glowing orb/spirit.

**Creature scale rule:** the creature should be SMALL relative to the environment. In wide and medium shots it occupies 5–15% of frame height. A creature that dominates the frame reads as a rendered asset, not a wild animal. Let the environment be primary.

#### Creature ref workflow (mandatory — do this before generating any scene)

1. Use authoritative creature descriptions (wiki, in-game codex). Inspect the original game art ref (`games/{GAME_TAG}/assets/`) only when a genuine anatomy ambiguity remains or the user explicitly asks; never inspect generated media.
2. **Write an exhaustive creature description** covering every anatomical feature: body shape, size proportions, armor/skin/fur texture, exact color with patches/gradients, horn shape (angle, length, curvature, attachment point), eye type, limb count and proportions, any distinctive features. The more specific the better — vague descriptions produce generic animals.
3. **Generate one format-bound photorealistic creature ref image** (NB2, with the authoritative game art source only if source inspection was necessary) — wide or 3/4 view showing full body.
4. **Use this same format-bound ref as the anchor for ALL subsequent scene images.** Do NOT chain refs scene-to-scene and do not borrow an image from another format. Generated media receives technical validation only; the user performs any visual review during debug.

**Prompt detail rule:** every image_prompt must describe the creature's key distinguishing features explicitly (horn shape, armor texture, fur color). Never write "a Sumpter Beast" without also describing what it looks like — NB2 will invent its own interpretation. Include: exact horn description ("two short curved horns growing outward from sides of skull, curving slightly upward at tips like a yak"), armor type ("rough stone-textured armor plates"), fur ("thick coarse dark grey-brown bristly fur mane"). If the prompt is vague, the creature will be wrong.

**Creature vertical placement rule (mandatory — subtitle safe zone):** the creature must be positioned in the **central vertical zone of the frame (roughly 20%–75% from the top)**. Never place the creature in the bottom quarter of the frame — that area is covered by subtitles (ASS burn-in). In wide shots where the creature is small, keep it at mid-frame height, not hovering near the ground. In the image_prompt, use explicit placement language: `"creature at mid-frame, center of image, not near bottom edge"`. This applies to all creature clips, including the CTA clip.

**Scene visual contrast rule (mandatory):** adjacent clips must differ in at least TWO of the following — or the edit will look like a jump cut:
  - Camera distance (wide / medium / extreme close-up)
  - Lighting quality (dawn golden hour / hard midday / overcast / night/IR)
  - Micro-environment (riverbank vs dense ferns vs rocky clearing vs trail camera position)
  - Creature action type (static rest / moving / dramatic behavior / CTA)

Recommended rhythm: **wide establishing → extreme close-up detail → dramatic behavior → CTA approach**. Never two consecutive wide shots or two consecutive medium shots. No two scenes with identical shot type in the entire video.

- **Camera style variety:** alternate between handheld telephoto, fixed trail camera, ground-level concealed, elevated wide. Set `camera_style` in each clip.
- **CTA-in-scene clip:** first verify that storyboard `sign_text` exactly equals `STORY_BIBLE_PATH -> cta.sign_text`. Its `image_prompt` MUST include that exact text, phrased as `"a small white rectangular card with handwritten black marker text reading '{sign_text}'"`. Put the text phrase near the start of the prompt and require the card to face the lens cleanly. NB2 owns readable sign text. If debug review finds the result illegible or misspelled, stop and follow the Storyboarder runner's claimed-output regeneration policy; never resubmit the same job or delete its state/claim. Do not ask Kling to regenerate lettering and do not burn replacement text in Editor.
- **No bg-reference files** — environment goes into `image_prompt` inline.
- **One PNG per clip — start frame only.** No end frames.
- General rules — `rules/roles/storyboarder.md`

### Animator

- All animated clips: **Kling v3 Standard I2V, `generate_audio: true`** — let Kling generate ambient nature sounds (still scenes are rendered locally, no paid clip).
- Still scenes (`motion: "still"`): no Kling call; render with `tools/still_shot.py` as `rules/roles/animator.md` §2b describes. The still clip has no audio stream. Never replace a failed Kling clip with a still.
- Retry one technically failed v3 request once with the same endpoint/settings. If it fails again, STOP and report the error. Do not switch to v2.6 or another provider.
- **Start frame only.** No `tail_image_url`.
- **Kling prompt hard limit: 512 serialized UTF-8 bytes.** Measure `len(prompt.encode("utf-8"))` before submitting. Trim secondary details first.
- **Polling URL:** status at `https://queue.fal.run/fal-ai/kling-video/requests/{REQUEST_ID}/status` — NOT the model path. Using the model path (`.../v3/standard/image-to-video/requests/...`) returns 405.
- **multi_prompt via fal.ai wrapper is unreliable.** Do NOT send multi-segment prompts as a combined string like `"multi_prompt[0]: ... multi_prompt[1]: ..."` — Kling ignores the format. Write ONE well-crafted single prompt covering the full 5s arc.

#### Anti-morphing rules (mandatory for every clip)

Face and body morphing is the most common failure mode in this format. Every motion prompt MUST include an explicit negative constraint: `"no face morphing, no facial deformation, no body distortion, anatomy stable throughout"`. Add this to the end of every Kling prompt.

**For wide/medium shots with creature face visible:** put motion budget into BODY, not face. Motion prompt should explicitly lock the head: `"head stays still and low, no head raise, no facial movement"`. Motion goes into: body sway, breathing, ear rotation, tail flick, environment (grass, leaves, water).

**For extreme close-up clips (armor, fur, texture):** head and face must be OUT of frame in the source image (NB2 handles this). Motion prompt: `"stone plates shift imperceptibly with slow breathing, fur bristles move in faint breeze, camera locked"`.

**For face/portrait close-ups:** use multi-prompting for more naturalistic motion — two motion stages within the 5s clip: e.g. `"first 2s: creature holds perfectly still, nostrils flaring. next 3s: slow deliberate turn of the head, ears angle toward camera"`. This avoids the static→morph failure pattern.

Animated clips' motion prompts must have three concurrent motion layers:
  1. Creature motion (breathing, moving, blinking — never face deformation)
  2. Environment motion (leaves swaying, water rippling, grass moving)
  3. Camera motion ("shaky handheld telephoto", "slight handheld drift", "fixed trail cam with minimal jitter")

**No repeated shot types across the episode.** If clip 1 is a wide telephoto, clip 2 cannot also be a wide telephoto. Check the full clip list before writing each motion prompt — vary distance, angle, and creature behavior.

- **Avoid fast motion** — documentary wildlife is slow, heavy, deliberate. Use: "moves slowly", "breathes deeply", "turns its head gradually".
- **CTA-in-scene clip:** do not ask Kling to generate or rewrite sign text. Animate only the creature's slow approach, stop, and presentation of the already-visible white card; preserve the NB2 lettering and keep the card facing the lens.
- After generation: audio is embedded in the MP4. Pass local paths to Editor.
- General rules — `rules/roles/animator.md`

### Sound

- **Speech:** use intentional native speech when supported → Chatterbox only with an approved narrator sample owned by this resolved `wild-documentary` bible → otherwise MiniMax. The current bibles resolve to MiniMax `Deep_Voice_Man`, speed `0.90`, emotion `neutral`.
  - Retry the same route/settings once on a technical failure, then STOP; no provider or local fallback.
  - Upload to Supabase as `tts-narration.mp3`
- **Segmentation for Editor:** provide a `tts_segments.json` with per-clip word counts and estimated timestamps so Editor can align narration to clips. Rough formula: ~0.45s per word at speed 0.90.
- **No background music** (default). If the user explicitly requests it: ambient nature underscore generated via MiniMax (instrumental) at vol 0.05 maximum.
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

- Still scenes: the clip is already 1080×1920, 30fps and exactly `duration_sec` (never trim it) and has **no audio stream**, so `[K-1:a]volume=0.20` does not exist for it: give that slot an `anullsrc` of its length instead (`anullsrc=r=48000:cl=stereo,atrim=duration=<clip length>`, `rules/roles/editor.md` "Still-shot clips").

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
- **No drawtext replacement for the sign** — the handwritten sign exists in the NB2/Kling visual. Never burn its wording as drawtext or subtitles, and never replace a misspelled card in Editor.
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

#### CTA sign and asset rule

The last generated creature clip carries the in-scene handwritten sign. Resolve its exact `sign_text` and the appended standard asset only from the exact story bible's top-level `cta` object. Never fall back to another game's bible, the game config, a special file, or a global phrase. If either value is missing or the standard asset is invalid, STOP and report the configuration error; do not synthesize a replacement end card.

- General rules — `rules/roles/editor.md`

---

## Output files

```
${OUTPUT_DIR}/
├── storyboard.json
├── tts-narration.mp3
├── tts_segments.json             # per-clip word counts + estimated timestamps
├── scenes/
│   ├── refs/
│   │   └── {creature}-ref.png    # one creature ref, reused across all clips
│   ├── scene-1/
│   │   ├── scene-1.png           # start frame only
│   │   ├── scene-1.mp4           # Kling output (audio embedded), or a silent still-shot clip
│   │   ├── scene-1-kling.wav     # extracted Kling audio (animated scenes only)
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
- [ ] Exactly ONE `creature_name` across all clips (episode is single-species); it is not already in the story bible's `covered_creatures`
- [ ] Creature anatomy comes from authoritative research; source-image inspection occurred only if genuinely necessary
- [ ] All scene image_prompts include explicit creature feature description (horns, armor, fur, color)
- [ ] All scene generations use the same format-bound creature ref; no cross-format image is used
- [ ] `character_speech: null` for ALL clips (no lipsync anywhere)
- [ ] All image prompts declare 9:16 and the locked photorealistic wildlife style; generated files pass technical decode/dimension checks
- [ ] No two clips with identical shot type (camera distance + creature pose)
- [ ] All Kling clips generated with `generate_audio: true`
- [ ] Still scenes (if any, preferably at most one) were planned in Phase 1, have `scene_video_kind: "still"`, numeric `duration_sec` and no audio stream, and stay within the `rules/roles/scenarist.md` "Still shots" cap; every other clip is a Kling v3 Standard clip
- [ ] Every Kling motion prompt includes `"no face morphing, no facial deformation, anatomy stable throughout"`
- [ ] Wide/medium shots: head locked in motion prompt, motion on body + environment
- [ ] Kling ambient audio attenuated to vol 0.20 in final mix; still scenes get a silent `anullsrc` slot
- [ ] TTS narration continuous (not cut per-clip), audible — RMS > -30 dB
- [ ] `atempo` applied to TTS: `TTS_DUR / VID_DUR` in range 0.95–1.10
- [ ] ASS subtitles — universal whisper style (editor.md §6), text matches the narration
- [ ] Last generated creature clip has `cta_in_scene: true`, the creature approaches/presents the white card, and the card contains the exact resolved `sign_text`
- [ ] Sign text comes from the NB2 start frame and is preserved by Kling; no drawtext/subtitle replacement is burned in Editor
- [ ] No speedup on video — `ffprobe duration` ≈ sum of clip durations
- [ ] No two adjacent clips with same camera distance AND same lighting
- [ ] Narrator gives only a brief observational reaction to the CTA sign; the creature never speaks
- [ ] Title overlay filter event is configured for 0–4s with Line 1 = `"{GAME_WORLD} DOCUMENTARY"` and Line 2 = creature name
- [ ] Standard CTA clip from Supabase appended after creature clips
- [ ] No AI Vision or machine visual inspection runs on generated media; the user performs any visual review during debug

---

## Anti-patterns

- ❌ Multiple different creatures/species in one episode — this format is ONE creature per video across 4–5 clips of different behaviors; do not mix in extra species to "fill" clip slots. Burned 2026-08-04: manager asked Scenarist for 3 different creatures (Horta, Denevan parasite, Sehlat) in a single episode when the story bible's own precedent (EP1 Targ, EP2 Mugato) and this file's structure are single-creature-per-episode.
- ❌ Game-art style NB2 images (cartoon proportions, smooth skin, bright colors) — requires photorealism
- ❌ Creature looks like a cartoon/game asset pasted into a background — use film grain (ISO 3200), describe glow casting light on surroundings, "no cartoon shading, no cel shading, no flat colors" in negative prompt; lead prompt with RAW/Canon/ISO specs. A smooth glowing orb or spirit is fine — it just must interact with the environment realistically (cast light, catch in haze, be partially occluded by foreground)
- ❌ Perfect studio lighting — always "natural ambient light only, no studio lighting, uneven exposure"
- ❌ Creature too large / dominant in wide shots — should occupy 5–15% of frame height in establishing shots; let environment be primary
- ❌ Creature placed in the bottom quarter of the frame — subtitles burn into that zone; always specify "creature at mid-frame, center of image, not near bottom edge" in image_prompt
- ❌ Not overriding game config style — for stylized games (Pokémon GO etc.) MUST add `style_override` to storyboard
- ❌ Vague creature description in image_prompt — write every feature explicitly (horn shape, armor texture, fur color, body proportions). "A Sumpter Beast" without description = NB2 invents a random animal
- ❌ Skipping creature research — always read authoritative textual sources; inspect a source image only when the permitted necessity condition above is met. Never rely on training data alone
- ❌ Chain refs scene-to-scene or assets from another format — use one format-bound creature ref for all shots
- ❌ Face morphing in Kling — must add `"no face morphing, no facial deformation, anatomy stable throughout"` to EVERY motion prompt
- ❌ Putting motion budget on the face in wide/medium shots — lock the head, animate the body and environment
- ❌ Same shot type repeated — no two clips with identical camera distance + creature pose. Vary: wide telephoto → extreme close-up → dramatic action → CTA trail cam
- ❌ Generic title overlay ("Wildlife Documentary") — use in-universe world name: "TEYVAT DOCUMENTARY", "KANTO DOCUMENTARY" etc.
- ❌ `generate_audio: false` — ambient sounds are the atmosphere; silence kills the format. A planned still scene is the only silent exception; prefer at most one
- ❌ Cutting TTS per-clip — severs words at clip boundaries; use ONE continuous TTS over full concat
- ❌ Skipping atempo normalization — TTS duration ≠ video duration; without atempo the narration is cut or runs long
- ❌ Manual ASS generation with `--text`/`--atempo`/`--style` — those flags are removed; Editor does it universally via whisper
- ❌ Using local ffmpeg (`/usr/local/bin/ffmpeg`) for subtitle burn — it lacks libfreetype; use `ffmpeg-full`
- ❌ Burning the sign wording as drawtext/subtitles — it must be part of the NB2 start frame and preserved through Kling
- ❌ Asking Kling to generate or correct readable sign text — Kling animates the existing card; NB2 owns the lettering
- ❌ Sending multi-prompt as `"multi_prompt[0]: ... multi_prompt[1]: ..."` string to Kling — not parsed; write one unified prompt
- ❌ Kling prompt over 512 serialized UTF-8 bytes — rejected at deferred validation
- ❌ Polling Kling at `.../v3/standard/image-to-video/requests/{ID}/status` — returns 405; use `.../kling-video/requests/{ID}/status`
- ❌ Two adjacent clips with same camera distance + same lighting — causes jump cut
- ❌ All scenes in same micro-environment — visual monotony; vary distance, light, specific location
- ❌ Speedup applied to video — documentary pace is deliberate
- ❌ Narrator exclamatory or excited — hushed, factual, reverent only
- ❌ `-shortest` in FFmpeg (always use `apad`)
- ❌ Character ref directly as scene image
