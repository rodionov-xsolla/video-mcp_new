# ElevenLabs TTS API Reference

Справочник по ElevenLabs Text-to-Speech API для экспрессивной озвучки.

---

## Аутентификация

Все запросы требуют заголовок:
```
xi-api-key: $ELEVENLABS_API_KEY
```

Переменная `ELEVENLABS_API_KEY` должна быть установлена в окружении перед запуском.

---

## Text-to-Speech — генерация озвучки

**Endpoint:** `POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`
**Метод:** POST (синхронный — возвращает аудиофайл напрямую)
**Стоимость:** ~$0.30/мин (~1000 символов ≈ 1 минута)

### Запрос

```bash
curl -s -X POST "https://api.elevenlabs.io/v1/text-to-speech/$VOICE_ID" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -o output.mp3 \
  -d '{
    "text": "So my little brother has been playing Roblox every single day for the past year...",
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
      "stability": 0.3,
      "similarity_boost": 0.8,
      "style": 0.7
    }
  }'
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `voice_id` | string (URL path) | Да | ID голоса (из таблицы ниже) |
| `text` | string | Да | Текст для озвучки (макс 5000 символов) |
| `model_id` | string | Нет | Модель. `eleven_multilingual_v2` для мультиязычности, `eleven_monolingual_v1` для EN only |
| `voice_settings.stability` | float | Нет | 0.0-1.0. Низкое = более экспрессивный. Для storytelling: **0.3** |
| `voice_settings.similarity_boost` | float | Нет | 0.0-1.0. Сходство с оригинальным голосом. Рекомендуется: **0.8** |
| `voice_settings.style` | float | Нет | 0.0-1.0. Усиление стиля/экспрессии. Для storytelling: **0.7** |

### Ответ

Файл возвращается напрямую в body (не JSON). Content-Type: `audio/mpeg`.

```bash
# Проверить что файл скачался (>1000 bytes)
ls -la output.mp3

# Получить длительность
ffprobe -v error -show_entries format=duration -of csv=p=0 output.mp3
```

---

## Рекомендованные голоса для storytelling

### EN мужские (экспрессивные):

| Voice ID | Имя | Стиль | Когда |
|----------|-----|-------|-------|
| `pNInz6obpgDQGcFmaJgB` | Adam | Глубокий, уверенный | Drama, revenge, sigma |
| `ErXwobaYiN019PkySvjV` | Antoni | Молодой, энергичный | Funny, shock, rage |
| `VR6AewLTigWG4xSOukaG` | Arnold | Грубый, брутальный | Rage, revenge |
| `TxGEqnHWrfWFTfGW9XjX` | Josh | Тёплый, повествовательный | Touching, drama |
| `yoZ06aMxZJJ28mfd3POQ` | Sam | Динамичный, молодой | Funny, shock |

### EN женские (экспрессивные):

| Voice ID | Имя | Стиль | Когда |
|----------|-----|-------|-------|
| `EXAVITQu4vr4xnSDxMaL` | Bella | Мягкий, эмоциональный | Touching, drama |
| `21m00Tcm4TlvDq8ikWAM` | Rachel | Уверенный, взрослый | Drama, revenge |
| `AZnzlk1XvdvUeBnXmlld` | Domi | Энергичный, молодой | Funny, shock |

### Мультиязычные:

Модель `eleven_multilingual_v2` поддерживает 29 языков. Тот же `voice_id` работает для любого языка — модель определяет язык по тексту автоматически.

**Поддерживаемые языки:** EN, RU, ES, PT, FR, DE, IT, PL, TR, AR, HI, JA, KO, ZH, NL, SV, ID, FI, UK, EL, CS, RO, DA, HU, NO, SK, HR, BG, MS.

---

## Voice Settings по тону

| Тон истории | stability | similarity_boost | style |
|-------------|-----------|------------------|-------|
| **Funny** | 0.25 | 0.75 | 0.8 |
| **Touching** | 0.35 | 0.85 | 0.6 |
| **Drama/Revenge** | 0.30 | 0.80 | 0.7 |
| **Shock/Rage** | 0.20 | 0.75 | 0.9 |

Низкая stability + высокий style = максимальная экспрессия.

---

## Важные правила

1. **Синхронный API** — ответ возвращается сразу (не нужен polling). Таймаут: 60 сек.
2. **Лимит:** 5000 символов на запрос. Если текст длиннее — разбей на части.
3. **Формат выхода:** MP3 по умолчанию. Для WAV добавь query parameter: `?output_format=pcm_44100`
4. **Rate limit:** ~100 запросов/мин на аккаунт.
5. **Стоимость:** ~$0.30/мин озвучки. 60 сек ролик ≈ $0.30.
