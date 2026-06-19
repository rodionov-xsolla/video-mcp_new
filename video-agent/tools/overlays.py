#!/usr/bin/env python3
from __future__ import annotations
"""
Generator of ORIGINAL graphic overlays (NOT subtitles).

Subtitles are spoken speech, one universal style, a separate script
(tools/add_subtitles.py). THIS script draws everything else "branded":
series title / title card, survival counter (in-game POV), outcome plate
(YOU DIED / YOU SURVIVED), top-list numbers (#5..#1), item names, slogan and
disclaimer (fake-ad), and channel-bug (the channel's PNG logo).

Contract:
  - Overlay specs live in storyboard.json: a per-scene `overlays[]` array
    (schema below) and an optional top-level `channel_bug` field.
  - The script EMITS a filter_complex fragment (a drawtext chain) per scene —
    the editor splices it into the `[vk]` branch BEFORE concat (single-pass §0,
    no extra re-encodes). channel_bug is a PNG overlay AFTER concat and AFTER subtitles.
  - The script does NOT run ffmpeg itself (except --check). It prints the filter
    string to stdout; empty stdout = the scene has no overlays (pass-through).

overlays[] schema (in each clip/scene of storyboard.json):
  {
    "type": "title|hud_counter|outcome_plate|rank_number|item_name|slogan|disclaimer",
    "text": "OSIAL\\nRISES",          // \\n -> stacked drawtext lines
    "position": "center|top-left|top-right|bottom-center|{x},{y}",
    "font": "ULT|TRJ|MED|ARI|IMPACT|MONT_BLACK|BEBAS",  // logical key (FONTS)
    "size": 130,
    "color": "white",                 // name or RRGGBB
    "stroke": {"color": "black", "width": 4},
    "enable": [0.0, 5.0],             // [start,end] -> between(t,..); ["gte", 13.5]; omit = whole clip
    "fade_in": 0.3,                   // optional alpha ramp from 0
    "opacity": 1.0,                   // optional constant opacity
    "line_gap": 160                   // optional y step between \\n lines (default = size*1.25)
  }

Usage:
  # fragment for one scene (editor calls it in a loop K=1..N):
  python3 overlays.py storyboard.json --scene-index 3 --workdir build \\
      --input-label "[v3pre]" --output-label "[v3]"
  # all scenes at once (one line per scene with non-empty overlays):
  python3 overlays.py storyboard.json --emit-all --workdir build
  # channel-bug (after concat+ASS):
  python3 overlays.py storyboard.json --channel-bug --bug-png build/channel-bug.png \\
      --input-label "[vsub]" --output-label "[vout]"
  # font validation before the expensive encode:
  python3 overlays.py storyboard.json --check
"""

import argparse
import json
import os
import sys


# ---------------------------------------------------------------------------
# Fonts: logical key -> list of candidate paths (first existing one).
# Hardcoding absolute paths in the rules is not portable — resolve with fallbacks.
# ---------------------------------------------------------------------------

FONTS = {
    # "ultra" display — titles. Trajan/Impact as a practical fallback.
    "ULT": [
        "/Library/Fonts/TrajanPro-Bold.otf",
        os.path.expanduser("~/Library/Fonts/TrajanPro-Bold.otf"),
        "/Library/Fonts/Montserrat-Black.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
    ],
    "TRJ": [
        "/Library/Fonts/TrajanPro-Bold.otf",
        os.path.expanduser("~/Library/Fonts/TrajanPro-Bold.otf"),
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
    ],
    "MED": [  # medium weight for sub-plates (hook_plate)
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ],
    "ARI": [  # Arial Unicode — needed for ％ U+FF05 in counters
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ],
    "IMPACT": [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/Library/Fonts/Impact.ttf",
    ],
    "MONT_BLACK": [
        "/Library/Fonts/Montserrat-Black.ttf",
        os.path.expanduser("~/Library/Fonts/Montserrat-Black.ttf"),
        "/System/Library/Fonts/Supplemental/Impact.ttf",
    ],
    "BEBAS": [
        "/Library/Fonts/BebasNeue-Regular.ttf",
        os.path.expanduser("~/Library/Fonts/BebasNeue-Regular.ttf"),
        "/System/Library/Fonts/Supplemental/Impact.ttf",
    ],
}

# Color name -> ffmpeg-compatible (ffmpeg understands names, but we fix the set)
NAMED_COLORS = {
    "white": "white", "black": "black", "red": "red", "green": "green",
    "yellow": "yellow", "blue": "blue", "gray": "gray", "lightgray": "0xBFBFBF",
    "orange": "orange",
}

