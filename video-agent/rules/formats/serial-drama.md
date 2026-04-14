# Формат "Serial Drama" — Сериальные микро-драмы

Сериальные микро-драмы с brainrot эстетикой и бесконечным сюжетом. Каждый эпизод — 25-40 секунд, 3-5 клипов, cliffhanger в конце.

> **Отладочный режим:** Если в задаче есть фраза «Отладочный режим» — после каждой фазы останавливайся и отправляй результат на согласование с пояснением (что сделано, почему, какие решения приняты). Не переходи к следующей фазе без одобрения. Подробнее — `rules/main/workflow.md`.

---

## Когда использовать

Идея содержит ключевые слова: "serial", "episode", "series", "ep1", "ep2", "сериал", или указан `series_id` существующего сериала.

---

## Обзор формата

- **Концепт:** бесконечные микро-драмы с brainrot эстетикой, cliffhanger-ы, петли сюжета
- **Модель:** Kling 2.6 Pro I2V (`generate_audio: false`)
- **Аудио:** ElevenLabs TTS (озвучка) + Kling Avatar v2 (липсинк для dialogue клипов)
- **Речь:** ElevenLabs → Kling Avatar v2 для dialogue клипов; TTS overlay (aecho) для I2V «за стеклом»
- **Длительность:** 25-40 сек (3-5 клипов × 5-10s)
- **Бюджет:** $10 максимум на эпизод
- **Стиль:** Pixar/Disney 3D render

---

## ФАЗА 0: ИНИЦИАЛИЗАЦИЯ

1. Загрузить `tools/fal-ai.md` — API reference
2. Загрузить `rules/main/fallback.md` — обработка ошибок
3. Загрузить `games/{GAME_TAG}/{GAME_TAG}.md` — конфиг игры
4. Если есть `games/{GAME_TAG}/serial-drama_special.md` → загрузить
5. Получить `game_assets` из Supabase:
   ```
   GET /rest/v1/game_assets?game_tag=eq.{GAME_TAG}&select=*
   ```
6. **Episode 1 (новый сериал):**
   - Инициализируй `games/{GAME_TAG}/serial-drama_story_bible.json` (персонажи, петли, мир)
   - Сгенерируй character references для всех ключевых персонажей
7. **Episode N+1 (продолжение):**
   - Загрузи `games/{GAME_TAG}/serial-drama_story_bible.json`
   - Выполни State Analysis (статусы персонажей, активные петли, anti-repetition)
   - Выполни Loop Management (каждые 5 эпизодов: закрой 1 малую петлю, открой 2 новых)
8. Перейди к Фазе 1 с контекстом Story Bible
9. **После генерации:** обнови story_bible.json (State Transition)
   - Обнови characters status, aura_points, relationships
   - Обнови active_loops / closed_loops
   - Добавь episode_summary + cliffhanger
   - Обнови anti_repetition (фразы, хуки, клиффхэнгеры)

**story_bible.json** хранится в `games/{GAME_TAG}/serial-drama_story_bible.json` (персистентный, не в output).
Эпизоды сохраняются в стандартный output: `output/YYYY-MM-DD/{GAME_TAG}/serial-drama/`

---

## Art Direction

**Стиль: Pixar/Disney 3D — около-пиксар.**

- Все персонажи — стилизованные 3D, пластиковые текстуры, экспрессивные лица
- `style_tags` берутся из game config (для Roblox: blocky Pixar 3D; для MLBB: anime Pixar hybrid)
- Мягкое ambient освещение, cinematic depth of field
- Яркие насыщенные цвета, драматичные тени в эмоциональных моментах

---

## ФАЗА 1: СЦЕНАРИЙ

### Visual Identity

- `style_tags` берутся из game config
- Описания персонажей берутся из Story Bible (поле `character_description`)
- Все описания персонажей — живые, детализированные (кожа, текстуры, детали одежды, выражение лица)

### Структура эпизода (~25-40s, 3-5 clips)

| Фаза | Тайминг | Цель | Клипов |
|------|---------|------|--------|
| **HOOK** | 0-5s | Визуальный парадокс + хук-фраза. Остановка скролла | 1 clip (5s) |
| **CLIMAX** | 5-30s | Диалог, конфронтация, нарастающий темп | 2-3 clips (5-10s каждый) |
| **CLIFFHANGER** | Последние 5s | Обрыв на пике. Шок, reveal, mid-sentence stop | 1 clip (5s) |

### Правила нарратива — ПРИНЦИПЫ СЦЕНАРИЯ

#### Что работает (TikTok/Reels аудитория):
- **Конфликт с первой секунды.** Не «жил-был», а «Ворф ведёт Чехова к шлюзу». Зритель попадает в середину действия.
- **Конкретные, визуальные ставки.** Кто-то умрёт, будет предан, потеряет всё. Не абстрактные эмоции — конкретная угроза в кадре.
- **Короткие, панчевые реплики.** 2-5 секунд на фразу. Не монологи, не речи — удар за ударом.
- **Баланс ACTION / DIALOGUE ~50/50.** Не все клипы — говорящие головы. Action-клипы (I2V) дают визуальный ритм, атмосферу, напряжение. Dialogue (Avatar) двигают сюжет.
- **Каждая сцена двигает сюжет.** Ноль филлера. Если клип убрать и ничего не потеряется — он не нужен.
- **Драма через действия, не слова.** «Ворф опускает глаза» говорит больше, чем монолог на 10 секунд.

