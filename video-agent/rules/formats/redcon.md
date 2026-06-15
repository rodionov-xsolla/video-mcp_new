---
subtitles: true
overlays: false
---

# Format "Redcon" — alternate-universe character story with lore divergence

A serious, cinematic "What If?" for game characters: one divergence point in canon, one alternative fate, told in first-person by the alternate-self. Think Marvel's What If? or DC Elseworlds — not comedy, but genuine tragedy, horror, or triumph that *could have been*. The character narrates their own alternate history as TTS overlay over I2V visualizations.

This file is the **playbook**: when to use, concept, budget, role briefs. Craft rules — in `rules/roles/*.md`.

---

## When to use

Keywords: "redcon", "what if lore", "alternate history", "альтернативная история", "what if character", "elseworlds", "что если бы", "lore what if", "divergence", "alternate fate", "another path".

**Distinct from:**
- `what-if-real-life` — that format is comedy (character in mundane real world). This format is serious lore.
- `character-story` — that format tells canonical backstory. This format tells a *non-canonical* alternate path.

---

## Concept

- **Genre:** alternate-universe lore, dramatic first-person monologue
- **Style:** identical to the game (taken from `games/{GAME_TAG}/{GAME_TAG}.md`)
- **Duration:** 35–45s (7–8 clips × 5s + 1 title card × 3s)
- **Budget:** up to $6.00 per video. Stop if spend > $5.40.
- **Frame format:** 9:16 (608×1080) for all scenes
- **Language:** English (all TTS and text)

### Models

- **Image:** NB2 (`fal-ai/nano-banana-2/edit`) — character refs + scene images
- **Video:** Kling v3 Standard I2V (`fal-ai/kling-video/v3/standard/image-to-video`) — `generate_audio: false`. Fallback to v2.6 Pro only if v3 produces artifacts. v3 supports native `multi_prompt` for multi-beat clips.
- **Audio:** ElevenLabs TTS overlay — first-person monologue as the alternate-self
- **Music:** Dark/ folder only — dramatic, tense, atmospheric

### Key mechanic

Same as `character-story`: character does NOT speak on camera (no lipsync). I2V visualizes scenes; TTS is the alternate-self narrating what happened. One key addition: **mandatory title card as clip 1** — a static text-over-image scene establishing the premise ("WHAT IF: / SPOCK / BECAME / BORG").

---

## Budget (rough estimates)

| Component | Cost |
|---|---|
| Title card image (NB2) | $0.08 |
| Title card I2V 5s (Kling v3 Standard, no audio) | $0.42 |
| Story clip image (NB2) | $0.08 |
| Story clip I2V 5s (Kling v3 Standard, no audio) | $0.42 |
| **Per story clip** | **~$0.50** |
| ElevenLabs TTS (~40s monologue) | ~$0.20 |
| Character refs (1–2) | $0.08 each |

| Variant | Clips | Cost |
|---|---|---|
| Base (recommended) | 1 title card + 6 story clips | ~$3.20 |
| Extended | 1 title card + 7 story clips | ~$3.55 |

---

## Video structure

| Phase | Clip | Timing | Goal |
|---|---|---|---|
| **TITLE CARD** | clip 1 | 0–5s | Text-on-dark-bg: "WHAT IF:" / [CHARACTER NAME] / "BECAME" / [ALTERNATE FATE]. Slow camera drift. No TTS here — silence or ambient music only. |
| **HOOK** | clip 2 | 5–10s | Alternate-self in their transformed state. Self-introduction in the new identity. Sets the horror/wonder. |
| **CANON REMINDER** | clip 3 | 10–15s | Brief glimpse of who they *were*. The before. |
| **DIVERGENCE** | clip 4 | 15–20s | The moment everything changed — the decision, the event, the point of no return. |
| **TRANSFORMATION** | clip 5 | 20–25s | What happened during / immediately after the divergence. The change. |
| **CONSEQUENCE** | clip 6 | 25–30s | What this alternate self *is now*. The weight of the new existence. |
| **REVELATION** | clip 7 | 30–35s | The twist, the irony, the tragic/triumphant final truth. What this divergence *means* in the bigger picture. |
| **CTA** | last ~5s | — | CTA clip |

### Narrative principles

- **Divergence must be lore-grounded.** The alternate path must be plausible within the canon world — not random. Cite the specific canon moment that *almost* happened differently.
- **The alternate self is self-aware.** They know who they were. The monologue holds that tension: "I remember who I was."
- **Irony and dark mirror.** The best What If stories show how the character's core traits lead them *into* the alternate fate — Spock's logic is what makes him vulnerable to the Borg.
- **Three motion layers per clip** (mandatory) — same rules as `character-story`.

### The monologue

- First-person, spoken by the *alternate-self* (not the original)
- ~90–120 words for 35–40s
- Clip 1 (title card): `tts_segment: null` — silence over the title card
- Each story clip: ~12–18 words
- Voice chosen for the *alternate* identity, not the canonical one (e.g. Borg-Spock = Daniel, stability 0.05, style 0.9 — flat, echoing with collective overtone)
- No narrator framing ("In a universe where...") — the character speaks directly, in medias res

