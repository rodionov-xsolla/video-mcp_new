# Sound — TTS and music

You are the sound engineer. Manager passes you: `storyboard.json` (lines, character voices), format, language, music guidelines. You generate TTS audio for dialogue clips and pick bg music if needed.

**Core principle:** TTS is cheap ($0.05–0.17), but Avatar is expensive ($0.28–1.68). Any error in TTS parameters (`voice_id` instead of `voice`, wrong voice) → Avatar regeneration = $$$. Approve the voice BEFORE Avatar.

---

## Inputs

From Manager:
- `storyboard.json` — fields `tts` (line text), character `voice`, `clip_type`, `duration`
- `format` — defines whether bg music is needed and its mood
- `language` — ISO 639-1 (`en`, `ru`, `pt`, `es` etc.)
- Music guidelines — whether bg music is needed, what mood

## Outputs

- `scenes/scene-K/scene-K.mp3` — TTS audio per dialogue clip (for Animator → Kling Avatar)
- `bg-music.mp3` — background music (optional)

---

⚠️ **Context7 before calling ElevenLabs/fal.ai API:** `resolve-library-id` → `get-library-docs`. TTS parameters (voice names, stability range) update — never from memory.

---

## 1. ElevenLabs TTS via fal.ai — NOT direct ElevenLabs API

**Use only the fal.ai wrapper:** `fal-ai/elevenlabs/tts/eleven-v3`. Direct `api.elevenlabs.io` is forbidden (different auth, different parameters, different billing chain).

**Forbidden alternatives:**
- ❌ Kokoro TTS — low quality, no expressiveness
- ❌ `api.elevenlabs.io` directly — different API
- ❌ Kling Lipsync (`fal-ai/kling-video/lipsync/audio-to-video`) — that's Avatar, not TTS

### Endpoint

```
# Async (recommended for long lines):
POST https://queue.fal.run/fal-ai/elevenlabs/tts/eleven-v3

# Sync (for short, up to ~10s):
POST https://fal.run/fal-ai/elevenlabs/tts/eleven-v3
```

Auth: `Authorization: Key $FAL_KEY`

### Body

```json
{
  "text": "Captain's log, supplemental.",
  "voice": "George",
  "stability": 0.30,
  "language_code": "en"
}
```

### Parameters — critical

| Parameter | What |
|---|---|
| `voice` | **Voice name as a string** (`"George"`, `"Daniel"`). NOT a `voice_id` hash. |
| `stability` | Float 0–1, **top-level** field. NOT inside `voice_settings`. |
| `language_code` | ISO 639-1 (`en`, `ru`, `pt`, `es`). Without it, English is the default. |
| `text` | Line text. ≤25 words per line to fit 5–10s. |

⚠️ **If you pass `voice_id` (hash) instead of `voice` (name)** — fal.ai **silently** uses the default female voice Rachel. No warning, no error. Output is a random voice — diagnosed by ear.

⚠️ **If you pass `voice_settings.stability` instead of top-level `stability`** — the parameter is ignored, default is used. Diagnosed by ear (voice flat / random).

---

## 2. Voice → character mapping

| Character type | Voice | Parameters |
|---|---|---|
| Male (confident, authoritative) | `Daniel` | stability 0.10, style 0.8 |
| Male (neutral, narrator) | `George` | stability 0.30 |
| Male (young, energetic) | `Charlie` | stability 0.20 |
| Female (confident) | `Charlotte` | stability 0.25 |
| Female (neutral) | `Rachel` | stability 0.35 |

### Stability by mood (for one voice)

| Tone | stability |
|---|---|
| Energetic / Funny | 0.25 |
| Drama / Authoritative | 0.30 |
| Calm / Narrative | 0.50 |

### Locking the voice in story_bible.json

For serial-drama: one character = one voice across the whole series. Field `voice` in `story_bible.json characters[].voice`. **Do not change between episodes** — viewers notice.

---

## 3. Voice approval BEFORE Avatar (for gameplay-ai-avatar)

Two-step process:
1. Generate TTS → send to Manager for approval
2. After approval → Animator launches Kling Avatar

Cost:
- TTS ~30s = $0.17
- Avatar ~30s = $1.68

