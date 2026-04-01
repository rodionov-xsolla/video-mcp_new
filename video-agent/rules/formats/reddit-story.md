# Формат "Reddit Story" — Нарратив поверх геймплея

Монолог от первого лица поверх рандомного геймплея с субтитрами. Личная история игрока — смешная, трогательная, шокирующая, rage. Офферволл вплетён в сюжет как действие героя.

> **Отладочный режим:** Если в задаче есть фраза «Отладочный режим» — после каждой фазы останавливайся и отправляй результат на согласование с пояснением (что сделано, почему, какие решения приняты). Не переходи к следующей фазе без одобрения. Подробнее — `rules/main/workflow.md`.

---

## Когда использовать

Идея содержит ключевые слова: "reddit story", "storytime", "история игрока", "personal story", "narrated gameplay".

---

## Обзор формата

- **Концепт:** экспрессивный монолог от первого лица поверх рандомного геймплея
- **Геймплей:** готовые клипы из `games/{GAME_TAG}/gameplay/`, НЕ привязаны к тексту — чистый фоновый визуал
- **TTS:** ElevenLabs (экспрессивный, мультиязычный, 29 языков)
- **Субтитры:** word-highlight, обязательны
- **Длительность:** до 60 сек (~150-170 слов)
- **Тон:** любой — funny, touching, drama, shock, rage. Главное цепляет
- **Бюджет:** $2.00 максимум (~$0.30-0.50 типичный)

---

## Офферволл-интеграция (НАТИВНАЯ)

Офферволл = ЧАСТЬ СЮЖЕТА, не реклама. Герой использует его как инструмент для достижения цели.

### Структура нарратива:

```
HEADLINE (саммари) → HOOK (завязка) → ПРОБЛЕМА → ОФФЕРВОЛЛ (решение) → ТВИСТ (кульминация)
```

### Правила:

- **НЕ начинать с покупки.** Сначала цепляющая история, потом офферволл появляется как естественное решение
- Офферволл упоминается КАК ДЕЙСТВИЕ ГЕРОЯ: "I grinded offerwall tasks", "выполнял задания", "completed a few offers"
- **НЕ** говорим "купите", "скачайте", НЕ называем сервис по имени
- CTA = overlay текстом "Link in bio" в последние 2 сек видео (НЕ голосом, НЕ в TTS тексте)

### Примеры нативной интеграции:

- **Roblox:** сестра мечтала о скине → я гриндил задания на офферволле → подарил ей на день рождения → она расплакалась
- **Oxide:** рейдер уничтожил мою базу → я неделю выполнял задания на офферволле → залутал лучший gear → отомстил solo
- **MLBB:** проигрывал каждый ранг → выполнил пару заданий, взял нового героя → вытащил 10 игр подряд

---

## Параметры запуска

| Параметр | Описание | Пример |
|----------|----------|--------|
| `game_tag` | Тег игры (совпадает с `gameplay/{game_tag}/`) | `Roblox` |
| `topic` | Тема/настроение (опционально) | `"funny sibling story"` |
| `language` | Язык | `EN`, `RU`, `PT-BR` |

Формат запуска: `reddit story: {game_tag}, {topic}, {language}`

Пример: `reddit story: Roblox, funny sibling revenge, EN`

---

## ФАЗА 0: ИНИЦИАЛИЗАЦИЯ

1. Загрузить game config: `games/{GAME_TAG}/{GAME_TAG}.md`
2. Загрузить `tools/elevenlabs.md` — ElevenLabs TTS API reference
3. Загрузить `rules/main/fallback.md` — обработка ошибок
4. **Валидация gameplay клипов:** проверить `games/{GAME_TAG}/gameplay/`:
   - Папка должна существовать и содержать хотя бы 1 `.mp4` файл
   - Если папка пуста → статус `failed`, сообщить пользователю
5. **Загрузить story bible:** `games/{GAME_TAG}/reddit-story_bible.json`
   - Если не существует → создать из шаблона (см. секцию Story Bible)
6. *(опционально)* Загрузить `music/tracks.json` — фоновая музыка

---

## ФАЗА 1: СЦЕНАРИЙ (storyboard.json)

### Правила нарратива

