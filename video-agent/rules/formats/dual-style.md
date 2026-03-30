# Правила dual-style генерации (Cartoon + Realistic)

Концепт: в одном кадре — cartoon/chibi игровой персонаж рядом с его фотореалистичной человеческой "копией".

---

## Когда использовать

- "Game vs Reality" / "Meet Your Character IRL"
- Сравнение игрового персонажа с реальным человеком
- Cosplay-контент
- "Which character are you?"

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
- **НЕ используй chain reference** между клипами разных персонажей (per consistency.md)

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

В `games/{game}.md` описывай ДВЕ версии каждого персонажа:

```markdown
### Hero Name (cartoon)
`cartoon chibi [class] character with bold black outlines, bright flat saturated colors, exaggerated proportions, [8+ деталей внешности]`

### Hero Name (realistic counterpart)
`photorealistic [пол] [телосложение], [те же детали костюма что у cartoon], real skin textures, [живые детали: кожа, шрамы, грязь], [эмоция]`
```

---

## Анти-паттерны

- ❌ Только "cartoon style" без конкретных маркеров (bold outlines, flat colors) — AI сделает semi-realistic
- ❌ Один промпт без разделения "on the left / on the right" — AI объединит в одного персонажа
- ❌ Реалистичная версия без "живых" деталей (кожа, текстуры) — получится 3D рендер, не человек
- ❌ Chain reference между клипами разных персонажей — сломает внешность
- ❌ Попытка сделать cartoon и realistic одинакового размера в промпте — пусть chibi будет меньше

---

## Consistency

Dual-style использует модифицированный Layer 3:
- `style_tags` включают ОБА стиля (cartoon + realistic)
- `lighting` и `color_palette` — **одинаковые** для всех сцен
- Каждая сцена содержит описания ОБОИХ стилей персонажа (cartoon + realistic)
- Chain reference работает стандартно (character-ref + предыдущая сцена)
