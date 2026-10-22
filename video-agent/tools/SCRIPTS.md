# Tools — справочник скриптов

Все пути относительно `video-agent/`. Скрипты сгруппированы по ролям.

---

## Легенда важности

| Уровень | Смысл |
|---------|-------|
| 🟠 ВЫСОКАЯ | Тратит деньги или блокирует пайплайн при падении |
| 🟡 СРЕДНЯЯ | Gate-скрипт — падение останавливает пайплайн, но без потерь |
| 🟢 НИЗКАЯ | Read-only или легко переигрываемый |

---

## Оркестратор

Оркестратор — интерактивный manager-агент (`../CLAUDE.md`), не скрипт: каждая фаза — отдельный вызов `Agent(subagent_type=...)`, инлайн-валидация (`jq`, `stat`, `ffprobe`) манагер делает сам после каждой фазы.

`pipeline.sh` и `queue/worker.sh` (bash-версия того же оркестратора, звавшая `codex exec`/`claude -p`) архивированы в `../legacy/launchers-2026-04/` — не рабочий путь, обе найденные попытки запуска падали на Scenarist. Не использовать.

---

## Storyboarder / NB2

### `fal_runner.py` 🟠

**Роль:** единственный transport/state layer для всех Storyboarder-вызовов Nano Banana 2 (~$0.08 за generation): text-to-image refs/backgrounds и edit-сцен. Runner фиксирует endpoint и параметры, защищает от повторного платного POST, возобновляет poll/download/upload, валидирует PNG, автоматически вызывает `queue/upload-asset.sh`, считает warning helper-а ошибкой и побайтово проверяет публичную копию. Прямые `curl`/fal.ai HTTP-вызовы из Storyboarder запрещены.

Перед работой:

```bash
test -f tools/fal_runner.py
python3 tools/fal_runner.py --help >/dev/null
```

Runner сам читает `.env` по умолчанию. Для real-run нужны `FAL_KEY`, а для job с upload также `SUPABASE_URL` и `SUPABASE_SERVICE_ROLE_KEY`; `--preflight` полностью offline и не тратит деньги. Jobs используют schema v1.

#### Полная job schema

Job — отдельный неизменяемый JSON-файл на один PNG. Неизвестные поля отклоняются.

```json
{
  "schema_version": 1,
  "job_id": "unique-stable-id",
  "route": "nb2.text | nb2.edit",
  "artifact_kind": "character_reference | location_reference | scene_start",
  "output_dir": "/absolute/path/to/episode-output",
  "output_path": "relative/path/inside/output-dir.png",
  "input": {
    "prompt": "3..50000 characters",
    "image_urls": ["https://permanent-ref.example/ref.png"],
    "seed": 12345
  },
  "supabase": {
    "game": "game-tag",
    "episode": "YYYY-MM-DD-format-slug",
    "name": "scene-1.png",
    "slug": "asset-slug",
    "variant": "optional-character-variant",
    "tags": "format-slug,series-id"
  }
}
```

Правила полей:

- `job_id`: 1–128 символов, первый символ ASCII letter/digit, далее только letters/digits и `._-`; он же имя state-каталога.
- `route: "nb2.text"`: `input.image_urls` нужно **полностью опустить**, не передавать `[]`.
- `route: "nb2.edit"`: требуется 1–4 уникальных HTTPS URL. Только постоянные URL; `fal.media` запрещён. Более строгий лимит активного format/role всё равно действует.
- `input.seed` необязателен, но если указан — только integer, не boolean.
- Отдельного поля `negative_prompt` в schema нет. Storyboarder дописывает все resolved negative constraints в конец `input.prompt`; добавление `negative_prompt` как соседнего поля будет отклонено preflight.
- `output_dir` — абсолютный путь. `output_path` — относительный `.png` внутри него; end-frame имена запрещены.
- Runner фиксирует `aspect_ratio: "9:16"`, `num_images: 1`, `output_format: "png"`, `resolution: "1K"`, `safety_tolerance: "5"`. Выход должен быть декодируемым portrait PNG: 9:16 либо документированный fallback 2:3, минимум 600×1000 и >1 KB.
- Поле `supabase` технически необязательно для локального runner job, но обязательно для Storyboarder. Производные upload arguments входят в `contract_sha256`, поэтому destination нельзя поменять после claim.

`artifact_kind` определяет upload kind; произвольный kind передать нельзя:

| artifact_kind | `upload-asset.sh --kind` | Обязательные `supabase` поля | Назначение |
|---|---|---|---|
| `character_reference` | `character` | `game`, `slug`; опционально `variant`, `tags` | reusable ref в `assets/` + `game_assets` |
| `location_reference` | `location` | `game`, `slug`; опционально `tags` | reusable location в `assets/` + `game_assets` |
| `scene_start` | `episode-scene` | `game`, `episode`, `name` | per-episode PNG в `episodes/`, без записи в `game_assets` |

Не используйте `variant` для `location_reference`. Avatar/branding/video не входят в текущий allowlist runner.

#### Команды: preflight, запуск, resume

```bash
JOB="$OUTPUT_DIR/build/fal/jobs/scene-1-v1.job.json"

python3 tools/fal_runner.py --preflight "$JOB"
python3 tools/fal_runner.py "$JOB"
```

Успешный real-run печатает одну JSON summary со следующими ключевыми полями:

