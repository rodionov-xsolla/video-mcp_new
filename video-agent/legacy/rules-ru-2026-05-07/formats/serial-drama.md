# Формат "Serial Drama" — Сериальные микро-драмы

Сериальные микро-драмы с brainrot эстетикой и бесконечным сюжетом. Каждый эпизод — 25–40 секунд, 3–5 клипов, cliffhanger в конце.

Этот файл — **playbook**: когда использовать, концепт, бюджет, состояние сериала (story bible), брифы каждой роли. Крафтовые правила — в `rules/roles/*.md`.

---

## Когда использовать

Ключевые слова: «serial», «episode», «series», «ep1», «ep2», «сериал», либо указан `series_id` существующего сериала.

---

## Концепт

- **Жанр:** бесконечные микро-драмы с brainrot эстетикой, cliffhanger-ы, петли сюжета
- **Стиль:** Pixar/Disney 3D — стилизованные 3D персонажи, пластиковые текстуры, экспрессивные лица, мягкое ambient освещение, cinematic depth of field
- **Длительность:** 25–40 сек (3–5 клипов × 5–10s)
- **Бюджет:** до $10 на эпизод. Остановись если расход > $9.00.
- **Формат кадра:** 9:16 (608×1080) для всех сцен. Квадрат запрещён.

### Состав клипов (балансы)

- **ACTION/DIALOGUE ~ 50/50.** Все-dialogue эпизод = монотонный и дорогой; все-action = нет сюжета.
- **I2V (Kling 2.6 Pro)** — action/reaction клипы (без звука)
- **Avatar (Kling Avatar v2)** — dialogue клипы с lipsync (TTS от ElevenLabs)
- **TTS overlay с aecho** — только для сцен «за стеклом/дверью» (персонаж виден через преграду, лицо не видно)

---

## Бюджет (ориентиры)

| Компонент | 5s клип | 10s клип |
|---|---|---|
| Image (NB2) | $0.04 | $0.04 |
| Kling I2V (generate_audio=false, $0.07/s) | $0.35 | $0.70 |
| ElevenLabs TTS (реплика 5–15s) | ~$0.05 | ~$0.07 |
| Kling Avatar v2 (dialogue) | ~$0.28 | ~$0.56 |
| **I2V action клип** | **~$0.39** | **~$0.74** |
| **Avatar dialogue клип** | **~$0.32** | **~$0.63** |

| Вариант | Клипов | Стоимость |
|---|---|---|
| Базовый (рекомендуемый) | 5 × 5s | ~$2.00–3.00 |
| Расширенный | 6–7 × 5s | ~$2.50–4.00 |
| Исключение (неделимый монолог) | 4×5s + 1×10s | ~$2.80–3.80 |

⚠️ **Динамика > экономия.** 2×5s почти всегда лучше 1×10s. Смена ракурса / реакция собеседника важнее $0.04 экономии.

---

## Структура эпизода (нарратив)

| Фаза | Тайминг | Цель | Клипов |
|---|---|---|---|
| **HOOK** | 0–5s | Визуальный парадокс + хук-фраза. Остановка скролла | 1 clip (5s, ACTION/I2V) |
| **CLIMAX** | 5–30s | Диалог, конфронтация, нарастающий темп | 2–3 clips (5–10s каждый) |
| **CLIFFHANGER** | последние 5s | Обрыв на пике. Шок, reveal, mid-sentence stop | 1 clip (5s, ACTION/I2V) |

### Что работает (TikTok/Reels аудитория)

- **Конфликт с первой секунды.** Не «жил-был», а «Ворф ведёт Чехова к шлюзу». Зритель попадает в середину действия.
- **Конкретные визуальные ставки.** Кто-то умрёт, будет предан, потеряет всё. Не абстрактные эмоции.
- **Короткие панчевые реплики.** 2–5s на фразу. Не монологи.
- **Каждая сцена двигает сюжет.** Ноль филлера.
- **Драма через действия, не слова.** «Ворф опускает глаза» > монолог на 10 секунд.

### Что НЕ работает

- ❌ Философские/сентиментальные сюжеты («Что Спок никогда не скажет»)
- ❌ Театральные речи, длинные монологи
- ❌ Медленный buildup без конфликта в первых 5 секундах
- ❌ Все клипы — dialogue (монотонно, дорого, скучно)
- ❌ Два подряд Avatar-клипа разных персонажей на ОДНОМ фоне в анфас (копипаст)

### Brainrot лексика

Уместна в диалогах: `rizz`, `sigma`, `cooked`, `negative aura`, `bro`, `no cap`, `NPC behavior`, `delulu`. Дозированно, не в каждой реплике. Не в нарраторе.

### Длительность — 5s по умолчанию

- Любая реплика ≤15 слов → **5s**
- Любое действие/реакция → **5s**
- 10s dialogue клип = **почти всегда ошибка** (статичная голова 10 секунд = смерть динамики). Разбей на 2×5s с разными ракурсами.
- 10s клип требует `duration_reason` в storyboard.json.

---

