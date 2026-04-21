# Формат "Dance Battle" — комедийные танцевальные батлы

Два персонажа соревнуются в танцевальном батле на сцене. Контраст между усилием и абсурдом — главный источник юмора. Никакой речи, только SFX + музыка.

Этот файл — **playbook**. Крафтовые правила (NB2 chain, Kling I2V, ffmpeg) — в `rules/roles/*.md`.

---

## Когда использовать

Ключевые слова: «dance battle», «dance», «танцевальный батл», «танец», «dance off», «dance competition», «баттл танцев».

Идеально для серии: новые персонажи каждый выпуск, одна и та же сцена.

---

## Концепт

- **Два персонажа** — визуально различные (размер, стиль, энергия)
- **Кадр:** wide shot, low angle (~15°), оба танцора в кадре
- **Стиль:** реалистичный 3D render с комедийной стилизацией
- **Модель:** Kling 2.6 Pro I2V ($0.14/s), **`generate_audio: true`** (Kling генерирует толпу, музыку, SFX)
- **Речь:** НЕТ — `character_speech: null` во всех сценах
- **Длительность:** 3×5s (15s) или 2×10s (20s)
- **Бюджет:** $5 максимум (~$2.30–$3.00 типично)

---

## Structure

| Клип | Длит. | Камера | Действие | Комедия |
|---|---|---|---|---|
| 1. Вход | 5s | Wide low-angle, slow lateral L→R | Выход на сцену, стартовые позы, толпа | Контраст внешности |
| 2. Батл | 5–10s | Medium push-in к ведущему | Персонаж A выполняет приём, B реагирует | Серьёзное лицо + абсурд |
| 3. Финал | 5s | Wide pull-back | Финальные фриз-позы, толпа взрывается | Неожиданный финал |

`camera_angle` обязательно разный для соседних клипов.

---

## Locked Parameters (одинаковые во всех видео серии)

Включаются в каждый `image_prompt` и `motion_prompt`:

- **Камера:** Wide shot from low angle (~15°) at stage-edge level, both characters fully in frame
- **Локация:** Circular dance arena-stage in a large hall, polished dark wooden floor with reflections, low podium
- **Толпа:** Dense crowd of spectators — silhouettes and raised hands in soft bokeh, reactive movement
- **Освещение:** Two contrasting spotlights — warm orange left, cool blue right — central white beam, light haze
- **Атмосфера:** Micro dust in light cones, energetic, festive, competitive, comedic
- **Render:** Realistic 3D render, PBR materials, cinematic realism with subtle comedic stylization

---

## Variable Parameters (меняются между выпусками)

- **Персонажи** (8+ визуальных деталей каждый, визуально различны)
- **Стили танца** — breakdance / ballroom / hip-hop / folk / robot / ballet / salsa / moonwalk / floss / headbang
- **Эмоции** — dead-serious concentration / smug confidence / panicked effort / disgusted determination
- **Победитель** — левый / правый / оба
- **Источник комедии** — size mismatch / speed mismatch / style clash / wardrobe malfunction

---

## Storyboard extensions

```json
{
  "format": "dance-battle",
  "visual_identity": {
    "character_a": {"name": "...", "description": "8+ details", "dance_style": "ballet", "emotion": "smug confidence"},
    "character_b": {"name": "...", "description": "8+ details", "dance_style": "breakdance", "emotion": "dead-serious concentration"},
    "comedy_source": "size mismatch — elegant lean dancer vs massive Viking",
    "environment_description": "[locked]",
    "lighting": "[locked]",
    "style_tags": "[locked]"
  },
  "scenes": [
    {"index": 1, "character_speech": null, "negative_prompt": "blur, distort, extra limbs, merged bodies, split screen", ...}
  ]
}
```

### 4-Layer prompt structure (для Kling)
```
Layer 1 — Camera movement (как камера ведёт себя во времени)
Layer 2 — Subjects & action physics (кто + конкретная механика тела)
Layer 3 — Environment & lighting (где + настройка света)
Layer 4 — Texture & style (качество рендера + материалы)
```

`image_prompt` = 60–100 слов, `motion_prompt` = 40–60 слов. Максимум 3–5 основных идей — Kling теряет связность при перегрузке.

---

## Anti-Drift Layer (для серии)

