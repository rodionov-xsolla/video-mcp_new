# Скилл: Создание нового формата видео

Пошаговая инструкция для агента. Описывает что спросить у пользователя, в каком порядке, какие решения от чего зависят, какие файлы создать и обновить.

**Когда использовать:** пользователь просит создать новый формат видео, который не покрывается существующими 8 форматами.

---

## Шаг 0. Подготовка

Прочитай перед началом:
1. `rules/roles/manager.md` строки 137–146 — таблица Format detection (существующие keywords)
2. `rules/main/budgets.md` — существующие бюджеты и цены моделей
3. 1–2 существующих формата, ближайших по концепции к новому — как reference

---

## Шаг 1. Сбор обязательных данных (Tier 1)

Спроси у пользователя **одним блоком**:

| # | Поле | Что спросить | Пример |
|---|------|-------------|--------|
| 1 | `slug` | Имя формата (kebab-case, EN) | `reaction-compilation` |
| 2 | `display_name` | Человеческое имя (рус) | «Реакция-компиляция» |
| 3 | `description` | Одно предложение — суть | «Нарезка реакций персонажа на игровые моменты» |
| 4 | `keywords` | Слова-триггеры (RU + EN, через запятую) | "reaction", "реакция", "compilation" |
| 5 | `duration` | Целевая длительность (диапазон, сек) | 20–40s |
| 6 | `clip_count` | Клипы × длительность | 4 × 5s |
| 7 | `style` | Визуальный стиль | Pixar 3D / Photorealistic / Anime / Game-specific |
| 8 | `budget_max` | Максимальный бюджет ($) | $5.00 |

### Валидация Tier 1

- [ ] `slug` — kebab-case, не совпадает с: `serial-drama`, `gameplay-ai-avatar`, `reddit-story`, `news`, `standard`, `dance-battle`, `dual-style`, `object-character`
- [ ] `keywords` — НЕ пересекаются с keywords из `manager.md:137-146`. Проверь каждое слово.
- [ ] `budget_max` — в диапазоне $1–$20
- [ ] Рассчитай `budget_stop` = round(`budget_max` × 0.90, 2)

---

## Шаг 2. Дерево решений по моделям (Tier 2)

Задай **ключевой вопрос**: Есть ли речь/диалог в видео?

### Ветка A: НЕТ речи → Kling I2V

Спроси:
- `generate_audio`: true (Kling генерирует SFX) или false (тишина, anullsrc)?
- Нужны start + end frames для каждого клипа? (да = лучше continuity, +$0.04/клип)
- `negative_prompt` обязателен? (да если multi-char или dual-style)
- Количество персонажей в кадре? (1 / 2 / переменное)

**Результат:** Image: NB2 → Video: Kling I2V → Audio: SFX only или тишина

### Ветка B: ДА речь → выбор источника голоса

Спроси: КТО генерирует голос?

#### B1: Veo3 T2V (голос встроен)
- motion_prompt включает `and says: "[text]"`
- `generate_audio: true` всегда
- NB2 images нужны? (title card only или полные сцены)

**Результат:** Image: NB2 (опц.) → Video: Veo3 T2V → Audio: встроен

#### B2: ElevenLabs TTS + Kling Avatar v2 (lipsync)
Спроси:
- Ускорение Avatar после генерации? (1.3x для энергичных / 1.0x для драмы)
- Двухэтапное согласование? (TTS → показать пользователю → затем Avatar)
- Голос: фиксированный на персонажа в story bible ИЛИ выбирается на каждое видео?

**Результат:** Image: NB2 (avatar ref) → TTS: ElevenLabs → Video: Kling Avatar v2

#### B3: ElevenLabs TTS overlay на silent video
Спроси:
- TTS volume? (default 1.0)
- SFX volume от Kling? (default 0.4)
- `adelay` задержка TTS? (default 500ms)

**Результат:** Image: NB2 → Video: Kling I2V (SFX) → TTS: ElevenLabs overlay

#### B4: MIXED (I2V action + Avatar dialogue в одном видео)
Спроси:
- Какие `clip_type` существуют? (action / dialogue / reaction / etc.)
- Какой clip_type → какая модель?
- Баланс action/dialogue? (50/50 / 70/30 / etc.)
- `generate_audio` для I2V клипов: true или false?