#### Что НЕ работает (избегать):
- ❌ Философские/сентиментальные сюжеты («Что Спок никогда не скажет», «вопросы идентичности»)
- ❌ Театральные речи, длинные монологи, пафосные заявления
- ❌ Медленный buildup без конфликта в первых 5 секундах
- ❌ Нелогичные переходы (персонаж вспоминает кого-то без контекста или причины)
- ❌ Все клипы — dialogue (7 из 7 войсоверов = монотонно, дорого, скучно)
- ❌ Путаница форматов (Reddit Story ≠ Serial Drama ≠ Gameplay AI Avatar — каждый формат имеет свою интонацию)

#### Структура:

1. **HOOK (первый клип, ACTION/I2V):**
   - Зритель попадает В СЕРЕДИНУ КОНФЛИКТА — не в начало, не в экспозицию
   - Визуальный удар: кто-то ведёт кого-то к шлюзу / красная тревога / персонаж стоит перед выбором
   - Brainrot overlay текст для остановки скролла
   - Пример: *Ворф ведёт Чехова по коридору. Чехов оглядывается на Кирка.*

2. **CLIMAX (середина, чередование ACTION + DIALOGUE):**
   - Конфликт раскрывается через диалог (Avatar, 2-3 сек каждый) + реакции (I2V, 5 сек)
   - Минимум 2 разных персонажа должны говорить за эпизод
   - Нарастание: первая реплика — вопрос, последняя — невозможный выбор
   - Brainrot лексика в диалогах где уместно (rizz, sigma, cooked, negative aura)

3. **CLIFFHANGER (последний клип, ACTION/I2V):**
   - Обрыв на ВИЗУАЛЬНОМ ДЕЙСТВИИ, не на словах
   - Зритель видит ЧТО произойдёт дальше и хочет узнать КАК
   - Тишина + действие сильнее любой реплики (Ворф опускает глаза, дверь запечатывается, свет гаснет)
   - "TO BE CONTINUED..." overlay на последние 2 секунды

### Длительность клипа — адаптивная

Агент сам выбирает длину каждого клипа:

| Контент в клипе | Длительность | Когда |
|----------------|-------------|-------|
| Короткая реплика (≤10 слов) | **5s** | Реакция, хук, панчлайн |
| Длинная реплика (>10 слов) | **10s** | Диалог, монолог, развитие |
| Одно действие + реакция | **5s** | Шок, поворот, reveal |
| Развёрнутый момент, 2+ персонажа говорят | **10s** | Конфронтация, объяснение |

**Правило:** выбирай минимально достаточную длину. Если реплика укладывается в 5 секунд — не растягивай на 10.

### Схема клипа (JSON)

Каждый клип в storyboard.json содержит следующие поля (помимо стандартных):

```json
{
  "format": "serial-drama",
  "series_id": "roblox-noob-revenge",
  "episode_number": 1,
  "retention_strategy": "...",
  "active_loops": ["..."],
  "cliffhanger": "...",
  "character_speech": null,
  "tts": "Реплика персонажа (текст для ElevenLabs TTS)",
  "camera_angle": "close-up"
}
```

- `character_speech` = `null` — голос через ElevenLabs TTS → Kling Avatar v2
- `tts` — текст реплики для ElevenLabs TTS (dialogue клипы) или TTS overlay с aecho (I2V «за стеклом»)
- `camera_angle` ОБЯЗАН отличаться от соседних клипов

### image_prompt

Шаблон: 40-80 слов, включает:
- `style_tags` из game config
- `character_description` из Story Bible
- состояние персонажа + выражение лица
- `camera_angle` (отличный от соседних клипов)
- 9:16 vertical composition

Правила 9:16:
- Максимум 2 фокусные точки в кадре
- Максимум 2 персонажа в кадре

**Пример image_prompt (1 персонаж):**
```
[style_tags], [character_description], standing in center frame, looking forward with wide innocent eyes and nervous expression, [environment], soft ambient lighting, cinematic depth of field, close-up shot, vertical composition, 9:16 aspect ratio
```

**Пример image_prompt (2 персонажа):**
```
[style_tags], [character_1_description], standing in foreground left, looking right at second character with angry expression,
[character_2_description], standing in background right slightly blurred, arms crossed, smug smirk looking down at first character,
[environment], [lighting], [camera_angle], vertical composition, 9:16 aspect ratio
```

### Anti-Repetition Check

Перед финализацией storyboard проверь `story_bible.json → anti_repetition`:

1. **Фразы:** Не повторяй фразы из последних 8 эпизодов
2. **Хуки:** Не используй тот же тип hook (если прошлый был "question hook" — используй "contrast hook" или "statement hook")
3. **Клиффхэнгеры:** Не повторяй тот же приём (если прошлый был "mid-sentence" — используй "reveal" или "unexpected entrance")
4. **Метафоры/сравнения:** Разнообразие обязательно

### Retention Strategy

Каждый эпизод ОБЯЗАН содержать в storyboard:

```json
{
  "retention_strategy": "Reveal that the noob has a secret golden item triggers curiosity — viewer MUST see next episode to learn what it does",
  "active_loops": ["noob's secret identity", "slender's revenge plan"],
  "cliffhanger": "Noob opens inventory and golden light illuminates his face — cut to black"
}
```

### Сохранение storyboard.json

Сохранить в `output/YYYY-MM-DD/{GAME_TAG}/serial-drama/storyboard.json` до начала генерации.

---

## ФАЗА 2: CHARACTER REFERENCE

Сгенерировать character reference для каждого ключевого персонажа из Story Bible.

