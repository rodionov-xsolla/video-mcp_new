#!/usr/bin/env python3
"""
Gate: cross-asset pre-flight check before Animator (Kling spend).
Usage: python tools/preflight_assets.py --output-dir <path>

Checks:
  1. Every image_url / audio_url returns HTTP 200
  2. No two dialogue clips share the same MP3 (md5 duplicate check)
  3. No stray PNG variants (-new, -v2, -copy) alongside the canonical scene-K.png
  4. Filename pattern matches clip index (scene-K.png under scenes/scene-K/)

Prints a mapping table (clip → image_url → audio_url → hero) for visual inspection.
Exits 1 if any check fails.
"""

import sys
import json
import hashlib
import pathlib
import argparse
import urllib.request
import urllib.error


def http_head_ok(url: str, timeout: int = 12) -> bool:
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 400
    except Exception:
        return False


def md5_of_file(path: pathlib.Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def clip_index(clip):
    return clip.get("index", clip.get("scene_number", clip.get("id", "?")))


def is_dialogue(clip):
    return (clip.get("clip_type") == "dialogue"
            or clip.get("type") == "dialogue"
            or clip.get("generate_audio") is True)


def get_image_url(clip):
    return (clip.get("scene_image")
            or clip.get("scene_image_url")
            or clip.get("image_url", ""))


def get_tts_url(clip):
    return clip.get("tts_url") or clip.get("audio_url", "")


def truncate(s: str, n: int = 60) -> str:
    return (s[:n - 2] + "..") if len(s) > n else s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    output_dir = pathlib.Path(args.output_dir)
    sb_file = output_dir / "storyboard.json"

    if not sb_file.exists():
        print(f"ERROR: storyboard.json not found at {sb_file}", file=sys.stderr)
        sys.exit(1)

    sb = json.loads(sb_file.read_text(encoding="utf-8"))
    clips = sb.get("scenes", sb.get("clips", []))

    if not clips:
        print("ERROR: storyboard.json has no scenes/clips", file=sys.stderr)
        sys.exit(1)

    errors = []
    mp3_hashes: dict[str, str] = {}  # md5 → clip index of first occurrence

    # Print mapping table header
    col = {"clip": 5, "type": 9, "image": 55, "audio": 55, "hero": 16}
    header = (f"{'Clip':<{col['clip']}}  {'Type':<{col['type']}}  "
               f"{'image_url':<{col['image']}}  {'audio_url':<{col['audio']}}  {'hero':<{col['hero']}}")
    print(header)
    print("-" * len(header))

    for clip in clips:
        idx = clip_index(clip)
        clip_type = clip.get("clip_type") or clip.get("type", "action")
        image_url = get_image_url(clip)
        audio_url = get_tts_url(clip)
        hero = clip.get("hero", "")

        print(
            f"{str(idx):<{col['clip']}}  {clip_type:<{col['type']}}  "
            f"{truncate(image_url, col['image']):<{col['image']}}  "
            f"{truncate(audio_url, col['audio']):<{col['audio']}}  "
            f"{hero:<{col['hero']}}"
        )

        # ── Check 1: image_url HTTP 200 ────────────────────────────────────
        if image_url:
            if not http_head_ok(image_url):
                errors.append(f"scene-{idx}: scene_image URL returns non-200 — {truncate(image_url, 80)}")
        else:
            errors.append(f"scene-{idx}: no scene_image/image_url in storyboard.json")

        # ── Check 2: tts_url HTTP 200 for dialogue ─────────────────────────
        if is_dialogue(clip):
            if audio_url:
                if not http_head_ok(audio_url):
                    errors.append(f"scene-{idx}: tts_url returns non-200 — {truncate(audio_url, 80)}")
            else:
                errors.append(f"scene-{idx}: dialogue clip has no tts_url in storyboard.json")

        # ── Check 3: no duplicate MP3 (local file md5) ────────────────────
        mp3_local = output_dir / "scenes" / f"scene-{idx}" / f"scene-{idx}.mp3"
        if mp3_local.exists():
            h = md5_of_file(mp3_local)
            if h in mp3_hashes:
                errors.append(
                    f"scene-{idx}: MP3 is byte-for-byte identical to scene-{mp3_hashes[h]} "
                    f"(copy-paste error — wrong audio for this clip)"
                )
            else:
                mp3_hashes[h] = str(idx)

        # ── Check 4: no stray PNG variants ────────────────────────────────
        scene_dir = output_dir / "scenes" / f"scene-{idx}"
        if scene_dir.exists():
            canonical = f"scene-{idx}.png"
            stray = [f.name for f in scene_dir.glob("*.png") if f.name != canonical]
            if stray:
                errors.append(
                    f"scene-{idx}: stray PNG(s) alongside {canonical}: {stray} "
                    f"— move to _archive/ or delete before Animator"
                )

    print()

    if errors:
        print(f"PRE-FLIGHT FAILED ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        print("\nFix all errors above before spending on Kling.", file=sys.stderr)
        sys.exit(1)

    print(f"PRE-FLIGHT PASSED: all {len(clips)} clips ready for Kling")


if __name__ == "__main__":
    main()
