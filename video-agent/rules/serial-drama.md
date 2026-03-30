# Формат: Serial Drama (Infinite Micro-Drama)

Сериальные микро-драмы с brainrot эстетикой и бесконечным сюжетом. Каждый эпизод — 25-40 секунд, 3-5 клипов, cliffhanger в конце.

## Автономность формата

**Serial-drama — полностью автономный формат.** Не наследует и не зависит от `rules/storyboard.md`.

- `storyboard.md` = правила для ваншот-роликов (один сюжет, без продолжения)
- `serial-drama.md` = правила для сериалов (story bible, эпизоды, персистентное состояние)

**При работе с serial-drama читай ТОЛЬКО этот файл.** `storyboard.md` не применяется.

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

1. **Start frame:** Nano Banana 2 → начальное изображение сцены (с chain reference) — $0.04
2. **End frame:** Nano Banana 2 → конечное изображение сцены (с chain reference) — $0.04
   - End frame показывает КАК сцена заканчивается (изменение позы, выражения, ракурса)
   - Start и end frame — это одна и та же локация, те же персонажи, но другая поза/эмоция/состояние
   - **НЕ путай с переходами между сценами!** Start/end frame — для консистентности ВНУТРИ клипа. Между сценами — кат.
3. **Animate:** Kling 2.6 Pro I2V → видеоклип — $0.35/5s или $0.70/10s
   - `start_image_url`: URL start frame
   - `end_image_url`: URL end frame
   - Kling интерполирует между двумя кадрами → плавная, контролируемая анимация
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

## Структура эпизода (~20-30s, 4-5 clips)

### Обязательные фазы:

| Фаза | Тайминг | Цель | Клипов |
|------|---------|------|--------|
| **ЗАЯВКА** | 0-5s | Ситуация, контекст, интрига. Остановка скролла | 1 clip (5s) |
| **РАЗВИТИЕ** | 5-15s | Диалог, нарастание, расстановка сил | 1-2 clips (5s каждый) |
| **КУЛЬМИНАЦИЯ** | 15-20s | Пиковый момент, конфронтация, reveal | 1 clip (5s) |
| **ПРОБЛЕМА** | Последние 5s | Новая проблема/угроза. НЕ решение, а эскалация | 1 clip (5s) |

### Правила нарратива:

1. **ЗАЯВКА (первый клип):**
   - Wide shot — показать локацию и расстановку сил
   - Контекст: где мы, кто здесь, что происходит
   - Хук-фраза: провокация, вопрос, шокирующее заявление
   - Пример: *"Four against one... real sigma behavior right there."*

2. **РАЗВИТИЕ (середина):**
   - Плотный диалог, каждый клип содержит реплику
   - Нарастание конфликта: от разговора → к конфронтации
   - Минимум 2 разных персонажа должны говорить за эпизод
   - Wide/medium shots — зритель видит локацию и взаимодействие
   - Brainrot лексика в диалогах (rizz, sigma, cooked, negative aura)

3. **КУЛЬМИНАЦИЯ:**
   - Поворотный момент — баланс сил меняется
   - Medium shot — видно реакцию персонажей И контекст

4. **ПРОБЛЕМА (последний клип):**
   - **НИКОГДА не обрывай и не обрезай последний клип!** Он должен быть полноценным
   - Не решение, а НОВАЯ проблема, угроза, вопрос
   - Wide shot — зритель видит масштаб проблемы
   - **Клифхэнгер = КОНКРЕТНАЯ ВИЗУАЛЬНАЯ СИТУАЦИЯ**, не абстракция:
     - ✅ Dave окружён 4 игроками, некуда бежать
     - ✅ Два персонажа стоят лицом к лицу, кулаки сжаты
     - ✅ Shadow стоит на краю площади, все замерли
     - ❌ Абстрактное свечение / пустой фон с персонажем
     - ❌ Обрезанная фраза без визуальной угрозы
     - ❌ Персонаж один на неясном фоне
   - "TO BE CONTINUED..." overlay на последние 2 секунды

### Start frame + End frame (обязательно для каждого клипа)

Каждый клип имеет **два изображения**: start frame и end frame. Kling I2V интерполирует между ними.

**Start frame** — начальное состояние сцены (поза, выражение, расположение).
**End frame** — конечное состояние (изменённая поза, реакция, новое выражение).

**Правила:**
- Start и end — **одна и та же локация**, те же персонажи, но другое состояние
- Разница между ними = **действие клипа** (поворот головы, смена эмоции, жест, реакция)
- **НЕ делай end frame = start frame следующего клипа.** Между клипами — кат. Start/end — только для консистентности ВНУТРИ клипа
- Оба frame генерируются через Nano Banana 2 с одинаковыми `image_urls` (те же character + location refs)
- В storyboard: `image_prompt` (start) и `end_frame_prompt` (end) для каждой сцены

