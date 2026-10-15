#!/usr/bin/env python3
"""Render a silent MP3 as a base64 data URI: the silent `target_audio_url` of an H3 Max clip.

H3 always writes its own soundtrack and invents speech for a visible face, so silent
characters move their lips. Given a `target_audio_url`, H3 moves the lips to that track;
a silent track of the clip's requested duration keeps the mouth closed (cost trials,
Test 6b). Used on every plain H3 Max clip whose sound is discarded
(`scene_video_audio: "none"`). Deterministic local ffmpeg, no network.

    python3 tools/silent_audio.py --duration 5
    python3 tools/silent_audio.py --duration 5 --out build/video/silence/scene-3.txt

Prints one JSON summary line on success; on failure prints JSON to stderr and exits 1.
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MIN_DURATION = 2.0  # H3 rejects a target audio track shorter than 2 s
MAX_DURATION = 15.0  # H3's longest clip
DURATION_TOLERANCE = 0.1
SAMPLE_RATE = 16000
BITRATE = "16k"
DATA_URI_PREFIX = "data:audio/mpeg;base64,"


class SilentAudioError(Exception):
    pass


def parse_duration(value):
    try:
        duration = float(value)
    except (TypeError, ValueError):
        raise SilentAudioError(f"duration must be a number of seconds, got {value!r}") from None
    if not math.isfinite(duration):
        raise SilentAudioError(f"duration must be a finite number of seconds, got {value!r}")
    if duration < MIN_DURATION or duration > MAX_DURATION:
        raise SilentAudioError(
            f"duration {duration:g}s is outside {MIN_DURATION:g}-{MAX_DURATION:g}s "
            "(H3 needs at least 2 s of target audio and runs at most 15 s)"
        )
    return duration


def build_command(ffmpeg, out, duration):
    return [ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", f"anullsrc=r={SAMPLE_RATE}:cl=mono",
            "-t", f"{duration:.3f}", "-c:a", "libmp3lame", "-b:a", BITRATE, str(out)]


def probe(ffprobe, path):
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration:stream=codec_type,codec_name",
         "-of", "json", str(path)],
        capture_output=True, text=True,
    )
    if result.returncode:
        raise SilentAudioError(result.stderr.strip() or f"ffprobe could not read {path}")
    return json.loads(result.stdout)


def render(duration):
    """Return the bytes of a silent mono MP3 of `duration` seconds."""
    duration = parse_duration(duration)
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise SilentAudioError("ffmpeg and ffprobe are required")
    with tempfile.TemporaryDirectory(prefix="silent-audio-") as tmp:
        mp3 = Path(tmp) / "silence.mp3"
        result = subprocess.run(build_command(ffmpeg, mp3, duration), capture_output=True, text=True)
        if result.returncode:
            raise SilentAudioError(result.stderr.strip().splitlines()[-1] if result.stderr.strip()
                                   else f"ffmpeg exited {result.returncode}")
        meta = probe(ffprobe, mp3)
        streams = meta.get("streams") or []
        audio = [s for s in streams if s.get("codec_type") == "audio"]
        actual = float((meta.get("format") or {}).get("duration") or 0)
        problems = []
        if len(streams) != 1 or len(audio) != 1 or audio[0].get("codec_name") != "mp3":
            problems.append("expected exactly one mp3 audio stream")
        if abs(actual - duration) > DURATION_TOLERANCE:
            problems.append(f"duration {actual:.3f}s, expected {duration:.3f}s")
        if problems:
            raise SilentAudioError("rendered silence failed validation: " + "; ".join(problems))
        return mp3.read_bytes()


def data_uri(data):
    return DATA_URI_PREFIX + base64.b64encode(data).decode("ascii")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Render a silent MP3 data URI for an H3 Max target_audio_url (free, local ffmpeg)")
    parser.add_argument("--duration", required=True,
                        help="seconds, the H3 job's payload duration (the scene's duration_sec); 2-15")
    parser.add_argument("--out", type=Path,
                        help="write only the data URI (no trailing newline) to this file instead of "
                             "printing it inside the JSON; read it into the job with jq --rawfile")
    args = parser.parse_args(argv)
    try:
        duration = parse_duration(args.duration)
        data = render(duration)
        summary = {"ok": True, "duration": duration, "bytes": len(data)}
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(data_uri(data), encoding="ascii")
            summary["out"] = str(args.out)
        else:
            summary["data_uri"] = data_uri(data)
    except (SilentAudioError, OSError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(summary, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
