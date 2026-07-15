---
ready_to_post: no
subtitles: true
overlays: false
---

# Format "Game News"

> TODO(style-refactor): style must come from the resolved chain (story bible top-level `style_tags` → game config `prompt_prefix`); character cards are style-free. This file not yet audited for hardcoded house-style.

> **Single video model — Kling Avatar v2 Standard.** No other video models. Opener and CTA — pre-built from Supabase. Characters — only from the current `news` series entries in `SUPABASE_ASSETS_FILE`.

This file is the **playbook**: when to use, pipeline, role briefs. Craft rules — in `rules/roles/*.md`.

---

## When to use

Keywords: "новости", "news", "game news", "weekly news", "patch recap", "обновление", "что нового".

---

## Concept

- **Anchor + Co-anchor** — two game characters at the news desk
- **2–3 news items** per episode (minimum 2, found via web search)
- **Only Kling Avatar v2 Standard** + routed speech audio (lipsync via `audio_url`)
- **Opener and CTA — pre-built videos from Supabase**, not regenerated
- **Duration:** 25–40s after speedup (excluding opener/CTA)
- **Budget:** up to $4 (~$2.50 typical)

---

## Pipeline (strict order)

### Phase 0: Initialization

1. Read game config: `games/{GAME_TAG}/{GAME_TAG}.md`
1a. Resolve the required current-format `STORY_BIBLE_PATH`. If it is missing, STOP and ask whether the user wants it created; create it only after explicit confirmation.
2. Read Manager's prefiltered `SUPABASE_ASSETS_FILE`. It contains only assets owned by this `news` format/series plus the separately resolved game CTA. Do not run a broad `game_tag` query.

Find from the result:
   - **Opener** — record with tag `opener` and `video` → download **`.mp4` video** (not the picture!)
   - **CTA** — record with tag `cta` → download `.mp4`
   - **Avatar refs** — records with tag `news` and the word `avatar` in `character_name` → download `.png`
3. If opener or CTA not found — **STOP**, notify the user
4. If avatar refs for anchor/co-anchor not found — **STOP**, notify the user (characters must be uploaded to Supabase in advance)

### Phase 1: News research

Web search **BEFORE** writing the script.

**Step 1.** Three queries:
1. `"{game_name}" patch notes {month} {year}`
2. `"{game_name}" update news {month} {year}`
3. `"{game_name}" new hero OR new character OR event {year}`

Priority: official patch notes → official socials → major game media → communities.

**Step 2.** Pick 2–3 news items:
- Recency (7–14 days)
- Significance (impacts the game)
- Diversity (not 3 nerfs in a row)

Fallback: if <2 real news items — community highlight (meme, meta shift, record).

**Step 3.** Save `research.json`:

```json
{
  "game_tag": "roblox",
  "research_date": "2026-04-30",
  "news_items": [
    {"index": 1, "headline": "...", "summary": "...", "source_url": "https://...", "type": "event"},
    {"index": 2, "headline": "...", "summary": "...", "source_url": "https://...", "type": "update"}
  ],
  "sources_consulted": ["url1", "url2", "url3"]
}
```

### Phase 2: Characters

**Anchor and co-anchor are taken only from the current-format entries in `SUPABASE_ASSETS_FILE`.** Use the URL from Phase 0.

**Topic reporter:** if a story needs a topical character (e.g. a pirate for a pirate event), generation of a new one is allowed:
1. **Character sheet** (NB2 text-to-image, 16:9) — concept art
2. **Avatar ref** (NB2 edit with sheet as ref, 9:16) — portrait at the desk, teeth visible for lipsync
3. Upload both to Supabase via `queue/upload-asset.sh` with tags `news,avatar`
4. In subsequent issues this character will already be in Supabase

### Phase 3: Script → `storyboard.json`

Structure — **exactly 3 dialogue scenes** (no title card — opener is taken pre-built):

| Scene | Role | Camera | Content |
|-------|------|--------|------------|
| 1 | **Anchor** | Frontal, medium close-up | Greeting + news #1 + handover to co-anchor |
| 2 | **Co-anchor** | Three-quarter, medium close-up | News #2 + reaction |
| 3 | **Anchor** | Slightly wider than scene 1 | Thanks + sign-off + CTA |

