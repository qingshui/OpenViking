# Claude Code Memory Plugin 设计文档

## 概述

Claude Code Memory Plugin 是一个基于远程 OpenViking API 的轻量级内存记忆插件，旨在为 AI Agent 提供持久化、可检索的记忆管理能力。

## 设计目标

### 核心目标

1. **远程存储**：所有记忆直接存储到远程 OpenViking 服务，无需本地数据库
2. **轻量级**：仅使用 Python 标准库，无额外依赖
3. **易集成**：简单 API，易于集成到 Claude Code 和其他系统
4. **语义搜索**：利用 OpenViking 的语义搜索能力实现智能记忆检索

### 非目标

- 不实现本地缓存或持久化
- 不实现复杂的记忆生命周期管理
- 不实现记忆优先级或过期机制

## 架构设计

### 系统架构

```
┌──────────────────────────────────────────────────────────────────────┐
│                     应用层                                              │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  RemoteMemoryPlugin                                             │  │
│  │  - store_design_doc / store_code_style / store_api_interface   │  │
│  │  - analyze_and_store_file / analyze_and_store_directory        │  │
│  │  - store_code_snippet / search_memories / initialize_session   │  │
│  └────────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  CodeAnalyzer (代码分析器)                                       │  │
│  │  - detect_language()                                           │  │
│  │  - analyze_python_file()                                       │  │
│  │  - analyze_file()                                              │  │
│  │  - analyze_directory()                                         │  │
│  └────────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     客户端层                                           │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  OpenVikingClient                                               │  │
│  │  - add_memory(uri, content)                                    │  │
│  │  - search_memories(query)                                      │  │
│  │  - get_memory_abstract(uri)                                    │  │
│  │  - delete_memory(uri)                                          │  │
│  └────────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     网络层                                             │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  HTTP/HTTPS                                                     │  │
│  │  - urllib.request                                               │  │
│  │  - JSON 编码/解码                                                │  │
│  └────────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     服务层                                             │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Remote OpenViking Service                                      │  │
│  │  - /api/v1/resources (存储记忆)                                 │  │
│  │  - /api/v1/search/find (搜索记忆)                               │  │
│  │  - /api/v1/content/abstract (获取摘要)                          │  │
│  │  - /api/v1/fs (管理记忆)                                        │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

### 组件说明

#### 1. RemoteMemoryPlugin（应用层）

**职责**：
- 提供高层记忆管理 API
- 生成记忆 URI
- 处理记忆类型转换
- 管理会话状态
- 调用 CodeAnalyzer 进行代码分析

**主要方法**：
```python
class RemoteMemoryPlugin:
    # 记忆存储
    def store_design_doc(title, content, tags) -> MemoryEntry
    def store_code_style(title, content, tags) -> MemoryEntry
    def store_api_interface(title, content, params, returns, tags) -> MemoryEntry
    def store_code_snippet(title, content, language, tags) -> MemoryEntry

    # 代码自动记忆
    def analyze_and_store_file(file_path, auto_store) -> MemoryEntry
    def analyze_and_store_directory(dir_path, auto_store) -> List[MemoryEntry]

    # 会话管理
    def initialize_session(session_id, context) -> None
    def update_session(new_context) -> None
    def get_session(session_id) -> Optional[Dict]

    # 搜索
    def search_memories(query, memory_types, limit) -> List[MemoryEntry]
```

#### 2. CodeAnalyzer（代码分析器）

**职责**：
- 检测文件编程语言
- 分析代码结构（函数、类、导入）
- 提取文档字符串
- 识别依赖关系

**支持语言**：
- Python (完整分析)
- JavaScript/TypeScript (基础分析)
- Java, Go, Rust, C/C++, PHP, Ruby, Swift, Kotlin, Scala
- Shell, SQL, HTML, CSS, JSON, YAML, Markdown

**主要方法**：
```python
class CodeAnalyzer:
    def detect_language(file_path) -> str
    def analyze_python_file(file_path, content) -> Dict
    def analyze_file(file_path) -> Dict
    def analyze_directory(dir_path, extensions) -> Dict
