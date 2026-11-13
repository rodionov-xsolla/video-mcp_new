#!/usr/bin/env bash
# Apply every migration in supabase/migrations/ (the project's existing ones, then the ledger's) to
# a fresh, throwaway Supabase Postgres container and run the pgTAP tests in ledger/tests/*.sql.
# Needs Docker only; nothing touches a real database.
#
#   ledger/tests/run.sh            # all tests
#   ledger/tests/run.sh 03         # only test files whose name contains "03"
#
# LEDGER_TEST_IMAGE overrides the image (default: the one the tests were written against).
set -euo pipefail
shopt -s nullglob

IMAGE="${LEDGER_TEST_IMAGE:-supabase/postgres:17.11.0.011}"
NAME="ledger-test-$$"
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
FILTER="${1:-}"

docker run -d --rm --name "$NAME" -e POSTGRES_PASSWORD=postgres \
  -v "$REPO:/repo:ro" "$IMAGE" >/dev/null
trap 'docker rm -f "$NAME" >/dev/null 2>&1 || true' EXIT

psql_in() {
  docker exec -i -e PGPASSWORD=postgres "$NAME" \
    psql -h localhost -U postgres -d postgres -X -v ON_ERROR_STOP=1 "$@"
}

# The image restarts Postgres once after its init scripts; wait until a TCP query works twice.
ready=0
for _ in $(seq 1 90); do
  if psql_in -qAt -c 'select 1' >/dev/null 2>&1; then
    ready=$((ready + 1))
    [ "$ready" -ge 2 ] && break
  else
    ready=0
  fi
  sleep 1
done
psql_in -qAt -c 'select 1' >/dev/null

echo "== migrations"
for f in "$REPO"/supabase/migrations/*.sql; do
  echo "   $(basename "$f")"
  psql_in -q -f "/repo/supabase/migrations/$(basename "$f")" >/dev/null
done

echo "== tests"
failed=0
for t in "$HERE"/*.sql; do
  name="$(basename "$t")"
  [ -n "$FILTER" ] && [[ "$name" != *"$FILTER"* ]] && continue
  if ! out="$(psql_in -qAt -f "/repo/ledger/tests/$name" 2>&1)"; then
    echo "FAIL $name (error)"; echo "$out" | sed 's/^/     /'; failed=1; continue
  fi
  if echo "$out" | grep -qE '^not ok|^# Looks like'; then
    echo "FAIL $name"; echo "$out" | grep -E '^not ok|^#' | sed 's/^/     /'; failed=1
  else
    echo "ok   $name ($(echo "$out" | grep -cE '^ok') checks)"
  fi
done

exit "$failed"
