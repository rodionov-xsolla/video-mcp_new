# Format "Dance Battle" — comedic dance battles

Two characters compete in a dance battle on stage. Contrast between effort and absurdity is the main source of humor. No speech, only SFX + music.

This file is the **playbook**. Craft rules (NB2 chain, Kling I2V, ffmpeg) — in `rules/roles/*.md`.

---

## When to use

Keywords: "dance battle", "dance", "танцевальный батл", "танец", "dance off", "dance competition", "баттл танцев".

Ideal for series: new characters every episode, the same stage.

---

## Concept

- **Two characters** — visually distinct (size, style, energy)
- **Frame:** wide shot, low angle (~15°), both dancers in frame
- **Style:** realistic 3D render with comedic stylization
- **Model:** Kling 2.6 Pro I2V ($0.14/s), **`generate_audio: true`** (Kling generates crowd, music, SFX)

> ⚠️ **FORMAT NEEDS REFACTOR (2026-05-26 audit).** Both `rules/roles/animator.md` line 74 and `tools/fal-ai.md` lines 190, 218, 378 state Kling I2V CANNOT generate audio in any version — `generate_audio: true` yields garbled noise, not SFX. This format's audio strategy is broken as written. Refactor options: (a) switch to Veo3 T2V (supports baked-in audio, $3.20/8 s with audio); (b) keep Kling I2V silent + add SFX/crowd via separate audio layer in Editor. Do NOT use unmodified — flag to Manager.
- **Speech:** NO — `character_speech: null` in all scenes
- **Duration:** 3×5s (15s) or 2×10s (20s)
- **Budget:** $5 max (~$2.30–$3.00 typical)

---

## Structure

| Clip | Dur. | Camera | Action | Comedy |
|---|---|---|---|---|
| 1. Entrance | 5s | Wide low-angle, slow lateral L→R | Walk on stage, starting poses, crowd | Appearance contrast |
| 2. Battle | 5–10s | Medium push-in to the lead | Character A executes a move, B reacts | Serious face + absurd |
| 3. Final | 5s | Wide pull-back | Final freeze poses, crowd erupts | Unexpected ending |

`camera_angle` mandatory different between adjacent clips.

---

## Locked Parameters (identical across all videos in the series)

Included in every `image_prompt` and `motion_prompt`:

- **Camera:** Wide shot from low angle (~15°) at stage-edge level, both characters fully in frame
- **Location:** Circular dance arena-stage in a large hall, polished dark wooden floor with reflections, low podium
- **Crowd:** Dense crowd of spectators — silhouettes and raised hands in soft bokeh, reactive movement
- **Lighting:** Two contrasting spotlights — warm orange left, cool blue right — central white beam, light haze
- **Atmosphere:** Micro dust in light cones, energetic, festive, competitive, comedic
- **Render:** Realistic 3D render, PBR materials, cinematic realism with subtle comedic stylization

---

## Variable Parameters (change between issues)

- **Characters** (8+ visual details each, visually distinct)
- **Dance styles** — breakdance / ballroom / hip-hop / folk / robot / ballet / salsa / moonwalk / floss / headbang
- **Emotions** — dead-serious concentration / smug confidence / panicked effort / disgusted determination
- **Winner** — left / right / both
- **Comedy source** — size mismatch / speed mismatch / style clash / wardrobe malfunction

---

## Storyboard extensions

```json
{
  "format": "dance-battle",
  "visual_identity": {
    "character_a": {"name": "...", "description": "8+ details", "dance_style": "ballet", "emotion": "smug confidence"},
    "character_b": {"name": "...", "description": "8+ details", "dance_style": "breakdance", "emotion": "dead-serious concentration"},
    "comedy_source": "size mismatch — elegant lean dancer vs massive Viking",
    "environment_description": "[locked]",
    "lighting": "[locked]",
    "style_tags": "[locked]"
  },
  "scenes": [
    {"index": 1, "character_speech": null, "negative_prompt": "blur, distort, extra limbs, merged bodies, split screen", ...}
  ]
}
```

### 4-Layer prompt structure (for Kling)
```
Layer 1 — Camera movement (how the camera behaves over time)
Layer 2 — Subjects & action physics (who + concrete body mechanics)
Layer 3 — Environment & lighting (where + light setup)
Layer 4 — Texture & style (render quality + materials)
```

