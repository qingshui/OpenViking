# Claude Code Memory Plugin

基于**远程 OpenViking API**的轻量级内存记忆插件。

**无需本地安装**，所有记忆直接存储到远程 OpenViking 服务。

## 状态

✅ **已更新** - 采用 bash hooks + Python bridge 架构，支持完整的钩子系统

详见 [`HOOKS_FIX.md`](HOOKS_FIX.md)

## 快速开始

### 在 Claude Code 中使用

**无需任何命令** - 插件会自动触发记忆存储：

```bash
# 读取代码文件时自动存储记忆
Read src/main.py  # 自动分析并存储代码

# 写入文件时自动记录
Write src/new_feature.py  # 自动记录工具调用

# 会话自动管理
# 会话开始和结束时自动初始化/提交记忆
```

**自动记忆功能**：
- 读取代码文件 → 自动分析并存储
- 使用工具 → 自动记录工具调用
- 会话开始 → 自动初始化
- 会话结束 → 自动提交

### 高级用法（Python API）

```python
from memory_plugin import RemoteMemoryPlugin

plugin = RemoteMemoryPlugin(
    openviking_url="http://localhost:1933",
    api_key="your-api-key"
)

# 存储用户信息
plugin.store_email("your@email.com")
plugin.store_phone("+1234567890")
plugin.store_address("Your Address")
```

## 功能特性

- **远程存储**：设计文档、代码规范、API 接口直接存储到 OpenViking
- **会话管理**：会话上下文远程存储和更新
- **代码自动记忆**：
  - 自动分析 Python/JavaScript/TypeScript/Java/Go/Rust 等代码文件
  - 提取函数、类、导入依赖等关键信息
  - 支持单文件分析和目录扫描
  - 自动生成模块概览和依赖关系记忆
- **分支感知**：
  - 自动检测 Git 分支信息
  - 支持多分支代码结构区分存储
  - 不同分支的 API 和代码规范独立管理
  - 支持版本化管理
- **团队共享**：
  - 支持多 Claude Code 共享存储
  - 团队级别的设计文档和代码规范
  - 用户追踪（记录修改者）
- **语义搜索**：基于 OpenViking 的语义搜索能力
- **轻量级**：仅使用 Python 标准库，无额外依赖
- **完整钩子系统**：
  - `PreToolUse` - 读取文件时自动分析代码
  - `PostToolUse` - 工具调用后自动记录结果
  - `UserPromptSubmit` - 用户提交消息时提示记忆可用性
  - `SessionStart` - 会话开始时初始化
  - `SessionEnd` - 会话结束时提交
  - `Stop` - 会话停止时清理

## 架构

```
bash hook scripts
    ↓
common.sh (shared helpers)
    ↓
memory_bridge.py (Python bridge)
    ↓
memory_plugin.py (core API)
```

### 钩子系统

| 钩子类型 | 触发时机 | 功能 |
|----------|----------|------|
| `PreToolUse` | 工具调用前 | 读取文件时自动分析代码 |
| `PostToolUse` | 工具调用后 | 工具调用后自动记录结果 |
| `UserPromptSubmit` | 用户提交消息 | 提示记忆可用性 |
| `SessionStart` | 会话开始时 | 初始化会话 |
| `SessionEnd` | 会话结束时 | 提交会话 |
| `Stop` | 会话停止时 | 清理资源 |

## 安装

### 自动安装

```bash
# 交互式安装
cd examples/claude-code-memory-plugin
chmod +x install.sh
./install.sh -i

# 或使用环境变量自动安装
export OPENVIKING_URL="http://localhost:1933"
./install.sh -a

# 安装到自定义目录
./install.sh -d ~/my-plugins/claude-memory
```

### 验证安装

```bash
# 验证插件架构（Claude Code 标准）
python3 verify_claude_plugin.py

# 验证基础安装
python3 verify_install.py

# 运行功能测试
python3 test_memory_plugin.py
python3 test_auto_memory.py
```