- Один ref на персонажа (один раз на весь сериал, переиспользуется в каждом эпизоде)
- Стиль: Pixar/Disney 3D, совпадает с `style_tags` из game config
- Если в `game_assets` есть `reference_image` для персонажа → использовать его вместо генерации
- Для multi-character сцен: `image_urls` включает refs обоих персонажей
- **Рот персонажа на референсе:** генерируй с лёгкой улыбкой, чтобы были видны зубы. Это улучшает качество липсинка на последующих этапах.

**Сохранение:** `scenes/refs/character-ref-{name}.png`

---

## ФАЗА 3: ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ

Генерировать изображения последовательно, по одному клипу за раз.

### Ассеты локации (обязательно для I2V консистентности):

Перед генерацией сцен — сгенерировать **location asset** (фон без персонажей) для каждой уникальной локации эпизода.

- Один background image на локацию (коридор, мостик, каюта и т.д.)
- Стиль совпадает с `style_tags` из game config
- Сохранить в `scenes/refs/bg-{location-name}.png`
- Использовать как реф в `image_urls` при генерации всех сцен в этой локации

**Почему:** Без единого background ref фон меняется между клипами → I2V выглядит рваной, теряется визуальная связность эпизода.

### Chain reference (стандартный паттерн):

- `image_urls`: [character-ref.png, bg-{location}.png] — для первой сцены в локации
- `image_urls`: [character-ref.png, bg-{location}.png, предыдущая-сцена.png] — для последующих сцен (chain)
- Для multi-character сцен: `image_urls` включает refs обоих персонажей + фон

#### ⚠️ Ограничение количества refs в NB2 (POV / over-shoulder кадры):

**Максимум 2 ref-изображения в `image_urls`** для сцен с обзорным ракурсом (коридор, мостик, POV).

- Если передать 3+ refs (char1 + char2 + bg), NB2 пытается «разместить» каждый ref как отдельную сущность → **персонажи удваиваются** (4 фигуры вместо 2)
- **Для POV / over-shoulder / wide кадров:** `[bg-ref, previous-scene-chain]` — без character refs
- **Для кадров с одним персонажем:** `[character-ref, bg-ref]` — максимум
- **Для multi-character I2V:** `[character-ref-1, bg-ref]` — второго персонажа описать словами в промпте, НЕ добавлять его ref

### Формат изображений сцен:

**Все сцены — вертикальный формат 9:16** (608×1080 в NB2).

Квадратный формат (1:1) не используется в serial-drama — это сериал, все кадры вертикальные.

| Тип сцены | Формат NB2 | Примечание |
|-----------|-----------|------------|
| I2V action | 608×1080 (9:16) | Kling I2V нативный формат |
| Avatar/dialogue | 608×1080 (9:16) | Вертикальный портрет, НЕ квадрат |
| Background asset | 608×1080 (9:16) | Фон для локации |

### Рот персонажа на изображениях сцен:
- **Сцены с липсинком** (персонаж говорит, будет применяться lipsync) — генерируй персонажа с лёгкой улыбкой / приоткрытым ртом, видны зубы. Это критично для качества липсинка.
- **Сцены без липсинка** (нет речи, или речь за кадром) — генерируй рот в нужном настроении сцены (злость, удивление, грусть и т.д.).

### Параметры:

- Модель: Nano Banana 2 (`fal-ai/nano-banana-2/edit`)
- Стоимость: $0.04 за изображение

**Сохранение:** `scenes/scene-{N}/scene-{N}.png`

---

## ФАЗА 4: АНИМАЦИЯ

Анимировать каждое изображение через Kling 2.6 Pro I2V.

### Параметры:

- Модель: `fal-ai/kling-video/v2.6/pro/image-to-video`
- `generate_audio` = `false` — **ВСЕГДА**. Kling НЕ генерирует звук. Вся озвучка через TTS
- `character_speech` = `null`
- `duration`: `"5"` или `"10"` (адаптивно, согласно storyboard)
- Валидация: файл > 1000 байт

#### Polling (fal.ai async):
```bash
# Submit:
POST https://queue.fal.run/fal-ai/kling-video/v2.6/pro/image-to-video
# → получаем request_id

# Status (ВАЖНО — base path = fal-ai/kling-video, НЕ полный endpoint):
GET https://queue.fal.run/fal-ai/kling-video/requests/{REQUEST_ID}/status

# Result:
GET https://queue.fal.run/fal-ai/kling-video/requests/{REQUEST_ID}
```
Polling каждые 15 сек, таймаут 10 мин. См. `rules/main/fallback.md` для таблицы base paths всех моделей.

### Разрешённые действия (ТОЛЬКО микродвижения):

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
- ❌ **Kling генерирует голос/слова** — generate_audio ВСЕГДА false

**Все сцены — статичные позиции персонажей с мягкой анимацией лица и жестов.**

### Несколько персонажей в кадре

Для динамики допускается **2 персонажа в одном кадре** (максимум, из-за 9:16):
- Один на переднем плане (крупно), второй на среднем плане или сбоку
- Оба в статичных позах с микродвижениями (один поворачивает голову к другому, второй жестикулирует)
- `gaze_direction` ОБЯЗАТЕЛЕН — кто на кого смотрит
- В image_prompt: опиши позицию каждого ("foreground left", "background right, slightly blurred")
- В motion_prompt: опиши микродвижения КАЖДОГО персонажа отдельно
- Используй chain reference обоих персонажей: `image_urls: [ref-char1, ref-char2]`

