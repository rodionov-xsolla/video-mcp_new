---
subtitle_style: bold
subtitle_offset_s: 0
subtitle_mask: false
subtitle_highlight: false
subtitle_extras: []
---

# Format "Special Report" — Single-reporter investigative special from a game's lore

> **Single video model — Kling Avatar v2 Standard.** Opener and CTA — pre-built from Supabase. Anchor — locked per game in story bible (DIFFERENT character from fun-news anchor for the same game). Reporter — single, locked per game, visits **3 locations** telling ONE unified ironic story. Tone — mock-journalistic / absurd-earnest. KEY VISUAL: reporter stands to the SIDE of frame, leaving room for the subject being investigated.

This file is the **playbook**: when to use, pipeline, role briefs. Craft rules — in `rules/roles/*.md`.

**Distinct from:**
- `fun-news.md` — newsroom with 2 separate news items, 2 reporters, reporter CENTERED in frame. Special Report: 1 reporter, 1 unified story, 3 locations, reporter OFF-CENTER (side composition).
- `streettalk.md` — vox-pop on the street, no studio. Special Report has a studio anchor + field reporter.
- `news.md` — real patch-note news. Special Report is FICTIONAL investigative, extrapolated from lore.

---

## When to use

Keywords: "special report", "спецрепортаж", "специальный репортаж", "расследование", "field investigation", "investigative report", "one reporter three locations", "on-location investigation", "genshin special report"

---

## Concept

- **1 permanent anchor** (locked per game in story bible, DIFFERENT from fun-news anchor) + **1 permanent reporter** (locked per game)
- Reporter visits **exactly 3 locations** to tell ONE unified ironic/absurd investigative story
- At each location: reporter stands to the **SIDE** of frame (~30% width), leaving 65-70% for the evidence/subject
- **Only Kling Avatar v2 Standard** + ElevenLabs TTS (lipsync via `audio_url`)
- **Opener and CTA — pre-built mp4 from Supabase**, not regenerated per episode
- **Tone:** mock-journalistic / ironic-investigative / absurd-earnest — reporter treats absurd topic with full journalistic seriousness
- **Duration:** 35–50s natural TTS speed (including opener + CTA)
- **Budget:** up to $4.50 hard cap (~$2.85 typical EP2+; pilot ~$3.35 with new assets)
- **Frame format:** 9:16 (1080×1920)

### Models

- **Image:** NB2 (3 per-episode on-location reporter edits + one-time anchor studio avatar)
- **Video:** Kling Avatar v2 Standard ($0.056/s of input audio duration)
- **Audio:** ElevenLabs TTS (per dialogue scene)

---

## Visual Identity & Branding (MANDATORY)

### Opener — game-specific, always required

Every special-report episode opens with a game-specific branded opener ("Genshin Special Report", "Roblox Special Report", etc.). Rules:
- Show name: `"{GameName} Special Report"` — distinct from `"{GameName} Funtasy News"` (fun-news). Separate branding, separate opener mp4.
- Visual style matches the game's aesthetic.
- If a fun-news opener exists for this game, the special-report opener must look visually different (different color scheme or layout) — two shows, two brands.

### Opener music = CTA music (same rules as fun-news)

Theme plays at opener (~2s) and reprises at CTA (~5s). Silence during all 5 dialogue scenes.

**Implementation (Editor):** pre-build `music-timed.wav` with `anullsrc` for the silence gap. Do NOT use `volume:enable` FFmpeg filter (passthrough bug).

### KEY VISUAL RULE: Reporter stands to the SIDE (MANDATORY)

**This is the defining visual signature of this format.** Unlike fun-news where reporters are centered:

- Reporter occupies the **LEFT or RIGHT 30-35%** of the 9:16 frame
- The **remaining 65-70%** of frame shows the subject — the object, creature, event, or place being reported on
- Reporter faces **slightly inward** toward the subject, holding a broadcast mic
- Creates a "reporter pointing at evidence" TV composition — like standing in front of a crime scene or burning building

