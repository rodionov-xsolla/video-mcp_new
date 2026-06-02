# Editor — FFmpeg assembly craft

You are the editor. Manager passes you: all `scene-K.mp4`, audio (TTS / Avatar audio / bg music), subtitles (if pre-made), format (split-screen / vertical), **opener and CTA from Supabase** (`.mp4` videos). You assemble `final.mp4` (1080×1920).

**Core principles:**
1. **One ffmpeg pipeline, not layered.** Each intermediate re-encode = quality loss and DTS issues.
2. **All clips → identical fps + audio format BEFORE concat.** Otherwise concat breaks.
3. **Never `-shortest` with TTS overlay** — clips video to audio length. Use `apad`.
4. **CTA is a file, do not rebuild it** if it's already valid.

FFmpeg:
- `/usr/local/bin/ffmpeg` — Homebrew 8.1, **without libfreetype** → drawtext does not work. Use only for concat/audio/scale.
- `/usr/local/bin/ffmpeg-full/ffmpeg` — tessus build with libfreetype → **drawtext works**. Use for subtitles.

Variable `$FFMPEG` defaults to `/usr/local/bin/ffmpeg-full/ffmpeg` (when drawtext is needed) or `/usr/local/bin/ffmpeg` (for other steps). Shell — `zsh` (macOS), arrays 1-indexed.

---

## Inputs

From Manager:
- `scenes/scene-K/scene-K.mp4` (K = 1..N) — animated clips (from Animator)
- `scenes/scene-K/scene-K.mp3` (opt.) — TTS audio (from Sound; for serial-drama I2V overlay; Avatar clips have embedded audio)
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
- normalized assets: `cta-normalized.mp4`, `cta-fallback.mp4`, opener-normalized, etc.
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

**This is the path. Use it for every format unless a section below explicitly overrides for that format (split-screen gameplay-ai-avatar, format-specific subtitle burn-in styles).**

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

### 0.2 Worked example (redcon / what-if-lore, 8 scenes + CTA)

This is the exact command that ships our redcon/what-if-lore Spock-Borg video (50s output, 1:28 wall-clock, 23 MB):

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

- **`-preset medium -crf 22`** — single-pass default. On 1080×1920, ~0.55× realtime (~90 s for 50 s output). Visually indistinguishable from `slow crf 20` after social-network re-encode (TikTok/Reels/Shorts re-transcode anyway).
- **`-preset slow -crf 20`** — ONLY for archival masters or when explicitly requested. Costs 3–5× wall-clock for 5–10% bitrate at perceptual parity. Do not use as default.
- `-pix_fmt yuv420p` — required for QuickTime + all social uploads.
- `-c:a aac -b:a 128k -ar 44100 -ac 2` — locked. Do not change.
- `-t TOTAL_DUR` — mandatory hard cap so `apad` / `amix duration=longest` do not extend final to music length (185 s of bg-music would otherwise leak through).

### 0.4 Audio shaping — match what the ASS expects

The ASS file from `tools/add_subtitles.py` is timed against the **final** TTS shape after atempo + adelay. The filter graph must apply the same operations in the same order. If you re-trim TTS or change atempo after generating ASS, subtitles will drift — regenerate the ASS.

