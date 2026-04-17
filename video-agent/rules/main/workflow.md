# Workflow Video Production Agent v6.0

Ты — автономный видео-агент. Твоя задача — создать короткое вертикальное видео (1080×1920, 9:16) для игровых каналов в соцсетях.

**Главный принцип:** Сначала сценарий, потом генерация. Никогда не генерируй визуал без готового сторибоарда.

---

## Отладочный режим

Если в задаче/промпте пользователя присутствует фраза **«Отладочный режим»**, агент работает **пошагово с согласованием**:

1. **После каждой фазы** (0–6) агент **останавливается** и отправляет результат на согласование
2. К каждому результату прикладывается **пояснение:**
   - Что сделано в этой фазе
   - Почему приняты конкретные решения (выбор модели, стиль, структура текста и т.д.)
   - Какие альтернативы были и почему отвергнуты
   - Есть ли неоднозначности или вопросы
3. **Агент НЕ переходит к следующей фазе**, пока текущая не одобрена пользователем
4. Если пользователь просит изменения — агент вносит правки и снова отправляет на согласование
5. Режим действует на **все фазы**, включая сценарий (Фаза 1) — текст сценария должен быть одобрен до генерации

**Без фразы «Отладочный режим»** агент работает автономно как обычно.

---

## Workflow — 6 фаз

### ФАЗА 0: ИНИЦИАЛИЗАЦИЯ

**0. Context7 — обязательная проверка документации:**
Перед вызовом ЛЮБОГО внешнего API (fal.ai, ElevenLabs, Kling, HeyGen, Supabase и др.) **обязательно** сверяйся с актуальной документацией через MCP-сервер Context7:
1. `resolve-library-id` → получи ID библиотеки/сервиса
2. `get-library-docs` → прочитай актуальные параметры, эндпоинты, форматы запросов

**НЕ полагайся на память или кешированные знания о параметрах API.** Параметры меняются (пример: `voice_id` → `voice` в fal.ai ElevenLabs). Context7 даёт актуальную документацию. Используй его при каждом сомнении в параметрах, эндпоинтах или формате запроса.

1. Прочитай `providers.json` → определи активных провайдеров:
   - Загрузи `tools/fal-ai.md` — основной tools-файл (изображения + видео)
   - `active.ffmpeg` → загрузи tools-файл
2. Прочитай конфиг игры: `games/{GAME_TAG}/{GAME_TAG}.md`
3. Прочитай `rules/main/storyboard.md` — правила написания сторибоарда
4. Прочитай `rules/main/budgets.md` — бюджеты и прайсинг
5. Прочитай `rules/main/fallback.md` — обработка ошибок
6. *(опционально)* Прочитай `music/tracks.json` — если музыка нужна
7. **Запроси ассеты из Supabase** (через MCP или REST API):
   `GET /rest/v1/game_assets?game_tag=eq.{GAME_TAG}&select=*`
   - Если есть `reference_image` → используй его URL вместо генерации character-ref (пропусти ФАЗУ 2)
   - Если есть `prompt_block` → используй как `character_description` в visual_identity
   - Если идея общая и не указан конкретный персонаж → выбери случайного из доступных
   - Если есть `gameplay_clip` → скачай в `games/{GAME_TAG}/gameplay/` (для форматов Reddit Story, Gameplay AI Avatar)
   - Если есть `avatar_ref` → скачай в `games/{GAME_TAG}/assets/avatars/`

8. **Определи формат и загрузи правила формата:**

   Определи формат по ключевым словам идеи:
   - "news", "новости", "game news", "patch recap", "обновление" → загрузи `rules/formats/news.md`
   - "serial", "episode", "series", "ep1", "ep2", "сериал" → загрузи `rules/formats/serial-drama.md`
   - "object character", "антропоморф", "talking object", предмет с эмоциями → загрузи `rules/formats/object-character.md`
   - "dual-style", "game vs reality", "cartoon + realistic" → загрузи `rules/formats/dual-style.md`
   - "gameplay ai avatar", "ai avatar", "talking head", "offerwall", "offer", "оффер", "бонус", "free diamonds" → загрузи `rules/formats/gameplay-ai-avatar.md`
   - "dance battle", "dance", "танцевальный батл", "танец", "dance off", "dance competition" → загрузи `rules/formats/dance-battle.md`
   - Иначе → загрузи `rules/formats/standard.md`

   Если есть game-specific файл для формата (`games/{GAME_TAG}/{format}_special.md`) → загрузи его тоже.

   **НЕ загружай файлы форматов, не относящихся к задаче.**

   **Модель генерации определяется файлом формата, не этим документом.**

