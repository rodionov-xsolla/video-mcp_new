# Формат "Gameplay AI Avatar" — Говорящая голова + Геймплей

AI-аватар (talking head) внизу экрана рассказывает про оффер/бонусы игры, а сверху идёт геймплей. Формат для продвижения офферов через TikTok/Shorts.

> **Отладочный режим:** Если в задаче есть фраза «Отладочный режим» — после каждой фазы останавливайся и отправляй результат на согласование с пояснением (что сделано, почему, какие решения приняты). Не переходи к следующей фазе без одобрения. Подробнее — `rules/main/workflow.md`.

---

## Когда использовать

Идея содержит ключевые слова: "gameplay ai avatar", "ai avatar", "talking head", "offerwall", "offer", "оффер", "бонус", "bonus", "free diamonds", "free gems", "download and get", "скачай и получи".

---

## Обзор формата

- **Аватар (talking head):** AI-персонаж внизу экрана, говорит про оффер
- **Геймплей (gameplay):** готовые клипы сверху экрана
- **Пропорции:** 60% геймплей (1080×1152) / 40% аватар (1080×768)
- **Длительность:** 25-40 сек
- **TTS:** ElevenLabs через fal.ai (`fal-ai/elevenlabs/tts/eleven-v3`) — экспрессивный, мультиязычный
- **Модель аватара:** Kling Avatar v2 Standard через fal.ai (`fal-ai/kling-video/ai-avatar/v2/standard`)
- **Языки:** 29 языков (ElevenLabs multilingual v2)
- **Бюджет:** $5 максимум (~$3 типичный)

### Визуальная раскладка (1080×1920, 9:16)

```
+------------------+
|                  |
|   GAMEPLAY       |  <- 60% (1080×1152)
|   (gameplay.mp4) |
|                  |
+------------------+
|  AI AVATAR       |  <- 40% (1080×768)
|  (talking head)  |
|                  |
+------------------+
```

---

## Параметры запуска

При запуске указываются:

| Параметр | Описание | Пример |
|----------|----------|--------|
| `game_tag` | Тег игры (должен совпадать с папкой `gameplay/{game_tag}/`) | `MLBB` |
| `offer_text` | Описание оффера | `"Download MLBB and get 500 diamonds, reach level 10"` |
| `language` | Язык скрипта и голоса (ISO код или название) | `EN`, `RU`, `PT-BR` |

Формат запуска: `gameplay ai avatar: {offer_text}, {language}`

Пример: `gameplay ai avatar: Download MLBB and get 500 diamonds for reaching level 10, EN`

---

## ФАЗА 0: ИНИЦИАЛИЗАЦИЯ

1. Загрузить game config: `games/{GAME_TAG}/{GAME_TAG}.md`
2. Загрузить `tools/fal-ai.md` — API reference (секция 6: HeyGen Avatar IV)
3. Загрузить `rules/main/fallback.md` — обработка ошибок
4. Распарсить параметры оффера из идеи:
   - `game_name` — название игры
   - `bonus` — что дают (diamonds, gems, coins, skin)
   - `condition` — что нужно сделать (reach level 10, complete tutorial)
   - `language` — язык скрипта и голоса
5. **Валидация gameplay клипов:** проверить `games/{GAME_TAG}/gameplay/`:
   - Папка должна существовать и содержать хотя бы 1 `.mp4` файл
   - Если папка пуста → статус `failed`, сообщить пользователю
6. *(опционально)* Загрузить `music/tracks.json` — фоновая музыка

---

## ФАЗА 1: СЦЕНАРИЙ (storyboard.json)

### Структура скрипта: Hook → Offer → Proof → CTA

| Секция | Время | Что говорит аватар | Что на геймплее |
|--------|-------|-------------------|-----------------|
| **HOOK** | 0-5s | Шок/парадокс, останавливающий скролл | Самый эпичный момент |
| **OFFER** | 5-15s | Объяснение оффера конкретно и просто | Красивый геймплей, прокачка |
| **PROOF** | 15-25s | Social proof — "я уже получил..." | Геймплей с наградами |
| **CTA** | 25-35s | Призыв к действию с urgency | Финальный эпик + текст overlay |