Order is `atempo` → `adelay`. atempo first compresses speech to fit the picture window; adelay then offsets it so TTS starts after any title-card silence (e.g. 5000 ms for redcon/what-if-lore's title card).

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
- **Subtitle generation** (§6) — different formats use different styles (PIL PNG word-highlight vs ASS chunked vs drawtext). All emit a file (PNG sequence / ASS / drawtext expr) that §0 ingests via `ass=`, `overlay=`, or `drawtext=`. The principle holds: generate the asset off-pipeline, burn in **inside** §0.
- **Per-scene drawtext / TBC / episode card** — express as `drawtext` filters chained onto the affected `[vk]` branch BEFORE concat. Do not run a separate pass.

### 0.6 When NOT to use the canonical pipeline

- A single scene needs per-scene filter that breaks the graph (rare — usually solvable by chaining filters on that `[vk]` branch)
- Debugging which stage corrupts output → run the legacy multi-stage (§§1–5) once, find the bad stage, fix the underlying filter, return to §0

There is **no quality reason** to prefer multi-stage. Every multi-stage run = N full re-encodes of the entire timeline = N× generation loss. Single-pass = one encode.

---

## 1. Normalization (scale + fps + audio) — LEGACY (debug only)

> ⚠️ **Prefer §0 single-pass pipeline.** This section describes the legacy multi-stage path. Use only when debugging an intermediate, or when §0 cannot express a required per-scene filter chain.

**Path convention for every snippet below.** Run all commands with `OUTPUT_DIR` as cwd. Inputs come from `scenes/scene-K/...` (unchanged). **Every scratch file in the snippets — `concat-list.txt`, `concat-final.txt`, `final-base.mp4`, `final-speed.mp4`, `video-concat.mp4`, `cta-normalized.mp4`, `cta-fallback.mp4`, `bg-music.mp3`, `tts-output.mp3`, `tts-fast.mp3`, etc. — must be written to `build/`, not to the root.** So when a snippet says `final-base.mp4`, you write `build/final-base.mp4` and read it the same way on the next step. The ONLY file that lands in the root is the final deliverable, via `mv build/final-music.mp4 final.mp4` at the very end. Run `mkdir -p build` before your first ffmpeg call. See "Workspace layout (MANDATORY)" above.

**CRITICAL:** before concat all clips MUST have identical fps and audio format.

I2V (Kling) is 24fps, Avatar (Kling Avatar) is 30fps → normalize EVERYTHING to 30fps.

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

For non-serial-drama formats that DO request an episode card: the first clip gets the episode number overlaid (e.g. `EPISODE 1`, `EPISODE 2`) via drawtext. Text in the upper third of the frame, white, with a black stroke, appearing at 1-3 seconds of the clip.

```bash
EP_NUM="EPISODE 1"  # from storyboard.json → episode_number
$FFMPEG_FULL -y -i scenes/scene-1/scene-1-scaled.mp4 \
  -vf "drawtext=fontfile='$IMPACT':text='$EP_NUM':fontsize=80:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h*0.15:enable='between(t,0.5,2.5)'" \
  -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -c:a copy \
  scenes/scene-1/scene-1-scaled.mp4
```

Font: Impact or equivalent. Use `$FFMPEG_FULL` (with libfreetype).

---

## 3d. Speed up the video (LEGACY — DO NOT USE for serial-drama)

> ⚠️ **OVERRIDE — for `serial-drama`: SKIP this section.** `formats/serial-drama.md` explicitly says `Do NOT speed up Avatar` and clip durations in the storyboard are the final timings (5s = 5s, not 5/1.15s). 1.15x bump on the whole episode also accelerates I2V action that the scenarist already paced at 5s. The block below applies only to formats that explicitly request the 1.15x bump in their playbook (e.g. `gameplay-ai-avatar` has its own 1.3x rule for Avatar audio, see section 11 of `animator.md`).

**After concat, BEFORE music overlay** (legacy formats only) — speed up the whole video by ~1.15x. This makes the video more dynamic without noticeable voice distortion.

```bash
$FFMPEG -y -i final-base.mp4 \
  -filter_complex "[0:v]setpts=PTS/1.15[v];[0:a]atempo=1.15[a]" \
  -map "[v]" -map "[a]" \
  -r 30 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  final-speed.mp4
```

**Pipeline order:**
1. Normalize clips (section 1)
2. Subtitles on dialogue clips (section 6)
3. Episode number on the first clip (section 3c)
4. TBC on the last clip (section 5)
5. Concat (section 2) → `final-base.mp4`
6. **Speed up 1.15x (this section)** → `final-speed.mp4`
7. Music (section 4) → `final.mp4`

Music is overlaid AFTER speedup — otherwise the music pitch shifts.

---

## 4. Background music (MANDATORY for all formats)

The track is picked by Sound (see `sound.md`). Editor receives the path to the track and the volume parameter, mixes with the final video:

```bash
$FFMPEG -y -i final-base.mp4 -i bg-music.mp3 \
  -filter_complex "[1:a]volume=0.15,apad=whole_dur=$VIDEO_DUR[music];[0:a][music]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 128k \
  final-with-music.mp4
```

- Music volume is set by Sound (serial-drama=0.15, gameplay=0.10, reddit-story=0.05)
- `apad=whole_dur=$VIDEO_DUR` — pad with silence if music is shorter than the video
- NEVER `-shortest`
- If Sound did not specify a track — **stop and ask Manager**. Music is mandatory

---

## 5. Video ending: fade-to-black + CTA (MANDATORY)

Every video ends with **fade-to-black → CTA text**. Two variants:

### 5.1 Custom CTA (priority)

If a prepared CTA video exists — concat it at the very end after all scenes.

**CTA lookup — priority order (MUST be scoped to `GAME_TAG`):**
1. **Supabase Storage** — `assets/{GAME_TAG}/cta-*.mp4`. CTA URL is recorded in the game .md file (`games/{GAME_TAG}/{GAME_TAG}.md` → CTA section).
2. **Most recent previous episode of the same `GAME_TAG`** — `output/.../{GAME_TAG}/.../cta-fallback.mp4` or similar.
3. **`games/{GAME_TAG}/assets/cta/cta.mp4`** — local shared CTA of the game.
4. **Programmatic fallback** (section 5.2) — generate "FOLLOW FOR MORE" on black.

> ⚠️ **NEVER pick a CTA from a game-agnostic location** (e.g. `video-agent/cta-star-trek-timelines.mp4` at the repo root — this is star-trek-timelines branded, do NOT use for any other game). Resolve the CTA strictly from a `GAME_TAG`-scoped path — Supabase URL from the game .md file, the most recent prior episode's `output/.../{GAME_TAG}/...cta-fallback.mp4`, or `games/{GAME_TAG}/assets/cta/cta.mp4`. **The path is the validation** — never Read a frame to confirm branding.

Different episodes may have different CTAs. Don't copy blindly — verify filename + size + duration via ffprobe. Brand correctness is guaranteed by the path, not by visual inspection.

Download: `curl`, NOT `urllib`. After download — `ffprobe` validation (duration, codec, dimensions). CTA is normalized via the same `scale + pad + 30fps + AAC` step (section 1).

### 5.2 Fallback CTA: fade-to-black + "FOLLOW FOR MORE"

**If no custom CTA found** — generate CTA programmatically:
- 2 seconds of black 1080×1920
- White text centered: `"FOLLOW FOR MORE"`
- Text fade-in from black (0.5s)

```bash
$FFMPEG_FULL -y \
  -f lavfi -i color=c=black:s=1080x1920:d=2:r=30 \
  -f lavfi -i anullsrc=r=44100:cl=stereo \
  -vf "drawtext=fontfile='$IMPACT':text='FOLLOW FOR MORE':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:alpha='if(lt(t,0.5),t/0.5,1)'" \
  -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p \
  -map 0:v -map 1:a -c:a aac -b:a 128k -shortest \
  cta-fallback.mp4
```

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

CTA (custom or fallback) is added AFTER the last clip in the concat list.

---

## 6. Subtitles — единый канонический путь

Стиль субтитров определяет **оркестратор** через front-matter формата (`subtitle_style`, `subtitle_offset_s`, `subtitle_mask`, `subtitle_highlight`, `subtitle_extras`). Editor получает их в виде плейсхолдеров `${SUBTITLE_*}` и просто прокидывает в `tools/add_subtitles.py`. Никаких форматных таблиц «serial-drama vs reddit-story» здесь больше нет — это работа `manager.md`.

### 6.0 Три hard-rules (нарушение → silent failure)

**Rule SUB-1 — субтитры это ПОСЛЕДНИЙ фильтр в `filter_complex`.**
В graph'е `ass=build/subs.ass[vsub]` идёт после `concat` и после ВСЕХ overlay-токенов (CTA-фильтры, маски, drawtext). Если бёрн саба попадёт ДО overlay'я — оверлей нарисуется поверх текста, в логах чисто. Проверка перед запуском ffmpeg: `grep -nE 'ass=|subtitles=' <filter_complex>` должна быть последним токеном в видеоцепочке перед `-map [v…]`.

**Rule SUB-2 — Loudnorm 2-pass на финальном аудио ДО сборки final.mp4.**
Цель: -14 LUFS integrated / -1 dBTP peak / 11 LU range (стандарт TikTok/YouTube/Reels/X). Двухпроходно:
```bash
# pass 1: measurement
$FFMPEG -i build/aout.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 \
  | sed -n '/^{$/,/^}$/p' > build/loudnorm.json

# pass 2: apply with measured params
M_I=$(jq -r .input_i build/loudnorm.json)
M_TP=$(jq -r .input_tp build/loudnorm.json)
M_LRA=$(jq -r .input_lra build/loudnorm.json)
M_THRESH=$(jq -r .input_thresh build/loudnorm.json)
OFFSET=$(jq -r .target_offset build/loudnorm.json)

$FFMPEG -y -i build/aout.wav \
  -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=$M_I:measured_TP=$M_TP:measured_LRA=$M_LRA:measured_thresh=$M_THRESH:offset=$OFFSET:linear=true" \
  -ar 44100 -ac 2 -c:a aac -b:a 128k build/aout-norm.m4a
```
Затем `aout-norm.m4a` идёт в final.mp4 (через `-i build/aout-norm.m4a -map …:a -c:a copy`). Без 2-pass соцсети сами понизят громкость неравномерно по сценам, и микс «прыгает».

**Rule SUB-3 — никаких порезов внутри слова.**
Если Editor подрезает хвост сцены под музыку / `-t TOTAL_DUR` / cliffhanger — snap к ближайшей `word.end ≤ target` из `scenes/scene-K/scene-K.timings.json` (Sound пишет этот файл, см. `sound.md` §12). Без snap'а последний саб обрывается на полуслове.

### 6.1 Обоснование MarginV safe-zone (для всех пресетов)

UI TikTok/Reels/Shorts (caption-bar, username, right-rail actions) перекрывает нижние 25-30% кадра 1080×1920. При `PlayResY=1920`:

| Пресет | MarginV | Позиция от низа | Когда применять |
|---|---|---|---|
| `bold` | 520 | ~27% | Фастпейс, punchy, конкурирует с UI — нужен запас |
| `narrative` | 420 | ~22% | Длинные строки, спокойный темп, ниже допустимо |

**Меньшие значения трогать только если у формата есть конкретная причина** (например, `--mask` для перекрытия артефактов Kling у самого низа кадра в `what-if-real-life`: MarginV=120 при mask=true опускает бокс прямо на артефакт). Это override от оркестратора через `SUBTITLE_EXTRAS`, а не дефолт.

⚠️ **Alignment=2 + MarginV — направление ОТ низа.** Бóльший MarginV = выше на экране. Меньший = ниже. Если задача — закрыть артефакт у самого низа, нужен МАЛЕНЬКИЙ MarginV (70-150), не большой.

### 6.2 Канонический вызов из editor pipeline

Editor получает от manager'а:
- `${SUBTITLE_STYLE}` — `bold` / `narrative` / `none` / `custom`
- `${SUBTITLE_OFFSET_S}` — число (pre-delay титульной карточки, 0 если её нет)
- `${SUBTITLE_MASK}` — `true` / `false`
- `${SUBTITLE_HIGHLIGHT}` — `true` / `false`
- `${SUBTITLE_EXTRAS}` — строка с дополнительными CLI-флагами (например `--secondary-style Customer=lightgray,52,1,120 --marginv 800`)

Если `${SUBTITLE_STYLE}` = `none` — НЕ генерировать ASS, в `filter_complex` нет `ass=` токена, переход сразу к audio map. Это `motion-dance`, `dual-style`, любая сцена с `scene_type: physical-gag`.

Если `${SUBTITLE_STYLE}` = `custom` — формат сам описывает per-scene drawtext-логику в своём правиле (это режим для `top-list` номеров/имён — там это graphic overlay, а не субтитры).

Иначе — для каждого диалогового клипа (или одного master.ass на весь концат) генерируем ASS:

```bash
# Per-scene вариант (multi-voice форматы — serial-drama, news, gameplay-ai-avatar, what-if-real-life):
TTS_TEXT=$(jq -r ".clips[$((K-1))].tts" storyboard.json)
DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 scenes/scene-$K/scene-$K.mp4)

EXTRA_FLAGS=""
[ "${SUBTITLE_MASK}" = "true" ] && EXTRA_FLAGS="$EXTRA_FLAGS --mask"
[ "${SUBTITLE_HIGHLIGHT}" = "true" ] && EXTRA_FLAGS="$EXTRA_FLAGS --highlight-words"

python3 tools/add_subtitles.py \
  - scenes/scene-$K/scene-$K.mp3 build/subs-scene-$K.ass \
  --emit-ass-only \
  --duration "$DUR" \
  --text "$TTS_TEXT" \
  --style "${SUBTITLE_STYLE}" \
  --offset "${SUBTITLE_OFFSET_S}" \
  --verify-audio scenes/scene-$K/scene-$K.mp3 \
  $EXTRA_FLAGS \
  ${SUBTITLE_EXTRAS}

# Single-voice (один TTS на весь концат — character-story, reddit-story, what-if-lore, redcon):
# ВАЖНО: audio-аргумент = ФИНАЛЬНОЕ аудио, которое реально идёт в микс (tts-fast.mp3,
# уже после atempo). НЕ передаём --atempo — множитель уже «запечён» в длительности файла,
# и подавать его нечем ошибиться. --verify-audio с тем же файлом ставит code-guard на дрейф.
python3 tools/add_subtitles.py \
  - build/tts-fast.mp3 build/subs.ass \
  --emit-ass-only \
  --duration "$MAIN_DUR" \
  --text "$FULL_NARRATION" \
  --style "${SUBTITLE_STYLE}" \
  --offset "${SUBTITLE_OFFSET_S}" \
  --verify-audio build/tts-fast.mp3 \
  $EXTRA_FLAGS \
  ${SUBTITLE_EXTRAS}
```

**Источник текста ВСЕГДА `storyboard.json`** (поле `tts` / `narrative_text` / `character_line` в зависимости от формата). Никогда не транскрибируй через faster-whisper известный текст. Whisper остаётся только как fallback внутри `add_subtitles.py` если `--text` не передан.

**Антидрейф by construction (вместо ручного `--atempo`).** ASS генерим из **того же аудио, что идёт в микс** — `build/tts-fast.mp3` (уже после `atempo`) для single-voice, `scene-$K.mp3` для per-scene. Тайминги тогда считаются по реальной длительности и не могут разойтись с фактическим звучанием. Флаг **`--atempo` устарел** — не передавай его: множитель уже запечён в длительности файла, а ручной множитель — это и был источник «съезжания» (несовпал с `filter_complex` → субтитры уезжали к концу клипа). Если файл по какой-то причине ещё не ускорен — сначала сделай `tts-fast.mp3` (§3b), потом генери ASS.

**`--verify-audio` ОБЯЗАТЕЛЕН** и указывает на то же финальное аудио. `add_subtitles.py` падает (exit 1), если конец последнего слова расходится с `offset + длина(аудио)` больше чем на 0.30с. Это code-guard: любой рассинхрон становится ошибкой билда, а не молча уезжает в прод. Не игнорируй его падение «ретраем» — чини источник (не то аудио / лишний `--atempo` / ASS сгенерён до финального speed).

**ASS генерится ПОСЛЕДНИМ — после того как форма аудио заморожена** (после любого `atempo`/whole-video speedup §3d). Если сначала собрал ASS, а потом поменял скорость — пересобери ASS.

**`--offset`** должен совпадать с `adelay` в filter_complex (в секундах). Например, для what-if-lore с титульной 5-секундной карточкой: `adelay=5000|5000` ↔ `--offset 5.0`.

### 6.3 ASS-инварианты (от Sound сюда, см. предыдущую версию `sound.md` §10)

1. **No event overlap within the same Style.** Два `Dialogue:` события одного стиля с пересекающимися временами рендерятся одновременно — текст ломается. `add_subtitles.py` гарантирует это by construction (каждый чанк живёт до начала следующего), но если ты редактируешь ASS вручную — проверяй.

2. **Last subtitle reaches clip end when masking.** При `--mask` последнее событие должно дотягиваться до `clip_duration - 0.05s`. Иначе во время хвостовой тишины артефакт под боксом снова виден. `add_subtitles.py` делает это автоматически (`out[-1] = (start, duration, word)`).

3. **Opaque box (BorderStyle=4) — НЕ во всю ширину кадра.** Бокс ASS обрамляет только текст + outline-padding. Никаких `drawbox` во всю ширину 1080 — это режет картинку. Если артефакт шире саба — увеличь `--secondary-style` font size или разбей фразу на длиннее чанк, но не делай full-width drawbox.

4. **Субтитры НЕ должны заходить на CTA.** Последнее ASS-событие в `subs.ass` должно заканчиваться не позже `MAIN_DUR` (конец последнего story-клипа, до CTA). `add_subtitles.py` генерирует тайминги по TTS, и если TTS-аудио после atempo+adelay длиннее `MAIN_DUR`, последний chunk автоматически вылазит за границу. После генерации ASS **всегда проверяй** конечный таймкод последнего `Dialogue:` события: если он > `MAIN_DUR`, обрежь его:
   ```bash
   # Пример: MAIN_DUR=40s → обрезать последний event
   sed -i '' "s/\(Dialogue:.*\),0:MM:SS\.ss,\(Default.*\)$/.../" build/subs.ass
   # Или вручную отредактируй последнюю строку в build/subs.ass
   ```
   CTA — отдельный branded ролик без субтитров. Субтитры на CTA = брак.

### 6.4 Programmatic self-eval после бёрна

После того как final.mp4 собран, перед handoff Manager'у — три программные проверки:

1. **Длительность.** `ffprobe duration final.mp4 ≈ sum(scene_durations) [+ CTA_dur] ± 200мс`. Иначе encode был прерван или amix утянул хвост в music.

2. **Loudness.** `ffmpeg -i final.mp4 -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null -` → `input_i` должен быть в [-15.0, -13.0]. Иначе loudnorm 2-pass не сработал.

3. **Bottom-strip variance per dialogue scene** (если `${SUBTITLE_STYLE} != none`). Для каждой сцены с непустым `tts` сэмплировать 1 кадр в `scene_midpoint + 0.5s`, посчитать pixel variance в bottom 25% кадра. Variance > порог (~500) ⇒ субтитр действительно прорендерился. Если хоть одна сцена даёт пустую полосу — бёрн саба провалился (libass не подцепился, fonts.conf битый, что-то ещё).

```bash
# вариант проверки: один кадр через ffmpeg + variance через ImageMagick / Python+PIL
$FFMPEG -y -ss "$SCENE_MID" -i final.mp4 -frames:v 1 -q:v 2 build/probe-$K.jpg
python3 -c "
import sys
from PIL import Image, ImageStat
img = Image.open(sys.argv[1]).convert('L')
w, h = img.size
strip = img.crop((0, int(h*0.75), w, h))
v = ImageStat.Stat(strip).stddev[0]
print(f'scene {sys.argv[2]} variance={v:.1f}')
sys.exit(0 if v > 15 else 1)
" build/probe-$K.jpg "$K"
```

До **3 ретраев** перепрожига с поправкой (например, на повторе передать `--marginv` ниже если variance подозрительно низкий). После 3 неуспешных — fail Manager'у, не молча.


## 7. Split-screen (gameplay-ai-avatar)

Layout: 60% gameplay top + 40% avatar bottom. Only `crop`, never `pad`.

```bash
# Avatar part: 1080×768
# Gameplay part: 1080×1152
$FFMPEG -y -i avatar-speedup.mp4 -i gameplay-trimmed.mp4 \
  -filter_complex "
    [1:v]scale=-1:1152:force_original_aspect_ratio=increase,crop=1080:1152[gp];
    [0:v]scale=-1:768:force_original_aspect_ratio=increase,crop=1080:768[av];
    [gp][av]vstack=inputs=2[v];
    [1:a]volume=0.25[bg];
    [0:a][bg]amix=inputs=2:duration=first[aout]
  " \
  -map "[v]" -map "[aout]" -c:v libx264 -preset slow -crf 20 -c:a aac -b:a 128k -r 30 \
  final-base.mp4
```

- Avatar audio = 100%, gameplay audio = 25% (background)
- Avatar already arrived from Animator with 1.3x speedup (setpts + atempo) — Editor does not touch the speed

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
- [ ] **Recap audio:** Avatar/dialogue clips from the recap kept original audio (not replaced with anullsrc)
- [ ] **Recap subtitles:** if recap contains dialogue — subtitles overlaid via add_subtitles.py
- [ ] **Episode number:** overlay ONLY on the first clip (if there's a recap — on the recap, NOT on scene-1). Verify no duplicate
- [ ] **Avatar audio during normalization:** Avatar clips (dialogue) normalized with `-c:a aac` (preserving original audio), NOT via `anullsrc`. `anullsrc` ONLY for I2V clips without audio
- [ ] **TTS overlay:** I2V clips with off-screen voiceover got TTS through aecho BEFORE subtitles
- [ ] **Subtitles:** all dialogue clips (Avatar + TTS overlay) have subtitles
- [ ] **Audio padding:** after add_subtitles.py — apad each clip to video duration
- [ ] **Fade-to-black:** on the last story clip (before CTA)
- [ ] **CTA:** last in the concat list
- [ ] **Music:** overlaid AFTER speed boost, volume per format

### Normalization by clip type

| Clip type | Video | Audio |
|---|---|---|
| I2V (action, silent) | scale + 30fps + libx264 | `-f lavfi -i anullsrc` → map 1:a |
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
- [ ] Subtitles readable, no overlap (if applicable)
- [ ] Duration within format expectations (serial-drama 25–40s; gameplay-ai-avatar 30–40s)
- [ ] **Workspace layout clean:** `ls OUTPUT_DIR` returns only `final.mp4`, `storyboard.json`, `scenes/`, optional `recap/` and `_archive/`. Anything else (concat lists, intermediate mp4s, temp audio, ad-hoc scripts, logs) is under `build/`. If `ls` shows stray files, move them into `build/` before handing off.

After verification — return the path to `final.mp4` to Manager. In debug mode — explanation (what was assembled, layout, which steps were skipped/added).

---

## 11. ffmpeg binary selection — libass requirement for ASS burn-in

System `ffmpeg` 8.x ships WITHOUT libass on this machine. If you run `-vf "ass=..."` or `-vf "subtitles=...ass"` with that binary, the filter is silently dropped — the video re-encodes without subtitles and no error is printed. The pipeline reports success and the user discovers missing subs later.

**Always burn ASS via `/usr/local/bin/ffmpeg-full/ffmpeg`** (or whichever build has libass). Detect at top of any script that burns subtitles:

```bash
FFMPEG=/usr/local/bin/ffmpeg-full/ffmpeg
[ -x "$FFMPEG" ] || FFMPEG=ffmpeg  # fallback
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

## 12a. Off-screen speaker subtitles — через `--secondary-style`

Если у формата есть второй голос (off-screen NPC, customer, narrator поверх Avatar'а — `dialogue-offscreen` сцены), оркестратор передаёт `SUBTITLE_EXTRAS` с флагом `--secondary-style`, например:

```
--secondary-style "Customer=lightgray,52,1,120"
```

(`Name=color,size,italic,marginv`). `add_subtitles.py` добавит второй ASS-стиль в тот же файл (см. `tools/add_subtitles.py` функцию `parse_secondary_style`).

**Тайминги** двух событий (Default + secondary) editor рассчитывает сам по `timings.json` (Sound пишет timings и для основного TTS, и для off-screen mp3 — `scene-K.timings.json` для `scene-K.mp3`, `scene-K.customer.timings.json` для `customer.mp3`). События обоих стилей попадают в один ASS:
- Customer events: `0:00:00.30` → `duration(customer.mp3)` (текст из `storyboard.json[scene].customer_line`)
- Default events: с `duration(customer.mp3) + 0.6s` (после паузы) (текст из `character_line` / `tts`)

Между Customer и Default диапазонами — без перекрытий (§6.3 invariant 1).

---

## 13a. Channel bug overlay (надканальный бренд)

Some games carry a permanent channel brand bug — a small static logo overlaid on every video like a TV station identifier (CNN/BBC/GLN style). Manager parses `channel_bug_url` from `games/{GAME_TAG}/{GAME_TAG}.md` and passes it as `CHANNEL_BUG_URL` in the editor prompt.

**Contract:**
- `CHANNEL_BUG_URL` empty / unset → NO overlay step. Skip this section entirely; pipeline runs as if channel branding does not exist.
- `CHANNEL_BUG_URL` non-empty → mandatory overlay. Apply per below.

### Positioning + sizing (universal — same across all formats / games)

| Parameter | Value | Why |
|---|---|---|
| Anchor corner | top-left | TikTok/Reels right-rail UI conflicts with right side; top-left stays clear of TikTok native UI + youtube Shorts cards. |
| Margin from edges | 40 px | Safe inside iPhone notch / mobile bezel. |
| Size at overlay | 110×110 | TV-bug subtlety. Larger = watermark, smaller = unreadable on 6" screens. |
| Source PNG | square RGBA, ≥256×256 (downscaled in filter) | Pre-baked alpha so we don't need to colorchannelmixer in the chain. |
| Opacity behavior | use PNG's baked alpha | If the source PNG was authored at 100% alpha and we need 70%, add `colorchannelmixer=aa=0.7` before overlay. |
| Lifetime | static, full video duration | No fade in/out; brand bug doesn't blink. |
| Apply position in graph | **after concat, before audio mapping** | One overlay over the whole timeline. NOT per-scene (would have to apply 5× and burn 5× more pixel work). |

### Single-pass filter_complex addendum

Add to §0 canonical pipeline when `CHANNEL_BUG_URL` is non-empty:

```bash
# In phase 0 (manager OR editor pre-flight): download to build/
curl -sLo build/channel-bug.png "$CHANNEL_BUG_URL"
[ -s build/channel-bug.png ] || { echo "ERROR: channel-bug.png empty"; exit 1; }

# In the ffmpeg invocation: add as last input
$FF -y \
  -i scenes/scene-1/scene-1.mp4 \
  ...  # all scenes
  -i build/cta-raw.mp4 \
  -i tts.mp3 \
  -i bg-music.mp3 \
  -i build/channel-bug.png \           # <-- NEW input, last position
  -filter_complex "\
    ...  # scene normalizes, concat → [vcat]
    [vcat]<existing video tail filters → [vsub]>; \
    [N+3:v]scale=110:110[bug]; \         # N+3 = channel-bug index (after cta, tts, music)
    [vsub][bug]overlay=40:40:format=auto[vout]; \
    ...  # audio branch unchanged → [aout]
  " \
  -map "[vout]" -map "[aout]" \
  ...
```

**Critical:** the overlay goes **AFTER** the ASS burn (`[vsub]`). Subtitles do not appear on top of the bug (bug is in top-left corner where subs never go), but visually it's cleaner to compose bug last so any pixel work on subtitles happens before the bug pixel is written.

If your specific format burns ASS per-scene inside each `[vk]` (fun-news / streettalk pattern), the overlay still goes after concat:

```
[vk] ... ass=build/scene-k.ass → [vk]   (per scene, k=1..N)
[v0..vN] concat=...→[vcat]
[vcat][bug]overlay=40:40[vout]          # bug applied to whole concat once
```

### Validation

Programmatic self-check after final.mp4 build:

```bash
# Sample one frame at t=1.0s, check top-left 200×200 region has non-empty pixel variance
$FFMPEG -y -ss 1.0 -i final.mp4 -frames:v 1 build/probe-bug.png 2>&1 | tail -3
python3 -c "
from PIL import Image, ImageStat
img = Image.open('build/probe-bug.png').convert('L')
strip = img.crop((30, 30, 230, 230))  # 200×200 area around bug
v = ImageStat.Stat(strip).stddev[0]
print(f'top-left variance: {v:.1f}')
import sys; sys.exit(0 if v > 25 else 1)
" || { echo "ERROR: channel bug missing or near-uniform"; exit 1; }
```

Variance > 25 means the bug is visually present (logo has structure → non-uniform luminance). Near-zero variance → bug overlay silently failed (likely chain error in filter_complex labels, or PNG was empty).

### Anti-patterns

- ❌ Bug per-scene (5 separate `[vk][bug]overlay` chains) — wastes pixel work, identical visual result.
- ❌ Bug on the CTA (visible double-brand) — the CTA is its own branded artifact; bug ends with the concat-before-CTA boundary OR runs through everything depending on game policy. Default: bug runs over entire timeline including CTA (consistent TV-bug behavior). If the game's CTA already has its own brand mark, override in format playbook.
- ❌ Bug fade in/out at scene transitions — looks broken, not TV-broadcast.
- ❌ Reading PNG via subprocess to "verify alpha" — programmatic variance check above is the standard. Do NOT visually Read the PNG in role-agent context (manager rule, `CLAUDE.md`).
- ❌ Bug position varying between videos in the same channel — kills brand recognition. Always top-left 40,40 at 110×110.
- ❌ Audio filter chain (`concat → adelay → amix`, or per-scene `amix` for ambient SFX) without `asetpts=N/SR/TB` after each stage and `aresample=async=1:first_pts=0` on inputs — produces a final.mp4 whose audio bitstream is correct but container timestamps are garbage (`start_time` ≈ 6.6 million years, `nb_frames` ≈ 2/sec instead of ~40/sec). Players ignore the audio → video appears silent. See §0.4.1 for the canonical recipe. Self-check: `ffprobe -select_streams a -show_entries stream=start_time,nb_frames final.mp4` — `start_time` MUST be ~0.

---

## 13. Artifact masking — never full-frame drawbox

Some clips arrive with generation artifacts (Kling Avatar v2 CJK hallucinations near the bottom of the frame, garbled UI text, etc.). To hide them, the right tool is:

1. **Preferred:** Subtitle ASS box (`BorderStyle=4`, через `--mask` от оркестратора) sized and positioned to cover exactly the artifact region (см. §6.1 для MarginV direction).
2. **Acceptable:** Narrow `drawbox` slightly wider than the artifact bbox (padding ≤ +40 px on each side).
3. **Forbidden:** Full-width `drawbox` covering the entire bottom strip — it crops the picture for no reason and users will reject the result.

Workflow: extract one frame at the artifact's timestamp, measure the artifact bbox, design the mask to cover the bbox + small padding, then re-encode all affected scenes — once.

---

## 14. Speedup is a mandatory step, not optional

The speedup pass (1.15× for serial-drama, 1.18× for comedy-sketch, format-dependent — see format playbook) is part of the standard pipeline order:

> normalize → subtitles → episode number → TBC → concat → **speedup** → music

If `duration(final.mp4) ≈ sum(scene_durations)` exactly, you skipped the speedup. Self-check before handoff:

```bash
EXPECTED=$(echo "scale=2; $SUM_OF_SCENES / $SPEEDUP_FACTOR" | bc)
ACTUAL=$($FFMPEG -i final.mp4 2>&1 | grep Duration | awk '{print $2}')
# ACTUAL should be within ±0.2s of EXPECTED
```

Music mix happens AFTER speedup so the music pitch is not affected.
