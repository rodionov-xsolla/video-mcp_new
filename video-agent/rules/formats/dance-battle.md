# Формат "Dance Battle" — Комедийные танцевальные батлы

Два персонажа соревнуются в танцевальном батле на сцене. Настроение — комедийное. Персонажи выкладываются на максимум: движения утрированные, слегка нелепые, выполненные с абсолютно серьёзным лицом. Контраст между усилием и абсурдом — главный источник юмора.

---

## Когда использовать

Идея содержит ключевые слова: "dance battle", "dance", "танцевальный батл", "танец", "dance off", "dance competition", "баттл танцев".

---

## Обзор формата

- **Концепт:** два персонажа на сцене, танцевальный батл, комедия
- **Персонажи:** любые — игровые, мемные, абсурдные комбинации
- **Стиль:** реалистичный 3D render с комедийной стилизацией
- **Модель:** Kling 2.6 Pro I2V (image → video)
- **Аудио:** `generate_audio: true` — Kling генерирует толпу, музыку, SFX
- **Речь:** НЕТ — никаких голосов, диалогов, нарратива
- **Длительность:** 3 клипа × 5s = ~15s (или 2 × 10s = ~20s)
- **Бюджет:** $5 максимум

---

## Серийный формат

Dance Battle идеально подходит для серии: новые персонажи в каждом выпуске, одна и та же сцена.

**Что меняется между выпусками:**
- Персонажи (внешность, пропорции, костюмы)
- Стили танца (breakdance, ballroom, hip-hop, folk, robot, ballet, salsa)
- Эмоции (серьёзная концентрация, самоуверенность, паника, отвращение)
- Кто "побеждает" визуально

**Что НЕ меняется (locked parameters):**
- Сцена, освещение, толпа, камера, render style (см. ниже)

---

## ФАЗА 0: ИНИЦИАЛИЗАЦИЯ

1. Загрузить `tools/fal-ai.md` — API reference (Kling 2.6 Pro I2V)
2. Загрузить `rules/main/fallback.md` — обработка ошибок
3. *(опционально)* Загрузить game config `games/{GAME_TAG}/{GAME_TAG}.md` — если персонажи из конкретной игры
4. Получить game_assets из Supabase: `GET /rest/v1/game_assets?game_tag=eq.{GAME_TAG}&select=*`
6. *(опционально)* Загрузить `music/tracks.json` — фоновая музыка
7. Определить из идеи:
   - Двух персонажей (или одного — тогда подобрать оппонента из той же вселенной)
   - Стили танца для каждого
   - Источник комедии (размер, скорость, стиль, костюм)

---

## ФАЗА 1: СЦЕНАРИЙ (storyboard.json)

### Locked Parameters (одинаковые для ВСЕХ видео серии)

Эти параметры включаются в КАЖДЫЙ `image_prompt` и `motion_prompt`:

**Камера (locked):**
Wide shot from low angle (~15°) at stage-edge level, both characters fully in frame.

**Локация (locked):**
Circular dance arena-stage in a large hall, polished dark wooden floor with reflections, low podium.

**Толпа (locked):**
Dense crowd of spectators around the stage — silhouettes and raised hands in soft bokeh. Crowd reacts with movement.

**Освещение (locked):**
Two contrasting colored spotlights from above — warm orange left, cool blue right — splitting the stage into two color zones. Central white spot from above hits the floor with a hard beam. Light haze catching the beams. Colored light pools on the polished floor.

**Атмосфера (locked):**
Light stage haze in spotlight beams. Micro dust particles in light cones. Energetic, festive, competitive, comedic.

**Render style (locked):**
Realistic 3D render, physically based materials, true-to-life textures, cinematic realism with subtle comedic stylization, realistic cloth and skin simulation.

### Variable Parameters (уникальные для каждого видео)

**Персонажи:**
- Детальное описание внешности, материалов, пропорций каждого (8+ деталей)
- Персонажи визуально РАЗЛИЧНЫ друг от друга
- Оба узнаваемы даже в движении

