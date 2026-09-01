# Six Reddit Stories Production Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce two English Reddit Story videos each for Growtopia, Genshin Impact, and Star Trek Timelines, with a native story CTA beat and the game-owned CTA video appended to every final MP4.

**Architecture:** Each game is an independent production domain with its own story bible, gameplay assets, CTA, output folders, and two scripts. Reddit Story skips generated images and animation: script → TTS → gameplay/background/subtitles/CTA assembly. The manager performs a cross-game verification after all six local videos exist; publishing remains behind the mandatory explicit user review gate.

**Tech Stack:** JSON storyboards, fal.ai TTS, ready-made gameplay and Supabase assets, FFmpeg/ffprobe, Whisper ASS subtitles, Supabase Storage, YouTube queue scripts.

**Spec:** `video-agent/rules/formats/reddit-story.md`

## Global Constraints

- Work only in the existing Conductor workspace on branch `egor-version`; do not create another worktree.
- Preserve the pre-existing untracked migration `supabase/migrations/20260817000000_mark_reusable_assets_unapproved.sql` unchanged.
- Artifacts and story-bible entries are English; user-facing status is Russian.
- Narrative order is HEADLINE → HOOK → IDENTIFICATION → INJUSTICE → PRESSURE → HUMAN ACTION → REVEAL → JUSTICE RESOLUTION.
- Target narration is 45–68 seconds; final MP4 adds the game-owned CTA asset and remains approximately 47–70 seconds.
- Every script includes the approved native CTA beat. The CTA is not a separate voiced sales pitch.
- Every final video includes word-highlight subtitles and the exact Supabase CTA video owned by its game.
- Gameplay offsets must differ meaningfully from recent entries in the exact story bible.
- No upload, YouTube scheduling, logging, story-bible mutation, commit, or push before explicit user approval of the six final videos.

---

### Task 1: Growtopia Pair

**Files:**
- Read: `video-agent/games/growtopia/reddit-story_bible.json`
- Read: `video-agent/games/growtopia/reddit-story_special.md`
- Create: two run directories under `video-agent/output/2026-08-31/growtopia/reddit-story/`
- Create per run: `storyboard.json`, TTS/audio artifacts, subtitle artifacts, `final.mp4`

**Interfaces:**
- Consumes: approved topics below and Growtopia gameplay/background/CTA assets.
- Produces: two validated local MP4 paths and two proposed story-bible records, without mutating the bible.

- [ ] **Step 1: Create story A storyboard** — headline: “My sister accused me of ignoring her wedding—until she saw the world I had built.” The reveal is an accessible reception layout for their grandmother. Native CTA beat: Gems from the link in bio purchase the final decorative blocks.
- [ ] **Step 2: Validate story A** — check concrete relationship setup, false verdict, narrator flaw, human action, reveal, restored justice, native CTA, word count, and JSON validity.
- [ ] **Step 3: Generate story A TTS and assemble** — use approved voice policy, fresh gameplay offsets, static Reddit background, forced-aligned subtitles, and Growtopia CTA video.
- [ ] **Step 4: Verify story A final** — `ffprobe` must report portrait 1080×1920, audio present, sane duration, and file size above 100 KB; confirm final duration exceeds narration by the CTA duration.
- [ ] **Step 5: Repeat for story B** — headline: “My best friend accused me of stealing our rarest lock. The trade history exposed who actually took it.” Native CTA beat: Gems from the link in bio restore the damaged shared world after the moderator is exposed.
- [ ] **Step 6: Report both local outputs** — include paths, durations, CTA evidence, and any blockers; do not upload or edit the bible.

### Task 2: Genshin Impact Pair

**Files:**
- Read: `video-agent/games/genshin-impact/reddit-story_bible.json`
- Create: two run directories under `video-agent/output/2026-08-31/genshin-impact/reddit-story/`
- Create per run: `storyboard.json`, TTS/audio artifacts, subtitle artifacts, `final.mp4`

**Interfaces:**
- Consumes: approved topics below and Genshin gameplay/background/CTA assets.
- Produces: two validated local MP4 paths and two proposed story-bible records, without mutating the bible.

