# Формат: Serial Drama (Infinite Micro-Drama)

Сериальные микро-драмы с brainrot эстетикой и бесконечным сюжетом. Каждый эпизод — 25-40 секунд, 3-5 клипов, cliffhanger в конце.

---

## Детекция формата

Формат "serial-drama" активируется если IDEA содержит:
- "serial", "episode", "series", "ep1", "ep2", "сериал"
- ИЛИ указан `series_id` существующего сериала

---

## Art Direction

**Стиль: Pixar/Disney 3D — около-пиксар.**

- Все персонажи — стилизованные 3D, пластиковые текстуры, экспрессивные лица
- `style_tags` берутся из game config (для Roblox: blocky Pixar 3D; для MLBB: anime Pixar hybrid)
- Мягкое ambient освещение, cinematic depth of field
- Яркие насыщенные цвета, драматичные тени в эмоциональных моментах

---

## Анимация — ТОЛЬКО микродвижения

**КРИТИЧЕСКОЕ ПРАВИЛО: Минимальная анимация. Никаких резких движений.**

Модель: **Kling 2.6 Pro I2V** для всех клипов.
- `character_speech` = `null` в storyboard — голос ТОЛЬКО через Kokoro TTS overlay
- `generate_audio` = `false` — **ЗАПРЕЩЕНО** давать Kling генерировать аудио/голос. Kling произносит слова некачественно. Весь звук идёт через TTS.

### Разрешённые действия:
- ✅ Поворот головы (медленный)
- ✅ Подъём/опускание бровей
- ✅ Смена выражения лица (улыбка → шок → злость)
- ✅ Жест рукой (указать, помахать, сжать кулак)
- ✅ Лёгкий наклон корпуса вперёд/назад
- ✅ Покачивание, перенос веса с ноги на ногу
- ✅ Моргание
- ✅ Движение окружения: ветер, частицы, свет пульсирует
- ✅ Движение камеры: push in, pull back, drift

### ЗАПРЕЩЁННЫЕ действия:
- ❌ Ходьба, бег, прыжки
- ❌ Удары, замахи, броски
- ❌ Резкие повороты всего тела
- ❌ Перемещение из точки A в точку B
- ❌ Падения, полёты
- ❌ Любые активные физические действия
- ❌ **Kling генерирует голос/слова** — generate_audio ВСЕГДА false. Голос только через Kokoro TTS

**Все сцены — статичные позиции персонажей с мягкой анимацией лица и жестов.**

### Несколько персонажей в кадре

Для динамики допускается **2 персонажа в одном кадре** (максимум, из-за 9:16):
- Один на переднем плане (крупно), второй на среднем плане или сбоку
- Оба в статичных позах с микродвижениями (один поворачивает голову к другому, второй жестикулирует)
- `gaze_direction` ОБЯЗАТЕЛЕН — кто на кого смотрит
- В image_prompt: опиши позицию каждого ("foreground left", "background right, slightly blurred")
- В motion_prompt: опиши микродвижения КАЖДОГО персонажа отдельно
- Используй chain reference обоих персонажей: `image_urls: [ref-char1, ref-char2]`

**Пример image_prompt с 2 персонажами:**
```
[style_tags], [character_1_description], standing in foreground left, looking right at second character with angry expression,
[character_2_description], standing in background right slightly blurred, arms crossed, smug smirk looking down at first character,
[environment], [lighting], [camera_angle], vertical composition, 9:16 aspect ratio
```

**Пример motion_prompt с 2 персонажами:**
```
Camera holds steady at medium shot. Foreground character turns head slowly toward the other, expression shifts to anger, fists clench. Background character raises eyebrow, slight lean back with amused smirk. Ambient particles drift. Tense confrontation energy.
```

---

## Длительность клипа — адаптивная

Агент сам выбирает длину каждого клипа:

| Контент в клипе | Длительность | Когда |
|----------------|-------------|-------|
| Короткая реплика (≤10 слов) | **5s** | Реакция, хук, панчлайн |
| Длинная реплика (>10 слов) | **10s** | Диалог, монолог, развитие |
| Одно действие + реакция | **5s** | Шок, поворот, reveal |
| Развёрнутый момент, 2+ персонажа говорят | **10s** | Конфронтация, объяснение |

**Правило:** выбирай минимально достаточную длину. Если реплика укладывается в 5 секунд — не растягивай на 10.

---

## Pipeline per clip

1. **Image:** Nano Banana 2 → scene image (с chain reference) — $0.04
2. **Animate:** Kling 2.6 Pro I2V → видеоклип — $0.35/5s или $0.70/10s
   - `generate_audio` = `false` **ВСЕГДА** — Kling НЕ генерирует звук. Вся озвучка через TTS
   - `character_speech` = `null` в storyboard
3. **TTS:** Kokoro TTS → аудио реплики — ~$0.02
   - Голос выбирается по эмоции персонажа (см. ниже)
4. **Lipsync:** Kling Lipsync → синхронизация губ — $0.50/5s или $1.00/10s
   - Применяй lipsync **только на крупных планах** (close-up, medium close-up)
   - На wide shot / low angle — достаточно TTS overlay без lipsync (губы не видны)
5. **FFmpeg:** наложение TTS + обрезка + сборка
   - **КРИТИЧНО:** НЕ используй `-shortest` — это обрежет видео до длины аудио!
   - **КРИТИЧНО:** Обрезай каждый клип по длине TTS, НЕ оставляй полное 10s видео с тишиной!

   ### Правило обрезки по TTS:
   ```
   clip_duration = 0.5 (pre-delay) + TTS_duration + 1.0 (post-silence)
   ```
   - 0.5s — пауза перед речью (зритель успевает увидеть кадр)
   - TTS_duration — длина озвучки
   - 1.0s — пауза после речи (зритель осмысляет)
   - Если clip_duration > video_duration → обрезать по видео

   ### FFmpeg паттерн для каждого клипа:
   ```bash
   # Получить длину TTS
   TTS_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 tts.wav)
   CLIP_DUR=$(echo "0.5 + $TTS_DUR + 1.0" | bc)

   # Наложить TTS с задержкой 0.5s и обрезать по длине
   ffmpeg -y -i scene.mp4 -i tts.wav \
     -filter_complex "[1:a]adelay=500|500[tts];[0:a][tts]amix=inputs=2:duration=first[a]" \
     -map 0:v -map "[a]" -t $CLIP_DUR \
     -ar 44100 -ac 2 -c:a aac -b:a 128k \
     scene-final.mp4
   ```

   ### Для lipsync клипов (аудио уже в видео):
   ```bash
   # Обрезать по той же формуле
   ffmpeg -y -i scene-lipsync.mp4 -t $CLIP_DUR \
     -ar 44100 -ac 2 -c:a aac -b:a 128k \
     scene-final.mp4
   ```

   ### Нормализация аудио:
   **ВСЕ клипы** перед склейкой должны иметь одинаковый аудио формат:
   - Sample rate: 44100 Hz
   - Channels: stereo (2)
   - Codec: AAC 128kbps

   Без нормализации concat даёт глитчи/тишину при смене формата между клипами.

### Выбор голоса Kokoro TTS

| Тип персонажа | Голос | Когда |
|---------------|-------|-------|
| Уверенный мужской (sigma, chad) | `am_adam` или `am_eric` | Сарказм, уверенность, угрозы |
| Паника / страх | `af_bella` или `am_puck` | Шок, испуг, отчаяние |
| Усталость / грусть | `am_michael` или `af_river` | Разочарование, усталость |
| Гордость / хвастовство | `am_onyx` или `af_heart` | Флекс, победа |
| Женский (preppy, девочки) | `af_bella` или `af_jessica` | Любой женский персонаж |
| Нуб / невинный | `am_puck` или `af_nova` | Наивность, непонимание |