**Камера между start и end frame:**
- Допускается **лёгкое** движение камеры для динамики: slow push-in, subtle drift, slight pan
- Разница в ракурсе между start и end — **минимальная** (не более 10-15°)
- Start: medium shot → End: чуть ближе (не резкий переход в close-up!)
- Start: центр кадра → End: чуть сместился влево/вправо
- **НЕ допускается:** резкая смена ракурса, разворот камеры на 180°, переход wide→close-up

**Пример:**
```json
{
  "index": 1,
  "duration_sec": 5,
  "image_prompt": "...Dave standing at plaza entrance, medium wide shot, neutral expression, arms at sides, looking forward...",
  "end_frame_prompt": "...Dave standing at plaza entrance, slightly tighter framing, eyes wide with shock, mouth slightly open, hands raised defensively...",
  "motion_prompt": "Camera slowly pushes in. Character's expression shifts from neutral to shock — eyes widen, hands rise slightly. Background crowd freezes."
}
```

- `image_prompt` описывает НАЧАЛО действия
- `end_frame_prompt` описывает КОНЕЦ действия
- `motion_prompt` описывает ЧТО ПРОИСХОДИТ между ними (для Kling)

### Правило логичных переходов между клипами

**Каждый клип логически вытекает из предыдущего:**
- Если персонаж стоял на площади в клипе 3 — в клипе 4 он всё ещё на площади (если сюжет не требует иного)
- Смена локации допускается, но должна быть **логически обоснована сюжетом**: персонаж ушёл, параллельное действие с другими персонажами, флешбэк, телепортация в игре
- Что НЕ допускается: случайная смена фона без причины, персонаж на площади → вдруг в пустоте с боке → обратно на площади
- **Все клипы одной локации используют один и тот же location ref** в `image_urls` — визуальная консистентность фона

---

## Asset Bank — переиспользуемые визуальные ассеты

Все ключевые визуальные элементы сериала **генерируются отдельно и сохраняются** для повторного использования. Это обеспечивает визуальную консистентность между эпизодами.

### Что сохраняется

| Тип ассета | Пример | Когда генерируется | Файл |
|------------|--------|-------------------|------|
| **Character ref** | Noob Dave, King Rex | Перед первым появлением персонажа | `ref-{name}.png` |
| **Location ref** | Площадь LUXURIA, тёмный переулок | Перед первым использованием локации | `loc-{name}.png` |
| **Object ref** | Золотой инвентарь, таинственный куб | Перед первым появлением объекта в кадре (НЕ раньше!) | `obj-{name}.png` |

### Хранение

Все ассеты лежат в `output/{series_id}/assets/`:
```
output/roblox-noob-revenge/assets/
├── ref-noob-dave.png         # персонаж
├── ref-king-rex.png          # персонаж
├── ref-shadow.png            # персонаж
├── loc-luxuria-plaza.png     # локация: главная площадь
├── loc-dark-alley.png        # локация: тёмный переулок
├── obj-golden-inventory.png  # объект (генерится только когда показываем!)
└── assets.json               # индекс всех ассетов с URL-ами
```

### assets.json — индекс ассетов

```json
{
  "characters": {
    "noob-dave": {"file": "ref-noob-dave.png", "url": "https://...", "created_episode": 1},
    "king-rex": {"file": "ref-king-rex.png", "url": "https://...", "created_episode": 1}
  },
  "locations": {
    "luxuria-plaza": {"file": "loc-luxuria-plaza.png", "url": "https://...", "created_episode": 1, "description": "Massive golden plaza with neon LUXURIA archway, golden fountain, blocky luxury buildings"}
  },
  "objects": {
    "golden-inventory": {"file": "obj-golden-inventory.png", "url": "https://...", "created_episode": null, "description": "Dave's secret inventory glowing gold — NOT generated until full reveal episode"}
  }
}
```

### Правила использования

1. **Перед генерацией сцены** — загрузи `assets.json`, найди нужные ассеты
2. **image_urls при генерации сцены:** `[character-ref-url, location-ref-url]` — модель копирует стиль персонажа И фона
3. **Для 2 персонажей в кадре:** `[char1-ref-url, char2-ref-url, location-ref-url]`
4. **Новая локация:** сгенерируй отдельно (без персонажей в кадре), сохрани как `loc-{name}.png`, загрузи URL в `assets.json`
5. **Новый объект:** сгенерируй отдельно ТОЛЬКО когда объект впервые появляется в кадре. Не раньше!

