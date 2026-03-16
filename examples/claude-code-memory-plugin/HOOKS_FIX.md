# Claude Code Memory Plugin Hooks 修复

## 参考实现

参考 `/home/users/humingqing/work/OpenViking/examples/claude-memory-plugin` 插件的实现方式。

## 问题分析

### 问题 1：调用大模型 API 前没有触发检索

**原因**：
- Claude Code **不支持** `PreLLMCall` 钩子类型
- 支持的钩子类型：`PreToolUse`, `PostToolUse`, `Stop`, `SubagentStop`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `PreCompact`, `Notification`

### 问题 2：收到返回结果时没有记录

**原因**：
- 只有 `PreToolUse` 钩子，没有 `PostToolUse` 钩子

## 修复方案

### 架构设计

参考 `claude-memory-plugin` 的实现，采用 **bash hooks + Python bridge** 的架构：

```
bash hook scripts
    ↓
common.sh (shared helpers)
    ↓
memory_bridge.py (Python bridge)
    ↓
memory_plugin.py (core API)
```

### 1. 更新 hooks/hooks.json

使用正确的钩子类型和 bash 脚本：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read",
        "hooks": [{"type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/auto_memory_hook.sh"}]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [{"type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/auto_record_hook.sh"}]
      }
    ],
    "SessionStart": [
      {
        "hooks": [{"type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/session_start.sh"}]
      }
    ],
    "Stop": [
      {
        "hooks": [{"type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/stop.sh", "async": true}]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [{"type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/session_end.sh"}]
      }
    ]
  }
}
```

### 2. 核心组件

#### `hooks/user_prompt_submit.sh` - 用户提示提交 Hook

在用户提交消息时提示记忆可用性：

```bash
# 触发时机：UserPromptSubmit
# 功能：轻量级记忆可用性提示
[claude-memory] Memory available (use memory-recall when historical context matters)
```

#### `skills/memory-recall/SKILL.md` - 记忆回忆技能

提供记忆检索技能，当用户询问历史决策、修复记录或上下文时使用：

```bash
# 使用记忆回忆技能
/memory-recall "用户认证模块的改动"
```

#### `common.sh` - 公共 helper 函数

提供 JSON 解析、路径处理等通用功能：

```bash
# JSON value extraction
_json_val() { ... }

# JSON string encoding
_json_encode_str() { ... }

# Run bridge script
run_bridge() { ... }
```

#### `memory_bridge.py` - Python 桥接脚本

提供稳定的 Python API 接口：

| 命令 | 功能 |
|------|------|
| `analyze-file` | 分析代码文件并存储 |
| `record-tool` | 记录工具调用结果 |
| `session-start` | 开始会话 |
| `session-end` | 结束会话 |
| `stop` | 清理 |

#### bash hook scripts

| 脚本 | 触发时机 | 功能 |
|------|----------|------|
| `auto_memory_hook.sh` | PreToolUse (Read) | 自动分析代码文件 |
| `auto_record_hook.sh` | PostToolUse | 记录工具调用结果 |
| `session_start.sh` | SessionStart | 初始化会话 |
| `session_end.sh` | SessionEnd | 提交会话 |
| `stop.sh` | Stop | 清理资源 |

### 3. 新增钩子文件

| 文件 | 说明 |
|------|------|
| `hooks/common.sh` | 公共 helper 函数 |
| `hooks/auto_memory_hook.sh` | 自动记忆 Hook |
| `hooks/auto_record_hook.sh` | 自动记录 Hook |
| `hooks/session_start.sh` | 会话开始 Hook |
| `hooks/session_end.sh` | 会话结束 Hook |
| `hooks/stop.sh` | 停止清理 Hook |
| `scripts/memory_bridge.py` | Python 桥接脚本 |

## 使用流程

### 完整工作流程

```
SessionStart → 用户消息 → LLM 调用 → PostToolUse (记录结果)
    ↓                                    ↓
初始化会话                          记录工具调用
    ↓                                    ↓
PreToolUse (Read) → 自动存储代码记忆
```

### 示例

```bash
# 1. Session 开始
[claude-memory] Memory plugin active

