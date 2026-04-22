# Формат "История персонажа" — Лор-монолог от первого лица с визуализацией

Плотно сбитый лор-ролик: персонаж рассказывает свою историю от первого лица, пока Kling I2V визуализирует ключевые моменты. TTS overlay на немое видео, субтитры PIL PNG.

Этот файл — **playbook**: когда использовать, концепт, бюджет, брифы каждой роли. Крафтовые правила — в `rules/roles/*.md`.

---

## Когда использовать

Ключевые слова: «character story», «история персонажа», «лор», «lore», «backstory», «origin story», «предыстория».

---

## Концепт

- **Жанр:** лор-монолог, визуальный сторителлинг от первого лица
- **Стиль:** идентичный игре (берётся из `games/{GAME_TAG}/{GAME_TAG}.md`)
- **Длительность:** 30–40 сек (6–8 клипов × 5s)
- **Бюджет:** до $6.00 на видео. Остановись если расход > $5.40.
- **Формат кадра:** 9:16 (608×1080) для всех сцен

### Модели

- **Image:** NB2 (`fal-ai/nano-banana-2/edit`) — character refs + scene images
- **Video:** Kling 2.6 Pro I2V (`fal-ai/kling-video/v2.6/pro/image-to-video`) — `generate_audio: false`
- **Audio:** ElevenLabs TTS overlay (`fal-ai/elevenlabs/tts/eleven-v3`) — монолог от первого лица
- **Музыка:** да, mood по сюжету, `volume` по настроению (0.10–0.20)

### Ключевая механика

Персонаж НЕ говорит на видео (нет lipsync). Видео — визуализация того, о чём рассказывает голос. I2V показывает действия, локации, ключевые моменты. TTS накладывается поверх как закадровый монолог.

---

## Бюджет (ориентиры)

| Компонент | 5s клип |
|---|---|
| Image (NB2) | $0.04 |
| Kling I2V 5s (generate_audio=false) | $0.35 |
| **Итого за клип** | **~$0.39** |

| Компонент | Стоимость |
|---|---|
| ElevenLabs TTS (~40s монолог) | ~$0.20 |
| Музыка (локальная) | $0.00 |

| Вариант | Клипов | Стоимость |
|---|---|---|
| Базовый (рекомендуемый) | 6 × 5s = 30s | ~$2.50 |
| Расширенный | 8 × 5s = 40s | ~$3.30 |
| С доп. refs/bg | 8 × 5s + 2–3 bg | ~$3.50 |

---

## Структура видео

Структура гибкая — сценарист адаптирует под историю конкретного персонажа. Ориентиры:

| Фаза | Тайминг | Цель | Клипов |
|---|---|---|---|
| **HOOK** | 0–5s | Драматический момент из середины/конца истории. Остановка скролла | 1 clip (5s) |
| **ORIGIN** | 5–15s | Кто персонаж, откуда, что определило путь | 2 clips (5s) |
| **TURNING POINT** | 15–25s | Ключевое событие: битва, предательство, потеря, обретение силы | 2 clips (5s) |
| **REVELATION** | 25–35s | Кем персонаж стал, чем известен сейчас, главная черта | 1–2 clips (5s) |
| **CTA** | последние ~5s | CTA clip | 1 clip |

### Что работает

- **In medias res.** Начинай с самого яркого момента, потом flashback к началу
- **Конкретные визуальные образы.** «Меч раскалился добела» > «Я стал сильнее»
- **Эмоциональные контрасты.** Тихий момент → взрыв действия → тишина
- **Каждый клип = новый визуальный образ.** Смена локации, ракурса, масштаба
- **Голос ведёт, видео иллюстрирует.** Не дублируй — дополняй

### Что НЕ работает

- ❌ Хронологический пересказ без хука (скучно)
- ❌ Абстрактные эмоции без визуальных ставок
- ❌ Монотонный видеоряд (один и тот же ракурс 40 секунд)
- ❌ Текст монолога дословно описывает то, что на экране
- ❌ Философские монологи без действия

### Монолог

- От первого лица персонажа
- ~80–120 слов на 30–40s
- Короткие предложения, панчевые фразы
- Голос подбирается из ElevenLabs по характеру персонажа
- Каждые 5s (1 клип) ≈ 10–15 слов

