---
subtitles: true
overlays: false
---

# Format "Gameplay AI Avatar" — Talking Head + Gameplay

> TODO(style-refactor): style must come from the resolved chain (story bible top-level `style_tags` → game config `prompt_prefix`); character cards are style-free. This file not yet audited for hardcoded house-style.

An AI avatar (talking head) at the bottom of the screen tells about a game offer/bonus, while gameplay plays at the top. Format for promoting offers via TikTok/Shorts.

This file is the **playbook**: when to use, concept, role briefs. Craft rules — in `rules/roles/*.md`.

---

## When to use

Keywords: "gameplay ai avatar", "ai avatar", "talking head", "offerwall", "offer", "оффер", "бонус", "bonus", "free diamonds", "free gems", "download and get", "скачай и получи".

---

## Concept

- **Avatar (talking head):** AI character at the bottom of the screen, talks about an offer
- **Gameplay:** pre-made clips from `games/{GAME_TAG}/gameplay/` at the top of the screen
- **Split-screen:** 60% gameplay (1080×1152) on top / 40% avatar (1080×768) below
- **Duration:** 25–40s
- **Budget:** up to $5 (~$1.90 typical). Stop if spend > $4.50.
- **Languages:** multilingual (MiniMax auto-detects)

### Visual layout (1080×1920, 9:16)

```
+------------------+
|                  |
|   GAMEPLAY       |  <- 60% (1080×1152)
|                  |
+------------------+
|  AI AVATAR       |  <- 40% (1080×768)
|  (talking head)  |
+------------------+
```

---

## Run parameters

| Parameter | Description | Example |
|---|---|---|
| `game_tag` | Game tag (must match the folder `games/{game_tag}/gameplay/`) | `MLBB` |
| `offer_text` | Offer description | `"Download MLBB and get 500 diamonds, reach level 10"` |
| `language` | Script and voice language (ISO code) | `EN`, `RU`, `PT-BR` |

Run format: `gameplay ai avatar: {offer_text}, {language}`

---

## Budget

| Item | Cost |
|---|---|
| Avatar ref (NB2, if not in asset bank) | $0.04 |
| MiniMax TTS (~30s) | ~$0.003 |
| Kling Avatar v2 Standard (~30s) | ~$1.68 |
| Gameplay (pre-made clips) | $0 |
| FFmpeg, music (local) | $0 |
| **Typical** | **~$1.90** |

---

## Script structure: Hook → Offer → Proof → CTA

| Section | Time | What the avatar says | What's on the gameplay |
|---|---|---|---|
| **HOOK** | 0–5s | Shock/paradox, scroll stopper | Most epic moment |
| **OFFER** | 5–15s | Concretely, simply explain the offer | Beautiful gameplay, leveling |
| **PROOF** | 15–25s | Social proof — "I already got…" | Gameplay with rewards |
| **CTA** | 25–35s | Call to action with urgency | Final epic moment |

### Screenwriting rules

**Tone:** energetic, brainrot-friendly, like a friend sharing a lifehack. Framing "I found this and I'm sharing", not corporate ad.

**Required elements:**
- Concrete numbers in every video ("500 diamonds", "level 10", "3 days")
- Urgency/deadline ("before they remove it", "only this week")
- Social proof ("I already got…", "everyone's doing this")
- Question or paradox in the hook ("Why is nobody talking about this?")
- First-person — "I found this…", "I already got…"

**Forbidden:**
- Corporate tone ("we recommend")
- Long sentences (max 15–20 words)
- Abstraction without specifics ("get cool stuff" → "get 500 free diamonds")
- Boring hook ("Hey guys, today I want to tell you about…")

### Hook examples

**EN:** "Why is NOBODY talking about this free diamond glitch?" / "They're literally paying you to play this game right now" / "Stop scrolling — this offer expires tomorrow"

**RU:** "Почему никто не говорит про эту халяву с алмазами?" / "Мне буквально заплатили за то что я играю" / "Стоп скроллинг — этот оффер заканчивается завтра"

---

## Storyboard Schema