**NB2 mandatory prompt anchor for all reporter scenes (scenes 2–4):**
```
[character name] standing to the [LEFT/RIGHT] of frame, body occupying ~30% of frame width,
facing slightly [RIGHT/LEFT] toward the subject area,
holding broadcast handheld mic with '[SHOW NAME]' printed on the mic flag,
mouth slightly open mid-speech for lipsync,
[SUBJECT: specific visual description of evidence] prominently filling the [other] 65% of frame,
game-authentic environment, semi-realistic photographic quality,
NOT cartoon, NOT centered portrait, 9:16 vertical broadcast field reporter composition,
professional key light on reporter's face, no text overlay, no captions
```

**Left vs. Right:** alternate across scenes 2→3→4 (e.g. left / right / left) unless story logic dictates a consistent direction.

### TV attributes

**Microphones:**
- Reporter always holds a **broadcast handheld mic with show's name on the flag** (e.g. `"Genshin Special Report"`)
- Anchor has a **desk mic** on the news desk
- NOT a blank flag, NOT a generic channel logo

**Studio:**
- Anchor's studio includes visible show branding: desk plaque or lower-third banner/sign
- NB2 anchor prompt: `"desk nameplate reading '[SHOW NAME]'"`

---

## Pipeline (strict order)

### Phase 0: Initialization

1. Read game config: `games/{GAME_TAG}/{GAME_TAG}.md`
2. Read / create `games/{GAME_TAG}/special-report_story_bible.json`
3. Query Supabase `game_assets` (filter `game_tag = "{GAME_TAG}"`):
   - **Opener** — tag `special-report,opener` → mp4
   - **CTA** — tag `cta` → mp4 (can reuse fun-news CTA)
   - **Anchor studio avatar** — tag `special-report,avatar`, character = anchor → png
   - **Reporter base avatar** — tag `special-report,avatar`, character = reporter → png

4. **STOP** if opener or CTA missing — notify user (one-time generation, ~$0.16 for opener NB2 + upload)
5. **STOP** if anchor or reporter avatar missing — generate (see Phase 2 avatar generation)

### Phase 1: Lore research

Web search BEFORE writing script. Goal: find **1 canon fact** to spin into a 3-beat investigative story.

**Step 1.** Two queries:
1. `"{game_name}" lore wiki characters`
2. `"{game_name}" world canon factions OR locations OR items`

**Step 2.** Pick 1 absurd/ironic fact → design ONE mock-investigative story with 3 "evidence" beats (one per location). The story is a unified narrative, not separate items.

**Step 3.** Check `episode_summaries` and `topic_rotation` — do not repeat a fact from the last 5 episodes.

**Step 4.** Design the 3 locations — must be visually distinct, escalate in absurdity:
- Location 1: first clue / sets up the investigation
- Location 2: confirmation / escalation
- Location 3: surprising conclusion

Save `research.json`:
```json
{
  "game_tag": "{TAG}",
  "research_date": "{YYYY-MM-DD}",
  "investigation_title": "...",
  "canon_fact": {"fact": "...", "source_url": "..."},
  "satire_angle": "ironic|mock-journalistic|absurd",
  "locations": [
    {
      "index": 1,
      "location": "Specific place + detailed visual description",
      "evidence": "What the reporter shows / points to here",
      "reporter_side": "left|right"
    },
    {"index": 2, "location": "...", "evidence": "...", "reporter_side": "left|right"},
    {"index": 3, "location": "...", "evidence": "...", "reporter_side": "left|right"}
  ],
  "topic_tags": ["faction-X", "character-Y", "location-Z"]
}
```

### Phase 2: Characters and on-location images

**Anchor** — locked per story bible. One-time NB2 studio avatar, reused every episode. Do NOT regenerate.

**Reporter** — locked per story bible. ONE reporter goes to all 3 locations.

**Per-episode: 3 on-location NB2 edits** ($0.08 × 3 = $0.24/episode) using reporter base avatar as `image_urls[0]`:

```
NB2 /edit:
  image_urls: [reporter_base_avatar_url]
  prompt: "[character] standing to the [reporter_side from research.json] of frame,
           occupying ~30% of frame width, facing slightly toward the center,
           holding broadcast handheld mic with '[SHOW NAME]' on the mic flag,
           mouth slightly open mid-speech for lipsync,
           [evidence from research.json: specific visual description] fills the other 65% of frame,
           [location description from research.json],
           semi-realistic photographic quality, game-authentic,
           NOT cartoon, NOT centered portrait,
           9:16 vertical broadcast field reporter composition,
           professional key light on face, no text overlay"
```

