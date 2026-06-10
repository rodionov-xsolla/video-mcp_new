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
- (субтитры — НЕ артефакт Sound; Editor генерит их сам по whisper, см. §8)

---

---

## 1. TTS engine selection

| Condition | Engine |
|---|---|
| `game_tag == "genshin impact"` (ANY format) | **Chatterbox** (§1b) — voice cloned from reference MP3 |
| All other games and formats | **MiniMax** (§1a) — preset voices |

**Genshin voice refs** live in Supabase Storage at `assets/genshin-impact/characters/{slug}/voice-1.mp3` (also voice-2.mp3, voice-3.mp3 where available). Use `voice-1.mp3` as the primary `audio_url` for Chatterbox. **105+ characters confirmed to have refs** — effectively the entire playable roster. For the rare character without a voice ref → fall back to MiniMax.

---

## 1a. MiniMax TTS via fal.ai

**Endpoint:**
```
# Async (recommended):
POST https://queue.fal.run/fal-ai/minimax/speech-2.8-hd

# Sync (short lines up to ~10s):
POST https://fal.run/fal-ai/minimax/speech-2.8-hd
```

Auth: `Authorization: Key $FAL_KEY`

### Body — always write to file, never inline shell string

```bash
cat > /tmp/tts-K.json <<EOF
{
  "prompt": "Captain's log, supplemental.",
  "voice_setting": {
    "voice_id": "Determined_Man",
    "speed": 0.9,
    "emotion": "neutral"
  },
  "audio_setting": { "format": "mp3" }
}
EOF

RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/minimax/speech-2.8-hd" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/tts-K.json)
```

### Parameters — critical

| Parameter | What |
|---|---|
| `prompt` | Text. Field is `prompt`, NOT `text`. ≤25 words per line. |
| `voice_setting.voice_id` | Voice name string — see mapping table below. |
| `voice_setting.emotion` | `angry`, `happy`, `sad`, `fearful`, `disgusted`, `surprised`, `neutral` |
| `voice_setting.speed` | 0.5–2.0. Default 1.0. Use 0.85–0.95 for dramatic delivery. |

⚠️ **Field is `prompt`, NOT `text`.** Using `text` → silent failure, empty audio.

### Emotive tags (insert directly in `prompt` text)

| Tag | Sound |
|-----|-------|
| `(laughs)` | laugh |
| `(groans)` | groan |
| `(sighs)` | sigh |
| `(coughs)` | cough |
| `(gasps)` | gasp |
| `(sniffs)` | sniff |
| `(yawns)` | yawn |
| `(clears throat)` | throat clear |
| `<#0.5#>` | pause N seconds |

### Polling

```bash
# Base = fal-ai/minimax (2 segments only)
STATUS_URL="https://queue.fal.run/fal-ai/minimax/requests/${REQUEST_ID}/status"
RESULT_URL="https://queue.fal.run/fal-ai/minimax/requests/${REQUEST_ID}"
```

**Forbidden:**
- ❌ Kokoro TTS — low quality
- ❌ ElevenLabs (`fal-ai/elevenlabs`) — replaced by MiniMax
- ❌ Kling Lipsync — that's Avatar, not TTS

---

## 1b. Chatterbox TTS via fal.ai (Genshin Impact serial-drama only)

Zero-shot voice cloning — no training, no extra cost. Pass the reference MP3 on every call.

**Endpoint:**
```
POST https://queue.fal.run/fal-ai/chatterbox/text-to-speech
```

Auth: `Authorization: Key $FAL_KEY`

### Body

```bash
cat > /tmp/tts-K.json <<EOF
{
  "text": "You shouldn't have come here.",
  "audio_url": "https://<supabase>/assets/genshin-impact/characters/tartaglia/voice-ref.mp3",
  "exaggeration": 0.55,
  "cfg": 0.5,
  "temperature": 0.7
}
EOF

RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/chatterbox/text-to-speech" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/tts-K.json)
```

### Parameters

| Parameter | What |
|---|---|
| `text` | Text to synthesize. Field is `text`. Per-clip dialogue: ≤25 words. Full monologue: ≤35 words per chunk — see §"Long-text monologue" below. |
| `audio_url` | Supabase public URL of the character's reference MP3. **Must be Supabase URL, not local path.** |
| `exaggeration` | 0.0–1.0. Emotional intensity. Dramatic dialogue: `0.6–0.7`. Whispers/calm: `0.3–0.4`. Default `0.25`. |
| `cfg` | 0.1–1.0. Guidance weight (pacing adherence). Higher = closer to reference cadence. Default `0.5`. ⚠️ Field is `cfg`, NOT `cfg_weight`. |
| `temperature` | 0.05–2.0. Higher = more expressive/creative. Default `0.7`. |
| `seed` | Optional int. Use for reproducibility. |

### Response — WAV output

```json
{ "audio": { "url": "https://v3b.fal.media/files/xxx/audio.wav", "content_type": "audio/wav" } }
```

