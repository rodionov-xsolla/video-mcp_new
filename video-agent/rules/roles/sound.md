# Sound — TTS and music

You are the sound engineer. Manager passes you: `storyboard.json` (lines, character voices), format, language, music guidelines. You generate TTS audio only for formats that require external TTS, and generate background music when needed.

**Core principle:** TTS is cheap ($0.05–0.17), but downstream video regeneration is expensive. Any error in voice mapping or audio URL can burn paid video budget (Kling Avatar, H3 lip-sync).

**Serial-drama override:** serial-drama dialogue is H3 lip-sync on our own MiniMax TTS (§5a). For every dialogue clip you generate each `character_speech` line in the speaker's locked series voice (§5a: the series' special-file table or `characters[].tts_voice`; a new pick only for a character with none), build the clip's one audio file, upload it as the clip's `tts_url` and write its length back; the Animator sends that file as the H3 lip-sync `target_audio_url`. Kling `voice_ids` / `create-voice` are no longer used.

---

## Inputs

From Manager:
- `storyboard.json` — fields `tts` (line text), character `voice`, `clip_type`, `duration`
- `format` — defines whether bg music is needed and its mood
- `language` — ISO 639-1 (`en`, `ru`, `pt`, `es` etc.)
- Music guidelines — whether bg music is needed, what mood

## Outputs

- `scenes/scene-K/scene-K.mp3` — TTS audio per dialogue clip for Avatar, H3 lip-sync (what-if-real-life, serial-drama) and TTS-overlay formats. Serial-drama also keeps one file per line (`scene-K-line-N.mp3`) and writes `tts_voices` (§5a).
- `bg-music.mp3` — background music when required by the format; **always required for serial-drama**
- (subtitles are NOT a Sound artifact; Editor generates them itself via whisper, see §8)

---

---

## 1. TTS engine selection

| Condition | Engine |
|---|---|
| The format explicitly uses native generated dialogue | **Native audio** — do not generate duplicate TTS |
| Serial-drama dialogue (H3 lip-sync) | **MiniMax** (§1a) in the character's locked series voice (§5a) — always, also for characters that have older voice samples |
| The exact format/series story bible owns an approved voice sample | **Chatterbox** (§1b) with that exact sample |
| Narrator/voice identity is not important, or the exact format has no approved sample | **MiniMax** (§1a) |

Voice samples are format/series-bound. Never search for or reuse a sample from another format, even inside the same game. The only exception is an explicit user instruction to copy it.

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
- ❌ ElevenLabs **TTS** (`fal-ai/elevenlabs/tts/*`)
- ✅ `fal-ai/elevenlabs/sound-effects` remains allowed for sound effects only
- ❌ Kling Lipsync — that's Avatar, not TTS

---

## 1b. Chatterbox TTS via fal.ai (only with an approved exact-format voice sample)

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
    "audio_url": "https://<supabase>/<exact-format-series>/voice-ref.mp3",
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

### Reference voice files — exact format/series ownership

Use only a permanent `voice_ref_url` already approved in the exact format/series story bible. A new sample remains run-local until the user approves the final video; Manager then records it in that same story bible. Missing or unapproved samples do not authorize cross-format lookup: use MiniMax when voice identity is unimportant, otherwise stop and ask the user.

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
6. Validate technically only: file exists, size is plausible, and `ffprobe` reports the expected duration range. Do not run semantic/AI review of the audio.

**Chunk boundaries for 7-clip character-story (~90 words):**
- Chunk 1: clips 1–3 (~38 words)
- Chunk 2: clips 4–5 (~26 words)
- Chunk 3: clips 6–7 (~26 words)

Never pass the whole monologue as a single Chatterbox call if total word count > 80. No exception.

---

### Example emotion guide for an exact-format approved Genshin voice sample

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

Within one format/series: one character = one voice across the whole series. Field `voice` in that format's `story_bible.json characters[].voice`; serial-drama uses `characters[].tts_voice` (`{"voice_id", "speed"}`, §5a). **Do not change between episodes** and do not borrow it for another format. A new pick stays run-local (in `storyboard.json`) until the user approves the episode; Manager then writes it to the bible.

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

For an existing exact-format/series voice already approved and locked in its story bible, no extra per-run voice approval is required. A new or missing sample stops for user direction.

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
2. **Upload via `queue/upload-asset.sh`** (NOT raw curl):
   ```bash
   queue/upload-asset.sh --kind episode-tts --game {GAME_TAG} \
     --episode {YYYY-MM-DD}-{format_slug} --name clip-N.mp3 ./tts-N.mp3
   ```
   Path → `episodes/{game}/{YYYY-MM-DD}-{format}/tts/clip-N.mp3`. **NOT registered** in `game_assets` (disposable, one-off).
