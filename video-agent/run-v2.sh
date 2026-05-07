#!/bin/bash
# run-v2.sh — опт-ин точка входа для суб-агентного pipeline.
# Старый run.sh не трогается (легаси, монолитный Claude).
#
# Использование:
#   ./run-v2.sh GAME_TAG "idea" [format]
#
# Делегирует в pipeline.sh, который оркестрирует:
#   monolith (phases 0-3) → Editor sub-agent (phase 4) → upload (phase 5)
#
# ENV (опц.):
#   PIPELINE_EDITOR_MODEL — модель для Editor (default: claude-sonnet-4-6)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$SCRIPT_DIR/pipeline.sh" "$@"
