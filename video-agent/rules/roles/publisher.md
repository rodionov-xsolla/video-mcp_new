# Publisher — posting to TikTok / Instagram via mobile-mcp + YouTube scheduling

Executed by the **main agent** (not a sub-agent): phone MCP tools are only available in the main session. Triggered by a user command in chat:

| Command | Platform | `--platform` | Mode |
|---|---|---|---|
| "Publish to TikTok" | TikTok | `tt` | **post-now** (no in-app scheduler) |
| "Publish to Instagram" | Instagram | `inst` | **post-now** (Reels). Native scheduler exists but requires a Professional account — post immediately by default |

Phone is **Android**, connected via USB. Post **one video per call**.

## Phone accounts ↔ game_tag (important!)

Multiple accounts exist in the same app on the phone. Only post the video matching the target account's game_tag, and always post from that account. `fetch-for-publish.sh` is always called with `--game <game_tag>`; verify the correct account is active in the app before posting.

| `--game` (game_tag) | TikTok account | Instagram account |
|---|---|---|
| `star-trek-timelines` | **starfleet archives** (@game_pulse0) | **lookscool1337** |
| `genshin-impact` | **genshin snap** | **game_pulse.gg** |

The user's command specifies the account, e.g. "Publish to TikTok **starfleet**" or "… **genshin**". If no account is named and multiple game_tags are in the queue — ask the user. game_tags without a phone account (e.g. `wwe-champions`, `roblox`) are **not published** — inform the user and stop.

## Architecture

mobile-mcp controls only the phone UI and **does not transfer files**. Video lives in Supabase Storage. Flow: `fetch-for-publish.sh` downloads the video and pushes it to the phone gallery via adb; then mobile-mcp selects it in the app.

## Pre-flight

1. `bash video-agent/queue/fetch-for-publish.sh` checks for adb and an authorized device on its own. But before posting, verify the phone is visible: `~/Library/Android/platform-tools/adb devices -l` → status `device` (not `unauthorized` / empty). If empty — ask the user to enable USB Debugging and accept the RSA prompt on the phone.
2. `mobile_list_available_devices` — phone must be in the list. (The `mobile-mcp` server is only picked up after restarting the Claude Code session.)

## Step 1 — fetch the video and push to phone

```bash
bash video-agent/queue/fetch-for-publish.sh --platform tt --game <game_tag>   # tt|inst
# e.g.: --game star-trek-timelines  (starfleet archives)
#        --game genshin-impact       (genshin snap)
```

- `--game` is required — it ensures the clip goes to the correct account.
- If output contains `NOTHING_TO_PUBLISH=1` — tell the user there are no unpublished videos for this game_tag and stop.
- Otherwise parse from stdout: `VIDEO_URL`, `DEVICE_PATH`, `CAPTION_SOURCE`, `GAME_TAG`, `FORMAT`. `VIDEO_URL` is needed in step 4.

## Step 2 — generate caption (at publish time, per platform)

Base: `CAPTION_SOURCE` (input_idea) + `GAME_TAG` / `FORMAT`. Write the caption yourself:
- **TikTok:** short punchy hook (1 line) + 3–5 TikTok-style hashtags (`#fyp` is fine), mention the game.
- **Instagram (Reels):** slightly more descriptive (1–2 lines) + IG hashtags, no `#fyp`.

Don't use `input_idea` verbatim — rewrite it for the platform. Emojis in moderation.

## Step 3 — navigate through the app UI (mobile-mcp)

General approach: **never hardcode coordinates**. On each screen: `mobile_list_elements_on_screen` first, find the target element by text/description, click at its center with `mobile_click_on_screen_at_coordinates`. After key steps — `mobile_take_screenshot` for self-check. Enter text with `mobile_type_keys`. System back navigation — `mobile_press_button` (BACK).

### TikTok (post-now)

1. `mobile_launch_app` TikTok (package usually `com.zhiliaoapp.musically`; confirm via `mobile_list_apps`).
2. **Verify active account** (multiple on the phone!). Profile tab → `mobile_list_elements_on_screen` → read account name at the top. If it's not the target account (per mapping table) — tap the name/account switcher and select the correct one (**starfleet archives** for `star-trek-timelines`, **genshin snap** for `genshin-impact`). `mobile_take_screenshot` to confirm the right account is active **before** uploading.
3. Bottom bar → **+** button (create).
4. Switch to the **Upload** tab → select the freshly pushed video (newest in gallery, `DEVICE_PATH`). → Next.
5. On the publish screen: tap the caption field → `mobile_type_keys` (caption from step 2).
6. Tap **Post**. Wait for the profile/feed screen as confirmation.

