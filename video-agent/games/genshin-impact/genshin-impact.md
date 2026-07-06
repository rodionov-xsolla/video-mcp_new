# Genshin Impact

## Posting status

- **ready_to_post:** yes   <!-- yes only when the game is tested and cleared for posting -->

**Formats (linked to this game):**

- character-story — ready_to_post: yes
- dual-style — ready_to_post: yes
- fake-ad — ready_to_post: yes
- fun-news — ready_to_post: yes
- in-game-pov — ready_to_post: yes
- reddit-story — ready_to_post: yes
- serial-drama — ready_to_post: yes
- special-report — ready_to_post: yes
- streettalk — ready_to_post: yes
- top-list — ready_to_post: yes


## Метаданные

- **Жанр:** Open-world Action RPG
- **Платформа:** iOS, Android, PC, PlayStation
- **Разработчик:** HoYoverse
- **Аудитория:** Global, anime fans, gacha/RPG players 16-35
- **Стиль арта:** Anime cel-shading, vibrant fantasy, painterly environments
- **Премьера:** September 2020 (active live service)
- **youtube_channel:** genshinsnap

---

## Концепция игры

Путешественник попадает в мир Тейват — семь наций, каждая под покровительством своего Архонта. Игрок исследует открытый мир, собирает персонажей через гача-систему и сражается с помощью стихийных реакций (Pyro, Hydro, Cryo, Electro, Anemo, Geo, Dendro).

**70+ игровых персонажей**, сотни событий, кооперативный режим, постоянные обновления.

---

## Visual Style Guide

### Цветовая палитра
- Основные: sky blue (#87ceeb), fantasy gold (#f5d060), emerald green (#50c878)
- Акценты: primogem violet (#a855f7), electro purple (#7c3aed), pyro orange (#f97316)
- Элементы: Pyro (#ff4500), Hydro (#1e90ff), Cryo (#b0e0e6), Electro (#9b59b6), Anemo (#95d5b2), Geo (#f0a500), Dendro (#4caf50)

### Освещение
- Яркое дневное с мягкими тенями — характерный anime-стиль
- Магические эффекты: светящиеся стихийные частицы
- Сцены боя: динамичный свет от взрывов и реакций
- Окружение: рассветное/закатное небо, пасторальные ландшафты Тейвата

### Композиция
- Персонажи: anime cel-shaded, чистые линии, яркие цвета
- Фон: Mondstadt (европейское средневековье), Liyue (Китай), Inazuma (Япония), Sumeru (Ближний Восток + тропики), Fontaine (Франция), Natlan (Мезоамерика), Snezhnaya (Россия)
- Вертикальная 9:16, mobile-first

### Стилистические ограничения
- **Anime cel-shading** — не реализм, не Pixar 3D
- Яркие насыщенные цвета, мягкие контуры
- Персонажи часто изящные/стройные, с выраженными аниме-чертами
- Элементальные символы и эффекты как часть визуальной идентичности

### Prompt prefix
```
Genshin Impact anime style, cel-shaded character art, vibrant fantasy colors, soft outline anime aesthetic, magical elemental effects, Teyvat world environment, clean detailed character illustration
```

> ⚠️ Это **базовый** house-style игры — fallback, используется только если в `{format}_story_bible.json` не задан top-level `style_tags`. Scenarist берёт стиль из story bible в первую очередь, и только при его отсутствии — отсюда.

---

## Нации Тейвата

| Нация | Архонт | Элемент | Вдохновение |
|-------|--------|---------|-------------|
| Mondstadt | Barbatos (Venti) | Anemo | Германия / Средневековая Европа |
| Liyue | Morax (Zhongli) | Geo | Китай |
| Inazuma | Ei (Raiden Shogun) | Electro | Япония |
| Sumeru | Nahida (Kusanali) | Dendro | Ближний Восток + Южная Азия |
| Fontaine | Focalors (Furina) | Hydro | Франция / Belle Époque |
| Natlan | Pyro Archon (Mavuika) | Pyro | Мезоамерика |
| Snezhnaya | Tsaritsa | Cryo | Россия |

---

## Character appearance

Character appearance cards live in the per-format story bibles (`characters`), NOT here — the same character may look different per format, and cards must stay style-free (appearance only: anatomy, costume, props, item colors; NO render-medium/style words). Style comes from the resolved `style_tags`. Canonical Genshin roster: `character-story_story_bible.json` → `characters` (master list; other formats reference it or the scenarist copies a card on first use). Dual-style pairs (game-style / photoreal twin split preserved as the format's `style_tags`): `dual-style_story_bible.json` → `characters`. If a character has no card in the target format's bible, the scenarist writes a style-free card and adds it to that bible.

---

## Tone of Voice

- Волшебный, эпичный, эмоциональный
- Отсылки к лору Тейвата, элементальным реакциям, именам персонажей
- Смесь wonder и adventure: «Путешественник», «Примогем», «Желания»
- Язык: English (основной), Russian

### Примеры фраз
- "Every character in Genshin has a story worth knowing..."
- "Top 5 most POWERFUL characters in Teyvat!"
- "This 5-star is absolutely BROKEN in the new meta!"
- "Ты знал, что Venti — это сам Бог Ветра?"

---

## Музыка

- **Mood:** ethereal, epic, emotional
- **BPM:** 90-130
- **Рекомендуемые треки из tracks.json:** epic-orchestral, ethereal-ambient, emotional-drama

## Overlay brand

Brand styling for graphic overlays (consumed by the scenarist when filling `overlays[]`; layout comes from the format's `## Overlays` section).

- font_display: BEBAS        # titles, rank numbers, slogans, names, outcome plates
- font_label: MED            # small text: hud counter, disclaimer, hook plate
- text_color: "#FFFFFF"
- accent_color: "#F5D060"    # amber-gold stroke/accent on display overlays (matches resin icon)
- stroke_width: 6
- channel_bug_url:           # none
