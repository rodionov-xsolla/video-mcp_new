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

## CTA (in-scene sign)

Standard sign text for Star Trek Timelines wild-documentary: **"Download the game / Link in bio"**
- Written in black marker on a small white rectangular card
- Held by the creature facing the lens cleanly
- Do NOT burn text into the video frame via ffmpeg — sign must be visible in the Kling-generated clip itself

## Post-Animator validation (manager must do this)

After the Animator phase, check that no two consecutive scene-N.mp4 files contain duplicated content (Kling CDN dedup bug — can occur silently during a retry):

```bash
ls -lh OUTPUT_DIR/scenes/scene-*/scene-*.mp4
```

If scene duplication detected (everything shifted by 1):
1. Archive wrong file: `cp scenes/scene-N/scene-N.mp4 _archive/scene-N_wrong.mp4 && rm scenes/scene-N/scene-N.mp4`
2. Shift correct files: `mv scene-(N+1).mp4 → scene-N.mp4`, etc.
3. Re-animate only the last missing scene(s) — do NOT re-run all scenes