**Пример motion_prompt с 2 персонажами:**
```
Camera holds steady at medium shot. Foreground character turns head slowly toward the other, expression shifts to anger, fists clench. Background character raises eyebrow, slight lean back with amused smirk. Ambient particles drift. Tense confrontation energy.
```

### Motion prompt шаблон

#### ⚠️ Motion prompt = ТЕХНИЧЕСКАЯ РЕЖИССУРА, не литература (КРИТИЧНО):

Kling **не понимает** имена персонажей, мотивации, эмоции. Он понимает только:
- **Камера:** куда двигается, какой план, какой ракурс
- **Позиции в кадре:** «figure on the left», «person in foreground»
- **Физические действия:** «turns head right», «hand rises slowly», «jaw tightens»
- **Окружение:** «light on the panel shifts from red to green», «particles drift»

**ЗАПРЕЩЕНО в motion prompt:**
- ❌ Имена персонажей: «Worf turns», «Kirk reacts» → Kling не знает кто это
- ❌ Настроения: «tension fills the room», «dramatic moment» → не конвертируется в движение
- ❌ Мотивации: «realizing the truth», «betrayed by his captain» → абстракция
- ❌ Литературные описания: «the weight of command presses on his shoulders» → ноль визуала

**ОБЯЗАТЕЛЬНО в motion prompt:**
- ✅ «Camera slow push-in from medium to close-up»
- ✅ «Figure on the right slowly turns head left toward the other figure»
- ✅ «Hand rises from waist to chest level, fingers spread»
- ✅ «Indicator light on the wall panel changes from red to green»
- ✅ «Both figures shift weight, the one on the left leans slightly toward the door»

```
Camera [slight push-in / holds steady / drifts slowly].
[Figure position] [micro-action: turns head slowly, raises eyebrow, clenches fist].
[Second micro-action: glances sideways, smirks, eyes widen].
[Environment: ambient particles drift, panel lights pulse, light shifts].
```

Примеры:
- ✅ `Camera holds steady at medium shot. Figure in center turns head slowly to face the viewer, eyebrows raise, mouth drops slightly open. Background panel lights flicker. Tense stillness.`
- ✅ `Slow push-in. Figure on the left extends arm holding a tablet toward figure on the right. Right figure's eyes widen, head pulls back slightly. Overhead light flickers.`
- ❌ `Worf shows Kirk the sealed order with his authorization code, Kirk is shocked` — имена + мотивации + нет физических действий
- ❌ `Character walks up to the other player and pushes him` — перемещение + физический контакт

### Старт + эндфрейм для I2V клипов (обязательно):

Для каждого **I2V action клипа** генерировать два изображения:
- `scene-{N}-start.png` — начальное состояние сцены
- `scene-{N}-end.png` — конечное состояние (куда движется анимация)

Передавать в Kling: `start_image_url` + `end_image_url`. Это даёт направление анимации.

#### ⚠️ Консистентность фона между фреймами — ОБЯЗАТЕЛЬНОЕ ПРАВИЛО:

**Оба фрейма генерировать с одним и тем же `bg-{location}.png` в `image_urls`.** НЕ чейнить эндфрейм от стартфрейма.

- Стартфрейм: `image_urls: [character-ref, bg-{location}]`
- Эндфрейм: `image_urls: [character-ref, bg-{location}]` (другой промпт персонажа — иная поза/выражение)

**Почему не чейн:** При генерации эндфрейма от стартфрейма фон дрейфует — меняется освещение, угол, цвет. Единый `bg-asset` как anchor гарантирует идентичный фон в обоих кадрах и минимизирует артефакты анимации.

#### ⚠️ Консистентность персонажей между фреймами:
- **Один и тот же персонаж** должен быть на старт-фрейме И на энд-фрейме
- **Не менять** угол камеры или локацию между start и end
- Энд-фрейм = продолжение той же сцены (другое выражение лица / другой жест), НЕ другая сцена

**Неправильно:** Кирк на старт-фрейме, Ворф на энд-фрейме → Kling перемешает персонажей в анимации.
**Правильно:** Кирк (удивлён) → Кирк (шокирован), тот же фон, та же камера.

#### ⚠️ Минимальное изменение композиции между start и end (КРИТИЧНО):

Start и end фреймы **ОБЯЗАНЫ быть почти идентичны** по композиции, перспективе и масштабу кадра.

- **Разрешено менять:** выражение лица, цвет индикатора, жест руки, поворот головы, мелкие детали окружения
- **ЗАПРЕЩЕНО менять:** глубину/перспективу (дальний план → крупный), масштаб кадра (зум), угол камеры (фронтально → со спины), расстояние до объекта

**Почему:** Если start = далёкий конец коридора, а end = крупный план у двери, Kling пытается «зумировать» между ними, **деформируя и растягивая фон**. Это выглядит как артефакт, а не как анимация.

**Пример правильно:**
- Start: Кирк и Ворф стоят у двери шлюза, индикатор красный (SEALED)
- End: Кирк и Ворф стоят у двери шлюза, индикатор зелёный (UNLOCKED), повернули головы друг к другу

**Пример НЕПРАВИЛЬНО:**
- Start: Кирк и Ворф в начале длинного коридора, далёкий план
- End: Кирк и Ворф стоят у двери, крупный план ← **ДЕФОРМАЦИЯ**

Для **Avatar/dialogue клипов** — только одно изображение (Kling Avatar сам управляет движением через audio).

### motion_prompt (обязателен для Avatar клипов):

`motion_prompt` **обязателен** для каждого Avatar клипа — без него мимика нейтральная.

