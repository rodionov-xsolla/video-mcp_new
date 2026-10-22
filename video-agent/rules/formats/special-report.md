---
ready_to_post: yes
subtitles: true
overlays: false
---

# Format "Special Report" — Single-reporter investigative special from a game's lore

> **Single video route — H3 lip-sync on MiniMax H3 Max Turbo** (`minimax.h3max.turbo.i2v` with the scene's TTS as `target_audio_url`; it replaced Kling Avatar v2 Standard after Test 12, and Kling Avatar is forbidden here). Opener and CTA — pre-built from Supabase. Anchor and reporter — locked independently in this format's resolved story bible. Reporter visits **3 locations** telling ONE unified ironic story. Tone — mock-journalistic / absurd-earnest. KEY VISUAL: reporter stands to the SIDE of frame, leaving room for the subject being investigated.

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

- **1 permanent anchor** + **1 permanent reporter**, both locked in this format's story bible without reading appearance or voice assignments from other formats
- Reporter visits **exactly 3 locations** to tell ONE unified ironic/absurd investigative story
- At each location: reporter stands to the **SIDE** of frame (~30% width), leaving 65-70% for the evidence/subject
- **Only H3 lip-sync on H3 Max Turbo** (`minimax.h3max.turbo.i2v`, `rules/roles/animator.md` §2a "H3 lip-sync") + routed speech audio (lip-sync via `target_audio_url` = the scene's `tts_url`). Every dialogue scene is one H3 lip-sync clip; no plain clip, no still, no Kling Avatar clip
- **Opener and CTA — pre-built mp4 from Supabase**, not regenerated per episode
- **Tone:** mock-journalistic / ironic-investigative / absurd-earnest — reporter treats absurd topic with full journalistic seriousness
- **Duration:** 35–50s natural TTS speed (including opener + CTA)
- **Budget:** up to $4.50 hard cap (~$2.35 typical EP2+; pilot ~$2.85 with new assets; Test 12: $2.64 per video)
- **Frame format:** 9:16 (1080×1920)

### Models

- **Image:** NB2 (3 per-episode on-location reporter edits + one-time anchor studio avatar)
- **Video:** H3 lip-sync on MiniMax H3 Max Turbo (`minimax.h3max.turbo.i2v`, $0.04/s of the returned clip length ≈ the TTS length). Kling Avatar v2 Standard ($0.056/s of input audio) is the replaced route (the Test 12 baseline) and is forbidden in this format
- **Audio:** native model speech when intentionally available; otherwise a current-format-owned sample through Chatterbox; otherwise MiniMax

---

## Visual Identity & Branding (MANDATORY)

### Opener — game-specific, always required

Every special-report episode opens with a game-specific branded opener ("Genshin Special Report", "Roblox Special Report", etc.). Rules:
- Show name: `"{GameName} Special Report"` — distinct from `"{GameName} Funtasy News"` (fun-news). Separate branding, separate opener mp4.
- Visual style matches the game's aesthetic.
- Use this format's own opener and branding only. Never inspect, reuse, or derive it from another format's opener; CTA is the sole automatic cross-format asset exception.

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
game-authentic environment, game-authentic look per the resolved style chain (game config prompt_prefix / story bible style_tags),
NOT centered portrait, 9:16 vertical broadcast field reporter composition,
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
2. Resolve required `games/{GAME_TAG}/special-report_story_bible.json`. If missing, STOP and ask whether the user wants it created; create it only after explicit confirmation.
3. Read Manager's prefiltered `SUPABASE_ASSETS_FILE`; it contains only assets owned by this `special-report` format/series plus the separately resolved game CTA. Do not run a broad `game_tag` query:
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
           game-authentic look per the resolved style chain (game config prompt_prefix / story bible style_tags),
           NOT centered portrait,
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

| Scene | Words | ~TTS dur | Cost (H3 lip-sync) |
|---|---|---|---|
| 1 Anchor intro | 15–20 | ~6–8s | ~$0.29 |
| 2 Reporter loc 1 | 20–28 | ~8–11s | ~$0.39 |
| 3 Reporter loc 2 | 20–28 | ~8–11s | ~$0.39 |
| 4 Reporter loc 3 | 20–28 | ~8–11s | ~$0.39 |
| 5 Anchor reaction | 15–20 | ~6–8s | ~$0.29 |
| **Total** | **~95–120** | **~36–49s** | **~$1.75** (Test 12: $2.14; Kling Avatar v2: $2.87) |

Every line's TTS must stay ≤15 s (H3's maximum); a longer line goes back to be shortened. The Animator quotes each line verbatim in a ≤512-byte prompt, so a reporter line near 28 words leaves little room for the descriptors (the tested 26-word line fit in 508 bytes with short descriptors).

Same punctuation tax rules as fun-news (prefer commas/em-dashes over periods).

### Phase 4: Animation (H3 lip-sync on H3 Max Turbo only)

For each dialogue scene:
1. Resolve speech source in this order: native model audio when intentionally supported for the scene → Chatterbox only when this resolved `special-report` story bible owns an approved sample for the speaker → otherwise MiniMax. Generate mp3 and upload to Supabase as the scene's `tts_url`; Sound also writes `tts_duration_sec` and `duration_sec` (= the TTS length rounded up to 0.1 s, `rules/roles/sound.md` §5b). Never read a sample or voice assignment from another format. On failure, retry once with the same source/settings, then STOP and report the error.
2. H3 lip-sync (`minimax.h3max.turbo.i2v`, `rules/roles/animator.md` §2a "H3 lip-sync" and "Talking-head prompt"), one `tools/kling_runner.py` job per scene: `image_url` = the scene's `scene_image_url` (the same still the Kling Avatar route used: per-location NB2 edit for reporter scenes, studio avatar for anchor scenes), `target_audio_url` = `tts_url`, `duration` = `duration_sec`, `seed: 20261021` (Animator brief). The Animator does not trim, speed up or remux the clip.
3. No speedup — natural TTS pace
4. `apad=whole_dur=<played_dur>` per scene, after the Editor's H3 trim to `duration_sec` (a clip that came back shorter plays whole)

### Phase 5: Assembly (FFmpeg)

Same canonical single-pass pipeline as fun-news. 7 clips: opener + 5 scenes + CTA.

```
Inputs:
  [0..4]  scene-1..5.mp4  (H3 lip-sync clips, own audio = the scene TTS; H3 trim to duration_sec first)
  [5]     opener.mp4      (pre-built, Supabase)
  [6]     cta.mp4         (pre-built, Supabase)
  [7]     music-timed.wav (pre-built by Sound)

VIDEO: opener → scene-1 → scene-2 → scene-3 → scene-4 → scene-5 (fade-out last 1s) → cta
AUDIO: per-scene clip audio (H3 trim) → apad → concat → adelay=2000 for opener offset → amix with music-timed.wav
```

Output: local `final.mp4`; after explicit user approval, Manager uploads through its canonical run-scoped path.

---

## Budget

| Component | Cost |
|---|---|
| 3 reporter on-location NB2 edits | 3 × $0.08 = **$0.24** |
| 5 H3 lip-sync scenes (~8s avg each; $0.04/s on the returned length) | 5 × ~$0.35 ≈ **$1.75** (Kling Avatar v2: 5 × $0.45 ≈ $2.25) |
| Routed speech generation (5 lines) | provider-dependent |
| **Steady-state total** | **~$2.35** |
| Pilot extra (2 new avatars + opener NB2) | +~$0.50 |
| **Pilot total** | **~$2.85** |

**Test 12 (Oct 2026, Kling Avatar v2 baseline → H3 lip-sync):** $3.37 → $2.64 per whole video (21.7% saved); the five clips $2.87 → $2.14 (its lines averaged ~10 s).

**Cap: $4.50. Stop if spend > $4.00.**

---

## Voices

| Role | Speech source | Direction |
|---|---|---|
| Anchor | native → current-format sample via Chatterbox → MiniMax | locked in resolved story bible |
| Reporter | native → current-format sample via Chatterbox → MiniMax | locked in resolved story bible |

For MiniMax, `voice_mapping` stores the MiniMax preset; for Chatterbox it stores the approved current-format sample URL. ElevenLabs IDs are forbidden.

---

## Story Bible

After explicit user confirmation on a missing-bible first run, create `games/{GAME_TAG}/special-report_story_bible.json`:

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

**FIFO 5** on `episode_summaries`. Append only after the user explicitly approves the presented final video:
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
${OUTPUT_DIR}/
├── storyboard.json
├── research.json
├── final.mp4
├── scenes/
│   ├── scene-1.mp4      # H3 lip-sync clip as returned (the Editor applies the H3 trim)
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
- [ ] Every scene is H3 lip-sync on `minimax.h3max.turbo.i2v` with the exact seven-field payload (`seed: 20261021`), `scene_video_audio: "native"`, `scene_video_lipsync: true`, and has `tts_url`, `tts_duration_sec` ≤ 15 and the rounded-up `duration_sec`; no Kling Avatar clip
- [ ] `final.mp4` duration 35–55s
- [ ] Anchor and reporter are resolved only from this format's story bible
- [ ] Reporter same character across scenes 2–4 (same `image_url` base)
- [ ] `reporter_side` alternates across scenes 2–4 (or is intentionally consistent)
- [ ] 3 location `image_prompt`s are visually distinct environments

---

## Anti-patterns

- ❌ Reporter centered in frame (kills the format's core visual identity)
- ❌ Reading or copying an anchor, reporter, appearance card, asset, or voice assignment from another format without explicit user instruction
- ❌ 3 locations with visually identical backgrounds (different names alone aren't enough)
- ❌ Separate unrelated news items instead of ONE unified investigation
- ❌ `-shortest` in FFmpeg (ALWAYS use `apad`)
- ❌ ElevenLabs or provider/sample switching after a failed speech generation
- ❌ `atempo` speedup on the lip-sync clips
- ❌ Kling Avatar v2 (`fal-ai/kling-video/ai-avatar/*`) for any special-report scene — replaced by H3 lip-sync after Test 12; never a fallback
- ❌ A plain clip on H3 Max Turbo, a lip-sync clip on H3 Max, or a still for a dialogue scene
- ❌ Gaze- or head-locking phrases in a lip-sync prompt (`unblinking`, `eyes locked on`, `steady eye contact with camera`, `facing the camera head-on`, `holds still`, `stares`) — H3 then stares into the lens
- ❌ Laying `scene-K.mp3` over a lip-sync clip (its soundtrack already is that TTS), trimming the clip in the Animator, or Kling Avatar's TTS trim in the Editor
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
- Frontal portrait, news desk with this format's own show branding and format-owned assets

- General rules — `rules/roles/storyboarder.md`

### Animator

- **ONLY H3 lip-sync on H3 Max Turbo** (`minimax.h3max.turbo.i2v`; `rules/roles/animator.md` §2a "H3 lip-sync" and "Talking-head prompt"), one `tools/kling_runner.py` job per scene, all 5 scenes. Kling Avatar v2 is forbidden (the replaced route); never a plain clip on H3 Max Turbo, never lip-sync on H3 Max, no still.
- `image_url` = the scene's `scene_image_url`: the per-episode on-location NB2 edit (reporter scenes) or the studio avatar (anchor scenes). Run the pre-flight curl check on `tts_url` and `scene_image_url` first (both 200; otherwise STOP and return to Manager).
- **Payload — exactly these seven fields (the Test 12 jobs):** `prompt`, `image_url` = `scene_image_url`, `target_audio_url` = `tts_url`, numeric `duration` = the TTS length rounded up to 0.1 s (`math.ceil(round(d*10,6))/10`, equal to the `duration_sec` Sound wrote), `resolution: "768P"`, `prompt_expansion_mode: "disabled"`, `seed: 20261021`. `expect`: `duration_seconds` = that `duration`, `duration_tolerance_seconds: 0.8`, `audio: "required"`, `min_bytes: 100000`, `min_width: 600`, `min_height: 1000`, `orientation: "portrait"`. Template: `tools/examples/minimax-h3-max-turbo-talking-head.job.json`.
- A scene whose TTS is longer than 15 s (H3's maximum) is not submitted: return it to be shortened.
- **Prompt (≤512 UTF-8 bytes):** the speaker by look, position and framing (from the storyboard and the scene image: the reporter's side of frame, the anchor at the desk), the expression and at most one small gesture; no gaze or head lock (`unblinking`, `eyes locked on`, `steady eye contact with camera`, `facing the camera head-on`, `holds still`, `stares`). Then the anchor/reporter gaze sentence — both address the viewer: `He looks into the camera like a TV news presenter, blinking naturally, with small relaxed head movements and changing expression between phrases; no frozen stare.` (`She` for a female speaker). End with `<Speaker> speaks the line "<line>" with lips in sync with the audio.` (`<line>` = the scene's `tts` verbatim). Over 512 bytes: shorten the descriptors first and keep the line whole; only if still too long, shorten the quoted line to its first sentence followed by `…` and report it. No music/voice clause. Example (Test 12, reporter standing to the side of frame, 508 bytes):
  ```
  Hu Tao, with dark twin tails and a black wide-brimmed hat, stands left of frame with a mic by folder stacks. Grinning. She looks into the camera like a TV news presenter, blinking naturally, with small relaxed head movements and changing expression between phrases; no frozen stare. Hu Tao speaks the line "Aiya, I'm inside Favonius headquarters, where Jean's desk hides under stacks of incident reports, all filed under one name, Klee. Bomb fishing, again. Next, the lake." with lips in sync with the audio.
  ```
- Write-back: `scene_video_kind: "i2v"`, `scene_video_route: "minimax.h3max.turbo.i2v"`, `scene_video_audio: "native"`, `scene_video_lipsync: true`, `motion_prompt` = the prompt. No speedup (`atempo`); do not trim, pre-encode or remux the clip.
- Retry a technically failed job once with the same route/settings, then STOP; no switch to Kling Avatar, H3 Max, another provider or a still.
- **Debug mode:** list the 5 planned clips with per-clip cost (requested `duration` × $0.04/s) before the paid batch; a lip-sync clip of about 7.5 s or longer is above the $0.30 confirm threshold.
- Cost: $0.04/s on the returned length, on the H3 lip-sync cost line.
- General rules — `rules/roles/animator.md`

### Sound

- Speech priority: native audio → approved sample owned by this `special-report` bible through Chatterbox → otherwise MiniMax
- Anchor and reporter routes come only from this format's resolved story bible; retry the same route once, then stop
- Upload each scene's mp3 as its `tts_url` before Phase 4 (the Animator sends it as the lip-sync `target_audio_url`) and write `tts_duration_sec` and `duration_sec` = the TTS length rounded up to 0.1 s on every scene (`rules/roles/sound.md` §5b). A line whose TTS is longer than 15 s is not uploaded: STOP and return it to be shortened.
- Ambient SFX: location-appropriate per reporter scene (optional, 0.10–0.15 vol)
- Music: opener + CTA only; dialogue = silence (same gate as fun-news)
- General rules — `rules/roles/sound.md`

### Editor

- 7-clip concat: opener (pre-built) + scenes 1–5 + CTA (pre-built)
- Every scene is an H3 lip-sync clip (`scene_video_lipsync: true`): **H3 trim** of video and audio to `duration_sec` first (play whole when the clip is shorter), never Kling Avatar's TTS trim; the clip's own audio is the scene's speech — never lay `scene-K.mp3` over it again
- `apad` per scene to the played video duration
- `build/voice-final.wav` for subtitle timing is extracted from the lip-sync clips' own audio (`rules/roles/editor.md` §6.1, multi-voice)
- `bold` subtitle style, per-scene ASS burn-in before concat
- Music-timed.wav: opener theme + anullsrc silence + CTA reprise (same as fun-news — no `volume:enable`)
- Fade-to-black on scene 5 (last 1s before CTA)
- General rules — `rules/roles/editor.md`
