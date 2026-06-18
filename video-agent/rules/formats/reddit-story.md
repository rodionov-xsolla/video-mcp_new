---
subtitles: true
overlays: false
---

# Format "Reddit Story" — first-person justice story over gameplay

A first-person monologue over random gameplay with word-highlight subtitles.

This format is not about gameplay mechanics alone.  
It is a **personal justice story inside a game**.

The narrator says "I", so the viewer mentally places themselves in the narrator's position.  
The story must make the viewer feel:

> "I understand him. I would feel the same. I want justice restored."

No AI-video generation.  
Only TTS + ready-made gameplay clips + FFmpeg assembly.

---

## When to use

Keywords:  
`reddit story`, `storytime`, `история игрока`, `personal story`, `narrated gameplay`, `игровая история`.

Run parameters:

- `game_tag`
- `topic` optional
- `language` — `EN` / `RU` / `PT-BR`

---

## Concept

- **Gameplay:** pre-made clips from `games/{GAME_TAG}/gameplay/`, random shuffle, not tied to text
- **Background:** static image from Supabase `game_assets` where `tags @> ['reddit-story-bg']` for this `game_tag`
- **TTS:** MiniMax via fal.ai `fal-ai/minimax/speech-2.8-hd`
- **Narrator voice:** `Determined_Man`
- **Emotion:** `neutral`
- **Speed:** `0.90`
- **Subtitles:** word-highlight via Whisper ASS, mandatory
- **Duration:** up to 60s, around 150–170 words
- **CTA:** overlay only, never voiced
- **No AI video generation:** only TTS + FFmpeg assembly
- **Budget:** $2 max, typical $0.30–0.50

---

## Core narrative principle

This format is built around **restored justice**.

The viewer must quickly understand that the narrator was:

- wrongly accused
- unfairly judged
- underestimated
- excluded
- mocked
- used
- ignored
- blamed for something more complex than it looked

The story must end positively or neutrally for the narrator.

The narrator can lose the match.  
The narrator can leave the team.  
The narrator can make a real mistake.

But the narrator **cannot end morally defeated**.

By the end, one of these must happen:

- truth becomes visible
- the narrator is cleared
- the guilty player is exposed
- the toxic player loses status
- the unfairly humiliated player is restored
- the team understands who was actually right
- the narrator keeps dignity and gains recognition

---

## Narrative structure

Fixed structure:

```text
HEADLINE → HOOK → IDENTIFICATION → INJUSTICE → PRESSURE → HUMAN ACTION → REVEAL → JUSTICE RESOLUTION
```

The story is not:

```text
problem → solution → random twist
```

The story is:

```text
I wanted something normal.
I was judged unfairly.
Pressure increased.
I acted like a real person.
The truth came out.
Justice was restored.
```

---

## Structure

| Element | Description | Dur. |
|---|---|---:|
| **headline** | Short catchy summary of the whole story — a hook that makes the viewer want to know how it happened | 1–2s |
| **hook** | A specific unfair or shocking detail that opens the story | 3–5s |
| **identification** | "I just wanted…" — human reason to care | 5–8s |
| **injustice** | Wrong accusation, humiliation, exclusion, stolen credit | 8–12s |
| **pressure** | Team, chat, friend, guild, system or timer makes it worse | 10–15s |
| **human action** | Narrator tries to fix it honestly, not perfectly | 10–15s |
| **reveal** | A fact changes the moral verdict | 8–12s |
| **justice resolution** | Hero restored, villain exposed, truth recognized | 5–8s |
| **CTA** | Fade-to-black → `Subscribe for more` | 2s |

Total TTS duration ≤ 58s.  
Final MP4 = TTS + 2s CTA ≈ 60s.

CTA is taken from Supabase `game_assets` with tags `cta` + `video`.  
If no CTA exists, fallback: fade-to-black → `SUBSCRIBE FOR MORE` drawtext for 2s.

---

## Mandatory emotional logic

Every story must answer these questions before scripting:

```text
GAME SITUATION:
Where does it happen?
Match, raid, guild, trade, tournament, dungeon, event, lobby.

MORAL NORM:
What human rule was broken?
Fairness, trust, recognition, honesty, respect, loyalty, second chance.

FALSE VERDICT:
What did others wrongly think about the narrator?
Weak, guilty, toxic, useless, cheating, trolling, selfish.

WHY VIEWER CARES:
What familiar emotion does this trigger?
Shame, unfairness, anxiety, embarrassment, anger, desire to prove yourself.

PRESSURE SOURCE:
Who makes it worse?
Team, chat, friend, guild leader, ranked system, timer, rival player.

NARRATOR FLAW:
Why is the narrator human, not perfect?
Stayed silent, panicked, misclicked, wanted approval, explained too late.

HUMAN ACTION:
What does the narrator do?
Checks replay, protects someone, stays in the match, tells the truth, takes responsibility.

REVEAL:
What fact changes the moral verdict?
Replay, repeated bug, chat log, hidden mechanic, confession, same mistake happens again.

JUSTICE RESOLUTION:
How is justice restored?
Hero cleared, villain punished, status restored, team apologizes, truth becomes public.
```

