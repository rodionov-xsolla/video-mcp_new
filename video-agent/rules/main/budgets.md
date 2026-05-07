# Budgets and pricing

## Budget limits

| Format | Maximum | Stop if |
|--------|---------|---------|
| Standard | **$5.00** | Spend > $4.50 |
| News | **$4.00** | Spend > $3.50 |
| Serial Drama | **$10.00** | Spend > $9.00 |
| Object Character (single) | **$1.50** | Spend > $1.30 |
| Object Character (series×5) | **$7.50** | Spend > $7.00 |
| Dual-style | **$5.00** | Spend > $4.50 |
| Gameplay AI Avatar | **$5.00** | Spend > $4.50 |
| Dance Battle | **$5.00** | Spend > $4.50 |
| Reddit Story | **$2.00** | Spend > $1.80 |
| Character Story | **$6.00** | Spend > $5.40 |
| Motion Dance | **$3.00** | Spend > $2.70 |

Tracking: after each generation, record the cost. Before the next one — check the limit.

---

## Pricing by model (fal.ai, USD)

| Model | Endpoint | Cost |
|--------|----------|-----------|
| Nano Banana 2 (image) | fal-ai/nano-banana-2/edit | ~$0.08 |
| GPT Image 1 (fallback image) | fal-ai/gpt-image-1/text-to-image | ~$0.02 |
| Kling v3 Standard I2V 5s (no audio) | fal-ai/kling-video/v3/standard/image-to-video | $0.42 |
| Kling v3 Standard I2V 5s (with audio) | fal-ai/kling-video/v3/standard/image-to-video | $0.63 |
| Kling v3 Standard I2V 10s (no audio) | fal-ai/kling-video/v3/standard/image-to-video | $0.84 |
| Kling v3 Standard I2V 10s (with audio) | fal-ai/kling-video/v3/standard/image-to-video | $1.26 |
| Kling 2.6 Pro I2V 5s (with audio, fallback) | fal-ai/kling-video/v2.6/pro/image-to-video | $0.70 |
| Kling 2.6 Pro I2V 5s (no audio, fallback) | fal-ai/kling-video/v2.6/pro/image-to-video | $0.35 |
| Kling 2.6 Pro I2V 10s (with audio, fallback) | fal-ai/kling-video/v2.6/pro/image-to-video | $1.40 |
| Kling 2.6 Pro I2V 10s (no audio, fallback) | fal-ai/kling-video/v2.6/pro/image-to-video | $0.70 |
| Veo3 T2V 8s (with audio) | fal-ai/veo3 | $3.20 |
| Veo3 T2V 8s (no audio) | fal-ai/veo3 | $1.60 |
| ElevenLabs TTS (via fal.ai) | fal-ai/elevenlabs/tts/eleven-v3 | ~$0.30/min (~$0.05–0.10/line). **voice = name, NOT voice_id** |
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
---
TOTAL: $X.XX
```

Never skip this report — the user must see the cost of every generation.
