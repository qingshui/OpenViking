#!/usr/bin/env bash
# Stop hook: cleanup on session stop.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Run bridge
OUT="$(run_bridge stop 2>/dev/null || true)"
if [[ -z "$OUT" || "$OUT" == "null" ]]; then
  echo '{}'
  exit 0
fi

OK="$(_json_val "$OUT" "ok" "false")"
if [[ "$OK" == "true" ]]; then
  echo '{"systemMessage": "[claude-memory] Cleanup completed"}'
else
  echo '{}'
fi
