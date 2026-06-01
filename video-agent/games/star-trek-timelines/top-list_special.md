# TOP List — settings for Star Trek Timelines

Game-specific overrides for the `top-list` format. The format playbook (`rules/formats/top-list.md`) reads this file when it exists; Scenarist and Storyboarder load it automatically.

## Title card — FIXED brand reference (MANDATORY)

All Star Trek top-list videos MUST reuse ONE locked title-card design instead of inventing a fresh composition per episode. Only the theme line under `TOP-5` changes.

- **Reference image (Supabase):** `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/star-trek-timelines/branding/top-list-titlecard.png`
  - Also in `game_assets`: `character_name=branding:top-list-titlecard`, `asset_type=generated_ref`, tags `top-list,title-card,reference,branding`.
- **Composition (already baked into the reference — keep VERBATIM):** deep-space starfield background with a crescent planet top-right; a silver Starfleet delta/command emblem inside a laurel wreath at the top; a large metallic chrome `TOP-5` wordmark with cool blue edge-lighting in the center; a Starfleet hero ship (Enterprise-style) gliding over a planet's blue limb with lit engine nacelles at the bottom.
- **What changes per episode:** ONLY the theme. Add the `{THEME}` text (e.g. `EPIC BATTLES`, `STARFLEET SHIPS`, `GREATEST CAPTAINS`) directly BELOW the `TOP-5` lettering, rendered in the SAME metallic/chrome style with the same blue edge-light and a matching bold condensed face, centered, scaled to fit the frame width. Do NOT re-draw or move the `TOP-5`, the emblem, or the ship.

### Storyboarder build (title card / scene 0)

- Generate via NB2 **edit** (`fal-ai/nano-banana-2/edit`) with `image_urls: ["<titlecard reference URL above>"]` — NOT text-to-image from scratch.
- `image_prompt` intent: "Keep this exact title-card composition unchanged — the Starfleet laurel emblem, the metallic chrome TOP-5 wordmark with blue edge lighting, the starship over the planet, and the deep-space starfield. Add the text `{THEME}` directly below the TOP-5 lettering in the same brushed-metal chrome style with cool blue edge-light, bold condensed uppercase, centered, fitting the frame width, integrated as if part of the original design." Append the locked `visual_identity.style_tags` for the episode.
- `negative_prompt` (text legibility, mandatory): `warped text, illegible letters, garbled text, distorted typography, blurred title, missing letters, extra letters, duplicated TOP-5, second emblem, watermark`.
- This reference is brand-locked and is the SAME design regardless of the episode's photoreal/3D style choice — the title card is consistent channel branding; per-episode `style_tags` only flavor the added theme text and any subtle background grade, never the layout.

## Title card text
- `top_font`: "Eurostile Bold Extended" (used for any Editor-side text; the baked TOP-5 in the reference already defines the look)
- `accent_color`: `#ff9900` (LCARS orange) for Editor `#N` overlays
- `title_card_style`: brushed-metal chrome + cool blue edge-light + deep-space starfield (matches the locked reference)

## Numbers / names
- `number_font`: Montserrat Black (Editor `#N` overlay)
- `name_font`: Bebas Neue, uppercase (Editor `{NAME}` plate at y=1300 — see format collision note)

## Narrator
- `narrator_voice`: "George"
- `tone_directive`: "energetic countdown host, building excitement toward number one"

## Music
- `music_mood`: orchestral-sci-fi epic (default track: `heroic-neptune.mp3`)