#### TikTok — coordinate fast-path (Redmi `23129RN51X`, screen 720×1650)

These coordinates were captured from a live run and are stable for this device + current TikTok version. Tap directly **without** `mobile_list_elements_on_screen`/screenshots at each step. Wait 2–5s between steps. Screenshots only at two checkpoints (marked 📸). If the screen doesn't match expectations — fall back to reading elements (coordinates may have shifted after an app update).

| # | Action | Tap (x, y) | Note |
|---|---|---|---|
| 1 | Launch TikTok | — | `mobile_launch_app com.zhiliaoapp.musically`, wait ~3s |
| 2 | **Profile** tab | `648, 1500` | 📸 verify active account (Starfleet Archives / genshin snap). Wrong one — switch via arrow next to name |
| 3 | **+** (Create) button | `360, 1485` | camera; sometimes needs a 2nd tap + `sleep 5` (first load is slow, black screen) |
| 4 | **Upload** (gallery, bottom-left) | `80, 1465` | `upload_hot_area` |
| 5 | Select **fresh video** (top-left) | `121, 377` | Recents sorted by date; just-pushed = top-left |
| 6 | Preview → **Next** | `528, 1478` | button `id/ooo` |
| 7 | Editor → **Next** | `530, 1481` | button `id/op0` |
| 8 | **Caption** field | `221, 250` | then `mobile_type_keys` (ASCII caption — emojis/dashes get mangled by adb) |
| 9 | Hide keyboard | — | `mobile_press_button BACK` |
| 10 | **More options** | `360, 1245` | open extra settings sheet |
| 11 | **AI-generated content** toggle | `640, 843` | enable (turns blue); required for AI videos |
| 12 | **Close** More options sheet | `664, 451` | X button |
| 13 | **Post** | `532, 1482` | 📸 verify before tapping: video/caption/Public/AI label. Irreversible |
| 14 | Wait for upload | — | progress spinner top-left; wait for 100%. Then run `log-publish.sh --platform tt --video-url $VIDEO_URL` |

**Network pre-flight:** TikTok here runs through VPN (`v2box`). Before posting, verify internet is actually alive (not just the tunnel is up): `adb shell ping -c 2 8.8.8.8` — packets must go through. If 100% loss / DNS doesn't resolve — the upload will stall (observed stalling at 60%); ask the user to reconnect the VPN node, **do not** set `tt_published` until the post is confirmed.

### Instagram (post-now, Reels)

1. `mobile_launch_app` Instagram (package `com.instagram.android`).
2. **Verify active account**: Profile tab (nav bar) → name at the top must be the target (**lookscool1337** for `star-trek-timelines`, **game_pulse.gg** for `genshin-impact`). 📸 If wrong — switch via arrow next to name.
3. **+** (create) → **Reel** → select newest video (first video thumbnail after the camera tile) → editor → **Next**.
4. "New reel" screen: tap "Write a caption…" field → `mobile_type_keys` (caption from step 2), confirm **OK**.
5. Enable the **Add AI label** toggle (for AI-generated videos).
6. Tap **Share**. Wait for "Posted to <account>" toast.

> ⚠️ **Instagram blocks UIAutomator** — `mobile_list_elements_on_screen` on IG screens fails with `Cannot read properties of undefined (reading 'node')`. Work **only via coordinates + screenshots** in IG, do not read elements.

#### Instagram — coordinate fast-path (Redmi `23129RN51X`, 720×1650)

Screenshots only at 📸 points. `sleep` 2–4s between steps. Coordinates from a live post-now Reel run.

| # | Action | Tap (x, y) | Note |
|---|---|---|---|
| 1 | Launch Instagram | — | `com.instagram.android`, wait ~4s |
| 2 | **Profile** tab (nav bar, far right) | `648, 1505` | 📸 verify active account per mapping table |
| 3 | **+** create (top-left) | `40, 120` | opens Create menu |
| 4 | **Reel** item (first row) | `150, 862` | |
| 5 | Select **fresh video** | `360, 630` | 1st video thumbnail (2nd column, top row; 1st cell is camera). Confirm by duration/preview |
| 6 | Reel editor → **Next →** | `646, 1515` | |
| 7 | **Caption** field | `300, 830` | then `mobile_type_keys` (ASCII). Close caption — **OK** at `662, 125` |
| 8 | **Add AI label** toggle | `662, 878` | enable (turns dark) |
| 9 | **Share** | `542, 1481` | 📸 verify before tapping. Irreversible |
| 10 | Wait for "Posted to …" toast | — | then run `log-publish.sh --platform inst --video-url $VIDEO_URL` |