**Headline (первая строка):**
- Кликбейтный саммари всей истории в одном предложении
- Провокационный, интригующий, задаёт тон ролику
- Произносится голосом + показывается субтитрами
- Примеры:
  - `"I spent 200 hours building and a 9 year old destroyed it all"`
  - `"my clan betrayed me so I wiped their entire base solo"`
  - `"she said Roblox is for kids so I showed her my inventory"`
  - `"I grinded for a week and what happened next broke me"`

**Основной текст (после headline):**
- Всегда от первого лица
- Короткие предложения (макс 15 слов)
- Разговорный стиль — как будто другу рассказываешь
- Игра = мир/сеттинг, не продукт. Упоминается естественно
- Конкретика: имена, числа, детали (не абстракции)
- Hook сразу после headline — затягивает в историю
- Офферволл = действие героя, не реклама
- **ТВИСТ обязателен** — неожиданный поворот, кульминация
- Без корпоративного тона, без прямой рекламы, без названий сервисов

**Запрещено:**
- Длинные предложения (>15 слов)
- Абстракция ("cool stuff" → "legendary dragon skin")
- Скучное начало ("Hey guys today I want to tell you...")
- Прямая реклама, CTA голосом, название сервиса
- Повтор тем/хуков из последних 10 историй (проверь bible)

### Anti-Repetition Check

Перед написанием сценария сверь с `reddit-story_bible.json`:
1. **Темы:** не дублируй темы из последних 10 историй
2. **Тон:** не повторяй один и тот же тон 3 раза подряд
3. **Хуки:** не используй похожий headline/hook
4. **Офферволл-угол:** разнообразь — не всегда "гриндил задания"

### Storyboard Schema

```json
{
  "format": "reddit-story",
  "game_tag": "Roblox",
  "language": "EN",
  "headline": "I spent 200 hours building and a 9 year old destroyed it all",
  "narrative_text": "So my little brother has been playing Roblox every single day for the past year...",
  "tone": "touching",
  "hook": "So my little brother has been playing Roblox every single day for the past year. Every. Single. Day.",
  "voice_id": "pNInz6obpgDQGcFmaJgB",
  "offerwall_angle": "grinded offerwall tasks to buy premium building tools for brother",
  "total_duration_sec": 55,
  "cta_overlay": "Link in bio"
}
```

---

## ФАЗА 2: SKIP

Нет character reference — формат использует готовый геймплей.

---

## ФАЗА 3: TTS (ElevenLabs)

Генерация экспрессивной озвучки через ElevenLabs API.

**Полная документация:** `tools/elevenlabs.md`

### Запрос

```bash
# Озвучиваем headline + narrative_text как единый текст
FULL_TEXT="$HEADLINE. $NARRATIVE_TEXT"

curl -s -X POST "https://api.elevenlabs.io/v1/text-to-speech/$VOICE_ID" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -o tts-output.mp3 \
  -d '{
    "text": "'"$FULL_TEXT"'",
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
      "stability": 0.3,
      "similarity_boost": 0.8,
      "style": 0.7
    }
  }'
```

### Настройки голоса для storytelling:
- `stability: 0.3` — низкая стабильность = более экспрессивный, эмоциональный
- `similarity_boost: 0.8` — высокое сходство с оригинальным голосом
- `style: 0.7` — усиленная стилизация (экспрессия, драма)

### Получить длительность:

```bash
FFMPEG=/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg
TTS_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 tts-output.mp3)
echo "TTS duration: ${TTS_DUR}s"
```

**Стоимость:** ~$0.30/мин (~$0.30 за 60 сек ролик)

---

## ФАЗА 4: SKIP

Нет AI-генерации видео — используем готовый геймплей.

---

## ФАЗА 5: FFmpeg СБОРКА

```bash
FFMPEG=/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg
```

### 5.1 Подготовка gameplay

Выбрать рандомные клипы из `games/{GAME_TAG}/gameplay/`, concat и trim по длительности TTS + 2 сек (для CTA overlay):

```bash
# Получить длительность TTS
TTS_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 tts-output.mp3)
TOTAL_DUR=$(echo "$TTS_DUR + 2" | bc)

# Если один клип достаточной длины:
$FFMPEG -y -i games/{GAME_TAG}/gameplay/clip1.mp4 -t $TOTAL_DUR \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30" \
  -c:v libx264 -preset slow -crf 10 -r 30 -pix_fmt yuv420p \
  -an \
  gameplay-trimmed.mp4
```

