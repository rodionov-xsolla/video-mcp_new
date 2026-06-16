---
subtitles: true
overlays: false
---

# Format "Reddit Story" — monologue over gameplay

A first-person monologue over random gameplay with word-highlight subtitles. Personal story: funny, touching, drama, shock, rage. Offerwall is woven into the plot as the hero's action.

This file is the **playbook**. Craft rules (TTS, subtitles, ffmpeg) — in `rules/roles/*.md`.

---

## When to use

Keywords: "reddit story", "storytime", "история игрока", "personal story", "narrated gameplay".

Run parameters: `game_tag`, `topic` (optional), `language` (`EN` / `RU` / `PT-BR`).

---

## Concept

- **Gameplay:** pre-made clips from `games/{GAME_TAG}/gameplay/`, random shuffle, **not tied to text** — pure background visual
- **Background:** static image from Supabase `game_assets` where `tags @> ['reddit-story-bg']` for this `game_tag`. Editor downloads it to `build/bg.png`. If not found — STOP and ask Manager to upload one.
- **TTS:** MiniMax via fal.ai (`fal-ai/minimax/speech-2.8-hd`), narrator voice `Determined_Man`, emotion `neutral`, speed 0.90
- **Subtitles:** word-highlight via Whisper ASS, mandatory
- **Duration:** up to 60s (~150–170 words)
- **No AI video generation** — only TTS + ffmpeg assembly
- **Budget:** $2 max (typical $0.30–0.50)

---

## Offerwall integration (native)

Offerwall = PART OF THE PLOT, not an ad. The hero uses it as a tool.

### Narrative structure (fixed)

```
HEADLINE → HOOK → PROBLEM → OFFERWALL (solution) → TWIST
```

### Rules
- **Don't start with the purchase.** First a gripping story, then offerwall as a natural solution.
- Offerwall is mentioned AS THE HERO'S ACTION: `"I grinded offerwall tasks"`, `"performed tasks"`.
- **Do NOT** say "buy", "download", do not name the service.
- CTA = **overlay** `"Subscribe for more"` in the last 2s. Never voiced.
- **TWIST mandatory** — an unexpected turn.

### Examples of native integration
- **Roblox:** sister dreamed of a skin → grinded tasks → gifted → she cried
- **Oxide:** raider destroyed the base → a week of doing tasks → gathered gear → revenge solo
- **MLBB:** kept losing → did a few tasks, took a new hero → won 10 games in a row

---

## Structure

| Element | Description | Dur. |
|---|---|---|
| **headline** | Clickbait summary in one sentence | 1–2s |
| **hook** | Story setup (concrete catchy fact) | 3–5s |
| **problem** | Conflict requiring a solution | 10–15s |
| **offerwall** | Hero's action as a step toward the goal | 5–10s |
| **twist** | Unexpected climax | 10–15s |
| **CTA** | Fade-to-black → `Subscribe for more` (like serial-drama) | 2s |

Total TTS duration ≤ 58s → final MP4 = TTS + 2s CTA ≈ 60s.

CTA is taken from Supabase `game_assets` (tag `cta` + `video`). Manager downloads in Phase 0, Editor normalizes and inserts as the last clip. If no CTA — fallback: fade-to-black → `SUBSCRIBE FOR MORE` drawtext (2s).

---

## Storyboard schema

```json
{
  "format": "reddit-story",
  "game_tag": "Roblox",
  "language": "EN",
  "headline": "I spent 200 hours building and a 9 year old destroyed it all",
  "narrative_text": "So my little brother has been playing Roblox every day... [full text]",
  "tone": "touching",
  "hook": "So my little brother has been playing Roblox every single day.",
  "offerwall_angle": "grinded offerwall tasks to buy premium building tools for brother",
  "tts": {"voice": "Daniel", "language_code": "en", "stability": 0.3, "style": 0.7},
  "total_duration_sec": 55,
  "cta_overlay": "Subscribe for more"
}
```

The `voice` field = **name**, not voice_id hash (see `rules/roles/sound.md`).

---

## Anti-Repetition Check

Before scripting, check `games/{GAME_TAG}/reddit-story_bible.json`:
- **Themes:** do not duplicate themes from the last 10 stories
- **Tone:** do not repeat the same tone 3 times in a row
- **Hooks:** do not use a similar headline/hook
- **Offerwall angle:** vary — not always "grinded tasks"

### Story bible structure
```json
{
  "game_tag": "Roblox",
  "total_stories": 0,
  "stories": [{"id": 1, "date": "...", "tone": "...", "theme": "...", "headline": "...", "offerwall_angle": "...", "output_dir": "..."}],
  "anti_repetition": {
    "recent_themes": ["..."],
    "recent_tones": ["..."],
    "recent_hooks": ["..."],
    "banned_combos": []
  }
}
```

Updated after each video (Manager, Phase 6). All lists FIFO, keep last 10.

---

## Role briefs

