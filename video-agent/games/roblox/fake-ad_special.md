# Roblox — Fake Ad format overrides

## Default character

**Noob** is the default protagonist for Roblox fake ads unless the brief specifies otherwise. He's the perfect straight-man for commercial parody — naive enough to genuinely believe the product will work.

Character prompt block (copy verbatim for scenes 0–3):
```
Noob Roblox protagonist: Roblox-style blocky humanoid, bright yellow smooth plastic skin, simple blue torso shirt, bright green pants, round compact head with wide innocent eyes, small curved mouth expressing the appropriate emotion for the scene beat, stubby short limbs, standard blocky proportions, matte plastic texture
```

## Announcer voice

**Voice:** `George`, **stability:** 0.35, **speed:** 1.0

Tone directive for TTS: `"energetic TV commercial announcer, confident and earnest, slightly over-the-top enthusiasm building to a deadpan punchline"`.

- NO Gen Z slang in the announcer VO — the joke is that the commercial is played straight while the visuals are absurd.
- Brainrot energy lives in the VISUALS (Noob failing, the obby, the product design), NOT in the announcer voice.

## Prompt prefix (mandatory, prepend to every scene image_prompt)

```
Roblox-inspired Pixar-style 3D render, blocky stylized characters, smooth plastic-like skin texture, expressive cartoon faces, vibrant saturated colors, soft ambient lighting, cinematic depth of field, toy-like proportions, game screenshot aesthetic, clean white rim light,
```

## Obby environment anchors

For scenes set in an obby (obstacle course), add these specifics to the image_prompt:

```
Roblox obby map environment: bright colorful blocky platforms at various heights, neon-edged platform tiles in red/green/blue, glowing acid/lava pool below (bright lime-green or orange-red), trembling/spinning obstacle platforms, cartoon-style danger zone aesthetic, blocky toy-like world proportions
```

- Acid = bright lime green
- Lava = vivid orange-red
- Platforms = primary colored tiles with slight glow outlines

## Packshot product design — Obby Energy (first ad)

For the Obby Energy Drink packshot scene, use this product description in the image_prompt:

```
Obby Energy drink can: tall sleek energy drink can with matte neon-yellow body, vivid electric-green 'OBBY ENERGY' logo text in blocky Roblox-style font, lightning bolt graphic on the side, small Roblox character silhouette running on platforms on the label, sparkling particles erupting from the top of the can, hero product shot angle (slight 3/4 tilt), clean electric-blue gradient background with neon-yellow sparkles, high-contrast commercial product photography aesthetic, Roblox-inspired Pixar-style 3D render
```

## Packshot slogan overlay style

Slogan/disclaimer overlay styling — see `## Overlay brand` in `roblox.md` (font_display=BEBAS,
accent_color=#FFD700 neon-yellow). Layout (position/size/timing) — `fake-ad.md` → `## Overlays`.

The neon-yellow stroke matches Roblox's brand yellow (`#FFD700` from game palette).

## Music mood

**`"upbeat-commercial"` → if not in tracks.json, use `"happy-energetic"` → fallback `"fun-news"` mood track.**

The music must stay cheerful and bouncy through the twist — do not use anything that sounds dark or sad. The upbeat-failure combo is the entire joke.

Volume: `0.25` (standard for this format).

## Tone override

- Announcer VO: straight commercial tone, NO brainrot slang — earnest absurdity
- Visual gags in the IMAGES and MOTION carry the Roblox brainrot energy
- Scene 3 (twist) Noob's expression: pure disbelief / "L detected" face — wide eyes, mouth open, classic Roblox surprised reaction
- Scene 0 (setup) Noob: tired, slumped shoulders, dead eyes staring at the obby ahead

## Budget note

NB2 costs ~$0.08/image × 5 = $0.40. Budget cap: $3.50.
