---
ready_to_post: yes
subtitles: false
overlays: false
---

# Format "Dual-Style" — cartoon + realistic

In one frame: cel-shaded anime-style game character (accurate in-game proportions by default, chibi only if explicitly requested) next to its photorealistic human "twin". Style contrast is the main device.

This file is the **playbook**. Craft rules (NB2, Kling I2V, ffmpeg) — in `rules/roles/*.md`.

This playbook is game-agnostic — every rule below applies identically whether the game is Genshin Impact, Star Trek Timelines, or any other title. Never reference a specific past episode, game, or date as the authority for a rule; state the rule itself so it transfers cleanly to any game/format run.

---

## When to use

Keywords: "dual-style", "game vs reality", "meet your character IRL", cosplay content, "which character are you".

---

## Pop-up promo banner (user override — `overlays: false` by default, opt-in per episode)

When the user asks for a promo/pop-up banner on a specific clip (e.g. "поп-ап баннер на клипе N сверху"), add ONE `overlays[]` entry of `type: "image"` to that scene only in storyboard.json — see `tools/overlays.py` schema. Sizing convention:
- **Large, not a small corner badge** — `width = canvas_width - 60` (1080 - 2×30, i.e. 30px side margin each side), `height: -1` (keep aspect ratio).
- `position: "top-center"` — centers automatically at that width, giving the 30px side margins for free; default top margin is 80px (baked into `_img_pos_to_xy`). For a non-80px top margin, use explicit `"{x},{y}"` instead (x = side margin, so it still centers for the given width).
- `enable: [t0, t1]` with `fade_in`/`fade_out` ≈0.5s so it reads as a pop-up, not a static overlay for the whole clip.
- If both figures fill most of the frame height, keep the banner narrower than full width and anchored to the very top edge so it doesn't cover either figure's head — confirm placement against the actual scene composition rather than assuming the default margin is safe.

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

### 0. Locked template — the primary method, do not re-derive from theory

A confirmed-working structure exists for this format. When results regress, copy this template's literal shape back verbatim rather than inventing a new prompting theory — the format has been through several rounds of "improvements" that measurably made likeness *worse* (denser prompts, then overly sparse prompts, contradictory motion instructions). The fix each time was reverting to this shape, not adding something new. Only the per-episode inputs (character/actor names, costume, environment) change; the structure does not.

**Character card (`visual_identity.characters.{Name}`) — exact shape, do not add more than this:**
```
"cartoon": "{Name} in anime cel-shaded style, accurate to in-game proportions, NOT chibi, NOT deformed, NOT exaggerated head-to-body ratio — normal in-game adult body height and proportions matching {his/her} actual in-game model. {2-3 costume/prop details straight off the canonical ref, no more}, bold black outlines, bright flat saturated anime colors, {one expression phrase}, {one build phrase}.",
"realistic": "photorealistic {Actor Name} as {Name}, {actor's REAL skin tone}, {actor's REAL eye color}, {actor's REAL distinguishing facial feature — cheekbones/jawline/etc}, {build}, wearing the identical {same 2-3 costume details}, {hair color} wig styled to match exactly, holding a matching {prop}, real skin textures, natural skin pores, cinema quality lighting, NOT anime, NOT cartoon, NOT illustrated."
```
The **realistic** line leads with the actor's own real physical features (skin tone, eye color, face shape) BEFORE costume. This is the one concrete, tested difference between working and failing attempts: prompts that jump straight to "wearing a matching X" without ever naming the actor's actual face lose likeness — NB2 has nothing to anchor identity to except the (cartoon) reference image, so it drifts toward that. Naming the real face first gives the model an explicit identity target.

