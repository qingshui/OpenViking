#!/usr/bin/env python3
"""测试插件接口是否正常工作"""

import sys
import json
import os

# 添加插件路径
PLUGIN_ROOT = "/home/users/humingqing/work/OpenViking/examples/claude-code-memory-plugin"
sys.path.insert(0, PLUGIN_ROOT)


def test_imports():
    """测试导入是否成功"""
    print("=" * 60)
    print("测试 1: 导入模块")
    print("=" * 60)

    try:
        from memory_plugin import (
            RemoteMemoryPlugin,
            MemoryType,
            MemoryEntry,
            OpenVikingClient,
        )
        print("✓ 成功导入 RemoteMemoryPlugin")
        print("✓ 成功导入 MemoryType")
        print("✓ 成功导入 MemoryEntry")
        print("✓ 成功导入 OpenVikingClient")
        return True
    except ImportError as e:
        print(f"✗ 导入失败：{e}")
        return False


def test_memory_type_enum():
    """测试 MemoryType 枚举"""
    print("\n" + "=" * 60)
    print("测试 2: MemoryType 枚举")
    print("=" * 60)

    try:
        from memory_plugin import MemoryType

        for mem_type in MemoryType:
            print(f"  - {mem_type.name}: {mem_type.value}")
        print("✓ MemoryType 枚举正常")
        return True
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return False


def test_memory_entry():
    """测试 MemoryEntry 类"""
    print("\n" + "=" * 60)
    print("测试 3: MemoryEntry 类")
    print("=" * 60)

    try:
        from memory_plugin import MemoryEntry, MemoryType

        entry = MemoryEntry(
            title="Test Document",
            content="Test content",
            memory_type=MemoryType.DESIGN_DOC,
            tags=["test", "verification"],
            metadata={"version": "1.0"}
        )
        print(f"  标题：{entry.title}")
        print(f"  类型：{entry.memory_type.value}")
        print(f"  标签：{entry.tags}")
        print(f"  元数据：{entry.metadata}")
        print("✓ MemoryEntry 类正常")
        return True
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return False


def test_openviking_client():
    """测试 OpenVikingClient 类"""
    print("\n" + "=" * 60)
    print("测试 4: OpenVikingClient 类")
    print("=" * 60)

    try:
        from memory_plugin import OpenVikingClient

        client = OpenVikingClient(
            base_url="http://localhost:1933",
            api_key="6z_TTilwV_CM16qV3ExG1PAVFCptrLp-ver8Xb1lGD8"
        )
        print(f"  Base URL: {client.base_url}")
        print(f"  API Key: {'*' * 8 if client.api_key else 'None'}")
        print("✓ OpenVikingClient 类正常")
        return True
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return False


def test_plugin_initialization():
    """测试插件初始化"""
    print("\n" + "=" * 60)
    print("测试 5: 插件初始化")
    print("=" * 60)

    try:
        from memory_plugin import RemoteMemoryPlugin

        plugin = RemoteMemoryPlugin(
            openviking_url="http://localhost:1933",
            api_key="6z_TTilwV_CM16qV3ExG1PAVFCptrLp-ver8Xb1lGD8"
        )
        print(f"  Base URL: {plugin.client.base_url}")
        print(f"  Base URI: {plugin.base_uri}")
        print(f"  Current Session: {plugin.current_session}")
        print("✓ 插件初始化正常")
        return plugin
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return None


def test_uri_generation(plugin):
    """测试 URI 生成"""
    print("\n" + "=" * 60)
    print("测试 6: URI 生成")
    print("=" * 60)

    if not plugin:
        print("跳过：插件未初始化")
        return False

    try:
        from memory_plugin import MemoryType

        test_cases = [
            (MemoryType.DESIGN_DOC, "test_document"),
            (MemoryType.CODE_STYLE, "test_code_style"),
            (MemoryType.API_INTERFACE, "test_api"),
            (MemoryType.SESSION, "test_session"),
            (MemoryType.PREFERENCE, "test_preference"),
        ]

        for mem_type, title in test_cases:
            uri = plugin._generate_uri(mem_type, title)
            print(f"  {mem_type.name} + {title} -> {uri}")

        print("✓ URI 生成正常")
        return True
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return False


