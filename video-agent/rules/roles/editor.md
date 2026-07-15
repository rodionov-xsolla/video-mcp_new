# Editor — FFmpeg assembly craft

You are the editor. Manager passes you: all `scene-K.mp4`, audio (embedded I2V/Avatar audio, optional external TTS/VO, bg music), subtitles (if pre-made), format (split-screen / vertical), **opener and CTA from Supabase** (`.mp4` videos). You assemble `final.mp4` (1080×1920).

**Core principles:**
1. **One ffmpeg pipeline, not layered.** Each intermediate re-encode = quality loss and DTS issues.
2. **All clips → identical fps + audio format BEFORE concat.** Otherwise concat breaks.
3. **Never `-shortest` with TTS overlay** — clips video to audio length. Use `apad`.
4. **CTA is a file, do not rebuild it** if it's already valid.
5. **NEVER pad a dialogue/Avatar clip to a longer target with `tpad=stop_mode=clone` or any freeze-last-frame trick.**
6. **Audio normalization before concat — MANDATORY.** Sources arrive with different sample rates: Chatterbox TTS = 24kHz mono, Kling I2V audio = 44.1kHz, anullsrc default = 48kHz stereo. Never let ffmpeg resolve this silently — it produces clipping spikes ("squeal") and mean RMS of -27dB with 0dB peaks. Always add `aresample=48000,aformat=channel_layouts=stereo` to EVERY audio input before it enters `concat` or `amix`. Standard: `[k:a]aresample=48000,aformat=channel_layouts=stereo[ak]`. Verify with `ffprobe -show_streams -select_streams a` on every input: all must show `sample_rate=48000 channels=2` before concat.
7. **ASS subtitle validation before final encode.** After generating `subs-master.ass`, read the `[Events]` section and check: (a) no Dialogue event is a fragment of 1–2 words while a longer duration implies the rest of the phrase was orphaned; (b) font size matches format spec (what-if-real-life: 58px, not 84px); (c) no two events overlap within the same Style. Fix before running the encode — fixing after costs a full re-encode.
9. **I2V `generate_audio:true` audio is paid-for content — never discard it.** When any I2V clip has `generate_audio: true` in storyboard.json, its audio costs $0.042/s extra and must survive into the final mix. Use `concat=n=N:v=1:a=1` (never `a=0`) so Kling-generated atmospheric sound passes through. **`voice-final.wav` is a whisper-alignment artifact — it contains TTS only (16kHz mono) and is NEVER the final audio source.** The final audio always comes from scene MP4 streams (`[k:a]`) mixed with `bg-music`. Using `voice-final.wav` as output audio silently discards all I2V sounds and Kling Avatar lipsync quality. Burned in serial-drama EP3 — cost 3 re-renders.
10. **Re-render audio checklist (subtitle/overlay fix, not a full regeneration).** When re-encoding final.mp4 to fix subtitles or overlays: (a) take `[k:a]` from every scene MP4 directly; (b) normalize to stereo 44100 Hz with `aformat`; (c) concat scene audio + `anullsrc` for any CTA/no-audio segment; (d) `amix` with `bg-music.mp3` at the declared volume. Never pass `voice-final.wav` as `-i` to the encode.
8. **Final encode is always synchronous.** Never run the subtitle-burn + music-mix encode in background. It writes the moov atom only on clean exit — a killed or background process produces a file with `moov atom not found`. Use `timeout 180` if needed. Validate with `ffprobe -v error -show_entries format=duration` immediately after: if it errors, the file is incomplete. An Avatar clip plays at its natural TTS length (~2–3s) — that is correct, not a bug to "fix". Freezing the last frame to inflate runtime produces a dead, frozen face after every line and looks broken (burned on EP7). Runtime is set by CONTENT (number/length of action clips), never by stretching a still. `apad`/`tpad` are allowed ONLY to close an audio↔video gap within a single clip (≤ its own natural length), never to extend a clip past where it ends.

FFmpeg:
- `/usr/local/bin/ffmpeg` — Homebrew 8.1, **without libfreetype or libass** → drawtext does not work, and `ass=` subtitle filter silently errors with "Invalid argument". Use only for concat/audio/scale steps that do not touch subtitles.
- `/usr/local/bin/ffmpeg-full/ffmpeg` — tessus build with libfreetype + libass → **both drawtext and `ass=build/subs.ass` work**. **Always use this binary for any encode that includes subtitles.** Using Homebrew ffmpeg for the subtitle pass is a silent failure — the encode completes but subs are not burned.

Variable `$FFMPEG` defaults to `/usr/local/bin/ffmpeg-full/ffmpeg` (when drawtext is needed) or `/usr/local/bin/ffmpeg` (for other steps). Shell — `zsh` (macOS), arrays 1-indexed.

---

## Inputs

From Manager:
- `scenes/scene-K/scene-K.mp4` (K = 1..N) — animated clips (from Animator)
- `scenes/scene-K/scene-K.mp3` (opt.) — external TTS/VO audio from Sound (Avatar/TTS-overlay formats, narrator/off-screen VO). Serial-drama I2V dialogue normally has embedded audio in `scene-K.mp4`.
- `bg-music.mp3` (opt.) — background music (from Sound)
- `storyboard.json` — for subtitle generation (line text, timings)
- `opener.mp4` (opt.) — opener video from Supabase (tag `opener` + `video`)
- `cta.mp4` — CTA video from Supabase (tag `cta` + `video`)
- `format` — defines layout (vertical 9:16 / split-screen for gameplay-ai-avatar) and subtitle method

## Outputs

`output/.../final.mp4` — 1080×1920, 30fps, AAC 128k stereo, no joint artifacts.

### Workspace layout (MANDATORY)

After your last command, the `OUTPUT_DIR` root must contain ONLY:

- `final.mp4` — the deliverable
- `storyboard.json` — narrative manifest (written by Scenarist, do not move)
- `scenes/` — per-scene PNGs/MP4s/MP3s organized by Storyboarder + Animator + Sound (do not touch)
- `recap/` — only if the format produces one (serial-drama recap clip, etc.)
- `_archive/` — only if you replaced an earlier `final.mp4`; move the prior version in here, do not delete

**Everything else goes under `OUTPUT_DIR/build/`.** This includes (non-exhaustive):

- ffmpeg concat helpers: `concat-list.txt`, `concat-final.txt`, `concat.mp4`
- intermediate renders: `final-base.mp4`, `final-speed.mp4`, `final-compressed.mp4`, `video-concat.mp4`, `video-concat-cta.mp4`
- normalized assets: `cta-normalized.mp4`, opener-normalized, etc.
- temp audio: `bg-music.mp3`, `tts-output.mp3`, `tts-fast.mp3`
- normalization / subtitle staging dirs: `norm/`, `subs/`
- ad-hoc scripts and logs: `gen_images.sh`, `submit_i2v_clean.sh`, `recover.sh`, `generate.sh`, `pipeline.log`, `recover.log`, `phase3_requests.txt`, `i2v_request_ids.txt`, `i2v_map.txt`, `scene_urls.env`

Operational rules:

1. Create `OUTPUT_DIR/build/` at the start of your work and write every intermediate there from the first command. Do not write to root and "clean up later" — you will forget.
2. The only files written to the root are `final.mp4` (atomically: write to `build/final.tmp.mp4`, ffprobe-validate, then `mv` to root) and, if regenerating, `_archive/`-rotation of the prior `final.mp4`.
3. Do NOT delete `build/` after success. It is debug surface for the next run — let `_archive/` rotation or a separate cleanup pass handle it.
4. If you discover stale intermediates in root from an older run, move them into `build/` before producing your own (do not nuke them).

