# Budgets and pricing

## Budget limits

| Format | Maximum | Stop if |
|--------|---------|---------|
| News | **$4.00** | Spend > $3.50 |
| Serial Drama | **$10.00** | Spend > $9.00 |
| Dual-style | **$5.00** | Spend > $4.50 |
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

Still scenes (`scene_video_kind: "still"`) are listed on their own line at $0.00.

Never skip this report — the user must see the cost of every generation.
