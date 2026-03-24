# Правила визуальной консистентности

Стратегия поддержания единого стиля, персонажа и окружения через все сцены видео.

---

## Три слоя консистентности

### Слой 1: Character Reference (anchor image)

Перед генерацией сцен создай **одно референсное изображение** персонажа.

**Что генерировать:**
```
[STYLE_TAGS], [CHARACTER_DESCRIPTION],
full body character pose, front-facing view, neutral dark background,
clear detailed character design, vertical composition, 9:16 aspect ratio
```

**Параметры:**
- `tool_type`: Используй `fal-ai/nano-banana-2/edit` с параметром `image_urls`
- `aspect_ratio`: `"9:16"`
- Сохрани как `character-ref.png`

**Зачем:** Это изображение станет якорем — `image_urls[0]` для ВСЕХ генераций сцен. Оно фиксирует внешность персонажа.

**Стоимость:** +~$0.04 (fal-ai/nano-banana-2/edit, одноразово).

**Если в `game_assets` есть `reference_image` для персонажа** — используй его URL как anchor вместо генерации нового. Это экономит кредиты и даёт более стабильный результат (загруженный юзером референс).

---

### Слой 2: Chain Reference (предыдущая сцена)

При генерации каждой сцены передавай `image_urls` с двумя референсами:

| Сцена | `image_urls` |
|-------|-------------|
| 1 | `[character-ref-url]` |
| 2 | `[character-ref-url, scene-1-url]` |
| 3 | `[character-ref-url, scene-2-url]` |
| N | `[character-ref-url, scene-(N-1)-url]` |

**Правила:**
- Всегда **2 референса**: anchor (character-ref) + предыдущая сцена
- Для сцены 1 — только anchor (1 референс)
- НЕ добавляй все предыдущие сцены — только последнюю

**URL-ы:** Используй URL из fal.ai output (`fal.media/files/...`). fal.ai URL-ы временные — скачивай файлы сразу после генерации.

---

### Слой 3: Prompt Consistency (основной механизм)

**Это самый важный слой.** `image_urls` — слабая подсказка. Промпт — главный инструмент.

**Правила:**
1. `character_description` — **дословно одинаковый** во всех сценах (копируй из visual_identity)
2. `environment_description` (базовый) — **дословно одинаковый** (копируй из visual_identity)
3. `style_tags` — **дословно одинаковые** (копируй из visual_identity)
4. `lighting` и `color_palette` — **дословно одинаковые**

**Что МЕНЯЕТСЯ между сценами:**
- `character_state` — действие персонажа (стоит → бежит → атакует)
- `environment_state` — состояние окружения (спокойно → битва → взрыв)
- `camera_style` — ракурс камеры (low angle → medium shot → close-up)

**Пример:**

Сцена 1 промпт:
```
MLBB style, anime aesthetic, vibrant colors, dramatic lighting,     ← ОДИНАКОВО
Lancelot, silver armor, blue cape, silver rapier, spiky hair,       ← ОДИНАКОВО
standing on cliff, cape billowing, sword at side, confident smirk,  ← УНИКАЛЬНО
arena at twilight, stone pillars, aurora sky, floating embers,      ← ОДИНАКОВО
calm before battle, distant towers,                                  ← УНИКАЛЬНО
hero spotlight, purple glow, golden rim light,                       ← ОДИНАКОВО
cinematic low angle, 9:16                                            ← может меняться
```

Сцена 2 промпт:
```
MLBB style, anime aesthetic, vibrant colors, dramatic lighting,     ← ОДИНАКОВО
Lancelot, silver armor, blue cape, silver rapier, spiky hair,       ← ОДИНАКОВО
charging forward, rapier extended, cape streaming, intense gaze,    ← УНИКАЛЬНО
arena at twilight, stone pillars, aurora sky, floating embers,      ← ОДИНАКОВО
alive with battle, explosions, dust and debris,                      ← УНИКАЛЬНО
hero spotlight, purple glow, golden rim light,                       ← ОДИНАКОВО
dynamic medium shot, 9:16                                            ← может меняться
```

---

## Консистентность при I2V анимации

### Одна модель на все сцены

