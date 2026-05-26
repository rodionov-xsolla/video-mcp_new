#!/usr/bin/env python3
"""
Add audio-synced subtitles to a video using faster-whisper + ASS.

Chunks text into groups of N words timed to actual speech.
Most chunks are plain white. Scenarist-marked phrases appear yellow+italic
only in the chunk(s) where they occur.

Usage:
  python3 add_subtitles.py <video.mp4> <audio.mp3> <output.mp4|output.ass> [options]

  When `output` ends with `.ass` OR `--emit-ass-only` is passed, the script
  emits only the ASS file and exits — no ffmpeg burn-in. This is the path used
  by the editor canonical single-pass pipeline (editor.md §0), which burns
  subtitles in via the `ass=` filter inside its own filter_complex.

Options:
  --emit-ass-only            emit ASS only; skip ffmpeg burn-in. Implied when
                             the output path ends in .ass. Use with the canonical
                             editor pipeline.
  --chunk N                  words per chunk (default: 3)
  --emphasis "phrase1,..."   comma-separated phrases to highlight (case-insensitive)
  --fontsize N               base font size in px (default: 72)
  --marginv N                bottom margin in px (default: 200)
  --lang CODE                whisper language hint (default: en)
  --no-scale                 skip scale/pad to 1080x1920 (legacy burn-in only)
  --tbc                      append TO BE CONTINUED... after last chunk
  --color AABBGGRR           highlight color in ASS hex (default: 0000FFFF = yellow)
  --duration SECS            override clip duration in seconds. Required when
                             --emit-ass-only is used without a video file
                             (pass "-" or any string as video arg, then --duration).
                             The last chunk extends to this duration.
  --atempo N.NN              audio will be sped up by this factor in editor;
                             whisper runs on the original mp3 but ASS timestamps
                             are divided by atempo so subs stay in sync after speedup
                             (cap 1.5× — voice quality degrades above)
  --start-offset SECS        shift all ASS timestamps by SECS forward. Use when
                             the canonical pipeline will apply `adelay` after
                             atempo — pass the adelay in seconds so the ASS
                             aligns with the audio's final position.

Stdout: output file path. Stderr: progress logs.
FFMPEG: /usr/local/bin/ffmpeg-full/ffmpeg  (tessus build, requires libass)
"""

import argparse
import subprocess
import sys
import os
import re
import string

FFMPEG = "/usr/local/bin/ffmpeg-full/ffmpeg"


def strip_punct(word: str) -> str:
    return word.strip(string.punctuation + "—–''")


def transcribe(mp3_path: str, lang: str) -> list[tuple[float, float, str]]:
    from faster_whisper import WhisperModel
    print(f"  [whisper] transcribing {os.path.basename(mp3_path)} ...", file=sys.stderr)
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(mp3_path, word_timestamps=True, language=lang)
    words = []
    for seg in segments:
        for w in seg.words:
            words.append((w.start, w.end, w.word.strip()))
    print(f"  [whisper] {len(words)} words", file=sys.stderr)
    return words


def chunk_words(words: list, chunk_size: int, clip_dur: float) -> list[tuple[float, float, list[str]]]:
    """Group into chunks; each chunk ends when the next starts."""
    chunks = []
    for i in range(0, len(words), chunk_size):
        group = words[i:i + chunk_size]
        clean = [strip_punct(w[2]) for w in group]
        start = group[0][0]
        chunks.append((start, clean))

    result = []
    for j, (start, clean) in enumerate(chunks):
        end = chunks[j + 1][0] if j + 1 < len(chunks) else clip_dur
        result.append((start, end, clean))
    return result


def apply_emphasis(chunk_text: str, phrases: list[str], color: str, kw_fs: int) -> str:
    """Wrap emphasis phrases in ASS inline tags.
    Tries full phrase first; if it spans chunk boundary, falls back to
    matching individual words of the phrase."""
    tag_open = f"{{\\c&H{color}&\\i1\\fs{kw_fs}}}"
    tag_close = "{\\r}"
    for phrase in phrases:
        # Try full phrase
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        if pattern.search(chunk_text):
            chunk_text = pattern.sub(
                lambda m: f"{tag_open}{m.group(0)}{tag_close}",
                chunk_text, count=1
            )
        else:
            # Fall back: highlight each word of the phrase that appears in this chunk
            for word in phrase.split():
                wp = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                if wp.search(chunk_text):
                    chunk_text = wp.sub(
                        lambda m: f"{tag_open}{m.group(0)}{tag_close}",
                        chunk_text, count=1
                    )
    return chunk_text


