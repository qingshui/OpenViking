# Claude Code Memory Plugin

基于 OpenViking API 实现的 Claude Code 内存记忆插件，支持自动更新内存记忆。

## 功能特性

- **自动记忆存储**：自动将对话上下文、设计文档、代码规范存储到 OpenViking
- **智能检索**：基于语义搜索快速找到相关记忆
- **类型化管理**：支持设计文档、代码规范、API 接口、会话记忆等多种类型
- **持久化存储**：所有记忆存储在 OpenViking 中，支持跨会话访问

## 安装

### 1. 启动 OpenViking 服务

```bash
# 启动服务
~/.openviking/services.sh start

# 或单独启动
~/.openviking/services.sh start-server
```

### 2. 安装依赖

```bash
# 无需额外依赖，使用 Python 标准库
python3 --version  # 需要 Python 3.10+
```

## 使用示例

### 基础使用

```python
from memory_plugin import ClaudeCodeMemoryPlugin, MemoryType

# 初始化插件
plugin = ClaudeCodeMemoryPlugin(
    openviking_url="http://localhost:1933",
    api_key="your-api-key"
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

# 搜索相关记忆
relevant_memories = plugin.get_relevant_memories("Python FastAPI database")
```

### 高级用法

#### 自动更新会话记忆

```python
# 更新会话上下文
plugin.update_session("正在开发 Python Web 应用，使用 FastAPI 框架和 PostgreSQL 数据库")

# 获取相关记忆
memories = plugin.get_relevant_memories(
    context="如何设计数据库模型",
    memory_types=[MemoryType.DESIGN_DOC, MemoryType.CODE_STYLE],
    limit=5
)
```

#### 记忆类型

| 类型 | 描述 | 标签 |
|------|------|------|
| `DESIGN_DOC` | 设计文档 | design, architecture |
| `CODE_STYLE` | 代码规范 | code, style, convention |
| `API_INTERFACE` | API 接口 | api, function |
| `SESSION` | 会话记忆 | session |
| `TASK` | 任务记忆 | task |
| `PREFERENCE` | 用户偏好 | preference |

## API 参考

### `ClaudeCodeMemoryPlugin`

#### `__init__(openviking_url, api_key)`
初始化插件

- `openviking_url`: OpenViking API 地址（默认：http://localhost:1933）
- `api_key`: API 密钥

#### `initialize_session(session_id, context)`
初始化会话

- `session_id`: 会话 ID
- `context`: 初始上下文

#### `update_session(new_context)`
更新会话上下文

- `new_context`: 新的上下文内容

#### `store_design_doc(title, content, tags)`
存储设计文档

- `title`: 文档标题
- `content`: 文档内容
- `tags`: 标签列表

#### `store_code_style(title, content, tags)`
存储代码规范

- `title`: 规范标题
- `content`: 规范内容
- `tags`: 标签列表

#### `store_api_interface(title, content, params, returns, tags)`
存储 API 接口

- `title`: 接口名称
- `content`: 接口签名
- `params`: 参数列表
- `returns`: 返回值信息
- `tags`: 标签列表

#### `get_relevant_memories(context, memory_types, limit)`
获取相关记忆

- `context`: 搜索上下文
- `memory_types`: 记忆类型列表
- `limit`: 返回数量限制

#### `get_memory_summary(uri)`
获取记忆摘要

- `uri`: 记忆 URI

## 与 Claude Code 集成

### 1. 作为工具使用

```python
# 在 Claude Code 中定义记忆工具
def store_memory(title: str, content: str, memory_type: str) -> str:
    """存储记忆到 OpenViking"""
    plugin = ClaudeCodeMemoryPlugin()
    memory = plugin.create_memory(title, content, MemoryType(memory_type))
    return f"Memory stored: {memory.uri}"
```

### 2. 自动记忆建议

```python
# 根据当前上下文推荐记忆
def get_memory_suggestions(context: str) -> List[str]:
    """获取记忆建议"""
    plugin = ClaudeCodeMemoryPlugin()
    memories = plugin.get_relevant_memories(context)
    return [m.title for m in memories]
```

## 配置

### 环境变量

```bash
# OpenViking 配置
export OPENVIKING_URL="http://localhost:1933"
export OPENVIKING_API_KEY="your-api-key"
```

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

## 注意事项

1. **OpenViking 服务**：确保 OpenViking 服务正在运行
2. **API 密钥**：使用正确的 API 密钥进行认证
3. **网络访问**：确保可以访问 OpenViking API
4. **存储限制**：注意 OpenViking 的存储容量限制

## 扩展

### 添加自定义记忆类型

```python
class CustomMemoryType(Enum):
    CUSTOM = "custom"

# 使用自定义类型
plugin.manager.create_memory(
    title="Custom Memory",
    content="Content",
    memory_type=CustomMemoryType.CUSTOM
)
```

### 自定义搜索逻辑

```python
def custom_search(query: str) -> List[MemoryEntry]:
    """自定义搜索"""
    plugin = ClaudeCodeMemoryPlugin()
    return plugin.manager.search_memories(query)
```

## License

Apache License 2.0
