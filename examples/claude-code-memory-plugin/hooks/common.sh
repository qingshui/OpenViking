#!/usr/bin/env bash
# Shared helpers for Claude Code Memory Plugin hooks.

set -euo pipefail

# INPUT is already read by the calling script to avoid double-read
# if [[ -z "$INPUT" ]]; then
#   INPUT="$(cat || true)"
# fi

# Add common bin paths to PATH
for p in "$HOME/.local/bin" "$HOME/.cargo/bin" "$HOME/bin" "/usr/local/bin"; do
  [[ -d "$p" ]] && [[ ":$PATH:" != *":$p:"* ]] && export PATH="$p:$PATH"
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Config paths
OV_CONF="$PROJECT_DIR/ov.conf"
BRIDGE="$PLUGIN_ROOT/scripts/memory_bridge.py"

# Python binary
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  PYTHON_BIN=""
fi

# JSON value extraction
_json_val() {
  local json="$1" key="$2" default="${3:-}"
  local result=""

  if command -v jq >/dev/null 2>&1; then
    result=$(printf '%s' "$json" | jq -r ".${key} // empty" 2>/dev/null) || true
  elif [[ -n "$PYTHON_BIN" ]]; then
    result=$(
      "$PYTHON_BIN" -c '
import json, sys
obj = json.loads(sys.argv[1])
val = obj
for k in sys.argv[2].split("."):
    if isinstance(val, dict):
        val = val.get(k)
    else:
        val = None
        break
if val is None:
    print("")
elif isinstance(val, bool):
    print("true" if val else "false")
else:
    print(val)
' "$json" "$key" 2>/dev/null
    ) || true
  fi

  if [[ -z "$result" ]]; then
    printf '%s' "$default"
  else
    printf '%s' "$result"
  fi
}

# JSON string encoding
_json_encode_str() {
  local str="$1"
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$str" | jq -Rs .
    return 0
  fi
  if [[ -n "$PYTHON_BIN" ]]; then
    printf '%s' "$str" | "$PYTHON_BIN" -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
    return 0
  fi
  printf '"%s"' "$str"
}

# Run bridge script
run_bridge() {
  if [[ -z "$PYTHON_BIN" ]]; then
    echo '{"ok": false, "error": "python not found"}'
    return 1
  fi
  if [[ ! -f "$BRIDGE" ]]; then
    echo '{"ok": false, "error": "bridge script not found"}'
    return 1
  fi

  "$PYTHON_BIN" "$BRIDGE" "$@"
}
