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
| MiniMax speech | `fal-ai/minimax/speech-2.8-hd` | `fal-ai/minimax` |
| Chatterbox | `fal-ai/chatterbox/text-to-speech` | `fal-ai/chatterbox` |

**If you use the full path** → fal.ai returns an empty body or 404, the task is "lost".

### Statuses and actions

| Status | Action |
|--------|--------|
| `IN_QUEUE` / `IN_PROGRESS` | Continue polling |
| `COMPLETED` | Fetch the result via GET /requests/{REQUEST_ID}, continue pipeline |
| `FAILED` | Retry the same serialized request once; if it fails again, stop the whole video |
| Timeout 10 min | Cancel, retry the same route once; a second timeout stops the whole video |

---

## Failure policy — no automatic fallback

The chosen provider, model and route remain fixed for the request. A transient/API/download/zero-byte failure gets one retry with the same serialized request. For deterministic HTTP 400/422, content-filter rejection, or a local FFmpeg command defect, correct only the rejected input/parameter/command and retry once on the same route. If that attempt fails, stop the whole video and return the actual error.

Do not switch to GPT Image, Kling 2.6, Ken Burns, another provider, a local substitute, or a no-audio/no-music result. A different model may be used only after the stopped run when the user explicitly authorizes that separate route.

---

## fal.ai API errors

| Error | Action |
|--------|--------|
| **Rate limited (429)** | Wait as requested, retry the same request once |
| **Invalid input (400/422)** | Correct only the rejected input/parameter, retry once on the same model |
| **Server error (500)** | Wait 60 seconds, retry once |
| **Model unavailable (503)** | Retry the same route once, then stop |
| **Timeout** | Retry the same route once, then stop |

Maximum **1 retry** per generation. Don't loop.

---

## FFmpeg errors

| Error | Action |
|--------|--------|
| Invalid command/input | Correct only the rejected command/input and retry once on the same route |
| HTTP 401/403 | Stop and report the authentication/quota error |
| HTTP 500 / timeout | Retry the same request once, then stop |
| Concat/audio overlay fails | Correct the same FFmpeg command once; never omit required audio or music |
| 0-byte file | Retry the same operation once, then stop |

---

## Download errors

| Error | Action |
|--------|--------|
| curl returned an error | Retry the same download once after 10 seconds |
| 0-byte file | Delete it and retry the same download once; then stop |
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
| Video generation | 10 minutes |
| File download (curl) | 120 seconds |
| FFmpeg operation | 5 minutes |
| **Whole pipeline (worker.sh)** | **40 minutes** |
