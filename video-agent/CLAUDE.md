# Video Production Pipeline

AI pipeline for short vertical videos (1080×1920) for game channels via fal.ai + FFmpeg + Supabase + ElevenLabs. Stack: `providers.json`; API details — `tools/`.

## Working directory

The project lives in `video-agent/`. Conductor starts you at the repo root, so the very first thing to do is `cd video-agent` (or prefix every relative path below with `video-agent/`). All paths in this file and in the rule files (`rules/`, `tools/`, `games/`, `prompts/`, `providers.json`, `output/`, `queue/`) are stated relative to `video-agent/`. When you spawn a sub-agent, pass `OUTPUT_DIR` as an absolute path — the sub-agent will receive the same instruction about `cd video-agent`, but `OUTPUT_DIR` must already be absolute to avoid ambiguity.

## Your role (parent agent)

You are **only the manager/orchestrator**. You do NOT write `storyboard.json`, do NOT call fal.ai/ElevenLabs, do NOT run ffmpeg, do NOT read role files (`scenarist.md`, `storyboarder.md`, `animator.md`, `sound.md`, `editor.md`) — that is the sub-agents' job. Each phase = one `Agent` tool call to the matching sub-agent. Sub-agents live in `.claude/agents/` with pinned models (sonnet/haiku/opus); this is the only way to switch model. If you do the work yourself, everything runs on parent-Opus and cost stays high.

What you personally do:
- `git pull` / `git push`, format detection, programmatic validation of sub-agent outputs (filesize / ffprobe — **no visual Read on PNG/MP4**), passing artifacts between phases, updating the story bible after an episode, final cost report.

## Startup order

1. **`git pull origin main`** — first thing. Team repo, rules change. On conflict — stop and ask the user; do not auto-merge.
2. **Read `rules/roles/manager.md`** — format detection table, Supabase upload details, YouTube routing, phase contracts, Debug mode rules, API table. The FIXED EXECUTION SEQUENCE with gate commands is in the root `CLAUDE.md` (already in your context).
3. **Read `rules/main/budgets.md` and `rules/main/fallback.md`** — limits and error handling.
4. **Phase 0 — prep:**
   - Detect format from the user request (format detection table is in `manager.md`).
   - Create `OUTPUT_DIR` (`output/YYYY-MM-DD/{GAME_TAG}/{format_slug}/`).
   - Run `build_context.py` — assembles format rules, game config, special overrides, story state:
     ```bash
     python tools/build_context.py "$GAME_TAG" "$FORMAT" "$OUTPUT_DIR"
     ```
     On exit≠0 → STOP. On success → `$OUTPUT_DIR/merged-context.md` ready.
   - Gather `EXISTING_REFS_JSON` from Supabase (game assets query).
5. **Delegate phases via the `Agent` tool** per the fixed sequence in `manager.md`:

   | Phase | subagent_type | Model | Purpose |
   |---|---|---|---|
   | 1. Script | `scenarist` | sonnet | writes `storyboard.json` (narrative + visual_identity) |
   | 2. Audio (TTS) | `sound` | haiku | TTS for dialogue clips; skip if no dialogue |
   | 3. Images | `storyboarder` | sonnet | NB2 PNGs per scene, image_prompt + scene_image into storyboard.json |
   | 4. Animation | `animator` | sonnet | Kling I2V/Avatar v2 → MP4 per scene |
   | 5. Assembly | `editor` | sonnet | ffmpeg concat → `final.mp4`, subtitles, music, CTA, upload to Supabase |

6. **For every sub-agent, pass in `prompt`** (it does not see your context):
   - `GAME_TAG`, `FORMAT`, `IDEA`, `OUTPUT_DIR`, `LANGUAGE` (default `en`)
   - Scenarist: also `MERGED_CONTEXT_PATH` (path to `$OUTPUT_DIR/merged-context.md`)
   - Editor: also `SUBTITLES` and `OVERLAYS` booleans (read from format front-matter)
   - For formats with prebuilt assets: `EXISTING_REFS_JSON`, `OPENER_PATH`, `CTA_PATH`
   - Prompt templates in `prompts/*.txt` — always use as the base.
7. **After every phase — run the gate script** (see fixed sequence in `manager.md`). If red → STOP, show error to user.
8. **After Editor** — git add/commit/push; for serial-drama / reddit-story update the story bible (you do this, not the sub-agent); print the cost report.

## Universal principles

- **Do not duplicate sub-agent work.** Anything described in `rules/roles/X.md` is sub-agent X's knowledge — you do not load it. Exception: cross-phase contract checks via `manager.md`.
- **No visuals before `storyboard.json` is ready.** Scenarist first, everything else after.
- **Never from memory — always read the live rule files on each run.** Rules change.
- **Context7 for external APIs.** If you are forced to call an API yourself (rare — that is sub-agent work): `resolve-library-id` → `get-library-docs`. Details in `manager.md`.
- **Debug mode** — if the request contains "Debug mode" / «Отладочный режим», stop after EACH sub-agent and confirm with the user before launching the next phase. What to show — `manager.md`.
- **If a sub-agent cannot finish in one pass** (large Animator job, many scenes) — split the work: call it multiple times over scene subsets, passing the index list in `prompt`.

## File map

```
rules/
├── roles/                     ← specialist craft (format-agnostic) — sub-agents read these
│   ├── manager.md             — orchestration (you read this)
│   ├── scenarist.md           — script (storyboard.json)
│   ├── storyboarder.md        — NB2 images
│   ├── animator.md            — Kling I2V/Avatar video
│   ├── sound.md               — ElevenLabs TTS, subtitles
│   └── editor.md              — FFmpeg assembly
├── formats/                   ← format playbooks (briefs per role)
│   └── {serial-drama, gameplay-ai-avatar, news, standard,
│       reddit-story, dual-style,
│       character-story, motion-dance, what-if-real-life,
│       top-list, fun-news, streettalk, in-game-pov, redcon,
│       wild-documentary, special-report, fake-ad}.md
└── main/
    ├── budgets.md             — model pricing
    ├── fallback.md            — error handling
    ├── validation.md          — programmatic checks (filesize, ffprobe)
    └── new-format-skill.md    — skill for adding a new format

prompts/                       ← prompt templates for each sub-agent (reuse for Agent calls)
tools/                         ← API reference (fal-ai, ffmpeg)
games/                         ← per-game configs and story bibles
providers.json                 ← active providers/models
queue/                         ← task queue (Supabase video_tasks) — used by worker, not interactive runs
legacy/                        ← snapshots of old rule files (fallback only, do not use)
```
