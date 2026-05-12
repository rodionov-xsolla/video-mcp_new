# Формат «Новости игры» (Game News)

> **Единственная модель для видео — Kling Avatar v2 Standard.** Никаких других видео-моделей. Opener и CTA — готовые из Supabase. Персонажи — из Supabase `game_assets`.

Этот файл — **playbook**: когда использовать, пайплайн, брифы ролям. Крафтовые правила — в `rules/roles/*.md`.

---

## Когда использовать

Ключевые слова: «новости», «news», «game news», «weekly news», «patch recap», «обновление», «что нового».

---

## Концепт

- **Anchor + Co-anchor** — два игровых персонажа за новостным столом
- **2–3 новости** за выпуск (минимум 2, найденные через веб-поиск)
- **Только Kling Avatar v2 Standard** + ElevenLabs TTS (lipsync через audio_url)
- **Opener и CTA — готовые видео из Supabase**, не генерируются заново
- **Длительность:** 25–40s после speedup (без opener/CTA)
- **Бюджет:** до $4 (~$2.50 типичный)

---

## Пайплайн (строгий порядок)

### Фаза 0: Инициализация

1. Прочитать game config: `games/{GAME_TAG}/{GAME_TAG}.md`
2. **Запросить ассеты из Supabase** — таблица `game_assets`, фильтр `game_tag = "{GAME_TAG}"`:

```bash
curl -s -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  "${SUPABASE_URL}/rest/v1/game_assets?game_tag=eq.{GAME_TAG}&select=*"
```

Из результата найти:
   - **Opener** — запись с тегом `opener` и `video` → скачать **`.mp4` видео** (не картинку!)
   - **CTA** — запись с тегом `cta` → скачать `.mp4`
   - **Avatar refs** — записи с тегом `news` и словом `avatar` в `character_name` → скачать `.png`
3. Если opener или CTA не найдены — **СТОП**, сообщить пользователю
4. Если avatar refs для anchor/co-anchor не найдены — **СТОП**, сообщить пользователю (персонажи должны быть заранее загружены в Supabase)

### Фаза 1: Исследование новостей

Веб-поиск **ДО** написания сценария.

**Шаг 1.** Три запроса:
1. `"{game_name}" patch notes {month} {year}`
2. `"{game_name}" update news {month} {year}`
3. `"{game_name}" new hero OR new character OR event {year}`

Приоритет: официальные патч-ноты → офиц. соцсети → крупные игровые медиа → сообщества.

**Шаг 2.** Отбор 2–3 новостей:
- Актуальность (7–14 дней)
- Значимость (влияет на игру)
- Разнообразие (не 3 нерфа подряд)

Fallback: если <2 реальных новостей — community highlight (мем, мета-сдвиг, рекорд).

**Шаг 3.** Сохранить `research.json`:

```json
{
  "game_tag": "roblox",
  "research_date": "2026-04-30",
  "news_items": [
    {"index": 1, "headline": "...", "summary": "...", "source_url": "https://...", "type": "event"},
    {"index": 2, "headline": "...", "summary": "...", "source_url": "https://...", "type": "update"}
  ],
  "sources_consulted": ["url1", "url2", "url3"]
}
```

### Фаза 2: Персонажи

**Anchor и co-anchor берутся из Supabase `game_assets`.** Использовать URL из Фазы 0.

**Репортёр «по теме»:** если новость требует тематического персонажа (например, пират для пиратского ивента), допускается генерация нового:
1. **Character sheet** (NB2 text-to-image, 16:9) — concept art
2. **Avatar ref** (NB2 edit с sheet как ref, 9:16) — портрет за столом, зубы видны для lipsync
3. Загрузить оба в Supabase через `queue/upload-asset.sh` с тегами `news,avatar`
4. В следующих выпусках этот персонаж уже будет в Supabase

### Фаза 3: Сценарий → `storyboard.json`

Структура — **ровно 3 dialogue-сцены** (без title card — opener берётся готовый):