Upload each as `refs/{reporter}-special-report-loc{N}-{topic}.png`.

**If anchor or reporter base avatar missing from Supabase:**
1. NB2 text-to-image character sheet (16:9) — $0.08
2. NB2 edit → 9:16 frontal avatar with mouth slightly open — $0.08
3. Upload to Supabase with tags `special-report,avatar`

### Phase 3: Script → `storyboard.json`

**Exactly 5 dialogue scenes** (opener and CTA are pre-built, not scripted):

| Scene | Role | Composition | Content |
|---|---|---|---|
| 1 | **Anchor intro** | Frontal, medium close-up, studio | Hook: tease the investigation. Introduce reporter + send to field. ~15–20 words. |
| 2 | **Reporter — Location 1** | SIDE composition, reporter_side from research.json | First evidence. Sets up investigation. Brief tease of next location at end. ~20–28 words. |
| 3 | **Reporter — Location 2** | SIDE composition, opposite side from scene 2 | Second evidence. Escalates absurdity. `"And that's not all…"` or equivalent. ~20–28 words. |
| 4 | **Reporter — Location 3** | SIDE composition, location bg | Third evidence = surprising conclusion. Handoff: `"{Anchor name}?"` ~20–28 words. |
| 5 | **Anchor reaction** | Frontal, medium close-up, studio | Deadpan reaction to findings. Ironic sign-off. ~15–20 words. |

**Tone:**
- Anchor: dry authority, treats absurd topic as serious breaking news
- Reporter: earnest mock-journalism, urgency escalates scenes 2→4

**Handoff rules:**
- Anchor → Reporter: `"{Reporter name} is on location."` / `"{Reporter name}, what do you see?"`
- Reporter → Anchor: `"{Anchor name}?"` (single-word handoff is correct)

**Word budget:**

| Scene | Words | ~TTS dur | Cost (Avatar v2) |
|---|---|---|---|
| 1 Anchor intro | 15–20 | ~6–8s | ~$0.40 |
| 2 Reporter loc 1 | 20–28 | ~8–11s | ~$0.50 |
| 3 Reporter loc 2 | 20–28 | ~8–11s | ~$0.50 |
| 4 Reporter loc 3 | 20–28 | ~8–11s | ~$0.50 |
| 5 Anchor reaction | 15–20 | ~6–8s | ~$0.40 |
| **Total** | **~95–120** | **~36–49s** | **~$2.30** |

Same punctuation tax rules as fun-news (prefer commas/em-dashes over periods).

### Phase 4: Animation (Kling Avatar v2 only)

For each dialogue scene:
1. ElevenLabs TTS → mp3 → upload to Supabase
2. Kling Avatar v2: `image_url` = per-location NB2 edit (reporter scenes) or studio avatar (anchor scenes). `audio_url` = TTS mp3 from Supabase.
3. No speedup — natural TTS pace
4. `apad=whole_dur=<raw_video_dur>` per scene (Avatar v2 trailing silence buffer)

### Phase 5: Assembly (FFmpeg)

Same canonical single-pass pipeline as fun-news. 7 clips: opener + 5 scenes + CTA.

```
Inputs:
  [0..4]  scene-1..5.mp4  (Avatar v2 raw)
  [5]     opener.mp4      (pre-built, Supabase)
  [6]     cta.mp4         (pre-built, Supabase)
  [7]     music-timed.wav (pre-built by Sound)

VIDEO: opener → scene-1 → scene-2 → scene-3 → scene-4 → scene-5 (fade-out last 1s) → cta
AUDIO: per-scene apad → concat → adelay=2000 for opener offset → amix with music-timed.wav
```

Output: `final.mp4` → Supabase `videos/{GAME_TAG}/{YYYY-MM-DD}/special-report_final.mp4`.

---

## Budget

| Component | Cost |
|---|---|
| 3 reporter on-location NB2 edits | 3 × $0.08 = **$0.24** |
| 5 Avatar v2 scenes (~8s avg each) | 5 × $0.45 ≈ **$2.25** |
| ElevenLabs TTS (5 lines) | 5 × ~$0.07 ≈ **$0.35** |
| **Steady-state total** | **~$2.85** |
| Pilot extra (2 new avatars + opener NB2) | +~$0.50 |
| **Pilot total** | **~$3.35** |