**Фиксируй голос для каждого персонажа в story_bible.json** — один персонаж = один голос на весь сериал.

---

## Структура эпизода (~25-40s, 3-5 clips)

### Обязательные элементы:

| Фаза | Тайминг | Цель | Клипов |
|------|---------|------|--------|
| **HOOK** | 0-5s | Визуальный парадокс + хук-фраза. Остановка скролла | 1 clip (5s) |
| **CLIMAX** | 5-30s | Диалог, конфронтация, нарастающий темп | 2-3 clips (5-10s каждый) |
| **CLIFFHANGER** | Последние 5s | Обрыв на пике. Шок, reveal, mid-sentence stop | 1 clip (5s) |

### Правила нарратива:

1. **HOOK (первый клип):**
   - Визуальный контраст: бедный нуб рядом с роскошным домом / спокойная сцена перед хаосом
   - Хук-фраза: провокация, вопрос, шокирующее заявление
   - Пример: *"Everybody laughed at the bacon hair... they had NO idea what was coming"*

2. **CLIMAX (середина):**
   - Плотный диалог, каждый клип содержит реплику
   - Нарастание конфликта: от разговора → к конфронтации → к reveal
   - Минимум 2 разных персонажа должны говорить за эпизод
   - Brainrot лексика в диалогах (rizz, sigma, cooked, negative aura)

3. **CLIFFHANGER (последний клип):**
   - Обрыв на самом интересном месте
   - Варианты: mid-sentence, reveal нового персонажа, неожиданный поворот
   - Последняя реплика ОБЯЗАТЕЛЬНО обрывается или заканчивается шоком
   - "TO BE CONTINUED..." overlay на последние 2 секунды

---

## Story Bible — persistent state

Файл `output/{series_id}/story_bible.json` хранит состояние вселенной между эпизодами.

### Структура:

```json
{
  "series_id": "roblox-noob-revenge",
  "game_tag": "Roblox",
  "title": "The Noob Who Was a Secret Millionaire",
  "style_tags": "Roblox-inspired Pixar-style 3D...",
  "created_at": "2026-03-27",
  "last_episode": 0,

  "characters": [
    {
      "name": "Noob Dave",
      "role": "protagonist",
      "character_description": "Roblox-style blocky humanoid...",
      "voice": "am_puck",
      "status": "new to the server, secretly rich",
      "aura_points": 0,
      "relationships": {}
    }
  ],

  "active_loops": [],
  "closed_loops": [],

  "world_state": {
    "location": "Roblox server lobby",
    "important_items": [],
    "key_events": []
  },

  "anti_repetition": {
    "recent_phrases": [],
    "recent_hooks": [],
    "recent_cliffhangers": []
  },

  "episode_summaries": []
}
```

### Правила обновления Story Bible:

**Перед генерацией (State Analysis):**
1. Загрузи `story_bible.json` из `output/{series_id}/`
2. Проанализируй: кто в каком статусе, какие петли активны, какой level ауры
3. Определи что должно произойти в этом эпизоде (Loop Management)

**После генерации (State Transition):**
1. Обнови `characters[].status` и `aura_points`
2. Обнови `relationships` если изменились
3. Обнови `active_loops` / `closed_loops`
4. Добавь `episode_summaries[]` с кратким содержанием + cliffhanger
5. Обнови `anti_repetition` — добавь использованные фразы, хуки, клиффхэнгеры
6. Обнови `world_state` — локация, важные предметы, события
7. Инкрементируй `last_episode`

---

## Loop Management (Recursive Continuity)

Петли интриги — нерешённые конфликты, которые удерживают зрителя.

### Правило 5 эпизодов:
- Каждые 5 эпизодов **закрой 1 малую петлю** (minor loop)
- Но **открой 2 новых** более масштабных
- Никогда не закрывай ВСЕ петли — минимум 2 активных всегда

### Типы петель:

| Тип | Длительность | Пример |
|-----|-------------|--------|
| **Minor** | 2-5 эпизодов | "Кто украл предмет?" |
| **Major** | 10-20 эпизодов | "Скрытая личность главного героя" |
| **Eternal** | Никогда не закрывается | "Война серверов" |

### Правило "No Finality":
- Любая победа — начало новой беды
- Любое раскрытие — порождает новую тайну
- Сериал НИКОГДА не заканчивается

---

## Retention Strategy (обязательный блок)

Каждый эпизод ОБЯЗАН содержать в storyboard:

```json
{
  "retention_strategy": "Reveal that the noob has a secret golden item triggers curiosity — viewer MUST see next episode to learn what it does",
  "active_loops": ["noob's secret identity", "slender's revenge plan"],
  "cliffhanger": "Noob opens inventory and golden light illuminates his face — cut to black"
}
```

---

## Anti-Repetition Check

Перед написанием storyboard проверь `story_bible.json → anti_repetition`:

1. **Фразы:** Не повторяй фразы из последних 8 эпизодов
2. **Хуки:** Не используй тот же тип hook (если прошлый был "question hook" — используй "contrast hook" или "statement hook")
3. **Клиффхэнгеры:** Не повторяй тот же приём (если прошлый был "mid-sentence" — используй "reveal" или "unexpected entrance")
4. **Метафоры/сравнения:** Разнообразие обязательно

---

## Storyboard additions для serial-drama

Дополнительные поля в storyboard.json (помимо стандартных):

```json
{
  "format": "serial-drama",
  "series_id": "roblox-noob-revenge",
  "episode_number": 1,
  "story_bible_path": "output/roblox-noob-revenge/story_bible.json",
  "retention_strategy": "...",
  "active_loops": ["..."],
  "cliffhanger": "...",
  "episode_summary": "краткое содержание для story bible"
}
```

---

## "TO BE CONTINUED..." Overlay

На последний клип финального видео — FFmpeg drawtext:

```bash
$FFMPEG -y -i final.mp4 \
  -vf "drawtext=text='TO BE CONTINUED...':fontsize=48:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-120:enable='between(t,duration-2,duration)'" \
  -c:a copy final-overlay.mp4
```

- Текст: белый с чёрной обводкой
- Позиция: по центру, нижняя часть экрана
- Появляется: за 2 секунды до конца видео
- Заменить `duration` на реальную длительность видео (получить через `ffprobe`)

---

## Бюджетные лимиты

### Стоимость с generate_audio=false

| Компонент | 5s клип | 10s клип |
|-----------|---------|----------|
| Image (Nano Banana 2) | $0.04 | $0.04 |
| Kling I2V (no audio) | $0.35 | $0.70 |
| Kokoro TTS | $0.02 | $0.02 |
| Lipsync (если face detected) | $0.50 | $1.00 |
| **Итого с lipsync** | **$0.91** | **$1.76** |
| **Итого без lipsync** | **$0.41** | **$0.76** |

> **1×10s выгоднее чем 2×5s** — та же цена за Kling, но 1 image вместо 2, 1 lipsync вместо 2.

| Вариант | Клипов | Стоимость | Когда |
|---------|--------|-----------|-------|
| Минимальный | 3 × 5s | ~$1.75-2.75 | Короткий эпизод |
| Типичный | 2×10s + 1×5s | ~$3-4.50 | Стандартный эпизод |
| Максимальный | 3×10s | ~$4-5.30 | Длинный эпизод |

**Лимит:** $10.00 на эпизод. Остановись если расход > $9.00.

**Оптимизация:**
- `generate_audio = false` — экономит 50% на Kling ($0.07/s вместо $0.14/s)
- Lipsync только на крупных планах с выраженными чертами лица
- Предпочитай 10s клипы вместо 2×5s

---

## Пример: Episode 1 — "The Noob Who Was a Secret Millionaire"