### Screenwriting Rules

**Tone:** энергичный, brainrot-friendly, как будто друг рассказывает лайфхак. Не корпоративная реклама — framing "я нашёл и делюсь".

**Framing:** всегда от первого лица — "I found this...", "I already got...", "My friend told me..."

**Обязательные элементы:**
- Конкретные цифры в каждом ролике ("500 diamonds", "level 10", "3 days")
- Urgency/дедлайн ("before they remove it", "only this week", "limited time")
- Social proof ("I already got...", "everyone's doing this")
- Вопрос или парадокс в hook ("Why is nobody talking about this?", "They're literally paying you to play")

**Запрещено:**
- Корпоративный тон ("мы рекомендуем", "скачайте наше приложение")
- Длинные предложения (макс 15-20 слов)
- Абстракция без конкретики ("get cool stuff" → "get 500 free diamonds")
- Скучный hook (никаких "Hey guys, today I want to tell you about...")

### Storyboard Schema

```json
{
  "format": "gameplay-ai-avatar",
  "game_tag": "MLBB",
  "language": "EN",
  "offer": {
    "game_name": "Mobile Legends: Bang Bang",
    "bonus": "500 diamonds",
    "condition": "reach level 10",
    "urgency": "limited time offer"
  },
  "avatar": {
    "ref_url": "https://supabase.../avatars/MLBB/avatar-ref.png",
    "character_description": "Young male gamer, 20s, wearing headphones around neck, casual hoodie, friendly smile, well-lit room background",
    "voice": "George",
    "prompt": "energetic gaming blogger speaking to camera, natural hand gestures, nodding",
    "source": "asset_bank"
  },
  "script": {
    "hook": "Yo, why is NOBODY talking about this? They're literally giving away 500 free diamonds right now!",
    "offer": "All you gotta do is download Mobile Legends through the link in my bio, play until level 10, and boom — 500 diamonds, just like that.",
    "proof": "I already got mine yesterday, look — spent them all on the new Lancelot skin. This is not a drill, it actually works.",
    "cta": "Link in bio, go go go! But hurry, they could remove this any day now."
  },
  "gameplay_clips": ["games/MLBB/gameplay/epic-moment-1.mp4"],
  "total_duration_sec": 30
}
```

---

## ФАЗА 2: CHARACTER REFERENCE (один раз на игру)

### Правило консистентности аватара

**Один аватар = одна игра.** Аватар генерируется ОДИН РАЗ и переиспользуется во ВСЕХ роликах этой игры. Это обеспечивает консистентность — зритель узнаёт "блогера" из ролика в ролик.

**Порядок действий:**
1. Проверь asset bank: `GET /rest/v1/game_assets?game_tag=eq.{GAME_TAG}&asset_type=eq.avatar_ref&select=*`
   - Если запрос не удался (timeout, ошибка) → генерируй новый аватар, но НЕ сохраняй в asset bank (чтобы не дублировать)
2. Если аватар есть → используй его `url` как `image_url` (пропусти генерацию)
3. Если аватара нет → сгенерируй и сохрани в asset bank

### Генерация нового аватара (только если нет в asset bank)

Сгенерируй через Nano Banana 2:

```
Young [gender] gamer in their 20s, [specific details: hair color, clothing],
wearing headphones around neck, casual hoodie, friendly approachable expression,
well-lit room with gaming setup in background,
upper body portrait, looking directly at camera,
semi-realistic style, 3:4 aspect ratio
```

- Стиль: **полуреалистичный** — не мультяшный, но и не фотореалистичный
- Поза: верхняя часть тела, смотрит в камеру
- Фон: уютная комната с геймерским сетапом
- **Рот:** генерируй с лёгкой улыбкой, чтобы были видны зубы. Это улучшает качество липсинка.
- Сохрани как `avatar-ref.png`

### Сохранение в asset bank (обязательно после генерации)

