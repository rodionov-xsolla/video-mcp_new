# Fallback and error handling

Behavior rules for timeouts, generation failures, and FFmpeg crashes.

---

## Async polling (fal.ai)

Video/image generation via fal.ai is asynchronous. After submitting a request:

1. Get `request_id` from the response
2. Poll status every **15 seconds**
3. Maximum wait time per generation: **10 minutes**

### ⚠️ CRITICAL: Base URL for status/result

Submit goes to the **full** endpoint, but status and result use the **2-segment base path** only.

```python
# Rule: base = first 2 segments of the endpoint
base = "/".join(endpoint.split("/")[:2])

# Status:  https://queue.fal.run/{base}/requests/{request_id}/status
# Result:  https://queue.fal.run/{base}/requests/{request_id}
```

| Model | Submit endpoint | Status/Result base |
|--------|-----------------|-------------------|
| NB2 edit | `fal-ai/nano-banana-2/edit` | `fal-ai/nano-banana-2` |
| Kling I2V | `fal-ai/kling-video/v2.6/pro/image-to-video` | `fal-ai/kling-video` |
| Kling Avatar v2 | `fal-ai/kling-video/ai-avatar/v2/standard` | `fal-ai/kling-video` |
| ElevenLabs TTS | `fal-ai/elevenlabs/tts/eleven-v3` | `fal-ai/elevenlabs` |
| ElevenLabs TTS (fal.ai) | `fal-ai/elevenlabs/tts/eleven-v3` | `fal-ai/elevenlabs` |

**If you use the full path** → fal.ai returns an empty body or 404, the task is "lost".

### Statuses and actions

| Status | Action |
|--------|--------|
| `IN_QUEUE` / `IN_PROGRESS` | Continue polling |
| `COMPLETED` | Fetch the result via GET /requests/{REQUEST_ID}, continue pipeline |
| `FAILED` | Retry once. If FAILED again → fallback |
| Timeout 10 min | Cancel the task, fallback |

---

## Fallback cascade

### Images

```
Nano Banana 2 ──QUEUE>5000──→ GPT Image 2 (primary fallback, fast)
Nano Banana 2 ──FAIL──→ retry once ──FAIL──→ GPT Image 2 ──FAIL──→ GPT Image 1 ──FAIL──→ status 'failed'
```

**Nano Banana 2 — primary model.** For the first scene (no reference) — first generate a character ref through Nano Banana 2 with a neutral prompt, use its URL as `image_urls[0]`. Do NOT switch to flux-pro or other models without an explicit error.

**GPT Image 2 — primary fallback when NB2 queue > 5000.** Check queue position after first submit: `queue_position > 5000` → cancel immediately, switch to GPT Image 2 for ALL remaining images in this run (don't mix models mid-episode). Endpoint: `fal-ai/gpt-image-2`. Key difference from GPT Image 1: **supports `image_urls` for chain reference** (same semantics as NB2 — bg-ref first, then character sheet). Size: `portrait_16_9` for 9:16 (outputs 608×1088). Burn-tested 2026-06-05, works with chain ref, ~$0.10/image. Typical time 1.5–3 min per image. Do NOT use `end_image_url` with Avatar (Avatar v2 doesn't use it anyway).

**GPT Image 1 — last resort fallback.** No chain reference support. Only if GPT Image 2 also fails.

**If `fal.run` sync endpoint is unresponsive** — use the `queue.fal.run` async endpoint with polling.

### Video

On generation failure — descend the cascade:

```
Kling I2V ──FAIL──→ retry once ──FAIL──→ Ken Burns (FFmpeg zoompan)
Ken Burns  ──FAIL──→ retry once ──FAIL──→ status 'failed', record error
```

On fallback:
- Re-plan scenes for the new approach
- Keep already-generated files (do not delete)
- Record original and final approach in the log

---

## fal.ai API errors

| Error | Action |
|--------|--------|
| **Rate limited (429)** | Wait 30 seconds, retry |
| **Invalid input (400/422)** | Check prompt and parameters, retry |
| **Server error (500)** | Wait 60 seconds, retry once |
| **Model unavailable (503)** | Fallback to the next model |
| **Timeout** | Fallback to the next model |

Maximum **1 retry** per generation. Don't loop.

---

## FFmpeg Cloud API errors

| Error | Action |
|--------|--------|
| HTTP 400 | Check JSON and request parameters |
| HTTP 401 | Check FFMPEG_API_KEY |
| HTTP 403 (quota) | Wait or use AI endpoint instead of standard |
| HTTP 500 (processing) | Retry once after 30 sec |
| Concat fails | Verify all clip URLs are accessible. Use AI endpoint with task description |
| Audio overlay fails | Try without music. If still failing — output video without audio |
| Ken Burns fails | Check image dimensions via `/ffprobe/analyze`. Make sure width ≥ 1080px |
| 0-byte file | Regenerate |

---

## Download errors

| Error | Action |
|--------|--------|
| curl returned an error | Retry after 10 seconds, max 3 attempts |
| 0-byte file | Delete and regenerate |
| URL expired | fal.ai URLs are temporary — always download immediately after generation |
| Re-requesting URL | **NEVER** re-request a fal.ai result URL to pass between stages. Download locally → upload to Supabase → use a permanent URL |

After each download, check the file size:
```bash
filesize=$(stat -f%z "scene-1.png" 2>/dev/null || stat -c%s "scene-1.png" 2>/dev/null)
if [ "$filesize" -lt 1000 ]; then
  echo "ERROR: Downloaded file is too small"
fi
```

---

## Error logging

For any error that leads to `status='failed'`:

<!-- TODO: implement INSERT into video_agent_runs -->
1. Record into `video_agent_runs`:
   - `status`: 'failed'
   - `error_message`: error description (which approach, which step, what went wrong)
   - `total_cost_usd`: spend up to the error
   - `scenes`: all scenes, including failed ones

2. Do not delete intermediate files — they are needed for diagnostics.

---

## Operation timeouts

| Operation | Timeout |
|----------|---------|
| Image generation (Nano Banana 2) | 120 seconds |
| Video generation (Kling 2.6 Pro I2V) | 10 minutes |
| File download (curl) | 120 seconds |
| FFmpeg operation | 5 minutes |
| **Whole pipeline (worker.sh)** | **40 minutes** |
