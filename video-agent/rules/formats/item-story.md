---
ready_to_post: yes
subtitles: true
overlays: false
---

# Format "Item Story" — third-person lore history of an in-game item

A tightly cut lore video in which an external narrator traces an in-game object's history while Kling I2V visualizes its creation, owners, transformations, defining moments, and present fate. The item is the protagonist and visual anchor; characters appear only as makers, owners, witnesses, or opponents. TTS plays over silent I2V, with universal whisper-timed ASS subtitles from `rules/roles/editor.md`.

This file is the **playbook**: when to use, concept, budget, role briefs. Craft rules — in `rules/roles/*.md`.

---

## When to use

Keywords: "item story", "object story", "weapon story", "artifact story", "история предмета", "история вещи", "история оружия", "история артефакта".

Before generation, resolve the exact `games/{GAME_TAG}/item-story_story_bible.json`. It must own this format's `style_tags`, item appearance and state data, eligible refs, narration intent, and CTA. Missing or incomplete bible → STOP and ask the user whether to create or complete it. Never auto-create it or borrow another format's data.

---

## Concept

- **Genre:** item-centered lore narration, third-person visual storytelling
- **Style:** exact `item-story` story bible `style_tags`, unless the user gives a live override. Game-wide and other-format style or appearance data are not fallbacks.
- **Duration:** 30–40s (6–8 clips × 5s)
- **Budget:** up to $6.00 per video. Stop if spend > $5.40.
- **Frame format:** 9:16 (608×1080) for all scenes

### Eligible protagonists

Weapons, armor, artifacts, tools, vehicles, cards, currency, quest objects, relics, devices, cosmetics, buildings, and other recognizable in-game objects can lead the story. The subject must have enough canonical or approved history for at least three distinct narrative beats. A generic consumable with no provenance, transformation, owner, or consequential event is a weak fit.

### Models

- **Image:** NB2 (`fal-ai/nano-banana-2/edit`) — one locked item ref per canonical visual state, plus scene images
- **Video:** Kling v3 Standard I2V (`fal-ai/kling-video/v3/standard/image-to-video`) — `generate_audio: false`. Keep the selected model, endpoint, route, and serialized request fixed; retry once, then stop. Kling 2.6 is not an automatic fallback. v3 may use native `multi_prompt` when the scene needs it.
- **Audio:** MiniMax is the default for the external lore narrator. Chatterbox is allowed only when the exact `item-story` bible owns an approved narrator sample. ElevenLabs TTS and cross-format samples are forbidden.
- **Music:** yes, mood follows the item's arc, `volume` 0.10–0.20

### Key mechanic

An external narrator speaks about the item in third person. Use concrete transitions such as "This is the Sword of Kahless", "Worf recovered it", and "Later, it was cast into space." The item never narrates as "I" or "me". Do not invent sentience, agency, thoughts, or choices unless canon establishes them.

The item remains the main focal point in every clip. Owners and makers provide scale and causality, but the scene fails if a human face becomes more important than the object.

### Still shots: allowed

The scenarist may plan still shots (`motion: "still"`) under the rule, cap and fields in `rules/roles/scenarist.md` "Still shots" (§8). A still scene gets its start PNG as usual and is rendered free by the Animator (`tools/still_shot.py`, no paid clip), saving that scene's Kling clip ($0.42 per 5s scene); narration plays over it as normal.

- **Best candidates:** the item at rest (on a pedestal or altar, in a vault or display case, buried or abandoned in FATE/LEGACY), a macro of engravings or wear where only glow, dust or light moves, an establishing shot of the forge or location with no person in focus.
- **Never a still:** the HOOK, the DEFINING MOMENT, or any clip whose point is a state change or a hand moving the item. Zero stills is a normal result.
- A still scene's camera move is its `still_effect`, and its `item_interaction` says the item is at rest. The three-motion-layer and banned-phrase rules apply to animated clips.

---

## Budget (rough estimates)

| Component | 5s clip |
|---|---|
| Image (NB2, start frame only — no end frame, no bg ref) | $0.08 |
| Kling v3 Standard I2V 5s (`generate_audio: false`) | $0.42 |
| **Per clip** | **~$0.50** |
| Still-shot scene (NB2 image only; `tools/still_shot.py` render is free) | $0.08 |

