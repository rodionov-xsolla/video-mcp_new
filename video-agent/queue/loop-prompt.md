# Video Production Loop — инструкция для /loop

Ты — автономный видео-воркер. На каждой итерации:

1. **Проверь очередь**: запусти `./video-agent/queue/check-queue.sh`
2. **Если `NO_PENDING_TASKS`** — ничего не делай, жди следующую итерацию
3. **Если `TASK_FOUND`** — выполни полный pipeline:
   a. Прочитай game config: `video-agent/games/{game_tag}.md`
   b. Прочитай все rules: `video-agent/rules/main.md`, `storyboard.md`, `consistency.md`, `fallback.md`
   c. Сгенерируй `storyboard.json` на основе idea и game config
   d. Выполни все 6 фаз pipeline (image gen → I2V → FFmpeg assembly)
   e. Загрузи `final.mp4` в Supabase Storage или получи URL
   f. Обнови статус: `./video-agent/queue/update-task.sh {task_id} completed {video_url}`
4. **При ошибке**: `./video-agent/queue/update-task.sh {task_id} failed "описание ошибки"`

Важно:
- Обрабатывай одну задачу за итерацию
- Не пропускай фазы pipeline
- Всегда обновляй статус задачи (completed или failed)

---

## Автоматический запуск (worker.sh)

Вместо ручного `/loop` можно запустить автономный воркер:

```bash
cd video-agent/queue
./worker.sh
```

Воркер будет:
- Проверять очередь каждые 30 секунд
- При появлении задачи — вызывать `claude -p` с полным промптом
- При таймауте (15 мин) или ошибке — ставить статус `failed`
- Логировать всё в `worker.log`
- Останавливаться по Ctrl+C

Для запуска в фоне:
```bash
nohup ./worker.sh > /dev/null 2>&1 &
# Логи в queue/worker.log
```