Если несколько клипов — concat перед обрезкой:
```bash
# Создать список клипов
ls games/{GAME_TAG}/gameplay/*.mp4 | shuf | while read f; do echo "file '$f'"; done > gameplay-list.txt

$FFMPEG -y -f concat -safe 0 -i gameplay-list.txt \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30" \
  -c:v libx264 -preset slow -crf 10 -r 30 -pix_fmt yuv420p -an \
  -t $TOTAL_DUR \
  gameplay-trimmed.mp4
```

**ВАЖНО:** геймплей без аудио (`-an`) — звук идёт только от TTS.

### 5.2 Overlay TTS на gameplay

```bash
$FFMPEG -y -i gameplay-trimmed.mp4 -i tts-output.mp3 \
  -filter_complex "[1:a]apad[a]" \
  -map 0:v -map "[a]" \
  -c:v copy -c:a aac -b:a 128k -ar 44100 -ac 2 \
  -t $TOTAL_DUR \
  assembled.mp4
```

**НИКОГДА не используй `-shortest`.** Используй `apad` + `-t` для точного контроля длительности.

### 5.3 Субтитры (word-highlight drawtext)

Субтитры разбиваются на сегменты по 3-5 слов. Каждый сегмент показывается с таймингом, синхронизированным с TTS.

**Параметры:**
- Шрифт: жирный sans-serif, fontsize=52
- Позиция: y=78% от верха (примерно 1500px), по центру (x=(w-text_w)/2)
- Фон: semi-transparent black box (drawbox)
- Акцентный цвет: из game config (color_palette)
- Тайминг: равномерно по длительности TTS

**FFmpeg drawtext для каждого сегмента:**
```bash
# Для коротких текстов (<30 сегментов) — inline filter:
$FFMPEG -y -i assembled.mp4 \
  -vf "
    drawbox=x=0:y=ih*0.74:w=iw:h=ih*0.12:color=black@0.6:t=fill:enable='between(t,0,$TTS_DUR)',
    drawtext=text='I spent 200 hours building':fontsize=52:fontcolor=white:fontfile=/System/Library/Fonts/Helvetica.ttc:x=(w-text_w)/2:y=h*0.78:enable='between(t,0.0,2.5)',
    drawtext=text='and a 9 year old':fontsize=52:fontcolor=yellow:fontfile=/System/Library/Fonts/Helvetica.ttc:x=(w-text_w)/2:y=h*0.78:enable='between(t,2.5,4.5)',
    drawtext=text='destroyed it all':fontsize=52:fontcolor=white:fontfile=/System/Library/Fonts/Helvetica.ttc:x=(w-text_w)/2:y=h*0.78:enable='between(t,4.5,6.0)'
  " \
  -c:a copy subtitled.mp4
```

**Для длинных текстов (30+ сегментов)** — используй `-filter_complex_script`:
```bash
# Записать фильтры в файл
cat > subtitle-filter.txt << 'EOF'
[0:v]drawbox=x=0:y=ih*0.74:w=iw:h=ih*0.12:color=black@0.6:t=fill:enable='between(t,0,55)',
drawtext=text='segment 1':fontsize=52:fontcolor=white:...enable='between(t,0.0,1.5)',
drawtext=text='segment 2':fontsize=52:fontcolor=yellow:...enable='between(t,1.5,3.0)',
...
[v]
EOF

$FFMPEG -y -i assembled.mp4 -filter_complex_script subtitle-filter.txt \
  -map "[v]" -map 0:a -c:a copy subtitled.mp4
```

### 5.4 CTA Overlay (последние 2 сек)

```bash
CTA_START=$(echo "$TOTAL_DUR - 2" | bc)

$FFMPEG -y -i subtitled.mp4 \
  -vf "drawtext=text='Link in bio':fontsize=44:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h*0.68:enable='between(t,$CTA_START,$TOTAL_DUR)'" \
  -c:a copy final-cta.mp4
```

### 5.5 Фоновая музыка (опционально)

```bash
$FFMPEG -y -i final-cta.mp4 -i bg-music.mp3 \
  -filter_complex "[1:a]volume=0.05[music];[0:a]volume=1.0[voice];[voice][music]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 128k \
  final.mp4
```

Если без музыки: `cp final-cta.mp4 final.mp4`

**НИКОГДА не используй `-shortest`.**

