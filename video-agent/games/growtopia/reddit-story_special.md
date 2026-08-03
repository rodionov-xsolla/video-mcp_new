# Growtopia — Reddit Story format overrides

These game-specific rules override conflicting defaults in
`rules/formats/reddit-story.md`. All other Reddit Story rules remain mandatory.

## Production status and source of truth

- Status: tested and approved on 2026-07-22.
- Exact story bible: `games/growtopia/reddit-story_bible.json`.
- The story bible owns episode history and anti-repetition data.
- The first approved episode is the cousin childhood-world restoration story.

## Gameplay source contract

Growtopia uses the two permanent Supabase `gameplay_clip` rows below. This
replaces the generic requirement for files under
`games/growtopia/gameplay/`. The Editor downloads the selected clips from
Supabase; the files under `games/growtopia/assets/` are local mirrors.

| Asset | Supabase tags | Local mirror | Permanent URL |
|---|---|---|---|
| `growtopia-gameplay-01` | `gameplay,reddit-story,vertical` | `games/growtopia/assets/Growtopia 1.mp4` | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/gameplay/growtopia-01.mp4` |
| `growtopia-gameplay-02` | `gameplay,reddit-story,vertical` | `games/growtopia/assets/growtopia 2.mp4` | `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/gameplay/growtopia-02.mp4` |

- Gameplay is a visual background and is not synchronized to narration.
- Vary clip order and trim offsets meaningfully between episodes.
- Record every used source and offset in the exact story bible after approval.

## Background and CTA

- Background: `game_assets`, `character_name=location:reddit-story`,
  `asset_type=generated_ref`, tags `reddit-story-bg,bg-ref,location`.
  Permanent URL:
  `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/locations/reddit-story.png`.
- CTA: `game_assets`, `character_name=branding:cta`,
  `asset_type=generated_ref`, tags `cta,video,branding`.
  Permanent URL:
  `https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/assets/growtopia/branding/cta.mp4`.
- The CTA is appended visually only and is never voiced.

## Narrative contract

- The conflict must come from a real relationship or life circumstance.
- Growtopia is the shared place and visual background for the human story.
- Do not build an episode around mechanics-only trading or scam drama unless
  the user explicitly approves that topic.
- Agree on the topic with the user before starting production.
- Preserve a concrete relationship setup, a changing moral verdict, a human
  corrective action, and a positive or neutral-positive resolution.

## User-approved promotion override

For Growtopia Reddit Stories only, a native story-motivated sentence may say
that the narrator obtained or used **Gems through the link in bio**. This is an
explicit game-specific exception to the generic offerwall ban.

- The Gems action must solve a concrete problem already established by the
  story; it cannot be the hook or the main subject.
- Say `the link in bio`, never `my bio`.
- Never say that the narrator downloaded the game through the link.
- Never name a service, offerwall, advertiser, purchase flow, or reward
  provider.
- Never add a separate spoken CTA or direct ad language.
- The final CTA remains silent and visual only.
