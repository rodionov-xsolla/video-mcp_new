#!/usr/bin/env python3
"""Render a still-shot scene clip: a slow eased pan or zoom over the scene PNG.

Free replacement for a paid I2V clip on scenes the scenarist marked
"motion": "still". Deterministic local ffmpeg, no network.

    python3 tools/still_shot.py --image scenes/scene-3/scene-3.png \
        --out scenes/scene-3/scene-3.mp4 --effect push-in --depth flat \
        --duration 5 --fps 30

Prints one JSON summary line on success; on failure prints JSON to stderr and exits 1.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

EFFECTS = ("push-in", "pull-out", "pan-right", "pan-left", "tilt-up", "tilt-down")
ZOOM_EFFECTS = ("push-in", "pull-out")
DEPTHS = ("flat", "some", "deep")
# Full move for flat compositions; a gentler zoom where missing parallax would show.
ZOOM_BY_DEPTH = {"flat": 0.12, "some": 0.07, "deep": 0.07}
OVERSAMPLE = 4  # render zoompan on a 4x canvas; avoids the jitter zoompan shows on small images
DURATION_TOLERANCE = 0.05

CENTER_X = "iw/2-(iw/zoom/2)"
CENTER_Y = "ih/2-(ih/zoom/2)"


class StillShotError(Exception):
    pass


def frame_count(duration, fps):
    frames = int(round(duration * fps))
    if frames < 2:
        raise StillShotError("duration x fps must give at least 2 frames")
    return frames


def ease(frames):
    # Cosine ease: smooth start and stop over the whole clip.
    return f"(0.5-0.5*cos(PI*on/{frames - 1}))"


def zoompan_expressions(effect, depth, frames):
    if effect not in EFFECTS:
        raise StillShotError(f"unknown effect {effect!r}; use one of {', '.join(EFFECTS)}")
    if depth not in DEPTHS:
        raise StillShotError(f"unknown depth {depth!r}; use one of {', '.join(DEPTHS)}")
    if depth != "flat" and effect not in ZOOM_EFFECTS:
        raise StillShotError(
            f"depth {depth!r} allows only push-in or pull-out; a pan or tilt over a deep "
            "composition shows the missing parallax"
        )
    zoom = ZOOM_BY_DEPTH[depth]
    e = ease(frames)
    if effect == "push-in":
        return f"1+{zoom}*{e}", CENTER_X, CENTER_Y
    if effect == "pull-out":
        return f"{1 + zoom:.2f}-{zoom}*{e}", CENTER_X, CENTER_Y
    held = f"{1 + zoom:.2f}"
    if effect == "pan-right":
        return held, f"(iw-iw/zoom)*{e}", CENTER_Y
    if effect == "pan-left":
        return held, f"(iw-iw/zoom)*(1-{e})", CENTER_Y
    if effect == "tilt-up":
        return held, CENTER_X, f"(ih-ih/zoom)*(1-{e})"
    return held, CENTER_X, f"(ih-ih/zoom)*{e}"  # tilt-down


def video_filter(effect, depth, frames, width, height, fps):
    z, x, y = zoompan_expressions(effect, depth, frames)
    big_w, big_h = width * OVERSAMPLE, height * OVERSAMPLE
    return (
        f"scale={big_w}:{big_h}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={big_w}:{big_h},"
        f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={width}x{height}:fps={fps},"
        "format=yuv420p"
    )


def build_command(ffmpeg, image, out, effect, depth, duration, fps, width, height,
                  audio, sample_rate, channels):
    frames = frame_count(duration, fps)
    command = [ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-i", str(image)]
    if audio == "silent":
        layout = "mono" if channels == 1 else "stereo"
        command += ["-f", "lavfi", "-t", f"{frames / fps:.6f}",
                    "-i", f"anullsrc=r={sample_rate}:cl={layout}"]
    command += ["-vf", video_filter(effect, depth, frames, width, height, fps),
                "-frames:v", str(frames),
                "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-movflags", "+faststart"]
    if audio == "silent":
        command += ["-map", "0:v:0", "-map", "1:a:0", "-c:a", "aac", "-b:a", "128k", "-shortest"]
    else:
        command += ["-an"]
    command.append(str(out))
    return command, frames


def probe(ffprobe, path):
    result = subprocess.run(
        [ffprobe, "-v", "error", "-count_frames", "-show_entries",
         "format=duration:stream=codec_type,width,height,nb_read_frames",
         "-of", "json", str(path)],
        capture_output=True, text=True,
    )
    if result.returncode:
        raise StillShotError(result.stderr.strip() or f"ffprobe could not read {path}")
    return json.loads(result.stdout)


def render(image, out, effect, depth="flat", duration=5.0, fps=30, width=1080, height=1920,
           audio="none", sample_rate=44100, channels=2, force=False):
    image, out = Path(image), Path(out)
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise StillShotError("ffmpeg and ffprobe are required")
    if not image.is_file():
        raise StillShotError(f"image not found: {image}")
    if out.suffix.lower() != ".mp4":
        raise StillShotError("output must be an .mp4")
    if out.exists() and not force:
        # The target may hold a paid clip; never overwrite one silently.
        raise StillShotError(f"output exists: {out} (pass --force to replace it)")
    if audio not in ("none", "silent"):
        raise StillShotError("audio must be none or silent")
    if duration <= 0 or fps <= 0 or width <= 0 or height <= 0:
        raise StillShotError("duration, fps, width and height must be positive")
    if width % 2 or height % 2:
        raise StillShotError("width and height must be even for yuv420p")

    # Render to a temporary file next to the target and move it into place only after it
    # passes validation, so a failed render never leaves a file at the real path.
    tmp = out.with_name(f".{out.stem}.rendering.mp4")
    command, frames = build_command(ffmpeg, image, tmp, effect, depth, duration, fps,
                                    width, height, audio, sample_rate, channels)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode:
            raise StillShotError(result.stderr.strip().splitlines()[-1] if result.stderr.strip()
                                 else f"ffmpeg exited {result.returncode}")

        meta = probe(ffprobe, tmp)
        streams = meta.get("streams") or []
        video = next((s for s in streams if s.get("codec_type") == "video"), None)
        has_audio = any(s.get("codec_type") == "audio" for s in streams)
        actual = float(meta["format"]["duration"])
        expected = frames / fps
        problems = []
        if not video or (video.get("width"), video.get("height")) != (width, height):
            problems.append(f"size {video and video.get('width')}x{video and video.get('height')}")
        if video and int(video.get("nb_read_frames") or 0) != frames:
            problems.append(f"{video.get('nb_read_frames')} frames, expected {frames}")
        if abs(actual - expected) > DURATION_TOLERANCE:
            problems.append(f"duration {actual:.3f}s, expected {expected:.3f}s")
        if has_audio != (audio == "silent"):
            problems.append("audio track mismatch")
        if problems:
            raise StillShotError("rendered clip failed validation: " + "; ".join(problems))
        os.replace(tmp, out)
    finally:
        tmp.unlink(missing_ok=True)

    data = out.read_bytes()
    return {
        "ok": True,
        "output": str(out),
        "image": str(image),
        "image_sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
        "effect": effect,
        "depth": depth,
        "zoom": ZOOM_BY_DEPTH[depth],
        "duration": round(actual, 6),
        "fps": fps,
        "frames": frames,
        "width": width,
        "height": height,
        "audio": audio,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "cost_usd": 0,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Render a still-shot scene clip (free, local ffmpeg)")
    parser.add_argument("--image", required=True, type=Path, help="scene still PNG")
    parser.add_argument("--out", required=True, type=Path, help="output MP4, normally scenes/scene-K/scene-K.mp4")
    parser.add_argument("--effect", required=True, choices=EFFECTS)
    parser.add_argument("--depth", default="flat", choices=DEPTHS,
                        help="scenarist's depth rating; some/deep use a gentler 7%% zoom and forbid pans/tilts")
    parser.add_argument("--duration", type=float, default=5.0, help="seconds, same as the clip it replaces")
    parser.add_argument("--fps", type=int, default=30, help="the editor normalizes every clip to 30 fps")
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1920)
    parser.add_argument("--audio", default="none", choices=("none", "silent"),
                        help="silent adds a silent track for formats whose clips carry audio")
    parser.add_argument("--sample-rate", type=int, default=44100)
    parser.add_argument("--channels", type=int, default=2, choices=(1, 2))
    parser.add_argument("--force", action="store_true", help="replace an existing output file")
    args = parser.parse_args(argv)
    try:
        summary = render(args.image, args.out, args.effect, args.depth, args.duration, args.fps,
                         args.width, args.height, args.audio, args.sample_rate, args.channels,
                         args.force)
    except StillShotError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(summary, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
