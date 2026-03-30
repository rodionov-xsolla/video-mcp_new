# Формат: Standard (I2V / T2V)

Стандартный формат видео. Используется по умолчанию, если идея не соответствует специальным форматам (news, serial-drama, object-character, dual-style).

---

## Детекция формата

Формат "standard" активируется если IDEA НЕ содержит ключевых слов других форматов:
- Не "news/новости/patch recap" (→ news)
- Не "serial/episode/сериал" (→ serial-drama)
- Не "object character/talking object" (→ object-character)
- Не "dual-style/game vs reality" (→ dual-style)

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

## Consistency

Стандартный формат использует все три слоя консистентности:
- **Layer 1:** Character Reference (anchor image) — см. workflow.md Phase 2
- **Layer 2:** Chain Reference (предыдущая сцена) — см. workflow.md Phase 3
- **Layer 3:** Prompt Consistency — см. storyboard.md секция 8
