# Формат "Motion Dance" — персонаж танцует под музыку через motion transfer с реф-видео

Одиночный персонаж (игровой скин, OC, мем) танцует под музыку. Движения берутся из реального танцевального видео через Kling Motion Control. Ключевая фишка — анализ реф-видео перед генерацией изображения, чтобы план и поза персонажа совпадали с референсом.

Этот файл — **playbook**: когда использовать, концепт, бюджет, брифы каждой роли.
Крафтовые правила — в `rules/roles/*.md`.

---

## Когда использовать

Ключевые слова: «motion dance», «motion control», «моушн», «motion transfer», «танцует под видео».

НЕ путать с Dance Battle (два персонажа батлятся через Kling I2V). Motion Dance = один персонаж + реальное реф-видео.

---

## Концепт

- **Жанр:** танцевальное видео с motion transfer
- **Стиль:** Game-specific (Roblox 3D, Pixar, Anime — определяется по игре)
- **Длительность:** 10–30s (определяется длиной реф-видео)
- **Клипов:** 1 (= 1 танец с одного реф-видео)
- **Бюджет:** до $3.00 на видео. Остановись если расход > $2.70.
- **Формат кадра:** 9:16 (1080×1920)

### Модели

- **Image:** Nano Banana 2 (персонаж + фон)
- **Video:** Kling Motion Control v2.6 Standard ($0.07/сек)
- **Audio:** `keep_original_sound: true` (музыка из реф-видео)

---

## Бюджет (ориентиры)

| Компонент | Стоимость |
|---|---|
| NB2 image (персонаж) | ~$0.08 |
| Kling Motion Control v2.6 10s | $0.70 |
| Kling Motion Control v2.6 15s | $1.05 |
| Kling Motion Control v2.6 20s | $1.40 |
| Kling Motion Control v2.6 30s | $2.10 |

| Вариант | Стоимость |
|---|---|
| Короткий танец (10s) | ~$0.78 |
| Средний танец (20s) | ~$1.48 |
| Длинный танец (30s) | ~$2.18 |

---

## Пайплайн

| Фаза | Действие | Кто |
|---|---|---|
| 0. Анализ реф-видео | Извлечь первый кадр + кадр из середины → определить план, ракурс, позу | Storyboarder |
| 1. Генерация изображения | NB2 — персонаж в том же плане/ракурсе что в реф-видео + фон | Storyboarder |
| 2. Загрузка в Supabase | image + video → постоянные URL | Animator |
| 3. Motion Control | Kling v2.6 Standard → танцующий персонаж | Animator |
| 4. Финализация | Скачать, проверить, опционально trim/scale | Editor |

### Фаза 0 — Анализ реф-видео (КРИТИЧНО)

Перед генерацией изображения персонажа **обязательно** извлеки кадры из реф-видео:

```bash
# Первый кадр
ffmpeg -i ref-video.mp4 -vframes 1 -q:v 2 ref-frame-first.jpg

# Кадр из середины
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 ref-video.mp4)
MIDPOINT=$(echo "$DURATION / 2" | bc -l)
ffmpeg -i ref-video.mp4 -ss $MIDPOINT -vframes 1 -q:v 2 ref-frame-mid.jpg
```

Проанализируй кадры:
- **План:** full body / upper body / medium shot?
- **Ракурс:** фронтальный / слегка сбоку / снизу?
- **Пропорции:** сколько кадра занимает человек?
- **Фон:** однотонный / сложный?

Эти данные определяют промпт для NB2 — персонаж должен быть в **том же плане и масштабе**, иначе motion transfer будет некорректным.

---

## Параметры Kling Motion Control

| Параметр | Значение | Пояснение |
|---|---|---|
| `image_url` | Supabase URL изображения | Постоянный URL, НЕ fal.media |
| `video_url` | Supabase URL реф-видео | Постоянный URL, НЕ fal.media |
| `character_orientation` | `"video"` | Движения из видео (макс 30с) |
| `keep_original_sound` | `true` | Сохраняем музыку из реф-видео |
| `prompt` | Краткое описание | "A cute Roblox girl dancing" |

### Polling

- Submit: `POST https://queue.fal.run/fal-ai/kling-video/v2.6/standard/motion-control`
- Polling base: `fal-ai/kling-video` (2-сегментный путь)
- Интервал: 15 секунд
- Таймаут: 10 минут

---

## Брифы ролям

### Scenarist
- SKIP — формат не использует storyboard.json. Вся "режиссура" — в реф-видео.
- Пользователь предоставляет: реф-видео + описание персонажа + описание фона.

### Storyboarder
- **Фаза 0 обязательна:** извлеки кадры из реф-видео, определи план/ракурс.
- Генерируй персонажа через NB2 в том же плане что в реф-видео.
- Если есть реф фона (карта из игры) — приложи как `image_urls` для консистентности.
- `image_urls`: `[bg-ref]` если есть фон-референс, иначе без `image_urls`.
- Персонаж: full body, чёткие пропорции, >5% площади кадра (требование Kling).
- Голова не должна быть закрыта (требование Motion Control).
- Общие правила — `rules/roles/storyboarder.md`

### Animator
- **Модель:** Kling Motion Control v2.6 Standard (`fal-ai/kling-video/v2.6/standard/motion-control`)
- **Перед генерацией:** загрузи image + video в Supabase (постоянные URL).
- `character_orientation: "video"` (движения из видео).
- `keep_original_sound: true` (музыка сохраняется).
- Длительность определяется реф-видео (макс 30с в video mode).
- Общие правила — `rules/roles/animator.md`

### Sound
- SKIP — звук берётся из реф-видео (`keep_original_sound: true`).
- TTS не нужен, субтитры не нужны.
- Общие правила — `rules/roles/sound.md`

### Editor
- Минимальная обработка: scale 1080×1920, 30fps если нужно.
- Опционально: trim начало/конец, fade out последние 1–2s.
- **НЕ** перекодировать аудио если `keep_original_sound: true`.
- Общие правила — `rules/roles/editor.md`

---

## Выходные файлы

```
output/YYYY-MM-DD_motion-test/
├── ref-frame-first.jpg       # Первый кадр реф-видео (анализ)
├── ref-frame-mid.jpg         # Средний кадр реф-видео (анализ)
├── character.png             # Сгенерированное изображение персонажа
├── dance-ref.mp4             # Реф-видео (оригинал)
└── final.mp4                 # Результат motion control
```

---

## Валидация перед публикацией

- [ ] Фаза 0 выполнена: кадры из реф-видео извлечены и проанализированы
- [ ] Персонаж в том же плане/масштабе что в реф-видео
- [ ] Персонаж занимает >5% кадра, голова не закрыта
- [ ] image + video загружены в Supabase (постоянные URL)
- [ ] `character_orientation: "video"`
- [ ] Реф-видео ≤30s
- [ ] Результат скачан, размер >10KB
- [ ] Бюджет ≤$3.00

---

## Анти-паттерны

- ❌ Генерировать изображение персонажа БЕЗ анализа реф-видео (план не совпадёт → кривой motion transfer)
- ❌ Передавать fal.media URL в `image_url` / `video_url` (протухнут)
- ❌ `character_orientation: "image"` для танцев (ограничение 10с, хуже для сложных движений)
- ❌ Реф-видео >30s (лимит Kling в video mode)
- ❌ Персонаж с закрытой головой (Kling не сможет трансферить мимику)
- ❌ `-shortest` в FFmpeg (универсальный анти-паттерн)
- ❌ Путать с Dance Battle (тот формат = два персонажа через Kling I2V, без motion transfer)
