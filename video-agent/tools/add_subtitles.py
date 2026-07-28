#!/usr/bin/env python3
from __future__ import annotations
"""
Unified ASS subtitle generator for the video pipeline.

ONE universal style for ALL formats. No per-format presets, masks, secondary-style,
marginv overrides, offset/atempo. By design — subtitles must look identical in every video.

TWO PRINCIPLES (breaking either = back to the old chaos):

  1. Whisper provides TIMECODES ONLY. The on-screen text is the canonical text from
     storyboard.json (exactly what Sound voiced). The whisper transcript can hallucinate /
     misspell words (especially Chatterbox clones) — we do NOT show it. Canonical words are
     aligned to the whisper timings (forced alignment, difflib + interpolation).

  2. Whisper runs on the FINAL mixed voice track (build/voice-final.wav — post-atempo,
     post-adelay, post-concat, pre-bg-music). Then the timings are correct BY CONSTRUCTION:
     there is no second timeline to drift against. That is why offset/atempo/verify-audio
     are no longer needed and have been removed.

UNIVERSAL STYLE:
    Helvetica Bold 72, UPPERCASE, white text + 6px black outline, bottom-center,
    MarginV=520 (~27% from the bottom, above TikTok/Reels/Shorts UI), MarginL/R=100
    (anti-overflow). 4-word chunks. WrapStyle=0 wraps a long chunk into 2 balanced lines.

CHUNKING RULES (strict):
    1. Sentence boundary is hard: a chunk never contains the end of one sentence and the
       start of the next (split text into sentences on .!?…, chunk within each).
    2. target = 4 words.
    3. No orphan single word: at least 2 words per chunk (rebalance within the sentence,
       5 words = 3+2, not 4+1). Exception — a one-word sentence.

Usage:
  # Canonical call from the editor pipeline:
  python3 add_subtitles.py build/voice-final.wav build/subs.ass \\
      --storyboard storyboard.json --lang en --main-dur 44.96

  # Timings JSON only (optional, whisper-based):
  python3 add_subtitles.py build/voice-final.wav out.timings.json \\
      --emit-timings --storyboard storyboard.json

Stdout: path of the output file. Stderr: progress.
FFMPEG: located across several paths (used for ffprobe duration).
"""

import argparse
import difflib
import json
import math
import os
import re
import string
import subprocess
import sys

# ---------------------------------------------------------------------------
# FFmpeg locator (only needed for ffprobe duration)
# ---------------------------------------------------------------------------

FFMPEG = "/usr/local/bin/ffmpeg-full/ffmpeg"
if not os.path.isfile(FFMPEG):
    for _alt in [
        "/opt/homebrew/Cellar/ffmpeg-full/8.1.1/bin/ffmpeg",
        "/opt/homebrew/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
    ]:
        if os.path.isfile(_alt):
            FFMPEG = _alt
            break


# ---------------------------------------------------------------------------
# THE one universal style (PrimaryColour etc. in BGR &HAABBGGRR)
# ---------------------------------------------------------------------------

UNIVERSAL_STYLE = {
    "name": "Default",
    "fontname": "Helvetica",
    "fontsize": 72,             # reduced from 84 — a 4-word CAPS chunk fits within marginl/r=100
    "primary": "&H00FFFFFF",    # white
    "secondary": "&H000000FF",
    "outline_col": "&H00000000",  # black
    "back": "&H00000000",
    "bold": 1,
    "italic": 0,
    "underline": 0,
    "strike": 0,
    "scalex": 100,
    "scaley": 100,
    "spacing": 0,
    "angle": 0,
    "borderstyle": 1,           # 1 = outline + drop shadow (NOT an opaque box)
    "outline": 6,
    "shadow": 0,
    "alignment": 2,             # bottom-center
    "marginl": 100,
    "marginr": 100,
    "marginv": 520,             # ~27% from the bottom of 1920 — above TikTok/Reels/Shorts UI
    "encoding": 1,
}

