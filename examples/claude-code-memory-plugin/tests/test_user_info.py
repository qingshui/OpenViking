#!/usr/bin/env python3
"""
测试个人信息存储功能
验证 API 正确性和功能完整性
"""

import sys
import json
import os

# 添加插件路径
PLUGIN_ROOT = "/home/users/humingqing/work/OpenViking/examples/claude-code-memory-plugin"
sys.path.insert(0, PLUGIN_ROOT)

from memory_plugin import (
    RemoteMemoryPlugin,
    MemoryType,
)


def test_import():
    """测试导入"""
    print("=" * 60)
    print("测试 1: 导入检查")
    print("=" * 60)

    try:
        from memory_plugin import RemoteMemoryPlugin, MemoryType
        print("✓ 成功导入 RemoteMemoryPlugin")
        print("✓ 成功导入 MemoryType")
        print("✓ MemoryType 可用类型:")
        for mt in MemoryType:
            print(f"  - {mt.name}: {mt.value}")
        return True
    except ImportError as e:
        print(f"✗ 导入失败：{e}")
        return False


def test_plugin_initialization():
    """测试插件初始化"""
    print("\n" + "=" * 60)
    print("测试 2: 插件初始化")
    print("=" * 60)

    try:
        plugin = RemoteMemoryPlugin(
            openviking_url="http://localhost:1933",
            api_key="6z_TTilwV_CM16qV3ExG1PAVFCptrLp-ver8Xb1lGD8"
        )
        print(f"✓ 插件初始化成功")
        print(f"  - Base URL: {plugin.client.base_url}")
        print(f"  - Base URI: {plugin.base_uri}")
        return plugin
    except Exception as e:
        print(f"✗ 初始化失败：{e}")
        return None


def test_store_design_doc(plugin):
    """测试存储设计文档（替代存储邮箱）"""
    print("\n" + "=" * 60)
    print("测试 3: 存储设计文档")
    print("=" * 60)

    if not plugin:
        print("跳过：插件未初始化")
        return False

    try:
        title = "test_user_email_info"
        content = """
# User Email Information

This document contains user email information for testing purposes.

## Email
- Primary: qshuihu@gmail.com

## Description
Test user email for verification of the memory plugin functionality.
"""

        entry = plugin.store_design_doc(
            title=title,
            content=content,
            tags=["email", "user_info", "test"]
        )

        if entry and entry.uri:
            print(f"✓ 设计文档存储成功")
            print(f"  - URI: {entry.uri}")
            print(f"  - 类型：{entry.memory_type.value}")
            print(f"  - 标签：{entry.tags}")
            return entry
        else:
            print("✗ 设计文档存储失败")
            return False
    except Exception as e:
        print(f"✗ 存储失败：{e}")
        return False


def test_store_code_style(plugin):
    """测试存储代码规范（替代存储电话）"""
    print("\n" + "=" * 60)
    print("测试 4: 存储代码规范")
    print("=" * 60)

    if not plugin:
        print("跳过：插件未初始化")
        return False

    try:
        title = "test_user_phone_info"
        content = """
# User Phone Information

This document contains user phone information for testing purposes.

## Phone
- Mobile: +86-138-0013-8000

## Description
Test mobile phone for verification of the memory plugin functionality.
"""

        entry = plugin.store_code_style(
            title=title,
            content=content,
            tags=["phone", "user_info", "test"]
        )

        if entry and entry.uri:
            print(f"✓ 代码规范存储成功")
            print(f"  - URI: {entry.uri}")
            print(f"  - 类型：{entry.memory_type.value}")
            print(f"  - 标签：{entry.tags}")
            return entry
        else:
            print("✗ 代码规范存储失败")
            return False
    except Exception as e:
        print(f"✗ 存储失败：{e}")
        return False


def test_store_api_interface(plugin):
    """测试存储 API 接口（替代存储地址）"""
    print("\n" + "=" * 60)
    print("测试 5: 存储 API 接口")
    print("=" * 60)

    if not plugin:
        print("跳过：插件未初始化")
        return False

    try:
        title = "test_user_address_info"
        content = """
# User Address Information

This document contains user address information for testing purposes.

## Address
- Location: 北京市海淀区中关村大街 1 号

## Description
Test office address for verification of the memory plugin functionality.
"""

        entry = plugin.store_api_interface(
            title=title,
            content=content,
            params=[],
            returns={},
            tags=["address", "user_info", "test"]
        )

        if entry and entry.uri:
            print(f"✓ API 接口存储成功")
            print(f"  - URI: {entry.uri}")
            print(f"  - 类型：{entry.memory_type.value}")
            print(f"  - 标签：{entry.tags}")
            return entry
        else:
            print("✗ API 接口存储失败")
            return False
    except Exception as e:
        print(f"✗ 存储失败：{e}")
        return False