---

## Role briefs

### Scenarist

- Write the alternate-self monologue (~90–120 words English, ~35–40s)
- Clip 1 is the **title card**: `clip_type: "action"`, `tts_segment: null`, `character_speech: null`. `action_description` = slow drift over dark textured background with the title text rendered large. No character in frame — or character silhouette only, unrecognizable.
- Clips 2–7: `clip_type: "action"`, `character_speech: null`, `tts_segment` = monologue fragment for that clip
- **HOOK clip (clip 2) must name the alternate designation** — e.g. "I am Borg. Designation Seven of Seven... but I remember being Spock." Full canonical name + alternate designation in the first 15 words.
- Age progression: if the character has canonical age variants, show the *before* clip at the younger/mid age, the *after* clips at the transformed state. Two character refs minimum: canonical-self and alternate-self.
- **The divergence clip (clip 4) must specify the exact canon year and event** in `action_description` so Storyboarder can ground the visual.
- Three motion layers per clip in `action_description` — same rules as `character-story`.
- `camera_angle` must differ between adjacent clips; every clip has an active camera move.
- `format: "redcon"` in storyboard.json
- General script rules — `rules/roles/scenarist.md`

**Storyboard.json — extra fields:**

```json
{
  "format": "redcon",
  "game_tag": "{GAME_TAG}",
  "character_name": "{canonical name}",
  "alternate_designation": "{what they became}",
  "divergence_point": "{brief: year + event that diverged}",
  "tts": {
    "full_text": "{full monologue — all tts_segments joined, clip 1 skipped}",
    "voice": "{voice name}",
    "stability": 0.05,
    "style": 0.9,
    "language_code": "en"
  },
  "music": {
    "mood": "dark",
    "volume": 0.15
  },
  "clips": [
    {
      "index": 1,
      "beats": ["title-card"],
      "duration_sec": 5,
      "clip_type": "action",
      "character_speech": null,
      "tts_segment": null,
      "title_lines": ["WHAT IF:", "{CHARACTER NAME}", "BECAME", "{ALTERNATE FATE}"],
      "character_state": "absent — title card only",
      "facial_expression": null,
      "action_description": "...",
      "camera_angle": "...",
      "image_prompt": "...",
      "negative_prompt": "..."
    }
  ]
}
```

### Storyboarder

- Style from `games/{GAME_TAG}/{GAME_TAG}.md`
- All frames 9:16 (608×1080)
- **Two character refs required:** (1) canonical-self ref (who they were), (2) alternate-self ref (what they became). Generate both upfront.
- **Title card (clip 1):** generate a dark atmospheric background image — NO character in frame, or only a distant/silhouetted shape. Overlay the `title_lines` as large centered text in the game's UI style. No bg-reference file — paint environment inline.
- Chain: clip 2 refs = `[alternate-self-ref]`; clip 3 (canon reminder) refs = `[canonical-self-ref]`; clips 4+ refs = `[alternate-self-ref, prev-scene.png]`
- **No bg-reference generation** — environment goes into `image_prompt` as text only
- **One PNG per clip — start frame only.** No end frames.
- General rules — `rules/roles/storyboarder.md`

### Animator

- All clips via **Kling v3 Standard I2V** (`generate_audio: false`); fallback v2.6 Pro only on v3 artifacts
- For multi-beat clips use v3's native `multi_prompt` array. **Segment length: 2–3s each. Max clip duration: 7s.** Never use 5+5=10s — 7s is the hard cap per pass. Example: divergence + transformation → 3s+3s=6s per clip.
- **Start frame only.** No `tail_image_url`.
- Title card clip: very slow camera drift (parallax or gentle push-in). Minimal motion — text must remain readable throughout 5s.
- Story clips: **active, dynamic prompts only** — three concurrent layers (camera + primary action + atmosphere), continuous present-tense verbs, no freeze phrases ("remains still", "holds position", "stays motionless" are banned).
- Duration: 5s for standard clips, up to 7s for multi-prompt clips
- General rules — `rules/roles/animator.md`

### Sound

- **TTS:** full monologue as ONE audio file (`tts-output.mp3`). All `tts_segment` values joined in order, clip 1 skipped (null). Mandatory chunking per `sound.md §1b` if total > 80 words.
- **Voice engine:** `game_tag == "genshin-impact"` → **Chatterbox** with character's `voice-1.mp3` from Supabase (`assets/genshin-impact/characters/{slug}/voice-1.mp3`). All other games → MiniMax preset voice matching the alternate-self identity. See `rules/roles/sound.md §1`.
- Generate `tts-output.mp3`, upload to Supabase as episode-tts asset
- **Subtitles:** the one universal whisper style from `build/voice-final.wav` (the title-card lead silence is already inside via adelay) — `rules/roles/editor.md` §6. No `--offset`/`--text`.
- Music: from `video-agent/music/Dark/` only — never Fun/
- General rules — `rules/roles/sound.md`

### Editor

**Use `rules/roles/editor.md §0 — canonical single-pass `filter_complex` pipeline`** (the redcon worked example in §0.2 ships exactly this format).

