# Video Production Pipeline

AI pipeline для коротких вертикальных видео (1080×1920) для игровых каналов через fal.ai + FFmpeg + Supabase + ElevenLabs. Стек: `providers.json`, API детали — `tools/`.

## Порядок запуска

1. **`git pull origin main`** — первым делом. Репозиторий командный, правила обновляются другими агентами. При конфликте — остановись и сообщи пользователю, не разрешай автоматически.
2. **Прочитай `rules/roles/manager.md`** — как оркестрировать пайплайн (детект формата, последовательность фаз, контракты между ролями, Supabase, git push после эпизода).
3. **Определи формат** по запросу пользователя → прочитай `rules/formats/{format}.md` (playbook этого формата, брифы ролям).
4. **При переключении на фазу читай соответствующий role-файл ЦЕЛИКОМ прямо перед началом работы по этой фазе** — не скопом все в начале, а каждый в момент входа в фазу:
   - Сценарий → `rules/roles/scenarist.md`
   - Изображения → `rules/roles/storyboarder.md`
   - Анимация (Kling I2V/Avatar) → `rules/roles/animator.md`
   - Аудио (TTS, субтитры) → `rules/roles/sound.md`
   - Сборка (FFmpeg) → `rules/roles/editor.md`

## Универсальные принципы

- **Никогда не генерируй визуал без готового `storyboard.json`.** Сначала сценарий, потом картинки.
- **Никогда из памяти — всегда читай актуальные rule-файлы при каждом запуске.** Правила меняются, память врёт.
- **Context7 перед вызовом любого внешнего API:** `resolve-library-id` → `get-library-docs`. Параметры fal.ai/ElevenLabs/Kling регулярно обновляются. Детали — в `manager.md`.
- **Отладочный режим** — если в запросе есть фраза «Отладочный режим», работай пошагово с согласованием после каждой фазы. Что останавливать и какое пояснение прикладывать — в `manager.md`.

## Карта файлов

```
rules/
├── roles/                     ← крафт специалистов (format-agnostic)
│   ├── manager.md             — оркестрация
│   ├── scenarist.md           — сценарий (storyboard.json)
│   ├── storyboarder.md        — NB2 изображения
│   ├── animator.md            — Kling I2V/Avatar видео
│   ├── sound.md               — ElevenLabs TTS, субтитры
│   └── editor.md              — FFmpeg сборка
├── formats/                   ← playbook-и форматов (брифы ролям)
│   └── {serial-drama, gameplay-ai-avatar, news, standard,
│       reddit-story, dance-battle, object-character, dual-style}.md
└── main/
    ├── budgets.md             — прайсинг моделей
    └── fallback.md            — обработка ошибок

tools/                         ← API reference (fal-ai, ffmpeg)
games/                         ← per-game конфиги и story bibles
providers.json                 ← активные провайдеры/модели
queue/                         ← очередь задач (Supabase video_tasks)
legacy/                        ← снимки старых rule-файлов (фолбэк, не использовать)
```