**image_prompt — exact shape, keep it this short (~100-120 words):**
```
Single continuous photograph, one seamless frame, no split screen, no diptych, no dividing line: two figures share one {environment, one short phrase} under {lighting, one short phrase}. Left: {Name}, anime cel-shaded style, bold black outlines, bright flat saturated colors, accurate adult in-game body proportions — NOT chibi, NOT deformed, NOT exaggerated head-to-body ratio, normal head size, normal full adult height matching {his/her} real in-game model — {2-3 costume details}, {expression}. Right, beside {him/her}: {Actor Name} as {his/her} photorealistic real-life twin, live-action photograph, real skin textures, natural pores, cinema lighting, NOT anime, NOT cartoon, identical {same 2-3 costume details}, same {expression}. Mirrored {pose} stance, {camera_angle} camera, vertical 9:16. Keep facial features, body proportions and costume from the reference image exactly consistent — no chibi, no cartoon exaggeration.
```
Do NOT itemize every accessory (headpiece, hairpin, tassel, weapon guard shape, etc.) — 2-3 signature details only, chosen from the canonical ref. Longer, denser prompts measurably hurt likeness in production testing; the reference image itself carries the full design fidelity, the text only needs to lock a couple of anchor details plus the actor's identity.

**negative_prompt (image generation) — reuse verbatim:**
```
blur, distort, merged characters, single character, text overlay, watermark, anime style on right figure, cartoon right side, cel-shaded right side, illustrated right figure, anime on both sides, chibi, deformed proportions, exaggerated head size
```

**Animator motion_prompt — exact shape, ALWAYS walking + dolly-back, regardless of what the scene's narrative pose says:**
```
Front camera dollies back as both walk toward it, centered and facing lens. {Anime role} left and @Element1 photoreal right walk in measured sync at equal camera distance. Faces locked forward: no head, eye, expression or identity change; no morphing. Only legs, fabric, natural hair and {particles} move. DIEGETIC AMBIENCE ONLY. NO MUSIC: no beat, melody, instruments, score or soundtrack.
```
**This is mandatory verbatim structure, not a suggestion, and there is no "static/subtle" variant** (see §Face stability below) — every clip walks toward camera with a dolly-back retreat, full stop. If Scenarist wrote a non-walking action_description (standing, sitting, mid-swing), Animator still converts it to this walking template for the motion_prompt — the narrative pose is the STARTING silhouette, not the final motion. Never instruct Animator to keep motion "subtle" or "static" for any scene; that directly contradicts this mandatory pattern and produces motionless clips.

Before preflight, measure the final substituted prompt as UTF-8 bytes (`len(prompt.encode("utf-8"))`), not character count. Hard-require **≤400 bytes** to retain margin below Kling `multi_prompt[].prompt`'s 512-byte provider limit; a near-limit prompt can pass a character-count check and still fail at deferred result fetch.

**Kling negative_prompt — reuse verbatim:**
```
blur, distort, deformed, extra limbs, extra fingers, morphing face, smoothing facial features, changing skin color, altering proportions, banding in blacks, posterization, harsh color shift, overexposed clipping, running, jogging, sprinting, split screen, dividing line, merged characters, single character, anime style on right figure
```
(`running, jogging, sprinting` keep the walk at a measured stride, not a run.)

**Environment:** a plain minimalist studio-floor segment (unified accent color per character, no complex scenery) is the tested-safe default. Richer/atmospheric environments are an available opt-in when the user asks for them, but treat them as a separate untested variable from the rest of this template — if likeness or composition regresses on a richer-environment episode, isolate that variable (try reverting to plain floor with everything else unchanged) before concluding the template itself is broken.

**Storyboarder ref policy:** use a single canonical reference image (see §Storyboarder role brief) as the sole chain-ref — no separate two-figure "cartoon + actor together" pre-generation step is needed by default; it adds cost and has not been shown to be necessary when the rest of this template is followed.

### 1. Style isolation markers (mandatory)

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
- **Default: accurate in-game body proportions on the cartoon side — NOT chibi.** A default chibi/exaggerated-proportions template can drift far enough from the real character design to be rejected outright. Chibi/deformed proportions are opt-in only, on explicit user request — never the default.
- **Do NOT force matching heights between the two figures.** Each figure keeps its OWN natural proportions: cartoon side = the character's accurate in-game proportions (petite/tall/whatever the character actually is); photorealistic side = the actor's own real natural adult height and build. Contrast comes from render style (cel-shaded vs photorealistic) and from each figure being true to its own source (game model vs real person), not from forcing one figure's scale onto the other. Shrinking an adult actor to match a petite/child-coded character's proportions reads as a dwarf/child, not a stylistic contrast.
- `character_description` (cartoon) and `image_prompt` must state explicitly: "accurate to in-game proportions, NOT chibi, NOT deformed, NOT exaggerated head-to-body ratio" for the cartoon side, and "actor's own natural real-world height and build, NOT scaled/shrunk/aged to match the character" for the photorealistic side. Add `chibi, deformed proportions, exaggerated head size, actor shrunk to child size, actor scaled to match character height` to `negative_prompt`.
- Anchor cartoon fidelity to the character's chain-ref `sheet.png` (face/costume/silhouette) rather than letting the prompt override what the reference image shows.