CHUNK_TARGET = 4

# Sentence-ending punctuation (hard chunk boundary)
SENT_END = set(".!?…")
# Inner punctuation — preferred (soft) break
INNER_PUNCT = set(",;:—")


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def strip_outer_punct(word: str) -> str:
    """Strip surrounding punctuation, keeping apostrophes inside the word."""
    return word.strip(string.punctuation + "—–«»“”‘’")


def norm_token(word: str) -> str:
    """Normalize for matching: lowercase without surrounding punctuation."""
    return strip_outer_punct(word).lower()


def get_duration(path: str) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path],
        text=True,
    )
    out = out.strip()
    try:
        return float(out)
    except ValueError:
        import json as _json
        return float(_json.loads(out)["format"]["duration"])


def fmt_ass_time(sec: float) -> str:
    if sec < 0:
        sec = 0.0
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"


# ---------------------------------------------------------------------------
# Canonical text from storyboard.json
#   single-voice: top-level .tts.full_text (or string .tts)
#   multi-voice:  .scenes[].tts / .clips[].tts in index order (skip null)
# ---------------------------------------------------------------------------

def canonical_text_from_storyboard(sb_path: str) -> str:
    with open(sb_path, encoding="utf-8") as f:
        sb = json.load(f)

    # single-voice: one monologue for the whole video
    tts = sb.get("tts")
    if isinstance(tts, dict) and tts.get("full_text", "").strip():
        return tts["full_text"].strip()
    if isinstance(tts, str) and tts.strip():
        return tts.strip()

    # multi-voice: collect scene lines in index order
    arr = sb.get("scenes") or sb.get("clips") or []
    arr = sorted(arr, key=lambda x: x.get("index", 0))
    parts = []
    for s in arr:
        t = s.get("tts") or s.get("character_speech") or s.get("narration")
        if not t:
            continue
        # character_speech can be a plain string ("line") or a list of
        # {"speaker": ..., "line": ...} dicts (serial-drama multi-speaker I2V
        # dialogue clips). str(list_of_dicts) would stringify the Python repr
        # ("SPEAKER LUMINE LINE DON'T STOP...") straight into the subtitle
        # track — extract just the spoken "line" text, in order, instead.
        if isinstance(t, list):
            lines = []
            for item in t:
                if isinstance(item, dict):
                    line = str(item.get("line", "")).strip()
                else:
                    line = str(item).strip()
                if line:
                    lines.append(line)
            t = " ".join(lines)
        if t and str(t).strip() and str(t).strip().lower() != "null":
            parts.append(str(t).strip())
    return " ".join(parts)


def lang_from_storyboard(sb_path: str) -> str:
    """Whisper language from storyboard: tts.language_code or top-level language. First 2 letters."""
    try:
        with open(sb_path, encoding="utf-8") as f:
            sb = json.load(f)
    except Exception:
        return "en"
    tts = sb.get("tts")
    code = ""
    if isinstance(tts, dict):
        code = tts.get("language_code", "") or ""
    code = code or sb.get("language", "") or "en"
    return (code[:2] or "en").lower()


# ---------------------------------------------------------------------------
# Whisper — TIMECODES ONLY (transcript text is not shown)
# ---------------------------------------------------------------------------

def whisper_words(audio_path: str, lang: str) -> list[tuple[float, float, str]]:
    print(f"  [whisper] transcribing {os.path.basename(audio_path)} (timings only) ...",
          file=sys.stderr)
    from faster_whisper import WhisperModel
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, word_timestamps=True, language=lang)
    words = []
    for seg in segments:
        for w in seg.words:
            words.append((w.start, w.end, w.word.strip()))
    print(f"  [whisper] {len(words)} words", file=sys.stderr)
    return words


# ---------------------------------------------------------------------------
# Forced alignment: canonical words <- whisper timings
# ---------------------------------------------------------------------------

