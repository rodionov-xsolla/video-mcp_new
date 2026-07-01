# Dual-Style VARIANT — Star Trek Timelines: Real Pairs (M+F)

## Overrides to standard dual-style.md

This variant differs from standard dual-style in ONE key way:
**Each clip shows TWO DIFFERENT game characters (one male + one female) in the SAME semi-realistic Pixar 3D style.**
There is NO anime/cartoon vs. realistic contrast. Both characters are full game-style Pixar 3D.

---

## Video structure (override: 4 clips, not 3)

| Clip | Pair | Male | Female |
|------|------|------|--------|
| 1 | Logic vs. Borg | Spock | Seven of Nine |
| 2 | DS9 Married Couple | Worf | Jadzia Dax |
| 3 | Legendary Captains | Picard | Michael Burnham |
| 4 | TOS Icons | Kirk | Uhura |

Each clip is 5 seconds. Total: ~20s + CTA.

---

## Image prompt rules (OVERRIDE — no style isolation markers)

DO NOT use "anime cel-shaded", "photorealistic", "bold black outlines", "live-action" — these are for standard dual-style only.

Both characters: **semi-realistic Pixar 3D, Star Trek Timelines art style**.

**Template:**
```
Star Trek Timelines style, semi-realistic Pixar 3D, cinematic Federation lighting,
[MALE CHARACTER full description] standing on the LEFT, [FEMALE CHARACTER full description]
standing on the RIGHT, both sharing a single continuous minimalist deep-space environment
(#0a0a12 dark background, subtle LCARS-style glow), no dividing line between characters,
both fully visible full-body figures, vertical 9:16 composition
```

**Negative prompt:**
```
split panel, dividing line, border between characters, anime, cartoon, chibi, cel-shaded,
photorealistic photograph, text overlay, UI overlay, single character, merged silhouettes
```

---

## Chain reference rules (OVERRIDE)

Each pair = independent chain. Do NOT pass previous pair's scene as chain ref.
For each pair: Scene image = [character-ref-male, character-ref-female] (both refs as anchors).

---

## Pose rule (MANDATORY — same across ALL clips)

Every clip: **both characters walk side by side toward the camera, matching stride, both looking directly into the lens.**
This is the format's visual signature — do NOT invent unique poses per pair.
Emotional differentiation comes ONLY from facial expressions and character-specific details (uniform, implants, accessories).

Example action_description structure:
```
[Male] and [Female] walk side by side toward the camera in a single matched stride, both facing the lens directly.
[Male] on the left — [costume detail], pace [adjective]. [Female] on the right — [costume detail], stride [adjective].
No interaction — two [era/show] legends advancing in perfect parallel.
Micro-motion: uniform fabric shifts with stride, [specific details] catch ambient light.
```

## Motion prompt rules (OVERRIDE)

Both characters move together in the walk-toward-camera motion. Micro-motion only for Kling I2V:
clothing sway, hair movement, badge glint. No running, no hits, no teleportation.
Camera: steady hold as they approach (no camera movement needed — the walk creates the dynamism).

---

## Audio

- NO character dialogue in any clip (character_speech: null)
- Kling generate_audio: true (ambient SFX built-in)
- VO track: "Download the game and assemble your crew." — added by Editor as off-camera narrator
- Banner: bannerST1.png overlaid at t=4s for 7 seconds — Editor handles via FFmpeg overlay
- Music: MiniMax Music v2.6, futuristic rhythmic space-opera, ~$0.03

---

## Editor overrides

- SUBTITLES: false
- OVERLAYS: true (banner overlay)
- BANNER_PATH: absolute path to `.context/attachments/xOn3VP/bannerST1.png`
- BANNER_ENABLE: t=4, duration=7 (disappears at t=11)
- BANNER_POSITION: bottom center, 80px from bottom edge
- VO_TEXT: "Download the game and assemble your crew."
- VO_TIMING: start at t=13 (over clip 3), or wherever pacing fits best
- Music volume: 0.35 (slightly lower to leave room for VO)
- VO volume: 1.0

---

## Budgets

| Item | Count | Cost |
|------|-------|------|
| NB2 image gen | 4 | $0.32 |
| Kling v3 Standard I2V 5s + audio | 4 | $2.52 |
| MiniMax TTS (VO) | 1 | ~$0.01 |
| MiniMax Music v2.6 | 1 | $0.03 |
| **Total** | | **~$2.88** |