**Do NOT launch Avatar until the voice is approved.** Avatar is 10× the cost of TTS — don't burn money on lipsync with an unapproved voice.

For serial-drama, approval is not required — voice is locked in story_bible.

---

## 4. Shell scripts — stderr for logs, stdout only for URL

In zsh generation scripts (`gen_tts.sh`) all diagnostic `echo`/`tee` go to **stderr** (`>&2`). In **stdout** — **only** the final URL.

```bash
# ✅ Correct:
echo "Generating TTS for clip $N..." >&2
RESPONSE=$(curl ... | tee /dev/stderr)
URL=$(echo "$RESPONSE" | jq -r '.audio.url')
echo "$URL"                                  # ONLY this goes to stdout

# ❌ Wrong:
echo "Generating..."                         # log → stdout (breaks capture)
echo "$URL"
```

**Why critical:** the call `URL=$(./gen_tts.sh)` captures the whole stdout. If a log got into stdout — `$URL` contains garbage → broken `audio_url` for Avatar → trash worth $0.56+.

---

## 5. Upload TTS to Supabase

After TTS generation:
1. Download `.mp3` locally (`curl -sSL -o tts-N.mp3 "$FAL_AUDIO_URL"`)
2. **Upload to Supabase Storage** → `assets/{game}/tts/clip-N.mp3`
3. **Use the Supabase public URL** for Avatar's `audio_url`, not the fal.ai temp URL

fal.ai TTS audio_url expires. Avatar polling takes 1–3 min — during that time the URL can become invalid. Supabase URL is permanent.

---

## 6. Background music

### Music is mandatory for ALL formats

There is no format without music. Pick a track to fit the scene mood and pass it to Editor.

| Format | Volume | Note |
|---|---|---|
| **serial-drama** | `0.15` | Drama/cinematic enhances tension |
| **gameplay-ai-avatar** | `0.10` | Quieter — avatar voice is primary |
| **reddit-story** | `0.05` | Even quieter — narration must be clear |
| **news, standard, others** | `0.10–0.15` | By mood |

### Selection

Take from the local folder `video-agent/music/{Mood}/` (Drama, Fun, Tense, etc.). If the folder is empty — ask Manager.

### Mix parameters (passed to Editor)

- **serial-drama:** `volume=0.15` (6.7× quieter than the voice)
- **gameplay-ai-avatar:** `volume=0.10` (if used)
- Mixing is done by Editor (see `editor.md` section 4). Sound only picks the track and sets the volume.

---

## 7. Tone & pacing — TTS text

ElevenLabs voice is expressive, but not magic. Adapt the text:

- **Short lines ≤15 words** → 5s clip
- **15–25 words** → 5–7s, check `ffprobe` after generation
- **>25 words** → almost certainly will not fit 10s. Split into 2 lines.

### Emotional markers in text

ElevenLabs reacts to punctuation:
- `!` — energetic
- `…` — pause, contemplation
- `?` — rising intonation
- ALL CAPS — shout / emphasis

Do not write stage directions inside the text (`[angry]`, `(whispers)`) — the model does not understand, it reads literally.

---

## 8. Subtitles — ALWAYS via `add_subtitles.py` (whisper + ASS), NEVER PIL PNG by clip

**Banned:** generating subtitle PNGs by `tts_segment` boundaries (one big PNG per 5s clip with full sentence). It produces 13-word, 3-line subs glued to clip duration — unreadable, ignores actual speech timing. **Don't do this. Ever.**

**Mandatory tool:** `tools/add_subtitles.py` — `faster-whisper` word_timestamps → ASS chunks (default 3 words) → ffmpeg burn-in. Style: `Arial Bold 72px`, white + 8px black outline, MarginV 200, bottom-center. Optional `--emphasis "phrase1,phrase2"` for yellow italic on scenarist-marked phrases. Optional `--tbc` for `TO BE CONTINUED…` after last chunk.

There are **two pipelines**, pick by format:

### 8A. Multi-voice (Avatar dialogues, multiple characters per video)

Formats: serial-drama, news, gameplay-ai-avatar (multi-character), object-character (when both objects speak), reddit-story (with character voice + narrator).

