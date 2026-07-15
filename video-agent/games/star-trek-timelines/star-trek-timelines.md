# Star Trek Timelines

## Posting status

- **ready_to_post:** yes   <!-- yes only when the game is tested and cleared for posting -->

**Formats (linked to this game):**

- character-story — ready_to_post: yes
- fake-ad — ready_to_post: yes
- fun-news — ready_to_post: yes
- in-game-pov — ready_to_post: yes
- redcon — ready_to_post: yes
- reddit-story — ready_to_post: yes
- room1701 — ready_to_post: yes
- serial-drama — ready_to_post: yes
- streettalk — ready_to_post: yes
- what-if-real-life — ready_to_post: yes
- wild-documentary — ready_to_post: yes


## Метаданные

- **Жанр:** Strategy RPG, Crew Collector (Gacha)
- **Платформа:** iOS, Android, Steam, Facebook
- **Разработчик:** Wicked Realm Games (ранее Disruptor Beam → Tilting Point)
- **Аудитория:** Global, фанаты Star Trek, gacha/RPG игроки 25-45 лет
- **Стиль арта:** Sci-fi LCARS UI, полуреалистичные 2D-портреты, 3D-корабли
- **Премьера:** Январь 2016 (10+ лет активной работы)
- **youtube_channel:** starfleetarchive

---

## Концепция игры

Временной кризис смешал все эпохи Star Trek. **Q** (всемогущее существо-трикстер) нанимает игрока как капитана корабля, чтобы навести порядок. Игрок собирает экипаж из ВСЕХ эпох Trek: TOS, TNG, DS9, Voyager, Enterprise, Discovery, Picard, Lower Decks, Strange New Worlds и фильмов.

**1350+ персонажей**, сотни кораблей, PvP и PvE.

---

## Visual Style Guide