This rule applies regardless of format. A reader of `OUTPUT_DIR` should see four-to-five items, not twenty.

---

## 0. Canonical pipeline — single-pass `filter_complex` (DEFAULT)

**This is the path. Use it for every format unless a section below explicitly overrides for that format (split-screen gameplay-ai-avatar). Subtitles are one style for all formats (§6), not an override.**

Multi-stage assembly (sections 1–5) is **legacy**: kept for debugging when you need to inspect an intermediate, or when a clip-specific filter (e.g. per-scene drawtext) cannot be expressed inside one filter graph. The legacy path is what made editor runs take 12–32 minutes for 50s output. Single-pass on the same hardware: **~90 seconds**.

### 0.1 Architecture

One `ffmpeg-full` invocation. All inputs (N scene MP4s + 1 CTA MP4 + 1 TTS MP3 + 1 music MP3) → `filter_complex` graph → single libx264 encode → `final.mp4`.

```
INPUTS:
  [0..N-1] scene-1.mp4 … scene-N.mp4
  [N]      cta.mp4 (already downloaded + ffprobe-validated; do NOT pre-normalize)
  [N+1]    tts-output.mp3 (raw from Sound; reshape inside filter_complex)
  [N+2]    bg-music.mp3   (raw from Sound; reshape inside filter_complex)

filter_complex (logical):
  [k:v] scale=1080:1920:force_original_aspect_ratio=decrease,
        pad=1080:1920:(ow-iw)/2:(oh-ih)/2,
        fps=30,
        setpts=PTS-STARTPTS    → [vk]            (each input k, including CTA)
  [vN_last]  + fade=t=out:st=DUR-1:d=1            (last story clip before CTA only)
  [v0]…[vN] concat=n=N+1:v=1:a=0                  → [vcat]
  [vcat]    ass=build/subs.ass                    → [vsub]

  [N+1:a]   atempo=X, adelay=PRE_MS|PRE_MS,
            volume=1.0                            → [atts]
  [N+2:a]   volume=MUS_VOL,
            afade=t=out:st=MAIN_DUR-1:d=1.0       → [amus]
  [atts][amus] amix=inputs=2:duration=longest:
                    dropout_transition=0:
                    normalize=0                   → [aout]

OUTPUT:
  -map [vsub] -map [aout]
  -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p
  -c:a aac -b:a 128k -ar 44100 -ac 2
  -t TOTAL_DUR
  final.mp4
```

### 0.2 Worked example (redcon , 8 scenes + CTA)

This is the exact command that ships our redcon/Spock-Borg video (50s output, 1:28 wall-clock, 23 MB):

```bash
FF=/usr/local/bin/ffmpeg-full/ffmpeg     # libass + libfreetype required
mkdir -p build

# Pre-flight (cheap, off the main pipeline):
#   1. CTA: curl + ffprobe (validate codec/dur; pass raw, do NOT re-encode)
#   2. ASS: tools/add_subtitles.py emits build/subs.ass aligned to the SAME
#      audio shaping (atempo, adelay) used below. See §6 for the script call.

SCENE_LAST_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 scenes/scene-8/scene-8.mp4)
FADE_START=$(echo "$SCENE_LAST_DUR - 1.0" | bc -l)
TOTAL_DUR=50.0                            # MAIN_DUR + CTA_DUR (computed)
MAIN_DUR=44.96                            # for afade=out anchor

$FF -y \
  -i scenes/scene-1/scene-1.mp4 \
  -i scenes/scene-2/scene-2.mp4 \
  -i scenes/scene-3/scene-3.mp4 \
  -i scenes/scene-4/scene-4.mp4 \
  -i scenes/scene-5/scene-5.mp4 \
  -i scenes/scene-6/scene-6.mp4 \
  -i scenes/scene-7/scene-7.mp4 \
  -i scenes/scene-8/scene-8.mp4 \
  -i build/cta-raw.mp4 \
  -i tts-output.mp3 \
  -i bg-music.mp3 \
  -filter_complex "\
[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30,setpts=PTS-STARTPTS[v0]; \
[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30,setpts=PTS-STARTPTS[v1]; \
[2:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30,setpts=PTS-STARTPTS[v2]; \
[3:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30,setpts=PTS-STARTPTS[v3]; \
[4:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30,setpts=PTS-STARTPTS[v4]; \
[5:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30,setpts=PTS-STARTPTS[v5]; \
[6:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30,setpts=PTS-STARTPTS[v6]; \
[7:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30,setpts=PTS-STARTPTS,fade=t=out:st=${FADE_START}:d=1.0[v7]; \
[8:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30,setpts=PTS-STARTPTS[v8]; \
[v0][v1][v2][v3][v4][v5][v6][v7][v8]concat=n=9:v=1:a=0[vcat]; \
[vcat]ass=build/subs.ass[vsub]; \
[9:a]atempo=1.46,adelay=5000|5000,volume=1.0[atts]; \
[10:a]volume=0.15,afade=t=out:st=${MAIN_DUR}:d=1.0[amus]; \
[atts][amus]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0[aout]" \
  -map "[vsub]" -map "[aout]" \
  -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ar 44100 -ac 2 \
  -t "$TOTAL_DUR" \
  build/final.tmp.mp4

# Atomic move only after ffprobe-validation:
ffprobe -v error -show_entries format=duration -of csv=p=0 build/final.tmp.mp4
mv build/final.tmp.mp4 final.mp4
```

### 0.3 Encoder choice

#### Encoder selection (lock once per run)

Hardware encoders are 2–5× faster than `libx264` on the same machine. Detect once at the start of assembly and set `$VCODEC_ARGS`:

```bash
# Detect best available H.264 encoder (run once, reuse $VCODEC_ARGS in every -c:v slot)
FF=/usr/local/bin/ffmpeg-full/ffmpeg

if $FF -encoders 2>/dev/null | grep -q h264_videotoolbox; then
  # Apple Silicon / Intel Mac — ~3–5× faster than libx264, no quality loss after social re-encode
  VCODEC_ARGS="-c:v h264_videotoolbox -b:v 5M -maxrate 7M -bufsize 10M"
elif $FF -encoders 2>/dev/null | grep -q h264_nvenc; then
  # NVIDIA GPU
  VCODEC_ARGS="-c:v h264_nvenc -preset p4 -cq 22 -b:v 0"
elif $FF -encoders 2>/dev/null | grep -q h264_amf; then
  # AMD GPU
  VCODEC_ARGS="-c:v h264_amf -quality balanced -qp_i 22 -qp_p 24"
elif $FF -encoders 2>/dev/null | grep -q h264_qsv; then
  # Intel Quick Sync
  VCODEC_ARGS="-c:v h264_qsv -preset medium -global_quality 22"
else
  # CPU route when no hardware encoder is available
  VCODEC_ARGS="-c:v libx264 -preset medium -crf 22"
fi
```

Then in every encode command replace `-c:v libx264 -preset medium -crf 22` with `$VCODEC_ARGS`.

**Notes:**
- `h264_videotoolbox` does not support `-crf` — use `-b:v 5M` target bitrate instead. At 1080×1920 this is equivalent quality to `crf 22` and well within TikTok/Reels/Shorts ingest limits.
- Always append `-pix_fmt yuv420p` — required regardless of encoder (QuickTime + social uploads).
- If the selected encoder fails mid-run, retry the same command once. A second failure stops the whole video; do not switch encoders.
- `ffmpeg-full` binary is still required for any encode that burns subtitles (`ass=` filter). Hardware encode is compatible with `ass=` — it is a video filter, not a codec constraint.

#### Software-route params (when `$VCODEC_ARGS` resolves to libx264 at pre-flight)

