#!/usr/bin/env bash
# SessionEnd hook: commit memory session.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Check if ov.conf exists
if [[ ! -f "$OV_CONF" ]]; then
  echo '{}'
  exit 0
fi

# Run bridge
OUT="$(run_bridge session-end 2>/dev/null || true)"
if [[ -z "$OUT" || "$OUT" == "null" ]]; then
  echo '{}'
  exit 0
fi

OK="$(_json_val "$OUT" "ok" "false")"
STATUS="$(_json_val "$OUT" "status_line" "[claude-memory] session ended")"

json_status=$(_json_encode_str "$STATUS")
echo "{\"systemMessage\": $json_status}"
