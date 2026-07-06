---
ready_to_post: yes
subtitles: true
overlays: true
---

# Format "Fake Ad" — Absurd fake commercial for in-game items with a mandatory twist ending

Fake TV commercial for a real or fictional in-game item. Follows classic commercial structure: problem → product → peak effect → **TWIST that makes the product useless** → packshot with product close-up and slogan. Tone: deadpan announcer, earnest to the point of absurdity. The twist is the punchline — the product works perfectly until the one moment that matters, then fails anyway.

This file is the **playbook**: when to use, concept, budget, role briefs. Craft rules — in `rules/roles/*.md`.

---

## When to use

Keywords: `"fake ad"`, `"fake commercial"`, `"рекламный ролик"`, `"фейковая реклама"`, `"реклама"`, `"commercial"`, `"advertisement"`, `"ad for"`, `"реклама предмета"`, `"obby energy"`, `"in-game ad"`, `"item ad"`, `"рекламный"`, `"ролик"`.

Typical themes: fictional energy drinks, useless power-ups, cosmetic items with absurd side-effects, overpromising potions or tools, in-game currency with fine print.

Not for: news / patch recaps (use `news`), character lore (use `character-story`), comedy sketches with dialogue (use `fun-news`).

---

## Concept

- **Genre:** Fake TV commercial — absurdist product advertisement
- **Style:** game-specific visual style (from `games/{GAME_TAG}/{GAME_TAG}.md`), but with commercial-ad staging (hero product angles, clean backgrounds, dynamic lighting)
- **Duration:** 15–20s total (5 clips × ~3–4s, rendered as 5s Kling clips with tight voiceover)
- **Budget:** up to **$3.50** per video. Stop if spend > **$3.00**.
- **Frame format:** 9:16 (1080×1920)

### Structure beat rules (HARD)

1. **TWIST is mandatory.** The product works exactly as advertised — until the one moment that matters. The twist must undercut the product's core promise at the worst possible time (final platform, final boss, final second). Without the twist, it's not this format.

2. **Packshot is mandatory.** The final scene is always a clean hero product shot (close-up) with the slogan. The slogan confirms the twist — it's the official tagline that acknowledges the product is useless ("Doesn't guarantee skill. Just confidence."). Editor overlays the slogan as text.

3. **Voiceover is a single announcer.** One continuous voice across scenes 0–3, then the tagline line on scene 4. No character dialogue, no lipsync. The VO is the commercial narrator — energetic, confident, completely earnest about the absurd product.

4. **Music is continuous and upbeat.** Unlike other formats (where music only plays at opener/CTA), fake-ad music runs through the ENTIRE video including the twist and packshot. Volume `0.25` (louder than default — commercial-style presence).

5. **Dialogue/sketch exception.** If the user brief requires a character-driven sketch, proposal, interview, confession, or other dialogue setup, the format may use character dialogue instead of a single announcer. This is still `fake-ad` only if it preserves the core commercial structure: a sincere setup, an unexpected ad turn/twist, and a final packshot or channel CTA. In this exception, keep dialogue short enough for 5s clips, use the user's live story beats over the default table below, and make the ad line feel like a deliberate commercial interruption.

### Models

- **Image:** Nano Banana 2 (5 scenes including packshot product hero shot)
- **Video:** Kling I2V v3 Standard (`generate_audio: false`) — all 5 scenes
- **Audio:** ElevenLabs TTS voiceover (one line per scene), music bed continuous

---

## Budget (rough estimates)

| Component | Per clip | 5 clips |
|---|---|---|
| NB2 image | $0.08 | **$0.40** |
| Kling I2V v3 Standard 5s (no audio) | $0.42 | **$2.10** |
| ElevenLabs TTS (5 short lines) | ~$0.05 | **~$0.25** |
| **Total** | | **~$2.75** |
| Fallback (Kling 2.6 Pro no audio) | $0.35 | ~$2.40 total |

