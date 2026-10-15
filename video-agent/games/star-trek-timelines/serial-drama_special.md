# Star Trek Timelines — Serial Drama Special Requirements

Специальные настройки формата Serial Drama для Star Trek Timelines.

Apply this generic game-level file only when Manager has resolved `STORY_BIBLE_PATH` to `games/star-trek-timelines/serial-drama_story_bible.json`. If the resolved path is `games/star-trek-timelines/room1701_story_bible.json`, ignore this entire file: ROOM 1701's exact bible, cast, style, locations, voices, and episode state take precedence and must never be overwritten by these generic Airlock/Trek defaults.

---

## Стиль для serial-drama формата
```
Star Trek cinematic 3D animation, semi-realistic Pixar-quality characters, detailed Starfleet uniforms with fabric texture, glowing LCARS console panels, dramatic sci-fi lighting with lens flares, deep space backgrounds with nebulae and stars, cinematic depth of field, volumetric light from viewscreens
```

## Locked TTS voices — The Airlock (H3 lip-sync dialogue)

Serial-drama dialogue is H3 lip-sync on MiniMax TTS (`rules/formats/serial-drama.md`, `rules/roles/sound.md` §5a). These are the voices and TTS settings used in the cost trial that the user approved for production (cost trial Test 9, The Airlock S2E1, October 2026). They are locked for this series: Sound uses them for these characters in every episode, never re-picks them, and records them in `storyboard.json → tts_voices` with `"source": "locked"`. A speaking character who is not listed here and has no `characters[].tts_voice` in the series bible gets a new pick by Sound (`"source": "new"`; Manager writes it to the bible only after the episode is approved).

| Character (storyboard `speaker` / bible `name`) | `voice_id` | `speed` | Why (Test 9) |
|---|---|---|---|
| Kirk / `Kirk` | `Determined_Man` | `0.9` | confident commanding captain, drama/authoritative speed |
| Scotty / `Scotty` | `Casual_Guy` | `1.0` | warm, energetic engineer, here alarmed; lighter and quicker than Kirk so the two read apart |
| Fleet Admiral / `Fleet_Admiral` | `Imposing_Manner` | `0.9` | cold, calculating older antagonist |
| Worf / `Worf` | `Deep_Voice_Man` | `0.9` | imposing, disciplined Klingon officer |

`voice_id` and `speed` are fixed per character; `emotion` is chosen per line from the scene's `facial_expression` / `character_state` (Test 9: Scotty `fearful`; Kirk `neutral`, `angry`, `neutral`; Fleet Admiral `neutral`; Worf `sad`).

**TTS request — one per `character_speech` line, exactly as tested** (`POST https://queue.fal.run/fal-ai/minimax/speech-2.8-hd`, poll base `fal-ai/minimax`, model `fal-ai/minimax/speech-2.8-hd`):

```json
{
  "prompt": "<the character_speech line, verbatim>",
  "voice_setting": {"voice_id": "<locked voice_id>", "speed": <locked speed>, "emotion": "<emotion for this line>"},
  "audio_setting": {"format": "mp3"},
  "language_boost": "English"
}
```

Example (Test 9, scene 1, line 1): `{"prompt": "Captain, Starfleet just locked every command code you own.", "voice_setting": {"voice_id": "Casual_Guy", "speed": 1.0, "emotion": "fearful"}, "audio_setting": {"format": "mp3"}, "language_boost": "English"}`.

**Clip audio — as tested:** per dialogue clip, 0.2 s of silence, then the lines in `character_speech` order with 0.3 s of silence between them, mono 44.1 kHz MP3 (`libmp3lame -q:a 2`; recipe in `rules/roles/sound.md` §5a), uploaded as the clip's `tts_url`. Test 9 clip lengths: 6.63 s, 7.45 s, 9.16 s.

---

## Типичные локации
- **Enterprise Bridge:** командная палуба, LCARS-консоли с оранжевым/синим свечением, большой экран с космосом, кресло капитана в центре
- **Transporter Room:** платформа телепортации с синим свечением, пульт управления, стены с панелями
- **Borg Cube Interior:** тёмный зелёный свет, механические стены с трубками, Borg-алькови с дронами, туман
- **Deep Space 9 Promenade:** космическая станция, магазины, Quark's Bar с неоновой вывеской, разные инопланетяне
- **Klingon Great Hall:** тёмный зал с факелами, каменные стены, трофеи, символ Империи
- **Vulcan Temple:** минималистичный интерьер, песчаные стены, свечи, медитация
- **Sickbay:** медицинский отсек, биокровать с голографическими мониторами, чистое белое освещение
- **Ready Room:** кабинет капитана, стол, книги/артефакты, окно в космос

## Типичные конфликты для сериала
- **Gauntlet Drama:** стрик на 30+ побед, и тут появляется Locutus противника
- **Behold Agony:** три легендарки, выбрать можно одну — и выбрал неправильно
- **Borg Assimilation:** капитан корабля (игрок) похищен Боргами, экипаж спасает
- **Mirror Universe:** злые двойники вторгаются в основную вселенную
- **Q's Trial:** Q устраивает суд над игроком, обвиняя в плохом капитанстве
- **Airlock Dilemma:** не хватает слотов, нужно выбросить любимого персонажа

## Пары персонажей для драмы
- **Kirk + Spock:** дружба логика и авантюриста
- **Picard + Locutus:** внутренний конфликт, PTSD от ассимиляции
- **Q + любой капитан:** манипуляция и испытания
- **Worf + честь:** выбор между Starfleet и Klingon Empire
- **Seven of Nine + Borg Queen:** борьба за свободу от Коллектива

## Музыка
- **Mood:** epic orchestral, dramatic tension, wonder/exploration
- **BPM:** 80-120
- **Рекомендуемые жанры:** orchestral sci-fi (Borg-сцены: low brass + electronic drones), exploration themes (strings + horns), dramatic reveals (timpani + choir)
