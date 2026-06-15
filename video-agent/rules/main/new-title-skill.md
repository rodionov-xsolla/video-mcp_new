# Skill: Adding a new game title

Step-by-step instructions for the agent. Describes what to ask the user, in what order, which decisions depend on what, which files to create and update.

**When to use:** the user asks to add a new game or title that is not yet in `games/`.

---

## Step 0. Preparation

Read before starting:
1. `games/genshin-impact/genshin-impact.md` — reference for Visual Style Guide + Character Prompt Blocks format
2. `games/pokemon-go/pokemon-go.md` — reference for CTA section + Trainer-style character blocks
3. `rules/roles/manager.md` lines 167–170 — Channel routing table (existing youtube_channel mappings)

---

## Step 1. Tier 1 — basic metadata (ask in one block)

| # | Field | What to ask | Example |
|---|-------|-------------|---------|
| 1 | `game_tag` | Slug for folder name and Supabase (kebab-case, EN) | `marvel-snap` |
| 2 | `display_name` | Human name with correct capitalization | "Marvel Snap" |
| 3 | `platform` | Platforms | iOS, Android, PC |
| 4 | `developer` | Studio name | Second Dinner |
| 5 | `audience` | Age range, casual/core, geo | 16–35, Core CCG, Global |
| 6 | `art_style` | One phrase describing visual style | "Comic-book 2D illustration" |
| 7 | `youtube_channel` | Which channel gets videos | `starfleetarchive` / `yellowguy` / `genshinsnap` / none |

### Tier 1 validation

- [ ] `game_tag` is kebab-case, all lowercase, no spaces
- [ ] `game_tag` does NOT match any existing folder in `games/`
- [ ] `youtube_channel` is one of: `starfleetarchive`, `yellowguy`, `genshinsnap`, or explicitly `none` (no guessing)

---

## Step 2. Visual Style Guide

Ask the user (or infer from `art_style` if obvious) — confirm before writing:

| # | Field | What to ask | Default |
|---|-------|-------------|---------|
| 1 | Color palette | 3–5 primary colors with HEX or description | — |
| 2 | Lighting style | ambient / dramatic / magical / neon / natural | ambient |
| 3 | Composition | vertical 9:16 / split-screen / AR overlay | vertical 9:16 |
| 4 | `prompt_prefix` for NB2/Kling | 1–2 anchor sentences that lock the art style | — |
| 5 | Style restrictions | What MUST NOT appear in generated images | — |

**`prompt_prefix` is mandatory.** It becomes the first sentence of every `image_prompt` in storyboard.json.
If the user can't provide one — draft it from `art_style` + color palette and ask for approval.

Example (Pokémon GO):
```
Pokémon GO style, vibrant cartoon 3D Pokémon character, bright saturated colors, playful round proportions, cute expressive face, magical AR glow, real-world environment backdrop
```

---

## Step 3. Character Prompt Blocks

Ask the user:
1. List the main characters / archetypes (5 minimum, 10+ recommended)
2. For each character — collect or draft a prompt block with **8+ visual details**:
   - Body type / proportions
   - Outfit / armor / costume with colors
   - Hair (color, length, style)
   - Accessories (weapons, jewelry, gadgets)
   - Expression / attitude
   - Signature pose or action
   - Characteristic special feature (glow, wings, tail, etc.)
   - Size relative to frame / scale

If the user provides a brief description — expand it to 8+ details and confirm.
If the user provides Supabase reference URLs — record them in a table (see format below).

### Character block template

```markdown
#### {Character Name}
`{art_style keywords}, {body description}, {outfit + colors}, {hair}, {accessories}, {expression}, {pose}, {special detail}`
```

Example (from pokemon-go.md):
```markdown
#### Pikachu (#025)
`cartoon 3D Pikachu Pokémon, chubby yellow electric mouse, long black-tipped ears, small red circle cheeks glowing faintly with electricity, bright energetic eyes, tiny arms, cute stubby tail with lightning bolt tip, surrounded by sparks`
```

### Reference images table (if Supabase URLs exist)

```markdown
## Reference images (Supabase)

> Base URL: `https://{SUPABASE_HOST}/storage/v1/object/public/Cosplay%20sources/`

