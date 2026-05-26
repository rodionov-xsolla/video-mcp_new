# Format "Fun News" — Fictional ironic news from a game's lore

> **Single video model — Kling Avatar v2 Standard.** Opener and CTA — pre-built from Supabase. Anchor — locked per game in story bible. Reporters — variable, pulled from Supabase by topic. Tone — ironic/satirical/absurd mix.

This file is the **playbook**: when to use, pipeline, role briefs. Craft rules — in `rules/roles/*.md`.

**Distinct from:**
- `news.md` — real game news (web search for actual patch notes / events). Fun News is **fictional** — invented headlines extrapolated from canon lore.
- `what-if-lore.md` — alternate-history one-shots about a single character/event. Fun News is a recurring newsroom format with multiple short items per episode.

---

## When to use

Keywords: "fun news", "fictional news", "fake news", "lore news", "ироничные новости", "выдуманные новости", "фейковые новости", "satire news", "lore satire".

---

## Concept

- **1 permanent anchor** (locked per game in story bible) + **1–2 changing reporters** per episode (chosen by topic from Supabase `game_assets`)
- **2–3 fictional news items** per episode, extrapolated from canon lore (no real patch notes)
- **Only Kling Avatar v2 Standard** + ElevenLabs TTS (lipsync via `audio_url`)
- **Opener and CTA — pre-built mp4 from Supabase**, not regenerated
- **Tone:** ironic / satirical / absurd / dry-deadpan — mix per item
- **Duration:** 20–40s after speedup (excluding opener/CTA)
- **Budget:** up to $4 (~$1.30–$1.80 typical)
- **Frame format:** 9:16 (1080×1920)

### Models

- **Image:** NB2 (only for new reporter refs not yet in Supabase)
- **Video:** Kling Avatar v2 Standard
- **Audio:** ElevenLabs TTS (per dialogue scene)

---

## Pipeline (strict order)

### Phase 0: Initialization

1. Read game config: `games/{GAME_TAG}/{GAME_TAG}.md`
2. Read / create `games/{GAME_TAG}/fun-news_story_bible.json` (see Story Bible section)
3. **Query Supabase `game_assets`** (filter `game_tag = "{GAME_TAG}"`):

```bash
curl -s -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  "${SUPABASE_URL}/rest/v1/game_assets?game_tag=eq.{GAME_TAG}&select=*"
```

Find from the result:
   - **Opener** — record with tag `opener` and `video` → `.mp4`
   - **CTA** — record with tag `cta` → `.mp4`
   - **Anchor avatar** — record matching `anchor.name` from the story bible, tag `fun-news` or `news` and `avatar` in `character_name` → `.png`
   - **Reporter avatars** — records with tag `fun-news` or `character` matching reporter names selected in Phase 1
4. **STOP** if opener / CTA / anchor avatar not found — notify the user (must be uploaded in advance).
5. **STOP** if a topic-matched reporter ref is missing — do **not** auto-generate on the fly. Phase 2 handles new reporter generation explicitly.

### Phase 1: Lore research

Web search **BEFORE** writing the script. Goal: collect 5–8 canon facts to satirize.

**Step 1.** Three queries:
1. `"{game_name}" lore wiki characters`
2. `"{game_name}" world canon factions OR locations OR items`
3. `"{game_name}" official backstory OR origin`

Priority: official wiki → game's own narrative material → fan-curated lore wikis.

**Step 2.** Pick 2–3 facts → derive fictional headlines. Each headline is a **mock news item** that twists, exaggerates, or absurdly recontextualizes a canon fact.

**Step 3.** Check `episode_summaries` and `topic_rotation` in the story bible — **do not repeat a satirized fact or theme used in the last 5 episodes**.

**Step 4.** Save `research.json`:

```json
{
  "game_tag": "{TAG}",
  "research_date": "{YYYY-MM-DD}",
  "canon_facts": [
    {"fact": "...", "source_url": "https://..."}
  ],
  "news_items": [
    {
      "index": 1,
      "headline": "...",
      "satire_angle": "ironic|satirical|absurd|dry-deadpan",
      "canon_fact_index": 0,
      "summary": "25–35-word fictional report"
    }
  ],
  "topic_tags": ["faction-X", "character-Y", "location-Z"]
}
```

