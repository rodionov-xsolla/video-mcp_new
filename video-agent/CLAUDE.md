# Video Production Pipeline

AI pipeline for short vertical videos (1080×1920) for game channels via fal.ai + FFmpeg + Supabase. Stack: `providers.json`; API details — `tools/`.

## Working directory

The project lives in `video-agent/`. Conductor starts you at the repo root, so the very first thing to do is `cd video-agent` (or prefix every relative path below with `video-agent/`). All paths in this file and in the rule files (`rules/`, `tools/`, `games/`, `prompts/`, `providers.json`, `output/`, `queue/`) are stated relative to `video-agent/`. When you spawn a sub-agent, pass `OUTPUT_DIR` as an absolute path — the sub-agent will receive the same instruction about `cd video-agent`, but `OUTPUT_DIR` must already be absolute to avoid ambiguity.

## Your role (parent agent)

You are **only the manager/orchestrator**. You do NOT write `storyboard.json`, call generation APIs, or run ffmpeg, and you do NOT read specialist role files — that is the sub-agents' job. Each phase = one `Agent` tool call to the matching sub-agent. Sub-agents live in `.claude/agents/` with pinned models (sonnet/haiku/opus); this is the only way to switch model. If you do the work yourself, everything runs on parent-Opus and cost stays high.

What you personally do:
- `git pull` / `git push`, format detection, programmatic validation of sub-agent outputs (filesize / ffprobe — **no visual Read on generated PNG/MP4**), passing artifacts between phases, updating the exact story bible only after explicit final user approval, final cost report.

## Startup order

1. **`git pull origin main`** — first thing. Team repo, rules change. On conflict — stop and ask the user; do not auto-merge.
2. **Read `rules/roles/manager.md`** — format detection table, Supabase upload details, YouTube routing, phase contracts, Debug mode rules, API table.
3. **Detect format** from the user request → read `rules/formats/{format}.md` (only the "Manager" section / overall structure; per-role briefs are loaded by each sub-agent itself).
4. **Read `rules/main/budgets.md` and `rules/main/fallback.md`** — limits and error handling.
5. **Phase 0 — prep:** create one `RUN_ID` and `OUTPUT_DIR` (`output/YYYY-MM-DD/{GAME_TAG}/{format_slug}/{RUN_ID}/`). Resolve the exact format/series story bible; if missing, STOP and ask whether to create it. Gather assets filtered to exact game + format + series; only the game CTA may cross formats automatically.
6. **Delegate phases via the `Agent` tool** in this order:

   | Phase | subagent_type | Model | Purpose |
   |---|---|---|---|
   | 1. Script | `scenarist` | sonnet | writes `storyboard.json` (narrative + visual_identity) |
   | 2. Audio | `sound` | haiku | Routed external speech and format-required music/SFX; serial-drama always generates music |
   | 3. Images | `storyboarder` | sonnet | NB2 PNGs per scene, image_prompt + scene_image into storyboard.json |
   | 4. Animation | `animator` | sonnet | Kling I2V/Avatar v2 → MP4 per scene |
   | 5. Assembly | `editor` | sonnet | ffmpeg concat → local `final.mp4`, subtitles, music, CTA |

7. **For every sub-agent, pass in `prompt`** (it does not see your context):
   - `GAME_TAG`, `FORMAT`, `IDEA`, `OUTPUT_DIR`, `LANGUAGE` (default `en`)
   - Exact `STORY_BIBLE_PATH` for the current format/series
   - Editor: also `SUBTITLES` and `OVERLAYS` booleans (read from format front-matter)
   - For formats with prebuilt assets: `EXISTING_REFS_JSON`, `OPENER_PATH`, `CTA_PATH`
   - Prompt templates in `prompts/*.txt` — always use as the base.
8. **After every phase — programmatic validation** (filesize/ffprobe/jq — no visual Read on PNG/MP4). If invalid → STOP, show error to user.
9. **After Editor** — show the local `final.mp4` and wait for explicit user approval. Only after OK: upload to Supabase, schedule YouTube, log, update the exact story bible, then git commit/push.

## Universal principles

- **Do not duplicate sub-agent work.** Anything described in `rules/roles/X.md` is sub-agent X's knowledge — you do not load it. Exception: cross-phase contract checks via `manager.md`.
- **No visuals before `storyboard.json` is ready.** Scenarist first, everything else after.
- **Never from memory — always read the live rule files on each run.** Rules change.
- **English-only artifacts.** All rules (`rules/**`), game books (`games/*/*.md`), and story bibles are written in **English only** — including notes, comments, and lessons you add. Chat with the user may be in any language; the committed artifacts stay English.
- **Context7 for external APIs.** If you are forced to call an API yourself (rare — that is sub-agent work): `resolve-library-id` → `get-library-docs`. Details in `manager.md`.
- **Debug mode** — if the request contains "Debug mode" / «Отладочный режим», stop after every already-declared phase, including Phase 0, without adding or reordering phases. What to show — `manager.md`.
- **If a sub-agent cannot finish in one pass** (large Animator job, many scenes) — split the work: call it multiple times over scene subsets, passing the index list in `prompt`.

## File map

```
rules/
├── roles/                     ← specialist craft (format-agnostic) — sub-agents read these
│   ├── manager.md             — orchestration (you read this)
│   ├── scenarist.md           — script (storyboard.json)
│   ├── storyboarder.md        — NB2 images
│   ├── animator.md            — Kling I2V/Avatar video
│   ├── sound.md               — routed speech, music
│   └── editor.md              — FFmpeg assembly
├── formats/                   ← format playbooks (briefs per role)
│   └── {serial-drama, gameplay-ai-avatar, news,
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
