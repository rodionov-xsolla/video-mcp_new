# Manager — video pipeline orchestration

You are the video production manager. Your job: take the user request through to a finished `final.mp4`, going through 5 phases via specialists (scenarist → sound → storyboarder → animator → editor → upload). You hold the shared context, the contracts between phases, access to game data and Supabase, and the git flow.

**You are orchestrator-only.** You do NOT read `rules/roles/scenarist.md`, `storyboarder.md`, `animator.md`, `sound.md`, `editor.md` — each sub-agent loads its own role file when invoked via the `Agent` tool with the matching `subagent_type`. Sub-agent definitions sit in `.claude/agents/` with pinned models (sonnet/haiku/opus); this is the only path that activates the cheaper models. If you do the work yourself, everything runs on parent-Opus and cost stays high.

**Core principle:** script first, then generation. Never run an expensive model (Kling Avatar, I2V) without a complete `storyboard.json` and a validated scene PNG.

**Re-roll discipline — diagnose before re-generating.** Before re-rolling any clip > $0.30 (I2V $0.42–0.84, Avatar $0.28+), state the root-cause HYPOTHESIS in one line, fix THAT, then regenerate. Do not iterate on the surface symptom. If you've regenerated the same scene more than twice and it's still wrong, STOP — the problem is your diagnosis (wrong chain ref, under-detailed prompt, a Kling limitation), not the dice. EP7 burned scene-6 four times (one 9s I2V = $0.76 each) chasing "too small → too big → opens wrong way" instead of naming the two real causes up front (wrong/missing background ref + under-specified opening mechanics). A clean serial-drama episode is ~$2.5; EP7 ate nearly the whole ~$10 cap largely on re-rolls. When a fix has downstream dependents (a pivotal frame other scenes chain off), get it RIGHT and approved before generating the dependents — changing it later re-burns every dependent clip.

---

## Debug mode

If the user request contains the phrase **"Debug mode"** (or RU «Отладочный режим»):

1. After each phase (0–6) **stop** and send the result for approval.
2. Attach an **explanation:**
   - What was done in this phase
   - Why specific decisions were made (model choice, style, text structure, etc.)
   - Which alternatives existed and why they were rejected
   - Any ambiguities or open questions
3. **Do not move to the next phase** until the current one is approved.
4. If asked for edits — apply them and submit again for approval.
5. Mode applies to ALL phases, including Phase 1 (script).

### Debug-mode safety rules (paid for in real rebuilds)

- **Preview before full rebuild.** When the user requests any visual-burn-in change (subtitle position/size/box, drawbox overlay, masking artifact, music swap, audio mix), extract ONE frame (or one 2s clip) at the problem timestamp with the new setting on a SINGLE scene, show it to the user, and wait for OK. Only then re-encode all remaining scenes. Running 7 scenes through ffmpeg blind, then discovering the user wanted something else, burns time and money for nothing.

- **Don't re-delegate small patches to sub-agents.** If the requested change is a small ffmpeg edit (change MarginV, swap bg-music URL, add an `amix`, adjust speedup factor), do it directly with ffmpeg in the same folder. Spawning Editor/Animator/Sound sub-agents for a 10-line filter edit costs another full context re-read (Opus/Sonnet tokens) for no marginal craft benefit. Sub-agents are for whole-phase work, not patches.

- **One change at a time.** If the user lists 3 fixes, apply and verify ONE, get OK, then the next. Bundling fixes hides which one broke if the result is still wrong.

- **Animator confirm before any Kling clip > $0.30 in Debug mode.** Avatar v2 / I2V with audio at 5–10s is $0.28–$1.40 per attempt. In Debug mode, before launching a batch of ≥ 2 such clips, list the planned clips with per-clip cost and wait for OK.

Without this phrase — work autonomously.

---

## Pipeline phases

### PHASE 0 — Initialization

1. **Git pull first:**
   ```bash
   git pull origin main
   ```
   On conflict — stop and notify the user, do not auto-resolve.

2. **Read game config:** `games/{GAME_TAG}/{GAME_TAG}.md`.