def test_api_methods(plugin):
    """测试 API 方法"""
    print("\n" + "=" * 60)
    print("测试 7: API 方法验证")
    print("=" * 60)

    if not plugin:
        print("跳过：插件未初始化")
        return False

    try:
        methods = [
            'store_design_doc',
            'store_code_style',
            'store_api_interface',
            'initialize_session',
            'update_session',
            'search_memories',
            'get_session',
            'get_all_memories',
        ]

        for method in methods:
            if hasattr(plugin, method):
                print(f"✓ {method} 方法存在")
            else:
                print(f"✗ {method} 方法不存在")
                return False

        print("✓ 所有 API 方法正常")
        return True
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return False


def test_bridge_script():
    """测试 Bridge 脚本"""
    print("\n" + "=" * 60)
    print("测试 8: Bridge 脚本")
    print("=" * 60)

    try:
        import subprocess

        # 测试 memory_bridge.py 是否存在
        script_path = os.path.join(PLUGIN_ROOT, "scripts", "memory_bridge.py")
        if __import__('os').path.exists(script_path):
            print(f"✓ Bridge 脚本存在：{script_path}")
            return True
        else:
            print(f"✗ Bridge 脚本不存在：{script_path}")
            return False
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return False


def test_hooks():
    """测试 Hooks"""
    print("\n" + "=" * 60)
    print("测试 9: Hooks")
    print("=" * 60)

    try:
        import os

        hooks_dir = f"{PLUGIN_ROOT}/hooks"
        if os.path.exists(hooks_dir):
            hooks_files = os.listdir(hooks_dir)
            print(f"✓ Hooks 目录存在")
            print(f"  Hooks 文件:")
            for f in hooks_files:
                print(f"    - {f}")
            return True
        else:
            print(f"✗ Hooks 目录不存在：{hooks_dir}")
            return False
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return False


def test_skills():
    """测试 Skills"""
    print("\n" + "=" * 60)
    print("测试 10: Skills")
    print("=" * 60)

    try:
        import os

        skills_dir = f"{PLUGIN_ROOT}/skills"
        if os.path.exists(skills_dir):
            skills_files = os.listdir(skills_dir)
            print(f"✓ Skills 目录存在")
            print(f"  Skills 文件:")
            for f in skills_files:
                print(f"    - {f}")
            return True
        else:
            print(f"✗ Skills 目录不存在：{skills_dir}")
            return False
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Claude Code Memory Plugin 接口测试")
    print("=" * 60)

    results = []

    # 测试 1: 导入
    results.append(("导入模块", test_imports()))

    # 测试 2: MemoryType 枚举
    results.append(("MemoryType 枚举", test_memory_type_enum()))

    # 测试 3: MemoryEntry 类
    results.append(("MemoryEntry 类", test_memory_entry()))

    # 测试 4: OpenVikingClient 类
    results.append(("OpenVikingClient 类", test_openviking_client()))

    # 测试 5: 插件初始化
    plugin = test_plugin_initialization()
    results.append(("插件初始化", plugin is not None))

    # 测试 6: URI 生成
    if plugin:
        results.append(("URI 生成", test_uri_generation(plugin)))
    else:
        results.append(("URI 生成", False))

    # 测试 7: API 方法
    if plugin:
        results.append(("API 方法", test_api_methods(plugin)))
    else:
        results.append(("API 方法", False))

    # 测试 8: Bridge 脚本
    results.append(("Bridge 脚本", test_bridge_script()))

    # 测试 9: Hooks
    results.append(("Hooks", test_hooks()))

    # 测试 10: Skills
    results.append(("Skills", test_skills()))

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {status}: {name}")

    print(f"\n通过：{passed}/{total}")

    if passed == total:
        print("\n✓ 所有测试通过！")
        sys.exit(0)
    else:
        print(f"\n✗ 有 {total - passed} 个测试失败。")
        sys.exit(1)


if __name__ == "__main__":
    main()
