# Формат "Object Character" — антропоморфные объекты

Бытовой предмет с выраженной эмоцией произносит 10-секундный монолог от первого лица. Вилка с глазами, уставшая кружка, злой тапок.

Этот файл — **playbook**. Крафтовые правила (NB2, Kling I2V, TTS, ffmpeg) — в `rules/roles/*.md`.

---

## Когда использовать

Ключевые слова: «object character», «антропоморф», «talking object», бытовой объект как персонаж.

---

## Концепт

- **1 объект → 1 клип × 10s** (single) или **5 роликов** (series)
- **Модель:** строго **Kling 2.6 Pro I2V** (`generate_audio: true` для SFX — скрип, стук, амбиент)
- **Речь:** через **ElevenLabs TTS** overlay (Kling не генерирует голос), `character_speech: null` в storyboard
- **Бюджет:** $1.50 (single) / $7.50 (series)
- **НЕ** Veo3 T2V

---

## Structure

**1 клип, 10s, Kling I2V.** Объект произносит монолог ≤25 слов.

Антропоморфизм усиливает личность, но **не убивает идентичность объекта**. Объект должен остаться узнаваемым:
- Глаза + брови
- Рот (с выражением)
- Конечности (предмет-подобные выросты, не человеческие руки)
- Поза / наклон
- Взаимодействие с окружением

---

## Логика интерпретации ввода

| Дано | Действие |
|---|---|
| Только объект | Выведи эмоцию, сцену, конфликт |
| Объект + эмоция | Выведи сильнейшее окружение для эмоции |
| Объект + сцена | Выведи читаемую эмоцию |
| Объект + эмоция + сцена | Сохрани всё, усиль кинематографичность |
| Несколько объектов | Лид + остальные related (series) |

### Предпочтительные эмоции
- Раздражённая правда, усталый реализм, тревожное предупреждение, отвращение, гордость, паника, сарказм, защитная фрустрация, изнурённая честность

**Избегай:** позитивная мотивация, абстрактный оптимизм, нейтральное повествование.

---

## Скрипт (монолог)

10s монолог от первого лица. Правила:
- Говори как сам объект
- Естественно произносимый текст
- Содержит: напряжение / фрустрацию / предупреждение / жалобу / инсайт / сарказм
- Эмоционально прямой, без филлеров
- **НЕТ** обращения к аудитории («you guys», «подписывайтесь»)
- **НЕТ** CTA-фраз, мотивационного тона
- ≤25 слов (на 10s)

Пример: `"Every single dinner party — spoons in the spotlight, knives get respect, and me? I'm the one they drop on the floor."`

---

## Storyboard extensions

```json
{
  "format": "object-character",
  "approach": 2,
  "visual_identity": {
    "character_description": "anthropomorphic silver dinner fork with expressive cartoon eyes, thick angry eyebrows, wide open mouth mid-rant, two small arm-like prongs gesturing wildly, slightly bent posture, metallic silver surface with scratches",
    "environment_description": "inside a dark kitchen drawer, cutlery silhouettes, warm light from above, wooden interior with crumbs",
    "style_tags": "stylized animated 3D render, Pixar-quality character design, expressive anthropomorphic object",
    "lighting": "warm volumetric light from above, dramatic rim light"
  },
  "tts": {
    "text": "[≤25 words monologue]",
    "voice": "Daniel",
    "stability": 0.20,
    "style": 0.8
  },
  "scenes": [
    {"index": 1, "duration_sec": 10, "character_speech": null, "motion_prompt": "[без текста речи]", ...}
  ]
}
```

### character_description — 8+ деталей (обязательно)
1. Материал/текстура (metallic, ceramic, rubber, wood)
2. Глаза (wide cartoon, squinting suspicious)
3. Брови (thick angry, raised worried)
4. Рот (wide open mid-rant, tight-lipped grimace)
5. Конечности (arm-like handles, stubby legs)
6. Поза (leaning aggressively, slouched defeated)
7. Износ/детали (scratches, stains, chips, dust)
8. Уникальная деталь (four sharp tines, chipped rim)

### Voice mapping (ElevenLabs через fal.ai)