---

## Video structure

| Scene | Beat | Duration | Visual | VO line |
|---|---|---|---|---|
| 0 | **Problem setup** | ~4s | Character in dire situation before the obstacle/challenge. Exhausted, hopeless, staring at the impossible. Wide establishing shot. | "300 platforms to the finish. Patience ran out at the third." |
| 1 | **Product appears** | ~4s | Character picks up / is handed / notices the product. Close-up of product in hand. | "Meet [Product Name]." |
| 2 | **Peak effect** | ~4s | Product in action — character is unstoppable, expert, confident. Dynamic camera. | "One sip. And suddenly you're flying." |
| 3 | **THE TWIST** | ~4s | The one moment where it all goes wrong anyway. Character fails at the very last step. Deadpan shot of the failure. | "And then… the last platform." (optional; VO may go silent to let the twist land) |
| 4 | **PACKSHOT** | ~4s | Product hero shot — product close-up, clean background, sparkles/glow. Slogan overlay by Editor. Small legal disclaimer overlay at bottom. | "[Product Name]. [Tagline / slogan from brief]." |

### VO tone

- Announcer energy: confident, building excitement in scenes 0–2
- Abrupt deadpan on scene 3 (the twist) — volume and energy match the confidence, which makes the drop funnier
- Scene 4 (packshot): official tagline delivery, still earnest despite what just happened
- Style direction for TTS: `"commercial announcer voice, energetic but deadpan, building confidence"`, stability 0.35

### The twist mechanics

The twist works on ONE rule: the product's core promise is fulfilled 100% — and then fails at the FINAL, LAST, MOST IMPORTANT moment before the goal. Examples:

- Energy drink gives perfect jump skills → misses the last platform anyway
- Speed potion makes character run at max speed → runs past the exit
- Armor upgrades defend against everything → server crashes on final boss
- Lucky charm guarantees rare drops → inventory is full when it drops

The VO for scene 3 may be short or even silent. The visual is the punchline. Don't explain the joke.

---

## Packshot — mandatory scene details

Scene 4 is always the packshot. Specific rules:

### NB2 image for packshot

- **Subject:** product only (the item/can/potion/object). NO character in frame.
- **Composition:** product centered, taking 50–70% of frame height, hero-product angle (slight 3/4 turn, dynamic tilt)
- **Background:** clean stylized gradient or branded color (game palette), sparkles/particles/energy glow — commercial-product staging
- **NO text baked into NB2** — text is applied by Editor as overlay
- `negative_prompt`: `"character, player, hands, text, labels, UI elements, watermark"`

### Kling I2V for packshot

- Gentle product rotation (15–20° arc over 5s)
- Sparkles drift across the lens continuously
- Slow push-in (camera moves toward product)
- `generate_audio: false`
- `negative_prompt`: `"on-screen text, captions, character, hands, walking, warped logo"`

## Overlays

Graphic overlays (NOT subtitles) — rendered by `tools/overlays.py` from `overlays[]` of scene 4
(packshot), before concat. **LAYOUT here; font/color/stroke from `games/{tag}/{tag}.md` →
`## Overlay brand`.** Never bake into NB2. Schema: `rules/roles/scenarist.md`.

**Slogan is MANDATORY on every fake-ad packshot.** A packshot without a slogan is just a product shot — never ship without it.

| # | type | position | size | enable | font role | text source |
|---|------|----------|------|--------|-----------|-------------|
| 1 | `slogan` | `(w-text_w)/2,1300` | 110 | whole clip, fade_in 0.3 | display | `\n` two-line slogan |
| 2 | `disclaimer` | `(w-text_w)/2,1800` | 28 | whole clip | label (opacity 0.6) | legal-humor line |