```json
{
  "format": "gameplay-ai-avatar",
  "game_tag": "MLBB",
  "language": "EN",
  "offer": {
    "game_name": "Mobile Legends: Bang Bang",
    "bonus": "500 diamonds",
    "condition": "reach level 10",
    "urgency": "limited time offer"
  },
  "avatar": {
    "ref_url": "https://supabase.../avatars/MLBB/avatar-ref.png",
    "character_description": "Young male gamer, 20s, wearing headphones around neck, casual hoodie, friendly smile, well-lit room background",
    "voice": "Determined_Man",
    "prompt": "energetic gaming blogger speaking to camera, natural hand gestures, nodding",
    "source": "asset_bank"
  },
  "script": {
    "hook": "Yo, why is NOBODY talking about this? They're literally giving away 500 free diamonds right now!",
    "offer": "All you gotta do is download Mobile Legends through the link in my bio, play until level 10, and boom — 500 diamonds.",
    "proof": "I already got mine yesterday, look — spent them all on the new Lancelot skin. Not a drill, it actually works.",
    "cta": "Link in bio, go go go! But hurry, they could remove this any day now."
  },
  "gameplay_clips": ["games/MLBB/gameplay/epic-moment-1.mp4"],
  "total_duration_sec": 30
}
```

---

## Avatar consistency (asset bank)

**One avatar = one game.** The avatar is generated ONCE and reused across all videos for that game — viewers recognize the "blogger".

### Order

1. **Check asset bank:** `GET /rest/v1/game_assets?game_tag=eq.{GAME_TAG}&asset_type=eq.avatar_ref&select=*`
2. **If exists** — use `url` as `image_url` (skip generation)
3. **If not** — generate via NB2, then save to Supabase Storage (`avatars/{GAME_TAG}/avatar-ref.png`) and register in `game_assets`:
   ```sql
   INSERT INTO game_assets (game_tag, character_name, asset_type, url, prompt_block, tags)
   VALUES ('{GAME_TAG}', 'avatar', 'avatar_ref', '{PUBLIC_URL}', '{PROMPT_USED}',
           '["avatar", "gameplay-ai-avatar"]');
   ```
4. **If query fails** (timeout) — generate a new one, but **do not save** to the asset bank (to avoid duplicates)

**NEVER regenerate the avatar** if it exists in the asset bank.

---

## Two-step generation: TTS → approval → Avatar

TTS costs ~$0.17, Avatar ~$1.68. **Do NOT launch Avatar** until the voice is approved.

1. Sound generates TTS → Manager sends for approval
2. After approval → Animator launches Kling Avatar v2 with the TTS audio_url from Supabase

### 3.3 Avatar speedup (mandatory)

Kling Avatar sounds sluggish at native speed. **Always apply 1.3x speedup** before assembly:

```bash
$FFMPEG -y -i avatar.mp4 \
  -filter_complex "[0:v]setpts=PTS/1.3[v];[0:a]atempo=1.3[a]" \
  -map "[v]" -map "[a]" \
  -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p \
  -ar 44100 -ac 2 -c:a aac -b:a 128k \
  avatar-fast.mp4

AVATAR_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 avatar-fast.mp4)
```

After this, use `avatar-fast.mp4` and `AVATAR_DUR` in all subsequent steps.
Subtitles: divide all faster_whisper timestamps by 1.3.

---

## Gameplay clip requirements

Files in `games/{GAME_TAG}/gameplay/`:

| Parameter | Requirement |
|---|---|
| Format | `.mp4` (H.264) |
| Resolution | **≥720p width**. Clips <720px are rejected (at scale=1080:-2 they smear into mush) |
| Aspect ratio | any (will be scaled to 1080×1152) |
| Duration | ≥10s (for trimming) |
| Content | epic gameplay moments, not menus/loading |

Manager validates the presence and resolution of clips in Phase 0. If folder is empty or all <720px → status `failed`, notify the user.

### Gameplay trimming

Gameplay is trimmed to Avatar duration (after 1.3x speedup). If multiple clips — pick epic moments and concat to the required length. **Keep gameplay audio** (will be at 25% volume in the final).

