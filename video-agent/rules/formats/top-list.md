---
ready_to_post: yes
subtitles: true
overlays: true
---

# Format "TOP List" — countdown of top-5 characters / locations / items in a game

Stylized "TOP 5" countdown video: an animated title card in the game's visual language, then 5 items revealed in **5 → 1** order with the climax on #1. Narrator delivers one short, punchy line per item ("In third place: T'Pol from Enterprise — Vulcan grace and a logic-defying figure.").

This file is the **playbook**: when to use, concept, budget, role briefs. Craft rules — in `rules/roles/*.md`.

---

## When to use

Keywords: `"top-5"`, `"top 5"`, `"топ-5"`, `"топ 5"`, `"top list"`, `"топ"`, `"топ персонажей"`, `"top characters"`, `"top heroes"`, `"top locations"`, `"top items"`, `"best characters"`, `"ranking"`, `"рейтинг"`, `"countdown"`.

Typical themes: top-5 women characters, top-5 starfleet ships, top-5 villains, top-5 maps/locations, top-5 weapons/skins/items, top-5 ultimates.

Not for: news / patch recaps (use `news`), lore monologue (use `character-story`), single hero action scene.

---

## Concept

- **Genre:** stylized listicle countdown (Buzzfeed-meets-MTV-countdown, in game style)
- **Style:** taken from the exact `top-list` story bible (`style_tags`, palette, lighting), unless the user gives a live override. Game-wide or another format's style/appearance data is not a fallback.
- **Style consistency rule (HARD):** the visual style is described ONCE at the video level in `visual_identity.style_tags` and applied VERBATIM to every scene's `image_prompt`. All 7 scenes must look like the same artist/render pipeline made them. Mixing two different render media in the same video looks broken — even a single off-style scene wrecks the countdown rhythm. Per-scene style overrides are FORBIDDEN.
- **Style resolution at video start (MANDATORY).** Manager resolves the target style as live user instruction → exact `top-list` story bible `style_tags`. When the exact bible or required style data is missing, STOP and ask whether to create or complete it before generation; never auto-create it or fall back to game-wide data. The chosen style is frozen in `visual_identity.style_tags` and applied verbatim per the previous rule.
- **Anchor-ref ownership (HARD):** only refs owned by the exact `game + top-list + series` may be passed to NB2. Do not inspect refs visually to decide whether another format's asset is "close enough". Resolve ownership from the exact story bible and metadata. If an owned ref is missing, generate a new top-list-bound ref or use the NB2 text endpoint with the full top-list-owned character description and omit `image_urls` entirely.
- **N:** fixed **5 items**
- **Order:** **5 → 1** (climax at #1)
- **Rank #1 is ALWAYS rendered as 2 clips × 5s = 10s total** — split visually (wide hero shot → close-up payoff) with narrator carrying across both halves. This gives the climax breathing room and a cinematic match-cut moment that no other rank gets.
- **Duration:** ~35s story total (1× title 5s + 4× item 5s + 2× rank-1 climax 5s = 35s) plus a Supabase CTA pack-shot if the game has one. If no pack-shot exists, use a CTA overlay only on the SECOND part of rank-1.
- **Total scenes in storyboard.json: 7** (indices 0..6). Rank-1 occupies indices 5 and 6, both with `rank: 1`, distinguished by `part: 1` and `part: 2`.
- **Budget:** up to **$5.00** per video. Stop if spend > **$4.50**.
- **Frame format:** 9:16 (1080×1920)

### Models

- **Image:** Nano Banana 2 (title card + 4 ranked items + 2 rank-1 climax images, 7 generations total)
- **Video:** MiniMax H3 Max I2V (route `minimax.h3max.i2v`, `minimax/h3-max/image-to-video`) — 768P, numeric `duration` = `duration_sec`, `prompt_expansion_mode: "disabled"`. H3 always returns a soundtrack; this format never uses it (`scene_video_audio: "none"`). Keep the selected model/endpoint/route fixed; retry the same serialized request once, then stop. Kling v3 Standard and Kling 2.6 are not automatic fallbacks. H3 has no `negative_prompt`, `multi_prompt` or end frame.
- **Audio:** MiniMax TTS narrator overlay by default. Chatterbox is allowed only with an approved sample owned by the exact `top-list` story bible. ElevenLabs TTS and cross-format voice samples are forbidden. Music bed stays under everything.
- **Pre-built assets:** title card is generated inline. CTA is a **pack-shot from Supabase if the game has one** (query `game_assets` for `tags @> ["cta"]` and `asset_type` containing "video"); otherwise fall back to a drawtext CTA overlay on the rank-1 part-2 clip. Star Trek Timelines, for example, has `assets/star-trek-timelines/refs/cta.mp4` ready.

### Still shots: allowed

The scenarist may plan still shots (`motion: "still"`) under the rule, cap and fields in `rules/roles/scenarist.md` "Still shots" (§8; 7 scenes → at most 2). A still scene gets its start PNG as usual and is rendered free by the Animator (`tools/still_shot.py`, no paid clip), saving ~$0.41 per 5s scene; narration and overlays play over it as normal.

- **Best candidate:** the title card (scene 0). Its text is baked into the NB2 image, and an I2V clip can warp baked letters; a slow `push-in` still keeps the title exactly as generated and loses only drifting sparkles.
- **Other candidates:** in a locations or items list only, a low-rank entry (#5 or #4) that shows an empty location or an object at rest, with no character in focus.
- **Never a still:** a character entry (characters acting, a reaction, a gesture or expression beat), or either rank-1 climax scene (5 and 6). Zero stills is a normal result.
- A still scene's camera move is its `still_effect`; the three-motion-layer, ≥2-action and banned-phrase rules apply to animated clips.
- In the cost trials (Oct 2026, Star Trek aliens list) the scenarist picked exactly the title card; H3 Max plus that still saved 12% of the whole video against Kling v3 Standard.

---

## Budget (rough estimates)

| Component | 5s clip | 7× total |
|---|---|---|
| NB2 image | $0.08 | $0.56 |
| MiniMax H3 Max I2V 5s ($0.08/s on the returned ~5.18s; clip sound unused) | ~$0.41 | ~$2.90 |
| **Per animated scene** | **~$0.49** | |
| Still-shot scene (NB2 image only; `tools/still_shot.py` render is free) | $0.08 | |
| External TTS (MiniMax, or Chatterbox with an approved exact-format sample) | see `providers.json` | see `providers.json` |
| NB2 anchor refs (per new character — when not in Supabase) | $0.08 | varies |

| Variant | Total |
|---|---|
| Typical (H3 Max, all anchors in Supabase) | **~$3.75** (~$3.35 with a still title card) |
| Worst case (2 new anchor refs to generate) | ~$3.90 (~$3.50 with a still title card) |

Approx. totals = 7 images + 7 clips + a small TTS/music allowance. Each planned still scene saves ~$0.41. Slightly more than the previous 6-clip layout because rank-1 is split into 2 clips for the climax. 

---

## Video structure

| Index | Beat | Duration | Visual | Narrator (TTS) |
|---|---|---|---|---|
| 0 (title) | Hook / theme reveal | 5s | Title-card NB2 + I2V (or a still shot): sparkles, lens-flare, slow push-in, baked "TOP 5 {THEME}" text | Optional: 1-line teaser, e.g. `"Five Starfleet women who broke the warp drive — who tops the list?"` |
| 1 (`#5`) | Lowest entry | 5s | Item NB2 + I2V: subtle motion (camera arc, breath, magical aura) | `"In fifth place: {NAME} — {one-line reason}."` |
| 2 (`#4`) | Rising | 5s | Item NB2 + I2V | `"Number four: {NAME} — {one-line reason}."` |
| 3 (`#3`) | Mid | 5s | Item NB2 + I2V (slightly more intense motion) | `"At three: {NAME} — {one-line reason}."` |
| 4 (`#2`) | Penultimate, tease #1 | 5s | Item NB2 + I2V (energy step up) | `"And the runner-up: {NAME} — {one-line reason}."` |
| 5 (`#1`, part 1) | **Climax** — wide hero reveal | 5s | Item NB2 + I2V (large motion: pull-back, dramatic lighting, particles, banner reveal) | `"Topping the list: {NAME}. {one-line reason A — pacing setup}."` |
| 6 (`#1`, part 2) | **Climax payoff**; CTA overlay last 1.5s ONLY if no Supabase CTA pack-shot exists | 5s | Item NB2 (chain from scene 5) + I2V (closer angle: emotional push-in, slow-motion hair drift, screen flash) | `"{one-line reason B — emotional/legacy beat}. Follow for more tops."` |

- `camera_angle` MUST be different for adjacent clips (close-up → medium → low-angle → wide → hero shot)
- Energy / motion intensity escalates from #5 → #1
- Numbers count DOWN (5, 4, 3, 2, 1) — never up
- **Rank-1 split rule (HARD):** the climax is ALWAYS rendered as 2× 5s clips. Part 1 = wide / hero / establishing reveal of the character/item. Part 2 = closer / emotional payoff (push-in, slow-mo hair drift, eye contact, object glow, or detail macro). Both clips share the same `rank: 1`, `name`, `character_description`, and the same approved anchor/source description for that subject. They differ in `part` (1 vs 2), `camera_angle` (wide → close), `motion_prompt` (reveal → payoff), and `tts` (split sentence).
- Narrator TTS for rank-1 is split into 2 separate ≤10-word lines, one per clip. Part-2's TTS MUST end with literal `"Follow for more tops."`
- `cta_overlay: true` ONLY on part 2 (scene 6) and ONLY when no Supabase CTA pack-shot exists — never on part 1.

---

## Title card (clip 0) — special construction

> 🔒 **Locked brand reference (if the game provides one).** A game may pin ONE fixed title-card design in `games/{GAME_TAG}/top-list_special.md` (a branding asset tagged `title-card`). When present, the title card is NOT composed from scratch per episode — Storyboarder generates scene 0 via **NB2 `/edit`** with `image_urls: ["<reference URL>"]`, keeps the locked composition VERBATIM (emblem, wordmark, hero art, background), and only adds the per-episode `{THEME}` text in the reference's matching style. This keeps every countdown on-brand. **Star Trek Timelines has this locked reference** (`assets/star-trek-timelines/branding/top-list-titlecard.png` — Starfleet laurel emblem + metallic `TOP-5` + ship over planet; only `{THEME}` changes under the `TOP-5`). See `games/star-trek-timelines/top-list_special.md`. If a game has NO such reference, fall back to the from-scratch two-stage build below.

Two-stage build (fallback when there is no locked reference), the same as a regular scene but with text baked into the NB2 image:

1. **NB2 image** (608×1080):
   - Composition: hero collage / silhouette montage of the 5 items behind a big foreground title plate
   - Text baked into the image: `"TOP 5"` (huge) and `"{THEME}"` (e.g. `"STARFLEET WOMEN"`)
   - Style: from the locked exact-top-list `visual_identity` (`style_tags`, `palette`, `lighting`)
   - Font: read `top_font` from `games/{GAME_TAG}/top-list_special.md` if present, otherwise default **"Montserrat Black"** or **"Bebas Neue"** (bold, sans-serif, high stroke), accent color from game `palette`
   - Add: lens-flare, sparkles, magical particles, embers — whatever fits the game's tone

2. **Motion** — the title card is the format's best still-shot candidate (see "Still shots: allowed"): as a still, a slow `push-in` over the PNG keeps the baked text exactly as generated. When it is animated, **H3 Max I2V**, `duration: 5`, `scene_video_audio: "none"` with a silent `target_audio_url`:
   - `motion_prompt`: short, multi-action — sparkles drift, light rays sweep across the title, slow camera push-in, particles swirl. Two distinct movements minimum.
   - Title plate must stay readable: no warp, no rotation past 5°, no obscuring particles in the center 60% of the frame
   - H3 has no `negative_prompt`; the text-legibility guard is the closing sentence `Text stays sharp and unchanged.` (plus `Mouth stays closed; no talking.` if a face is visible in the collage)

3. **No text-overlay pass needed** in Editor for the title card — text is baked into NB2. Editor only handles the optional narrator subtitle.

---

## Per-item clip (clips 1–5) — visual structure

NB2 image of the character / location / item, **no number-text baked in** (numbers are added by Editor as a drawtext/PIL overlay, so we can iterate fast without re-rendering NB2):

- Composition: hero pose / iconic shot of the item. Character/object occupies center 50–70% of frame, leaves room top-left or top-right for the number overlay
- Style: from the locked exact-top-list `visual_identity` (`style_tags`, `palette`, `lighting`)
- For locations: wide establishing shot, optional foreground silhouette for depth
- For items/weapons: 3/4 hero-product angle on a stylized background (smoke, sparks, energy)

I2V `motion_prompt`: ≥2 distinct micro-motions, e.g. `"hair drifts in low gravity AND camera arcs slowly to the right; particles drift across the lens"`. Escalate motion intensity #5 → #1.

---

## Overlays

Graphic overlays (NOT subtitles) — rendered by `tools/overlays.py` from `clips[].overlays[]`,
per-scene before concat. **LAYOUT here; font/color/stroke come from `games/{tag}/{tag}.md` →
`## Overlay brand`.** Never bake into NB2. Schema: `rules/roles/scenarist.md`.

Top-list item clips use rank overlays ONLY. **Do not render character/item names as graphic overlays.**
Name plates cover faces too often in vertical character shots and compete with subtitles. The name must be
communicated in narration instead (see `## TTS name lock` below).

| # | type | position | size | enable | font role | text source |
|---|------|----------|------|--------|-----------|-------------|
| 1 | `rank_number` `"#5"` | `80,200` (top-left) | 220 | whole clip | display (accent color + stroke) | `"#{rank}"` |

Example overlay objects (brand fields from game config):
```json
"overlays": [
  {"type":"rank_number","text":"#5","position":"80,200","font":"MONT_BLACK","size":220,"color":"yellow","stroke":{"color":"black","width":4}}
]
```

> HARD RULE: `item_name` overlays are banned in top-list. If the audience needs the name, the narrator
> says it. The only always-on item overlay is `rank_number`.

## TTS name lock

Every ranked item scene must explicitly say the item/character `name` in its `tts`.

- Ranks 5..2: the `tts` line must include the exact `name` string from the scene object after the rank phrase.
- Rank 1 part 1: the `tts` line must include the exact `name` string after `"Topping the list:"`.
- Rank 1 part 2 may omit the name if part 1 already said it, but must not introduce a conflicting nickname.
- Do not rely on subtitle-only or overlay-only naming. If the name is not spoken, the scene fails Scenarist validation.

### CTA — pack-shot from Supabase (preferred)

If `game_assets` has a CTA video (`tags @> ["cta"]`, `asset_type` like "%video%" OR file extension `.mp4`):
- Download once at Phase 0 (Manager), pass URL/path to Editor as `CTA_PATH`
- Editor normalizes (scale 1080×1920, fps=30, AAC 128k) and **concatenates after scene 6** as the final clip
- Apply fade-to-black ONLY on the CTA tail (last 0.5–1.0s), NOT on scene 6
- No drawtext CTA on scene 6 in this path
- Music: fade out music 0.5s before the CTA clip starts so the pack-shot's own audio (if any) breathes; if pack-shot is silent, music continues at volume 0.10 under the pack shot

### CTA — fallback drawtext (only if no Supabase pack-shot)

If no Supabase CTA video exists for the game: drawtext on the rank-1 part-2 clip (scene 6), last 1.5s: `"Follow for more tops →"` lower-center, white on translucent black box. Fade out final 1.0s of scene 6.

---

## Subtitles

Narrator subtitles — the **one universal style** (editor.md §6), generated by Editor via whisper on
`build/voice-final.wav` (per-scene TTS concatenated in order). One `build/subs.ass` for the whole video,
burned as the last video filter. CAPS 72px, MarginV=520 (occupies y≈1256–1400).
No per-scene drawtext / manual style / position override.

---

## Prompting rules (NB2 + I2V)

### NB2 chain

- **Anchor ref:** use only a permanent ref explicitly recorded by the exact `top-list` story bible and tagged for the exact game/format/series. Never search broadly by character name, visually inspect candidates, or reuse another format's ref. If no owned ref exists, call the NB2 text endpoint with the full top-list-owned `character_description` + locked style tags and omit `image_urls` entirely (never pass an empty array).
- **Chain strategy:** `[anchor_ref?, prev_scene?]` (max 2 refs). Title card has no prev_scene — pure text-to-image with style refs only. For ranks 5–2 each character is different, so chaining on prev_scene would bleed the previous character's identity into the next — usually anchor-only is safer. **The rank-1 climax pair IS the exception**: scene 6 ALWAYS chains on scene 5 (same character, style continuity guaranteed by the pair).
- **Identity:** `visual_identity.character_description` is verbatim across the brief; per-item `character_description` overrides for that specific entry only.
- **Style verbatim:** the EXACT `visual_identity.style_tags` string is appended to every `image_prompt` (every scene, no exceptions). Storyboarder MUST copy-paste it; rewording or paraphrasing loses style fidelity.

### Rank-1 climax pair — visual differentiation (HARD RULE)

Scene 5 (part 1) and scene 6 (part 2) feature the SAME character. To prevent NB2 from copying scene-5 verbatim when chained, scene 6's `image_prompt` MUST add a **"winner beat"** that visually distinguishes it as the victory shot — choose one or combine:

- **Crown / laurel wreath** (gold laurel above the head)
- **Fireworks / golden sparks bursting** around the character
- **Pedestal / podium / raised platform** lifting the character
- **#1 banner unfurling** behind them
- **Golden spotlight from above** + soft confetti
- **Trophy / medal** held or floating beside them

Combined with a tighter crop (close-up vs scene 5's wide hero), the second image must read clearly as the "this is the winner" moment — not a static rerun of part 1.

### Selection rules for ranked characters (HARD RULE)

- When the user asks for a demographic/category-limited ranking (male characters, women, villains, archons, ships, locations, weapons), every ranked entry MUST satisfy that category. Do not include a mascot, companion, child character, object, or mixed-gender duo unless the user explicitly asks for it.
- Character appearance text must come from the exact `top-list` story bible. Do not reuse game-wide or another format's Character Prompt Blocks. If an eligible entry lacks a top-list-owned description, stop and ask whether to add it rather than silently copying or substituting an appearance.
- The ranking should have one clear principle stated in `description` or `ranking_basis`: popularity / lore impact / meta power / visual charisma / comedy value. Do not silently mix criteria scene by scene.
- For live-service games, avoid claiming "current meta" unless the user explicitly requests a patch/meta ranking and the latest game state has been verified. For evergreen shorts, prefer lore impact + recognizability + visual variety.
- Keep rank variety visual as well as narrative: adjacent entries should not share the same dominant element/color/faction/location if an equally strong alternative exists.

## Story bible (mandatory for top-list)

Every game that runs `top-list` keeps local state in `games/{GAME_TAG}/top-list_story_bible.json`.
Manager loads it through `tools/build_context.py` during Phase 0 and updates it after the final video is approved/published.

Generation may not start without this exact bible and its required style/appearance/asset ownership data. Missing or incomplete bible → STOP and ask the user whether to create or complete it; never auto-create it or borrow data from another format.

Purpose:
- Prevent repeating the same top list under a slightly different title.
- Track recent categories (`male-characters`, `villains`, `locations`, `weapons`, etc.).
- Track winners and repeated entries so the channel does not overuse the same character/item.
- Keep a record of the ranking basis, because "best", "strongest", "popular", "lore impact", and "visual charisma" are different lists.

Schema:
```json
{
  "series_id": "top-list-{GAME_TAG}",
  "game_tag": "{GAME_TAG}",
  "title": "{Game Name} Top Lists",
  "created_at": "YYYY-MM-DD",
  "last_episode": 0,
  "anti_repetition": {
    "cooldown_episodes": 6,
    "recent_themes": [],
    "recent_categories": [],
    "recent_winners": [],
    "recent_entries": []
  },
  "reserved_topics": [],
  "lists": [
    {
      "episode": 1,
      "date": "YYYY-MM-DD",
      "theme": "GENSHIN MEN",
      "category": "male-characters",
      "ranking_basis": "lore impact + recognizability + visual variety",
      "entries": [
        {"rank": 5, "name": "Kazuha"},
        {"rank": 4, "name": "Xiao"},
        {"rank": 3, "name": "Tartaglia"},
        {"rank": 2, "name": "Neuvillette"},
        {"rank": 1, "name": "Zhongli"}
      ],
      "winner": "Zhongli",
      "final_url": "",
      "youtube_url": "",
      "duration_sec": null,
      "status": "completed",
      "notes": ""
    }
  ]
}
```

Before Scenarist:
- Read `Story State` from `merged-context.md`.
- Do NOT reuse a theme/category that appears in the recent cooldown unless the user explicitly asks for a remake.
- Do NOT reuse the same #1 winner from the last cooldown window unless the user explicitly asks for that character/category.
- Reusing 1-2 popular characters across different categories is allowed, but the full five-entry lineup must not duplicate a previous list.

After publishing:
- Manager appends one `lists[]` entry with the final theme, category, ranking basis, entries, winner, URLs, duration, and status.
- Manager updates `last_episode` and the `anti_repetition` FIFO arrays.
- If a run is cancelled after storyboard approval but before publish, log it with `status: "cancelled"` and `final_url: ""` so parallel workspaces know the topic was attempted.

### I2V (H3 Max)

- `scene_video_audio: "none"` and a silent `target_audio_url` on every animated clip (always — TTS overlay handles sound, music bed handles ambience; H3's own soundtrack is discarded)
- `duration: 5` (locked for every clip including title; a still scene keeps `duration_sec: 5`)
- `motion_prompt`: minimum 2 different actions, escalating from #5 → #1
- Title card extra: when animated, the prompt ends with `Text stays sharp and unchanged.` (H3 has no `negative_prompt`); as a still it needs no guard
- Polling: done by `tools/kling_runner.py` against the route's poll base in `tools/video_routes.json` (H3 Max: `https://queue.fal.run/minimax/h3-max`); never poll by hand

---

## Music

- **Per-game mood** — pulled from `games/{GAME_TAG}/{GAME_TAG}.md` (e.g., MLBB → anime-epic, Star Trek → orchestral-sci-fi, Marvel Snap → comic-burst). If game config doesn't specify, default to **"hype / epic countdown"**.
- Volume: `0.15`
- Apply via `amix` on the concatenated video with `apad` on music side. **NEVER `-shortest`.**
- Optional: small `volume` boost (×1.5) on clip 5 (`#1`) for the climax. Implement via timeline crossfade if used.

---

## Voice generation

| Role | Default route | Voice intent | Notes |
|---|---|---|---|
| Narrator | MiniMax | energetic countdown host | Chatterbox only with an approved exact-top-list sample recorded in the story bible |

Lines are **short** (8–15 words). Voice intent: `"energetic countdown host, building excitement toward number one"`. ElevenLabs TTS and cross-format samples are forbidden.

---

## Game-specific overrides (optional)

`games/{GAME_TAG}/top-list_special.md` (create only if needed):

```markdown
# TOP List — settings for {Game Name}

## Title card
- `top_font`: e.g. "Eurostile Bold Extended" (Star Trek), "Anime FX" (MLBB)
- `title_card_style`: extra style line for NB2 prompt
- `accent_color`: hex for text stroke / glow

## Numbers
- `number_font`: defaults to top_font
- Names are spoken in TTS, not rendered as overlays.

## Narrator
- `voice_intent`: e.g. "energetic countdown host"
- `tone_directive`: extra direction for TTS

## Music
- `music_mood`: e.g. "orchestral-sci-fi", "anime-epic", "comic-burst"
```

If file absent → defaults from this playbook.

---

## Storyboard JSON (template)

```json
{
  "format": "top-list",
  "theme": "STARFLEET WOMEN",
  "game_tag": "star-trek",
  "visual_identity": {
    "style_tags": "from exact top-list story bible",
    "palette": "from exact top-list story bible",
    "lighting": "from exact top-list story bible",
    "top_font": "Eurostile Bold Extended",
    "accent_color": "#F5A623"
  },
  "music": {"mood": "orchestral-sci-fi", "volume": 0.15},
  "voices": {
    "narrator": {"voice_intent": "energetic countdown host", "language_code": "en"}
  },
  "scenes": [
    {
      "index": 0,
      "role": "title_card",
      "clip_type": "title",
      "duration_sec": 5,
      "title_text": "TOP 5",
      "subtitle_text": "STARFLEET WOMEN",
      "tts": "Five Starfleet women who broke the warp drive — who tops the list?",
      "image_prompt": "...",
      "motion_prompt": "sparkles drift across title, lens flare sweeps left to right, slow camera push-in"
    },
    {
      "index": 1,
      "rank": 5,
      "name": "T'Pol",
      "clip_type": "item",
      "duration_sec": 5,
      "camera_angle": "medium close-up, three-quarter",
      "character_description": "Vulcan woman, dark hair, blue Enterprise NX-01 uniform...",
      "tts": "In fifth place: T'Pol from Enterprise — Vulcan grace and a logic-defying figure.",
      "image_prompt": "...",
      "motion_prompt": "eyes blink subtly, hair drifts, camera arcs slowly to the right",
      "overlays": [
        {"type":"rank_number","text":"#5","position":"80,200","font":"MONT_BLACK","size":220,"color":"yellow","stroke":{"color":"black","width":4}}
      ]
    },
    {"index": 2, "rank": 4, "name": "...", "...": "..."},
    {"index": 3, "rank": 3, "name": "...", "...": "..."},
    {"index": 4, "rank": 2, "name": "...", "...": "..."},
    {
      "index": 5,
      "rank": 1,
      "name": "Seven of Nine",
      "clip_type": "item_climax",
      "duration_sec": 5,
      "camera_angle": "low-angle hero shot",
      "tts": "Topping the list: Seven of Nine. The queen of Borg-meets-bombshell. Follow for more tops.",
      "image_prompt": "...",
      "motion_prompt": "camera zooms in, screen flash, particles burst from behind, hair drifts",
      "cta_overlay": true,
      "overlays": [
        {"type":"rank_number","text":"#1","position":"80,200","font":"MONT_BLACK","size":220,"color":"yellow","stroke":{"color":"black","width":4}}
      ]
    }
  ]
}
```

---

## Role briefs

### Scenarist

- Exactly **7 scenes**: 1 title + 4 items (ranks 5..2) + 2 climax clips (both rank 1, `part` 1 and 2).
- Check `Story State` from `merged-context.md` before choosing the theme/ranking. Avoid recent categories, full lineups, and winners unless the user's idea explicitly repeats them.
- Set top-level `category` and `ranking_basis` in `storyboard.json`. `category` should be machine-friendly (`male-characters`, `villains`, `locations`, `weapons`, etc.).
- Title scene fields: `role: "title_card"`, `clip_type: "title"`, `title_text`, `subtitle_text`, optional `tts`. It is the format's best still-shot candidate (see "Still shots: allowed").
- Item scene fields: `rank` (int), `name`, `character_description` (8+ visual details), `camera_angle`, `motion_hint`, `tts`, **`overlays[]`** (one object: `rank_number` `"#{rank}"` — see the `## Overlays` section).
- Rank-1 climax: TWO scenes (indices 5 and 6) BOTH with `rank: 1`. Index 5 = `part: 1`, `clip_type: "item_climax"`. Index 6 = `part: 2`, `clip_type: "item_climax"`. Same `name` and `character_description`. Different `camera_angle` (wide → close), `motion_hint`, and `tts` text.
- `tts` for ranks 5..2: **8–15 words**, must START with the rank phrase ("In fifth place: / Number four: / At three: / And the runner-up:"). Include the exact `name` + one-line reason.
- `tts` for rank 1: **two short lines (≤10 words each)**. Part 1 starts with `"Topping the list:"` + exact `name` + a pacing-setup beat. Part 2 = emotional/legacy beat + literal closing `"Follow for more tops."`
- `camera_angle` different for adjacent scenes (including across the rank-1 pair: e.g. wide hero → close-up push-in); every scene has an active camera move (a still scene's `still_effect` counts).
- `motion_hint` ≥2 different actions per animated scene; intensity escalates 5→1; rank-1 part 2 is the most intense.
- Still shots: optional, per "Still shots: allowed" above and `rules/roles/scenarist.md` "Still shots"; zero is a normal result.
- `cta_overlay: true` ONLY on the rank-1 part-2 scene (index 6) when no Supabase CTA pack-shot exists. NOT on part 1.
- Read style, palette, lighting, and appearance only from the exact `top-list` story bible (or live user override). `top-list_special.md` may supply format-owned layout/font directives, but never cross-format appearance/style/voice assets.
- General rules — `rules/roles/scenarist.md`

### Storyboarder

- **7 NB2 generations** (title + 4 items + 2 climax clips for rank-1). All 608×1080 (9:16).
- **Title card NB2**: bake `"TOP 5"` + `"{theme}"` text into the image using `top_font` from `visual_identity` (defaults Montserrat Black / Bebas Neue). Use only exact-top-list-owned style refs, no prior-scene ref. Add sparkles/lens-flare/particles aligned with the locked palette.
- **Item NB2**: do NOT bake numbers — numbers are an Editor overlay. Compose with center 50–70% subject + clear space top-left for the `#N` overlay.
- **No on-screen text on character images (HARD RULE).** Per-item NB2 outputs must be CLEAN illustrations — no character-card layout, no game UI labels, no nameplate banners, no era/series logos ("STAR TREK: DEEP SPACE NINE", "VOYAGER" etc.), no #N number, no caption strip, no rarity stars/borders. All text and number callouts come from Editor drawtext overlays. Every per-item `image_prompt` MUST end with `". Clean illustration with NO on-screen text, NO captions, NO labels, NO logos, NO nameplate banners, NO game UI of any kind."` Push the same intent into NB2 `negative_prompt` so any drift is caught: `"on-screen text, character card layout, trading card, nameplate, banner text, game UI labels, captions, watermark, rarity stars, series logo, era label, subtitle"`. (The H3 clip takes no `negative_prompt`; a clean start frame is the guard.)
- **Rank-1 climax pair (scenes 5 + 6):** generate part 1 first (wide hero shot, ≥7-detail backdrop, dramatic establishing composition). Then generate part 2 using part 1 as `[anchor_ref?, scene-5_image]` chain — same character, closer angle, same lighting/palette. Part 2 = closer crop, more intimate; show eyes/face cleanly for the emotional payoff.
- Chain refs: `[exact_top_list_anchor_ref?, same_run_prev_scene?]`; title card uses no prior-scene ref; rank-1 part 2 ALWAYS chains on part 1 from the same run.
- An anchor is eligible only when the exact `top-list` story bible records it and its metadata matches the exact game/format/series. Do not visually compare or borrow another format's asset. If the owned anchor is missing, use NB2 text-to-image with the full top-list-owned `character_description` and omit `image_urls`, or generate/upload a new reusable top-list-bound anchor when repeated use is planned.
- Character description verbatim from `visual_identity` + per-scene additions.
- General rules — `rules/roles/storyboarder.md`

### Animator

- **Model:** all animated scenes via the format's route, **MiniMax H3 Max I2V** (`minimax.h3max.i2v`), through `tools/kling_runner.py` (payload: `prompt`, `image_url`, numeric `duration`, `resolution: "768P"`, `prompt_expansion_mode: "disabled"`; see `tools/examples/minimax-h3-max-scene-video.job.json`). `expect.audio: "optional"`, never `"forbidden"` (H3 always returns a soundtrack). Write `scene_video_audio: "none"` on every scene. The model/endpoint/route and serialized request stay fixed; retry once on the same route, then stop; any other route (Kling v3 Standard, Kling 2.6) requires a separate explicit user authorization after the stopped run.
- Every animated clip adds a **silent `target_audio_url`** of its `duration` (clip sound is discarded): a data URI from `tools/silent_audio.py --duration <duration_sec> --out <file>`, read into the job with `jq --rawfile` before `--preflight` (`rules/roles/animator.md` §2a "Silent `target_audio_url`"; it stops H3 from mouthing words, Test 6b).
- **Still scenes** (`motion: "still"`, usually the title card): no paid job; render with `tools/still_shot.py` as `rules/roles/animator.md` describes.
- **All 7 scenes:** `duration: 5`, **NO end frame** (start frame only — H3 has none; on Kling, end frames make it interpolate-then-freeze).
- **Three motion layers per animated clip (MANDATORY).** Every animated clip's `motion_prompt` must specify three concurrent layers, each continuing throughout the full 5s — no "then settles" / "then steady" / "then dies" cues (I2V models read those as freeze):
  1. **Camera move** — pick one per clip: slow push-in, slow pull-back, lateral dolly, low boom up, crane up, parallax handheld drift, slow arc. Distribute variety across the 7 clips. NEVER "camera holds steady".
  2. **Environment motion** — wind, smoke, sparks, particles, light flicker, distant figures, holographic UI motion, console glow pulses, viewscreen shimmer, starfield drift. Continuous throughout the 5s.
  3. **Character action** — one gesture or expression beat sustained through the clip (slow head turn, eyes lifting, half-smile forming, jaw tightening, hand drifting). Sustained, NOT completed mid-clip.
- **Phrasing rules for `motion_prompt`:**
  - Continuous-tense verbs (`is drifting`, `tightens`, `lifts gently`) and explicit duration cues (`throughout the shot`, `held for the full 5 seconds`, `continues across the frame`).
  - **Banned phrases (read as freeze by I2V models):** `"then settles"`, `"then steady"`, `"then holds"`, `"then dissipates"`, `"then dies"`, `"camera holds steady"`, `"hold position"`, `"no morphing"`, `"maintain exact character appearance"`. NEVER use.
  - **Avoid stacked negative listings.** Do not pile `No walking, no running, no fighting, no impact`. Replace with positive grounded instructions ("character remains rooted at the console", "feet planted, weight shifts gently").
  - Trust the I2V model to hold identity from the start frame — do not write defensive identity-lock phrases.
- **Micro vs. macro motion.** Avoid full-body locomotion (walking, running, combat hits) — identity drift becomes visible. Motion WITHIN the frame (head, hands, torso, breath, sustained gestures, environment) MUST be alive.
- **Rank-1 climax pair (scenes 5 + 6):** generate independently as two separate H3 Max calls (no end frame; two distinct shots; never a still). Part 1 motion: pull-back reveal + viewscreen flare + golden particles bursting outward + still-sustained character pose. Part 2 motion: slow push-in + laurel wreath shimmer + golden sparks rising + character eyes lifting to camera in the final third. Strongest motion intensity of the whole video.
- **No `negative_prompt` on H3 — closing sentences instead.** Kling's universal anti-text / anti-talking `negative_prompt` becomes at most two short plain sentences at the end of `prompt` (`rules/roles/animator.md` §2a), never a banned phrase:
  - Ranked items (scenes 1–6): `Mouth stays closed; no talking.` whenever a face is visible; add a second sentence only if an exclusion is truly needed. The clean start frame (no baked text, Storyboarder rule) is the anti-text guard.
  - Animated title card (scene 0): `Text stays sharp and unchanged.` (plus the mouth sentence if a face is visible). A still title card needs neither.
  - No sound clause is needed (clip sound is discarded). Keep prompts ≤512 UTF-8 bytes.
- Polling: done by `tools/kling_runner.py` against the route's poll base in `tools/video_routes.json` (H3 Max: `https://queue.fal.run/minimax/h3-max`); never poll by hand.
- Validate after each clip: filesize > 100KB, ffprobe duration within 0.8s of 5.0s (H3 returns ~5.18s; the Editor trims it to `duration_sec`, do not trim yourself). A still clip is exact (±0.05s).
- General rules — `rules/roles/animator.md`

### Sound

- **TTS route:** MiniMax for the narrator by default; Chatterbox only with an approved exact-top-list sample from the story bible. ElevenLabs TTS is forbidden.
- Voice intent comes from `voices.narrator`; never look up or reuse another format's sample.
- Save each `.mp3` locally; upload only when a downstream API requires a permanent run-scoped URL.
- **Subtitles are not generated by Sound.** Editor builds one universal whisper-timed `build/subs.ass` from the final shaped voice track and burns it as the last video filter.
- **Music bed**: generate with MiniMax Music from the storyboard mood, `volume=0.15`. Retry the same request once, then stop; never substitute a local/Supabase track or silently omit music.
- General rules — `rules/roles/sound.md`

### Editor

- For each item clip with a `rank` (scenes 1–6), `clips[].overlays[]` carries **one always-on overlay** (rendered by `tools/overlays.py` before concat; font/color from game `## Overlay brand`):
  - `rank_number` `#{N}` huge top-left (display font ~220px, accent stroke), full duration
- `item_name` overlays are banned for top-list. Names are carried by `tts`.
- Rank-1 pair (scenes 5 + 6) both show `#1`. They are visually continuous (same rank), but distinct shots.
- Title card (scene 0): NO number/name overlay (text is in NB2). Its optional narration is handled by the universal ASS timeline.
- Per-scene branches apply rank overlays and normalization before concat (fill-and-crop to 1080×1920 ending in `setsar=1`, 30fps; H3 clips trimmed to `duration_sec`, still clips already exact; `rules/roles/editor.md`). A still scene gets its rank overlay like any other scene. Burn the one universal ASS only after concat, as the last video filter.
- Concat with re-encode (NOT `-c copy`); hard cuts, NO crossfade between items (countdown rhythm). Hard cut also between rank-1 part 1 and part 2 — the match-cut is the moment, not a dissolve.
- **CTA pack-shot from Supabase (preferred):** query `game_assets` for `tags @> ["cta"]` + video asset. If present, normalize (1080×1920, 30fps, AAC 128k) and concatenate AFTER scene 6 as the final clip. Apply fade-to-black on the pack-shot tail (last 0.5–1.0s), NOT on scene 6. Music fades 0.5s before the pack-shot starts.
- **CTA fallback (only if no Supabase pack-shot):** drawtext `"Follow for more tops →"` lower-center on translucent black box on scene 6, last 1.5s. Fade-to-black final 1.0s of scene 6.
- Music: `amix` with TTS, music `volume=0.15`, music `apad`. **NEVER `-shortest`.**
- General rules — `rules/roles/editor.md`

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/top-list/
├── storyboard.json
├── scenes/
│   ├── scene-0/                # title card
│   │   ├── scene-0.png         # NB2 with baked title text
│   │   ├── scene-0.mp4         # H3 I2V raw, or local still render
│   │   ├── scene-0.mp3         # TTS (optional)
│   │   └── scene-0-sub.mp4     # with subtitle (if tts)
│   ├── scene-1/                # rank #5
│   │   ├── scene-1.png         # NB2 (no number)
│   │   ├── scene-1.mp4         # H3 I2V raw
│   │   ├── scene-1.mp3         # narrator TTS
│   │   ├── scene-1-overlay.mp4 # with #5 rank overlay
│   │   └── scene-1-sub.mp4     # + subtitle
│   ├── scene-2/  # rank #4
│   ├── scene-3/  # rank #3
│   ├── scene-4/  # rank #2
│   ├── scene-5/  # rank #1 part 1 (wide hero reveal)
│   └── scene-6/  # rank #1 part 2 (close payoff + CTA + fade)
├── concat-list.txt
└── final.mp4
```

---

## Validation before publishing

Generated PNG/MP4/audio receives technical validation only (path, size, hash, dimensions, codec, duration, schema). Visual composition and text-legibility items below are prompt/schema requirements and user-review criteria; they do not authorize AI Vision, frame sampling, or machine semantic inspection.

- [ ] `format: "top-list"`, `theme` set, exactly **7 scenes** (1 title + 4 items + 2 rank-1 climax clips)
- [ ] `category` and `ranking_basis` set at top level
- [ ] Story bible checked before Scenarist; theme/category/winner/full lineup do not violate recent cooldown
- [ ] Ranks present: 5, 4, 3, 2, 1, 1 (rank 1 appears twice with `part: 1` and `part: 2`); no other duplicates / gaps
- [ ] Title-card prompt/schema contains `"TOP 5"` + `"{theme}"`; generated file passes programmatic size/dimension/hash checks, with appearance left to user review
- [ ] Item NB2s have NO number baked in (numbers come from Editor overlay)
- [ ] Animated scenes use `minimax.h3max.i2v` with `scene_video_audio: "none"`, a silent `target_audio_url` and no end frame, duration within 0.8s of 5s (played as 5s after the Editor's trim); still scenes (if any) have `scene_video_kind: "still"`, are not a character entry or the rank-1 pair, and stay within the `rules/roles/scenarist.md` "Still shots" cap
- [ ] `camera_angle` different for adjacent scenes (including across rank-1 pair: part 1 wide → part 2 close)
- [ ] `motion_hint` ≥2 different actions per animated scene; intensity escalates 5→1; every scene has an active camera move (a still's `still_effect` counts)
- [ ] Each item TTS begins with the correct rank phrase ("In fifth place / Number four / At three / Runner-up / Topping the list")
- [ ] Each ranked item TTS says the exact scene `name` (rank-1 part 1 must say it; part 2 may omit it)
- [ ] Rank-1 TTS split across two parts: part 1 ≤10w; part 2 ≤10w and ends with literal "Follow for more tops."
- [ ] TTS uses MiniMax, or Chatterbox only with an approved exact-top-list sample; no ElevenLabs TTS or cross-format voice sample
- [ ] Rank overlays are applied on per-scene branches before concat; one universal whisper-timed ASS is burned last after concat; no `item_name` overlays
- [ ] CTA: if game has Supabase pack-shot video → concatenated after scene 6 (no drawtext CTA on scene 6, no fade-to-black on scene 6 — fade goes on pack-shot tail). If no pack-shot → drawtext CTA on scene 6 last 1.5s + fade-to-black on scene 6 last 1.0s.
- [ ] Per-item prompts/negative prompts enforce CLEAN illustrations with no on-screen text, character-card layout, game UI labels, era logos, or nameplate banners; generated files receive technical checks only
- [ ] `visual_identity.style_tags` was resolved from the exact top-list bible or a live user override and applied verbatim to every `image_prompt`
- [ ] Every animated clip's `motion_prompt` includes three concurrent layers (camera move + environment motion + character action) and contains NONE of the banned freeze phrases (`then settles`, `then steady`, `camera holds steady`, `hold position`, `no morphing`, `maintain exact character appearance`)
- [ ] No H3 job has a `negative_prompt`; every animated prompt ends with at most two closing sentences: `Mouth stays closed; no talking.` whenever a face is visible, `Text stays sharp and unchanged.` on an animated title card
- [ ] Music `volume=0.15`, mixed via `amix` + `apad`, NO `-shortest`. Music fades 0.5s before pack-shot starts (if pack-shot path used).
- [ ] `final.mp4`: 1080×1920, 30fps. Duration = ~35s without pack-shot or ~35s + pack-shot length. Budget ≤ $5.00

---

## Anti-patterns

- ❌ Baking numbers (`"#5"`, `"#4"`...) into NB2 — locks the rendering, can't iterate. Always overlay in Editor.
- ❌ Rendering character/item names as overlays (`item_name`) in top-list — they cover faces and fight subtitles. Names must be spoken in TTS.
- ❌ TTS that skips the scene `name` — if the name is not said aloud, the audience loses the entry after name overlays were removed.
- ❌ Counting UP (1→5). Always 5→1 with climax on #1.
- ❌ Same `camera_angle` on adjacent items (kills rhythm).
- ❌ Using the I2V clip's own sound (`scene_video_audio` must be `"none"`), or an H3 clip without its silent `target_audio_url` — TTS+music bed already cover sound, and without the silent track H3 mouths words.
- ❌ `negative_prompt`, `generate_audio`, `multi_prompt` or an end frame on the H3 route (not supported; guards are closing sentences).
- ❌ Per-scene drawtext subtitles or format-local subtitle styling. Use one universal whisper-timed ASS on the final shaped voice timeline and burn it last.
- ❌ Crossfade between item clips — countdown needs hard cuts for snap rhythm.
- ❌ `-shortest` in FFmpeg (universal). Always `apad` on music side.
- ❌ ElevenLabs TTS, a cross-format voice sample, or Chatterbox without an approved exact-top-list sample.
- ❌ An animated title card without the closing `Text stays sharp and unchanged.` — I2V warps baked text without a guard. A still title card avoids the problem.
- ❌ A still on a character entry or on either rank-1 climax scene — stills are for the title card or a character-free low-rank entry only.
- ❌ Generating a brand-new CTA video inside the top-list run. If a game already has a Supabase CTA pack-shot, use it. If it does not, use the drawtext fallback on rank-1 part 2.
- ❌ TTS lines longer than 15 words on rank 5–2, or longer than 10 words on rank-1 parts — eats into the 5s clip, narration runs over the next clip's overlay.
- ❌ Rendering rank-1 as a single 5s or 10s clip. RULE: rank-1 is ALWAYS 2× 5s clips with a hard match-cut. No exceptions.
- ❌ Identical `camera_angle` between rank-1 part 1 and part 2 — the climax pair must visually contrast (wide → close).
- ❌ CTA overlay on rank-1 part 1 — only part 2 carries the CTA and the fade-to-black.
- ❌ Mixing visual styles between scenes (e.g. a rendered 3D look in one scene, a painted illustration in the next). Style is locked at the VIDEO level in `visual_identity.style_tags` and applied verbatim to every `image_prompt`. Even one off-style scene breaks the countdown rhythm.
- ❌ Pulling a broad Supabase anchor by character name or visually comparing candidates. Use only the exact-top-list ref recorded in the story bible and ownership metadata; otherwise use text-to-image with top-list-owned appearance data or generate a new top-list-bound ref.
- ❌ Scene 6 looking identical to scene 5. The chain reference makes NB2 reproduce part 1 unless the prompt explicitly demands a NEW visual element (crown / laurel wreath / fireworks / pedestal / #1 banner) plus a tighter crop. No winner beat = broken climax cut.
- ❌ Per-item NB2 outputs containing baked text — character-card layouts, game UI labels, era/series logos ("STAR TREK: DEEP SPACE NINE"), nameplate banners, rarity stars. Per-item images must be CLEAN; all callouts come from Editor drawtext overlays.
- ❌ Generating without resolved exact-top-list `style_tags`, or silently falling back to game-wide/another-format style data.
- ❌ `motion_prompt` with "camera holds steady" / "then settles" / "then steady" / "hold position" / "no morphing" / "maintain exact character appearance" — I2V models read these as freeze cues and produce static clips. Every animated clip needs three concurrent motion layers (camera + environment + character); a planned still shot is a rendered camera move chosen in Phase 1 under "Still shots: allowed", not a freeze prompt.
- ❌ Using a drawtext CTA overlay when the game already has a Supabase pack-shot video. The pack-shot is the on-brand, branded ending; drawtext is the fallback.
- ❌ Skipping `top-list_story_bible.json` or forgetting to update it after publishing. Repeating the same "Top 5 men/villains/locations" kills the format faster than a weak individual entry.