| Сцена | Роль | Камера | Содержание |
|-------|------|--------|------------|
| 1 | **Anchor** | Фронтально, medium close-up | Приветствие + новость #1 + передача co-anchor |
| 2 | **Co-anchor** | Три-четверти, medium close-up | Новость #2 + реакция |
| 3 | **Anchor** | Чуть шире сцены 1 | Благодарность + прощание + CTA |

При 3 новостях — 4 сцены (anchor ведёт #1 и #3, co-anchor — #2).

**Скрипты:**
- **Сцена 1:** `"Welcome to [Show]! [Новость #1 подробно, 25-35 слов]. [Имя co-anchor], what do you have?"`
- **Сцена 2:** `"Thanks [anchor]! [Новость #2 подробно, 25-35 слов]. [Реакция/оценка]."`
- **Сцена 3:** `"[Благодарность]. That's [Show] for today. Follow for more, see you next time!"` (15–20 слов)

**Передача слова — обязательно по имени.** Ведущие обращаются друг к другу как в реальном выпуске новостей:
- Anchor → Co-anchor: `"Sarah, what do you have?"` / `"Over to you, Sarah!"` / `"Sarah, tell us more"`
- Co-anchor → Anchor: `"Thanks Jake!"` / `"Back to you, Jake"` 
- Anchor → Репортёр (если есть): `"Let's check in with [имя]"` / `"[Имя], what's the latest?"`
- Репортёр → Anchor: `"Thanks [anchor]!"` / `"Back to you, [anchor]"`

Это создаёт ощущение живого эфира и связывает сцены. Каждая передача слова содержит **имя** следующего/предыдущего ведущего.

Тон — из game config (Tone of Voice). Каждая dialogue-сцена обязана иметь поле `tts` с текстом для ElevenLabs.

### Фаза 4: Анимация (только Kling Avatar v2)

Для каждой dialogue-сцены:
1. **ElevenLabs TTS** → `.mp3` → загрузить в Supabase
2. **Kling Avatar v2** с параметрами:
   - `image_url` = avatar ref из Supabase (9:16, не квадрат!)
   - `audio_url` = TTS mp3 из Supabase (не fal.ai temp URL!)
   - `motion_prompt` = broadcaster energy, hand gestures, head turns
   - `negative_prompt` обязателен (anti-text набор — avatar ref содержит текст на экране)
3. **1.18x speedup** после генерации:

```bash
$FFMPEG -y -i avatar.mp4 \
  -filter_complex "[0:v]setpts=PTS/1.18[v];[0:a]atempo=1.18[a]" \
  -map "[v]" -map "[a]" \
  -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  avatar-fast.mp4
```

1.18x для news — чётко и разборчиво, не торопливо. Не 1.3x.

### Фаза 5: Сборка (FFmpeg)

Строгий порядок:

1. **Субтитры** — наложить per-scene на каждый `-fast.mp4` (НЕ на concat! whisper пропускает голоса при concat)
2. **Нормализация** всех клипов: 1080×1920, 30fps, AAC 128k
3. **Opener** — нормализовать скачанный из Supabase `.mp4` (тот же scale/fps/codec)
4. **Concat:** opener → scene-1-sub → scene-2-sub → scene-3-sub
5. **Музыка:** fun/energetic beat, `volume=0.10`
6. **Fade-to-black:** последние 1.5s
7. **CTA:** concat с нормализованным CTA из Supabase
8. → `final.mp4`

---

## Голоса

| Роль | Голос (ElevenLabs) | stability |
|------|--------------------|-----------|
| Anchor (мужской) | George или Daniel | 0.25 |
| Co-anchor (женский) | Charlotte или Rachel | 0.25 |

`stability: 0.25` = energetic broadcaster tone. Использовать `voice` (имя строкой), не `voice_id` хеш.

---

## Storyboard JSON (шаблон)

```json
{
  "format": "news",
  "show_name": "{Game} News Flash",
  "research": {"file": "research.json", "news_items": [...]},
  "visual_identity": {
    "characters": {
      "anchor": {"name": "...", "character_description": "..."},
      "co_anchor": {"name": "...", "character_description": "..."}
    },
    "environments": {
      "studio": "..."
    }
  },
  "voices": {
    "anchor": {"voice": "George", "stability": 0.25, "language_code": "en"},
    "co_anchor": {"voice": "Charlotte", "stability": 0.25, "language_code": "en"}
  },
  "scenes": [
    {"index": 1, "role": "anchor", "clip_type": "dialogue", "news_item_index": 1, "tts": "..."},
    {"index": 2, "role": "co_anchor", "clip_type": "dialogue", "news_item_index": 2, "tts": "..."},
    {"index": 3, "role": "anchor", "clip_type": "dialogue", "tts": "..."}
  ]
}
```

---

## Бюджет

| Статья | Стоимость |
|--------|-----------|
| Opener (из Supabase) | $0 |
| CTA (из Supabase) | $0 |
| Avatar refs (из Supabase) | $0 |
| Новый репортёр «по теме» (sheet + ref, если нужен) | ~$0.12 |
| ElevenLabs TTS (~25-35s) | ~$0.20 |
| Kling Avatar v2 (3 сцены, ~25-35s raw) | ~$1.40–2.00 |
| **Типичный** | **~$1.60–2.20** |

**Лимит: $4.00.** Остановись если расход > $3.50.

---

## Выходные файлы

```
output/YYYY-MM-DD/{GAME_TAG}/news/
├── research.json
├── storyboard.json
├── scenes/
│   ├── scene-1/
│   │   ├── scene-1.mp3           # TTS
│   │   ├── scene-1.mp4           # Kling Avatar raw
│   │   ├── scene-1-fast.mp4      # 1.18x speedup
│   │   └── scene-1-sub.mp4       # с субтитрами
│   ├── scene-2/...
│   └── scene-3/...
└── final.mp4
```

---

## Брифы ролям

### Scenarist
- 3 dialogue-сцены (opener/CTA — готовые, не в storyboard)
- 25–35 слов на основные сцены, 15–20 на outro
- Тон — из game config Tone of Voice
- Передача слова: "Sarah, what do you have?" → "Thanks Jake!"
- camera_angle разный для соседних сцен
- Общие правила — `rules/roles/scenarist.md`

### Storyboarder
- Anchor/co-anchor берутся из Supabase — не генерировать
- Тематический репортёр (если нужен) — сгенерировать sheet + avatar ref, загрузить в Supabase
- Общие правила — `rules/roles/storyboarder.md`

### Animator
- **ТОЛЬКО Kling Avatar v2 Standard**
- `audio_url` и `image_url` — Supabase permanent URLs
- `negative_prompt` обязателен
- 1.18x speedup после генерации
- Общие правила — `rules/roles/animator.md`

### Sound
- ElevenLabs TTS для каждой dialogue-сцены
- Субтитры per-scene (не на concat)
- Музыка: energetic/fun, `volume=0.10`
- Общие правила — `rules/roles/sound.md`

### Editor
- Скачать opener + CTA из Supabase, нормализовать
- Субтитры per-scene → нормализация → concat с opener → музыка → fade → CTA
- Общие правила — `rules/roles/editor.md`

---

## Валидация

- [ ] `research.json` с 2–3 новостями и источниками
- [ ] Avatar refs для обоих персонажей из Supabase
- [ ] Opener и CTA скачаны из Supabase (не сгенерированы)
- [ ] Все dialogue-сцены — Kling Avatar v2, ничего другого
- [ ] `negative_prompt` на всех Avatar генерациях
- [ ] 1.18x speedup на всех Avatar клипах
- [ ] Субтитры per-scene (не на concat)
- [ ] camera_angle разный для соседних сцен
- [ ] Финал: 1080×1920, 30fps, 25–40s (без opener/CTA), бюджет < $4

---

## ЗАПРЕЩЕНО

- Любые видео-модели кроме Kling Avatar v2 Standard
- Генерация opener/CTA — берутся готовые из Supabase
- Перегенерация существующих персонажей — anchor/co-anchor берутся из Supabase `game_assets`
- Субтитры на склеенном видео — whisper пропускает голоса при concat
- 1.3x speedup — слишком быстро, только 1.18x
- fal.ai temp URLs для Kling — только Supabase permanent URLs
- `voice_id` хеш — использовать `voice` имя строкой
- Один avatar ref на двоих — каждый персонаж = свой ref
