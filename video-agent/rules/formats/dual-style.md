---
ready_to_post: yes
subtitles: false
overlays: true
---

# Format "Dual-Style" — one character, two canonical presentations

In one frame, two clearly related presentations of a character walk toward a front-facing retreating camera in one shared environment. The comparison may translate a stylized source character into live action, or compare an original live-action persona with its canonical alternate. Both are the same format and production pipeline.

This file is the **playbook**. Craft rules (NB2, Kling I2V, ffmpeg) — in `rules/roles/*.md`.

This playbook is game-agnostic — every rule below applies identically whether the game is Genshin Impact, Star Trek Timelines, or any other title. Never reference a specific past episode, game, or date as the authority for a rule; state the rule itself so it transfers cleanly to any game/format run.

## Canonical contract and precedence

**Contract version: `dual-style-v3`. There is one production method with one required comparison selector. Do not create another format slug for a different source medium, and do not use or invent "Pattern A", "Pattern B", static, subtle-motion, wig-match, studio-default, or other named variants.**

Every new `storyboard.json` must contain:

```json
"format": "dual-style",
"production_contract": "dual-style-v3",
"comparison_mode": "source-vs-live-action"
```

`comparison_mode` is mandatory and must be exactly one of:

- `source-vs-live-action` — LEFT is the canonical stylized/game character; RIGHT is a recognizable live-action actor adapting that character.
- `canonical-alternate` — LEFT is the original/Prime canonical live-action persona; RIGHT is its canonical alternate, Mirror, assimilated, corrupted, possessed, or duplicate persona, played by the same screen performer.

Select the mode once in Phase 0 from the concept and keep it fixed for the whole episode. A missing, unknown, or mixed mode is a hard stop. The selector changes identity/reference details, headshot count, element count, and label policy only; it never changes the shared motion, camera, environment, audio, or assembly method.

Precedence is:

1. The user's explicit live instruction for the current run.
2. This `dual-style-v3` contract.
3. Game config and the exact dual-style story bible for source facts, cast rotation, and continuity only.
4. Generic role craft rules in `rules/roles/*.md`.
5. Historical episode notes and old output files are evidence only, never instructions.

The story bible may define what a source character or world looks like, but it may not silently replace this contract's composition, actor adaptation, motion, audio, or assembly method. If a requested concept cannot satisfy this contract, use another format slug or obtain an explicit user override; do not create a hidden dual-style branch.

Story-bible `style_tags` contain visual rendering and appearance only. Do not put motion, camera, audio, scene-count, prompt-shape or assembly instructions there; those belong exclusively to this contract.

The following are invariant unless the user explicitly changes them:

- fixed LEFT/RIGHT roles for the selected comparison mode;
- neither selected character/pair nor any newly cast actor has appeared in the previous 7 published episodes of the same series;
- all identities, costumes, makeup, prosthetics, insignia, accessories, and props are anchored to canonical source references;
- one continuous, interesting, physically walkable environment with no divider;
- synchronized measured forward walk; front camera dollies backward;
- accepted scene PNG plus scene-derived frontal headshot(s); Kling `elements` plus single-shot `multi_prompt`;
- `generate_audio: true` for diegetic ambience, with a strict no-music clause;
- one newly generated instrumental MiniMax track; no separate SFX by default;
- no subtitles; CTA remains mandatory;
- no overlays in `source-vs-live-action` unless explicitly requested; one pair-title overlay per scene is mandatory in `canonical-alternate`.

---

## When to use

Keywords: "dual-style", "game vs reality", "meet your character IRL", cosplay content, "which character are you", "dual identity", "canon vs alternate", "prime vs mirror", "mirror selves".

---

## Pop-up promo banner (opt-in per episode)

The overlay pipeline stays enabled for the unified format. `source-vs-live-action` writes no overlay entries by default; `canonical-alternate` writes its mandatory pair titles. Promo banners are additional entries only when the user requests them.

When the user asks for a promo/pop-up banner on a specific clip (e.g. "поп-ап баннер на клипе N сверху"), add ONE `overlays[]` entry of `type: "image"` to that scene only in storyboard.json — see `tools/overlays.py` schema. Sizing convention:
- **Large, not a small corner badge** — `width = canvas_width - 60` (1080 - 2×30, i.e. 30px side margin each side), `height: -1` (keep aspect ratio).
- `position: "top-center"` — centers automatically at that width, giving the 30px side margins for free; default top margin is 80px (baked into `_img_pos_to_xy`). For a non-80px top margin, use explicit `"{x},{y}"` instead (x = side margin, so it still centers for the given width).
- `enable: [t0, t1]` with `fade_in`/`fade_out` ≈0.5s so it reads as a pop-up, not a static overlay for the whole clip.
- If both figures fill most of the frame height, keep the banner narrower than full width and anchored to the very top edge so it doesn't cover either figure's head — confirm placement against the actual scene composition rather than assuming the default margin is safe.

---

## Shared concept

- **Default: 3 clips × 5s**. An explicit user-requested pair/clip count replaces 3; always use exactly one pair per clip.
- **Model:** Kling v3 Standard I2V, `generate_audio: true`, `elements`, one-entry `multi_prompt`
- **Speech:** NO, `character_speech: null` everywhere
- **Music:** one new instrumental MiniMax Music v2.6 track is mandatory
- **Separate SFX:** `false` unless explicitly requested
- **Budget:** $5 max

