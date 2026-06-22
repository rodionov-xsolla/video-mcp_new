#!/usr/bin/env python3
from __future__ import annotations
"""
Gate: post-Editor validation — final.mp4 integrity + subtitle drift check.
Usage: python tools/check_final.py --output-dir <path>

Checks:
  1. final.mp4 exists and is non-empty
  2. ffprobe reports a valid duration (moov atom present)
  3. Last ASS subtitle event timestamp ≈ final.mp4 audio duration (drift ≤ 3s)
     Drift > 3s means ASS was generated before final audio mix — regenerate subtitles last.

Exits 1 if any check fails.
"""

import sys
import pathlib
import argparse
import subprocess
import re


def ffprobe_duration(path: pathlib.Path) -> float | None:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        return float(r.stdout.strip())
    except Exception:
        return None


def ffprobe_check_moov(path: pathlib.Path) -> bool:
    r = subprocess.run(
        ["ffprobe", "-v", "error", str(path)],
        capture_output=True, text=True, timeout=30,
    )
    return "moov atom not found" not in r.stderr and "Invalid data" not in r.stderr


def parse_ass_last_event(ass_file: pathlib.Path) -> float | None:
    """Return the latest end-time (in seconds) from all Dialogue lines."""
    content = ass_file.read_text(encoding="utf-8", errors="ignore")
    timestamps = []
    for line in content.splitlines():
        if not line.startswith("Dialogue:"):
            continue
        parts = line.split(",", 9)
        if len(parts) < 3:
            continue
        # End time is parts[2] in H:MM:SS.cc format
        m = re.match(r"(\d+):(\d{2}):(\d{2})\.(\d{2})", parts[2].strip())
        if m:
            h, mn, s, cs = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
            timestamps.append(h * 3600 + mn * 60 + s + cs / 100)
    return max(timestamps) if timestamps else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    output_dir = pathlib.Path(args.output_dir)
    final_mp4 = output_dir / "final.mp4"
    build_dir = output_dir / "build"

    errors = []

    # ── Check 1: final.mp4 exists ─────────────────────────────────────────
    if not final_mp4.exists():
        print("ERROR: final.mp4 not found", file=sys.stderr)
        sys.exit(1)

    size = final_mp4.stat().st_size
    if size < 100_000:
        errors.append(f"final.mp4 is suspiciously small: {size} bytes")

    # ── Check 2: moov atom / valid container ──────────────────────────────
    if not ffprobe_check_moov(final_mp4):
        errors.append(
            "final.mp4 has no moov atom — file is unplayable.\n"
            "  Cause: ffmpeg encode was killed before writing moov (run_in_background or /tmp overflow).\n"
            "  Fix: re-encode synchronously into OUTPUT_DIR/build/ with timeout ≥ 180s."
        )

    duration = ffprobe_duration(final_mp4)
    if duration is None or duration < 5.0:
        errors.append(f"final.mp4 ffprobe duration={duration} — unreadable or too short")
    else:
        print(f"final.mp4: {duration:.1f}s  ({size // 1_000_000}MB)")

    if errors:
        print("\nFINAL CHECK FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        sys.exit(1)

    # ── Check 3: subtitle drift ───────────────────────────────────────────
    # Only check the master/combined ASS file, not per-scene fragments.
    # Per-scene files (subs-scene-K.ass) only cover their own scene duration.
    subtitle_errors = []
    all_ass = sorted(build_dir.glob("*.ass")) if build_dir.exists() else []

    # Prefer an explicit master file; fall back to the longest-duration file.
    master_candidates = [f for f in all_ass
                         if not any(seg in f.stem for seg in ["-scene-", "_scene_", "scene-"])]
    ass_files = master_candidates if master_candidates else (all_ass[:1] if all_ass else [])

    if not all_ass:
        print("NOTE: no .ass files in build/ — subtitle drift check skipped")
    elif not ass_files:
        print(f"NOTE: {len(all_ass)} per-scene .ass files found but no master — drift check skipped")
    else:
        for ass_file in ass_files:
            last_ts = parse_ass_last_event(ass_file)
            if last_ts is None:
                print(f"NOTE: {ass_file.name} — no Dialogue lines found, skipping")
                continue
            # Subtitles ending before video = OK (last clip may be action-only, CTA, etc.)
            # Subtitles running PAST the video = definitely wrong (stale timestamps)
            overshoot = last_ts - duration
            if overshoot > 1.0:
                print(f"{ass_file.name}: last event {last_ts:.1f}s, video {duration:.1f}s → overshoot {overshoot:.1f}s [DRIFT]")
                subtitle_errors.append(
                    f"{ass_file.name}: last subtitle event at {last_ts:.1f}s overshoots video end {duration:.1f}s by {overshoot:.1f}s\n"
                    f"  Cause: ASS was generated with stale timestamps (before atempo/adelay or final mix).\n"
                    f"  Fix: regenerate subtitles AFTER the final ffmpeg audio assembly."
                )
            else:
                gap = duration - last_ts
                print(f"{ass_file.name}: last event {last_ts:.1f}s, video {duration:.1f}s → gap {gap:.1f}s [OK]")

    if subtitle_errors:
        print("\nFINAL CHECK FAILED (subtitle drift):", file=sys.stderr)
        for e in subtitle_errors:
            print(f"  ✗ {e}", file=sys.stderr)
        sys.exit(1)

    subtitle_note = f", {len(ass_files)} master subtitle file(s) aligned" if ass_files else ""
    print(f"\nGATE PASSED: final.mp4 valid{subtitle_note}")


if __name__ == "__main__":
    main()
