#!/usr/bin/env python3
"""
Gate: check estimated episode runtime after Sound phase.
Usage: python tools/check_runtime.py --output-dir <path> --format <format>

Measures:
  - dialogue clips: actual TTS duration via ffprobe on scene-K.mp3
  - action clips: declared duration_sec from storyboard.json
Prints breakdown and compares against per-format target range.
Exits 1 if runtime is outside the target range.
"""

import sys
import json
import pathlib
import argparse
import subprocess

# Target runtime ranges in seconds per format slug.
# Adjust as formats evolve — these are the current sweet spots.
FORMAT_RANGES = {
    "serial-drama":      (28, 65),
    "reddit-story":      (40, 95),
    "fun-news":          (28, 60),
    "streettalk":        (25, 55),
    "special-report":    (35, 70),
    "news":              (20, 55),
    "what-if-real-life": (28, 65),
    "redcon":            (28, 65),
    "top-list":          (35, 85),
    "gameplay-ai-avatar":(25, 65),
    "character-story":   (28, 65),
    "in-game-pov":       (25, 60),
    "wild-documentary":  (28, 65),
    "fake-ad":           (15, 45),
    "dual-style":        (20, 50),
    "motion-dance":      (20, 50),
}
DEFAULT_RANGE = (15, 100)


def ffprobe_duration(path):
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=15,
        )
        return float(r.stdout.strip())
    except Exception:
        return None


def clip_index(clip):
    return clip.get("index", clip.get("scene_number", clip.get("id", "?")))


def is_dialogue(clip):
    return (clip.get("clip_type") == "dialogue"
            or clip.get("type") == "dialogue"
            or clip.get("generate_audio") is True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--format", required=True, dest="format_slug")
    args = parser.parse_args()

    output_dir = pathlib.Path(args.output_dir)
    sb_file = output_dir / "storyboard.json"

    if not sb_file.exists():
        print("ERROR: storyboard.json not found", file=sys.stderr)
        sys.exit(1)

    sb = json.loads(sb_file.read_text(encoding="utf-8"))

    # reddit-story flat format: measure tts-output.mp3 directly
    flat_formats = {"reddit-story"}
    if sb.get("format") in flat_formats:
        mp3 = output_dir / "tts-output.mp3"
        lo, hi = FORMAT_RANGES.get(args.format_slug, DEFAULT_RANGE)
        if mp3.exists():
            dur = ffprobe_duration(mp3)
            if dur and dur > 0:
                print(f"Estimated runtime: {dur:.1f}s")
                print(f"Target range [{args.format_slug}]: {lo}–{hi}s")
                print(f"\nBreakdown:\n  tts-output.mp3  {dur:.1f}s")
                if dur < lo:
                    print(f"\nGATE FAILED: runtime {dur:.1f}s is BELOW minimum {lo}s", file=sys.stderr)
                    sys.exit(1)
                elif dur > hi:
                    print(f"\nGATE FAILED: runtime {dur:.1f}s EXCEEDS maximum {hi}s", file=sys.stderr)
                    sys.exit(1)
                else:
                    print(f"\nGATE PASSED: runtime {dur:.1f}s is within [{lo}–{hi}]s")
                return
        print("ERROR: tts-output.mp3 not found — run Sound phase first", file=sys.stderr)
        sys.exit(1)

    clips = sb.get("scenes", sb.get("clips", []))

    total = 0.0
    breakdown = []
    warnings = []

    for clip in clips:
        idx = clip_index(clip)
        declared = float(clip.get("duration_sec", clip.get("duration", 5)))

        if is_dialogue(clip):
            mp3 = output_dir / "scenes" / f"scene-{idx}" / f"scene-{idx}.mp3"
            if mp3.exists():
                dur = ffprobe_duration(mp3)
                if dur and dur > 0:
                    breakdown.append(f"  scene-{idx:>2}  dialogue  TTS={dur:.1f}s  (declared={declared}s)")
                    total += dur
                    if dur > declared + 1.5:
                        warnings.append(
                            f"scene-{idx}: TTS {dur:.1f}s exceeds declared clip duration {declared}s "
                            f"by {dur - declared:.1f}s — consider shortening text or extending clip"
                        )
                    continue
                else:
                    breakdown.append(f"  scene-{idx:>2}  dialogue  TTS=?? (ffprobe failed) → using declared {declared}s")
            else:
                breakdown.append(f"  scene-{idx:>2}  dialogue  mp3 not found → using declared {declared}s")
        else:
            breakdown.append(f"  scene-{idx:>2}  action    {declared}s")

        total += declared

    lo, hi = FORMAT_RANGES.get(args.format_slug, DEFAULT_RANGE)

    print(f"Estimated runtime: {total:.1f}s")
    print(f"Target range [{args.format_slug}]: {lo}–{hi}s")
    print("\nBreakdown:")
    for b in breakdown:
        print(b)

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  ⚠ {w}")

    if total < lo:
        print(
            f"\nGATE FAILED: runtime {total:.1f}s is BELOW minimum {lo}s\n"
            f"  → Ask Scenarist to add a scene or lengthen existing dialogue",
            file=sys.stderr,
        )
        sys.exit(1)
    elif total > hi:
        print(
            f"\nGATE FAILED: runtime {total:.1f}s EXCEEDS maximum {hi}s\n"
            f"  → Ask Scenarist to shorten dialogue or remove a scene",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        print(f"\nGATE PASSED: runtime {total:.1f}s is within [{lo}–{hi}]s")


if __name__ == "__main__":
    main()
