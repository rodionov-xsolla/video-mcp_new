# Validation Policy

Центральная политика валидации сгенерированных бинарных ассетов (PNG/MP4/MP3). Применяется всеми ролями (Storyboarder, Animator, Editor).

## Default: Programmatic only — НЕ читай бинарники

**По умолчанию НЕ используй Read tool для PNG/MP4/MP3.** Каждый Read бинарника тратит vision-токены, которые дорого стоят и раздувают контекст.

Валидация выполняется через bash:

### Для PNG (изображений)
```bash
# Файл скачался
[ -s "scene-1.png" ] && [ $(stat -f%z scene-1.png) -gt 1000 ]

# Размеры корректные (1080×1920 для вертикали)
identify -format "%wx%h" scene-1.png   # → "1080x1920"
# или через ffprobe
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 scene-1.png
```

### Для MP4 (видео)
```bash
# Файл скачался (Kling возвращает <1KB JSON при ошибке)
[ -s "scene-1.mp4" ] && [ $(stat -f%z scene-1.mp4) -gt 100000 ]

# Длительность близка к ожидаемой (±0.1s)
ffprobe -v error -show_entries format=duration -of csv=p=0 scene-1.mp4

# Есть видеопоток
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of csv=p=0 scene-1.mp4
```

### Для MP3 (аудио)
```bash
[ -s "scene-1.mp3" ] && [ $(stat -f%z scene-1.mp3) -gt 1000 ]

# Длительность
ffprobe -v error -show_entries format=duration -of csv=p=0 scene-1.mp3
```

## Visual validation: opt-in per format

Visual validation (Read tool на бинарник) включается **ТОЛЬКО** если в format playbook явно указано:

```yaml
visual_validation: required        # Полная visual проверка всех ассетов
visual_validation: first-scene     # Только первая сцена + character refs
```

**Default (если поля нет): visual_validation: off** — Read бинарников запрещён.

### Текущие форматы

Все default форматы — `visual_validation: off`. Если формат требует визуальной работы с кадрами как часть **генерации** (например, motion-dance анализирует кадры реф-видео в Phase 0 — это часть pipeline, не пост-валидация), это описано в самом format playbook и НЕ относится к этой политике.

Эта политика регулирует только **пост-генерационную проверку** результатов NB2/Kling/FFmpeg.

## Что заменяет визуальная проверка

Раньше agent читал PNG глазами и проверял 9 пунктов (storyboarder.md секция 19):
- Персонаж = тот, кого заказывали
- Стиль единый
- Количество фигур = запрошенному
- Композиция start ≈ end (для I2V)
- Нет лишних персонажей
- Пропорции в constrained frames
- Рот корректный для lipsync
- Фон совпадает с bg-ref
- Нет цветовых артефактов на коже

**Текущий подход:** эти проверки выполняются на уровне **prompt engineering**, не post-hoc валидации:
- Чёткий character_description (8+ деталей) в JSON
- Стабильные `image_urls` для chain reference
- Negative prompts против артефактов
- Constraint frames для пропорций
- Программная проверка filesize/dimensions

Если NB2 даёт мусор — это уже видно в финальном видео, ловится на этапе ревью контента (вне pipeline).

## Когда включать visual_validation в формат

Включай только если:
1. Формат имеет уникальные визуальные требования (танец, поза, специфический объект)
2. Стоимость "брака на финальном видео" выше чем стоимость vision-токенов
3. Программная валидация принципиально не покрывает требование

В остальных случаях — оставляй default (off).