3. **Use the returned Supabase public URL** for Avatar's `audio_url` or H3 lip-sync's `target_audio_url` (what-if-real-life and serial-drama dialogue), not the fal.ai temp URL

fal.ai TTS audio_url expires. Avatar polling takes 1–3 min — during that time the URL can become invalid. Supabase URL is permanent.

---

## 5a. Serial-drama dialogue — TTS for H3 lip-sync

Every serial-drama `clip_type: "dialogue"` clip is an H3 lip-sync clip (`rules/formats/serial-drama.md`): H3 Max Turbo moves the visible speakers' lips to one audio file and returns that file unchanged as the clip's soundtrack. You make that file. Tested in the cost trials (Test 9, `trials/2026-10-cost-trials/`, The Airlock S2E1): 3 dialogue clips, 6 lines, 249 characters, $0.025 of TTS.

**1. Voices — one MiniMax voice per speaking character, for the whole series.** Use the series' locked voices; pick only for a character that has none.
- **Locked voices**, in this order: (a) the series' "Locked TTS voices" table in `games/{GAME_TAG}/serial-drama_special.md`, when that file applies to the resolved series (it names the series and its bible; The Airlock's table holds the Test 9 voices: Kirk `Determined_Man` 0.9, Scotty `Casual_Guy` 1.0, Fleet Admiral `Imposing_Manner` 0.9, Worf `Deep_Voice_Man` 0.9); (b) `characters[].tts_voice` (`{"voice_id", "speed"}`) in the exact series bible. Use them exactly; never re-pick a locked character.
- A speaker with no locked voice: pick one from §2 (character type → `voice_id`; tone → `speed`, e.g. drama/authoritative 0.9, energetic 1.0). Two characters who share a clip must sound clearly apart (different `voice_id`, or at least a different speed and register). If the character's legacy `voice` field already names a MiniMax preset from §2, use it. Never use the Kling-era fields (`voice_id_kling`, `voice_ref_url`, `voice_route`), an ElevenLabs ID, or a voice from another format or series.
- Record every speaker of the episode in `storyboard.json` (top level):
  ```json
  "tts_voices": {
    "Kirk":   {"voice_id": "Determined_Man", "speed": 0.9, "source": "locked"},
    "<speaker without a locked voice>": {"voice_id": "<§2 preset>", "speed": 1.0, "source": "new"}
  }
  ```
  `"locked"` = from the special file's table, `"bible"` = from `characters[].tts_voice`, `"new"` = picked in this run. Do **not** edit the story bible or the special file: Manager writes the `new` picks to `characters[].tts_voice` only after the user approves the episode.
- Debug mode: report the mapping table (character → `voice_id` → speed → locked/bible/new) at the Phase 2 stop. If the user changes a pick, regenerate **every** line of that character under the same filenames (§2 "one pass").

**2. Lines.** For each dialogue clip K and each `character_speech` item N (in order), generate the line with MiniMax TTS (§1a, `fal-ai/minimax/speech-2.8-hd`), one request per line, with exactly the body tested in Test 9:
```json
{
  "prompt": "<the line, verbatim>",
  "voice_setting": {"voice_id": "<speaker's voice_id>", "speed": <speaker's speed>, "emotion": "<emotion for this line>"},
  "audio_setting": {"format": "mp3"},
  "language_boost": "English"
}
```
`emotion` is picked per line from the scene's `facial_expression` / `character_state` (§1a emotion list); `language_boost` is `"English"` for `en` (the tested value; another run language uses that language's name). Save `scenes/scene-K/scene-K-line-N.mp3`. All lines of one character use the same `voice_id` and `speed`.

