"""
测试远程记忆插件功能
无需本地安装，直接连接远程 OpenViking 服务
"""

import sys
import os

# 添加插件根目录到路径
PLUGIN_ROOT = "/home/users/humingqing/work/OpenViking/examples/claude-code-memory-plugin"
sys.path.insert(0, PLUGIN_ROOT)

from memory_plugin import (
    RemoteMemoryPlugin,
    OpenVikingClient,
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


def test_remote_memory_plugin(client):
    """测试远程记忆插件"""
    print("\n" + "=" * 50)
    print("测试远程记忆插件")
    print("=" * 50)

    plugin = RemoteMemoryPlugin(
        openviking_url="http://localhost:1933",
        api_key="6z_TTilwV_CM16qV3ExG1PAVFCptrLp-ver8Xb1lGD8"
    )

    # 测试存储设计文档
    print("\n1. 存储设计文档...")
    design_doc = plugin.store_design_doc(
        title="Test Project Architecture",
        content="# Test Project Architecture\n\nThis is a test project.",
        tags=["architecture", "test"]
    )
    print(f"Design doc stored: {design_doc.uri}")
    print(f"Title: {design_doc.title}")

    # 测试存储代码规范
    print("\n2. 存储代码规范...")
    code_style = plugin.store_code_style(
        title="Python Coding Standards",
        content="# Python Coding Standards\n\n## Naming\n- Variables: snake_case",
        tags=["python", "standards"]
    )
    print(f"Code style stored: {code_style.uri}")

    # 测试存储 API 接口
    print("\n3. 存储 API 接口...")
    api_interface = plugin.store_api_interface(
        title="create_user",
        content="create_user(name: str, email: str) -> User",
        params=[
            {"name": "name", "type": "str", "description": "User name"},
            {"name": "email", "type": "str", "description": "User email"}
        ],
        returns={"type": "User"},
        tags=["api", "user"]
    )
    print(f"API interface stored: {api_interface.uri}")

    # 测试初始化会话
    print("\n4. 初始化会话...")
    plugin.initialize_session(
        session_id="test-session-001",
        context="正在开发一个 Python Web 应用"
    )
    print("Session initialized: test-session-001")

    # 测试搜索记忆
    print("\n5. 搜索记忆...")
    memories = plugin.search_memories("Python FastAPI", limit=5)
    print(f"Found {len(memories)} memories:")
    for memory in memories:
        print(f"  - {memory.title} [{memory.memory_type.value}]")

    # 测试更新会话
    print("\n6. 更新会话...")
    plugin.update_session("正在开发 Python Web 应用，使用 FastAPI 框架")
    print("Session updated")

    # 获取会话数据
    print("\n7. 获取会话数据...")
    session_data = plugin.get_session("test-session-001")
    if session_data:
        print(f"Session context: {session_data.get('context', '')[:100]}...")

    return plugin


def main():
    """主测试函数"""
    print("\n" + "#" * 60)
    print("# Remote Memory Plugin 测试")
    print("# 使用远程 OpenViking 服务")
    print("#" * 60)

    # 测试 OpenViking 客户端
    client = test_openviking_client()

    # 测试远程记忆插件
    plugin = test_remote_memory_plugin(client)

    print("\n" + "=" * 50)
    print("所有测试完成！")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
