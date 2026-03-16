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
