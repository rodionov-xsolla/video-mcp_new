---
ready_to_post: yes
subtitles: true
overlays: false
---

# Format "Fun News" — Fictional ironic news from a game's lore

> **Single video route — H3 lip-sync on MiniMax H3 Max Turbo** (`minimax.h3max.turbo.i2v` with the scene's TTS as `target_audio_url`; it replaced Kling Avatar v2 Standard after Test 12, and Kling Avatar is forbidden here). Scene 0 is one pre-built branding asset resolved from the game bible: use non-empty `hook_url` when present (currently Star Trek), otherwise `opener_url` (currently Genshin). CTA — pre-built from Supabase. Anchor — locked per game in story bible. Reporters — variable, pulled from Supabase by topic. Tone — ironic/satirical/absurd mix.

This file is the **playbook**: when to use, pipeline, role briefs. Craft rules — in `rules/roles/*.md`.

**Distinct from:**
- `news.md` — real game news (web search for actual patch notes / events). Fun News is **fictional** — invented headlines extrapolated from canon lore.
- `redcon.md` — alternate-history one-shots about a single character/event. Fun News is a recurring newsroom format with multiple short items per episode.

---

## When to use

Keywords: "fun news", "fictional news", "fake news", "lore news", "ироничные новости", "выдуманные новости", "фейковые новости", "satire news", "lore satire".

---

## Concept

- **1 permanent anchor** (locked per game in story bible) + **1–2 changing reporters** per episode (chosen by topic from Supabase `game_assets`)
- **2–3 fictional news items** per episode, extrapolated from canon lore (no real patch notes)
- **Only H3 lip-sync on H3 Max Turbo** (`minimax.h3max.turbo.i2v`, `rules/roles/animator.md` §2a "H3 lip-sync") + routed speech audio (lip-sync via `target_audio_url` = the scene's `tts_url`). Every dialogue scene is one H3 lip-sync clip; no plain clip, no still, no Kling Avatar clip
- **Opening branding clip (scene 0) — pre-built and reused.** Resolve `hook_url` first when non-empty; otherwise use `opener_url`. Never regenerate it per episode. No subtitles or channel bug on scene 0.
- **CTA — pre-built mp4 from Supabase**, not regenerated. Jingle bg-music plays over it.
- **Tone:** ironic / satirical / absurd / dry-deadpan — mix per item
- **Duration:** 35–50s at natural speech speed (including opening clip + CTA)
- **Budget:** up to $4.50 hard cap (~$2.50 typical for episode 2+; Test 12: $1.91 per video; pilot episodes run higher due to one-time prep + iteration)
- **Frame format:** 9:16 (1080×1920)

### Models

- **Image:** NB2 (per-episode on-location backgrounds for reporters + one-time anchor avatar)
- **Video:** H3 lip-sync on MiniMax H3 Max Turbo (`minimax.h3max.turbo.i2v`, $0.04/s of the **returned clip length** ≈ the TTS length — see Budget pitfall below). Kling Avatar v2 Standard ($0.056/s of input audio) is the replaced route (the Test 12 baseline) and is forbidden in this format
- **Audio:** intentional native speech when available → approved sample owned by this `fun-news` bible through Chatterbox → otherwise MiniMax

---

## Visual Identity & Branding (MANDATORY)

### Opening branding clip (scene 0) — reusable asset, always prepended

Every fun-news episode opens with exactly one pre-built asset from the resolved story bible. If `hook_url` is non-empty, use it (Star Trek currently has the baked-SFX hook). Otherwise use non-empty `opener_url` (Genshin currently has the standard opener). Reuse the chosen asset every episode.

**Default behaviour (Manager):** resolve `OPENING_URL = hook_url || opener_url`, download it, measure its actual duration with `ffprobe`, and prepend it as scene 0. No regeneration, no SFX work.

**Storyboard:** record the resolved opening asset URL and kind (`hook` or `opener`). Never declare both active.

**No subtitles, no channel bug** on scene 0.

#### When to regenerate the opening asset (explicit user request only)
Only regenerate if the user explicitly asks for a new opening asset. Process:
- **Kling I2V** — physical comedy beat with anchor (falls, teleports, chair collapses, etc.). Wide/action shot. Title card burn-in after action beat shows show name. ~4–6s.
- **SFX audio** — use intentional native audio where available; otherwise generate any required vocal reaction via the normal speech route. A failed request is retried once with the same provider/settings, then production stops. Do not switch provider or use a local fallback.
- After the user explicitly approves the new asset: upload it under this game and format, then update the field that was resolved (`hook_url` or `opener_url`).

### Opening audio and CTA music

Preserve the resolved opening asset's own audio. Generate an upbeat, non-jarring instrumental theme for the CTA. During all dialogue scenes: **no background music** (real silence). Music placement:
- t=0 → measured opening end: opening asset audio only
- opening end → CTA start: **silence** — dialogue only, no music
- CTA start → end (~5s): generated CTA theme plays with fade-out

**Implementation (Editor):** build a `music-timed.wav` using `anullsrc` for the silence portion — do NOT use `volume=0:eval=frame:enable=...` (FFmpeg passthrough bug: `enable` is an identity filter, not a gate; audio plays at full volume when condition is false). The only correct approach is pre-baked real silence.

### TV attributes (all scenes, both anchor and reporters)

**Microphones:**
- Reporters always hold a **broadcast handheld microphone** with the **show's name printed on the mic flag** (e.g. "GoT Daily", "Trek Report"). NOT a generic channel logo, NOT a blank flag.
- Anchor has a **desk mic** visible on the news desk.
- Mic flag must be legible — include in NB2 prompt: `"handheld broadcast mic with '[SHOW NAME]' printed on the mic flag in the reporter's hand"`.

**Studio signage:**
- The anchor's studio must include **visible show branding** — a desk plaque or lower-third banner/sign with the show name. One tasteful sign at desk level (NOT a wall-size logo, NOT text floating on background). Include in NB2 anchor prompt: `"desk nameplate reading '[SHOW NAME]'"`.

### Reporter background matches news topic (MANDATORY)

On-location backgrounds must reflect the **specific news item being covered**, not just the reporter's general territory:
- Varys covering a dragon story → background shows dragons, scorched stone, fire smoke — NOT bare King's Landing corridor
- Jon Snow covering a winter story → blizzard, falling snow, icy Wall details in frame
- Any reporter → the viewer should be able to guess the topic from the background alone before the reporter speaks

**Scenarist responsibility:** `news_items[].location` must be a specific, visually rich description: not `"King's Landing"` but `"King's Landing dragon landing zone — scorched stone pavement, smoke plumes, charred wood beams in background"`.

**Storyboarder responsibility:** inject these topic-specific elements into the NB2 on-location edit prompt — the background should SHOW the news, not just indicate the general region.

---

## Pipeline (strict order)

### Phase 0: Initialization

1. Read game config: `games/{GAME_TAG}/{GAME_TAG}.md`
2. Resolve required `games/{GAME_TAG}/fun-news_story_bible.json`. If missing, STOP and ask whether the user wants it created; create it only after explicit confirmation.
3. Read Manager's prefiltered `SUPABASE_ASSETS_FILE`. It contains only assets owned by this `fun-news` format/series plus the separately resolved game CTA. Do not run a broad `game_tag` query.

Find from the result:
   - **Opening asset** — resolve the story bible's non-empty `hook_url`, otherwise `opener_url`, to its `.mp4`
   - **CTA** — record with tag `cta` and `video` → `.mp4`
   - **Anchor avatar** — record matching `anchor.character_name` from the story bible, tag `fun-news` and `avatar` → `.png`
   - **Reporter base avatars** — records with tag `fun-news` and `avatar` matching reporter names selected in Phase 1; these are the **portrait base** for per-episode on-location edits

4. **STOP** if neither `hook_url` nor `opener_url`, the CTA, or the anchor avatar can be resolved — notify the user. Never synthesize a replacement CTA/end card.
5. **STOP** if a topic-matched reporter base avatar is missing — Phase 2 handles new reporter generation explicitly.

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
      "summary": "20-30-word fictional report — KEEP TIGHT, see word-budget below",
      "location": "Where the reporter stands (Vulcan Academy, Starfleet briefing room, etc.) — used for NB2 on-location bg",
      "kicker_phrases": ["phrase1", "phrase2"]
    }
  ],
  "topic_tags": ["faction-X", "character-Y", "location-Z"]
}
```

### Phase 2: Characters and on-location backgrounds

**Anchor** — read `anchor.character_name` from story bible. Avatar ref already downloaded in Phase 0. Anchor stays in the same news-desk studio every episode (do **not** regenerate per episode).

**Reporters** — choose **1–2** based on `topic_tags`:
- Prefer canon characters that are thematically tied to the news topic (a Vulcan-themed item → Spock; a Voyager-themed item → Seven of Nine; a Klingon honor-themed item → Worf).
- Look up reporter base avatars in Supabase by `character_name` and tag `fun-news,avatar`.

**Reporters always carry a microphone (MANDATORY):**

Every reporter in every on-location image must visibly hold a **broadcast handheld microphone** — the kind a field reporter holds up to their mouth. This is a core visual identity signal of the fun-news format (they are field reporters, not studio guests). The microphone must appear in the NB2 on-location prompt explicitly: `"holding a broadcast handheld microphone in one hand"`. Do NOT use a desk mic (that belongs to the anchor only) or a lavalier/clip mic (invisible). If the character previously held a scroll or other prop, replace it with the microphone or add it to the free hand.

**Per-episode on-location backgrounds (MANDATORY, $0.08 × N_reporters per episode):**

The format spec calls for reporters to appear **on location relevant to their news item**, not against bare/abstract studio backgrounds. For each reporter selected in Phase 1, generate a fresh NB2 **edit** using the base avatar as `image_urls[0]`:

```
NB2 /edit with:
  image_urls: [reporter_base_avatar_url]
  prompt: "{character} on-location field reporter at {news_item.location},
           {game house-style from the resolved style chain — game config prompt_prefix / story bible style_tags, verbatim},
           9:16 vertical, ... mouth slightly open mid-speech for lipsync,
           professional broadcasting key light on face,
           no on-screen text overlay, no captions"
