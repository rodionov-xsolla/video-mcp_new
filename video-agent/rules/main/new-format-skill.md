# Skill: Creating a new video format

Step-by-step instructions for the agent. Describes what to ask the user, in what order, which decisions depend on what, which files to create and update.

**When to use:** the user asks to create a new video format that is not covered by the existing 8 formats.

---

## Step 0. Preparation

Read before starting:
1. `rules/roles/manager.md` lines 137–146 — Format detection table (existing keywords)
2. `rules/main/budgets.md` — existing budgets and model prices
3. 1–2 existing formats closest in concept to the new one — as reference

---

## Step 1. Collecting required data (Tier 1)

Ask the user **in one block**:

| # | Field | What to ask | Example |
|---|------|-------------|--------|
| 1 | `slug` | Format name (kebab-case, EN) | `reaction-compilation` |
| 2 | `display_name` | Human name | "Reaction Compilation" |
| 3 | `description` | One sentence — the essence | "Compilation of character reactions to game moments" |
| 4 | `keywords` | Trigger words (RU + EN, comma-separated) | "reaction", "реакция", "compilation" |
| 5 | `duration` | Target duration (range, sec) | 20–40s |
| 6 | `clip_count` | Clips × duration | 4 × 5s |
| 7 | `style` | Visual style | Pixar 3D / Photorealistic / Anime / Game-specific |
| 8 | `budget_max` | Maximum budget ($) | $5.00 |

### Tier 1 validation

- [ ] `slug` — kebab-case, doesn't match: `serial-drama`, `gameplay-ai-avatar`, `reddit-story`, `news`, `standard`, `dance-battle`, `dual-style`, `object-character`
- [ ] `keywords` — DO NOT overlap with keywords in `manager.md:137-146`. Check each word.
- [ ] `budget_max` — in the range $1–$20
- [ ] Compute `budget_stop` = round(`budget_max` × 0.90, 2)

---

## Step 2. Model decision tree (Tier 2)

Ask the **key question**: Is there speech/dialogue in the video?

### Branch A: NO speech → Kling I2V

Ask:
- `generate_audio`: true (Kling generates SFX) or false (silence, anullsrc)?
- Need start + end frames for each clip? (yes = better continuity, +$0.04/clip)
- `negative_prompt` mandatory? (yes for multi-char or dual-style)
- Number of characters in frame? (1 / 2 / variable)

**Result:** Image: NB2 → Video: Kling I2V → Audio: SFX only or silence

### Branch B: YES speech → choose voice source

Ask: WHO generates the voice?

#### B1: Veo3 T2V (voice baked in)
- motion_prompt includes `and says: "[text]"`
- `generate_audio: true` always
- Need NB2 images? (title card only or full scenes)

**Result:** Image: NB2 (opt.) → Video: Veo3 T2V → Audio: embedded

#### B2: ElevenLabs TTS + Kling Avatar v2 (lipsync)
Ask:
- Speed up Avatar after generation? (1.3x for energetic / 1.0x for drama)
- Two-step approval? (TTS → show user → then Avatar)
- Voice: locked per character in story bible OR chosen per video?

**Result:** Image: NB2 (avatar ref) → TTS: ElevenLabs → Video: Kling Avatar v2

#### B3: ElevenLabs TTS overlay on silent video
Ask:
- TTS volume? (default 1.0)
- SFX volume from Kling? (default 0.4)
- `adelay` TTS delay? (default 500ms)

**Result:** Image: NB2 → Video: Kling I2V (SFX) → TTS: ElevenLabs overlay

#### B4: MIXED (I2V action + Avatar dialogue in one video)
Ask:
- What `clip_type`s exist? (action / dialogue / reaction / etc.)
- Which clip_type → which model?
- action/dialogue balance? (50/50 / 70/30 / etc.)
- `generate_audio` for I2V clips: true or false?

**Result:** Image: NB2 → Video: Kling I2V + Kling Avatar v2 → TTS: ElevenLabs (for Avatar)

### Branch C: No video generation (assembly only)

Ask:
- Where do clips come from? (`games/{TAG}/gameplay/` / user uploads / Supabase)
- How are they selected? (shuf random / user-specified / by storyboard)
- Audio handling: strip (`-an`) / keep (volume=X)?
- TTS needed? (narration overlay)

**Result:** Video: pre-existing clips → TTS: ElevenLabs (opt.) → Assembly: FFmpeg

---

## Step 3. Conditional questions (Tier 3–5)

Ask ONLY relevant sections. Skip non-applicable ones.

### 3a. Image Generation (if NB2 is used)

| # | Question | Defaults |
|---|--------|----------|
| 1 | How many character refs? | 1 |
| 2 | Bg-reference per location mandatory? | no |
| 3 | Chain strategy for scene refs? | `[anchor, prev-scene]` |
| 4 | Image aspect ratio | 608×1080 (9:16) |
| 5 | Special image_prompt requirements? | no |

### 3b. Episodic / Serial (if format is episodic)