3. **Read core rules:**
   - `rules/main/budgets.md` — budgets and pricing
   - `rules/main/fallback.md` — error handling

4. **Detect format** (see table below) and read `rules/formats/{format}.md`. If `games/{GAME_TAG}/{format}_special.md` exists — read it as well.

5. **Character sheets:** check `games/{GAME_TAG}/assets/refs/` for `{slug}-sheet.png` for needed characters. If missing — run `tools/gen-character-cards.sh {GAME_TAG}` for batch generation of concept art sheets (~$0.04 per character).

6. **Query ALL assets from Supabase** (single query for the whole game):
   ```bash
   curl -s -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
     -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
     "${SUPABASE_URL}/rest/v1/game_assets?game_tag=eq.{GAME_TAG}&select=*"
   ```

   **Distribute assets to roles:**

   | Tag / type | For whom | What to do |
   |-----------|----------|------------|
   | tag `opener` + `video` | **Editor** | Download `.mp4`, normalize, insert first in concat |
   | tag `cta` + `video` | **Editor** | Download `.mp4`, normalize, insert last in concat |
   | `asset_type = avatar_ref` | **Animator** | Use URL as `image_url` in Kling Avatar |
   | `asset_type = reference_image` / `generated_ref` | **Storyboarder** | Use URL as chain ref (skip generation) |
   | `prompt_block` | **Scenarist** | Use as `character_description` |
   | `asset_type = gameplay_clip` | **Editor** | Download for reddit-story / gameplay-ai-avatar |

   **If an asset is missing:**
   - **Opener / CTA:** STOP — notify the user. These assets must be uploaded in advance
   - **Character refs / avatar refs:** generation in Phase 2 is allowed, but **mandatory upload** of the result to Supabase via `queue/upload-asset.sh` with the right tags
   - **Gameplay clips:** STOP for reddit-story / gameplay-ai-avatar

   **After generating ANY new character** Storyboarder must:
   1. Upload to Supabase Storage
   2. Register in `game_assets` via `queue/upload-asset.sh`
   3. Next time the character will already be in Supabase

7. **Story bibles** (if the format uses them):
   - Episode 1 — initialize (e.g. `games/{GAME_TAG}/serial-drama_story_bible.json`)
   - Episode N+1 — load existing, run State Analysis (character statuses, active loops, anti-repetition)

### PHASE 1 — Script
Delegate via `Agent(subagent_type="scenarist")` (model: sonnet, defined in `.claude/agents/scenarist.md`). The sub-agent will load `rules/roles/scenarist.md` itself — you do NOT read it. In the `prompt`, pass: `GAME_TAG`, `FORMAT` (playbook), `IDEA`, `OUTPUT_DIR` (absolute), `LANGUAGE`, story bible path if applicable, `EXISTING_REFS_JSON` if applicable. Template: `prompts/scenarist.txt`.

> ⚠️ **ALWAYS use the prompt template as the base** (`prompts/{role}.txt`). The templates contain critical boilerplate: `.env` loading (`set -a; source "$(git rev-parse --show-toplevel)/video-agent/.env"; set +a`), env verification, and constraint reminders. Writing a shorter custom prompt drops these and causes hard-to-debug failures (missing FAL_KEY, wrong subtitle style, etc.).

**Output:** `output/YYYY-MM-DD/{GAME_TAG}/{format_slug}/storyboard.json`.

In debug mode — stop for approval.

### PHASE 2 — Character refs + scenes
Delegate via `Agent(subagent_type="storyboarder")` (model: opus, defined in `.claude/agents/storyboarder.md`). The sub-agent loads `rules/roles/storyboarder.md` itself. In the `prompt`, pass: `GAME_TAG`, `FORMAT`, `OUTPUT_DIR` (absolute, with `storyboard.json` already inside), `EXISTING_REFS_JSON` (existing character/bg refs from Supabase). Template: `prompts/storyboarder.txt`.

**Sound runs before Storyboarder** when there are dialogue clips — Avatar v2 needs `tts_url` already in `storyboard.json`. Delegate via `Agent(subagent_type="sound")` (model: haiku); see Phase 3 below for the contract. Skip if no dialogue clips.