---

## Headline rules

The headline is the first thing the viewer hears and reads.  
It is a **short catchy summary of the whole story** — a hook that makes them want to watch until the end.  
It must carry the full emotional premise in one sentence: what happened, who was wronged, and that justice will follow.

Bad:

```text
This was the craziest match of my life.
```

Good:

```text
My team reported me for throwing a match I was trying to save.
```

Bad:

```text
A toxic player ruined our raid.
```

Good:

```text
The most toxic player in our raid was the only one telling the truth.
```

Bad:

```text
I found a secret item in the game.
```

Good:

```text
Everyone laughed at my item until it exposed who was lying.
```

Headline formula:

```text
[Wrong judgment] + [specific game situation] + [promise of reversal]
```

The headline is voiced and shown in subtitles.

---

## Identification rules

The narrator must start from a small human intention.

Use:

```text
I just wanted one clean match before logging off.
I only joined because my friend needed one more player.
I was trying not to embarrass myself.
I wanted to prove I belonged in the guild.
I just wanted to help a new player.
```

Avoid:

```text
I wanted to destroy everyone.
I wanted revenge.
I wanted to become the strongest.
I wanted to make them suffer.
```

The narrator should feel relatable, not power-fantasy evil.

---

## Human action rules

The resolution must happen through human action.

Allowed:

```text
I stayed in the match.
I checked the replay.
I defended the new player.
I told the truth.
I admitted my part.
I asked for one more round.
I refused to blame someone else.
I showed the chat log.
```

Avoid:

```text
A random bug solved everything.
The game magically rewarded me.
The villain randomly confessed for no reason.
The narrator simply got stronger.
```

Game mechanics can help, but they cannot replace human agency.

---

## Resolution rules

Every story must resolve the injustice.

### Positive

```text
The team apologizes.
The narrator is invited back.
The toxic player is kicked.
The stolen strategy is recognized.
The narrator wins the duel.
```

### Neutral-positive

```text
The match is lost, but the narrator is cleared.
The narrator leaves the guild, but keeps dignity.
The team does not fully apologize, but truth becomes public.
The narrator does not get the reward, but gets recognition.
```

### Social restoration

```text
The humiliated player is defended.
The group realizes who was lying.
The narrator is finally understood.
The unfair verdict is reversed.
```

Forbidden endings:

```text
The narrator remains blamed.
Nobody learns the truth.
The villain gets away with everything.
The narrator just quits sadly.
The twist only makes things worse.
The story ends in pure sad realism.
```

---

## Tone

Allowed tones:

- justice
- touching
- funny justice
- rage-to-relief
- humiliation-to-respect
- misunderstood hero
- underdog
- betrayal resolved
- soft drama
- comeback

Forbidden tones:

- hopeless
- cruel
- grim
- gore
- death drama
- revenge fantasy
- bullying without resolution
- shock for shock's sake

No deaths.  
No gore.  
No heavy cruelty.  
No real-world tragedy.

---

## Storyboard schema

```json
{
  "format": "reddit-story",
  "game_tag": "Roblox",
  "language": "EN",
  "headline": "My team reported me for throwing a match I was trying to save.",
  "narrative_text": "I only joined because my friend needed one more player... [full text]",
  "tone": "rage-to-relief",
  "game_situation": "ranked match with random teammates",
  "moral_engine": "false accusation",
  "moral_norm": "fairness",
  "false_verdict": "the narrator intentionally threw the match",
  "viewer_emotion": "being blamed for something unfairly",
  "pressure_source": "team chat and report threats",
  "narrator_flaw": "panicked and explained too late",
  "human_action": "checked replay and stayed calm",
  "reveal": "the replay showed the captain gave the wrong call",
  "justice_resolution": "the narrator is cleared and the captain loses credibility",
  "resolution_type": "neutral-positive",
  "tts": {
    "voice": "Determined_Man",
    "language_code": "en",
    "emotion": "neutral",
    "speed": 0.90
  },
  "total_duration_sec": 55,
  "cta_overlay": "Subscribe for more"
}
```

The `voice` field is the voice name, not a voice_id hash.

---

## Anti-Repetition Check

Before scripting, check:

```text
games/{GAME_TAG}/reddit-story_bible.json
```

Do not duplicate from the last 10 stories:

- moral engine
- game situation
- false verdict
- pressure source
- resolution type
- headline structure
- hook structure
- tone

Do not repeat the same tone 3 times in a row.

---

## Story bible structure

```json
{
  "game_tag": "Roblox",
  "total_stories": 0,
  "stories": [
    {
      "id": 1,
      "date": "...",
      "tone": "...",
      "game_situation": "...",
      "moral_engine": "...",
      "moral_norm": "...",
      "false_verdict": "...",
      "pressure_source": "...",
      "resolution_type": "...",
      "headline": "...",
      "output_dir": "..."
    }
  ],
  "anti_repetition": {
    "recent_moral_engines": ["..."],
    "recent_game_situations": ["..."],
    "recent_false_verdicts": ["..."],
    "recent_pressure_sources": ["..."],
    "recent_resolution_types": ["..."],
    "recent_tones": ["..."],
    "recent_hooks": ["..."],
    "banned_combos": []
  }
}
```

Updated after each video by Manager in Phase 6.  
All lists are FIFO. Keep last 10.

---

## Role briefs

### Scenarist

- Write in first person.
- Headline: short catchy summary of the whole story, one sentence. Voiced and shown in subtitles.
- `narrative_text`: conversational style.
- Sentences must be ≤15 words.
- Total text: 150–170 words.
- Structure: `HEADLINE → HOOK → IDENTIFICATION → INJUSTICE → PRESSURE → HUMAN ACTION → REVEAL → JUSTICE RESOLUTION`.
- Answer all 9 emotional logic questions before scripting.
- The narrator must be relatable, not perfect.
- Add specific details: names, ranks, items, timers, guild names, chat phrases.
- Do not write generic phrases like "cool stuff" or "bad player".
- The injustice must be clear by the first 5–7 seconds.
- The resolution must restore justice.
- CTA is overlay only, never voiced.
- No corporate tone.
- No service names.
- No direct ad language.
- Anti-repetition check via `reddit-story_bible.json`.
- General rules: `rules/roles/scenarist.md`.

---

### Storyboarder

**SKIP.**

No NB2 generation.  
Ready-made gameplay is used.

Manager checks for at least one `.mp4` in:

```text
games/{GAME_TAG}/gameplay/
```

during Phase 0.

---

### Animator

**SKIP.**

No Kling, Veo3, Runway or AI-video generation.  
Only random gameplay clips are used.

---

### Sound

- Use MiniMax via fal.ai: `fal-ai/minimax/speech-2.8-hd`.
- ElevenLabs is not used.
- Kokoro is not used.
- Narrator voice: `Determined_Man`.
- Emotion: `neutral`.
- Speed: `0.90`.
- Input text = `headline + "\n\n" + narrative_text`.
- Generate one file: `tts-output.mp3`.
- Do not generate an SRT file.
- Editor generates timings via Whisper during assembly.
- Music optional.
- Music volume: `0.05`.
- Narration must be clear.
- General rules: `rules/roles/sound.md`.

---

### Editor

Canonical layout. Do not deviate.

#### Layout 1080×1920

- **Background:** query Supabase `game_assets` where `game_tag = {GAME_TAG}` and `tags @> ['reddit-story-bg']`.
- Download background to `build/bg.png`.
- Scale background to 1080×1920.
- If not found, STOP and ask Manager to upload a background asset with tag `reddit-story-bg`.
- **Gameplay panel:** 960×1280, overlaid at `x=60`, `y=320`.
- This leaves 60px side borders and 320px top/bottom borders.
- **Subtitles:** generated via Whisper on `tts-output.mp3`.
- Subtitles are saved as `build/subs.ass`.
- Burn subtitles into the gameplay panel.
- `MarginV=520` puts subtitles inside the gameplay panel.

#### Assembly

Three-step assembly:

```text
1. Normalize gameplay.
2. Single-pass encode with background, gameplay, subtitles, TTS and music.
3. Concat CTA.
```

#### Step 1 — Normalize gameplay

Normalize each gameplay clip to 960×1280.

Use crop-to-fill.  
Never use pad.

Correct FFmpeg filter:

```text
scale=960:1280:force_original_aspect_ratio=increase,crop=960:1280
```

Optional:

```text
-ss OFFSET
```

to start gameplay from a specific timestamp.

Run Whisper on `tts-output.mp3` before step 2:

```text
build/subs.ass
```

#### Step 2 — Single-pass encode

Use:

```text
/usr/local/bin/ffmpeg-full/ffmpeg
```

Must use `ffmpeg-full` because libass is required.