```json
{
  "ok": true,
  "job_id": "scene-1-v1",
  "phase": "DONE",
  "output_path": "/absolute/.../scenes/scene-1/scene-1.png",
  "state_path": "/absolute/.../build/fal/scene-1-v1/state.json",
  "supabase_url": "https://.../scene-1.png"
}
```

Preflight offline проверяет JSON/schema/path/payload и вычисляет два hash: `payload_sha256` для точного fal request body и `contract_sha256` для контракта, включая route, artifact kind, canonical output и Supabase destination. После успешного preflight job JSON считается immutable. Reference URLs проверяются перед submit, а публичный Supabase файл — побайтово после upload.

**Resume всегда тем же job:** после прерванного poll, истёкшего download URL или ошибки Supabase снова запустить `python3 tools/fal_runner.py "$JOB"`. Не менять job JSON, `job_id` или `output_path`. Runner продолжит сохранённый `request_id`; при `VALIDATED` повторит только upload; при `DONE` вернёт idempotent summary без сети/оплаты.

**Не заменять ambiguous POST:** состояния `UNKNOWN`/ambiguous submit означают, что POST мог пройти и уже стоить денег. Не создавать replacement job, не архивировать его и не делать второй POST; остановиться и сообщить state path.

**Платный retry только явно:** definitive provider generation failure становится `PAID_RETRY_REQUIRED`. По умолчанию второй POST не выполняется. После отдельного явного разрешения можно один раз возобновить тот же immutable job командой `python3 tools/fal_runner.py --allow-paid-retry "$JOB"`. Флаг нельзя добавлять заранее или автоматически. Безопасный повтор submit после definitive 429 не требует этого флага, потому что request не был принят.

**Claimed canonical regeneration:** у runner нет безопасной команды reset/archive. Никогда не удалять и не перемещать PNG/state/request/claim вручную; сохранить их и остановиться для отдельного решения о восстановлении.

#### Text ref job

Новый ref в текущем runner MVP — portrait single-figure PNG, не обязательный legacy 16:9 sheet. Prompt строится в порядке backdrop → subject/anatomy → camera/lighting → constraints.

```json
{
  "schema_version": 1,
  "job_id": "20260716-mugato-wild-documentary-ref-v1",
  "route": "nb2.text",
  "artifact_kind": "character_reference",
  "output_dir": "/ABSOLUTE/OUTPUT_DIR",
  "output_path": "scenes/refs/mugato-ref-v1.png",
  "input": {
    "prompt": "Neutral damp-forest reference clearing with unobtrusive foliage; a single full-body Mugato with exhaustive canon anatomy; eye-level wildlife reference camera and soft natural overcast light; portrait 9:16, one creature only, all anatomy visible, no lettering."
  },
  "supabase": {
    "game": "star-trek-timelines",
    "slug": "mugato",
    "variant": "wild-documentary",
    "tags": "wild-documentary,character-reference"
  }
}
```

Для location ref поменять `artifact_kind` на `location_reference`, убрать `variant`, указать location `slug`, а prompt должен явно фиксировать пустую сцену (`NO characters in scene` согласно роли/формату).

#### Edit scene job

Scene job создаётся только после того, как все нужные ref jobs завершились и их постоянные `supabase_url` записаны в `input.image_urls`.

```json
{
  "schema_version": 1,
  "job_id": "20260716-mugato-scene-1-v1",
  "route": "nb2.edit",
  "artifact_kind": "scene_start",
  "output_dir": "/ABSOLUTE/OUTPUT_DIR",
  "output_path": "scenes/scene-1/scene-1.png",
  "input": {
    "prompt": "A rain-dark Neural forest clearing behind wet foreground leaves; one canon-accurate Mugato at mid-frame with every defining anatomical feature explicit; concealed telephoto camera, natural overcast light, heavy film grain; portrait 9:16, anatomy locked to the reference, no text or UI.",
    "image_urls": [
      "https://YOUR_PROJECT.supabase.co/storage/v1/object/public/assets/star-trek-timelines/characters/mugato/variants/wild-documentary.png"
    ]
  },
  "supabase": {
    "game": "star-trek-timelines",
    "episode": "2026-07-16-wild-documentary",
    "name": "scene-1.png"
  }
}
```

Tracked template: `tools/examples/fal-nb2-edit-scene.job.json`. Заменить `output_dir`, permanent Supabase ref URL, game/episode/name, prompt и уникальный `job_id`; затем обязательно запустить preflight. Placeholder URL синтаксически валиден для preflight, но real-run ожидаемо остановится на reference check, пока его не заменят.

#### Storyboard write-back и CTA

После `DONE`:

- `scene_image` = локальный `output_path` из summary;
- `scene_image_url` = постоянный `supabase_url` из summary/state;
- `image_urls` = только постоянные Supabase URLs нужных refs в правильном role-defined порядке;
- `result_url` из state и любые fal/fal.media URLs никогда не пишутся в storyboard и не передаются Animator.

Для CTA sign сначала прочитать `cta.sign_text` из **точного resolved story bible**. Положить строку в storyboard и NB2 prompt verbatim, потребовать только её и отсутствие любого дополнительного текста. Global phrase, другой game/format bible, special file или guessed fallback запрещены. Missing/empty CTA field — stop до job creation.

#### Dependency order и bounded concurrency