**Физика танца:**
- Каждый танцор получает КОНКРЕТНОЕ движение с механикой тела
- Перенос веса, постановка ног, реакция одежды/волос/тела на движение
- Позы асимметричны — один делает одно, другой реагирует по-другому
- Каждое движение имеет ЧЁТКОЕ конечное положение

**Мимика:**
- Конкретная, комедийная, разная для каждого персонажа
- Мёртвая серьёзность на смешных движениях = комедия
- НИКОГДА не generic "happy" или "excited"

### Структура клипов

| Клип | Dur | Камера | Действие | Комедия |
|------|-----|--------|----------|---------|
| **1. Вход** | 5s | Wide shot, slow lateral tracking L→R | Персонажи выходят на сцену, принимают стартовые позы, толпа реагирует | Контраст внешности: размер, стиль, энергия |
| **2. Батл** | 5-10s | Gentle push-in к ведущему танцору | Персонаж A выполняет танцевальный приём, Персонаж B реагирует | Мёртвая серьёзность + абсурдное движение |
| **3. Финал** | 5s | Pull-back to wide, settle | Финальная поза/фриз, толпа взрывается, побеждающий персонаж триумфирует | Неожиданный финал, payoff контраста |

### 4-Layer Prompt Structure (для Kling)

Каждый `image_prompt` и `motion_prompt` строится по 4-слойной структуре:

```
Layer 1 — Camera movement (как камера ведёт себя во времени)
Layer 2 — Subjects & action physics (кто + конкретная механика тела)
Layer 3 — Environment & lighting (где + настройка света)
Layer 4 — Texture & style (качество рендера + материалы)
```

**Prompt пишется как один цельный абзац в этом порядке слоёв.**

**Правила для Kling:**
- Максимум 3-5 основных идей в промпте — Kling теряет связность при перегрузке
- Камера описывается кинематографическими терминами (tracking, push-in, orbit, pan)
- Механика тела: перенос веса, постановка ног, траектория рук
- Руки привязаны к чему-то: хватают одежду, хлопают по полу, указывают на оппонента
- Конечные точки движения: "freezes in a splits pose" НЕ "dances energetically"
- Одно главное действие на персонажа за раз — не одновременные сложные движения
- **60-100 слов** для image_prompt, **40-60 слов** для motion_prompt

### Negative Prompt (для каждой сцены)

Стандартный negative prompt для dance battle:
```
blur, distort, low quality, static pose, frozen frame, extra limbs, merged bodies, text overlay, watermark, split screen, duplicate characters
```

### Storyboard Schema

```json
{
  "format": "dance-battle",
  "game_tag": "MLBB",
  "visual_identity": {
    "character_a": {
      "name": "Lancelot",
      "description": "Lean athletic swordsman, silver shoulder-length hair, pale porcelain skin, ornate blue-silver armor with flowing cape, confident smirk, sharp jawline",
      "dance_style": "ballet",
      "emotion": "smug confidence"
    },
    "character_b": {
      "name": "Franco",
      "description": "Massive barrel-chested Viking, wild red beard braided with metal rings, fur-lined leather armor, iron helmet slightly askew, bewildered squint",
      "dance_style": "breakdance",
      "emotion": "dead-serious concentration"
    },
    "comedy_source": "size mismatch — elegant lean dancer vs massive confused Viking",
    "environment_description": "Circular dance arena-stage in a large hall, polished dark wooden floor with reflections, low podium",
    "lighting": "Two contrasting colored spotlights — warm orange left, cool blue right — central white spot, light haze in beams",
    "style_tags": "realistic 3D render, physically based materials, cinematic realism with subtle comedic stylization"
  },
  "narrative_arc": {
    "hook": "Two mismatched warriors face off on a dance floor",
    "development": "Each performs their style — elegant vs brute force",
    "climax": "Unexpected winner or both freeze in absurd pose"
  },
  "scenes": [
    {
      "index": 1,
      "beats": ["entrance", "staredown"],
      "duration_sec": 5,
      "character_state": "Character A strikes elegant pose, Character B cracks knuckles",
      "facial_expression": "A: confident half-smile, B: confused squint",
      "character_speech": null,
      "environment_state": "Crowd silhouettes buzz with anticipation, spotlights lock onto stage",
      "camera_angle": "wide low-angle",
      "image_prompt": "[4-layer structure: camera → subjects → environment → style, 60-100 words]",
      "motion_prompt": "[camera movement + body mechanics + end state, 40-60 words]",
      "negative_prompt": "blur, distort, low quality, static pose, frozen frame, extra limbs, merged bodies"
    },
    {
      "index": 2,
      "beats": ["battle_move_a", "reaction_b"],
      "duration_sec": 10,
      "character_state": "A performs pirouette ending in split, B attempts breakdance spin",
      "facial_expression": "A: focused elegance, B: panicked effort with gritted teeth",
      "character_speech": null,
      "environment_state": "Crowd erupts, light haze pulses, floor reflections distort with movement",
      "camera_angle": "medium push-in",
      "image_prompt": "...",
      "motion_prompt": "...",
      "negative_prompt": "..."
    },
    {
      "index": 3,
      "beats": ["finale", "crowd_reaction"],
      "duration_sec": 5,
      "character_state": "Both freeze in final poses — A in elegant bow, B mid-headstand wobbling",
      "facial_expression": "A: triumphant closed-eye smile, B: upside-down bewilderment",
      "character_speech": null,
      "environment_state": "Crowd roars, confetti-like particles in spotlight beams, energy peak",
      "camera_angle": "wide pull-back",
      "image_prompt": "...",
      "motion_prompt": "...",
      "negative_prompt": "..."
    }
  ]
}
```

