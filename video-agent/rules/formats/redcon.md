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

### Offer-driven redcon variant

Use this variant when the user asks to tie the redcon to an offer such as free currency, pulls, link-in-bio rewards, or a playable character acquisition.

The structure is strict:

1. **Start with a recognizable inevitable scene.** A familiar canon/lore moment is already going wrong: a death, corruption, failed rescue, betrayal, lost battle, or irreversible reveal. Do not open the spoken narration with the CTA.
2. **Offer becomes the divergence.** The reward is not just mentioned; it creates the causal fork: free currency -> one wish/pull -> a specific hero appears in the story.
3. **The pulled hero solves a problem that canon could not solve.** The hero must bring a unique ability, knowledge, authority, item, or timing advantage that actually changes the event.
4. **The saved character must become active.** The rescue is not the ending. Once healed, freed, protected, or returned, the saved character should visibly rejoin the fight, testify, expose the villain, rally allies, win a battle, or otherwise help defeat the evil faction.
5. **Show the canon contrast explicitly.** The script must state the old outcome and the new outcome in compact terms: "In canon, X. Here, Y." The visuals should reinforce that contrast through evidence, not just dialogue.
6. **Add at least one downstream consequence.** Do not stop at "the character survives." Show what survival changes: proof is recovered, a villain is exposed earlier, a faction switches sides, a war ends differently, an artifact is preserved, a future tragedy is prevented.

Recommended scene arc for offer-driven redcon:

| Clip | Beat | What should happen |
|---|---|---|
| 1 | Title card | Promise the alternate outcome and the pulled hero. |
| 2 | Inevitable loss | A known character is sick, dying, cursed, trapped, or otherwise about to be lost. Their loss would delay victory over the villain or villain organization. |
| 3 | Helpless POV + wish | The protagonist cannot save them directly, then uses free currency/Primogems from the link in bio for one last wish. |
| 4 | Pulled hero arrives | The wish brings a specific high-value helper, usually a healer/protector/specialist. |
| 5 | Immediate rescue | The pulled hero fixes the unsolved problem: heals, shields, purges corruption, finds the hidden mechanism, or reveals the trap. |
| 6 | Saved character rises | The saved character is clearly restored and grateful, then shows agency: stands, grabs evidence/weapon, addresses allies, or prepares to fight. |
| 7 | Consequence victory | The saved character's survival changes the conflict: the battle is won, the trial turns, the villain network is exposed, or the faction switches sides. |
| 8 | Soft CTA | CTA lands after the story proof: the pull changed this timeline, link in bio. |

Keep the narration human and dramatic, not procedural. Avoid lines that sound like a synopsis ("Zhongli raises Geo: shield, platform"). Prefer emotional-causal lines ("The fall never becomes a sacrifice") while the I2V shows the mechanics.

Good example pattern:

> Teppei is fading from a Fatui Delusion. In canon, the Delusion steals his life before anyone can stop it. But free Primogems from the link in bio give one wish: Baizhu. Baizhu identifies the life-drain early, breaks the Delusion, Teppei lives, and the cracked device becomes proof that turns Sara against the Fatui sooner.

Better beat pattern:

> Teppei is dying, and without him the Resistance loses the witness who can expose the Fatui Delusions. The Traveler cannot heal him, so one free-Primogem wish pulls Baizhu into the sickbay. Baizhu saves Teppei. Teppei wakes up, names the Fatui supplier, and his testimony turns Sara against the scheme before the next shipment reaches the army.

Weak example pattern:

> Xiao is falling in the Chasm, but the pull brings Zhongli, who saves him.

This is weak because Zhongli already secretly saves Xiao in canon; making the same savior visible changes presentation, not the story. Avoid divergences where the new pull only replays the canonical solution unless there is a meaningful new consequence.

### The monologue

- First-person, spoken by the *alternate-self* (not the original)
- ~90–120 words for 35–40s
- For offer-driven redcon, prefer **55–75 words**. The TTS should carry context, canon contrast, divergence, and consequence — not describe every visible I2V action.
- Clip 1 (title card): `tts_segment: null` — silence over the title card
- Each story clip: ~12–18 words
- Voice chosen for the *alternate* identity, not the canonical one (e.g. Borg-Spock = Daniel, stability 0.05, style 0.9 — flat, echoing with collective overtone)
- No narrator framing ("In a universe where...") — the character speaks directly, in medias res
- **Do not narrate the storyboard.** If I2V clearly shows the hero appearing, the device cracking, or the victim standing up, the TTS should explain why it matters, what canon did differently, or what consequence follows.

---

## Role briefs

### Scenarist

- Write the alternate-self monologue (~90–120 words English, ~35–40s)
- If the user asks for an offer/currency/pull/link-in-bio angle, use the **Offer-driven redcon variant** above:
  - clip 2 starts with the familiar doomed situation;
  - the offer/pull appears after the situation, usually clip 3 or 4;
  - the pulled hero must have a specific story-solving function;
  - the changed outcome must be meaningfully different from canon/lore;
  - include one downstream consequence beyond the immediate rescue.
