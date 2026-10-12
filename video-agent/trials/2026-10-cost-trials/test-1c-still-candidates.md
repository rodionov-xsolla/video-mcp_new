# Cost trial — Test 1c: mark all still candidates, then review and choose (free)

**This is a cost-trial test, not a video run.** Skip the CLAUDE.md startup steps and phases.
No paid generation calls (no fal, no `kling_runner.py`, no `fal_runner.py`, no `upload-asset.sh`),
no Supabase writes, no git commits or pushes, nothing approved or published. Never modify a baseline
run folder. Write only under `video-agent/output/_trials/2026-10-cost-trials/still-candidates/`.
Skip any Neuronet code search; this repo is not indexed there.

## Goal

Test 1b chose only one still per video. This test checks whether a two-step process finds more
savings without hurting quality: the scenarist first marks **every** scene that could be a still,
then reviews those candidates and chooses the final stills under a cap.

## Baselines (paths relative to `video-agent/output/`)

| id | run folder |
|---|---|
| b0 | `2026-10-02/genshin-impact/redcon/20261002-171449-83169` |
| b1 | `2026-10-09/star-trek-timelines/wild-documentary/20261009-134524-31003` |
| b2 | `2026-10-09/genshin-impact/item-story/20261009-135251-32050` |
| b3 | `2026-10-09/star-trek-timelines/character-story/20261009-135906-33618-picard` |
| b4 | `2026-10-09/genshin-impact/in-game-pov/20261009-140239-35452` |
| b5 | `2026-10-09/star-trek-timelines/what-if-real-life/20261009-140321-36049` |

## Inputs for every scenarist call

Call the `scenarist` sub-agent with the `Agent` tool, synchronously, never in the background. Pass the game,
the format, the video's title or idea, and **only Phase-1 fields** for every scene from the baseline's
`storyboard.json`: `index`, `clip_type`, `beats`, `action_description`, `character_state`,
`facial_expression`, `character_speech`, `tts_segment`, `environment_state`, `camera_angle`,
`title_lines`. Do **not** pass `motion_prompt`, image prompts, image URLs or file paths. In production
the scenarist decides before those exist. Add: *"This is an evaluation task. Do not read or write any
files and do not run commands. Reply with JSON only."*

## The rule (draft scenarist rule under test, pass it word for word in every call)

