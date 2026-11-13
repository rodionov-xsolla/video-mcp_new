#!/usr/bin/env bash
# Show the ledger working: start a throwaway local database with every Supabase migration, send the
# plan's worked example through ledger.record_run(), and print what the ledger keeps after each step.
# Needs Docker only. Nothing touches a real database, and the database is deleted at the end.
#
#   ledger/demo/run.sh           # runs straight through (about 30 s)
#   ledger/demo/run.sh --pause   # waits for Enter between steps, for recording
set -euo pipefail
shopt -s nullglob

IMAGE="${LEDGER_TEST_IMAGE:-supabase/postgres:17.11.0.011}"
NAME="ledger-demo-$$"
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
PAUSE=()
[ "${1:-}" = "--pause" ] && PAUSE=(-v pause=1)

echo "XPN cost ledger demo: a fresh local database, deleted afterwards"
printf "Starting Postgres and applying supabase/migrations/ ... "
docker run -d --rm --name "$NAME" -e POSTGRES_PASSWORD=postgres -v "$REPO:/repo:ro" "$IMAGE" >/dev/null
trap 'docker rm -f "$NAME" >/dev/null 2>&1 || true' EXIT

ready=0
for _ in $(seq 1 90); do
  if docker exec -e PGPASSWORD=postgres "$NAME" psql -h localhost -U postgres -qAt -c 'select 1' >/dev/null 2>&1; then
    ready=$((ready + 1)); [ "$ready" -ge 2 ] && break
  else
    ready=0
  fi
  sleep 1
done

count=0
for f in "$REPO"/supabase/migrations/*.sql; do
  docker exec -e PGPASSWORD=postgres "$NAME" psql -h localhost -U postgres -X -q -v ON_ERROR_STOP=1 \
    -f "/repo/supabase/migrations/$(basename "$f")" >/dev/null
  count=$((count + 1))
done
echo "done ($count migrations)"

TTY=()
[ -t 0 ] && TTY=(-t)
docker exec -i ${TTY[@]+"${TTY[@]}"} -e PGPASSWORD=postgres "$NAME" \
  psql -h localhost -U postgres -X -v ON_ERROR_STOP=1 ${PAUSE[@]+"${PAUSE[@]}"} -f /repo/ledger/demo/demo.sql
