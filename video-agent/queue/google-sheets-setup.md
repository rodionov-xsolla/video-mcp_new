# Google Sheets → Supabase интеграция

## 1. Создай Google Sheet

Структура листа **"Video Tasks"**:

| A: Game | B: Idea | C: Priority | D: Status | E: Video URL | F: Task ID |
|---------|---------|-------------|-----------|--------------|------------|
| Oxide   | Noob builds castle | 0 | pending | | |

## 2. Добавь Apps Script

Открой **Extensions → Apps Script** и вставь код ниже.

### Code.gs

```javascript
const SUPABASE_URL = 'https://txckerrkubbvmzlionjf.supabase.co';
const SUPABASE_ANON_KEY = 'YOUR_ANON_KEY_HERE'; // вставь свой ключ

/**
 * Триггер: при редактировании ячейки.
 * Когда заполнены Game (A) и Idea (B), а Task ID (F) пуст —
 * создаёт задачу в Supabase и записывает task_id обратно.
 */
function onEdit(e) {
  const sheet = e.source.getActiveSheet();
  if (sheet.getName() !== 'Video Tasks') return;

  const row = e.range.getRow();
  if (row <= 1) return; // skip header

  const game = sheet.getRange(row, 1).getValue();
  const idea = sheet.getRange(row, 2).getValue();
  const taskId = sheet.getRange(row, 6).getValue();

  // Только если Game и Idea заполнены, а Task ID пуст
  if (!game || !idea || taskId) return;

  const priority = sheet.getRange(row, 3).getValue() || 0;

  const response = UrlFetchApp.fetch(SUPABASE_URL + '/rest/v1/video_tasks', {
    method: 'POST',
    headers: {
      'apikey': SUPABASE_ANON_KEY,
      'Authorization': 'Bearer ' + SUPABASE_ANON_KEY,
      'Content-Type': 'application/json',
      'Prefer': 'return=representation'
    },
    payload: JSON.stringify({
      game_tag: game,
      idea: idea,
      priority: priority,
      source: 'google_sheets',
      source_row_id: String(row)
    })
  });

  const result = JSON.parse(response.getContentText());
  if (result && result[0] && result[0].id) {
    sheet.getRange(row, 6).setValue(result[0].id);    // Task ID
    sheet.getRange(row, 4).setValue('pending');         // Status
  }
}

/**
 * Периодический триггер (каждые 2 мин): синхронизация статусов.
 * Проходит по строкам с Task ID и обновляет Status и Video URL.
 */
function syncStatuses() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Video Tasks');
  if (!sheet) return;

  const lastRow = sheet.getLastRow();
  if (lastRow <= 1) return;

  for (let row = 2; row <= lastRow; row++) {
    const taskId = sheet.getRange(row, 6).getValue();
    const currentStatus = sheet.getRange(row, 4).getValue();

    // Только для задач, которые ещё не завершены
    if (!taskId || currentStatus === 'completed' || currentStatus === 'failed') continue;

    const response = UrlFetchApp.fetch(
      SUPABASE_URL + '/rest/v1/video_tasks?id=eq.' + taskId + '&select=status,output_video_url',
      {
        headers: {
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': 'Bearer ' + SUPABASE_ANON_KEY
        }
      }
    );

    const result = JSON.parse(response.getContentText());
    if (result && result[0]) {
      sheet.getRange(row, 4).setValue(result[0].status);
      if (result[0].output_video_url) {
        sheet.getRange(row, 5).setValue(result[0].output_video_url);
      }
    }
  }
}
```

## 3. Настрой триггеры

В Apps Script → **Triggers** (⏰):

1. **onEdit** — уже работает автоматически (simple trigger)
   - Но для `UrlFetchApp` нужен **installable trigger**:
   - Нажми **+ Add Trigger** → `onEdit` → From spreadsheet → On edit
2. **syncStatuses** — периодический:
   - Нажми **+ Add Trigger** → `syncStatuses` → Time-driven → Every 2 minutes

## 4. Как использовать

1. Заполни строку: Game = `Oxide`, Idea = `Noob builds castle`
2. Apps Script автоматически создаст задачу в Supabase
3. Task ID появится в колонке F, Status = `pending`
4. Claude Code `/loop` подхватит задачу и начнёт генерацию
5. Через ~5-10 мин статус обновится на `completed` + URL видео
