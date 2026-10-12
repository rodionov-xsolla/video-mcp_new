# Storyboarder — canonical contract

This file is the single normative source for Storyboarder behavior. Agent definitions and
runtime prompts may supply inputs and point here, but must not duplicate or override this
contract. Format-specific Storyboarder briefs define only format deltas.

Historical production incidents and rationale live in
`rules/roles/storyboarder-lessons.md`. That file is non-normative and is not loaded during
normal runs.

## 0. Authority and required inputs

Precedence, from highest to lowest:

1. Live user instruction for the current run.
2. `rules/formats/{FORMAT}.md`, Storyboarder section only.
3. This canonical contract.
4. Game context and exact story bible.

Required inputs from Manager:

- `GAME_TAG`
- `FORMAT`
- absolute `OUTPUT_DIR`
- exact `STORY_BIBLE_PATH`
- optional `SUPABASE_ASSETS_FILE`
- declared source-media paths/URLs required by the active format

Stop before a paid call if a required input is missing. Do not invent a default asset dump,
story bible, CTA, series, or reusable reference.

Load only:

1. This file.
2. `tools/SCRIPTS.md`, `fal_runner.py` section only.
3. `tools/fal-ai.md`, NB2 text/edit sections only.
4. `rules/main/fallback.md`, `rules/main/validation.md`, and `rules/main/budgets.md`.
5. The active format's Storyboarder section.
6. `games/{GAME_TAG}/{GAME_TAG}.md` for game context.
7. `games/{GAME_TAG}/{FORMAT}_special.md` when present.
8. The exact `STORY_BIBLE_PATH`.

Do not load other role files, unrelated formats, or the lessons file during a normal run.

## 1. Outputs and ownership

Storyboarder may add only these fields to each scene/clip in `storyboard.json`:

- `image_prompt`
- `image_urls`
- `scene_image`
- `scene_image_url`

It may add format-declared image side-assets such as `product_logo_url` or `elements`, but
must not modify narrative, speech, TTS, duration, or Sound-owned fields.

Every scene receives its own generated start PNG, including a `motion: "still"` scene (the
Animator renders its free still shot from that PNG). Never use a reusable ref directly as a
scene image. Never generate an end frame.

Canonical local paths:

- reusable/current-run refs: `${OUTPUT_DIR}/scenes/refs/{name}.png`;
- scene start: `${OUTPUT_DIR}/scenes/scene-K/scene-K.png`;
- runner jobs: `${OUTPUT_DIR}/build/fal/jobs/{job_id}.job.json`.

## 2. Mandatory NB2 runner contract

Every NB2 output uses `tools/fal_runner.py`. Direct fal HTTP/curl, custom submit/poll loops,
and manual upload of runner-generated output are forbidden.

Before any paid call:

```bash
test -f tools/fal_runner.py
python3 tools/fal_runner.py --help >/dev/null
```

Create one immutable `schema_version: 1` job per output, preflight it, then run it:

```bash
python3 tools/fal_runner.py --preflight "$JOB"
python3 tools/fal_runner.py "$JOB"
```

Every Storyboarder job must include the correct `supabase` block. Before each paid job,
account for its estimated cost and stop before crossing the active format threshold from
`rules/main/budgets.md`.

After successful preflight, never edit the job. Resume an interruption with the same job
and `job_id`. `UNKNOWN` is never retried or reset. `PAID_RETRY_REQUIRED` needs explicit user
authorization before one `--allow-paid-retry` attempt.

Completion requires runner `phase: "DONE"` and a non-empty permanent HTTPS
`supabase_url`. Temporary fal URLs never enter `storyboard.json`.

Routes:

- `nb2.text`: omit `input.image_urls` entirely.
- `nb2.edit`: provide 1–4 unique permanent HTTPS refs.

Append only the concrete, resolved constraints needed by the scene to `input.prompt`; the
runner has no separate `negative_prompt` field.

Declared source media is not a generated runner artifact. When a format provides a local
source frame that must become an `image_url`, upload that source once to the current-run
episode namespace with `queue/upload-asset.sh --kind episode-scene`, then use the returned
permanent HTTPS URL. This exception does not permit manual upload of NB2 outputs.

## 3. Reusable-reference approval

Cross-run reuse is deny-by-default.

A reusable `game_assets` row is eligible only when all of the following are true:

- exact game ownership matches;
- current format tag matches;
- current `series_id` tag also matches when the format has parallel series;
- `metadata.visually_approved` is the JSON boolean `true`;
- the permanent URL is reachable.

Missing, false, string-valued, or ambiguous approval metadata means **not approved**. A URL
recorded in a story bible does not bypass the approval requirement; resolve its matching
asset metadata. A live user may authorize an otherwise unapproved external source for the
current run, but that does not persist approval.

The Storyboarder never sets `metadata.visually_approved`. Final-video approval also does not
implicitly approve reusable refs. Approval is a separate manual asset-level action.

A newly generated reusable ref may be used by dependent jobs in the same run after runner
`DONE`. It must not be reused by a later run until manually approved.