## Story Bible — персистентное состояние сериала

Файл `games/{GAME_TAG}/serial-drama_story_bible.json` хранит состояние вселенной между эпизодами. **Обязателен** для serial-drama.

### Структура

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
      "character_description": "Roblox-style blocky humanoid, bright yellow smooth plastic skin, simple blue torso shirt, bright green pants, round head with wide innocent eyes, small curved mouth, matte plastic texture",
      "voice": "Charlie",
      "status": "just joined the server, secretly rich",
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

### State Analysis (перед генерацией)

1. Загрузи story bible из `games/{GAME_TAG}/serial-drama_story_bible.json`
2. Проанализируй: кто в каком статусе, какие петли активны, какой level ауры
3. Выполни Anti-Repetition Check (см. ниже)
4. Определи что произойдёт в этом эпизоде (Loop Management)

### State Transition (после генерации, Manager обновляет)

1. Обнови `characters[].status` и `aura_points`
2. Обнови `relationships` если изменились
3. Обнови `active_loops` / `closed_loops`
4. Добавь `episode_summaries[]` с кратким содержанием + cliffhanger
5. Обнови `anti_repetition` — добавь использованные фразы, хуки, клиффхэнгеры
6. Обнови `world_state`
7. Инкрементируй `last_episode`

---

## Loop Management (Recursive Continuity)

Петли интриги — нерешённые конфликты, которые удерживают зрителя.

| Тип | Длительность | Пример |
|---|---|---|
| **Minor** | 2–5 эпизодов | «Кто украл предмет?» |
| **Major** | 10–20 эпизодов | «Скрытая личность главного героя» |
| **Eternal** | Не закрывается | «Война серверов» |

### Правила

- Каждые 5 эпизодов **закрой 1 малую петлю**, но **открой 2 новых** более масштабных
- Минимум 2 активных петли всегда
- **No Finality:** любая победа — начало новой беды; любое раскрытие — порождает новую тайну
- Сериал НИКОГДА не заканчивается

---

## Retention Strategy (обязательно в storyboard)

Каждый эпизод содержит в storyboard:

```json
{
  "retention_strategy": "Reveal that the noob has a secret golden item triggers curiosity — viewer MUST see next episode to learn what it does",
  "active_loops": ["noob's secret identity", "slender's revenge plan"],
  "cliffhanger": "Noob opens inventory and golden light illuminates his face — cut to black"
}
```

---

## Anti-Repetition Check

Перед написанием storyboard проверь `anti_repetition` в story bible:

1. **Фразы:** не повторяй из последних 8 эпизодов
2. **Хуки:** не используй тот же тип (если прошлый «question hook» — используй «contrast» или «statement»)
3. **Клиффхэнгеры:** не повторяй приём (mid-sentence / reveal / unexpected entrance)
4. **Метафоры/сравнения:** разнообразие обязательно

---

## Брифы ролям

### Scenarist

- Структура эпизода: HOOK → CLIMAX (2–3 клипа) → CLIFFHANGER
- **5s дефолт**, 10s dialogue = почти всегда ошибка (разбей на 2×5s)
- Balance ACTION/DIALOGUE ~ 50/50; минимум 2 разных персонажа говорят за эпизод
- Читай story bible: характеры, голоса (поле `voice`), активные петли, anti-repetition
- **`retention_strategy` обязателен** в storyboard — почему клиффхэнгер тянет следующий эпизод
- Brainrot лексика дозированно, только в диалогах
- camera_angle отличается для каждого соседнего клипа
- **НЕТ title cards / brainrot-тегов / имён персонажей оверлеями** — только субтитры диалогов + TBC
- Общие правила сценария — `rules/roles/scenarist.md`

### Storyboarder

- Стиль Pixar/Disney 3D (`style_tags` из story bible)
- Все кадры 9:16 (608×1080) — квадрат запрещён
- **bg-reference на каждую локацию** обязателен — без него фон дрейфует между клипами (см. `storyboarder.md` секция 2)
- Character refs: персонажи из story bible, рот с зубами для lipsync клипов
- I2V клипы требуют start + end frame (оба с одним bg-ref в `image_urls`)
- Каждый клип = отдельный scene PNG (не ref напрямую)
- Визуальная валидация обязательна
- Общие правила — `rules/roles/storyboarder.md`

### Animator

- I2V клипы через Kling 2.6 Pro (`generate_audio: false`, всегда) — только микро-движения
- Avatar клипы через Kling Avatar v2 Standard (с TTS audio_url)
- Motion prompt = технический (позиции, камера, физические действия), без имён/настроений
- Один model на весь эпизод — не смешивай Kling I2V v2.6 Pro с Avatar v2
- Start ≈ end для I2V; persistent character в обоих фреймах
- **НЕ ускорять Avatar** в serial-drama (1.3x — только для gameplay-ai-avatar)
- Общие правила — `rules/roles/animator.md`

### Sound

