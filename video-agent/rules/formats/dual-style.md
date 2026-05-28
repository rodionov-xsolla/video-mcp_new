---
subtitle_style: none
subtitle_offset_s: 0
subtitle_mask: false
subtitle_highlight: false
subtitle_extras: []
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
- **Model:** Kling 2.6 Pro I2V, `generate_audio: true` (SFX)

> ⚠️ **FORMAT NEEDS REFACTOR (2026-05-26 audit).** `animator.md` line 74 and `tools/fal-ai.md` lines 190, 218, 378 state Kling I2V cannot generate audio in any version — `generate_audio: true` yields garbled noise, not SFX. Refactor options: switch to Veo3 T2V for embedded audio, or keep Kling silent and add SFX as separate audio layer in Editor. Do NOT run unmodified.
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

### 1. Cartoon and realistic markers (mandatory)

Without these markers AI will make both realistic.

**Cartoon:**
- `bold black outlines`
- `bright flat saturated colors`
- `exaggerated chibi proportions`
- `large head, small body` (if chibi)

**Realistic:**
- `photorealistic`
- `real skin textures`
- `natural proportions`
- `weathered / sun-darkened / tanned`

### 2. Connection between versions
- Same costume (colors, type of clothing, accessories)
- Same pose (`matching pose`, `mirrored stance`)
- Same key details (pink bandana on cartoon → pink on realistic)

### 3. Positioning
- Cartoon **always** on the left, realistic **always** on the right (or fixed the other way around — one decision for the whole video)
- `side by side`, not one behind the other

### 4. Sizes in frame
- Cartoon may be **smaller** (chibi = small), realistic larger
- This enhances the contrast, do not try to align by height

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
  "scenes": [
    {
      "index": 1,
      "character_speech": null,
      "negative_prompt": "blur, distort, merged characters, single character, text overlay, watermark",
      "image_prompt": "[ENV], on the left a cartoon chibi [CHAR] with bold black outlines bright flat saturated colors [DETAILS], on the right a photorealistic human [MATCHING OUTFIT] real skin textures [DETAILS], both [ACTION], [LIGHTING], [CAMERA], vertical composition, 9:16 aspect ratio",
      "motion_prompt": "The cartoon [CHAR] on the left [EXAGGERATED ACTION]. The realistic [CHAR] on the right [GROUNDED MATCHING ACTION]."
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
- **Kling 2.6 Pro I2V**, `generate_audio: true` (SFX), `aspect_ratio: "9:16"`
- `duration`: "5" or "10"; without `end_image_url`
- `character_speech: null` → Kling does not receive speech text
- One model for the whole video
- General rules — `rules/roles/animator.md`

### Sound
- TTS **not needed** (no speech)
- Optional music: Kling SFX `volume=0.6`, music `volume=0.15`
- Subtitles do not apply
- General rules — `rules/roles/sound.md`

### Editor
- Scale 1080×1920, 30fps, concat with re-encode, hard cuts (no crossfade)
- Music via `amix`; **NEVER `-shortest`**
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
- [ ] Budget ≤$5

---

## Anti-patterns

- ❌ "cartoon style" without concrete markers (bold outlines, flat colors) — AI will make semi-realistic
- ❌ A single prompt without `on the left / on the right` — AI will merge into one character
- ❌ Realistic without "live" details (skin, textures) — you get a 3D render, not a human
- ❌ Chain reference between different characters — breaks appearance
- ❌ Trying to align cartoon and realistic by height — let chibi stay smaller
- ❌ `character_speech ≠ null` (Kling I2V does not generate voice)
- ❌ `-shortest` in ffmpeg
