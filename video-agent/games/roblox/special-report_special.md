# Roblox — Special Report format overrides

## Anchor scenes: reuse scene-1 PNG for scene-5 (MANDATORY)

Scene 1 (anchor intro) and Scene 5 (anchor sign-off) use the **same source PNG**. Storyboarder MUST copy scene-1.png → scene-5.png instead of generating a new image. Reason: independent NB2 generations of the same prompt produce slightly different framing/proportions, causing zoom-out artifacts when Avatar animates scene-5 vs scene-1.

Rule: after generating scene-1.png, run `cp scenes/scene-1/scene-1.png scenes/scene-5/scene-5.png`. Upload scene-5.png to Supabase as a separate episode-scene (upsert OK). Then set `image_urls` for scene 5 = same as scene 1.

## Reporter gaze: must face directly into camera

Reporter field scenes (scenes 2–4): Noob MUST look **directly into the camera lens**. Add explicit anchor to every reporter image_prompt:

```
eyes looking DIRECTLY into camera lens, direct eye contact with viewer, NOT looking sideways or off-frame
```

Without this, NB2 places the reporter's gaze toward the subject (side composition) instead of the camera — unnatural for broadcast TV reporter delivery.

## Voice override (reporter)

**Reporter (Noob): `Young_Knight`, emotion `happy`, speed `1.1`** — NOT `Casual_Guy`.

`Casual_Guy` sounds too sluggish for brainrot delivery — confirmed EP1 pilot feedback. `Young_Knight` with speed 1.1 gives the snappy "no cap fr fr" energy the character needs.

## Image generator

**Primary generator: NB2** (standard, same as all other formats).

Use `fal-ai/nano-banana-2/edit` with chain refs per storyboarder.md. Existing Supabase refs for `chad-sigma` and `noob` characters are available — reuse before generating new ones.

## Prompt prefix (mandatory, prepend to every scene image_prompt)

```
Roblox-inspired Pixar-style 3D render, blocky stylized characters, smooth plastic-like skin texture, expressive cartoon faces, vibrant saturated colors, soft ambient lighting, cinematic depth of field, toy-like proportions, game screenshot aesthetic, clean white rim light,
```

## Character prompt blocks (copy verbatim)

### Chad/Sigma (anchor)
```
Chad-Sigma Roblox anchor: Roblox-style muscular blocky humanoid, square prominent jaw set in stern deadpan expression, dark aviator sunglasses, short buzz-cut dark hair, black fitted tank top showing blocky muscular arms, dark cargo pants, crossed arms power pose, polished matte plastic texture, imposing wide shoulder proportions, sitting behind LARGE BROADCAST ANCHOR DESK with illuminated 'ROBLOX SPECIAL REPORT' nameplate on front panel in bright yellow letters, dark sleek studio desk with neon blue and yellow accent strips, ANCHOR DESK PROMINENTLY VISIBLE in lower portion of frame
```

### Noob (reporter)
```
Noob Roblox reporter: Roblox-style blocky humanoid, bright yellow smooth plastic skin, simple blue torso shirt, bright green pants, round compact head with wide innocent eyes, small curved mouth slightly open mid-speech, stubby short limbs holding broadcast handheld mic with 'ROBLOX SPECIAL REPORT' printed on mic flag, standard blocky proportions, matte plastic texture
```

## Side composition rule (mandatory for scenes 2–4)

Every reporter scene MUST use the side composition anchor (from special-report.md). For Roblox:

```
Noob Roblox reporter standing to the [LEFT/RIGHT] of frame, body occupying ~30% of frame width,
facing slightly [RIGHT/LEFT] toward the subject,
holding broadcast handheld mic with 'ROBLOX SPECIAL REPORT' on flag, mouth slightly open,
[SUBJECT] prominently filling the [other] 65% of frame,
Roblox-inspired Pixar-style 3D render, blocky characters, vibrant saturated colors,
NOT centered portrait, 9:16 vertical broadcast field reporter composition
```

## Tone override

- All dialogue has maximum Gen Z / brainrot energy
- Noob reporter uses: `no cap`, `fr fr`, `sigma violation`, `negative aura`, `cooked`, `rizz`
- Chad anchor: zero slang, full deadpan — the straight-man contrast makes the brainrot funnier
- Investigation topic must be rooted in real Roblox game mechanics (obby deaths, Robux economy, pet trading, etc.)

## Budget note

NB2 costs ~$0.08/image. Budget cap: $4.50.

## Opener

First episode: Storyboarder generates the "Roblox Special Report" opener card PNG via NB2 (text-to-image, no refs), then Animator animates it with Kling I2V (3–5s). Upload to `assets/roblox/branding/special-report-opener.mp4`. Store URL in story bible `opener_url`.

Subsequent episodes: reuse the stored `opener_url` — do NOT regenerate.
