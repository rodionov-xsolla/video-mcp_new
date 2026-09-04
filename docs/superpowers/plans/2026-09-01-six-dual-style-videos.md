# Six Dual-Style Videos Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce six approved `dual-style-v3` videos: two each for Genshin Impact, Growtopia, and Star Trek Timelines.

**Architecture:** Each game is an independent production task containing two sequential video runs. Every run follows the repository pipeline (`scenarist -> sound -> storyboarder -> animator -> editor`), receives programmatic validation after each phase, and stops at the local review gate before publication. Runs are executed sequentially because all games share the same constrained APFS volume and provider state.

**Tech Stack:** Repository video-agent rules, Nano Banana 2 via `fal_runner.py`, Kling v3 Standard via `kling_runner.py`, MiniMax Music v2.6, FFmpeg, Supabase assets.

**Spec:** `video-agent/rules/formats/dual-style.md`

## Global Constraints

- Use `format: "dual-style"` and `production_contract: "dual-style-v3"`.
- Genshin Impact and Growtopia use `comparison_mode: "source-vs-live-action"`; Star Trek Timelines uses `comparison_mode: "canonical-alternate"`.
- Every clip is 5 seconds, has synchronized forward walking toward a front-facing retreating camera, `character_speech: null`, `generate_audio: true`, `sfx: false`, and one-entry `multi_prompt`.
- No subtitles. No promo popup. Append the exact game-owned animated CTA to every final video.
- Generate one new instrumental MiniMax track per video; preserve clean diegetic ambience and music through the CTA.
- Maximum generation spend is $5.00 per video; stop before the next paid generation if spend exceeds $4.50.
- Preserve the untracked user migration `supabase/migrations/20260817000000_mark_reusable_assets_unapproved.sql` unchanged.
- Do not upload, schedule YouTube, mutate story bibles, commit, or push until the user explicitly approves the local finals.
- Keep `storyboard.json`, accepted scene artifacts, and `final.mp4`; remove only regenerable run-owned assembly intermediates when disk pressure requires it.

---

### Task 1: Genshin Impact Pair

**Files:**
- Create: `video-agent/output/2026-09-01/genshin-impact/dual-style/<run-id>/storyboard.json`
- Create: `video-agent/output/2026-09-01/genshin-impact/dual-style/<run-id>/scenes/`
- Create: `video-agent/output/2026-09-01/genshin-impact/dual-style/<run-id>/final.mp4`
- Read: `video-agent/games/genshin-impact/dual-style_story_bible.json`

**Interfaces:**
- Consumes: approved cast lists and exact Genshin dual-style bible/CTA.
- Produces: two validated local 1080x1920 MP4 files and per-run cost evidence.

- [ ] **Step 1:** Run Phase 0 for both concepts, verify cast/actor cooldown and resolve exact game-owned CTA/assets.
- [ ] **Step 2:** Produce and validate “Archons & Fatui” with Raiden Shogun/Gal Gadot, Tartaglia/Tom Holland, Furina/Florence Pugh, and Arlecchino/Eva Green.
- [ ] **Step 3:** Produce and validate “Teyvat’s Elite” with Wriothesley/Henry Cavill, Yae Miko/Margot Robbie, Neuvillette/Timothée Chalamet, and Navia/Sydney Sweeney.
- [ ] **Step 4:** Run `jq`, file-size, stream, resolution, start-time, duration, CTA-tail, and loudness checks on both finals; record the exact commands and outputs.

### Task 2: Growtopia Pair

**Files:**
- Create: `video-agent/output/2026-09-01/growtopia/dual-style/<run-id>/storyboard.json`
- Create: `video-agent/output/2026-09-01/growtopia/dual-style/<run-id>/scenes/`
- Create: `video-agent/output/2026-09-01/growtopia/dual-style/<run-id>/final.mp4`
- Read: `video-agent/games/growtopia/dual-style_story_bible.json`

**Interfaces:**
- Consumes: approved new cast additions, exact Growtopia dual-style bible/CTA, and canonical source references.
- Produces: two validated local 1080x1920 MP4 files and per-run cost evidence.

- [ ] **Step 1:** Extend only the run-local proposed cast with Dragon Set, Chef Set, Adventurer Set, A Burglar, Locke the Salesman, and Mark the Mechanic; do not mutate the bible before approval.
- [ ] **Step 2:** Produce and validate “Growtopia Jobs in Real Life” with generic non-celebrity photorealistic adult performers on the right.
- [ ] **Step 3:** Produce and validate “Growtopia Street Legends” with generic non-celebrity photorealistic adult performers on the right.
- [ ] **Step 4:** Run `jq`, file-size, stream, resolution, start-time, duration, CTA-tail, and loudness checks on both finals; record the exact commands and outputs.

### Task 3: Star Trek Timelines Pair

**Files:**
- Create: `video-agent/output/2026-09-01/star-trek-timelines/dual-style/<run-id>/storyboard.json`
- Create: `video-agent/output/2026-09-01/star-trek-timelines/dual-style/<run-id>/scenes/`
- Create: `video-agent/output/2026-09-01/star-trek-timelines/dual-style/<run-id>/final.mp4`
- Read: `video-agent/games/star-trek-timelines/dual-style_story_bible.json`

**Interfaces:**
- Consumes: approved canonical pairs, exact Star Trek dual-style bible/CTA, and source-verified persona references.
- Produces: two validated local 1080x1920 MP4 files and per-run cost evidence.

- [ ] **Step 1:** Verify each original/alternate persona against canonical sources and extend only the run-local proposed pair pool.
- [ ] **Step 2:** Produce and validate “Same Face, Different Fate” with Riker/Thomas Riker, The Doctor/Warship Doctor, Kes/Warlord Kes, and Odo/Mirror Odo.
- [ ] **Step 3:** Produce and validate “DS9: Dark Reflections” with Dukat/Pah-wraith Dukat, Garak/Mirror Garak, Jadzia Dax/Mirror Jadzia, and Bareil/Mirror Bareil.
- [ ] **Step 4:** Run `jq`, file-size, stream, resolution, start-time, duration, CTA-tail, overlay-title, and loudness checks on both finals; record the exact commands and outputs.

### Task 4: Batch Review Gate

**Files:**
- Create: `.context/six-dual-style-final-verification.json`
- Create: `.context/six-dual-style-cost-report.md`

**Interfaces:**
- Consumes: all six local final MP4 files and their storyboards/provider state.
- Produces: one verification manifest and one itemized cost report for user review.

- [ ] **Step 1:** Verify all six final paths exist and each contains 1080x1920 H.264 video plus AAC audio with `start_time=0`.
- [ ] **Step 2:** Verify every storyboard matches the selected comparison mode and all `dual-style-v3` hard gates.
- [ ] **Step 3:** Calculate images, video, and music spend for each run and the six-video total.
- [ ] **Step 4:** Present all six local finals to the user and stop before any publication or story-bible mutation.
