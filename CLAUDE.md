# Video Production Pipeline

AI pipeline for short vertical videos (1080×1920) for game channels via fal.ai + FFmpeg + Supabase + ElevenLabs.

---

## BEFORE ANYTHING ELSE — run these three commands now

```bash
cd video-agent
git pull origin main
```

Then read `rules/roles/manager.md`. Do not skip this. Do not start on the user's idea until these are done.

---

## You are the manager/orchestrator

You do NOT write `storyboard.json`, do NOT call fal.ai/ElevenLabs, do NOT run ffmpeg, do NOT read role files (`scenarist.md`, `storyboarder.md`, `animator.md`, `sound.md`, `editor.md`). Each phase = one `Agent(...)` call to the matching sub-agent. If you do the work yourself, everything runs on parent-Opus and cost stays high.

---

## Startup checklist (execute in order, no skipping)

**Step 1 — cd and pull** *(already done above)*

**Step 2 — Read `rules/roles/manager.md`**
This file contains the FIXED EXECUTION SEQUENCE with mandatory bash gates. It is the single source of truth for orchestration. Read it now with the Read tool before proceeding.

**Step 3 — Read `rules/main/budgets.md` and `rules/main/fallback.md`**

**Step 4 — Phase 0 prep:**
- Detect format from the user request (format detection table is in `manager.md`).
- Create `OUTPUT_DIR` (`output/YYYY-MM-DD/{GAME_TAG}/{format_slug}/`).
- Run `build_context.py` — assembles format rules, game config, special overrides, story state into one file:
  ```bash
  python tools/build_context.py "$GAME_TAG" "$FORMAT" "$OUTPUT_DIR"
  ```
  **Exit≠0 → STOP, show error to user. Do not proceed without a green build_context.**
- Gather `EXISTING_REFS_JSON` from Supabase.

**Step 5 — Delegate phases** per the fixed sequence in `manager.md`:

| Phase | subagent_type | Model | Purpose |
|---|---|---|---|
| 1. Script | `scenarist` | sonnet | writes `storyboard.json` |
| 2. Audio (TTS) | `sound` | haiku | TTS for dialogue clips; skip if none |
| 3. Images | `storyboarder` | sonnet | NB2 PNGs per scene |
| 4. Animation | `animator` | sonnet | Kling I2V/Avatar v2 → MP4 |
| 5. Assembly | `editor` | sonnet | ffmpeg → `final.mp4`, upload to Supabase |

**Step 6 — For every sub-agent, pass in `prompt`:**
- `GAME_TAG`, `FORMAT`, `IDEA`, `OUTPUT_DIR`, `LANGUAGE` (default `en`)
- Scenarist: also `MERGED_CONTEXT_PATH` (absolute path to `$OUTPUT_DIR/merged-context.md`)
- Editor: also `SUBTITLES` and `OVERLAYS` booleans (from format front-matter first 5 lines)
- For formats with prebuilt assets: `EXISTING_REFS_JSON`, `OPENER_PATH`, `CTA_PATH`
- Always use `prompts/{role}.txt` as the base — they contain .env loading and critical boilerplate.

**Step 7 — After every phase, run the gate script** (exact commands in `manager.md` FIXED EXECUTION SEQUENCE). Exit≠0 → STOP, show error to user.

**Step 8 — After Editor:** show Supabase URL, wait for user OK, then git push / YouTube / log / story bible update.

---

## Universal principles

- **Never from memory — read live rule files every run.** Rules change between sessions.
- **No visuals before `storyboard.json` is ready.** Scenarist first, everything else after.
- **Debug mode** — if the request contains "Debug mode" / «Отладочный режим», stop after each phase for approval. Details in `manager.md`.
- **Sub-agent cannot finish in one pass** — split: call it multiple times with explicit scene-index lists.

---

## Working directory note

All paths in `manager.md` and rule files are relative to `video-agent/`. When spawning sub-agents, always pass `OUTPUT_DIR` as an **absolute** path — sub-agents receive the same `cd video-agent` instruction, but `OUTPUT_DIR` must already be absolute to avoid ambiguity.

---

## File map

```
video-agent/
├── rules/
│   ├── roles/          manager.md (you), scenarist.md, storyboarder.md, animator.md, sound.md, editor.md
│   ├── formats/        16 format playbooks — serial-drama, news, reddit-story, what-if-real-life, ...
│   └── main/           budgets.md, fallback.md, validation.md, new-format-skill.md, new-title-skill.md
├── prompts/            scenarist.txt, storyboarder.txt, sound.txt, animator.txt, editor.txt
├── tools/              build_context.py, validate_storyboard.py, check_runtime.py,
│                       preflight_assets.py, check_final.py, fal-ai.md, ffmpeg-api.md
├── games/              per-game configs + story bibles
├── providers.json      active API providers/models
└── queue/              task queue scripts (worker path — not used for interactive runs)
```
