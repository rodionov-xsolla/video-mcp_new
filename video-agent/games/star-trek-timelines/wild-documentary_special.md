# Star Trek Timelines — Wild Documentary overrides

## Title overlay (mandatory)

Do NOT generate a title overlay PNG via Pillow — use the locked branding asset instead.

**Supabase URL:**
`https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/star-trek-timelines/branding/wild-documentary-overlay.png`

**Local copy:** `games/star-trek-timelines/Wildlife_overlay.png`

**Specs:**
- 1536×1024 RGBA
- Content: "STAR TREK TIMELINES / WILDLIFE" branded title card with gradient vignette
- Apply in ffmpeg pass-2 after concat: scale to video width (`scale=608:405`), top-aligned with 85px offset (`overlay=0:85`)
- Fade in: `st=0:d=0.5:alpha=1`; fade out: `st=3.5:d=0.5:alpha=1`
- Always use `format=rgba` before fade filters (prevents alpha-channel flicker)
- Always use `/usr/local/bin/ffmpeg-full/ffmpeg` (has libass for subtitle burn)

**Editor ffmpeg snippet (pass-2 filter_complex):**
```
[1:v]scale=608:405,format=rgba,fade=t=in:st=0:d=0.5:alpha=1,fade=t=out:st=3.5:d=0.5:alpha=1[ovl];[0:v][ovl]overlay=0:85:format=auto[vovl];[vovl]ass={ASSFILE}[vout]
```

## CTA

Append only the existing Star Trek CTA asset after the creature clips. Do not generate an in-scene sign, CTA frame, spoken substitute, or synthetic end card. If the asset is unavailable, stop and report the error.

## Post-Animator validation (technical only)

After the Animator phase, verify file count, expected index mapping, decodability, dimensions, durations, and hashes. Identical hashes across different scene indices are a technical duplicate signal; do not use AI Vision or visually compare generated frames.

```bash
shasum -a 256 OUTPUT_DIR/scenes/scene-*/scene-*.mp4
```

If a file is technically missing, corrupt, or byte-identical to another index, retry that same Kling v3 request once with the same settings. A second failure stops the video with an error; do not shift guessed files or switch provider/model.
