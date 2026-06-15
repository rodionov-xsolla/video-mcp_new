# Star Trek Timelines

## Метаданные

- **Жанр:** Strategy RPG, Crew Collector (Gacha)
- **Платформа:** iOS, Android, Steam, Facebook
- **Разработчик:** Wicked Realm Games (ранее Disruptor Beam → Tilting Point)
- **Аудитория:** Global, фанаты Star Trek, gacha/RPG игроки 25-45 лет
- **Стиль арта:** Sci-fi LCARS UI, полуреалистичные 2D-портреты, 3D-корабли
- **Премьера:** Январь 2016 (10+ лет активной работы)
- **youtube_channel:** starfleet

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
- Персонажи: полуреалистичные портреты, **semi-realistic Pixar 3D**, НЕ cartoon/мультяшные
- Фон: мостик корабля, космос, планеты, станции
- UI вдохновлён LCARS (закруглённые прямоугольные панели Star Trek)
- Вертикальная 9:16, mobile-first

### Стилистические ограничения
- **НЕ cartoon, НЕ chibi, НЕ stylized** — только semi-realistic Pixar-quality 3D
- Для молодых персонажей (Chekov) — явно указывать `"realistic adult proportions, full-height figure"` в промпте, иначе модель генерирует карикатурные/непропорциональные фигуры
- Не использовать эра-специфичные слова (`"TNG"`, `"TOS"`) в промптах — модель переопределяет цвет формы. Писать цвет явно: `"gold-yellow uniform"`, `"red uniform"`