После генерации сохрани аватар в Supabase для переиспользования:

1. Загрузи изображение в Supabase Storage: `avatars/{GAME_TAG}/avatar-ref.png`
2. Зарегистрируй в `game_assets`:
```sql
INSERT INTO game_assets (game_tag, character_name, asset_type, url, prompt_block, tags)
VALUES ('{GAME_TAG}', 'avatar', 'avatar_ref', '{PUBLIC_URL}', '{PROMPT_USED}', '["avatar", "gameplay-ai-avatar"]');
```

**НИКОГДА не генерируй аватар повторно**, если он уже есть в asset bank для этой игры. Один и тот же `image_url` → одно и то же лицо → консистентность.

---

## ФАЗА 3: AVATAR VIDEO

Двухэтапный процесс: **сначала TTS → согласование голоса → затем lipsync-видео.**

**ВАЖНО:** НЕ генерируй avatar video пока голос не одобрен. TTS стоит ~$0.17, avatar ~$1.90 — не трать деньги на lipsync с неутверждённым голосом.

### 3.1 Генерация голоса (ElevenLabs через fal.ai)

**Endpoint:** `POST https://queue.fal.run/fal-ai/elevenlabs/tts/eleven-v3` (async) или `POST https://fal.run/fal-ai/elevenlabs/tts/eleven-v3` (sync)

```bash
curl -s -X POST "https://fal.run/fal-ai/elevenlabs/tts/eleven-v3" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "'"$FULL_SCRIPT"'",
    "voice": "George",
    "stability": 0.3,
    "language_code": "ru"
  }'
```

**ВНИМАНИЕ — параметры fal.ai обёртки НЕ совпадают с прямым ElevenLabs API:**

| Параметр fal.ai | Описание | НЕ путать с |
|---|---|---|
| `voice` | **Имя голоса** строкой ("George", "Daniel") | ~~`voice_id`~~ (хеш) |
| `stability` | Float 0-1, top-level | ~~`voice_settings.stability`~~ |
| `language_code` | ISO 639-1 ("ru", "en") | — |

При передаче неправильных параметров (например `voice_id` вместо `voice`) API **молча** использует дефолтный женский голос Rachel.

**Доступные мужские голоса (глубокие):** `George`, `Daniel`, `Adam`, `Brian`, `Chris`

**Настройки по тону:**

| Тон | stability |
|-----|-----------|
| Energetic / Funny | 0.25 |
| Drama / Authoritative | 0.30 |
| Calm / Narrative | 0.50 |

**Стоимость:** ~$0.30/мин (~$0.17 за 30 сек)

**После генерации — предоставь аудио на согласование.** Не переходи к 3.2 без одобрения.

### 3.2 Генерация avatar video (Kling Avatar v2)

**Endpoint:** `POST https://queue.fal.run/fal-ai/kling-video/ai-avatar/v2/standard`

```bash
RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/kling-video/ai-avatar/v2/standard" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "'$AVATAR_REF_URL'",
    "audio_url": "'$TTS_AUDIO_URL'",
    "prompt": "confident character speaking to camera, subtle head movements, slight hand gestures"
  }')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
```

**Polling:** стандартный fal.ai паттерн (каждые 15 сек). **Важно:** polling через BASE путь модели:
```
Status: https://queue.fal.run/fal-ai/kling-video/requests/{REQUEST_ID}/status
Result: https://queue.fal.run/fal-ai/kling-video/requests/{REQUEST_ID}
```

`audio_url` должен быть публично доступным (загрузи в Supabase Storage перед отправкой).

**КРИТИЧНО: Передача TTS → Kling Avatar.**
1. Сгенерировать TTS → скачать `.mp3` локально
2. Загрузить локальный файл в Supabase Storage (`assets/{game}/tts/clip-N.mp3`)
3. Использовать **Supabase public URL** для `audio_url` в Kling Avatar
4. **НИКОГДА** не перезапрашивать fal.ai result URL — они временные и ненадёжные при повторном запросе
5. **Перед отправкой** — вывести таблицу маппинга и проверить уникальность всех URL:
```
Clip 1: image=kirk.png | audio=supabase.co/.../clip-1.mp3 | text="Captain's log..."
Clip 2: image=worf.png | audio=supabase.co/.../clip-2.mp3 | text="This is..."
```

