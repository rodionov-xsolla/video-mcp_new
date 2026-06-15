#!/usr/bin/env python3
"""
Gate: validate storyboard artifacts for a given pipeline stage.
Usage: python tools/validate_storyboard.py --stage <scenarist|sound|storyboarder|animator> --output-dir <path>
Exits 1 if validation fails.
"""

import sys
import json
import pathlib
import argparse
import subprocess


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
    # clip_type is the canonical field in current storyboard schema; type/generate_audio are fallbacks
    return (clip.get("clip_type") == "dialogue"
            or clip.get("type") == "dialogue"
            or clip.get("generate_audio") is True)


def get_image_url(clip):
    return (clip.get("scene_image")
            or clip.get("scene_image_url")
            or clip.get("image_url", ""))


def get_tts_url(clip):
    return clip.get("tts_url") or clip.get("audio_url", "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True,
                        choices=["scenarist", "sound", "storyboarder", "animator"])
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    output_dir = pathlib.Path(args.output_dir)
    sb_file = output_dir / "storyboard.json"
    errors = []

    # storyboard.json is required at every stage
    if not sb_file.exists():
        print(f"ERROR: storyboard.json not found at {sb_file}", file=sys.stderr)
        sys.exit(1)

    try:
        sb = json.loads(sb_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: storyboard.json is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    clips = sb.get("scenes", sb.get("clips", []))
    if not clips:
        print("ERROR: storyboard.json has no scenes/clips", file=sys.stderr)
        sys.exit(1)

    # ── scenarist gate ────────────────────────────────────────────────────────
    if args.stage == "scenarist":
        for clip in clips:
            idx = clip_index(clip)
            clip_type = clip.get("clip_type") or clip.get("type")
            if not clip_type:
                errors.append(f"scene-{idx}: missing clip_type field")
            # Must have either action content or dialogue content
            has_content = (clip.get("action_description") or clip.get("motion_prompt")
                           or clip.get("tts") or clip.get("character_speech") or clip.get("dialogue"))
            if not has_content:
                errors.append(f"scene-{idx}: no action_description/motion_prompt or tts/dialogue")
        if not errors:
            print(f"GATE PASSED scenarist: storyboard.json valid — {len(clips)} scenes")

    # ── sound gate ────────────────────────────────────────────────────────────
    elif args.stage == "sound":
        dialogue_clips = [c for c in clips if is_dialogue(c)]
        if not dialogue_clips:
            print("GATE PASSED sound: no dialogue clips (sound phase was skipped — OK)")
        else:
            ok = 0
            for clip in dialogue_clips:
                idx = clip_index(clip)
                # Check tts_url written back into storyboard
                if not get_tts_url(clip):
                    errors.append(f"scene-{idx}: dialogue clip has no tts_url/audio_url in storyboard.json")
                # Check local mp3 file
                mp3 = output_dir / "scenes" / f"scene-{idx}" / f"scene-{idx}.mp3"
                if not mp3.exists():
                    errors.append(f"scene-{idx}: {mp3.name} not found on disk")
                elif mp3.stat().st_size < 5_000:
                    errors.append(f"scene-{idx}: {mp3.name} suspiciously small ({mp3.stat().st_size} bytes)")
                else:
                    ok += 1
            if not errors:
                print(f"GATE PASSED sound: {ok}/{len(dialogue_clips)} dialogue clips have TTS audio")

    # ── storyboarder gate ─────────────────────────────────────────────────────
    elif args.stage == "storyboarder":
        ok = 0
        for clip in clips:
            idx = clip_index(clip)
            png = output_dir / "scenes" / f"scene-{idx}" / f"scene-{idx}.png"
            if not png.exists():
                errors.append(f"scene-{idx}: {png.name} not found")
            elif png.stat().st_size < 1_000:
                errors.append(f"scene-{idx}: {png.name} too small ({png.stat().st_size} bytes)")
            else:
                if not get_image_url(clip):
                    errors.append(f"scene-{idx}: PNG on disk but no scene_image/image_url in storyboard.json")
                else:
                    ok += 1
        if not errors:
            print(f"GATE PASSED storyboarder: {ok}/{len(clips)} scene PNGs present with URLs")

    # ── animator gate ─────────────────────────────────────────────────────────
    elif args.stage == "animator":
        ok = 0
        for clip in clips:
            idx = clip_index(clip)
            mp4 = output_dir / "scenes" / f"scene-{idx}" / f"scene-{idx}.mp4"
            if not mp4.exists():
                errors.append(f"scene-{idx}: {mp4.name} not found")
            elif mp4.stat().st_size < 100_000:
                errors.append(f"scene-{idx}: {mp4.name} suspiciously small ({mp4.stat().st_size} bytes)")
            else:
                dur = ffprobe_duration(mp4)
                if dur is None or dur < 1.0:
                    errors.append(f"scene-{idx}: {mp4.name} ffprobe returned duration={dur}")
                else:
                    ok += 1
        if not errors:
            print(f"GATE PASSED animator: {ok}/{len(clips)} scene MP4s valid")

    if errors:
        print(f"\nGATE FAILED ({args.stage}, {len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
