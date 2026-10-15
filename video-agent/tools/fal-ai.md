# fal.ai API Reference

Справочник по API fal.ai для генерации изображений, видео и озвучки.

---

## Аутентификация

Все запросы требуют заголовок:
```
Authorization: Key $FAL_KEY
```

Переменная `FAL_KEY` должна быть установлена в окружении перед запуском.

---

## 1. Nano Banana 2 — основная модель генерации изображений

**Стоимость:** ~$0.08 за изображение

> **Основная модель для всех сцен, character refs, bg-assets.**
>
> **Storyboarder execution rule:** все NB2 text/edit вызовы выполняются только через `tools/fal_runner.py` по job contract из `tools/SCRIPTS.md`. Storyboarder не исполняет curl-примеры, submit/poll/download snippets или endpoint вручную. Код ниже — reference-only для сопровождения runner; при расхождении executable allowlist/state machine runner имеет приоритет.

### 1a. Text-to-Image (без референса — для character references)

**Endpoint:** `https://queue.fal.run/fal-ai/nano-banana-2`
**Метод:** POST (асинхронный — нужен polling)

> **Используй этот endpoint для генерации character references** (нет входного изображения). Поле `image_urls` НЕ передаётся.

### 1b. Image-to-Image / Edit (с референсом — для сцен)

**Endpoint:** `https://queue.fal.run/fal-ai/nano-banana-2/edit`
**Метод:** POST (асинхронный — нужен polling)

> **Используй этот endpoint для генерации сцен** с chain reference (image_urls обязателен).

### Raw HTTP запрос (reference-only; Storyboarder не исполняет)

```bash
curl -s -X POST "https://queue.fal.run/fal-ai/nano-banana-2/edit" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Star Trek cinematic 3D animation, Worf in dramatic pose, Klingon warrior armor, dark council chamber, 9:16 vertical",
    "image_urls": ["https://supabase.../character-ref.png"],
    "aspect_ratio": "9:16",
    "output_format": "png",
    "resolution": "1K",
    "safety_tolerance": "5"
  }'
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Текстовое описание (мин 3 символа, макс 50000) |
| `image_urls` | array of strings | Нет | URL-ы референсных изображений для chain reference консистентности. Runner `nb2.edit` принимает 1–4 уникальных permanent HTTPS URL; более строгий format/role limit всё равно действует. Для `nb2.text` поле нужно **полностью опустить** — пустой `[]` вызывает ошибку |
| `aspect_ratio` | enum | Нет | `"9:16"` для вертикального видео. Варианты: "1:1", "16:9", "9:16", "4:3", "3:4" и др. По умолчанию: "auto" |
| `num_images` | integer | Нет | 1-4, по умолчанию 1 |
| `output_format` | enum | Нет | "jpeg", "png", "webp". По умолчанию "png" |
| `resolution` | enum | Нет | "0.5K", "1K", "2K", "4K". По умолчанию "1K" |
| `safety_tolerance` | enum | Нет | "1"-"6", по умолчанию "4". Для игрового контента ставь "5" |
| `seed` | integer | Нет | Для воспроизводимости результатов |

### Ответ

```json
{
  "images": [
    {
      "url": "https://fal.media/files/abc123/image.png",
      "width": 1080,
      "height": 1920,
      "content_type": "image/png"
    }
  ]
}
```

### Raw polling/download (reference-only; в pipeline это делает runner)

Оба endpoint'а (с `/edit` и без) — **асинхронные**. Нужен polling.

```bash
# 1. Отправь запрос → получи request_id
REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')

# 2. Polling каждые 10 секунд
while true; do
  STATUS=$(curl -s "https://queue.fal.run/fal-ai/nano-banana-2/requests/$REQUEST_ID/status" \
    -H "Authorization: Key $FAL_KEY" | jq -r '.status')
  case "$STATUS" in
    "COMPLETED") break ;;
    "FAILED") echo "FAILED"; exit 1 ;;
    *) sleep 10 ;;
  esac
done

# 3. Получи результат
RESULT=$(curl -s "https://queue.fal.run/fal-ai/nano-banana-2/requests/$REQUEST_ID" \
  -H "Authorization: Key $FAL_KEY")
IMAGE_URL=$(echo "$RESULT" | jq -r '.images[0].url')
curl -s -o scene-1.png "$IMAGE_URL"

# 4. Проверь что файл скачался (>1000 bytes)
ls -la scene-1.png
```

> **ВАЖНО:** URL для polling/результата всегда `fal-ai/nano-banana-2/requests/{ID}` — без `/edit`, даже если запрос был на `/edit` endpoint.

### Chain Reference Usage

```bash
# Сцена 1 (только референс персонажа):
"image_urls": ["$CHARACTER_REF_URL"]

# Сцена 2+ (референс персонажа + предыдущая сцена):
"image_urls": ["$CHARACTER_REF_URL", "$PREV_SCENE_URL"]
```

---

## 1c. GPT Image 1 — справочник альтернативного маршрута

**Endpoint:** `https://queue.fal.run/fal-ai/gpt-image-1/text-to-image`
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** ~$0.02 за изображение

> Автоматически не использовать. Этот endpoint допустим только если он выбран для отдельного запуска заранее или явно разрешён пользователем после остановленного запуска. Ошибка Nano Banana 2 не разрешает переключение.

### Запрос

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/gpt-image-1/text-to-image" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Star Trek cinematic 3D animation, Worf in dramatic pose, Klingon warrior armor, dark council chamber, 9:16 vertical",
    "image_size": "1024x1536"
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Текстовое описание |
| `image_size` | enum | Нет | `"auto"`, `"1024x1024"`, `"1536x1024"`, `"1024x1536"`. Для 9:16 используй `"1024x1536"` |

### Polling и получение результата

```bash
STATUS=$(curl -s "https://queue.fal.run/fal-ai/gpt-image-1/requests/$REQUEST_ID/status" \
  -H "Authorization: Key $FAL_KEY" | jq -r '.status')

RESULT=$(curl -s "https://queue.fal.run/fal-ai/gpt-image-1/requests/$REQUEST_ID" \
  -H "Authorization: Key $FAL_KEY")

IMAGE_URL=$(echo "$RESULT" | jq -r '.images[0].url')
curl -s -o scene-1.png "$IMAGE_URL"
```

### Ответ

```json
{
  "images": [
    {
      "url": "https://v3b.fal.media/files/...",
      "content_type": "image/png",
      "width": 1024,
      "height": 1536
    }
  ]
}
```

---

## 2. Kling v3 Standard — I2V route for `multi_prompt` / `voice_ids` / `elements` (historical/alternate; no active H3 format uses it)

**Endpoint:** `https://queue.fal.run/fal-ai/kling-video/v3/standard/image-to-video`
**Route in `tools/video_routes.json`:** `kling.v3.standard.i2v`
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** $0.084/сек без аудио (5s = $0.42, 10s = $0.84) | $0.126/сек с аудио (5s = $0.63, 10s = $1.26)

> **Which route (15 Oct 2026):** plain image-to-video for `redcon`, `item-story`, `character-story`, `in-game-pov`, `wild-documentary`, `top-list`, `fake-ad`, the I2V scenes of `what-if-real-life` and the action clips of `serial-drama` runs on **MiniMax H3 Max** (§2y, `minimax.h3max.i2v`); `what-if-real-life` and `serial-drama` dialogue runs on **H3 Max Turbo** lip-sync (`minimax.h3max.turbo.i2v`, §2y "H3 Max Turbo lip-sync"); `dual-style` runs on **H3 Max reference-to-video** (`minimax.h3max.r2v`, §2y "H3 Max face reference"). H3 Max Turbo is never used for plain clips. Kling v3 Standard is therefore **not the active route of any of these ten formats**; it stays documented here as the historical/alternate route for `multi_prompt`, `voice_ids` and `elements`, and for a playbook that still names a Kling I2V clip (e.g. the `fun-news` / `streettalk` openers). The Kling Avatar formats keep Kling Avatar v2 (§7) and `motion-dance` keeps Kling Motion Control. The format playbook declares the route; the animator never switches route after the run starts, and there is no automatic fallback between them.