Example (brand fields from game config):
```json
"overlays": [
  {"type":"slogan","text":"DOESN'T GUARANTEE SKILL.\nJUST CONFIDENCE.","position":"(w-text_w)/2,1300","font":"BEBAS","size":110,"color":"white","stroke":{"color":"black","width":6},"fade_in":0.3},
  {"type":"disclaimer","text":"May cause overconfidence. Not responsible for lava deaths.","position":"(w-text_w)/2,1800","font":"MED","size":28,"color":"white","opacity":0.6}
]
```

### Slogan structure (HARD rule)

The `slogan` field **must always follow this two-line structure:**

```
PRODUCT NAME.
TAGLINE THAT CONFIRMS THE TWIST.
```

Example: `"RESIN ENERGY.\nDOESN'T RESTORE RESIN. HELPS YOU OUTLIVE THE WAIT."`

- **Line 1:** Product name in caps — anchors the brand
- **Line 2:** The tagline — the official acknowledgement that the product is absurd/useless
- Use `\n` as the line break — `overlays.py` stacks the slogan lines
- Scenarist puts `slogan` and `disclaimer` into scene 4 `overlays[]` (types `slogan`/`disclaimer`). If missing — Scenarist re-run.

---

## Storyboard JSON (template)

```json
{
  "format": "fake-ad",
  "product_name": "Obby Energy",
  "game_tag": "roblox",
  "language": "en",
  "visual_identity": {
    "style_tags": "from game config — applied verbatim to all image_prompts",
    "palette": "from game config",
    "lighting": "from game config"
  },
  "voices": {
    "announcer": {
      "voice": "George",
      "stability": 0.35,
      "style": "commercial announcer voice, energetic but deadpan, building confidence"
    }
  },
  "music": {
    "mood": "upbeat commercial jingle, life-affirming, energetic",
    "volume": 0.25
  },
  "scenes": [
    {
      "index": 0,
      "beat": "setup",
      "duration_sec": 5,
      "tts": "300 platforms to the finish. Patience ran out at the third.",
      "image_prompt": "...",
      "motion_prompt": "..."
    },
    {
      "index": 1,
      "beat": "product",
      "duration_sec": 5,
      "tts": "Meet Obby Energy.",
      "image_prompt": "...",
      "motion_prompt": "..."
    },
    {
      "index": 2,
      "beat": "peak_effect",
      "duration_sec": 5,
      "tts": "One sip. And suddenly you're flying.",
      "image_prompt": "...",
      "motion_prompt": "..."
    },
    {
      "index": 3,
      "beat": "twist",
      "duration_sec": 5,
      "tts": "And then… the last platform.",
      "image_prompt": "...",
      "motion_prompt": "..."
    },
    {
      "index": 4,
      "beat": "packshot",
      "duration_sec": 5,
      "tts": "Obby Energy. Doesn't guarantee skill. Just confidence.",
      "overlays": [
        {"type":"slogan","text":"DOESN'T GUARANTEE SKILL.\nJUST CONFIDENCE.","position":"(w-text_w)/2,1300","font":"BEBAS","size":110,"color":"white","stroke":{"color":"black","width":6},"fade_in":0.3},
        {"type":"disclaimer","text":"May cause overconfidence. Not responsible for lava deaths.","position":"(w-text_w)/2,1800","font":"MED","size":28,"color":"white","opacity":0.6}
      ],
      "image_prompt": "...",
      "motion_prompt": "..."
    }
  ]
}
```

---

## Prompting rules (NB2 + Kling)

### Scene 0 (setup) — the problem

- Wide shot: character in full body, obstacle/challenge fills 50%+ of frame
- Character body language: exhausted, defeated, staring at the impossible
- Environment is dangerous/daunting — acid, lava, impossible gaps, height
- Game-authentic environment, apply `visual_identity.style_tags` verbatim

### Scenes 1–2 (product + peak effect)