```

**Python 文件分析输出**：
```python
{
    'language': 'python',
    'file_path': '/path/to/file.py',
    'functions': [
        {
            'name': 'function_name',
            'params': [{'name': 'param1', 'type': 'str'}],
            'return_type': 'Dict',
            'line': 10
        }
    ],
    'classes': [
        {
            'name': 'ClassName',
            'inherits': 'object',
            'line': 25
        }
    ],
    'imports': ['os', 'sys', 'typing'],
    'docstrings': ['First line of docstring...'],
    'total_lines': 100
}
```

#### 2. OpenVikingClient（客户端层）

**职责**：
- 封装 OpenViking API 调用
- 处理 HTTP 请求和响应
- 错误处理和重试

**主要方法**：
```python
class OpenVikingClient:
    def add_memory(uri, content, reason) -> Dict
    def search_memories(query, limit) -> Dict
    def get_memory_abstract(uri) -> Dict
    def delete_memory(uri) -> Dict
```

#### 3. MemoryEntry（数据模型）

**职责**：
- 表示单个记忆条目
- 存储记忆的基本信息

**字段**：
```python
@dataclass
class MemoryEntry:
    title: str              # 记忆标题
    content: str            # 记忆内容
    memory_type: MemoryType # 记忆类型
    tags: List[str]         # 标签
    metadata: Dict[str, Any] # 元数据
    uri: Optional[str]      # OpenViking URI
```

#### 4. MemoryType（枚举）

**职责**：
- 定义记忆类型分类

**类型**：
```python
class MemoryType(Enum):
    DESIGN_DOC = "design_doc"        # 设计文档
    CODE_STYLE = "code_style"        # 代码规范
    API_INTERFACE = "api_interface"  # API 接口
    SESSION = "session"              # 会话记忆
    TASK = "task"                    # 任务记忆
    PREFERENCE = "preference"        # 用户偏好
    CODE_FILE = "code_file"          # 代码文件分析
    CODE_MODULE = "code_module"      # 模块/包分析
    CODE_DEPENDENCY = "code_dependency"  # 依赖关系
```

**代码记忆说明**：
- `CODE_FILE`: 单个代码文件的详细分析，包含函数、类、导入等
- `CODE_MODULE`: 整个目录/模块的概览统计
- `CODE_DEPENDENCY`: 项目依赖的外部库列表

## 数据模型

### 记忆 URI 结构

```
viking://resources/memories/{memory_type}/{safe_title}

示例:
- viking://resources/memories/design_doc/project_architecture
- viking://resources/memories/code_style/python_standards
- viking://resources/memories/api_interface/create_user
- viking://resources/memories/session/dev-session-1
```

### URI 生成规则

1. **Scope**: 固定为 `resources`（OpenViking 支持的范围）
2. **路径**: `memories/{memory_type}/{title}`
3. **Title 处理**:
   - 转换为小写
   - 移除特殊字符（只保留字母、数字、下划线、连字符）
   - 使用下划线分隔单词

### 存储格式

记忆内容以 Markdown 格式存储：

```markdown
## Title
{title}

## Content
{content}

## Tags
{tags}