### КРИТИЧНЫЕ ПРАВИЛА объектов и раскрытий

- **НЕ генерируй объект заранее.** Если объект заявлен в сюжете через намёк (свечение, тень, упоминание) — его ref НЕ создаётся. Ref создаётся только когда объект **впервые полностью виден в кадре**.
- **Тяни reveal объекта на 2-3+ эпизода.** Ep1: намёк (свечение). Ep2-3: упоминания. Ep4+: полный reveal → генерируй ref.
- **Каждый объект в assets.json содержит `description`** — чёткое описание функций и назначения. Не "mysterious item", а "golden crown that grants server admin privileges to whoever wears it".

### Правило camera/composition

- **Максимум wide/medium shots** — показывают локацию и контекст
- **Минимум close-ups** — только для ключевых эмоциональных моментов (1-2 на эпизод максимум)
- **НЕТ LEGO-элементов** — Roblox ≠ LEGO. Никаких кирпичиков, инструкций по сборке, LEGO-логотипов

---

## Screenwriting Rules

### 1. Речевой паттерн персонажа

Каждый персонаж имеет **уникальный ритм и стиль речи**, зафиксированный в story_bible. TTS-голос — это только тембр. Речевой паттерн — это КАК персонаж строит фразы.

Определи для каждого персонажа в `story_bible.json → characters[].speech_pattern`:

| Пример | Паттерн |
|--------|---------|
| Rex | Короткие команды, ультиматумы. "Get him. Now." / "Wrong answer." Никогда не объясняет — приказывает. |
| Dave | Запинки, паузы, неуверенность → внезапные sigma-моменты. "I... I don't think... actually, nah." |
| Shadow | Максимум 3-5 слов за реплику. Каждое слово — удар. "You're not ready." Молчание = сила. |
| Bacon Bob | Самоуничижительный юмор, длинные фразы, бормотание. "Man, I've been here six months and I still can't..." |
| Bella | Притворно-наивная, вопросительные интонации, скрытая манипуляция. "Wait, like, seriously? That's so... interesting." |

**Правило:** Если убрать имя говорящего — зритель всё равно должен понять КТО говорит по стилю фразы.

### 2. Show Don't Tell

**Не заставляй персонажей объяснять что происходит.** Показывай через действие и реакцию.

| ❌ Tell | ✅ Show |
|---------|--------|
| "They said this server eats noobs alive" | Dave стоит на площади, игроки отворачиваются, один толкает его плечом |
| "He's really rich actually" | Случайный игрок замечает иконку в инвентаре Dave, глаза расширяются |
| "Nobody likes Rex" | Игроки расступаются когда Rex идёт, но за спиной переглядываются |
| "Shadow is dangerous" | Rex, который никого не боится, делает шаг назад увидев Shadow |

**Правило:** Перед каждой репликой спроси — можно ли это ПОКАЗАТЬ вместо того чтобы говорить? Если да — покажи. Реплики — для эмоций, угроз, юмора. Не для экспозиции.

### 3. Delivery Promise — отдавай, не только тизерь

Каждый эпизод ОБЯЗАН дать зрителю **хотя бы один маленький payoff** (ответ, reveal, событие), создавая при этом 2 новых вопроса.

| Эпизод | Payoff (отдаём) | Новые вопросы (создаём) |
|--------|----------------|------------------------|
| Ep1 | Dave приходит на сервер (контекст) | Что у него в инвентаре? Почему он так спокоен? |
| Ep2 | Dave отказывает Rex (действие!) | Что будет? Кто эти игроки что его окружили? |
| Ep3 | Shadow появляется, все отступают | Кто он? Почему Rex его боится? Что он хочет от Dave? |

**Правило:** Если в эпизоде только тизеры и ни одного payoff — переписать. После 3 серий без payoff зритель уходит.

### 4. Тикающие часы (Urgency)

Каждый конфликт должен иметь **дедлайн или давление**. Это создаёт urgency и причину смотреть следующую серию.

| ❌ Без urgency | ✅ С urgency |
|----------------|-------------|
| "Плати tax" | "Плати tax до заката, или тебя банят с сервера" |
| "Trade duel" | "Trade duel через 3 дня. Проиграешь — отдаёшь ВСЁ" |
| "Shadow появился" | "Shadow сказал: у тебя один эпизод чтобы решить" |

**Правило:** Если конфликт может висеть бесконечно без последствий — добавь дедлайн. Дедлайн = давление = engagement.

### 5. B-story / Субплоты

Второстепенные персонажи (Bacon Bob, Bella) должны иметь **свои мини-арки**, которые пересекаются с основным сюжетом.

