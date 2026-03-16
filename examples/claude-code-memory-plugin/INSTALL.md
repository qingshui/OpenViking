# Claude Code Memory Plugin 安装指南

## 概述

本插件**无需本地安装**，所有记忆直接存储到远程 OpenViking 服务。

只需复制插件代码到任意位置即可使用。

## 前置要求

### 1. Python 环境

- Python 3.10 或更高版本
- **无需额外依赖**，使用 Python 标准库

### 2. OpenViking 服务

确保可以访问 OpenViking API：

```bash
# 本地服务
curl http://localhost:1933/health

# 或远程服务
curl http://your-openviking-server:1933/health
```

## 安装步骤

### 1. 复制插件代码

```bash
# 从 OpenViking 仓库复制
cp -r /home/users/humingqing/work/OpenViking/examples/claude-code-memory-plugin \
      ~/.openviking/claude-code-memory-plugin

# 或克隆到任意位置
git clone <repository-url> ~/claude-code-memory-plugin
```

### 2. 配置环境变量（可选）

```bash
# 设置 OpenViking API 地址
export OPENVIKING_URL="http://localhost:1933"

# 设置 API 密钥
export OPENVIKING_API_KEY="6z_TTilwV_CM16qV3ExG1PAVFCptrLp-ver8Xb1lGD8"
```

### 3. 验证安装

```bash
cd ~/.openviking/claude-code-memory-plugin

# 运行测试
python3 test_memory_plugin.py
```

## 快速开始

### 基础使用

```python
from memory_plugin import RemoteMemoryPlugin, MemoryType

# 初始化插件
plugin = RemoteMemoryPlugin(
    openviking_url="http://localhost:1933",
    api_key="your-api-key"
)

# 存储记忆
plugin.store_design_doc(
    title="Project Architecture",
    content="# Project Architecture\n\n## Overview...",
    tags=["architecture"]
)

# 搜索记忆
memories = plugin.search_memories("Python FastAPI")
```

## 远程 OpenViking 配置

### 使用远程服务

如果 OpenViking 部署在远程服务器上：

```python
plugin = RemoteMemoryPlugin(
    openviking_url="https://openviking.example.com:1933",
    api_key="your-remote-api-key"
)
```

### 配置文件

创建 `~/.claude/code-memory-config.json`:

```json
{
  "openviking_url": "https://openviking.example.com:1933",
  "api_key": "your-api-key",
  "search_limit": 5
}
```

## 故障排除

### 1. 连接失败

```bash
# 测试 API 连接
curl http://localhost:1933/health

# 检查服务状态
~/.openviking/services.sh status
```

### 2. 认证失败

检查 API 密钥是否正确：

```bash
curl http://localhost:1933/api/v1/system/status \
  -H "X-API-Key: your-api-key"
```

### 3. 存储失败

检查 OpenViking 服务是否正常处理请求：

```bash
# 查看服务器日志
tail -f ~/.openviking/log/server.log
```

## 使用示例

### 存储项目文档

```python
from memory_plugin import RemoteMemoryPlugin

plugin = RemoteMemoryPlugin(
    openviking_url="http://localhost:1933",
    api_key="6z_TTilwV_CM16qV3ExG1PAVFCptrLp-ver8Xb1lGD8"
)

# 存储设计文档
plugin.store_design_doc(
    title="System Architecture",
    content="""
# System Architecture

## Components
- API Server: FastAPI
- Database: PostgreSQL
- Cache: Redis
""",
    tags=["architecture", "backend"]
)

# 存储代码规范
plugin.store_code_style(
    title="Python Standards",
    content="""
# Python Standards

## Naming Conventions
- Variables: snake_case
- Classes: PascalCase

## Code Quality
- Type hints required
- Follow PEP 8
""",
    tags=["python", "standards"]
)

# 存储 API 接口
plugin.store_api_interface(
    title="create_user",
    content="create_user(name: str, email: str) -> User",
    params=[
        {"name": "name", "type": "str", "description": "User name"},
        {"name": "email", "type": "str", "description": "User email"}
    ],
    returns={"type": "User"},
    tags=["api", "user"]
)
```

### 管理会话

```python
# 初始化会话
plugin.initialize_session("dev-session-1", "正在开发用户模块")

# 更新会话
plugin.update_session("已完成用户注册，正在实现登录")

# 获取会话
session = plugin.get_session("dev-session-1")
print(session["context"])
```

### 搜索记忆

```python
# 搜索相关记忆
memories = plugin.search_memories("Python FastAPI database")

for memory in memories:
    print(f"- {memory.title}: {memory.content[:100]}...")
```

### 分支感知功能

#### 多分支代码结构区分

