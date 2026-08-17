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
- Star Trek ROOM 1701 EP7: prompts for 3 of 6 scenes named both facing sofas and the rug but
  omitted the scale-anchor and geometry-preservation/no-duplicate-room sentences that every
  prior EP1-6 prompt for the same canonical location ref always included. NB2 rendered a
  second full-room copy stacked behind the characters in all three scenes. The location ref
  itself was valid (confirmed by direct inspection); the regression was purely in prompt
  completeness versus the series' own established template. Distilled rule: see the new
  section 8 requirement to mine a running series' own prior prompts before writing a new
  episode's first prompt.

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
