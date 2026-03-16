# Claude Code Memory Plugin

基于**远程 OpenViking API**的轻量级内存记忆插件。

**无需本地安装**，所有记忆直接存储到远程 OpenViking 服务。

## 功能特性

- **远程存储**：设计文档、代码规范、API 接口直接存储到 OpenViking
- **会话管理**：会话上下文远程存储和更新
- **语义搜索**：基于 OpenViking 的语义搜索能力
- **轻量级**：仅使用 Python 标准库，无额外依赖

## 快速开始

### 1. 确保 OpenViking 服务可用

```bash
# 本地服务
~/.openviking/services.sh start

# 或远程服务
# 配置 OPENVIKING_URL 为远程地址
export OPENVIKING_URL="http://your-openviking-server:1933"
```

### 2. 使用插件

```python
from memory_plugin import RemoteMemoryPlugin, MemoryType

# 初始化插件
plugin = RemoteMemoryPlugin(
    openviking_url="http://localhost:1933",
    api_key="your-api-key"
)

# 存储设计文档
plugin.store_design_doc(
    title="Project Architecture",
    content="# Project Architecture\n\n## Overview...",
    tags=["architecture", "backend"]
)

# 存储代码规范
plugin.store_code_style(
    title="Python Standards",
    content="# Python Standards\n\n## Naming...",
    tags=["python", "standards"]
)

# 存储 API 接口
plugin.store_api_interface(
    title="create_user",
    content="create_user(name: str, email: str) -> User",
    params=[{"name": "name", "type": "str"}],
    returns={"type": "User"},
    tags=["api", "user"]
)

# 搜索记忆
memories = plugin.search_memories("Python FastAPI database")
print(f"Found {len(memories)} memories")

# 初始化会话
plugin.initialize_session("session-001", "正在开发 Python Web 应用")

# 更新会话
plugin.update_session("使用 FastAPI 和 PostgreSQL")
```

## 核心 API

### `RemoteMemoryPlugin`

| 方法 | 描述 |
|------|------|
| `store_design_doc(title, content, tags)` | 存储设计文档 |
| `store_code_style(title, content, tags)` | 存储代码规范 |
| `store_api_interface(title, content, params, returns, tags)` | 存储 API 接口 |
| `initialize_session(session_id, context)` | 初始化会话 |
| `update_session(new_context)` | 更新会话 |
| `search_memories(query, memory_types, limit)` | 搜索记忆 |
| `get_session(session_id)` | 获取会话数据 |
| `get_all_memories(memory_type)` | 列出所有记忆 |

### 记忆类型

| 类型 | 描述 |
|------|------|
| `DESIGN_DOC` | 设计文档 |
| `CODE_STYLE` | 代码规范 |
| `API_INTERFACE` | API 接口 |
| `SESSION` | 会话记忆 |
| `TASK` | 任务记忆 |
| `PREFERENCE` | 用户偏好 |

## 环境变量

```bash
# OpenViking API 地址
export OPENVIKING_URL="http://localhost:1933"

# API 密钥
export OPENVIKING_API_KEY="your-api-key"
```

## 使用示例

### 存储项目规范

```python
plugin = RemoteMemoryPlugin()

# 存储项目架构
plugin.store_design_doc(
    title="Backend Architecture",
    content="""
# Backend Architecture

## Tech Stack
- FastAPI
- PostgreSQL
- Redis

## Design Patterns
- Repository pattern
- Dependency injection
""",
    tags=["architecture", "backend"]
)

# 存储代码规范
plugin.store_code_style(
    title="Python Standards",
    content="""
# Python Standards

## Naming
- Variables: snake_case
- Classes: PascalCase

## Code Quality
- Type hints required
- Docstrings for all functions
""",
    tags=["python", "standards"]
)
```

### 管理会话

```python
# 初始化会话
plugin.initialize_session("dev-session-1", "正在开发用户模块")

# 在开发过程中更新会话
plugin.update_session("已完成用户注册功能，正在实现登录功能")

# 获取会话上下文
session = plugin.get_session("dev-session-1")
print(session["context"])
```

## 测试

```bash
cd examples/claude-code-memory-plugin
python3 test_memory_plugin.py
```

## 与 Claude Code 集成

### 作为工具使用

```python
# 在 Claude Code 对话中使用记忆工具
def store_memory(title: str, content: str, memory_type: str) -> str:
    """存储记忆到 OpenViking"""
    plugin = RemoteMemoryPlugin()
    if memory_type == "design_doc":
        plugin.store_design_doc(title, content)
    elif memory_type == "code_style":
        plugin.store_code_style(title, content)
    return f"Memory stored: {title}"

def get_memory_context(context: str) -> str:
    """获取相关记忆"""
    plugin = RemoteMemoryPlugin()
    memories = plugin.search_memories(context, limit=3)
    return "\n".join([f"- {m.title}: {m.content[:100]}..." for m in memories])
```

## 配置

### 配置文件

创建 `~/.claude/code-memory-config.json`:

```json
{
  "openviking_url": "http://localhost:1933",
  "api_key": "your-api-key",
  "default_memory_types": ["design_doc", "code_style", "api_interface"],
  "search_limit": 5
}
```

## 优势

1. **无需本地存储**：所有记忆存储在 OpenViking，无需本地数据库
2. **跨设备同步**：记忆通过 OpenViking 服务同步
3. **语义搜索**：利用 OpenViking 的语义搜索能力
4. **轻量级**：仅使用 Python 标准库

## License

Apache License 2.0
