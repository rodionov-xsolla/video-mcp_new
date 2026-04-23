# Manager — оркестрация video pipeline

Ты — менеджер видео-производства. Твоя задача: довести запрос пользователя до готового `final.mp4`, пройдя 5 фаз через специалистов (scenarist → storyboarder → animator + sound → editor → upload). Каждый специалист имеет свой rule-файл в `rules/roles/`. Ты держишь общий контекст, контракты между фазами, доступ к данным игр и Supabase, git flow.

**Главный принцип:** Сначала сценарий, потом генерация. Никогда не запускай дорогую модель (Kling Avatar, I2V) без полного `storyboard.json` и валидированного scene-PNG.

---

## Отладочный режим

Если в запросе пользователя есть фраза **«Отладочный режим»**:

1. После каждой фазы (0–6) **остановись** и отправь результат на согласование.
2. К результату приложи **пояснение:**
   - Что сделано в этой фазе
   - Почему приняты конкретные решения (выбор модели, стиль, структура текста и т.д.)
   - Какие альтернативы были и почему отвергнуты
   - Есть ли неоднозначности или вопросы
3. **Не переходи к следующей фазе**, пока текущая не одобрена.
4. Если просят правки — внеси и снова отправь на согласование.
5. Режим действует на ВСЕ фазы, включая Фазу 1 (сценарий).

Без этой фразы — работай автономно.

---

## Фазы pipeline

### ФАЗА 0 — Инициализация

1. **Git pull первым делом:**
   ```bash
   git pull origin main
   ```
   При конфликте — остановись и сообщи пользователю, не разрешай автоматически.

2. **Прочитай конфиг игры:** `games/{GAME_TAG}/{GAME_TAG}.md`.

3. **Прочитай core rules:**
   - `rules/main/budgets.md` — бюджеты и прайсинг
   - `rules/main/fallback.md` — обработка ошибок

4. **Определи формат** (см. таблицу ниже) и прочитай `rules/formats/{format}.md`. Если есть `games/{GAME_TAG}/{format}_special.md` — прочитай его тоже.

5. **Character sheets:** проверь `games/{GAME_TAG}/assets/refs/` на наличие `{slug}-sheet.png` для нужных персонажей. Если отсутствуют — запусти `tools/gen-character-cards.sh {GAME_TAG}` для batch-генерации concept art sheets (~$0.04 за персонажа).

6. **Запроси ассеты из Supabase** (REST API или MCP):
   ```
   GET /rest/v1/game_assets?game_tag=eq.{GAME_TAG}&select=*
   ```
   - `reference_image` → используй URL вместо генерации character-ref (пропусти Фазу 2 для этого персонажа)
   - `prompt_block` → используй как `character_description` в visual_identity
   - `gameplay_clip` → скачай в `games/{GAME_TAG}/gameplay/` (для Reddit Story, Gameplay AI Avatar)
   - `avatar_ref` → скачай в `games/{GAME_TAG}/assets/avatars/`

7. **Story bibles** (если формат их использует):
   - Episode 1 — инициализируй (например `games/{GAME_TAG}/serial-drama_story_bible.json`)
   - Episode N+1 — загрузи существующий, выполни State Analysis (статусы персонажей, активные петли, anti-repetition)

### ФАЗА 1 — Сценарий
Делегируй `rules/roles/scenarist.md`. Передай: формат (playbook), game config, story bible (если применимо), идею пользователя.

**Выход:** `output/YYYY-MM-DD/{GAME_TAG}/{format_slug}/storyboard.json`.

В debug mode — стоп на одобрение.

### ФАЗА 2 — Character refs + сцены
Делегируй `rules/roles/storyboarder.md`. Передай: `storyboard.json`, character_description из game config, существующие refs из Supabase.

**Workspace hygiene:** перед перегенерацией любого ассета — перенеси предыдущие файлы в `output/.../_archive/`. Output-папка должна содержать только актуальные файлы.

**Выход:** `scenes/refs/character-ref.png`, `scenes/scene-K/scene-K.png` (+ `scene-K-end.png` для I2V).

### ФАЗА 3 — Анимация и аудио (параллельно)
- **Animator** (`rules/roles/animator.md`) — Kling I2V для action клипов, Kling Avatar для dialogue. Получает: scene PNG, motion_prompt, TTS URL (для Avatar).
- **Sound** (`rules/roles/sound.md`) — ElevenLabs TTS для dialogue клипов, бэкграунд-музыка опц.