**Network pre-flight (same as TikTok):** IG runs through VPN `v2box`. ICMP `ping` is **blocked** through this VPN (100% loss even when internet is working) — this is a false signal. Real check: `adb shell dumpsys connectivity | grep VALIDATED` (VPN network must be `IS_VALIDATED`) or just open IG and verify the feed loads. IG nav bar is at the same height as TikTok (`y≈1505`).

On any unexpected UI (wrong screen, login popup, steps exhausted) — `mobile_take_screenshot`, **stop and ask the user**, don't click blind.

## Step 4 — mark as published in Supabase

Only after actual success in the app:

```bash
bash video-agent/queue/log-publish.sh --platform tt   --video-url "$VIDEO_URL"
bash video-agent/queue/log-publish.sh --platform inst --video-url "$VIDEO_URL"
```

This sets `tt_published` / `inst_published = now()`, so the next `fetch-for-publish.sh` call won't return this video (idempotency).

## Summary to user

Report: which video was published (title/URL), to which platform, post-now or scheduled (and at what time), and how many unpublished videos remain in the queue.

---

## YouTube — scheduled upload after final-video approval

Separate flow: Editor first returns a technically valid local `final.mp4`; Manager shows it to the user. Only after explicit approval does Manager upload it to Supabase and start this scheduled YouTube flow.

**No-exception rule:** no immediate publishing. Private upload with a scheduled open date only. Every upload requires explicit user confirmation — **even when debug mode is off**.

### YouTube channels ↔ game_tag

| game_tag | Public channel | `--channel` alias |
|---|---|---|
| `star-trek-timelines` | `starfleetarchive` | `starfleet` |
| `genshin-impact` | `genshinsnap` | `genshin` |

If game_tag is not in the table — inform the user that the channel is not configured and stop.

### YT step 1 — confirm approval state

Require Manager's explicit confirmation that the user approved this exact local final video. That approval is sufficient for its Supabase upload and scheduled YouTube upload; do not ask a second redundant confirmation. A direct bulk-queue command still requires the user to specify the batch.

### YT step 2 — calculate publish date

Query the target channel's existing scheduled/public videos and choose the nearest future free calendar date. Publication time is always **23:50 Moscow time (`20:50:00Z`)**. The chosen date must also satisfy: the same format is not scheduled on either adjacent calendar date (`D-1` or `D+1`). If the nearest free date violates that rule, advance one day at a time until both conditions pass. Apply the same calculation independently to every video in a batch.

### YT step 3 — fetch videos from queue

```bash
curl -sS \
  "${SUPABASE_URL}/rest/v1/video_agent_runs\
?game_tag=eq.${GAME_TAG}&yt_published=is.null&status=eq.completed\
&output_video_url=not.is.null&order=created_at.asc&limit=${N}\
&select=id,output_video_url,input_idea,format" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

If the list is empty — inform the user and stop.

### YT step 4 — download and upload

For each video in the batch:

```bash
# Download
LOCAL_PATH="/tmp/yt_upload_${i}.mp4"
curl -sSL -o "$LOCAL_PATH" "$VIDEO_URL"

# Upload (private + scheduled open date)
YOUTUBE_URL=$(bash video-agent/queue/youtube-upload.sh \
  --channel "$CHANNEL" \
  --publish-at "$PUBLISH_AT" \
  "$LOCAL_PATH" \
  "$TITLE" \
  "$DESCRIPTION" \
  "private" | tail -1)
```

- `--publish-at` — date from step 2, **always explicit** (do not omit, do not pass `now`)
- `privacy` = `"private"` always
- The script returns the YouTube URL as the last line of stdout

### YT step 5 — write to Supabase

```bash
bash video-agent/queue/log-publish.sh \
  --platform yt \
  --video-url "$SUPABASE_VIDEO_URL" \
  --publish-at "$PUBLISH_AT" \
  --youtube-url "$YOUTUBE_URL"
```

### YT step 6 — summary to user

```
Uploaded 2 videos to YouTube:
- "I Almost Quit Star Trek" → youtube.com/watch?v=xxx — goes public June 13 at 23:50 MSK
- "My teammate was a surgeon" → youtube.com/watch?v=yyy — goes public June 14 at 23:50 MSK

2 videos still in queue.
```

### Forbidden (YT)

- ❌ `--publish-at=now` — no immediate publishing
- ❌ Omitting `--publish-at` (the script will auto-pick a date via YT API — slower and ignores our Supabase queue)
- ❌ Uploading without explicit user confirmation
- ❌ Skipping the `yt_published` write to Supabase after a successful upload