| # | Question | Options |
|---|--------|----------|
| 1 | Story bible needed? | yes / no |
| 2 | What fields in the story bible? | characters+status+relationships / themes+tones FIFO / custom |
| 3 | Anti-repetition: what to rotate? | phrases / hooks / cliffhangers / styles / emotions / custom |
| 4 | Loop management? | Minor/Major/Eternal / no |
| 5 | State transitions after an episode? | list of fields to update |

### 3c. Pre-Production Phase (if any)

| # | Question | Options |
|---|--------|----------|
| 1 | Research phase? | web search → research.json / no |
| 2 | Asset bank check? | Supabase game_assets / no |
| 3 | State analysis? | story bible / no |

### 3d. Subtitles

| # | Question | Options |
|---|--------|----------|
| 1 | Subtitles needed? | yes / no |
| 2 | Method? | PIL PNG overlay / drawtext ffmpeg / none |
| 3 | Font/size? | Arial Bold 38-48px / Montserrat Bold 42px / custom |
| 4 | Position? | lower third / split boundary / custom y= |
| 5 | Word-highlight? | yes (accent color) / no (plain white) |

### 3e. CTA / TBC

| # | Question | Options |
|---|--------|----------|
| 1 | CTA needed? | clip in concat-list / overlay last 2s / none |
| 2 | TBC overlay? | yes (2s before end) / no |
| 3 | Fade out? | yes (1.0s) / no |

### 3f. Music

| # | Question | Defaults |
|---|--------|----------|
| 1 | Background music? | optional |
| 2 | Volume level? | 0.15 |
| 3 | Mood category? | drama / energetic / comedic / lo-fi |
| 4 | Kling SFX + music together? Volumes? | SFX 0.4, music 0.15 |

### 3g. Layout

| # | Question | Default |
|---|--------|---------|
| 1 | Standard vertical 9:16 or split-screen? | vertical |
| 2 | (if split) Proportions? | 60/40 |
| 3 | (if split) What top / bottom? | — |
| 4 | (if split) Scale+crop rules? | `scale=1080:-2,crop=...` |
| 5 | (if split) Audio mixing volumes? | — |

### 3h. Game-Specific Overrides

| # | Question | Default |
|---|--------|---------|
| 1 | Need `{format}_special.md` per game? | no |
| 2 | Which fields in special? | style / characters / music mood / search keywords |

---

## Step 4. Budget calculation

Based on collected data, compute typical and maximum cost.

### Model prices (from `budgets.md`)

| Model | 5s | 10s |
|--------|----|----|
| NB2 image | $0.04 | $0.04 |
| Kling I2V (no audio) | $0.35 | $0.70 |
| Kling I2V (with audio) | $0.70 | $1.40 |
| Kling Avatar v2 | $0.28 | $0.56 |
| ElevenLabs TTS (line) | ~$0.05–0.10 | ~$0.07–0.15 |
| Veo3 T2V 8s (with audio) | — | $3.20 |

### Formula

```
typical_cost = (clip_count × image_cost) + (clip_count × video_cost) + tts_cost
```

- [ ] `typical_cost` ≤ `budget_max`
- [ ] If not — propose reducing clip_count or switching the model

---

## Step 5. Generating the playbook file

Create `rules/formats/{slug}.md` following the canonical structure:

