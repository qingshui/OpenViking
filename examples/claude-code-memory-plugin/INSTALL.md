# Claude Code Memory Plugin 安装指南

## 前置要求

### 1. Python 环境

- Python 3.10 或更高版本
- 无需额外依赖，使用 Python 标准库

### 2. OpenViking 服务

确保 OpenViking 服务正在运行：

```bash
# 启动所有服务
~/.openviking/services.sh start

# 或单独启动服务器
~/.openviking/services.sh start-server
```

### 3. 配置 OpenViking

确保 OpenViking 配置文件存在：

```bash
# 检查配置文件
ls -la ~/.openviking/ov.conf
```

如果不存在，创建配置文件：

```bash
mkdir -p ~/.openviking

cat > ~/.openviking/ov.conf << 'EOF'
{
  "server": {
    "host": "0.0.0.0",
    "port": 1933,
    "root_api_key": "your-root-api-key-here"
  },
  "storage": {
    "workspace": "$HOME/.openviking/data",
    "agfs": {
      "port": 1833,
      "log_level": "warn",
      "backend": "local",
      "timeout": 10,
      "retry_times": 3
    }
  },
  "embedding": {
    "max_concurrent": 10,
    "dense": {
      "provider": "openai_compatible",
      "api_key": "your-api-key-here",
      "api_base": "http://your-embedding-server:port",
      "model": "your-embedding-model",
      "dimension": 1024
    }
  },
  "vlm": {
    "provider": "openai",
    "api_key": "your-api-key-here",
    "api_base": "http://your-llm-server:port",
    "model": "your-llm-model"
  }
}
EOF
```

## 安装步骤

### 1. 克隆或复制插件代码

```bash
# 从 OpenViking 仓库复制
cp -r /home/users/humingqing/work/OpenViking/examples/claude-code-memory-plugin \
      ~/.openviking/claude-code-memory-plugin

# 或使用 git clone
# git clone <repository-url> examples/claude-code-memory-plugin
```

### 2. 设置 Python 环境变量（可选）

```bash
# 添加插件路径到 PYTHONPATH
export PYTHONPATH="$HOME/.openviking/claude-code-memory-plugin:$PYTHONPATH"
```

### 3. 验证安装

```bash
cd ~/.openviking/claude-code-memory-plugin

# 运行测试
python3 test_memory_plugin.py
```

预期输出：

```
############################################################
# Claude Code Memory Plugin 测试
############################################################
==================================================
测试 OpenViking 客户端
==================================================
Health check: {'status': 'ok'}
System status: {'status': 'ok', ...}

...

==================================================
所有测试完成！
==================================================
```

## 快速开始

### 基础使用

```python
from memory_plugin import ClaudeCodeMemoryPlugin, MemoryType

# 初始化插件
plugin = ClaudeCodeMemoryPlugin(
    openviking_url="http://localhost:1933",
    api_key="6z_TTilwV_CM16qV3ExG1PAVFCptrLp-ver8Xb1lGD8"
)

# 初始化会话
plugin.initialize_session(
    session_id="session-001",
    context="正在开发一个 Python Web 应用"
)

# 存储设计文档
plugin.store_design_doc(
    title="Project Architecture",
    content="# Project Architecture\n## Overview...",
    tags=["architecture", "backend"]
)

# 存储代码规范
plugin.store_code_style(
    title="Python Coding Standards",
    content="# Python Coding Standards...",
    tags=["python", "standards"]
)

# 存储 API 接口
plugin.store_api_interface(
    title="create_user",
    content="create_user(name: str, email: str) -> User",
    params=[
        {"name": "name", "type": "str", "description": "User name"}
    ],
    returns={"type": "User"},
    tags=["api", "user"]
)

# 获取相关记忆
relevant_memories = plugin.get_relevant_memories(
    context="Python FastAPI database",
    memory_types=[MemoryType.DESIGN_DOC, MemoryType.CODE_STYLE],
    limit=5
)
```

## 与 Claude Code 集成

### 1. 作为独立脚本使用

创建 `memory_manager.py`：

