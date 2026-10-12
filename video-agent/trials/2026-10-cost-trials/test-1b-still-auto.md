# Cost trial — Test 1b: automatic still selection (free)

**This is a cost-trial test, not a video run.** Skip the CLAUDE.md startup steps and phases.
No paid generation calls (no fal, no `kling_runner.py`, no `fal_runner.py`, no `upload-asset.sh`),
no Supabase writes, no git commits or pushes, nothing approved or published. Never modify a baseline
run folder. Write only under `video-agent/output/_trials/2026-10-cost-trials/still-auto/`.

## Goal

Test whether the **scenarist**, given a still-shot rule, picks the right scenes on its own. For each
baseline, the scenarist chooses 0–2 scenes to become still shots, with an effect. Then build the full
video with those choices and report how much Kling spend the choices would have saved.

## Baselines (paths relative to `video-agent/output/`)

| id | run folder |
|---|---|
| b0 | `2026-10-02/genshin-impact/redcon/20261002-171449-83169` |
| b1 | `2026-10-09/star-trek-timelines/wild-documentary/20261009-134524-31003` |
| b2 | `2026-10-09/genshin-impact/item-story/20261009-135251-32050` |
| b3 | `2026-10-09/star-trek-timelines/character-story/20261009-135906-33618-picard` |
| b4 | `2026-10-09/genshin-impact/in-game-pov/20261009-140239-35452` |
| b5 | `2026-10-09/star-trek-timelines/what-if-real-life/20261009-140321-36049` |

## Step 1 — the scenarist chooses (one call per baseline)

For each baseline, call the `scenarist` sub-agent with the `Agent` tool (synchronously, never in the
background). Give it, in the prompt:

- the game, the format, and the video's title or idea;
- **only Phase-1 fields** for every scene, copied from the baseline's `storyboard.json`: `index`,
  `clip_type`, `beats`, `action_description`, `character_state`, `facial_expression`,
  `character_speech`, `tts_segment`, `environment_state`, `camera_angle`, `title_lines`.
  Do **not** pass `motion_prompt`, image prompts, image URLs or any file paths. In production the
  scenarist decides before those exist;
- the rule below, word for word;
- this instruction: *"This is an evaluation task. Do not read or write any files and do not run
  commands. Reply with JSON only."*

### The rule (draft scenarist rule under test)

> **Still shots.** A still shot replaces a scene's animation with a slow camera move over that scene's
> still image, rendered for free. It saves the scene's whole animation cost, so use it wherever it does
> not hurt the video, but never at the cost of quality.
>
> Score every scene's intended motion:
> - **0** — nothing in the frame moves; any motion is camera-only (a slow drift, pan or push over a static
>   scene): empty locations, landscapes, establishing shots, objects at rest, maps, documents.
> - **1** — minimal ambient motion a viewer would not miss if frozen (faint dust, distant tiny details),
>   with no character's face or body in focus.
> - **2** — clearly visible environmental motion (mist, snow, rain, water, fire, smoke, flags, crowds), or
>   a character present even if mostly still.
> - **3** — character action, facial performance, dialogue, lip-sync, or a scene whose point is movement.
>
> Choose **0, 1 or 2** scenes per video. Only scenes scoring 0 or 1; prefer 0. Never a scene with
> character speech or lip-sync. Never the action peak or climax. Never two still shots in a row. Prefer
> openers, location changes, transitions and pauses before a reveal. Choosing none is correct when no
> scene qualifies.
>
> Pick the effect from the scene's intent:
> - **push-in** — moving toward a subject or detail; building tension; focusing attention.
> - **pull-out** — revealing scale; endings and aftermath; leaving a place.
> - **pan-right** — wide landscapes and horizontal compositions; sweeping across a location.

### Required reply (JSON only)

```json
{
  "scores": [{"index": 1, "motion": 0, "why": "one short sentence"}],
  "stills": [{"index": 1, "effect": "push-in", "reason": "one short sentence"}]
}
```

Save each reply to `still-auto/<id>/selection.json`. Validate it programmatically: at most 2 stills,
every still has motion score 0 or 1, no still has `character_speech`, no two stills are adjacent, and
the effect is one of push-in, pull-out, pan-right. If a reply breaks a rule, call the scenarist once
more with the error. If it still breaks a rule, record the violation and drop the offending stills.

## Step 2 — build the videos

For each baseline that has at least one still, do steps 1–7 of `test-1-still-shot.md`. Those steps
cover the copy, the path fixes, keeping the originals, rendering, silent audio for audio-on clips,
re-assembly and verification. Use these values instead:

- output under `still-auto/<id>/` and `still-auto/review/`;
- the scenes and effects from that baseline's `selection.json`, which may be up to 2 scenes;
- one scene sheet per selected scene: `review/<id>-scene-<K>-sheet.mp4`, original on the left labelled
  `KLING`, still on the right labelled `STILL`. This test is about the choice, not blind judging;
- the full videos as `review/<id>-original.mp4` and `review/<id>-auto-still.mp4`. No blind A/B.

Baselines where the scenarist chose no scenes get no video, only their `selection.json`.

## Step 3 — savings

For each selected scene, look up the baseline's video job for that scene (`build/video/jobs/`).
Kling v3 Standard costs $0.084/s with audio off and $0.126/s with audio on, times the job's duration.
A scene with no Kling I2V job saves $0, because it was never a paid clip. Also compute each baseline's
total Kling I2V spend from its jobs, so the saving can be shown as a percentage.

## Report back

1. Per baseline: every scene's motion score with its one-line "why", the chosen stills (scene, effect,
   reason), any rule violation, and the review file paths.
2. A savings table: baseline, Kling I2V spend, saved by the chosen stills, % saved.
3. Anything that differed from these instructions.