---

## Structure

| Clip | Beat | Dur. | camera_angle |
|---|---|---|---|
| 1 | hook — first pair walks toward lens | 5s | frontal wide low-angle |
| 2 | development — next pair walks toward lens | 5s | frontal medium eye-level |
| 3 | climax — final default pair walks toward lens | 5s | frontal wide pull-back |

For user-requested additional clips, continue alternating frontal lens height/framing. Camera remains in front and retreats in every clip; a different `camera_angle` never authorizes a side, rear, orbit, or static camera.

Multi-character video: 1 clip = 1 pair (cartoon + realistic of one character), chain reference does **not** cross between different characters.

---

## `source-vs-live-action` mode

Use this mode only when the right side is a real-world adaptation of a stylized/game source character.

- LEFT: canonical source rendering, canonical proportions and height class.
- RIGHT: a specific recognizable actor keeping their real face, natural hair, natural adult height, natural build, and age.
- The right costume is a near-identical practical construction of the source design: preserve silhouette, panels, cutouts, color blocking, signature ornaments/armor/accessories, and prop while translating material physics.
- One scene-derived frontal headshot and one Kling element are required for the right actor.
- No pair-title overlay unless the user explicitly requests one.

### Key prompting rules

#### 0. Locked template — the only method

Only the per-episode inputs change: character, actor, source-backed costume anchors, particles, environment, lighting, and frontal framing. Do not rewrite the method from theory and do not recover an older method from output files.

**Character card (`visual_identity.characters.{Name}`) — exact semantic order:**
```
"cartoon": "{Name} in the canonical source-game rendering and canonical in-game height/proportions, not newly chibi-fied or rescaled. {4-6 source-backed silhouette/costume/prop anchors}. {source rendering markers}, {one expression phrase}, {one build phrase}.",
"realistic": "Recognizable photorealistic {Actor Name} as a live-action adaptation of {Name}: {actor's real skin tone}, {real eye color}, {real distinguishing facial feature}, {natural adult build}, and natural {real hair color/style/length}. Preserve the source costume's silhouette, panel layout, cutouts, color placement, signature ornaments, armor, accessories and props almost identically, rebuilt in believable practical materials. Keep the actor's real face, natural hair, natural adult height and build; no character-colored wig, no copied anime hairstyle, no shrinking or age change. Real skin texture and cinema-quality lighting; not anime, cartoon or illustration."
```

The realistic line always establishes the actor's real identity and natural body/hair before describing the adaptation. Fantasy anatomy that is indispensable to recognition, such as horns or animal ears, may be added as restrained practical prosthetics or a headpiece without replacing the actor's natural hair or face.

**Costume translation has one meaning:**

- preserve the full recognizable design and explicitly name 4–6 source-backed anchors: overall silhouette, major garment panels/cutouts, exact color blocking, signature armor/ornaments, essential accessory, and prop;
- translate only the material physics: tailored woven fabric, leather, suede, fur-texture trim, brushed metal, resin, jewelry, body paint, and restrained prosthetics;
- never reduce the adaptation to a palette-inspired outfit, generic couture, or a simplified cosplay;
- never copy the source character's hair color/style onto the actor.

**image_prompt — exact semantic order:**
```
One seamless shared environment with no split screen, diptych, panel border or dividing line. Describe a broad, flat, dry, unobstructed walking lane extending toward the front camera and behind both figures; put hazards, walls, props and scenery safely to the sides. LEFT only: canonical {Name} from the attached source reference, in the source-game rendering with canonical height/proportions and complete source-backed design. RIGHT only: recognizable photorealistic {Actor Name} with real face, natural hair, natural adult height/build, wearing the near-identical practical costume construction defined in the character card. Both stand side by side on solid ground, fully visible, with matched starting stance and enough clear floor for a forward walk and camera retreat. {frontal camera_angle}, unified face lighting, vertical 9:16.
```

The prompt must be complete enough to lock identity, costume construction, and walkable staging without cataloguing every micro-accessory. The attached canonical reference carries fine design detail; text names the 4–6 anchors that must survive. There is no legacy 100–120-word target.

**negative_prompt (image generation) — reuse verbatim:**
```
blur, distort, merged characters, single character, text overlay, watermark, split screen, diptych, dividing line, anime style on right figure, cartoon right side, cel-shaded right side, illustrated right figure, anime on both sides, unintended chibi, deformed proportions, exaggerated head size, actor shrunk to character height, actor aged down, character-colored wig on actor, copied anime hairstyle on actor, generic palette-inspired costume, simplified costume, unsafe footing, cliff edge, narrow ledge, blocked walking path
```

**Animator motion_prompt — exact shape, ALWAYS walking + dolly-back, regardless of what the scene's narrative pose says:**
```
Front camera dollies back as both walk toward it, centered and facing lens. {source role} left and @Element1 photoreal right walk in measured sync. Faces locked forward: no head, eye, expression or identity change; no morphing. Only legs, fabric, natural hair and {particles} move. DIEGETIC AMBIENCE ONLY. NO MUSIC: no beat, melody, instruments, score or soundtrack.
```
**This is mandatory verbatim structure, not a suggestion, and there is no "static/subtle" variant** (see §Face stability below). Scenarist must write the forward walk into every `action_description`; if any scene instead declares standing, sitting, dancing, fighting, jumping or another action, return the storyboard for correction before spending on animation. Animator never chooses or silently converts between motion approaches.

