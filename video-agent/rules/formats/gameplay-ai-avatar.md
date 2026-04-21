# Формат "Gameplay AI Avatar" — Говорящая голова + Геймплей

AI-аватар (talking head) снизу экрана рассказывает про оффер/бонусы игры, а сверху идёт геймплей. Формат для продвижения офферов через TikTok/Shorts.

Этот файл — **playbook**: когда использовать, концепт, брифы каждой роли. Крафтовые правила — в `rules/roles/*.md`.

---

## Когда использовать

Ключевые слова: «gameplay ai avatar», «ai avatar», «talking head», «offerwall», «offer», «оффер», «бонус», «bonus», «free diamonds», «free gems», «download and get», «скачай и получи».

---

## Концепт

- **Аватар (talking head):** AI-персонаж снизу экрана, говорит про оффер
- **Геймплей:** готовые клипы из `games/{GAME_TAG}/gameplay/` сверху экрана
- **Split-screen:** 60% геймплей (1080×1152) сверху / 40% аватар (1080×768) снизу
- **Длительность:** 25–40 сек
- **Бюджет:** до $5 (~$1.90 типичный). Остановись если расход > $4.50.
- **Языки:** 29 языков (ElevenLabs multilingual v2)

### Визуальная раскладка (1080×1920, 9:16)

```
+------------------+
|                  |
|   GAMEPLAY       |  <- 60% (1080×1152)
|                  |
+------------------+
|  AI AVATAR       |  <- 40% (1080×768)
|  (talking head)  |
+------------------+
```

---

## Параметры запуска

| Параметр | Описание | Пример |
|---|---|---|
| `game_tag` | Тег игры (должен совпадать с папкой `games/{game_tag}/gameplay/`) | `MLBB` |
| `offer_text` | Описание оффера | `"Download MLBB and get 500 diamonds, reach level 10"` |
| `language` | Язык скрипта и голоса (ISO код) | `EN`, `RU`, `PT-BR` |

Формат запуска: `gameplay ai avatar: {offer_text}, {language}`

---

## Бюджет

| Статья | Стоимость |
|---|---|
| Avatar ref (NB2, если нет в asset bank) | $0.04 |
| ElevenLabs TTS (~30s) | ~$0.17 |
| Kling Avatar v2 Standard (~30s) | ~$1.68 |
| Gameplay (готовые клипы) | $0 |
| FFmpeg, music (локально) | $0 |
| **Типичный** | **~$1.90** |

---

## Структура скрипта: Hook → Offer → Proof → CTA

| Секция | Время | Что говорит аватар | Что на геймплее |
|---|---|---|---|
| **HOOK** | 0–5s | Шок/парадокс, остановка скролла | Самый эпичный момент |
| **OFFER** | 5–15s | Объяснение оффера конкретно и просто | Красивый геймплей, прокачка |
| **PROOF** | 15–25s | Social proof — «я уже получил…» | Геймплей с наградами |
| **CTA** | 25–35s | Призыв к действию с urgency | Финальный эпик |

### Screenwriting правила

**Tone:** энергичный, brainrot-friendly, как будто друг рассказывает лайфхак. Framing «я нашёл и делюсь», не корпоративная реклама.

