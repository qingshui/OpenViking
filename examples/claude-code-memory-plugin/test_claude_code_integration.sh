#!/usr/bin/env bash
# Test Claude Code hook integration

set -euo pipefail

PLUGIN_DIR="${1:-$HOME/.claude/claude-code-memory-plugin}"

echo "=========================================="
echo "Claude Code 插件集成测试"
echo "=========================================="
echo ""
echo "插件目录：$PLUGIN_DIR"
echo ""

# 测试 1: SessionStart 钩子
echo "1. 测试 SessionStart 钩子..."
CLAUDE_HOOK_INPUT='{}' bash "$PLUGIN_DIR/hooks/session_start.sh" 2>&1 | head -1
echo ""

# 测试 2: PreToolUse (Read) 钩子
echo "2. 测试 PreToolUse (Read) 钩子..."
CLAUDE_HOOK_INPUT='{"tool_name": "Read", "file_path": "'"$PLUGIN_DIR"'/memory_plugin.py"}' bash "$PLUGIN_DIR/hooks/auto_memory_hook.sh" 2>&1 | head -1
echo ""

# 测试 3: PostToolUse 钩子
echo "3. 测试 PostToolUse 钩子..."
CLAUDE_HOOK_INPUT='{"tool_name": "Read", "tool_result": "File content: test"}' bash "$PLUGIN_DIR/hooks/auto_record_hook.sh" 2>&1 | head -1
echo ""

# 测试 4: UserPromptSubmit 钩子
echo "4. 测试 UserPromptSubmit 钩子..."
CLAUDE_HOOK_INPUT='{"prompt": "测试用户提示，用于记忆检索"}' bash "$PLUGIN_DIR/hooks/user_prompt_submit.sh" 2>&1 | head -1
echo ""

# 测试 5: SessionEnd 钩子
echo "5. 测试 SessionEnd 钩子..."
bash "$PLUGIN_DIR/hooks/session_end.sh" 2>&1 | head -1
echo ""

# 测试 6: Stop 钩子
echo "6. 测试 Stop 钩子..."
bash "$PLUGIN_DIR/hooks/stop.sh" 2>&1 | head -1
echo ""

echo "=========================================="
echo "测试完成！"
echo "=========================================="
echo ""
echo "在 Claude Code 中使用:"
echo "  /memory                    # 查看帮助"
echo "  Read src/main.py           # 自动存储代码记忆"
echo "  /memory search \"Python\"    # 搜索记忆"
echo "  /memory-recall \"auth\"      # 回忆记忆"