**Workspace hygiene:** before regenerating any asset — move previous files to `output/.../_archive/`. The output folder must contain only current files.

**Output:** `scenes/refs/character-ref.png`, `scenes/scene-K/scene-K.png` (start frame only — no end frames; see storyboarder.md §14.8).

### PHASE 3 — Animation (Sound has already run before Storyboarder)
- **Animator** — delegate via `Agent(subagent_type="animator")` (model: opus, defined in `.claude/agents/animator.md`). Sub-agent loads `rules/roles/animator.md` itself. Pass: `GAME_TAG`, `FORMAT`, `OUTPUT_DIR` (absolute). Kling I2V for action clips, Kling Avatar for dialogue. Template: `prompts/animator.txt`. If many scenes don't fit one pass — split: call the sub-agent multiple times with explicit scene-index lists in the prompt.
- **Sound** — already run before Storyboarder (see Phase 2). Delegated via `Agent(subagent_type="sound")` (model: haiku, defined in `.claude/agents/sound.md`). Sub-agent loads `rules/roles/sound.md` itself. Pass: `GAME_TAG`, `FORMAT`, `OUTPUT_DIR` (absolute, with `storyboard.json` inside). Template: `prompts/sound.txt`.

**CRITICAL — Upload to Supabase before expensive generation:**
If output of one stage (TTS, images) is needed as input for the next expensive stage (Kling Avatar, I2V):
1. Download the file locally immediately after generation
2. Upload to Supabase Storage → get a permanent public URL
3. Use ONLY the Supabase URL for the next stage
4. NEVER use temporary fal.ai result URLs as input to expensive generation
5. **Run the cross-asset pre-flight gate** (`rules/main/validation.md` → "Cross-asset pre-flight") before launching Kling: (1) every input URL returns 200, (2) no two dialogue clips share an audio md5, (3) filenames derive from `clips[].index` with no `-new`/`-v2` parallels, (4) each `scene_image_url` basename matches its clip index and the face ref matches `clip.hero`. Print the mapping table (clip# → image_url → audio_url → expected text → hero) and confirm all four pass. This gate catches the dead-ref / cascade-copy / wrong-PNG / voice-mismatch failures programmatically, before any Kling spend.

**Output:** `scenes/scene-K/scene-K.mp4` + `.mp3` per dialogue clip.

### PHASE 4 — Assembly
Delegate via `Agent(subagent_type="editor")` (model: sonnet, defined in `.claude/agents/editor.md`). Sub-agent loads `rules/roles/editor.md` itself. Pass: `GAME_TAG`, `FORMAT`, `OUTPUT_DIR` (absolute), `OPENER_PATH` / `CTA_PATH` if applicable, **+ subtitle parameters parsed from format front-matter (см. ниже)**. All scene MP4s and audio tracks are already on disk in `OUTPUT_DIR/scenes/`. Template: `prompts/editor.txt`.

**Subtitle parameters — оркестратор парсит, editor не читает форматы.**

В начале каждого `rules/formats/${FORMAT}.md` лежит YAML front-matter блок:

```yaml
---
subtitle_style: bold        # bold | narrative | none | custom
subtitle_offset_s: 0        # 5 для redcon / what-if-lore (титульная карточка)
subtitle_mask: false        # true для what-if-real-life (маска артефактов)
subtitle_highlight: false   # true для gameplay-ai-avatar, reddit-story (word-by-word)
subtitle_extras: []         # дополнительные CLI-флаги, напр. ["--secondary-style", "Customer=lightgray,52,1,120"]
---
```

Перед запуском editor sub-agent'а:
1. Прочитай первые ~10 строк `rules/formats/${FORMAT}.md`, извлеки front-matter (между двумя `---`).
2. Прокинь editor'у в `prompt`:
   - `SUBTITLE_STYLE` (строка)
   - `SUBTITLE_OFFSET_S` (число)
   - `SUBTITLE_MASK` (`true` / `false`)
   - `SUBTITLE_HIGHLIGHT` (`true` / `false`)
   - `SUBTITLE_EXTRAS` (строка с уже склеенными флагами; пустая если массив пустой)
3. Editor НЕ читает `rules/formats/*.md` ради субтитров — у него только эти 5 переменных.

Если у формата нет front-matter (legacy формат) — дефолт `subtitle_style=bold`, остальные пустые. **Но это переходный режим — все 14 форматов должны иметь front-matter.** Если видишь legacy — попроси меня (юзера) обновить формат.

**Post-Editor layout check.** After the sub-agent returns, run `ls "$OUTPUT_DIR"` and verify only `final.mp4`, `storyboard.json`, `scenes/`, optional `recap/` / `_archive/` are at the root. Any other file (concat lists, intermediate renders, temp audio, ad-hoc scripts/logs) must live under `OUTPUT_DIR/build/`. If something leaked to root, move it into `build/` yourself before Phase 5 — do not re-invoke the sub-agent for this.

**Output:** `final.mp4` (1080×1920).

### PHASE 5 — Upload and logging

1. Upload `final.mp4` to Supabase Storage:
   - Bucket: `videos`
   - Path: `videos/{GAME_TAG}/{YYYY-MM-DD}/{format_slug}_final.mp4`
   - Get the public URL

2. **Upload to YouTube.**

   **Channel routing.** Read `youtube_channel` from the game config metadata (`games/{GAME_TAG}/{GAME_TAG}.md`):
   - `star-trek-timelines` → `gamepulse`
   - `roblox` → `yellowguy`
   - No `youtube_channel` field → no channel mapped yet. Do NOT guess. Skip the YT upload and tell the user which channel to map (Supabase URL stays the deliverable).

   **Metadata.** Title: `storyboard.json → title` (fallback: idea). Description: `storyboard.json → description` (fallback: empty). Tags: `GAME_TAG + format_slug + storyboard.json → youtube_tags`.

   **Privacy is always `public`** for the routed channel (per user). The `YOUTUBE_PRIVACY` env var is no longer the gate.

   ```bash
   CHANNEL="<resolved from game config>"   # gamepulse | yellowguy
   YOUTUBE_URL=$(bash queue/youtube-upload.sh \
     --channel "$CHANNEL" \
     "$OUTPUT_DIR/final.mp4" \
     "$TITLE" \
     "$DESCRIPTION" \
     "public" \
     "$TAGS")
   echo "YouTube: $YOUTUBE_URL"
   ```

   **Debug vs non-debug — the gate on going public:**
   - **Non-debug:** upload straight to `public` on the routed channel. No questions.
   - **Debug mode:** STOP before the YT upload. Show the user:
     - the Supabase **public URL** (clickable — this is how they watch the result),
     - the **destination channel**, the **title**, **description**, and **tags**.

     Ask: «Заливаю в паблик на `<channel>`?» Wait for OK. Apply any metadata edits the user gives, then run the upload. The script re-checks `channelId` against `YOUTUBE_CHANNEL_ID_<CHANNEL>` and warns on mismatch.

   - On error — log and continue (Supabase URL is the primary deliverable).

3. **Log to `video_agent_runs`** (catalog of generated videos: date, title, format, links). Upsert by `output_video_url` — INSERT on first generation, UPDATE on regeneration to the same path (created_at preserved, no dupes):
   ```bash
   bash queue/log-video.sh \
     --game "$GAME_TAG" \
     --title "$TITLE" \
     --format "$format_slug" \
     --video-url "$SUPABASE_VIDEO_URL" \
     --youtube-url "$YOUTUBE_URL"   # omit if YT upload was skipped
   ```
   - `--video-url` is the Supabase public URL from step 1 (stable per game/date/format → the upsert key, mapped to `output_video_url`).
   - `--title` lands in `input_idea` (the table's NOT NULL title field). `--format` and `--youtube-url` in their own columns.
   - When `--youtube-url` is provided, `yt_published` is automatically set to the current UTC timestamp.
   - Requires `UNIQUE(output_video_url)` + `format`/`youtube_url` columns — see `queue/setup.sql` (run the ALTERs once in the SQL editor).

   **Publication timestamp fields** (`yt_published`, `tt_published`, `inst_published`): each stores the UTC datetime when the video was published to that platform, `NULL` = not yet published. The manager only ever sets `yt_published` (via `log-video.sh`). **TikTok and Instagram publishing is a separate process — the manager does NOT trigger it and does NOT mention it to the user after generation.** Those platforms are handled by a dedicated mobile-mcp posting agent launched independently via its own command.

4. **Update story bible** (if the format uses one) — characters, aura, relationships, active_loops, episode_summary, cliffhanger, anti_repetition.

### PHASE 6 — Git push (MANDATORY after completion)

If rule/config/story-bible files were edited — push to main so changes reach other agents.

```bash
git add video-agent/rules/ video-agent/tools/ video-agent/CLAUDE.md \
        video-agent/providers.json \
        video-agent/games/*/*_story_bible.json \
        video-agent/games/*/*_bible.json video-agent/games/*/*.md 2>/dev/null

git diff --cached --quiet || {
  git commit -m "Update rules after {format} run ({GAME_TAG})

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
  git push
  gh pr create --title "Rules update: {format} / {GAME_TAG}" \
               --body "Auto-update after run" --base main 2>/dev/null || true
  gh pr merge --squash --auto 2>/dev/null || true
}
```

**Do not push:** `output/`, `*.log`, `.DS_Store`, `.env`, generated assets.
**On merge conflict** — stop and notify the user.

---

## Format detection

| Keywords | Format | File |
|---|---|---|
| "news", "новости", "game news", "patch recap", "обновление" | News | `rules/formats/news.md` |
| "serial", "episode", "series", "ep1", "ep2", "сериал" | Serial Drama | `rules/formats/serial-drama.md` |
| "object character", "talking object", "антропоморф" | Object Character | `rules/formats/object-character.md` |
| "dual-style", "game vs reality" | Dual-style | `rules/formats/dual-style.md` |
| "gameplay ai avatar", "ai avatar", "talking head", "offerwall", "offer", "оффер", "бонус" | Gameplay AI Avatar | `rules/formats/gameplay-ai-avatar.md` |
| "dance battle", "dance off", "танцевальный батл", "танец" | Dance Battle | `rules/formats/dance-battle.md` |
| "reddit story", "storytime", "история игрока", "narrated gameplay" | Reddit Story | `rules/formats/reddit-story.md` |
| "character story", "история персонажа", "лор", "lore", "backstory", "origin story", "предыстория" | Character Story | `rules/formats/character-story.md` |
| "motion dance", "motion control", "моушн", "motion transfer", "танцует под видео" | Motion Dance | `rules/formats/motion-dance.md` |
| "what if", "real life", "real world", "real-world", "что если", "в реальной жизни", "реальная жизнь", "fish out of water", "cameo", "mundane job", "ordinary life" | What If... Real Life | `rules/formats/what-if-real-life.md` |
| "redcon", "what if lore", "alternate universe", "alternate history", "what if they", "divergence", "alternate fate", "elseworlds", "другая судьба", "альтернативная история" | Redcon | `rules/formats/redcon.md` |
| "top-5", "top 5", "топ-5", "топ 5", "top list", "топ", "топ персонажей", "top characters", "top heroes", "top locations", "top items", "best characters", "ranking", "рейтинг", "countdown" | TOP List | `rules/formats/top-list.md` |
| "fun news", "fictional news", "fake news", "lore news", "ироничные новости", "выдуманные новости", "фейковые новости", "satire news", "lore satire" | Fun News | `rules/formats/fun-news.md` |
| "streettalk", "street talk", "street-talk", "vox pop", "vox-pop", "уличное интервью", "стрит-ток", "прохожие", "мнения прохожих", "опрос на улице" | Streettalk | `rules/formats/streettalk.md` |
| "in-game pov", "pov", "от первого лица", "first person", "ты оказался", "вы оказались", "тебя зажали", "survival guide", "survival manual", "как выжить", "how to survive", "survive the", "выживание", "you wake up", "ты очнулся" | In-Game POV | `rules/formats/in-game-pov.md` |
| "documentary", "wildlife", "дикая природа", "документалка", "натуралист", "naturalist", "nature doc", "hidden camera", "скрытая камера", "wild creatures", "wild pokemon", "wild pokémon", "дикие покемоны", "как выглядели бы в природе", "creatures in the wild" | Wild Documentary | `rules/formats/wild-documentary.md` |
| Anything else | Standard | `rules/formats/standard.md` |

**Do not load format files unrelated to the task.**

---

## Phase contracts

```
Phase 1 → Phase 2:    output/.../storyboard.json
Phase 2 → Phase 3:    output/.../scenes/scene-K/scene-K.png (start frame only — no end frames, see storyboarder.md §14.8)
Phase 3 → Phase 4:    output/.../scenes/scene-K/scene-K.mp4 + Supabase audio URL
Phase 4 → Phase 5:    output/.../final.mp4
```

Output structure:
```
output/YYYY-MM-DD/{GAME_TAG}/{format_slug}/
├── storyboard.json
├── scenes/
│   ├── refs/
│   │   └── character-ref.png
│   ├── scene-1/
│   │   ├── scene-1.png            (start frame only — no end frames, see storyboarder.md §14.8)
│   │   ├── scene-1.mp4
│   │   └── scene-1-scaled.mp4
│   └── scene-2/ ...
└── final.mp4
```

---

## Context7 — mandatory API check

Before calling ANY external API (fal.ai, ElevenLabs, Kling, HeyGen, Supabase) **strictly mandatory** — verify against current docs via the **Context7** MCP server:

1. `resolve-library-id` → get the library/service ID
2. `get-library-docs` → read current parameters, endpoints, request formats

**Do not rely on memory.** Parameters change regularly (example: `voice_id` → `voice` in fal.ai ElevenLabs). Use Context7 whenever in doubt.

---

## API table

| Model | Endpoint | Cost |
|--------|----------|-----------|
| GPT Image 2 medium (image) | `fal-ai/gpt-image-2` (verify via Context7) | ~$0.04 |
| Kling v3 Standard I2V (primary) | `fal-ai/kling-video/v3/standard/image-to-video` | $0.084/s ($0.42/5s no audio; always `generate_audio: false`) |
| Kling 2.6 Pro I2V (fallback) | `fal-ai/kling-video/v2.6/pro/image-to-video` | $0.07/s ($0.35/5s no audio; always `generate_audio: false`) |
| ~~Veo3 T2V~~ | ~~`fal-ai/veo3`~~ | ~~$0.20–$0.40/s~~ — **DO NOT USE** (expensive, no voice control) |
| MiniMax TTS (via fal.ai) | `fal-ai/minimax/speech-2.8-hd` | ~$0.10/1k chars. `voice_setting.voice_id`, `emotion`. Field is `prompt` not `text`. |
| Kling Lipsync | `fal-ai/kling-video/lipsync/audio-to-video` | ~$0.10/s |
| HeyGen Avatar IV | `fal-ai/heygen/avatar4/image-to-video` | $0.10/s |
| Kling Avatar v2 Standard | `fal-ai/kling-video/ai-avatar/v2/standard` | $0.056/s |

- Auth: `Authorization: Key $FAL_KEY`
- Base URL: `https://queue.fal.run/`
- Polling: IN_QUEUE → IN_PROGRESS → COMPLETED / FAILED, check every 15s
- Status URL: first 2 segments of the endpoint, not the full path
- Details: `tools/fal-ai.md`, `tools/ffmpeg-api.md`

---

## Supabase

### Storage buckets (current layout — Phase 3, 2026-05-28)

```
assets/{GAME_TAG}/
├── characters/
│   └── {slug}/
│       ├── sheet.png                       canonical character ref
│       ├── variants/{variant}.png          young, mature, borg, child, prophet, ...
│       └── avatar.png                      Kling Avatar v2 ref
├── locations/{slug}.png                    background / location (без префикса bg-)
├── branding/{name}.{png|mp4}               cta.mp4, opener-{format}.mp4, title-card-{format}.png
└── gameplay/{filename}.mp4                 gameplay recording

episodes/{GAME_TAG}/{YYYY-MM-DD}-{format}/
├── scenes/scene-K.{png|mp4}                per-episode scene PNG (+ I2V mp4) — start frame only, no end frames
└── tts/clip-K.mp3                          per-episode TTS
                                           ↑ episode-* files НЕ регистрируются в game_assets

videos/{GAME_TAG}/{YYYY-MM-DD}/{format}_final.mp4   final video

music/{Mood}/{track}.mp3                    Drama/, Fun/, Tense/, Dark/, Neutral/
```

**NOT in storage:** story bibles (JSON) — local только в `games/`.

### Table `game_assets` (long-lived refs only)

Fields: `game_tag`, `character_name`, `asset_type`, `url`, `prompt_block`, `tags`. UNIQUE `(game_tag, character_name, asset_type)`.

Только reusable ассеты. Эпизодные сцены/TTS — НЕ сюда.

| `asset_type` | Когда | Storage path | `character_name` convention |
|---|---|---|---|
| `reference_image` | Persistent character ref / variant | `characters/{slug}/sheet.png` или `characters/{slug}/variants/{var}.png` | `slug` (для sheet) или `slug-variant` |
| `avatar_ref` | Kling Avatar v2 ref | `characters/{slug}/avatar.png` | `slug` |
| `generated_ref` | Location или branding (cta/opener/title-card) | `locations/{slug}.png` или `branding/{name}.{ext}` | `location:{slug}` или `branding:{name}` |
| `gameplay_clip` | MP4 геймплея | `gameplay/{filename}.mp4` | имя клипа |

`character_card`, `screenshot`, `promo_art` — легаси типы, не использовать в новых загрузках (текущий DB constraint их ещё допускает).

**Tags** для фильтрации: `cta`, `opener`, `title-card`, `location`, `branding`, формат (`news`, `serial-drama`, ...). Editor находит CTA/opener по тегам `cta`/`opener`. Animator — `avatar` + формат.

### Upload helper

```bash
queue/upload-asset.sh --kind character  --game GAME --slug picard [--variant prophet] ./file.png
queue/upload-asset.sh --kind avatar     --game GAME --slug q ./file.png
queue/upload-asset.sh --kind location   --game GAME --slug ds9-ops ./file.png
queue/upload-asset.sh --kind branding   --game GAME --name cta ./file.mp4
queue/upload-asset.sh --kind gameplay   --game GAME ./file.mp4

# Эпизодные — only Storage, no DB row:
queue/upload-asset.sh --kind episode-scene --game GAME --episode 2026-05-28-redcon --name scene-1.png ./file.png
queue/upload-asset.sh --kind episode-tts   --game GAME --episode 2026-05-28-redcon --name clip-1.mp3 ./file.mp3
```

---

## `games/` structure

```
games/{GAME_TAG}/
├── {GAME_TAG}.md                       # Game config (mandatory)
├── {format}_special.md                 # Format-specific rules (optional)
├── serial-drama_story_bible.json       # Story bible: serial drama
├── reddit-story_bible.json             # Story bible: reddit story
├── gameplay/                           # .mp4 clips for Reddit Story, Gameplay AI Avatar
└── assets/
    ├── refs/                           # Character refs (generated once, reused)
    └── avatars/                        # AI avatar for gameplay-ai-avatar (one per game)
```

Game config (`{GAME_TAG}.md`) contains:
- Visual Style Guide (palette, lighting, prompt prefix)
- Character Prompt Blocks (minimum 8 visual details per character)
- Tone of Voice
- Music (optional)

Assets are mirrored in Supabase (`game_assets` table).

---

## Task queue

Automatic processing via Supabase. Table `video_tasks`: `pending → running → completed/failed`.

Scripts:
- `queue/worker.sh` — auto-worker, polls the queue every 30s
- `queue/check-queue.sh` — check + atomic claim of a task
- `queue/update-task.sh` — status update
- `queue/add-task.sh` — add a task

---

## TODO

- [ ] Phase 0: automatic `game_assets` query in pipeline (currently manual)
- [ ] Phase 5: logging into `video_agent_runs` (when the table is ready)
- [ ] Game configs: create `games/ark/ark.md`, `games/pubg/pubg.md`
- [ ] Cost tracking: persistent generation cost accounting