> **Still shots.** A still shot replaces a scene's animation with a slow camera move over that scene's
> still image, rendered for free. It saves that scene's entire animation cost. Use it wherever it does not
> hurt the video, never at the cost of quality.
>
> **Savings are not available in every video.** Many videos have no eligible scene: fast action,
> first-person footage, and dialogue- or character-driven stories must stay fully animated. Choosing zero
> stills is a normal, correct result. Never lower the quality bar to find a saving.
>
> **Impact score**: what freezing the scene would cost the viewer. Judge what a viewer would notice and
> lose, not how much changes on screen. A flickering fire changes many pixels but tells nothing; a camera
> rising to reveal a second object changes fewer pixels but is the point of the shot.
> - **0**: nothing is lost. Nothing in the frame moves, or the only motion is a camera move a still
>   effect reproduces. Empty locations, landscapes, establishing shots, objects at rest, maps, documents.
> - **1**: only atmosphere is lost. Decorative motion that adds life but no information: fire and flame
>   flicker, embers, an aura or glow, mist, smoke, rain, drifting particles, light flicker, or anonymous
>   hands simply holding or adjusting a grip with no face shown. The still's camera move keeps it alive.
> - **2**: a noticeable but secondary loss. A dominant moving element that will clearly read as frozen (a
>   crashing wave, a crowd, a flag filling the frame), or a small action beat that is not the scene's point.
> - **3**: information or performance is lost. The motion tells the story: a reveal or transition (the
>   camera travels to show a new subject or place), an action that changes the situation, a character's
>   face or performance, dialogue or lip-sync.
>
> **Camera-move match.** If a scene's intended motion is mainly a camera move that a still effect
> can reproduce (a push-in, pull-out, pan, tilt or slow drift over the same subject), it is a strong
> candidate: score its impact by what moves *inside* the frame, not by the camera move. "The camera slowly
> pushes in on the empty shrine" is impact 0, even though it is written as animation. A camera move that
> travels to reveal a new subject or place is different: it carries information, so it is impact 3.
>
> **Depth check (parallax).** A still effect is a flat 2D move. It imitates a camera that turns or
> zooms in place, but not a camera that travels past things at different distances, where near objects
> slide past faster than far ones.
> - **Good fit:** compositions with little depth, or where everything is far away: landscapes, skylines,
>   wide establishing shots, flat subjects (walls, maps, documents, screens, paintings), and objects in
>   close-up against a plain or blurred background.
> - **Depth is a risk flag, not a disqualifier:** the camera travels past things (a crane, a dolly, moving
>   past pillars, trees or railings), or a strong foreground object sits close to the camera in front of a
>   distant background. Such a scene can still be a candidate, with risk `medium`; the review step decides.
>   Exclude only a true fly-through, where moving through the space is the entire point of the shot.
> - **Rate every scene's depth:** `flat`, `some` or `deep`. A scene rated `some` or `deep` must use
>   push-in or pull-out, never a pan or tilt: a zoom is where a flat image differs least from a real
>   camera. It is rendered with a gentler move, so the missing parallax shows less.
>
> **Effect**, chosen to match the scene's camera move, or the shot if none is described:
> - **push-in**: moving toward a single subject or detail; building tension; focusing attention.
> - **pull-out**: revealing scale; endings and aftermath; leaving a place.
> - **pan-right** / **pan-left**: wide or horizontal compositions; sweeping across a location.
> - **tilt-up** / **tilt-down**: tall compositions; rising up to or down from a subject (a crane move).
> When a video has more than one still, do not use the same effect twice in a row.

## Call 1: mark every candidate

Ask the scenarist to score every scene and mark **every** scene that could work as a still:

- impact 0 or 1: always a candidate;
- impact 2: a candidate only if the moving element is small, in the background, or would not be missed if
  frozen, with risk `medium`;
- impact 3, or any scene with character speech or lip-sync: never a candidate.

Reply:

```json
{"scenes": [{"index": 1, "impact": 0, "candidate": true, "risk": "low|medium|none",
             "story_role": "opener|establishing|transition|pause|build-up|climax|ending|other",
             "depth": "flat|some|deep",
             "effect": "push-in|pull-out|pan-right|pan-left|tilt-up|tilt-down|null", "why": "one short sentence"}]}
```

Save it to `still-candidates/<id>/candidates.json`.

## Call 2: review and choose

Send the scenarist its own candidate list from call 1 and ask it to review the candidates and choose the
final stills:

- **cap:** at most `round(N / 3)` stills, where N is the number of scenes, and never more than 3;
- prefer impact 0, then 1, then medium-risk 2; drop a candidate if freezing it would be noticed;
- never a climax; prefer to spread stills through the video. Two stills in a row are allowed only when
  both score 0 or 1 and they use different effects; never when either is a medium-risk impact-2 scene;
- the effects follow the rule above, with no repeat in a row;
- zero is allowed.

Reply:

```json
{"stills": [{"index": 1, "effect": "pan-right", "reason": "one short sentence"}],
 "rejected": [{"index": 4, "why_not": "one short sentence"}]}
```

Save it to `still-candidates/<id>/selection.json`. Validate programmatically: count within the cap, every
still was a candidate in call 1, no character speech, no `climax` role, effect is allowed and not
repeated in a row, and adjacent stills both score 0 or 1. On a violation, call the scenarist once more with the error. If it
still fails, record the violation and drop the offending stills.

## Call 3 (optional): convert one animated scene

