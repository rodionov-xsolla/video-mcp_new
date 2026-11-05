---
ready_to_post: no
subtitles: true
overlays: false
---

# Format "Game News"

> TODO(style-refactor): style must come from the resolved chain (story bible top-level `style_tags` → game config `prompt_prefix`); character cards are style-free. This file not yet audited for hardcoded house-style.

> **Single video route — H3 lip-sync on MiniMax H3 Max Turbo** (`minimax.h3max.turbo.i2v` with the scene's TTS as `target_audio_url`; it replaced Kling Avatar v2 Standard after Test 13, and Kling Avatar is forbidden here). No other video models. Opener and CTA — pre-built from Supabase. Characters — only from the current `news` series entries in `SUPABASE_ASSETS_FILE`.

This file is the **playbook**: when to use, pipeline, role briefs. Craft rules — in `rules/roles/*.md`.

---

## When to use

Keywords: "новости", "news", "game news", "weekly news", "patch recap", "обновление", "что нового".

---

## Concept

- **Anchor + Co-anchor** — two game characters at the news desk
- **2–3 news items** per episode (minimum 2, found via web search)
- **Only H3 lip-sync on H3 Max Turbo** (`minimax.h3max.turbo.i2v`, `rules/roles/animator.md` §2a "H3 lip-sync") + routed speech audio (lip-sync via `target_audio_url` = the scene's `tts_url`). Every dialogue scene is one H3 lip-sync clip; no plain clip, no still, no Kling Avatar clip
- **Opener and CTA — pre-built videos from Supabase**, not regenerated
- **Duration:** 25–40s after speedup (excluding opener/CTA)
- **Budget:** up to $4 (~$1.60 typical; Test 13: $1.59 per video)

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

**Per-episode desk stills (Storyboarder, one NB2 edit per dialogue scene, $0.08 each):** `image_urls` = that scene's speaker avatar ref; the speaker at the news desk with the scene's camera (Phase 3 table) and the expression of the line, mouth slightly open with teeth visible (`rules/roles/storyboarder.md` §9), no on-screen text. Upload it to the current-run episode namespace as the scene's `scene_image_url`; it is the first frame of the lip-sync clip (Test 13 animated exactly such per-scene desk stills).

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

Every line's TTS must stay ≤15 s (H3's maximum; Test 13's longest line was 12.3 s, ~35 words); a longer line goes back to be shortened. The Animator quotes each line verbatim in a ≤512-byte prompt, so keep the greeting and handoff short (Test 13's ~35-word lines fit in 511–512 bytes only with short descriptors).

Tone — from game config (Tone of Voice). Every dialogue scene must have a `tts` field with its spoken text.

### Phase 4: Animation (H3 lip-sync on H3 Max Turbo only)

For each dialogue scene:
1. **Resolve speech source:** native model audio when the selected scene model intentionally supports it; otherwise Chatterbox only with an approved voice sample owned by this `news` format; otherwise MiniMax. Never read a sample or voice assignment from another format. Generate `.mp3` and upload it to Supabase as the scene's `tts_url`; Sound also writes `tts_duration_sec` and `duration_sec` (= the TTS length rounded up to 0.1 s, `rules/roles/sound.md` §5b). On failure, retry once with the same source/settings, then STOP and report the error.
2. **H3 lip-sync** (`minimax.h3max.turbo.i2v`, `rules/roles/animator.md` §2a "H3 lip-sync" and "Talking-head prompt"), one `tools/kling_runner.py` job per scene: `image_url` = the scene's `scene_image_url` (the Phase 2 desk still, 9:16), `target_audio_url` = `tts_url` (Supabase permanent URL, not a fal.ai temp URL), `duration` = `duration_sec`, `resolution: "768P"`, `prompt_expansion_mode: "disabled"`, `seed: 20261021` and the lip-sync `prompt` (Animator brief). The Animator does not trim, speed up or remux the clip.
3. **1.18x speedup — the Editor's step, after the H3 trim** (Phase 5 step 0). The speed-up command is the one the Kling Avatar route used, unchanged; the input is cut to `duration_sec` first (video and audio):

```bash
$FFMPEG -y -t "$DURATION_SEC" -i scene-K.mp4 \
  -filter_complex "[0:v]setpts=PTS/1.18[v];[0:a]atempo=1.18[a]" \
  -map "[v]" -map "[a]" \
  -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  scene-K-fast.mp4
```

1.18x for news — clear and intelligible, not rushed. Not 1.3x. A clip that came back shorter than `duration_sec` is sped up whole.

### Phase 5: Assembly (FFmpeg)

Strict order:

0. **H3 trim + 1.18x speedup** per scene (Phase 4 step 3) → `scene-K-fast.mp4`. The clip's own audio is the scene's speech (`scene_video_lipsync: true`): never lay `scene-K.mp3` over it, never Kling Avatar's TTS trim
1. **Subtitles** — overlay per-scene on each `-fast.mp4` (NOT on concat! whisper skips voices on concat)
2. **Normalize** all clips: 1080×1920, 30fps, AAC 128k
3. **Opener** — normalize the `.mp4` downloaded from Supabase (same scale/fps/codec)
4. **Concat:** opener → scene-1-sub → scene-2-sub → scene-3-sub
4a. **Lip-sync offset:** the concatenated speech track (opener silence, scenes, CTA) plays 200 ms after the picture: `adelay=200:all=1`, `asetpts=N/SR/TB`, trimmed to the video length; the picture does not move (`rules/roles/editor.md` §0.5, Test 15: 200 ms looked right after the 1.18x speed-up)
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
| Per-episode desk stills (NB2 edit, 3 scenes) | $0.24 |
| New topic reporter (sheet + ref, if needed) | ~$0.16 |
| Routed speech generation (~25-35s) | provider-dependent |
| H3 Max Turbo lip-sync (3 scenes, ~25-35 s returned × $0.04/s) | ~$1.00–1.40 (Kling Avatar v2: ~$1.40–2.00) |
| **Typical** | **~$1.30–1.70** |

**Test 13 (Oct 2026, Kling Avatar v2 baseline → H3 lip-sync, Roblox anchor and co-anchor):** $2.03 → $1.59 per whole video (21.7% saved); the three clips $1.71 → $1.27 (12.4 → 12.960 s, 12.1 → 12.256 s, 6.2 → 6.592 s returned).

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
│   │   ├── scene-1.mp4           # H3 lip-sync clip as returned
│   │   ├── scene-1-fast.mp4      # Editor: H3 trim + 1.18x speedup
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
- Anchor/co-anchor avatar refs are taken from Supabase — do not regenerate them
- One NB2 desk still per dialogue scene from the speaker's avatar ref (Phase 2): the scene's camera, mouth slightly open with teeth visible, no on-screen text → `scene_image_url`
- Topic reporter (if needed) — generate sheet + avatar ref, upload to Supabase
- General rules — `rules/roles/storyboarder.md`

### Animator
- **ONLY H3 lip-sync on H3 Max Turbo** (`minimax.h3max.turbo.i2v`; `rules/roles/animator.md` §2a "H3 lip-sync" and "Talking-head prompt"), one `tools/kling_runner.py` job per dialogue scene. Kling Avatar v2 is forbidden (the replaced route); never a plain clip on H3 Max Turbo, never lip-sync on H3 Max, no still.
- `image_url` = the scene's `scene_image_url` (the per-episode desk still). Run the pre-flight curl check on `tts_url` and `scene_image_url` first (both 200; otherwise STOP and return to Manager). Both are Supabase permanent URLs.
- **Payload — exactly these seven fields (the Test 13 jobs):** `prompt`, `image_url` = `scene_image_url`, `target_audio_url` = `tts_url`, numeric `duration` = the TTS length rounded up to 0.1 s (`math.ceil(round(d*10,6))/10`, equal to the `duration_sec` Sound wrote), `resolution: "768P"`, `prompt_expansion_mode: "disabled"`, `seed: 20261021`. `expect`: `duration_seconds` = that `duration`, `duration_tolerance_seconds: 0.8`, `audio: "required"`, `min_bytes: 100000`, `min_width: 600`, `min_height: 1000`, `orientation: "portrait"`. Template: `tools/examples/minimax-h3-max-turbo-talking-head.job.json`.
- A scene whose TTS is longer than 15 s (H3's maximum) is not submitted: return it to be shortened.
- **Prompt (≤512 UTF-8 bytes):** the speaker by look, position and framing (at the news desk, the scene's camera), the expression and at most one small gesture; no gaze or head lock (`unblinking`, `eyes locked on`, `steady eye contact with camera`, `facing the camera head-on`, `holds still`, `stares`). Then the presenter gaze sentence — anchor, co-anchor and reporter all address the viewer: `He looks into the camera like a TV news presenter, blinking naturally, with small relaxed head movements and changing expression between phrases; no frozen stare.` (`She` for a female speaker). End with `<Speaker> speaks the line "<line>" with lips in sync with the audio.` (`<line>` = the scene's `tts` verbatim). Over 512 bytes: shorten the descriptors first and keep the line whole; only if still too long, shorten the quoted line to its first sentence followed by `…` and report it. No music/voice clause. Example (Test 13, co-anchor, 512 bytes):
  ```
  Sarah, a blocky Roblox co-anchor in a coral blazer, sits at the news desk, three-quarter view. Grinning. She looks into the camera like a TV news presenter, blinking naturally, with small relaxed head movements and changing expression between phrases; no frozen stare. Sarah speaks the line "Thanks Jake! Music joins the party too: Ken Carson performs in The Block today, after CG5 and Dolly Babe shows, with integrations in Blade Ball and Fisch. Spooky season is loud, no cap!" with lips in sync with the audio.
  ```
- Write-back: `scene_video_kind: "i2v"`, `scene_video_route: "minimax.h3max.turbo.i2v"`, `scene_video_audio: "native"`, `scene_video_lipsync: true`. Do not trim or speed up the clip (the Editor does both).
- Cost: $0.04/s on the returned length, on the H3 lip-sync cost line.
- General rules — `rules/roles/animator.md`

### Sound
- Generate speech for each dialogue scene using native audio → current-format-owned Chatterbox sample → otherwise MiniMax. Retry the same route once, then stop; do not switch providers.
- Subtitles per-scene (not on concat)
- Music: energetic/fun, `volume=0.10`
- General rules — `rules/roles/sound.md`

### Editor
- Per scene first: H3 trim to `duration_sec`, then the 1.18x speedup (Phase 4 step 3) → `scene-K-fast.mp4`; the clip's own audio is the speech, never `scene-K.mp3` over it
- Download opener + CTA from Supabase, normalize
- Subtitles per-scene → normalization → concat with opener → music → fade → CTA
- General rules — `rules/roles/editor.md`

---

## Validation

- [ ] `research.json` with 2–3 news items and sources
- [ ] Avatar refs for both characters from Supabase
- [ ] Opener and CTA downloaded from Supabase (not generated)
- [ ] All dialogue scenes — H3 lip-sync on `minimax.h3max.turbo.i2v` with the exact seven-field payload (`seed: 20261021`), `scene_video_audio: "native"`, `scene_video_lipsync: true`, and `tts_url`, `tts_duration_sec` ≤ 15 and the rounded-up `duration_sec`; no Kling Avatar clip
- [ ] H3 trim, then 1.18x speedup, on all lip-sync clips (Editor)
- [ ] Subtitles per-scene (not on concat)
- [ ] camera_angle different for adjacent scenes
- [ ] Final: 1080×1920, 30fps, 25–40s (excluding opener/CTA), budget < $4

---

## FORBIDDEN

- Any video route other than H3 lip-sync on H3 Max Turbo; Kling Avatar v2 (`fal-ai/kling-video/ai-avatar/*`) — replaced after Test 13, never a fallback
- A plain clip, a still, or lip-sync on H3 Max for a dialogue scene
- Gaze- or head-locking phrases in a lip-sync prompt (`unblinking`, `eyes locked on`, `steady eye contact with camera`, `facing the camera head-on`, `holds still`, `stares`)
- Laying `scene-K.mp3` over a lip-sync clip, or trimming/speeding up the clip in the Animator
- Generating opener/CTA — taken from Supabase
- Regenerating existing current-format characters — anchor/co-anchor come from the filtered `SUPABASE_ASSETS_FILE`
- Subtitles on a concatenated video — whisper skips voices on concat
- 1.3x speedup — too fast, only 1.18x
- fal.ai temp URLs for the lip-sync job — only Supabase permanent URLs
- ElevenLabs or a voice/sample copied from another format
- One avatar ref for both — each character = its own ref