### 5. Single shared space — no panel divide (mandatory)

Both versions must occupy **one continuous environment**. A visible dividing line or split-panel effect means the prompt used positional language ("on the left half / on the right half") that forced the AI into a diptych layout.

**WRONG — causes split panels:**
> "on the left [anime character] …, on the right [realistic character] …"

**CORRECT — shared space:**
> "[anime-style character] stands side by side with their photorealistic counterpart in [unified environment], both sharing the same continuous space, no dividing line"

The environment description, lighting, and ground plane must be written as **one scene** that both figures inhabit together. The positioning words `left` / `right` may still appear to anchor each figure within the description, but the scene framing must never imply two separate panels or halves.

### 6. Actor-as-realistic counterpart (optional)

Instead of a generic photorealistic human, the realistic side can depict a **specific real-world actor** who resembles the character and could play them in a live-action film. This dramatically increases virality.

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

---

## Storyboard extensions

```json
{
  "format": "dual-style",
  "visual_identity": {
    "character_description": {
      "cartoon": "[Name] in anime cel-shaded style, accurate to in-game proportions, NOT chibi, NOT deformed, NOT exaggerated head-to-body ratio — normal in-game adult body height/proportions matching the real in-game model. [2-3 costume/prop details from the canonical ref, no more], bold black outlines, bright flat saturated anime colors, [one expression], [one build phrase].",
      "realistic": "photorealistic [Actor Name] as [Name], [actor's REAL skin tone], [actor's REAL eye color], [actor's REAL distinguishing facial feature], [build], wearing the identical [same 2-3 costume details], [hair color] wig styled to match exactly, holding a matching [prop], real skin textures, natural skin pores, cinema quality lighting, NOT anime, NOT cartoon, NOT illustrated. — see §0 locked template, reuse verbatim shape"
    },
    "environment_description": "[concrete location]",
    "style_tags": "cartoon cel-shaded with bold black outlines, photorealistic human counterpart, dual-style side by side",
    "color_palette": "[one palette for both versions]",
    "lighting": "[unified lighting across all scenes]"
  },
  "sfx": false,
  "scenes": [
    {
      "index": 1,
      "character_speech": null,
      "negative_prompt": "blur, distort, merged characters, single character, text overlay, watermark, anime style on right figure, cartoon right side, cel-shaded right side, illustrated right figure, anime on both sides, chibi, deformed proportions, exaggerated head size",
      "image_prompt": "[see §0 locked template — compact, ~100-120 words, 2-3 costume details per figure]",
      "motion_prompt": "[see §0 locked template — mandatory walking + dolly-back, never static]"
    }
  ]
}
```

- `style_tags` must include **both** styles
- `lighting` / `color_palette` identical across all scenes
- `image_prompt` follows §0's compact shape, not an exhaustive accessory inventory

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
- `negative_prompt`: use the §0 locked list verbatim
- General rules — `rules/roles/scenarist.md`

### Storyboarder
- **Source ref, preferred order:**
  1. **First choice: the canonical game-wide `reference_image` for that character (untagged / no format tag) if one exists in `game_assets`.** This is the artist-accurate design source — anchor the cartoon-side `image_prompt` and NB2 chain-ref to it directly. This is a standing, format-specific exception to the general "refs never cross formats" rule, authorized for dual-style.
  2. If no canonical game-wide ref exists, use an existing dual-style-tagged asset for that character if one exists.
  3. Only if neither exists, generate a fresh dual-style-bound cartoon anchor from text — and in that case, do NOT write any distinctive design detail (hair color/style, signature accessories, outfit colors) from memory/assumption. Guessing well-known design facts from memory has repeatedly produced wrong results (wrong hairstyle, wrong hair color) even for well-known characters. If no canonical ref exists to anchor to, that is a signal to ask the user for a source image rather than proceed on memory.