Output is **WAV**. Convert to MP3 after download:
```bash
curl -sSL -o /tmp/tts-K.wav "$AUDIO_URL"
ffmpeg -i /tmp/tts-K.wav -codec:a libmp3lame -qscale:a 2 scenes/scene-K/scene-K.mp3
```

### Reference voice files — upload once per series, reuse URL

Reference MP3s live in `games/genshin impact/`. Upload each to Supabase **once** before EP1 and store the permanent URL in the story bible `voice_ref_url` field.

Subsequent episodes: read `voice_ref_url` from the story bible, pass directly as `audio_url`.

### Polling (base path = `fal-ai/chatterbox`)

```bash
# Submit → base is first 2 segments of the endpoint path
STATUS_URL="https://queue.fal.run/fal-ai/chatterbox/requests/${REQUEST_ID}/status"
RESULT_URL="https://queue.fal.run/fal-ai/chatterbox/requests/${REQUEST_ID}"
```

### ⚠️ Body must be built via Python — never bash heredoc

Apostrophes in TTS text (e.g. `"You shouldn't have come here."`) break bash single-quote heredoc substitution silently — the text field arrives empty and Chatterbox generates blank audio. Always write the JSON body with Python:

```python
import json, subprocess
body = {
    "text": "You shouldn't have come here.",
    "audio_url": "https://.../voice-ref.mp3",
    "exaggeration": 0.65,
    "cfg": 0.45,
    "temperature": 0.7
}
with open("/tmp/tts-K.json", "w") as f:
    json.dump(body, f)
# Then: curl -s -X POST "..." -H "..." -d @/tmp/tts-K.json
```

### ⚠️ Long-text monologue: 90+ words → mandatory chunking

Chatterbox **silently fails** on inputs of 90+ words. Symptoms: phrases shuffle order, later fragments appear at 8–10s, clips 6-7 become garbled repetitions or hallucinations. The output audio is shorter than expected (~29s for 90w instead of ~37s) and missing large sections.

**Root cause:** Chatterbox has an internal context window; it does not error — it produces broken audio without warning.

**Mandatory fix for character-story and any full-monologue TTS > 80 words:**

1. Split the monologue into chunks of **≤35 words** each
2. Generate each chunk as a **separate Chatterbox request** (same `audio_url`, `exaggeration`, `cfg`, `temperature`)
3. Download each chunk as `.wav`
4. Concatenate with ffmpeg:

```bash
# write concat list
printf "file '/tmp/chunk1.wav'\nfile '/tmp/chunk2.wav'\nfile '/tmp/chunk3.wav'\n" > /tmp/chunks.txt

ffmpeg -y -f concat -safe 0 -i /tmp/chunks.txt \
  -codec:a libmp3lame -qscale:a 2 \
  /tmp/tts-full.mp3
```

5. Measure combined duration (`ffprobe -i /tmp/tts-full.mp3 -show_entries format=duration`). If `dur(tts) > dur(timeline)` — apply `atempo` ≤ 1.1× in the final FFmpeg assembly (cap at 1.4× total).
6. **Verify with Whisper** if available: `faster-whisper /tmp/tts-full.mp3 --model medium` — all N clips must appear in order and in full.

**Chunk boundaries for 7-clip character-story (~90 words):**
- Chunk 1: clips 1–3 (~38 words)
- Chunk 2: clips 4–5 (~26 words)
- Chunk 3: clips 6–7 (~26 words)

Never pass the whole monologue as a single Chatterbox call if total word count > 80. No exception.

---

### Emotion guide for Genshin characters

| Character | Scene type | exaggeration | cfg |
|---|---|---|---|
| Childe | casual / cocky | 0.55 | 0.50 |
| Childe | intense / combat | 0.70 | 0.45 |
| Childe | cold threat / menace | 0.30 | 0.70 |
| Childe | whisper (secret, apology) | 0.18–0.20 | 0.72–0.75 |
| Childe | cliffhanger reveal | 0.55 | 0.50 |
| Lumine | determined / composed | 0.55 | 0.50 |
| Lumine | desperate / raw urgency | 0.82–0.85 | 0.35–0.40 |
| Lumine | defiant anger | 0.68–0.72 | 0.42–0.45 |
| Lumine | angry / betrayed | 0.65 | 0.45 |
| Agent | cold orders | 0.40 | 0.60 |
| Agent | threatening | 0.55 | 0.55 |

**Rule: never use default `exaggeration 0.25` for serial-drama dialogue.** Every line has an emotional register — look at `facial_expression` and `character_state` in storyboard.json to pick the row above. If a scene has no clear match, use `exaggeration 0.45` (neutral drama floor).

---

## 2. Voice → character mapping

| Character type | voice_id | emotion |
|---|---|---|
| Male (confident, authoritative) | `Deep_Voice_Man` | `angry` or `neutral` |
| Male (neutral, narrator) | `Determined_Man` | `neutral` |
| Male (young, energetic) | `Casual_Guy` | `happy` or `neutral` |
| Male (imposing, villain) | `Imposing_Manner` | `angry` |
| Male (logical, calm) | `Elegant_Man` | `neutral` |
| Male (patient, wise) | `Patient_Man` | `neutral` |
| Male (young hero) | `Young_Knight` | `angry` or `neutral` |
| Female (confident) | `Inspirational_girl` | `neutral` |
| Female (neutral) | `Calm_Woman` | `neutral` |
| Female (friendly) | `Friendly_Person` | `happy` |