---

## ФАЗА 2: CHARACTER REFERENCE

Сгенерируй ДВУХ персонажей через Nano Banana 2:

**Character A:**
```
[STYLE_TAGS], [CHARACTER_A_DESCRIPTION],
full body character pose, standing confident, dark stage background with colored spotlights,
clear detailed character design, vertical composition, 9:16 aspect ratio
```

**Character B:** (отдельная генерация)
```
[STYLE_TAGS], [CHARACTER_B_DESCRIPTION],
full body character pose, standing ready, dark stage background with colored spotlights,
clear detailed character design, vertical composition, 9:16 aspect ratio
```

- Сохрани как `character-ref-a.png` и `character-ref-b.png`
- **8+ визуальных деталей** на каждого персонажа
- Стиль: одинаковый для обоих (realistic 3D render)
- Персонажи ВИЗУАЛЬНО РАЗЛИЧНЫ (размер, цвет, пропорции)

---

## ФАЗА 3: ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ

Для каждой сцены K, используй **chain reference**:

- Сцена 1: `image_urls: [character-ref-a-url, character-ref-b-url]`
- Сцена 2+: `image_urls: [character-ref-a-url, character-ref-b-url, scene-(K-1)-url]`

**ВАЖНО:** оба character reference передаются в каждую сцену для консистентности обоих персонажей.

`image_prompt` = полный 4-layer prompt из storyboard (60-100 слов).

---

## ФАЗА 4: АНИМАЦИЯ (Kling 2.6 Pro I2V)

Для каждой сцены K:
- `start_image_url` = scene-K.png URL
- `prompt` = `motion_prompt` из storyboard (40-60 слов)
- `duration` = `"5"` или `"10"` (согласно storyboard)
- `generate_audio` = **`true`** — Kling генерирует звуки толпы, музыку, SFX
- `aspect_ratio` = `"9:16"`
- `negative_prompt` = из storyboard

**Kling I2V ограничения для танца:**
- Kling I2V лучше всего работает с позовыми переходами, а не с активной хореографией
- ✅ Перенос веса, наклоны, повороты корпуса, жесты руками, смена позы, фриз-позы
- ✅ Медленные движения с чёткими конечными точками
- ⚠️ Быстрые вращения, прыжки, splits — могут вызвать артефакты, использовать осторожно
- ❌ Одновременные сложные движения обоих персонажей

**Рекомендация:** один персонаж выполняет движение, второй реагирует статично или минимально. Это и технически надёжнее, и комедийнее.

---

## ФАЗА 5: СБОРКА

