# Формат "Standard" — универсальный I2V / T2V

Универсальный формат-по-умолчанию: экшен, стендап, гайды, рейтинги, трейлеры. Выбирается, когда идея не подходит под специализированные форматы.

Этот файл — **playbook**. Крафтовые правила (motion_prompt style, NB2 chain, ffmpeg пайплайн) — в `rules/roles/*.md`.

---

## Когда использовать

Ключевые слова: любые, **кроме** «news», «serial/сериал», «object character», «dual-style», «gameplay ai avatar / offerwall», «dance battle», «reddit story».

Типичные кейсы: экшен-сцены, стендап-шутки, топ-N рейтинги, гайды, атмосферные трейлеры.

---

## Концепт

- **3 клипа × 5–10s** → 15–30s total (4 клипа — только если каждый содержит уникальное действие)
- **Модель зависит от речи:**
  - `character_speech` = null → **Kling 2.6 Pro I2V** ($0.14/s, микро-движения, SFX через `generate_audio: true`)
  - `character_speech` ≠ null → **Veo3 T2V** ($0.20–0.40/s, генерирует голос + липсинк)
- **Одна модель на весь ролик.** Не смешивай Kling + Veo3 (разная пластика/температура).
- **Бюджет:** $5 (I2V) / $10 (T2V)

---

## Подходы (approach)

| Тип контента | Approach | Цепочка |
|---|---|---|
| Экшен, стендап, комбо, гайды, топ-N | **Approach 2** | NB2 anchor → NB2 scene → Kling I2V / Veo3 T2V |
| Кинематограф, трейлер, атмосфера | **Approach 3** | Veo3 T2V напрямую (без image chain) |

По умолчанию — Approach 2. Если пользователь указал — используй его.

---

## Structure (по умолчанию)

| Клип | Beat | Длит. | camera_angle |
|---|---|---|---|
| 1 | hook | 5s | close-up / medium close-up |
| 2 | development | 10s | medium / wide |
| 3 | climax + CTA overlay | 5–10s | low angle / dynamic |

- CTA — оверлей на последнем клипе, не отдельная сцена.
- camera_angle **разный** для соседних клипов (обязательно).
- 4-й клип — только если каждый из 4 несёт уникальное действие.

---

## Storyboard extensions

```json
{
  "format": "standard",
  "approach": "2",
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
- Narrative arc: hook → development → climax + CTA overlay
- `character_speech` определяет модель анимации — зафикси ДО Storyboarder
- Минимум 2 РАЗНЫХ действия в каждом motion_prompt (не зацикленное)
- `character_state` / `camera_angle` меняются между сценами; `character_description` дословно одинаковый
- Общие правила — `rules/roles/scenarist.md`

### Storyboarder
- Approach 2: anchor ref + chain по предыдущей сцене (max 2 refs)
- Approach 3: визуал пропускается, Veo3 генерирует сам
- Стиль — из `games/{GAME_TAG}/{GAME_TAG}.md` (prompt_prefix, palette, lighting)
- Для lipsync-сцен: приоткрытый рот / лёгкая улыбка с зубами
- Общие правила — `rules/roles/storyboarder.md`

### Animator
- **Kling I2V** для сцен без речи: `generate_audio: true` (SFX), микро-движения, start≈end
- **Veo3 T2V** для сцен с речью: motion_prompt формата `[действие] and says: "[реплика]"`
- Одна модель на весь ролик — не миксуй I2V и T2V
- Polling base path = первые 2 сегмента endpoint
- Общие правила — `rules/roles/animator.md`

### Sound
- Если все сцены Kling I2V → фоновая музыка опционально (volume=0.15)
- Если Veo3 T2V → голос встроен в клип, ElevenLabs не нужен
- Субтитры диалогов — опционально; title/brainrot оверлеи запрещены
- Общие правила — `rules/roles/sound.md`

### Editor
- Scale каждую сцену в 1080×1920, fps=30, `-preset slow -crf 10`
- Concat с re-encode (`libx264`), NOT `-c copy`; hard cuts, НЕТ crossfade
- CTA overlay на последних 2–3s (curl + ffprobe валидация)
- Музыка через `amix`; **НИКОГДА `-shortest`** — используй `apad`
- Общие правила — `rules/roles/editor.md`

---

## Выходные файлы

```
output/YYYY-MM-DD/{GAME_TAG}/standard/
├── storyboard.json
├── scenes/
│   ├── refs/character-ref.png        (Approach 2)
│   ├── scene-1/{scene-1.png, scene-1.mp4, scene-1-scaled.mp4}
│   ├── scene-2/...
│   └── scene-3/...
├── concat-list.txt
└── final.mp4
```

---

## Валидация

- [ ] `format: "standard"`, `approach` = "2" или "3"
- [ ] `character_speech` null → Kling I2V; ≠ null → Veo3 T2V (одна модель на весь ролик)
- [ ] 3 клипа (или 4 с обоснованием каждого)
- [ ] `camera_angle` разный для соседних клипов
- [ ] `motion_prompt` ≥2 разных действия; Veo3 включает точный текст реплики
- [ ] `visual_identity.character_description` ≥8 визуальных деталей
- [ ] `gaze_direction` при 2+ персонажах в кадре
- [ ] Бюджет: $5 (I2V) / $10 (T2V)
- [ ] `final.mp4` 1080×1920, 30fps; hard cuts; нет `-shortest`