### Цветовая палитра
- Основные: deep space black (#0a0a12), LCARS orange (#ff9900), Federation blue (#3366cc)
- Акценты: LCARS purple (#9966cc), rarity gold (#ffd700), warp blue (#00ccff)
- Рарити: gray (1-star), green (2-star), blue (3-star), purple (4-star), gold (5-star)

### Освещение
- Тёмный космический фон с яркими точечными источниками (звёзды, консоли, фазерные лучи)
- LCARS-интерфейс: мягкое свечение оранжевых/синих панелей
- Мостик корабля: приглушённый свет с бликами от экранов
- Космические бои: яркие вспышки фазеров, торпед, щитов

### Композиция
- Персонажи: **3D cinematic sci-fi**, НЕ cartoon/мультяшные
- Фон: мостик корабля, космос, планеты, станции
- UI вдохновлён LCARS (закруглённые прямоугольные панели Star Trek)
- Вертикальная 9:16, mobile-first

### Стилистические ограничения
- **НЕ cartoon, НЕ chibi, НЕ stylized, НЕ toy-like** — только 3D cinematic sci-fi
- Для молодых персонажей (Chekov) — явно указывать `"realistic adult proportions, full-height figure"` в промпте, иначе модель генерирует карикатурные/непропорциональные фигуры
- Не использовать эра-специфичные слова (`"TNG"`, `"TOS"`) в промптах — модель переопределяет цвет формы. Писать цвет явно: `"gold-yellow uniform"`, `"red uniform"`

> Это справочный контекст игры, не fallback внешности/стиля формата. Для генерации обязателен top-level `style_tags` из точного `{format}_story_bible.json`; если bible отсутствует или поле не задано, остановиться и спросить пользователя о создании/дополнении.

### Prompt prefix
```
Star Trek Timelines style, cinematic sci-fi character portrait, cinematic Federation lighting, deep space environment, Starfleet uniform details, clean cinematic frame, no UI overlay
```

> ⚠️ В prefix описываем **стиль** (свет, палитра, художественное направление), не диегетический UI. Слова `LCARS interface aesthetic`, `HUD`, `text overlay`, `panel borders` сюда не пихать — NB2 трактует их буквально и рисует UI поверх лица. LCARS-панели рисуем локально в `environment_state` тех сцен, где они нужны (title card, DS9 Ops).

---

## Фракции

### Основные (союзники/нейтральные)
| Фракция | Отношение | Описание |
|---------|-----------|----------|
| **Federation** | Friendly | Объединённая Федерация Планет — мирные исследователи с мощным флотом |
| **Bajoran** | Friendly | Глубоко религиозный народ, жертвы Кардассианской оккупации |
| **Ferengi Alliance** | Friendly | Реформированные Ференги, торговля и прогресс |
| **Cardassian Union** | Neutral | Ослаблены после Доминионской войны, шпионаж |
| **Maquis** | Neutral | Повстанцы из Федерации, борцы за свободу / террористы |
| **Section 31** | Neutral | Секретная спецслужба Федерации, "цель оправдывает средства" |

### Враждебные
| Фракция | Отношение | Описание |
|---------|-----------|----------|
| **Klingon Empire** | Hostile | Воинская цивилизация, честь превыше всего |
| **Romulan Star Empire** | Hostile | Обман и шпионаж через Tal Shiar |
| **Ferengi Traditionalists** | Hostile | Консервативные Ференги, жадность |
| **Augments** | Despised | Генетически улучшенные люди (народ Хана) |
| **Terran Empire** | Despised | Злая Федерация из Зеркальной Вселенной |
| **Klingon-Cardassian Alliance** | Despised | Альянс Зеркальной Вселенной |
| **Hirogen** | Despised | Охотники из Дельта-Квадранта |
| **Dominion** | Despised | Перевёртыши + Ворта + Джем'Хадар |
| **Borg** | Despised | Коллектив, ассимилирующий всё. "Сопротивление бесполезно" |

### Ключевые отношения между фракциями
- **Федерация ↔ Клингоны:** то союзники, то враги (зависит от эпохи)
- **Федерация ↔ Борги:** абсолютные враги, без компромиссов
- **Федерация ↔ Ромуланцы:** холодная война, взаимное недоверие
- **Баджорцы ↔ Кардассианцы:** ненависть (оккупация)
- **Зеркальные фракции:** враги всех из основной вселенной
- **Q:** надфракционный, манипулирует всеми

---

## Tone of Voice

- Эпичный sci-fi с юмором (Q задаёт тон — сарказм + величие)
- Nostalgia-driven: "помнишь этот момент из сериала?"
- Гачa-юмор: боль от пустых паков, радость от легендарки
- Контраст между пафосом Trek и абсурдом мобильной игры
- Язык: English (для I2V моделей), Russian (для текста/субтитров)

### Примеры фраз
- "I opened 10 packs and got nothing but Ensign Ricky..."
- "My Gauntlet streak! NOOO!"
- "Resistance is futile. So is my dilithium budget."
- "Today is a good day to... open a Behold?"
- "I've been on this Voyage for 10 hours. No regrets. Okay, some regrets."
- "Captain's log: I airlocked my favorite crew. For slots. I'm a monster."

---

## Character appearance

Character appearance cards live in the per-format story bibles (`characters[]` / `characters{}`), NOT here — the same character may look different per format, and cards must stay style-free (appearance only; style comes from the resolved `style_tags`). Assets and appearance or voice descriptions are format-bound: never read or copy them from another format automatically. If a character has no card in the target format's bible, Scenarist writes a run-local style-free card into `storyboard.json` / `proposed_bible_updates`; Manager applies it to the exact bible only after explicit final user approval. If canon/the user brief is insufficient, STOP and ask. Cross-format copying is allowed only when the user explicitly instructs it.

---

## Игровой сленг (для сценариев)

| Термин | Значение |
|--------|----------|
| Gauntlet | PvP на бросках Proficiency, эксклюзивные награды |
| Voyage | Экспедиция 12 членов экипажа, пока не кончится антиматерия |
| Behold | Выбор 1 из 3 случайных персонажей из пака |
| Airlock | Удалить персонажа навсегда |
| Cryostasis / Freeze | Заморозить экипаж для освобождения слота |
| Chronitons | Энергия для миссий |
| Dilithium | Премиум-валюта |
| Honor | Заработанная валюта для Honor Hall |
| FFFE | Fully Fused, Fully Equipped — максимальный персонаж |
| Fuse / Fusion | Слияние дубликатов для повышения звёзд |
| Polestars | Фильтры для Crew Retrieval |
| Whale | Донатер |
| F2P | Free-to-play игрок |
| Immortalize | Полностью прокачать персонажа |
| Warp | Автопрохождение 3-звёздочной миссии |
| Big Book | Комьюнити-гайд по оценке персонажей |

---

## Идеи для контента (что зайдёт аудитории)

### Комедия / Relatable
- "Когда открыл 10 паков и получил только 1-star Ensign Ricky"
- "Behold: 3 персонажа, которые у тебя уже есть"
- "Voyage на 10 часов, антиматерия на 1%... рискнуть?"
- "Пришлось выбросить в Airlock любимого персонажа ради слота"
- "Мой Gauntlet-стрик на 30 побед... и тут Locutus противника"
- "Q объясняет тебе почему ты плохой капитан"

### Драма / Лор
- "Пикард становится Локутусом — самый трагичный момент Trek"
- "Kirk vs Picard — кто лучший капитан? (драматическая битва)"
- "Khan возвращается — история мести"
- "Зеркальная Вселенная: когда все герои — злодеи"
- "Borg Queen vs Seven of Nine — битва за душу"

### Gameplay AI Avatar
- "Гайд: как пройти Gauntlet без доната"
- "Топ-5 персонажей для Voyage в 2026"
- "Crew Retrieval: как получить легендарку бесплатно"
- "Ошибки новичка в Star Trek Timelines"

---

## Референсные изображения

> **TODO:** загрузить в Supabase Storage и обновить URL:
> - Скриншоты геймплея (мостик, Gauntlet, корабельные бои)
> - Промо-арт персонажей (Kirk, Picard, Borg Queen)
> - LCARS UI элементы

---

## Музыка

- **Mood:** epic orchestral sci-fi, dramatic, with touches of wonder
- **BPM:** 80-120 (медленнее для драмы, быстрее для экшна)
- **Рекомендуемые:** orchestral space themes, synth-wave с Trek-вайбом, напряжённые Borg-сцены (low brass + electronics)

---

## CTA

- **Статус:** ready
- **Supabase URL:** `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/star-trek-timelines/branding/cta.mp4`
- **Текст:** "DOWNLOAD THE GAME · LINK IN BIO"
- **Формат:** 720×1280, 30fps, ~5s — idle animation, star particles drifting
- **Использование:** Editor скачивает, нормализует (scale+pad 1080×1920+30fps+AAC), конкатенирует в конец после всех сцен