- Scene 1: character holding product prominently, close-to-medium shot, product label visible
- Scene 2: ACTION — character in motion, dynamic composition (low angle, motion blur, energy trails)
- Scene 2 motion_prompt: at least 2 concurrent motion layers (character action + environment reaction), camera follows the action

### Scene 3 (twist)

- The failure shot — character falling/failing, the exact moment of defeat
- Keep the same visual language as scene 2 (continuity makes the drop funnier)
- Camera: slightly wide to show the context of the failure (we need to see what they failed at)
- Do NOT cut away before the impact/failure is fully visible

### Scene 4 (packshot)

- See Packshot rules above (NO character, product hero shot, clean bg)

---

## Music

- **Mood:** upbeat, life-affirming, energetic commercial jingle — starts cheerful, STAYS cheerful even through the twist (the tonal mismatch is part of the joke)
- **Volume:** `0.25` (louder than default — commercial-style presence)
- **Duration:** continuous through all 5 scenes, including packshot
- **No fade during twist** — music does NOT dip on scene 3. The upbeat music playing over the failure amplifies the absurdity.
- Select from `music/tracks.json` mood `"upbeat-commercial"` or `"energetic-pop"`. If neither exists, use `"fun-news"` mood track.

---

## Role briefs

### Scenarist

- **5 scenes exactly:** setup → product → peak_effect → twist → packshot
- The TWIST (scene 3) must directly contradict the product's core promise at the WORST possible moment. The twist is the punchline — the more specific and concrete, the funnier.
- VO lines are SHORT (6–12 words each). Punchy, commercial rhythm. No complex sentences.
- Scene 4 fields: `tts` (tagline VO), `slogan` (text overlay, may differ from tts — often shorter/punchier), `disclaimer` (legal humor, 1 line, small text at bottom).
- `slogan` should be the official tagline from the brief (e.g. `"DOESN'T GUARANTEE SKILL.\nJUST CONFIDENCE."`). Uppercase. May be 2 lines (use `\n`).
- `disclaimer` is optional but strongly recommended — it's a reliable laugh beat.
- Character in scenes 0–3: confirm which character to use from game config (e.g. Roblox → Noob by default unless brief specifies otherwise).
- General script rules — `rules/roles/scenarist.md`

### Storyboarder

- 5 NB2 images (one per scene) **+ 1 standalone product logo image** (see below).
- Scenes 0–3: character + environment. Scene 4 (packshot): product ONLY, no character.
- Apply `visual_identity.style_tags` verbatim to EVERY image_prompt.
- Scene 4 NB2: hero-product angle, centered, sparkles/glow. `negative_prompt` must include `"character, player, hands, text, labels"`.
- Do NOT bake any text into NB2 (no slogan, no product name on the can, no UI). Editor handles all text.
- General rules — `rules/roles/storyboarder.md`

#### Product logo — mandatory separate asset

Generate a **standalone logo PNG** for the advertised product at the same time as scene images (Phase 3). Do NOT skip this step.

- **Prompt:** product name in stylized letters on a dark/branded background, small brand icon below the text. NO character, NO props (no PADD, no hands), NO scene environment. Clean graphic treatment — centered, readable at small size.
- **negative_prompt:** `"character, person, face, hands, props, device, PADD, background scene, complex environment"`
- **Save to:** `scenes/refs/product-logo.png`
- **Upload to Supabase:** `episodes/{GAME_TAG}/{RUN_ID}/refs/product-logo.png`
- **Write back to storyboard.json:** `"product_logo_url": "<supabase_url>"`

**Why:** the product name/logo appears in BOTH scene 1 (on a prop/surface) and the packshot overlay. Cropping it from a scene image loses quality and always captures unwanted elements (PADD border, hands, background). A dedicated logo PNG can be reused cleanly as a video overlay by the Editor without quality loss.

### Animator