- TTS через fal.ai ElevenLabs — `voice` (имя строкой) из story bible, `language_code` ISO 639-1, `stability` по mood
- Один персонаж = один голос на весь сериал (фиксация в story bible)
- **Субтитры: PIL PNG overlay** (ffmpeg 8.1 без libfreetype не умеет drawtext)
  - Шрифт Arial/Helvetica Bold 38–48px, белый + stroke 3px, нижняя треть
  - ТОЛЬКО dialogue subs + TBC. Никаких title cards, brainrot-тегов, имён персонажей.
- Фоновая музыка: drama/cinematic, `volume=0.15`
- Общие правила — `rules/roles/sound.md`

### Editor

- **Один ffmpeg pipeline на всю финальную сборку** (concat + overlays + music + fade + CTA). НЕ послойно.
- I2V клипы: нормализация fps 24 → 30 обязательна перед concat
- Avatar клипы: trim to TTS_dur + 0.3s, `apad=whole_dur=${TARGET}` (не `pad_dur`)
- TTS overlay «за стеклом» (редко): `aecho=0.8:0.9:10:0.3`, `adelay=500`
- Субтитры через PNG overlay chain (filter_complex)
- **CTA включается в concat-list** как последний клип (не отдельный re-encode)
- TBC overlay за 2s до конца (до fade)
- Fade out 1.0s на MAIN_DUR (до CTA); CTA идёт после fade в тишине
- Общие правила — `rules/roles/editor.md`

---

## CTA (Call to Action)

CTA-ролик берётся из Supabase `game_assets` (тег `cta` + `video`). Manager скачивает его в Фазе 0 и передаёт Editor-у.

### Сборка

CTA добавляется в concat-list.txt **как последний клип** ПЕРЕД финальной сборкой. Тайминги:

- `MAIN_DUR` = основной контент без CTA
- `CTA_DUR` = длительность CTA
- `TOTAL_DUR` = MAIN_DUR + CTA_DUR
- Музыка `amix` на MAIN_DUR, fade заканчивается до CTA
- `-t TOTAL_DUR` включает CTA

**Результат:** один ffmpeg pass вместо трёх.

---

## Выходные файлы

```
output/YYYY-MM-DD/{GAME_TAG}/serial-drama/
├── storyboard.json
├── scenes/
│   ├── refs/
│   │   ├── character-ref-{name}.png
│   │   └── bg-{location}.png
│   ├── scene-1/
│   │   ├── scene-1.png
│   │   ├── scene-1-end.png (только для I2V)
│   │   ├── scene-1.mp4
│   │   ├── scene-1-scaled.mp4
│   │   └── tts-1.mp3 (только для dialogue)
│   └── scene-N/...
├── subs/sub-N.png
└── final.mp4
```

Также: `games/{GAME_TAG}/serial-drama_story_bible.json` — персистентный, обновляется после каждого эпизода.

После загрузки: `videos/{GAME_TAG}/{YYYY-MM-DD}/serial-drama_final.mp4` в Supabase.

---

## Валидация перед публикацией

- [ ] `format: "serial-drama"`, `series_id`, `episode_number` = story_bible.last_episode + 1
- [ ] `retention_strategy`, `active_loops`, `cliffhanger` заполнены
- [ ] Первый клип — HOOK, последний — CLIFFHANGER
- [ ] ACTION/DIALOGUE ~ 50/50; минимум 2 персонажа говорят
- [ ] Dialogue клипы = 5s (10s только с `duration_reason`)
- [ ] Все изображения 608×1080 (9:16)
- [ ] bg-reference на каждую локацию создан
- [ ] I2V start + end frames: одинаковый персонаж, одинаковый bg
- [ ] TTS через fal.ai ElevenLabs (`voice` имя, не `voice_id`)
- [ ] Субтитры PIL PNG; только dialogue + TBC
- [ ] fps нормализован в 30 перед concat
- [ ] Один ffmpeg pipeline, не послойно
- [ ] CTA включен в concat-list (не отдельный re-encode)
- [ ] TBC overlay за 2s до конца; fade out 1.0s
- [ ] Anti-repetition check пройден
- [ ] Story bible обновлён после генерации

---

## Анти-паттерны

- ❌ `generate_audio: true` в Kling (голос плохой)
- ❌ Kokoro TTS, Kling Lipsync, direct ElevenLabs API
- ❌ `voice_id` хеш вместо `voice` имени
- ❌ 1:1 квадрат для Avatar (только 9:16)
- ❌ character ref напрямую как scene image (каждый клип = отдельный PNG)
- ❌ Разный персонаж на start/end I2V (Kling перемешает)
- ❌ `-shortest` в FFmpeg
- ❌ Закрытие всех петель (минимум 2 активных)
- ❌ Повторение хуков/клиффхэнгеров из последних 8 эпизодов
- ❌ Переделка клипов, которые работают (каждая лишняя генерация = $0.35+)
- ❌ Послойная сборка (ломает музыку и тайминг)
- ❌ Title cards, brainrot-теги, имена персонажей оверлеями
- ❌ Длительные дialogue клипы 10s ради экономии $0.04 (убивает динамику)
