# Формат "Новости игры" (Game News)

Новостной выпуск: игровой персонаж ведёт новости из тематической студии, второй персонаж — репортёр с места событий.

Этот файл — **playbook**: когда использовать, концепт, брифы каждой роли. Крафтовые правила — в `rules/roles/*.md`.

---

## Когда использовать

Ключевые слова: «новости», «news», «game news», «weekly news», «patch recap», «обновление», «что нового».

---

## Концепт

- **Ведущий (anchor):** игровой персонаж за новостным столом в тематической студии
- **Репортёр (field reporter):** другой игровой персонаж с микрофоном на игровой локации
- **3 новости** за выпуск
- **Все сцены со звуком и речью** → `character_speech` ≠ null → **Veo3 T2V** (обязательно, генерирует голос + липсинк)
- **Длительность:** ~27s (3s title + 24s новости)
- **Бюджет:** до $10 (Veo3 с аудио = $0.40/с × 24s = $9.60)

---

## Structure (4 элемента, фиксировано)

| Сцена | Роль | Локация | Длит. | Модель |
|---|---|---|---|---|
| 0 | **Title Card** | — | 3s | Image + Ken Burns |
| 1 | **Anchor** — приветствие + новость #1 | Студия | 8s | Veo3 T2V |
| 2 | **Field Reporter** — новость #2 (с места событий) | Игровая локация | 8s | Veo3 T2V |
| 3 | **Anchor** — новость #3 + прощание | Студия | 8s | Veo3 T2V |

### Скрипты (шаблоны)

- **Сцена 1:** `"Welcome to [Show]! I'm [name]. Big news — [новость #1 в 15-18 слов]!"`
- **Сцена 2:** `"Thanks [anchor]! I'm here at [location] where [новость #2 в 15-18 слов]!"`
- **Сцена 3:** `"[Новость #3 в 12-15 слов]. That's all for this week — like and subscribe!"`

**Max 20-25 слов на сцену** (должно уместиться в 8s).

---

## Фаза исследования (до storyboard)

Manager выполняет Research ДО Scenarist-а:

### Шаг 1. Поиск новостей
Веб-поиск по 3 запросам:
1. `"{game_name}" patch notes {month} {year}`
2. `"{game_name}" update news {month} {year}`
3. `"{game_name}" new hero OR new character OR event {year}`

Приоритет источников: официальные патч-ноты → официальные соцсети → крупные игровые медиа → сообщества.

### Шаг 2. Отбор 3 новостей
- Актуальность (7–14 дней)
- Значимость (влияет на игру)
- Разнообразие (не 3 нерфа подряд)

Fallback: если <3 реальных новостей — community highlight (популярный клип, мем, мета-сдвиг).

### Шаг 3. research.json

```json
{
  "game_tag": "MLBB",
  "research_date": "2026-03-24",
  "news_items": [
    {"index": 1, "headline": "Aurora Rework в патче 1.9.12", "summary": "...", "source_url": "https://...", "type": "patch"},
    {"index": 2, "headline": "Новая jungle карта для рангов", "summary": "...", "source_url": "https://...", "type": "update"},
    {"index": 3, "headline": "Призовой фонд Mythic Tournament x2", "summary": "...", "source_url": "https://...", "type": "event"}
  ],
  "sources_consulted": ["url1", "url2", "url3"]
}
```

Сохраняется в `OUTPUT_DIR/research.json` и передаётся Scenarist-у.

---

## Storyboard extensions

Стандартная структура + поля:

```json
{
  "format": "news",
  "show_name": "MLBB News Flash",
  "research": {"file": "research.json", "news_items": [...]},
  "visual_identity": {
    "characters": {
      "anchor": {"name": "Lancelot", "character_description": "..."},
      "field_reporter": {"name": "Fanny", "character_description": "..."}
    },
    "environments": {
      "studio": "modern gaming news studio with holographic screen behind desk showing MLBB logo, purple and blue neon lighting, sleek black desk...",
      "field_location": "newly redesigned jungle map at golden hour, towering ancient trees..."
    }
  },
  "scenes": [
    {"index": 1, "role": "anchor", "news_item_index": 1, ...},
    {"index": 2, "role": "field_reporter", "news_item_index": 2, ...},
    {"index": 3, "role": "anchor", "news_item_index": 3, ...}
  ]
}
```

Поля сцены: `role` (`anchor` / `field_reporter`), `news_item_index`.

---

## Брифы ролям

### Scenarist
- 4 фиксированных сцены (title + 3 новости); ≤20-25 слов на сцену
- Тон — энергичный новостной ведущий; использовать Tone of Voice из game config
- Обязательно `motion_prompt` формата `[действие] and says: "[реплика]"` — Veo3 понимает этот pattern
- `character_speech` ≠ null для всех сцен
- camera_angle разный для соседних сцен
- Общие правила — `rules/roles/scenarist.md`

### Storyboarder
- Стиль: тематика игры (из `games/{GAME_TAG}/{GAME_TAG}.md` → News Format → Studio Description)
- Студия: новостной стол, экран/баннер с логотипом игры, освещение
- Field location: активное окружение (частицы, движение), соответствует содержанию новости #2
- Title card — одно изображение 9:16 с логотипом шоу
- Общие правила — `rules/roles/storyboarder.md`

### Animator
- **Veo3 T2V** (`fal-ai/veo3`) — единственная модель для news. $0.20–0.40/с, 8s клип = $1.60–3.20
- НЕ Kling I2V (нужна речь + липсинк + рот-в-рот от T2V)
- `generate_audio: true` (Veo3 генерирует голос)
- motion_prompt обязателен с точным текстом реплики: `[действие] and says: "[реплика]"`
- Base path polling: смотри `tools/fal-ai.md`
- Общие правила — `rules/roles/animator.md`

### Sound
- Speech генерируется Veo3 напрямую — ElevenLabs TTS **не нужен**
- Фоновая музыка: опционально, новостной/energetic beat, `volume=0.15`
- Субтитры: не обязательны для news (разборчивая Veo3 речь); если нужны — drawtext SRT
- Общие правила — `rules/roles/sound.md`

### Editor
- Title card: 3s Ken Burns (slow zoom или pan на статичном PNG)
- Concat 4 клипов с re-encode, fps 30, AAC 128k
- Общие правила — `rules/roles/editor.md`

---

## Выходные файлы

```
output/YYYY-MM-DD/{GAME_TAG}/news/
├── research.json
├── storyboard.json
├── scenes/
│   ├── title-card.png
│   ├── scene-1/scene-1.mp4 (Veo3 anchor)
│   ├── scene-2/scene-2.mp4 (Veo3 field)
│   └── scene-3/scene-3.mp4 (Veo3 anchor)
└── final.mp4
```

---

## Валидация

- [ ] `research.json` с 3 новостями и источниками
- [ ] 4 сцены (title + 3 Veo3)
- [ ] Все motion_prompts включают точный текст реплики в формате `[действие] and says: "[реплика]"`
- [ ] Длительности: 3s + 3×8s = 27s; бюджет < $10
- [ ] `character_speech` ≠ null в сценах 1–3
- [ ] camera_angle разный для соседних сцен
- [ ] Студия и field location соответствуют Tone of Voice и стилю игры
