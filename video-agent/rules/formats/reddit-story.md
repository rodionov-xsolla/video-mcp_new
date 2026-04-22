# Формат "Reddit Story" — монолог поверх геймплея

Монолог от первого лица поверх рандомного геймплея с word-highlight субтитрами. Личная история: funny, touching, drama, shock, rage. Офферволл вплетён в сюжет как действие героя.

Этот файл — **playbook**. Крафтовые правила (TTS, субтитры, ffmpeg) — в `rules/roles/*.md`.

---

## Когда использовать

Ключевые слова: «reddit story», «storytime», «история игрока», «personal story», «narrated gameplay».

Параметры запуска: `game_tag`, `topic` (опционально), `language` (`EN` / `RU` / `PT-BR`).

---

## Концепт

- **Геймплей:** готовые клипы из `games/{GAME_TAG}/gameplay/`, рандомный шафл, **не привязан к тексту** — чистый фоновый визуал
- **TTS:** ElevenLabs через fal.ai (экспрессивно, `stability=0.3`, `style=0.7`, 29 языков)
- **Субтитры:** word-highlight drawtext, обязательны
- **Длительность:** до 60s (~150–170 слов)
- **AI-генерация видео отсутствует** — только TTS + ffmpeg сборка
- **Бюджет:** $2 максимум (типично $0.30–0.50)

---

## Офферволл-интеграция (нативная)

Офферволл = ЧАСТЬ СЮЖЕТА, не реклама. Герой использует его как инструмент.

### Структура нарратива (фиксированная)

```
HEADLINE → HOOK → ПРОБЛЕМА → ОФФЕРВОЛЛ (решение) → ТВИСТ
```

### Правила
- **НЕ начинай с покупки.** Сначала цепляющая история, потом офферволл как естественное решение.
- Офферволл упоминается КАК ДЕЙСТВИЕ ГЕРОЯ: `"I grinded offerwall tasks"`, `"выполнял задания"`.
- **НЕ** говори «купите», «скачайте», не называй сервис по имени.
- CTA = **overlay** `"Link in bio"` в последние 2s. Никогда не озвучивается голосом.
- **ТВИСТ обязателен** — неожиданный поворот.

### Примеры нативной интеграции
- **Roblox:** сестра мечтала о скине → гриндил задания → подарил → она расплакалась
- **Oxide:** рейдер уничтожил базу → неделю выполнял задания → собрал gear → отомстил solo
- **MLBB:** проигрывал → выполнил пару заданий, взял нового героя → 10 игр подряд выиграл

---

## Structure

| Элемент | Описание | Длит. |
|---|---|---|
| **headline** | Кликбейт-саммари в одном предложении | 1–2s |
| **hook** | Завязка истории (конкретный цепляющий факт) | 3–5s |
| **проблема** | Конфликт, который требует решения | 10–15s |
| **офферволл** | Действие героя как шаг к цели | 5–10s |
| **твист** | Неожиданная кульминация | 10–15s |
| **CTA overlay** | `Link in bio` (только текст) | 2s |

Общая длительность TTS ≤ 58s → финальный MP4 = TTS + 2s CTA ≈ 60s.

---

## Storyboard schema

```json
{
  "format": "reddit-story",
  "game_tag": "Roblox",
  "language": "EN",
  "headline": "I spent 200 hours building and a 9 year old destroyed it all",
  "narrative_text": "So my little brother has been playing Roblox every day... [full text]",
  "tone": "touching",
  "hook": "So my little brother has been playing Roblox every single day.",
  "offerwall_angle": "grinded offerwall tasks to buy premium building tools for brother",
  "tts": {"voice": "Daniel", "language_code": "en", "stability": 0.3, "style": 0.7},
  "total_duration_sec": 55,
  "cta_overlay": "Link in bio"
}
```

Поле `voice` = **имя**, не хэш voice_id (см. `rules/roles/sound.md`).

---

## Anti-Repetition Check

Перед сценарием сверь с `games/{GAME_TAG}/reddit-story_bible.json`:
- **Темы:** не дублируй темы из последних 10 историй
- **Тон:** не повторяй один и тот же 3 раза подряд
- **Хуки:** не используй похожий headline/hook
- **Офферволл-угол:** разнообразь — не всегда «гриндил задания»