Keep `{source role}` at ≤20 ASCII characters and `{particles}` at ≤24 ASCII characters. Before preflight, measure the final substituted prompt as UTF-8 bytes (`len(prompt.encode("utf-8"))`), not character count. Hard-require **≤400 bytes** to retain margin below Kling `multi_prompt[].prompt`'s 512-byte provider limit; a near-limit prompt can pass a character-count check and still fail at deferred result fetch.

**Kling negative_prompt — reuse verbatim:**
```
blur, distort, deformed, extra limbs, extra fingers, morphing face, smoothing facial features, changing skin color, altering proportions, banding in blacks, posterization, harsh color shift, overexposed clipping, running, jogging, sprinting, split screen, dividing line, merged characters, single character, anime style on right figure
```
(`running, jogging, sprinting` keep the walk at a measured stride, not a run.)

**Environment:** an interesting, source-world-specific location is the default. It must be staged as a real walking set: a broad level center lane, solid dry footing, several meters of clear floor in front of and behind the pair, a safe camera retreat corridor, and hazards or scenic features kept behind guards or several meters to the sides. Never place the pair on an exposed cliff edge, narrow ledge, broken bridge, water, lava, stairs, loose rubble, or a blocked path. A plain studio floor is allowed only when the user explicitly asks for it or explicitly approves it as a controlled recovery after a failed rich-background frame.

**Storyboarder ref policy:** use a single canonical reference image (see §Storyboarder role brief) as the sole chain-ref — no separate two-figure "cartoon + actor together" pre-generation step is needed by default; it adds cost and has not been shown to be necessary when the rest of this template is followed.

#### 1. Style isolation markers (mandatory)

The canonical chain-ref carries the source-game rendering — without explicit isolation, NB2 can apply it to BOTH figures.

**Left figure markers:** name the exact source rendering shown by the canonical reference, for example `anime cel-shaded`, `2D pixel art`, or `stylized 3D game render`. For anime/cel-shaded sources include:
- `anime cel-shaded style`
- `bold black outlines`
- `bright flat saturated colors`

**Right figure (realistic) markers — must be explicit and strong:**
- `photorealistic photograph`
- `live-action movie still`
- `real human being`
- `real skin textures, natural skin pores`
- `cinema quality lighting`
- `NOT anime, NOT cartoon, NOT illustrated`

**Style isolation in image_prompt (mandatory):**
Explicitly bind each style to its side using the phrase:
> `{exact source-game rendering} on the LEFT figure only, photorealistic live-action style on the RIGHT figure only`

**Negative prompt must include:**
> `anime style on right figure, cartoon right side, cel-shaded right side, illustrated right figure, anime on both sides`

#### 2. Connection between versions
- Near-identical costume design: same silhouette, panels, cutouts, exact color placement, signature ornaments/armor/accessories and props; only material physics become live-action practical
- Matched starting stance and forward-walking direction
- Actor identity stays real: natural hair, face, age, height and build do not copy the source character

#### 3. Positioning
- Anime/cartoon version **always** on the left, realistic **always** on the right (or fixed the other way around — one decision for the whole video)
- `side by side`, not one behind the other

#### 4. Sizes in frame
- **Cartoon/source side keeps the canonical source proportions and canonical height class.** Do not turn a normally proportioned source character into chibi, and do not enlarge a canonically small/chibi character into an adult body.
- **Do NOT force matching heights between the two figures.** Each figure keeps its OWN natural proportions: cartoon side = the character's accurate in-game proportions (petite/tall/whatever the character actually is); photorealistic side = the actor's own real natural adult height and build. Contrast comes from render style (cel-shaded vs photorealistic) and from each figure being true to its own source (game model vs real person), not from forcing one figure's scale onto the other. Shrinking an adult actor to match a petite/child-coded character's proportions reads as a dwarf/child, not a stylistic contrast.
- `character_description` and `image_prompt` must state "canonical source-game height and proportions, not rescaled" for the source figure and "actor's own natural adult height and build, not scaled, shrunk, enlarged or aged to match the character" for the photorealistic figure.
- Anchor cartoon fidelity to the character's chain-ref `sheet.png` (face/costume/silhouette) rather than letting the prompt override what the reference image shows.

#### 5. Single shared space — no panel divide (mandatory)

Both versions must occupy **one continuous environment**. A visible dividing line or split-panel effect means the prompt used positional language ("on the left half / on the right half") that forced the AI into a diptych layout.

**WRONG — causes split panels:**
> "on the left [anime character] …, on the right [realistic character] …"

**CORRECT — shared space:**
> "[anime-style character] stands side by side with their photorealistic counterpart in [unified environment], both sharing the same continuous space, no dividing line"

The environment description, lighting, and ground plane must be written as **one scene** that both figures inhabit together. The positioning words `left` / `right` may still appear to anchor each figure within the description, but the scene framing must never imply two separate panels or halves.