> Используй только когда этот endpoint выбран Scenarist/Manager/Animator для текущего запуска. Они определяют duration, request shape и `generate_audio` по сценарию и format playbook, затем передают уже готовый provider payload runner'у.
>
> **Execution rule:** все v3 Standard I2V формы выполняются через schema-v3 `tools/kling_runner.py`. Полный `payload` (`prompt` или `multi_prompt`, `voice_ids`, `elements`, будущие provider fields) передаётся без изменений и без format-specific решений внутри runner. Curl/poll/download ниже — reference-only. Другие инструменты выбирает оркестратор; совместимый fal queue endpoint добавляется в `tools/video_routes.json`, другой protocol использует отдельный adapter.

### Отправка запроса

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/kling-video/v3/standard/image-to-video" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Worf stands at the bridge console, turns slowly toward camera, jaw set with determination, low-angle push-in, dramatic lighting",
    "start_image_url": "https://supabase.../scene-1.png",
    "duration": "5",
    "generate_audio": false,
    "negative_prompt": "blur, distort, low quality, static, morphing faces"
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Описание анимации: камера, позиции, действия. Технический, не литературный |
| `start_image_url` | string | Да | URL начального кадра (постоянный Supabase URL) |
| `end_image_url` | string | Нет | API parameter exists, but this pipeline forbids it and never creates end frames |
| `multi_prompt` | list | Нет | Массив шотов для одного непрерывного клипа из одного `start_image_url`. См. §2d и `animator.md §5a`. Передавать ЛИБО `prompt`, ЛИБО `multi_prompt`, не оба |
| `duration` | enum | Нет | `"3"`–`"15"` секунд, по умолчанию "5" |
| `generate_audio` | boolean | Нет | Follow the exact format: `true` for native dialogue with `voice_ids` (the historical serial-drama route) or native ambience; otherwise as declared by the format |
| `cfg_scale` | float | Нет | Сила следования промпту, 0.0–1.0, по умолчанию 0.5 |
| `negative_prompt` | string | Нет | Что исключить |
| `elements` | list | Нет | Кастомные персонажи/объекты, которые можно ввести в кадр и звать из промпта (`@Element1`, `@Element2`). Каждый элемент: `frontal_image_url` + `reference_image_urls` (**обязателен, ≥1 URL**) ЛИБО `video_url` (только 1 video-элемент на запрос). Все URL — постоянные Supabase. ✅ burn-tested 2026-06-01, работает с `multi_prompt` — см. §2c |

### Polling статуса

> ⚠️ **КРИТИЧНО:** Polling и результат — по **базовому 2-сегментному пути** `fal-ai/kling-video`, НЕ по полному пути submit endpoint.

```bash
while true; do
  STATUS_RESPONSE=$(curl -s "https://queue.fal.run/fal-ai/kling-video/requests/$REQUEST_ID/status" \
    -H "Authorization: Key $FAL_KEY")

  STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')

  case "$STATUS" in
    "COMPLETED") break ;;
    "FAILED") echo "FAILED"; exit 1 ;;
    *) sleep 15 ;;
  esac
done
```

### Получение результата

```bash
RESULT=$(curl -s "https://queue.fal.run/fal-ai/kling-video/requests/$REQUEST_ID" \
  -H "Authorization: Key $FAL_KEY")

VIDEO_URL=$(echo "$RESULT" | jq -r '.video.url')
curl -s -o scene-1.mp4 "$VIDEO_URL"
```

### Ответ

```json
{
  "video": {
    "url": "https://fal.media/files/abc123/output.mp4",
    "content_type": "video/mp4",
    "file_name": "output.mp4",
    "file_size": 1234567
  }
}
```

### 2c. `elements` — ввод персонажей/объектов в кадр

> ✅ **Burn-tested 2026-06-01 (v3 Standard, `elements` + `multi_prompt` вместе, $0.50).** Подтверждено: комбинация принимается и рендерит. Выводы теста — в конце секции.

`multi_prompt` тянет всё из одного `start_image_url` → новые сущности в кадре сами не появляются. Чтобы ввести персонажа/объект, которого нет на стартовом кадре, передай его как `element` и сошлись из промпта через `@Element1`.

Схема одного элемента (`KlingV3ComboElementInput`):

```json
"elements": [
  {
    "frontal_image_url": "https://supabase.../worf-front.png",
    "reference_image_urls": [
      "https://supabase.../worf-side.png",
      "https://supabase.../worf-3q.png"
    ]
  }
]
```

В `prompt` (или в промпте конкретного шота `multi_prompt`): `"@Element1 enters through the airlock door"`.

| Поле | Тип | Описание |
|------|-----|----------|
| `frontal_image_url` | string | Главный (фронтальный) вид элемента |
| `reference_image_urls` | array | **ОБЯЗАТЕЛЕН при `frontal_image_url`: ≥1 URL.** 1–3 доп. ракурса. Если чистый ракурс только один — допустимо передать тот же URL повторно (fal.ai принимает дубликат), но идентичность будет слабее |
| `video_url` | string | Видео-референс элемента. **Только 1 video-элемент на запрос** |
| `voice_id` | string | Привязка голоса (только для video-элементов) |