- [ ] **Step 1: Create story A storyboard** — headline: “My girlfriend thought I spent our rent money on Primogems. The bank statement made her cry.” Reveal: Primogems were free and the savings funded a visit to her mother. Native CTA beat: free Primogems from the link in bio are the evidence.
- [ ] **Step 2: Validate story A** — check complete justice structure, financial premise clarity without misleading claims, native CTA, word count, and JSON validity.
- [ ] **Step 3: Generate story A TTS and assemble** — use approved voice policy, fresh gameplay offsets, static Reddit background, forced-aligned subtitles, and Genshin CTA video.
- [ ] **Step 4: Verify story A final** — `ffprobe` must report portrait 1080×1920, audio present, sane duration, and file size above 100 KB; confirm final duration exceeds narration by the CTA duration.
- [ ] **Step 5: Repeat for story B** — headline: “My co-op team blamed the weakest player for ruining every run—until I recorded what our leader was doing.” Native CTA beat: free Primogems from the link in bio help the newcomer build a character without the toxic leader.
- [ ] **Step 6: Report both local outputs** — include paths, durations, CTA evidence, and any blockers; do not upload or edit the bible.

### Task 3: Star Trek Timelines Pair

**Files:**
- Read: `video-agent/games/star-trek-timelines/reddit-story_bible.json`
- Create: two run directories under `video-agent/output/2026-08-31/star-trek-timelines/reddit-story/`
- Create per run: `storyboard.json`, TTS/audio artifacts, subtitle artifacts, `final.mp4`

**Interfaces:**
- Consumes: approved topics below and Star Trek Timelines gameplay/background/CTA assets.
- Produces: two validated local MP4 paths and two proposed story-bible records, without mutating the bible.

- [ ] **Step 1: Create story A storyboard** — headline: “My manager caught me playing Star Trek during an airport shutdown. Then my fleet saved the terminal.” Reveal: international fleet members provide translation and family-contact help. Native CTA beat: the narrator met them after downloading the game through the link in bio.
- [ ] **Step 2: Validate story A** — check concrete fleet relationship setup, realistic scope of help, narrator flaw, restored justice, native CTA, word count, and JSON validity.
- [ ] **Step 3: Generate story A TTS and assemble** — use exact Star Trek voice policy, fresh gameplay offsets, static Reddit background, forced-aligned subtitles, and Star Trek CTA video.
- [ ] **Step 4: Verify story A final** — `ffprobe` must report portrait 1080×1920, audio present, sane duration, and file size above 100 KB; confirm final duration exceeds narration by the CTA duration.
- [ ] **Step 5: Repeat for story B** — headline: “My family said I was hiding inside my late mother’s game account. Then they heard what she left there.” Native CTA beat: the narrator downloads the game through the link in bio to understand her final crew clue.
- [ ] **Step 6: Report both local outputs** — include paths, durations, CTA evidence, and any blockers; do not upload or edit the bible.

### Task 4: Cross-Game Review and User Gate

**Files:**
- Verify: all six `storyboard.json` files and all six `final.mp4` files.
- Create: `.context/six-reddit-stories-2026-08-31-verification.json`

**Interfaces:**
- Consumes: outputs and proposed records from Tasks 1–3.
- Produces: one verification manifest and a review message containing all six clickable local files.

- [ ] **Step 1: Inventory outputs** — record game, topic, output path, file size, width, height, duration, audio stream count, narration CTA line, and final CTA asset for each video.
- [ ] **Step 2: Validate story contracts** — programmatically assert six unique headlines, six native CTA beats, six positive/neutral justice resolutions, and two videos per game.
- [ ] **Step 3: Validate media contracts** — run `ffprobe` for every final and fail the gate on missing audio, wrong orientation/resolution, undersized file, or duration outside the format allowance.
- [ ] **Step 4: Present local review gate** — report all six local paths and concise plot summaries, then wait for explicit user approval before any external publication or repository mutation.

### Task 5: Publish Approved Batch

**Files:**
- Modify after approval only: the three exact `reddit-story_bible.json` files.
- Use after approval only: `video-agent/queue/log-video.sh`, Supabase upload flow, and mapped YouTube upload scripts.

**Interfaces:**
- Consumes: explicit user approval plus the six verified local finals.
- Produces: six Supabase URLs, YouTube URLs/schedule entries where a channel is mapped, six log records, three updated story bibles, and a pushed commit.

- [ ] **Step 1: Upload all six approved finals to Supabase** — verify every public URL byte-for-byte or by the project’s upload validator.
- [ ] **Step 2: Schedule mapped channels** — schedule both Genshin videos on `genshinsnap` and both Star Trek videos on `starfleetarchive`; document Growtopia as Supabase-only unless its config gains a mapped channel.
- [ ] **Step 3: Log and update bibles** — append exact run metadata, topics, CTA angles, gameplay offsets, output paths, public URLs, and YouTube details.
- [ ] **Step 4: Verify and publish repository state** — validate JSON, inspect diff against `origin/main`, commit only intended files, push `egor-version`, and verify remote HEAD.