With 3 news items — 4 scenes (anchor delivers #1 and #3, co-anchor — #2).

**Scripts:**
- **Scene 1:** `"Welcome to [Show]! [News #1 in detail, 25-35 words]. [Co-anchor name], what do you have?"`
- **Scene 2:** `"Thanks [anchor]! [News #2 in detail, 25-35 words]. [Reaction/take]."`
- **Scene 3:** `"[Thanks]. That's [Show] for today. See you next time."` (10–15 words). The existing CTA asset follows; do not synthesize CTA language or an end card.

**Handoff — by name, mandatory.** Anchors call each other by name like in a real newscast:
- Anchor → Co-anchor: `"Sarah, what do you have?"` / `"Over to you, Sarah!"` / `"Sarah, tell us more"`
- Co-anchor → Anchor: `"Thanks Jake!"` / `"Back to you, Jake"` 
- Anchor → Reporter (if any): `"Let's check in with [name]"` / `"[Name], what's the latest?"`
- Reporter → Anchor: `"Thanks [anchor]!"` / `"Back to you, [anchor]"`

This creates the feeling of a live broadcast and links the scenes. Each handoff contains the **name** of the next/previous anchor.

Tone — from game config (Tone of Voice). Every dialogue scene must have a `tts` field with its spoken text.

### Phase 4: Animation (Kling Avatar v2 only)

For each dialogue scene:
1. **Resolve speech source:** native model audio when the selected scene model intentionally supports it; otherwise Chatterbox only with an approved voice sample owned by this `news` format; otherwise MiniMax. Never read a sample or voice assignment from another format. Generate `.mp3` and upload it to Supabase. On failure, retry once with the same source/settings, then STOP and report the error.
2. **Kling Avatar v2** with parameters:
   - `image_url` = avatar ref from Supabase (9:16, not square!)
   - `audio_url` = TTS mp3 from Supabase (not fal.ai temp URL!)
   - `motion_prompt` = broadcaster energy, hand gestures, head turns
   - `negative_prompt` mandatory (anti-text set — avatar ref has on-screen text)
3. **1.18x speedup** after generation:

```bash
$FFMPEG -y -i avatar.mp4 \
  -filter_complex "[0:v]setpts=PTS/1.18[v];[0:a]atempo=1.18[a]" \
  -map "[v]" -map "[a]" \
  -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  avatar-fast.mp4
```

1.18x for news — clear and intelligible, not rushed. Not 1.3x.

### Phase 5: Assembly (FFmpeg)

Strict order:

1. **Subtitles** — overlay per-scene on each `-fast.mp4` (NOT on concat! whisper skips voices on concat)
2. **Normalize** all clips: 1080×1920, 30fps, AAC 128k
3. **Opener** — normalize the `.mp4` downloaded from Supabase (same scale/fps/codec)
4. **Concat:** opener → scene-1-sub → scene-2-sub → scene-3-sub
5. **Music:** fun/energetic beat, `volume=0.10`
6. **Fade-to-black:** last 1.5s
7. **CTA:** concat with normalized CTA from Supabase
8. → `final.mp4`

---

## Voices

| Role | Speech route | Direction |
|------|--------------|-----------|
| Anchor | native → format-owned sample via Chatterbox → MiniMax | energetic broadcaster |
| Co-anchor | native → format-owned sample via Chatterbox → MiniMax | energetic broadcaster |

When MiniMax is selected, store its preset in `voice`; when Chatterbox is selected, store the current-format sample URL. Do not use ElevenLabs IDs.

---

## Storyboard JSON (template)

```json
{
  "format": "news",
  "show_name": "{Game} News Flash",
  "research": {"file": "research.json", "news_items": [...]},
  "visual_identity": {
    "characters": {
      "anchor": {"name": "...", "character_description": "..."},
      "co_anchor": {"name": "...", "character_description": "..."}
    },
    "environments": {
      "studio": "..."
    }
  },
  "voices": {
    "anchor": {"route": "minimax", "voice": "{MINIMAX_PRESET}", "language_code": "en"},
    "co_anchor": {"route": "minimax", "voice": "{MINIMAX_PRESET}", "language_code": "en"}
  },
  "scenes": [
    {"index": 1, "role": "anchor", "clip_type": "dialogue", "news_item_index": 1, "tts": "..."},
    {"index": 2, "role": "co_anchor", "clip_type": "dialogue", "news_item_index": 2, "tts": "..."},
    {"index": 3, "role": "anchor", "clip_type": "dialogue", "tts": "..."}
  ]
}
```

---

## Budget

| Item | Cost |
|--------|-----------|
| Opener (from Supabase) | $0 |
| CTA (from Supabase) | $0 |
| Avatar refs (from Supabase) | $0 |
| New topic reporter (sheet + ref, if needed) | ~$0.12 |
| Routed speech generation (~25-35s) | provider-dependent |
| Kling Avatar v2 (3 scenes, ~25-35s raw) | ~$1.40–2.00 |
| **Typical** | **~$1.60–2.20** |

**Limit: $4.00.** Stop if spend > $3.50.

---

## Output files

```
${OUTPUT_DIR}/
├── research.json
├── storyboard.json
├── scenes/
│   ├── scene-1/
│   │   ├── scene-1.mp3           # TTS
│   │   ├── scene-1.mp4           # Kling Avatar raw
│   │   ├── scene-1-fast.mp4      # 1.18x speedup
│   │   └── scene-1-sub.mp4       # with subtitles
│   ├── scene-2/...
│   └── scene-3/...
└── final.mp4
```

---

## Role briefs

### Scenarist
- 3 dialogue scenes (opener/CTA — pre-built, not in storyboard)
- 25–35 words for main scenes, 15–20 for outro
- Tone — from game config Tone of Voice
- Handoff: "Sarah, what do you have?" → "Thanks Jake!"
- camera_angle different for adjacent scenes
- General rules — `rules/roles/scenarist.md`

### Storyboarder
- Anchor/co-anchor are taken from Supabase — do not generate
- Topic reporter (if needed) — generate sheet + avatar ref, upload to Supabase
- General rules — `rules/roles/storyboarder.md`

### Animator
- **ONLY Kling Avatar v2 Standard**
- `audio_url` and `image_url` — Supabase permanent URLs
- `negative_prompt` mandatory
- 1.18x speedup after generation
- General rules — `rules/roles/animator.md`

### Sound
- Generate speech for each dialogue scene using native audio → current-format-owned Chatterbox sample → otherwise MiniMax. Retry the same route once, then stop; do not switch providers.
- Subtitles per-scene (not on concat)
- Music: energetic/fun, `volume=0.10`
- General rules — `rules/roles/sound.md`

### Editor
- Download opener + CTA from Supabase, normalize
- Subtitles per-scene → normalization → concat with opener → music → fade → CTA
- General rules — `rules/roles/editor.md`

---

## Validation

- [ ] `research.json` with 2–3 news items and sources
- [ ] Avatar refs for both characters from Supabase
- [ ] Opener and CTA downloaded from Supabase (not generated)
- [ ] All dialogue scenes — Kling Avatar v2, nothing else
- [ ] `negative_prompt` on all Avatar generations
- [ ] 1.18x speedup on all Avatar clips
- [ ] Subtitles per-scene (not on concat)
- [ ] camera_angle different for adjacent scenes
- [ ] Final: 1080×1920, 30fps, 25–40s (excluding opener/CTA), budget < $4

---

## FORBIDDEN

- Any video models other than Kling Avatar v2 Standard
- Generating opener/CTA — taken from Supabase
- Regenerating existing current-format characters — anchor/co-anchor come from the filtered `SUPABASE_ASSETS_FILE`
- Subtitles on a concatenated video — whisper skips voices on concat
- 1.3x speedup — too fast, only 1.18x
- fal.ai temp URLs for Kling — only Supabase permanent URLs
- ElevenLabs or a voice/sample copied from another format
- One avatar ref for both — each character = its own ref