- **Максимум 3 элемента на запрос** (лимит Kling 3.0 для video; fal.ai-схема `maxItems` не enforce'ит, но Kling отвалит на отложенной валидации). На элемент: 1 фронталь + до 3 ракурсов (макс 4 картинки). Видео-элемент — только 1.
- `elements` задаётся **на уровне запроса**, не на уровне шота. Каждый шот `multi_prompt` может звать любой `@ElementN` в своём `prompt`.
- Референсы элемента (фронталь + ракурсы) генерит Storyboarder как character-sheet-набор и грузит в Supabase — см. `storyboarder.md §15.2`.
- Все URL — постоянные Supabase, НЕ fal.media.

**⚠️ Валидация `elements` отложенная (deferred):** ошибки схемы возвращаются НЕ на submit (там 200/IN_QUEUE), а при fetch результата — в поле `detail`, и джоба «завершается» за ~16с без `video.url`. Всегда проверяй `video.url` в результате; если его нет — смотри `detail`. (Это иначе, чем `prompt`+`multi_prompt` вместе → там немедленный 422.)

**Выводы burn-test 2026-06-01 (Spock/Kirk, 3 шота × 2с):**
- ✅ **Element для крупного плана лица в финальном шоте работает отлично** — чинит EP6-баг «третий шот дрейфует в реализм»: заякоренное элементом лицо держит Pixar-стиль и on-model.
- ⚠️ **Идентичность элемента в маленькой/перекрытой области кадра слабая** (лицо Кирка в иллюминаторе под красным светом прочиталось обобщённо). Для надёжной узнаваемости element должен занимать заметную площадь кадра; для мелких/затенённых появлений идентичность не гарантируется.
- `reference_image_urls` обязателен (≥1). Дубликат фронтали как ракурс принимается, но это stopgap — для identity-critical планов давай реальный второй ракурс.

### 2d. `multi_prompt` — несколько шотов в одном вызове

Один непрерывный MP4 из N последовательных шотов от одного `start_image_url`. Полные правила, лимиты (≤15s/вызов, ≤6 шотов) и chaining для >15s — в `animator.md §5a`. Здесь — только напоминание схемы:

```json
{
  "start_image_url": "https://supabase.../scene-2.png",
  "multi_prompt": [
    {"prompt": "шот 1 …", "duration": "3"},
    {"prompt": "шот 2 …", "duration": "3"}
  ],
  "shot_type": "customize",
  "duration": "6",
  "generate_audio": false
}
```

- Передавать **ЛИБО `prompt`, ЛИБО `multi_prompt`**, не оба (иначе 422).
- `end_image_url` ЗАПРЕЩЁН вместе с `multi_prompt` (422).
- Каждый шот: `prompt` (обяз.) + `duration` (enum `"1"`–`"15"`). Сумма длительностей шотов = верхнему `duration`.
- **Промпт каждого шота ≤512 сериализованных UTF-8 байт (хард-лимит Kling), не Unicode-символов.** Валидация отложенная: over-limit шот проходит submit, но падает 422 в `detail` при fetch. До preflight измеряй `len(prompt.encode("utf-8"))`; формат может задавать меньший safety ceiling (исторический Kling `dual-style-v3`: ≤400 байт).

---

## 2y. MiniMax H3 Max — image-to-video (plain I2V route)

**Status:** the plain I2V route for `redcon`, `item-story`, `character-story`, `in-game-pov`, `wild-documentary`, `top-list`, `fake-ad`, the I2V scenes of `what-if-real-life` and the action clips of `serial-drama`. H3 Max Turbo (`minimax.h3max.turbo.i2v`) is the lip-sync route for `what-if-real-life` and `serial-drama` dialogue only ("H3 Max Turbo lip-sync" below), so both formats are all-H3; `dual-style` uses H3 Max reference-to-video ("H3 Max face reference" below). Decided 12 Oct 2026 after the cost trials in `trials/2026-10-cost-trials/`: plain clips moved from H3 Max Turbo to H3 Max after Test 6, where Turbo made characters open their mouths as if talking while the narrator spoke, plus some weird animations (Test 6b re-ran the same scenes on H3 Max). `serial-drama` (Test 9) and `dual-style` (Test 8) moved from Kling v3 Standard on 15 Oct 2026. The Kling Avatar formats keep Kling Avatar v2 (§7) until each has passed one pilot.

**Endpoint:** `https://queue.fal.run/minimax/h3-max/image-to-video`
**Polling base:** `https://queue.fal.run/minimax/h3-max` (first 2 segments, like every fal endpoint)
**Route in `tools/video_routes.json`:** `minimax.h3max.i2v` (result path `["video", "url"]`)
**Method:** POST through schema-v3 `tools/kling_runner.py` (`route: "minimax.h3max.i2v"`) — never raw curl. The runner is model-agnostic; no runner code change. Template: `tools/examples/minimax-h3-max-scene-video.job.json`.
**Cost:** $0.08/s at 768P (fal promo $0.048/s until 15 Oct 2026). Assume billing on the **returned** length: 3 s ≈ $0.25, 5 s ≈ $0.41, 10 s ≈ $0.83. Kling v3 Standard for comparison: $0.084/s audio off (5 s = $0.42), $0.126/s audio on (5 s = $0.63).

### Payload (exact field set; nothing else)

H3 Max Turbo lip-sync dialogue clips use the same field set plus exactly one field, `target_audio_url` ("H3 Max Turbo lip-sync" below). A plain H3 Max clip whose sound is discarded (`scene_video_audio: "none"`) also adds exactly one field: a **silent** `target_audio_url` ("Silent `target_audio_url`" below).

```json
"payload": {
  "prompt": "<motion_prompt>",
  "image_url": "<permanent Supabase URL of the scene still>",
  "duration": 5,
  "resolution": "768P",
  "prompt_expansion_mode": "disabled"
}
```

| Parameter | Type | Value |
|---|---|---|
| `prompt` | string | Motion prompt, ≤512 serialized UTF-8 bytes; rules below |
| `image_url` | string | Permanent Supabase URL of the scene still (never `fal.media`). The field is `image_url`, not Kling's `start_image_url` |
| `duration` | number | The scene's `duration_sec` as a **number** (`5`, not Kling's string `"5"`). H3 accepts 0.92–15 s |
| `resolution` | string | `"768P"` |
| `prompt_expansion_mode` | string | `"disabled"` — keeps H3 from rewriting the animator's prompt (the result's `expanded_prompt` stays null) |

### `expect`

```json
"expect": {
  "kind": "video",
  "duration_seconds": 5,
  "duration_tolerance_seconds": 0.8,
  "audio": "optional",
  "min_bytes": 100000,
  "min_width": 600,
  "min_height": 1000,
  "orientation": "portrait"
}
```

- `duration_seconds` = the scene's `duration_sec`; tolerance `0.8` because H3 can return up to ~0.7 s more than requested.
- `audio`: `"required"` when the format uses clip sound (`in-game-pov`, `wild-documentary`, what-if physical gags, `serial-drama` action clips, `dual-style`, and every lip-sync clip), `"optional"` when it does not. **Never `"forbidden"`**: H3 always returns a soundtrack, so a forbidden-audio job fails validation after the clip is paid for.
- Whether the editor uses the clip's sound is decided by the scene's `scene_video_audio` (`"native"` / `"none"`, written by the animator), not by whether the file has an audio stream.

### Output (measured on 33 H3 Max clips in Test 2, Oct 2026; H3 Max Turbo matches)

- 768×1344, 24 fps, AAC 32 kHz stereo; **always** has an audio stream (silent, about −91 dB, when the job sent a silent `target_audio_url`).
- Runs slightly long: 5.184 s for 5 s, 3.072 s for 3 s (up to ~0.7 s over). The editor trims `minimax.*` clips to `duration_sec` during normalization, never below it.
- 768×1344 (4:7) is slightly wider than 9:16; the editor's fill-and-crop scaling for portrait clips gives a clean 1080×1920 with no bars.
- No content refusals on Genshin Impact or Star Trek characters (33 H3 Max and 66 H3 Max Turbo trial clips; unlike Seedance, §2z).
- Response shape is the same as Kling (`{"video": {"url": "https://...fal.media/...", ...}}`); download immediately — the runner does this. Polling is the generic fal queue pattern (see the polling table below).

### Prompt rules