1. Reusable character/location ref jobs: строго синхронно до `DONE` + Supabase URL.
2. Scene jobs с previous-scene/scene-to-scene refs: строго по dependency order.
3. Только независимые scene jobs, когда формат не использует previous-scene chain, можно запускать foreground batch с максимум 3 процессами. Каждый job должен иметь уникальные `job_id`, `output_path`, state и claim.

Пример для заранее проверенного списка независимых jobs (`scene-jobs.txt`, один путь на строку):

```bash
xargs -P 3 -n 1 sh -c '
  python3 tools/fal_runner.py --preflight "$1" &&
  python3 tools/fal_runner.py "$1"
' sh < scene-jobs.txt
```

`xargs` остаётся foreground и ждёт все jobs. Не использовать detached `&`, не запускать зависимые сцены параллельно и не добавлять отдельный batch runner.

**Состояние на диске:**

```text
${OUTPUT_DIR}/build/fal/jobs/{job-file}.job.json   # authored immutable job
${OUTPUT_DIR}/build/fal/{job_id}/request.json     # canonical payload, writes runner
${OUTPUT_DIR}/build/fal/{job_id}/state.json       # phase/request_id/result/upload state
${OUTPUT_DIR}/build/fal/_claims/*.json            # output-path ownership; не удалять
```

---

## Animator / fal.ai Video Execution

### `kling_runner.py` 🟠

**Роль:** format-agnostic transport/state layer для fal.ai video routes из `tools/video_routes.json`. Scenarist/Manager/Animator заранее выбирают инструмент, duration, audio policy и создают полный provider `payload`. Runner не знает форматов, не переписывает payload и не решает, нужны ли `prompt`, `multi_prompt`, `voice_ids`, `elements` или другие provider fields. Он только проверяет permanent input URLs, безопасно выполняет submit/poll/download/upload и валидирует MP4 по переданному оркестратором `expect`.

Новый формат на существующем route не требует никаких изменений runner или registry. Новый endpoint с тем же fal queue protocol добавляется одной записью в `tools/video_routes.json` (`submit_url`, `poll_base`, `result_url_path`). Другой provider/protocol получает отдельный adapter; generic runner core и существующие jobs не расширяются format-specific branches.

Один immutable job создаёт один MP4:

```json
{
  "schema_version": 3,
  "job_id": "unique-scene-video-id",
  "route": "kling.v3.standard.i2v",
  "artifact_kind": "scene_video",
  "output_dir": "/absolute/episode/output",
  "output_path": "scenes/scene-1/scene-1.mp4",
  "payload": {
    "prompt": "exact provider request authored by Animator",
    "start_image_url": "https://permanent-supabase/scene-1.png",
    "duration": "5",
    "generate_audio": true,
    "negative_prompt": "resolved technical constraints"
  },
  "expect": {
    "kind": "video",
    "duration_seconds": 5,
    "duration_tolerance_seconds": 0.4,
    "audio": "required",
    "min_bytes": 100000,
    "min_width": 600,
    "min_height": 1000,
    "orientation": "portrait"
  },
  "supabase": {
    "game": "game-tag",
    "episode": "YYYY-MM-DD-format-run-id",
    "name": "scene-1.mp4"
  }
}
```

**H3 Max job** (route `minimax.h3max.i2v`, the plain I2V route of the H3 formats — see `fal-ai.md §2y`; what-if and serial-drama dialogue lip-sync and every fun-news, special-report and streettalk scene use H3 Max Turbo `minimax.h3max.turbo.i2v` with `target_audio_url`, templates `tools/examples/minimax-h3-max-turbo-lipsync.job.json`, `tools/examples/minimax-h3-max-turbo-serial-dialogue.job.json` and `tools/examples/minimax-h3-max-turbo-talking-head.job.json` (the talking-head formats add `seed: 20261021`); dual-style uses H3 Max face reference `minimax.h3max.r2v`, template `tools/examples/minimax-h3-max-r2v-face-ref.job.json`, payload below). Same schema, same runner, same commands; only `route`, `payload` and `expect` differ:

```json
{
  "schema_version": 3,
  "job_id": "unique-scene-video-id",
  "route": "minimax.h3max.i2v",
  "artifact_kind": "scene_video",
  "output_dir": "/absolute/episode/output",
  "output_path": "scenes/scene-1/scene-1.mp4",
  "payload": {
    "prompt": "motion prompt authored by Animator, ending with at most two short constraint sentences",
    "image_url": "https://permanent-supabase/scene-1.png",
    "duration": 5,
    "resolution": "768P",
    "prompt_expansion_mode": "disabled"
  },
  "expect": {
    "kind": "video",
    "duration_seconds": 5,
    "duration_tolerance_seconds": 0.8,
    "audio": "optional",
    "min_bytes": 100000,
    "min_width": 600,
    "min_height": 1000,
    "orientation": "portrait"
  },
  "supabase": {
    "game": "game-tag",
    "episode": "YYYY-MM-DD-format-run-id",
    "name": "scene-1.mp4"
  }
}
```