Что описывать:
- Конкретные физические маркеры эмоций ("jaw tightens", "eyes narrow" — не "angry")
- Поведение ДО речи, ВО ВРЕМЯ и ПОСЛЕ
- Направление взгляда (прямо в камеру / в сторону)

**Сохранение:** `scenes/scene-{N}/scene-{N}.mp4`

---

## ФАЗА 5: СБОРКА

### 5.1 TTS (ElevenLabs)

Сгенерировать озвучку через ElevenLabs TTS для всех dialogue клипов.

- Текст берётся из поля `tts` в storyboard (не из `character_speech`)
- Голос выбирается по типу персонажа и зафиксирован в story_bible.json
- Параметр: `voice` (имя, не `voice_id`), `language_code`, `stability`

**Эндпоинт:** `POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`
**Auth:** `xi-api-key: $ELEVENLABS_API_KEY`
**Стоимость:** ~$0.30/мин (~$0.10 за типичную фразу 5-15 сек)

#### Выбор голоса ElevenLabs

| Тип персонажа | Голос | Параметры |
|---------------|-------|-----------|
| Мужской (уверенный, авторитетный) | `Daniel` | stability 0.10, style 0.8 |
| Мужской (нейтральный, рассказчик) | `George` | stability 0.30 |
| Мужской (молодой, энергичный) | `Charlie` | stability 0.20 |
| Женский (уверенный) | `Charlotte` | stability 0.25 |
| Женский (нейтральный) | `Rachel` | stability 0.35 |

**Фиксируй голос для каждого персонажа в story_bible.json** — один персонаж = один голос на весь сериал. Поле `voice` = имя голоса (строка), НЕ voice_id хеш.

**Сохранение:** `scenes/scene-{N}/tts-{N}.mp3`

### 5.2 Kling Avatar v2 (lip sync для dialogue клипов)

Для каждого **dialogue клипа**: ElevenLabs TTS → Kling Avatar v2 Standard.

- Загрузить `tts-{N}.mp3` в Supabase Storage → получить URL
- Вызвать `fal-ai/kling-video/ai-avatar/v2/standard` с `image_url` (9:16 сцена) + `audio_url` + `motion_prompt`
- `motion_prompt` обязателен: описывать мимику ДО, ВО ВРЕМЯ и ПОСЛЕ реплики
- Стоимость: ~$0.056/сек (billing по длине видео)
- Kling Avatar добавляет молчащий хвост — обрезать по `audio_dur + 1.0s` (см. 5.3)

#### Polling (fal.ai async):
```bash
# Submit:
POST https://queue.fal.run/fal-ai/kling-video/ai-avatar/v2/standard
# → request_id

# Status (base = fal-ai/kling-video, НЕ полный путь):
GET https://queue.fal.run/fal-ai/kling-video/requests/{REQUEST_ID}/status

# Result:
GET https://queue.fal.run/fal-ai/kling-video/requests/{REQUEST_ID}
```

**Сохранение:** `scenes/scene-{N}/scene-{N}.mp4`

⚠️ **НЕ используй Kling Lipsync (`fal-ai/kling-video/lipsync/audio-to-video`)** — он стоит $0.10/сек и не подходит по бюджету. Используй только Kling Avatar v2.

### 5.3 Масштабирование — разные правила для I2V и Avatar

**I2V action клипы** (`generate_audio=false` → нет аудио в файле):
```bash
VID_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 scene-N.mp4)
ffmpeg -y -i scene-N.mp4 \
  -f lavfi -i "anullsrc=r=44100:cl=stereo" \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -map 0:v -map 1:a -t "$VID_DUR" \
  -r 30 -c:v libx264 -crf 18 -preset fast \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  scene-N-scaled.mp4
```
⚠️ Kling I2V с `generate_audio=false` выдаёт видео **без аудиодорожки**. Без явного `anullsrc` concat сломается.

**Avatar/dialogue клипы** (Kling Avatar добавляет молчащий хвост: video_dur > audio_dur):
```bash
AUDIO_DUR=$(ffprobe -v error -show_entries stream=duration -select_streams a:0 -of csv=p=0 scene-N.mp4)
TARGET=$(python3 -c "print(round($AUDIO_DUR + 1.0, 3))")
ffmpeg -y -i scene-N.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,tpad=stop_mode=clone:stop_duration=1.0" \
  -af "apad=pad_dur=1.0" \
  -t "$TARGET" \
  -r 30 -c:v libx264 -crf 18 -preset fast \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  scene-N-final.mp4
```
⚠️ Kling Avatar добавляет 0.25–1.79s тишины в конец. При concat хвосты суммируются и сдвигают весь тайминг. Всегда обрезать до `audio_dur + 1.0s` через `tpad + apad + -t TARGET`.

### 5.4 Аудио: I2V = тишина, Avatar = lipsync, исключения

**I2V action клипы** — **NO TTS overlay**. Только тихая дорожка (anullsrc из шага 5.3).

**Avatar/dialogue клипы** — аудио уже встроено Kling Avatar (lipsync). Не накладывать TTS поверх.

**Исключение — сцена «за стеклом/дверью»**: персонаж виден через преграду, лицо не видно → TTS накладывается на I2V с muffled эффектом:
```bash
TTS_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 tts.mp3)
CLIP_DUR=$(python3 -c "print(round(0.5 + $TTS_DUR + 1.0, 3))")
ffmpeg -y -i scene-N-scaled.mp4 -i tts-N.mp3 \
  -filter_complex "[1:a]adelay=500|500,aecho=0.8:0.9:10:0.3[tts];[0:a][tts]amix=inputs=2:duration=first,apad[a]" \
  -map 0:v -map "[a]" -t "$CLIP_DUR" \
  -c:v libx264 -crf 18 -ar 44100 -ac 2 -c:a aac -b:a 128k \
  scene-N-final.mp4
```

