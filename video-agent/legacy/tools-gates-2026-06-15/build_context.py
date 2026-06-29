#!/usr/bin/env python3
"""
Build merged context file for (game, format) pair.
Usage: python tools/build_context.py <GAME_TAG> <FORMAT> <OUTPUT_DIR>

Assembles OUTPUT_DIR/merged-context.md with:
  ## Format Rules      ← rules/formats/{format}.md
  ## Visual Identity   ← games/{game}/{game}.md
  ## Special Overrides ← games/{game}/{format}_special.md  (if present)
  ## Story State       ← games/{game}/{format}_story_bible.json (if present)

Exits 1 if format rules or game config are missing.
Exits 1 if story bible is expected (format in STORY_BIBLE_FORMATS) but file is absent
and this is clearly not episode 1 (heuristic: output dir already has storyboard.json).
"""

import sys
import json
import pathlib

STORY_BIBLE_FORMATS = {"serial-drama", "reddit-story", "fun-news", "streettalk", "special-report"}


def render_serial_drama_state(bible: dict) -> str:
    lines = []
    last_ep = bible.get("last_episode", 0)
    next_ep = (last_ep or 0) + 1
    lines.append(f"**Series:** {bible.get('title', '(untitled)')}")
    lines.append(f"**Last episode:** {last_ep}  →  **Next episode:** {next_ep}")

    eps = bible.get("episode_summaries", [])
    if eps:
        last = eps[-1]
        lines.append(f"\n**Previous summary:** {last.get('summary', '')}")
        if last.get("cliffhanger"):
            lines.append(f"**Open cliffhanger:** {last['cliffhanger']}")

    loops = bible.get("active_loops", [])
    if loops:
        lines.append("\n**Active loops (must be advanced, not ignored):**")
        for lp in loops:
            lines.append(f"  - {lp}")

    chars = bible.get("characters", [])
    if chars:
        lines.append("\n**Character roster:**")
        for c in chars:
            name = c.get("name", "?")
            role = c.get("role", "")
            status = c.get("status", "active")
            aura = c.get("aura_points", "")
            voice = c.get("elevenlabs_voice") or c.get("voice", "")
            line = f"  - **{name}** ({role}) status={status}"
            if aura:
                line += f" aura={aura}"
            if voice:
                line += f" voice={voice}"
            lines.append(line)

    anti = bible.get("anti_repetition", {})
    if isinstance(anti, dict):
        phrases = anti.get("recent_phrases", [])
        hooks = anti.get("recent_hooks", [])
        cliffs = anti.get("recent_cliffhangers", [])
        if phrases:
            lines.append(f"\n**Do NOT reuse these phrases:** {', '.join(repr(p) for p in phrases[-4:])}")
        if hooks:
            lines.append(f"**Do NOT reuse these hooks:** {', '.join(hooks[-4:])}")
        if cliffs:
            lines.append(f"**Do NOT reuse these cliffhangers:** {', '.join(cliffs[-3:])}")

    planned = bible.get("planned_arc", "")
    if planned:
        lines.append(f"\n**Planned arc:** {planned}")

    return "\n".join(lines)


def render_reddit_story_state(bible: dict) -> str:
    lines = []
    total = bible.get("total_stories", 0)
    lines.append(f"**Stories produced:** {total}")

    stories = bible.get("stories", [])
    if stories:
        last = stories[-1]
        lines.append(f"**Last story:** #{last.get('id')} — {last.get('headline', '')} (tone: {last.get('tone')}, theme: {last.get('theme')})")

    anti = bible.get("anti_repetition", {})
    if isinstance(anti, dict):
        recent_themes = anti.get("recent_themes", [])
        recent_tones = anti.get("recent_tones", [])
        banned = anti.get("banned_combos", [])
        if recent_themes:
            lines.append(f"\n**Recently used themes (avoid repeating):** {', '.join(recent_themes[-4:])}")
        if recent_tones:
            lines.append(f"**Recently used tones:** {', '.join(recent_tones[-4:])}")
        if banned:
            lines.append(f"**Banned combos:** {', '.join(str(b) for b in banned[-3:])}")

    return "\n".join(lines)