Only if call 2 chose **no stills at all**, send the scenarist its scenes and ask whether **one** of them could be rewritten as a still shot without hurting the video. In production
this is the step where the scenarist designs a scene for a still before anything is generated. Rules:

- at most **1** conversion per video, and the total number of stills stays within the cap;
- only a scene whose motion is decorative, not its point; never a scene with a character in focus,
  dialogue, lip-sync, or the `climax` role;
- the rewritten scene must be a camera-only shot that passes the depth check (little depth, nothing
  travelling past the camera);
- the same adjacency and effect rules as call 2;
- when in doubt, convert nothing; zero conversions is a normal result.

Reply:

```json
{"conversions": [{"index": 6, "effect": "pull-out",
                  "new_action_description": "the scene rewritten as a camera-only shot",
                  "why_safe": "one short sentence"}]}
```

Save it to `<id>/conversions.json`, even when the list is empty. Validate it like call 2, plus the
1-conversion limit. On these fixed baselines the conversion is rendered from the scene's existing still,
which was made for animation. That is the worst case: in production the still itself would be generated
from the rewritten, calmer description.

## Build the videos

For each baseline with at least one still, follow steps 1–6 of `test-1-still-shot.md`: copy, fix paths,
keep originals, render each still (silent audio track for audio-on clips), re-assemble, verify. Use
`still-candidates/<id>/` and the scenes and effects from `selection.json` plus `conversions.json`. For a still whose scene is rated `some` or `deep` in `candidates.json`, render a
gentler move: a 7% zoom instead of 12% (push-in `z='1+0.07*${EASE}'`, pull-out
`z='1.07-0.07*${EASE}'`, both with the push-in x/y). Then make one full-length
side-by-side video per baseline, `still-candidates/review/<id>-full-side-by-side.mp4`. Use this command,
already tested on this machine, with one `drawtext` enable window per still scene. Find each window as
the stretch where the two videos differ (frame PSNR < 40 between them):

```bash
FONT=/System/Library/Fonts/Supplemental/Arial.ttf
L="scale=540:960:force_original_aspect_ratio=increase,crop=540:960,setsar=1"
ffmpeg -y -i ORIGINAL.mp4 -i STILL.mp4 -filter_complex "[0:v]${L},drawtext=fontfile=${FONT}:text=ANIMATED:x=20:y=20:fontsize=40:fontcolor=white:borderw=3[l];[1:v]${L},drawtext=fontfile=${FONT}:text=STILL:x=20:y=20:fontsize=40:fontcolor=white:borderw=3,drawtext=fontfile=${FONT}:text='STILL SCENE':x=(w-text_w)/2:y=h-90:fontsize=44:fontcolor=yellow:borderw=4:enable='between(t,A1,B1)+between(t,A2,B2)'[r];[l][r]hstack=inputs=2[v]" -map "[v]" -map 1:a -c:v libx264 -crf 21 -preset veryfast -c:a aac -b:a 160k OUT.mp4
```

The shell is zsh: always use `${VAR}` and don't rely on word-splitting unquoted variables.

## Savings

For each still, look up the baseline's video job for that scene in `build/video/jobs/`. Kling v3 Standard
costs $0.084/s with audio off and $0.126/s with audio on, times the job's duration. A scene with no
Kling I2V job saves $0. Also compute each baseline's total Kling I2V spend, to show the saving as a %.

## Report back

1. Per baseline: every scene's impact score, candidate flag, risk and story role; the chosen stills with
   effect and reason; the rejected candidates with why-not; any conversion with its rewritten description and
   why it is safe; any rule violation.
2. A savings table: baseline, Kling I2V spend, saved, % saved, compared with the first 1c run's choices
   (b0: scenes 1 and 7, b1: scene 1, b2: scenes 3 and 7, b3: scene 6, b4: scene 0, b5: none), which averaged 10.5% saved per whole video. List each still's depth rating and whether it used the gentle move.
3. The review file paths, and anything that differed from these instructions.
