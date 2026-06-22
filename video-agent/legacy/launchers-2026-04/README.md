# Old launchers (archived 2026-06-22)

- `run.sh` — оригинальная точка входа (монолитный Claude вызов через `claude -p`).
- `run-v2.sh` — переходник, делегировал в `pipeline.sh`.

Канонический запуск теперь только через `pipeline.sh` (он же используется `queue/worker.sh`).