- **Whenever a canonical or dual-style ref IS used (the normal case, options 1-2 above): only pull 2-3 signature costume/hair details into the character card and image_prompt per the §0 locked template — do not itemize every accessory visible in the reference image.** The reference image itself, passed as the actual chain-ref to NB2, carries the full design fidelity; the text prompt's job is to name the character/actor and lock 2-3 anchor details, not to describe the whole outfit.
- Borrowing a ref from another *format's* dedicated tagged asset (e.g. a `redcon`-tagged or `serial-drama`-tagged variant) still requires explicit user instruction — only the canonical untagged game-wide ref is pre-authorized for reuse.
- **Multi-character:** every new character starts the chain anew (do NOT pass the previous character's scene)
- For one character: scene 1 = `[asset]`; scene 2+ = `[asset, scene-(K-1)]`
- **Face-lock headshot (mandatory side-asset, every character pairing, every episode):** after the scene PNG is accepted, generate ONE additional frontal headshot crop of the photorealistic figure via NB2 edit, using the already-rendered scene PNG as the image reference (not a fresh text-only generation) — the headshot must match the exact identity already locked in that scene, not a new likeness. Plain neutral background, head+shoulders, facing camera, neutral expression. Upload as a per-episode asset (`episode-scene` kind), not `game_assets`. Cost ≈$0.04–0.08.
- General rules — `rules/roles/storyboarder.md`

### Animator
- **Kling v3 Standard I2V**, `aspect_ratio: "9:16"`
- `duration`: "5" or "10"; without `end_image_url`
- `character_speech: null` → Kling does not receive speech text
- One model for the whole video
- **`generate_audio: true` risk — unwanted music.** Kling can add a score even when the intended output is ambient SFX. Every motion prompt must end with the exact strong clause from §0: `DIEGETIC AMBIENCE ONLY. NO MUSIC: no beat, melody, instruments, score or soundtrack.` Avoid `cinematic`, `epic`, `dramatic`, `trailer`, and rhythm/tempo language in Kling-facing text. If Kling still bakes music into an individual clip, Editor must mute that clip's native audio before mixing the separately generated `bg-music.mp3`; never stack the accidental score under the intended track.
- **Face stability — one mandatory pattern, no exceptions:**
  - **Macro-motion (walking toward camera) with `elements` face-lock is the only supported pattern — see the §0 locked template's motion_prompt and reuse it verbatim, substituting only names/details.** Requires the Storyboarder-generated frontal headshot passed as `elements[0].frontal_image_url`, with the scene PNG as `reference_image_urls`. **`elements` is mandatory-paired with `multi_prompt: true`** — passing `elements` with a bare top-level `prompt` causes a deferred 500 at result-fetch (`rules/roles/animator.md` §4). Reference the bound face as `@Element1` in the shot prompt; still state the explicit face-lock clause (no head turn/no morphing) even with `elements` — the binding reduces drift, it does not by itself guarantee zero motion.
  - **No "keep it static/subtle" override, ever, for any scene, regardless of the narrative pose Scenarist wrote.** Every clip walks forward into a dolly-back retreat per the §0 template; there is no static variant. An instruction to keep motion "subtle" for an idle-stance scene directly contradicts this pattern and produces motionless statue clips.
  - Every episode requires the Storyboarder-generated frontal headshot side-asset for every character pairing — do not skip it.
  - **Camera direction for walking shots — camera must be IN FRONT of the figures (receding/dolly-back tracking, retreating at their walking pace), never behind.** The whole point of dual-style is comparing the two faces side by side; a behind-the-figures tracking shot shows only backs/backs-of-heads and defeats the format.
  - Use the exact Kling `negative_prompt` list from §0 verbatim.
- General rules — `rules/roles/animator.md`

### Sound
- TTS **not needed** (no speech)
- **SFX defaults to `false`.** When Animator uses `generate_audio: true` (native Kling ambient sound baked into every clip), a separate per-scene CassetteAI SFX layer is redundant — the ambient sound is already covered. Only set `sfx: true` if the user explicitly asks for an extra distinct SFX layer on top, or if `generate_audio: false` is used for this episode (no native ambient audio at all).
- **SFX per scene via CassetteAI on fal.ai** (only when `sfx: true` is explicitly set in storyboard.json):
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
${OUTPUT_DIR}/
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
- [ ] Realistic character card names the actor's REAL physical features (skin tone, eye color, distinguishing facial feature) BEFORE costume details — not costume-only description (see §0 locked template)
- [ ] image_prompt is compact (~100-120 words, 2-3 costume details per figure) — not an exhaustive accessory inventory
- [ ] Every distinctive design detail (hair color/style, signature accessories) is sourced from an actual canonical/dual-style reference image, never invented from memory
- [ ] Animator motion_prompt follows the §0 walking + dolly-back template verbatim — no "static/subtle" override regardless of the scene's narrative pose
- [ ] Camera is in front (dolly-back), not behind, for macro-motion shots; `elements` + `multi_prompt: true` used for face-lock (mandatory every episode); frontal headshot side-asset generated for every character pairing; no real actor name in motion_prompt
- [ ] Every Kling motion prompt ends with the exact strong diegetic-only/no-music clause and is ≤400 UTF-8 bytes after substitutions
- [ ] If a clip still contains accidental Kling music: Editor mutes that clip's native audio before mixing `bg-music.mp3`
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
- ❌ Forcing cartoon and realistic to the same height/scale — each keeps its own natural proportions (see §4); shrinking the actor to match a petite/child-coded character reads as a dwarf/child, not a stylistic contrast
- ❌ Defaulting to chibi/exaggerated proportions without an explicit user request — drifts from the real character design; state "accurate to in-game proportions, NOT chibi" in every cartoon `character_description`/`image_prompt`
- ❌ Camera positioned BEHIND the figures for a walking/macro-motion shot — hides both faces, defeats the format's core comparison device. Camera goes in front (dolly-back) for any shot where the figures move toward it.
- ❌ Passing Kling `elements` with a bare top-level `prompt` (no `multi_prompt: true`) — causes a deferred 500 at result-fetch, not an immediate error
- ❌ Real actor name in Animator/Kling-facing motion_prompt text — Kling doesn't parse identity from names; use `elements`/the image for likeness, describe the figure only by role/position in motion_prompt
- ❌ `generate_audio: true` with an energetic/cinematic motion_prompt and no anti-music clause, when a separate `bg-music.mp3` already exists — Kling may bake in its own unwanted score on top
- ❌ Counting prompt characters instead of serialized UTF-8 bytes — near-limit `multi_prompt` text can fail only at result fetch; enforce ≤400 bytes before preflight
- ❌ Mixing an accidental Kling score beneath the intended `bg-music.mp3` — mute the contaminated clip audio first
- ❌ `character_speech ≠ null` (Kling I2V does not generate voice)
- ❌ `-shortest` in ffmpeg
- ❌ Re-deriving the prompt method from theory instead of copying the §0 locked template verbatim — trying successive unverified "fixes" without a controlled comparison against a known-working example tends to make likeness worse, not better. When something worked before, copy its literal structure first; only vary per-episode names/details.
- ❌ Instructing Animator to keep motion "static/subtle" for any scene — contradicts the mandatory walking + dolly-back pattern (see §0 and Animator brief) and produces motionless statue clips
- ❌ Inventing hair color/style or costume details "from known character facts" without an actual reference image to check against — verify against a real canonical/dual-style asset every time
- ❌ Citing a specific past episode/game/date as the justification for a rule — state the rule itself; this playbook must transfer cleanly to any game

---

## Story Bible

Required path: `games/{GAME_TAG}/dual-style_story_bible.json`. If it is missing, Manager must stop and ask whether to create it; creation is allowed only after the user's explicit yes.

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

**Story Bible update (Manager, only after the user explicitly approves the local `final.mp4`):**

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