### Story Bible (инициализация):
```json
{
  "series_id": "roblox-noob-revenge",
  "game_tag": "Roblox",
  "title": "The Noob Who Was a Secret Millionaire",
  "last_episode": 0,
  "characters": [
    {
      "name": "Noob Dave",
      "role": "protagonist",
      "character_description": "Roblox-style blocky humanoid character, bright yellow smooth plastic skin, simple blue torso shirt with no details, bright green pants, round head with wide innocent eyes, small curved mouth, stubby short limbs, toy-like proportions with oversized head, matte plastic texture",
      "voice": "am_puck",
      "status": "just joined the server",
      "aura_points": 0,
      "relationships": {}
    },
    {
      "name": "King Rex",
      "role": "antagonist",
      "character_description": "Roblox-style blocky humanoid with oversized golden crown with embedded jewels, thick diamond chain necklace with dollar pendant, white fluffy fur coat over gold vest, designer sunglasses pushed up on forehead, smug arrogant expression with raised eyebrow, glossy shiny plastic texture",
      "voice": "am_onyx",
      "status": "self-proclaimed server king",
      "aura_points": 500,
      "relationships": {}
    }
  ],
  "active_loops": [],
  "closed_loops": [],
  "world_state": {
    "location": "Roblox Adopt Me server lobby",
    "important_items": [],
    "key_events": []
  },
  "anti_repetition": {"recent_phrases": [], "recent_hooks": [], "recent_cliffhangers": []},
  "episode_summaries": []
}
```

### Storyboard sketch:

**Clip 1 (HOOK, 5s, close-up):**
- Noob Dave стоит в лобби, смотрит вокруг с широко открытыми глазами
- TTS: *"So uh... this is my first day on this server..."*
- Motion: Camera slight push-in. Character turns head slowly, eyes widen. Ambient neon signs glow.

**Clip 2 (CLIMAX, 10s, medium shot):**
- King Rex стоит перед Noob Dave, смотрит сверху вниз, презрительная ухмылка
- TTS (Rex): *"Bro really showed up with ZERO drip. Negative aura detected. You don't belong here."*
- TTS (Dave): *"I... I just wanted to play..."*
- Motion: Camera holds steady. Rex leans forward slightly, raises hand dismissively. Dave shrinks back, expression shifts to sad.

**Clip 3 (CLIMAX, 5s, wide shot):**
- Другие игроки вокруг смеются, указывают на Dave
- TTS: *"Even the NPCs got more style than this bacon hair lookin—"*
- Motion: Camera drifts slightly. Background characters' heads turn. Dave clenches fists, jaw tightens.

**Clip 4 (CLIFFHANGER, 5s, close-up):**
- Dave открывает инвентарь, золотой свет озаряет его лицо
- TTS: *"You know what... let me show you something..."*
- Motion: Camera pushes in on face. Golden light illuminates from below. Eyes narrow, slight smirk appears. Cut to black.
- **"TO BE CONTINUED..."** overlay последние 2 секунды

---

## Валидация serial-drama storyboard

Помимо стандартной валидации (из `rules/storyboard.md`), проверь:

- [ ] `format: "serial-drama"` присутствует
- [ ] `series_id` заполнен
- [ ] `episode_number` корректен (= story_bible.last_episode + 1)
- [ ] `retention_strategy` заполнен и конкретен
- [ ] `active_loops` актуальны
- [ ] `cliffhanger` описан
- [ ] Первый клип — HOOK (визуальный парадокс + хук-фраза)
- [ ] Последний клип — CLIFFHANGER (обрыв на пике)
- [ ] Каждый клип содержит реплику (character_speech through TTS)
- [ ] Brainrot лексика присутствует в диалогах
- [ ] Анимация — ТОЛЬКО микродвижения (нет ходьбы, бега, ударов)
- [ ] Длительность клипов адаптивная (5s для коротких, 10s для длинных реплик)
- [ ] `character_speech: null` во ВСЕХ сценах (Kling I2V, голос через TTS)
- [ ] Story bible загружена (если episode > 1) и будет обновлена после генерации
- [ ] Anti-repetition check пройден (нет повторов из последних 8 эпизодов)