def force_align(
    canon_tokens: list[str],
    w_words: list[tuple[float, float, str]],
    total_dur: float,
) -> tuple[list[tuple[float, float]], float]:
    """Returns (timings, ratio): timings[i] = (start,end) for canon_tokens[i];
    ratio is the fraction of matched canonical words (used to warn about divergence).
    """
    n = len(canon_tokens)
    timings: list[tuple[float, float] | None] = [None] * n

    if not w_words:
        # No timings at all — distribute evenly over total_dur (last resort)
        if n:
            step = total_dur / n
            timings = [(i * step, (i + 1) * step) for i in range(n)]
        return [t for t in timings], 0.0

    c_norm = [norm_token(t) for t in canon_tokens]
    w_norm = [norm_token(w[2]) for w in w_words]

    sm = difflib.SequenceMatcher(a=c_norm, b=w_norm, autojunk=False)
    matched = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                ws = w_words[j1 + k]
                timings[i1 + k] = (ws[0], ws[1])
                matched += 1
        else:
            # canon[i1:i2] maps to whisper[j1:j2] (either side may be empty)
            cnt = i2 - i1
            if cnt <= 0:
                continue
            if j2 > j1:
                span_s = w_words[j1][0]
                span_e = w_words[j2 - 1][1]
                step = (span_e - span_s) / cnt if cnt else 0.0
                for k in range(cnt):
                    timings[i1 + k] = (span_s + k * step, span_s + (k + 1) * step)
            # if the whisper side is empty — leave None, fill by interpolation below

    # Fill the remaining None by interpolation between known neighbors
    _fill_none(timings, total_dur)
    # Monotonicity
    _enforce_monotonic(timings)

    ratio = matched / n if n else 1.0
    return [t for t in timings], ratio


def _fill_none(timings: list, total_dur: float) -> None:
    n = len(timings)
    # first known
    first = next((i for i in range(n) if timings[i] is not None), None)
    if first is None:
        # nothing at all — distribute evenly
        step = total_dur / n if n else 0.0
        for i in range(n):
            timings[i] = (i * step, (i + 1) * step)
        return
    # leading run of None
    if first > 0:
        s0 = timings[first][0]
        step = s0 / (first + 1) if first else 0.0
        for i in range(first):
            timings[i] = (i * step, (i + 1) * step)
    # interior / trailing
    i = first
    while i < n:
        if timings[i] is not None:
            i += 1
            continue
        # gap [i .. j-1]
        j = i
        while j < n and timings[j] is None:
            j += 1
        left_end = timings[i - 1][1]
        right_start = timings[j][0] if j < n else total_dur
        cnt = j - i
        step = (right_start - left_end) / cnt if cnt else 0.0
        for k in range(cnt):
            timings[i + k] = (left_end + k * step, left_end + (k + 1) * step)
        i = j


def _enforce_monotonic(timings: list) -> None:
    prev_e = 0.0
    for i, (s, e) in enumerate(timings):
        s = max(s, prev_e)
        e = max(e, s)
        timings[i] = (s, e)
        prev_e = e


# ---------------------------------------------------------------------------
# Chunking (strict rules)
# ---------------------------------------------------------------------------

def split_sentences(tokens: list[str]) -> list[list[int]]:
    """Token indices grouped by sentence (boundary on .!?…)."""
    sentences: list[list[int]] = []
    cur: list[int] = []
    for idx, tok in enumerate(tokens):
        cur.append(idx)
        if tok and tok[-1] in SENT_END:
            sentences.append(cur)
            cur = []
    if cur:
        sentences.append(cur)
    return sentences