# Named positions -> (x_expr, y_expr). For title/outcome y is often overridden.
NAMED_POS = {
    "center": ("(w-text_w)/2", "(h-text_h)/2"),
    "top-left": ("40", "40"),
    "top-right": ("w-text_w-40", "80"),
    "bottom-center": ("(w-text_w)/2", "h-text_h-200"),
    "top-center": ("(w-text_w)/2", "200"),
}


def resolve_font(key: str) -> str | None:
    """Logical key or absolute path -> existing font file path."""
    if key and os.path.isabs(key) and os.path.isfile(key):
        return key
    for cand in FONTS.get(key, []):
        if os.path.isfile(cand):
            return cand
    return None


def resolve_color(c: str) -> str:
    if not c:
        return "white"
    if c.lower() in NAMED_COLORS:
        return NAMED_COLORS[c.lower()]
    hexc = c.lstrip("#").upper()
    if len(hexc) == 6:
        return f"0x{hexc}"
    return c


def _enable_expr(enable) -> str | None:
    if not enable:
        return None
    if isinstance(enable, (list, tuple)):
        if len(enable) == 2 and enable[0] == "gte":
            return f"gte(t,{float(enable[1])})"
        if len(enable) == 2:
            return f"between(t,{float(enable[0])},{float(enable[1])})"
    return None


def _alpha_expr(fade_in: float, opacity: float, enable) -> str | None:
    """alpha for drawtext (0..1). fade_in ramps from the start of the enable window."""
    base = opacity if opacity is not None else 1.0
    if not fade_in:
        return f"{base}" if base != 1.0 else None
    # window start
    t0 = 0.0
    if isinstance(enable, (list, tuple)) and len(enable) == 2 and enable[0] != "gte":
        t0 = float(enable[0])
    elif isinstance(enable, (list, tuple)) and len(enable) == 2 and enable[0] == "gte":
        t0 = float(enable[1])
    return f"if(lt(t-{t0},{fade_in}),(t-{t0})/{fade_in}*{base},{base})"