```python
#!/usr/bin/env python3
"""
Claude Code Memory Manager
用于管理 Claude Code 的记忆
"""

import sys
import os

# 添加插件路径
sys.path.insert(0, os.path.dirname(__file__))

from memory_plugin import ClaudeCodeMemoryPlugin, MemoryType

def main():
    # 初始化插件
    plugin = ClaudeCodeMemoryPlugin()

    # 从命令行参数获取操作
    if len(sys.argv) < 2:
        print("Usage: memory_manager.py <command> [args]")
        print("Commands: init, store, search, list")
        return

    command = sys.argv[1]

    if command == "init":
        session_id = sys.argv[2] if len(sys.argv) > 2 else "default"
        plugin.initialize_session(session_id, "New session")
        print(f"Session initialized: {session_id}")

    elif command == "store":
        title = sys.argv[2] if len(sys.argv) > 2 else "Memory"
        content = sys.argv[3] if len(sys.argv) > 3 else ""
        memory_type = MemoryType(sys.argv[4]) if len(sys.argv) > 4 else MemoryType.SESSION
        plugin.store_design_doc(title, content)
        print(f"Memory stored: {title}")

    elif command == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        memories = plugin.get_relevant_memories(query)
        print(f"Found {len(memories)} memories:")
        for m in memories:
            print(f"  - {m.title}")

    elif command == "list":
        # List all memories
        print("Use OpenViking CLI to list memories:")
        print("  ov ls viking://resources/memories/")

if __name__ == "__main__":
    main()
```

### 2. 在 Claude Code 中使用

创建 `~/.claude/code_memory_tools.py`：

```python
"""
Claude Code Memory Tools
用于在 Claude Code 对话中使用记忆功能
"""

from memory_plugin import ClaudeCodeMemoryPlugin, MemoryType

# 初始化插件
plugin = ClaudeCodeMemoryPlugin()

def store_memory(title: str, content: str, memory_type: str) -> str:
    """存储记忆到 OpenViking"""
    try:
        mem_type = MemoryType(memory_type)
        if mem_type == MemoryType.DESIGN_DOC:
            plugin.store_design_doc(title, content)
        elif mem_type == MemoryType.CODE_STYLE:
            plugin.store_code_style(title, content)
        elif mem_type == MemoryType.API_INTERFACE:
            plugin.store_api_interface(title, content)
        else:
            plugin.manager.create_memory(title, content, mem_type)
        return f"Memory stored: {title}"
    except Exception as e:
        return f"Error storing memory: {str(e)}"

def get_memory_context(context: str) -> str:
    """获取相关记忆作为上下文"""
    try:
        memories = plugin.get_relevant_memories(context, limit=3)
        if not memories:
            return "No relevant memories found."

        context_text = "Relevant memories:\n"
        for m in memories:
            context_text += f"- {m.title}: {m.content[:200]}...\n"
        return context_text
    except Exception as e:
        return f"Error retrieving memories: {str(e)}"
```

## 配置选项

### 环境变量

```bash
# OpenViking API 地址
export OPENVIKING_URL="http://localhost:1933"

# API 密钥
export OPENVIKING_API_KEY="6z_TTilwV_CM16qV3ExG1PAVFCptrLp-ver8Xb1lGD8"

# 插件路径
export MEMORY_PLUGIN_PATH="$HOME/.openviking/claude-code-memory-plugin"
```

### 配置文件

创建 `~/.claude/code-memory-config.json`：

```json
{
  "openviking_url": "http://localhost:1933",
  "api_key": "6z_TTilwV_CM16qV3ExG1PAVFCptrLp-ver8Xb1lGD8",
  "default_memory_types": ["design_doc", "code_style", "api_interface"],
  "search_limit": 5,
  "auto_save_session": true,
  "session_timeout": 3600
}
```

## 故障排除

### 1. 连接失败

```bash
# 检查 OpenViking 服务
~/.openviking/services.sh status

# 测试 API 连接
curl http://localhost:1933/health
```

### 2. 认证失败

检查 API 密钥是否正确：

```python
# 验证 API 密钥
curl http://localhost:1933/api/v1/system/status \
  -H "X-API-Key: your-api-key"
```

### 3. 存储失败

检查临时文件权限：

```bash
# 检查临时目录
ls -la /tmp/

# 确保可以写入
touch /tmp/test_write && rm /tmp/test_write
```

## 更新

```bash
# 从仓库更新
cd ~/.openviking/claude-code-memory-plugin
git pull origin main

# 或重新复制
rm -rf ~/.openviking/claude-code-memory-plugin
cp -r /home/users/humingqing/work/OpenViking/examples/claude-code-memory-plugin \
      ~/.openviking/claude-code-memory-plugin
```

## 卸载

```bash
# 删除插件目录
rm -rf ~/.openviking/claude-code-memory-plugin

# 清理环境变量
# 编辑 ~/.bashrc 或 ~/.zshrc 并移除相关导出
```

## 支持

- [OpenViking 文档](https://www.openviking.ai/docs)
- [GitHub Issues](https://github.com/volcengine/OpenViking/issues)
- [社区讨论](https://github.com/volcengine/OpenViking/discussions)