#### Правило обрезки по TTS (только для I2V с TTS overlay — сцена «за стеклом»):

```
clip_duration = 0.5 (pre-delay) + TTS_duration + 1.0 (post-silence)
```

**КРИТИЧНО: НИКОГДА не используй `-shortest`** — обрежет видео до длины аудио.

### 5.5 Склейка клипов

Concat всех клипов с re-encode (не stream copy):

#### ⚠️ Нормализация FPS перед concat (КРИТИЧНО):

Kling I2V выдаёт **24fps**, Kling Avatar выдаёт **30fps**. При concat без нормализации ffmpeg дропает кадры (до 109 штук), ломая хронометраж — клипы пролетают за 1 секунду или зависают на месте.

**Перед concat обязательно перекодировать ВСЕ I2V клипы в 30fps:**
```bash
ffmpeg -y -i scene-N-scaled.mp4 \
  -vf "fps=30" \
  -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ar 44100 \
  scene-N-30fps.mp4
```

**Проверить после concat:** в выводе ffmpeg должно быть `dup=0 drop=0`. Если есть dropped frames — FPS не нормализован.

**ВСЕ клипы** перед склейкой должны иметь одинаковый формат:
- **FPS: 30** (нормализовать I2V из 24fps)
- Sample rate: 44100 Hz
- Channels: stereo (2)
- Codec: AAC 128kbps

Без нормализации concat даёт глитчи/тишину при смене формата между клипами.

#### ⚠️ Верификация тайминга перед concat (обязательно):

Перед финальной склейкой — вывести тайминг всех клипов и убедиться что всё корректно:

```bash
# Вывести продолжительность каждого клипа и кумулятивный тайминг
CUMULATIVE=0
for clip in scene-1-final.mp4 scene-2-final.mp4 ...; do
  DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $clip)
  echo "$clip: ${DUR}s → cumulative: ${CUMULATIVE}s"
  CUMULATIVE=$(python3 -c "print(round($CUMULATIVE + $DUR, 3))")
done
```

Ожидаемая структура:
- I2V action клипы: фиксированная длительность (5.0-5.1s)
- Avatar dialogue клипы: audio_dur + 1.0s (убедись что хвост обрезан)
- Пауза между репликами: 1.0s встроена в обрезку Avatar

**Не приступай к concat если тайминг не сходится** — пересчитай и пересобери проблемный клип.

### 5.6 Субтитры для dialogue клипов

**Обязательно.** Наложить субтитры поверх финального видео через FFmpeg drawtext.

#### Формат субтитров:

- Шрифт: Montserrat Bold (или Arial Bold если нет)
- Размер: 42px
- Цвет: белый с чёрной обводкой (`borderw=3:bordercolor=black`)
- Позиция: нижняя треть экрана (y=1550 для 1080×1920)
- Тайминг: точно по TTS аудио каждого dialogue клипа

#### Сборка субтитров:

1. Определить точное время начала каждого dialogue клипа в финальном видео (из тайминга 5.5)
2. Построить drawtext фильтр:

```bash
$FFMPEG -y -i concat.mp4 \
  -vf "
    drawtext=text='Реплика 1':fontsize=42:fontcolor=white:borderw=3:bordercolor=black:fontfile=/Users/admin/Library/Fonts/Montserrat-Bold.ttf:x=(w-text_w)/2:y=1550:enable='between(t,START_1,END_1)',
    drawtext=text='Реплика 2':fontsize=42:fontcolor=white:borderw=3:bordercolor=black:fontfile=/Users/admin/Library/Fonts/Montserrat-Bold.ttf:x=(w-text_w)/2:y=1550:enable='between(t,START_2,END_2)'
  " \
  -c:a copy subtitled.mp4
```

- `START_N` = время начала dialogue клипа N в финальном видео
- `END_N` = START_N + TTS_DUR (без паузы хвоста)
- Длинные реплики (>40 символов) — разбить на 2 строки через `\n`
- I2V action клипы — субтитров нет (тишина)

**Сохранение:** `subtitled.mp4` (до TBC overlay)

### 5.7 Финальная сборка — ОДИН ffmpeg pipeline (КРИТИЧНО)

**Собирать финал в ОДНОМ вызове ffmpeg:** concat + музыка + субтитры + TBC overlay + пауза + fade.

**НЕ делать послойно** (сначала concat+музыка → потом tpad+fade поверх → потом overlay). При послойном подходе музыка обрезается на границе оригинала, apad добавляет тишину вместо продолжения музыки.

**Шаблон финальной сборки:**
```bash
ffmpeg -y \
  -i concat.mp4 -i music.mp3 \
  -i subtitle1.png -i subtitle2.png ... -i tbc.png \
  -filter_complex "
    [0:v][2:v]overlay=0:0:enable='between(t,SUB1_START,SUB1_END)'[v1];
    [v1][3:v]overlay=0:0:enable='between(t,SUB2_START,SUB2_END)'[v2];
    ...
    [vN][M:v]overlay=0:0:enable='between(t,TBC_START,TBC_END)'[vfinal];
    [vfinal]tpad=stop_mode=clone:stop_duration=PAUSE,fade=t=out:st=FADE_START:d=FADE_DUR[vout];
    [0:a][1:a]amix=inputs=2:weights='1 0.15':normalize=0,afade=t=out:st=FADE_START:d=FADE_DUR[aout]
  " \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ar 44100 -ac 2 \
  -t TOTAL_DURATION \
  final.mp4
```

