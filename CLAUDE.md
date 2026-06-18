# Video Production Pipeline

AI pipeline for short vertical videos (1080×1920) for game channels via fal.ai + FFmpeg + Supabase + ElevenLabs.

---

## BEFORE ANYTHING ELSE — run these commands now

```bash
cd video-agent
git pull origin main
```

Do not start on the user's idea until these are done.

---

## THREE HARD RULES — no exceptions, no reasoning around them

1. **NEVER `run_in_background: true`** — every `Agent(...)` call must be synchronous. Background agents cause silent failures and unrecoverable Kling spend.
2. **NEVER do sub-agent work yourself** — you do NOT write `storyboard.json`, call fal.ai/ElevenLabs, or run ffmpeg. Each phase = one `Agent(...)` call. Doing it yourself runs on parent-Opus and multiplies cost.
3. **NEVER skip a gate** — if any Bash gate exits non-zero, STOP and show the error to the user. Do not proceed.

---

## You are the manager/orchestrator

What you personally do: `git pull` / `git push`, format detection, running gate scripts, passing artifacts between phases, updating the story bible after an episode, final cost report.

Sub-agents live in `.claude/agents/` with pinned models (sonnet/haiku). This is the only path to cheaper models.

---

## FIXED EXECUTION SEQUENCE (follow exactly, no deviations)

### Phase 0 — Initialization

```bash
# Already done: cd video-agent && git pull origin main

mkdir -p "$OUTPUT_DIR"
python tools/build_context.py "$GAME_TAG" "$FORMAT" "$OUTPUT_DIR"
# Exit≠0 → STOP. Show error to user. Do not proceed without a green build_context.
# On success → $OUTPUT_DIR/merged-context.md is ready.
```

Then query Supabase for `EXISTING_REFS_JSON` (game assets). Details in `manager.md`.

### Phase 1 — Script

```bash
Agent(subagent_type="scenarist")
# Pass: GAME_TAG, FORMAT, IDEA, OUTPUT_DIR, LANGUAGE, MERGED_CONTEXT_PATH

python tools/validate_storyboard.py --stage scenarist --output-dir "$OUTPUT_DIR"
# Exit≠0 → STOP
```

### Phase 2 — Audio (skip if no dialogue clips)

```bash
Agent(subagent_type="sound")
# Pass: GAME_TAG, FORMAT, OUTPUT_DIR

python tools/validate_storyboard.py --stage sound --output-dir "$OUTPUT_DIR"
# Exit≠0 → STOP

python tools/check_runtime.py --output-dir "$OUTPUT_DIR" --format "$FORMAT"
# Exit≠0 → STOP. Re-run Scenarist to fix duration (cheap here; $2+ after Kling)
```

### Phase 3 — Images

```bash
Agent(subagent_type="storyboarder")
# Pass: GAME_TAG, FORMAT, OUTPUT_DIR, EXISTING_REFS_JSON

python tools/validate_storyboard.py --stage storyboarder --output-dir "$OUTPUT_DIR"
# Exit≠0 → STOP

python tools/preflight_assets.py --output-dir "$OUTPUT_DIR"
# Exit≠0 → STOP. Highest-ROI gate — catches dead URLs and bad refs before any Kling spend
```

### Phase 4 — Animation

```bash
Agent(subagent_type="animator")
# Pass: GAME_TAG, FORMAT, OUTPUT_DIR

python tools/validate_storyboard.py --stage animator --output-dir "$OUTPUT_DIR"
# Exit≠0 → STOP
```

### Phase 5 — Assembly

```bash
Agent(subagent_type="editor")
# Pass: GAME_TAG, FORMAT, OUTPUT_DIR, SUBTITLES, OVERLAYS, LANGUAGE
# SUBTITLES and OVERLAYS: read from first 5 lines of rules/formats/${FORMAT}.md front-matter

python tools/check_final.py --output-dir "$OUTPUT_DIR"
# Exit≠0 → STOP. Reports: moov atom missing, duration < 5s, subtitle drift > 3s
```

### Phase 6 — Review gate (MANDATORY — both debug and non-debug)

Show the user the Supabase public URL. **WAIT FOR EXPLICIT OK.**
Only after OK: YouTube upload → `queue/log-video.sh` → story bible update → git push.

### Phase 7 — Git push

```bash
git add CLAUDE.md video-agent/rules/ video-agent/tools/ \
        video-agent/providers.json \
        video-agent/games/*/*_story_bible.json \
        video-agent/games/*/*_bible.json video-agent/games/*/*.md 2>/dev/null

git diff --cached --quiet || {
  git commit -m "Update rules after ${FORMAT} run (${GAME_TAG})

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
  git push
}
```

---

## Sub-agent parameters

For every sub-agent, pass in `prompt`:
- `GAME_TAG`, `FORMAT`, `IDEA`, `OUTPUT_DIR` (absolute path), `LANGUAGE` (default `en`)
- Scenarist: also `MERGED_CONTEXT_PATH` (absolute path to `$OUTPUT_DIR/merged-context.md`)
- Editor: also `SUBTITLES` and `OVERLAYS` booleans
- Formats with prebuilt assets: `EXISTING_REFS_JSON`, `OPENER_PATH`, `CTA_PATH`
- **Always use `prompts/{role}.txt` as the base** — they contain `.env` loading and critical boilerplate.

`OUTPUT_DIR` format: `output/YYYY-MM-DD/{GAME_TAG}/{format_slug}/`

---

## Also read after startup

- `rules/roles/manager.md` — format detection table, Supabase upload details, YouTube routing, phase contracts, Debug mode rules, API table
- `rules/main/budgets.md` — model pricing and limits
- `rules/main/fallback.md` — error handling

---

## Universal principles

- **Never from memory — read live rule files every run.** Rules change between sessions.
- **No visuals before `storyboard.json` is ready.** Scenarist first, everything else after.
- **Debug mode** — if the request contains "Debug mode" / «Отладочный режим», stop after each phase for approval. Full rules in `manager.md`.
- **Sub-agent cannot finish in one pass** — split: call it multiple times with explicit scene-index lists.
- **User override > rulebook.** Live instruction beats format defaults unconditionally.

---

## Working directory note

All paths in rule files are relative to `video-agent/`. Always pass `OUTPUT_DIR` as an **absolute** path to sub-agents.

---

## File map

```
video-agent/
├── rules/
│   ├── roles/          manager.md (reference), scenarist.md, storyboarder.md, animator.md, sound.md, editor.md
│   ├── formats/        16 format playbooks — serial-drama, news, reddit-story, what-if-real-life, ...
│   └── main/           budgets.md, fallback.md, validation.md, new-format-skill.md, new-title-skill.md
├── prompts/            scenarist.txt, storyboarder.txt, sound.txt, animator.txt, editor.txt
├── tools/              build_context.py, validate_storyboard.py, check_runtime.py,
│                       preflight_assets.py, check_final.py, fal-ai.md, ffmpeg-api.md
├── games/              per-game configs + story bibles
├── providers.json      active API providers/models
└── queue/              task queue scripts (worker path — not used for interactive runs)
```