**Cap: $4.50. Stop if spend > $4.00.**

---

## Voices

| Role | Voice source | stability | style |
|---|---|---|---|
| Anchor | `voice_mapping.anchor` in story bible | 0.55 | omit |
| Reporter | `voice_mapping.reporter` in story bible | 0.55 | omit |

Use `voice` (name string), NOT `voice_id` hash.

---

## Story Bible

Create on first run: `games/{GAME_TAG}/special-report_story_bible.json`

```json
{
  "series_id": "special-report-{GAME_TAG}",
  "game_tag": "{GAME_TAG}",
  "title": "{GameName} Special Report",
  "created_at": "{TODAY}",
  "last_episode": 0,
  "anchor": {
    "character_name": "",
    "display_name": "",
    "voice": "",
    "stability": 0.55,
    "style": null,
    "tone_signature": "...",
    "supabase_avatar_url": ""
  },
  "reporter": {
    "character_name": "",
    "display_name": "",
    "voice": "",
    "stability": 0.55,
    "style": null,
    "tone_signature": "...",
    "supabase_avatar_url": ""
  },
  "voice_mapping": {
    "anchor": "",
    "reporter": ""
  },
  "style_tone": "ironic|mock-journalistic|absurd",
  "topic_rotation": {
    "recent_topic_tags": [],
    "recent_canon_facts": [],
    "cooldown_episodes": 5
  },
  "episode_summaries": [],
  "opener_url": "",
  "cta_url": ""
}
```

**FIFO 5** on `episode_summaries`. Append after editor confirms `final.mp4`:
```json
{
  "episode": N,
  "date": "YYYY-MM-DD",
  "anchor": "...",
  "reporter": "...",
  "investigation_title": "...",
  "locations": ["...", "...", "..."],
  "topic_tags": ["..."],
  "final_url": "...",
  "duration_sec": 0
}
```

---

## Anti-repetition check

Before Phase 3, validate:
- [ ] Canon fact not in `recent_canon_facts` (last 5 episodes)
- [ ] None of `topic_tags` overlap with `recent_topic_tags`
- [ ] 3 locations distinct from all locations used in the previous episode

---

## Storyboard JSON (template, 5 scenes)

```json
{
  "format": "special-report",
  "show_name": "{GameName} Special Report",
  "episode": 1,
  "game_tag": "{TAG}",
  "language": "en",
  "visual_identity": {
    "characters": {
      "anchor":   {"name": "...", "character_description": "...", "image_url": "supabase://..."},
      "reporter": {"name": "...", "character_description": "...", "image_url": "supabase://..."}
    },
    "environments": {
      "studio":     "anchor's news desk studio with '[SHOW NAME]' nameplate",
      "location_1": "...",
      "location_2": "...",
      "location_3": "..."
    }
  },
  "scenes": [
    {
      "index": 1, "character": "anchor", "role": "studio",
      "tts": "...",
      "image_prompt": "...",
      "motion_prompt": "talking head, anchor at news desk, authoritative expression, slight lean forward",
      "kicker": "SPECIAL REPORT"
    },
    {
      "index": 2, "character": "reporter", "role": "location_1",
      "reporter_side": "left",
      "tts": "...",
      "image_prompt": "[character] standing to the LEFT of frame, ~30% frame width, subject fills RIGHT 65%...",
      "motion_prompt": "reporter talking, gesturing with free hand toward subject on the right",
      "kicker": "..."
    },
    {
      "index": 3, "character": "reporter", "role": "location_2",
      "reporter_side": "right",
      "tts": "...",
      "image_prompt": "[character] standing to the RIGHT of frame, ~30% frame width, subject fills LEFT 65%...",
      "motion_prompt": "reporter talking, gesturing with free hand toward subject on the left",
      "kicker": "..."
    },
    {
      "index": 4, "character": "reporter", "role": "location_3",
      "reporter_side": "left",
      "tts": "...",
      "image_prompt": "[character] standing to the LEFT of frame, ~30% frame width, subject fills RIGHT 65%...",
      "motion_prompt": "reporter talking, pointing at evidence behind them",
      "kicker": "..."
    },
    {
      "index": 5, "character": "anchor", "role": "studio",
      "tts": "...",
      "image_prompt": "...",
      "motion_prompt": "talking head, anchor at news desk, dry deadpan reaction, slight raise of eyebrow",
      "kicker": "..."
    }
  ]
}
```