### 在 Claude Code 中使用

安装后，插件会自动注册到 Claude Code。你可以使用以下命令：

```bash
# 查看帮助
/memory

# 分析代码文件（自动触发）
Read src/main.py

# 手动分析
/memory analyze src/main.py

# 搜索记忆
/memory search "Python FastAPI"

# 列出所有记忆
/memory list

# 列出分支
/memory branches

# 使用记忆回忆技能
/memory-recall "用户认证模块的改动"
```

### 卸载

```bash
./uninstall.sh

# 强制卸载（不确认）
./uninstall.sh -f
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

### 代码自动记忆

#### 分析单个文件

```python
# 分析单个 Python 文件
entry = plugin.analyze_and_store_file("/path/to/your/file.py")
print(f"Stored: {entry.uri}")
# 自动提取函数、类、导入、docstring 等信息

# 分析 JavaScript 文件
js_entry = plugin.analyze_and_store_file("/path/to/app.js")
```

#### 扫描整个项目目录

```python
# 扫描整个项目
memories = plugin.analyze_and_store_directory("/path/to/project")
print(f"Stored {len(memories)} memories:")
for m in memories:
    print(f"  - {m.title} [{m.memory_type.value}]")

# 输出示例:
# - project (code_module) - 模块概览
# - main.py (code_file) - 主文件分析
# - user_handler.py (code_file) - 用户处理模块
# - project_dependencies (code_dependency) - 依赖关系
```

#### 存储代码片段

```python
# 存储自定义代码片段
snippet = plugin.store_code_snippet(
    title="user_handler",
    content='''def handle_user_request(user_id: int) -> Dict:
    """Handle user request with validation"""
    user = get_user(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    return {"status": "success", "data": user}''',
    language="python",
    tags=["handler", "user"]
)
```

#### 自动记忆提取内容

分析 Python 文件时会自动提取：
- **函数列表**: 函数名、参数、返回值类型
- **类定义**: 类名、继承关系
- **导入依赖**: 所有使用的库和模块
- **Docstrings**: 函数和类的文档字符串

### 分支感知功能

#### 初始化分支感知插件

```python
from memory_plugin import GitBranchInfo, TeamScope

# 创建分支信息
main_branch = GitBranchInfo("main")
feature_branch = GitBranchInfo("feature/user-auth")

# 创建团队作用域（包含分支信息）
team_scope = TeamScope(
    team_id="engineering",
    project_id="viking",
    branch_info=main_branch
)

# 初始化插件（指定团队和分支）
plugin = RemoteMemoryPlugin(
    openviking_url="http://localhost:1933",
    api_key="your-api-key",
    team_scope=team_scope,
    user_id="alice"  # 用户 ID 用于追踪修改
)
```

#### 分支特定的设计文档存储

```python
# 存储到 main 分支
main_doc = plugin.store_design_doc(
    title="API Design",
    content="# API Design\n\nMain branch API...",
    tags=["api", "main"],
    branch_aware=True  # 包含分支信息
)
print(f"URI: {main_doc.uri}")
# viking://resources/memories/design_doc/main/api_design

# 切换到 feature 分支
feature_scope = TeamScope(
    team_id="engineering",
    project_id="viking",
    branch_info=GitBranchInfo("feature/user-auth")
)
feature_plugin = RemoteMemoryPlugin(
    openviking_url="http://localhost:1933",
    api_key="your-api-key",
    team_scope=feature_scope
)

# 存储到 feature 分支（与 main 分支独立）
feature_doc = feature_plugin.store_design_doc(
    title="API Design",
    content="# API Design\n\nFeature branch API...",
    tags=["api", "feature"],
    branch_aware=True
)
print(f"URI: {feature_doc.uri}")
# viking://resources/memories/design_doc/feature-user-auth/api_design
```

#### 版本化管理

```python
# 存储带版本的设计文档
versioned_doc = plugin.store_design_doc_versioned(
    title="API Design",
    content="# API Design v2\n\nUpdated content...",
    tags=["api", "versioned"]
)

