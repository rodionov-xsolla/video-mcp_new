# Format "Object Character" — anthropomorphic objects

A household item with a strong emotion delivers a 10-second first-person monologue. A fork with eyes, a tired mug, an angry slipper.

This file is the **playbook**. Craft rules (NB2, Kling I2V, TTS, ffmpeg) — in `rules/roles/*.md`.

---

## When to use

Keywords: "object character", "антропоморф", "talking object", a household object as a character.

---

## Concept

- **1 object → 1 clip × 10s** (single) or **5 videos** (series)
- **Model:** strictly **Kling 2.6 Pro I2V** (`generate_audio: true` for SFX — creak, knock, ambient)
- **Speech:** via **ElevenLabs TTS** overlay (Kling does not generate voice), `character_speech: null` in storyboard
- **Budget:** $1.50 (single) / $7.50 (series)
- **NOT** Veo3 T2V

---

## Structure

**1 clip, 10s, Kling I2V.** The object delivers a monologue ≤25 words.

Anthropomorphism strengthens personality but **does not kill object identity**. The object must remain recognizable:
- Eyes + brows
- Mouth (with expression)
- Limbs (object-like protrusions, not human hands)
- Pose / tilt
- Interaction with environment

---

## Input interpretation logic

| Given | Action |
|---|---|
| Only the object | Derive emotion, scene, conflict |
| Object + emotion | Derive the strongest environment for the emotion |
| Object + scene | Derive a readable emotion |
| Object + emotion + scene | Keep all, enhance cinematics |
| Multiple objects | Lead + others related (series) |

### Preferred emotions
- Annoyed truth, tired realism, anxious warning, disgust, pride, panic, sarcasm, defensive frustration, exhausted honesty

**Avoid:** positive motivation, abstract optimism, neutral narration.

---

## Script (monologue)

10s monologue, first-person. Rules:
- Speak as the object itself
- Naturally speakable text
- Contains: tension / frustration / warning / complaint / insight / sarcasm
- Emotionally direct, no filler
- **NO** addressing the audience ("you guys", "subscribe")
- **NO** CTA phrases, motivational tone
- ≤25 words (for 10s)

Example: `"Every single dinner party — spoons in the spotlight, knives get respect, and me? I'm the one they drop on the floor."`

---

## Storyboard extensions

```json
{
  "format": "object-character",
  "approach": 2,
  "visual_identity": {
    "character_description": "anthropomorphic silver dinner fork with expressive cartoon eyes, thick angry eyebrows, wide open mouth mid-rant, two small arm-like prongs gesturing wildly, slightly bent posture, metallic silver surface with scratches",
    "environment_description": "inside a dark kitchen drawer, cutlery silhouettes, warm light from above, wooden interior with crumbs",
    "style_tags": "stylized animated 3D render, Pixar-quality character design, expressive anthropomorphic object",
    "lighting": "warm volumetric light from above, dramatic rim light"
  },
  "tts": {
    "text": "[≤25 words monologue]",
    "voice": "Daniel",
    "stability": 0.20,
    "style": 0.8
  },
  "scenes": [
    {"index": 1, "duration_sec": 10, "character_speech": null, "motion_prompt": "[no speech text]", ...}
  ]
}
```

### character_description — 8+ details (mandatory)
1. Material/texture (metallic, ceramic, rubber, wood)
2. Eyes (wide cartoon, squinting suspicious)
3. Brows (thick angry, raised worried)
4. Mouth (wide open mid-rant, tight-lipped grimace)
5. Limbs (arm-like handles, stubby legs)
6. Pose (leaning aggressively, slouched defeated)
7. Wear/details (scratches, stains, chips, dust)
8. Unique detail (four sharp tines, chipped rim)

### Voice mapping (ElevenLabs via fal.ai)