---

## Брифы ролям

### Scenarist

- Напиши монолог от первого лица персонажа (~80–120 слов, 30–40s)
- Структура: HOOK (in medias res) → ORIGIN → TURNING POINT → REVELATION
- Раздели монолог на фрагменты по 10–15 слов = по одному на клип (5s)
- `clip_type: "action"` для всех клипов (I2V, не Avatar)
- `character_speech: null` для всех клипов (голос через TTS overlay, не в видео)
- Поле `tts` в storyboard.json — текст монолога для каждого клипа
- `action_description` — что происходит визуально, НЕ повтор текста монолога
- Минимум 2 разных действия на клип (микро-движения)
- camera_angle отличается между соседними клипами
- Количество персонажей в кадре — по сюжету (1–2, макс 2 в кадре)
- bg-reference на каждую уникальную локацию
- Голос: выбери из ElevenLabs по характеру (Daniel — уверенный, George — нейтральный, Charlie — молодой, Charlotte — женский)
- Общие правила сценария — `rules/roles/scenarist.md`

**Storyboard.json — дополнительные поля:**

```json
{
  "format": "character-story",
  "game_tag": "{GAME_TAG}",
  "character_name": "{name}",
  "tts": {
    "full_text": "{весь монолог}",
    "voice": "{voice name}",
    "stability": 0.25,
    "style": 0.75,
    "language_code": "{ISO 639-1}"
  },
  "music": {
    "mood": "{mood}",
    "volume": 0.15
  },
  "clips": [
    {
      "index": 1,
      "beats": ["hook"],
      "duration_sec": 5,
      "clip_type": "action",
      "character_speech": null,
      "tts_segment": "{фрагмент монолога для этого клипа}",
      "character_state": "...",
      "facial_expression": "...",
      "action_description": "...",
      "camera_angle": "...",
      "image_prompt": "...",
      "negative_prompt": "..."
    }
  ]
}
```

### Storyboarder

- Стиль берётся из `games/{GAME_TAG}/{GAME_TAG}.md` (идентичный игре)
- Все кадры 9:16 (608×1080)
- Character ref: создай anchor ref (нейтральная поза, тёмный фон) из game config
- bg-reference на каждую уникальную локацию (локации меняются по ходу истории)
- Chain: scene-N refs = `[character-ref, bg-ref-for-this-location]`
- Если 2 персонажа в кадре — оба через refs, макс 2 refs на изображение
- `image_prompt` описывает визуальное действие из `action_description`, НЕ текст монолога
- Визуальная валидация каждого PNG обязательна
- I2V start + end frame на каждый клип (оба с одинаковым персонажем и bg)
- Общие правила — `rules/roles/storyboarder.md`

### Animator

- Все клипы через **Kling 2.6 Pro I2V** (`generate_audio: false`)
- Только микро-движения: взгляд, жест, поворот головы, ветер, частицы, камера
- Motion prompt = технический: позиции, камера, физические действия
- Start ≈ end для I2V (один персонаж, один bg, минимальное отличие)
- Длительность: 5s для всех клипов
- Polling: base URL `fal-ai/kling-video`, каждые 15s, макс 10 мин
- НЕ использовать: Kling Avatar, Veo3, generate_audio: true
- Общие правила — `rules/roles/animator.md`

### Sound

- **TTS:** ElevenLabs через fal.ai (`fal-ai/elevenlabs/tts/eleven-v3`)
  - `voice` = имя строкой (Daniel, George, Charlie, Charlotte), НЕ voice_id
  - Один голос на всё видео (персонаж один)
  - `stability` и `style` по характеру персонажа
  - Генерируй полный монолог одним запросом (не по фрагментам)
- **Субтитры: PIL PNG overlay** (как serial-drama)
  - Шрифт Arial/Helvetica Bold 38–48px, белый + stroke 3px, нижняя треть
  - Разбивка по `tts_segment` из storyboard — один сегмент на клип
  - Только текст монолога. Никаких title cards, имён, тегов
- **Музыка:** по настроению из storyboard (`music.mood`)
  - Выбери трек из `music/tracks.json` по mood
  - `volume` из storyboard (default 0.15)
