# Storyboarder production lessons — non-normative archive

This file preserves incident history and rationale removed from the canonical Storyboarder
contract. It is not loaded during normal production. The normative rules are only in
`rules/roles/storyboarder.md` and the active format's Storyboarder brief.

## Identity and anatomy

- ROOM 1701 scenes 5/6: missing identity refs produced random stand-ins and broke voice
  ownership. Distilled rule: every identity-critical visible character needs an eligible ref.
- Roblox Streettalk EP1: tight microphone framing dropped a reporter arm; an interviewee was
  pushed off-center and looked away from the microphone. Distilled rule: specify grip,
  visible-limb pose, centered placement, and gaze target when those details matter.
- Genshin Dual Style EP6: a weak "held bow" phrase produced a detached/floating weapon.
  Distilled rule: describe explicit hand-to-prop contact.
- Serial Drama EP7 controlled repeats: identical prompt and refs sometimes duplicated a
  background character. Distilled rule: bind each ref to role/position, while recognizing
  that generation remains stochastic.
- Star Trek Serial Drama EP13: nominal character names and inconsistent ref paths encouraged
  duplicate/drifting faces. Distilled rule: use physical identity blocks and one locked URL.

## Location, scale, and continuity

- Roblox serial drama: wide location refs made characters and a fountain read at incorrect
  scale. Distilled rule: match bg camera distance and use object-relative scale anchors.
- Star Trek EP7: a hatch changed design across scenes. Distilled rule: carry a concise part
  manifest and the relevant same-run continuity anchor.
- Genshin Don't Save Me EP4/EP6: independent backgrounds caused teleporting blocking; reusing
  one unchanged bg also prevented visible movement to a new vantage point. Distilled rule:
  use `continues_from_scene` only for direct continuity and create a correctly framed location
  ref for material repositioning.
- Star Trek Airlock EP14: editing onto a console-only bg inherited broken scale and left no
  space for the requested chair/characters. Distilled rule: do not use a base whose geometry
  cannot support the scene.
- Genshin Don't Save Me EP10: an old warehouse location ref contained a duplicate doorway
  that propagated into dependent scenes. Distilled rule: only manually approved reusable refs
  may cross runs.
- Star Trek ROOM 1701 EP7: 3 of 6 scenes rendered with a second, disconnected full-room copy
  stacked behind the characters. First-pass diagnosis (comparing against a different prior
  episode's prompts) was wrong and had to be corrected. Direct comparison of all 6 of this
  episode's own scenes showed prompt length did not correlate with the failure (the longest
  v1 prompt was one of the broken scenes; a clean scene's prompt was longer than two broken
  ones). The actual cause, confirmed against Scenarist's own `environment_state` field: for
  the 3 clean scenes, Scenarist had already scoped `environment_state` down to the shot
  distance ("sofas and window stay off-frame", a singular sofa instead of a plural
  establishing list); for the 3 broken scenes, `environment_state` listed the full wide-room
  landmark set ("facing blue sofas, delta rug, collectible shelves... remain visible")
  unscoped, and Storyboarder copied it into `image_prompt` verbatim without reconciling it
  against its own close/medium `camera_angle` choice. Two of the three broken scenes also
  combined the wide canonical location ref with a same-run continuation frame plus two
  identity refs (4 total `image_urls`) — two different camera framings of the same room
  anchoring one job at once, a compounding second cause. The location ref itself was valid.
  Distilled rule: see the revised section 8 — reconcile `environment_state` landmarks against
  your own chosen camera distance before writing `image_prompt`; do not pass through an
  unscoped background list, and do not assume a longer/more-qualified prompt is the fix.

## Prompt refinement

- Star Trek EP7: terse mechanical actions made doors/hatches open in implausible directions.
  Distilled rule: specify mechanism, direction, frozen phase, and transition medium.
- Genshin Don't Save Me EP10: repeated "no glass/no window" clauses overcorrected one small
  defect and changed the whole building. Distilled rule: retain the working prompt and replace
  one local defect with one concrete target description.
- Star Trek EP7: a plural crowd phrase with one character ref created clones. Distilled rule:
  avoid plural people when only one identity is anchored.
- Star Trek EP6: a looker's face appeared inside a porthole as the unidentified figure.
  Distilled rule: use a featureless silhouette when the second identity has no ref.

## Pipeline contracts

- Several runs lost money after malformed or dead refs silently degraded identity. Distilled
  rule: require permanent reachable URLs and runner state before generation.
- End frames combined with Kling `multi_prompt` returned 422 and doubled image spend.
  Distilled rule: start frame only.
- Scene-derived fixes chained from other redo frames accumulated drift. Distilled rule:
  regenerate from eligible canonical refs, not rejected derivatives.
