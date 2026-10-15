# Budgets and pricing

## Budget limits

| Format | Maximum | Stop if |
|--------|---------|---------|
| News | **$4.00** | Spend > $3.50 |
| Serial Drama | **$10.00** | Spend > $9.00 (all-H3: a full 6-clip episode is ~$3.25; Test 9: $3.24 vs $6.57 on Kling) |
| Dual-style | **$5.00** | Spend > $4.50 (H3 face reference: a 3-pair episode is ~$1.80, each extra pair ~$0.57) |
| Gameplay AI Avatar | **$5.00** | Spend > $4.50 |
| Reddit Story | **$2.00** | Spend > $1.80 |
| Character Story | **$6.00** | Spend > $5.40 |
| Motion Dance | **$3.00** | Spend > $2.70 |
| What If... Real Life | **$6.00** | Spend > $5.40 |
| TOP List | **$5.00** | Spend > $4.50 |
| Fun News | **$4.50** | Spend > $4.00 |
| Streettalk | **$7.00** | Spend > $6.30 (pilot allowance; EP2+ target ~$3.00) |
| In-Game POV | **$7.00** | Spend > $6.30 |
| Redcon | **$6.00** | Spend > $5.40 |
| Wild Documentary | **$5.00** | Spend > $4.50 |
| Special Report | **$4.50** | Spend > $4.00 (pilot allowance; EP2+ target ~$2.85) |
| Fake Ad | **$3.50** | Spend > $3.00 |
| Item Story | **$6.00** | Spend > $5.40 |

Tracking: after each generation, record the cost. Before the next one — check the limit.

---

## Pricing by model (fal.ai, USD)

| Model | Endpoint | Cost |
|--------|----------|-----------|
| Nano Banana 2 (image) | fal-ai/nano-banana-2/edit | ~$0.08 |
| GPT Image 1 (alternate route; no automatic fallback) | fal-ai/gpt-image-1/text-to-image | ~$0.02 |
| MiniMax H3 Max I2V 3s (768P; always returns sound) | minimax/h3-max/image-to-video | ~$0.25 |
| MiniMax H3 Max I2V 5s (768P; always returns sound) | minimax/h3-max/image-to-video | ~$0.41 |
| MiniMax H3 Max I2V 10s (768P; always returns sound) | minimax/h3-max/image-to-video | ~$0.83 |
| MiniMax H3 Max face reference 5s (`reference-to-video`, route `minimax.h3max.r2v`; dual-style; clip ambience kept) | minimax/h3-max/reference-to-video | ~$0.41 ($0.08/s on the returned ~5.18 s; Kling v3 Standard with audio was $0.63) |
| MiniMax H3 Max Turbo lip-sync only (`target_audio_url`; what-if-real-life and serial-drama dialogue), 5 s exchange | minimax/h3-max-turbo/image-to-video | $0.04/s on the returned length; 5 s ≈ $0.21, a 7 s two-speaker exchange ≈ $0.30 (Kling Avatar v2: $0.056/s, 5 s = $0.28) |
| Still shot (`motion: "still"`; replaces a paid clip) | local ffmpeg, `tools/still_shot.py` | $0.00 |
| Kling v3 Standard I2V 5s (no audio) | fal-ai/kling-video/v3/standard/image-to-video | $0.42 |
| Kling v3 Standard I2V 5s (with audio) | fal-ai/kling-video/v3/standard/image-to-video | $0.63 |
| Kling v3 Standard I2V 10s (no audio) | fal-ai/kling-video/v3/standard/image-to-video | $0.84 |
| Kling v3 Standard I2V 10s (with audio) | fal-ai/kling-video/v3/standard/image-to-video | $1.26 |
| Kling 2.6 Pro I2V 5s (with audio; format-selected route) | fal-ai/kling-video/v2.6/pro/image-to-video | $0.70 |
| Kling 2.6 Pro I2V 5s (no audio; format-selected route) | fal-ai/kling-video/v2.6/pro/image-to-video | $0.35 |
| Kling 2.6 Pro I2V 10s (with audio; format-selected route) | fal-ai/kling-video/v2.6/pro/image-to-video | $1.40 |
| Kling 2.6 Pro I2V 10s (no audio; format-selected route) | fal-ai/kling-video/v2.6/pro/image-to-video | $0.70 |
| MiniMax TTS | fal-ai/minimax/speech-2.8-hd | ~$0.10/1k chars (~$0.001–0.005/phrase). `voice_setting.voice_id`, `emotion` |
| Chatterbox TTS (approved exact-format sample only) | fal-ai/chatterbox/text-to-speech | ~$0.05–0.08/phrase. Zero-shot voice clone from the exact format/series reference MP3. |
| Kling Lipsync | fal-ai/kling-video/lipsync/audio-to-video | ~$0.10/s |
| HeyGen Avatar IV | fal-ai/heygen/avatar4/image-to-video | $0.10/s |
| Kling Avatar v2 Standard | fal-ai/kling-video/ai-avatar/v2/standard | $0.056/s |
| Kling Motion Control v2.6 Standard | fal-ai/kling-video/v2.6/standard/motion-control | $0.07/s |
| Kling Motion Control v3 Standard | fal-ai/kling-video/v3/standard/motion-control | $0.126/s |
| Kling Motion Control v3 Pro | fal-ai/kling-video/v3/pro/motion-control | $0.168/s |

MiniMax H3 Max (route `minimax.h3max.i2v`, the plain I2V route) costs **$0.08/s at 768P**, counted on the **returned** clip length (it returns ~5.18 s for a 5 s request and ~3.07 s for 3 s): 3 s ≈ $0.25, 5 s ≈ $0.41, 10 s ≈ $0.83. fal runs a promo price of $0.048/s until 15 Oct 2026; budget and report at $0.08/s. Kling v3 Standard for comparison: $0.084/s audio off (5 s = $0.42), $0.126/s audio on (5 s = $0.63). Still shots are rendered locally and cost nothing.

H3 lip-sync (what-if-real-life and serial-drama dialogue) runs on H3 Max Turbo (route `minimax.h3max.turbo.i2v` plus `target_audio_url`; Turbo is never used for plain clips) at $0.04/s on the returned length: a 4.8 s TTS returns 5.184 s ≈ $0.21, against $0.28 for a 5 s Kling Avatar v2 clip ($0.056/s); serial-drama's two-speaker exchanges (6.7–9.2 s of TTS in Test 9) returned 7.3–9.4 s ≈ $0.29–0.38, against $1.08–1.39 for the same clips on Kling v3 Standard with voices ($0.154/s). Dual-style runs on H3 Max face reference (`minimax.h3max.r2v`) at H3 Max's $0.08/s. Kling v3 Standard I2V is no longer the active route of any of the ten H3 formats. The Kling Avatar formats keep Kling Avatar v2 until their pilots.

---

## Mandatory cost report

After completing video generation, ALWAYS show the user a detailed breakdown:

```
=== Generation cost ===
Images: N × $X.XX = $X.XX
Video (model, duration): N × $X.XX = $X.XX
Still shots (local): N × $0.00 = $0.00
---
TOTAL: $X.XX
```

H3 Max and H3 Max face-reference clips are reported at $0.08/s on the returned length (the runner's `validation.duration` for the downloaded clip, before the editor's trim), not on the requested `duration`; H3 Max Turbo lip-sync clips go on their own line at $0.04/s, counted the same way. Still scenes (`scene_video_kind: "still"`) are listed on their own line at $0.00.

Never skip this report — the user must see the cost of every generation.