- `payload` is exactly these five fields (plus a silent `target_audio_url` on clips whose sound is discarded, below): `image_url` (not `start_image_url`), `duration` as a **number** equal to the scene's `duration_sec` (H3 accepts 0.92–15 s), `resolution: "768P"`, `prompt_expansion_mode: "disabled"`. H3 has no `negative_prompt`, `generate_audio`, `multi_prompt`, `voice_ids`, `elements` or `shot_type`.
- `expect.duration_tolerance_seconds` is `0.8`: H3 returns ~5.18 s for 5 s and can run up to ~0.7 s long.
- `expect.audio` is `"required"` when the format uses clip sound and `"optional"` when it does not — **never `"forbidden"`**: H3 always returns a soundtrack, so a forbidden-audio job fails validation after payment. Whether the editor uses the clip's sound comes from the scene's `scene_video_audio`, not from the stream.
- **Clips whose sound is discarded** (`scene_video_audio: "none"`) add exactly one field, a silent `target_audio_url` (`data:audio/mpeg;base64,...`, from `silent_audio.py` below; `rules/roles/animator.md` §2a). The template `tools/examples/minimax-h3-max-scene-video.job.json` shows the five-field payload, so add the field with `jq --rawfile` before `--preflight`. `"native"` clips send the five fields unchanged. A `data:` value is not a URL to the runner: it is not checked before submit and is sent untouched.
- **Dual-style face-reference job** (route `minimax.h3max.r2v`): the same schema with exactly seven payload fields — `prompt`, `image_url` (scene still = start frame), `reference_image_urls` (the frontal headshot URL(s)), `aspect_ratio: "9:16"`, `duration: 5`, `resolution: "768P"`, `prompt_expansion_mode: "disabled"` — and `expect.audio: "required"`, tolerance `0.8`; no `target_audio_url`. The runner checks every URL in `reference_image_urls` before submit like any other payload URL.

Граница ответственности:

- `payload` — любой непустой canonical JSON object; runner передаёт его без field allowlist, type conversion или format-specific validation;
- все URL, найденные внутри payload на любой глубине, должны быть permanent HTTPS и проверяются до paid submit; fal temporary URLs запрещены; значение `data:` (silent `target_audio_url`) — не URL и передаётся без проверки;
- `expect` задаёт техническую проверку результата: duration/tolerance, audio `required|optional|forbidden`, minimum bytes/dimensions и orientation;
- route descriptor, exact payload, exact `expect`, Supabase destination и output path входят в immutable contract hash;
- runner recovery никогда не меняет payload или route. Смена инструмента/параметров — решение оркестратора и новый job после остановленного запуска.

Команды:

```bash
JOB="$OUTPUT_DIR/build/video/jobs/scene-1-v3.job.json"

python3 tools/kling_runner.py --preflight "$JOB"
python3 tools/kling_runner.py "$JOB"   # invoke with Bash timeout ≥150s (see below)
```

**Poll window / Bash timeout (updated 2026-07-17).** `--poll-timeout` default is **140s**: the runner polls up to 140s then self-exits gracefully into a resumable `PENDING` state, rather than being SIGKILLed by an external ~120s tool timeout mid-download. **Always invoke the run command with a Bash timeout of ~150s** (`timeout: 150000`) so the 140s window runs uninterrupted with headroom for the final status fetch. Kling renders that take longer than 140s simply exit-and-resume: rerun the exact same command; the runner continues the saved `request_id` and **re-fetches a fresh result URL** (never reuses a stale one — `result_url(force)` + `EXPIRED_LINK_HTTP` 403/404/410 handling), so no paid generation or download link is ever lost across a resume.

После успешного preflight job неизменяем. Для resume повторяется ровно та же вторая команда с тем же job/job_id: runner продолжает сохранённый request ID, бесплатно обновляет истёкший result URL, повторяет только upload из `VALIDATED`, а для `DONE` возвращает `skipped: true`.

`UNKNOWN` означает ambiguous paid POST: второй submit запрещён. Definitive provider failure становится `PAID_RETRY_REQUIRED`; только отдельное явное разрешение допускает один повтор того же контракта:

```bash
python3 tools/kling_runner.py --allow-paid-retry "$JOB"
```

Runner не имеет archive/reset и не выполняет automatic batch. State хранится в `${OUTPUT_DIR}/build/video/{job_id}/`, claim — в `${OUTPUT_DIR}/build/video/_claims/`. Tracked templates: `tools/examples/minimax-h3-max-scene-video.job.json`, `tools/examples/minimax-h3-max-serial-action.job.json` (serial-drama action, Test 9), `tools/examples/minimax-h3-max-turbo-lipsync.job.json` (what-if), `tools/examples/minimax-h3-max-turbo-serial-dialogue.job.json` (serial-drama dialogue, Test 9), `tools/examples/minimax-h3-max-turbo-talking-head.job.json` (fun-news / special-report / streettalk talking head, Test 12), `tools/examples/minimax-h3-max-r2v-face-ref.job.json` (dual-style, Test 8); historical Kling: `tools/examples/kling-v3-standard-scene-video.job.json`, `tools/examples/kling-v3-serial-dialogue.job.json`, `tools/examples/kling-v3-elements.job.json`.

---

### `still_shot.py` 🟢

**Role:** renders a still-shot scene clip — a slow eased camera move (push, pull, pan or tilt) over the scene's still PNG — for scenes the scenarist marked `"motion": "still"` in Phase 1 (only in formats whose playbook says "Still shots: allowed"). Called by the animator agent instead of a paid I2V job. Deterministic local ffmpeg, no network, **$0**.

**Run:**
```bash
python3 tools/still_shot.py --image scenes/scene-K/scene-K.png \
    --out scenes/scene-K/scene-K.mp4 \
    --effect <still_effect> --depth <still_depth> --duration <duration_sec>
```

**Flags:**