**Результат:** Image: NB2 → Video: Kling I2V + Kling Avatar v2 → TTS: ElevenLabs (для Avatar)

### Ветка C: Нет генерации видео (только монтаж)

Спроси:
- Откуда клипы? (`games/{TAG}/gameplay/` / пользователь загружает / Supabase)
- Как выбираются? (shuf random / user-specified / по стортибоарду)
- Audio handling: strip (`-an`) / keep (volume=X)?
- TTS нужен? (narration overlay)

**Результат:** Video: pre-existing clips → TTS: ElevenLabs (опц.) → Assembly: FFmpeg

---

## Шаг 3. Условные вопросы (Tier 3–5)

Задавай ТОЛЬКО релевантные секции. Пропускай неприменимые.

### 3a. Image Generation (если NB2 используется)

| # | Вопрос | Defaults |
|---|--------|----------|
| 1 | Сколько character refs? | 1 |
| 2 | bg-reference на локацию обязателен? | нет |
| 3 | Chain strategy для scene refs? | `[anchor, prev-scene]` |
| 4 | Aspect ratio images | 608×1080 (9:16) |
| 5 | Особые требования к image_prompt? | нет |

### 3b. Episodic / Serial (если формат серийный)

| # | Вопрос | Варианты |
|---|--------|----------|
| 1 | Story bible нужен? | да / нет |
| 2 | Какие поля в story bible? | characters+status+relationships / themes+tones FIFO / custom |
| 3 | Anti-repetition: что ротировать? | phrases / hooks / cliffhangers / styles / emotions / custom |
| 4 | Loop management? | Minor/Major/Eternal / нет |
| 5 | State transitions после эпизода? | список полей для обновления |

### 3c. Pre-Production Phase (если есть)

| # | Вопрос | Варианты |
|---|--------|----------|
| 1 | Research phase? | web search → research.json / нет |
| 2 | Asset bank check? | Supabase game_assets / нет |
| 3 | State analysis? | story bible / нет |

### 3d. Субтитры

| # | Вопрос | Варианты |
|---|--------|----------|
| 1 | Нужны субтитры? | да / нет |
| 2 | Метод? | PIL PNG overlay / drawtext ffmpeg / нет |
| 3 | Шрифт/размер? | Arial Bold 38-48px / Montserrat Bold 42px / custom |
| 4 | Позиция? | нижняя треть / split boundary / custom y= |
| 5 | Word-highlight? | да (accent color) / нет (plain white) |

### 3e. CTA / TBC

| # | Вопрос | Варианты |
|---|--------|----------|
| 1 | CTA нужен? | clip в concat-list / overlay последние 2s / нет |
| 2 | TBC overlay? | да (за 2s до конца) / нет |
| 3 | Fade out? | да (1.0s) / нет |

### 3f. Музыка

| # | Вопрос | Defaults |
|---|--------|----------|
| 1 | Фоновая музыка? | опциональна |
| 2 | Volume level? | 0.15 |
| 3 | Mood category? | drama / energetic / comedic / lo-fi |
| 4 | Kling SFX + музыка одновременно? Volumes? | SFX 0.4, music 0.15 |

### 3g. Layout

| # | Вопрос | Default |
|---|--------|---------|
| 1 | Standard vertical 9:16 или split-screen? | vertical |
| 2 | (если split) Пропорции? | 60/40 |
| 3 | (если split) Что сверху / снизу? | — |
| 4 | (если split) Scale+crop правила? | `scale=1080:-2,crop=...` |
| 5 | (если split) Audio mixing volumes? | — |

### 3h. Game-Specific Overrides

| # | Вопрос | Default |
|---|--------|---------|
| 1 | Нужен `{format}_special.md` на игру? | нет |
| 2 | Какие поля в special? | style / characters / music mood / search keywords |

---

## Шаг 4. Расчёт бюджета

На основе собранных данных рассчитай типичную и максимальную стоимость.

### Цены моделей (из `budgets.md`)

