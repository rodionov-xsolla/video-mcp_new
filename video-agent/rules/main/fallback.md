# Fallback and error handling

Behavior rules for timeouts, generation failures, and FFmpeg crashes.

---

## Async polling (fal.ai)

Video/image generation via fal.ai is asynchronous. After submitting a request:

1. Get `request_id` from the response
2. Poll status every **15 seconds**
3. Maximum wait time per generation: **10 minutes**

### NB2 Storyboarder override — runner owns recovery

Every Storyboarder NB2 text/edit request goes through `tools/fal_runner.py`. Its durable state machine overrides the generic manual submit/poll/retry rules in this file:

- Never submit, poll, fetch, download, or retry NB2 with direct curl/HTTP.
- After preflight, keep the job JSON immutable. Resume `PENDING`, interrupted poll/download, or `VALIDATED` upload failure by rerunning the **same job file and `job_id`**.
- A definitive provider generation failure becomes `PAID_RETRY_REQUIRED`; runner does not issue a replacement paid POST by default. Only explicit authorization permits one same-contract retry via `--allow-paid-retry`. Do not add a role/manager wrapper retry.
- `UNKNOWN` / `AmbiguousSubmitError` means the POST may have succeeded without a safely recorded response. **Never resubmit.** Stop and report `state_path`.
- `FAILED` and `INPUT_REJECTED` are terminal for that job. Generic advice below to edit a rejected request and retry does not authorize mutation/resubmission of a runner job.
- The runner has no safe reset command for a claimed canonical output. Never delete state or `_claims` manually; preserve them and stop for an explicit recovery decision.

### Kling v3 Standard Animator override — runner owns recovery

All schema-v3 video jobs follow the same transport safety contract. The runner never chooses a semantic fallback: recovery resumes the exact saved route and payload. A different tool, duration, audio setting, or request body is an orchestrator decision represented by a new job after the current run has stopped:

- Never wrap the runner in a submit/poll/download retry loop; rerun the same immutable job to resume its saved request ID.
- `UNKNOWN` is ambiguous and must never be resubmitted.
- A definitive remote generation failure becomes `PAID_RETRY_REQUIRED`; one replacement POST requires separate explicit authorization and `--allow-paid-retry`.
- `VALIDATED` resumes only Supabase upload; `DONE` is idempotent. `FAILED` and `INPUT_REJECTED` are terminal.
- Do not delete or move the runner's state, request, claim, MP4, or job contract.

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
| `FAILED` | Generic non-runner call: retry the same serialized request once. NB2/Kling runner: let saved state decide; terminal runner `FAILED` stops |
| Timeout 10 min | Generic non-runner call: cancel/retry once. NB2/Kling runner: rerun the same job to resume the saved request ID; never submit a replacement |

---

## Failure policy — no automatic fallback

The chosen provider, model and route remain fixed for the request. A transient/API/download/zero-byte failure gets one retry with the same serialized request. For deterministic HTTP 400/422, content-filter rejection, or a local FFmpeg command defect, correct only the rejected input/parameter/command and retry once on the same route. If that attempt fails, stop the whole video and return the actual error. For NB2 and allowlisted Kling v3 Standard runner jobs, the runner overrides above apply instead: do not mutate or wrap-retry the job.

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
| Image generation (Nano Banana 2 runner polling window) | 10 minutes |
| Video generation | 10 minutes |
| File download (curl) | 120 seconds |
| FFmpeg operation | 5 minutes |
| **Whole pipeline (interactive manager run)** | **40 minutes** |