- Kling I2V v3 Standard, `generate_audio: false`, `duration: 5` — all 5 scenes.
- Three concurrent motion layers per clip (camera move + environment + character/product action).
- Scene 2 (peak_effect): highest energy motion — character in flight, dynamic camera, maximum sense of speed/power.
- Scene 3 (twist): motion captures the fall/failure fully — do not let Kling hold on a mid-air pose; the whole fall arc should read.
- Scene 4 (packshot): gentle rotation + slow push-in + sparkles. Very different from scenes 2–3.
- Universal `negative_prompt`: `"on-screen text, captions, watermark, game UI, blurry face, talking, mouth open, lip sync"`.
- General rules — `rules/roles/animator.md`

### Sound

- ElevenLabs TTS for each scene with non-empty `tts` (all 5 scenes in this format).
- Voice from `voices.announcer` in storyboard — use `voice` name string, NOT `voice_id` hash.
- Upload each `.mp3` to Supabase → write `tts_url` back into scene in storyboard.json.
- **Subtitles: announcer VO only** — the one universal style (editor.md §6). Only each scene's main `tts` goes into `voice-final.wav` and gets subtitled; reactions (`character_reactions[*].tts`) are NOT subtitled (they are not in voice-final). The packshot slogan/disclaimer is a graphic overlay via `tools/overlays.py` (types `slogan`, `disclaimer`), NOT a subtitle.
- Music bed: upbeat commercial mood, `volume: 0.25`, continuous through ALL scenes including packshot. **NO music gate** (unlike fun-news/special-report, music does NOT go silent for dialogue — this is a commercial, VO rides on top of the music).
- General rules — `rules/roles/sound.md`

### Editor

- 5 clips, hard cuts, NO crossfade (commercial rhythm).
- **NO opener or CTA** pre-built clips — this format is standalone.
- **Packshot text overlays (MANDATORY for scene 4):**
  - Read `slogan` from `storyboard.json scenes[4].slogan` → drawtext overlay, centered, Bebas Neue / Montserrat Black ~100px, white + 6px black stroke, fade-in at 0.3s.
  - Read `disclaimer` from `storyboard.json scenes[4].disclaimer` → drawtext overlay, bottom @ y=1800, Arial 28px, white 60% opacity, appears at 1.0s.
  - If `disclaimer` is null or empty — skip it.
