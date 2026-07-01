# Genshin Impact — Fake Ad format overrides

## Default character

**Lumine (Traveler)** is the default protagonist for Genshin fake ads unless the brief specifies otherwise. She's the perfect straight-man — earnest, determined, and deeply afflicted by resin anxiety.

If the user brief specifies canonical characters, product, setting, or a sketch/dialogue premise, that live brief overrides this Lumine/Resin Energy default completely. Keep only the Genshin visual style, Supabase asset reuse, and packshot/CTA discipline from this file. Do not force Lumine, Paimon, resin anxiety, Resin Energy, or the resin notification into briefs about other characters or products.

Character prompt block (copy verbatim for scenes 0–3):
```
female Traveler Lumine: white and gold traveler outfit with star constellation motifs and flowing white sash, long blonde hair with signature silver star-shaped hair clip, sharp determined expression, one-handed sword at her side, graceful athletic build, anime cel-shaded style
```

**Paimon** — mandatory companion in scenes 1–2, optional elsewhere:
```
Paimon: small floating fairy companion, round child-like face with big expressive eyes, white puffy dress with pale blue accents, white hair with twin tails tied with pale blue ribbons, tiny floating crown accessory, always hovering slightly above ground level, cheerful earnest expression, anime cel-shaded style
```

## Announcer voice

**Voice:** `George`, **stability:** 0.35, **speed:** 1.0

Tone directive for TTS: `"TV commercial announcer, confident and deadpan, building calm authority — the product is a calming energy drink, so the voice mirrors the zen the product promises"`.

- Language: **English**
- NO Gen Z slang — deadpan sincerity makes the absurd twist funnier
- Scene 3 (twist): delivery goes quieter, matter-of-fact, like a nature documentary narrator reporting an unexpected extinction

## Prompt prefix (mandatory, prepend to every scene image_prompt)

```
Genshin Impact anime style, cel-shaded character art, vibrant fantasy colors, soft outline anime aesthetic, magical elemental effects, Teyvat world environment, clean detailed character illustration,
```

## Scene 0 environment — Resin anxiety setup

For the resin-checking scene, use this environment anchor:

```
Mondstadt city plaza environment: cobblestone streets, European medieval fantasy architecture with warm stone buildings, windmill silhouette in background, afternoon golden light, clear blue sky with soft clouds, cozy fantasy town aesthetic
```

Lumine's state in scene 0: hunched over her glowing map interface, eyes darting, hand moving to open-close the resin counter repeatedly, subtle twitch energy, exhausted but unable to stop.

## Scene 2 environment — Zen peak effect

After drinking, Lumine sits in peaceful meditation:

```
Mondstadt hillside meadow: bright green rolling hills with wildflowers, Mondstadt city visible in soft distance, clear sky, gentle warm sunlight, serene pastoral fantasy landscape, Genshin Impact open world aesthetic
```

Lumine's state in scene 2: sitting cross-legged on the grass, eyes closed, soft smile, hands resting on knees, completely at peace. Paimon floats beside her looking mildly confused but supportive.

## Scene 3 — The Twist (resin fills, he walks away)

Notification visual: glowing Genshin-style UI element floating in air showing `⬡ 160 / 160` with a soft pulse animation.

Lumine's state: opens one eye, sees the notification, closes the eye again gently. Stands up slowly. Puts the empty can down. Walks away toward the horizon. Paimon watches her leave, holds up a tiny sign: `"she's fine"`.

The camera stays on the can on the ground and the notification floating in the air as Lumine walks out of frame.

## Packshot product design — Resin Energy can

For the Resin Energy can packshot (scene 4):

```
Resin Energy drink can: tall sleek energy drink can with matte pale blue and white body, soft gradient from powder blue at top to white at base, large hexagonal resin symbol (⬡) in glowing amber-gold on the label, elegant serif product name in clean white lettering, subtle elemental particle effects drifting around the can, calming zen energy vibe contradicting the energy drink format, sparkles erupting gently from the top of the can, hero product shot angle (slight 3/4 tilt), clean soft lavender gradient background with pale gold sparkles, high-contrast commercial product photography aesthetic, Genshin Impact anime style
```

- Background palette: pale lavender → soft white gradient (matches Genshin UI tones)
- The resin symbol (⬡) should glow amber-gold — matches in-game resin icon color
- No character, no hands, no text baked in (Editor handles slogan overlay)

## Packshot slogan overlay style

Slogan/disclaimer overlay styling — see `## Overlay brand` in `genshin-impact.md` (font_display=BEBAS,
accent_color=#F5D060 amber-gold matching the resin icon). Layout (position/size/timing) — `fake-ad.md` → `## Overlays`.

## Music mood

**`"upbeat-commercial"` → fallback `"happy-energetic"` → fallback `"fun-news"` mood track.**

The music must stay cheerful and bouncy even through the twist. The key irony of this ad: upbeat commercial jingle plays as the hero achieves enlightenment and quits the game.

Volume: `0.25`.

## Tone override

- Announcer VO: calm, confident, slightly zen — mirrors the product's "calming energy" promise
- Scene 0: nervous quick cuts visually, but announcer stays cool and detached
- Scene 2: announcer voice softens slightly on "The calm to endure" — peak serenity
- Scene 3 (twist): total deadpan. "He didn't notice." said like reporting a weather forecast.
- Paimon in scene 3: confused but supportive expression (she holds a tiny sign `"she's fine"` — visual gag, not in VO)

## Budget note

NB2 costs ~$0.08/image × 5 = $0.40. Budget cap: $3.50. Genshin anime style renders cleanly in NB2 — no special fallback needed unless anime cel-shading breaks (retry with more explicit style_tags).