**Параметры:**
- `image_url` — URL аватар-картинки (из asset bank или загруженный в Supabase)
- `audio_url` — URL аудио (TTS из шага 3.1, загруженный в Supabase)
- `prompt` — описание движений (жесты, повороты головы, настроение)

**Стоимость:** $0.056/сек → 30 сек = ~$1.68

Результат: `avatar.mp4` — видео с lipsync и движениями.

---

## ФАЗА 4: GAMEPLAY PREP

### Требования к gameplay клипам

Клипы в `games/{GAME_TAG}/gameplay/` должны соответствовать:

| Параметр | Требование |
|----------|-----------|
| Формат | `.mp4` (H.264) |
| Разрешение | минимум 720p, рекомендуется 1080p+ |
| Aspect ratio | любой (будет масштабирован в 1080×1152) |
| Длительность | минимум 10 сек (для обрезки) |
| Содержание | эпичные моменты, геймплей, не меню/загрузка |

### Подготовка

1. Проверь папку `games/{GAME_TAG}/gameplay/` — должен быть хотя бы 1 `.mp4`
2. **Проверь разрешение каждого клипа перед использованием:**
```bash
ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0 clip.mp4
```
   - **Минимум 720p по ширине (≥720px).** Клипы ниже 720px — **отбраковать**, не использовать.
   - При `scale=1080:-2` клип 286px растянется в 4x — это мыло. Только 720p+ даёт приемлемое качество.
3. Если клипов несколько — выбери наиболее эпичные моменты из тех, что прошли проверку
4. Нормализуй fps до 30 и обрежь по длительности `avatar.mp4`. **Сохраняй аудио** геймплея:

```bash
FFMPEG=/usr/local/bin/ffmpeg-full/ffmpeg

# Получить длительность аватара
AVATAR_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 avatar.mp4)

# Обрезать и нормализовать геймплей (С аудио)
$FFMPEG -y -i games/MLBB/gameplay/clip1.mp4 -t $AVATAR_DUR \
  -vf "fps=30" \
  -c:v libx264 -preset slow -crf 10 -r 30 -pix_fmt yuv420p \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  gameplay-trimmed.mp4
```

**ВАЖНО:** аудио геймплея **сохраняется** — оно будет подмешано на ~25% громкости при сборке.

Если несколько клипов — concat перед обрезкой:
```bash
cat > gameplay-list.txt << EOF
file 'games/MLBB/gameplay/clip1.mp4'
file 'games/MLBB/gameplay/clip2.mp4'
EOF

$FFMPEG -y -f concat -safe 0 -i gameplay-list.txt \
  -vf "fps=30" \
  -c:v libx264 -preset slow -crf 10 -r 30 -pix_fmt yuv420p \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  -t $AVATAR_DUR \
  gameplay-trimmed.mp4
```

---

## ФАЗА 5: FFmpeg СБОРКА (split-screen)

### 5.1 Нормализация fps (обязательно перед сборкой)

Оба видео ДОЛЖНЫ быть 30 fps перед split-screen:
- `gameplay-trimmed.mp4` — уже нормализован в ФАЗЕ 4 (`-r 30`)
- `avatar.mp4` — проверить: `ffprobe -v error -select_streams v -show_entries stream=r_frame_rate avatar.mp4`
- Если avatar.mp4 НЕ 30fps — нормализовать:
```bash
$FFMPEG -y -i avatar.mp4 -vf "fps=30" -c:v libx264 -preset slow -crf 10 -r 30 \
  -ar 44100 -ac 2 -c:a aac -b:a 128k avatar-30fps.mp4
```

### 5.2 Split-screen: геймплей сверху + аватар снизу

**НИКОГДА не используй `pad` — только `crop`.** Чёрные поля по бокам недопустимы. Финал строго 1080×1920.