| Character | Supabase URL |
|-----------|-------------|
| {Name}    | `{full URL}` |
```

---

## Step 4. Tone of Voice

Ask in one block:

| # | Field | Options | Example |
|---|-------|---------|---------|
| 1 | Tone | epic / brainrot / nostalgic / educational / hype / cinematic | nostalgic + energetic |
| 2 | Primary language | EN / RU / mix | EN (main) |
| 3 | Obligatory vocabulary | Genre slang, memes, catchphrases | "shiny", "CP", "legendary raid" |
| 4 | Example phrases | 3–5 lines the scenarist can use as tone reference | "Which starter would YOU choose?" |

### Game slang table (if applicable)

If the game has significant in-game terminology, create a table:

```markdown
## Game slang

| Term | Meaning |
|------|---------|
| {term} | {explanation} |
```

This helps scenarist write authentic scripts without guessing terminology.

---

## Step 5. Recommended formats

List 3–5 formats from `rules/formats/` that suit this game. For each — one-word rationale.

Example:
```markdown
## Formats for this game

- **`character-story`** — deep lore per character
- **`top-list`** — tier lists and rankings
- **`serial-drama`** — episodic story arcs
- **`news`** — patch notes, events, meta updates
- **`redcon`** — "what if X happened in the game world"
```

If a format needs game-specific rules, note it:
> `serial-drama` → create `games/{GAME_TAG}/serial-drama_special.md` before first production run.

---

## Step 6. Music

Ask or infer from tone:

| # | Field | Options |
|---|-------|---------|
| 1 | Mood category | Badass / Dark / Emotional sad / Energetic / Fun / Heroic |
| 2 | BPM range | e.g. 110–140 |
| 3 | Specific tracks | Names from `music/tracks.json` (optional) |

---

## Step 7. CTA — MANDATORY

**Every title MUST have a CTA before going into production.** A missing CTA means the Editor cannot close videos correctly.

### 7a. Check if CTA already exists

```bash
curl -s \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  "${SUPABASE_URL}/rest/v1/game_assets?game_tag=eq.{GAME_TAG}&asset_type=eq.cta&select=url"
```

- **Empty array `[]`** → CTA is missing → go to 7b
- **URL returned** → CTA exists → go to 7c

### 7b. CTA does not exist — generate it

Ask the user **in one block**:

| # | Question | Default |
|---|----------|---------|
| 1 | What should the CTA show? | Game logo + "FOLLOW FOR MORE" |
| 2 | Duration | 3s |
| 3 | Call to action text | "LINK IN BIO" / "FOLLOW" / "SUBSCRIBE" |
| 4 | Animation style | Dynamic (Veo3) or static overlay (Kling I2V) |

**Model decision:**
- Veo3 T2V — if the CTA needs motion and sound baked in (`generate_audio: true`)
- Kling I2V — if a styled still frame + subtle motion is sufficient

Generate one clip. Cost: ~$3.20 (Veo3 8s) or ~$0.63 (Kling I2V 5s with audio).

After generation:
1. Validate with ffprobe: resolution `1080x1920`, duration > 1s
2. Upload to Supabase Storage:
   - Bucket: `assets`
   - Path: `{GAME_TAG}/branding/cta.mp4`
   - Get the public URL
3. Insert into `game_assets`:
   ```bash
   curl -s -X POST \
     -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
     -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
     -H "Content-Type: application/json" \
     -d '{"game_tag":"{GAME_TAG}","character_name":"cta","asset_type":"cta","url":"{URL}","tags":["cta","branding"]}' \
     "${SUPABASE_URL}/rest/v1/game_assets"
   ```
4. Record in the game config (see template below)

### 7c. CTA already exists — verify and document

1. Run ffprobe on the URL: check `1080x1920`, duration > 1s
2. Record in the game config

### CTA section template for game config

```markdown
## CTA

- **Status:** ready
- **URL:** {supabase_public_url}
- **Format:** 1080×1920, 30fps, ~{duration}s
```

If CTA is not yet generated, write:

```markdown
## CTA