**3. Clip audio.** Build `scenes/scene-K/scene-K.mp3`: 0.2 s of silence, then the lines in order with 0.3 s of silence between consecutive lines, mono 44.1 kHz MP3 (the Test 9 recipe; two-line example):
```bash
ffmpeg -nostdin -y -i scene-K-line-1.mp3 -i scene-K-line-2.mp3 -filter_complex \
  "anullsrc=r=44100:cl=mono,atrim=0:0.2[s0];anullsrc=r=44100:cl=mono,atrim=0:0.3[s1];\
[0:a]aresample=44100,aformat=channel_layouts=mono[a0];[1:a]aresample=44100,aformat=channel_layouts=mono[a1];\
[s0][a0][s1][a1]concat=n=4:v=0:a=1[o]" -map '[o]' -ar 44100 -ac 1 -c:a libmp3lame -q:a 2 scene-K.mp3
```
More lines add one `[sN]` 0.3 s gap and one `[aN]` input each, in order. Measure it with `ffprobe` (`TTS_DUR`). Above **15 s** (H3's maximum) → do not upload: STOP and return the scene to Manager (shorten the text first, or split the clip).

**4. Upload and write back.** Upload `scene-K.mp3` exactly as §5 (`queue/upload-asset.sh --kind episode-tts --game {GAME_TAG} --episode {YYYY-MM-DD}-{format_slug} --name clip-K.mp3`), then write to that scene:
- `tts_url` — the returned permanent Supabase URL (never a fal URL);
- `tts_duration_sec` — `TTS_DUR`;
- `duration_sec` — `TTS_DUR` rounded **up** to 0.1 s (`math.ceil(round(TTS_DUR * 10, 6)) / 10`): the clip's real length, which the Animator sends as the lip-sync `duration` and the Editor trims to. This is the one storyboard field written by the Scenarist that you overwrite, and only on serial-drama dialogue clips.

Never lay this file over a clip yourself and never create parallel `-new`/`-v2` files (§2). Off-screen or behind-glass lines whose speaker is not lip-synced follow §9 instead (their own file, same `tts_voice`).

---

## 6. Background music

### Music follows the format; serial-drama and dual-style music are mandatory

Generate `bg-music.mp3` with MiniMax Music (`fal-ai/minimax-music/v2.6`) whenever the format requires music. **Serial-drama and dual-style (`dual-style-h3`) always require a newly generated background track and may never skip it.** Do not pull tracks from Supabase or the local `video-agent/music/` library.

| Format | Volume | Note |
|---|---|---|
| **serial-drama** | `0.45` | Was `0.15` until burned in EP13 (2026-07-14): measured near-inaudible against dialogue/SFX in a real mix (probed at ~-33dB in a silent scene, close to the noise floor) — user reported the music as completely missing. Raised to `0.45` and confirmed audible by direct dB probe (`editor.md` §4). If a future mix still reads as too quiet or too loud, re-probe and adjust — don't just retype a remembered number. |
| **dual-style** | target `-20 LUFS` | Music is the primary continuous bed. Editor measures and normalizes it rather than trusting a fixed scalar; clean clip ambience (H3) sits near `-28 LUFS`. |
| **gameplay-ai-avatar** | `0.10` | Quieter — avatar voice is primary |
| **reddit-story** | `0.05` | Even quieter — narration must be clear |
| **news, others** | `0.10–0.15` | By mood |

### Generation — MiniMax Music

Full request/polling schema: `tools/fal-ai.md §8`. Essentials:
- Endpoint: `POST https://queue.fal.run/fal-ai/minimax-music/v2.6`; polling base `fal-ai/minimax-music` (NOT the full path — see the base-path rule in fal-ai.md).
- Body: `{ "prompt": "<music prompt, ≤2000 chars>", "is_instrumental": true, "duration": <30–60> }`. The required field is `prompt`; never send the legacy `style` field, which the live v2.6 endpoint rejects.
- **`is_instrumental: true` ALWAYS** — background music has no vocals/lyrics.
- `duration` ≈ the video length (30–60s); generating slightly longer and letting Editor trim is fine.
- Download the result to `${OUTPUT_DIR}/bg-music.mp3` **immediately** (fal.ai URLs expire).
- Cost ~$0.03/track (see `budgets.md`).

**Build the music `prompt`** from (a) the format's emotional register (§11 mood map) + (b) the game's atmosphere (game config `music.mood` / Tone of Voice). Always instrumental, no vocals, fits a 9:16 short. Example (sitcom serial): `"instrumental low-density comedy underscore, light and playful, no vocals, no lyrics, no dramatic swell, suitable for a vertical short video"`.

On generation failure, retry the same request once. A second failure stops the whole video when music is required; never silently omit required music or switch route/provider/model.

### Mix parameters (passed to Editor)

- **serial-drama:** `volume=0.45` (was `0.15` — burned as near-inaudible, see the table above)
- **dual-style:** music target approximately `-20 LUFS`; clean clip ambience (H3) approximately `-28 LUFS`; final mix near `-20 LUFS`, true peak no higher than `-2 dBTP`
- **gameplay-ai-avatar:** `volume=0.10` (if used)
- Mixing is done by Editor (see `editor.md` section 4). Sound only generates the track and sets the volume.

---

## 7. Tone & pacing — TTS text

Generated speech is expressive, but not magic. Adapt the text:

- **Short lines ≤15 words** → 5s clip
- **15–25 words** → 5–7s, check `ffprobe` after generation
- **>25 words** → almost certainly will not fit 10s. Split into 2 lines.

### Emotional markers in text

Speech engines react to punctuation:
- `!` — energetic
- `…` — pause, contemplation
- `?` — rising intonation
- ALL CAPS — shout / emphasis

Use only the supported emotive tags from §1 (`(laughs)`, `(groans)`, etc.). Any other stage directions (`[angry]`, `(whispers)`, `[quietly]`) — the model reads literally as text. Emotion control goes in `voice_setting.emotion`, not in the text.

---

## 8. Subtitles — Sound does NOT touch subtitles at all

**Sound generates no PNG, burns no ASS, writes no `timings.json`.** Subtitles are entirely on Editor:
it runs faster-whisper on the final voice track (`build/voice-final.wav`) and burns the one universal
ASS. The text is the canonical text from the storyboard. Details — `rules/roles/editor.md` §6.

Your only job — quality required TTS files and `bg-music.mp3`. For serial-drama that is the dialogue TTS of every dialogue clip (§5a) plus the music.

### Forbidden

- ❌ Generating PNG subs / writing `*.ass` / `*.timings.json` from sound — that is Editor's job.
- ❌ Proportional timings (`--text`) — removed from the pipeline entirely (whisper on the real audio).

### Audio/video duration mismatch — speed control

If `dur(tts) > dur(video_timeline)` — Editor applies `atempo` to the TTS (cap **1.4×**; higher degrades
the voice). Subtitles are computed from the ALREADY sped-up speech (`voice-final.wav`), so they cannot
drift — you don't recompute anything.

If `dur(tts) < dur(video_timeline)` — Editor extends the last clip with a freeze-frame; do **not** pad with leading silence at the start of the TTS.

If the mismatch is > 40% — send it back to Scenarist, don't mask it with atempo.

---

## Checklist before handing off to Manager

### TTS
- [ ] All external-TTS dialogue clips have `scene-K.mp3`; every serial-drama dialogue clip has its line files, its built `scene-K.mp3` (0.2 s lead-in, 0.3 s gaps, ≤15 s), `tts_url`, `tts_duration_sec` and the rounded-up `duration_sec` (§5a)
- [ ] Serial-drama: `tts_voices` lists every speaker with `voice_id`, `speed` and `source` (`bible`/`new`); one voice per character in every line; the story bible is untouched
- [ ] All files > 5 KB, duration matches expectation (~0.4s per word)
- [ ] `voice` (name as string), not `voice_id`; `stability` top-level; `language_code` set (MiniMax routes, including serial-drama §5a: `voice_setting.voice_id` + `speed` + `emotion`, field `prompt`)
- [ ] All TTS uploaded to Supabase where a downstream Avatar / H3 lip-sync / TTS-overlay format needs it
- [ ] Mapping table printed (clip K → text → voice → audio URL)
- [ ] For gameplay-ai-avatar: voice approved with Manager BEFORE launching Avatar

### Music (if any)
- [ ] `bg-music.mp3` generated by MiniMax Music for serial-drama; it is never skipped or replaced with a local track
- [ ] Volume agreed with Editor (0.45 serial-drama, 0.10 gameplay, 0.05 reddit-story)

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

## 10. ASS subtitle invariants — moved to editor.md

ASS invariants (no event overlap, last event reaches clip end, MarginV direction, no full-width opaque box) are Editor's job, see `rules/roles/editor.md` §6. Sound writes no ASS.

## 11. Music mood must match the format

The MiniMax `style` prompt must match the format's emotional register (this used to be a folder pick from `music/` — now it shapes the generation prompt in §6). Quick mapping:

| Mood | Use for | `style`-prompt keywords |
|---|---|---|
| fun / light | comedy-sketch, lighthearted reaction | upbeat, playful, comedic, bright, bouncy |
| attractive / energetic | dual-style | polished instrumental pulse, energetic, aspirational, modern, no trailer swell |
| dark / tense | serial-drama (tense beats), horror, somber news | dark, tense, ominous, cinematic, low strings |
| neutral / drama | news, reddit-story (calm narration) | calm, restrained, ambient underscore, neutral |
| tense / action | serial-drama (cliffhanger), action recap | driving beat, suspenseful, rising tension |

Always add `instrumental, no vocals, no lyrics` and `suitable for a vertical short video`. If the format is comedic but the generated track is melancholic/ambient — regenerate with corrected keywords before handing off.

---

## 12. `timings.json` — REMOVED from the pipeline

Sound used to write `scene-K.timings.json`. No longer **needed**: Editor runs faster-whisper on the
final voice track (`build/voice-final.wav`) and takes word boundaries straight from the
`build/subs.ass` events. No `--emit-timings`, no `--text`. Sound creates no `*.timings.json`.

Snap-to-word-boundary on a tail trim (if ever needed) is done by Editor from the `subs.ass` events.
