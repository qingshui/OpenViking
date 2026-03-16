# 钩子系统配置总结

## 钩子列表

| 钩子类型 | 触发时机 | 脚本 | 超时 | 功能 |
|----------|----------|------|------|------|
| `PreToolUse` | 工具调用前 | `auto_memory_hook.sh` | 30s | 读取文件时自动分析代码 |
| `PostToolUse` | 工具调用后 | `auto_record_hook.sh` | 30s | 工具调用后自动记录结果 |
| `UserPromptSubmit` | 用户提交消息 | `user_prompt_submit.sh` | 10s | 提示记忆可用性 |
| `SessionStart` | 会话开始时 | `session_start.sh` | 10s | 初始化会话 |
| `SessionEnd` | 会话结束时 | `session_end.sh` | 20s | 提交会话 |
| `Stop` | 会话停止时 | `stop.sh` | 60s | 清理资源 |

---

## 钩子功能详解

### 1. PreToolUse (自动记忆)

**触发条件**: 使用 `Read` 命令读取文件时

**功能**:
- 自动分析代码文件
- 提取函数、类、导入信息
- 存储到 OpenViking
- 显示反馈消息

**示例输出**:
```
✅ 已自动存储代码记忆 (main 分支):
📁 viking://resources/memories/code_file/main/contextpy
📊 函数：9, 类：2
```

---

### 2. PostToolUse (工具记录)

**触发条件**: 使用任何工具时

**功能**:
- 记录工具调用结果
- 存储到 OpenViking
- 显示反馈消息

**支持的工具**:
- Read, Write, Edit, Exec, Search, Message, WebFetch, Bash

**示例输出**:
```
✅ 已记录工具调用：Write
📁 viking://resources/memories/api_interface/api_interfacetoolcallwrite
```

---

### 3. UserPromptSubmit (用户提示)

**触发条件**: 用户提交消息时

**功能**:
- 分析用户提示
- 判断是否需要记忆辅助
- 显示记忆可用性提示

**示例输出**:
```
[claude-memory] Memory available (use memory-recall when historical context matters)
```

**触发条件**:
- 提示长度 >= 10 字符
- 提示内容有意义

---

### 4. SessionStart (会话开始)

**触发条件**: 新会话开始时

**功能**:
- 初始化记忆会话
- 显示活跃状态
- 提示可用命令

**示例输出**:
```json
{
  "systemMessage": "[claude-memory] Memory plugin active",
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Use /memory commands to manage memories."
  }
}
```

---

### 5. SessionEnd (会话结束)

**触发条件**: 会话结束时

**功能**:
- 提交会话记忆
- 清理临时数据

**示例输出**:
```json
{
  "ok": true,
  "committed": true,
  "status_line": "[claude-memory] Session ended"
}
```

---

### 6. Stop (停止)

**触发条件**: 会话停止时

**功能**:
- 清理资源
- 异步执行（不阻塞）

**示例输出**:
```json
{
  "ok": true,
  "cleaned": true
}
```

---

## hooks.json 配置

```json
{
  "description": "Claude Code Memory Plugin - Auto memory storage when reading code files",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/auto_memory_hook.sh",
            "timeout": 30
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/auto_record_hook.sh",
            "timeout": 30
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/user_prompt_submit.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/session_start.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/session_end.sh",
            "timeout": 20
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/stop.sh",
            "async": true,
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

---

## 测试状态

| 钩子 | 状态 | 测试结果 |
|------|------|----------|
| PreToolUse | ✓ 通过 | 自动分析代码文件 |
| PostToolUse | ✓ 通过 | 记录工具调用 |
| UserPromptSubmit | ✓ 通过 | 提示记忆可用性 |
| SessionStart | ✓ 通过 | 初始化会话 |
| SessionEnd | ✓ 通过 | 提交会话 |
| Stop | ✓ 通过 | 清理资源 |

**总计**: 6/6 通过

---

## 使用场景

### 场景 1: 代码分析

```bash
# 用户操作
Read openviking/core/context.py

# 自动触发
# 1. PreToolUse 钩子 → 分析代码
# 2. 显示反馈消息
# 3. 存储到 OpenViking
```

### 场景 2: 工具记录

```bash
# 用户操作
Write src/new_feature.py

# 自动触发
# 1. PostToolUse 钩子 → 记录工具
# 2. 显示反馈消息
# 3. 存储到 OpenViking
```

### 场景 3: 记忆提示

```bash
# 用户操作
帮我分析一下 OpenViking 的客户端实现

# 自动触发
# 1. UserPromptSubmit 钩子 → 分析提示
# 2. 显示记忆可用性提示
# 3. 提示使用 memory-recall
```

### 场景 4: 会话管理

```bash
# 会话开始
# 1. SessionStart 钩子 → 初始化
# 2. 显示活跃状态

# 会话进行中
# - 自动记忆存储

# 会话结束
# 1. SessionEnd 钩子 → 提交
# 2. 清理数据
```

---

## 配置说明

### 环境变量

```bash
# CLAUDE_PLUGIN_ROOT - 插件根目录
export CLAUDE_PLUGIN_ROOT=/root/.claude/claude-code-memory-plugin
```

### 配置文件

```json
{
  "openviking_url": "http://localhost:1933",
  "api_key": "",
  "search_limit": 5,
  "install_dir": "/root/.claude/claude-code-memory-plugin"
}
```

---

## 总结

所有钩子功能已正确配置并测试通过：

1. ✓ **PreToolUse** - 自动代码分析
2. ✓ **PostToolUse** - 工具记录
3. ✓ **UserPromptSubmit** - 记忆提示
4. ✓ **SessionStart** - 会话初始化
5. ✓ **SessionEnd** - 会话提交
6. ✓ **Stop** - 资源清理

插件已准备就绪，可以在 Claude Code 中正常使用！