Format-specific parameters to compute and pass into §0:
- `PRE_MS = 5000` — TTS starts after the 5 s title card via `adelay=5000|5000`
- `atempo = TTS_DUR / 40` — TTS window is `MAIN_DUR − 5 s` (title card silence). If atempo > 1.4, you may exceed the conventional cap up to ~1.5 for this format (Borg-flat voice is naturally slow); ASS must be regenerated against the exact final atempo.
- `MAIN_DUR = 5 + 6*5 + 10 = 45 s` (title + 6 story clips + 10 s coda) — adjust if scene count changes
- Fade-to-black: 1.0 s on the last story clip (scene-8) before CTA
- Music: `volume=0.15`, `afade=t=out:st=(MAIN_DUR−1):d=1.0`

ASS generation: `tools/add_subtitles.py` against `tts-output.mp3` PRE-shaped (atempo applied, then 5 s adelay prepended), so the ASS timeline matches what §0 feeds the `ass=` filter.

**Title card text (MANDATORY) — через ASS, не через drawtext или overlay.**
`title_lines` из `storyboard.json` (clip 1) рендерятся как отдельные `Dialogue:` события в том же `subs.ass` — ровно тот же механизм что и субтитры, просто крупнее и с позиционированием через `\pos`. Добавить 4 события (по числу строк) с таймингами `0:00:00.50–0:00:04.80` (чуть позже старта, исчезают до конца title card):

```ass
Dialogue: 0,0:00:00.50,0:00:04.80,Default,,0,0,0,,{\an5\pos(540,720)\fs65\c&H00FFFFFF&}WHAT IF:
Dialogue: 0,0:00:00.50,0:00:04.80,Default,,0,0,0,,{\an5\pos(540,870)\fs165\c&H00FFFFFF&}{CHARACTER NAME}
Dialogue: 0,0:00:00.50,0:00:04.80,Default,,0,0,0,,{\an5\pos(540,1010)\fs65\c&H00FFFFFF&}BECAME
Dialogue: 0,0:00:00.50,0:00:04.80,Default,,0,0,0,,{\an5\pos(540,1115)\fs100\c&H0000D7FF&}{ALTERNATE FATE}
```

- `\an5` = center alignment, `\pos(540, y)` = horizontal center в 1080px кадре
- Строка 1 "WHAT IF:" — `\fs65`, белый `\c&H00FFFFFF&`
- Строка 2 имя персонажа — `\fs165`, белый (крупнее всего)
- Строка 3 "BECAME" — `\fs65`, белый
- Строка 4 альт-судьба — `\fs100`, золотой `\c&H0000D7FF&` (ASS BGR для `#FFD700`)
- y-позиции рассчитаны для PlayResY=1920; суммарный блок ~400px, центрирован чуть выше середины кадра

Эти события добавляются **в начало** `[Events]` секции (до первого subtitle-события) чтобы Layer=0 совпадал и порядок был предсказуем.

General rules — `rules/roles/editor.md`

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/redcon/
├── storyboard.json
├── scenes/
│   ├── refs/
│   │   ├── {char-slug}-canonical-ref.png
│   │   └── {char-slug}-alternate-ref.png
│   ├── scene-1/            (title card)
│   │   ├── scene-1.png
│   │   └── scene-1.mp4
│   └── scene-N/...
├── tts-output.mp3
├── build/
│   ├── concat-noaudio.mp4
│   └── concat-subbed.mp4
├── concat-list.txt
└── final.mp4
```

---

## Validation before publishing

- [ ] `format: "redcon"` in storyboard.json
- [ ] `character_speech: null` for ALL clips
- [ ] `tts_segment: null` for title card (clip 1 only)
- [ ] Two character refs generated: canonical + alternate
- [ ] Clip 2 `tts_segment` contains canonical name + alternate designation
- [ ] Divergence clip specifies year and canon event in `action_description`
- [ ] All images 608×1080
- [ ] No bg-reference files
- [ ] One PNG per scene — no end frames
- [ ] camera_angle differs between adjacent clips; every clip has active camera move
- [ ] Motion prompts: three concurrent layers, continuous verbs, no banned freeze phrases
- [ ] TTS voice = alternate-self identity (not canonical)
- [ ] Music from Dark/ only
- [ ] Subtitles via `add_subtitles.py` with `--offset 5`
- [ ] TTS delayed 5s in final mix (after title card)
- [ ] CTA included
- [ ] `-shortest` NOT used

---

## Anti-patterns

- ❌ Comedy tone — this format is serious lore, not fish-out-of-water
- ❌ Random divergence not grounded in canon
- ❌ Narrator framing ("In a universe where...") — character speaks directly
- ❌ Title card with character face (it must be text-first, atmospheric, not a portrait)
- ❌ TTS starting over the title card (5s silence before TTS in final mix)
- ❌ Single character ref — both canonical-self and alternate-self refs are mandatory
- ❌ Music from Fun/ — dark atmospheric only
- ❌ `generate_audio: true` in Kling I2V
- ❌ End frames / `tail_image_url`
- ❌ `-shortest` in FFmpeg
- ❌ Freeze phrases in motion_prompt
