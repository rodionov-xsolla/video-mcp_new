# Формат "Standard" — I2V / T2V

Стандартный формат видео. Используется по умолчанию, если идея не соответствует специальным форматам (news, serial-drama, object-character, dual-style, gameplay-ai-avatar, dance-battle).

---

## Когда использовать

Формат "standard" активируется если IDEA НЕ содержит ключевых слов других форматов:
- Не "news/новости/patch recap" (→ news)
- Не "serial/episode/сериал" (→ serial-drama)
- Не "object character/talking object" (→ object-character)
- Не "dual-style/game vs reality" (→ dual-style)
- Не "gameplay ai avatar/offerwall/offer" (→ gameplay-ai-avatar)
- Не "dance battle/танцевальный батл" (→ dance-battle)

---

## Обзор формата

- **Концепт:** универсальный формат для экшена, стендапов, гайдов, рейтингов, трейлеров
- **Модель (без речи):** Kling 2.6 Pro I2V (`generate_audio: true`)
- **Модель (с речью):** Veo3 T2V (`generate_audio: true`)
- **Длительность:** 15-30 сек (3 клипа × 5-10s)
- **Бюджет:** $5 (I2V) / $10 (T2V)

---

## ФАЗА 0: ИНИЦИАЛИЗАЦИЯ

1. Загрузить `tools/fal-ai.md` — API reference
2. Загрузить `rules/main/storyboard.md` — правила промптинга + консистентность
3. Загрузить `rules/main/fallback.md` — обработка ошибок
4. Загрузить `games/{GAME_TAG}/{GAME_TAG}.md` — конфиг игры
5. *(опционально)* Загрузить `music/tracks.json` — фоновая музыка
6. Определить наличие речи в идее → выбор модели (Kling I2V или Veo3 T2V)

---

## Подходы

| Тип контента | Подход | Модели |
|-------------|--------|--------|
| Динамичный контент, экшен, стендап, комбо | **Approach 2** (I2V/T2V) | Image → Kling 2.6 Pro I2V (без речи) / Veo3 T2V (с речью) |
| Кинематограф, трейлеры, атмосферные видео | **Approach 3** (T2V) | Veo3 T2V |
| Списки, рейтинги, советы, гайды, "Top N" | **Approach 2** (I2V) | Image → Kling 2.6 Pro I2V |

По умолчанию: Approach 2. Если пользователь указал подход — используй его.

---

## Выбор модели

Модель определяется наличием речи:
- `character_speech` ≠ null → **Veo3 T2V** (генерирует голос + липсинк)
- `character_speech` = null → **Kling 2.6 Pro I2V** (звуковые эффекты, без голоса)

---

## Клипы и длительности

| Подход | Клипов | Длительность каждого | Итого |
|--------|--------|---------------------|-------|
| Approach 2 (I2V/T2V) | **3** (по умолч.) | **5–10 сек** | **15–30 сек** |
| Approach 3 (T2V) | 2–3 | 5–8 сек | 16-24 сек |

**I2V правило:** По умолчанию 3 клипа. 4 клипа — ТОЛЬКО если каждый содержит достаточно действия и уникального движения.

---

## Анимация

### Approach 2 — Kling 2.6 Pro (без речи) / Veo3 T2V (с речью)

##### Без речи — Kling 2.6 Pro I2V

Для каждой сцены K (где `character_speech` = null):
- `start_image_url` = scene-K.png URL
- `prompt` = `motion_prompt` из storyboard (НЕ включай `character_speech`)
- `duration` = `"5"` или `"10"` (согласно storyboard)
- `generate_audio` = `true` (Kling генерирует звуковые эффекты)
- `aspect_ratio` = `"9:16"`
- Без `end_image_url`

##### С речью — Veo3 T2V

Для каждой сцены K (где `character_speech` ≠ null):
- `prompt` = `image_prompt` + `motion_prompt` объединённые (ОБЯЗАТЕЛЬНО включи текст `character_speech`)
- `generate_audio` = `true`
- `duration` = `"8s"`
- `aspect_ratio` = `"9:16"`

### Approach 3 — T2V

Используй Veo3 T2V с промптом из storyboard.
`prompt` = полный `image_prompt` + `motion_prompt` объединённые.

---

## Бюджет

| Подход | Максимум |
|--------|----------|
| Approach 2 (I2V) | **$5.00** |
| Approach 3 (T2V) | **$10.00** |

---

## Валидация

- [ ] `format: "standard"` присутствует в storyboard
- [ ] Подход (approach) соответствует типу контента
- [ ] `character_speech` ≠ null → модель Veo3 T2V; `character_speech` = null → Kling I2V
- [ ] Одна модель на все сцены (не миксовать Kling + Veo3)
- [ ] `camera_angle` разный для каждого соседнего клипа
- [ ] `motion_prompt` содержит минимум 2 действия
- [ ] `image_prompt` содержит "vertical composition, 9:16 aspect ratio"
- [ ] Если речь → текст включён в `motion_prompt` (Veo3)
- [ ] Если без речи → `motion_prompt` НЕ содержит текст речи
- [ ] Бюджет не превышен ($5 I2V / $10 T2V)
- [ ] Character Reference → chain reference для консистентности (см. `rules/main/storyboard.md`)

---

## Анти-паттерны

**НЕ делай:**
- Не миксуй Kling I2V и Veo3 T2V в одном видео — разная пластика и цветовая температура
- Не передавай `character_speech` в Kling I2V — модель не генерирует голос
- Не делай больше 4 клипов без обоснования — каждый клип должен нести уникальное действие
- Не используй абстрактные термины в промптах для Kling: "nice background", "good lighting", "dynamic pose"
- Не используй `end_image_url` — только hard cut между разными планами камеры
- Не используй `-shortest` в FFmpeg — обрезает видео до длины аудио

---

## Выходные файлы

```
OUTPUT_DIR/
├── storyboard.json
├── scenes/
│   ├── refs/
│   │   └── character-ref.png
│   ├── scene-1/
│   │   ├── scene-1.png
│   │   ├── scene-1.mp4
│   │   └── scene-1-scaled.mp4
│   ├── scene-2/
│   │   └── ...
│   └── scene-3/
│       └── ...
└── final.mp4
```

---

## Consistency

Стандартный формат использует все три слоя консистентности:
- **Layer 1:** Character Reference (anchor image) — см. `rules/main/storyboard.md`
- **Layer 2:** Chain Reference (предыдущая сцена) — см. `rules/main/storyboard.md`
- **Layer 3:** Prompt Consistency — единый стиль через все клипы
