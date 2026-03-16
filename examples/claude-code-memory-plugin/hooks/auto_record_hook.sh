#!/usr/bin/env bash
# PostToolUse hook: record tool call results to OpenViking.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Read INPUT from stdin (Claude Code passes input via stdin)
INPUT="$(cat || true)"

# Get tool info
TOOL_NAME="$(_json_val "$INPUT" "tool_name" "")"
TOOL_RESULT="$(_json_val "$INPUT" "tool_result" "")"

# Only record important tools
IMPORTANT_TOOLS=("Read" "Write" "Edit" "Exec" "Search" "Message" "WebFetch" "Bash")
RECORD_TOOL=false
for tool in "${IMPORTANT_TOOLS[@]}"; do
  if [[ "$TOOL_NAME" == "$tool" ]]; then
    RECORD_TOOL=true
    break
  fi
done

if [[ "$RECORD_TOOL" != "true" || -z "$TOOL_RESULT" ]]; then
  echo '{}'
  exit 0
fi

# Run the Python bridge
OUT="$(run_bridge record-tool --tool-name "$TOOL_NAME" --tool-result "$TOOL_RESULT" 2>/dev/null || true)"
if [[ -z "$OUT" || "$OUT" == "null" ]]; then
  echo '{}'
  exit 0
fi

OK="$(_json_val "$OUT" "ok" "false")"
if [[ "$OK" != "true" ]]; then
  echo '{}'
  exit 0
fi

URI="$(_json_val "$OUT" "uri" "")"

if [[ -z "$URI" ]]; then
  echo '{}'
  exit 0
fi

# Build message (use \n for newlines)
MSG="✅ 已记录工具调用：$TOOL_NAME\n📁 $URI"

# Encode message as JSON string
json_msg=$(printf '%b' "$MSG" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
echo "{\"systemMessage\": $json_msg}"