- There is no `negative_prompt`: what used to go there becomes **at most two short plain sentences at the end of `prompt`**, for example `No music, no voices.` / `Faces and costumes stay unchanged.` / `Text stays sharp and unchanged.`. **Whenever a character's face is visible outside a lip-sync scene, one of the two is always `Mouth stays closed; no talking.`** (H3 otherwise invents speech and moves the lips; see animator.md §2a)
- Formats that keep clip sound (`in-game-pov`, `wild-documentary`, `serial-drama` action clips, `dual-style`) end every prompt with their sound clause (`No music, no voices.` or the format's ambient-only wording, e.g. `Diegetic ambience only, no music, no voices.` in serial-drama, `Diegetic ambience only, no music.` in dual-style).
- Keep the prompt ≤512 UTF-8 bytes (measure `len(prompt.encode("utf-8"))`). Plain sentences only — no `++emphasis++` syntax.
- Micro-motion guidance (one clear camera move, small settling motions, nothing that needs new anatomy) stays good practice; phrase it model-neutrally.
- Multi-beat action (e.g. `redcon`): write the beats as one staged prompt (`first …, then …`) in a 5–7 s clip. Untested on H3.

### What H3 lacks (compared with Kling v3 Standard)

- No `negative_prompt`, no `generate_audio` switch (sound is always on), no `multi_prompt`, no `voice_ids`, no `elements`, no `shot_type`, no `end_image_url` use (the pipeline never creates end frames), no `++emphasis++` syntax.
- The formats that used them moved anyway: `serial-drama` replaces Kling multi-shot voiced dialogue with one H3 lip-sync clip per exchange on our TTS, and `dual-style` replaces `elements` face-lock with the H3 Max face reference (`reference_image_urls`). `reference_image_urls` and `aspect_ratio` exist only on the face-reference endpoint.
- **One model per episode:** all animated clips of an episode use the playbook's one I2V route. The single exception: H3 Max Turbo lip-sync dialogue clips may sit next to H3 Max action clips (`what-if-real-life`, `serial-drama`), as Kling Avatar dialogue clips sit next to the I2V clips where a playbook declares both. Still shots (`tools/still_shot.py`, `$0`) are not a model.

### Silent `target_audio_url` (H3 Max clips whose sound is discarded)

**Rule:** every plain H3 Max clip (`minimax.h3max.i2v`) whose clip sound is discarded (`scene_video_audio: "none"`: `redcon`, `item-story`, `character-story`, `top-list`, `fake-ad`, and the `monologue` / `inner-thought` / animated title-card scenes of `what-if-real-life`) carries a silent `target_audio_url` of the requested `duration`. Clips whose own sound is used (`scene_video_audio: "native"`: `wild-documentary`, `in-game-pov`, what-if physical gags, `serial-drama` action clips; `dual-style` face-reference clips too) do not: they keep H3's soundtrack and their sound clause. `Mouth stays closed; no talking.` stays in the prompt; lip-sync clips keep their TTS `target_audio_url`.

**Why:** H3 always writes its own soundtrack and invents speech for a visible face, so silent characters move their lips. Given an audio track through `target_audio_url`, H3 moves the lips to that track; a silent track keeps them closed. Test 6b (`trials/2026-10-cost-trials/`): 30 H3 Max clips in silent-clip scenes were sent with a silent `target_audio_url` (a base64 data URI of a silent MP3); all 30 came back with a silent soundtrack (about −91 dB), and the user approved H3 Max for production.

```json
"payload": {
  "prompt": "<motion_prompt>",
  "image_url": "<permanent Supabase URL of the scene still>",
  "target_audio_url": "data:audio/mpeg;base64,<silent MP3 of `duration` seconds>",
  "duration": 5,
  "resolution": "768P",
  "prompt_expansion_mode": "disabled"
}
```

| Parameter | Type | Value |
|---|---|---|
| `target_audio_url` | string | `data:audio/mpeg;base64,...` of a silent mono 16 kHz MP3 (16 kbit/s) as long as the payload `duration`, made by `python3 tools/silent_audio.py --duration <duration_sec> --out <file>` and read into the job with `jq --rawfile` (`tools/SCRIPTS.md`). H3 accepts the data URI (2–15 s); it is not uploaded, and `kling_runner.py` checks only `http(s)` values, so it passes the string through untouched |

`duration`, `expect` (`audio "optional"`, tolerance `0.8`) and the write-back (`scene_video_audio: "none"`) stay those of the plain clip; the route stays `minimax.h3max.i2v`. Full rule: `rules/roles/animator.md` §2a.

### H3 Max Turbo lip-sync (`target_audio_url`; `what-if-real-life` and `serial-drama` dialogue)

**Endpoint:** `https://queue.fal.run/minimax/h3-max-turbo/image-to-video`
**Polling base:** `https://queue.fal.run/minimax/h3-max-turbo`
**Route in `tools/video_routes.json`:** `minimax.h3max.turbo.i2v` (result path `["video", "url"]`)

H3 Max Turbo, used only for lip-sync: the plain payload above plus one field. Lip-sync on H3 Max is untested; never send a lip-sync job to `minimax.h3max.i2v`, and never send a plain clip to Turbo. Tested in Tests 4 and 4b (`trials/2026-10-cost-trials/`): with the prompt rules below the user judged it on par with or slightly better than Kling Avatar v2 (§7), at $0.04/s against $0.056/s. Test 9 used it for two on-screen speakers in `serial-drama` (the clip's lines in one TTS file; the user chose it over Kling native voices). Templates: `tools/examples/minimax-h3-max-turbo-lipsync.job.json` (what-if), `tools/examples/minimax-h3-max-turbo-serial-dialogue.job.json` (serial-drama, the Test 9 scene 1 job).

```json
"payload": {
  "prompt": "<lip-sync prompt, rules below>",
  "image_url": "<permanent Supabase URL of the scene still>",
  "target_audio_url": "<permanent Supabase URL of the scene's TTS file (the whole dialogue exchange)>",
  "duration": 4.8,
  "resolution": "768P",
  "prompt_expansion_mode": "disabled"
}
```

| Parameter | Type | Value |
|---|---|---|
| `target_audio_url` | string | The scene's `tts_url`: the TTS file uploaded to Supabase by the Sound phase before Phase 4 (as for Avatar's `audio_url`); never `fal.media` |
| `duration` | number | The TTS file's length rounded **up** to 0.1 s (4.70 s → `4.8`), not `duration_sec` |

`expect`: `duration_seconds` = that `duration`, `duration_tolerance_seconds 0.8`, `audio "required"`, `min_bytes 100000`, `min_width 600`, `min_height 1000`, `orientation "portrait"`.

**Measured (9/9 clips, no refusals):**
- H3 rounds the length up further and pads the audio with silence: 4.8 → 5.184 s, 4.1 → 4.48 s.
- The returned soundtrack **is the TTS file itself** (cross-correlation 1.000, lag 0), so the series voices are unchanged. The animator writes `scene_video_audio: "native"` and `scene_video_lipsync: true`; the editor uses the clip's audio, never lays the TTS over it again, and applies the H3 trim (not Avatar's TTS trim).
- Cost: $0.04/s on the returned length (a 5 s exchange ≈ $0.21; Kling Avatar v2 $0.28).

**Prompt rules (Test 4b):** build the prompt from the scene's `facial_expression` / `action_description`, then
1. remove every phrase that locks the gaze or head (`unblinking`, `eyes locked on`, `eyes steady on`, `facing the camera head-on`, `holds still`);
2. add `He/She does not stare into the lens: his/her gaze rests on <the listener> just beside the camera and drifts naturally between phrases, with small, relaxed head movements throughout.`;
3. end with `<Speaker> speaks the line "<line>" with lips in sync with the audio;` plus, when another (off-screen) voice speaks first in the TTS, `lips closed while the off-screen <listener> speaks.`;
4. ≤512 UTF-8 bytes; no music/voice clause is needed (the soundtrack is replaced by the TTS).

**Serial-drama two-speaker prompt (Test 9):** `<style medium>. <location light>. A <speaker A look>, <position A>; a <speaker B look>, <position B>. The <A> speaks first: "<line 1>" Then the <B> answers: "<line 2>" Each character's lips move only while they speak and stay closed otherwise. They do not stare into the lens: their gaze rests on each other and drifts naturally, with small relaxed head movements.` (lines verbatim with their own punctuation; ≤512 UTF-8 bytes; full rule: `rules/formats/serial-drama.md`). Its `target_audio_url` is the clip's TTS: 0.2 s lead-in, the lines in order with 0.3 s gaps, mono 44.1 kHz MP3 (`rules/roles/sound.md` §5a). Test 9: 6.7 → 7.328 s, 7.5 → 8.032 s, 9.2 → 9.44 s returned; soundtrack = the TTS (lag 0).

### H3 Max face reference (`reference-to-video`; `dual-style`)

**Endpoint:** `https://queue.fal.run/minimax/h3-max/reference-to-video`
**Polling base:** `https://queue.fal.run/minimax/h3-max` (the same base as H3 Max I2V)
**Route in `tools/video_routes.json`:** `minimax.h3max.r2v` (result path `["video", "url"]`)
**Method:** schema-v3 `tools/kling_runner.py` only. Template: `tools/examples/minimax-h3-max-r2v-face-ref.job.json` (the Test 8 V2 scene 1 job).
**Cost:** $0.08/s at 768P on the returned length, like H3 Max (5 s → 5.184 s ≈ $0.41; Kling v3 Standard with audio was $0.63).

`dual-style` only (`rules/formats/dual-style.md`, contract `dual-style-h3`): the scene still is the start frame and the scene-derived frontal headshot(s) are face references, replacing Kling `elements` + `multi_prompt`. Tested in Test 8 (`trials/2026-10-cost-trials/`): 6/6 clips OK (3 of them this variant), the endpoint accepted `image_url` together with `reference_image_urls`, and the user chose it over start-frame-only H3 Max.

