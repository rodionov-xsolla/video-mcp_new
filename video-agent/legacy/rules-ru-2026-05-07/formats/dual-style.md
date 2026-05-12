# Формат "Dual-Style" — cartoon + realistic

В одном кадре: cartoon/chibi игровой персонаж рядом со своей фотореалистичной человеческой «копией». Контраст стилей — главный приём.

Этот файл — **playbook**. Крафтовые правила (NB2, Kling I2V, ffmpeg) — в `rules/roles/*.md`.

---

## Когда использовать

Ключевые слова: «dual-style», «game vs reality», «meet your character IRL», cosplay-контент, «which character are you».

---

## Концепт

- **Cartoon слева + realistic справа** (позиционирование фиксировано на всё видео)
- **3 клипа × 5–10s** → 15–30s total
- **Модель:** Kling 2.6 Pro I2V, `generate_audio: true` (SFX)
- **Речь:** НЕТ, `character_speech: null` везде
- **Бюджет:** $5 максимум

---

## Structure

| Клип | Beat | Длит. | camera_angle |
|---|---|---|---|
| 1 | hook — оба появляются рядом | 5s | wide low-angle |
| 2 | development — характер через позу | 5–10s | medium eye-level |
| 3 | climax — синхронное действие или контрастная реакция | 5–10s | wide pull-back |

`camera_angle` разный для соседних клипов (обязательно).

Мульти-персонажное видео: 1 клип = 1 пара (cartoon + realistic одного персонажа), chain reference **не** пересекается между разными персонажами.

---

## Ключевые правила промптинга

### 1. Cartoon и realistic маркеры (обязательны)

Без этих маркеров AI сделает обоих реалистичными.

**Cartoon:**
- `bold black outlines`
- `bright flat saturated colors`
- `exaggerated chibi proportions`
- `large head, small body` (если chibi)

**Realistic:**
- `photorealistic`
- `real skin textures`
- `natural proportions`
- `weathered / sun-darkened / tanned`

### 2. Связь между версиями
- Одинаковый костюм (цвета, тип одежды, аксессуары)
- Одинаковая поза (`matching pose`, `mirrored stance`)
- Одинаковые ключевые детали (розовая бандана у cartoon → розовая у realistic)

### 3. Позиционирование
- Cartoon **всегда** слева, realistic **всегда** справа (или фиксировано наоборот — одно решение на весь ролик)
- `side by side`, не один за другим

### 4. Размеры в кадре
- Cartoon может быть **меньше** (chibi = маленький), realistic крупнее
- Это усиливает контраст, не пытайся выровнять по высоте

---

## Storyboard extensions

```json
{
  "format": "dual-style",
  "visual_identity": {
    "character_description": {
      "cartoon": "cartoon chibi [class] with bold black outlines, bright flat saturated colors, exaggerated proportions, [8+ details]",
      "realistic": "photorealistic [пол] [build], [тот же костюм], real skin textures, [живые детали], [эмоция]"
    },
    "environment_description": "[конкретная локация]",
    "style_tags": "cartoon chibi with bold black outlines, photorealistic human counterpart, dual-style side by side",
    "color_palette": "[одна палитра для обеих версий]",
    "lighting": "[единое освещение на все сцены]"
  },
  "scenes": [
    {
      "index": 1,
      "character_speech": null,
      "negative_prompt": "blur, distort, merged characters, single character, text overlay, watermark",
      "image_prompt": "[ENV], on the left a cartoon chibi [CHAR] with bold black outlines bright flat saturated colors [DETAILS], on the right a photorealistic human [MATCHING OUTFIT] real skin textures [DETAILS], both [ACTION], [LIGHTING], [CAMERA], vertical composition, 9:16 aspect ratio",
      "motion_prompt": "The cartoon [CHAR] on the left [EXAGGERATED ACTION]. The realistic [CHAR] on the right [GROUNDED MATCHING ACTION]."
    }
  ]
}
```

- `style_tags` обязаны включать **оба** стиля
- `lighting` / `color_palette` одинаковые во всех сценах
- `image_prompt` 40–80 слов, max 2 фокусные точки