---

## ФАЗА 6: UPLOAD & LOG + BIBLE UPDATE

1. Загрузи `final.mp4` в Supabase Storage: `videos/{GAME_TAG}/{TIMESTAMP}_final.mp4`
2. Покажи отчёт о стоимости
3. **Обнови story bible** (`games/{GAME_TAG}/reddit-story_bible.json`):
   - Инкрементируй `total_stories`
   - Добавь запись в `stories[]`
   - Обнови `anti_repetition` (recent_themes, recent_tones, recent_hooks)

---

## Story Bible

Файл `games/{GAME_TAG}/reddit-story_bible.json` — персистентный, отслеживает все истории для предотвращения повторов.

### Шаблон (для новой игры):

```json
{
  "game_tag": "Roblox",
  "total_stories": 0,
  "stories": [],
  "anti_repetition": {
    "recent_themes": [],
    "recent_tones": [],
    "recent_hooks": [],
    "banned_combos": []
  }
}
```

### Запись истории:

```json
{
  "id": 1,
  "date": "2026-03-31",
  "tone": "touching",
  "theme": "brother builds memorial city for dead dog",
  "headline": "my little brother built an entire city for our dead dog",
  "hook": "So my little brother has been playing Roblox every single day",
  "offerwall_angle": "grinded offerwall tasks to buy premium building tools for brother",
  "language": "EN",
  "output_dir": "output/2026-03-31/Roblox/reddit-story/"
}
```

### Правила обновления:

- `recent_themes` — хранить последние 10 тем
- `recent_tones` — хранить последние 10 тонов
- `recent_hooks` — хранить последние 10 headlines
- Если массив > 10 — удалять самые старые (FIFO)

---

## Бюджет

| Статья | Стоимость |
|--------|-----------|
| ElevenLabs TTS (~60 сек) | ~$0.30 |
| Gameplay (готовые клипы) | $0.00 |
| FFmpeg (локальный) | $0.00 |
| Музыка (локальная) | $0.00 |
| **Типичный** | **~$0.30-0.50** |
| **Макс** | **$2.00** |

**Лимит:** $2.00. Остановись если расход > $1.80.

---

## Валидация (чеклист перед генерацией)

- [ ] `games/{GAME_TAG}/gameplay/` содержит хотя бы 1 `.mp4` файл
- [ ] `headline` — кликбейтный, провокационный, 1 предложение
- [ ] `narrative_text` — 150-170 слов, от первого лица
- [ ] Все предложения ≤ 15 слов
- [ ] Офферволл вплетён в сюжет как действие героя (не реклама)
- [ ] ТВИСТ присутствует — неожиданный поворот
- [ ] НЕ начинается с покупки — сначала история
- [ ] Нет корпоративного тона / прямой рекламы / названий сервисов
- [ ] Anti-repetition check пройден (тема/тон/хук не дублируют последние 10)
- [ ] `voice_id` выбран и соответствует `language`
- [ ] Общая длительность ≤ 60 сек
- [ ] Бюджет не превысит $2.00

---

## Анти-паттерны

**НЕ делай:**
- Не привязывай кадры геймплея к тексту — это рандомный визуал
- Не используй Kokoro TTS — только ElevenLabs для этого формата
- Не начинай историю с покупки/офферволла — сначала цепляющая завязка
- Не используй `-shortest` в FFmpeg — используй `apad` + `-t`
- Не повторяй темы/хуки из последних 10 историй (проверь bible)
- Не превышай 15 слов в предложении
- Не используй корпоративный тон ("мы рекомендуем", "скачайте")
- Не называй сервис офферволла по имени
- Не озвучивай CTA голосом — только overlay текстом

---

## Выходные файлы

```
OUTPUT_DIR/
├── storyboard.json         # Сценарий (ФАЗА 1)
├── tts-output.mp3          # Озвучка ElevenLabs (ФАЗА 3)
├── gameplay-trimmed.mp4    # Обрезанный геймплей (ФАЗА 5.1)
├── assembled.mp4           # Gameplay + TTS (ФАЗА 5.2)
├── subtitled.mp4           # С субтитрами (ФАЗА 5.3)
└── final.mp4               # Финальное видео (ФАЗА 5.4/5.5)
```

**Также:** `games/{GAME_TAG}/reddit-story_bible.json` — обновляется после каждого ролика.