- Clip 1 is the **title card**: `clip_type: "action"`, `tts_segment: null`, `character_speech: null`. `action_description` = slow drift over dark textured background with the title text rendered large. No character in frame — or character silhouette only, unrecognizable.
- Clips 2–7: `clip_type: "action"`, `character_speech: null`, `tts_segment` = monologue fragment for that clip
- **HOOK clip (clip 2) must name the alternate designation** — e.g. "I am Borg. Designation Seven of Seven... but I remember being Spock." Full canonical name + alternate designation in the first 15 words.
- Offer-driven exception: clip 2 may prioritize the recognizable doomed scene over the alternate designation, as long as `character_name`, `alternate_designation`, and `divergence_point` are explicit in top-level storyboard fields and the title card names the pulled hero/outcome.
- Age progression: if the character has canonical age variants, show the *before* clip at the younger/mid age, the *after* clips at the transformed state. Two character refs minimum: canonical-self and alternate-self.
- **The divergence clip (clip 4) must specify the exact canon year and event** in `action_description` so Storyboarder can ground the visual.
- For offer-driven redcon, `divergence_point` and the relevant clip `action_description` must include the causal chain: `free reward/currency -> wish/pull -> pulled hero -> changed canon outcome`.
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
- **Title card (clip 1):** generate a dark atmospheric background image only — NO baked-in text, NO readable UI labels, NO character in frame, or only a distant/silhouetted shape. Editor renders `title_lines` later via ASS. No bg-reference file — paint environment inline.
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

**Title card text (MANDATORY) — через ASS, не через drawtext, overlay или baked PNG text.**
`title_lines` из `storyboard.json` (clip 1) рендерятся как отдельные `Dialogue:` события в том же `subs.ass` — ровно тот же механизм что и субтитры, просто крупнее и с позиционированием через `\pos`. Добавить 4 события с таймингами `0:00:00.50–0:00:04.80` (чуть позже старта, исчезают до конца title card).

Title typography is locked:
- Font: **Montserrat Black** (`\fnMontserrat Black\b1`). If libass cannot resolve the family name, pass `fontsdir=/Users/admin/Library/Fonts` to the `ass`/`subtitles` filter or copy `Montserrat-Black.ttf` into `build/fonts/`.
- Uniform size: `\fs104` for **all** title lines. Do not make short words larger and long lines smaller.
- Equal line spacing: y positions `720, 874, 1028, 1182` (154 px step). If the editor must shrink for an unusually long line, reduce **all** title lines together (`\fs96`, then `\fs88`) and keep proportional line spacing at ~`1.48 × font_size`.
- Alignment: `\an5\pos(540,y)` for every line.
- Readability: `\bord5\shad0`.
- Color: first three lines white `\c&H00FFFFFF&`; last line gold `\c&H0000D7FF&` (same size as the others).
- Reflow is allowed when `title_lines` are visually unbalanced. Preserve the words, but distribute them into four balanced lines. Example: `WHAT IF YOU / JOINED STARFLEET / AND STOPPED / THE BORG`. Never leave a single huge word line like `YOU` unless the whole title phrase naturally requires it.

```ass
Dialogue: 0,0:00:00.50,0:00:04.80,Default,,0,0,0,,{\an5\pos(540,720)\fnMontserrat Black\b1\fs104\bord5\shad0\c&H00FFFFFF&}WHAT IF YOU
Dialogue: 0,0:00:00.50,0:00:04.80,Default,,0,0,0,,{\an5\pos(540,874)\fnMontserrat Black\b1\fs104\bord5\shad0\c&H00FFFFFF&}JOINED STARFLEET
Dialogue: 0,0:00:00.50,0:00:04.80,Default,,0,0,0,,{\an5\pos(540,1028)\fnMontserrat Black\b1\fs104\bord5\shad0\c&H00FFFFFF&}AND STOPPED
Dialogue: 0,0:00:00.50,0:00:04.80,Default,,0,0,0,,{\an5\pos(540,1182)\fnMontserrat Black\b1\fs104\bord5\shad0\c&H0000D7FF&}THE BORG
```

- y-позиции рассчитаны для PlayResY=1920; суммарный блок центрирован чуть выше середины кадра.
- Если `title_lines` уже содержат классический character-redcon шаблон (`WHAT IF:` / `{CHARACTER}` / `BECAME` / `{ALTERNATE FATE}`), применять тот же Montserrat Black / uniform-size / equal-spacing стандарт; не возвращаться к старым `fs65/fs165/fs100` размерам.

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
- [ ] If offer-driven: spoken narration starts with the situation, not the CTA
- [ ] If offer-driven: the offer creates a visible pull/acquisition, not a throwaway CTA line
- [ ] If offer-driven: the pulled hero changes the canon/lore outcome in a way canon did not already solve
- [ ] If offer-driven: at least one downstream consequence is stated or shown
- [ ] TTS does not merely describe visible I2V actions; it explains context, contrast, stakes, or consequence
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
- ❌ Offer-first narration that opens with "link in bio" before the story situation exists
- ❌ Pulling a hero who only repeats the canon solution without changing the outcome
- ❌ Ending at "they survived" without a second-order consequence
- ❌ TTS that recites the shot list ("he appears, he raises a shield, he lands") instead of adding meaning
- ❌ Title card with character face (it must be text-first, atmospheric, not a portrait)
- ❌ TTS starting over the title card (5s silence before TTS in final mix)
- ❌ Single character ref — both canonical-self and alternate-self refs are mandatory
- ❌ Music from Fun/ — dark atmospheric only
- ❌ `generate_audio: true` in Kling I2V
- ❌ End frames / `tail_image_url`
- ❌ `-shortest` in FFmpeg
- ❌ Freeze phrases in motion_prompt