При ≥2 выпусках подряд ротируй:
- **Стили танца** — не повторять в 5 подряд
- **Эмоции** — dead-serious / smug / panicked / surprised / disgusted
- **Победитель** — левый → правый → оба → …
- **Акцент камеры** — push-in слева → push-in справа → wide
- **Энергия толпы** — взрыв / шокированная тишина / смешанные реакции / build-up
- **Источник комедии** — size / speed / style / wardrobe / prop interaction

Если приём / финал камеры / комедийный механизм идентичен прошлому выпуску — заменить.

---

## Брифы ролям

### Scenarist
- 3 клипа (5/5-10/5) или 2×10s; `character_speech: null` везде
- 4-layer prompt structure; ≤3-5 ideas per prompt
- Конкретная механика тела: перенос веса, позиция рук, траектория — не «dancing»
- Каждое движение имеет чёткое конечное положение
- Один персонаж действует, второй реагирует (не оба одновременно)
- Comedy source очевиден без объяснения
- Общие правила — `rules/roles/scenarist.md`

### Storyboarder
- **Два character refs (A и B)** — генерируются отдельно, оба передаются в каждую сцену
- image_urls: `[ref-a, ref-b]` для scene 1; `[ref-a, ref-b, scene-(K-1)]` для 2+ (max 3 refs — watch ref duplication)
- Персонажи визуально РАЗЛИЧНЫ; 8+ деталей каждый
- Стиль одинаковый для обоих (realistic 3D render)
- Общие правила — `rules/roles/storyboarder.md`

### Animator
- **Kling 2.6 Pro I2V** с `generate_audio: true` (толпа + SFX генерируется моделью)
- ✅ перенос веса, наклоны, повороты корпуса, фриз-позы, медленные движения с чёткими конечными точками
- ⚠️ быстрые вращения, прыжки, splits — артефакты, использовать осторожно
- ❌ одновременные сложные движения обоих — один действует, другой статично реагирует
- `negative_prompt` обязателен: `blur, distort, extra limbs, merged bodies, split screen, duplicate characters`
- Общие правила — `rules/roles/animator.md`

### Sound
- TTS **не нужен** (нет речи)
- Опциональная музыка track поверх Kling SFX: Kling SFX `volume=0.6`, музыка `volume=0.25`
- Субтитры не применяются
- Общие правила — `rules/roles/sound.md`

### Editor
- Scale 1080×1920, 30fps, concat с re-encode, hard cuts (crossfade запрещён)
- Музыка через `amix`; **НИКОГДА `-shortest`**
- Общие правила — `rules/roles/editor.md`

---

## Banned terms (в промптах Kling)

```
nice background, good lighting, cool vibe, beautiful atmosphere
masterpiece, best quality, ultra detailed, 4K, 8K, trending on artstation
dynamic pose, dynamic scene, dynamic energy
various, several, multiple
energetic, lively, vibrant
dancing (описывай КОНКРЕТНОЕ движение)
```

---

## Выходные файлы

```
output/YYYY-MM-DD/{GAME_TAG}/dance-battle/
├── storyboard.json
├── scenes/
│   ├── refs/{character-ref-a.png, character-ref-b.png}
│   ├── scene-1/{scene-1.png, scene-1.mp4, scene-1-scaled.mp4}
│   ├── scene-2/...
│   └── scene-3/...
├── concat-list.txt
└── final.mp4
```

---

## Валидация

- [ ] `format: "dance-battle"`, `character_speech: null` во всех сценах
- [ ] `generate_audio: true` для всех Kling вызовов
- [ ] Два character refs сгенерированы, оба переданы в image_urls каждой сцены
- [ ] 8+ визуальных деталей на каждого персонажа; визуально различны
- [ ] 4-layer prompt structure; image_prompt 60–100 слов, motion_prompt 40–60 слов
- [ ] `camera_angle` разный для соседних клипов
- [ ] Конкретная механика движений (не «dancing»)
- [ ] `negative_prompt` заполнен
- [ ] Для серии: Anti-Drift проверен (стили/эмоции/финал не дублируют последний выпуск)
- [ ] Бюджет ≤$5

---

## Priority Hierarchy (при конфликте)

1. **Kling technical compliance** — 4-layer, word count, physics
2. **Character recognizability**
3. **Motion clarity**
4. **Comedic contrast**
5. **Camera coherence**
6. **Visual spectacle**
7. **Sound direction**