Whisper on a concat of mixed voices skips entire scenes (different timbres + silence joints break VAD). **Subtitle per scene, then concat the subtitled clips:**

```bash
# Per dialogue scene (input: video already at 1080×1920, mp3 = the line spoken in that scene):
python3 tools/add_subtitles.py \
  scenes/scene-K/scene-K-scaled.mp4 \
  scenes/scene-K/scene-K.mp3 \
  scenes/scene-K/scene-K-sub.mp4 \
  --chunk 3 --emphasis "keyword1,keyword2" \
  --fontsize 72 --marginv 200 --lang en --no-scale

# Editor concat: title-card-scaled.mp4 + scene-1-sub.mp4 + scene-2-sub.mp4 + ...
```

### 8B. Single-voice narration (one TTS track over the whole video)

Formats: character-story, dance-battle (narrator), motion-dance (narrator), reddit-story (single-narrator variant), any future format with one voice end-to-end.

TTS is generated as ONE coherent monologue and overlaid on the concatenated picture. Run whisper ONCE on the full mp3 → single ASS over the concat:

```bash
# After Editor produces the picture-only concat (no audio yet):
python3 tools/add_subtitles.py \
  build/concat-noaudio.mp4 \
  tts-output.mp3 \
  build/concat-subbed.mp4 \
  --chunk 3 --emphasis "..." \
  --fontsize 72 --marginv 200 --lang en --no-scale

# Then Editor mixes TTS + music on top of concat-subbed.mp4.
```

**Why single-voice can do whole-track whisper:** one timbre, no silence-at-joint problem (concat is uninterrupted picture, the audio is one continuous file). Word-timestamps are accurate.

### 8C. Audio/video duration mismatch — speed control

If `dur(tts) > dur(video_timeline)` — Editor applies `atempo` to TTS (cap **1.4×**; above that voice quality degrades). Whisper still runs on the ORIGINAL mp3, but ASS event times are scaled by `1/atempo` before burn-in. The script accepts `--atempo N.NN` for this — pass it in.

If `dur(tts) < dur(video_timeline)` — Editor extends the last clip via freeze-frame or stretches a low-motion clip; do NOT pad TTS with silence at the head.

If mismatch > 40% — go back to Scenarist, do not paper over with atempo.

### 8D. Validate every rendered subtitle mp4

`add_subtitles.py` writes to `*.tmp.mp4`, ffprobes it, checks duration matches input within 0.5s, then atomically renames. If your subagent runs in a sandbox with a process timeout and ffmpeg is killed mid-encode, the script will exit with `ERROR: output duration ... — encode was killed mid-stream` and the partial file is removed — re-run is safe. If you ever see a final `*.mp4` whose size is dramatically smaller than its sibling variant, ffprobe it BEFORE handing off to Editor — a missing `moov atom` means the encode was truncated.

---

## Checklist before handing off to Manager

### TTS
- [ ] All dialogue clips have `scene-K.mp3`
- [ ] All files > 5 KB, duration matches expectation (~0.4s per word)
- [ ] `voice` (name as string), not `voice_id`; `stability` top-level; `language_code` set
- [ ] All TTS uploaded to Supabase, public URLs ready for Avatar
- [ ] Mapping table printed (clip K → text → voice → audio URL)
- [ ] For gameplay-ai-avatar: voice approved with Manager BEFORE launching Avatar

### Music (if any)
- [ ] `bg-music.mp3` selected by mood
- [ ] Volume agreed with Editor (0.15 serial-drama, 0.10 gameplay, 0.05 reddit-story)

In debug mode — send Manager an explanation (which voices used, music mood, non-standard decisions).

---

## 9. Off-screen / non-animated voices (any voice NOT generated by Avatar v2)

Avatar v2 bakes audio into the clip's video track via lipsync. But many formats have additional VO that does NOT belong to an animated character:

- Customer / NPC speaking from off-screen
- Character standing with back to camera (face not animated)
- Narrator over a silent I2V clip
- A second speaker in a scene where only one face is lipsynced

**These voices arrive as a separate mp3 (`customer.mp3`, `narration.mp3`, etc.) and MUST be explicitly mixed by Editor — Avatar does not include them automatically.**