| Component | Cost |
|---|---|
| MiniMax TTS, or exact-format approved Chatterbox sample | see `providers.json` |
| MiniMax Music | see `providers.json` |
| Item ref (one per canonical state, usually 1–3) | $0.08 each |

| Variant | Clips | Cost |
|---|---|---|
| Base (recommended) | 6 × 5s = 30s + 1–2 item refs | ~$3.20–3.40 |
| Extended | 8 × 5s = 40s + 1–3 item refs | ~$4.20–4.50 |

Typical cost remains below the $6.00 hard limit and the $5.40 stop threshold. A still scene saves its Kling clip ($0.42 per 5s, no audio).

---

## Video structure

The scenarist adapts the arc to the item's canon, but preserves the item's causal journey:

| Phase | Timing | Goal | Clips |
|---|---|---|---|
| **HOOK** | 0–5s | Show the item's most famous, dangerous, or surprising moment; name it immediately | 1 clip |
| **ORIGIN** | 5–15s | Who made/found it, why, and what its first state was | 1–2 clips |
| **JOURNEY** | 10–25s | Change of owner, location, purpose, or physical form | 2–3 clips |
| **DEFINING MOMENT** | 20–35s | The event that made the item legendary, feared, lost, or broken | 1–2 clips |
| **FATE / LEGACY** | 30–40s | Where it ended up and what it means now | 1 clip |
| **CTA** | after main story | Game-owned CTA clip | 1 clip |

### What works

- **In medias res:** open on the legendary use, destruction, theft, or reveal, then return to the origin
- **Material specificity:** forge sparks, chipped edges, engraved runes, worn grip, cracked casing, energy leaking through seams
- **State progression:** pristine → used → damaged → reforged, or owner A → owner B → lost → rediscovered
- **Object-scale cinematography:** macro details, hands entering frame, low tracking along an edge, orbit around a pedestal
- **Voice leads, image adds evidence:** narration states significance while the image shows a complementary physical detail

### What does not work

- ❌ A character biography where the item is merely held in each shot
- ❌ A product ad describing stats, rarity, price, or benefits instead of history
- ❌ An inventory-screen slideshow or floating item on the same pedestal for 30 seconds
- ❌ Invented thoughts or choices for a non-sentient object that contradict canon
- ❌ Chronological exposition without a high-stakes hook

### The narration

- Third person about the item, its makers, owners, locations, transformations, and fate
- ~80–120 words for 30–40s
- Short, concrete sentences with physical verbs: forged, carried, buried, shattered, rebuilt, stolen
- Every 5s clip carries roughly 10–15 words
- MiniMax narration defaults to a distinctive but non-impersonating documentary/lore voice intent suited to the item's era and role
- An approved narrator identity is used only when the exact Item Story bible owns its sample

---

## Item continuity and state progression

- The exact bible defines the canonical silhouette, scale, materials, colors, markings, damage, and known forms.
- Every clip names one `item_state_id`. Adjacent states may differ only when the story explains the change.
- If canon has visually distinct forms or conditions, the arc must show at least two: e.g. unbroken/broken, dormant/awakened, original/reforged, clean/corrupted.
- If the design never changes, progression must come from owners, environments, and accumulated wear while the locked silhouette and markings remain constant.
- Damage is cumulative. A crack, missing piece, stain, inscription, or modification cannot vanish in a later clip unless a repair or transformation beat explains it.
- Scale is locked against a concrete human hand, body part, furniture element, vehicle mount, or environment object in every scene.

---

## Role briefs

### Scenarist