### Scenarist
- Headline — clickbait, provocative, 1 sentence; voiced + shown in subtitles
- `narrative_text` first-person, conversational style, sentences ≤15 words
- Structure HEADLINE→HOOK→PROBLEM→OFFERWALL→TWIST
- Specifics (names, numbers, details) — not "cool stuff" → "legendary dragon skin"
- No corporate tone, service names, voiced CTA
- Anti-repetition check via `reddit-story_bible.json`
- General rules — `rules/roles/scenarist.md`

### Storyboarder
- **SKIP** — no NB2 generation, ready-made gameplay is used
- Manager checks for ≥1 `.mp4` in `games/{GAME_TAG}/gameplay/` in Phase 0

### Animator
- **SKIP** — no Kling/Veo3, only random gameplay

### Sound
- **MiniMax via fal.ai** (`fal-ai/minimax/speech-2.8-hd`) — ElevenLabs is no longer used
- Narrator voice: `Determined_Man`, emotion `neutral`, speed `0.90`
- Input text = `headline + "\n\n" + narrative_text` as a single prompt → `tts-output.mp3`
- **Do not generate an SRT file** — Editor generates timings via Whisper in assembly
- Music optional, `volume=0.05` (quieter than usual — narration must be clear)
- General rules — `rules/roles/sound.md`

### Editor

**Layout (canonical — do not deviate):**
- **Background:** query Supabase `game_assets` where `game_tag = {GAME_TAG}` AND `tags @> ['reddit-story-bg']` → download to `build/bg.png` → scaled to 1080×1920. If not found — STOP, ask Manager to upload a background asset with tag `reddit-story-bg` for this game.
- **Gameplay panel:** 960×1280 (3:4), overlaid at x=60, y=320 → 60px side borders, 320px top/bottom borders of background visible
- **Subtitles:** generated via Whisper on `tts-output.mp3` → `build/subs.ass`, then burned in the single-pass encode (step 2). MarginV=520 puts them inside the gameplay panel — correct.

**Three-step assembly (steps 2+3+4 merged into one ffmpeg-full pass):**
```
1. Normalize gameplay  → scale each clip to 960×1280, crop-to-fill (NEVER pad — pad adds black bars)
                          ffmpeg: scale=960:1280:force_original_aspect_ratio=increase,crop=960:1280
                          Optional: -ss OFFSET to start gameplay from a specific timestamp.
                          Also run Whisper on tts-output.mp3 → build/subs.ass before step 2.
2. Single-pass encode  → /usr/local/bin/ffmpeg-full/ffmpeg:
                          [bg 1080×1920][gameplay 960×1280]overlay=x=60:y=320,ass='subs.ass',fps=30
                          + amix TTS(apad) + bg-music(vol=0.05), -t TTS_DUR → build/main-final.mp4
                          MUST use ffmpeg-full (libass). Combines composite + subtitle burn + audio in one pass.
3. Concat CTA          → ffmpeg-full concat main-final.mp4 + cta-norm.mp4 → final.mp4
```

**NEVER normalize gameplay to 1080×810** — that is landscape (4:3) applied to portrait (3:4) clips, produces massive black bars baked into gp_norm files.

**CTA:** query `game_assets` where `tags @> ['cta','video']` for this `game_tag`. Accept any `asset_type` (`promo_art` or `generated_ref`) — skip records tagged `legacy`.

- TTS overlay via `apad` (**NEVER `-shortest`**)
- General rules — `rules/roles/editor.md`

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/reddit-story/
├── storyboard.json
├── tts-output.mp3
├── gameplay-trimmed.mp4
├── assembled.mp4
├── subtitled.mp4
└── final.mp4
```

Plus an update to `games/{GAME_TAG}/reddit-story_bible.json`.

---

## Validation

- [ ] `games/{GAME_TAG}/gameplay/` contains ≥1 `.mp4`
- [ ] `headline` — clickbait, 1 sentence
- [ ] `narrative_text` 150–170 words; all sentences ≤15 words; first-person
- [ ] Offerwall woven as the hero's action; no direct ad / service name
- [ ] Twist present
- [ ] Anti-repetition: theme/tone/hook do not duplicate the last 10 (checked)
- [ ] `voice` = name (Daniel/George/...), not hash
- [ ] CTA — overlay only, not voiced
- [ ] Total duration ≤60s; budget ≤$2
- [ ] `reddit-story_bible.json` updated after the video

---

## Anti-patterns

- ❌ ElevenLabs or Kokoro — only MiniMax via `fal-ai/minimax/speech-2.8-hd`
- ❌ Hardcoding a game-specific background URL — always query Supabase by tag `reddit-story-bg`
- ❌ Normalizing gameplay to 1080×810 (landscape) — clips are portrait 3:4, panel is 960×1280
- ❌ Tying gameplay to text — must be random
- ❌ Starting with the purchase/offerwall — first a gripping story
- ❌ `-shortest` in ffmpeg — use `apad + -t`
- ❌ Repeating themes/hooks from the last 10 (bible)
- ❌ Sentences >15 words
- ❌ Corporate tone ("we recommend", "download")
- ❌ Voiced CTA / service name in the text
