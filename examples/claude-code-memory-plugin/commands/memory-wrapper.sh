#!/bin/bash
# Memory Command Wrapper
# 用于 /memory 命令的包装脚本

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SCRIPT="${PLUGIN_ROOT}/scripts/memory_command.py"

if [ ! -f "$SCRIPT" ]; then
    echo '{"error": "memory_command.py not found"}'
    exit 1
fi

python3 "$SCRIPT" "$@"