def chunk_sentence(sent_idxs: list[int], target: int) -> list[list[int]]:
    """Split ONE sentence into chunks. Guarantees: no 1-word chunk (unless the whole
    sentence is a single word); balanced sizes; <= ~target.
    """
    n = len(sent_idxs)
    if n <= 1:
        return [sent_idxs]               # single word — unavoidable
    if n <= target:
        return [sent_idxs]               # fits in one chunk (>=2 words)

    # k = minimum number of chunks so each is <= target.
    # For target=4 this always yields sizes >=2 (no orphan possible).
    k = math.ceil(n / target)
    base, rem = divmod(n, k)
    sizes = [base + (1 if i < rem else 0) for i in range(k)]
    # safety: if some size ends up 1, reduce k
    while k > 1 and min(sizes) < 2:
        k -= 1
        base, rem = divmod(n, k)
        sizes = [base + (1 if i < rem else 0) for i in range(k)]

    out: list[list[int]] = []
    p = 0
    for s in sizes:
        out.append(sent_idxs[p:p + s])
        p += s
    return out


def build_chunks(tokens: list[str], target: int) -> list[list[int]]:
    chunks: list[list[int]] = []
    for sent in split_sentences(tokens):
        chunks.extend(chunk_sentence(sent, target))
    return chunks


# ---------------------------------------------------------------------------
# ASS building
# ---------------------------------------------------------------------------

def _style_line(style: dict) -> str:
    return (
        f"Style: {style['name']},{style['fontname']},{style['fontsize']},"
        f"{style['primary']},{style['secondary']},{style['outline_col']},{style['back']},"
        f"{style['bold']},{style['italic']},{style['underline']},{style['strike']},"
        f"{style['scalex']},{style['scaley']},{style['spacing']},{style['angle']},"
        f"{style['borderstyle']},{style['outline']},{style['shadow']},"
        f"{style['alignment']},{style['marginl']},{style['marginr']},{style['marginv']},"
        f"{style['encoding']}"
    )


def build_ass(events: list[tuple[float, float, str]]) -> str:
    header_lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        ("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
         "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
         "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
         "Alignment, MarginL, MarginR, MarginV, Encoding"),
        _style_line(UNIVERSAL_STYLE),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    out = ["\n".join(header_lines)]
    for start, end, text in events:
        out.append(
            f"Dialogue: 0,{fmt_ass_time(start)},{fmt_ass_time(end)},"
            f"{UNIVERSAL_STYLE['name']},,0,0,0,,{text}"
        )
    return "\n".join(out) + "\n"


def assemble_events(
    canon_tokens: list[str],
    timings: list[tuple[float, float]],
    chunks: list[list[int]],
    voice_dur: float,
    main_dur: float | None,
) -> list[tuple[float, float, str]]:
    """Chunks -> ASS events. Dense pulse (chunk end = next chunk start).
    The last event is clamped to main_dur (or voice_dur)."""
    events: list[tuple[float, float, str]] = []
    n = len(chunks)
    cap = main_dur if main_dur is not None else voice_dur
    for j, group in enumerate(chunks):
        start = timings[group[0]][0]
        if j + 1 < n:
            end = timings[chunks[j + 1][0]][0]
        else:
            end = min(timings[group[-1]][1], cap)
        # display: UPPERCASE, without surrounding punctuation
        words = [strip_outer_punct(canon_tokens[i]) for i in group]
        text = " ".join(w for w in words if w).upper()
        if not text:
            continue
        # main_dur clamp: drop events entirely past the boundary, trim overlapping ones
        if main_dur is not None:
            if start >= main_dur:
                continue
            end = min(end, main_dur)
        if end <= start:
            end = start + 0.30
        events.append((start, end, text))
    return events


# ---------------------------------------------------------------------------
# Timings JSON (optional mode, whisper-based, no --text)
# ---------------------------------------------------------------------------