def test_get_memories(plugin):
    """测试获取记忆"""
    print("\n" + "=" * 60)
    print("测试 6: 获取记忆")
    print("=" * 60)

    if not plugin:
        print("跳过：插件未初始化")
        return False

    try:
        # 搜索用户信息相关的记忆
        memories = plugin.search_memories("user info", limit=5)
        print(f"✓ 搜索成功，找到 {len(memories)} 条结果")
        for mem in memories[:3]:
            print(f"  - {mem.title} [{mem.memory_type.value}]")
            print(f"    URI: {mem.uri}")
        return True
    except Exception as e:
        print(f"✗ 获取失败：{e}")
        return False


def test_memory_type_enum():
    """测试 MemoryType 枚举"""
    print("\n" + "=" * 60)
    print("测试 7: MemoryType 枚举")
    print("=" * 60)

    try:
        print("所有记忆类型:")
        for mem_type in MemoryType:
            print(f"  - {mem_type.name}: {mem_type.value}")

        # 检查 MemoryType 是否包含预期类型
        expected_types = ["DESIGN_DOC", "CODE_STYLE", "API_INTERFACE", "SESSION", "TASK", "PREFERENCE"]
        for expected in expected_types:
            if hasattr(MemoryType, expected):
                print(f"✓ {expected} 枚举存在")
            else:
                print(f"✗ {expected} 枚举不存在")
                return False
        return True
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return False


def test_generate_uri(plugin):
    """测试 URI 生成"""
    print("\n" + "=" * 60)
    print("测试 8: URI 生成")
    print("=" * 60)

    if not plugin:
        print("跳过：插件未初始化")
        return False

    try:
        # 测试不同记忆类型的 URI 生成
        test_cases = [
            (MemoryType.DESIGN_DOC, "test_document"),
            (MemoryType.CODE_STYLE, "test_code_style"),
            (MemoryType.API_INTERFACE, "test_api"),
            (MemoryType.PREFERENCE, "test_preference"),
        ]

        for mem_type, title in test_cases:
            uri = plugin._generate_uri(mem_type, title)
            print(f"  - {mem_type.name} + {title} -> {uri}")

        print("✓ URI 生成正常")
        return True
    except Exception as e:
        print(f"✗ URI 生成失败：{e}")
        return False


def test_api_methods(plugin):
    """测试 API 方法"""
    print("\n" + "=" * 60)
    print("测试 9: API 方法验证")
    print("=" * 60)

    if not plugin:
        print("跳过：插件未初始化")
        return False

    try:
        # 检查方法是否存在
        methods = [
            'store_design_doc',
            'store_code_style',
            'store_api_interface',
            'search_memories',
            'get_session',
            'get_all_memories'
        ]

        for method in methods:
            if hasattr(plugin, method):
                print(f"✓ {method} 方法存在")
            else:
                print(f"✗ {method} 方法不存在")
                return False

        return True
    except Exception as e:
        print(f"✗ 方法验证失败：{e}")
        return False


def test_memory_command():
    """测试 memory 命令"""
    print("\n" + "=" * 60)
    print("测试 10: memory 命令")
    print("=" * 60)

    try:
        import subprocess

        # 测试 /memory 命令
        result = subprocess.run(
            [
                "python3",
                f"{PLUGIN_ROOT}/scripts/memory_command.py",
                "search",
                "test",
                "--limit", "3"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            output = json.loads(result.stdout)
            print(f"✓ search 命令成功")
            print(f"  - 返回：{json.dumps(output, ensure_ascii=False, indent=2)}")
        else:
            print(f"✗ search 命令失败：{result.stderr}")

        return True
    except Exception as e:
        print(f"✗ 命令测试失败：{e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("个人信息存储功能测试")
    print("=" * 60)

    results = []

    # 测试 1: 导入
    results.append(("导入检查", test_import()))

    # 测试 2: 插件初始化
    plugin = test_plugin_initialization()
    results.append(("插件初始化", plugin is not None))

    # 测试 3: 存储设计文档
    if plugin:
        email_entry = test_store_design_doc(plugin)
        results.append(("存储设计文档", email_entry is not None))
    else:
        results.append(("存储设计文档", False))

    # 测试 4: 存储代码规范
    if plugin:
        phone_entry = test_store_code_style(plugin)
        results.append(("存储代码规范", phone_entry is not None))
    else:
        results.append(("存储代码规范", False))

    # 测试 5: 存储 API 接口
    if plugin:
        address_entry = test_store_api_interface(plugin)
        results.append(("存储 API 接口", address_entry is not None))
    else:
        results.append(("存储 API 接口", False))

    # 测试 6: 获取记忆
    if plugin:
        results.append(("获取记忆", test_get_memories(plugin)))
    else:
        results.append(("获取记忆", False))

    # 测试 7: MemoryType 枚举
    results.append(("MemoryType 枚举", test_memory_type_enum()))

    # 测试 8: URI 生成
    if plugin:
        results.append(("URI 生成", test_generate_uri(plugin)))
    else:
        results.append(("URI 生成", False))

    # 测试 9: API 方法
    if plugin:
        results.append(("API 方法", test_api_methods(plugin)))
    else:
        results.append(("API 方法", False))

    # 测试 10: memory 命令
    results.append(("memory 命令", test_memory_command()))

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
