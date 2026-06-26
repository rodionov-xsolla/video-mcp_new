# One-off Supabase storage migrations (May 2026)

Скрипты использовались разово при миграции `game_assets` и storage paths. Не запускать автоматически — каждый из них принимает уникальное состояние БД.

- `migrate-storage.py` + `migration-plan*.tsv` + `migration-apply.log` — план/исполнение rename'ов.
- `cleanup-category-a.py` — удаление устаревших ассетов категории A.
- `phase4/` — повторная итерация миграции БД-маппинга после storage-фазы.

Архивировано 2026-06-22.