```
# Format "{display_name}" — {description}

{paragraph description: genre, target audience, key gimmick}

This file is the **playbook**: when to use, concept, budget, role briefs.
Craft rules — in `rules/roles/*.md`.

---

## When to use

Keywords: "{keyword1}", "{keyword2}", ...

---

## Concept

- **Genre:** {style description}
- **Style:** {visual style}
- **Duration:** {duration range} ({clip_count} clips × {clip_duration})
- **Budget:** up to ${budget_max} per video. Stop if spend > ${budget_stop}.
- **Frame format:** {9:16 (608×1080) / split-screen layout}

### Models

- **Image:** {NB2 / skip}
- **Video:** {Kling I2V / Kling Avatar v2 / Veo3 T2V / pre-existing clips}
- **Audio:** {generate_audio / ElevenLabs TTS / overlay / none}

---

## Budget (rough estimates)

| Component | 5s clip | 10s clip |
|---|---|---|
| {model rows from Step 4} | | |

| Variant | Clips | Cost |
|---|---|---|
| Base (recommended) | {N} × {dur} | ~${typical} |

---

## Episode / video structure

| Phase | Timing | Goal | Clips |
|---|---|---|---|
| {beat rows} | | | |

{conditional sections: Story Bible, Loop Management, Anti-Repetition,
 Retention Strategy, Pre-Production, Gameplay Clips, Visual Layout,
 Prompting Rules, Voice Mapping, Locked/Variable Parameters}

---

## Role briefs

### Scenarist
{format-specific instructions}
- General script rules — `rules/roles/scenarist.md`

### Storyboarder
{format-specific instructions OR "SKIP — format does not use NB2 image gen."}
- General rules — `rules/roles/storyboarder.md`

### Animator
{format-specific instructions OR "SKIP — format does not use AI video gen."}
- General rules — `rules/roles/animator.md`

### Sound
{format-specific instructions}
- General rules — `rules/roles/sound.md`

### Editor
{format-specific instructions}
- General rules — `rules/roles/editor.md`

---

## Output files

{directory tree, output structure}

---

## Validation before publishing

- [ ] {checklist items based on format specifics}

---

## Anti-patterns

- ❌ {common mistakes for this format}
- ❌ `-shortest` in FFmpeg (ALWAYS use `apad`)
- ❌ `voice_id` hash instead of `voice` name in ElevenLabs
- ❌ Character ref directly as scene image
```

### Mandatory sections (always include)

1. When to use
2. Concept
3. Budget
4. Structure
5. Role briefs (all 5 + SKIP where not needed)
6. Output files
7. Validation
8. Anti-patterns

### Conditional sections (include when answered "yes")

| Section | When |
|--------|-------|
| Story Bible | format is serial |
| Loop Management | serial format with intrigue loops |
| Anti-Repetition Check | serial format |
| Retention Strategy | serial format |
| Pre-Production / Research Phase | has pre-research |
| Gameplay Clip Requirements | uses pre-existing clips |
| Visual Layout | split-screen |
| Prompting Rules | special prompt structure (4-layer, markers) |
| Voice Mapping | multiple voices / emotion-based pick |
| Locked / Variable Parameters | parameters locked across the series |
| CTA | has a call to action |

---

## Step 6. Updating cross-cutting files

After creating the playbook, update 4 files:

### 6a. `rules/main/budgets.md`

Add a row to the "Budget limits" table (after the last row):

```
| {Display Name} | **${budget_max}** | Spend > ${budget_stop} |
```

If the format has variants (single/series, I2V/T2V), add separate rows.

### 6b. `video-agent/CLAUDE.md`

Find lines 36-37:
```
│   └── {serial-drama, gameplay-ai-avatar, news, standard,
│       reddit-story, dance-battle, object-character, dual-style}.md
```
Add `{slug}` into the list inside `{}`.

### 6c. `rules/roles/manager.md`

Find the Format detection table (lines 137-146). Add a row **BEFORE** "Anything else | Standard":

```
| "{keyword1}", "{keyword2}" | {Display Name} | `rules/formats/{slug}.md` |
```

### 6d. `video-agent/STRUCTURE.md`

Find the listing of format files (lines 119-126). Add:

```
│       ├── {slug}.md           # {display_name}
```

---

## Step 7. Auxiliary files (if needed)

### Story Bible Template (if format is serial)

Create `games/{GAME_TAG}/{slug}_story_bible.json`:

```json
{
  "series_id": "",
  "game_tag": "",
  "title": "",
  "style_tags": "",
  "created_at": "{TODAY}",
  "last_episode": 0,
  "characters": [],
  "active_loops": [],
  "closed_loops": [],
  "world_state": {},
  "anti_repetition": {},
  "episode_summaries": []
}
```

Adapt fields per answers from step 3b.

### Game-Specific Special Template (if needed)

Create `games/{GAME_TAG}/{slug}_special.md`:

```markdown
# {Display Name} — settings for {Game Name}

{fields from step 3h}
```

---

## Step 8. Final validation

Show the user the checklist:

- [ ] `rules/formats/{slug}.md` created, contains all required sections
- [ ] `budgets.md` contains a row with the new format
- [ ] `CLAUDE.md` has the slug in the format list
- [ ] `manager.md` has the keywords in the Format detection table
- [ ] `STRUCTURE.md` has the file in the listing
- [ ] Keywords DO NOT overlap with existing formats
- [ ] Budget realistic: `typical_cost` ≤ `budget_max`
- [ ] All role briefs filled or marked SKIP with a reason
- [ ] Conditional sections included/excluded correctly
- [ ] Auxiliary files created (if needed)

---

## Defaults (auto-fill if user did not specify)

| Field | Default | When to change |
|------|---------|-------------|
| Frame format | 9:16 (1080×1920) | Split-screen layout |
| Default clip duration | 5s | Format requires otherwise |
| `generate_audio` I2V | true | If separate TTS overlay (false) |
| Music volume | 0.15 | Per format (0.05–0.25) |
| Subtitle method | none | If there is speech |
| CTA | none | If specified |
| TBC | none | Only serial |
| fps | 30 | Always |
| Codec | libx264, preset slow, crf 20 | Always |
| Audio | AAC 128k stereo | Always |
| `budget_stop` | budget_max × 0.90 | — |
| `-shortest` | **NEVER** | Universal anti-pattern |

---

## Skill anti-patterns

- ❌ Creating a format without polling the user (don't guess — ask)
- ❌ Copying an existing format and renaming (each format is unique)
- ❌ Skipping cross-cutting file updates (playbook without detection keywords = dead format)
- ❌ Keywords overlapping with existing formats (detection conflict)
- ❌ Budget without computing per model prices (unrealistic limit)
- ❌ Empty role briefs without SKIP marker (agent won't know — do or not)
