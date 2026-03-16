#!/usr/bin/env bash
# PreToolUse hook: auto memory storage when reading code files.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Read INPUT from stdin (Claude Code passes input via stdin)
INPUT="$(cat || true)"

# Check if it's a Read tool call
TOOL_NAME="$(_json_val "$INPUT" "tool_name" "")"
if [[ "$TOOL_NAME" != "Read" ]]; then
  echo '{}'
  exit 0
fi

# Get file path
FILE_PATH="$(_json_val "$INPUT" "file_path" "")"
if [[ -z "$FILE_PATH" ]]; then
  echo '{}'
  exit 0
fi

# Check if it's a directory or file
if [[ -d "$FILE_PATH" ]]; then
  # Directory analysis
  IS_DIRECTORY=true
elif [[ -f "$FILE_PATH" ]]; then
  # Check file extension (only code files)
  CODE_EXTENSIONS=("py" "js" "ts" "jsx" "tsx" "java" "go" "rs" "c" "cpp" "h" "php" "rb" "swift" "kt" "scala")
  EXT="${FILE_PATH##*.}"
  EXT_LOWER=$(echo "$EXT" | tr '[:upper:]' '[:lower:]')
  IS_CODE_FILE=false
  for ext in "${CODE_EXTENSIONS[@]}"; do
    if [[ "$EXT_LOWER" == "$ext" ]]; then
      IS_CODE_FILE=true
      break
    fi
  done

  if [[ "$IS_CODE_FILE" != "true" ]]; then
    echo '{}'
    exit 0
  fi
  IS_DIRECTORY=false
else
  echo '{}'
  exit 0
fi

# Run the Python bridge
OUT="$(run_bridge analyze-file --file-path "$FILE_PATH" 2>/dev/null || true)"
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
FUNCTIONS="$(_json_val "$OUT" "functions" "0")"
CLASSES="$(_json_val "$OUT" "classes" "0")"
BRANCH="$(_json_val "$OUT" "branch" "")"
IS_DIR="$(_json_val "$OUT" "is_directory" "false")"
FILE_COUNT="$(_json_val "$OUT" "file_count" "1")"

if [[ -z "$URI" ]]; then
  echo '{}'
  exit 0
fi

# Build message (use \n for newlines)
MSG="✅ 已自动存储代码记忆"
if [[ -n "$BRANCH" ]]; then
  MSG="$MSG ($BRANCH 分支)"
fi
if [[ "$IS_DIR" == "true" ]]; then
  MSG="$MSG:\n📁 $URI\n📊 文件：$FILE_COUNT, 函数：$FUNCTIONS, 类：$CLASSES"
else
  MSG="$MSG:\n📁 $URI\n📊 函数：$FUNCTIONS, 类：$CLASSES"
fi

# Encode message as JSON string
json_msg=$(printf '%b' "$MSG" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
echo "{\"systemMessage\": $json_msg}"