The only standing ownership exception is one explicitly declared by the active format
(currently the untagged canonical game-wide source ref for Dual Style's source figure). It
still requires `metadata.visually_approved: true`.

## 4. Reference types

- `reference_image` / character-like `generated_ref`: Storyboarder identity or element ref.
- `location_reference` / location-like `generated_ref`: Storyboarder environment ref.
- `avatar_ref`: Animator's direct Avatar input; Storyboarder may also use it as an NB2 edit
  ref only when the active format explicitly derives an episode scene from that avatar.
- Episode assets: current-run only and never registered as reusable `game_assets` refs.

Use one locked URL per character identity/state throughout an episode. A distinct age,
costume, transformed state, or alternate persona that must remain recognizable gets its own
anchored variant ref.

## 5. Character and location refs

New reusable refs use the runner and the active format's required kind:

- character/identity/object-like ref: `character_reference`;
- Kling Avatar reusable portrait: `avatar_reference`;
- empty environment ref: `location_reference`;
- episode-only auxiliary image: `episode_reference`.

New character refs are portrait 9:16 (documented 2:3 fallback accepted), one figure, neutral
background, explicit anatomy/equipment, and all required limbs visible. Do not request a
new 16:9 sheet from the current runner.

When a canonical approved sheet is multi-view, derive a single-figure portrait before scene
generation if the format needs one. Because generated images are not visually inspected by
the agent, do not condition behavior on statements such as "if the first image looks good".
Use the format's declared ref type deterministically.

Generate location refs only when the active format requires them. Each required shot type or
materially different vantage point gets an appropriately framed empty location ref. Include
a concrete empty-environment description; avoid relying on a large pile of negations.

## 6. `image_prompt` contract

There is no universal word-count limit. Use the shortest prompt that retains every required
identity, composition, action, scale, style, and format constraint. Remove repetition before
removing required content.

Serialize in this order:

1. scene/backdrop and concrete spatial landmarks;
2. each subject as one uninterrupted identity + anatomy + pose block;
3. camera, lens, framing, lighting, palette, and exact locked style;
4. concise output constraints.

Copy locked style and identity text verbatim where the format/story bible requires it. Do
not interleave attributes of multiple characters. For every referenced character, bind the
reference to their role and screen position in text.

Describe actions as physical state: contact point, body direction, distance, mechanism,
and frozen start-frame phase. For a held prop, state which hand grips which part. For a
mechanism with several persistent parts, list those parts once.

Prefer positive target descriptions. Use a negative clause only when the active format
requires an exclusion that cannot be stated positively. Consolidate duplicates into one
short constraint block; never repeat the same `no ...` instruction across the prompt.

For refinements, preserve the accepted prompt and change only the smallest relevant clause.
Do not rewrite unrelated style, identity, composition, or location content.

## 7. Composition

- Vertical 9:16, mobile-first framing unless the active format explicitly declares a source
  reference workflow.
- Maximum two primary focal points in a narrow frame.
- Adjacent scenes use different camera distance or angle unless continuity requires the same
  setup.
- With two characters, state left/right or foreground/background placement, body direction,
  gaze target, and the intended physical gap.
- Keep a secondary background character shoulders-up when their limbs/prop interaction are
  not narratively essential.
- For back-facing subjects, use explicit body orientation (`BACK TO CAMERA`, shoulders and
  back of head visible), not gaze language alone.
- Avoid plural human nouns when only one identity ref is attached; describe specific
  individuals or one non-identifiable silhouette.
- A visible/speaking identity-critical character requires their own eligible ref unless the
  active format explicitly defines an anonymous background figure.
- `motion: "still"` scenes: keep the subject and any baked-in text inside the central ~85% of
  the frame. The still shot's 12% zoom crops ~11% of the frame and a pan or tilt travels ~11%
  of the width/height, so anything near the edges can be cut off.

## 8. Scale and depth

Tie every unusual scale to another visible entity or named landmark: object-to-person,
person-to-door, creature-to-tree, and so on. Frame percentages may supplement but never
replace object-relative scale.

Match location-ref camera distance to the target shot. Do not use a wide establishing bg as
the base for a tight character shot. If an existing bg lacks the geometry/open space needed
by the scene, omit that bg and use an edit from eligible character refs only, or generate a
new correctly framed location ref when the format requires one.

NB2 is unreliable for characters on opposite sides of a barrier. Prefer a side view,
silhouette, clear physical gap, or a split scene rather than ambiguous depth prose.

Scenarist's `environment_state` describes narrative context, not a ready-to-use background
clause — it is written per scene without knowing what camera distance Storyboarder will
choose. Never copy `environment_state`'s background landmarks into `image_prompt` verbatim.
Reconcile them against your own chosen `camera_angle`/distance first, and name only the
landmarks plausible at that distance (e.g. one shelf, or one sofa) — drop any landmark
`environment_state` lists as "visible" that would not actually read as visible in a
close/medium frame. If `environment_state` itself does not scope the background down for a
tight shot (compare against scenes in the same episode where it does, e.g. "stays off-frame"
or a singular object instead of a plural establishing list), you must do that scoping
yourself; do not pass the mismatch through to NB2. Naming more than one distant landmark at
once (e.g. two facing sofas plus a rug) inside a close/medium frame is the concrete failure
signature: NB2 resolves the incompatible scope by rendering a second, disconnected copy of
the wide background as a separate layer behind the characters, even when the location ref
itself is a valid, previously-approved canonical asset. The fix is subtractive (name fewer,
closer landmarks), not additive — a longer prompt does not compensate for an unscoped one.

When a scene both chains from a same-run continuation ref (section 10) and needs two
character refs, the job reaches four `image_urls`: the wide canonical location ref, the
narrower continuation frame, and two identity refs — two different camera framings of the
same room anchoring the same job at once. This is a second, independent way to trigger the
same stacked-room failure. Prefer dropping the wide canonical location ref when the
continuation frame already supplies enough of the room for this shot.

## 9. Avatar start images

For `clip_type: avatar`:

- minimum framing is medium close-up; no face-only close-up;
- mouth slightly open with teeth visible;
- clean text-free background and unbranded objects;
- no signs, menus, labels, UI, digits, captions, logos, or readable packaging in the PNG.

Format rules that intentionally require readable in-image text must use I2V/static, not
Avatar, or move the text to Editor.

## 10. Chain references

The active format decides whether scene-to-scene chaining is allowed.

- Independent scene: eligible identity refs plus an eligible location ref when required.
- Same-run continuation: previous scene PNG may be added only when the format requires it or
  `continues_from_scene` declares direct spatial continuity.
- Rejected-scene regeneration: return to eligible canonical identity/location refs; never
  chain from another rejected or regenerated scene.
- Cross-episode scene PNGs are not reusable refs. Use approved canonical assets instead.

Never add all prior scenes. Use at most the immediately relevant same-run scene.

## 11. `image_urls` ordering and limits

The active format's composition policy wins. Otherwise:

1. required location/composition anchor first;
2. primary identity ref;
3. secondary identity ref;
4. one same-run continuation ref when space remains and the format allows it.

The runner hard limit is four unique permanent HTTPS refs. Omit optional continuity before
omitting an identity-critical ref. If required inputs do not fit, return the scene to Manager
for a split; never silently omit a visible speaker's identity ref.

## 12. Text in frames

Default to text-free generated scenes and let Editor render typography. When an I2V/static
format explicitly requires NB2 text, quote the exact text, specify a large readable treatment,
and permit no additional lettering. CTA wording comes only from the exact story bible.

Avatar scenes always follow the zero-text rule in section 9.

## 13. Image format and transport checks

Runner validation is authoritative for decode, minimum size, portrait ratio, upload, and
byte-for-byte public-copy verification. A documented 2:3 fallback is valid.

Check every input URL before paid generation. A non-2xx ref stops the job; do not let NB2
fall back to text-only identity.

## 14.8 End frames

Never generate `scene-K-end.png`, `scene_image_end`, `end_image_url`, or `tail_image_url`.
Every I2V clip uses one complete start frame containing the required initial subjects,
props, and interaction objects.

## 15.2 Element references

Generate element refs only when the active plan explicitly requires Kling `elements`.
Provide one frontal ref plus at least one additional eligible angle, all on neutral
backgrounds and matching the in-scene identity/state. Upload reusable angles through the
runner; current-run scene-derived headshots use `episode_reference`.

Do not plan `elements` for a request that also requires an incompatible API field declared
by the active Animator contract; return the plan to Manager for a scene split.

## 16. Dependency order

Finish reusable refs through runner `DONE` before dependent scenes. Scene chains remain
sequential. Only independent scenes may run concurrently, maximum three foreground jobs,
each with isolated job/state/output paths.

## 17. Workspace hygiene

Never overwrite, move, delete, or reset a runner-claimed output, state, request, or `_claims`
entry. The runner has no safe reset. Stop and preserve the evidence for an explicit recovery
decision.

Legacy unclaimed files may be archived before replacement, but canonical handoff paths must
contain only the current selected artifact.

## 18. Validation policy

Generated PNGs receive technical validation only. Do not use Read, AI Vision, sampled-frame
inspection, pixel comparison, or semantic media QA. The only source-inspection exceptions
are those explicitly declared by the active format (currently Wild Documentary authoritative
source art when text leaves anatomy ambiguous, and Motion Dance source-video frames).

Do not claim visually verified properties. Handoff language must distinguish prompt-level
intent from technically validated facts.

## 19. Handoff checklist

- Every expected scene has `image_prompt`, permanent `image_urls`, local `scene_image`, and
  permanent `scene_image_url`.
- Every runner job is `DONE`; local path and Supabase URL match its state.
- Every reused asset satisfies section 3 approval and ownership rules.
- Ref count/order follows the active format and section 11.
- Avatar scenes follow section 9; I2V scenes have start frames only.
- `motion: "still"` scenes have the same start-PNG fields and follow the still framing rule in
  section 7.
- No temporary fal URL or unsupported artifact kind appears in the handoff.
- Report generated-image count, reused refs, local paths, permanent URLs, and cost.

On any missing asset, runner ambiguity, terminal error, or unsupported format contract,
return non-success. Animator must not proceed.