- **`-preset medium -crf 22`** — single-pass default. On 1080×1920, ~90 s for 50 s output.
- **`-preset slow -crf 20`** — ONLY for archival masters or when explicitly requested. 3–5× wall-clock for marginal quality gain after social re-encode. Do not use as default.

#### Locked audio params (do not change)

- `-c:a aac -b:a 128k -ar 44100 -ac 2` — locked.
- `-t TOTAL_DUR` — mandatory hard cap so `apad` / `amix duration=longest` do not extend final to music length.

### 0.4 Audio shaping — match what the ASS expects

The ASS file from `tools/add_subtitles.py` is timed against the **final** TTS shape after atempo + adelay. The filter graph must apply the same operations in the same order. If you re-trim TTS or change atempo after generating ASS, subtitles will drift — regenerate the ASS.

Order is `atempo` → `adelay`. atempo first compresses speech to fit the picture window; adelay then offsets it so TTS starts after any title-card silence (e.g. 5000 ms for redcon's title card).

#### 0.4.1 Audio PTS hygiene — `asetpts=N/SR/TB` + `aresample=async=1` (MANDATORY)

When the audio chain combines `concat`, `adelay`, `amix`, or any per-scene `amix` (e.g. ambient SFX layer + TTS), PTS drift compounds silently — ffmpeg writes the mp4 cleanly, ffprobe shows reasonable codec info, but the **container audio timestamp** ends up far outside the playable range. Symptom: `ffprobe` reports `start_time` like `209146758205323.687500` (≈ 6.6 million years), `duration` is hugely negative, and `nb_frames` is tiny (e.g. 88 frames for a 44s video). Most players (QuickTime, browsers, mobile) refuse to play this audio — the video appears silent even though the bitstream contains data.

The fix is two filters, applied at every chain boundary in the audio branch:

1. `aresample=async=1:first_pts=0` on every audio INPUT (`[k:a]`, `[bg_music:a]`, ambient `[amb:a]`) — resyncs the source PTS to start at 0. Avatar v2 audio inherits its container PTS which can be wildly off-zero.
2. `asetpts=N/SR/TB` after **every** filter that re-times audio: after `atempo`, after `apad`, after `concat`, after `adelay`, after `amix`. `N/SR/TB` regenerates monotonic PTS from sample count.

Canonical per-scene audio branch (replaces the simpler chain in §0.1):

```
[k:a]aresample=async=1:first_pts=0,atempo=1.3,apad=whole_dur=<sped_dur_k>,asetpts=N/SR/TB[ak]
```

If scene K layers ambient SFX (custom format extension, e.g. WWE Champions fun-news scene_ambient field) — apply the ambient mix BEFORE atempo, but also reset PTS at every chain join:

```
[k:a]aresample=async=1:first_pts=0[ttsk];
[amb_k:a]volume=<amb_vol>,atrim=0:<raw_dur_k>,asetpts=N/SR/TB[ambk];
[ttsk][ambk]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[mixk];
[mixk]atempo=1.3,apad=whole_dur=<sped_dur_k>,asetpts=N/SR/TB[ak]
```

Concat + adelay + bg-music mix tail:

```
[a0][a1][a2][a3][a4]concat=n=5:v=0:a=1,asetpts=N/SR/TB[adlg];
[adlg]adelay=2000|2000,asetpts=N/SR/TB[atts];
[bg:a]aresample=async=1:first_pts=0,volume=0.15,afade=t=out:st=<TOTAL-1>:d=1.0,asetpts=N/SR/TB[amus];
[atts][amus]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0,asetpts=N/SR/TB[aout]
```

**Self-check after first pass:** `ffprobe -v error -select_streams a -show_entries stream=duration,start_time,nb_frames final.mp4`. If `start_time` is anything other than `0.000000` (or close), or `nb_frames` is < ~40/sec of duration, the audio PTS is broken — rebuild with the recipe above.

WWE Champions fun-news pilot (2026-06-01) burned 1× re-render because the original pass omitted both filters on a chain that included `adelay+amix`. Cost: $0 (audio-only rebuild reusing same scene mp4s + bg-music) but ~10 min wasted. Don't repeat.

### 0.5 Format-specific overrides

- **gameplay-ai-avatar split-screen** (§7) — the per-scene 60/40 stack cannot be expressed across N scene inputs cleanly inside one concat. Two-stage: first build each split-scene composite (§7), then feed those composites as inputs into the §0 canonical pipeline.
- **serial-drama "behind glass" TTS overlay** (§3) — per-scene aecho is a pre-mix on the I2V scene before §0. Treat output of §3 as the canonical input `[k:v]/[k:a]` for the main pipeline.
- **Subtitle generation** (§6) — ONE universal ASS for the whole video, whisper-timed from `build/voice-final.wav`. `§0` picks it up as the last video filter `ass=build/subs.ass`. No per-format styles.
- **Player-POV subtitle clamp (redcon + any format with a silent title card clip):** After `add_subtitles.py` generates `subs.ass`, post-process it in Python to remove/clamp Whisper subtitle events (layer-0, no `\pos`/`\fn` override) that fall inside the title card window. Window = `[clip_1_dur, clip_1_dur + title_card_dur]`. Events ending after window start → clamp end. Events starting inside window → move start to window end. Events fully inside → drop. Verify zero layer-0 subtitle conflicts before encoding. Title card text events (Montserrat Black, `\pos`) are NOT subtitles — do not touch them.
- **Graphic overlays** (§6.5) — `tools/overlays.py` emits per-scene `drawtext` fragments spliced into the `[vk]` branch BEFORE concat. No generic channel-bug overlay exists.

### 0.6 When NOT to use the canonical pipeline

- A single scene needs per-scene filter that breaks the graph (rare — usually solvable by chaining filters on that `[vk]` branch)
- Debugging which stage corrupts output → run the legacy multi-stage (§§1–5) once, find the bad stage, fix the underlying filter, return to §0

There is **no quality reason** to prefer multi-stage. Every multi-stage run = N full re-encodes of the entire timeline = N× generation loss. Single-pass = one encode.

---

## 1. Normalization (scale + fps + audio) — LEGACY (debug only)

> ⚠️ **Prefer §0 single-pass pipeline.** This section describes the legacy multi-stage path. Use only when debugging an intermediate, or when §0 cannot express a required per-scene filter chain.

**Path convention for every snippet below.** Run all commands with `OUTPUT_DIR` as cwd. Inputs come from `scenes/scene-K/...` (unchanged). **Every scratch file in the snippets — `concat-list.txt`, `concat-final.txt`, `final-base.mp4`, `final-speed.mp4`, `video-concat.mp4`, `cta-normalized.mp4`, `bg-music.mp3`, `tts-output.mp3`, `tts-fast.mp3`, etc. — must be written to `build/`, not to the root.** So when a snippet says `final-base.mp4`, you write `build/final-base.mp4` and read it the same way on the next step. The ONLY file that lands in the root is the final deliverable, via `mv build/final-music.mp4 final.mp4` at the very end. Run `mkdir -p build` before your first ffmpeg call. See "Workspace layout (MANDATORY)" above.

**CRITICAL:** before concat all clips MUST have identical fps and audio format.

I2V (Kling) is 24fps, Avatar (Kling Avatar) is 30fps → normalize EVERYTHING to 30fps.

**CRITICAL — concat.txt requires ABSOLUTE paths.** The `-f concat` demuxer resolves `file` entries relative to the concat.txt location, not the ffmpeg cwd. If you write `file 'norm-1.mp4'` and run ffmpeg from a different directory, it silently fails (exit 137, OOM kill, or "No such file"). Always write absolute paths:

```bash
# Correct — absolute paths:
cat > "$B/concat.txt" << EOF
file '$B/norm-1.mp4'
file '$B/norm-2.mp4'
EOF

# Wrong — relative paths cause exit 137:
cat > build/concat.txt << 'EOF'
file 'norm-1.mp4'
file 'norm-2.mp4'
EOF
```

**CRITICAL — filter_complex stream indices.** When you pass N input files to ffmpeg, each `-i` gets its own index [0], [1], [2]... If all clips are already normalized and concatenated into one `concat-base.mp4`, then in the final overlay pass there is ONLY ONE video input `[0:v]`. Don't mix the two: separate clips as inputs → filter_complex with concat; an already-concatenated base → overlays + subtitles only.

### 1.0a Avatar silence trim — BEFORE concat

Avatar clips render to exactly TTS duration, but may contain a silent tail (Avatar MP4 container is slightly longer than the speech). Trim **both video AND audio** before feeding into concat:

```python
# In filter_complex — for each Avatar clip (input index i, TTS duration = tts_dur):
f"[{i}:v]trim=end={tts_dur},setpts=PTS-STARTPTS,scale=...,fps=30,setsar=1[sv{i}]"
f"[{i}:a]atrim=end={tts_dur},asetpts=PTS-STARTPTS,aformat=sample_rates=44100:channel_layouts=stereo[sa{i}]"
```

**I2V clips: NEVER trim.** Their declared duration is intentional. Only Avatar-based dialogue clips are trimmed.

### 1.0b Joint v+a concat for formats with embedded dialogue audio

When clips carry embedded dialogue audio (serial-drama I2V `generate_audio:true`, Avatar-based formats), **never split video and audio into two separate concat chains** — they will drift under any A/V processing. Instead use a single `concat=n=N:v=1:a=1` with interleaved pairs:

```python
# Interleaved: [sv0][sa0][sv1][sa1]...[svN-1][saN-1]
pairs = "".join(f"[sv{i}][sa{i}]" for i in range(n))
f"{pairs}concat=n={n}:v=1:a=1[vconcat][aconcat]"
```

- I2V clips with audio: pair `[sv_i]` (scaled video, never trimmed) with `[sa_i]` (normalized audio from embedded stream).
- I2V clips without audio: pair `[sv_i]` with `[sa_i]` generated from `anullsrc`.
- Avatar clips: pair `[sv_i]` (scaled+trimmed) with `[sa_i]` (trimmed audio from embedded stream).
- CTA: pair scaled video with `anullsrc,atrim=duration={CTA_DUR}`.

Overlay narrator VO + bg-music on `[aconcat]` via `amix=inputs=3:duration=first:normalize=0`. `duration=first` anchors output to scene audio length; `normalize=0` prevents volume division.

### 1.1 I2V clips — add silent audio

I2V clips **do not contain an audio stream**. Before concat, mandatory: add silence — otherwise ffmpeg concat skips empty audio packets and all subsequent dialogue shifts left.

```bash
$FFMPEG -y -i scene-K-scaled.mp4 \
  -f lavfi -i anullsrc=r=44100:cl=stereo \
  -c:v copy -c:a aac -b:a 128k \
  -map 0:v -map 1:a -shortest \
  scene-K-scaled-audio.mp4
```

**Check:** after normalization, every clip's `ffprobe -select_streams a:0` must show an audio stream. If not — add `anullsrc`.

```bash
$FFMPEG -y -i scenes/scene-K/scene-K.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -r 30 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  scenes/scene-K/scene-K-scaled.mp4
```

Required parameters:
- `-r 30` — 30 fps
- `-preset slow -crf 20` — high quality
- `-ar 44100 -ac 2 -c:a aac -b:a 128k` — normalized audio

---

## 2. Concat

**Hard cut only.** Do NOT use `crossfade`, `xfade`, `end_image_url`. Different `camera_angle` between clips makes cuts professional.

```bash
cat > concat-list.txt << 'EOF'
file 'scenes/scene-1/scene-1-scaled.mp4'
file 'scenes/scene-2/scene-2-scaled.mp4'
file 'scenes/scene-3/scene-3-scaled.mp4'
EOF

$FFMPEG -y -f concat -safe 0 -i concat-list.txt \
  -r 30 -c:v libx264 -preset slow -crf 20 \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  final-base.mp4
```

**IMPORTANT:** Concat with re-encode (`-c:v libx264`), NOT stream copy (`-c copy`). Stream copy causes non-monotonic DTS and overlapping frames.

---

## 3. TTS overlay for serial-drama I2V "behind glass" clips

For serial-drama: I2V clips can have TTS overlay (when the character speaks but no lipsync) — voice is overlaid with an aecho effect ("behind glass").

```bash
$FFMPEG -y -i scenes/scene-K/scene-K-scaled.mp4 -i scenes/scene-K/scene-K.mp3 \
  -filter_complex "[1:a]aecho=0.8:0.88:60:0.4,apad=whole_dur=5[voice];[0:a][voice]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 128k \
  scenes/scene-K/scene-K-with-tts.mp4
```

**CRITICAL:**
- `apad=whole_dur=5` (clip duration in s) — pads with silence to video length. WITHOUT it + `duration=first` the mix may cut off.
- NOT `-shortest` — would clip video to TTS audio length.

---

## 3b. TTS duration matching (atempo)

When TTS (full monologue) does not match the video duration:

| Situation | Solution |
|---|---|
| TTS > video | Speed up TTS: `atempo=VIDEO_DUR/TTS_DUR` (usually 1.1–1.3x) |
| TTS < video | Pad with silence: `apad=whole_dur=VIDEO_DUR` |
| TTS ≈ video (±1s) | Leave as is, `apad` will close the gap |

```bash
# Example: TTS 43s, video 35s → speed up 1.23x
TTS_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 tts-output.mp3)
VIDEO_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 video-concat.mp4)
SPEED=$(echo "$TTS_DUR / $VIDEO_DUR" | bc -l)
$FFMPEG -y -i tts-output.mp3 -filter:a "atempo=$SPEED" tts-fast.mp3
```

**atempo limits:** 0.5–100.0. For speedup >2x — chain: `atempo=2.0,atempo=1.5` = 3x.

**Rule:** Voice must not be cut (`-t`). Either speed up (atempo) or pad with silence (apad). Cutting = lost final phrase.

---

## 3c. Episode number on the first clip (LEGACY — DO NOT USE for serial-drama)

> ⚠️ **OVERRIDE — for `serial-drama` and any format whose playbook lists `❌ Title cards / brainrot tags / character name overlays` in anti-patterns: SKIP this section entirely.** No "EPISODE N" drawtext. The episode opens cold on the recap clip. The block below remains for legacy formats that explicitly request an episode card in their playbook.

An episode/series plate ("EPISODE N", series title) is a **graphic overlay**, not a subtitle.
`tools/overlays.py` draws it (`title` type) from `scenes[].overlays[]` in the storyboard, see §6.5.
No manual drawtext here. For serial-drama there is none at all (cold open on the recap).

---

## 3d. Speed up the video (LEGACY — DO NOT USE for serial-drama)

> ⚠️ **OVERRIDE — for `serial-drama`: SKIP this section.** Serial-drama is I2V-only and clip durations in the storyboard are the final timings (5s = 5s, not 5/1.15s). 1.15x bump on the whole episode accelerates I2V action/dialogue that the scenarist already paced. The block below applies only to formats that explicitly request the 1.15x bump in their playbook (e.g. `gameplay-ai-avatar` has its own 1.3x rule for Avatar audio, see section 11 of `animator.md`).

**After concat, BEFORE music overlay** (legacy formats only) — speed up the whole video by ~1.15x. This makes the video more dynamic without noticeable voice distortion.

```bash
$FFMPEG -y -i final-base.mp4 \
  -filter_complex "[0:v]setpts=PTS/1.15[v];[0:a]atempo=1.15[a]" \
  -map "[v]" -map "[a]" \
  -r 30 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  final-speed.mp4
```

**Pipeline order (with the new subtitle flow):**
1. Normalize clips (section 1)
2. Per-scene graphic overlays (§6.5) on `[vk]` BEFORE concat
3. Concat → `final-base.mp4`
4. **Speed up (this section, legacy formats)** → `final-speed.mp4`
5. Build `build/voice-final.wav` from the ALREADY sped-up speech (§6.1) and generate `build/subs.ass` (§6.2)
6. Burn `ass=` as the last video filter
7. Music (section 4), mixed AFTER speedup (otherwise the pitch shifts)

Subtitles are always generated from the FINAL (post-speed) speech and burned last — they cannot drift.

---

## 4. Background music (MANDATORY for all formats)

The track is picked by Sound (see `sound.md`). Editor receives the path to the track and the volume parameter, mixes with the final video:

```bash
$FFMPEG -y -i final-base.mp4 -i bg-music.mp3 \
  -filter_complex "[1:a]volume=0.15,apad=whole_dur=$VIDEO_DUR[music];[0:a][music]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 128k \
  final-with-music.mp4
```

- Music volume is set by Sound (gameplay=0.10, reddit-story=0.05; serial-drama was 0.15 but see the audibility note below — verify with a real probe rather than trusting this number as-is)
- `apad=whole_dur=$VIDEO_DUR` — pad with silence if music is shorter than the video
- NEVER `-shortest`
- If Sound did not specify a track — **stop and ask Manager**. Music is mandatory

**Mandatory pre-flight check (do this BEFORE the final encode, not after):** `[ -s "$OUTPUT_DIR/bg-music.mp3" ]` (or `build/bg-music.mp3`). If the file is absent or empty, this is a hard stop — do not encode `final.mp4` without music "to be safe" or "since Manager can add it later." Burned 2026-07-09: star-trek-timelines `what-if-real-life` shipped as a finished, human-reviewed `final.mp4` with no music track at all because Editor built and delivered the whole video without ever checking for `bg-music.mp3`. Checking after encoding is too late — the file already looks "done."

**"Music is in the filter graph" ≠ "music is audible" — always verify with a real probe, not by reading your own `filter_complex`.** Burned in EP13 star-trek-airlock (2026-07-14, serial-drama): the graph included `amix` with the music track at `volume=0.15` exactly as documented, but the user reported the final video had no audible music at all. Isolated testing showed `volume=0.15` (linear, not dB) attenuates the raw track by ~-16.5dB — combined with an already-quiet source track, the mixed result measured close to the noise floor in silent/no-dialogue scenes. Raising to `volume=0.45` fixed it, confirmed by measurement, not by re-reading the filter graph. **After every music mix, probe a genuinely silent/no-dialogue scene window and report the actual dB numbers** — do not report "music mixed at volume=X" as if that were proof of audibility.
- **Probing gotcha: `-ss` placement changes what you measure.** `ffmpeg -i final.mp4 -ss T -t D -af volumedetect -f null -` (accurate seek — `-ss` AFTER `-i`) measures only the T→T+D window. `ffmpeg -ss T -i final.mp4 -t D ...` (fast/input-side seek) can behave inconsistently across ffmpeg builds/containers and has produced misleading whole-file-like stats during this same incident — if two probes of the same window disagree, try both seek placements before concluding the audio itself is the problem.
- **Do not let the music fade end exactly at a hard cut (e.g. the CTA boundary).** An `afade=t=out:st=<content_end>:d=1.0` timed to land precisely where the next segment (CTA) starts leaves that entire following segment dead silent, which reads as "the music disappeared" even more than a low volume does. Time the fade to end within the final ~1–1.5s of the whole video, not at an internal segment boundary, unless the CTA segment has its own audio.

---

## 4a. reddit-story — canonical assembly (three steps, DO NOT skip or reorder)

reddit-story has no scene MP4s — only `tts-output.mp3` + raw gameplay clips + a game-specific background PNG.

**Three encode passes total** (was four — steps 2+3+4 merged into one ffmpeg-full pass to halve CPU time).

### Layout
- **Background:** query Supabase `game_assets` where `game_tag = {GAME_TAG}` AND `tags @> ['reddit-story-bg']` → download to `build/bg.png`, scaled 1080×1920. If not found — STOP, ask Manager to upload one with tag `reddit-story-bg`.
- **Gameplay panel:** 960×1280 (3:4), overlaid at x=60, y=320 — 60px side borders + 320px top/bottom of background visible
- **Subtitles:** burned in the same pass as composite + audio (on top of overlay), MarginV=520 — correct

### Step 0 — download background

```bash
source .env
BG_URL=$(curl -s -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  "${SUPABASE_URL}/rest/v1/game_assets?game_tag=eq.${GAME_TAG}&tags=cs.{reddit-story-bg}&select=url" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['url'] if d else '')")
[ -z "$BG_URL" ] && { echo "ERROR: no reddit-story-bg asset for ${GAME_TAG}"; exit 1; }
curl -s -o build/bg.png "$BG_URL"
```

### Step 1 — normalize gameplay clips (CRITICAL: crop-to-fill, never pad)

Inspect actual clip dimensions first (`ffprobe -show_entries stream=width,height`). Scale to 960×1280 via crop-to-fill regardless of source resolution. The source clip is longer than TTS_DUR, so `-ss OFFSET` is **mandatory**, not optional.

**OFFSET must vary between runs and go meaningfully deep into the clip** — do not default to a small offset (e.g. ~30–40s) every time. Check the exact format/series story bible for `gameplay_offset_sec` used in the last 2–3 approved episodes, then pick a new valid offset at least 3–4 minutes away. Report it to Manager as a pending state change; Manager records it only after the user approves the final video.

```bash
FFMPEG=/usr/local/bin/ffmpeg-full/ffmpeg
# OFFSET: pick per-run, 3-4 min away from recent episodes' offsets (see above)
ffmpeg -y -ss "$OFFSET" -i games/${GAME_TAG}/gameplay/clip.mp4 -t "$TTS_DUR" \
  -vf "scale=960:1280:force_original_aspect_ratio=increase,crop=960:1280,setsar=1,fps=30" \
  -an -c:v libx264 -preset fast -crf 22 \
  build/gp_norm.mp4
```

**NEVER use `force_original_aspect_ratio=decrease` + `pad` for gameplay** — pad fills with black, baking black bars into the file before compositing. Normalizing to 1080×810 (landscape) is also wrong — it inverts the aspect ratio.

Also generate subtitles before Step 2 (needed by the single-pass encode):
```bash
# Whisper on tts-output.mp3 → build/subs.ass
python3 tools/add_subtitles.py tts-output.mp3 build/subs.ass \
  --storyboard storyboard.json --lang en --main-dur "$TTS_DUR"
```

### Step 2 — single-pass composite + subtitles + audio (ffmpeg-full required)

Combines overlay, libass subtitle burn, and audio mix in one encode. Saves one full re-encode vs the old 4-step approach.

```bash
SUBS_ABS="$(pwd)/build/subs.ass"
/usr/local/bin/ffmpeg-full/ffmpeg -y \
  -loop 1 -framerate 30 -i build/bg.png \
  -stream_loop -1 -i build/gp_norm.mp4 \
  -i tts-output.mp3 \
  -i bg-music.mp3 \
  -filter_complex "
    [0:v]scale=1080:1920,setsar=1[bg];
    [1:v]setsar=1[gp];
    [bg][gp]overlay=x=60:y=320,ass='${SUBS_ABS}',fps=30[vout];
    [2:a]apad[tts];
    [3:a]volume=0.05[mus];
    [tts][mus]amix=inputs=2:duration=first[aout]
  " \
  -map "[vout]" -map "[aout]" \
  -t "$TTS_DUR" \
  -c:v libx264 -preset fast -crf 22 \
  -c:a aac -b:a 128k -ar 44100 -ac 2 \
  build/main-final.mp4
```

**MUST use `/usr/local/bin/ffmpeg-full/ffmpeg`** — system Homebrew ffmpeg has no libass → `ass=` filter silently fails, no subtitles burned.

### Step 3 — concat CTA → final.mp4

```bash
printf "file 'main-final.mp4'\nfile 'cta-norm.mp4'\n" > build/concat-final.txt
/usr/local/bin/ffmpeg-full/ffmpeg -y -f concat -safe 0 -i build/concat-final.txt \
  -c:v libx264 -preset medium -crf 22 -c:a aac -b:a 128k -ar 44100 -ac 2 \
  -movflags +faststart final.mp4
```

### CTA asset

Query `game_assets` where `game_tag = {GAME_TAG}` AND `tags @> ['cta','video']`. Accept any `asset_type` — games use either `promo_art` (e.g. star-trek-timelines) or `generated_ref` (e.g. genshin-impact). Skip any record tagged `legacy`.

---

## 5. Video ending: existing game CTA (MANDATORY)

Every video ends with the existing CTA resolved for its `GAME_TAG`. This game CTA is the only asset automatically shared across formats. Resolve it from the game's configured Supabase/local CTA path and validate only filename, size, codec, dimensions, and duration. If it is missing or invalid, stop the whole video; never create an end frame, synthetic CTA, text card, or copy one from another game.

Download with `curl`, then normalize it via the same `scale + pad + 30fps + AAC` step (section 1).

### 5.3 Fade-to-black before CTA

The last video clip (before CTA) must have a fade-to-black on the last 1 second:

```bash
# Applied to the last clip during normalization
CLIP_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 scene-N-scaled.mp4)
FADE_START=$(echo "$CLIP_DUR - 1.0" | bc -l)
$FFMPEG -y -i scene-N-scaled.mp4 \
  -vf "fade=t=out:st=$FADE_START:d=1.0" \
  -c:v libx264 -preset slow -crf 20 -c:a copy \
  scene-N-scaled.mp4
```

### 5.4 Concat with CTA

```bash
cat > concat-list.txt << 'EOF'
file 'scenes/scene-1/scene-1-scaled.mp4'
...
file 'scenes/scene-N/scene-N-scaled.mp4'
file 'cta-scaled.mp4'
EOF
```

The resolved game CTA is added AFTER the last clip in the concat list.

---

## 6. Subtitles — ONE universal style, whisper-timed

Subtitles are **identical across all formats**: one style/size/position, always timed by faster-whisper.
No per-format presets, masks, secondary-style, marginv/offset/atempo. Graphic overlays (series title,
survival %, top-list numbers, slogans) are NOT subtitles — a separate script `tools/overlays.py` draws
them (see §6.5).

`manager` passes you one subtitle flag: `SUBTITLES` (`true`/`false`). If `false` (motion-dance,
dual-style) — no ASS is generated, no `ass=` token in `filter_complex`. Individual silent scenes
(silent I2V / physical-gag) are detected by an empty `tts` in the storyboard scene, not by a format
flag — whisper simply finds no speech there in the final voice track.

### 6.0 Three hard rules

**SUB-1 — `ass=build/subs.ass` is the LAST video filter.** It comes after `concat` and all overlay tokens
from §6.5. Check: `ass=` is the last token of the video chain before `-map [v…]`.

**SUB-2 — Loudnorm 2-pass on the final audio** (-14 LUFS / -1 dBTP / 11 LU). Two passes (measure →
apply), otherwise social platforms drop the volume unevenly across scenes.

**SUB-4 — subtitle events must not bleed outside dialogue scene windows.** After `add_subtitles.py` runs, build the cumulative timeline from the actual scene MP4 durations and classify clips from `storyboard.json`. Every ASS `Dialogue` event must fit inside one dialogue clip window. If an event overlaps action/silent I2V, CTA, or the next dialogue scene, clamp it to the dialogue window it overlaps most. If Whisper merged words across a boundary (`THE GIRL DIPLOMACY`, `HOW CIVILIZATIONS FALL FIRST`), split the text manually at the scene boundary. This applies to serial-drama I2V dialogue as well as Avatar-based formats.

**SUB-3 — never cut inside a word.** If you trim a scene tail for music / `-t TOTAL_DUR`, snap to a word
boundary. The boundaries come from `build/subs.ass` events (already whisper-aligned); no separate
`timings.json` is needed.

### 6.1 build/voice-final.wav — the key step (timings correct BY CONSTRUCTION)

Whisper runs on **the exact voice track that ships in the final** (post-atempo, post-adelay, post-concat,
pre-bg-music). Then the subtitle and audio timelines cannot diverge — there is no second timeline. That
is why `--offset/--atempo/--verify-audio` no longer exist.

`build/voice-final.wav` = the `[aout]` audio branch of §0 **minus bg-music**, frozen to disk.

**Single-voice** (character-story, reddit-story, redcon — one `tts-output.mp3` over the whole concat):
```bash
# same atempo->adelay pair that §0 bakes into the video:
$FFMPEG -y -i build/tts-output.mp3 \
  -af "atempo=${SPEED},adelay=${PRE_MS}|${PRE_MS},aresample=48000" \
  -ac 1 build/voice-final.wav
```
The `adelay` lead silence shifts the first word to `${PRE_MS}` — whisper sees the real position, no
`--offset` needed.

**Multi-voice** (serial-drama, news, gameplay-ai-avatar, what-if-real-life, fun-news, special-report):
```bash
# For EACH scene K in index order, build its speech slot EXACTLY as long as the scene:
#   - silent I2V / action / physical-gag -> anullsrc for the clip length (silence placeholder)
#   - I2V dialogue / Avatar dialogue -> EXTRACT audio from scene-K.mp4 ITSELF.
#       Do not use source scene-K.mp3 for timing; the video MP4 is the audio the viewer hears.
#   - + off-screen VO (customer.mp3 etc.) — same amix as in §0
#   - apply the same per-scene atempo/apad as in §0 (slot length == video clip length)
# then concat in index order, no bg-music:
$FFMPEG -y <per-scene inputs> \
  -filter_complex "<per-scene shaping, slot_k == clip_dur_k>,concat=n=${N}:v=0:a=1[a]" \
  -map "[a]" -ac 1 build/voice-final.wav
```
**Critical:** each slot == its scene length (silence under silent scenes). Then the sum ≈ `MAIN_DUR`,
and `add_subtitles.py` checks this (it fails if `voice-final` is far shorter than `--main-dur` — the
common "glued the lines back-to-back without silence" bug). `voice-final.wav` is exactly the speech the
viewer hears (bg-music excluded: it does not move speech timing, and whisper transcribes cleaner without
music).

This removes the single-voice / multi-voice split: both produce one `voice-final.wav`, both call the script identically.

### 6.2 Canonical call (the only one)

```bash
python3 tools/add_subtitles.py \
  build/voice-final.wav \
  build/subs.ass \
  --storyboard storyboard.json \
  --lang "${LANGUAGE}" \
  --main-dur "${MAIN_DUR}"
```

- **Whisper gives timecodes only. We burn the scenarist's text** (forced alignment): the script reads
  the canonical text from `storyboard.json` (`scenes[].tts` in order for multi-voice; top-level
  `tts.full_text` for single-voice) and aligns it to the whisper timings. The whisper transcript
  (with Chatterbox hallucinations) never reaches the screen.
- **NO** `--text`, `--style`, `--offset`, `--atempo`, `--verify-audio`, `--mask`, `--secondary-style`,
  `--marginv`, `--highlight-words` — all removed from the script.
- `--main-dur ${MAIN_DUR}` (end of the last story clip before CTA) — the script clamps the last event
  itself so the subtitle never runs onto the CTA. No manual `sed` on the ASS.
- Style is fixed in the script: Helvetica 72, CAPS, white + black outline, MarginV=520, 4-word chunks.

Burn with the `ass=` filter, NOT `subtitles=` (on macOS ffmpeg-full `subtitles=` can return a black
frame). And only via `/usr/local/bin/ffmpeg-full/ffmpeg` (libass), see §11.

```bash
-vf "ass='$OUTPUT_DIR/build/subs.ass'"
```

### 6.3 ASS invariants

1. **No event overlap** — `add_subtitles.py` guarantees it by construction (each chunk lives until the
   next one starts).
2. **Subtitles never reach the CTA** — guaranteed by `--main-dur`.
3. **No opaque box / full-width drawbox** — the style uses an outline (borderstyle=1), not a box.

### 6.4 Technical self-eval after the burn

1. **Duration:** `ffprobe duration final.mp4 ≈ sum(scene_durations)[+ CTA] ± 200ms`.
2. **Loudness:** `input_i` in [-15.0, -13.0].
3. **Subtitle pipeline:** validate the ASS file structure/timestamps, confirm the selected FFmpeg binary exposes the `ass` filter, and require a successful encode. Do not sample frames, calculate pixel variance, or perform semantic/visual subtitle review.

### 6.5 Graphic overlays — `tools/overlays.py` (NOT subtitles)

If `manager` passed `OVERLAYS=true`, draw the branded graphic overlays from `storyboard.json`
(`scenes[].overlays[]` — title card / series title, hud_counter (survival %), outcome_plate
(YOU DIED/SURVIVED), rank_number (#5..#1), item_name, slogan, disclaimer). The script emits a drawtext
fragment **per scene** that you splice into the `[vk]` branch **before concat** (single-pass §0):

```bash
for K in $(seq 1 $N); do
  FRAG=$(python3 tools/overlays.py storyboard.json --scene-index $K --workdir build \
           --input-label "[v${K}pre]" --output-label "[v${K}]")
  # empty FRAG = the scene has no overlays -> the branch stays [v${K}pre]->[v${K}] passthrough
done
# fragments are inserted into filter_complex between scale/pad/fps ([v${K}pre]) and concat
```

Before the expensive encode: `python3 tools/overlays.py storyboard.json --check` (font validation).

drawtext rules (macOS): only `ffmpeg-full` (libfreetype); the script already uses `textfile=` and
`expansion=none` (escapes `:` and `%`), `fontfile=` resolved from the FONTS map with fallbacks.


## 7. Split-screen (gameplay-ai-avatar) — 3-zone layout

The universal subtitle sits at a fixed MarginV=520 → it actually occupies **y≈1256–1400**
(2 lines) on the 1920 canvas. There used to be a `--marginv 800` seam trick here; now the position is
fixed, so we fit the layout to it: a **3-zone vstack** where the caption band lands exactly on y1256–1400.
Only `crop`, never `pad`.

- Gameplay top: 1080×1255 (crop) — y0–1255
- **Caption band: 1080×150 (y1255–1405)** — a darkened strip; the subtitle (y1256–1400) lands right here
- Avatar bottom: 1080×515 (crop) — y1405–1920

Sum 1255+150+515 = 1920 ✓. The subtitle covers neither gameplay nor the avatar's face — it has its own band.

```bash
$FFMPEG -y -i avatar-speedup.mp4 -i gameplay-trimmed.mp4 \
  -filter_complex "
    [1:v]scale=1080:1255:force_original_aspect_ratio=increase,crop=1080:1255[gp];
    [0:v]scale=1080:515:force_original_aspect_ratio=increase,crop=1080:515[av];
    color=c=black@0.60:s=1080x150:d=1[band];
    [gp][band][av]vstack=inputs=3[v];
    [1:a]volume=0.25[bg];
    [0:a][bg]amix=inputs=2:duration=first[aout]
  " \
  -map "[v]" -map "[aout]" -c:v libx264 -preset slow -crf 20 -c:a aac -b:a 128k -r 30 \
  final-base.mp4
```

- The subtitle is burned with `ass=` AFTER this composite (see §6) — at MarginV=520 it lands on the dark band.
- Avatar audio = 100%, gameplay audio = 25% (background)
- Avatar already arrived from Animator with 1.3x speedup (setpts + atempo) — Editor does not touch the speed
- No `--marginv 800`/seam trick — the subtitle position is the same for all formats.

---

## 8. Single pipeline preferred over layered

If possible, combine steps in one ffmpeg call via `-filter_complex`. Each intermediate re-encode = quality loss + DTS issues.

Example of combining concat + bg music + subtitles in one call: use `[0:v][0:a]` for the scene, `concat` filter, then `amix`, then `subtitles` — all inside one `-filter_complex`. Only if readable.

If layered — each layer through `-c:v libx264 -preset slow -crf 20`, not `-c copy`.

---

## 8.1 Never suppress ffmpeg stderr

❌ `$FFMPEG ... 2>/dev/null` — error is swallowed, output file is not created, pipeline silently moves on with broken/empty result.

✅ `$FFMPEG ... 2>&1 | tail -20` — see the error, can diagnose.

---

## 8.2 Output file validation — only after the process exits

❌ `ffprobe output.mp4` while ffmpeg is still writing → `moov atom not found` (moov is written last). False "corrupt", panic, second ffmpeg launched → both crash.

✅ First make sure ffmpeg has exited:
```bash
$FFMPEG -y -i input.mp4 ... output.mp4 2>&1 | tail -5
# ffprobe ONLY after this:
ffprobe -v error -show_entries format=duration -of csv=p=0 output.mp4
```

If ffmpeg runs in the background — wait for the process to exit:
```bash
until ! pgrep -qf "ffmpeg.*output"; do sleep 5; done
```

**Never start a second ffmpeg on the same output file** — first `pkill`, then `rm`, then a new run.

Safety net: `-movflags +faststart` writes moov at the start of the file (after finalization), enabling faster streaming, but does NOT save you from interrupted writes.

---

## 8.3 subprocess + ffmpeg in Python scripts

❌ `subprocess.run(cmd, capture_output=True)` — ffmpeg writes ~3KB/s of progress to stderr. On 60s video = ~180KB. Pipe buffer = 64KB → deadlock: ffmpeg blocks on stderr write, Python waits on ffmpeg.

✅ Stderr to a file:
```python
with open("render.log", "w") as log:
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=log)
```

Bug fixed in `tools/add_subtitles.py` (2026-04-29). When adding new scripts with subprocess + ffmpeg — verify this pattern.

---

## 9. zsh pitfalls

Shell on macOS — zsh. Arrays 1-indexed: `arr=(a b c)` → `arr[1]=a`, `arr[0]=empty`.

**Do not use arrays in batch scripts** — write explicit commands per clip. Arrays silently return empty and break ffmpeg parameters (empty `-ss`, empty input path).

❌ Bad:
```zsh
SCENES=(scene-1 scene-2 scene-3)
for s in $SCENES; do $FFMPEG -i $s.mp4 ...; done
```

✅ Better — explicit:
```zsh
$FFMPEG -i scene-1.mp4 ...
$FFMPEG -i scene-2.mp4 ...
$FFMPEG -i scene-3.mp4 ...
```

Or use bash explicitly: `#!/bin/bash`.

---

## 9.1 Pre-assembly checklist (serial-drama)

Before starting concat, walk through this checklist. Each missed item = re-assembly of the whole final.mp4.

- [ ] **Recap:** if EP2+ — last 1-2 clips of the previous episode are at the start of the concat list
- [ ] **Recap audio:** dialogue clips from the recap kept original audio (not replaced with anullsrc)
- [ ] **Recap subtitles:** if recap contains dialogue — subtitles overlaid via add_subtitles.py
- [ ] **Episode number:** overlay ONLY on the first clip (if there's a recap — on the recap, NOT on scene-1). Verify no duplicate
- [ ] **Dialogue audio during normalization:** serial-drama I2V dialogue / Avatar dialogue normalized with `-c:a aac` (preserving original audio), NOT via `anullsrc`. `anullsrc` ONLY for clips without audio
- [ ] **TTS overlay:** I2V clips with off-screen voiceover got TTS through aecho BEFORE subtitles
- [ ] **Subtitles:** all dialogue clips (serial-drama I2V dialogue, Avatar dialogue, and TTS overlay) have subtitles
- [ ] **Audio padding:** after add_subtitles.py — apad each clip to video duration
- [ ] **Fade-to-black:** on the last story clip (before CTA)
- [ ] **CTA:** last in the concat list
- [ ] **Music:** overlaid after concat and any format-specific speed step, volume per format

### Normalization by clip type

| Clip type | Video | Audio |
|---|---|---|
| I2V (action, silent) | scale + 30fps + libx264 | `-f lavfi -i anullsrc` → map 1:a |
| I2V dialogue / I2V with generated audio | scale + 30fps + libx264; never trim | **Preserve original:** normalize embedded audio to target sample rate/channels |
| I2V + TTS overlay | first normalize as I2V, then amix with TTS via aecho | |
| Avatar (dialogue, with audio) | scale + 30fps + libx264 | **Preserve original:** `-ar 44100 -ac 2 -c:a aac` (NOT anullsrc) |
| Recap (from previous episode) | scale + 30fps + libx264 | Check ffprobe: has audio → keep; none → anullsrc |

---

## 10. Checks before handing off final.mp4

- [ ] File exists, size > 100 KB (`stat -f%z final.mp4`)
- [ ] `ffprobe` shows correct duration (close to sum of clip durations)
- [ ] `ffprobe` shows 1080×1920, 30 fps
- [ ] Audio tracks present, AAC stereo
- [ ] FFmpeg concat is deterministic — if input clips passed programmatic validation, the output is correct. Do NOT Read frames from `final.mp4` (`rules/main/validation.md`)
- [ ] CTA in place (if applicable)
- [ ] Subtitle ASS timestamps are valid and non-overlapping; the libass encode completed successfully (if applicable)
- [ ] Duration within format expectations (serial-drama 25–40s; gameplay-ai-avatar 30–40s)
- [ ] **Workspace layout clean:** `ls OUTPUT_DIR` returns only `final.mp4`, `storyboard.json`, `scenes/`, optional `recap/` and `_archive/`. Anything else (concat lists, intermediate mp4s, temp audio, ad-hoc scripts, logs) is under `build/`. If `ls` shows stray files, move them into `build/` before handing off.

After verification — return the path to `final.mp4` to Manager. In debug mode — explanation (what was assembled, layout, which steps were skipped/added).

---

## 11. ffmpeg binary selection — libass requirement for ASS burn-in

System `ffmpeg` 8.x ships WITHOUT libass on this machine. If you run `-vf "ass=..."` or `-vf "subtitles=...ass"` with that binary, the filter is silently dropped — the video re-encodes without subtitles and no error is printed. The pipeline reports success and the user discovers missing subs later.

**Always burn ASS via `/usr/local/bin/ffmpeg-full/ffmpeg`** (or whichever build has libass). Detect at top of any script that burns subtitles:

```bash
FFMPEG=/usr/local/bin/ffmpeg-full/ffmpeg
[ -x "$FFMPEG" ] || { echo "ERROR: ffmpeg-full is required"; exit 1; }
$FFMPEG -hide_banner -filters 2>&1 | grep -q '^ T.. ass ' || {
  echo "ERROR: ffmpeg lacks libass — ASS burn-in will silently fail"; exit 1; }
```

`-vf "subtitles=foo.srt"` (SRT) works with stock ffmpeg; only ASS specifically needs libass. If your subtitles are SRT, the stock binary is fine.

---

## 12. Off-screen / non-animated VO must be explicitly mixed

Any scene that has a voice NOT generated by Avatar v2 (off-screen NPC, customer, narrator, back-to-camera speaker — see `sound.md` §9) arrives as an additional mp3 in `scenes/scene-K/`. Avatar's lipsynced audio is in the clip's video track; the extra VO is a separate file. Editor MUST mix them — they do not combine automatically.

Per-scene amix pattern (extra VO during silence padding at start of Avatar clip):

```bash
$FFMPEG -y -i scene-K-scaled.mp4 -i scenes/scene-K/extra-vo.mp3 \
  -filter_complex "[1:a]apad[c];[0:a][c]amix=inputs=2:duration=first:normalize=0[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k scene-K-mixed.mp4
```

**Sanity RMS check after mix:** measure RMS of the final audio on the interval where the extra VO is supposed to be heard. If the result is ≤ -35 dB → the VO did not land in the mix (most likely you forgot `-i extra-vo.mp3` or got the filter labels wrong). -22 to -28 dB is the normal range for a clearly audible mixed VO.

```bash
$FFMPEG -i final.mp4 -ss 1.5 -t 2.0 -af "volumedetect" -f null - 2>&1 | grep mean_volume
```

---

## 13. Kling artifacts — fix with prompts, do NOT mask

Masking artifacts with a subtitle box (the old `--mask` / BorderStyle=4) is **removed**. Kling
artifacts (CJK hallucinations, garbled text near the frame bottom) are prevented at the prompt level —
the format playbook's negative_prompt (see what-if-real-life.md). No full-width `drawbox` and no
opaque-box subtitles: the one style uses an outline only.

## 14. Speedup is a mandatory step, not optional (LEGACY FORMATS ONLY — see §3d override)

> ⚠️ **`serial-drama` is excluded from this section — see §3d.** Its I2V clip durations are the scenarist's final, deliberate pacing (5s = 5s). Applying the §14 self-check below to serial-drama will flag a correct, unsped-up `final.mp4` as if the speedup step were missing — it is not missing, it does not apply. Burned 2026-07-14 (star-trek-airlock EP13): this section's blanket "1.15× for serial-drama" line directly contradicted §3d's explicit override and caused a rebuild to wrongly speed up an episode that had already been correctly assembled without speedup.

The speedup pass (1.18× for comedy-sketch, format-dependent — see format playbook; NOT serial-drama) is part of the standard pipeline order for formats that request it:

> normalize → subtitles → episode number → TBC → concat → **speedup** → music

If `duration(final.mp4) ≈ sum(scene_durations)` exactly, you skipped the speedup. Self-check before handoff:

```bash
EXPECTED=$(echo "scale=2; $SUM_OF_SCENES / $SPEEDUP_FACTOR" | bc)
ACTUAL=$($FFMPEG -i final.mp4 2>&1 | grep Duration | awk '{print $2}')
# ACTUAL should be within ±0.2s of EXPECTED
```

Music mix happens AFTER speedup so the music pitch is not affected.