### 5.1 Масштабирование

```bash
FFMPEG=/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg

$FFMPEG -y -i scene-K.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -r 30 -c:v libx264 -preset slow -crf 10 -pix_fmt yuv420p \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  scene-K-scaled.mp4
```

### 5.2 Склейка (hard cut)

```bash
cat > concat-list.txt << EOF
file 'scene-1-scaled.mp4'
file 'scene-2-scaled.mp4'
file 'scene-3-scaled.mp4'
EOF

$FFMPEG -y -f concat -safe 0 -i concat-list.txt \
  -r 30 -c:v libx264 -preset slow -crf 10 \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  assembled.mp4
```

**Concat с re-encode** (не `-c copy`). Без crossfade — разные планы камеры делают каты профессиональными.

### 5.3 Фоновая музыка (опционально)

Если Kling-generated audio недостаточно, добавь трек:

```bash
$FFMPEG -y -i assembled.mp4 -i bg-music.mp3 \
  -filter_complex "[0:a]volume=0.6[sfx];[1:a]volume=0.25[music];[sfx][music]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 128k \
  final.mp4
```

- Kling SFX (толпа, удары): `volume=0.6`
- Музыка: `volume=0.25`
- **НИКОГДА не используй `-shortest`**

---

## ФАЗА 6: UPLOAD & LOG

1. Загрузи `final.mp4` в Supabase Storage:
   - Путь: `videos/{GAME_TAG}/{YYYY-MM-DD}/dance-battle_final.mp4`
   - Получи публичный URL

2. Запиши лог в `video_agent_runs`:
   - game_tag, input_idea, approach_used, model_used, total_cost_usd, output_video_url, status, video_duration_seconds, scenes

3. Покажи отчёт о стоимости пользователю.

4. Для серий: обнови Anti-Drift Layer трекинг (какие стили/эмоции/победители использовались).

---

## Anti-Drift Layer (для серийного производства)

При создании нескольких выпусков подряд, ОБЯЗАТЕЛЬНО ротируй:

**Стили танца** (не повторять в 5 выпусках подряд):
breakdance, ballroom, hip-hop, folk, robot, ballet, salsa, moonwalk, floss, headbang

**Эмоции на лицах:**
dead-serious concentration, smug confidence, panicked effort, surprised mid-move, disgusted determination

**Кто "побеждает" визуально:**
левый персонаж → правый → оба → левый → ...

**Акцент камеры:**
push-in к левому → push-in к правому → wide → ...

**Энергия толпы:**
взрыв → шокированная тишина → смешанные реакции → медленный build-up → ...

**Источник комедии:**
size mismatch → speed mismatch → style clash → wardrobe malfunction → prop interaction → ...

**Детекция повторений:**
- Если тот же танцевальный приём что в прошлый раз → заменить
- Если два подряд видео с одинаковым финалом камеры → изменить второй
- Если комедийный механизм идентичен → переключить на другой источник юмора

---

## Бюджет

| Статья | Стоимость |
|--------|-----------|
| Character ref A (Nano Banana 2) | $0.04 |
| Character ref B (Nano Banana 2) | $0.04 |
| Scene images (3 × $0.04) | $0.12 |
| Kling I2V (5s + 10s + 5s = 20s, с аудио) | 20 × $0.14 = **$2.80** |
| FFmpeg (локальный) | $0.00 |
| **Итого** | **~$3.00** |

**Альтернативный бюджет (3 × 5s):**
| Статья | Стоимость |
|--------|-----------|
| Refs + scenes | $0.20 |
| Kling I2V (15s, с аудио) | 15 × $0.14 = **$2.10** |
| **Итого** | **~$2.30** |

**Лимит:** $5.00. Остановись если расход > $4.50.

---

## Валидация (чеклист перед генерацией)

