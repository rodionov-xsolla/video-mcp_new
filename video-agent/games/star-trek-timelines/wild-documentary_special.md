# Star Trek Timelines — Wild Documentary overrides

## Title overlay (mandatory)

Do NOT generate a title overlay PNG via Pillow — use the locked branding asset instead.

**Supabase URL:**
`https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/star-trek-timelines/branding/wild-documentary-overlay.png`

**Local copy:** `games/star-trek-timelines/Wildlife_overlay.png`

**Specs:**
- 1536×1024 RGBA
- Content: "STAR TREK TIMELINES / WILDLIFE" branded title card with gradient vignette
- Apply in ffmpeg pass-2 after concat: scale proportionally to the 1080-wide final canvas (`scale=1080:720`), top-third offset (`overlay=0:151`)
- Fade in: `st=0:d=0.5:alpha=1`; fade out: `st=3.5:d=0.5:alpha=1`
- Always use `format=rgba` before fade filters (prevents alpha-channel flicker)
- Always use `/usr/local/bin/ffmpeg-full/ffmpeg` (has libass for subtitle burn)

**Editor ffmpeg snippet (pass-2 filter_complex):**
```
[1:v]scale=1080:720,format=rgba,fade=t=in:st=0:d=0.5:alpha=1,fade=t=out:st=3.5:d=0.5:alpha=1[ovl];[0:v][ovl]overlay=0:151:format=auto[vovl];[vovl]ass={ASSFILE}[vout]
```

(Corrected 2026-08-05 — the previous `scale=608:405, overlay=0:85` numbers were written against a stale 608-wide canvas assumption; production has used the actual 1080×1920 canvas since EP2.)

## CTA (in-scene sign + standard asset)

The exact `STORY_BIBLE_PATH` is the sole source for this format's CTA. Read `cta.sign_text` and `cta.standard_asset_url` from `games/star-trek-timelines/wild-documentary_story_bible.json`; do not duplicate or hard-code either value in this special file.

- Store the bible phrase verbatim in `sign_text`, set `cta_in_scene: true`, and show the creature presenting the small white rectangular card face-on to the lens.
- Generate the readable card in the NB2 start frame; Kling only animates the approach and presentation while preserving the lettering.
- Do not burn or repair the wording with ffmpeg drawtext or subtitles.
- After the in-scene CTA clip, append the bible's `cta.standard_asset_url`. Missing or unavailable values are blocking errors.

## Post-Animator validation (technical only)

After the Animator phase, verify file count, expected index mapping, decodability, dimensions, durations, and hashes. Identical hashes across different scene indices are a technical duplicate signal; do not use AI Vision or visually compare generated frames.

```bash
shasum -a 256 OUTPUT_DIR/scenes/scene-*/scene-*.mp4
```

If a file is technically missing, corrupt, or byte-identical to another index, retry that same Kling v3 request once with the same settings. A second failure stops the video with an error; do not shift guessed files or switch provider/model.