| Emotion | Voice | stability | style |
|---|---|---|---|
| Annoyance, sarcasm | Daniel / George | 0.20 | 0.8 |
| Panic, anxiety | Charlie | 0.15 | 0.9 |
| Tiredness, sadness | George | 0.35 | 0.6 |
| Pride, self-confidence | Daniel | 0.10 | 0.8 |
| Female (confident) | Charlotte | 0.25 | 0.7 |

---

## Series (5 videos)

If `format: "series"` — main + 4 related objects from the same thematic universe (kitchen / morning routine / stationery / burnout / clutter).

Every related character must have:
- A unique object (do not repeat main)
- A unique emotion or variation
- A unique conflict, script (not a templated substitution)
- A unique voice (alternate male/female)

Each episode → its own storyboard.json → its own final.mp4.

---

## Role briefs

### Scenarist
- 1 object = 1 clip × 10s; `character_speech: null` (Kling does not generate voice)
- Script in the `tts` section (text, voice, stability, style), ≤25 words
- `motion_prompt` contains ≥2 actions, **WITHOUT speech text**
- 8+ visual details in `character_description`
- Environment tied to the real use of the object
- General rules — `rules/roles/scenarist.md`

### Storyboarder
- Anchor ref of the object (NB2, 9:16, neutral dark bg); scene image with `image_urls: [anchor]`
- For a lipsync scene — mouth slightly open / slight smile (teeth visible for lipsync quality)
- General rules — `rules/roles/storyboarder.md`

### Animator
- **Kling 2.6 Pro I2V**, `duration: "10"`, `generate_audio: true` (SFX), `aspect_ratio: "9:16"`
- `prompt` = motion_prompt WITHOUT speech text
- **NOT** Veo3 T2V
- General rules — `rules/roles/animator.md`

### Sound
- **ElevenLabs TTS via fal.ai** (`fal-ai/elevenlabs/tts/eleven-v3`); `voice` name, not hash
- Voice/stability/style — from the `tts` section of storyboard (see Voice mapping above)
- Subtitles not required (10s monologue is intelligible)
- General rules — `rules/roles/sound.md`

### Editor
- Scale 1080×1920, 30fps
- Mix: Kling SFX `volume=0.4`, TTS voice `volume=1.0` + `adelay=500|500` (0.5s delay)
- Trim: `-t CLIP_DUR` where `CLIP_DUR = 0.5 + TTS_DUR + 1.0s`
- **NEVER `-shortest`** (clips video to audio length)
- General rules — `rules/roles/editor.md`

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/object-character/
├── storyboard.json
├── scenes/
│   ├── refs/character-ref.png
│   └── scene-1/{scene-1.png, scene-1.mp4, scene-1-scaled.mp4}
├── voiceover.wav
└── final.mp4
```

Series: each episode in its own OUTPUT_DIR.

---

## Validation

- [ ] Object is recognizable as an item (not an abstract creature)
- [ ] `character_description` ≥8 visual details (eyes/brows/mouth/limbs/pose)
- [ ] Script first-person, ≤25 words, no CTA / addressing the viewer / motivational tone
- [ ] Contains conflict/tension/emotion (not neutral)
- [ ] `character_speech: null`; speech text in the `tts` section
- [ ] `motion_prompt` does NOT contain speech text; contains ≥2 actions
- [ ] `generate_audio: true` in the Kling call
- [ ] For series: 5 unique objects (emotion/conflict/script/voice); not templates with substitutions
- [ ] Budget ≤$2 (single) / ≤$10 (series)

---

## Anti-patterns

- ❌ Abstract object without identity ("cute blob with face")
- ❌ Object = a human with item texture
- ❌ Script addresses the viewer ("Hey guys!", "Subscribe!")
- ❌ Motivational tone
- ❌ Speech text in `motion_prompt` (Kling does not generate voice)
- ❌ `character_speech` ≠ null
- ❌ Identical script templates in series
- ❌ Veo3 T2V for this format
- ❌ `-shortest` in ffmpeg
