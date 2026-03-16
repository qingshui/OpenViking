"""
测试记忆插件功能
"""

import sys
import os

# 添加插件目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from memory_plugin import (
    ClaudeCodeMemoryPlugin,
    OpenVikingClient,
    MemoryManager,
    MemoryType,
    MemoryEntry
)


def test_openviking_client():
    """测试 OpenViking 客户端"""
    print("=" * 50)
    print("测试 OpenViking 客户端")
    print("=" * 50)

    client = OpenVikingClient(
        base_url="http://localhost:1933",
        api_key="6z_TTilwV_CM16qV3ExG1PAVFCptrLp-ver8Xb1lGD8"
    )

    # 测试健康检查
    result = client._make_request("GET", "/health")
    print(f"Health check: {result}")

    # 测试系统状态
    result = client._make_request("GET", "/api/v1/system/status")
    print(f"System status: {result}")

    return client


def test_memory_manager(client):
    """测试记忆管理器"""
    print("\n" + "=" * 50)
    print("测试记忆管理器")
    print("=" * 50)

    manager = MemoryManager(client)

    # 测试存储设计文档
    print("\n1. 存储设计文档...")
    design_doc = manager.create_memory(
        title="Test Project Architecture",
        content="""# Project Architecture

## Overview
This is a test project for Claude Code Memory Plugin.

## Components
- API Server: FastAPI
- Database: PostgreSQL
- Cache: Redis

## Design Principles
- Modular design
- Clean code
- Testable
""",
        memory_type=MemoryType.DESIGN_DOC,
        tags=["architecture", "test", "backend"],
        metadata={"version": "1.0", "author": "test"}
    )
    print(f"Design doc stored: {design_doc.uri}")
    print(f"ID: {design_doc.id}")

    # 测试存储代码规范
    print("\n2. 存储代码规范...")
    code_style = manager.create_memory(
        title="Python Coding Standards",
        content="""# Python Coding Standards

## Naming Conventions
- Variables: snake_case
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE

## Code Structure
- Maximum line length: 88 characters
- Use type hints
- Follow PEP 8

## Documentation
- Docstrings for all functions
- Comments for complex logic
""",
        memory_type=MemoryType.CODE_STYLE,
        tags=["python", "standards", "pep8"],
        metadata={"version": "1.0"}
    )
    print(f"Code style stored: {code_style.uri}")

    # 测试存储 API 接口
    print("\n3. 存储 API 接口...")
    api_interface = manager.create_memory(
        title="create_user",
        content="create_user(name: str, email: str) -> User",
        memory_type=MemoryType.API_INTERFACE,
        tags=["api", "user", "fastapi"],
        metadata={
            "params": [
                {"name": "name", "type": "str", "description": "User name"},
                {"name": "email", "type": "str", "description": "User email"}
            ],
            "returns": {"type": "User", "description": "Created user object"}
        }
    )
    print(f"API interface stored: {api_interface.uri}")

    # 测试搜索记忆
    print("\n4. 搜索记忆...")
    memories = manager.search_memories("Python FastAPI database", limit=5)
    print(f"Found {len(memories)} memories:")
    for memory in memories:
        print(f"  - {memory.title} ({memory.memory_type.value})")

    # 测试获取记忆
    print("\n5. 获取记忆...")
    retrieved = manager.get_memory(design_doc.uri)
    if retrieved:
        print(f"Retrieved: {retrieved.title}")
        print(f"Content preview: {retrieved.content[:100]}...")

    # 测试更新记忆
    print("\n6. 更新记忆...")
    updated = manager.update_memory(
        design_doc.uri,
        f"""# Project Architecture

## Overview
Updated test project with new features.

## Components
- API Server: FastAPI
- Database: PostgreSQL
- Cache: Redis
- Message Queue: RabbitMQ

## Design Principles
- Modular design
- Clean code
- Testable
- Scalable
"""
    )
    if updated:
        print(f"Updated: {updated.title}")
        print(f"Updated at: {updated.updated_at}")

    # 测试获取摘要
    print("\n7. 获取记忆摘要...")
    summary = manager.client.content_abstract(design_doc.uri)
    if "data" in summary:
        print(f"Abstract: {summary['data']}")

    return manager