**Структура B-story:**
- Засев (ep 2-3): короткий момент — Bob что-то прячет, Bella шепчется с кем-то
- Развитие (ep 4-6): B-story начинает влиять на основную — Bob знает секрет Rex'а, Bella играет обе стороны
- Пересечение (ep 7+): B-story сливается с основной и усиливает stakes

**Правило:** В каждом эпизоде минимум **1 момент** (реплика, взгляд, действие) который развивает B-story. Не обязательно целый клип — достаточно одной фразы от второстепенного персонажа.

Фиксируй активные B-stories в `story_bible.json → b_stories[]`:
```json
{
  "b_stories": [
    {
      "id": "b-1",
      "character": "Bacon Bob",
      "seed_episode": 2,
      "description": "Bob knows something about Rex's past that could destroy him",
      "status": "seeded",
      "intersects_main_at": "ep 5-6 estimated"
    }
  ]
}
```

### 6. World Rules — законы мира

Каждая сериальная вселенная имеет **неизменные правила**, которые определяют конфликты и stakes. Правила мира — это фундамент, на котором строится вся драма.

**Что такое world rule:**
- Ограничение или закон, который действует на ВСЕХ персонажей
- Имеет чёткие **последствия** за нарушение
- Создаёт natural stakes без искусственного нагнетания

**Примеры:**

| Rule | Implication | Драматический потенциал |
|------|-------------|------------------------|
| Только одна Admin Crown на сервере | Кто владеет — контролирует всё, может банить любого | Борьба за корону = борьба за власть |
| Fanum Tax обязателен для новичков | Отказ = публичное унижение + bounty на голову | Dave отказывает → мгновенный конфликт |
| Trade Duel — binding contract | Проигравший отдаёт всё, что поставил | Каждый дуэль = всё или ничего |
| Забаненный игрок теряет весь инвентарь | Навсегда. Без возврата. | Угроза бана = угроза потери всего |

**Правила фиксируются в `story_bible.json → world_rules[]`** при создании сериала и НЕ меняются без серьёзной сюжетной причины (которая сама становится major event).

**КРИТИЧНО:**
- Если правило мира заявлено — оно ОБЯЗАНО соблюдаться. Персонаж нарушает правило → последствия наступают. Нельзя "забыть" правило.
- Правила мира создают **естественные конфликты** — используй их вместо искусственного нагнетания.
- При написании сценария **сверяйся с world_rules** — каждый конфликт должен быть обоснован логикой мира.

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
      "speech_pattern": "Hesitant, pauses, stutters — then sudden confident sigma drops. 'I... I don't think... actually, nah.'",
      "status": "new to the server, secretly rich",
      "aura_points": 0,
      "relationships": {}
    }
  ],

  "b_stories": [],

  "asset_bank_path": "output/roblox-noob-revenge/assets/assets.json",

  "active_loops": [],
  "closed_loops": [],

  "world_rules": [
    {
      "rule": "Only one Admin Crown exists on the server",
      "implication": "Whoever holds it controls the server — absolute power, can ban anyone",
      "status": "active"
    },
    {
      "rule": "Fanum Tax is mandatory — every new player pays 30% of inventory to Rex",
      "implication": "Refusing = public humiliation + server-wide bounty",
      "status": "active"
    },
    {
      "rule": "Trade Duels are binding — loser gives up everything they wagered",
      "implication": "No takebacks, no cheating — server enforces the deal",
      "status": "active"
    }
  ],

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
7. **Обнови `world_rules`** — если в эпизоде заявлено новое правило мира, НЕМЕДЛЕННО добавь его в `world_rules[]` с `rule`, `implication`, `status: "active"`
8. **Обнови `b_stories`** — если засеяна новая B-story, добавь в `b_stories[]`
9. **Обнови `characters[].speech_pattern`** — если речевой паттерн уточнился по ходу серии
10. Инкрементируй `last_episode`

**КРИТИЧНО:** Story Bible — единственный источник правды для конкретного сериала. Всё что заявлено в сюжете (правила мира, персонажи, объекты, конфликты) ОБЯЗАНО быть зафиксировано в story_bible.json этого тайтла. Если чего-то нет в библии — этого не существует для следующих серий.

**Новые правила мира можно создавать** по мере развития сюжета — если это органично вытекает из событий. Но перед добавлением нового правила **сверься с существующими `world_rules`** — новое правило НЕ ДОЛЖНО противоречить уже заявленным. Если возникает противоречие — это либо ошибка сценария (исправь), либо сюжетное событие (правило мира меняется, старое получает `status: "overridden"` с указанием эпизода и причины).

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