def emit_timings_json(out_path: str, text: str, duration: float,
                      words: list[tuple[float, float, str]]) -> None:
    payload = {
        "duration_s": round(duration, 3),
        "text": text,
        "words": [
            {"text": w, "start": round(s, 3), "end": round(e, 3)}
            for (s, e, w) in words
        ],
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    # 2 positionals (audio, output) or legacy 3 (video, audio, output)
    ap.add_argument("paths", nargs="+",
                    help="audio output  (or legacy: video audio output)")
    ap.add_argument("--storyboard", default=None,
                    help="path to storyboard.json — source of the CANONICAL text (required for burn)")
    ap.add_argument("--lang", default=None, help="whisper language (default: from storyboard language_code)")
    ap.add_argument("--main-dur", type=float, default=None,
                    help="end of the last story clip (before CTA) — subtitle clamp")
    ap.add_argument("--emit-ass-only", action="store_true",
                    help="ASS only (canonical mode; default when output is .ass)")
    ap.add_argument("--emit-timings", action="store_true",
                    help="timings JSON only (whisper-based, optional)")
    ap.add_argument("--min-align-ratio", type=float, default=0.5,
                    help="forced-alignment threshold: below it -> exit 1 (guards against wrong audio/language)")
    args = ap.parse_args()

    # ---- positionals: support the legacy 3-arg call -----------------------
    pos = args.paths
    if len(pos) == 3:
        # legacy: first arg is the video ('-' or a path), drop it
        if pos[0] == "-" or os.path.exists(pos[0]):
            print(f"  [compat] dropping legacy video argument '{pos[0]}'", file=sys.stderr)
            audio, output = pos[1], pos[2]
        else:
            audio, output = pos[1], pos[2]
    elif len(pos) == 2:
        audio, output = pos[0], pos[1]
    else:
        print("ERROR: expected 2 positional arguments: <audio> <output>", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(audio):
        print(f"ERROR: audio not found: {audio}", file=sys.stderr)
        sys.exit(1)

    voice_dur = get_duration(audio)

    # ---- GUARD voice-final.wav: duration must be ~ MAIN_DUR (the picture track) ----
    # The most common multi-voice voice-final build bug: lines glued back-to-back WITHOUT
    # silence under the silent/action scenes -> the track is far shorter than the picture ->
    # subtitles drift in absolute time. Whisper aligns words to the audio, but audio != video
    # timeline. Catch it here.
    if args.main_dur is not None and not args.emit_timings:
        if voice_dur < args.main_dur * 0.6:
            print(f"ERROR: voice-final ({voice_dur:.1f}s) is far shorter than MAIN_DUR "
                  f"({args.main_dur:.1f}s). Looks like build/voice-final.wav was assembled without the "
                  f"silence under the silent/action scenes — subtitles will drift in absolute time. "
                  f"Rebuild voice-final as [aout] minus bg-music (editor.md §6.1).",
                  file=sys.stderr)
            sys.exit(1)
        if voice_dur > args.main_dur + 1.0:
            print(f"  [warn] voice-final ({voice_dur:.1f}s) is longer than MAIN_DUR ({args.main_dur:.1f}s) — "
                  f"the last words will be clamped. Tune atempo so the speech fits the picture.",
                  file=sys.stderr)

    # ---- whisper language: explicit --lang, else from storyboard, else en --------
    lang = args.lang or (lang_from_storyboard(args.storyboard) if args.storyboard else "en")
    print(f"  [lang] whisper language = {lang}", file=sys.stderr)

    # ---- timings-only mode (optional) -------------------------------------
    if args.emit_timings:
        words = whisper_words(audio, lang)
        text = canonical_text_from_storyboard(args.storyboard) if args.storyboard else \
            " ".join(w for (_, _, w) in words)
        emit_timings_json(output, text, voice_dur, words)
        print(f"  [timings] {output} ({len(words)} words)", file=sys.stderr)
        print(output)
        return

    # ---- canonical text ---------------------------------------------------
    if not args.storyboard:
        print("ERROR: --storyboard is required for the burn (text source)", file=sys.stderr)
        sys.exit(1)
    canon_text = canonical_text_from_storyboard(args.storyboard)
    if not canon_text.strip():
        # No lines anywhere in the video — empty ASS (burn = no-op)
        with open(output, "w", encoding="utf-8") as f:
            f.write(build_ass([]))
        print("  [subs] canonical text empty — empty ASS", file=sys.stderr)
        print(output)
        return

    canon_tokens = [t for t in re.split(r"\s+", canon_text.strip()) if t]

    # ---- whisper timings + forced alignment -------------------------------
    w_words = whisper_words(audio, lang)
    timings, ratio = force_align(canon_tokens, w_words, voice_dur)
    if ratio < args.min_align_ratio:
        print(f"ERROR: forced-alignment ratio {ratio:.2f} < {args.min_align_ratio:.2f} — "
              f"the whisper transcript diverged badly from the canonical text. Likely causes: wrong "
              f"language (currently lang={lang} — check storyboard language_code), wrong audio in "
              f"voice-final.wav, or music/noise in the track. Fix the source, not the threshold. "
              f"(Deliberately lower it via --min-align-ratio.)", file=sys.stderr)
        sys.exit(1)
    print(f"  [align] ratio {ratio:.2f} OK ({len(canon_tokens)} canonical words)",
          file=sys.stderr)

    # ---- chunking ---------------------------------------------------------
    chunks = build_chunks(canon_tokens, CHUNK_TARGET)

    # ---- events + clamp ---------------------------------------------------
    events = assemble_events(canon_tokens, timings, chunks, voice_dur, args.main_dur)

    # sanity: the last word should not extend past audio + 50ms
    if timings:
        last_end = timings[-1][1]
        if last_end > voice_dur + 0.05:
            print(f"  [warn] last word ends at {last_end:.2f}s > audio {voice_dur:.2f}s "
                  f"(whisper may have rounded up).", file=sys.stderr)

    ass = build_ass(events)
    with open(output, "w", encoding="utf-8") as f:
        f.write(ass)
    print(f"  [subs] {output}: {len(events)} events, {len(chunks)} chunks, "
          f"style=universal(72,CAPS,mv520)", file=sys.stderr)
    print(output)


# ===========================================================================
# === LEGACY (dead path, never invoked) =====================================
# Kept for history / possible revert. NOT called from main().
# The old proportional text-based timing (the source of "drift"), karaoke,
# and second-speaker are deliberately disabled by an architectural decision.
# ===========================================================================

_MIN_WORD_S = 0.15
_MAX_WORD_S = 0.60


def _legacy_proportional_timings(text: str, duration: float):
    """LEGACY. Proportional timings from text (NO whisper). Do not use — does not land
    on the real pauses, was a source of desync."""
    raw_tokens = [t for t in re.split(r"\s+", text.strip()) if t]
    if not raw_tokens:
        return []
    weights = [max(1, len(strip_outer_punct(tok))) for tok in raw_tokens]
    total_w = sum(weights)
    durs = [duration * w / total_w for w in weights]
    durs = [max(_MIN_WORD_S, min(_MAX_WORD_S, d)) for d in durs]
    scale = duration / sum(durs)
    durs = [d * scale for d in durs]
    out, cursor = [], 0.0
    for tok, d in zip(raw_tokens, durs):
        out.append((cursor, cursor + d, tok))
        cursor += d
    if out:
        s, _, w = out[-1]
        out[-1] = (s, duration, w)
    return out


def _legacy_apply_highlight_words(chunk_clean, chunk_orig, chunk_start, highlight_color):
    """LEGACY. Karaoke word-by-word highlight (\\kf). Disabled — one flat white style."""
    word_durs_cs = [max(5, int(round((we - ws) * 100))) for (ws, we, _) in chunk_orig]
    parts = [f"{{\\2c&H{highlight_color}&}}"]
    for word, cs in zip(chunk_clean, word_durs_cs):
        if word:
            parts.append(f"{{\\kf{cs}}}{word} ")
    return "".join(parts).rstrip()


def _legacy_parse_secondary_style(spec, base):
    """LEGACY. Second speaker style. Disabled — all speech in one style."""
    name, _, rest = spec.partition("=")
    parts = [p.strip() for p in rest.split(",")]
    return dict(base, name=name.strip())


if __name__ == "__main__":
    main()