**КРИТИЧЕСКИ ВАЖНО:** Используй ОДНУ I2V модель для ВСЕХ сцен видео. Разные модели (Kling vs Veo3) дают разный визуальный стиль, цветовую температуру и "пластику" движений. Смешивание моделей ломает консистентность.

Приоритет: Kling 2.6 Pro I2V (без речи) / Veo3 T2V (с речью). Если выбранная модель падает — повтори 2-3 раза ту же модель, только потом переключайся.

### Переходы — hard cut с разными планами

**НЕ используй `end_image_url`, crossfade или xfade.** Вместо этого:
- Каждая сцена имеет РАЗНЫЙ `camera_angle` (close-up → wide → low angle)
- Склейка через простой `concat` (hard cut)
- Разные планы камеры делают каты осмысленными и профессиональными

### Мульти-персонажные видео

Если в видео несколько героев (каждый герой = отдельная сцена):

**Reference images:**
- Генерируй (или используй предоставленный) отдельный reference для КАЖДОГО героя
- `image_urls` в каждой сцене содержит reference ТОЛЬКО текущего героя сцены

**Visual identity:**
```json
{
  "visual_identity": {
    "characters": {
      "Saber": "futuristic cyber warrior, blue-black mech armor...",
      "Nana": "cute small cat-girl, pink hair, fox ears...",
      "Alice": "demon queen, crimson bat wings, dark horns..."
    },
    "style_tags": "единые для всех",
    "color_palette": "единые для всех",
    "lighting": "единые для всех"
  }
}
```

**Правила:**
- `style_tags`, `lighting`, `color_palette` — **одинаковые** для всех сцен (единство стиля)
- `character_description` — **разный** для каждой сцены (разные герои)
- В storyboard каждый клип имеет поле `hero` с именем текущего персонажа
- Chain reference НЕ используется между сценами разных героев (нет смысла)

### Второстепенные персонажи (на заднем плане)

Когда в кадре видны другие персонажи кроме ГГ:

1. **Всегда** включай их описание из `visual_identity.characters` в `image_prompt`
2. Описание должно быть **КОНКРЕТНЫМ и ЖИВЫМ** — человеческие детали:
   - ✅ "weathered leather vest, scarred bearded face, sun-darkened skin, tribal tattoos"
   - ❌ "metal armor, helmet" (модель интерпретирует как робота/киборга)
3. Минимум 3 "живые" детали: кожа, шрамы, грязь, пот, борода, татуировки
4. Указывай **их действие:** "stands with arms crossed, smirking menacingly"
5. Указывай **позицию в кадре:** "in the background, slightly blurred" / "in mid-ground"

### Визуальная логика кадра

При мульти-персонажных сценах:

**В image_prompt:**

| Указание | Зачем | Пример |
|----------|-------|--------|
| Позиция персонажа | Модель знает масштаб | "in foreground" / "in background" |
| Направление тела ГГ | Модель знает ориентацию | "body turned toward the girl, back to the raider" |
| Действие вторичного | Модель знает что рисовать | "girl walks away with her back to camera" |

**В motion_prompt:**

| Указание | Пример |
|----------|--------|
| Направление взгляда | "character's eyes follow the girl leaving" |
| Кого НЕ смотрит (при неоднозначности) | "ignoring the raider behind" |
| Направление жеста/руки | "reaches toward the girl with right hand" |

---

### Ken Burns (Approach 1)

Консистентность полностью через промпты (слой 3). Дополнительно:
- Чередуй направление зума между сценами для разнообразия
- Все сцены одного разрешения и fps

---

## Чеклист перед генерацией

- [ ] Character reference изображение сгенерировано и URL сохранён
- [ ] Каждая сцена имеет `image_urls` с character-ref + предыдущей сценой
- [ ] `character_description` идентичен во всех промптах (проверь копипастом)
- [ ] `environment_description` базовый идентичен во всех промптах
- [ ] `style_tags`, `lighting`, `color_palette` идентичны
- [ ] ОДНА модель анимации для всех сцен одного типа (Kling для I2V, Veo3 для T2V)
- [ ] `camera_angle` РАЗНЫЙ для каждой соседней сцены