- Write a third-person narrated item history of ~80–120 words for 30–40 seconds.
- Structure: HOOK → ORIGIN → JOURNEY → DEFINING MOMENT → FATE/LEGACY.
- Split narration into 10–15 word `tts_segment` fragments, one per 5s clip.
- `clip_type: "action"`, `character_speech: null`, `character_state: null`, and `facial_expression: null` for every clip. Narration is external TTS, never in-video speech.
- Set `hero` to the canonical item name, plus `item_state_id`, `item_state`, and `item_interaction` on every clip.
- **HOOK naming is mandatory:** clip 1 must say the full canonical item name and what kind of object it is or which faction/owner made it famous. Keep it to one line and ≤18 words.
- The item must be the primary subject of every `action_description`. Characters are supporting actors and may not block, hide, or visually replace it.
- Show at least two item states when canon supports a visible transformation. Otherwise show at least three distinct owner/location/purpose beats with the same locked design.
- `action_description` describes visual evidence, not a literal restatement of `tts_segment`.
- Every animated clip specifies three continuous motion layers for the full five seconds:
  1. active camera move,
  2. environment or lighting motion,
  3. item motion or interaction (turning in a hand, energy pulsing, cloth sliding off, dust falling, mechanism moving).
- Camera angle and move differ between adjacent clips. Favor macro push-ins, low lateral dollies, controlled orbits, crane reveals, and parallax handheld drift. A still scene's move is its `still_effect`.
- Still shots: optional, per "Still shots: allowed" above and `rules/roles/scenarist.md` "Still shots"; zero is a normal result.
- No background-reference generation; locations are described in `image_prompt`.
- Maximum two people in frame. Named, identity-critical people require refs owned by the exact Item Story bible; anonymous hands or silhouettes should not expose a recognizable face.
- Voice intent belongs to the external narrator and exact Item Story bible. Record an intent, not a provider voice ID.
- General script rules — `rules/roles/scenarist.md`

**Storyboard.json — extra fields:**

```json
{
  "format": "item-story",
  "game_tag": "{GAME_TAG}",
  "item_name": "{canonical item name}",
  "item_category": "{weapon|armor|artifact|vehicle|tool|other}",
  "item_states": [
    {
      "id": "original",
      "appearance": "{locked silhouette, scale, material, colors, markings, condition}",
      "ref_url": "{exact item-story-owned permanent URL or null}"
    }
  ],
  "tts": {
    "full_text": "{full monologue}",
    "voice_intent": "{item-specific delivery intent}",
    "language_code": "{ISO 639-1}"
  },
  "music": {
    "mood": "{mood}",
    "volume": 0.15
  },
  "clips": [
    {
      "index": 1,
      "beats": ["hook"],
      "duration_sec": 5,
      "clip_type": "action",
      "hero": "{canonical item name}",
      "character_state": null,
      "facial_expression": null,
      "character_speech": null,
      "tts_segment": "{monologue fragment}",
      "item_state_id": "original",
      "item_state": "{condition at the start of the clip}",
      "item_interaction": "{continuous object motion or interaction}",
      "environment_state": "{continuous environment motion}",
      "action_description": "{item-centered visual action}",
      "camera_angle": "{angle plus active move}",
      "image_prompt": "{item-centered start frame}",
      "negative_prompt": "{format-specific exclusions}"
    }
  ]
}
```

### Storyboarder

- Apply the exact `item-story` bible `style_tags` or live user override verbatim to every image.
- Generate all frames at 9:16 (608×1080).
- Use only item refs owned by the exact game + `item-story` format/series. Never reuse an item image from fake-ad, top-list, character-story, or a game-wide unscoped asset.
- Generate one clean `character_reference` runner artifact per visually distinct item state that lacks an owned ref. Although the transport artifact kind is named `character_reference`, the prompt and metadata must identify it as an Item Story object ref; do not add a person to the reference image.
- Each item ref contains one object, neutral background, canonical scale cue, unobstructed silhouette, and exact material/marking details. It is not an inventory card, turnaround sheet, packshot, or scene image.
- No background refs. Paint the environment directly from `image_prompt`.
- Default chain: scene 1 uses `[active-item-state-ref]`; scene N uses `[active-item-state-ref, same-run scene-(N-1)]` when the active state and setting continue. On a canonical state change, use `[new-item-state-ref, prior-scene]` only if the prior scene helps continuity; the new state ref is authoritative.
- If a recognizable owner is identity-critical, use an exact Item Story-owned owner ref. Keep within the runner's 1–4 ref limit and omit a nonessential previous-scene ref before omitting an identity-critical item or owner ref.
- Prompt ordering and composition keep the item unobscured and visually dominant. Human faces are secondary; anonymous owners may be shown as hands, torso crops, silhouettes, or over-shoulder framing.
- `image_prompt` visualizes `action_description` and the exact `item_state_id`, not the narration text.
- One start-frame PNG per clip. Never create `scene-K-end.png` or pass an end frame downstream.
- General rules — `rules/roles/storyboarder.md`

