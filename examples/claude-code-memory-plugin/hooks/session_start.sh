#!/usr/bin/env bash
# SessionStart hook: initialize memory session.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Read INPUT from stdin (Claude Code passes input via stdin)
INPUT="$(cat || true)"

# Run bridge
OUT="$(run_bridge session-start 2>/dev/null || true)"
if [[ -z "$OUT" || "$OUT" == "null" ]]; then
  echo '{}'
  exit 0
fi

OK="$(_json_val "$OUT" "ok" "false")"
STATUS="$(_json_val "$OUT" "status_line" "[claude-memory] initialization failed")"
ADDL="$(_json_val "$OUT" "additional_context" "")"

json_status=$(_json_encode_str "$STATUS")

if [[ "$OK" == "true" && -n "$ADDL" ]]; then
  json_addl=$(_json_encode_str "$ADDL")
  echo "{\"systemMessage\": $json_status, \"hookSpecificOutput\": {\"hookEventName\": \"SessionStart\", \"additionalContext\": $json_addl}}"
  exit 0
fi

echo "{\"systemMessage\": $json_status}"