### Speed by tone

| Tone | speed |
|---|---|
| Energetic / Funny | 1.0 |
| Drama / Authoritative | 0.9 |
| Calm / Narrative | 0.85 |

### Locking the voice in story_bible.json

For serial-drama: one character = one voice across the whole series. Field `voice` in `story_bible.json characters[].voice`. **Do not change between episodes** — viewers notice.

### One character = one voice = one pass within an episode

All lines of a character in one episode are generated **with the same `voice` + `stability`**, ideally in one batch. **Never regenerate a single line into a parallel file** (`ep6-scene-1-new.mp3`, `..-v2`, `..-fixed`). A one-off re-gen drops the locked voice/stability params and produces an audibly different voice for the same character — EP6's Admiral spoke with two different voices because scene 1 was re-rendered as a separate `-new` file while scene 3 kept the original. Regeneration overwrites the **same** filename keyed to the clip index (archive the old one first). If you re-do one line, re-confirm `voice`/`stability` match every other line of that character.

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
2. **Upload via `queue/upload-asset.sh`** (НЕ raw curl):
   ```bash
   queue/upload-asset.sh --kind episode-tts --game {GAME_TAG} \
     --episode {YYYY-MM-DD}-{format_slug} --name clip-N.mp3 ./tts-N.mp3
   ```
   Path → `episodes/{game}/{YYYY-MM-DD}-{format}/tts/clip-N.mp3`. **НЕ регистрируется** в `game_assets` (одноразовое).
3. **Use the returned Supabase public URL** for Avatar's `audio_url`, not the fal.ai temp URL

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
| **news, others** | `0.10–0.15` | By mood |

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

Use only the supported emotive tags from §1 (`(laughs)`, `(groans)`, etc.). Any other stage directions (`[angry]`, `(whispers)`, `[quietly]`) — the model reads literally as text. Emotion control goes in `voice_setting.emotion`, not in the text.

---

## 8. Subtitles — Sound НЕ касается субтитров вообще

**Sound не генерирует PNG, не бёрнит ASS, не пишет `timings.json`.** Субтитры полностью на Editor:
он гоняет faster-whisper по финальной речевой дорожке (`build/voice-final.wav`) и бёрнит единый
универсальный ASS. Текст — канонический из storyboard. Подробнее — `rules/roles/editor.md` §6.

Твоя единственная задача — качественные `scene-K.mp3` (TTS) и `bg-music.mp3`. Всё.

### Запрещено

- ❌ Генерация PNG-сабов / запись `*.ass` / `*.timings.json` из sound — это работа editor'а.
- ❌ Пропорциональные тайминги (`--text`) — удалены из пайплайна вообще (whisper по реальному звуку).

### Audio/video duration mismatch — speed control

Если `dur(tts) > dur(video_timeline)` — Editor применит `atempo` к TTS (cap **1.4×**; выше деградирует
голос). Субтитры считаются по УЖЕ ускоренной речи (`voice-final.wav`), так что съехать не могут —
тебе ничего пересчитывать не нужно.

Если `dur(tts) < dur(video_timeline)` — Editor расширит последний клип freeze-frame'ом; **не** допы тишиной в начале TTS.

Если несоответствие > 40% — обратно к Scenarist, не маскировать atempo.

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

## 10. ASS subtitle invariants — переехали в editor.md

ASS-инварианты (no event overlap, last-event reaches clip end, MarginV direction, opaque box не во всю ширину) — это работа Editor, см. `rules/roles/editor.md` §subtitles. Sound не пишет ASS.

## 11. Music tone must match format mood

Pick `bg-music.mp3` from the folder that matches the format's emotional register, not from the whole library. Quick mapping:

| Mood folder | Use for |
|---|---|
| `music/Fun/` | comedy-sketch, lighthearted reaction |
| `music/Dark/` | serial-drama (tense beats), horror, news (somber) |
| `music/Neutral/` (or Drama) | news, reddit-story (calm narration) |
| `music/Tense/` | serial-drama (cliffhanger), action recap |

If the format is comedic and the picked track is melancholic/ambient — the whole video reads wrong. Re-pick before handing off.

---

## 12. `timings.json` — УДАЛЁН из пайплайна

Раньше Sound писал `scene-K.timings.json`. Больше **не нужно**: Editor гоняет faster-whisper по
финальной речевой дорожке (`build/voice-final.wav`) и берёт границы слов прямо из событий
`build/subs.ass`. Никаких `--emit-timings`, никаких `--text`. Sound не создаёт `*.timings.json`.

Snap-to-word-boundary при тримминге хвоста (если был нужен) Editor делает по `subs.ass`-событиям.
