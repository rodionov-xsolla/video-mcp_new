#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

source ../.env

BASE="${SUPABASE_URL}/storage/v1/object/music"

upload() {
  local file="$1"
  local name="$2"
  local ct="$3"
  echo -n "Uploading $name... "
  HTTP=$(curl -s -w "%{http_code}" -o /dev/null -X PUT \
    "${BASE}/${name}" \
    -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
    -H "Content-Type: $ct" \
    -H "x-upsert: true" \
    --data-binary "@${file}")
  echo "$HTTP"
}

upload "Badass/badass-alucinante.mp3" "badass-alucinante.mp3" "audio/mpeg"
upload "Badass/badass-brodyaga-phonk.mp3" "badass-brodyaga-phonk.mp3" "audio/mpeg"
upload "Dark/dark-28-days-later.mp3" "dark-28-days-later.mp3" "audio/mpeg"
upload "Dark/dark-crystal-castles.mp3" "dark-crystal-castles.mp3" "audio/mpeg"
upload "Dark/dark-gesaffelstein-night-tower.m4a" "dark-gesaffelstein-night-tower.m4a" "audio/mp4"
upload "Emotional sad/emotional-3am-walk.mp3" "emotional-3am-walk.mp3" "audio/mpeg"
upload "Emotional sad/emotional-after-dark-sweater.mp3" "emotional-after-dark-sweater.mp3" "audio/mpeg"
upload "Emotional sad/emotional-u-kamina.mp3" "emotional-u-kamina.mp3" "audio/mpeg"
upload "Energetic/energetic-she-knows.mp3" "energetic-she-knows.mp3" "audio/mpeg"
upload "Energetic/energetic-simulacao.mp3" "energetic-simulacao.mp3" "audio/mpeg"
upload "Energetic/energetic-kompa-pasion.mp3" "energetic-kompa-pasion.mp3" "audio/mpeg"
upload "Fun/fun-central-cee-doja.m4a" "fun-central-cee-doja.m4a" "audio/mp4"
upload "Fun/fun-robot-rock-funk.mp3" "fun-robot-rock-funk.mp3" "audio/mpeg"
upload "Heroic/heroic-neptune.mp3" "heroic-neptune.mp3" "audio/mpeg"
upload "Heroic/heroic-royalty-slowed.mp3" "heroic-royalty-slowed.mp3" "audio/mpeg"

echo "Done! All 15 tracks uploaded."