| Flag | Default | Meaning |
|------|---------|---------|
| `--image` | required | scene still PNG |
| `--out` | required | output `.mp4`, normally `scenes/scene-K/scene-K.mp4` |
| `--effect` | required | `push-in`, `pull-out`, `pan-right`, `pan-left`, `tilt-up`, `tilt-down` (the scene's `still_effect`) |
| `--depth` | `flat` | the scene's `still_depth`: `flat` = 12% move; `some` / `deep` = gentler 7% zoom, `push-in` / `pull-out` only |
| `--duration` | `5` | seconds, the scene's `duration_sec` |
| `--fps` | `30` | the editor normalizes every clip to 30 fps |
| `--width` / `--height` | `1080` / `1920` | must be even (yuv420p) |
| `--audio` | `none` | `none` = no audio stream; `silent` adds a silent AAC track |
| `--sample-rate` / `--channels` | `44100` / `2` | only for `--audio silent` |
| `--force` | off | replace an existing output file |

**Output:** one JSON line on stdout, for example:

```json
{"ok":true,"output":"scenes/scene-3/scene-3.mp4","image":"scenes/scene-3/scene-3.png","effect":"push-in","depth":"flat","zoom":0.12,"duration":5.0,"fps":30,"frames":150,"width":1080,"height":1920,"audio":"none","bytes":2345678,"sha256":"<64 hex>","cost_usd":0}
```

On failure it prints `{"ok": false, "error": "..."}` to stderr and exits 1. Before reporting success it checks its own render with ffprobe (size, exact frame count, duration within ±0.05 s, audio track as requested). The animator copies `sha256`, `image_sha256` (the source PNG) and `frames` into the scene's `still_render` and sets `scene_video_kind: "still"`, `scene_video_route: "local.still_shot"`, `scene_video_url: null`, `scene_video_audio: "none"`.

**Reads:** scene PNG  
**Writes:** one MP4  
**Network:** none

**⚠ Pitfalls:**
- **Refuses to overwrite** an existing `--out` without `--force` — the path may hold a paid clip. Never pass `--force` over a path that a runner job claimed (`build/video/_claims/`).
- Stills are planned in Phase 1 only. Never render one as a fallback after a failed paid clip; if the tool fails, stop and report.
- `--depth some|deep` with a pan or tilt is rejected: the missing parallax would show.
- A 12% zoom crops ~11% and a pan travels ~11% of the width, so the storyboarder keeps the subject and any baked-in text inside the central ~85% of the frame.

---

### `silent_audio.py` 🟢

**Role:** renders the **silent `target_audio_url`** of a plain H3 Max clip (`minimax.h3max.i2v`) whose sound is discarded (`scene_video_audio: "none"`): a silent mono MP3 of the requested `duration` as a base64 `data:audio/mpeg;base64,...` URI. H3 always writes its own soundtrack and invents speech for a visible face; given a silent track it keeps the mouth closed (Test 6b: 30/30 clips returned a silent soundtrack, about −91 dB). Called by the animator agent while writing the job. Not for `"native"` clips (wild-documentary, in-game-pov, what-if physical gags) and not for H3 lip-sync (TTS). Local ffmpeg, no network, **$0**. Rule: `rules/roles/animator.md` §2a "Silent `target_audio_url`".

**Run:**
```bash
python3 tools/silent_audio.py --duration <duration_sec> --out "$OUTPUT_DIR/build/video/silence/scene-K.txt"
jq --rawfile silence "$OUTPUT_DIR/build/video/silence/scene-K.txt" \
  '.payload.target_audio_url = $silence' "$JOB_DRAFT" > "$JOB"   # before --preflight
```

**Flags:**

| Flag | Default | Meaning |
|------|---------|---------|
| `--duration` | required | seconds, the H3 payload `duration` (the scene's `duration_sec`); 2–15 s (H3 needs at least 2 s of target audio) |
| `--out` | off | write only the data URI (no trailing newline) to this file; without it the URI is printed inside the JSON |

ffmpeg command: `-f lavfi -i anullsrc=r=16000:cl=mono -t <d> -c:a libmp3lame -b:a 16k` into a temp file (~2 KB per second; a 5 s track is ~10 KB, ~14 KB as a data URI).

**Output:** one JSON line on stdout: `{"ok":true,"duration":5.0,"bytes":10376,"data_uri":"data:audio/mpeg;base64,..."}`; with `--out` the line has `"out": "<file>"` instead of `"data_uri"` (`bytes` = MP3 size). Before reporting success it checks its render with ffprobe (one mp3 stream, duration within 0.1 s). On failure it prints `{"ok": false, "error": "..."}` to stderr and exits 1 (also for a duration below 2 s or above 15 s).

**Reads:** nothing  
**Writes:** the `--out` file only (temp MP3 removed)  
**Network:** none

**⚠ Pitfalls:**
- Add the field before `--preflight`: after it the job is immutable.
- Never paste, shorten or hand-edit the data URI, and never reuse one rendered for a different `duration`.
- The returned H3 clip carries a silent audio stream: expected, not a defect (the stream is discarded anyway).

---

## FFmpeg-помощники (вызываются editor-агентом)

---

### `add_subtitles.py` 🟠

**Роль:** Генерирует ASS-субтитры через Whisper forced-alignment. Вызывается editor-агентом.

**Запуск:**
```bash
python tools/add_subtitles.py <audio_file> <output_ass> \
    --storyboard storyboard.json \
    --lang en \
    --main-dur 44.96 \
    [--emit-ass-only | --emit-timings]
```

**Что делает:**
1. Загружает Whisper medium модель (500 MB, CPU, int8) — первый запуск качает модель
2. Прогоняет `voice-final.wav` через Whisper → получает слова с таймингами
3. Извлекает canonical text из storyboard.json (что должно быть сказано)
4. Forced-alignment: сопоставляет canonical слова с Whisper-таймингами через difflib
5. Делит на чанки (цель: 4 слова, минимум: 2 слова, соблюдая границы предложений)
6. Пишет `.ass` файл с единым стилем (Helvetica Bold 72, белый + чёрный контур, MarginV=520)

**Функции:**
- `whisper_words(audio, lang, model)` — запускает faster_whisper, возвращает список слов с start/end
- `force_align(canonical_tokens, whisper_words)` — difflib SequenceMatcher, интерполяция для ненайденных слов
- `split_sentences(tokens)` — разбивка по границам предложений (`.`, `!`, `?`)
- `chunk_sentence(sentence, target=4, min_words=2)` — балансировка чанков
- `build_ass(events, style)` — генерирует ASS заголовок + события
- `canonical_text_from_storyboard(sb)` — собирает текст из всех dialogue-клипов
- `lang_from_storyboard(sb)` — определяет язык для Whisper

**Читает:** WAV аудиофайл, storyboard.json  
**Пишет:** `.ass` файл субтитров  
**Сеть:** нет (Whisper работает локально)

**⚠ Подводные камни:**
- Загрузка Whisper модели при первом запуске — блокирующая операция 10–30 с
- Если alignment ratio < 0.5 (transcript расходится с canonical на >50%) — exit 1. Причина: голос другого персонажа или сильно отредактированный текст
- `voice-final.wav` должен быть ≥60% длины `main_dur` — иначе exit 1 (детектирует битые сборки). При ре-рендере отдельных сцен этот guard может ложно срабатывать
- CJK (китайский, японский) работает хуже — Whisper иногда путает тайминги при syllable-based языках
- Интерполяция для ненайденных слов — если Whisper пропустил слово, тайминг угадывается, возможен дрейф

---

### `overlays.py` 🟡

**Роль:** Генерирует `drawtext` FFmpeg-фильтры для графических оверлеев (заголовки, HUD, плашки). Вызывается editor-агентом.

**Запуск:**
```bash
python tools/overlays.py storyboard.json \
    [--scene-index N | --emit-all | --channel-bug] \
    [--bug-png PATH --bug-input-label "[5:v]"] \
    [--workdir build] \
    [--input-label "[v3pre]" --output-label "[v3]"] \
    [--check]
```

**Типы оверлеев:**

| Тип | Описание |
|-----|----------|
| `title` | Заголовок сцены (bottom-center, y=520) |
| `hud_counter` | Счётчик (число + единицы) |
| `outcome_plate` | Итоговая плашка (WIN / LOSE / и т.п.) |
| `rank_number` | Номер в рейтинге |
| `item_name` | Название предмета |
| `slogan` | Слоган |
| `disclaimer` | Мелкий текст-дисклеймер |

**Ключевые функции:**
- `resolve_font(key_or_path)` — ищет шрифт по логическому ключу (ULT/TRJ/MED/ARI/IMPACT/MONT_BLACK/BEBAS) с fallback на Impact. Пути хардкожены под macOS
- `build_overlay_drawtexts(scene, scene_idx, workdir, input_label, output_label)` — конвертирует spec оверлея в цепочку drawtext фильтров
- `_enable_expr(start, end)` — выражение `between(t,...)` для FFmpeg enable
- `_alpha_expr(start, fade_dur)` — ramp для fade-in
- `_write_textfile(text, path)` — записывает .txt для drawtext textfile= (обходит проблему спецсимволов)
- `channel_bug_fragment(png, input_label, output_label)` — PNG оверлей логотипа канала

**Читает:** storyboard.json  
**Пишет:** temp `.txt` файлы в `build/ovl-s{idx}-{oi}-{li}.txt`  
**Сеть:** нет

**⚠ Подводные камни:**
- Шрифты захардкожены под macOS (`/Library/Fonts/`, `/System/Library/Fonts/`). На Linux/CI — fallback на Impact без предупреждения
- Temp `.txt` файлы не удаляются — накапливаются в `build/` со временем
- `--check` режим показывает отсутствующие шрифты — без него ошибка обнаружится только при запуске FFmpeg (поздно)
- Строки с `\n` разбиваются на несколько drawtext — каждая строка отдельный фильтр с ручным y-смещением

---

## API-справочники (документация, не скрипты)

---

### `fal-ai.md` 🟢

Основной справочник по fal.ai API. Читается sub-агентами (storyboarder, animator, sound).

**Покрывает:**
- Nano Banana 2 — T2I / I2I с chain reference. $0.08/img
- GPT Image 1 — альтернативный маршрут только по предварительному/явному разрешению; не automatic fallback. $0.02/img  
- MiniMax H3 Max I2V — $0.08/s at 768P (5 s ≈ $0.41 on the returned length); plain I2V route (redcon, item-story, character-story, in-game-pov, wild-documentary, top-list, fake-ad, what-if-real-life I2V scenes, serial-drama action clips)
- MiniMax H3 Max face reference (`reference-to-video`, route `minimax.h3max.r2v`) — $0.08/s at 768P (5 s ≈ $0.41); dual-style only (start frame + headshot `reference_image_urls`)
- MiniMax H3 Max Turbo lip-sync — $0.04/s at 768P (5 s ≈ $0.21); what-if-real-life and serial-drama dialogue and the fun-news, special-report and streettalk talking heads only, never plain clips
- Kling v3 Standard I2V — $0.084/с без audio, $0.126/с с audio. multi_prompt, voice_ids, elements — historical/alternate: not the active route of any of the ten H3 formats (serial-drama and dual-style moved to H3 on 15 Oct 2026)
- Kling v2.6 Pro — отдельный format/user-selected I2V route; не automatic fallback
- Veo 3 — T2V / I2V, $1.60–$3.20 за 8-секундный клип
- MiniMax TTS — Speech 2.8-HD, $0.10/1k символов
- MiniMax TTS + exact-format Chatterbox; ElevenLabs TTS запрещён, ElevenLabs Sound Effects разрешён только для SFX
- Kling Lipsync — audio-to-video lip-sync
- Kling Avatar v2 — image + audio → avatar видео. $0.056/с (news and gameplay-ai-avatar only; fun-news, special-report and streettalk moved to H3 lip-sync)

**Критичные правила из документа:**
- fal.media URL — временные, скачивать немедленно
- Polling base path = первые 2 сегмента endpoint (не полный путь с версией)
- Kling: `generate_audio` выбирается оркестратором по storyboard + format playbook до создания exact payload; native-audio режимы сохраняют оплаченный audio, silent-режимы используют `false`
- H3 (Max and Max Turbo) always returns sound (no audio switch): the editor uses clip sound only when the scene's `scene_video_audio` is `"native"`; `expect.audio` is never `"forbidden"`
- `multi_prompt[].prompt`: provider hard limit is 512 serialized UTF-8 bytes, not Unicode character count. Measure `len(prompt.encode("utf-8"))`; exact format playbooks may require a lower safety ceiling (the historical Kling `dual-style-v3`: ≤400 bytes).
- Elements: максимум 3 на запрос
- Параллельных запросов: не более 3

---

### `ffmpeg-api.md` 🟢

Справочник FFmpeg Cloud API (ffmpeg-api.com). Читается editor-агентом.

**Ключевые ограничения:**
- ✅ Ken Burns (zoompan) — работает
- ❌ Concat через filter_complex с `[]` и `;` — API отклоняет ("Invalid characters")
- ❌ R2 presigned URLs из результата — нельзя переиспользовать как input (403)
- ❌ AI endpoint `/ai/ffmpeg/process` — нестабилен на сложных задачах

**Рекомендованный паттерн:**
```
FFmpeg Cloud API → Ken Burns отдельных изображений
Local ffmpeg → concat + audio mix (filter_complex)
Supabase → upload final.mp4
```

---

## Пост-генерация

---

### `queue/log-video.sh` 🟢

**Роль:** Регистрирует готовое видео в каталоге `video_agent_runs`. Вызывается manager-ом после Phase 5 (после явного OK от пользователя).

**Запуск:**
```bash
./queue/log-video.sh \
    --game GAME_TAG \
    --title "идея" \
    --format FORMAT \
    --video-url "https://..." \
    [--youtube-url "https://..."] \
    [--yt-publish-at "2026-06-20T20:59:00Z" | --immediate]
```

**Что делает:** UPSERT в `video_agent_runs` по `output_video_url` — создаёт или обновляет запись.

Если передан `--youtube-url`, скрипт требует `--yt-publish-at` (реальный `SCHEDULED_FOR` из `youtube-upload.sh`) или `--immediate` (ролик реально ушёл public сразу) — без одного из них ошибка, а не тихий фоллбэк на `now()`.

**Читает:** `.env` (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)  
**Пишет:** Supabase таблица `video_agent_runs`

**⚠ Подводные камни:**
- Без `--video-url` — молча падает (обязательный параметр)
- UPSERT по `output_video_url` — повторный вызов с тем же URL обновит запись, не создаст дубль

---

### `queue/youtube-upload.sh` 🟠

**Роль:** Загружает `final.mp4` на YouTube через Data API v3. Поддерживает несколько каналов и отложенную публикацию.

**Запуск:**
```bash
./queue/youtube-upload.sh \
    [--channel CHANNEL_NAME] \
    [--publish-date "2026-06-20" | --publish-at "2026-06-20T20:17:00Z" | now] \
    [--thumbnail thumb.png] \
    final.mp4 "Заголовок" "Описание" [private|public] [теги]
```

**Что делает:**
1. Обновляет OAuth2 access token через refresh token
2. В auto-schedule проверяет занятость даты; для auto и `--publish-date` выбирает случайную минуту в окне 22:00–23:50 МСК
3. Resumable upload → YouTube
4. Опционально загружает thumbnail
5. Возвращает YouTube URL + `SCHEDULED_FOR=ISO8601`

**Каналы:** задаются через `YOUTUBE_REFRESH_TOKEN_<CHANNEL>` и `YOUTUBE_CHANNEL_ID_<CHANNEL>` в `.env`  
**Читает:** `.env` (YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN[_CHANNEL])  
**Пишет:** загружает видео на YouTube

**⚠ Подводные камни:**
- `--publish-date YYYY-MM-DD` закрепляет дату, но случайно выбирает время 22:00–23:50 МСК; `SCHEDULED_FOR` возвращает фактический UTC timestamp
- Без `--publish-date` и `--publish-at` автоматически находит ближайшую свободную дату и случайное время в том же окне
- Resumable upload не возобновляется при падении — при сетевой ошибке нужно запускать заново
- Verifies channel ID только если `YOUTUBE_CHANNEL_ID_<CHANNEL>` задан в env

---

### `queue/upload-asset.sh` 🟢

**Роль:** Загружает ассеты игры (character ref, avatar, location, CTA, gameplay) в Supabase Storage и регистрирует их в `game_assets`. Используется при добавлении нового персонажа или игры.

**Запуск:**
```bash
# Character sheet:
./queue/upload-asset.sh --kind character --game GAME --slug picard [--variant prophet] file.png

# Avatar ref (для Kling Avatar):
./queue/upload-asset.sh --kind avatar --game GAME --slug q file.png

# Gameplay клип:
./queue/upload-asset.sh --kind gameplay --game GAME clip.mp4

# CTA/opener:
./queue/upload-asset.sh --kind branding --game GAME --name cta cta.mp4
```

**Структура хранения:**
```
assets/{GAME}/characters/{slug}/sheet.png
assets/{GAME}/characters/{slug}/variants/{variant}.png
assets/{GAME}/characters/{slug}/avatar.png
assets/{GAME}/locations/{slug}.png
assets/{GAME}/branding/{name}.{ext}
assets/{GAME}/gameplay/{name}.mp4
```

**Читает:** локальный файл  
**Пишет:** Supabase Storage + строка в `game_assets` (кроме episode-scene/episode-tts — только Storage)

**⚠ Подводные камни:**
- Нет проверки существования — при повторной загрузке того же пути тихо перезапишет (upsert)
- `episode-scene` и `episode-tts` не пишут строку в `game_assets` — только загружают файл

---

## Игровые данные / ассеты

### `growtopia_parser.py` 🟢

**Роль:** Парсит спрайты NPC из Growtopia Fandom-вики (`Category:NPCs`) через MediaWiki API (без HTML-скрейпинга; только stdlib + `certifi`). Складывает сырой спрайт в `games/growtopia/assets/refs/{slug}.*` и с `--preprocess` — готовый под NB2 PNG в `refs/nb2/{slug}.png` (первый кадр + nearest-neighbor апскейл до ~512px, чтобы сохранить резкие пиксели). Пишет манифест `refs/npcs.json` (name → file → source_url → wiki_page) — заготовка под будущую заливку в Supabase.

**Запуск:**
```bash
python3 tools/growtopia_parser.py --dry-run                 # список NPC, без скачивания
python3 tools/growtopia_parser.py --preprocess              # полный прогон + NB2-версии
python3 tools/growtopia_parser.py --limit 1 --preprocess    # тест на одном
```

**Выбор картинки (важно):** канонический игровой спрайт берётся из `<span class="growsprite">` карточки, чей заголовок совпадает с именем NPC (window-crop из общего атласа `ItemSprites.png`). Если такого нет — только файл со словом `sprite` в имени, иначе `NO IMAGE`. Промо-рендеры, UI-диалоги, постеры и юзер-фото сознательно **не** берутся (мусор для пиксель-рефа). Известные wiki-плейсхолдеры (баннер «REPORT») отсекаются по md5 (`JUNK_HASHES`).

**Читает:** Growtopia Fandom API  
**Пишет:** локальные файлы в `games/growtopia/assets/refs/` (картинки `.webp/.png` в git не попадают — игнор `*.png`/`*.webp`; в git идёт только `npcs.json`)

**⚠ Подводные камни:**
- NPC-боссы/квестовые без atlas-спрайта (Growganoth, Buddy, Dr. Destructo, бот-левелы) → `NO IMAGE`, при необходимости добавляются вручную
- Fandom отдаёт WebP под именем `.PNG` — расширение определяется по магическим байтам, не по URL
- Resume-friendly: уже скачанные (по манифесту) пропускаются

---

## Быстрая таблица

| Скрипт | Важность | Вызывается | Мутирует |
|--------|----------|------------|----------|
| `fal_runner.py` | 🟠 | storyboarder-агент | NB2 job state + PNG + Supabase |
| `kling_runner.py` | 🟠 | animator-агент | format-agnostic fal video payload state + MP4 + Supabase |
| `still_shot.py` | 🟢 | animator agent (`motion: "still"` scenes) | one local scene MP4, $0, no network |
| `silent_audio.py` | 🟢 | animator agent (H3 Max clips with `scene_video_audio: "none"`) | silent MP3 data URI for `target_audio_url` (`--out` file only), $0, no network |
| `add_subtitles.py` | 🟠 | editor-агент | .ass файл |
| `overlays.py` | 🟡 | editor-агент | temp .txt файлы |
| `log-video.sh` | 🟢 | manager (после OK) | Supabase video_agent_runs |
| `youtube-upload.sh` | 🟠 | manager (после OK) | YouTube + Supabase |
| `upload-asset.sh` | 🟢 | вручную | Supabase Storage + game_assets |
| `growtopia_parser.py` | 🟢 | вручную (сетап тайтла) | локальные рефы Growtopia + `npcs.json` |
| `fal-ai.md` | 🟢 | справочник sub-агентов | — |
| `ffmpeg-api.md` | 🟢 | справочник editor-агента | — |
