# Legacy

Снимки старых rule-файлов до реструктуризации в роли (`rules/roles/`).

**Не используются активной работой агента.** Лежат как фолбэк на случай отката.

## Что внутри

- `CLAUDE.md` — старый монолитный entry point (233 строки, всё в одном)
- `rules/main/workflow.md` — старый 6-фазный pipeline (один Claude делал всё)
- `rules/main/storyboard.md` — старая инструкция по сторибоарду (визуал + нарратив + пейсинг в одном)
- `rules/formats/*.md` — снимки 8 форматов ДО укорачивания до playbook (Этап 3): serial-drama (1231 строк), gameplay-ai-avatar (542), news, standard, reddit-story, dance-battle, object-character, dual-style

## Зачем

Распределение крафта по ролям — большая правка. Если новая структура не сработает или потеряет важные нюансы, эти файлы позволяют:
1. Точно сравнить «что было / что стало»
2. Откатить через `git mv` обратно в `rules/main/`

## Откат

```bash
git mv video-agent/legacy/CLAUDE.md video-agent/CLAUDE.md
git mv video-agent/legacy/rules/main/workflow.md video-agent/rules/main/workflow.md
git mv video-agent/legacy/rules/main/storyboard.md video-agent/rules/main/storyboard.md
# (для форматов — после Этапа 3)
```

После успешной приживаемости новой структуры эту папку можно удалить.