### Prompt prefix
```
Star Trek Timelines style, semi-realistic sci-fi character portrait, cinematic Federation lighting, deep space environment, Starfleet uniform details, clean cinematic frame, no UI overlay
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

## Герои для промптов

### Федерация / Герои

| Персонаж | Эпоха | Визуальные ключи |
|----------|-------|------------------|
| Captain Kirk | TOS | Атлетичный, каштановые волосы набок, золотая командная туника с дельтой Starfleet, чёрные брюки, самоуверенная поза |
| Mr. Spock | TOS | Заострённые уши, дугообразные брови, чёрные волосы-каре, оливковая кожа, синяя научная туника, спокойное выражение, одна бровь поднята |
| Captain Picard | TNG | Лысый, благородный, красно-чёрная форма TNG (красные плечи, чёрный корпус), комбейдж на груди, руки за спиной |
| Commander Data | TNG | Бледно-жёлтая кожа, зализанные чёрные волосы, жёлто-золотые глаза, золото-чёрная форма, безэмоциональное лицо |
| Commander Worf | TNG/DS9 | Клингонские гребни на лбу, тёмная кожа, длинные тёмные волосы в хвосте, козлиная бородка, золотая форма + металлический пояс-перевязь |
| Captain Janeway | VOY | Рыжевато-каштановые волосы в пучке, красно-чёрная форма Voyager, решительное выражение |
| Seven of Nine | VOY | Блондинка, волосы гладко зачёсаны, импл Борга над левым глазом (металлическая звёздочка), серебристо-голубой костюм, пронзительный взгляд |
| Commander Riker | TNG | Высокий, широкоплечий, тёмные волосы, фирменная борода, красно-чёрная форма, усмешка |

### Злодеи / Антагонисты

| Персонаж | Фракция | Визуальные ключи |
|----------|---------|------------------|
| Khan | Augments | Мускулистый, длинные тёмные волосы, открытая грудь, надменное выражение, одежда воина |
| Borg Queen | Borg | Серая кожа, лысая голова с кибер-шлемом, механический позвоночник/шея, чёрный костюм с био-трубками, зловещая полуулыбка |
| Q | Neutral | Среднего возраста, надменная ухмылка, чаще в красно-чёрной форме капитана Starfleet, иногда в мантии судьи |
| Locutus | Borg | Лицо Пикара, серая кожа Борга, красный лазерный окуляр, кибер-трубки от головы/шеи, чёрная броня Борга |
| Gul Dukat | Cardassian | Серая чешуйчатая кожа, ложкообразный гребень на лбу, кардассианские шейные гребни, зализанные тёмные волосы, серо-коричневая военная форма |

### Зеркальная Вселенная (Mirror Universe)
Злые версии героев: тёмные милитаристские формы, эмблема Терранской Империи (меч через планету). Mirror Spock — с козлиной бородкой. Mirror Kirk — агрессивный, жестокий.

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

## Character Prompt Blocks

### Captain Kirk (TOS, command gold)
`semi-realistic male Starfleet captain, athletic build, light brown hair swept to the side, confident charming smirk showing teeth, gold yellow command tunic with black collar and Starfleet delta badge on left chest, black trousers, standing heroic pose with phaser in hand, dramatic bridge lighting, deep space visible through viewport behind`

### Mr. Spock (TOS, science blue)
`semi-realistic male Vulcan Starfleet officer, pointed ears, sharply arched thick eyebrows, straight black bowl-cut hair, olive-tinted skin, calm emotionless expression with one eyebrow slightly raised, blue science tunic with black collar and Starfleet delta badge, hands clasped behind back, starship bridge background with LCARS consoles`

### Captain Picard (TNG, command red)
`semi-realistic bald male Starfleet captain, distinguished refined appearance, serious authoritative expression, red and black TNG uniform with red shoulders and black body, Starfleet combadge on left chest, four rank pips on collar, one hand extended in commanding gesture, Enterprise-D bridge background, dramatic blue lighting`

### Locutus of Borg (assimilated Picard)
`semi-realistic Borg-assimilated male, pale gray cybernetic skin, bald head with black Borg skull cap and tubes, red laser eye-piece over left eye, mechanical tubes running from neck and jaw, black Borg body armor with green glowing circuitry, emotionless menacing stare, dark Borg cube interior background with green ambient light`

### Borg Queen
`semi-realistic female Borg Queen, pale grayish skin, bald head with dark biomechanical skull cap, exposed mechanical spine and neck vertebrae visible, black form-fitting bodysuit with grey biomechanical tubing, dark hollow eyes with sinister knowing half-smile, Borg alcove background with green glowing lights`

### Khan (classic, Wrath of Khan era)
`semi-realistic muscular male warrior, long flowing dark hair, broad bare chest visible through torn open red uniform, thick gold necklace, deeply tanned weathered skin, intense vengeful expression with clenched jaw, strong defined cheekbones, dramatic side lighting, desolate planet surface background`

### Q (in Starfleet uniform)
`semi-realistic middle-aged male in Starfleet captain uniform, red and black TNG uniform, smug knowing grin, slightly theatrical pose with one hand raised as if snapping fingers, mischievous gleaming eyes, slightly disheveled appearance suggesting casual disregard for protocol, Enterprise bridge background slightly distorted with golden omnipotent glow`

### Seven of Nine (Voyager)
`semi-realistic blonde female, hair pulled back tightly in a bun, metallic starburst-shaped Borg implant above left eye, small metallic implant on left hand, form-fitting silver and blue catsuit, athletic build, intense striking blue eyes, confident stance with arms crossed, Voyager astrometrics lab background with star charts`

### Commander Worf (TNG)
`semi-realistic male Klingon Starfleet officer, prominent triangular cranial ridges on forehead, dark brown skin, long dark hair in warrior ponytail, groomed goatee beard, gold and black TNG operations uniform, diagonal metal warrior baldric sash across chest, fierce honorable expression, strong muscular build, Enterprise corridor background`

### Gul Dukat (Cardassian)
`semi-realistic male Cardassian, gray scaly textured skin, prominent spoon-shaped cranial ridge on forehead, raised neck ridges, slicked-back dark hair, Cardassian military uniform in gray-brown with armored shoulders, charming manipulative smile, tall lean build, Cardassian warship bridge background with dark metallic tones`

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

---

## GLN Channel Branding (надканальный бренд)

Всё ST-Timelines контент идёт как сетка **Galactic Lol Network (GLN)** — фановый ТВ-канал по вселенной Star Trek. Brand-bug накладывается Editor'ом ПОВЕРХ финального видео (после concat, до субтитров), как это делают реальные ТВ-каналы (CNN/BBC/RT).

- **`channel_bug_url`**: `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/star-trek-timelines/branding/gln-bug.png`
- **Источник логотипа:** Gemini Generated (2026-05-29), вырезан до RGBA (background transparent), 512×512 PNG, ~42 KB
- **Позиция в кадре:** top-left, отступ 40 px от верха и левого края
- **Размер при overlay:** 110×110 px (downscale из 512×512 через `scale=110:110` в filter_complex)
- **Прозрачность:** альфа уже зашита в PNG (~70% эффективная); если нужно сильнее погасить — `colorchannelmixer=aa=0.7` в overlay цепочке
- **Поведение:** static, full-video duration (без fade in/out)
- **Применимо к форматам:** ВСЕ ST-Timelines форматы (streettalk, fun-news, news, character-story, redcon, ...). Editor читает `channel_bug_url` из game config и применяет автоматически — см. `rules/roles/editor.md` §13a.
- **Когда НЕ применять:** если game config не содержит `channel_bug_url` (другие игры — Roblox, MLBB и пр.), а также если конкретный формат явно отключает через свой playbook (нет таких форматов на момент 2026-05-29).

**Анти-паттерны:**
- ❌ Bug на CTA — CTA это отдельный branded ролик, bug на нём = двойной брендинг. Применять ТОЛЬКО на основном контенте (между opener и CTA, или на всём, если opener тоже свой — зависит от format-specific решения).
- ❌ Bug меняет позицию / размер от ролика к ролику. Везде одинаково — top-left, 110×110, 40px отступ.
- ❌ Bug на 100% непрозрачности или больше 200×200 px — это watermark, не TV bug. Сатира требует тонкости.