### Kling readiness
- [ ] Prompt следует 4-layer structure (camera → subjects → environment → style)
- [ ] Камера описана кинематографическими терминами (tracking, push-in, orbit, pan)
- [ ] Оба персонажа имеют конкретную механику тела, не абстрактный "dancing"
- [ ] Каждое движение имеет чёткое конечное положение
- [ ] Руки привязаны к чему-то или имеют конкретную траекторию
- [ ] image_prompt: 60-100 слов, motion_prompt: 40-60 слов
- [ ] Нет image-generation ключевых слов (masterpiece, best quality, 4K, 8K, trending)
- [ ] Нет статичных описаний — всё в движении

### Comedy check
- [ ] Два персонажа создают визуальный контраст (размер, стиль, энергия)
- [ ] Мимика конкретная и разная для каждого
- [ ] Источник комедии очевиден без объяснения
- [ ] Dead-serious effort + absurd movement = humor

### Pipeline check
- [ ] `character_speech: null` для всех сцен (нет голоса)
- [ ] `generate_audio: true` (Kling генерирует толпу и SFX)
- [ ] `camera_angle` разный для соседних клипов
- [ ] `character_description` содержит 8+ визуальных деталей для каждого
- [ ] Два отдельных character reference (A и B)
- [ ] Бюджет не превысит $5.00

---

## Анти-паттерны

**НЕ делай:**
- Не используй абстрактные слова: "nice background", "good lighting", "cool vibe", "dynamic pose", "energetic"
- Не используй image-generation теги: "masterpiece", "best quality", "ultra detailed", "trending on artstation", "4K", "8K"
- Не описывай "dancing" — опиши КОНКРЕТНОЕ движение (перенос веса, позиция рук, наклон)
- Не используй "various", "several", "multiple" — укажи точное количество
- Не давай обоим персонажам одновременные сложные движения — один действует, другой реагирует
- Не повторяй стили/эмоции/финалы в серии (см. Anti-Drift Layer)
- Не добавляй речь/голос/нарратив — формат чисто визуальный + SFX

---

## Banned Terms (никогда не использовать в промптах)

```
nice background, good lighting, cool vibe, detailed scene, beautiful atmosphere
high quality, masterpiece, best quality, ultra detailed
trending on artstation, 4K, 8K, UHD
dynamic pose, dynamic scene, dynamic energy
various, several, multiple
energetic, lively, vibrant
dancing (описывай КОНКРЕТНОЕ движение)
```

---

## Priority Hierarchy

При конфликте элементов, следуй этому порядку:

1. **Kling technical compliance** — 4-layer structure, word count, motion physics
2. **Character recognizability** — зритель должен узнать кто танцует
3. **Motion clarity** — зритель должен понять что каждый делает
4. **Comedic contrast** — смешное должно быть видимым, не подразумеваемым
5. **Camera coherence** — кадр должен быть физически возможным
6. **Visual spectacle** — освещение, атмосфера, толпа
7. **Sound direction** — соответствие музыки

**Примеры разрешения конфликтов:**
- Детальная внешность делает промпт слишком длинным → убери прилагательные внешности, сохрани глаголы движения
- Сложный танцевальный приём делает обоих неузнаваемыми → упрости движение, сохрани персонажа
- Идеальный угол камеры скрывает одного танцора → расширь кадр, пожертвуй push-in драмой
- Комедия требует изменить locked освещение → сохрани освещение, найди комедию в другом

---

## Выходные файлы

```
OUTPUT_DIR/
├── storyboard.json       # Сценарий (ФАЗА 1)
├── character-ref-a.png   # Референс персонажа A (ФАЗА 2)
├── character-ref-b.png   # Референс персонажа B (ФАЗА 2)
├── scene-1.png           # Изображение сцены 1 (ФАЗА 3)
├── scene-2.png           # Изображение сцены 2
├── scene-3.png           # Изображение сцены 3
├── scene-1.mp4           # Анимация сцены 1 (ФАЗА 4)
├── scene-2.mp4           # Анимация сцены 2
├── scene-3.mp4           # Анимация сцены 3
├── scene-1-scaled.mp4    # 1080×1920, 30fps (ФАЗА 5)
├── scene-2-scaled.mp4
├── scene-3-scaled.mp4
├── assembled.mp4         # Склейка без доп. музыки (ФАЗА 5)
└── final.mp4             # Финальное видео (ФАЗА 5)
```