- **Status:** TODO — asset not uploaded
- **Content (plan):** {game logo} + "{call to action text}"
- **After generation:** upload to Supabase `assets/{GAME_TAG}/branding/cta.mp4`
- **Format:** 1080×1920, 30fps, ~3s
```

### 7d. Opener (optional, recommended)

Ask: "Should we create an opener now (2–3s intro clip) or add it to TODO?"

- Yes → same generation flow as CTA, `asset_type=opener`, path `{GAME_TAG}/branding/opener.mp4`
- No → write a TODO section in the game config identical to CTA TODO template above

---

## Step 8. Create files

### 8a. Main game config

Create `games/{GAME_TAG}/{GAME_TAG}.md` with this section order:

```
# {Display Name}

## Metadata
## Game concept
## Visual Style Guide
  ### Color palette
  ### Lighting
  ### Composition
  ### Style restrictions
  ### Prompt prefix
## Character Prompt Blocks
## Reference images (Supabase)   ← only if URLs exist
## Trainer / team archetypes     ← only for games with team system
## Tone of Voice
  ### Example phrases
## Formats for this game
## Music
## Game slang                    ← only if applicable
## CTA
## Opener
```

### 8b. Assets directory

Create placeholder files so git tracks the directories:

```bash
mkdir -p games/{GAME_TAG}/assets/refs games/{GAME_TAG}/assets/avatars
touch games/{GAME_TAG}/assets/refs/.gitkeep
touch games/{GAME_TAG}/assets/avatars/.gitkeep
```

### 8c. Update cross-cutting files

**`rules/roles/manager.md`** — Channel routing section (~line 168):
Add a line before the "No `youtube_channel` field" catch-all:
```
- `{game_tag}` → `{youtube_channel}`
```
Skip if `youtube_channel` is none.

**`video-agent/STRUCTURE.md`** — games listing section:
Add a row for the new game folder.

**`video-agent/CLAUDE.md`** — TODO section:
If there is a TODO list with `games/ark/ark.md`, `games/pubg/pubg.md` style entries, remove the new game from the pending list (or leave a note that it's done).

---

## Step 9. Final validation checklist

Show the user:

- [ ] `games/{GAME_TAG}/{GAME_TAG}.md` created with all required sections
- [ ] `prompt_prefix` written and confirmed by user
- [ ] ≥ 5 Character Prompt Blocks (8+ visual details each)
- [ ] Tone of Voice + example phrases filled
- [ ] ≥ 3 recommended formats listed
- [ ] CTA: status = `ready` with URL, OR status = `TODO` with content plan
- [ ] `youtube_channel` set (or explicitly `none`)
- [ ] `manager.md` Channel routing updated (if `youtube_channel` is set)
- [ ] `STRUCTURE.md` updated
- [ ] `assets/refs/.gitkeep` and `assets/avatars/.gitkeep` created

---

## Defaults (auto-fill if user did not specify)

| Field | Default | When to change |
|-------|---------|----------------|
| Composition | vertical 9:16 (1080×1920) | split-screen games |
| CTA duration | 3s | user specifies otherwise |
| CTA model | Kling I2V | if motion + sound required → Veo3 |
| Opener | TODO (not blocking) | user wants it now |
| Language | EN (main) | user specifies RU or mix |
| Music BPM | 110–140 | per game mood |
| Character blocks minimum | 5 | always try for 10+ |

---

## Skill anti-patterns

- ❌ Skipping CTA — every title needs one before production; document it as TODO at minimum
- ❌ `game_tag` with spaces or uppercase — breaks folder paths, Supabase queries, ffmpeg scripts
- ❌ Character prompt blocks under 8 details — the storyboarder will generate generic characters
- ❌ No `prompt_prefix` — every scene will look different; visual identity breaks across episodes
- ❌ Guessing `youtube_channel` — only set if the user confirms it; wrong channel = wrong public upload
- ❌ Creating the game config without creating `assets/refs/` — storyboarder errors on missing path
- ❌ Forgetting to update `manager.md` Channel routing — the manager skips YT upload silently
- ❌ Copying a game config from another title and renaming — each game has unique palette, slang, tone