# 存储带版本的 API 接口
versioned_api = plugin.store_api_interface_versioned(
    title="create_user",
    content="create_user(name: str, email: str) -> User",
    params=[{"name": "name", "type": "str"}],
    returns={"type": "User"}
)
```

#### 分支特定的搜索

```python
# 搜索 main 分支的记忆
main_memories = plugin.search_memories("API", branch="main")
print(f"Main branch: {len(main_memories)} memories")

# 搜索 feature 分支的记忆
feature_memories = plugin.search_memories("API", branch="feature/user-auth")
print(f"Feature branch: {len(feature_memories)} memories")

# 获取特定分支的所有记忆
all_main_api = plugin.get_branch_memories(
    MemoryType.API_INTERFACE,
    branch="main",
    limit=20
)

# 列出所有有记忆的分支
branches = plugin.list_branches()
print(f"Branches with memories: {branches}")
```

#### 团队共享存储

```python
# 创建团队共享作用域
team_scope = TeamScope(
    team_id="engineering",
    project_id="viking"
    # 不指定 branch_info 表示团队级别共享（不分分支）
)

# 存储团队级别的设计文档
team_doc = plugin.store_design_doc(
    title="Team Standards",
    content="# Team Coding Standards\n\nAll branches...",
    tags=["team", "standards"],
    branch_aware=False  # 不区分分支
)

# 所有团队成员、所有分支都可以访问
```

## 核心 API

| 方法 | 描述 |
|------|------|
| `store_design_doc(title, content, tags, branch_aware, version)` | 存储设计文档（支持分支和版本） |
| `store_code_style(title, content, tags, branch_aware, version)` | 存储代码规范（支持分支） |
| `store_api_interface(title, content, params, returns, tags, branch_aware, version)` | 存储 API 接口（支持分支和版本） |
| `store_design_doc_versioned(title, content, tags)` | 存储带版本的设计文档 |
| `store_api_interface_versioned(title, content, params, returns, tags)` | 存储带版本的 API 接口 |
| `analyze_and_store_file(file_path, auto_store)` | 分析并存储单个代码文件 |
| `analyze_and_store_directory(dir_path, auto_store)` | 分析并存储整个目录 |
| `store_code_snippet(title, content, language, tags)` | 存储代码片段 |
| `initialize_session(session_id, context)` | 初始化会话 |
| `update_session(new_context)` | 更新会话 |
| `search_memories(query, memory_types, limit, branch)` | 搜索记忆（支持分支过滤） |
| `get_branch_memories(memory_type, branch, limit)` | 获取特定分支的所有记忆 |
| `list_branches()` | 列出所有有记忆的分支 |
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
| `CODE_FILE` | 代码文件分析 |
| `CODE_MODULE` | 模块/包分析 |
| `CODE_DEPENDENCY` | 依赖关系 |
| `TEAM_SHARED` | 团队共享记忆 |

## 环境变量

```bash
# OpenViking API 地址
export OPENVIKING_URL="http://localhost:1933"

# API 密钥
export OPENVIKING_API_KEY="your-api-key"

# 安装目录
export INSTALL_DIR="$HOME/.claude/claude-code-memory-plugin"
```

## 配置文件

创建 `~/.claude/code-memory-config.json`:

```json
{
  "openviking_url": "http://localhost:1933",
  "api_key": "your-api-key",
  "search_limit": 5,
  "install_dir": "$HOME/.claude/claude-code-memory-plugin"
}
```

## 优势

1. **无需本地存储**：所有记忆存储在 OpenViking，无需本地数据库
2. **跨设备同步**：记忆通过 OpenViking 服务同步
3. **语义搜索**：利用 OpenViking 的语义搜索能力
4. **轻量级**：仅使用 Python 标准库
5. **完整钩子系统**：支持完整的 Claude Code 钩子生命周期

## License

Apache License 2.0