def fmt_ass_time(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def build_ass(chunks: list, base_fs: int, marginv: int,
              emphasis: list[str], color: str, tbc: bool) -> str:
    kw_fs = base_fs + 14

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Bold,{base_fs},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,8,0,2,10,10,{marginv},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"""

    lines = [header]
    for start, end, clean_words in chunks:
        text = " ".join(w for w in clean_words if w)
        if emphasis:
            text = apply_emphasis(text, emphasis, color, kw_fs)
        lines.append(
            f"Dialogue: 0,{fmt_ass_time(start)},{fmt_ass_time(end)},Default,,0,0,0,,{text}"
        )

    if tbc and chunks:
        tbc_start = chunks[-1][1]
        lines.append(
            f"Dialogue: 0,{fmt_ass_time(tbc_start)},{fmt_ass_time(tbc_start + 3.0)},Default,,0,0,0,,TO BE CONTINUED..."
        )

    return "\n".join(lines) + "\n"


def get_duration(path: str) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path],
        text=True
    )
    return float(out.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("audio")
    ap.add_argument("output")
    ap.add_argument("--chunk", type=int, default=3)
    ap.add_argument("--emphasis", default="")
    ap.add_argument("--fontsize", type=int, default=72)
    ap.add_argument("--marginv", type=int, default=380)
    ap.add_argument("--lang", default="en")
    ap.add_argument("--no-scale", action="store_true")
    ap.add_argument("--tbc", action="store_true")
    ap.add_argument("--color", default="0000FFFF")
    ap.add_argument("--atempo", type=float, default=1.0,
                    help="audio speedup factor in editor; ASS timestamps divided by this")
    ap.add_argument("--emit-ass-only", action="store_true",
                    help="emit ASS only, skip ffmpeg burn-in (canonical pipeline mode)")
    ap.add_argument("--duration", type=float, default=None,
                    help="override clip duration in seconds; required with --emit-ass-only when no video file is given")
    ap.add_argument("--start-offset", type=float, default=0.0,
                    help="shift all timestamps forward by SECS (use with canonical pipeline adelay)")
    args = ap.parse_args()

    if args.atempo < 1.0 or args.atempo > 1.5:
        print(f"ERROR: --atempo must be in [1.0, 1.5], got {args.atempo}", file=sys.stderr)
        sys.exit(1)

    # Auto-detect ass-only mode from output extension
    ass_only = args.emit_ass_only or args.output.lower().endswith(".ass")

    emphasis = [p.strip() for p in args.emphasis.split(",") if p.strip()] if args.emphasis else []

    if args.duration is not None:
        clip_dur = float(args.duration)
    elif ass_only and (args.video == "-" or not os.path.exists(args.video)):
        print("ERROR: --emit-ass-only without a video file requires --duration SECS", file=sys.stderr)
        sys.exit(1)
    else:
        clip_dur = get_duration(args.video)
    words = transcribe(args.audio, args.lang)
    if not words:
        print("ERROR: no words detected", file=sys.stderr)
        sys.exit(1)

    if args.atempo != 1.0:
        words = [(s / args.atempo, e / args.atempo, w) for (s, e, w) in words]
        print(f"  [atempo] timestamps scaled by 1/{args.atempo:.3f}", file=sys.stderr)

    if args.start_offset != 0.0:
        off = args.start_offset
        words = [(s + off, e + off, w) for (s, e, w) in words]
        print(f"  [offset] timestamps shifted by +{off:.2f}s", file=sys.stderr)

    chunks = chunk_words(words, args.chunk, clip_dur)
    print(f"  [subtitles] {len(chunks)} chunks:", file=sys.stderr)
    for s, e, ws in chunks:
        print(f"    {s:.2f}→{e:.2f}  {' '.join(ws)}", file=sys.stderr)

    ass_content = build_ass(chunks, args.fontsize, args.marginv, emphasis, args.color, args.tbc)

    if ass_only:
        ass_path = args.output if args.output.lower().endswith(".ass") else args.output + ".ass"
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(ass_content)
        print(f"  [ass-only] wrote {ass_path} ({len(chunks)} chunks)", file=sys.stderr)
        print(ass_path)
        return

    ass_path = args.output.replace(".mp4", ".ass")
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)

    scale_filter = "" if args.no_scale else \
        "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,"
    vf = f"{scale_filter}subtitles={ass_path}"

    tmp_output = args.output + ".tmp.mp4"
    cmd = [FFMPEG, "-y", "-i", args.video, "-vf", vf,
           "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-c:a", "copy",
           tmp_output]

    print("  [ffmpeg] rendering ...", file=sys.stderr)
    log_path = args.output.replace(".mp4", ".ffmpeg.log")
    with open(log_path, "w") as log_f:
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=log_f)
    if result.returncode != 0:
        with open(log_path) as f:
            lines = f.readlines()
        print("".join(lines[-40:]), file=sys.stderr)
        if os.path.exists(tmp_output):
            os.remove(tmp_output)
        sys.exit(1)

    # Validate: output duration must match input within 0.5s.
    try:
        out_dur = get_duration(tmp_output)
    except Exception as e:
        print(f"ERROR: ffprobe failed on rendered output ({e}) — likely truncated/no moov", file=sys.stderr)
        os.remove(tmp_output)
        sys.exit(1)
    if abs(out_dur - clip_dur) > 0.5:
        print(f"ERROR: output duration {out_dur:.2f}s != input {clip_dur:.2f}s — encode was killed mid-stream", file=sys.stderr)
        os.remove(tmp_output)
        sys.exit(1)

    os.replace(tmp_output, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