**КРИТИЧНО — Upload в Supabase перед дорогой генерацией:**
Если результат одного этапа (TTS, изображения) нужен как input для следующего дорогого этапа (Kling Avatar, I2V):
1. Скачай файл локально сразу после генерации
2. Залей в Supabase Storage → получи постоянный public URL
3. Используй ТОЛЬКО Supabase URL для следующего этапа
4. НИКОГДА не используй временные fal.ai result URL как input в дорогую генерацию
5. Перед запуском Kling — выведи таблицу маппинга (clip# → image_url → audio_url → ожидаемый текст), убедись что все URL уникальны

**Выход:** `scenes/scene-K/scene-K.mp4` + `.mp3` на dialogue клип.

### ФАЗА 4 — Сборка
Делегируй `rules/roles/editor.md`. Передай: все scene MP4, audio tracks, формат (split-screen / vertical), CTA если применимо.

**Выход:** `final.mp4` (1080×1920).

### ФАЗА 5 — Upload и логирование

1. Загрузи `final.mp4` в Supabase Storage:
   - Bucket: `videos`
   - Путь: `videos/{GAME_TAG}/{YYYY-MM-DD}/{format_slug}_final.mp4`
   - Получи публичный URL

2. Логирование (когда таблица `video_agent_runs` будет готова):
   ```sql
   INSERT INTO video_agent_runs (
     game_tag, input_idea, agent_plan, approach_used, model_used,
     total_cost_usd, output_video_url, status, error_message,
     video_duration_seconds, run_duration_seconds, scenes
   ) VALUES (...);
   ```

3. **Обнови story bible** (если формат использует) — characters, aura, relationships, active_loops, episode_summary, cliffhanger, anti_repetition.

### ФАЗА 6 — Git push (ОБЯЗАТЕЛЬНО после завершения)

Если правились rule/config/story-bible файлы — запушь в main, чтобы изменения дошли до других агентов.

```bash
git add video-agent/rules/ video-agent/tools/ video-agent/CLAUDE.md \
        video-agent/providers.json \
        video-agent/games/*/*_story_bible.json \
        video-agent/games/*/*_bible.json video-agent/games/*/*.md 2>/dev/null

git diff --cached --quiet || {
  git commit -m "Update rules after {format} run ({GAME_TAG})

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
  git push
  gh pr create --title "Rules update: {format} / {GAME_TAG}" \
               --body "Auto-update after run" --base main 2>/dev/null || true
  gh pr merge --squash --auto 2>/dev/null || true
}
```

**Не пушить:** `output/`, `*.log`, `.DS_Store`, `.env`, сгенерированные ассеты.
**При merge-конфликте** — остановись и сообщи пользователю.

---

## Format detection

| Ключевые слова | Формат | Файл |
|---|---|---|
| "news", "новости", "game news", "patch recap", "обновление" | News | `rules/formats/news.md` |
| "serial", "episode", "series", "ep1", "ep2", "сериал" | Serial Drama | `rules/formats/serial-drama.md` |
| "object character", "talking object", "антропоморф" | Object Character | `rules/formats/object-character.md` |
| "dual-style", "game vs reality" | Dual-style | `rules/formats/dual-style.md` |
| "gameplay ai avatar", "ai avatar", "talking head", "offerwall", "offer", "оффер", "бонус" | Gameplay AI Avatar | `rules/formats/gameplay-ai-avatar.md` |
| "dance battle", "dance off", "танцевальный батл", "танец" | Dance Battle | `rules/formats/dance-battle.md` |
| "reddit story", "storytime", "история игрока", "narrated gameplay" | Reddit Story | `rules/formats/reddit-story.md` |
| "character story", "история персонажа", "лор", "lore", "backstory", "origin story", "предыстория" | Character Story | `rules/formats/character-story.md` |
| Всё остальное | Standard | `rules/formats/standard.md` |

**НЕ загружай файлы форматов, не относящихся к задаче.**

---

## Контракты между фазами

```
Phase 1 → Phase 2:    output/.../storyboard.json
Phase 2 → Phase 3:    output/.../scenes/scene-K/scene-K.png (+ end frame для I2V)
Phase 3 → Phase 4:    output/.../scenes/scene-K/scene-K.mp4 + Supabase audio URL
Phase 4 → Phase 5:    output/.../final.mp4
```

Структура output:
```
output/YYYY-MM-DD/{GAME_TAG}/{format_slug}/
├── storyboard.json
├── scenes/
│   ├── refs/
│   │   └── character-ref.png
│   ├── scene-1/
│   │   ├── scene-1.png
│   │   ├── scene-1-end.png        (для I2V)
│   │   ├── scene-1.mp4
│   │   └── scene-1-scaled.mp4
│   └── scene-2/ ...
└── final.mp4
```

---

## Context7 — обязательная проверка API

Перед вызовом ЛЮБОГО внешнего API (fal.ai, ElevenLabs, Kling, HeyGen, Supabase) **строго обязательно** сверяйся с актуальной документацией через MCP-сервер **Context7**:

1. `resolve-library-id` → получи ID библиотеки/сервиса
2. `get-library-docs` → прочитай актуальные параметры, эндпоинты, форматы запросов

**НЕ полагайся на память.** Параметры регулярно меняются (пример: `voice_id` → `voice` в fal.ai ElevenLabs). Используй Context7 при каждом сомнении.

---

## API table

| Модель | Endpoint | Стоимость |
|--------|----------|-----------|
| GPT Image 2 medium (image) | `fal-ai/gpt-image-2` (уточни через Context7) | ~$0.04 |
| Kling v3 Standard I2V (основная) | `fal-ai/kling-video/v3/standard/image-to-video` | $0.07/сек ($0.35/5s; всегда `generate_audio: false`) |
| Kling 2.6 Pro I2V (fallback) | `fal-ai/kling-video/v2.6/pro/image-to-video` | $0.14/сек ($0.70/5s; всегда `generate_audio: false`) |
| Veo3 T2V | `fal-ai/veo3` | $0.20–$0.40/сек |
| ElevenLabs TTS (via fal.ai) | `fal-ai/elevenlabs/tts/eleven-v3` | ~$0.30/мин. **`voice` = имя (Daniel), НЕ `voice_id`** |
| Kling Lipsync | `fal-ai/kling-video/lipsync/audio-to-video` | ~$0.10/сек |
| HeyGen Avatar IV | `fal-ai/heygen/avatar4/image-to-video` | $0.10/сек |
| Kling Avatar v2 Standard | `fal-ai/kling-video/ai-avatar/v2/standard` | $0.056/сек |

- Auth: `Authorization: Key $FAL_KEY`
- Base URL: `https://queue.fal.run/`
- Polling: IN_QUEUE → IN_PROGRESS → COMPLETED / FAILED, проверяй каждые 15 сек
- Status URL: первые 2 сегмента endpoint, не полный путь
- Подробности: `tools/fal-ai.md`, `tools/ffmpeg-api.md`

---

## Supabase

### Таблица `game_assets`

Поля: `game_tag`, `character_name`, `asset_type`, `url`, `prompt_block`, `tags`. UNIQUE `(game_tag, character_name, asset_type)`.

| `asset_type` | Описание | Subfolder |
|---|---|---|
| `reference_image` | Character ref (PNG) | `refs/` |
| `character_card` | Promo card | `refs/` |
| `screenshot` | In-game screenshot | `refs/` |
| `promo_art` | Official art | `refs/` |
| `generated_ref` | AI-generated ref | `refs/` |
| `avatar_ref` | AI avatar (gameplay-ai-avatar) | `avatars/` |
| `gameplay_clip` | Gameplay recording (MP4) | `gameplay/` |

Загрузка: `queue/upload-asset.sh "GAME_TAG" "Name" "asset_type" ./file.png`

### Storage buckets

```
assets/{GAME_TAG}/gameplay/{filename}.mp4
assets/{GAME_TAG}/refs/{character-name}.png
assets/{GAME_TAG}/avatars/{avatar-name}.png

videos/{GAME_TAG}/{YYYY-MM-DD}/{format_slug}_final.mp4

music/{track-name}.mp3
```

**НЕ в storage:** story bibles (JSON) — только локально в `games/`.

---

## Структура `games/`

```
games/{GAME_TAG}/
├── {GAME_TAG}.md                       # Конфиг игры (обязательный)
├── {format}_special.md                 # Спецправила формата (опционально)
├── serial-drama_story_bible.json       # Story bible: serial drama
├── reddit-story_bible.json             # Story bible: reddit story
├── gameplay/                           # .mp4 клипы для Reddit Story, Gameplay AI Avatar
└── assets/
    ├── refs/                           # Character refs (генерируются один раз, переиспользуются)
    └── avatars/                        # AI-аватар для gameplay-ai-avatar (один на игру)
```

Конфиг игры (`{GAME_TAG}.md`) содержит:
- Visual Style Guide (палитра, освещение, prompt prefix)
- Character Prompt Blocks (минимум 8 визуальных деталей на персонажа)
- Tone of Voice
- Музыка (опц.)

Ассеты дублируются в Supabase (`game_assets` таблица).

---

## Очередь задач

Автоматическая обработка через Supabase. Таблица `video_tasks`: `pending → running → completed/failed`.

Скрипты:
- `queue/worker.sh` — автоворкер, проверяет очередь каждые 30 сек
- `queue/check-queue.sh` — проверка + атомарный claim задачи
- `queue/update-task.sh` — обновление статуса
- `queue/add-task.sh` — добавление задачи

---

## TODO

- [ ] Фаза 0: автоматический запрос game_assets в pipeline (сейчас ручной)
- [ ] Фаза 5: логирование в `video_agent_runs` (когда таблица будет готова)
- [ ] Game configs: создать `games/ark/ark.md`, `games/pubg/pubg.md`
- [ ] Cost tracking: персистентный подсчёт стоимости генераций
