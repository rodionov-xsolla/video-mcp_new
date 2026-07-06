# MLBB (Mobile Legends: Bang Bang)

> TODO(style-refactor): character appearance must move to per-format story bibles `characters[]` (style-free); style → top-level `style_tags` in the bible, fallback = `prompt_prefix`. This game config not yet migrated (see star-trek-timelines / genshin-impact for the pattern).

## Метаданные

- **Жанр:** MOBA
- **Платформа:** Mobile
- **Аудитория:** Southeast Asia, Россия, LATAM
- **Стиль арта:** Anime/fantasy, яркие цвета, динамичные позы

---

## Visual Style Guide

### Цветовая палитра
- Основные: deep blue (#1a237e), gold (#ffd700), crimson (#dc143c)
- Акценты: электрический синий (#00bcd4), пурпурный (#9c27b0)

### Освещение
- Драматичное, hero spotlight
- Эффекты магии/энергии — свечение, частицы

### Композиция
- Персонаж в центре, крупный план
- Вертикальная 9:16, mobile-first
- Фон: battlefield, мистические леса, древние храмы

### Prompt prefix
```
MLBB Mobile Legends style, anime aesthetic, vibrant saturated colors, dramatic hero lighting, fantasy battle atmosphere, high detail character art
```

---

## Герои для промптов

| Герой | Роль | Визуальные ключи |
|-------|------|------------------|
| Lancelot | Assassin | Серебряный меч, синий плащ, быстрые движения |
| Fanny | Assassin | Тросы, воздушные атаки, динамичные полёты |
| Chou | Fighter | Боевые искусства, удары ногами, энергетические волны |
| Gusion | Assassin | Магические кинжалы, мистическая энергия |
| Ling | Assassin | Меч, прыжки по стенам, лунный свет |
| Benedetta | Assassin | Меч испанского стиля, элегантные атаки |
| Kagura | Mage | Японский зонтик, цветы сакуры |
| Esmeralda | Mage/Tank | Щиты, магическая энергия, кристаллы |
| Wanwan | Marksman | Маленькая, быстрая, световые стрелы |
| Aamon | Assassin | Невидимость, тёмная магия, кристаллы |

---

## Tone of Voice

- Энергичный, соревновательный, хайповый
- Короткие панчлайны
- Игровой сленг приветствуется ("MVP", "savage", "манёвр", "push rank")
- Восклицательные знаки, динамика
- Язык: English (основной), Russian

### Примеры фраз
- "This hero is absolutely BROKEN right now!"
- "Top 5 heroes that will carry you to Mythic!"
- "You WON'T believe this Lancelot combo!"

---

## Character Prompt Blocks

Готовые `character_description` для вставки в visual_identity. Копируй дословно.

### Lancelot
`male warrior assassin Lancelot, silver armor with intricate blue engravings, flowing royal blue cape, gleaming silver rapier, athletic build, spiky silver-blue hair, confident piercing gaze`

### Fanny
`female assassin Fanny, dark purple and silver battle suit, twin steel cables attached to wrists, short dark hair with purple streaks, athletic agile build, fierce determined expression`

### Chou
`male martial artist fighter Chou, white and gold martial arts outfit with dragon motifs, red headband, athletic muscular build, black spiky hair, determined fierce expression, fighting stance`

### Gusion
`male assassin mage Gusion, dark red and gold ornate coat, multiple floating magical daggers, slicked-back dark hair, sharp handsome features, confident arrogant smirk`

### Ling
`male assassin Ling, traditional Chinese white and cyan warrior outfit, long elegant sword, long flowing black hair in ponytail, lean athletic build, calm focused expression`

### Benedetta
`female assassin Benedetta, Spanish-style dark red and black fencing outfit, ornate rapier, long flowing black hair, elegant athletic build, graceful confident pose`

### Kagura
`female mage Kagura, traditional Japanese pink and white kimono, magical cherry blossom umbrella, long dark hair with flower ornaments, petite build, gentle mysterious smile`

### Esmeralda
`female mage tank Esmeralda, flowing purple and gold mystical dress, twin magical shields, long wavy dark hair with golden accessories, elegant build, powerful commanding gaze`

### Wanwan
`female marksman Wanwan, orange and white Chinese warrior outfit, small dual crossbows, twin buns hairstyle with ribbons, small petite build, playful mischievous grin`

### Aamon
`male assassin mage Aamon, dark crystalline armor with glowing purple edges, floating dark crystals around him, pale skin, slicked-back white hair, cold calculating expression`

---

## Музыка

- **Mood:** epic, energetic
- **BPM:** 130-160
- **Рекомендуемые треки из tracks.json:** epic-gaming-beat, upbeat-action