def test_claude_code_plugin():
    """测试 Claude Code 记忆插件"""
    print("\n" + "=" * 50)
    print("测试 Claude Code 记忆插件")
    print("=" * 50)

    plugin = ClaudeCodeMemoryPlugin(
        openviking_url="http://localhost:1933",
        api_key="6z_TTilwV_CM16qV3ExG1PAVFCptrLp-ver8Xb1lGD8"
    )

    # 测试初始化会话
    print("\n1. 初始化会话...")
    plugin.initialize_session(
        session_id="test-session-001",
        context="正在开发一个 Python Web 应用，使用 FastAPI 和 PostgreSQL"
    )
    print("Session initialized: test-session-001")

    # 测试存储设计文档
    print("\n2. 存储设计文档...")
    design = plugin.store_design_doc(
        title="Web Application Architecture",
        content="""# Web Application Architecture

## Overview
A scalable web application built with modern technologies.

## Tech Stack
- Backend: Python FastAPI
- Database: PostgreSQL with SQLAlchemy
- Cache: Redis
- Frontend: React

## Architecture Pattern
- RESTful API
- Microservices ready
- Containerized with Docker
""",
        tags=["architecture", "backend", "web"]
    )
    print(f"Stored: {design.uri}")

    # 测试存储代码规范
    print("\n3. 存储代码规范...")
    style = plugin.store_code_style(
        title="FastAPI Project Standards",
        content="""# FastAPI Project Standards

## Project Structure
```
project/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   └── models/
├── tests/
├── requirements.txt
└── main.py
```

## Code Style
- Use async/await
- Type hints required
- Error handling with exceptions
""",
        tags=["fastapi", "standards", "python"]
    )
    print(f"Stored: {style.uri}")

    # 测试存储 API 接口
    print("\n4. 存储 API 接口...")
    api = plugin.store_api_interface(
        title="GET /users/{user_id}",
        content="GET /users/{user_id} -> User",
        params=[
            {"name": "user_id", "type": "int", "location": "path", "description": "User ID"}
        ],
        returns={
            "type": "User",
            "description": "User details",
            "schema": {
                "id": "int",
                "name": "str",
                "email": "str"
            }
        },
        tags=["api", "rest", "users"]
    )
    print(f"Stored: {api.uri}")

    # 测试获取相关记忆
    print("\n5. 获取相关记忆...")
    relevant = plugin.get_relevant_memories(
        context="Python FastAPI database PostgreSQL architecture",
        memory_types=[MemoryType.DESIGN_DOC, MemoryType.CODE_STYLE],
        limit=5
    )
    print(f"Found {len(relevant)} relevant memories:")
    for memory in relevant:
        print(f"  - {memory.title} [{memory.memory_type.value}]")

    # 测试更新会话
    print("\n6. 更新会话...")
    plugin.update_session("正在开发 Python FastAPI Web 应用，使用 PostgreSQL 数据库和 Redis 缓存")
    print("Session updated")

    # 获取记忆摘要
    print("\n7. 获取记忆摘要...")
    summary = plugin.get_memory_summary(design.uri)
    if summary:
        print(f"Summary keys: {list(summary.keys())}")


def main():
    """主测试函数"""
    print("\n" + "#" * 60)
    print("# Claude Code Memory Plugin 测试")
    print("#" * 60)

    # 测试 OpenViking 客户端
    client = test_openviking_client()

    # 测试记忆管理器
    manager = test_memory_manager(client)

    # 测试记忆插件
    test_claude_code_plugin()

    print("\n" + "=" * 50)
    print("所有测试完成！")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