```json
"payload": {
  "prompt": "The photoreal woman on the right has exactly the face in Image 1; keep it unchanged. Front camera dollies back as both walk toward it, centered and facing lens. Anime Keqing left and photoreal Keqing right walk in measured sync. Faces locked forward: no head, eye, expression or identity change; no morphing. Only legs, fabric, natural hair and electro sparks move. Diegetic ambience only, no music. Mouth stays closed; no talking.",
  "image_url": "<permanent Supabase URL of the scene still (start frame)>",
  "reference_image_urls": ["<permanent Supabase URL of the frontal headshot>"],
  "aspect_ratio": "9:16",
  "duration": 5,
  "resolution": "768P",
  "prompt_expansion_mode": "disabled"
}
```

| Parameter | Type | Value |
|---|---|---|
| `prompt` | string | The playbook's locked walk template: opens with `The photoreal woman/man on the right has exactly the face in Image 1; keep it unchanged.`, ends with `Diegetic ambience only, no music. Mouth stays closed; no talking.`; ≤512 UTF-8 bytes (Test 8: 431–439) |
| `image_url` | string | The scene still (start frame), permanent Supabase URL |
| `reference_image_urls` | array | The frontal headshot(s) only, permanent Supabase URLs (one in `source-vs-live-action`; two, original then alternate, in `canonical-alternate`, untested) |
| `aspect_ratio` | string | `"9:16"` |
| `duration` | number | `5` |
| `resolution` | string | `"768P"` |
| `prompt_expansion_mode` | string | `"disabled"` |