```bash
$FFMPEG -y -i gameplay-trimmed.mp4 -i avatar.mp4 \
  -filter_complex "
    [0:v]fps=30,scale=1080:-2,crop=1080:1152:0:(ih-1152)/2[top];
    [1:v]fps=30,scale=1080:-2,crop=1080:768:0:0[bot];
    [top][bot]vstack=inputs=2[v];
    [0:a]volume=0.25[gameplay_audio];
    [1:a]volume=1.0[avatar_audio];
    [avatar_audio][gameplay_audio]amix=inputs=2:duration=first[a]
  " \
  -map "[v]" -map "[a]" \
  -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  -shortest \
  assembled.mp4
```

**Правила масштабирования (scale + crop, НЕ pad):**
- `scale=1080:-2` — масштабируем по ширине до 1080, высота пропорционально
- `crop=1080:HEIGHT:0:Y` — обрезаем до нужной высоты
- **Геймплей (top):** crop по центру `(ih-1152)/2` — убирает UI сверху и снизу
- **Аватар (bottom):** crop сверху `0:0` — лицо остаётся, обрезается только низ
- Итого: top=1080×1152 + bottom=1080×768 = **1080×1920**

**Аудио-микс:**
- **Голос аватара** (`[1:a]`): `volume=1.0` — основной, доминирует
- **Звук геймплея** (`[0:a]`): `volume=0.25` — фоновый, ~25% громкости для атмосферы
- `amix=inputs=2:duration=first` — длительность по голосу аватара
- Если у геймплея нет аудио-дорожки — используй только `[1:a]` как раньше

**Ключевые моменты:**
- `-r 30` и единый fps — предотвращает рассинхронизацию
- Разрешение финала **строго 1080×1920** — проверяй через `ffprobe`

### 5.3 Субтитры на границе экранов

Субтитры размещаются на стыке геймплея и аватара — непрозрачная чёрная плашка, Montserrat Bold.

```bash
$FFMPEG -y -i assembled.mp4 \
  -vf "
    drawbox=x=0:y=1100:w=iw:h=104:color=black@1.0:t=fill:enable='between(t,0,$TTS_DUR)',
    drawtext=text='segment 1':fontsize=42:fontcolor=white:fontfile=/Users/admin/Library/Fonts/Montserrat-Bold.ttf:x=(w-text_w)/2:y=1122:enable='between(t,0.0,1.5)',
    drawtext=text='segment 2':fontsize=42:fontcolor=yellow:fontfile=/Users/admin/Library/Fonts/Montserrat-Bold.ttf:x=(w-text_w)/2:y=1122:enable='between(t,1.5,3.0)'
  " \
  -c:a copy subtitled.mp4
```

**Параметры субтитров:**
- Шрифт: **Montserrat Bold** (`/Users/admin/Library/Fonts/Montserrat-Bold.ttf`), 42px
- Позиция: `y=1122` (на границе top/bottom зон)
- Фон: непрозрачная чёрная полоса `y=1100, h=104`
- Акцент: каждый 5-й сегмент жёлтый, остальные белые
- Сегменты: 3-4 слова, равномерно по длительности TTS

### 5.3 Фоновая музыка (опционально)

```bash
$FFMPEG -y -i assembled.mp4 -i bg-music.mp3 \
  -filter_complex "[1:a]volume=0.10[music];[0:a]volume=1.0[mix];[mix][music]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 128k \
  final.mp4
```

- Микс голос+геймплей из assembled: `volume=1.0` (уже содержит баланс 100% голос / 25% геймплей)
- Музыка: `volume=0.10` (едва слышна, дополнительный фон)
- Если без музыки: `cp assembled.mp4 final.mp4`

**НИКОГДА не используй `-shortest`.**

---

## ФАЗА 6: UPLOAD & LOG

1. Загрузи `final.mp4` в Supabase Storage: `videos/{GAME_TAG}/{TIMESTAMP}_final.mp4`
2. Покажи отчёт о стоимости
3. Покажи итоговую длительность

