# Google Sheets → Game Assets (Supabase)

Инструкция для управления ассетами персонажей через Google Sheets.

## 1. Создай таблицу

Создай новый Google Sheet (или новый лист в существующей таблице) с именем **"Game Assets"**.

### Столбцы:

| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| game_tag | character_name | asset_type | url | prompt_block | tags | status |

### Допустимые значения:
- **asset_type**: `reference_image`, `character_card`, `screenshot`, `promo_art`, `generated_ref`
- **tags**: через запятую: `assassin,male,anime`
- **status**: заполняется автоматически скриптом (`synced`, `error: ...`)

### Пример заполнения:

| game_tag | character_name | asset_type | url | prompt_block | tags | status |
|----------|---------------|------------|-----|-------------|------|--------|
| MLBB | Lancelot | character_card | | male warrior assassin Lancelot, silver armor... | assassin,male,anime | |
| Kekele | Pirate | reference_image | https://...img_2.png | | pirate,male,reference | |

**URL** — опционален. Если пустой, запись создастся без изображения (только prompt_block).

## 2. Apps Script

Открой: **Extensions → Apps Script**

Вставь код:

```javascript
// === НАСТРОЙКИ ===
const SUPABASE_URL = "https://txckerrkubbvmzlionjf.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR4Y2tlcnJrdWJidm16bGlvbmpmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY0NjU0MDAsImV4cCI6MjA3MjA0MTQwMH0.PNKifWzFeyNk3mORtfaORSX8XpBuo0HYeQu4tF35JJg";
const SHEET_NAME = "Game Assets";

// === При редактировании строки — отправляем ассет в Supabase ===
function onAssetEdit(e) {
  const sheet = e.source.getActiveSheet();
  if (sheet.getName() !== SHEET_NAME) return;

  const row = e.range.getRow();
  if (row < 2) return; // skip header

  const data = sheet.getRange(row, 1, 1, 7).getValues()[0];
  const [gameTag, characterName, assetType, url, promptBlock, tags, status] = data;

  // Нужны минимум game_tag, character_name, asset_type
  if (!gameTag || !characterName || !assetType) return;

  // Если уже synced — не отправляем повторно
  if (status === "synced") return;

  // URL опционален — если нет, записываем только prompt_block
  const assetUrl = url || null;

  // Формируем tags как JSON array
  const tagsArray = tags ? String(tags).split(",").map(t => t.trim()) : [];

  const payload = {
    game_tag: gameTag,
    character_name: characterName,
    asset_type: assetType,
    url: assetUrl,
    prompt_block: promptBlock || null,
    tags: tagsArray,
    metadata: {}
  };

  try {
    const response = UrlFetchApp.fetch(`${SUPABASE_URL}/rest/v1/game_assets`, {
      method: "post",
      headers: {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": `Bearer ${SUPABASE_ANON_KEY}`,
        "Content-Type": "application/json",
        "Prefer": "return=representation,resolution=merge-duplicates"
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });

    const code = response.getResponseCode();
    if (code === 200 || code === 201) {
      sheet.getRange(row, 7).setValue("synced");
    } else {
      sheet.getRange(row, 7).setValue(`error: ${code} ${response.getContentText().substring(0, 200)}`);
    }
  } catch (err) {
    sheet.getRange(row, 7).setValue(`error: ${err.message}`);
  }
}
```

## 3. Настройка триггера

1. В Apps Script: **Triggers** (значок часов слева)
2. **+ Add Trigger**:
   - Function: `onAssetEdit`
   - Event source: From spreadsheet
   - Event type: **On edit**
3. Сохрани. Разреши доступ при запросе.

## 4. Использование

1. Заполняешь строку: game_tag, character_name, asset_type, prompt_block, tags
2. Скрипт автоматически отправляет в Supabase
3. В столбце G появляется `synced` или `error: ...`

Для загрузки изображений:
- Загрузи файл в Supabase Storage (bucket `assets`) или `Cosplay sources`
- Вставь публичный URL в столбец D (url)
- Или используй `upload-asset.sh` для загрузки файлов с диска