- Общие правила — `rules/roles/sound.md`

### Editor

- **Один ffmpeg pipeline** на всю финальную сборку
- Нормализация каждого клипа: scale 1080×1920, 30fps, `preset slow`, `crf 20`
- I2V 24fps → нормализация в 30fps обязательна
- **Concat:** hard cuts, без crossfade
- **TTS overlay:**
  - Полный монолог (один файл) накладывается на concat видео
  - `apad=whole_dur=${MAIN_DUR}` (не `-shortest`)
  - TTS volume=1.0
- **Музыка:**
  - `amix` с TTS, `volume` из storyboard
  - Длительность = MAIN_DUR (до CTA)
  - Fade out музыки 1.0s перед CTA
- **Субтитры:** PIL PNG overlay chain через filter_complex
- **CTA:** в concat-list как последний клип
  - MAIN_DUR = контент без CTA
  - CTA_DUR = длительность CTA
  - TOTAL_DUR = MAIN_DUR + CTA_DUR
  - `-t TOTAL_DUR`
- Общие правила — `rules/roles/editor.md`

---

## CTA (Call to Action)

CTA-ролик (~5s) добавляется в конец. Ссылка на asset в `games/{GAME_TAG}/assets/cta/cta.mp4` или Supabase URL.

### Подготовка

1. Скачать CTA через `curl` (НЕ urllib)
2. `ffprobe` валидация: если файл уже валиден — не перекачивать
3. Нормализовать в `games/{GAME_TAG}/assets/cta-normalized.mp4` (scale 1080×1920, 30fps, AAC 128k)

### Сборка

CTA добавляется в concat-list.txt как последний клип ПЕРЕД финальной сборкой.

---

## Выходные файлы

```
output/YYYY-MM-DD/{GAME_TAG}/character-story/
├── storyboard.json
├── scenes/
│   ├── refs/
│   │   ├── character-ref.png
│   │   └── bg-{location}.png
│   ├── scene-1/
│   │   ├── scene-1.png
│   │   ├── scene-1-end.png
│   │   ├── scene-1.mp4
│   │   └── scene-1-scaled.mp4
│   └── scene-N/...
├── tts-output.mp3
├── subs/
│   └── sub-N.png
├── concat-list.txt
└── final.mp4
```

---

## Валидация перед публикацией

- [ ] `format: "character-story"` в storyboard.json
- [ ] `character_speech: null` для всех клипов (голос через TTS, не в видео)
- [ ] `tts_segment` заполнен для каждого клипа
- [ ] Полный монолог = сумма всех `tts_segment`
- [ ] Все изображения 608×1080 (9:16)
- [ ] bg-reference на каждую уникальную локацию
- [ ] I2V start + end frames: одинаковый персонаж, одинаковый bg
- [ ] camera_angle отличается между соседними клипами
- [ ] TTS через fal.ai ElevenLabs (`voice` имя, не `voice_id`)
- [ ] Субтитры PIL PNG: только текст монолога
- [ ] fps нормализован в 30 перед concat
- [ ] Один ffmpeg pipeline, не послойно
- [ ] Музыка fade out перед CTA
- [ ] CTA включен в concat-list
- [ ] `-shortest` НЕ используется

---

## Анти-паттерны

- ❌ `generate_audio: true` в Kling I2V (голос плохой, используем TTS overlay)
- ❌ Kling Avatar / Veo3 (формат не использует lipsync)
- ❌ `character_speech ≠ null` (голос только через TTS overlay)
- ❌ `voice_id` хеш вместо `voice` имени в ElevenLabs
- ❌ TTS по фрагментам (генерируй весь монолог одним запросом)
- ❌ Текст монолога = описание видеоряда (голос дополняет, не дублирует)
- ❌ character ref напрямую как scene image (каждый клип = отдельный PNG)
- ❌ Разный персонаж на start/end I2V (Kling морфирует)
- ❌ `-shortest` в FFmpeg (используй `apad`)
- ❌ Послойная сборка (ломает музыку и тайминг)
- ❌ Монотонный видеоряд (один ракурс на все 40 секунд)
- ❌ Title cards, brainrot-теги, имена персонажей оверлеями
