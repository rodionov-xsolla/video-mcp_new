# Cost trial — Test 1: still shot (free)

**This is a cost-trial test, not a video run.** Skip the CLAUDE.md startup steps and phases.
Only local ffmpeg work. No paid API calls (no fal, no `kling_runner.py`, no `fal_runner.py`,
no `upload-asset.sh`), no Supabase writes, no git commits or pushes, nothing approved or published.
Never modify a baseline run folder. Everything you write goes under
`video-agent/output/_trials/2026-10-cost-trials/still-shot/`.

## Goal

For each baseline, make a copy of the run, replace one scene's clip with a "still shot" (a slow
eased pan or zoom over that scene's existing still, rendered by local ffmpeg), re-assemble the
copy's final video with the same assembly steps the editor used, and produce files for a blind review.

## Baselines and scenes (paths relative to `video-agent/output/`)

| id | run folder | scene | effect | notes |
|---|---|---|---|---|
| b0 | `2026-10-02/genshin-impact/redcon/20261002-171449-83169` | 1 | push-in | Kling clip, audio off. No `build/assemble.sh`; the filter graph is in `build/filter.txt`. Scene 1 motion includes mist/snow, which a still freezes. |
| b1 | `2026-10-09/star-trek-timelines/wild-documentary/20261009-134524-31003` | 1 | pan-right | Kling clip WITH native audio. Assembly is in `build/premix.sh`, `build/audio_graph.sh`, `build/final.sh` (check `premix.log` / `final-encode.log` for the order). |
| b2 | `2026-10-09/genshin-impact/item-story/20261009-135251-32050` | 7 | push-in | The pipeline already rendered scene 7 locally (some motion, no Kling). Use the still named in `storyboard.json` → `scene_image` (there is also a `scene-7-v2.png`). |
| b3 | `2026-10-09/star-trek-timelines/character-story/20261009-135906-33618-picard` | 6 | push-in | No scene-6 clip exists: `build/assemble.sh` holds `scenes/scene-6/scene-6.png` frozen with `-loop 1 -t 5.03`. Swap that input for the still-shot clip. |
| b4 | `2026-10-09/genshin-impact/in-game-pov/20261009-140239-35452` | 0 | push-in | Title-card establishing shot, Kling clip WITH native audio. `build/assemble.sh` has MODE `measure` then `encode` (two-pass loudnorm). |
| b5 | `2026-10-09/star-trek-timelines/what-if-real-life/20261009-140321-36049` | 6 | push-in | Rule check only: this scene contains a character, so it is NOT eligible in production. Shows why. `build/assemble.sh` uses `MODE=measure` then `MODE=final` with LN_* env vars. |

## Steps for each baseline

1. **Copy** the whole run folder to `output/_trials/2026-10-cost-trials/still-shot/<id>/`.
2. **Fix paths in the copy.** b3's `assemble.sh` does `cd` to the ORIGINAL folder, and b5 uses `cd "$OUT"`.
   Rewrite every reference to the original run folder in the copy's scripts to the copy's folder, then
   `grep` the copy's scripts to prove nothing points at the original run folder. References to
   `video-agent/tools/` (e.g. `overlays.py`) and the ffmpeg binary are fine.
3. **Keep the original scene clip** in the copy as `scenes/scene-K/scene-K.orig.mp4` (b3 has none).
4. **Render the still clip** to the copy's `scenes/scene-K/scene-K.mp4`. Match the original clip's
   duration and fps (`ffprobe` it; for b3 use 30 fps × 151 frames = 5.033 s). Set `D` = frame count:

   ```bash
   EASE="(0.5-0.5*cos(PI*on/$((D-1))))"
   ffmpeg -y -i "${STILL}" -vf "scale=4320:7680:force_original_aspect_ratio=increase:flags=lanczos,crop=4320:7680,zoompan=z='1+0.12*${EASE}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=${D}:s=1080x1920:fps=${FPS},format=yuv420p" -c:v libx264 -preset slow -crf 18 -an "${OUT}"
   ```

   Effects (replace the zoompan expressions): `push-in` as above; `pan-right` =
   `z='1.12':x='(iw-iw/zoom)*${EASE}':y='ih/2-(ih/zoom/2)'`; `pull-out` = `z='1.12-0.12*${EASE}'` with the push-in x/y; `pan-left` = `z='1.12':x='(iw-iw/zoom)*(1-${EASE})':y='ih/2-(ih/zoom/2)'`; `tilt-up` = `z='1.12':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-${EASE})'`; `tilt-down` = `z='1.12':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*${EASE}'`.
   Always use braces (`${VAR}`): zsh mangles `$VAR:` followed by a letter.
   **Audio:** if the original clip had an audio track (b1, b4), add a silent stereo track of the same
   duration and sample rate (`-f lavfi -i anullsrc=r=<rate>:cl=stereo -shortest -c:a aac`). That is honest:
   in production a still scene has no Kling sound. Do not copy the original clip's audio onto it.
5. **Re-assemble the copy** with the same scripts and passes the editor used. For b0 reconstruct the
   command from `build/filter.txt` and the run's files. If any assembly can't be reproduced exactly,
   don't improvise: skip that baseline's full video, still make its scene sheet (step 7), and report why.
6. **Verify:** the variant final's duration matches the baseline final (±0.05 s) and it has an audio track;
   each baseline's `final.mp4` sha256 is unchanged (record before and after).
7. **Scene sheet:** `review/<id>-scene-sheet.mp4`, the original scene clip and the still clip side by side
   (b3: the frozen PNG vs the still clip). Use the tested command with 2 inputs:

   ```bash
   FONT=/System/Library/Fonts/Supplemental/Arial.ttf
   L="scale=540:960:force_original_aspect_ratio=increase,crop=540:960,setsar=1,fps=24"
   ffmpeg -y -i A.mp4 -i B.mp4 -filter_complex "[0:v]${L},drawtext=fontfile=${FONT}:text=A:x=24:y=24:fontsize=56:fontcolor=white:borderw=3[a];[1:v]${L},drawtext=fontfile=${FONT}:text=B:x=24:y=24:fontsize=56:fontcolor=white:borderw=3[b];[a][b]hstack=inputs=2" -t 5 -c:v libx264 -crf 20 -an sheet.mp4
   ```

8. **Blind pair:** copy the baseline final and the variant final to `review/<id>-A.mp4` and `review/<id>-B.mp4`
   in a random order per baseline (use the same random order for that baseline's scene sheet). Write the
   answer key to `still-shot/key.json`. Do not print the key in your reply.

## Report back

A short table per baseline: done / skipped (and why), the review file paths, both durations, and anything
that differed from these instructions.