---

### ФАЗА 1: СТОРИБОАРД

**Цель:** написать полный сценарий до начала генерации.

Подход и модели определяются загруженным файлом формата.

> **Один подход на всё видео.** Не смешивай подходы внутри одного ролика — это осознанное ограничение для консистентности визуального стиля.

1. **Напиши visual_identity** — единый визуальный стиль:
   - `character_description` — из секции "Character Prompt Blocks" в game config (или напиши сам)
   - `environment_description` — конкретная локация из игры
   - `style_tags`, `color_palette`, `lighting` — из game config

2. **Напиши narrative arc:** hook → development → climax

3. **Определи пейсинг** — сколько клипов нужно (по умолч. 3). Объедини beats с малым действием
4. **Напиши клипы** — для каждого:
   - `beats` (массив), `duration_sec: 5 or 10`, `character_state`, `facial_expression`, `character_speech`, `environment_state`
   - **Выбор длительности:** **5s по умолчанию для всех клипов.** 10s — только если реплика/действие физически не помещается в 5s и нельзя разбить. (Kling поддерживает только 5 или 10 сек) — см. детальные правила в файле формата.
   - `camera_angle` — ОБЯЗАТЕЛЬНО разный для соседних клипов (close-up → wide → low angle)
   - `motion_prompt` — уникальное движение камеры для каждого клипа (НЕ шаблонное). Если 2 beats — опиши оба этапа: `"First 4 seconds: ... Then: ..."`
   - `hero` — (опционально) имя персонажа для мульти-персонажных видео

5. **Собери `image_prompt`** для каждого клипа по шаблону из `rules/main/storyboard.md`

6. **Валидируй:** пейсинг (нет пустых клипов), хронометраж (~24 сек), бюджет, arc complete, character_speech в motion_prompt, camera_angle разный

7. **Сохрани** `storyboard.json` в OUTPUT_DIR

---

### ФАЗА 2: CHARACTER REFERENCE

Перед генерацией сцен создай **одно референсное изображение** персонажа (anchor image).

**Что генерировать:**
```
[STYLE_TAGS], [CHARACTER_DESCRIPTION],
full body character pose, front-facing view, neutral dark background,
clear detailed character design, vertical composition, 9:16 aspect ratio
```

**Параметры:**
- Используй `fal-ai/nano-banana-2/edit` с параметром `image_urls`
- `aspect_ratio`: `"9:16"`
- Сохрани как `scenes/refs/character-ref.png`

**Зачем:** Это изображение станет якорем — `image_urls[0]` для ВСЕХ генераций сцен. Оно фиксирует внешность персонажа.

**ВАЖНО: стилистика референса = стилистика видео.** Если видео фотореалистичное — генерируй референс в фотореалистичном стиле. Если аниме — в аниме. Несовпадение стиля ломает визуальную консистентность.

**Рот персонажа на референсе:** генерируй с лёгкой улыбкой, чтобы были видны зубы. Это улучшает качество липсинка на последующих этапах.

**Без `image_urls`:** Nano Banana 2 поддерживает генерацию только по тексту — просто не передавай поле `image_urls` в запросе (НЕ передавай пустой массив `[]` — это вызывает ошибку).

**Стоимость:** +~$0.04 (одноразово).

**Если в `game_assets` есть `reference_image`** — используй его URL как anchor вместо генерации нового.

---

### ФАЗА 3: ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ

**Рот персонажа на изображениях сцен:**
- **Сцены с липсинком** (персонаж говорит, будет применяться lipsync) — генерируй персонажа с лёгкой улыбкой / приоткрытым ртом, видны зубы. Это критично для качества липсинка.
- **Сцены без липсинка** (нет речи, или речь за кадром) — генерируй рот в нужном настроении сцены (злость, удивление, грусть и т.д.).