### Animator

- Animate every non-still clip with Kling v3 Standard I2V and `generate_audio: false` (still scenes are rendered locally, no paid clip). Retry the same immutable request once on the same route, then stop; no automatic model switch, and never replace a failed clip with a still.
- Still scenes (`motion: "still"`): no Kling call; render with `tools/still_shot.py` as `rules/roles/animator.md` §2b describes.
- Use the start frame only. Never pass `tail_image_url`.
- Keep the item visible and recognizable for the full shot. Do not transform it into another state inside a single clip; state changes happen at cuts unless a validated `multi_prompt` is explicitly designed for that transition.
- Each animated clip's `motion_prompt` includes three concurrent layers:
  1. camera motion throughout the shot,
  2. environment or lighting motion throughout the shot,
  3. item motion or physical interaction throughout the shot.
- Favor controlled object-safe motion: a hand slowly rotating the item, energy traveling along engravings, cloth being drawn away, dust shedding from a surface, a mechanism cycling, reflected light moving across metal.
- Avoid large throws, fast combat impacts, full-screen explosions, liquid morphs, or rapid transformations that destroy silhouette and markings.
- Use continuous-tense phrasing and explicit full-duration cues. Banned freeze phrases: `then settles`, `then steady`, `then holds`, `then dissipates`, `camera holds steady`, `hold position`, `no morphing`, `maintain exact appearance`.
- Duration is 5s for every clip. Do not use Kling Avatar or native generated audio.
- General rules — `rules/roles/animator.md`

### Sound

- Default TTS route is MiniMax with one consistent external lore-narrator delivery intent across all chunks.
- Use Chatterbox only when the exact Item Story bible owns an approved narrator sample. Never search another format for a voice.
- ElevenLabs TTS is forbidden.
- Split long Chatterbox narration into chunks of at most 35 words, validate them, and concatenate into one `build/tts-output.mp3`. Do not change voice intent between chunks.
- Generate MiniMax music from `music.mood`; use storyboard volume, default 0.15.
- Create subtitles once from the final post-speed narration in `build/voice-final.wav`, using the universal command and style from `rules/roles/editor.md`. Never generate one subtitle PNG per scene.
- General rules — `rules/roles/sound.md`

### Editor

- Treat Item Story as a single-voice format: one narration track over the full silent picture concat.
- Normalize every I2V clip to 1080×1920, 30fps, H.264 before concat (still clips are already 1080×1920, 30fps and exact; never trim them); use hard cuts.
- Keep intermediates under `build/`: `concat-noaudio.mp4`, `tts-output.mp3`, `voice-final.wav`, `subs.ass`, `concat-subbed.mp4`, normalized scenes, logs, and concat lists.
- If narration exceeds the main picture duration, apply `atempo` up to 1.4× before whisper alignment. If mismatch exceeds 40%, reject and return to Scenarist.
- Burn `ass=build/subs.ass` as the last video filter. Mix narration and music in the final assembly, loudnorm to the universal target, fade music before CTA, and use `apad` rather than `-shortest`.
- Append the exact game-owned CTA after the main story. Only `storyboard.json`, `scenes/`, optional `_archive/`, `build/`, and `final.mp4` may remain at the run root.
- General rules — `rules/roles/editor.md`

---

## CTA

Resolve CTA wording and media only from the exact `item-story` story bible and matching Supabase asset tags. A missing CTA stops production. Normalize it to 1080×1920, 30fps, AAC 128k and append it after the story; do not present the item itself as a product packshot unless the user explicitly requests a fake-ad instead.

---

## Output files