**Ключевые моменты:**
- Музыка подмешивается `amix` на ВСЮ длину финала (включая паузу и fade)
- `afade` применяется к уже смикшированному аудио
- Субтитры = PNG overlays через Pillow (если drawtext недоступен из-за отсутствия libfreetype)
- `-t TOTAL_DURATION` = concat_duration + pause + fade
- **Brainrot overlay** — только по согласованию, НЕ добавлять автоматически

### 5.8 "TO BE CONTINUED..." Overlay

- Текст: белый с чёрной обводкой
- Позиция: по центру, нижняя часть экрана
- Появляется: за 2 секунды до конца видео (до fade)
- Реализация: PNG overlay через Pillow (см. 5.7 шаблон)

### 5.9 Фоновая музыка

Наложить фоновую музыку с `volume=0.15`. Музыка встраивается в единый pipeline (см. 5.7).

**NEVER `-shortest`.**

---

## ФАЗА 6: UPLOAD & LOG

1. Загрузить `final.mp4` в Supabase Storage:
   ```
   videos/{GAME_TAG}/{YYYY-MM-DD}/serial-drama_final.mp4
   ```
2. Записать лог в таблицу `video_agent_runs`
3. Обновить Story Bible (State Transition — см. Фазу 0, шаг 9)
4. Показать cost report (разбивка по компонентам: image, video, TTS, lipsync, итого)

---

## Story Bible — persistent state

Файл `games/{GAME_TAG}/serial-drama_story_bible.json` хранит состояние вселенной между эпизодами.

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
      "voice": "Charlie",
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
1. Загрузи `serial-drama_story_bible.json` из `games/{GAME_TAG}/`
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

Перед написанием storyboard проверь `serial-drama_story_bible.json → anti_repetition`:

1. **Фразы:** Не повторяй фразы из последних 8 эпизодов
2. **Хуки:** Не используй тот же тип hook (если прошлый был "question hook" — используй "contrast hook" или "statement hook")
3. **Клиффхэнгеры:** Не повторяй тот же приём (если прошлый был "mid-sentence" — используй "reveal" или "unexpected entrance")
4. **Метафоры/сравнения:** Разнообразие обязательно

---

## Бюджетные лимиты

### Стоимость с generate_audio=false

| Компонент | 5s клип | 10s клип |
|-----------|---------|----------|
| Image (Nano Banana 2) | $0.04 | $0.04 |
| Kling I2V (no audio) | $0.70 | $1.40 |
| ElevenLabs TTS (5-15 сек реплика) | ~$0.05 | ~$0.07 |
| Kling Avatar v2 (dialogue клип) | $0.056/сек | $0.056/сек |
| **Итого I2V (action)** | **$0.74** | **$1.47** |
| **Итого Avatar (dialogue)** | **~$0.32** | **~$0.63** |

> **1×10s выгоднее чем 2×5s** — та же цена за Kling, но 1 image вместо 2, 1 lipsync вместо 2.

| Вариант | Клипов | Стоимость | Когда |
|---------|--------|-----------|-------|
| Минимальный | 3 × 5s | ~$1.75-2.75 | Короткий эпизод |
| Типичный | 2×10s + 1×5s | ~$3-4.50 | Стандартный эпизод |
| Максимальный | 3×10s | ~$4-5.30 | Длинный эпизод |

**Лимит:** $10.00 на эпизод. Остановись если расход > $9.00.

**Оптимизация:**
- `generate_audio = false` — **ВСЕГДА** в serial-drama. Kling-голос плохого качества
- Lipsync только на крупных планах с выраженными чертами лица
- Предпочитай 10s клипы вместо 2×5s
- ⚠️ Kling I2V 5s = **$0.70** (не занижать до $0.35 при планировании)

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
      "voice": "Charlie",
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

## Валидация serial-drama

- [ ] `format: "serial-drama"` присутствует
- [ ] `series_id` заполнен
- [ ] `episode_number` корректен (= story_bible.last_episode + 1)
- [ ] `retention_strategy` заполнен и конкретен
- [ ] `active_loops` актуальны
- [ ] `cliffhanger` описан
- [ ] Первый клип — HOOK (визуальный парадокс + хук-фраза)
- [ ] Последний клип — CLIFFHANGER (обрыв на пике)
- [ ] Dialogue клипы имеют TTS через ElevenLabs + Kling Avatar v2 (не Kokoro, не Kling Lipsync)
- [ ] **Все изображения — 608×1080 (9:16)**, включая Avatar dialogue клипы (НЕ квадрат 1:1)
- [ ] **Каждый клип имеет отдельно сгенерированное scene image** (Фаза 3) — нельзя использовать character ref как кадр
- [ ] **Location assets сгенерированы** для каждой уникальной локации и включены в `image_urls`
- [ ] **Старт- и энд-фреймы I2V содержат одного и того же персонажа** — нет перестановок между фреймами
- [ ] **motion_prompt прописан** для всех Avatar клипов (мимика до/во время/после реплики)
- [ ] **Верификация тайминга** пройдена перед concat (Фаза 5.5) — длительности всех клипов проверены
- [ ] **Субтитры наложены** (Фаза 5.6) — drawtext на все dialogue клипы с точным таймингом
- [ ] Brainrot лексика присутствует в диалогах
- [ ] Анимация — ТОЛЬКО микродвижения (нет ходьбы, бега, ударов, прыжков)
- [ ] Длительность клипов адаптивная: 5s (≤10 слов реплики) или 10s (>10 слов)
- [ ] `camera_angle` отличается для каждого соседнего клипа
- [ ] Story bible загружена (если episode > 1) и будет обновлена после генерации
- [ ] Anti-repetition check пройден (нет повторов из последних 8 эпизодов)
- [ ] "TO BE CONTINUED..." overlay запланирован на последние 2 секунды
- [ ] Chain reference использован для всех изображений (Фаза 3)
- [ ] `generate_audio: false` во всех Kling запросах
- [ ] **Cost log ведётся** с первого API-вызова (не считать по памяти)
- [ ] **Промпты проверены** — не пустые, пути абсолютные
- [ ] **FPS нормализован** — все I2V клипы перекодированы в 30fps перед concat
- [ ] **Motion prompts технические** — позиции в кадре, камера, физические действия (не имена, не эмоции)
- [ ] **NB2 refs ≤ 2** для POV/wide кадров (избежать дублирования персонажей)