---

## Output files

```
output/{YYYY-MM-DD}/{GAME_TAG}/special-report/
├── storyboard.json
├── research.json
├── final.mp4
├── scenes/
│   ├── scene-1.mp4
│   ├── scene-2.mp4
│   ├── scene-3.mp4
│   ├── scene-4.mp4
│   └── scene-5.mp4
└── build/
    ├── scene-1.ass ... scene-5.ass
    ├── music-timed.wav
    └── concat.txt
```

---

## Validation before publishing

- [ ] All 5 scene mp4s exist and each > 100KB
- [ ] `ffprobe` duration ≥ 5s per scene
- [ ] `final.mp4` duration 35–55s
- [ ] Anchor character ≠ fun-news anchor for the same game (confirmed via story bible comparison)
- [ ] Reporter same character across scenes 2–4 (same `image_url` base)
- [ ] `reporter_side` alternates across scenes 2–4 (or is intentionally consistent)
- [ ] 3 location `image_prompt`s are visually distinct environments

---

## Anti-patterns

- ❌ Reporter centered in frame (kills the format's core visual identity)
- ❌ Same anchor as fun-news for the same game (defeats the purpose of having two formats)
- ❌ 3 locations with visually identical backgrounds (different names alone aren't enough)
- ❌ Separate unrelated news items instead of ONE unified investigation
- ❌ `-shortest` in FFmpeg (ALWAYS use `apad`)
- ❌ `voice_id` hash instead of `voice` name in ElevenLabs
- ❌ `atempo` speedup on Avatar v2 output
- ❌ Reusing fun-news opener for special-report (separate brand, separate mp4)

---

## Role briefs

### Scenarist

- Research 1 canon fact → design ONE investigative story with 3 escalating evidence beats
- Scenes 2→3→4 are a continuous narrative arc (setup → escalation → surprising conclusion), NOT independent news items
- Fill `reporter_side` ("left" or "right") in the storyboard for each reporter scene — alternate by default
- Each location description must be specific and visually rich enough for NB2 to render the evidence clearly
- Anchor in scenes 1 and 5 — dry authority, same character energy as the game's existing TV universe
- General script rules — `rules/roles/scenarist.md`

### Storyboarder

**Mandatory framing for scenes 2–4 (reporter on location):**
- Reporter occupies **left or right ~30%** of the 9:16 frame per `reporter_side` field
- Evidence/subject fills the **other ~65-70%** of the frame — it must be identifiable without dialogue
- Do NOT generate a centered portrait — this breaks the format
- Use the reporter base avatar from story bible as `image_urls[0]` in NB2 edit
- Prompt template: see `KEY VISUAL RULE` section above

**Scenes 1 and 5 (anchor studio):**
- Frontal portrait, news desk with show branding — same rules as fun-news anchor

- General rules — `rules/roles/storyboarder.md`

### Animator

- Kling Avatar v2 Standard only
- Reporter scenes: `image_url` = per-episode on-location NB2 edit; anchor scenes: studio avatar
- No speedup (`atempo`)
- `apad=whole_dur=<raw_video_dur>` per scene before concat
- General rules — `rules/roles/animator.md`

### Sound

- ElevenLabs TTS, `voice` name string, `stability: 0.55`, `style: omit`
- Anchor voice: `voice_mapping.anchor` from story bible
- Reporter voice: `voice_mapping.reporter` from story bible
- Ambient SFX: location-appropriate per reporter scene (optional, 0.10–0.15 vol)
- Music: opener + CTA only; dialogue = silence (same gate as fun-news)
- General rules — `rules/roles/sound.md`

### Editor

- 7-clip concat: opener (pre-built) + scenes 1–5 + CTA (pre-built)
- `apad` per scene to raw video duration
- `bold` subtitle style, per-scene ASS burn-in before concat
- Music-timed.wav: opener theme + anullsrc silence + CTA reprise (same as fun-news — no `volume:enable`)
- Fade-to-black on scene 5 (last 1s before CTA)
- General rules — `rules/roles/editor.md`
