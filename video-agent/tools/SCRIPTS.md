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

---

### `pipeline.sh` 🟠

**Роль:** Главная точка входа для генерации. Запускает 5 фаз последовательно, каждая — отдельный Claude-вызов с пинованной моделью. После каждой фазы — инлайн-валидация (`jq`, `stat`, `ffprobe`).

**Запуск:**
```bash
./pipeline.sh <GAME_TAG> "idea" [FORMAT] [OUTPUT_DIR] [TASK_ID]
```

**Фазы и модели:**

| Фаза | Субагент | Модель | Результат |
|------|----------|--------|-----------|
| 0 | — | bash | `git pull`, asset query → `_supabase-assets.json` |
| 1 | scenarist | Sonnet 4.6 | `storyboard.json` |
| 2 | sound | Haiku 4.5 | `scene-K/scene-K.mp3` |
| 3 | storyboarder | Sonnet 4.6 | `scene-K/scene-K.png` |
| 4 | animator | Sonnet 4.6 | `scene-K/scene-K.mp4` |
| 5 | editor | Sonnet 4.6 | `final.mp4` + Supabase URL |

**Читает:** `.env`, `prompts/*.txt`, game/format/rules файлы (делегирует субагентам)  
**Пишет:** `{OUTPUT_DIR}/pipeline.log`, `claude-{phase}.log`, все артефакты фаз, статус в Supabase `video_tasks`

**⚠ Подводные камни:**
- Модели переопределяются через env: `PIPELINE_SCENARIST_MODEL`, `PIPELINE_EDITOR_MODEL` и т.д.
- При падении любой фазы обновляет статус задачи в Supabase и останавливается — повтор с той же фазы невозможен без ручного вмешательства
- `TASK_ID` опционален — без него статус в `video_tasks` не обновляется (при ручном запуске норм, при queue-запуске — обязателен)

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
- GPT Image 1 — fallback без chain ref. $0.02/img  
- Kling v3 Standard I2V — $0.084/с без audio, $0.126/с с audio. multi_prompt, elements
- Kling v2.6 Pro — fallback I2V
- Veo 3 — T2V / I2V, $1.60–$3.20 за 8-секундный клип
- MiniMax TTS — Speech 2.8-HD, $0.10/1k символов
- ElevenLabs TTS через fal.ai — fallback
- Kling Lipsync — audio-to-video lip-sync
- Kling Avatar v2 — image + audio → avatar видео. $0.056/с

**Критичные правила из документа:**
- fal.media URL — временные, скачивать немедленно
- Polling base path = первые 2 сегмента endpoint (не полный путь с версией)
- `generate_audio: false` для всех I2V (audio добавляется отдельно)
- multi_prompt: каждый shot ≤ 512 символов (жёсткий лимит Kling)
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
    [--publish-at "2026-06-20T20:59:00Z" | now] \
    [--thumbnail thumb.png] \
    final.mp4 "Заголовок" "Описание" [private|public] [теги]
```

**Что делает:**
1. Обновляет OAuth2 access token через refresh token
2. Проверяет занятость слота на канале (чтобы не ставить два видео в один день)
3. Resumable upload → YouTube
4. Опционально загружает thumbnail
5. Возвращает YouTube URL + `SCHEDULED_FOR=ISO8601`

**Каналы:** задаются через `YOUTUBE_REFRESH_TOKEN_<CHANNEL>` и `YOUTUBE_CHANNEL_ID_<CHANNEL>` в `.env`  
**Читает:** `.env` (YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN[_CHANNEL])  
**Пишет:** загружает видео на YouTube

**⚠ Подводные камни:**
- Без `--publish-at` автоматически находит ближайший свободный слот в 20:59 UTC — неожиданно если хочешь загрузить как черновик
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

## Быстрая таблица

| Скрипт | Важность | Вызывается | Мутирует |
|--------|----------|------------|----------|
| `pipeline.sh` | 🟠 | вручную / worker | всё (оркестратор) |
| `add_subtitles.py` | 🟠 | editor-агент | .ass файл |
| `overlays.py` | 🟡 | editor-агент | temp .txt файлы |
| `log-video.sh` | 🟢 | manager (после OK) | Supabase video_agent_runs |
| `youtube-upload.sh` | 🟠 | manager (после OK) | YouTube + Supabase |
| `upload-asset.sh` | 🟢 | вручную | Supabase Storage + game_assets |
| `fal-ai.md` | 🟢 | справочник sub-агентов | — |
| `ffmpeg-api.md` | 🟢 | справочник editor-агента | — |