---

## Анти-паттерны

**НЕ делай:**
- Не используй `generate_audio: true` — Kling-генерированный голос плохого качества
- **Не используй Kokoro TTS** — только ElevenLabs TTS (`api.elevenlabs.io/v1/text-to-speech`)
- **Не используй Kling Lipsync** (`fal-ai/kling-video/lipsync`) — используй Kling Avatar v2 Standard
- Не передавай `voice_id` хеш в ElevenLabs fal.ai — используй параметр `voice` (имя строкой)
- **Не используй квадратный формат (1:1) для Avatar клипов** — serial-drama строго 9:16 (608×1080). Квадрат даёт неправильное кадрирование и не соответствует финальному 1080×1920
- **Не пропускай генерацию scene images** (Фаза 3) — нельзя использовать character ref напрямую как кадр видео. Каждый клип требует отдельного сгенерированного изображения сцены с правильным фоном и позой персонажа
- **Не менять персонажа между старт- и энд-фреймом** I2V клипа — оба фрейма должны содержать одного и того же персонажа, один и тот же фон, одну и ту же камеру
- **Не пропускай верификацию тайминга** перед concat (Фаза 5.5) — проверь длительность каждого клипа и кумулятивный тайминг перед склейкой
- **Не пропускай субтитры** (Фаза 5.6) — drawtext обязателен для всех dialogue клипов
- Не используй Veo3 T2V для этого формата — только Kling I2V
- Не давай персонажам активных действий (ходьба, бег, прыжки, удары) — только микро-движения
- Не превышай 25 слов на реплику TTS — не уложится в 10 сек
- Не используй `-shortest` в FFmpeg — обрезает видео до длины аудио
- Не закрывай все сюжетные петли — всегда должен оставаться открытый cliffhanger
- Не повторяй хуки/клиффхэнгеры из последних 8 эпизодов (anti-repetition)
- **Не переделывай клипы, которые работают** — если клип выглядит хорошо, не трогай его. Спроси перед переделкой. Каждая лишняя генерация = $0.70+ и риск получить хуже
- **Не собирай финал послойно** — только один ffmpeg pipeline (см. 5.7). Послойная сборка ломает музыку и тайминг

---

## Правила процесса (ОБЯЗАТЕЛЬНО)

### Лог API-вызовов (cost tracking в реальном времени)

**Вести лог КАЖДОГО API-вызова** прямо во время работы — не считать по памяти в конце.

Формат лога (в `{OUTPUT_DIR}/cost_log.txt`):
```
NB2  | scene-1-start.png  | $0.04 | OK
NB2  | scene-1-end.png    | $0.04 | OK
NB2  | scene-5-start.png  | $0.04 | WASTED (empty prompt)
I2V  | scene-2.mp4        | $0.70 | OK
AVT  | scene-3.mp4        | $0.28 | OK (5s)
TTS  | tts-3.mp3          | $0.05 | OK
```

**После каждой фазы** — показать промежуточный итог расходов.
**В финальном отчёте** — точная сумма из лога, не приблизительная оценка.

### Валидация данных перед API-вызовом

Перед отправкой запроса в любой API:
1. **Проверить что промпт не пустой** — вывести первые 50 символов промпта в лог
2. **Проверить что файлы/URL существуют** — если `image_url` из локального файла, убедиться что файл > 0 байт
3. **Проверить абсолютные пути** — `storyboard.json` читать только по полному пути `${OUTPUT_DIR}/storyboard.json`

**Почему:** Пустой промпт = потраченные $0.04-$0.70 впустую. Неправильный путь = пустой промпт.

### Не переделывать без согласования

- Если клип уже сгенерирован и выглядит приемлемо — **НЕ перегенерировать** без явного запроса
- Если хочешь что-то улучшить — **спроси**, показав что именно не нравится и почему
- Лишняя переделка I2V = $0.70, Avatar = $0.28-0.56 — деньги, которые можно было потратить на качество других сцен

---

## Выходные файлы

```
OUTPUT_DIR/
├── storyboard.json
├── scenes/
│   ├── refs/
│   │   ├── character-ref-{name}.png
│   │   └── ...
│   ├── scene-1/
│   │   ├── scene-1.png
│   │   ├── scene-1.mp4
│   │   ├── scene-1-scaled.mp4
│   │   └── tts-1.wav
│   ├── scene-2/
│   │   └── ...
│   └── scene-N/
│       └── ...
└── final.mp4
```

**Также:** `games/{GAME_TAG}/serial-drama_story_bible.json` — персистентный, обновляется после каждого эпизода.
