---
ready_to_post: yes
subtitles: true
overlays: false
---

# Format "Streettalk" — Vox-pop street interview from the universe's «street»

> **Single video route — H3 lip-sync on MiniMax H3 Max Turbo** (`minimax.h3max.turbo.i2v` with the scene's TTS as `target_audio_url`; it replaced Kling Avatar v2 Standard after Test 12, and Kling Avatar is forbidden here). Opener and CTA pre-built from Supabase. Reporter (anchor) locked per game in story bible. Interviewees variable, chosen by topic. Tone — ironic / satirical / absurd.

This file is the **playbook**: when to use, pipeline, role briefs. Craft rules — in `rules/roles/*.md`.

**Distinct from:**
- `news.md` — anchored newsroom with real game-news headlines. Streettalk has NO studio, ONLY street.
- `fun-news.md` — anchored newsroom with fictional headlines; anchor + 1-2 reporters in studio + on-location B-roll. Streettalk has NO anchor-in-studio: one reporter on the street + 3 vox-pop interviewees.
- `what-if-real-life.md` — character-in-mundane-job sketch. Streettalk is a recurring news format, not a one-shot sketch.

---

## When to use

Keywords: "streettalk", "street talk", "street-talk", "vox pop", "vox-pop", "уличное интервью", "стрит-ток", "прохожие", "мнения прохожих", "опрос на улице".

---

## Concept

- **1 permanent reporter** (locked per game in story bible) + **3 interviewees** per episode (variable, chosen by topic from Supabase or generated)
- **1 absurd question** per episode — reporter asks, 3 passers-by react with different angles
- **Only H3 lip-sync on H3 Max Turbo** (`minimax.h3max.turbo.i2v`, `rules/roles/animator.md` §2a "H3 lip-sync") + routed speech audio (lip-sync via `target_audio_url` = the scene's `tts_url`). Every dialogue scene is one H3 lip-sync clip; no plain clip, no still, no Kling Avatar clip
- **Opener and CTA — pre-built mp4 from Supabase**, not regenerated per episode
- **Tone:** absurd / satirical / dry-deadpan / earnest-cluelessness — one angle per interviewee, must differ across the 3
- **Duration:** 30–45s after speedup (opener 2s + 5 dialogue scenes ~30-35s + CTA ~5s)
- **Budget:** up to $7.00 hard cap for pilot; ~$3.00 steady-state EP2+ target (typical estimate ~$2.24; Test 12: $2.02 per video)
- **Frame format:** 9:16 (1080×1920)

### Models

- **Image:** NB2 (per-episode on-location edits for reporter + interviewees on the show's signature location)
- **Video:** H3 lip-sync on MiniMax H3 Max Turbo (`minimax.h3max.turbo.i2v`, $0.04/s of the returned clip length ≈ the TTS length). Kling Avatar v2 Standard ($0.056/s of input audio) is the replaced route (the Test 12 baseline) and is forbidden in this format
- **Audio:** intentional native speech → approved sample owned by this `streettalk` bible through Chatterbox → otherwise MiniMax

---

## Visual Identity & Branding (MANDATORY)

### Opener — game-specific, always required

Every streettalk episode must open with a **game-specific branded opener** (pre-built in Supabase, reused every episode). Rules:
- **Visual style** — matches the game's aesthetic exactly: if it's DS9, the opener looks like a DS9 newscast; if it's a fantasy game, the opener uses that world's visual language. NOT a generic "street interview" template.
- **Show name formula — `{GameName} Streettalk`** (MANDATORY). The show is named after the game, not a generic channel brand. Examples: "Genshin Streettalk", "Roblox Streettalk", "Pokémon Streettalk", "Star Trek Streettalk". Never use "GLN" in Streettalk; GLN belongs only to Star Trek Fun News.
  - The `{GameName}` is the short recognizable name from the game config (e.g., "Genshin", "Roblox", "WWE") — not the full legal title.
  - Story bible `title` field: `"{GameName} Streettalk — {Location}"` (e.g., "Genshin Streettalk — Mondstadt Plaza").
  - Storyboard `show_name` field: same formula.
- **Show name and location prominently displayed** — e.g. "Genshin Streettalk — Mondstadt Plaza". The card establishes both the show identity and the location.

### Opener music = CTA music (same theme, only at those two points)

The opener and the CTA/packshot share the **same musical theme** — light and fitting for the game's atmosphere. The music must feel like it belongs to the game world: a fantasy RPG gets something ethereal or adventurous; a fighting game gets something punchy; a city-builder gets something upbeat and urban. NOT a one-size-fits-all energetic track. Sound generates the track via MiniMax using a `style` prompt built from the game config's `music.mood` / atmosphere — see Sound brief. During all dialogue scenes: **no background music** (real silence). Only ambient SFX plays during dialogue (see Sound section). Music placement:
- t=0 → opener end (~2s): theme plays
- t=2s → CTA start: **silence** — dialogue + ambient SFX only
- CTA start → end (~5s): same theme reprises with fade-out

**Implementation (Editor):** build a `music-timed.wav` using `anullsrc` for the silence portion (same approach as fun-news). Do NOT use `volume:enable` filter (FFmpeg passthrough bug). Ambient SFX is a separate layer mixed at 0.15 throughout the dialogue; only the music track is gated.

### TV attributes (all scenes)

**Microphones:**
- Reporter always holds a **broadcast handheld microphone with the show's name on the mic flag** — the flag text is `storyboard.json → show_name` short form (e.g., "Genshin Streettalk", "Star Trek Streettalk"). NOT a generic channel logo, NOT GLN, NOT a blank flag.
- For interviewee scenes: reporter's mic is visible in the foreground from off-screen (standard vox-pop framing). The flag is still readable.
- Include in NB2 prompt: `"reporter holds broadcast mic with '{show_name_short}' on the mic flag"` (reporter scenes) or `"reporter's mic with '{show_name_short}' flag in foreground"` (interviewee scenes). `show_name_short` = `"{GameName} Streettalk"` (without the location suffix).

**Show signage:**
- The reporter intro/outro shot should include **visible show branding** in the environment: a street banner, marquee, or lower-third graphic establishing the show. This is optional for on-the-fly location shots but preferred for the opener-frame reference.

### Reporter/interviewee background matches question topic (MANDATORY)

On-location backgrounds must visually relate to the **specific question being asked**, not just the general location:
- Question about a Klingon honor dispute → at minimum one Klingon element visible in background, or signage referencing the dispute
- Question about dragon incidents → even on the Promenade, background extras or signage should hint at the dragon topic
- The viewer should be able to partially infer the topic from the background

**Storyboarder responsibility:** when generating on-location NB2 edits, inject topic-related visual elements into the background description — don't use the location ref as-is if the question has a more specific visual hook.

---

## Pipeline (strict order)

### Phase 0: Initialization (manager)

1. Read game config: `games/{GAME_TAG}/{GAME_TAG}.md`.
2. Resolve required `games/{GAME_TAG}/streettalk_story_bible.json`. If missing, STOP and ask whether the user wants it created; create it only after explicit confirmation.
3. Read Manager's prefiltered `SUPABASE_ASSETS_FILE`, containing only this `streettalk` format/series plus the separately resolved game CTA. Do not run a broad `game_tag` query:
   - **Opener** — record matching the story bible's `opener_url` (tag `streettalk` + `opener` + `video`). If missing → flag for Phase 2 prep (one-time cost ~$0.50).
   - **CTA** — record with tag `cta` + `video`.
   - **Reporter base avatar** — record matching `reporter.character_name`, tag `streettalk` + `avatar` + `reporter` → `.png`. If missing → Phase 2 generates (one-time per game).
   - **Location reference** — record matching `location.slug` (e.g. `bg-ds9-promenade`), tag `streettalk` + `location` → `.png`. If missing → Phase 2 generates.
   - **Interviewee base refs** — records matching interviewee names selected in Phase 1 (canonical or new); tags `streettalk` + `interviewee` + `character_name`.
4. **STOP** if CTA missing — must be uploaded in advance per game.
5. Reporter/location/opener missing — **expected on pilot**; Phase 2 generates them, manager logs `pilot_prep_cost`.

### Phase 1: Script (scenarist)

**No web research required** (streettalk is fictional satire, not real news). But check `episode_summaries` and `topic_rotation` in story bible — anti-repetition.

**Step 1.** Pick **1 question** (the «vox-pop ask») rooted in canon lore. The question must:
- be absurd-but-canon-plausible (e.g. "Why is Worf no longer fining people?", "Klingon opera через universal translator — деградация?")
- be UNIVERSAL enough that 3 different species/factions on the show's location have distinct stake in answering
- NOT collide with `recent_question_tags` (last 5 episodes)

**Step 2.** Pick **3 interviewees**, each a different angle:
- Different species/faction (e.g. Klingon + Bajoran + Ferengi; or Vulcan + Andorian + Tellarite)
- Different reaction tone — `dry-deadpan`, `absurd`, `earnest-cluelessness`, `satirical-takedown`, `meta-confused`
- Different relationship to the question (insider / outsider / hypocrite / bystander)
- At least one canon character (recognizable to the audience); the other two can be generic-NPC types from the world (named "Bajoran Civilian", "Ferengi Bartender", etc.) — these can become recurring side-characters if reused.

**Step 3.** Write 5 scenes:

| Scene | Role | Camera | Content |
|---|---|---|---|
| 1 | **Reporter intro** | Reporter on location, frontal medium close-up, holding show-branded mic | Hook-first: `"{Reporter} here on the {location} for {show_name_short}. Today's question: {QUESTION}. Let's find out."` (15–22 words, ~6-9s). `show_name_short` = e.g. "Genshin Streettalk", "Roblox Streettalk". |
| 2 | **Interviewee 1** | Interviewee on location, three-quarter medium close-up, reporter's mic visible in foreground | Reaction to question + signature line per interviewee's angle. (18–25 words, ~7-10s). |
| 3 | **Interviewee 2** | Different framing from scene 2 (closer, or different background slice of the location) | Different angle. (18–25 words, ~7-10s). |
| 4 | **Interviewee 3** | Different framing from scenes 2-3 — wider or with another extra in background blur | Different angle. (18–25 words, ~7-10s). |
| 5 | **Reporter outro** | Reporter on location, slightly wider than scene 1, fade-out last 1s before CTA | Ironic sign-off + signature catchphrase. (12–18 words, ~5-7s). Do NOT tease next episode (non-serial). |

**Total word budget:** ~85–110 words (~32–45s raw TTS, ~22–30s after 1.5× speedup — fast vox-pop pace).

**Title cards (lower-third drawtext, MANDATORY for vox-pop genre).** Each talking head gets a lower-third name-and-role card visible during the first 1.5-2.0s of their scene (after which it fades out so the face is unobstructed). This is standard cable-news / vox-pop convention — viewers see WHO is speaking. The reporter does NOT need to say their own name aloud (the title card covers it); they say the channel branding instead.

Scenarist populates `scenes[K].title_card`:

```json
{
  "name": "Jake Sisko",
  "subtitle": "{GameName} Streettalk Reporter",
  "show": true
}
```

`show: false` for scenes where no card is shown (e.g. the closing reporter outro where the viewer already knows him — convention is to title once at first appearance, not twice). For pilot: show=true on scenes 1-4, show=false on scene 5.

Editor renders via drawtext (see Editor brief).

**Punctuation tax** — each `.` adds ~0.5s TTS pause. Prefer commas / em-dashes for reporter pace. Interviewees can use full sentences (their pace is the joke).

**`subtitles.emphasis.scene_K`**: per scene pick 1-2 short kicker phrases (≤14 chars uppercase). Examples: `"NO FINES"`, `"73%"`, `"BLOODWINE"`, `"BAJORAN VIBES"`. Used by Sound for word-highlight in ASS.

**Anti-repetition check (manager runs before approving storyboard):**
- [ ] `question_tag` NOT in `recent_question_tags` (last 5 episodes).
- [ ] At least 2 of 3 interviewees NEW vs previous episode (don't re-run Quark+Worf+Garak twice).
- [ ] At least one species/faction NEW vs previous episode.
- [ ] Tone distribution (3 different angles in this episode).

### Phase 2: Characters and on-location backgrounds (storyboarder)

**Reporter** — read `reporter.character_name` from story bible:
- If `reporter.supabase_avatar_url` exists in story bible AND Supabase confirms — pull, do NOT regenerate.
- Otherwise (pilot): generate **character sheet** (NB2 text-to-image, 16:9 concept art, ~$0.08) + **avatar ref** (NB2 edit with sheet as ref, 9:16, frontal portrait, mic in hand, mouth slightly open for lipsync, ~$0.08). Upload both to Supabase via `queue/upload-asset.sh --kind character` + `--kind avatar`, tags `streettalk,reporter,{character-slug}`.

**Location reference** — read `location.slug` from story bible:
- If exists in Supabase — pull.
- Pilot: generate one **location ref** (NB2 9:16, the show's signature street/promenade, no characters, ~$0.08), upload as `--kind location --slug {location-slug}`, tags `streettalk,location,{location-slug}`.

**Opener (one-time prep, ~$0.50):**
If `opener_url` empty in story bible:
1. NB2 title card 9:16 (~$0.08): location background slightly blurred + huge centered "{GAME_NAME} STREETTALK" title text + small "{LOCATION_NAME}" subtitle. No GLN logo or channel bug. Style: game-specific tv-broadcast title card.
2. Kling I2V 5s **no audio** (~$0.42): subtle camera push-in, no characters, title-card animation.
3. Trim to 2s, upload via `--kind branding --name streettalk-opener`, tags `streettalk,opener,video,{game-tag}`.
4. Write the URL into run-local `proposed_bible_updates.opener_url`; Manager applies it to the exact story bible only after explicit final user approval.

**Per-episode interviewees:**
For each of 3 interviewees:
- If `character_name` has a ref owned by this exact Streettalk series/story bible — use it as the base and NB2-edit an on-location variant. A same-game ref from another format is treated as missing unless the user explicitly authorizes copying it. ~$0.08 per interviewee.
- If NEW character — generate sheet + on-location ref. ~$0.16 per interviewee. Upload base ref tagged `streettalk,interviewee,{slug}` for future reuse.

**Per-episode on-location edits (MANDATORY):**
For each of the 5 dialogue scenes generate a fresh NB2 edit using base avatar as `image_urls[0]`:

```
NB2 /edit with:
  image_urls: [character_base_avatar_url]
  prompt: "{character} on-location at {location_name},
           <resolved style_tags for this game/format — applied verbatim>,
           <anti-drift negatives derived from that style — e.g. the opposite render medium>,
           9:16 vertical, three-quarter medium close-up,
           reporter holds {GameName} Streettalk-branded microphone in foreground for reporter scenes,
           or mic visible in foreground from off-screen for interviewee scenes,
           mouth slightly open mid-speech for lipsync,
           professional broadcasting key light on face,
           background slightly out of focus showing {location_name} hints,
           NO on-screen text overlay, NO captions, NO LCARS UI"
```

Upload per-episode scene PNGs to the Manager-provided current-run episode namespace via `--kind episode-scene` (NOT registered in `game_assets`).

### Phase 3: Audio (sound)

Generate speech for each of the 5 scenes. Resolve each speaker in this order: native model audio when intentionally supported → Chatterbox only with an approved sample owned by this resolved `streettalk` story bible → otherwise MiniMax. Reporter and interviewee assignments come only from this format's `voice_mapping` / format-local defaults. Never read a sample or assignment from another format. On failure, retry once with the same route/settings, then STOP and report the error.

Upload each scene's mp3 as its `tts_url` before Phase 4 (the Animator sends it as the lip-sync `target_audio_url`) and write `tts_duration_sec` and `duration_sec` = the TTS length rounded up to 0.1 s on every scene (`rules/roles/sound.md` §5b). A line whose TTS is longer than 15 s is not uploaded: STOP and return it to be shortened.

Subtitles are NOT Sound's job. Editor generates the one universal ASS via whisper from `build/voice-final.wav` (editor.md §6). No `timings.json`.

**Ambient SFX (MANDATORY — silence is not OK for vox-pop):**

A street-interview clip with NO ambient = uncanny / fake — viewers register the absence instantly. Sound must generate ONE ambient SFX track (length ≈ total dialogue audio + 2s buffer) and write its URL into `storyboard.json → music.ambient_url`.

Generation via the configured SFX provider (`fal-ai/elevenlabs/sound-effects`): `prompt: <story bible's location.ambient_prompt>`, `duration_seconds: 22` (max). For >22s coverage, generate 2 clips and concat. Retry one failed request once with the same provider/settings; if it fails again, STOP and report the error. Do not switch providers or use a local fallback.

Save raw output to `build/ambient.mp3`, upload to the Manager-provided current-run episode namespace, and write the URL into storyboard.

**Ambient prompt seed (per-game, from story bible's `location.ambient_prompt`).** Example for DS9 promenade: `"DS9 Promenade ambient: low chatter of multiple alien species voices in unintelligible languages, soft Bajoran-Cardassian station hum, distant footsteps on metal walkway, occasional door-chime and PADD beeps, no music no melody, urban marketplace texture with indoor reverb, layered crowd murmur, no clear English words"`.

**Music generation (opener + CTA theme only):**
Generated by Sound via MiniMax (instrumental, see `rules/roles/sound.md` §6) based on the game's atmosphere. Build the `style` prompt like this:
1. Read `games/{GAME_TAG}/{GAME_TAG}.md` → `music.mood` field (e.g., `ethereal`, `epic`, `fun`, `energetic`).
2. Build the MiniMax `style` prompt from that mood plus the game's atmosphere — a game-appropriate theme.
3. If the game has no `music.mood`: use a neutral instrumental prompt fitting the game's setting.
4. The track must feel like it belongs to the game world — a fantasy RPG should not open with trap phonk; a fighting game should not open with melancholic piano.

The chosen track plays **only during opener (~2s) and CTA (~5s)**; during dialogue only ambient SFX plays. Write `music.start_offset_sec` into storyboard.json. Volume in music-timed.wav: **`0.06`** (vox-pop is dialogue + ambient dominant; music is a brief atmospheric pulse at the bookends only, not a continuous underscore).

**Audio layer volume contract** (Editor consumes):
- Dialogue (the lip-sync clips' own audio, which is the scene TTS): **1.0**
- Ambient SFX: **0.15** (subtle crowd texture under dialogue + music — tuned 2026-05-29 pilot, original 0.25 was too dominant; lowered to let music breathe and voices stay primary)
- BG music: **0.06** (subliminal pulse, NOT 0.15)

### Phase 4: Animation (animator) — H3 lip-sync on H3 Max Turbo only

For each of the 5 scenes:
1. **Sound's mp3** is already uploaded to the Manager-provided current-run episode namespace as the scene's `tts_url`, with `tts_duration_sec` and the rounded-up `duration_sec` (Phase 3).
2. **H3 lip-sync** (`minimax.h3max.turbo.i2v`, `rules/roles/animator.md` §2a "H3 lip-sync" and "Talking-head prompt"), one `tools/kling_runner.py` job per scene:
   - `image_url` = the scene's on-location PNG from Supabase (`scene_image_url`, the same still the Kling Avatar route used)
   - `target_audio_url` = the scene's `tts_url` (NOT a fal.ai temp URL)
   - `duration` = `duration_sec` (the TTS length rounded up to 0.1 s), `seed: 20261021`, and the role's lip-sync prompt (Animator brief: the reporter looks into the camera, an interviewee looks at the off-screen reporter)
3. The runner downloads, validates and uploads each clip; the Animator does not trim, speed up or remux it.
4. **Per-scene speedup applied in Editor's filter_complex** — NOT pre-encoded. Default 1.5× (TikTok vox-pop pace). Per-scene override via `storyboard.json → scenes[K].speedup`. Pilot decision 2026-05-29: most scenes 1.5×, but interviewee scenes can push to **1.7×** when the voice/character holds the higher pace (validated on Brian/Worf + Charlotte/Jadzia). Reporter Liam stays at 1.5× to keep authoritative news-anchor weight. Do NOT push above 1.7× — Brian's low register starts to chipmunk.

**Pre-launch validation (manager, in debug mode):**
List the 5 planned lip-sync clips with per-clip cost (requested `duration` × $0.04/s; billed on the returned length, ≈ the TTS length). Confirm with user before launching — the cost follows the audio length, not a flat per-clip price.

### Phase 5: Assembly (editor)

**Inputs to editor sub-agent prompt (manager parses + passes):**
- Standard: scene mp4s, opener.mp4, cta.mp4, bg-music.mp3, storyboard.json
- Subtitles: the one universal style (editor.md §6), the orchestrator only passes `SUBTITLES=true`. Karaoke highlight is disabled by architecture.

**Canonical single-pass `filter_complex` (per `editor.md` §0):**

```
INPUTS:
  [0] opener.mp4  (no audio, normalize via scale+pad+fps)
  [1..5] scene-1..5.mp4  (H3 lip-sync clips, own audio = the scene TTS; untrimmed)
  [6] cta.mp4
  [7] bg-music.mp3
  [8] ambient.mp3  (Sound's generated DS9 promenade SFX — MANDATORY)

VIDEO branch:
  [0:v] scale/pad/fps,setpts=PTS-STARTPTS                           → [vop]
  [k:v] trim=end=DUR_k,setpts=PTS-STARTPTS,scale/pad/fps,setpts=(PTS-STARTPTS)/${SP_k},ass=build/scene-k.ass [vk]   (k=1..5; H3 trim first, DUR_k = duration_sec; SP_k from storyboard.json scenes[K-1].speedup, default 1.5)
  [5:v] + fade=t=out:st=SPED_DUR-1:d=1.0 on scene-5 only
  [6:v] scale/pad/fps,setpts=PTS-STARTPTS                           → [vct]
  [vop][v1][v2][v3][v4][v5][vct] concat=n=7:v=1:a=0                 → [vcat]

AUDIO branch (THREE layers: dialogue + ambient + music):
  [k:a] atrim=end=DUR_k,asetpts=PTS-STARTPTS,atempo=${SP_k},asetpts=PTS-STARTPTS,apad=whole_dur=<sped_video_dur_k>  [ak]   (the clip's own audio; H3 trim, then the per-scene speedup from storyboard; sped_video_dur_k = played_dur_k / SP_k)
  [a1][a2][a3][a4][a5] concat=n=5:v=0:a=1                            → [adlg]
  [adlg] adelay=2000|2000                                            → [atts]   (2s opener silence prefix)
  [8:a]  volume=0.15,apad=whole_dur=TOTAL_DUR,
         afade=t=in:st=0:d=0.5,
         afade=t=out:st=TOTAL-1:d=1.0                                → [aamb]   (ambient SFX, 0.15 — plays throughout)
  [7:a]  (music-timed.wav — pre-built: 2s theme + silence + 5s theme; volume 0.06 baked in)
                                                                     → [amus]   (music bookends only)
  [atts][aamb][amus] amix=inputs=3:duration=longest:
                          dropout_transition=0:
                          normalize=0                                → [aout]

OUTPUT:
  -map [vcat] -map [aout]
  -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p
  -c:a aac -b:a 128k -ar 44100 -ac 2
  -t TOTAL_DUR
  build/final.tmp.mp4   → mv final.mp4 after ffprobe-validate
```

**Ambient layer rules:**
- `apad=whole_dur=TOTAL_DUR` — ambient must cover the entire timeline (opener through CTA). If the source ambient.mp3 is shorter than TOTAL_DUR, apad with silence — but a 22s clip on a 45s timeline gives 23s of dead air. Sound must deliver ≥ TOTAL_DUR worth of ambient (concat 2 generations if needed).
- `afade=t=in:st=0:d=0.5` — soft fade-in at video start so opener-to-dialogue boundary isn't a hard ambient cut.
- Volume 0.25 — audible chatter texture; viewer registers «street» without ambient overwhelming the interviewee.

**Post-build audio self-check (Editor):**
Run `volumedetect` on a 1-second window of the FIRST dialogue scene at the dialogue midpoint. Mean volume should be in [-25, -15] dB. If quieter (< -28 dB) → either ambient drowned the dialogue (lower ambient volume to 0.18) or the lip-sync clip's audio (the scene TTS) is unexpectedly soft (re-mix with `volume=1.3` on `[adlg]` branch).

**Per-scene `apad=whole_dur=<sped_video_dur>` is MANDATORY** — small audio/video length differences per clip stack into lip-sync drift across 5 scenes without it (~4s by scene 5 in the Kling Avatar pilot). Every scene is an H3 lip-sync clip (`scene_video_lipsync: true`): its own audio is the scene's speech, so never lay `scene-K.mp3` over it again and never apply Kling Avatar's TTS trim; the H3 trim to `duration_sec` comes first (a clip that came back shorter plays whole).

**ASS subtitles** — the one universal style, generated by Editor via whisper from `build/voice-final.wav` (editor.md §6). No `--text`/`--style`/`--highlight-words`/`--verify-audio`. Karaoke highlight is disabled by architecture (one flat white style across all formats).

**Lower-third title cards (drawtext).** For each scene K where `storyboard.json → scenes[K].title_card.show == true`, add to that scene's `[vk]` branch (BEFORE the ASS burn-in):

```
drawtext=fontfile='/Library/Fonts/Helvetica-Bold.ttf':text='{NAME}':
  fontsize=58:fontcolor=white:borderw=3:bordercolor=black:
  x=80:y=h-340:
  enable='between(t,0.3,2.0)',
drawtext=fontfile='/Library/Fonts/Helvetica.ttf':text='{SUBTITLE}':
  fontsize=34:fontcolor=#cccccc:borderw=2:bordercolor=black:
  x=80:y=h-280:
  enable='between(t,0.3,2.0)'
```

- Position: lower-third, left-aligned (x=80, y from bottom ~270-340 px). Stays clear of TikTok bottom UI bar (which starts ~y=h-200).
- Timing: shown from t=0.3s to t=2.0s, then disappears so the talking head is unobstructed for the rest of the scene.
- Two-line: NAME (larger, bold) on top of SUBTITLE (smaller, regular).
- Font: Helvetica Bold (name) + Helvetica Regular (subtitle). If either required font is unavailable, STOP and report the missing dependency; do not silently substitute another font.
- White text + black outline (3px name, 2px subtitle) — readable against any background.
- Use `ffmpeg-full` binary (libfreetype required for drawtext).

Title cards go BEFORE the ASS burn in the filter chain so the ASS subtitles can never overlap with the lower-third (different y-positions anyway, but order matters for clean composition):
```
[k:v] scale/pad/fps,setpts=(PTS-STARTPTS)/1.5,drawtext=...NAME...,drawtext=...SUBTITLE...,ass=build/scene-k.ass [vk]
```

If `title_card.show == false` for a scene, skip drawtext, just `[k:v] scale/pad/fps,setpts=...,ass=build/scene-k.ass [vk]`.

**Output upload** — after explicit user approval, Manager uploads `final.mp4` through its canonical run-scoped path.

---

## Voices

| Role | Speech route | Notes |
|---|---|---|
| Reporter (locked) | native → format-owned Chatterbox sample → MiniMax | Fast snappy news-on-the-street pace. |
| Interviewee | native → format-owned Chatterbox sample → MiniMax | Locked in this format when first used. |

Format-local species/character defaults may contain MiniMax preset names or approved `streettalk` sample URLs only. They are never imported from another format.

---

## Story Bible

After explicit user confirmation on a missing-bible first run, create `games/{GAME_TAG}/streettalk_story_bible.json`:

```json
{
  "series_id": "streettalk-{GAME_TAG}",
  "game_tag": "{GAME_TAG}",
  "title": "{GameName} Streettalk — {Location}",
  "created_at": "{TODAY}",
  "last_episode": 0,
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
    "reporter": "",
    "interviewees": {}
  },
  "species_voice_defaults": {
    "klingon": "{MINIMAX_PRESET}",
    "vulcan": "{MINIMAX_PRESET}",
    "bajoran": "{MINIMAX_PRESET}",
    "ferengi": "{MINIMAX_PRESET}",
    "cardassian": "{MINIMAX_PRESET}",
    "romulan": "{MINIMAX_PRESET}",
    "starfleet": "{MINIMAX_PRESET}"
  },
  "location": {
    "slug": "",
    "display_name": "",
    "supabase_ref_url": "",
    "description_for_nb2": "..."
  },
  "interviewee_pool": [],
  "topic_rotation": {
    "recent_question_tags": [],
    "recent_interviewees": [],
    "recent_species": [],
    "cooldown_episodes": 5
  },
  "episode_summaries": [],
  "opener_url": "",
  "cta_url": ""
}
```

**FIFO 5** on `episode_summaries`. Append per episode only after the user explicitly approves the presented final video:

```json
{
  "episode": N,
  "date": "YYYY-MM-DD",
  "reporter": "Jake Sisko",
  "question": "Why isn't Worf fining anyone anymore?",
  "question_tag": "worf-no-fines",
  "interviewees": [
    {"name": "Quark", "species": "ferengi", "tone": "satirical-takedown"},
    {"name": "Bajoran Civilian", "species": "bajoran", "tone": "earnest-cluelessness"},
    {"name": "Klingon Veteran", "species": "klingon", "tone": "absurd"}
  ],
  "structure": "5 scenes — reporter intro → 3 vox-pop → reporter outro",
  "topic_tags": [...],
  "final_url": "...",
  "duration_sec": 38.4
}
```

**Update `topic_rotation` after each episode:**
- `recent_question_tags`: push new tag, drop oldest beyond 5
- `recent_interviewees`: push the 3 names, drop oldest beyond 15 (= 5 episodes × 3)
- `recent_species`: push the 3 species, drop oldest beyond 15

---

## Anti-repetition check

Before Phase 3, manager validates against story bible:

- [ ] `question_tag` NOT in `recent_question_tags` (last 5 episodes).
- [ ] At least 2 of 3 interviewees NEW vs previous episode.
- [ ] At least one species NEW vs previous episode.
- [ ] 3 distinct tones in this episode (no two interviewees with same tone).

If collision → scenarist regenerates with cooldown.

---

## Storyboard JSON (template, 5 scenes)

```json
{
  "format": "streettalk",
  "show_name": "{GameName} Streettalk — {Location}",
  "episode": 1,
  "game_tag": "{TAG}",
  "language": "en",
  "question": {"text": "...", "tag": "..."},
  "visual_identity": {
    "characters": {
      "reporter":   {"name": "...", "character_description": "...", "image_url": "supabase://avatars/reporter.png"},
      "interviewee_1": {"name": "...", "species": "...", "tone": "...", "character_description": "...", "image_url": "supabase://refs/i1-on-location.png"},
      "interviewee_2": {"name": "...", "species": "...", "tone": "...", "character_description": "...", "image_url": "supabase://refs/i2-on-location.png"},
      "interviewee_3": {"name": "...", "species": "...", "tone": "...", "character_description": "...", "image_url": "supabase://refs/i3-on-location.png"}
    },
    "environments": {
      "main_location": "..."
    }
  },
  "voices": {
    "reporter":      {"voice": "Liam",  "stability": 0.55, "language_code": "en"},
    "interviewee_1": {"voice": "Josh",  "stability": 0.55, "language_code": "en"},
    "interviewee_2": {"voice": "Adam",  "stability": 0.55, "language_code": "en"},
    "interviewee_3": {"voice": "Brian", "stability": 0.55, "language_code": "en"}
  },
  "scenes": [
    {"index": 1, "role": "reporter",      "camera": "frontal-med-cu",       "tts": "{Reporter} here on the {Location} for {GameName} Streettalk. Today's question: {QUESTION}. Let's find out."},
    {"index": 2, "role": "interviewee_1", "camera": "3q-med-cu-mic-fg",     "tone": "satirical-takedown",  "tts": "..."},
    {"index": 3, "role": "interviewee_2", "camera": "closer-different-bg",  "tone": "earnest-cluelessness","tts": "..."},
    {"index": 4, "role": "interviewee_3", "camera": "wider-extra-blur-bg",  "tone": "absurd",              "tts": "..."},
    {"index": 5, "role": "reporter",      "camera": "wider-frontal",        "tts": "{Ironic sign-off}. {Catchphrase}."}
  ],
  "subtitles": {"method": "ass-emit-only", "style": "bold", "word_highlight": true, "emphasis": {"scene_1": "...", "scene_2": "...", "scene_3": "...", "scene_4": "...", "scene_5": "..."}, "speedup": 1.5},
  "music": {"mood": "{game_mood_from_config}", "track_name": "{track_picked_by_sound}", "volume": 0.06},
  "opener": {"url": "supabase://branding/streettalk-opener.mp4"},
  "cta":    {"url": "supabase://branding/cta.mp4"}
}
```

---

## Budget

**Per-second pricing (from `budgets.md`):**
- NB2 image: $0.08
- H3 Max Turbo lip-sync: $0.04/s of the returned clip length (≈ the TTS length)
- Kling Avatar v2 Standard (replaced; the Test 12 baseline): $0.056/s of input audio
- Kling I2V 5s (no audio): $0.42
- Routed speech generation: provider-dependent

**Per-episode breakdown (steady-state, prep already in Supabase):**

| Item | Cost | Notes |
|---|---|---|
| Opener (Supabase) | $0 | one-time prep |
| CTA (Supabase) | $0 | one-time prep |
| Reporter base avatar (Supabase) | $0 | one-time prep |
| Location ref (Supabase) | $0 | one-time prep |
| Interviewee on-location edits (3 × $0.08) | $0.24 | NB2 edits per episode |
| Reporter scene edits (2 × $0.08) | $0.16 | scene 1 + scene 5 |
| Routed speech generation (5 lines, ~35s) | provider-dependent | |
| H3 Max Turbo lip-sync (5 scenes × ~7s audio ≈ 36.5s returned × $0.04) | ~$1.46 | dominant cost (Kling Avatar v2: ~$1.96) |
| Ambient SFX (1-2 clips via configured SFX provider) | ~$0.08 | mandatory; silence breaks vox-pop |
| **Typical episode 2+** | **~$2.24** | well under cap |

**Test 12 (Oct 2026, Kling Avatar v2 baseline → H3 lip-sync):** $2.51 → $2.02 per whole video (19.5% saved); the five clips $1.92 → $1.43.

**Pilot (episode 1) overhead — one-time prep:**

| Item | Cost |
|---|---|
| NB2 reporter sheet + avatar | $0.16 |
| NB2 location ref | $0.08 |
| NB2 opener title card | $0.08 |
| Kling I2V opener 5s (no audio) | $0.42 |
| NB2 base refs for 3 new interviewees (if none in Supabase) | $0.24 |
| **One-time prep** | **~$0.98** |

**Realistic pilot total** (prep + first episode): ~$3.22 if everything works first try.

**Iteration tax** (per fun-news pilot post-mortem, expect +50% for first run): **~$4.83 expected, $7.00 hard cap.**

**Limits**
- **Hard cap: $7.00** (pilot allowance).
- **Soft stop: $6.30** — review before continuing.
- Episode 2+ target: ~$3.00.

---

## Output files

```
${OUTPUT_DIR}/
├── storyboard.json
├── scenes/
│   ├── scene-1/                  # reporter intro
│   │   ├── scene-1.png           # on-location NB2 edit
│   │   ├── scene-1.mp3           # TTS
│   │   └── scene-1.mp4           # H3 lip-sync clip as returned (the Editor applies the H3 trim)
│   ├── scene-2/  ...             # interviewee 1
│   ├── scene-3/  ...             # interviewee 2
│   ├── scene-4/  ...             # interviewee 3
│   └── scene-5/  ...             # reporter outro
├── build/                         # ffmpeg intermediates, ASS files (per editor.md workspace rule)
│   ├── scene-1.ass ... scene-5.ass
│   ├── opener-raw.mp4
│   ├── cta-raw.mp4
│   ├── bg-music.mp3
│   └── final.tmp.mp4
└── final.mp4                       # only deliverable in root
```

---

## Role briefs

### Scenarist
- 5 dialogue scenes (opener/CTA pre-built, not in storyboard).
- One absurd question; 3 interviewees of different species/tones.
- Word budget: reporter intro 15–22, interviewee 18–25 each, reporter outro 12–18.
- Hook-first reporter intro — present the question, don't preview answers.
- Each interviewee has distinct `tone` (one of: `dry-deadpan` / `absurd` / `earnest-cluelessness` / `satirical-takedown` / `meta-confused`); 3 distinct tones in one episode.
- Reporter outro: ironic sign-off + catchphrase. Do NOT recap interviewees.
- Mandatory: `subtitles.emphasis.scene_K` per scene (≤14 chars uppercase kicker phrases).
- Anti-repetition vs story bible `topic_rotation`.
- **Conversational delivery, NOT theatrical.** Streettalk is a fast vox-pop genre — short, sharp, alive. Hard rules:
  - **Average sentence length ≤ 8 words.** A long sentence is OK if there's a punchy 3-word line right after.
  - **No more than ONE period mid-line** — let one beat land then move on. Multiple periods = TTS pause inflation = dead air.
  - **No "ladies and gentlemen", "as we can see", "in conclusion", "without further ado"** — pure announcer-speak, kills the street-energy. Strip on first pass.
  - **No semicolons.** Use periods only at sentence ends, commas / em-dashes inside.
  - **Each interviewee answers in ONE sentence + ONE short follow-up.** Not two paragraphs.
- General rules — `rules/roles/scenarist.md`.

### Storyboarder
- Pull reporter avatar / location ref / opener from Supabase if present in story bible. Otherwise generate as one-time prep (logged to `pilot_prep_cost`).
- 3 interviewees: each gets one on-location NB2 edit using base ref as `image_urls[0]`. Reporter gets two (scene 1 + scene 5).
- All 5 scene images 9:16, three-quarter or frontal med-CU, mic visible per scene (reporter holds mic with show-name flag for intro/outro; mic with flag in foreground for interviewees). Show name on mic flag = `storyboard.json → show_name` short form, e.g. "Genshin Streettalk" or "Star Trek Streettalk" — never GLN.
- **Background matches question topic** — inject topic-specific visual elements into every on-location edit. If the question is about food prices, background should hint at a market/vendor. If about Klingon honor, Klingon visual elements in background. Do not use the bare location ref as-is when a specific question topic offers a richer visual hook.
- For each canon interviewee, use only a ref tagged for this `streettalk` format; if none exists, generate a fresh format-bound ref. Never pull a ref from another format without explicit user instruction.
- Upload per-episode scene PNGs to the Manager-provided current-run episode namespace (NOT registered in `game_assets`).
- New base refs for previously-unseen interviewees: tagged `streettalk,interviewee,{slug}` for future episodes.
- General rules — `rules/roles/storyboarder.md`.

### Sound
- Generate speech for all 5 scenes via native audio → approved `streettalk` sample through Chatterbox → otherwise MiniMax. Read routes only from this format's resolved story bible.
- Retry one failure once with the same route/settings, then stop; never switch provider or borrow another format's sample.
- Replace periods with commas/em-dashes in reporter lines (anchor anti-pattern from fun-news).
- Upload each mp3 to the Manager-provided current-run episode namespace as the scene's `tts_url` before Phase 4, and write `tts_duration_sec` and `duration_sec` = the TTS length rounded up to 0.1 s on every scene (`rules/roles/sound.md` §5b). A line whose TTS is longer than 15 s is not uploaded: STOP and return it to be shortened.
- Generate music via MiniMax using a `style` prompt built from game config `music.mood` / atmosphere (instrumental, see `rules/roles/sound.md` §6); if the game has no `music.mood`, use a neutral instrumental prompt fitting the game's setting. Volume `0.06`.
- General rules — `rules/roles/sound.md`.

### Animator
- **ONLY H3 lip-sync on H3 Max Turbo** (`minimax.h3max.turbo.i2v`; `rules/roles/animator.md` §2a "H3 lip-sync" and "Talking-head prompt"), one `tools/kling_runner.py` job per scene, all 5 scenes. Kling Avatar v2 is forbidden (the replaced route); never a plain clip on H3 Max Turbo, never lip-sync on H3 Max, no still.
- `image_url` = on-location scene PNG from Supabase (`scene_image_url`). `target_audio_url` = TTS mp3 from Supabase (`tts_url`, NOT fal.ai temp). Run the pre-flight curl check on both first (both 200; otherwise STOP and return to Manager).
- **Payload — exactly these seven fields (the Test 12 jobs):** `prompt`, `image_url` = `scene_image_url`, `target_audio_url` = `tts_url`, numeric `duration` = the TTS length rounded up to 0.1 s (`math.ceil(round(d*10,6))/10`, equal to the `duration_sec` Sound wrote), `resolution: "768P"`, `prompt_expansion_mode: "disabled"`, `seed: 20261021`. `expect`: `duration_seconds` = that `duration`, `duration_tolerance_seconds: 0.8`, `audio: "required"`, `min_bytes: 100000`, `min_width: 600`, `min_height: 1000`, `orientation: "portrait"`. Template: `tools/examples/minimax-h3-max-turbo-talking-head.job.json` (the Test 12 scene 2 job below).
- A scene whose TTS is longer than 15 s (H3's maximum) is not submitted: return it to be shortened.
- **Prompt (≤512 UTF-8 bytes):** the speaker by look, position and framing (from the storyboard and the scene image), the expression and at most one small gesture; no gaze or head lock (`unblinking`, `eyes locked on`, `steady eye contact with camera`, `facing the camera head-on`, `holds still`, `stares`). Then ONE gaze sentence by role (`She` / `her` for a female speaker):
  - reporter intro and outro (scenes 1 and 5, addressing the viewer): `He looks into the camera like a TV news presenter, blinking naturally, with small relaxed head movements and changing expression between phrases; no frozen stare.`
  - interviewees (scenes 2–4, talking to the off-screen reporter): `He does not stare into the lens: his gaze rests on the reporter just beside the camera and drifts naturally between phrases, with small, relaxed head movements throughout.`

  End with `<Speaker> speaks the line "<line>" with lips in sync with the audio.` (`<line>` = the scene's `tts` verbatim). Over 512 bytes: shorten the descriptors first and keep the line whole; only if still too long, shorten the quoted line to its first sentence followed by `…` and report it. No music/voice clause. Example (Test 12, interviewee scene 2, 511 bytes):
  ```
  A Bajoran vendor in an earth-toned tunic stands behind his stall counter, three-quarter medium close-up. Wide puzzled eyes; he gestures toward the candle dish. He does not stare into the lens: his gaze rests on the reporter just beside the camera and drifts naturally between phrases, with small, relaxed head movements throughout. The vendor speaks the line "Oh, the constable sleeps in a bucket? I thought that was a very small shrine, I've been leaving offerings for weeks." with lips in sync with the audio.
  ```
- Write-back: `scene_video_kind: "i2v"`, `scene_video_route: "minimax.h3max.turbo.i2v"`, `scene_video_audio: "native"`, `scene_video_lipsync: true`, `motion_prompt` = the prompt. Do NOT pre-encode the 1.5× speedup — Editor does it in `filter_complex`; do not trim or remux the clip either.
- Retry a technically failed job once with the same route/settings, then STOP; no switch to Kling Avatar, H3 Max, another provider or a still.
- Explicit per-scene mapping: one job per scene, `job_id` and `output_path` derived from the scene index (no bash off-by-one — see fun-news pilot post-mortem).
- Cost: $0.04/s on the returned length, on the H3 lip-sync cost line.
- General rules — `rules/roles/animator.md`.

### Editor
- Canonical single-pass `filter_complex` per `editor.md` §0.
- Inputs: opener + 5 scene mp4s + cta + bg-music.
- Every scene is an H3 lip-sync clip (`scene_video_lipsync: true`): **H3 trim** of video and audio to `duration_sec` first in each scene branch (play whole when the clip is shorter), then the per-scene speedup; never Kling Avatar's TTS trim. The clip's own audio is the scene's speech: never lay `scene-K.mp3` over it again.
- Per-scene `apad=whole_dur=<sped_video_dur>` on audio — mandatory.
- `build/voice-final.wav` for subtitle timing is extracted from the lip-sync clips' own audio with the same per-scene speedup (`rules/roles/editor.md` §6.1, multi-voice).
- Per-scene ASS burn-in inside each `[vk]` BEFORE concat.
- `adelay=2000|2000` matches 2s opener silence prefix.
- Fade-out on scene-5 video (last 1s before CTA) + afade-out on music.
- `-t TOTAL_DUR` mandatory.
- Atomic finalize: `build/final.tmp.mp4` → ffprobe-validate → `mv` to root.
- Do not upload the final before review; Manager uploads it after explicit user approval.
- General rules — `rules/roles/editor.md`.

---

## Validation

- [ ] 5 dialogue scenes with 3 distinct interviewee tones.
- [ ] Reporter locked per story bible (not changed between episodes).
- [ ] All scenes have on-location backgrounds matching story bible's `location` (not bare base refs).
- [ ] Opener + CTA from Supabase (not regenerated per episode after pilot).
- [ ] Every scene is H3 lip-sync on `minimax.h3max.turbo.i2v` with the exact seven-field payload (`target_audio_url` = `tts_url`, `duration` = TTS rounded up to 0.1 s, `seed: 20261021`), the role's gaze sentence (reporter: camera; interviewee: off-screen reporter) and the closing lip-sync sentence (≤512 bytes); `scene_video_audio: "native"`, `scene_video_lipsync: true`; no Kling Avatar clip.
- [ ] Every scene has `tts_url`, `tts_duration_sec` ≤ 15 and `duration_sec` = the TTS length rounded up to 0.1 s.
- [ ] H3 trim to `duration_sec` before the speedup, per-scene `apad=whole_dur=<sped_video_dur>`; no `scene-K.mp3` laid over a lip-sync clip.
- [ ] ASS subtitles per scene with word-highlight on kicker phrases.
- [ ] Anti-repetition vs story bible passed (question tag + interviewees + species).
- [ ] Voice settings: `stability: 0.55`, `style` omitted, `voice` by name.
- [ ] Final 1080×1920, 30fps, ≤45s total, budget ≤ $7.00 pilot / ≤ $3.00 EP2+.
- [ ] Ambient SFX present (file `build/ambient.mp3` exists, mixed at 0.25 in filter graph).
- [ ] No theatrical announcer-speak in any scene's tts. Average sentence ≤ 8 words.
- [ ] Reporter stays in their story-bible tone_signature register — no announcer voice.
- [ ] show_name uses `{GameName} Streettalk` formula; GLN is absent.
- [ ] Mic flag in all 5 scene PNGs shows the correct show name (e.g., "Genshin Streettalk").
- [ ] Music track matches game atmosphere (not a mismatched genre).

---

## Anti-patterns

- ❌ Generic/non-game-specific opener — opener must be visually styled to the specific game world, not a generic vox-pop card.
- ❌ Background music during dialogue scenes — music plays ONLY at opener (~2s) and CTA (~5s). Use `music-timed.wav` with `anullsrc` for silence. Ambient SFX continues throughout at 0.15 (separate layer).
- ❌ Opener and CTA with different music themes — same track/offset, same game-appropriate theme at both bookends.
- ❌ Wrong game music — a fantasy RPG opener must not use trap phonk; a city-builder must not open with horror ambient. Generate via MiniMax with a `style` prompt built from the game mood.
- ❌ Mic flag without show name — reporter's mic must bear the game-specific show name (e.g., "Genshin Streettalk", "Roblox Streettalk"). Generic, blank, or wrong-game flag breaks TV identity.
- ❌ "GLN Streettalk" on any mic/opener — GLN belongs only to Star Trek Fun News. Streettalk always uses its `{GameName} Streettalk` identity.
- ❌ On-location background unrelated to question topic — even at the signature location, inject question-specific visual elements (topic-related characters, signs, or props in background).
- ❌ Studio/anchor scenes — streettalk is ENTIRELY on-location, never cuts back to a desk.
- ❌ Same question/topic recycled within 5 episodes.
- ❌ All 3 interviewees same species/faction — kills the «vox-pop diversity» joke.
- ❌ All 3 interviewees with same tone — flattens the comedic rhythm.
- ❌ Reporter outro that recaps interviewees — outro should be ironic sign-off only.
- ❌ Bare character ref as scene image — must be on-location NB2 edit.
- ❌ Character refs whose style conflicts with the resolved `style_tags` — the lip-sync clip mirrors the input ref's style. Prefer refs matching the target style, and derive the anti-drift negative from `style_tags`.
- ❌ Lip-sync cost estimate as flat "N × 5s" — H3 lip-sync is billed at $0.04/s of the returned clip length (≈ the TTS length).
- ❌ Kling Avatar v2 (`fal-ai/kling-video/ai-avatar/*`) for any streettalk scene — replaced by H3 lip-sync after Test 12; never a fallback.
- ❌ A plain clip on H3 Max Turbo, a lip-sync clip on H3 Max, or a still for a dialogue scene.
- ❌ Gaze- or head-locking phrases in a lip-sync prompt (`unblinking`, `eyes locked on`, `steady eye contact with camera`, `facing the camera head-on`, `holds still`, `stares`) — H3 then stares into the lens; an interviewee looks at the off-screen reporter, not into the lens.
- ❌ Laying `scene-K.mp3` over a lip-sync clip (its soundtrack already is that TTS), trimming the clip in the Animator, or Kling Avatar's TTS trim in the Editor.
- ❌ ElevenLabs speech, provider switching after retry, or another format's voice/sample.
- ❌ fal.ai temp URLs as `image_url` / `target_audio_url` — only Supabase permanent.
- ❌ `-shortest` in FFmpeg — use `apad` + `-t TOTAL_DUR`.
- ❌ Pre-encoding `-fast.mp4` per scene — speedup happens in editor's `filter_complex`.
- ❌ Title cards / drawtext episode-number overlay (this is non-serial — no episode card).
- ❌ Silent ambient track (no street SFX layer) — uncanny / fake immediately. Mandatory ambient at 0.25 volume.
- ❌ Theatrical / announcer-speak in any line ("Ladies and gentlemen", "in conclusion", "without further ado"). Streettalk is vox-pop, not a speech.
- ❌ Long sentences with 3+ periods. Each `.` is a 0.5s TTS pause; vox-pop must feel alive.
- ❌ **Reporter missing arm/hand (Roblox EP1, scenes 1 & 5).** Prevent this in the prompt: explicitly add `"both arms and hands fully visible, mic held with full hand grip, no missing limbs"`. Generated frames receive technical validation only; any visual judgment is the user's during debug review.
- ❌ **Interviewee off-center and wrong gaze direction (Roblox EP1, scene 2).** NB2 placed Bacon Hair far left of frame, looking away from the off-screen mic. Fix: interviewee image_prompt MUST include `"character centered in frame"` + `"eyes and body angled toward reporter's mic in foreground, three-quarter turn toward the mic side"`. Never let NB2 default to a neutral/profile pose for vox-pop — the character must always be turned toward the interviewer.

---

## Future ideas

- **Recurring extras**: `interviewee_pool` accumulates generic-NPC base refs (e.g. "Bajoran Bartender", "Mondstadt Merchant") that show up across episodes as recognizable side-characters — builds a universe of recurring faces per game.
- **Guest episodes**: define the guest independently in the `streettalk` story bible and create format-bound assets. Cross-format appearances/assets are used only when the user explicitly instructs it.
- **Question types**: rotate question framings — political ("Should X be allowed Y?"), economic ("Will prices ever come down?"), pop-culture ("Is Z still cool?"), philosophical ("Does the universal translator make us lazier?").