---

## Role briefs

### Scenarist

- Structure: Hook → Offer → Proof → CTA (see table above)
- Each section ≤20 words; hook ≤20 words + question/paradox
- Concrete numbers, urgency, social proof
- Tone: energetic, first-person; NOT corporate
- One Avatar clip per video (don't split into scenes — 30s monologue), duration = estimate at ~2.5 words/sec
- **NO title cards / brainrot tags** — only drawtext subtitles at the split-screen seam
- General rules — `rules/roles/scenarist.md`

### Storyboarder

- Avatar ref — semi-realistic style (not cartoon, not photorealistic)
- Portrait 3:4, upper body, looking at camera, slight smile with teeth (critical for lipsync)
- Background: cozy room with gamer setup, good lighting
- **Only if not in asset bank** — check first
- General rules — `rules/roles/storyboarder.md`

### Animator

- **Kling Avatar v2 Standard** (`fal-ai/kling-video/ai-avatar/v2/standard`) — one clip for the whole video
- **`audio_url` mandatory Supabase public URL** (not fal.ai temp) — Avatar polling takes minutes
- Motion prompt: "energetic gaming blogger speaking to camera, natural hand gestures, nodding"
- **Mandatory 1.3x speedup** after Avatar generation (`setpts=PTS/1.3`, `atempo=1.3`) — at native speed it's sluggish
- After speedup: `AVATAR_DUR = ffprobe duration` — used to trim gameplay
- General rules — `rules/roles/animator.md`

### Sound

- TTS via fal.ai MiniMax — `voice_setting.voice_id`, `emotion` per tone, field is `prompt` not `text`
- Male deep voices: `Deep_Voice_Man`, `Determined_Man`, `Imposing_Manner`, `Elegant_Man`, `Patient_Man`
- **Subtitles: drawtext + faster_whisper** (not PIL PNG — this format uses ffmpeg-full with libfreetype)
  - Font: Montserrat Bold 42px (`/Users/admin/Library/Fonts/Montserrat-Bold.ttf`)
  - Background: opaque black bar `y=1100, h=104` (drawbox)
  - Position: `y=1122` (at the split-screen seam)
  - Accent: every 5th segment in yellow
  - Segments of 3–4 words, `start[N] = max(end[N-1], orig_start)` (anti-overlap)
- **Transcribe `avatar-fast.mp3` (already 1.3x sped up)** — timestamps are correct out-of-the-box
- Background music (optional) — `volume=0.10` (quiet bg)
- General rules — `rules/roles/sound.md`

### Editor

- **Split-screen:** `scale + crop`, never `pad`
  - Gameplay: `scale=1080:-2,crop=1080:1152:0:(ih-1152)/2` (removes top and bottom UI)
  - Avatar: `scale=1080:-2,crop=1080:768:0:0` (face stays, bottom is cropped)
  - `vstack=inputs=2` (gameplay top, avatar bottom) = 1080×1920
- **Audio mix:** Avatar voice 100%, gameplay 25% (background); `amix=inputs=2:duration=first`
- If gameplay has no audio track — Avatar audio only
- `-r 30` unified fps; final **strictly 1080×1920** (`ffprobe` to verify)
- Music (if any): `volume=0.10`, `amix` with main audio; NEVER `-shortest`
- General rules — `rules/roles/editor.md`

1. Upload `final.mp4` to Supabase Storage: `videos/{GAME_TAG}/{TIMESTAMP}_final.mp4`
2. Show cost report
3. Show final duration

---

## Budget

| Item | Cost |
|--------|-----------|
| Avatar ref (Nano Banana 2) | $0.04 (or $0 from asset bank/user provided) |
| MiniMax TTS (~30s) | ~$0.003 |
| Kling Avatar v2 Standard (30s) | ~$1.68 |
| Gameplay (pre-made clips) | $0.00 |
| FFmpeg (local) | $0.00 |
| Music (local) | $0.00 |
| **Typical** | **~$1.90** |

**Limit:** $5.00. Stop if spend > $4.50.

---

## Validation (checklist before generation)

Before launching PHASE 3, verify:

- [ ] `games/{GAME_TAG}/gameplay/` contains at least 1 `.mp4`
- [ ] Script contains all 4 sections: hook, offer, proof, cta
- [ ] Hook ≤ 20 words, contains a question or paradox
- [ ] Each section ≤ 20 words
- [ ] Concrete numbers (bonus amount, level)
- [ ] Urgency/deadline present
- [ ] Social proof present
- [ ] No corporate tone / direct ad
- [ ] `voice` (name, NOT voice_id hash) selected and matches `language`
- [ ] `prompt` for Kling Avatar v2 filled (motion description)
- [ ] Avatar ref checked in asset bank (or new one generated)
- [ ] Total script duration 25-40s (estimate: ~2.5 words/sec)
- [ ] Budget will not exceed $5.00

---

## Anti-patterns

**Do NOT:**
- **DO NOT use Kokoro TTS or ElevenLabs** — only MiniMax via fal.ai
- **Field is `prompt`, NOT `text`** — using `text` causes silent failure (empty audio)
- **DO NOT generate avatar video without an approved voice** — TTS first, approval, then lipsync
- **DO NOT use `pad`** in split-screen — only `scale + crop`, no black bars
- **DO NOT crop avatar by center** — crop from bottom (`crop=W:H:0:0`) so the face is not affected
- Do not generate a new avatar if it's already in the asset bank
- Do not compress gameplay below 720p — quality loss is visible in split-screen
- Do not forget to normalize fps to 30 before split-screen
- Do not use `-shortest` when overlaying music

---

## Output files

```
output/YYYY-MM-DD/{GAME_TAG}/gameplay-ai-avatar/
├── storyboard.json
├── scenes/refs/avatar-ref.png (only if generated)
├── tts-output.mp3
├── avatar.mp4                  # raw Kling Avatar
├── avatar-fast.mp4             # 1.3x speedup
├── gameplay-trimmed.mp4        # gameplay trimmed to AVATAR_DUR
├── subs.srt                    # subtitles (faster_whisper)
├── assembled.mp4               # split-screen without subtitles
└── final.mp4                   # with subtitles + (opt.) music
```

After upload: `videos/{GAME_TAG}/{TIMESTAMP}_final.mp4` in Supabase.

---

## Validation before publishing

- [ ] `games/{GAME_TAG}/gameplay/` contains ≥1 `.mp4`, all clips ≥720p width
- [ ] Script has all 4 sections (hook, offer, proof, cta)
- [ ] Hook ≤20 words, with question/paradox
- [ ] Each section ≤20 words; numbers, urgency, social proof present
- [ ] `voice` (name, not `voice_id`) matches `language`
- [ ] Avatar ref checked in asset bank (reused if present)
- [ ] TTS approved by user BEFORE launching Avatar
- [ ] Avatar sped up 1.3x before assembly
- [ ] fps normalized to 30 before split-screen
- [ ] Final 1080×1920, 30 fps, AAC 128k stereo (`ffprobe`)
- [ ] Subtitles drawtext, no overlap, yellow accent every 5th
- [ ] Budget < $5

---

## Anti-patterns

- ❌ Kokoro TTS, ElevenLabs — only MiniMax via fal.ai
- ❌ `voice_id` hash — use `voice` name string
- ❌ Launching Avatar without approved TTS ($1.68 wasted on an unapproved voice)
- ❌ Re-generating avatar when present in the asset bank
- ❌ `pad` in split-screen (only `scale + crop`, no black bars)
- ❌ Avatar crop by center (only `crop=W:H:0:0` so the face is not affected)
- ❌ Gameplay clips <720p (will be mushy at scale=1080)
- ❌ Forgetting 1.3x speedup (Avatar sounds sluggish)
- ❌ Forgetting fps normalize to 30 before split-screen
- ❌ `-shortest` when overlaying music
- ❌ PIL PNG subtitles (this format uses drawtext, not PIL)