```python
from memory_plugin import GitBranchInfo, TeamScope, RemoteMemoryPlugin

# 场景：main 分支和 feature 分支有不同的 API 设计

# 1. 在 main 分支工作
main_scope = TeamScope(
    team_id="engineering",
    project_id="viking",
    branch_info=GitBranchInfo("main")
)
main_plugin = RemoteMemoryPlugin(
    openviking_url="http://localhost:1933",
    api_key="your-api-key",
    team_scope=main_scope,
    user_id="alice"
)

# 存储 main 分支的 API 设计
main_plugin.store_api_interface(
    title="create_user",
    content="create_user(name: str, email: str) -> User",
    params=[{"name": "name", "type": "str"}],
    branch_aware=True
)

# 2. 切换到 feature 分支
feature_scope = TeamScope(
    team_id="engineering",
    project_id="viking",
    branch_info=GitBranchInfo("feature/user-auth")
)
feature_plugin = RemoteMemoryPlugin(
    openviking_url="http://localhost:1933",
    api_key="your-api-key",
    team_scope=feature_scope,
    user_id="bob"
)

# 存储 feature 分支的 API 设计（独立存储）
feature_plugin.store_api_interface(
    title="create_user",
    content="create_user(name: str, email: str, phone: str) -> User",
    params=[{"name": "name", "type": "str"}, {"name": "email", "type": "str"}, {"name": "phone", "type": "str"}],
    branch_aware=True
)

# 3. 搜索特定分支的记忆
main_apis = feature_plugin.search_memories("create_user", branch="main")
feature_apis = feature_plugin.search_memories("create_user", branch="feature/user-auth")

print(f"Main branch API params: {len(main_apis[0].metadata.get('params', []))}")  # 2 params
print(f"Feature branch API params: {len(feature_apis[0].metadata.get('params', []))}")  # 3 params
```

#### 团队共享存储

```python
# 团队级别的设计文档（所有分支共享）
team_scope = TeamScope(
    team_id="engineering",
    project_id="viking"
    # 不指定 branch_info -> 团队共享
)

team_plugin = RemoteMemoryPlugin(
    openviking_url="http://localhost:1933",
    api_key="your-api-key",
    team_scope=team_scope
)

# 存储团队规范（不分分支）
team_plugin.store_code_style(
    title="Python Standards",
    content="# Python Standards\n- Variables: snake_case\n- Classes: PascalCase",
    tags=["team", "standards"],
    branch_aware=False  # 不区分分支
)

# 所有团队成员、所有分支都可以访问
```

#### 版本化管理

```python
# 自动版本化管理
plugin = RemoteMemoryPlugin(
    openviking_url="http://localhost:1933",
    api_key="your-api-key"
)

# 版本 1
plugin.store_design_doc_versioned(
    title="System Architecture",
    content="# Architecture v1\nOld design..."
)

# 版本 2（自动递增）
plugin.store_design_doc_versioned(
    title="System Architecture",
    content="# Architecture v2\nNew design with microservices..."
)

# 版本 3（自动递增）
plugin.store_design_doc_versioned(
    title="System Architecture",
    content="# Architecture v3\nAdded event-driven architecture..."
)
```

#### 分支信息检测

```python
from memory_plugin import GitBranchInfo

# 手动指定分支
branch = GitBranchInfo("feature/user-authentication")
print(branch.get_branch_prefix())  # "feature-user-authentication"
print(branch.is_feature_branch())  # True
print(branch.is_main_branch())     # False

# 自动检测（从 Git 仓库）
branch = GitBranchInfo(repo_path="/path/to/git/repo")
# 自动从 Git 获取当前分支名称
```

#### 使用 CodeAnalyzer 进行自定义分析

```python
from memory_plugin import CodeAnalyzer

analyzer = CodeAnalyzer()

# 检测文件语言
lang = analyzer.detect_language("file.py")  # "python"

# 分析单个文件
result = analyzer.analyze_file("/path/to/file.py")
print(f"Functions: {len(result['functions'])}")
print(f"Classes: {len(result['classes'])}")
print(f"Imports: {result['imports']}")

# 分析整个目录
dir_result = analyzer.analyze_directory("/path/to/project", ['.py', '.js'])
print(f"Total files: {dir_result['summary']['total_files']}")
print(f"Total functions: {dir_result['summary']['total_functions']}")
print(f"Libraries: {dir_result['summary']['libraries']}")
```

## 优势

1. **无需本地存储**：所有记忆存储在 OpenViking 服务
2. **轻量级**：仅使用 Python 标准库
3. **跨设备同步**：记忆通过 OpenViking 服务同步
4. **语义搜索**：利用 OpenViking 的语义搜索能力

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