---

## Game config требование

В `games/{GAME_TAG}/{GAME_TAG}.md` должны быть **ДВЕ** версии каждого персонажа:

```markdown
### Hero Name (cartoon)
`cartoon chibi [class] with bold black outlines, bright flat saturated colors, exaggerated proportions, [8+ details]`

### Hero Name (realistic counterpart)
`photorealistic [gender] [build], [same costume as cartoon], real skin textures, [skin/scars/dirt], [emotion]`
```

Если этих блоков нет — Manager должен флагом остановить до их добавления.

---

## Брифы ролям

### Scenarist
- 3 клипа × 5–10s; `character_speech: null` везде
- Cartoon и realistic маркеры обязательны в image_prompt (см. выше)
- Одинаковый костюм/поза/детали между версиями
- `motion_prompt` описывает действия **обоих** персонажей отдельно
- `negative_prompt`: `blur, distort, merged characters, single character, text overlay, watermark`
- Общие правила — `rules/roles/scenarist.md`

### Storyboarder
- Source ref: игровой ассет (screenshot / character_card) из `game_assets` Supabase или `games/{GAME_TAG}/assets/refs/`
- Если нет — сгенерируй cartoon-версию через NB2 как anchor
- **Мульти-персонаж:** каждый новый персонаж начинает chain заново (НЕ передавай сцену предыдущего персонажа)
- Для одного персонажа: scene 1 = `[asset]`; scene 2+ = `[asset, scene-(K-1)]`
- Общие правила — `rules/roles/storyboarder.md`

### Animator
- **Kling 2.6 Pro I2V**, `generate_audio: true` (SFX), `aspect_ratio: "9:16"`
- `duration`: "5" или "10"; без `end_image_url`
- `character_speech: null` → Kling не получает текст речи
- Одна модель на весь ролик
- Общие правила — `rules/roles/animator.md`

### Sound
- TTS **не нужен** (нет речи)
- Опциональная музыка: Kling SFX `volume=0.6`, music `volume=0.15`
- Субтитры не применяются
- Общие правила — `rules/roles/sound.md`

### Editor
- Scale 1080×1920, 30fps, concat с re-encode, hard cuts (без crossfade)
- Музыка через `amix`; **НИКОГДА `-shortest`**
- Общие правила — `rules/roles/editor.md`

---

## Выходные файлы

```
output/YYYY-MM-DD/{GAME_TAG}/dual-style/
├── storyboard.json
├── scenes/
│   ├── refs/character-ref.png
│   ├── scene-1/{scene-1.png, scene-1.mp4, scene-1-scaled.mp4}
│   ├── scene-2/...
│   └── scene-3/...
├── concat-list.txt
└── final.mp4
```

---

## Валидация

- [ ] Cartoon маркеры в image_prompt (`bold black outlines`, `bright flat saturated colors`, `exaggerated proportions`)
- [ ] Realistic маркеры в image_prompt (`photorealistic`, `real skin textures`)
- [ ] Костюм/поза/детали совпадают между версиями
- [ ] Cartoon и realistic на фиксированных сторонах (на всё видео)
- [ ] `character_speech: null` во всех клипах
- [ ] `camera_angle` разный для соседних клипов
- [ ] `style_tags` включают оба стиля; `lighting`/`color_palette` единые
- [ ] Для мульти-персонажа: chain reference не пересекается между разными персонажами
- [ ] `negative_prompt` заполнен
- [ ] Бюджет ≤$5

---

## Анти-паттерны

- ❌ «cartoon style» без конкретных маркеров (bold outlines, flat colors) — AI сделает semi-realistic
- ❌ Один промпт без `on the left / on the right` — AI объединит в одного персонажа
- ❌ Realistic без «живых» деталей (кожа, текстуры) — получится 3D рендер, не человек
- ❌ Chain reference между разными персонажами — ломает внешность
- ❌ Попытка выровнять cartoon и realistic по высоте — пусть chibi будет меньше
- ❌ `character_speech ≠ null` (Kling I2V не генерит голос)
- ❌ `-shortest` в ffmpeg