```

Upload each per-episode on-location PNG to the Manager-provided current-run episode namespace (no `game_assets` registration).

**If a topic-matched reporter has NO base avatar in Supabase:**
1. **Character sheet** (NB2 text-to-image, 16:9 concept art) — `$0.08`
2. **Avatar ref** (NB2 edit with sheet as ref, 9:16, frontal portrait, teeth visible for lipsync) — `$0.08`
3. Upload both to Supabase via `queue/upload-asset.sh` with tags `fun-news,avatar`
4. In future episodes this reporter is already in Supabase

**Style consistency:** the lip-sync clip animates the scene image itself and closely tracks it. Use only refs created/tagged for this `fun-news` format; if none exists, generate a new format-bound ref. Never borrow another format's image or appearance/voice description unless the user explicitly instructs it.

### Phase 3: Script → `storyboard.json`

Structure — **scene 0 (resolved pre-built opening clip) + 5 dialogue scenes** (CTA is pre-built, not in storyboard):

| Scene | Role | Camera | Content |
|---|---|---|---|
| 0 | **Opening branding clip** | Pre-built | `hook_url` when present, otherwise `opener_url`; preserve its own content/audio and actual duration. |
| 1 | **Anchor intro** | Frontal, medium close-up | Hook-first: `"Hi, I'm {Anchor} with {Show} — {hook line}. {Reporter 1} is on the line."` Do **not** tease the items' contents — that's spoiler. |
| 2 | **Reporter 1** | On-location, three-quarter medium close-up | Fictional news #1 + ironic kicker. Ends with `"{Anchor name}?"` — handoff back to anchor. |
| 3 | **Anchor reaction (interstitial)** | Frontal, medium close-up | Short, in-character reaction + handoff to reporter 2. Example: `"Astonishing, as expected — {Reporter 2}, you're up."` — ~5–8 words. |
| 4 | **Reporter 2** | On-location, frontal/different angle from scene 2 | Fictional news #2 + reaction. Ends with `"{Anchor name}?"` handoff. |
| 5 | **Anchor outro** | Slightly wider than scene 1, fade-out last 1s before CTA | Wrap + signature ironic sign-off + "Goodnight." Do **not** tease next episode (this format is non-serial). |

With 1 reporter: scenes 1, 2, 3, 4, 5 = anchor → R1 → anchor reaction (recap-ish) → anchor (delivers news #2 directly) → anchor outro. But two reporters is the default — recruit from `reporter_pool`.

**Handoff — by name, mandatory.**
- Anchor → Reporter: terse, no preamble: `"{Reporter name} is on the line."` / `"{Reporter name}, you're up."`
- Reporter → Anchor: terse: `"{Anchor name}?"` (single-word handoff is correct)

**Tone per scene** — pick from `satire_angle` of the corresponding news item (`ironic` / `satirical` / `absurd` / `dry-deadpan`). Adjacent reporter scenes (2 and 4) should not repeat the same angle. The anchor reaction in scene 3 should be **sarcastic** — a dry put-down that doesn't take the previous item seriously.

**Script word budget (HARD — drives lip-sync cost):**

| Scene | Words | Speech @ ~2.5 wps | Natural final duration | Cost (H3 lip-sync) |
|---|---|---|---|---|
| 1 Anchor intro | 15–20 | ~6–8s | ~6–8s | ~$0.29 |
| 2 Reporter 1 | **max 18** | ~5–7s | ~5–7s | ~$0.25 |
| 3 Anchor reaction | 5–10 | ~3–5s | ~3–5s | ~$0.17 |
| 4 Reporter 2 | **max 18** | ~5–7s | ~5–7s | ~$0.25 |
| 5 Anchor outro | 15–20 | ~6–10s | ~6–10s | ~$0.33 |
| **Total** | **~70–86** | **~25–37s** | **~25–37s** | **~$1.30** (Test 12: $1.40; Kling Avatar v2: $1.89) |

Every line's TTS must stay ≤15 s (H3's maximum); a longer line goes back to be shortened.

**Punctuation pacing** — speech engines can add a noticeable pause on every `.`, slightly less on `,` and `—`. To keep the anchor energetic, prefer commas and em-dashes for natural cadence; reserve periods for the final beat.

Every dialogue scene has a `tts` field with its spoken text.

### Phase 4: Animation (H3 lip-sync on H3 Max Turbo only)

For each dialogue scene:
1. Resolve speech per speaker: intentional native model speech → Chatterbox only with an approved sample owned by this resolved `fun-news` bible → otherwise MiniMax. Generate `.mp3` and upload it to Supabase as the scene's `tts_url`; Sound also writes `tts_duration_sec` and `duration_sec` (= the TTS length rounded up to 0.1 s, `rules/roles/sound.md` §5b). Retry one failure once with the same route/settings, then STOP; never switch provider or borrow another format's sample.
2. **H3 lip-sync** (`minimax.h3max.turbo.i2v`, `rules/roles/animator.md` §2a "H3 lip-sync" and "Talking-head prompt"), one `tools/kling_runner.py` job per scene:
   - `image_url` = the scene's `scene_image_url` (9:16, not square) — the same still the Kling Avatar route used: the anchor's studio avatar, or a reporter's per-episode **on-location** edit from Phase 2.
   - `target_audio_url` = the scene's `tts_url` (the TTS mp3 **from Supabase**, not a fal.ai temp URL).
   - `duration` = the TTS length rounded up to 0.1 s (`duration_sec`), plus `resolution: "768P"`, `prompt_expansion_mode: "disabled"`, `seed: 20261021` and the lip-sync `prompt` (Animator brief).
3. **Output ≈ the TTS length** (Test 12: 6.6 → 6.592 s, 12.4 → 12.960 s); its soundtrack is the TTS itself. The Animator does not trim, speed up or remux the clip; the Editor applies the H3 trim to `duration_sec` (Phase 5).
4. **No speedup.** The lip-sync clip goes straight into the Editor's canonical pipeline at natural TTS speed. Applying atempo=1.3 (tried in EP1–2 on Kling Avatar) makes characters sound unnatural.

### Phase 5: Assembly (FFmpeg)

Canonical single-pass pipeline (see `rules/roles/editor.md` §0). Pseudo-graph:

```
Inputs:
  [0..4]   scene-1..5.mp4 (H3 lip-sync clips, video + their own audio = the scene TTS; untrimmed)
  [5]      opening.mp4 (`hook_url` when non-empty, otherwise `opener_url`; actual duration measured)
  [6]      cta.mp4 (Supabase, no audio)
  [7]      bg-music.mp3 (Sound's MiniMax-generated track)
  [8]      gln-bug.png ONLY IF GAME_TAG=star-trek-timelines AND FORMAT=fun-news

VIDEO branch:
  [5:v]  scale/pad/fps,setpts=PTS-STARTPTS                          → [vopen] (no subtitles/bug)
  [k:v]  trim=end=DUR_k,setpts=PTS-STARTPTS,scale/pad/fps,setpts=PTS-STARTPTS,ass=build/scene-k.ass → [vk]   (k=0..4; H3 trim, DUR_k = duration_sec)
  [4:v]  + fade=t=out:st=PLAYED_DUR-1:d=1.0 on scene-5 only
  [6:v]  scale/pad/fps,setpts=PTS-STARTPTS                          → [vct]
  [v0][v1][v2][v3][v4] concat=n=5:v=1:a=0                          → [vmain]
  IF GAME_TAG=star-trek-timelines AND FORMAT=fun-news:
    [8:v]scale=110:110,format=rgba[bug];[vmain][bug]overlay=40:40    → [vmainout]
  ELSE:
    [vmainout] = [vmain] (do not download or reference any channel bug)
  [vopen][vmainout][vct] concat=n=3:v=1:a=0                         → [vout]

AUDIO branch:
  [5:a]  asetpts=PTS-STARTPTS                                        → [aopen] (preserve embedded audio; inject matching anullsrc only if absent)
  [k:a]  atrim=end=DUR_k,asetpts=PTS-STARTPTS,apad=whole_dur=<played_dur_k> → [ak]   (k=0..4, scenes 1-5; the clip's own audio)
  [a0][a1][a2][a3][a4] concat=n=5:v=0:a=1                           → [adlg]
  [adlg] adelay=<OPEN_DUR_MS>|<OPEN_DUR_MS>                          → [atts]   (measured opening duration; never fixed 2s)
  [7:a]  (music-timed.wav — silence for opening+dialogue, theme for CTA) → [amus]
  [aopen][atts][amus] amix=inputs=3:duration=longest:normalize=0     → [aout]

Output:
  -map [vout] -map [aout]
  -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p
  -c:a aac -b:a 128k -ar 44100 -ac 2
  -t TOTAL_DUR
  build/final.tmp.mp4   → mv final.mp4 after ffprobe-validate
```

**Critical:** every scene is an H3 lip-sync clip (`scene_video_lipsync: true`, `scene_video_audio: "native"`). The Editor applies the **H3 trim** (`rules/roles/editor.md` §0.1): video and audio cut to the scene's `duration_sec` (`DUR_k`, the TTS length rounded up to 0.1 s, so the cut only removes H3's padding and never the speech); a clip that came back shorter than `duration_sec` plays whole (played length = its MP4 duration). Then `apad=whole_dur=<played_dur>` per scene aligns audio in the concat graph; without `apad`, audio drifts ahead of video by scene 5. The clip's own audio is the scene's speech: never lay `scene-K.mp3` over it again, and never apply Kling Avatar's TTS trim.

**ASS subtitles** — one ASS per scene via `tools/add_subtitles.py --emit-ass-only --emphasis "<kicker phrases>"`, burned into the corresponding `[vk]` branch BEFORE concat. Per-scene burn-in (rather than one ASS over concat) keeps timings local and trivially correct.

**Music** — preserve the opening asset's own embedded audio and do not layer a second track over it. Sound generates an upbeat comedic instrumental for the CTA only. Dialogue remains silent except for speech/location ambience. Editor pre-builds `build/music-timed.wav` using the measured `OPEN_DUR`:

```bash
ffmpeg -y \
  -i bg-music.mp3 \
  -f lavfi -i "anullsrc=r=44100:cl=stereo" \
  -filter_complex "
    [1:a]atrim=start=0:end=${OPEN_DUR_PLUS_DLG_DUR},asetpts=PTS-STARTPTS[a_sil];
    [0:a]atrim=start=OFFSET:end=$((OFFSET+5)),asetpts=PTS-STARTPTS,volume=0.15,afade=t=out:st=4.0:d=1.0[a_cta];
    [a_sil][a_cta]concat=n=2:v=0:a=1[aout]
  " -map "[aout]" -c:a pcm_s16le build/music-timed.wav
```

Where `OFFSET` is the CTA-theme track offset, `OPEN_DUR` comes from `ffprobe` on the resolved opening asset, and `DLG_DUR` is the sum of the dialogue clips' played lengths. Then input [7] is `music-timed.wav` with simple `aresample=44100`; no fixed 2-second assumption.

**Fade** — fade-to-black on the last scene before CTA (`fade=t=out:st=PLAYED_DUR-1:d=1.0`, its played length after the H3 trim), and `afade=t=out` on music at TOTAL-1.

**Output upload** — after user approval, Manager uploads `final.mp4` using its canonical run-scoped object path.

---

## Voices

| Role | Speech route | Notes |
|---|---|---|
| Anchor (locked) | native → approved `fun-news` sample via Chatterbox → MiniMax | Fast, snappy news-anchor energy; assignment lives only in the resolved bible. |
| Reporter | native → approved `fun-news` sample via Chatterbox → MiniMax | Locked in this format when first used. |

Do not use ElevenLabs IDs or import a voice/sample from another format. The current Genshin and Star Trek bibles contain MiniMax preset names; if a format-owned approved sample is later added, record its URL explicitly before selecting Chatterbox.

---

## Story Bible

After explicit user confirmation on a missing-bible first run, create `games/{GAME_TAG}/fun-news_story_bible.json`:

```json
{
  "series_id": "fun-news-{GAME_TAG}",
  "game_tag": "{GAME_TAG}",
  "title": "{Game} Lore Newsflash",
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
  "voice_mapping": {
    "anchor": "",
    "reporters": {}
  },
  "reporter_pool": [
    {"character_name": "", "display_name": "", "voice": "", "stability": 0.55, "tone_signature": "...", "supabase_avatar_url": "", "last_seen_episode": null}
  ],
  "style_tone": "ironic|satirical|absurd|dry-deadpan",
  "topic_rotation": {
    "recent_topic_tags": [],
    "recent_canon_facts": [],
    "recent_satire_angles": [],
    "recent_reporters": [],
    "recent_hooks": [],
    "recent_reporter_angles": [],
    "anchor_joke_types": [],
    "recent_locations": [],
    "banned_combos": [],
    "cooldown_episodes": 5
  },
  "episode_summaries": [],
  "hook_url": "",
  "opener_url": "",
  "cta_url": ""
}
```

**Field formats for `topic_rotation` objects:**
- `recent_hooks` entries: `{"text": "headline string", "type": "semantic-slug"}` — hook type describes the JOKE FRAME, not topic. Generic types: `regulatory-bureaucratic`, `mock-academic-study`, `economic-crash-satire`, `institutional-self-contradiction`, `anniversary-absurdism`, `civic-protest-absurdism`, `government-agency-reaction`, `bureaucratic-monster-absurdism`, `institutional-rebranding-satire`. Game-specific types defined in each bible.
- `recent_reporter_angles` entries: `{"reporter": "Display Name", "angle_type": "slug"}` — type describes HOW the reporter delivers the joke, not what about. Defined per-game based on character personality.
- `anchor_joke_types` entries: plain strings, FIFO 5. Defined per-game. Describes which anchor running-bit was used this episode.

**FIFO 5** on `episode_summaries` — keep last 5, drop older. Append per episode only after the user explicitly approves the presented final video:

```json
{
  "episode": N,
  "date": "YYYY-MM-DD",
  "anchor": "Q",
  "reporters": ["Spock", "Seven of Nine"],
  "structure": "5 scenes — anchor intro → reporter 1 → anchor reaction → reporter 2 → anchor outro",
  "news_items": [{"index": 1, "headline": "...", "reporter": "..."}, ...],
  "topic_tags": [...],
  "final_url": "...",
  "duration_sec": 45.6
}
```

**Anti-repetition:** before Phase 1, manager checks `recent_topic_tags`, `recent_canon_facts`, `recent_satire_angles`, `recent_reporters`, `recent_hooks`, `recent_reporter_angles`, `anchor_joke_types`, `recent_locations`, and `banned_combos`; the scenarist's research.json must not collide.

**Story Bible update (Manager, only after explicit final user approval):**

Extract from `research.json` and `storyboard.json`, then update `topic_rotation`:

1. `news_items[].satire_angle` → append each to `recent_satire_angles`; trim to last **10** items (FIFO, 2 per episode × 5 episodes).
2. `episode_summary.reporters` → append each to `recent_reporters`; trim to last **6** items (FIFO, 2 per episode × 3 episodes).
3. `news_items[].headline` + `news_items[].hook_type` → append each as `{"text": headline, "type": hook_type}` to `recent_hooks`; trim to last **10** items (FIFO).
4. `news_items[].topic_tags` → extend `recent_topic_tags`; trim to last 5 episodes' worth.
5. Resolved canon facts used this episode → append each to `recent_canon_facts`; trim to last **5** items (FIFO).
6. `news_items[].location` → append each to `recent_locations`; trim to last **6** items (FIFO, 2 per episode × 3 episodes).
7. For each reporter selected: set `reporter_pool[].last_seen_episode = current episode number`.
8. `news_items[].reporter` + `news_items[].reporter_angle_type` → append each as `{"reporter": name, "angle_type": type}` to `recent_reporter_angles`; trim to last **6** items (FIFO, 2 per episode × 3 episodes).
9. Anchor bit used this episode → append to `anchor_joke_types`; trim to last **5** items (FIFO).

**No loop management** (this is not serial — each episode is standalone).

---

## Anti-repetition check

Before Phase 3, manager validates:

- [ ] None of `news_items[].canon_fact_index` resolves to a fact in `recent_canon_facts`.
- [ ] None of `topic_tags` overlap with `recent_topic_tags` (last 5 episodes).
- [ ] `satire_angle`: neither news item's angle appears 3+ times consecutively in the tail of `recent_satire_angles`.
- [ ] Reporter rotation: at least 1 reporter differs from those in the last episode (`recent_reporters[-2:]`). Prefer reporters with the lowest `last_seen_episode`.
- [ ] Hooks (text): no headline shares a dominant keyword with any `recent_hooks[].text`.
- [ ] Hooks (type): `news_items[].hook_type` does not repeat the same type 2+ times consecutively in `recent_hooks[].type` tail.
- [ ] Reporter angles: no `{reporter, angle_type}` pair in this episode matches the same pair in `recent_reporter_angles` — same reporter may return, but must use a different angle_type.
- [ ] Anchor bit: `anchor_joke_types` proposed this episode not identical to the last entry in `anchor_joke_types`.
- [ ] Locations: neither `news_items[].location` matches any entry in `recent_locations` (last 3 episodes).
- [ ] Banned combos: no `{reporter, topic_tag}` or `{satire_angle, topic_tag}` pair matches an entry in `banned_combos`.

If a collision is found — scenarist regenerates research.json with cooldown applied.

---

## Storyboard JSON (template, 5 scenes)

```json
{
  "format": "fun-news",
  "show_name": "{Game} Lore Newsflash",
  "episode": 1,
  "game_tag": "{TAG}",
  "language": "en",
  "research": {"file": "research.json"},
  "visual_identity": {
    "characters": {
      "anchor":     {"name": "...", "character_description": "...", "image_url": "supabase://avatars/anchor.png"},
      "reporter_1": {"name": "...", "character_description": "...", "image_url": "supabase://refs/reporter-1-on-location.png"},
      "reporter_2": {"name": "...", "character_description": "...", "image_url": "supabase://refs/reporter-2-on-location.png"}
    },
    "environments": {
      "q_studio":          "news desk for anchor scenes",
      "reporter_1_location": "tied to news item #1",
      "reporter_2_location": "tied to news item #2"
    }
  },
  "voices": {
    "anchor":    {"route": "minimax", "voice": "{MINIMAX_PRESET}", "language_code": "en"},
    "reporter_1":{"route": "minimax", "voice": "{MINIMAX_PRESET}", "language_code": "en"},
    "reporter_2":{"route": "minimax", "voice": "{MINIMAX_PRESET}", "language_code": "en"}
  },
  "scenes": [
    {"index": 1, "role": "anchor",     "satire_angle": "hook-intro",       "tts": "Hi, I'm {Anchor} with {Show}. {Hook}. {R1 name} is on the line."},
    {"index": 2, "role": "reporter_1", "satire_angle": "dry-deadpan",      "news_item_index": 1, "tts": "...",
     "scene_ambient": {"label": "location-slug", "description": "...", "volume": 0.10}},
    {"index": 3, "role": "anchor",     "satire_angle": "sarcastic-handoff", "tts": "{Reaction} — {R2 name}, you're up."},
    {"index": 4, "role": "reporter_2", "satire_angle": "clinical-absurdism", "news_item_index": 2, "tts": "...",
     "scene_ambient": {"label": "location-slug", "description": "...", "volume": 0.10}},
    {"index": 5, "role": "anchor",     "satire_angle": "satirical-wrap",   "tts": "..."}
  ],
  "subtitles": {"method": "ass-emit-only", "word_highlight": true, "emphasis": {"scene_1": "...", "scene_2": "...", "scene_3": "...", "scene_4": "...", "scene_5": "..."}, "atempo": 1.0},
  "speedup": 1.0,
  "music": {"mood": "energetic|comedic|fun", "volume": 0.15},
  "opening": {"kind": "hook|opener", "url": "{resolved hook_url || opener_url}", "duration_sec": 0},
  "cta":    {"url": "supabase://branding/cta.mp4"}
}
```

---

## Budget

**Per-second pricing (from `budgets.md`):**
- NB2 image: $0.08
- H3 Max Turbo lip-sync: **$0.04/s of the returned clip length** (≈ the TTS length; NOT per clip — this trips most cost estimates)
- Kling Avatar v2 Standard (replaced; the Test 12 baseline): $0.056/s of input audio duration
- Routed speech generation: provider-dependent

**Per-episode breakdown (steady-state, prep already in Supabase):**

| Item | Cost | Notes |
|---|---|---|
| Opener (Supabase) | $0 | one-time prep, see below |
| CTA (Supabase) | $0 | one-time prep |
| Anchor avatar (Supabase) | $0 | one-time prep |
| Reporter base avatars (Supabase) | $0 | one-time per reporter joining pool |
| Reporter **on-location** edits per episode | $0.16 | 2 × NB2 edit, scene-specific bg |
| Routed speech generation (5 lines, ~38s audio) | provider-dependent | |
| H3 Max Turbo lip-sync (5 scenes × $0.04/s ≈ 50s returned) | ~$2.00 | dominant cost (Kling Avatar v2: ~$2.80) |
| **Typical episode 2+** | **~$2.46** | under hard cap |

**Test 12 (Oct 2026, Kling Avatar v2 baseline → H3 lip-sync):** $2.40 → $1.91 per whole video (20.4% saved); the five clips $1.89 → $1.40.

**Pilot (episode 1) overhead — one-time prep:**

| Item | Cost |
|---|---|
| NB2 anchor sheet | $0.08 |
| NB2 anchor avatar edit | $0.08 |
| NB2 opener title image (assume 1 iteration) | $0.08 |
| Kling I2V opener 5s (no audio) → trim to 2s | $0.42 |
| NB2 base avatars for first 2 reporters (if not in Supabase) | $0.32 |
| **One-time prep** | **~$0.98** |

**Realistic pilot total** (prep + first episode): ~**$3.45** if everything works first try.

**Iteration tax (what actually happens on pilots):**

| Reason | Typical hit |
|---|---|
| User rejects 1 NB2 result (opener, anchor, reporter style) | +$0.08–$0.16 per regen |
| Texts trimmed mid-flight → re-TTS | +$0.30 |
| User wants on-location bg after first render → re-render the lip-sync clips | +$1.00–$1.45 |
| Off-by-one or label mistake in scene/job mapping → re-render wrong scene | +$0.35–$0.70 |

These are historical cost risks, not permission to continue past the cap. A technical failure gets one same-provider retry; a second failure or projected cap breach stops the video with an error.

**Limits**

- **Hard cap: $4.50** (raised from $4 after pilot empirical data — the Kling Avatar-era typical $3.26 was too close to $4 to absorb 1 retry).
- **Soft stop: $4.00** — review before continuing.
- Pilots: record approved one-time prep separately; never write an overrun into the bible before explicit final user approval.

---

## Output files

```
${OUTPUT_DIR}/
├── research.json
├── storyboard.json
├── scenes/
│   ├── scene-1/    # anchor intro
│   │   ├── scene-1.mp3           # TTS
│   │   └── scene-1.mp4           # H3 lip-sync clip as returned (no -fast.mp4, no speedup; the Editor applies the H3 trim)
│   ├── scene-2/    # reporter 1 on-location
│   ├── scene-3/    # anchor reaction
│   ├── scene-4/    # reporter 2 on-location
│   └── scene-5/    # anchor outro
├── build/          # ffmpeg intermediates, ASS files (per editor.md workspace rule)
│   ├── scene-1.ass ... scene-5.ass
│   ├── opener-raw.mp4
│   ├── cta-raw.mp4
│   ├── bg-music.mp3
│   └── final.tmp.mp4
└── final.mp4       # only deliverable in OUTPUT_DIR root
```

---

## Role briefs

### Scenarist
- **5 dialogue scenes** (opener/CTA are pre-built — not in storyboard). Structure: anchor intro → reporter 1 → anchor reaction → reporter 2 → anchor outro.
- Fictional headlines derived from canon lore (no real patch notes).
- Word budget: anchor intro 15–20, **reporter max 18 (hard cap)**, anchor reaction 5–10, **reporter max 18 (hard cap)**, anchor outro 15–20.
- **Hook-first intro** — do NOT tease item contents in scene 1 (spoiler). Tease the brand/show, not the news.
- Anchor reaction (scene 3) is sarcastic/dismissive — NOT a recap of item 1.
- Mandatory by-name handoffs. Reporter handoff is single-word: `"{Anchor name}?"`
- `satire_angle` per scene; reporter scenes 2 and 4 must differ.
- Anti-repetition vs story bible `topic_rotation`.
- `research.json.news_items[].location` must be populated — used by Storyboarder for on-location bg generation.
- `research.json.news_items[].kicker_phrases` — used by Sound for ASS word-highlight.
- **`scene_ambient` (MANDATORY for reporter scenes 2 and 4):** every on-location reporter scene must include a `scene_ambient` block:
  ```json
  "scene_ambient": {
    "label": "location-slug",
    "description": "Brief ambient description — e.g. 'Market crowd chatter, distant cart wheels, seagull calls, Liyue harbor wind'. No music. No clear speech.",
    "volume": 0.10
  }
  ```
  The ambient description must match the **specific location** of the news item (not a generic outdoor sound). Editor mixes this at `volume` under the TTS track.
- **`subtitles.emphasis.scene_K` length cap: ≤14 characters per phrase (UPPERCASE on Helvetica Bold 96px overflows the 1080-wide frame above that).** Prefer punchy short kickers (`"COOKED"`, `"NO CAP"`, `"73%"`, `"BHLF"`, `"SKILL ISSUE"`). For longer concepts, trim to the key word or split into two emphasis entries. See `rules/roles/scenarist.md` § `subtitle_emphasis` for full word-budget rules.
- General rules — `rules/roles/scenarist.md`.

### Storyboarder
- Anchor avatar — pulled from Supabase, do NOT regenerate.
- Reporter base avatars — pulled from Supabase by `character_name` tag; generate sheet+ref only for brand-new reporters joining the pool.
- **Per-episode on-location backgrounds (MANDATORY)** — NB2 edit using reporter base ref as `image_urls[0]`, with the news item's `location` in the prompt. The background must visually reflect the **specific news topic**: if the story is about dragons, include dragons/fire/scorched stone in the background; if about The Wall, show ice and blizzard. Use the full location description from `research.json news_items[].location` (not just the region name). Apply the game's house-style from the resolved style chain (game config `prompt_prefix` / story bible `style_tags`) verbatim, and derive any style negatives from it so the on-location edit stays on-brand rather than drifting to the video model's prior.
- **Reporters always hold a broadcast handheld microphone (MANDATORY)** — every on-location reporter image must include `"holding a broadcast handheld microphone in one hand"` in the NB2 prompt. No exceptions. This is the visual identity of the format.
- 9:16 (1080×1920) all images, frontal/three-quarter, teeth visible for lipsync.
- Upload per-episode on-location images to the Manager-provided current-run episode namespace.
- General rules — `rules/roles/storyboarder.md`.

### Animator
- **ONLY H3 lip-sync on H3 Max Turbo** (`minimax.h3max.turbo.i2v`; `rules/roles/animator.md` §2a "H3 lip-sync" and "Talking-head prompt"), one `tools/kling_runner.py` job per dialogue scene, all 5 scenes. Kling Avatar v2 is forbidden (the replaced route); never a plain clip on H3 Max Turbo, never lip-sync on H3 Max, no still.
- Before each job, run the pre-flight curl check on `tts_url` and `scene_image_url` (both 200; otherwise STOP and return to Manager). Both are Supabase permanent URLs (no fal.ai temp).
- **Payload — exactly these seven fields (the Test 12 jobs):** `prompt`, `image_url` = `scene_image_url`, `target_audio_url` = `tts_url`, numeric `duration` = the TTS length rounded up to 0.1 s (`math.ceil(round(d*10,6))/10`, equal to the `duration_sec` Sound wrote), `resolution: "768P"`, `prompt_expansion_mode: "disabled"`, `seed: 20261021`. `expect`: `duration_seconds` = that `duration`, `duration_tolerance_seconds: 0.8`, `audio: "required"`, `min_bytes: 100000`, `min_width: 600`, `min_height: 1000`, `orientation: "portrait"`. Template: `tools/examples/minimax-h3-max-turbo-talking-head.job.json`.
- A scene whose TTS is longer than 15 s (H3's maximum) is not submitted: return it to be shortened.
- **Prompt (≤512 UTF-8 bytes):** the speaker by look, position and framing (from the storyboard and the scene image), the expression and at most one small gesture; no gaze or head lock (`unblinking`, `eyes locked on`, `steady eye contact with camera`, `facing the camera head-on`, `holds still`, `stares`). Then the anchor/reporter gaze sentence — the anchor and both reporters address the viewer: `He looks into the camera like a TV news presenter, blinking naturally, with small relaxed head movements and changing expression between phrases; no frozen stare.` (`She` for a female speaker). End with `<Speaker> speaks the line "<line>" with lips in sync with the audio.` (`<line>` = the scene's `tts` verbatim). Over 512 bytes: shorten the descriptors first and keep the line whole; only if still too long, shorten the quoted line to its first sentence followed by `…` and report it. No music/voice clause. Example (Test 12, anchor scene 1, 512 bytes):
  ```
  Q, a graying man in a red-and-black Starfleet uniform, sits behind the news desk, frontal medium close-up, desk mic in front. Smug smirk, one eyebrow raised; a small head tilt on the greeting. He looks into the camera like a TV news presenter, blinking naturally, with small relaxed head movements and changing expression between phrases; no frozen stare. Q speaks the line "Hi, I'm Q with Star Trek Lore Newsflash — where the future is always my fault. Spock is on the line." with lips in sync with the audio.
  ```
- Write-back: `scene_video_kind: "i2v"`, `scene_video_route: "minimax.h3max.turbo.i2v"`, `scene_video_audio: "native"`, `scene_video_lipsync: true`, `motion_prompt` = the prompt. Do not trim, speed up, pre-encode or remux the clip: the Editor applies the H3 trim.
- Retry a technically failed job once with the same route/settings, then STOP; no switch to Kling Avatar, H3 Max, another provider or a still.
- Explicit per-scene mapping: one job per scene, `job_id` and `output_path` derived from the scene index (no bash off-by-one — see the pilot notes).
- **Debug mode:** list the 5 planned clips with per-clip cost (requested `duration` × $0.04/s) before the paid batch; a lip-sync clip of about 7.5 s or longer is above the $0.30 confirm threshold.
- Cost: $0.04/s on the returned length, on the H3 lip-sync cost line.
- General rules — `rules/roles/animator.md`.

### Sound
- Generate speech for each of the 5 dialogue scenes via intentional native speech → approved sample owned by this `fun-news` bible through Chatterbox → otherwise MiniMax.
- Retry the same route/settings once, then stop; never switch provider or use another format's sample/assignment.
- **Speech speed MUST be 1.0 (or omitted).** If natural speech exceeds the word-budget window, shorten the text; no Editor-side speedup exists.
- Replace periods with commas/em-dashes in anchor lines where natural — periods bloat duration via TTS pause inflation.
- Upload each mp3 to the Manager-provided current-run episode namespace as the scene's `tts_url` before Phase 4 (the Animator sends it as the lip-sync `target_audio_url`), and write `tts_duration_sec` and `duration_sec` = the TTS length rounded up to 0.1 s on every scene (`rules/roles/sound.md` §5b). A line whose TTS is longer than 15 s is not uploaded: STOP and return it to be shortened.
- ASS subtitles — the one universal style, generated by Editor via whisper from `build/voice-final.wav` (editor.md §6). No `--atempo`/`--emphasis`. One `build/subs.ass` for the whole video.
- **Location ambient SFX (MANDATORY for scenes 2 and 4):** read `scene_ambient.description` and `scene_ambient.volume`, generate it with the configured SFX provider, and mix it under speech. Retry the same request once on failure, then stop; do not switch provider or use a local/another-format fallback.
- Music: generate the CTA track via MiniMax with an upbeat comedic news `style` prompt. Preserve the opening asset's embedded audio and keep dialogue free of background music. Write `music.start_offset_sec` into storyboard.json; default 0.
- General rules — `rules/roles/sound.md`.

### Editor
- Canonical single-pass `filter_complex` (see `rules/roles/editor.md` §0). One ffmpeg call, no intermediate re-encodes.
- Inputs: 5 scene mp4s + resolved opening asset (`hook_url || opener_url`) + CTA + bg-music; optional GLN PNG only for exact `star-trek-timelines + fun-news`.
- Every scene is an H3 lip-sync clip (`scene_video_lipsync: true`): **H3 trim** of video and audio to `duration_sec` first in each scene branch (play whole when the clip is shorter), never Kling Avatar's TTS trim. The clip's own audio is the scene's speech: never lay `scene-K.mp3` over it again.
- **Per-scene `apad=whole_dur=<played_dur>` on audio** — non-negotiable. Without it, audio leads video by 3+ seconds by scene 5.
- `build/voice-final.wav` for subtitle timing is extracted from the lip-sync clips' own audio (`rules/roles/editor.md` §6.1, multi-voice).
- Per-scene ASS burn-in inside each `[vk]` branch BEFORE concat.
- `adelay=OPEN_DUR_MS|OPEN_DUR_MS` on concat dialogue audio, where `OPEN_DUR_MS` is measured from the resolved opening asset; never hardcode 2 seconds.
- Fade-out on scene-5 video (last 1s before CTA) + afade-out on music.
- `-t TOTAL_DUR` mandatory to cap on amix duration=longest.
- Atomic finalize: write to `build/final.tmp.mp4`, ffprobe-validate, `mv` to `final.mp4`.
- Do not upload the final before review; Manager uploads it after explicit user approval.
- General rules — `rules/roles/editor.md`.

---

## Validation

- [ ] `research.json` with 2–3 fictional items, each tied to a real canon fact + `location` + `kicker_phrases`.
- [ ] Anchor matches `anchor.character_name` from story bible (locked).
- [ ] Reporters chosen by topic; **on-location backgrounds generated this episode** (not bare base avatars).
- [ ] On-location refs uploaded to Supabase (so debug runs and re-renders can refer to them).
- [ ] Exactly one opening asset resolved from the bible: non-empty `hook_url`, otherwise `opener_url`; CTA downloaded from Supabase.
- [ ] Reporter scenes 2 and 4 have `scene_ambient` block with location-specific description and volume 0.08–0.12.
- [ ] All TTS generated at `speed=1.0` (no compensatory TTS speedup).
- [ ] All 5 dialogue scenes — H3 lip-sync on `minimax.h3max.turbo.i2v` with the exact seven-field payload (`target_audio_url` = `tts_url`, `duration` = TTS rounded up to 0.1 s, `seed: 20261021`), the anchor/reporter gaze sentence and the closing lip-sync sentence (≤512 bytes); `scene_video_audio: "native"`, `scene_video_lipsync: true`; no Kling Avatar clip.
- [ ] Every scene has `tts_url`, `tts_duration_sec` ≤ 15 and `duration_sec` = the TTS length rounded up to 0.1 s.
- [ ] 5-scene structure: anchor → R1 → anchor → R2 → anchor.
- [ ] Adjacent reporter scenes (2 and 4) have different `satire_angle`.
- [ ] H3 trim to `duration_sec` and per-scene `apad=whole_dur=<played_dur>` applied in Editor's filter_complex; no `scene-K.mp3` laid over a lip-sync clip.
- [ ] ASS subtitles per-scene with word-highlight on kicker phrases.
- [ ] By-name handoffs in every scene transition.
- [ ] No collision with `recent_topic_tags` / `recent_canon_facts` (last 5 episodes).
- [ ] Speech routes come only from this `fun-news` bible and use native → format-owned Chatterbox sample → otherwise MiniMax.
- [ ] GLN/channel bug input and overlay exist only for the exact pair `GAME_TAG=star-trek-timelines` + `FORMAT=fun-news`, sourced from that resolved bible's `channel_branding.channel_bug_url`; Genshin and every other pair omit it entirely.
- [ ] Final: 1080×1920, 30fps, ≤50s total using measured opening duration, budget ≤ $4.50 hard cap.

---

## Anti-patterns

- ❌ Generic/non-game-specific opener — opener must be visually styled to the game world (dark fantasy, sci-fi, etc.), not a generic news broadcast card.
- ❌ Background music during dialogue scenes — music plays ONLY at opener (~2s) and CTA (~5s). Use `music-timed.wav` with real silence (anullsrc); do NOT use `volume:enable` filter (FFmpeg passthrough bug).
- ❌ Layering CTA music over the opening asset or letting it play under dialogue — preserve opening audio, then real silence, then CTA music.
- ❌ Mic flag without show name — reporter mics must have the show name on the flag (e.g. "GoT Daily"). Generic or blank flags break the TV identity.
- ❌ Anchor studio without show signage — anchor desk must include a visible nameplate or lower-third sign with the show name.
- ❌ Generic reporter background unrelated to news topic — if Varys is covering a dragon fire story, the background must show dragons/fire, not a bare stone corridor. Background must telegraph the topic.
- ❌ Using real patch notes / live web search results as news items (that's `news.md`, not Fun News).
- ❌ Changing the anchor between episodes (anchor is locked per game).
- ❌ Generating opener / CTA per episode — they are one-time-per-game assets pulled from Supabase.
- ❌ Bare character refs as reporter `image_url` — reporters must be **on-location** matching their news item. A reporter speaking about a closed conference shouldn't be standing on a starship bridge.
- ❌ Reporter refs whose style conflicts with the game's resolved style chain — the lip-sync clip mirrors the input style. Use refs matching the game's house-style (`style_tags` / `prompt_prefix`) and derive on-location-edit style negatives from that target.
- ❌ Anchor intro that teases item contents — kills the surprise. Hook the brand, not the news.
- ❌ Anchor reaction scene that recaps the previous item — make it a dry put-down (`"Astonishing, as expected — {Next reporter}, you're up."`).
- ❌ Daniel voice with `style: 0.8` / `stability: 0.2` — theatrical, slow. Use `stability: 0.55` + no `style`. Validated on pilot.
- ❌ Too many periods in anchor lines — each `.` adds ~0.5s of TTS pause. Use commas and em-dashes.
- ❌ Subtitles on a concatenated video — burn ASS **per-scene** inside the single-pass filter_complex.
- ❌ Any atempo speedup on dialogue scenes — Fun News uses **1.0× (no speedup)**. Characters must sound natural. atempo=1.3 was tried in EP1–2 (Kling Avatar era) and sounds unnatural; it also caused AV sync drift with Kling Avatar v2's trailing-silence tail.
- ❌ fal.ai temp URLs as `image_url` / `target_audio_url` — only Supabase permanent URLs.
- ❌ Kling Avatar v2 (`fal-ai/kling-video/ai-avatar/*`) for any fun-news scene — replaced by H3 lip-sync after Test 12; never a fallback.
- ❌ A plain clip on H3 Max Turbo, a lip-sync clip on H3 Max, or a still for a dialogue scene.
- ❌ Gaze- or head-locking phrases in a lip-sync prompt (`unblinking`, `eyes locked on`, `steady eye contact with camera`, `facing the camera head-on`, `holds still`, `stares`) — H3 then stares into the lens; use the anchor/reporter gaze sentence.
- ❌ A `seed` other than `20261021`, or a missing one.
- ❌ ElevenLabs speech, provider switching after retry, or another format's voice/sample.
- ❌ Repeating a canon fact or topic_tag used in the last 5 episodes.
- ❌ Same `satire_angle` on adjacent reporter scenes.
- ❌ Lip-sync cost estimate based on "N × 5s clip" — **WRONG**. H3 lip-sync is billed per **second of the returned clip** (≈ the TTS length): a 12.4 s line returns 12.96 s ≈ $0.52, not $0.21. Compute from the word-budget table. (Kling Avatar v2, the replaced route, was billed per second of input audio: a 17 s mp3 cost $0.95.)
- ❌ Pre-encoding `-fast.mp4` per scene — no speedup is applied; the lip-sync clip is used as returned.
- ❌ Trimming, speeding up or remuxing a lip-sync clip in the Animator, or Kling Avatar's TTS trim (`tts_dur + 0.2s`) in the Editor — lip-sync clips get only the Editor's H3 trim to `duration_sec` (a shorter clip plays whole).
- ❌ Laying `scene-K.mp3` over a lip-sync clip — its soundtrack already is that TTS, so the line plays twice.
- ❌ Audio concat **without** per-scene `apad=whole_dur=<played_dur>` — clip audio and video lengths differ slightly; without `apad` the drift stacks across all 5 scenes (up to 4s by the outro).
- ❌ Bash off-by-one in scene-id/job arrays — prefer `declare -a IDS; IDS[N]=...` indexing or named structs over `IDS=("" "a" "b")` + `IDS[$((N-1))]`.
- ❌ `-shortest` in FFmpeg (use `apad` and `-t TOTAL_DUR`).
- ❌ Reporter dialogue over 18 words — every comma, period, and dash adds 0.3–0.8s of TTS dead air; deliberate character voices (Klingon, Vulcan) amplify this. Keep reporter lines punchy: 1–2 short sentences + kicker word. HARD CAP: 18 words per reporter scene.
- ❌ Do NOT generate gloomy/dark music for satirical news — the `style` prompt must be clearly upbeat/comedic; a somber underscore tanks the ironic tone (Genshin EP1 pilot).
- ❌ No location ambient SFX on reporter scenes — every on-location reporter scene must have a `scene_ambient` block describing the background noise of the location (market crowd, wind, city bustle, nature, etc.) at volume 0.08–0.12. Silence on location feels unnatural. See Scenarist brief below.
- ❌ TTS `speed` parameter > 1.0 — always generate TTS at `speed=1.0` (or omit the field). There is no Editor-side speedup to "absorb" a fast TTS. If a reporter's line sounds too long, shorten the text.

---

## Pilot notes (for future format maintainers)

The Star Trek Timelines episode 1 pilot (2026-05-26) burned $8.13 vs the original budget estimate of $1.40–$1.50. Root causes:

1. **Cost-model error in original spec** — estimated Avatar v2 as 4 × 5s clips ($1.12), reality is 50s audio × $0.056 = $2.80. Spec budget table now reflects per-audio-second pricing.
2. **Mid-flight requirement changes** — added on-location backgrounds (+$1.60), added 5th scene (+$0.21), trimmed/rewrote texts (+$0.40 in re-TTS). Future episodes assume on-location + 5-scene from the start.
3. **fal.ai result GC** — Avatar v2 results expire after ~5–30 min if not downloaded; one scene was lost ($0.88 to resubmit). Animator role brief now explicitly calls out prompt download.
4. **Off-by-one in download loop** — `IDS=("" "a" "b" ...)` + `IDS[$((N-1))]` shifted scene labels, requiring a re-investigation pass. Anti-pattern documented above.
5. **Lipsync drift from apad omission** — first Editor pass produced 3s audio lead; fixed with per-scene `apad=whole_dur=<trimmed_video_dur>`. Anti-pattern documented.

Steady-state episode 2 forecast (with prep in Supabase, on-location built into pipeline from start, no rework): **~$3.26**, under $4.50 hard cap.

These notes date from the Kling Avatar v2 era. Since Test 12 (Oct 2026) the clips run on H3 lip-sync through `tools/kling_runner.py` (which downloads each result itself), and a typical episode is ~$2.46.