Генерируй **последовательно** (каждая сцена зависит от предыдущей — chain reference).

Для каждой сцены K:
1. Собери `image_urls` (chain reference):

   | Сцена | `image_urls` |
   |-------|-------------|
   | 1 | `[character-ref-url]` |
   | 2 | `[character-ref-url, scene-1-url]` |
   | 3 | `[character-ref-url, scene-2-url]` |
   | N | `[character-ref-url, scene-(N-1)-url]` |

   **Правила chain reference:**
   - Всегда **2 референса**: anchor (character-ref) + предыдущая сцена
   - Для сцены 1 — только anchor (1 референс)
   - НЕ добавляй все предыдущие сцены — только последнюю

2. Вызови image gen с `image_prompt` из storyboard + `image_urls`
3. Скачай `scenes/scene-K/scene-K.png`, сохрани URL для следующей сцены
4. Запиши стоимость (в USD)

**URL-ы:** Используй URL из fal.ai output (`fal.media/files/...`). fal.ai URL-ы временные — скачивай файлы сразу после генерации.

**КРИТИЧНО: Передача файлов между этапами pipeline.**
Если результат одного этапа (TTS аудио, изображения) нужен как input для следующего дорогого этапа (Kling Avatar, Kling I2V, Lipsync):
1. **Скачай файл локально** сразу после генерации
2. **Загрузи в Supabase Storage** — получи постоянный public URL
3. **Используй ТОЛЬКО Supabase URL** для следующего этапа
4. **НИКОГДА не перезапрашивай** fal.ai result URL повторно — они могут стать невалидными
5. **Перед отправкой** в дорогую генерацию — выведи таблицу маппинга (clip# → image_url → audio_url → ожидаемый текст) и убедись что все URL уникальны и корректны

---

### ФАЗА 4: АНИМАЦИЯ

Модель и параметры анимации определяются файлом формата. Общие правила:

**КРИТИЧЕСКИ ВАЖНО: Одна модель на все сцены.** Используй ОДНУ модель для ВСЕХ сцен видео. Разные модели (Kling vs Veo3) дают разный визуальный стиль, цветовую температуру и "пластику" движений. Смешивание ломает консистентность.

Если модель падает — повтори ту же модель (до 3 попыток), только потом переключайся на fallback.

**Переходы — hard cut с разными планами:**
- НЕ используй `end_image_url`, crossfade или xfade
- Каждая сцена имеет РАЗНЫЙ `camera_angle` (close-up → wide → low angle)
- Склейка через простой `concat` (hard cut)

**Polling:** fal.ai статусы: IN_QUEUE → IN_PROGRESS → COMPLETED / FAILED. Проверяй каждые 15 сек.

Скачай каждый `scenes/scene-K/scene-K.mp4` локально. Проверь файл > 1000 bytes.

---

### ФАЗА 5: СБОРКА

Используй **локальный ffmpeg**: `/usr/local/bin/ffmpeg`

**КРИТИЧНО: Shell = zsh (macOS).** Массивы в zsh начинаются с индекса 1, НЕ 0. `arr=(a b c)` → `arr[1]=a`, `arr[0]=пустота`. **Не использовать массивы в batch-скриптах** — писать явные команды для каждого клипа. Массивы молча возвращают пустоту и ломают параметры ffmpeg (пустой `-ss`, пустой input path).

#### 5.1 Масштабирование

Все клипы к единому формату:
```bash
$FFMPEG -y -i scenes/scene-K/scene-K.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -r 30 -c:v libx264 -preset slow -crf 10 -pix_fmt yuv420p \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  scenes/scene-K/scene-K-scaled.mp4
```

**Обязательные параметры масштабирования:**
- `-r 30` — 30 fps (все клипы в одном fps перед склейкой)
- `-preset slow -crf 10` — высокое качество, без потери битрейта
- `-ar 44100 -ac 2 -c:a aac -b:a 128k` — нормализация аудио (44100Hz, stereo, AAC 128k)

**КРИТИЧНО:** Все клипы ДОЛЖНЫ иметь одинаковый fps и аудиоформат перед склейкой.

#### 5.2 Склейка

**Только hard cut** (каты между разными планами камеры):
```bash
cat > concat-list.txt << EOF
file 'scenes/scene-1/scene-1-scaled.mp4'
file 'scenes/scene-2/scene-2-scaled.mp4'
...
EOF

$FFMPEG -y -f concat -safe 0 -i concat-list.txt \
  -r 30 -c:v libx264 -preset slow -crf 10 \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  final.mp4
```

**ВАЖНО:** Concat с re-encode (`-c:v libx264`), НЕ stream copy (`-c copy`). Stream copy вызывает non-monotonic DTS и наложение кадров.

**НЕ используй crossfade/xfade.** Разные планы камеры делают каты профессиональными.

#### 5.3 Фоновая музыка (опционально)

Если видео выиграет от фоновой музыки — наложи трек из `music/tracks.json`:

1. Выбери трек по mood/game из `music/tracks.json`
2. Скачай трек: `curl -s -o bg-music.mp3 "$TRACK_URL"`
3. Миксуй с видео (музыка тише, звуковые эффекты громче):
```bash
$FFMPEG -y -i final.mp4 -i bg-music.mp3 \
  -filter_complex "[1:a]volume=0.15[music];[0:a][music]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 128k final-with-music.mp4
```

**НИКОГДА не используй `-shortest`** — обрезает видео до длины аудио.

---

### ФАЗА 6: UPLOAD & LOG

1. Загрузи `final.mp4` в Supabase Storage (bucket `videos`):
   - Путь: `videos/{GAME_TAG}/{YYYY-MM-DD}/{format_slug}_final.mp4`
   - Пример: `videos/Roblox/2026-03-31/reddit-story_final.mp4`
   - Получи публичный URL

2. Запиши лог в `video_agent_runs`:
```sql
INSERT INTO video_agent_runs (
  game_tag, input_idea, agent_plan, approach_used, model_used,
  total_cost_usd, output_video_url, status, error_message,
  video_duration_seconds, run_duration_seconds, scenes
) VALUES (...);
```

3. **Синхронизация правил с main (ОБЯЗАТЕЛЬНО после завершения ролика):**

Если во время работы правились rule-файлы (`rules/`, `tools/`, `CLAUDE.md`, `providers.json`) или story bibles — запушь изменения в main, чтобы они были доступны другим агентам и следующим запускам.

```bash
# Стейджить ТОЛЬКО rule/config/story-bible файлы (не output, не ассеты)
git add video-agent/rules/ video-agent/tools/ video-agent/CLAUDE.md \
        video-agent/providers.json video-agent/games/*/*_story_bible.json \
        video-agent/games/*/*_bible.json video-agent/games/*/*.md 2>/dev/null

# Если есть что коммитить:
git diff --cached --quiet || {
  git commit -m "Update rules after {format} run ({GAME_TAG})

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
  git push
  gh pr create --title "Rules update: {format} / {GAME_TAG}" --body "Auto-update after run" --base main 2>/dev/null || true
  gh pr merge --squash --auto 2>/dev/null || true
}
```

**Не пушить:** `output/`, `*.log`, `.DS_Store`, `.env`, сгенерированные ассеты.

**При merge-конфликте** — остановись и сообщи пользователю, не разрешай автоматически.

**Почему:** Правила только в локальной ветке не применяются другими запусками. Пользователь жаловался что исправления не дошли до других агентов. После каждого ролика актуальная база правил должна быть доступна всем.

---

## Выходные файлы

```
output/YYYY-MM-DD/{GAME_TAG}/{format_slug}/
├── storyboard.json          # Полный сторибоард (ФАЗА 1)
├── scenes/
│   ├── refs/
│   │   └── character-ref.png    # Якорное изображение (ФАЗА 2)
│   ├── scene-1/
│   │   ├── scene-1.png          # Изображение сцены (ФАЗА 3)
│   │   ├── scene-1.mp4          # Анимированный клип (ФАЗА 4)
│   │   └── scene-1-scaled.mp4   # Масштабированный (ФАЗА 5)
│   └── scene-2/
│       └── ...
└── final.mp4                # Финальное видео (ФАЗА 5)
```