---

## Бюджет

| Статья | Стоимость |
|--------|-----------|
| Avatar ref (Nano Banana 2) | $0.04 (или $0 из asset bank/user provided) |
| ElevenLabs TTS (~30 сек) | ~$0.17 |
| Kling Avatar v2 Standard (30s) | ~$1.68 |
| Gameplay (готовые клипы) | $0.00 |
| FFmpeg (локальный) | $0.00 |
| Музыка (локальная) | $0.00 |
| **Типичный** | **~$1.90** |

**Лимит:** $5.00. Остановись если расход > $4.50.

---

## Валидация (чеклист перед генерацией)

Перед запуском ФАЗЫ 3 проверь:

- [ ] `games/{GAME_TAG}/gameplay/` содержит хотя бы 1 `.mp4` файл
- [ ] Скрипт содержит все 4 секции: hook, offer, proof, cta
- [ ] Hook ≤ 20 слов, содержит вопрос или парадокс
- [ ] Каждая секция ≤ 20 слов
- [ ] Есть конкретные цифры (количество бонуса, уровень)
- [ ] Есть urgency/дедлайн
- [ ] Есть social proof
- [ ] Нет корпоративного тона / прямой рекламы
- [ ] `voice` (имя, НЕ voice_id хеш) выбран и соответствует `language`
- [ ] `prompt` для Kling Avatar v2 заполнен (описание движений)
- [ ] Avatar ref проверен в asset bank (или сгенерирован новый)
- [ ] Общая длительность скрипта 25-40 сек (оценка: ~2.5 слова/сек)
- [ ] Бюджет не превысит $5.00

---

## Анти-паттерны

**НЕ делай:**
- **НЕ используй Kokoro TTS** — только ElevenLabs через fal.ai
- **НЕ передавай `voice_id`** (хеш) в fal.ai ElevenLabs — используй `voice` (имя строкой)
- **НЕ генерируй avatar video без одобренного голоса** — сначала TTS, согласование, потом lipsync
- **НЕ используй `pad`** в split-screen — только `scale + crop`, никаких чёрных полей
- **НЕ обрезай аватар по центру** — crop снизу (`crop=W:H:0:0`), чтобы не задеть лицо
- Не генерируй новый аватар если он уже есть в asset bank
- Не сжимай gameplay ниже 720p — потеря качества заметна в split-screen
- Не забывай нормализовать fps до 30 перед split-screen
- Не используй `-shortest` при наложении музыки

---

## Выходные файлы

```
output/YYYY-MM-DD/{GAME_TAG}/gameplay-ai-avatar/
├── storyboard.json              # Сценарий (ФАЗА 1)
├── scenes/
│   └── refs/
│       └── avatar-ref.png       # Референс аватара (ФАЗА 2, если генерировался)
├── tts-output.mp3               # Голос ElevenLabs (ФАЗА 3.1)
├── avatar.mp4                   # Аватар с lipsync (ФАЗА 3.2)
├── gameplay-trimmed.mp4         # Обрезанный геймплей (ФАЗА 4)
├── assembled.mp4                # Split-screen без субтитров (ФАЗА 5.2)
├── subtitled.mp4                # С субтитрами (ФАЗА 5.3)
└── final.mp4                    # Финальное видео (ФАЗА 5.4/5.5)
```

---

## Примеры hook-ов (для вдохновения)

**EN:**
- "Why is NOBODY talking about this free diamond glitch?"
- "They're literally paying you to play this game right now"
- "I just got 500 diamonds for FREE and I'm shook"
- "Stop scrolling — this offer expires tomorrow"
- "My friend showed me this and I can't believe it's real"

**RU:**
- "Почему никто не говорит про эту халяву с алмазами?"
- "Мне буквально заплатили за то что я играю"
- "Я только что получил 500 алмазов БЕСПЛАТНО и я в шоке"
- "Стоп скроллинг — этот оффер заканчивается завтра"
- "Друг показал мне это и я не могу поверить что это реально"