| Эмоция | Voice | stability | style |
|---|---|---|---|
| Раздражение, сарказм | Daniel / George | 0.20 | 0.8 |
| Паника, тревога | Charlie | 0.15 | 0.9 |
| Усталость, грусть | George | 0.35 | 0.6 |
| Гордость, самоуверенность | Daniel | 0.10 | 0.8 |
| Женский (уверенный) | Charlotte | 0.25 | 0.7 |

---

## Series (5 роликов)

Если `format: "series"` — main + 4 related объекта из той же тематической вселенной (кухня / утренняя рутина / канцелярия / выгорание / беспорядок).

Каждый related character обязан иметь:
- Уникальный объект (не повторять main)
- Уникальную эмоцию или вариацию
- Уникальный конфликт, скрипт (не шаблон с подстановками)
- Уникальный голос (чередуй male/female)

Каждый эпизод → отдельный storyboard.json → отдельный final.mp4.

---

## Брифы ролям

### Scenarist
- 1 объект = 1 клип × 10s; `character_speech: null` (Kling не генерит голос)
- Скрипт в секции `tts` (text, voice, stability, style), ≤25 слов
- `motion_prompt` содержит ≥2 действия, **БЕЗ текста речи**
- 8+ визуальных деталей в `character_description`
- Environment привязан к реальному использованию объекта
- Общие правила — `rules/roles/scenarist.md`

### Storyboarder
- Anchor ref объекта (NB2, 9:16, neutral dark bg); scene image с `image_urls: [anchor]`
- Для сцены с липсинком — рот приоткрыт / лёгкая улыбка (зубы видны для качества липсинка)
- Общие правила — `rules/roles/storyboarder.md`

### Animator
- **Kling 2.6 Pro I2V**, `duration: "10"`, `generate_audio: true` (SFX), `aspect_ratio: "9:16"`
- `prompt` = motion_prompt БЕЗ текста речи
- **НЕ** Veo3 T2V
- Общие правила — `rules/roles/animator.md`

### Sound
- **ElevenLabs TTS через fal.ai** (`fal-ai/elevenlabs/tts/eleven-v3`); `voice` имя, не хэш
- Voice/stability/style — из `tts` секции storyboard (см. Voice mapping выше)
- Субтитры не обязательны (10s монолог разборчив)
- Общие правила — `rules/roles/sound.md`

### Editor
- Scale 1080×1920, 30fps
- Mix: Kling SFX `volume=0.4`, TTS voice `volume=1.0` + `adelay=500|500` (0.5s задержка)
- Trim: `-t CLIP_DUR` где `CLIP_DUR = 0.5 + TTS_DUR + 1.0s`
- **НИКОГДА `-shortest`** (обрезает видео до длины аудио)
- Общие правила — `rules/roles/editor.md`

---

## Выходные файлы

```
output/YYYY-MM-DD/{GAME_TAG}/object-character/
├── storyboard.json
├── scenes/
│   ├── refs/character-ref.png
│   └── scene-1/{scene-1.png, scene-1.mp4, scene-1-scaled.mp4}
├── voiceover.wav
└── final.mp4
```

Series: каждый эпизод в отдельной OUTPUT_DIR.

---

## Валидация

- [ ] Объект узнаваем как предмет (не абстрактное существо)
- [ ] `character_description` ≥8 визуальных деталей (глаза/брови/рот/конечности/поза)
- [ ] Скрипт от первого лица, ≤25 слов, без CTA / обращения к зрителю / мотивационного тона
- [ ] Содержит конфликт/напряжение/эмоцию (не нейтральный)
- [ ] `character_speech: null`; текст речи в секции `tts`
- [ ] `motion_prompt` НЕ содержит текст речи; содержит ≥2 действия
- [ ] `generate_audio: true` в Kling вызове
- [ ] Для series: 5 уникальных объектов (эмоция/конфликт/скрипт/голос); не шаблоны с подстановками
- [ ] Бюджет ≤$2 (single) / ≤$10 (series)

---

## Анти-паттерны

- ❌ Абстрактный объект без идентичности («cute blob with face»)
- ❌ Объект = человек с текстурой предмета
- ❌ Скрипт обращается к зрителю («Hey guys!», «Subscribe!»)
- ❌ Мотивационный тон
- ❌ Текст речи в `motion_prompt` (Kling не генерит голос)
- ❌ `character_speech` ≠ null
- ❌ Одинаковые шаблоны скриптов в series
- ❌ Veo3 T2V для этого формата
- ❌ `-shortest` в ffmpeg
