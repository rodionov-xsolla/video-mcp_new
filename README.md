# Video MCP — AI Video Production Agent

Autonomous agent for generating short vertical videos (1080×1920, 9:16) for game social media channels. Built on Claude Code + fal.ai + FFmpeg + Supabase.

## How it works

```
Idea → Script → TTS Audio → Storyboard Images → Animation → Assembly → Upload
```

The agent takes a game tag and an idea, writes the script, generates character images via NB2, animates them with Kling I2V or Avatar v2, assembles the final video with FFmpeg, and uploads to Supabase.

## Stack

| Component | Provider |
|---|---|
| Images | Nano Banana 2 (`fal-ai/nano-banana-2/edit`) |
| I2V Animation | Kling v3 Standard (`fal-ai/kling-video/v3/standard/image-to-video`) |
| Lipsync Avatar | Kling Avatar v2 (`fal-ai/kling-video/ai-avatar/v2/standard`) |
| TTS (most games) | MiniMax Speech 2.8 HD (`fal-ai/minimax/speech-2.8-hd`) |
| TTS (Genshin) | Chatterbox (`fal-ai/chatterbox/text-to-speech`) |
| Assembly | FFmpeg (local) |
| Storage | Supabase Storage (`videos/`, `assets/`) |
| Task queue | Supabase `video_tasks` table |

## Quick start

```bash
cd video-agent
cp .env.example .env
# Fill in API keys: FAL_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
```

Then open Claude Code in the `video-agent/` directory and describe the video you want.

## Formats

| Format | Description |
|---|---|
| `serial-drama` | Multi-episode drama series with persistent characters and story bible |
| `gameplay-ai-avatar` | Talking head (Avatar v2 lipsync) over gameplay footage |
| `reddit-story` | Player story narrated over gameplay, Reddit-style |
| `news` | News anchor + reporter, studio format |
| `fun-news` | Satirical in-universe news with fictional stories |
| `character-story` | Lore monologue — character narrates their own backstory |
| `redcon` | Alternate-universe divergence — "what if" lore told by the alternate self |
| `what-if-real-life` | Comedy — game character stuck in mundane real-world situations |
| `dual-style` | Split cartoon vs. realistic visual style |
| `motion-dance` | Motion-control dance transfer from reference video |
| `top-list` | TOP-5 countdown of characters / locations / items |
| `streettalk` | Vox-pop street interview — reporter + 3 interviewees |
| `in-game-pov` | First-person POV survival manual — "you wake up in the game" |
| `wild-documentary` | Nature doc — game creatures as real animals, naturalist voiceover |
| `fake-ad` | Absurd fake commercial with a twist ending |

## Games supported

| game_tag | Game | YouTube channel |
|---|---|---|
| `star-trek-timelines` | Star Trek Timelines | starfleet (`--channel starfleet`) |
| `genshin-impact` | Genshin Impact | genshin (`--channel genshin`) |
| `roblox` | Roblox | — |
| `wwe-champions` | WWE Champions | — |

## Pipeline phases

| Phase | Agent | What happens |
|---|---|---|
| 0. Init | Manager | git pull, read game config + format playbook + budgets |
| 1. Script | Scenarist | writes `storyboard.json` |
| 2. Audio | Sound | TTS per dialogue clip → Supabase URLs into storyboard.json |
| 3. Images | Storyboarder | NB2 PNG per scene → Supabase URLs into storyboard.json |
| 4. Animation | Animator | Kling I2V / Avatar v2 → MP4 per scene |
| 5. Assembly | Editor | ffmpeg concat + subtitles + music + CTA → `final.mp4` → Supabase |

## YouTube upload (after generation)

After a video is generated, the agent asks how many to schedule on YouTube. Videos are uploaded as private with a scheduled open date (11:59 PM MSK / 20:59 UTC). The queue is tracked in `video_agent_runs.yt_published`.

```bash
# Upload is done via:
bash queue/youtube-upload.sh --channel starfleet --publish-at "2026-06-15T20:59:00Z" video.mp4 "Title" "Description" "private"
```

## Budget (per video)

| Format | Typical cost |
|---|---|
| serial-drama (5 Avatar clips) | ~$2.50–3.50 |
| gameplay-ai-avatar | ~$1.50–2.50 |
| reddit-story | ~$1.50–2.50 |
| character-story / redcon | ~$3.20–3.55 |
| news / fun-news / streettalk | ~$2.00–3.00 |

Hard stop: $10/video. Warn at $9.

## Project structure

```
video-agent/
├── CLAUDE.md                  # Agent entry point + orchestration rules
├── STRUCTURE.md               # File map and architecture
├── providers.json             # Active API providers
│
├── rules/
│   ├── main/                  # budgets, fallback, validation, new-format-skill
│   ├── formats/               # One playbook per format (see table above)
│   └── roles/                 # Craft rules per specialist role
│       ├── manager.md
│       ├── scenarist.md
│       ├── storyboarder.md
│       ├── animator.md
│       ├── sound.md
│       ├── editor.md
│       └── publisher.md
│
├── games/                     # Per-game configs and story bibles
├── tools/                     # API reference (fal-ai, ffmpeg)
├── music/                     # Background music by mood (Dark/, Fun/, Tense/, Neutral/)
├── queue/                     # Task queue scripts + YouTube/Supabase integration
├── prompts/                   # Sub-agent prompt templates
└── output/                    # Generated videos (gitignored media)
```