### Story bible структура
```json
{
  "game_tag": "Roblox",
  "total_stories": 0,
  "stories": [{"id": 1, "date": "...", "tone": "...", "theme": "...", "headline": "...", "offerwall_angle": "...", "output_dir": "..."}],
  "anti_repetition": {
    "recent_themes": ["..."],
    "recent_tones": ["..."],
    "recent_hooks": ["..."],
    "banned_combos": []
  }
}
```

Обновляется после каждого ролика (Manager, Фаза 6). Все списки FIFO, хранить последние 10.

---

## Брифы ролям

### Scenarist
- Headline — кликбейтный, провокационный, 1 предложение; произносится голосом + показывается субтитрами
- `narrative_text` от первого лица, разговорный стиль, предложения ≤15 слов
- Структура HEADLINE→HOOK→ПРОБЛЕМА→ОФФЕРВОЛЛ→ТВИСТ
- Конкретика (имена, числа, детали) — не «cool stuff» → «legendary dragon skin»
- Нет корпоративного тона, имён сервисов, CTA голосом
- Anti-repetition check по `reddit-story_bible.json`
- Общие правила — `rules/roles/scenarist.md`

### Storyboarder
- **SKIP** — нет NB2 генерации, используется готовый геймплей
- Manager проверяет наличие ≥1 `.mp4` в `games/{GAME_TAG}/gameplay/` в Фазе 0

### Animator
- **SKIP** — нет Kling/Veo3, только рандомный геймплей

### Sound
- ElevenLabs через fal.ai (`fal-ai/elevenlabs/tts/eleven-v3`); `voice` имя (не хэш)
- `stability=0.3`, `style=0.7` для storytelling-экспрессии
- Озвучиваем `headline + narrative_text` как единый текст → `tts-output.mp3`
- **SRT файл не генерируем** — тайминги считает Editor из TTS_DUR
- Музыка опционально, `volume=0.05` (тише обычного — нарратив должен быть чётким)
- Общие правила — `rules/roles/sound.md`

### Editor
- Gameplay: `shuf` клипов → concat → trim to `TTS_DUR + 2s`, `-an` (убрать оригинальный звук)
- Scale 1080×1920, 30fps; TTS overlay через `apad` (**НИКОГДА `-shortest`**)
- **Word-highlight субтитры** (drawtext, 3–5 слов на сегмент, равномерный тайминг по TTS_DUR, акцентный цвет из game config) — Editor строит фильтры сам; для 30+ сегментов `-filter_complex_script`. Детали — `rules/roles/editor.md` секция "reddit-story — drawtext word-highlight"
- CTA overlay последние 2s (`drawtext`, `enable='between(t,CTA_START,TOTAL_DUR)'`)
- Общие правила — `rules/roles/editor.md`

---

## Выходные файлы

```
output/YYYY-MM-DD/{GAME_TAG}/reddit-story/
├── storyboard.json
├── tts-output.mp3
├── gameplay-trimmed.mp4
├── assembled.mp4
├── subtitled.mp4
└── final.mp4
```

Плюс обновление `games/{GAME_TAG}/reddit-story_bible.json`.

---

## Валидация

- [ ] `games/{GAME_TAG}/gameplay/` содержит ≥1 `.mp4`
- [ ] `headline` — кликбейт, 1 предложение
- [ ] `narrative_text` 150–170 слов; все предложения ≤15 слов; от первого лица
- [ ] Офферволл вплетён как действие героя; нет прямой рекламы / имени сервиса
- [ ] Твист присутствует
- [ ] Anti-repetition: тема/тон/хук не дублируют последние 10 (checked)
- [ ] `voice` = имя (Daniel/George/...), не хэш
- [ ] CTA — overlay только, не голосом
- [ ] Общая длительность ≤60s; бюджет ≤$2
- [ ] `reddit-story_bible.json` обновлён после ролика

---

## Анти-паттерны

- ❌ Kokoro TTS или direct ElevenLabs API — только `fal-ai/elevenlabs/tts/eleven-v3`
- ❌ Привязка геймплея к тексту — должно быть рандомно
- ❌ Начало с покупки/офферволла — сначала цепляющая история
- ❌ `-shortest` в ffmpeg — используй `apad + -t`
- ❌ Повтор тем/хуков из последних 10 (bible)
- ❌ Предложения >15 слов
- ❌ Корпоративный тон («мы рекомендуем», «скачайте»)
- ❌ CTA голосом / название сервиса в тексте
