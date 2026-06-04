#!/bin/bash
# Schedules 6 Starfleet Archives videos for daily publication at 23:00 MSK (20:00 UTC)
# starting from 2026-06-03.
#
# Run once — uploads all 6 as "private + scheduled", YouTube auto-publishes at the set time.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
ATTACHMENTS="${REPO_ROOT}/.context/attachments"

SUPABASE_URL="https://txckerrkubbvmzlionjf.supabase.co"
SUPABASE_KEY=$(grep SUPABASE_SERVICE_ROLE_KEY "${REPO_ROOT}/video-agent/.env" | cut -d= -f2-)

log_youtube() {
  local GAME_TAG="$1" IDEA="$2" FORMAT="$3" VIDEO_URL="$4" YOUTUBE_URL="$5"
  curl -s -X POST "${SUPABASE_URL}/rest/v1/video_agent_runs" \
    -H "apikey: ${SUPABASE_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_KEY}" \
    -H "Content-Type: application/json" \
    -H "Prefer: resolution=merge-duplicates,return=minimal" \
    -d "{
      \"game_tag\": \"${GAME_TAG}\",
      \"input_idea\": \"${IDEA}\",
      \"format\": \"${FORMAT}\",
      \"output_video_url\": \"${VIDEO_URL}\",
      \"youtube_url\": \"${YOUTUBE_URL}\",
      \"status\": \"completed\"
    }" > /dev/null
}

upload_scheduled() {
  local ATTACHMENT_ID="$1" TITLE="$2" DESCRIPTION="$3" TAGS="$4"
  local PUBLISH_AT="$5" FORMAT="$6" SUPABASE_VIDEO_URL="$7"
  local VIDEO_PATH="${ATTACHMENTS}/${ATTACHMENT_ID}/final.mp4"

  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  Uploading: ${TITLE}"
  echo "  Schedule:  ${PUBLISH_AT}"
  echo "  File:      ${VIDEO_PATH}"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  YOUTUBE_URL=$("${SCRIPT_DIR}/youtube-upload.sh" \
    --channel gamepulse \
    --publish-at "${PUBLISH_AT}" \
    "${VIDEO_PATH}" \
    "${TITLE}" \
    "${DESCRIPTION}" \
    "private" \
    "${TAGS}" | tail -1)

  echo "  → ${YOUTUBE_URL}"

  # Log to Supabase
  log_youtube "star-trek-timelines" "${TITLE}" "${FORMAT}" "${SUPABASE_VIDEO_URL}" "${YOUTUBE_URL}"
  echo "  ✓ Logged to Supabase"
}

# ── Video 1 ─────────────────────────────────────────────────────────────────
upload_scheduled \
  "0G2Hr8" \
  "Nyota Uhura — Character Story | Star Trek Timelines" \
  "She heard the galaxy's last transmission — and answered. Nyota Uhura's story in Star Trek Timelines. 🖖

#StarTrek #StarTrekTimelines #Uhura #CharacterStory #StarfleetArchives" \
  "star trek,star trek timelines,uhura,nyota uhura,character story,sci-fi,gaming,starfleet archives" \
  "2026-06-03T20:00:00Z" \
  "character-story" \
  "https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/videos/star-trek-timelines/2026-05-23/character-story_final.mp4"

# ── Video 2 ─────────────────────────────────────────────────────────────────
upload_scheduled \
  "jn8exT" \
  "Dr. Carol Marcus — Character Story | Star Trek Timelines" \
  "She created life from nothing — the Genesis Device changed the galaxy forever. Dr. Carol Marcus's story in Star Trek Timelines. 🖖

#StarTrek #StarTrekTimelines #CarolMarcus #CharacterStory #StarfleetArchives" \
  "star trek,star trek timelines,carol marcus,character story,sci-fi,gaming,starfleet archives" \
  "2026-06-04T20:00:00Z" \
  "character-story" \
  "https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/videos/star-trek-timelines/2026-05-26/character-story_final.mp4"

# ── Video 3 ─────────────────────────────────────────────────────────────────
upload_scheduled \
  "7k3OuO" \
  "TOP 5 Women of Star Trek | Star Trek Timelines" \
  "Five iconic women shaped the galaxy — but who tops the list? Our ranking of the most legendary women in Star Trek Timelines. 🖖

#StarTrek #StarTrekTimelines #TopList #WomenOfStarTrek #StarfleetArchives" \
  "star trek,star trek timelines,top 5,women of star trek,top list,sci-fi,gaming,starfleet archives" \
  "2026-06-05T20:00:00Z" \
  "top-list" \
  "https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/videos/star-trek-timelines/2026-05-26/top-list_final.mp4"

# ── Video 4 ─────────────────────────────────────────────────────────────────
upload_scheduled \
  "uVJtpL" \
  "Capt. Jonathan Archer — Character Story | Star Trek Timelines" \
  "Before Kirk. Before Picard. There was Archer — the man who built the Federation. Captain Jonathan Archer's story in Star Trek Timelines. 🖖

#StarTrek #StarTrekTimelines #Archer #JonathanArcher #CharacterStory #StarfleetArchives" \
  "star trek,star trek timelines,archer,jonathan archer,captain archer,character story,sci-fi,gaming,starfleet archives" \
  "2026-06-06T20:00:00Z" \
  "character-story" \
  "https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/videos/star-trek-timelines/2026-05-27/character-story-archer_final.mp4"

# ── Video 5 ─────────────────────────────────────────────────────────────────
upload_scheduled \
  "M68zUk" \
  "TOP 5 Star Trek Ships | Star Trek Timelines" \
  "Five legendary starships — which one defined the franchise? Our ranking of the most iconic Star Trek vessels in Star Trek Timelines. 🖖

#StarTrek #StarTrekTimelines #TopList #Starships #EnterpriseNCC1701 #StarfleetArchives" \
  "star trek,star trek timelines,top 5,star trek ships,starships,enterprise,sci-fi,gaming,starfleet archives" \
  "2026-06-07T20:00:00Z" \
  "top-list" \
  "https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/videos/star-trek-timelines/2026-05-28/top-list_final.mp4"

# ── Video 6 ─────────────────────────────────────────────────────────────────
upload_scheduled \
  "0pfTFn" \
  "Battle of Wolf 359 — Survival Chance: 2% | In-Game POV" \
  "You're on the USS Saratoga. The Borg cube is already here. Can you survive Wolf 359? In-Game POV | Star Trek Timelines. 🖖

#StarTrek #StarTrekTimelines #BattleOfWolf359 #Borg #InGamePOV #StarfleetArchives" \
  "star trek,star trek timelines,battle of wolf 359,borg,in-game pov,sci-fi,gaming,starfleet archives" \
  "2026-06-08T20:00:00Z" \
  "in-game-pov" \
  "https://txckerrkubbvmzlionjf.supabase.co/storage/v1/object/public/videos/star-trek-timelines/2026-06-01/in-game-pov-v2_final.mp4"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  All 6 videos scheduled! 🖖"
echo "  Publishing daily at 23:00 MSK (20:00 UTC)"
echo "  Jun 3 → Jun 8"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
