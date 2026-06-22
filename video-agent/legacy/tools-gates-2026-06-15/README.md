# Gate scripts (archived 2026-06-22)

Added in `d834cce` (2026-06-15), reverted 2026-06-22. The layer was not used in practice — validation between phases is done inline in `pipeline.sh` (`jq` on `storyboard.json`, `stat`/`ffprobe` on artifacts).

Files:
- `build_context.py` — assembled `merged-context.md` for Scenarist
- `validate_storyboard.py` — per-stage checks
- `check_runtime.py` — TTS-vs-target-duration check
- `preflight_assets.py` — URL liveness / dup MP3 / stray PNG before Kling
- `check_final.py` — final.mp4 integrity (moov atom, subtitle drift)

Kept here for reference in case any of the checks are worth re-introducing as inline logic.
