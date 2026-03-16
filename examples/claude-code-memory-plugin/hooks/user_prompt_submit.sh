#!/usr/bin/env bash
# UserPromptSubmit hook: lightweight memory availability hint.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Read INPUT from stdin (Claude Code passes input via stdin)
INPUT="$(cat || true)"

PROMPT="$(_json_val "$INPUT" "prompt" "")"
if [[ -z "$PROMPT" || ${#PROMPT} -lt 10 ]]; then
  echo '{}'
  exit 0
fi

OUT="$(run_bridge ingest-user-prompt --prompt "$PROMPT" 2>/dev/null || true)"
if [[ -z "$OUT" || "$OUT" == "null" ]]; then
  msg='[claude-memory] Memory available (use memory-recall when historical context matters)'
  json_msg=$(_json_encode_str "$msg")
  echo "{\"systemMessage\": $json_msg}"
  exit 0
fi

OK="$(_json_val "$OUT" "ok" "false")"
STATUS="$(_json_val "$OUT" "status_line" "[claude-memory] Memory available")"

json_status=$(_json_encode_str "$STATUS")
echo "{\"systemMessage\": $json_status}"