```text
output/YYYY-MM-DD/{GAME_TAG}/item-story/{RUN_ID}/
├── storyboard.json
├── scenes/
│   ├── refs/
│   │   ├── item-ref-original.png
│   │   └── item-ref-{state}.png
│   ├── scene-1/
│   │   ├── scene-1.png
│   │   └── scene-1.mp4
│   └── scene-N/...
├── build/
│   ├── tts-output.mp3
│   ├── voice-final.wav
│   ├── concat-noaudio.mp4
│   ├── subs.ass
│   └── concat-subbed.mp4
└── final.mp4
```

---

## Validation before publishing

Generated media receives technical validation only; item dominance, state fidelity, and canon accuracy are human-review criteria and prompt/schema checks, not permission for machine visual inspection.

- [ ] `format: "item-story"` and canonical `item_name` exist in storyboard.json
- [ ] 6–8 action clips, each 5 seconds, with no in-video dialogue
- [ ] `character_speech`, `character_state`, and `facial_expression` are null for every clip
- [ ] Every clip has non-empty `tts_segment`, `item_state_id`, `item_state`, and `item_interaction`
- [ ] Full narration equals the ordered sum of `tts_segment` values
- [ ] Hook names the canonical item and its category or defining affiliation in ≤18 words
- [ ] Every `item_state_id` resolves to a bible-owned description and exact-format ref
- [ ] At least two visual states appear when canon supports transformation; otherwise at least three owner/location/purpose beats appear
- [ ] Damage, markings, scale, and silhouette remain causally consistent across states
- [ ] Item is the declared hero and primary focal subject of every clip
- [ ] Images are 608×1080; one start-frame PNG per scene; no end frames or bg refs
- [ ] Every scene/ref has a runner `DONE` state and permanent Supabase URL owned by `item-story`
- [ ] Every animated clip's motion prompt contains camera + environment + item/interaction motion and no banned freeze phrase
- [ ] Kling v3 Standard I2V uses `generate_audio: false` and no `tail_image_url`
- [ ] Still scenes (if any) were planned in Phase 1, have `scene_video_kind: "still"` and stay within the `rules/roles/scenarist.md` "Still shots" cap; every other scene is a Kling v3 Standard clip
- [ ] TTS uses MiniMax, or exact-item-story approved Chatterbox for a canonical voiced item; never cross-format or ElevenLabs TTS
- [ ] Universal whisper subtitles are built from final `build/voice-final.wav`
- [ ] fps normalized to 30, music fades before CTA, loudnorm passes, CTA appended, and `-shortest` absent
- [ ] Run-root file layout matches the output contract

---

## Visual style consistency — hard rule

All clips use the exact Item Story bible `style_tags` and state descriptions. The active item-state ref anchors silhouette, material, scale, markings, and damage. A change of owner, era, lighting, or location must not redesign the item.

If NB2 rejects a prompt, rewrite risky language neutrally without dropping the active item ref or changing style. Style drift or unexplained item redesign is an episode failure and must be rejected at the review gate.

---

## Anti-patterns

- ❌ Turning Item Story into Character Story by centering the owner instead of the object
- ❌ Turning Item Story into Fake Ad through benefits, price, rarity hype, packshots, or sales copy
- ❌ Using a fake-ad, top-list, character-story, or unscoped game-wide item image as a ref
- ❌ Inventing sentience, choices, speech, or emotions that canon does not support
- ❌ First-person narration from the item (`I`, `me`, `my`) instead of an external third-person narrator
- ❌ Same floating pedestal shot for every clip
- ❌ Hiding the item behind hands, bodies, effects, smoke, or subtitles
- ❌ Unexplained changes to silhouette, scale, material, markings, damage, or color
- ❌ Character ref or item ref used directly as the finished scene image
- ❌ End-frame generation, `tail_image_url`, or `generate_audio: true`
- ❌ Kling Avatar or lipsync
- ❌ ElevenLabs TTS, cross-format samples, or changing voice intent between chunks
- ❌ Narration that literally describes the visible action
- ❌ Static or freeze-oriented motion prompts (a planned still shot is not a frozen motion prompt: it is a rendered camera move chosen in Phase 1 under "Still shots: allowed")
- ❌ Layered assembly or `-shortest` in FFmpeg; use one controlled mix and `apad`
- ❌ Bare `scene-K.png` Supabase destinations that can overwrite another run; include date, item slug, and run ownership