**Обязательные элементы:**
- Конкретные цифры в каждом ролике («500 diamonds», «level 10», «3 days»)
- Urgency/дедлайн («before they remove it», «only this week»)
- Social proof («I already got…», «everyone's doing this»)
- Вопрос или парадокс в hook («Why is nobody talking about this?»)
- От первого лица — «I found this…», «I already got…»

**Запрещено:**
- Корпоративный тон («мы рекомендуем»)
- Длинные предложения (макс 15–20 слов)
- Абстракция без конкретики («get cool stuff» → «get 500 free diamonds»)
- Скучный hook («Hey guys, today I want to tell you about…»)

### Примеры hook-ов

**EN:** «Why is NOBODY talking about this free diamond glitch?» / «They're literally paying you to play this game right now» / «Stop scrolling — this offer expires tomorrow»

**RU:** «Почему никто не говорит про эту халяву с алмазами?» / «Мне буквально заплатили за то что я играю» / «Стоп скроллинг — этот оффер заканчивается завтра»

---

## Storyboard Schema

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
    "offer": "All you gotta do is download Mobile Legends through the link in my bio, play until level 10, and boom — 500 diamonds.",
    "proof": "I already got mine yesterday, look — spent them all on the new Lancelot skin. Not a drill, it actually works.",
    "cta": "Link in bio, go go go! But hurry, they could remove this any day now."
  },
  "gameplay_clips": ["games/MLBB/gameplay/epic-moment-1.mp4"],
  "total_duration_sec": 30
}
```

---

## Консистентность аватара (asset bank)

**Один аватар = одна игра.** Аватар генерируется ОДИН РАЗ и переиспользуется во всех роликах этой игры — зритель узнаёт «блогера».

### Порядок

1. **Проверь asset bank:** `GET /rest/v1/game_assets?game_tag=eq.{GAME_TAG}&asset_type=eq.avatar_ref&select=*`
2. **Если есть** — используй `url` как `image_url` (пропусти генерацию)
3. **Если нет** — сгенерируй через NB2, затем сохрани в Supabase Storage (`avatars/{GAME_TAG}/avatar-ref.png`) и зарегистрируй в `game_assets`:
   ```sql
   INSERT INTO game_assets (game_tag, character_name, asset_type, url, prompt_block, tags)
   VALUES ('{GAME_TAG}', 'avatar', 'avatar_ref', '{PUBLIC_URL}', '{PROMPT_USED}',
           '["avatar", "gameplay-ai-avatar"]');
   ```
4. **Если query упал** (timeout) — генерируй новый, но **не сохраняй** в asset bank (чтобы не дублировать)

**НИКОГДА не генерируй аватар повторно** если он есть в asset bank.

---

## Двухэтапная генерация: TTS → согласование → Avatar

TTS стоит ~$0.17, Avatar ~$1.68. **НЕ запускай Avatar** пока голос не одобрен.

1. Sound генерирует TTS → Manager отдаёт на согласование
2. После одобрения → Animator запускает Kling Avatar v2 с TTS audio_url из Supabase

---

## Требования к gameplay клипам

Файлы в `games/{GAME_TAG}/gameplay/`:

| Параметр | Требование |
|---|---|
| Формат | `.mp4` (H.264) |
| Разрешение | **≥720p по ширине**. Клипы <720px отбраковываются (при scale=1080:-2 растягиваются в мыло) |
| Aspect ratio | любой (будет масштабирован в 1080×1152) |
| Длительность | ≥10 сек (для обрезки) |
| Содержание | эпичные моменты геймплея, не меню/загрузка |

Manager в Фазе 0 валидирует наличие и разрешение клипов. Если папка пуста или все <720px → статус `failed`, сообщить пользователю.

### Обрезка геймплея

Геймплей обрезается по длительности Avatar (после 1.3x speedup). Если клипов несколько — выбери эпичные моменты и concat-ни до нужной длительности. **Сохраняй аудио геймплея** (будет на 25% громкости в финале).

---

## Брифы ролям

### Scenarist

- Структура: Hook → Offer → Proof → CTA (см. таблицу выше)
- Каждая секция ≤20 слов; hook ≤20 слов + вопрос/парадокс
- Конкретные цифры, urgency, social proof
- Tone: энергичный, от первого лица; НЕ корпоративный
- Один клип Avatar на весь ролик (не дробить на сцены — 30s монолог), длительность = оценка по ~2.5 слова/сек
- **НЕТ title cards / brainrot-тегов** — только drawtext субтитры на стыке split-screen
- Общие правила — `rules/roles/scenarist.md`

### Storyboarder

- Avatar ref — полуреалистичный стиль (не мультяшный, не фотореалистичный)
- Portrait 3:4, upper body, смотрит в камеру, лёгкая улыбка с зубами (критично для lipsync)
- Фон: уютная комната с геймерским сетапом, хорошее освещение
- **Только если нет в asset bank** — проверяй первым делом
- Общие правила — `rules/roles/storyboarder.md`

### Animator

- **Kling Avatar v2 Standard** (`fal-ai/kling-video/ai-avatar/v2/standard`) — один клип на весь ролик
- **`audio_url` обязательно Supabase public URL** (не fal.ai temp) — polling Avatar занимает минуты
- Motion prompt: «energetic gaming blogger speaking to camera, natural hand gestures, nodding»
- **Обязательно 1.3x speedup** после генерации Avatar (`setpts=PTS/1.3`, `atempo=1.3`) — на нативной скорости вяло
- После speedup: `AVATAR_DUR = ffprobe duration` — используется для обрезки геймплея
- Общие правила — `rules/roles/animator.md`

### Sound

- TTS через fal.ai ElevenLabs — `voice` (имя, не `voice_id`), `stability` по тону (0.25 energetic, 0.30 drama, 0.50 calm), `language_code` ISO
- Мужские глубокие голоса: `George`, `Daniel`, `Adam`, `Brian`, `Chris`
- **Субтитры: drawtext + faster_whisper** (не PIL PNG — этот формат использует ffmpeg-full с libfreetype)
  - Шрифт: Montserrat Bold 42px (`/Users/admin/Library/Fonts/Montserrat-Bold.ttf`)
  - Фон: непрозрачная чёрная полоса `y=1100, h=104` (drawbox)
  - Позиция: `y=1122` (на стыке split-screen)
  - Акцент: каждый 5-й сегмент жёлтый
  - Сегменты 3–4 слова, `start[N] = max(end[N-1], orig_start)` (анти-наложение)
- **Транскрибируй `avatar-fast.mp3` (уже ускоренный 1.3x)** — timestamps out-of-the-box корректные
- Фоновая музыка (опционально) — `volume=0.10` (тихий фон)
- Общие правила — `rules/roles/sound.md`

### Editor

- **Split-screen:** `scale + crop`, никогда `pad`
  - Геймплей: `scale=1080:-2,crop=1080:1152:0:(ih-1152)/2` (убирает UI сверху и снизу)
  - Аватар: `scale=1080:-2,crop=1080:768:0:0` (лицо остаётся, обрезается низ)
  - `vstack=inputs=2` (геймплей сверху, аватар снизу) = 1080×1920
- **Аудио-микс:** голос Avatar 100%, gameplay 25% (фон); `amix=inputs=2:duration=first`
- Если у gameplay нет audio track — только Avatar audio
- `-r 30` единый fps; финал **строго 1080×1920** (`ffprobe` проверить)
- Музыка (если есть): `volume=0.10`, `amix` с основным аудио; НИКОГДА `-shortest`
- Общие правила — `rules/roles/editor.md`

---

## Выходные файлы

```
output/YYYY-MM-DD/{GAME_TAG}/gameplay-ai-avatar/
├── storyboard.json
├── scenes/refs/avatar-ref.png (только если генерировался)
├── tts-output.mp3
├── avatar.mp4                  # сырой Kling Avatar
├── avatar-fast.mp4             # 1.3x speedup
├── gameplay-trimmed.mp4        # обрезанный геймплей под AVATAR_DUR
├── subs.srt                    # субтитры (faster_whisper)
├── assembled.mp4               # split-screen без субтитров
└── final.mp4                   # с субтитрами + (опц.) музыкой
```

После загрузки: `videos/{GAME_TAG}/{TIMESTAMP}_final.mp4` в Supabase.

---

## Валидация перед публикацией

- [ ] `games/{GAME_TAG}/gameplay/` содержит ≥1 `.mp4`, все клипы ≥720p по ширине
- [ ] Скрипт имеет все 4 секции (hook, offer, proof, cta)
- [ ] Hook ≤20 слов, с вопросом/парадоксом
- [ ] Каждая секция ≤20 слов; есть цифры, urgency, social proof
- [ ] `voice` (имя, не `voice_id`) соответствует `language`
- [ ] Avatar ref проверен в asset bank (переиспользован, если есть)
- [ ] TTS одобрен пользователем ДО запуска Avatar
- [ ] Avatar ускорен 1.3x перед сборкой
- [ ] fps нормализован в 30 перед split-screen
- [ ] Финал 1080×1920, 30 fps, AAC 128k stereo (`ffprobe`)
- [ ] Субтитры drawtext, не наложены друг на друга, жёлтый акцент каждый 5-й
- [ ] Бюджет < $5

---

## Анти-паттерны

- ❌ Kokoro TTS — только ElevenLabs через fal.ai
- ❌ `voice_id` хеш — использовать `voice` имя строкой
- ❌ Запуск Avatar без одобренного TTS ($1.68 в трубу на неутверждённом голосе)
- ❌ Повторная генерация аватара при наличии в asset bank
- ❌ `pad` в split-screen (только `scale + crop`, никаких чёрных полей)
- ❌ Crop аватара по центру (только `crop=W:H:0:0`, чтобы не задеть лицо)
- ❌ Gameplay клипы <720p (будут мылом при scale=1080)
- ❌ Забыть 1.3x speedup (Avatar звучит вяло)
- ❌ Забыть fps normalize до 30 перед split-screen
- ❌ `-shortest` при наложении музыки
- ❌ PIL PNG субтитры (это формат использует drawtext, не PIL)