def _write_textfile(workdir: str, scene_idx, oi, li, text: str) -> str:
    os.makedirs(workdir, exist_ok=True)
    path = os.path.join(workdir, f"ovl-s{scene_idx}-{oi}-{li}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def build_overlay_drawtexts(ov: dict, scene_idx, oi: int, workdir: str) -> list[str]:
    """One overlay object -> list of drawtext filters (one per \\n line)."""
    font = resolve_font(ov.get("font", "IMPACT"))
    if font is None:
        print(f"  [warn] font '{ov.get('font')}' not found — falling back to Impact", file=sys.stderr)
        font = resolve_font("IMPACT")
    size = int(ov.get("size", 72))
    color = resolve_color(ov.get("color", "white"))
    stroke = ov.get("stroke") or {}
    bw = int(stroke.get("width", 0))
    bcolor = resolve_color(stroke.get("color", "black"))
    enable = ov.get("enable")
    en = _enable_expr(enable)
    alpha = _alpha_expr(ov.get("fade_in", 0), ov.get("opacity", 1.0), enable)

    # position
    pos = ov.get("position", "center")
    if isinstance(pos, str) and pos in NAMED_POS:
        x_expr, y_base = NAMED_POS[pos]
    elif isinstance(pos, str) and "," in pos:
        x_str, y_str = pos.split(",", 1)
        x_expr, y_base = x_str.strip(), y_str.strip()
    elif isinstance(pos, dict):
        x_expr, y_base = str(pos.get("x", "(w-text_w)/2")), str(pos.get("y", "200"))
    else:
        x_expr, y_base = NAMED_POS["center"]

    lines = str(ov.get("text", "")).split("\\n")
    if len(lines) == 1 and "\n" in lines[0]:
        lines = lines[0].split("\n")
    line_gap = int(ov.get("line_gap", round(size * 1.25)))

    filters = []
    for li, line in enumerate(lines):
        if not line.strip():
            continue
        tf = _write_textfile(workdir, scene_idx, oi, li, line)
        # y for multi-line: shift down; for center expressions add an offset
        if li == 0:
            y_expr = y_base
        else:
            y_expr = f"({y_base})+{li * line_gap}"
        parts = [
            f"drawtext=textfile='{tf}'",
            f"fontfile='{font}'",
            f"fontsize={size}",
            f"fontcolor={color}",
            "expansion=none",
            f"x={x_expr}",
            f"y={y_expr}",
        ]
        if bw > 0:
            parts.append(f"borderw={bw}")
            parts.append(f"bordercolor={bcolor}")
        if en:
            parts.append(f"enable='{en}'")
        if alpha:
            parts.append(f"alpha='{alpha}'")
        filters.append(":".join(parts))
    return filters


def scene_fragment(scene: dict, scene_idx, workdir: str,
                   in_label: str, out_label: str) -> str:
    """All overlays of a scene -> one filter fragment '[in]drawtext,...[out]'.
    Empty if there are no overlays."""
    overlays = scene.get("overlays") or []
    all_dt = []
    for oi, ov in enumerate(overlays):
        all_dt.extend(build_overlay_drawtexts(ov, scene_idx, oi, workdir))
    if not all_dt:
        return ""
    return f"{in_label}" + ",".join(all_dt) + f"{out_label}"


def scene_idx(s: dict):
    """Scene/clip index: supports `index` (scenes) and `call_index` (in-game-pov clips)."""
    return s.get("index", s.get("call_index", 0))


def find_scenes(sb: dict) -> list[dict]:
    arr = sb.get("scenes") or sb.get("clips") or []
    return sorted(arr, key=scene_idx)


def channel_bug_fragment(bug_label: str, in_label: str, out_label: str) -> str:
    """channel-bug: PNG 110×110, top-left 40,40, after concat+ASS.
    bug_label is the REAL ffmpeg input label of the PNG (e.g. '[5:v]', where 5 = index
    of the last '-i build/channel-bug.png'). The editor must add this input and pass
    its index via --bug-input-label.
    Fragment: [5:v]scale=110:110[bug];[vsub][bug]overlay=40:40[vout]
    """
    return (f"{bug_label}scale=110:110[bug];"
            f"{in_label}[bug]overlay=40:40:format=auto{out_label}")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("storyboard", help="path to storyboard.json")
    ap.add_argument("--scene-index", type=int, default=None,
                    help="scene index (1-based) — emit the fragment for it")
    ap.add_argument("--emit-all", action="store_true",
                    help="one line per scene with overlays: 'IDX<TAB>fragment'")
    ap.add_argument("--channel-bug", action="store_true",
                    help="emit the channel-bug overlay (after concat)")
    ap.add_argument("--bug-png", default=None, help="path to the logo PNG (for --channel-bug; existence check)")
    ap.add_argument("--bug-input-label", default="[BUG:v]",
                    help="REAL ffmpeg input label of the PNG, e.g. '[5:v]' (index of -i channel-bug.png)")
    ap.add_argument("--workdir", default="build", help="where to write the textfiles")
    ap.add_argument("--input-label", default="[vin]")
    ap.add_argument("--output-label", default="[vout]")
    ap.add_argument("--check", action="store_true",
                    help="check that all fonts referenced in the storyboard exist")
    args = ap.parse_args()

    with open(args.storyboard, encoding="utf-8") as f:
        sb = json.load(f)
    scenes = find_scenes(sb)

    if args.check:
        used = set()
        for s in scenes:
            for ov in (s.get("overlays") or []):
                used.add(ov.get("font", "IMPACT"))
        missing = [k for k in used if resolve_font(k) is None]
        for k in sorted(used):
            print(f"  font {k}: {resolve_font(k) or 'MISSING'}", file=sys.stderr)
        if missing:
            print(f"ERROR: fonts not found: {missing}", file=sys.stderr)
            sys.exit(1)
        print("  [check] all fonts found", file=sys.stderr)
        return

    if args.channel_bug:
        if not args.bug_png or not os.path.isfile(args.bug_png):
            print(f"ERROR: --bug-png not found: {args.bug_png}", file=sys.stderr)
            sys.exit(1)
        if args.bug_input_label == "[BUG:v]":
            print("  [warn] --bug-input-label not set: pass the REAL PNG input index "
                  "(e.g. '[5:v]' where 5 = position of '-i build/channel-bug.png' among -i). "
                  "The fragment currently has the placeholder [BUG:v] — ffmpeg will reject it.", file=sys.stderr)
        print(channel_bug_fragment(args.bug_input_label, args.input_label, args.output_label))
        return

    if args.emit_all:
        for s in scenes:
            idx = scene_idx(s)
            frag = scene_fragment(s, idx, args.workdir,
                                  f"[v{idx}pre]", f"[v{idx}]")
            if frag:
                print(f"{idx}\t{frag}")
        return

    if args.scene_index is not None:
        match = next((s for s in scenes if scene_idx(s) == args.scene_index), None)
        if match is None:
            print(f"ERROR: scene index={args.scene_index} not found", file=sys.stderr)
            sys.exit(1)
        frag = scene_fragment(match, args.scene_index, args.workdir,
                              args.input_label, args.output_label)
        if frag:
            print(frag)
        # empty stdout = no overlays (editor does pass-through)
        return

    print("ERROR: specify --scene-index, --emit-all, --channel-bug or --check", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