#### 6. Actor-as-realistic counterpart (default)

The realistic side depicts a **specific publicly known, widely recognizable actor** who could plausibly play the character in a live-action adaptation. A generic person is allowed only by explicit user instruction.

**Game config:** the `(realistic counterpart)` block must then describe the actor's real appearance + the character's costume:
```
### Hero Name (realistic counterpart)
`recognizable photorealistic [ACTOR NAME], [actor's real physical features: complexion, build, eye color, face structure, natural hair], wearing a near-identical practical construction of [CHARACTER COSTUME], [emotion matching the source figure]`
```

**Scenarist:** `action_description` must name the actor explicitly: "…her photorealistic counterpart, played by [Actor Name], stands…"

**Rules:**
- Only use publicly known actors — no private individuals
- **Prefer widely recognized, A-list/globally famous actors over lesser-known ones** — virality scales with name/face recognition; when choosing between two plausible look-alikes, pick the more famous one.
- Reject any actor or source character present in the previous 7 episode summaries of the exact series before writing the storyboard
- The actor's costume must be a near-identical practical construction of the game design, preserving its silhouette, panels, color blocking, signature accessories and weapon
- The actor keeps natural hair color/style/length; never use a character-colored wig or copied anime hairstyle
- The actor keeps natural adult height/build even when the source character is small or chibi
- Do NOT alter the actor's face (no heavy makeup or distortion in the prompt)
- `style_tags`: add `live-action cast, [Actor Name] as [Character]`
- **Actor names are for Scenarist/Storyboarder prompts only (image generation) — never pass a real person's name into Animator/Kling-facing text** (motion_prompt, elements prompt reference). Kling doesn't parse identity from names; describe the photorealistic figure only by role/position ("the photorealistic figure on the right") and let the image itself (start frame + `elements` face-lock) carry the likeness.

---

## `canonical-alternate` mode

Use this mode when the source franchise is already live action and both sides are official screen personas of the same character.

- LEFT: the original/Prime canonical screen persona.
- RIGHT: a canonical alternate, Mirror, assimilated, corrupted, possessed, or duplicate persona.
- Both figures use the same recognizable canonical screen performer. There is no fancasting and no unrelated Hollywood actor.
- Each persona follows its own canonical hair, facial hair, makeup, prosthetics, uniform, accessories, insignia, and weapons. The natural-hair adaptation rule from `source-vs-live-action` does not apply because neither side is a newly cast adaptation.
- One accepted scene requires two frontal headshots derived from that same scene: left/original and right/alternate.
- Kling receives two `elements`, one for each persona, and the exact shared one-entry `multi_prompt`.

### Canonical reference policy

Preferred source order for each persona:

1. an exact series-owned `dual-style` reference;
2. an official canonical screen reference uploaded as a series-owned `dual-style` asset;
3. a fresh format-owned reference generated from a source-verified, style-free appearance card.

Never invent distinctive uniform, insignia, hairstyle, makeup, prosthetic, or weapon details from memory. Use 4–6 source-backed visual anchors per persona. The two derived headshots are per-episode assets, not reusable `game_assets`.

Character-card semantic order:

```text
"original": "Recognizable photorealistic {screen performer} as canonical {Original Name}: {source-backed face, hair, makeup/prosthetic, uniform, insignia, prop and build anchors}. Exact live-action screen persona, real skin and practical materials."
"alternate": "The same recognizable {screen performer} as canonical {Alternate Name}: same underlying face and adult proportions, with {source-backed alternate hair/facial hair, makeup/prosthetic, uniform/armor, insignia, accessory and prop anchors}. Exact live-action alternate persona, not a generic redesign."
```

Scene-prompt semantic order:

```text
One seamless shared live-action environment with no split screen, diptych, panel border or dividing line. Describe a broad level dry center aisle with several meters of clear floor ahead and behind both figures and a safe camera retreat corridor; keep consoles, rails, weapons, fire, debris and drops safely to the sides. LEFT only: canonical {Original Name} from the attached original reference. RIGHT only: canonical {Alternate Name} from the attached alternate reference, with the same recognizable screen performer but exact alternate costume/makeup. Both stand side by side, fully visible on solid ground, prepared to walk toward the frontal camera. {frontal framing}, unified face light, vertical 9:16.
```

Image negative prompt, verbatim:

```text
blur, distort, merged characters, single character, text overlay, watermark, split screen, diptych, dividing line, illustrated, cartoon, anime, game render, different actors, unrelated faces, face swap, matching uniforms, missing alternate details, generic redesign, deformed proportions, extra limbs, unsafe footing, cliff edge, narrow ledge, blocked walking path
```

Motion prompt, exact shape:

```text
Front camera dollies back as @Element1 original left and @Element2 alternate right walk toward it in measured sync, centered facing lens. Faces locked: no head, eye, expression or identity change; no morphing. Only legs, costume fabric, hair and {particles} move. DIEGETIC AMBIENCE ONLY. NO MUSIC: no beat, melody, instruments, score or soundtrack.
```

Keep `{particles}` at no more than 24 ASCII characters. Measure the final substituted prompt as UTF-8 bytes and require ≤400 bytes.

Kling negative prompt, verbatim:

```text
blur, distort, deformed, extra limbs, extra fingers, morphing face, changing identity, different actors, smoothing facial features, changing skin color, altering proportions, running, jogging, sprinting, split screen, dividing line, merged characters, single character, banding in blacks, posterization, harsh color shift, overexposed clipping
```

Exact provider payload:

```json
{
  "start_image_url": "{accepted permanent scene PNG URL}",
  "multi_prompt": [
    {
      "prompt": "{exact substituted canonical-alternate motion template, <=400 UTF-8 bytes}",
      "duration": "5"
    }
  ],
  "shot_type": "customize",
  "duration": "5",
  "aspect_ratio": "9:16",
  "generate_audio": true,
  "elements": [
    {
      "frontal_image_url": "{original_headshot_url}",
      "reference_image_urls": ["{same scene PNG URL}"]
    },
    {
      "frontal_image_url": "{alternate_headshot_url}",
      "reference_image_urls": ["{same scene PNG URL}"]
    }
  ],
  "negative_prompt": "{exact canonical-alternate Kling negative prompt}"
}
```

No bare `prompt`, no `end_image_url`, and no real performer name in Kling-facing text.

### Pair-title overlay — mandatory

Every scene displays:

```text
{ORIGINAL NAME} VS {ALTERNATE NAME}
```

Render it locally after scene generation; never ask the image model to draw text.

- top-center at a safe position checked against both faces;
- uppercase, bold condensed sans serif;
- original name white, `VS` warm gold, alternate name pale gold/white;
- subtle dark backing or stroke, never a full-width opaque banner;
- maximum 960px text width; shrink or use a balanced two-line layout rather than clipping;
- short 0.15–0.25s fade at the cut;
- never cover a face, key prosthetic, or CTA.

---

## Storyboard extensions

```json
{
  "format": "dual-style",
  "production_contract": "dual-style-v3",
  "comparison_mode": "source-vs-live-action",
  "visual_identity": {
    "character_description": {
      "cartoon": "[Name] in the canonical source-game rendering and canonical height/proportions, not rescaled. [4-6 source-backed costume/silhouette/prop anchors], [one expression], [one build phrase].",
      "realistic": "Recognizable photorealistic [Actor Name] as a live-action adaptation of [Name]: [real complexion], [real eyes], [real facial feature], [natural adult build], and natural [real hair]. Preserve the source costume almost identically in practical materials: [same 4-6 design anchors]. Keep the actor's real face, natural hair, natural adult height and build; no character-colored wig, copied anime hairstyle, shrinking or age change."
    },
    "environment_description": "[interesting source-world location with a broad level center walking lane, safe footing, clear camera retreat corridor, and hazards/scenery kept to the sides]",
    "style_tags": "source-game rendering on left only, recognizable photorealistic live-action actor on right only, near-identical practical costume construction, natural actor hair/height/build, one seamless shared environment",
    "color_palette": "[one palette for both versions]",
    "lighting": "[unified lighting across both figures in each scene]",
    "height_policy": "source figure keeps canonical height/proportions; actor keeps natural adult height/build",
    "hair_policy": "source figure keeps canonical hair; actor keeps natural real hair with no matching wig",
    "environment_policy": "interesting source-world setting with safe unobstructed forward path and camera retreat corridor",
    "animation_policy": "measured synchronized forward walk with front dolly-back in every clip",
    "audio_policy": "Kling diegetic ambience only plus one separate instrumental MiniMax music track; no separate SFX by default"
  },
  "sfx": false,
  "music_required": true,
  "generate_audio": true,
  "multi_prompt": true,
  "scenes": [
    {
      "index": 1,
      "character_speech": null,
      "negative_prompt": "[exact §0 image negative prompt]",
      "image_prompt": "[§0 semantic order: shared walkable environment, canonical source left, recognizable natural actor right, near-identical practical costume, safe frontal staging]",
      "motion_prompt": "[exact §0 walking + front dolly-back template]"
    }
  ]
}
```

- `style_tags` must include **both** styles
- `production_contract` must equal `dual-style-v3` and `comparison_mode` must be valid; missing or different values are a hard stop
- `image_prompt` follows §0's semantic order and names 4–6 source-backed design anchors without an exhaustive micro-accessory inventory

---

## Game config requirement (`source-vs-live-action` only)

`games/{GAME_TAG}/{GAME_TAG}.md` must contain **TWO** versions of each character:

```markdown
### Hero Name (cartoon)
`[canonical source rendering] [class], canonical source height/proportions, [source-backed costume/silhouette/prop details]`

### Hero Name (realistic counterpart)
`recognizable photorealistic [actor], real face/natural hair/natural adult height and build, wearing a near-identical practical construction of the source costume, real skin textures, [emotion]`
```

In `source-vs-live-action`, if these blocks are missing, Manager must flag and stop until they are added. `canonical-alternate` instead uses the exact series-owned character cards and canonical references in its dual-style story bible.

---

## Role briefs

### Scenarist
- Write `production_contract: "dual-style-v3"` and the one valid `comparison_mode`; default 3 clips × 5s, or exactly the user-requested count; `character_speech: null` everywhere
- In `source-vs-live-action`, cartoon and realistic markers are mandatory; preserve the near-identical practical costume adaptation with natural actor hair/height/build.
- In `canonical-alternate`, use the same canonical screen performer for both official personas and write the exact `{ORIGINAL} VS {ALTERNATE}` overlay text for every scene.
- Every `action_description` is the same production action: both figures walk toward a front-facing retreating camera; only environment, starting stance and particles vary
- `negative_prompt`: use the §0 locked list verbatim
- General rules — `rules/roles/scenarist.md`

### Storyboarder
- Apply the reference/headshot branch selected by `comparison_mode`. `source-vs-live-action` uses one right-actor headshot; `canonical-alternate` uses two scene-derived headshots, one per persona.
- For `canonical-alternate`, use exact series-owned canonical screen references for both personas and never fancast.
- The following source-reference rules apply to `source-vs-live-action`:
- **Source ref, preferred order:**
  1. **First choice: the canonical game-wide `reference_image` for that character (untagged / no format tag) if one exists in `game_assets`.** This is the artist-accurate design source — anchor the cartoon-side `image_prompt` and NB2 chain-ref to it directly. This is a standing, format-specific exception to the general "refs never cross formats" rule, authorized for dual-style.
  2. If no canonical game-wide ref exists, use an existing dual-style-tagged asset for that character if one exists.
  3. Only if neither exists, generate a fresh dual-style-bound cartoon anchor from text — and in that case, do NOT write any distinctive design detail (hair color/style, signature accessories, outfit colors) from memory/assumption. Guessing well-known design facts from memory has repeatedly produced wrong results (wrong hairstyle, wrong hair color) even for well-known characters. If no canonical ref exists to anchor to, that is a signal to ask the user for a source image rather than proceed on memory.
- **Whenever a canonical or dual-style ref IS used (the normal case, options 1-2 above): pull 4–6 signature silhouette/costume/prop anchors into the character card and image_prompt per §0.** The reference carries fine design fidelity; the text must still lock the overall silhouette, major panels/cutouts, color blocking, signature ornament/armor/accessory and essential prop so the live-action costume is near-identical rather than merely inspired.
- Borrowing a ref from another *format's* dedicated tagged asset (e.g. a `redcon`-tagged or `serial-drama`-tagged variant) still requires explicit user instruction — only the canonical untagged game-wide ref is pre-authorized for reuse.
- **Multi-character:** every new character starts the chain anew (do NOT pass the previous character's scene)
- For one character: scene 1 = `[asset]`; scene 2+ = `[asset, scene-(K-1)]`
- **Face-lock headshot (mandatory side-asset, every character pairing, every episode):** after the scene PNG is accepted, generate ONE additional frontal headshot crop of the photorealistic figure via NB2 edit, using the already-rendered scene PNG as the image reference (not a fresh text-only generation) — the headshot must match the exact identity already locked in that scene, not a new likeness. Plain neutral background, head+shoulders, facing camera, neutral expression. Upload as a per-episode asset (`episode-scene` kind), not `game_assets`. Cost ≈$0.04–0.08.
- Before accepting each scene, verify solid footing and a clear forward lane/camera retreat corridor. A visually attractive frame that strands either figure on an edge, ledge, obstacle, stair, hazard or blocked path is rejected before animation.
- General rules — `rules/roles/storyboarder.md`

### Animator
- **Kling v3 Standard I2V**, `aspect_ratio: "9:16"`
- `duration: "5"`; without `end_image_url`
- `character_speech: null` → Kling does not receive speech text
- One model for the whole video
- **Exact `source-vs-live-action` payload shape — no bare `prompt`:**
  ```json
  {
    "start_image_url": "{accepted permanent scene PNG URL}",
    "multi_prompt": [
      {
        "prompt": "{exact substituted §0 motion template, <=400 UTF-8 bytes}",
        "duration": "5"
      }
    ],
    "shot_type": "customize",
    "duration": "5",
    "aspect_ratio": "9:16",
    "generate_audio": true,
    "elements": [
      {
        "frontal_image_url": "{derived permanent actor headshot URL}",
        "reference_image_urls": ["{same accepted scene PNG URL}"]
      }
    ],
    "negative_prompt": "{exact §0 Kling negative prompt}"
  }
  ```
- **`generate_audio: true` risk — unwanted music.** Kling can add a score even when the intended output is ambient SFX. Every motion prompt must end with the exact strong clause from §0: `DIEGETIC AMBIENCE ONLY. NO MUSIC: no beat, melody, instruments, score or soundtrack.` Avoid `cinematic`, `epic`, `dramatic`, `trailer`, and rhythm/tempo language in Kling-facing text. If Kling still bakes music into an individual clip, Editor must mute that clip's native audio before mixing the separately generated `bg-music.mp3`; never stack the accidental score under the intended track.
- **Face stability — one mandatory pattern, no exceptions:**
  - **Macro-motion (walking toward camera) with `elements` face-lock is the only supported pattern — see the §0 locked template's motion_prompt and reuse it verbatim, substituting only names/details.** Requires the Storyboarder-generated frontal headshot passed as `elements[0].frontal_image_url`, with the scene PNG as `reference_image_urls`. **`elements` is mandatory-paired with `multi_prompt: true`** — passing `elements` with a bare top-level `prompt` causes a deferred 500 at result-fetch (`rules/roles/animator.md` §4). Reference the bound face as `@Element1` in the shot prompt; still state the explicit face-lock clause (no head turn/no morphing) even with `elements` — the binding reduces drift, it does not by itself guarantee zero motion.
  - **No "keep it static/subtle" override, ever.** Every `action_description` and motion prompt must already declare the forward walk and front dolly-back. A non-walking scene is returned to Scenarist before generation, not reinterpreted by Animator.
  - Every episode requires the Storyboarder-generated frontal headshot side-asset for every character pairing — do not skip it.
  - **Camera direction for walking shots — camera must be IN FRONT of the figures (receding/dolly-back tracking, retreating at their walking pace), never behind.** The whole point of dual-style is comparing the two faces side by side; a behind-the-figures tracking shot shows only backs/backs-of-heads and defeats the format.
  - Use the exact Kling `negative_prompt` list from §0 verbatim.
- In `canonical-alternate`, use the exact two-element payload and prompt lists from that mode's section. Both headshots and the accepted scene URL are mandatory.
- General rules — `rules/roles/animator.md`

### Sound
- TTS **not needed** (no speech)
- **SFX is `false`.** Kling native ambience covers environmental sound. Set `sfx: true` only when the user explicitly asks for a separate SFX layer.
- **SFX per scene via CassetteAI on fal.ai** (only when `sfx: true` is explicitly set in storyboard.json):
  - Endpoint: `https://queue.fal.run/cassetteai/sound-effects-generator` (async, polling base = `cassetteai/sound-effects-generator`)
  - Auth: `Authorization: Key $FAL_KEY`
  - Body (JSON file): `{"prompt": "[sfx_description from scene]", "duration": 5}`
  - Poll every 15s until COMPLETED; download WAV from `audio_file.url`
  - Save to: `OUTPUT_DIR/scenes/scene-K/scene-K-sfx.wav`; convert to mp3 via ffmpeg if needed
  - One SFX file per scene; write `sfx_url` (local path) back into storyboard.json
  - Cost: **$0.01 per generation** (4 scenes = $0.04)
- Music: **must be generated via MiniMax Music v2.6** (`fal-ai/minimax-music/v2.6`, $0.03/track). Tracks from `music/tracks.json` are forbidden. Parameters: `is_instrumental: true`, mood attractive/energetic but not trailer-like, BPM 120–150. Duration must cover the entire scenes-plus-CTA timeline. Save as `OUTPUT_DIR/bg-music.mp3`.
- Subtitles do not apply
- General rules — `rules/roles/sound.md`

### Editor
- Scale 1080×1920, 30fps, concat with re-encode, hard cuts (no crossfade)
- **Animated CTA mandatory at the end** — fetch from `game_assets` where `tags` contains `cta` and `video`. Append after the last scene clip. If CTA is missing in Supabase — STOP and notify the Manager.
- **Audio mix:** keep clean Kling diegetic ambience at approximately `-28 LUFS`; normalize the dedicated MiniMax music bed to approximately `-20 LUFS`; target the final mix near `-20 LUFS` with true peak no higher than `-2 dBTP`. Do not rely on a fixed scalar alone—measure the result.
- **Accidental Kling music is the only dual-style exception to the generic "never discard paid I2V audio" rule.** If a clip is flagged as containing a score/melody, mute that clip's native audio completely; never place it beneath the MiniMax track. Keep clean ambience from the other clips. Record which clip was muted in storyboard notes.
- **SFX mixing** (only when explicitly requested and `scene-K-sfx.mp3` files are present): align each file to its scene start using `amix` or per-stream `adelay`; SFX target approximately `-28 LUFS`. NEVER `-shortest`.
- **Music plays through the full video including CTA** — do not cut music before the CTA clip. Apply `afade=t=out` only at the very end of the last clip.
- In `canonical-alternate`, render the mandatory exact pair-title overlay on every scene. In `source-vs-live-action`, render no comparison overlay unless the user requested one.
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

- [ ] `production_contract == "dual-style-v3"` and one valid `comparison_mode`; no second format slug, Pattern A/B, static, subtle-motion, wig-match, or studio-default branch
- [ ] `source-vs-live-action`: one scene-derived right-actor headshot and one element; no overlay unless requested
- [ ] `canonical-alternate`: same canonical screen performer for both personas, two scene-derived headshots and two elements, exact pair-title overlay on every scene
- [ ] In `source-vs-live-action`, exact source-rendering markers are bound to the left figure only; source height/proportions remain canonical
- [ ] In `source-vs-live-action`, realistic markers appear in image_prompt (`photorealistic`, `real skin textures`)
- [ ] In `source-vs-live-action`, the realistic card names the actor's real physical features before costume details
- [ ] In `source-vs-live-action`, the actor retains real face, natural hair, adult height/build, and age; costume is a near-identical practical construction with 4–6 source-backed anchors
- [ ] Every distinctive design detail (hair color/style, signature accessories) is sourced from an actual canonical/dual-style reference image, never invented from memory
- [ ] Environment is source-world-specific and interesting, with solid dry footing, broad unobstructed forward lane and camera retreat corridor; hazards/scenery stay safely to the sides
- [ ] Every `action_description` already declares synchronized forward walking and front dolly-back; Animator motion_prompt follows the §0 template verbatim
- [ ] Camera is in front (dolly-back), not behind, for macro-motion shots; `elements` + `multi_prompt: true` used for face-lock (mandatory every episode); frontal headshot side-asset generated for every character pairing; no real actor name in motion_prompt
- [ ] Every Kling motion prompt ends with the exact strong diegetic-only/no-music clause and is ≤400 UTF-8 bytes after substitutions
- [ ] If a clip still contains accidental Kling music: Editor mutes that clip's native audio before mixing `bg-music.mp3`
- [ ] Clean Kling ambience is near `-28 LUFS`, MiniMax music near `-20 LUFS`, final near `-20 LUFS` and ≤`-2 dBTP`
- [ ] Comparison roles remain on fixed sides for the whole video
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
- ❌ Re-scaling the source figure: do not newly chibi-fy a normally proportioned character and do not enlarge a canonically small/chibi character
- ❌ Enlarging a canonically small/chibi source figure or shrinking/aging-down the real actor so their heights match
- ❌ Copying the source character's hair color/style onto the actor with a wig; preserve the actor's natural hair and use restrained prosthetics only for indispensable fantasy anatomy
- ❌ Treating "realistic adaptation" as loose palette-inspired couture or simplifying away signature costume panels, cutouts, armor, ornaments, accessories or props
- ❌ Using a plain studio as an unannounced fallback; it requires an explicit user request or explicit approval after a failed rich-environment frame
- ❌ Choosing a beautiful but unwalkable composition: cliff edge, ledge, stairs, rubble, hazard, narrow bridge, blocked lane or no camera retreat corridor
- ❌ Camera positioned BEHIND the figures for a walking/macro-motion shot — hides both faces, defeats the format's core comparison device. Camera goes in front (dolly-back) for any shot where the figures move toward it.
- ❌ Passing Kling `elements` with a bare top-level `prompt` (no `multi_prompt: true`) — causes a deferred 500 at result-fetch, not an immediate error
- ❌ Real actor name in Animator/Kling-facing motion_prompt text — Kling doesn't parse identity from names; use `elements`/the image for likeness, describe the figure only by role/position in motion_prompt
- ❌ `generate_audio: true` with an energetic/cinematic motion_prompt and no anti-music clause, when a separate `bg-music.mp3` already exists — Kling may bake in its own unwanted score on top
- ❌ Counting prompt characters instead of serialized UTF-8 bytes — near-limit `multi_prompt` text can fail only at result fetch; enforce ≤400 bytes before preflight
- ❌ Mixing an accidental Kling score beneath the intended `bg-music.mp3` — mute the contaminated clip audio first
- ❌ `character_speech ≠ null` (Kling I2V does not generate voice)
- ❌ `-shortest` in ffmpeg
- ❌ Re-deriving the prompt method from theory instead of copying the §0 locked template verbatim — trying successive unverified "fixes" without a controlled comparison against a known-working example tends to make likeness worse, not better. When something worked before, copy its literal structure first; only vary per-episode names/details.
- ❌ Recovering Pattern A/B or another legacy branch from a historical episode note/output; `dual-style-v3` with a required comparison mode is the only normative method
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
  "production_contract": "dual-style-v3",
  "comparison_mode": "source-vs-live-action",
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
    "cooldown_episodes": 7
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

**`action_types`** — under `dual-style-v3`, every produced clip uses `"walking-approach"`. Visual variety belongs in characters, environments, starting silhouettes, particles, lens height and framing; it never changes the motion contract.

**Story Bible update (Manager, only after the user explicitly approves the local `final.mp4`):**

1. Characters used → append each to `recent_characters`; retain the flattened characters from the last **7 episodes**.
2. In `source-vs-live-action`, actors used → append to `recent_actors`; retain the flattened actors from the last **7 episodes**. In `canonical-alternate`, store canonical screen performers only as episode provenance; cooldown is enforced on the character pair, not treated as fancasting rotation.
3. Environments used → append each to `recent_environments`; trim to last **6 episodes' worth** (FIFO).
4. Action types used → append each to `recent_action_types`; retain the flattened values from the last **6 episodes**.
5. For each character featured: set `character_pool[].last_seen_episode = current episode number`.
6. Append `episode_summary`; FIFO keep last **7** so the cooldown can be reconstructed without guesswork.
7. Increment `last_episode`.

---

## Anti-repetition check

Before Phase 1 (scenarist), manager validates proposed character/environment selection:

- [ ] None of the selected characters appear in `recent_characters` (last 7 episodes).
- [ ] None of the selected environments appear in `recent_environments` (last 6 episodes).
- [ ] In `source-vs-live-action`, none of the newly cast actors appear in `recent_actors` (last 7 episodes, flattened).
- [ ] In `canonical-alternate`, none of the selected original/alternate pairs appear in `recent_characters` (last 7 episodes).
- [ ] Every proposed `action_type` is `walking-approach`; repetition is expected and exempt from generic action-rotation checks.
- [ ] Prefer characters with the lowest (or null) `last_seen_episode` when choosing from the pool.

If a collision is found — scenarist picks different characters / environments before writing storyboard.json.
