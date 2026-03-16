# Claude Code 集成指南

## 问题分析

基于对 `/home/users/humingqing/work/claude-code` 代码库的分析，发现 memory plugin 需要按照 Claude Code 的插件架构进行重构。

## Claude Code 插件架构要求

### 标准插件结构

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # 插件元数据（必需）
├── commands/                # Slash 命令定义（必需）
│   └── *.md
├── hooks/                   # Hook 配置（可选但推荐）
│   ├── hooks.json
│   └── *.py
├── agents/                  # Agent 定义（可选）
│   └── *.md
├── skills/                  # 技能知识（可选）
│   └── SKILL.md
└── README.md
```

### 当前状态对比

**问题状态（修复前）**:
```
claude-code-memory-plugin/
├── memory_plugin.py          # Python 模块（需要重新设计）
├── README.md
├── INSTALL.md
├── DESIGN.md
├── test_*.py
├── install.sh
└── uninstall.sh
```

❌ 缺少 `.claude-plugin/plugin.json` - 无法被 Claude Code 识别
❌ 缺少 `commands/` 目录 - 无法通过 Slash 命令调用
❌ 缺少 `hooks/` 目录 - 无法自动触发记忆功能

**修复后状态**:
```
claude-code-memory-plugin/
├── .claude-plugin/
│   └── plugin.json          ✅ 已创建
├── commands/
│   ├── memory.md            ✅ 已创建
│   └── memory-wrapper.sh    ✅ 已创建
├── hooks/
│   ├── hooks.json           ✅ 已创建
│   └── auto_memory_hook.py  ✅ 已创建
├── scripts/
│   └── memory_command.py    ✅ 已创建
├── memory_plugin.py         # 核心模块（保持）
├── README.md
├── INSTALL.md
└── DESIGN.md
```

## 修复内容

### 1. 插件元数据 (`.claude-plugin/plugin.json`)

```json
{
  "name": "claude-code-memory",
  "version": "1.0.0",
  "description": "Remote memory plugin for Claude Code",
  "author": {
    "name": "OpenViking Team",
    "email": "support@openviking.ai"
  }
}
```

### 2. Hook 配置 (`hooks/hooks.json`)

```json
{
  "description": "Auto memory storage when reading code files",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read",
        "hooks": [{
          "type": "command",
          "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/auto_memory_hook.py",
          "timeout": 30
        }]
      }
    ]
  }
}
```

**功能**: 在读取代码文件时自动分析并存储记忆

### 3. Slash 命令 (`commands/memory.md`)

提供以下命令：
- `/memory analyze <file_path>` - 分析代码文件
- `/memory store-design <title> <content>` - 存储设计文档
- `/memory store-api <title> <signature>` - 存储 API 接口
- `/memory search <query>` - 搜索记忆
- `/memory list [type]` - 列出记忆
- `/memory branches` - 列出分支

### 4. 命令执行脚本 (`scripts/memory_command.py`)

处理所有 `/memory` 命令的执行逻辑。

### 5. Hook 执行器 (`hooks/auto_memory_hook.py`)

在 `Read` 工具调用前自动分析代码文件并存储记忆。

## 使用方式

### 在 Claude Code 中使用

安装插件后，可以直接使用：

```bash
# 查看帮助
/memory

# 分析代码文件（自动触发）
Read src/main.py  # 自动存储记忆

# 手动分析
/memory analyze src/main.py

# 搜索记忆
/memory search "Python FastAPI"

# 列出所有记忆
/memory list

# 列出分支
/memory branches
```

### 自动触发机制

1. **PreToolUse Hook**: 当使用 `Read` 工具读取代码文件时
2. **自动分析**: 调用 `CodeAnalyzer.analyze_file()`
3. **自动存储**: 调用 `RemoteMemoryPlugin.analyze_and_store_file()`
4. **返回提示**: 显示存储结果

## 参考实现

参考 `hookify` 插件的实现：
- `.claude-plugin/plugin.json` - 插件元数据
- `hooks/hooks.json` - Hook 配置
- `hooks/pretooluse.py` - Hook 执行器
- `commands/*.md` - Slash 命令定义

## 后续优化建议

### 1. 添加更多 Hook 事件

```json
{
  "PostToolUse": [{
    "matcher": "Write|Edit",
    "hooks": [{
      "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/update_on_change.py"
    }]
  }]
}
```

### 2. 添加 Agent 定义

```markdown
---
name: memory-agent
description: Expert in managing and organizing code memories
---

# Memory Agent

You are an expert in...
```

### 3. 添加技能知识

```markdown
# SKILL: Memory Management

Best practices for...
```

### 4. 注册到 marketplace.json

在 `/home/users/humingqing/work/claude-code/.claude-plugin/marketplace.json` 中添加：

```json
{
  "name": "claude-code-memory",
  "description": "Memory plugin for Claude Code",
  "source": "./examples/claude-code-memory-plugin",
  "category": "productivity"
}
```

## 文件清单

| 文件 | 用途 | 状态 |
|------|------|------|
| `.claude-plugin/plugin.json` | 插件元数据 | ✅ 已创建 |
| `hooks/hooks.json` | Hook 配置 | ✅ 已创建 |
| `hooks/auto_memory_hook.py` | 自动记忆 Hook | ✅ 已创建 |
| `commands/memory.md` | Slash 命令文档 | ✅ 已创建 |
| `commands/memory-wrapper.sh` | 命令包装脚本 | ✅ 已创建 |
| `scripts/memory_command.py` | 命令执行器 | ✅ 已创建 |
| `memory_plugin.py` | 核心模块 | ✅ 保持 |
| `README.md` | 使用文档 | ✅ 已更新 |

## 验证

安装后验证：

```bash
# 1. 检查插件结构
ls -la ~/.claude/claude-code-memory-plugin/.claude-plugin/
ls -la ~/.claude/claude-code-memory-plugin/hooks/
ls -la ~/.claude/claude-code-memory-plugin/commands/

# 2. 运行验证脚本
python3 ~/.claude/claude-code-memory-plugin/verify_install.py

# 3. 在 Claude Code 中测试
/memory
/memory analyze <某个代码文件>
```