`expect`: `duration_seconds 5`, `duration_tolerance_seconds 0.8`, `audio "required"` (the format mixes the clip's ambience), `min_bytes 100000`, `min_width 600`, `min_height 1000`, `orientation "portrait"`. No `target_audio_url`. Measured: 768×1344, 5.184 s, AAC audio. The animator writes `scene_video_route: "minimax.h3max.r2v"`, `scene_video_audio: "native"`; the editor applies the H3 trim.

---

## 2z. Seedance 2.0 Mini (reference-to-video) — DEBUG TEST I2V alternative, not default

**Status: test route for a single debug run (genshin-dont-save-me-en EP10), added 2026-08-17. Not the default serial-drama I2V model — `serial-drama.md` mandates H3 (H3 Max action clips, H3 Max Turbo lip-sync dialogue) for normal runs. Use this route ONLY when the orchestrator explicitly says so for the current run.**

**⚠️ Burned 2026-08-17 (genshin-dont-save-me-en EP10, scene 1 test): Seedance rejects licensed-game-character output with `content_policy_violation` / `cause: copyright`.** A real, full-length generation (`inference_time` ~127s, i.e. actually billed, not an instant validation reject) of Lumine/Childe (Genshin Impact) was rejected post-generation at result-fetch with HTTP 422 and `"Output video has sensitive content. Potential copyright violation."` (`reason: partner_validation_failed`). This is a post-generation content filter, not a prompt-text issue — it appears to trigger on recognizable licensed-game character likeness rendered in the reference image, independent of prompt wording. Do not retry this route for Genshin Impact (or presumably other licensed-game) character content without a materially different approach (e.g. a licensing/whitelist arrangement with fal.ai, or genuinely original characters) — a second identical-style attempt is likely to burn the same ~$0.15/s (720p) generation cost again for the same rejection. Separately, note the **minimum 2.0s `audio_urls` duration** — a 1.88s TTS line was rejected instantly (free, ~2s inference) with `audio_duration_too_short`; pad short dialogue lines with trailing silence before submitting.

**Endpoint:** `https://queue.fal.run/bytedance/seedance-2.0/mini/reference-to-video`
**Route in `tools/video_routes.json`:** `seedance2.mini.reference_to_video`
**Метод:** POST через `tools/kling_runner.py` (format-agnostic transport, `route: "seedance2.mini.reference_to_video"`) — не raw curl.
**Стоимость:** ~$0.0721/сек @480p, ~$0.1547/сек @720p (5s @720p ≈ $0.77, 10s @720p ≈ $1.55). Audio generation included, no extra charge.

### Параметры (payload)

| Параметр | Тип | Обяз. | Описание |
|---|---|---|---|
| `prompt` | string | Да | Текстовое описание сцены/движения |
| `image_urls` | array of strings | Нет (по факту нужен минимум 1 стартовый кадр) | До 9 изображений, JPEG/PNG/WebP, ≤30MB каждое. Ссылаться в prompt как `@Image1`, `@Image2` |
| `video_urls` | array of strings | Нет | До 3 видео, суммарно 2–15s |
| `audio_urls` | array of strings | Нет | До 3 файлов MP3/WAV, суммарно ≤15s, ≤15MB каждый. **Это способ подать TTS-реплику для липсинка** — требует хотя бы один `image_urls`/`video_urls`. Нет отдельного `voice_ids`/`multi_prompt`, как у Kling — весь диалог подаётся уже сгенерированным Sound-фазой аудио-файлом |
| `resolution` | enum | Нет | `"480p"`, `"720p"` (default `"720p"`) |
| `duration` | enum | Нет | `"auto"` или `"4"`–`"15"` (секунды) |
| `aspect_ratio` | enum | Нет | `"9:16"` для вертикального (default `"auto"` — всегда указывать явно) |
| `generate_audio` | boolean | Нет | default `true` — генерирует synced ambience/SFX/lip-sync поверх поданного `audio_urls`. Для action-клипов без реплики можно оставить true для ambience |
| `seed` | integer | Нет | воспроизводимость |

### Ключевые отличия от Kling v3 Standard (исторический serial-drama route)

- Нет `voice_ids` / `multi_prompt` / `elements` / `shot_type: "customize"` — каждый scene submit одиночный `prompt` + один стартовый кадр (`image_urls[0]`).
- Диалоговый клип = сгенерированный Sound-фазой TTS mp3/wav передаётся как `audio_urls[0]`; модель делает lip-sync сама (нет отдельного Avatar-эндпоинта).
- Идентичность персонажей — только через физические дескрипторы в `prompt` (та же rule, что и для Kling, см. `rules/formats/serial-drama.md`), имена по-прежнему запрещены в визуальном тексте.
- Не смешивать в одном эпизоде Kling и Seedance клипы — один motion-модель = один визуальный стиль движения, как и для Kling vs HeyGen (см. `rules/roles/animator.md` §"Do not mix").

### Ответ

```json
{
  "video": { "url": "https://fal.media/files/.../output.mp4", "content_type": "video/mp4" },
  "seed": 12345
}
```

Polling — тот же generic fal-queue паттерн (`requests/{id}/status` → `COMPLETED`/`FAILED`), см. общий раздел ниже.

---

## 2a. Kling Motion Control — motion transfer с реф-видео

Переносит движения из референсного видео на статичное изображение персонажа.

### Endpoints

| Вариант | Endpoint | Стоимость |
|---------|----------|-----------|
| **v2.6 Standard (основной)** | `fal-ai/kling-video/v2.6/standard/motion-control` | $0.07/сек |
| v3 Standard | `fal-ai/kling-video/v3/standard/motion-control` | $0.126/сек |
| v3 Pro | `fal-ai/kling-video/v3/pro/motion-control` | $0.168/сек |

### Запрос (v2.6 Standard)

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/kling-video/v2.6/standard/motion-control" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cute Roblox girl dancing energetically",
    "image_url": "https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/motion-test/character.png",
    "video_url": "https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/motion-test/dance-ref.mp4",
    "character_orientation": "video",
    "keep_original_sound": true
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|:---:|----------|
| `image_url` | string | Да | URL изображения персонажа (постоянный Supabase URL). Персонаж: чёткие пропорции, >5% площади, голова открыта |
| `video_url` | string | Да | URL референсного видео с движением (постоянный Supabase URL). Макс 10с (image mode) / 30с (video mode) |
| `character_orientation` | enum | Да | `"video"` = ориентация по видео (макс 30с, лучше для танцев). `"image"` = по картинке (макс 10с) |
| `prompt` | string | Нет | Описание |
| `keep_original_sound` | boolean | Нет | Сохранить звук из реф-видео (default: true) |
| `elements` | list | Нет | Привязка лица для консистентности (макс 1, только video mode) |

### Polling

```bash
# Base = fal-ai/kling-video (НЕ полный путь v2.6/standard/motion-control)
while true; do
  STATUS=$(curl -s "https://queue.fal.run/fal-ai/kling-video/requests/$REQUEST_ID/status" \
    -H "Authorization: Key $FAL_KEY" | jq -r '.status')
  case "$STATUS" in
    "COMPLETED") break ;;
    "FAILED") echo "FAILED"; exit 1 ;;
    *) sleep 15 ;;
  esac
done

RESULT=$(curl -s "https://queue.fal.run/fal-ai/kling-video/requests/$REQUEST_ID" \
  -H "Authorization: Key $FAL_KEY")
VIDEO_URL=$(echo "$RESULT" | jq -r '.video.url')
curl -s -o output.mp4 "$VIDEO_URL"
```

### Ответ

```json
{
  "video": {
    "url": "https://fal.media/files/abc123/output.mp4",
    "content_type": "video/mp4",
    "file_name": "output.mp4",
    "file_size": 19489104
  }
}
```

### Требования к входным файлам

- **Изображение:** персонаж с чёткими пропорциями тела, голова не закрыта, занимает >5% кадра
- **Видео:** реальные движения человека, макс 30с (video mode) / 10с (image mode)
- **Оба файла** — постоянные Supabase URL (НЕ fal.media)

---

## 2b. Kling 2.6 Pro — справочник альтернативного I2V-маршрута

**Endpoint:** `https://queue.fal.run/fal-ai/kling-video/v2.6/pro/image-to-video`
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** $0.07/сек без аудио (5s = $0.35, 10s = $0.70) | $0.14/сек с аудио (5s = $0.70, 10s = $1.40)

> Автоматически не использовать вместо Kling v3. Endpoint допустим только когда его заранее задаёт playbook/Manager или пользователь явно разрешает отдельный новый маршрут после остановки.

### Отправка запроса

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/kling-video/v2.6/pro/image-to-video" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "The hero swings his sword with dynamic motion, camera follows the action",
    "start_image_url": "https://fal.media/files/abc123/scene-1.png",
    "duration": "5",
    "generate_audio": false,
    "negative_prompt": "blur, distort, low quality, static"
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Описание анимации |
| `start_image_url` | string | Да | URL исходного изображения |
| `duration` | enum | Нет | `"5"` или `"10"` секунд, по умолчанию "5" |
| `generate_audio` | boolean | Нет | Follow the exact format; never override its native/silent audio rule |
| `negative_prompt` | string | Нет | Что исключить |
| `end_image_url` | string | Нет | API parameter exists, but this pipeline forbids it and never creates end frames |

### Polling статуса

```bash
# Base для polling = fal-ai/kling-video (первые 2 сегмента)
while true; do
  STATUS_RESPONSE=$(curl -s "https://queue.fal.run/fal-ai/kling-video/requests/$REQUEST_ID/status" \
    -H "Authorization: Key $FAL_KEY")

  STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')

  case "$STATUS" in
    "COMPLETED") break ;;
    "FAILED") echo "FAILED"; exit 1 ;;
    *) sleep 15 ;;
  esac
done
```

### Получение результата

```bash
RESULT=$(curl -s "https://queue.fal.run/fal-ai/kling-video/requests/$REQUEST_ID" \
  -H "Authorization: Key $FAL_KEY")

VIDEO_URL=$(echo "$RESULT" | jq -r '.video.url')
curl -s -o scene-1.mp4 "$VIDEO_URL"
```

### Ответ

```json
{
  "video": {
    "url": "https://fal.media/files/abc123/output.mp4",
    "content_type": "video/mp4",
    "file_name": "output.mp4",
    "file_size": 1234567
  }
}
```

---

## 4. MiniMax TTS — внешняя речь без важной идентичности голоса

Использовать, когда формат требует внешний TTS, но у точного format/series нет утверждённого voice sample либо рассказчик/голос не важен. При утверждённом sample точного формата используется Chatterbox по `rules/roles/sound.md`; format-native dialogue не дублируется TTS.

**Endpoint:** `https://queue.fal.run/fal-ai/minimax/speech-2.8-hd`
**Метод:** POST (async, polling через `fal-ai/minimax`)
**Стоимость:** ~$0.10/1k chars (~$0.001–0.005 за фразу)

### Запрос

```bash
cat > /tmp/tts-body.json <<'EOF'
{
  "prompt": "Stand down, Worf. That is an order.",
  "voice_setting": {
    "voice_id": "Deep_Voice_Man",
    "speed": 0.9,
    "emotion": "angry"
  },
  "audio_setting": { "format": "mp3" }
}
EOF

RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/minimax/speech-2.8-hd" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/tts-body.json)

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

⚠️ **КРИТИЧНО:** поле называется `prompt`, НЕ `text`. Голос — `voice_setting.voice_id`, НЕ `voice`.

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Текст для озвучки. Поддерживает теги и паузы. |
| `voice_setting.voice_id` | string | Нет | ID голоса. Default: `Wise_Woman` |
| `voice_setting.speed` | float | Нет | 0.5–2.0. Темп речи. Default: 1.0 |
| `voice_setting.emotion` | string | Нет | `angry`, `happy`, `sad`, `fearful`, `disgusted`, `surprised`, `neutral` |
| `voice_setting.vol` | float | Нет | 0–10. Громкость. Default: 5 |
| `audio_setting.format` | string | Нет | `mp3`, `pcm`, `flac`. Default: mp3 |

### Теги в тексте

| Тег | Звук |
|-----|------|
| `(laughs)` | смех |
| `(groans)` | рёв/стон |
| `(sighs)` | вздох |
| `(coughs)` | кашель |
| `(gasps)` | резкий вдох |
| `(sniffs)` | шмыганье |
| `(yawns)` | зевок |
| `(clears throat)` | прочистка горла |
| `<#0.5#>` | пауза 0.5 сек |

### Голоса (все доступные)

| voice_id | Характер |
|----------|---------|
| `Deep_Voice_Man` | глубокий мужской |
| `Determined_Man` | решительный мужской |
| `Imposing_Manner` | властный мужской |
| `Young_Knight` | молодой мужской |
| `Casual_Guy` | разговорный мужской |
| `Patient_Man` | спокойный мужской |
| `Elegant_Man` | формальный мужской |
| `Decent_Boy` | нейтральный мужской |
| `Wise_Woman` | мудрая женская |
| `Calm_Woman` | спокойная женская |
| `Friendly_Person` | дружелюбная |
| `Inspirational_girl` | воодушевляющая женская |
| `Lively_Girl` | живая женская |
| `Lovely_Girl` | мягкая женская |
| `Sweet_Girl_2` | сладкая женская |
| `Exuberant_Girl` | экспрессивная женская |
| `Abbess` | строгая женская |

### Polling

```bash
# Base path для polling = fal-ai/minimax (первые 2 сегмента)
STATUS_URL="https://queue.fal.run/fal-ai/minimax/requests/${REQUEST_ID}/status"
RESULT_URL="https://queue.fal.run/fal-ai/minimax/requests/${REQUEST_ID}"
```

### Ответ

```json
{
  "audio": {
    "url": "https://fal.media/files/abc123/speech.mp3",
    "content_type": "audio/mpeg"
  }
}
```

Выходной формат: MP3 (готов для FFmpeg, конвертация не нужна).

---

## 4a. ElevenLabs TTS — ЗАПРЕЩЁННЫЙ legacy-справочник

**Endpoint:** `https://queue.fal.run/fal-ai/elevenlabs/tts/eleven-v3`
**Polling base:** `fal-ai/elevenlabs`
**Стоимость:** ~$0.03–0.05 за фразу

> **Не вызывать. ElevenLabs TTS запрещён.** Разрешён только отдельный endpoint `fal-ai/elevenlabs/sound-effects` для SFX; это не TTS.

### Запрос

```bash
cat > /tmp/el-body.json << 'EOF'
{
  "text": "Enterprise. You are under quarantine.",
  "voice": "Liam"
}
EOF

RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/elevenlabs/tts/eleven-v3" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/el-body.json)

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### ⚠️ КРИТИЧНО: правильные параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `text` | string | Да | Текст для озвучки |
| `voice` | string | Да | **Имя голоса** (не UUID, не `voice_id`!) |

**Правильно:** `{"text": "...", "voice": "Liam"}`
**Неправильно:** `{"text": "...", "voice_id": "Liam"}` — игнорируется, fallback на дефолтный голос
**Неправильно:** `{"text": "...", "voice_id": "TX3LPaxmHKxFdv7VOQHJ"}` — UUID не работает

### Голоса (соответствие персонажей)

| Персонаж | `voice` |
|----------|---------|
| Kirk, Mirror Kirk | `Daniel` |
| Chekov | `Charlie` |
| Fleet Admiral | `Liam` |
| Worf, Scotty | `George` |
| Spock | `Brian` |

### Polling и ответ

```bash
# Polling base = fal-ai/elevenlabs (2 сегмента)
STATUS_URL="https://queue.fal.run/fal-ai/elevenlabs/requests/${REQUEST_ID}/status"
RESULT_URL="https://queue.fal.run/fal-ai/elevenlabs/requests/${REQUEST_ID}"

# Ответ
{
  "audio": {
    "url": "https://v3b.fal.media/files/abc123/output.mp3",
    "content_type": "audio/mpeg"
  }
}
```

---

## Общий паттерн polling (для ВСЕХ fal.ai endpoints)

> ⚠️ **КРИТИЧНО:** Polling ВСЕГДА по **базовому 2-сегментному пути**, НЕ по полному submit endpoint.

| Submit endpoint | Polling base |
|-----------------|-------------|
| `fal-ai/nano-banana-2` | `fal-ai/nano-banana-2` |
| `fal-ai/nano-banana-2/edit` | `fal-ai/nano-banana-2` |
| `fal-ai/kling-video/v3/standard/image-to-video` | `fal-ai/kling-video` |
| `fal-ai/kling-video/v2.6/pro/image-to-video` | `fal-ai/kling-video` |
| `minimax/h3-max/image-to-video` | `minimax/h3-max` |
| `minimax/h3-max/reference-to-video` (dual-style face reference) | `minimax/h3-max` |
| `minimax/h3-max-turbo/image-to-video` (lip-sync only) | `minimax/h3-max-turbo` |
| `fal-ai/kling-video/ai-avatar/v2/standard` | `fal-ai/kling-video` |
| `fal-ai/kling-video/lipsync/audio-to-video` | `fal-ai/kling-video` |
| `fal-ai/kling-video/v2.6/standard/motion-control` | `fal-ai/kling-video` |
| `fal-ai/kling-video/v3/standard/motion-control` | `fal-ai/kling-video` |
| `fal-ai/kling-video/v3/pro/motion-control` | `fal-ai/kling-video` |
| `fal-ai/elevenlabs/tts/eleven-v3` | `fal-ai/elevenlabs` |
| `fal-ai/minimax-music/v2.6` | `fal-ai/minimax-music` |
| `fal-ai/gpt-image-1/text-to-image` | `fal-ai/gpt-image-1` |
| `fal-ai/heygen/avatar4/image-to-video` | `fal-ai/heygen` |

**Правило:** `base = "/".join(endpoint.split("/")[:2])`

```
1. POST запрос на полный endpoint → получить request_id
2. Каждые 15 секунд: GET https://queue.fal.run/{BASE}/requests/{request_id}/status
3. Проверить статус:
   - "IN_QUEUE" / "IN_PROGRESS" → продолжить polling
   - "COMPLETED" → GET https://queue.fal.run/{BASE}/requests/{request_id} → скачать результат
   - "FAILED" → повторить тот же serialized request один раз; вторая ошибка останавливает весь ролик
4. Таймаут: 10 минут максимум
5. При таймауте: один повтор того же route/request; второй таймаут останавливает весь ролик
```

**Если использовать полный путь вместо base — fal.ai вернёт пустой body, 404 или 405. Деньги за генерацию будут потрачены, результат не скачается.**

---

## 5. Kling Lipsync — Audio-to-Video (липсинк)

**Endpoint:** `https://queue.fal.run/fal-ai/kling-video/lipsync/audio-to-video`
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** ~$0.10/сек

> Принимает видео + аудио, генерирует липсинк (движение губ синхронно с речью).

### Запрос

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/kling-video/lipsync/audio-to-video" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://fal.media/files/abc123/scene-1.mp4",
    "audio_url": "https://fal.media/files/abc123/voiceover.wav"
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `video_url` | string | Да | URL исходного видео (из Kling I2V) |
| `audio_url` | string | Да | URL внешней речи от маршрута, выбранного Sound (MiniMax или exact-format Chatterbox) |

### Polling и получение результата

```
# Base = fal-ai/kling-video (НЕ полный путь lipsync/audio-to-video)
Status: https://queue.fal.run/fal-ai/kling-video/requests/{REQUEST_ID}/status
Result: https://queue.fal.run/fal-ai/kling-video/requests/{REQUEST_ID}
```

### Ответ

```json
{
  "video": {
    "url": "https://fal.media/files/abc123/output.mp4",
    "content_type": "video/mp4"
  }
}
```

### Пайплайн с липсинком

```
Image → Kling I2V (анимация) → Sound-selected external speech → Kling Lipsync (видео + аудио → липсинк) → FFmpeg (склейка)
```

**ВАЖНО:** `audio_url` должен быть доступен endpoint на всё время запроса; используй постоянный run-scoped URL для выбранного Sound-маршрута.

---

## 6. HeyGen Avatar IV — Text-to-Avatar Video (голос + видео в одном)

**Endpoint:** `https://queue.fal.run/fal-ai/heygen/avatar4/image-to-video`
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** $0.10/сек

> Принимает изображение + текст скрипта → генерирует talking head видео с голосом, lipsync, мимикой и жестами рук. Голос генерируется внутри модели — отдельный TTS не нужен.

### Запрос

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/heygen/avatar4/image-to-video" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://fal.media/files/abc123/avatar-ref.png",
    "script": "Yo, why is nobody talking about this? They are literally giving away 500 free diamonds right now! All you gotta do is download the game through the link in my bio and reach level 10.",
    "voice_id": "...",
    "custom_motion_prompt": "energetic gaming blogger speaking to camera, natural hand gestures, nodding"
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `image_url` | string | Да | URL изображения аватара (portrait, upper body, смотрит в камеру) |
| `script` | string | Да | Текст, который аватар произнесёт. Модель сама генерирует голос и lipsync |
| `voice_id` | string | Нет | Имя голоса из списка HeyGen (300+ голосов, 175+ языков). EN рекомендации: `Chill Brian`, `Bold Blake`, `Ivy`, `Cute Chloe - Friendly` |
| `custom_motion_prompt` | string | Нет | Описание жестов и движений ("energetic blogger, hand gestures"). **Именно `custom_motion_prompt`**, НЕ `motion_prompt` |

### Polling и получение результата

```bash
# Проверяй каждые 15 секунд
while true; do
  STATUS=$(curl -s "https://queue.fal.run/fal-ai/heygen/avatar4/image-to-video/requests/$REQUEST_ID/status" \
    -H "Authorization: Key $FAL_KEY" | jq -r '.status')
  case "$STATUS" in
    "COMPLETED") break ;;
    "FAILED") echo "FAILED"; exit 1 ;;
    *) sleep 15 ;;
  esac
done

RESULT=$(curl -s "https://queue.fal.run/fal-ai/heygen/avatar4/image-to-video/requests/$REQUEST_ID" \
  -H "Authorization: Key $FAL_KEY")
VIDEO_URL=$(echo "$RESULT" | jq -r '.video.url')
curl -s -o avatar.mp4 "$VIDEO_URL"
```

### Ответ

```json
{
  "video": {
    "url": "https://fal.media/files/abc123/output.mp4",
    "content_type": "video/mp4"
  }
}
```

### Доступные голоса (примеры)

300+ голосов на 175+ языках. Популярные для gaming-контента:

**EN мужские:** `Chill Brian`, `Andrew Rizz`, `Bold Blake`, `Jack Sterling - Broadcaster`, `Expressive Evan`, `Mellow Marcus`
**EN женские:** `Ivy`, `Cute Chloe - Friendly`, `Feisty Fiona - Excited`, `Ellie Faye - Excited`, `Willow`
**Универсальные:** `Warm Pro Narrator`, `Professor Dean`, `Radio Rick`

> Полный список голосов: проверь через fal.ai playground на странице модели.

> **Используется для формата Gameplay AI Avatar.** Один вызов = голос + lipsync + мимика + жесты. Отдельный TTS не нужен.

---

## 7. Kling Avatar v2 — Image + Audio to Avatar Video (fallback)

**Endpoint (Standard):** `https://queue.fal.run/fal-ai/kling-video/ai-avatar/v2/standard`
**Endpoint (Pro):** `https://queue.fal.run/fal-ai/kling-video/ai-avatar/v2/pro`
**Метод:** POST (асинхронный — нужен polling)
**Стоимость:** $0.056/сек (Standard), $0.115/сек (Pro)

> Принимает изображение + аудио → генерирует talking head с lipsync. В отличие от HeyGen, требует отдельный TTS для генерации аудио.

### Запрос

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/kling-video/ai-avatar/v2/standard" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://fal.media/files/abc123/avatar-ref.png",
    "audio_url": "https://fal.media/files/abc123/speech.wav"
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `image_url` | string | Да | URL изображения аватара |
| `audio_url` | string | Да | URL аудиофайла (WAV/MP3) — из ElevenLabs TTS через fal.ai |

### Polling

Аналогично другим Kling endpoints — base `fal-ai/kling-video`:
```
# Base = fal-ai/kling-video (НЕ полный путь ai-avatar/v2/standard)
Status: https://queue.fal.run/fal-ai/kling-video/requests/{REQUEST_ID}/status
Result: https://queue.fal.run/fal-ai/kling-video/requests/{REQUEST_ID}
```

### Пайплайн с Kling Avatar v2 (fallback для Gameplay AI Avatar)

```
Nano Banana 2 (avatar ref) → ElevenLabs TTS (speech.wav, через fal.ai) → Kling Avatar v2 (image + audio → avatar.mp4) → FFmpeg split-screen
```

> **Используй как fallback**, если HeyGen Avatar IV не работает. Дешевле ($0.056/сек vs $0.10/сек), но требует отдельный TTS.

---

## 8. MiniMax Music v2.6 — AI-generated background music

**Endpoint:** `https://queue.fal.run/fal-ai/minimax-music/v2.6`
**Polling base:** `fal-ai/minimax-music`
**Стоимость:** $0.03 за трек

> Генерирует инструментальную музыку по текстовому описанию. Используется для форматов, где треки из библиотеки запрещены (авторские права → страйки). `is_instrumental: true` — обязательно для фоновой музыки без вокала.

### Запрос

⚠️ **КРИТИЧНО:** поле называется `prompt`, НЕ `style`. С `style` эндпоинт возвращает upstream 422 `body.prompt Field required` (подтверждено боем 2026-07-21, EP13 genshin character-story).

```bash
cat > /tmp/music-body.json << 'EOF'
{
  "prompt": "energetic upbeat anime action music, driving beat 140bpm, orchestral synth blend, heroic bold melody, suitable for vertical short video, cinematic hype",
  "is_instrumental": true,
  "duration": 30
}
EOF

RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/minimax-music/v2.6" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/music-body.json)

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `prompt` | string | Да | Текстовое описание музыки (до 2000 символов). Актуальный v2.6 API отклоняет legacy-поле `style`. |
| `is_instrumental` | boolean | Нет | `true` = без вокала. **Всегда `true` для фоновой музыки** |
| `duration` | integer | Нет | Длительность в секундах (рекомендуется 30–60) |

### Polling

```bash
while true; do
  STATUS=$(curl -s "https://queue.fal.run/fal-ai/minimax-music/requests/$REQUEST_ID/status" \
    -H "Authorization: Key $FAL_KEY" | jq -r '.status')
  case "$STATUS" in
    "COMPLETED") break ;;
    "FAILED") echo "FAILED"; exit 1 ;;
    *) sleep 15 ;;
  esac
