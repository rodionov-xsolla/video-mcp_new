# Формат "Standard" — универсальный I2V

Универсальный формат-по-умолчанию: экшен, стендап, гайды, рейтинги, трейлеры. Выбирается, когда идея не подходит под специализированные форматы.

Этот файл — **playbook**. Крафтовые правила (motion_prompt style, NB2 chain, ffmpeg пайплайн) — в `rules/roles/*.md`.

---

## Когда использовать

Ключевые слова: любые, **кроме** «news», «serial/сериал», «object character», «dual-style», «gameplay ai avatar / offerwall», «dance battle», «reddit story», «character story».

Типичные кейсы: экшен-сцены, стендап-шутки, топ-N рейтинги, гайды, атмосферные трейлеры.

---

## Концепт

- **3 клипа × 5–10s** → 15–30s total (4 клипа — только если каждый содержит уникальное действие)
- **Модель: Kling I2V** (v3 Standard или 2.6 Pro fallback) — `generate_audio: true` (SFX)
- **Речь:** `character_speech: null` во всех сценах — голос через TTS overlay, если нужен
- **Одна модель на весь ролик**
- **Бюджет:** $5

---

## Structure (по умолчанию)

| Клип | Beat | Длит. | camera_angle |
|---|---|---|---|
| 1 | hook | 5s | close-up / medium close-up |
| 2 | development | 10s | medium / wide |
| 3 | climax + CTA overlay | 5–10s | low angle / dynamic |

- CTA — из Supabase `game_assets` (тег `cta`), нормализованный, в concat-list как последний клип
- camera_angle **разный** для соседних клипов (обязательно)
- 4-й клип — только если каждый из 4 несёт уникальное действие

---

## Storyboard extensions

```json
{
  "format": "standard",
  "visual_identity": {
    "character_description": "8+ визуальных деталей (кожа, шрамы, одежда, оружие)",
    "environment_description": "конкретная локация из игры",
    "style_tags": "из game config prompt_prefix",
    "color_palette": "из game config",
    "lighting": "из game config"
  },
  "scenes": [
    {"index": 1, "beats": ["hook"], "duration_sec": 5, "camera_angle": "close-up", ...}
  ]
}
```

Общие поля сцены (camera_angle, character_state, facial_expression, gaze_direction, character_speech, motion_prompt) — в `rules/roles/scenarist.md`.

---

## Брифы ролям

### Scenarist
- 3 клипа × 5–10s; 4 только при полной загрузке уникальным действием
- Narrative arc: hook → development → climax
- `character_speech: null` во всех сценах
- Минимум 2 РАЗНЫХ действия в каждом motion_prompt (не зацикленное)
- `character_state` / `camera_angle` меняются между сценами; `character_description` дословно одинаковый
- Общие правила — `rules/roles/scenarist.md`

### Storyboarder
- Anchor ref + chain по предыдущей сцене (max 2 refs)
- Стиль — из `games/{GAME_TAG}/{GAME_TAG}.md` (prompt_prefix, palette, lighting)
- Персонажи из Supabase `game_assets` — если есть, переиспользуй ref
- Общие правила — `rules/roles/storyboarder.md`

### Animator
- **Kling I2V** (v3 Standard primary, 2.6 Pro fallback): `generate_audio: true` (SFX), микро-движения, start≈end
- Polling base path = первые 2 сегмента endpoint
- Общие правила — `rules/roles/animator.md`

### Sound
- TTS overlay (ElevenLabs через fal.ai), если нужен голос поверх видео
- Фоновая музыка опционально (volume=0.15)
- Субтитры диалогов — опционально; title/brainrot оверлеи запрещены
- Общие правила — `rules/roles/sound.md`

### Editor
- Scale каждую сцену в 1080×1920, fps=30, `-preset slow -crf 20`
- Concat с re-encode (`libx264`), NOT `-c copy`; hard cuts, НЕТ crossfade
- CTA из Supabase, нормализовать, в concat-list последним клипом
- Музыка через `amix`; **НИКОГДА `-shortest`** — используй `apad`
- Общие правила — `rules/roles/editor.md`

---

## Выходные файлы

```
output/YYYY-MM-DD/{GAME_TAG}/standard/
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

- [ ] `format: "standard"`
- [ ] `character_speech: null` во всех сценах — Kling I2V, не T2V
- [ ] 3 клипа (или 4 с обоснованием каждого)
- [ ] `camera_angle` разный для соседних клипов
- [ ] `motion_prompt` ≥2 разных действия
- [ ] `visual_identity.character_description` ≥8 визуальных деталей
- [ ] `gaze_direction` при 2+ персонажах в кадре
- [ ] CTA из Supabase `game_assets`
- [ ] Бюджет ≤$5
- [ ] `final.mp4` 1080×1920, 30fps; hard cuts; нет `-shortest`

---

## ЗАПРЕЩЕНО

- Любые T2V модели (дорого, нет контроля)
- `character_speech ≠ null` — голос только через TTS overlay
- `-shortest` в ffmpeg
- Генерация CTA — берётся из Supabase
