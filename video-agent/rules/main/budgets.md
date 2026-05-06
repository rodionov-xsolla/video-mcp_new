# Бюджеты и стоимость

## Бюджетные лимиты

| Формат | Максимум | Остановись если |
|--------|----------|-----------------|
| Standard | **$5.00** | Расход > $4.50 |
| News | **$4.00** | Расход > $3.50 |
| Serial Drama | **$10.00** | Расход > $9.00 |
| Object Character (single) | **$1.50** | Расход > $1.30 |
| Object Character (series×5) | **$7.50** | Расход > $7.00 |
| Dual-style | **$5.00** | Расход > $4.50 |
| Gameplay AI Avatar | **$5.00** | Расход > $4.50 |
| Dance Battle | **$5.00** | Расход > $4.50 |
| Reddit Story | **$2.00** | Расход > $1.80 |
| Character Story | **$6.00** | Расход > $5.40 |
| Motion Dance | **$3.00** | Расход > $2.70 |

Трекинг: после каждой генерации записывай стоимость. Перед следующей — проверяй лимит.

---

## Стоимость по моделям (fal.ai, USD)

| Модель | Endpoint | Стоимость |
|--------|----------|-----------|
| Nano Banana 2 (image) | fal-ai/nano-banana-2/edit | ~$0.08 |
| GPT Image 1 (fallback image) | fal-ai/gpt-image-1/text-to-image | ~$0.02 |
| Kling v3 Standard I2V 5s (без аудио) | fal-ai/kling-video/v3/standard/image-to-video | $0.42 |
| Kling v3 Standard I2V 5s (с аудио) | fal-ai/kling-video/v3/standard/image-to-video | $0.63 |
| Kling v3 Standard I2V 10s (без аудио) | fal-ai/kling-video/v3/standard/image-to-video | $0.84 |
| Kling v3 Standard I2V 10s (с аудио) | fal-ai/kling-video/v3/standard/image-to-video | $1.26 |
| Kling 2.6 Pro I2V 5s (с аудио, fallback) | fal-ai/kling-video/v2.6/pro/image-to-video | $0.70 |
| Kling 2.6 Pro I2V 5s (без аудио, fallback) | fal-ai/kling-video/v2.6/pro/image-to-video | $0.35 |
| Kling 2.6 Pro I2V 10s (с аудио, fallback) | fal-ai/kling-video/v2.6/pro/image-to-video | $1.40 |
| Kling 2.6 Pro I2V 10s (без аудио, fallback) | fal-ai/kling-video/v2.6/pro/image-to-video | $0.70 |
| Veo3 T2V 8s (с аудио) | fal-ai/veo3 | $3.20 |
| Veo3 T2V 8s (без аудио) | fal-ai/veo3 | $1.60 |
| ElevenLabs TTS (via fal.ai) | fal-ai/elevenlabs/tts/eleven-v3 | ~$0.30/мин (~$0.05–0.10/фраза). **voice = имя, НЕ voice_id** |
| Kling Lipsync | fal-ai/kling-video/lipsync/audio-to-video | ~$0.10/сек |
| HeyGen Avatar IV | fal-ai/heygen/avatar4/image-to-video | $0.10/сек |
| Kling Avatar v2 Standard | fal-ai/kling-video/ai-avatar/v2/standard | $0.056/сек |
| Kling Motion Control v2.6 Standard | fal-ai/kling-video/v2.6/standard/motion-control | $0.07/сек |
| Kling Motion Control v3 Standard | fal-ai/kling-video/v3/standard/motion-control | $0.126/сек |
| Kling Motion Control v3 Pro | fal-ai/kling-video/v3/pro/motion-control | $0.168/сек |

---

## Обязательный отчёт о стоимости

После завершения генерации видео ВСЕГДА показывай пользователю детальную разбивку:

```
=== Стоимость генерации ===
Изображения: N × $X.XX = $X.XX
Видео (модель, длительность): N × $X.XX = $X.XX
---
ИТОГО: $X.XX
```

Никогда не пропускай этот отчёт — пользователь должен видеть стоимость каждой генерации.