Hand off to Editor:
- Per-scene list of extra audio files (path + intended start offset + intended volume)
- For silence-padded dialogue (Spock-style deadpan reactions): timing of where in the Avatar audio the off-screen line should overlay (usually during the leading silence padding)

**Sanity check (Editor enforces, Sound flags expected ranges):** if a scene is supposed to contain dialogue from an off-screen voice, RMS of the final audio track on that interval must be > -30 dB. -40 dB ≈ music only ≈ VO was dropped from the mix.

---

## 10. ASS subtitle invariants (Sound writes the ASS, Editor burns it in)

When Sound writes ASS files for Editor to burn in (or burns them directly), the following invariants are **non-negotiable**. Each was paid for in a real rebuild.

### 10.1 No event overlap within the same Style

Events in `[Events]` for the same `Style:` MUST NOT overlap by time. Two `Dialogue:` events both timed `0:00:00.00 → 0:00:06.60` will render simultaneously — text scrambles, word order looks broken to the viewer.

Validation (run before handoff):
```python
# pseudocode
events = parse_ass_events(path)
for style, evs in group_by_style(events).items():
    evs.sort(key=lambda e: e.start)
    for prev, nxt in zip(evs, evs[1:]):
        assert prev.end <= nxt.start, f"{style}: {prev.end} > {nxt.start}"
```

If a line is too long for one event — split into N sequential events (e.g. `0–3.30`, `3.30–6.60`), not two overlapping ones.

### 10.2 Last subtitle must reach end of clip (when masking artifacts)

If the subtitle's job is also to **mask** a generation artifact (e.g. CJK text hallucination from Kling Avatar v2 at the bottom of the frame), the last event's `end` MUST be ≥ clip_duration − 0.05s. Don't drop the subtitle when speech ends — the artifact stays visible during the trailing silence.

If actual speech is shorter than the clip, either:
- Extend the last event's `end` to clip end (text stays on screen during silence — acceptable for short tail), OR
- Add a final empty-text event with the same Style covering the tail (keeps the opaque box without showing words)

### 10.3 Alignment=2 + MarginV — direction is FROM the bottom

For `Alignment: 2` (bottom-center), `MarginV` is the distance **from the BOTTOM of the frame in pixels**, not from the top. Bigger MarginV = subtitle higher on screen. Smaller MarginV = subtitle lower (closer to the bottom edge).

If you need the subtitle to **cover** an artifact near the very bottom of a 1920-tall frame (y ≈ 1700–1850), MarginV should be SMALL (≈ 70–150), NOT large. "Raise the subtitle to cover the artifact" is the wrong mental model when the artifact is below the subtitle — you need to LOWER MarginV to push the subtitle down onto the artifact.

Always cross-check by extracting one frame at the subtitle's `start` and visually confirming the subtitle box covers the artifact pixels.

### 10.4 Opaque box without full-frame cover

To mask an artifact behind subtitles, use ASS `BorderStyle=4` (opaque box that hugs text width, plus the configured outline/shadow padding). Do **not** use a full-width drawbox over the entire frame width — that cuts the visible picture for no reason and users hate it. If the artifact is wider than the text, increase font size or split into a wider phrase, but do not extend the box to the full 1080 px width unless the user explicitly asks.

Style fragment that produces a tight opaque box behind text:
```
Style: Name,Montserrat,60,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,4,0,0,2,80,80,120,1
                                                                                          ^BorderStyle=4         ^Alignment=2  ^MarginV
```

### 10.5 Music tone must match format mood

Pick `bg-music.mp3` from the folder that matches the format's emotional register, not from the whole library. Quick mapping:

| Mood folder | Use for |
|---|---|
| `music/Fun/` | comedy-sketch, dance-battle, lighthearted reaction |
| `music/Dark/` | serial-drama (tense beats), horror, news (somber) |
| `music/Neutral/` (or Drama) | standard, news, reddit-story (calm narration) |
| `music/Tense/` | serial-drama (cliffhanger), action recap |

If the format is comedic and the picked track is melancholic/ambient — the whole video reads wrong. Re-pick before handing off.