`image_prompt` = 60–100 words, `motion_prompt` = 40–60 words. Max 3–5 main ideas — Kling loses coherence on overload.

---

## Anti-Drift Layer (for series)

When you have ≥2 issues in a row, rotate:
- **Dance styles** — do not repeat in 5 consecutive
- **Emotions** — dead-serious / smug / panicked / surprised / disgusted
- **Winner** — left → right → both → …
- **Camera accent** — push-in left → push-in right → wide
- **Crowd energy** — eruption / shocked silence / mixed reactions / build-up
- **Comedy source** — size / speed / style / wardrobe / prop interaction

If a move / camera ending / comedy mechanism is identical to the previous issue — replace.

---

## Role briefs

### Scenarist
- 3 clips (5/5-10/5) or 2×10s; `character_speech: null` everywhere
- 4-layer prompt structure; ≤3-5 ideas per prompt
- Concrete body mechanics: weight shift, hand position, trajectory — not "dancing"
- Every move has a clear endpoint position
- One character acts, the other reacts (not both at once)
- Comedy source obvious without explanation
- General rules — `rules/roles/scenarist.md`

### Storyboarder
- **Two character refs (A and B)** — generated separately, both passed into every scene
- image_urls: `[ref-a, ref-b]` for scene 1; `[ref-a, ref-b, scene-(K-1)]` for 2+ (max 3 refs — watch ref duplication)
- Characters visually DISTINCT; 8+ details each
- Style identical for both (realistic 3D render)
- General rules — `rules/roles/storyboarder.md`

### Animator
- **Kling 2.6 Pro I2V** with `generate_audio: true` (crowd + SFX generated by the model)
- ✅ weight shifts, leans, torso turns, freeze poses, slow movements with clear endpoints
- ⚠️ fast spins, jumps, splits — artifacts, use carefully
- ❌ simultaneous complex movements of both — one acts, the other statically reacts
- `negative_prompt` mandatory: `blur, distort, extra limbs, merged bodies, split screen, duplicate characters`
- General rules — `rules/roles/animator.md`

### Sound
- TTS **not needed** (no speech)
- Optional music track over Kling SFX: Kling SFX `volume=0.6`, music `volume=0.25`
- Subtitles do not apply
- General rules — `rules/roles/sound.md`

### Editor
- Scale 1080×1920, 30fps, concat with re-encode, hard cuts (crossfade forbidden)
- Music via `amix`; **NEVER `-shortest`**
- General rules — `rules/roles/editor.md`

---

## Banned terms (in Kling prompts)

```
nice background, good lighting, cool vibe, beautiful atmosphere
masterpiece, best quality, ultra detailed, 4K, 8K, trending on artstation
dynamic pose, dynamic scene, dynamic energy
various, several, multiple
energetic, lively, vibrant
dancing (describe a CONCRETE movement)
```

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/dance-battle/
├── storyboard.json
├── scenes/
│   ├── refs/{character-ref-a.png, character-ref-b.png}
│   ├── scene-1/{scene-1.png, scene-1.mp4, scene-1-scaled.mp4}
│   ├── scene-2/...
│   └── scene-3/...
├── concat-list.txt
└── final.mp4
```

---

## Validation

- [ ] `format: "dance-battle"`, `character_speech: null` in all scenes
- [ ] `generate_audio: true` for all Kling calls
- [ ] Two character refs generated, both passed into image_urls of every scene
- [ ] 8+ visual details per character; visually distinct
- [ ] 4-layer prompt structure; image_prompt 60–100 words, motion_prompt 40–60 words
- [ ] `camera_angle` different for adjacent clips
- [ ] Concrete movement mechanics (not "dancing")
- [ ] `negative_prompt` filled
- [ ] For series: Anti-Drift verified (styles/emotions/finals don't duplicate the last issue)
- [ ] Budget ≤$5

---

## Priority Hierarchy (on conflict)

1. **Kling technical compliance** — 4-layer, word count, physics
2. **Character recognizability**
3. **Motion clarity**
4. **Comedic contrast**
5. **Camera coherence**
6. **Visual spectacle**
7. **Sound direction**
