# Формат "Dual-Style" — Cartoon + Realistic

Концепт: в одном кадре — cartoon/chibi игровой персонаж рядом с его фотореалистичной человеческой "копией".

---

## Когда использовать

- "Game vs Reality" / "Meet Your Character IRL"
- Сравнение игрового персонажа с реальным человеком
- Cosplay-контент
- "Which character are you?"

---

## Обзор формата

- **Концепт:** cartoon + realistic версия одного персонажа рядом в кадре
- **Модель:** Kling 2.6 Pro I2V (`generate_audio: true`)
- **Аудио:** Kling SFX (звуковые эффекты)
- **Речь:** нет (`character_speech: null`)
- **Длительность:** 15-30 сек (3 клипа × 5-10s)
- **Бюджет:** $5 максимум

---

## ФАЗА 0: ИНИЦИАЛИЗАЦИЯ

1. Загрузить `tools/fal-ai.md` — API reference
2. Загрузить `rules/main/storyboard.md` — правила промптинга + консистентность
3. Загрузить `rules/main/fallback.md` — обработка ошибок
4. Загрузить `games/{GAME_TAG}/{GAME_TAG}.md` — конфиг игры
5. Проверить наличие dual-style Character Prompt Blocks в game config (cartoon + realistic версии)
6. Определить персонажей для каждого клипа

---

## Структура image_prompt

```
[ENVIRONMENT],
on the left a cartoon chibi [CHARACTER] with bold black outlines bright flat colors exaggerated proportions [DETAILS],
on the right a photorealistic human [MATCHING OUTFIT AND BUILD] real skin textures [DETAILS],
both [ACTION/POSE],
[LIGHTING], [CAMERA], vertical composition, 9:16 aspect ratio
```

---

## Ключевые правила

### 1. Чёткое разделение стилей

Cartoon-версия ОБЯЗАНА содержать маркеры стиля, иначе AI сделает обоих реалистичными:

**Cartoon маркеры:**
- `bold black outlines` — жирные контуры
- `bright flat saturated colors` — плоская яркая заливка
- `exaggerated chibi proportions` — преувеличенные пропорции
- `large head, small body` — большая голова (если chibi)

**Realistic маркеры:**
- `photorealistic` — фотореализм
- `real skin textures` — реальная текстура кожи
- `natural proportions` — естественные пропорции
- `weathered / sun-darkened / tanned` — реалистичные детали кожи

### 2. Связь между версиями

Обе версии одного персонажа должны быть очевидно связаны:
- **Одинаковый костюм** — цвета, тип одежды, аксессуары
- **Одинаковая поза** — `matching pose`, `mirrored stance`
- **Одинаковые ключевые детали** — если у cartoon розовая бандана, у realistic тоже

### 3. Позиционирование

- Cartoon **всегда** на одной стороне (обычно left), realistic **всегда** на другой (right)
- Позиция фиксирована на всё видео (не меняется между клипами одного персонажа)
- `side by side` — рядом, не один за другим

### 4. Размеры в кадре

- Cartoon может быть **меньше** (chibi = маленький), realistic — крупнее
- Это нормально и даже желательно — подчёркивает контраст стилей
- Не пытайся выровнять их по высоте в промпте

---

## Reference images

- Используй **игровой ассет** (скриншот, character card) как `image_urls[0]`
- Это помогает AI модели "увидеть" cartoon-стиль персонажа
- **НЕ используй chain reference** между клипами разных персонажей

---

## Motion prompt

- Описывай действия **обоих** персонажей отдельно:
  ```
  The cartoon pirate on the left bounces with exaggerated steps.
  The realistic pirate on the right walks with heavy confident swagger.
  ```
- Можно добавлять взаимодействие:
  ```
  Real pirate strokes his beard, cartoon pirate copies the gesture with oversized hand.
  ```
- Если без речи — `character_speech: null` для всех клипов

---

## Мульти-персонажное видео

Если показываем несколько персонажей (каждому свой клип):

| Аспект | Правило |
|--------|---------|
| Клипы | 1 клип = 1 пара (cartoon + realistic одного персонажа) |
| Reference | Каждый клип получает свой image_urls с ассетом текущего персонажа |
| Chain reference | НЕ используется между клипами разных персонажей |
| style_tags | Единые для всех клипов |
| lighting | Единое или подобранное под среду клипа |
| camera_angle | Разный для каждого соседнего клипа |

---

## Character Prompt Blocks для dual-style

В `games/{GAME_TAG}/{GAME_TAG}.md` описывай ДВЕ версии каждого персонажа:

```markdown
### Hero Name (cartoon)
`cartoon chibi [class] character with bold black outlines, bright flat saturated colors, exaggerated proportions, [8+ деталей внешности]`

### Hero Name (realistic counterpart)
`photorealistic [пол] [телосложение], [те же детали костюма что у cartoon], real skin textures, [живые детали: кожа, шрамы, грязь], [эмоция]`
```

---

## Бюджет

| Компонент | Стоимость |
|-----------|-----------|
| Character reference (game asset или Nano Banana 2) | $0.04/шт |
| Scene images (3 × Nano Banana 2) | $0.12 |
| Kling I2V (3 × 5-10s, с аудио) | 15-30s × $0.14 = $2.10-$4.20 |
| FFmpeg (локальный) | $0.00 |
| **Итого** | **~$2.50-$4.50** |

**Лимит:** $5.00. Остановись если расход > $4.50.

---

## Валидация

- [ ] Cartoon маркеры присутствуют в image_prompt (bold outlines, flat colors, exaggerated proportions)
- [ ] Realistic маркеры присутствуют в image_prompt (photorealistic, real skin textures)
- [ ] Костюм/поза/детали совпадают между cartoon и realistic версиями
- [ ] Позиционирование: cartoon на одной стороне, realistic на другой (фиксировано)
- [ ] `character_speech: null` для всех клипов
- [ ] `camera_angle` разный для каждого соседнего клипа
- [ ] `style_tags` включают оба стиля (cartoon + realistic)
- [ ] `lighting` и `color_palette` одинаковые для всех сцен
- [ ] Chain reference между клипами разных персонажей НЕ используется
- [ ] Бюджет не превышен ($5.00)

---

## Анти-паттерны

- ❌ Только "cartoon style" без конкретных маркеров (bold outlines, flat colors) — AI сделает semi-realistic
- ❌ Один промпт без разделения "on the left / on the right" — AI объединит в одного персонажа
- ❌ Реалистичная версия без "живых" деталей (кожа, текстуры) — получится 3D рендер, не человек
- ❌ Chain reference между клипами разных персонажей — сломает внешность
- ❌ Попытка сделать cartoon и realistic одинакового размера в промпте — пусть chibi будет меньше

---

## Выходные файлы

```
OUTPUT_DIR/
├── storyboard.json
├── scenes/
│   ├── refs/
│   │   └── character-ref.png      # Game asset или сгенерированный ref
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

Dual-style использует модифицированный Layer 3:
- `style_tags` включают ОБА стиля (cartoon + realistic)
- `lighting` и `color_palette` — **одинаковые** для всех сцен
- Каждая сцена содержит описания ОБОИХ стилей персонажа (cartoon + realistic)
- Chain reference работает стандартно (character-ref + предыдущая сцена)