Composite:

```text
[bg 1080×1920][gameplay 960×1280]overlay=x=60:y=320,ass='subs.ass',fps=30
```

Audio:

```text
TTS(apad) + bg-music(volume=0.05)
```

Use:

```text
-t TTS_DUR
```

Never use:

```text
-shortest
```

Output:

```text
build/main-final.mp4
```

#### Step 3 — Concat CTA

Query `game_assets` where:

```text
tags @> ['cta','video']
```

for this `game_tag`.

Accept any `asset_type`:

- `promo_art`
- `generated_ref`

Skip records tagged:

```text
legacy
```

Normalize CTA if needed.  
Concat:

```text
main-final.mp4 + cta-norm.mp4 → final.mp4
```

If no CTA exists, fallback:

```text
fade-to-black → SUBSCRIBE FOR MORE drawtext, 2s
```

---

## Output files

```text
output/YYYY-MM-DD/{GAME_TAG}/reddit-story/
├── storyboard.json
├── tts-output.mp3
├── gameplay-trimmed.mp4
├── assembled.mp4
├── subtitled.mp4
└── final.mp4
```

Plus update:

```text
games/{GAME_TAG}/reddit-story_bible.json
```

---

## Validation

### Assets

- [ ] `games/{GAME_TAG}/gameplay/` contains at least one `.mp4`.
- [ ] Supabase has background asset with tag `reddit-story-bg`.
- [ ] CTA asset exists or fallback CTA is generated.

### Script

- [ ] `headline` is one sentence — short catchy summary of the whole story.
- [ ] `headline` contains a moral hook (wrong judgment + game situation + promise of reversal).
- [ ] Story is first-person.
- [ ] Text is 150–170 words.
- [ ] All sentences are ≤15 words.
- [ ] The injustice is clear in the first 5–7 seconds.
- [ ] The narrator has a relatable human intention.
- [ ] The narrator is not perfect.
- [ ] There is a clear false verdict.
- [ ] There is social pressure.
- [ ] The narrator takes human action.
- [ ] The reveal changes the moral verdict.
- [ ] Justice is restored.
- [ ] Ending is positive or neutral-positive for the narrator.
- [ ] CTA is overlay only.
- [ ] CTA is not voiced.
- [ ] No direct ad language.
- [ ] No service names.
- [ ] No deaths, gore or grim cruelty.

### Anti-repetition

- [ ] `moral_engine` does not duplicate recent stories.
- [ ] `false_verdict` does not duplicate recent stories.
- [ ] `pressure_source` does not duplicate recent stories.
- [ ] `headline` and `hook` are not similar to the last 10.
- [ ] Same tone is not repeated 3 times in a row.
- [ ] `reddit-story_bible.json` is updated after video generation.

### Technical

- [ ] Voice = `Determined_Man`.
- [ ] TTS generated via MiniMax fal.ai.
- [ ] Whisper ASS subtitles generated by Editor.
- [ ] Gameplay normalized to 960×1280.
- [ ] Crop-to-fill is used.
- [ ] No black bars.
- [ ] `ffmpeg-full` is used.
- [ ] `apad + -t` is used.
- [ ] `-shortest` is not used.
- [ ] Final duration ≤60s.
- [ ] Budget ≤$2.

---

## Anti-patterns

### Narrative anti-patterns

- ❌ Story about gameplay mechanics only.
- ❌ No moral injustice.
- ❌ No false verdict.
- ❌ Narrator is a perfect victim with no human flaw.
- ❌ Villain is evil for no reason.
- ❌ Everyone is toxic just because.
- ❌ Twist does not change the moral verdict.
- ❌ Ending leaves narrator blamed.
- ❌ Villain gets away with everything.
- ❌ Story ends in pure sad realism.
- ❌ Hero only wins because of power-up or random event.
- ❌ Revenge fantasy.
- ❌ Death, gore, grim cruelty.
- ❌ Bullying without resolution.
- ❌ Corporate tone.
- ❌ Voiced CTA.
- ❌ Offerwall integration of any kind.

### Technical anti-patterns

- ❌ ElevenLabs or Kokoro.
- ❌ AI-video generation.
- ❌ Hardcoding a game-specific background URL.
- ❌ Normalizing gameplay to 1080×810.
- ❌ Padding gameplay with black bars.
- ❌ Tying gameplay to text.
- ❌ Using `-shortest`.
- ❌ Repeating hooks from the last 10.
- ❌ Sentences longer than 15 words.

---

## One-line generator instruction

```text
Do not write a story about a game.
Write a first-person story about an unfair verdict inside a game.
The narrator is the viewer's avatar.
The injustice must be resolved by the end.
```