| Модель | 5s | 10s |
|--------|----|----|
| NB2 image | $0.04 | $0.04 |
| Kling I2V (без аудио) | $0.35 | $0.70 |
| Kling I2V (с аудио) | $0.70 | $1.40 |
| Kling Avatar v2 | $0.28 | $0.56 |
| ElevenLabs TTS (фраза) | ~$0.05–0.10 | ~$0.07–0.15 |
| Veo3 T2V 8s (с аудио) | — | $3.20 |

### Формула

```
typical_cost = (clip_count × image_cost) + (clip_count × video_cost) + tts_cost
```

- [ ] `typical_cost` ≤ `budget_max`
- [ ] Если нет — предложи уменьшить clip_count или сменить модель

---

## Шаг 5. Генерация playbook-файла

Создай `rules/formats/{slug}.md` по канонической структуре:

```
# Формат "{display_name}" — {description}

{описание абзацем: жанр, целевая аудитория, ключевая фишка}

Этот файл — **playbook**: когда использовать, концепт, бюджет, брифы каждой роли.
Крафтовые правила — в `rules/roles/*.md`.

---

## Когда использовать

Ключевые слова: «{keyword1}», «{keyword2}», ...

---

## Концепт

- **Жанр:** {style description}
- **Стиль:** {visual style}
- **Длительность:** {duration range} ({clip_count} клипов × {clip_duration})
- **Бюджет:** до ${budget_max} на видео. Остановись если расход > ${budget_stop}.
- **Формат кадра:** {9:16 (608×1080) / split-screen layout}

### Модели

- **Image:** {NB2 / skip}
- **Video:** {Kling I2V / Kling Avatar v2 / Veo3 T2V / pre-existing clips}
- **Audio:** {generate_audio / ElevenLabs TTS / overlay / none}

---

## Бюджет (ориентиры)

| Компонент | 5s клип | 10s клип |
|---|---|---|
| {model rows from Step 4} | | |

| Вариант | Клипов | Стоимость |
|---|---|---|
| Базовый (рекомендуемый) | {N} × {dur} | ~${typical} |

---

## Структура {эпизода/видео}

| Фаза | Тайминг | Цель | Клипов |
|---|---|---|---|
| {beat rows} | | | |

{conditional sections: Story Bible, Loop Management, Anti-Repetition,
 Retention Strategy, Pre-Production, Gameplay Clips, Visual Layout,
 Prompting Rules, Voice Mapping, Locked/Variable Parameters}

---

## Брифы ролям

### Scenarist
{format-specific instructions}
- Общие правила сценария — `rules/roles/scenarist.md`

### Storyboarder
{format-specific instructions ИЛИ "SKIP — формат не использует NB2 image gen."}
- Общие правила — `rules/roles/storyboarder.md`

### Animator
{format-specific instructions ИЛИ "SKIP — формат не использует AI video gen."}
- Общие правила — `rules/roles/animator.md`

### Sound
{format-specific instructions}
- Общие правила — `rules/roles/sound.md`

### Editor
{format-specific instructions}
- Общие правила — `rules/roles/editor.md`

---

## Выходные файлы

{дерево директорий, output structure}

---

## Валидация перед публикацией

- [ ] {checklist items based on format specifics}

---

## Анти-паттерны

- ❌ {common mistakes for this format}
- ❌ `-shortest` в FFmpeg (ВСЕГДА используй `apad`)
- ❌ `voice_id` хеш вместо `voice` имени в ElevenLabs
- ❌ character ref напрямую как scene image
```

### Обязательные секции (всегда включать)

1. Когда использовать
2. Концепт
3. Бюджет
4. Структура
5. Брифы ролям (все 5 + SKIP где не нужны)
6. Выходные файлы
7. Валидация
8. Анти-паттерны

### Условные секции (включать при ответе «да»)

| Секция | Когда |
|--------|-------|
| Story Bible | формат серийный |
| Loop Management | формат серийный с петлями интриги |
| Anti-Repetition Check | формат серийный |
| Retention Strategy | формат серийный |
| Pre-Production / Research Phase | есть pre-research |
| Gameplay Clip Requirements | используются pre-existing clips |
| Visual Layout | split-screen |
| Prompting Rules | особая структура промптов (4-layer, markers) |
| Voice Mapping | несколько голосов / emotion-based выбор |
| Locked / Variable Parameters | параметры фиксированы на серию |
| CTA | есть call to action |

---

## Шаг 6. Обновление cross-cutting файлов

После создания playbook обнови 4 файла:

### 6a. `rules/main/budgets.md`

Добавь строку в таблицу «Бюджетные лимиты» (после последней строки):

```
| {Display Name} | **${budget_max}** | Расход > ${budget_stop} |
```

Если формат имеет варианты (single/series, I2V/T2V), добавь отдельные строки.

### 6b. `video-agent/CLAUDE.md`

Найди строки 36-37:
```
│   └── {serial-drama, gameplay-ai-avatar, news, standard,
│       reddit-story, dance-battle, object-character, dual-style}.md
```
Добавь `{slug}` в перечисление внутри `{}`.

### 6c. `rules/roles/manager.md`

Найди таблицу Format detection (строки 137-146). Добавь строку **ПЕРЕД** «Всё остальное | Standard»:

```
| "{keyword1}", "{keyword2}" | {Display Name} | `rules/formats/{slug}.md` |
```

### 6d. `video-agent/STRUCTURE.md`

Найди listing format files (строки 119-126). Добавь:

```
│       ├── {slug}.md           # {display_name}
```

---

## Шаг 7. Auxiliary файлы (если нужны)

### Story Bible Template (если формат серийный)

Создай `games/{GAME_TAG}/{slug}_story_bible.json`:

```json
{
  "series_id": "",
  "game_tag": "",
  "title": "",
  "style_tags": "",
  "created_at": "{TODAY}",
  "last_episode": 0,
  "characters": [],
  "active_loops": [],
  "closed_loops": [],
  "world_state": {},
  "anti_repetition": {},
  "episode_summaries": []
}
```

Адаптируй поля под ответы из шага 3b.

### Game-Specific Special Template (если нужен)

Создай `games/{GAME_TAG}/{slug}_special.md`:

```markdown
# {Display Name} — настройки для {Game Name}

{поля из шага 3h}
```

---

## Шаг 8. Финальная валидация

Покажи пользователю чеклист:

- [ ] `rules/formats/{slug}.md` создан, содержит все обязательные секции
- [ ] `budgets.md` содержит строку с новым форматом
- [ ] `CLAUDE.md` содержит slug в списке форматов
- [ ] `manager.md` содержит keywords в таблице Format detection
- [ ] `STRUCTURE.md` содержит файл в listing
- [ ] Keywords НЕ пересекаются с существующими форматами
- [ ] Бюджет реалистичен: `typical_cost` ≤ `budget_max`
- [ ] Все role briefs заполнены или помечены SKIP с причиной
- [ ] Условные секции включены/исключены корректно
- [ ] Auxiliary файлы созданы (если нужны)

---

## Defaults (авто-заполнение если пользователь не указал)

| Поле | Default | Когда менять |
|------|---------|-------------|
| Frame format | 9:16 (1080×1920) | Split-screen layout |
| Default clip duration | 5s | Формат требует иное |
| `generate_audio` I2V | true | Если отдельный TTS overlay (false) |
| Music volume | 0.15 | По формату (0.05–0.25) |
| Subtitle method | нет | Если есть речь |
| CTA | нет | Если указано |
| TBC | нет | Только serial |
| fps | 30 | Всегда |
| Codec | libx264, preset slow, crf 20 | Всегда |
| Audio | AAC 128k stereo | Всегда |
| `budget_stop` | budget_max × 0.90 | — |
| `-shortest` | **НИКОГДА** | Универсальный анти-паттерн |

---

## Анти-паттерны скилла

- ❌ Создавать формат без опроса пользователя (не угадывай — спрашивай)
- ❌ Копировать существующий формат и менять имя (каждый формат уникален)
- ❌ Пропускать обновление cross-cutting файлов (playbook без detection keywords = мёртвый формат)
- ❌ Keywords, пересекающиеся с существующими форматами (конфликт детекции)
- ❌ Бюджет без расчёта по ценам моделей (нереалистичный лимит)
- ❌ Пустые role briefs без SKIP-пометки (агент не поймёт — делать или нет)