def render_generic_state(bible: dict) -> str:
    lines = []
    eps = bible.get("episode_summaries", bible.get("stories", []))
    if eps:
        last = eps[-1]
        lines.append(f"**Episodes/stories:** {len(eps)}")
        summary = last.get("summary") or last.get("headline", "")
        if summary:
            lines.append(f"**Last:** {summary}")

    anti = bible.get("anti_repetition", {})
    if isinstance(anti, dict):
        for k, v in anti.items():
            if v and isinstance(v, list):
                lines.append(f"**{k} (recent, avoid reuse):** {', '.join(str(x) for x in v[-4:])}")

    return "\n".join(lines) if lines else json.dumps(bible, indent=2, ensure_ascii=False)[:600]


def main():
    if len(sys.argv) < 4:
        print("Usage: build_context.py <GAME_TAG> <FORMAT> <OUTPUT_DIR>", file=sys.stderr)
        sys.exit(1)

    game_tag = sys.argv[1]
    format_slug = sys.argv[2]
    output_dir = pathlib.Path(sys.argv[3])

    # Resolve base: script lives in video-agent/tools/, base is video-agent/
    base = pathlib.Path(__file__).resolve().parent.parent

    rules_format_file = base / "rules" / "formats" / f"{format_slug}.md"
    game_config_file = base / "games" / game_tag / f"{game_tag}.md"
    special_file = base / "games" / game_tag / f"{format_slug}_special.md"
    story_bible_file = base / "games" / game_tag / f"{format_slug}_story_bible.json"

    errors = []

    if not rules_format_file.exists():
        errors.append(f"Format rules not found: {rules_format_file}")
    if not game_config_file.exists():
        errors.append(f"Game config not found: {game_config_file}")

    if errors:
        print("build_context.py FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Story bible: required if format uses it AND bible is absent while output already exists
    # (catching the "manager forgot to load existing bible" case, not the episode-1 case)
    story_bible_data = None
    has_output = (output_dir / "storyboard.json").exists()
    if format_slug in STORY_BIBLE_FORMATS:
        if story_bible_file.exists():
            try:
                story_bible_data = json.loads(story_bible_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                errors.append(f"Story bible is not valid JSON: {story_bible_file} — {e}")
        else:
            if has_output:
                # Output exists but no bible — likely a lost/deleted bible, not episode 1
                errors.append(
                    f"Story bible expected for format '{format_slug}' but not found: {story_bible_file}\n"
                    f"  (storyboard.json already exists in {output_dir} — this does not look like episode 1)\n"
                    f"  If this IS episode 1, create an empty bible first, then re-run."
                )
            else:
                print(f"NOTE: No story bible at {story_bible_file} — treating as episode/story 1 (OK)")

    if errors:
        print("build_context.py FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Assemble merged-context.md
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "merged-context.md"

    sections = []
    toc = []

    sections.append(f"## Format Rules\n\n{rules_format_file.read_text(encoding='utf-8')}")
    toc.append("Format Rules")

    sections.append(f"## Visual Identity\n\n{game_config_file.read_text(encoding='utf-8')}")
    toc.append("Visual Identity")

    if special_file.exists():
        sections.append(f"## Special Overrides\n\n{special_file.read_text(encoding='utf-8')}")
        toc.append("Special Overrides")
    else:
        print(f"NOTE: No special overrides at {special_file} (optional — OK)")

    if story_bible_data is not None:
        if format_slug == "serial-drama":
            state_text = render_serial_drama_state(story_bible_data)
        elif format_slug == "reddit-story":
            state_text = render_reddit_story_state(story_bible_data)
        else:
            state_text = render_generic_state(story_bible_data)
        sections.append(f"## Story State\n\n{state_text}")
        toc.append("Story State")

    separator = "\n\n---\n\n"
    out_file.write_text(separator.join(sections), encoding="utf-8")

    print(f"OK: merged-context.md written → {out_file}")
    print(f"Sections: {' | '.join(toc)}")


if __name__ == "__main__":
    main()