## Metadata
{json.dumps(metadata, indent=2)}
```

## API 设计

### 记忆存储 API

```python
def store_design_doc(title: str, content: str, tags: Optional[List[str]] = None) -> MemoryEntry
```

**参数**：
- `title`: 记忆标题
- `content`: 记忆内容
- `tags`: 可选标签列表

**返回**：
- `MemoryEntry`: 存储的记忆条目

**错误处理**：
- 如果存储失败，抛出 `Exception`，包含错误信息

### 记忆搜索 API

```python
def search_memories(query: str, memory_types: Optional[List[MemoryType]] = None, limit: int = 5) -> List[MemoryEntry]
```

**参数**：
- `query`: 搜索关键词
- `memory_types`: 可选的记忆类型过滤
- `limit`: 返回结果数量限制

**返回**：
- `List[MemoryEntry]`: 匹配的记忆列表

### 会话管理 API

```python
def initialize_session(session_id: str, context: str) -> None
def update_session(new_context: str) -> None
def get_session(session_id: str) -> Optional[Dict]
```

**会话数据结构**：
```json
{
  "session_id": "session-001",
  "context": "正在开发 Python Web 应用",
  "start_time": 1234567890.0,
  "updates": [
    {"time": 1234567891.0, "context": "使用 FastAPI 框架"},
    {"time": 1234567892.0, "context": "添加 PostgreSQL 数据库"}
  ]
}
```

## 错误处理

### 错误类型

1. **连接错误**：无法连接到 OpenViking 服务
2. **认证错误**：API 密钥无效或过期
3. **存储错误**：记忆存储失败
4. **搜索错误**：搜索请求失败

### 错误处理策略

```python
try:
    plugin.store_design_doc(title, content)
except Exception as e:
    # 记录错误，但不中断程序
    print(f"Warning: Failed to store memory: {e}")
```

## 性能考虑

### 1. 临时文件处理

存储记忆时使用临时文件：
- 创建临时文件写入内容
- 调用 OpenViking API
- 删除临时文件

**优点**：
- 避免内存占用
- 支持大内容存储

**缺点**：
- 额外的 I/O 操作

### 2. 并发控制

当前设计不支持并发存储，后续可考虑：
- 添加队列机制
- 实现批量存储

### 3. 缓存策略

当前设计不缓存记忆，每次搜索都调用远程 API。后续可考虑：
- 本地缓存搜索结果
- 实现过期策略

## 安全考虑

### 1. API 密钥管理

- 建议通过环境变量传递 API 密钥
- 避免硬编码在代码中

```python
import os
api_key = os.environ.get("OPENVIKING_API_KEY")
plugin = RemoteMemoryPlugin(api_key=api_key)
```

### 2. 内容验证

- 验证输入内容的长度
- 过滤敏感信息

### 3. 网络传输

- 建议使用 HTTPS 协议
- 确保 TLS 加密

## 扩展性设计

### 1. 自定义记忆类型

```python
class CustomMemoryType(Enum):
    CUSTOM = "custom"

plugin.manager.create_memory(
    title="Custom Memory",
    content="Content",
    memory_type=CustomMemoryType.CUSTOM
)
```

### 2. 自定义存储后端

可通过继承 `OpenVikingClient` 实现自定义存储：

```python
class CustomClient(OpenVikingClient):
    def add_memory(self, uri, content, reason):
        # 自定义存储逻辑
        pass
```

### 3. 插件扩展

可添加新的记忆管理方法：

```python
class ExtendedMemoryPlugin(RemoteMemoryPlugin):
    def store_task(self, title, content, priority):
        # 任务记忆存储
        pass
```

## 测试策略

### 1. 单元测试

测试每个方法的正确性：
- 存储方法
- 搜索方法
- 会话管理方法

### 2. 集成测试

测试与 OpenViking 服务的集成：
- 实际 API 调用
- 错误处理

### 3. 性能测试

测试大规模数据场景：
- 大量记忆存储
- 复杂搜索查询

## 未来改进方向

### 短期

1. 添加缓存机制
2. 实现批量存储
3. 添加记忆过期机制

### 中期

1. 支持本地缓存
2. 实现记忆优先级
3. 添加记忆聚合功能

### 长期

1. 支持多 OpenViking 实例
2. 实现记忆同步机制
3. 添加记忆版本控制

## 参考

- [OpenViking API 文档](https://www.openviking.ai/docs)
- [Claude Code 文档](https://claude.ai/docs)