# 2. 读取代码文件
Read src/main.py
✅ 已自动存储代码记忆 (main 分支):
📁 viking://resources/memories/code_file/main/src_mainpy
📊 函数：12, 类：3

# 3. 工具调用后
✅ 已记录工具调用：Read
📁 viking://resources/memories/api_interface/tool-call-read

# 4. Session 结束
[claude-memory] Session ended
```

## 配置选项

在 `~/.claude/code-memory-config.json` 中可以配置：

```json
{
  "openviking_url": "http://localhost:1933",
  "api_key": "your-api-key",
  "use_branch_aware": true
}
```

或在 `ov.conf` 中配置：

```json
{
  "server": {
    "host": "localhost",
    "port": 1933,
    "api_key": "your-api-key"
  }
}
```

## 验证

安装后验证：

```bash
# 1. 检查钩子配置
cat ~/.claude/claude-code-memory-plugin/hooks/hooks.json

# 2. 检查脚本权限
ls -la ~/.claude/claude-code-memory-plugin/hooks/*.sh

# 3. 在 Claude Code 中测试
# Session 开始应该看到提示
# 使用 Read 工具触发自动存储
Read src/main.py
# 使用其他工具后应该看到记录提示
```

## 文件变更清单

| 文件 | 变更 | 状态 |
|------|------|------|
| `hooks/hooks.json` | 更新为 bash hooks | ✅ 已修改 |
| `hooks/common.sh` | 新建公共 helper | ✅ 已创建 |
| `hooks/auto_memory_hook.sh` | Bash 版本自动记忆 | ✅ 已创建 |
| `hooks/auto_record_hook.sh` | Bash 版本自动记录 | ✅ 已创建 |
| `hooks/user_prompt_submit.sh` | 用户提示提交 Hook | ✅ 已创建 |
| `hooks/session_start.sh` | 会话开始 Hook | ✅ 已创建 |
| `hooks/session_end.sh` | 会话结束 Hook | ✅ 已创建 |
| `hooks/stop.sh` | 停止清理 Hook | ✅ 已创建 |
| `scripts/memory_bridge.py` | Python 桥接脚本 | ✅ 已更新 |
| `skills/memory-recall/SKILL.md` | 记忆回忆技能 | ✅ 已创建 |
| `hooks/auto_memory_hook.py` | 删除 (Python 版本) | ✅ 已删除 |
| `hooks/auto_record_hook.py` | 删除 (Python 版本) | ✅ 已删除 |
| `hooks/auto_retrieve_hook.py` | 删除 (PreLLMCall 不支持) | ✅ 已删除 |
| `HOOKS_FIX.md` | 修复文档 | ✅ 已更新 |

## 参考实现

参考 `/home/users/humingqing/work/OpenViking/examples/claude-memory-plugin`：

- `hooks/hooks.json` - 钩子配置结构
- `hooks/common.sh` - 公共 helper 函数
- `scripts/ov_memory.py` - Python 桥接脚本模式
- bash hooks - 使用 `$INPUT` 读取 JSON 输入

## 总结

✅ **已修复记录问题** - 添加 `PostToolUse` 钩子记录工具调用结果

✅ **采用标准架构** - 参考 `claude-memory-plugin` 的 bash + Python bridge 架构

✅ **完整的钩子系统** - SessionStart, SessionEnd, Stop, UserPromptSubmit 等完整支持

✅ **记忆回忆技能** - 新增 `memory-recall` skill 支持历史记忆检索

⚠️ **自动检索限制** - Claude Code 不支持 `PreLLMCall` 钩子，无法在 LLM 调用前自动检索

**钩子类型**：
- `PreToolUse` - 读取文件时自动分析代码
- `PostToolUse` - 工具调用后自动记录结果
- `UserPromptSubmit` - 用户提交消息时提示记忆可用性
- `SessionStart` - 会话开始时初始化
- `SessionEnd` - 会话结束时提交
- `Stop` - 会话停止时清理

**使用方式**：
- 自动存储：`Read` 工具调用时自动分析代码文件
- 自动记录：`PostToolUse` 钩子自动记录工具调用结果
- 记忆提示：`UserPromptSubmit` 钩子提示记忆可用性
- 手动检索：使用 `/memory search` 命令或 `memory-recall` skill