done

RESULT=$(curl -s "https://queue.fal.run/fal-ai/minimax-music/requests/$REQUEST_ID" \
  -H "Authorization: Key $FAL_KEY")
AUDIO_URL=$(echo "$RESULT" | jq -r '.audio.url // .audio_file.url')
curl -s -o bg-music.mp3 "$AUDIO_URL"
```

### Ответ

```json
{
  "audio": {
    "url": "https://fal.media/files/abc123/music.mp3",
    "content_type": "audio/mpeg"
  }
}
```

---

## Важные правила

1. **fal.ai URL-ы ВРЕМЕННЫЕ.** Скачивай файлы сразу после генерации. Не рассчитывай на повторный доступ.
2. **Перед дорогой генерацией (Kling / H3 I2V, Avatar) — загрузи ВСЕ входные файлы в Supabase Storage.** Используй ТОЛЬКО постоянные Supabase URL как `start_image_url`, `image_url` (H3), `reference_image_urls` (H3 face reference), `end_image_url`, `audio_url`, `target_audio_url` (H3 lip-sync). Временные fal.ai URL протухают → генерация стоимостью $0.12–$1.40 пропадает.
3. **Polling — по 2-сегментному base пути.** НЕ по полному submit endpoint. См. таблицу в "Общий паттерн polling".
4. **Проверяй размер** скачанного файла (>1000 байт для изображений, >10000 для видео).
5. **Clip sound is decided from the storyboard and format playbook before the job is written.** Kling: Scenarist/Manager/Animator choose `generate_audio` — native dialogue/SFX/ambient use `true` and the paid audio is kept; silent Kling I2V uses `false` and gets `anullsrc` only at assembly. H3 (Max and Max Turbo) has no audio switch and always returns sound: the animator writes `scene_video_audio` (`"native"` when the format mixes the clip's own sound, `"none"` otherwise), and for `"none"` the editor ignores the clip's stream and uses the same silent/`anullsrc` path. Every scene records `scene_video_audio` (`"none"` for silent Kling clips and still shots too).
6. **Не отправляй больше 3 параллельных запросов** — rate limiting.
7. **Сохраняй request_id** — нужен для polling и отмены задач.

### Пайплайн загрузки в Supabase перед дорогой генерацией

```bash
# 1. Генерируй изображение через NB2 → скачай локально
# 2. Загрузи в Supabase Storage
#    Путь ОБЯЗАН содержать дату и формат для scene PNG, иначе следующий эпизод
#    того же game_tag затрёт предыдущий. См. storyboarder.md §15.1.
#    scene PNG:  ${GAME_TAG}/scenes/${YYYY-MM-DD}/${FORMAT_SLUG}/scene-K.png
#    bg/char ref: ${GAME_TAG}/refs/${name}.png  (без даты — шарится между эпизодами)
STORAGE_PATH="${GAME_TAG}/scenes/${DATE}/${FORMAT_SLUG}/${FILENAME}"
curl -s -X POST "https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/assets/${STORAGE_PATH}" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: image/png" \
  --data-binary @"$LOCAL_FILE"

# 3. Получи постоянный URL
PERMANENT_URL="https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/${STORAGE_PATH}"

# 4. Используй PERMANENT_URL как start_image_url в Kling I2V (H3 Max / H3 Max Turbo: image_url; H3 Max face reference: image_url + reference_image_urls)
```

**Никогда не передавай `fal.media` URL в `start_image_url` / `image_url` / `end_image_url` / `audio_url`.**