### Phase 2: Characters

**Anchor** — read `anchor.character_name` from story bible. Avatar ref already downloaded in Phase 0.

**Reporters** — choose **1–2** based on `topic_tags`:
- Prefer canon characters that are thematically tied to the news topic (a pirate-themed item → pirate reporter; a mage event → mage reporter).
- Look up matching avatars in Supabase by `character_name` and tag `fun-news` / `character`.

**If a topic-matched reporter has no Supabase avatar:**
1. **Character sheet** (NB2 text-to-image, 16:9 concept art)
2. **Avatar ref** (NB2 edit with sheet as ref, 9:16, frontal portrait at the desk, teeth visible for lipsync)
3. Upload both to Supabase via `queue/upload-asset.sh` with tags `fun-news,avatar`
4. In future episodes this reporter is already in Supabase

### Phase 3: Script → `storyboard.json`

Structure — **exactly 4 dialogue scenes** (opener/CTA are pre-built, not in storyboard):

| Scene | Role | Camera | Content |
|---|---|---|---|
| 1 | **Anchor intro** | Frontal, medium close-up | Greeting + tease of items + handover by name to Reporter 1 |
| 2 | **Reporter 1** | Three-quarter, medium close-up | Fictional news #1 (25–35 words) + ironic kicker |
| 3 | **Reporter 2** *(or Anchor if only 1 reporter)* | Different angle from scene 2 | Fictional news #2 (25–35 words) + reaction |
| 4 | **Anchor outro** | Slightly wider than scene 1 | Wrap + signature ironic sign-off + CTA tease |

