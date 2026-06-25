# TOP List — settings for Genshin Impact

Game-specific overrides for the `top-list` format. Use this file for countdowns on the Genshin channel; layout still comes from `rules/formats/top-list.md`.

## Visual style lock

- `style_tags`: `Genshin Impact anime style, cel-shaded character art, vibrant fantasy colors, soft outline anime aesthetic, magical elemental effects, Teyvat world environment, clean detailed character illustration`
- Use the game-style/anime character blocks from `games/genshin-impact/genshin-impact.md`.
- Do NOT use Dual-Style photorealistic counterpart blocks for top-list unless the user explicitly asks for a real-life/actor version.
- Do NOT use Pixar 3D, photorealistic, gritty live action, or Western comic style. The house style is bright anime cel-shading.

## Title card

- `top_font`: "Bebas Neue"
- `title_card_style`: anime gacha event splash art, floating Primogem shards, elemental sigils, gold ornamental frame accents, clean readable vertical composition
- `accent_color`: "#F5D060"
- Title text: `"TOP 5"` plus the episode theme, e.g. `"GENSHIN MEN"` or `"MALE CHARACTERS"`.
- No locked title-card reference exists yet. Generate the title card from scratch using NB2 text-to-image until a branded reference is created and uploaded.

## Overlay brand

Brand styling for graphic overlays. Scenarist fills `overlays[]`; layout comes from `top-list.md` → `## Overlays`.

- font_display: BEBAS
- font_name: BEBAS
- font_label: MED
- text_color: "#FFFFFF"
- accent_color: "#F5D060"
- stroke_width: 6
- channel_bug_url:

## Male character countdown defaults

If the user asks for `top 5 male characters`, `топ 5 мужских персонажей`, or equivalent without specifying the ranking principle, use this evergreen ranking basis:

- `ranking_basis`: lore impact + recognizability + visual variety, not current patch meta
- Order 5 → 1:
  - `#5`: Kazuha (Kaedehara Kazuha) — serene samurai wanderer, Anemo maple visual language
  - `#4`: Xiao — intense Yaksha, green-black Adeptus armor, darker combat energy
  - `#3`: Tartaglia (Childe) — Fatui Harbinger charisma, Hydro aggression, strong contrast against Xiao
  - `#2`: Neuvillette — Fontaine authority, Hydro dragon elegance, tall blue-white silhouette
  - `#1`: Zhongli — Geo Archon, iconic Liyue design, strongest evergreen lore/payoff choice

Use the exact `Character Prompt Blocks` for these characters from `genshin-impact.md`. If a different basis is requested (`meta`, `husbando`, `lore power`, `funniest`, `villains`), Scenarist may reorder or replace entries, but must write the chosen `ranking_basis` into `storyboard.json`.

## Rank-1 winner beat

For Zhongli as #1:

- Part 1: wide hero reveal in Liyue Harbor or near a golden Geo stone stele, amber light, floating Geo sigils, long coat silhouette readable.
- Part 2: close-up payoff with golden laurel, floating stone pillars, amber Geo shield shimmer, and a subtle gold `#1` winner aura. Keep the face and eyes clean; no UI labels or game HUD.

## Narrator

- `narrator_voice`: "George"
- `tone_directive`: "energetic anime countdown host, playful but not thirsty, building excitement toward number one"

## Music

- `music_mood`: ethereal epic anime countdown