- **Music:** continuous `amix` across all 5 scenes. `volume=0.25`. **NO `-shortest`.**
- **Subtitles: `bold` style**, announcer VO only. Run `add_subtitles.py` for scenes 0–4 using `tts` field text. Do NOT subtitle `character_reactions` lines.
- Normalize: 1080×1920, 30fps, `-c:v libx264 -preset slow -crf 20`, AAC 128k stereo.
- Fade-to-black on scene 4 (packshot) last 1.0s.
- General rules — `rules/roles/editor.md`

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/fake-ad/
├── storyboard.json
├── scenes/
│   ├── refs/
│   │   ├── product-logo.png         (MANDATORY: standalone logo — reused in scene 1 prop + packshot overlay)
│   │   └── product-ref.png          (optional: reference for the product if complex design)
│   ├── scene-0/
│   │   ├── scene-0.png              (NB2: character in problem setup)
│   │   ├── scene-0.mp4              (Kling I2V raw)
│   │   └── scene-0.mp3              (TTS VO)
│   ├── scene-1/   (product appears)
│   ├── scene-2/   (peak effect)
│   ├── scene-3/   (twist)
│   └── scene-4/
│       ├── scene-4.png              (NB2: product hero shot, NO character)
│       ├── scene-4.mp4              (Kling I2V raw)
│       ├── scene-4-packshot.mp4     (with slogan + disclaimer overlays)
│       └── scene-4.mp3              (TTS tagline)
├── concat-list.txt
└── final.mp4
```

---

## Validation before publishing

- [ ] Exactly **5 scenes** with beats: `setup`, `product`, `peak_effect`, `twist`, `packshot`
- [ ] Scene 4 has `slogan` field (non-empty)
- [ ] Scene 4 NB2 contains NO character (product only) — filesize > 50KB
- [ ] All 5 Kling clips: `generate_audio: false`, duration ≈ 5.0s ±0.2s
- [ ] `final.mp4` duration 20–30s (5 × 5s + transitions)
- [ ] Slogan drawtext overlay applied to scene 4 (visible in final.mp4)
- [ ] Music runs continuously through ALL 5 clips including scene 4 (no gap, no gate)
- [ ] Subtitles (`bold`) burned on scenes 0–4 for announcer VO only — character reactions NOT captioned
- [ ] Twist (scene 3) shows the FAILURE completely — character actually falls/fails, not just starts to fall
- [ ] Budget ≤ $3.50

---

## Anti-patterns

- ❌ Forgetting the TWIST — the product MUST fail at the worst possible moment. A straight commercial is not this format.
- ❌ Character in the packshot (scene 4). Packshot = product only. Character presence kills the commercial ending.
- ❌ Baking slogan text into NB2 — Kling warps it. Editor handles all text overlays.
- ❌ Cropping the logo from a scene image (e.g. from the PADD in scene 1) — always captures borders/hands/background, degrades quality. Generate `product-logo.png` as a separate NB2 asset in Phase 3.
- ❌ `generate_audio: true` — wastes ~$0.21/clip. TTS+music bed handle all audio.
- ❌ Music gating (going silent during VO). Music is continuous in this format — the mismatch between upbeat music and the twist is intentional.
- ❌ Long VO lines (>15 words per scene). Commercial rhythm = punchy, 6–12 words.
- ❌ Explaining the twist in the VO. Let the visual speak. Scene 3 VO may be minimal ("And then…") or even empty.
- ❌ `-shortest` in FFmpeg. Always `apad`.
- ❌ `voice_id` hash in ElevenLabs. Use `voice` name string.
- ❌ Subtitle burn-in on any scene. No captions — this is a TV commercial. (Front-matter has `subtitles: true` for the announcer VO — if the channel wants captions; for none, set `subtitles: false`. By default the ad announcer is subtitled.)

---

## Story Bible

Create on first run: `games/{GAME_TAG}/fake-ad_story_bible.json`

```json
{
  "series_id": "fake-ad-{GAME_TAG}",
  "game_tag": "{GAME_TAG}",
  "title": "{Game} Fake Ad",
  "created_at": "{TODAY}",
  "last_episode": 0,
  "advertised_products": [],
  "anti_repetition": {
    "recent_lines": [],
    "recent_themes": [],
    "recent_tones": [],
    "recent_hooks": [],
    "recent_twist_types": [],
    "recent_problem_types": [],
    "recent_characters": [],
    "recent_environments": [],
    "banned_combos": []
  },
  "episode_summaries": [],
  "cta_url": ""
}
```

**`advertised_products`** — **PERMANENT, NEVER TRIM.** Every product ever advertised stays in this list forever. This is the primary anti-repetition guarantee of the fake-ad format: the same product is never re-advertised. Each entry:
```json
{
  "episode": 1,
  "product_name": "Resin Energy",
  "product_slug": "resin-energy",
  "tagline": "Doesn't restore resin. Helps you outlive the wait.",
  "game_mechanic_referenced": "original-resin",
  "date": "YYYY-MM-DD"
}
```

**`anti_repetition`** fields (all FIFO):

- `recent_lines` — FIFO 8 — exact spoken lines: product tagline + up to 2 key voiceover lines per episode. Example: `"Doesn't restore resin. Helps you outlive the wait."` Prevents repeating the same phrasing construction across episodes.
- `recent_themes` — FIFO 5 — broad episode theme slug: `resin-economy`, `obby-skill-check`, `stamina-grind`, `gacha-luck`
- `recent_tones` — FIFO 5 — announcer tone style: `zen-deadpan`, `earnest-absurd`, `desperation-sell`
- `recent_hooks` — FIFO 5 — **full narrative arc as plain text** (the most important field after `advertised_products`): comma-separated key beats of the episode — character + problem → product → peak → twist → finale. Example: `"Lumine exhausted at resin cap, Resin Energy drink appears, runs through domain, sits meditating — enlightenment achieved, walks away from game, Paimon holds sign"`
- `recent_twist_types` — FIFO 5 — semantic slug for how the product fails: `enlightenment-walk-away`, `run-past-exit`, `server-crash-at-victory`, `inventory-full-on-rare-drop`
- `recent_problem_types` — FIFO 5 — setup obstacle category: `resin-anxiety`, `obby-fail-loop`, `stamina-drain`, `farming-burnout`
- `recent_characters` — FIFO 10 — character starring in the ad (cooldown 10 episodes)
- `recent_environments` — FIFO 6 — scene 0–2 locations (cooldown 6 episodes)
- `banned_combos` — permanent dynamic blocklist — e.g. `{"character": "Lumine", "theme": "resin-economy"}` if a combo is exhausted

**`episode_summaries`** — FIFO 5:
```json
{
  "episode": 1,
  "date": "YYYY-MM-DD",
  "product_name": "Resin Energy",
  "product_slug": "resin-energy",
  "character": "Lumine",
  "theme": "resin-economy",
  "twist_type": "enlightenment-walk-away",
  "problem_type": "resin-anxiety",
  "environments": ["Mondstadt city plaza cobblestone", "Mondstadt hillside meadow"],
  "tone": "zen-deadpan",
  "hook": "Lumine exhausted at resin cap, Resin Energy drink appears, runs through domain, sits meditating — enlightenment achieved, walks away from game, Paimon holds sign",
  "final_url": "...",
  "duration_sec": 25.0,
  "cost_usd": 2.75
}
```

**Story Bible update (Manager, after editor confirms `final.mp4`):**

1. Add entry to `advertised_products` (product_name, slug, tagline, mechanic, date) — **DO NOT TRIM — this list is permanent.**
2. `theme` → append to `recent_themes`; FIFO 5.
3. `tone` → append to `recent_tones`; FIFO 5.
4. `hook` (narrative arc text) → append to `recent_hooks`; FIFO 5.
5. `twist_type` → append to `recent_twist_types`; FIFO 5.
6. `problem_type` → append to `recent_problem_types`; FIFO 5.
7. `character` → append to `recent_characters`; FIFO 10.
8. Scene 0–2 environments → append each to `recent_environments`; FIFO 6.
9. Tagline + up to 2 key voiceover lines → append each to `recent_lines`; FIFO 8.
10. Append `episode_summary`; FIFO 5.
11. Increment `last_episode`.

---

## Anti-repetition check

Before Phase 1 (scenarist), manager validates proposed product and creative choices:

- [ ] `product_slug` of the proposed product is **absent** from `advertised_products[].product_slug` — **permanent check, no FIFO window. This is the core rule of the fake-ad format.**
- [ ] `theme` does not match any of the last 5 in `recent_themes`.
- [ ] Proposed narrative arc (`hook`) does not echo the beats in any entry in `recent_hooks`.
- [ ] `twist_type` does not match any of the last 5 in `recent_twist_types`.
- [ ] `problem_type` does not match any of the last 5 in `recent_problem_types`.
- [ ] `character` is not in `recent_characters` (last 10 episodes).
- [ ] None of the proposed scene 0–2 environments appear in `recent_environments` (last 6 episodes).
- [ ] `tone` does not match either of the last 2 in `recent_tones`.
- [ ] Proposed `{character, theme}` combo is not in `banned_combos`.
- [ ] None of the proposed tagline or key voiceover lines appear in `recent_lines` (last 8).

If a collision is found — scenarist proposes a different product concept or creative angle before writing `storyboard.json`.