With 2 reporters: scenes 1, 2, 3, 4 = anchor → R1 → R2 → anchor.
With 1 reporter: scenes 1, 2, 3, 4 = anchor → R1 → anchor → anchor (anchor delivers news #2 directly).

**Handoff — by name, mandatory.**
- Anchor → Reporter: `"Over to [reporter name] on the scene"` / `"[Name], what are you seeing?"`
- Reporter → Anchor: `"Back to you, [anchor name]"` / `"That's all from [location], [anchor name]"`
- Reporter → Reporter: `"[Other reporter name] has more — over to you"`

**Tone per scene** — pick from `satire_angle` of the corresponding news item (`ironic` / `satirical` / `absurd` / `dry-deadpan`). Adjacent scenes should not repeat the same angle.

**Script length:**
- Anchor intro: 20–30 words
- Reporter scenes: 25–35 words
- Anchor outro: 15–20 words

Every dialogue scene has a `tts` field with the text for ElevenLabs.

### Phase 4: Animation (Kling Avatar v2 only)

For each dialogue scene:
1. **ElevenLabs TTS** → `.mp3` → upload to Supabase (Sound role)
2. **Kling Avatar v2** with parameters:
   - `image_url` = avatar ref from Supabase (9:16, not square)
   - `audio_url` = TTS mp3 **from Supabase** (not fal.ai temp URL)
   - `motion_prompt` = `broadcaster energy, hand gestures, head turns, subtle smirk on ironic line`
   - `negative_prompt` mandatory (anti-text set — avatar ref may have studio overlays / text)
3. **1.3x speedup** after generation (energetic ironic delivery):

```bash
$FFMPEG -y -i avatar.mp4 \
  -filter_complex "[0:v]setpts=PTS/1.3[v];[0:a]atempo=1.3[a]" \
  -map "[v]" -map "[a]" \
  -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  avatar-fast.mp4
```

### Phase 5: Assembly (FFmpeg)

Canonical single-pass pipeline (see `rules/roles/editor.md` §0):

1. **Subtitles ASS** — per-scene via `tools/add_subtitles.py --emit-ass-only` with word-highlight on the satirical kicker phrases (`--emphasis "..."`).
2. **Normalize** all clips: 1080×1920, 30fps, AAC 128k.
3. **Opener** — normalize the `.mp4` downloaded from Supabase (same scale/fps/codec).
4. **Concat** in one filter_complex: opener → scene-1-sub → scene-2-sub → scene-3-sub → scene-4-sub → CTA.
5. **Music:** comedic / lo-fi beat, `volume=0.15`.
6. **Fade-to-black** last 1.0s before CTA join.
7. → `final.mp4` → upload to Supabase.

---

## Voices

| Role | Voice (ElevenLabs) | stability | Notes |
|---|---|---|---|
| Anchor (locked) | from `voice_mapping.anchor` in story bible | 0.25 | one voice across all episodes |
| Reporter (per character) | from `voice_mapping.reporters[character_name]` | 0.30 | locked once a reporter character is first used |

`stability: 0.25` = energetic broadcaster tone. Use `voice` (name string), not `voice_id` hash.

---

## Story Bible

Create on first run: `games/{GAME_TAG}/fun-news_story_bible.json`

```json
{
  "series_id": "fun-news-{GAME_TAG}",
  "game_tag": "{GAME_TAG}",
  "title": "{Game} Lore Newsflash",
  "created_at": "{TODAY}",
  "last_episode": 0,
  "anchor": {
    "character_name": "",
    "voice": "",
    "tone_signature": "deadpan anchor with a smirk"
  },
  "voice_mapping": {
    "anchor": "",
    "reporters": {}
  },
  "style_tone": "ironic|satirical|absurd|dry-deadpan",
  "topic_rotation": {
    "recent_topic_tags": [],
    "recent_canon_facts": [],
    "cooldown_episodes": 5
  },
  "episode_summaries": [
    {
      "episode": 0,
      "date": "",
      "anchor": "",
      "reporters": [],
      "news_items": [],
      "topic_tags": []
    }
  ]
}
```

**FIFO 5** on `episode_summaries` — keep last 5, drop older.
**Anti-repetition:** before Phase 1, manager checks `recent_topic_tags` and `recent_canon_facts`; the scenarist's research.json must not collide.
**No loop management** (this is not serial — each episode is standalone).

---

## Anti-repetition check

Before Phase 3, manager validates:

- [ ] None of `news_items[].canon_fact_index` resolves to a fact in `recent_canon_facts`.
- [ ] None of `topic_tags` overlap with `recent_topic_tags` (last 5 episodes).
- [ ] `satire_angle` distribution differs from the previous episode (don't run two `absurd`-only episodes back-to-back).

If a collision is found — scenarist regenerates research.json with cooldown applied.

---

## Storyboard JSON (template)

```json
{
  "format": "fun-news",
  "show_name": "{Game} Lore Newsflash",
  "episode": 1,
  "research": {"file": "research.json"},
  "visual_identity": {
    "characters": {
      "anchor": {"name": "...", "character_description": "..."},
      "reporter_1": {"name": "...", "character_description": "..."},
      "reporter_2": {"name": "...", "character_description": "..."}
    },
    "environments": {
      "studio": "lore-themed news desk, game-specific signage"
    }
  },
  "voices": {
    "anchor":    {"voice": "George",    "stability": 0.25, "language_code": "en"},
    "reporter_1":{"voice": "Daniel",    "stability": 0.30, "language_code": "en"},
    "reporter_2":{"voice": "Charlotte", "stability": 0.30, "language_code": "en"}
  },
  "scenes": [
    {"index": 1, "role": "anchor",     "clip_type": "dialogue", "satire_angle": "dry-deadpan", "tts": "..."},
    {"index": 2, "role": "reporter_1", "clip_type": "dialogue", "satire_angle": "absurd",      "news_item_index": 1, "tts": "..."},
    {"index": 3, "role": "reporter_2", "clip_type": "dialogue", "satire_angle": "ironic",      "news_item_index": 2, "tts": "..."},
    {"index": 4, "role": "anchor",     "clip_type": "dialogue", "satire_angle": "satirical",   "tts": "..."}
  ]
}
```

---

## Budget

| Item | 5s clip | Cost |
|---|---|---|
| Opener (from Supabase) | — | $0 |
| CTA (from Supabase) | — | $0 |
| Anchor avatar ref (from Supabase) | — | $0 |
| Reporter avatar ref (already in Supabase) | — | $0 |
| New reporter (sheet + ref, only if absent) | — | ~$0.16 |
| ElevenLabs TTS (4 lines, ~20–30s) | — | ~$0.25–0.35 |
| Kling Avatar v2 (4 × 5s = 20s raw @ $0.056/s) | $0.28 | ~$1.12 |

| Variant | Clips | Reporter refs in Supabase | Typical cost |
|---|---|---|---|
| Base | 4 × 5s | yes | **~$1.40–$1.50** |
| Worst case (1 new reporter) | 4 × 5s | partial | **~$1.65** |

**Limit: $4.00.** Stop if spend > **$3.60**.

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/fun-news/
├── research.json
├── storyboard.json
├── scenes/
│   ├── scene-1/
│   │   ├── scene-1.mp3           # TTS
│   │   ├── scene-1.mp4           # Kling Avatar raw
│   │   ├── scene-1-fast.mp4      # 1.3x speedup
│   │   └── scene-1-sub.ass       # ASS subtitles
│   ├── scene-2/...
│   ├── scene-3/...
│   └── scene-4/...
└── final.mp4
```

---

## Role briefs

### Scenarist
- 4 dialogue scenes (opener/CTA are pre-built — not in storyboard)
- Fictional headlines derived from canon lore (no real patch notes)
- Anchor intro 20–30 words, reporter scenes 25–35 words, anchor outro 15–20 words
- Mandatory by-name handoffs between anchor ↔ reporter
- `satire_angle` per scene; adjacent scenes must differ
- Anti-repetition vs story bible `topic_rotation`
- General rules — `rules/roles/scenarist.md`

### Storyboarder
- Anchor and existing reporters — taken from Supabase, do **not** regenerate
- Only generate NB2 character sheet + avatar ref for **brand-new** reporters; upload to Supabase with tags `fun-news,avatar`
- 9:16 (608×1080) avatar refs, frontal, teeth visible for lipsync
- General rules — `rules/roles/storyboarder.md`

### Animator
- **ONLY Kling Avatar v2 Standard**
- `audio_url` and `image_url` — Supabase permanent URLs (no fal.ai temp)
- `negative_prompt` mandatory
- 1.3x speedup after generation
- General rules — `rules/roles/animator.md`

### Sound
- ElevenLabs TTS for each dialogue scene
- ASS subtitles per-scene via `tools/add_subtitles.py --emit-ass-only --emphasis "<kicker phrases>"` (word-highlight on punchlines)
- Music: comedic / lo-fi, `volume=0.15`
- General rules — `rules/roles/sound.md`

### Editor
- Download opener + CTA from Supabase, normalize
- Canonical single-pass pipeline: per-scene ASS burn-in inside one filter_complex → concat (opener → scenes → CTA) → music → fade
- General rules — `rules/roles/editor.md`

---

## Validation

- [ ] `research.json` with 2–3 fictional items, each tied to a real canon fact
- [ ] Anchor matches `anchor.character_name` from story bible (locked)
- [ ] Reporters chosen by topic, refs present in Supabase OR explicitly generated in Phase 2
- [ ] Opener and CTA downloaded from Supabase (not generated)
- [ ] All dialogue scenes — Kling Avatar v2, nothing else
- [ ] `negative_prompt` on all Avatar generations
- [ ] 1.3x speedup on all Avatar clips
- [ ] ASS subtitles per-scene with word-highlight on kicker phrases
- [ ] `satire_angle` differs between adjacent scenes
- [ ] No collision with `recent_topic_tags` / `recent_canon_facts` (last 5 episodes)
- [ ] By-name handoffs in every scene transition
- [ ] Final: 1080×1920, 30fps, 20–40s (excluding opener/CTA), budget < $4

---

## Anti-patterns

- ❌ Using real patch notes / live web search results as news items (that's `news.md`, not Fun News)
- ❌ Changing the anchor between episodes (anchor is locked per game)
- ❌ Generating opener / CTA — always pulled from Supabase
- ❌ Regenerating existing characters — anchor and known reporters are from Supabase
- ❌ Subtitles on a concatenated video — burn ASS per-scene inside the single-pass filter_complex
- ❌ 1.18x or 1.0x speedup — Fun News uses **1.3x** (ironic energetic delivery)
- ❌ fal.ai temp URLs for Kling — only Supabase permanent URLs
- ❌ `voice_id` hash — use `voice` name string
- ❌ Repeating a canon fact or topic_tag used in the last 5 episodes
- ❌ Same `satire_angle` on adjacent scenes
- ❌ `-shortest` in FFmpeg (use `apad`)
