#!/usr/bin/env python3
"""测试插件接口是否正常工作"""

import sys
import json

# 添加插件路径
PLUGIN_ROOT = "/home/users/humingqing/work/OpenViking/examples/claude-code-memory-plugin"
sys.path.insert(0, str(PLUGIN_ROOT))

def test_imports():
    """测试导入是否成功"""
    print("=" * 60)
    print("测试 1: 导入模块")
    print("=" * 60)

    try:
        from memory_plugin import (
            RemoteMemoryPlugin, GitBranchInfo, TeamScope,
            MemoryType, MemoryEntry, CodeAnalyzer
        )
        print("✓ 成功导入 RemoteMemoryPlugin")
        print("✓ 成功导入 GitBranchInfo")
        print("✓ 成功导入 TeamScope")
        print("✓ 成功导入 MemoryType")
        print("✓ 成功导入 MemoryEntry")
        print("✓ 成功导入 CodeAnalyzer")
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


def test_git_branch_info():
    """测试 GitBranchInfo 类"""
    print("\n" + "=" * 60)
    print("测试 3: GitBranchInfo 类")
    print("=" * 60)

    try:
        from memory_plugin import GitBranchInfo

        # 测试基本分支
        branch = GitBranchInfo("main")
        print(f"  分支名：{branch.branch_name}")
        print(f"  分支前缀：{branch.get_branch_prefix()}")
        print(f"  是否主分支：{branch.is_main_branch()}")

        # 测试功能分支
        feature_branch = GitBranchInfo("feature/user-auth")
        print(f"  功能分支：{feature_branch.branch_name}")
        print(f"  功能分支前缀：{feature_branch.get_branch_prefix()}")
        print(f"  是否功能分支：{feature_branch.is_feature_branch()}")

        print("✓ GitBranchInfo 类正常")
        return True
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return False


def test_team_scope():
    """测试 TeamScope 类"""
    print("\n" + "=" * 60)
    print("测试 4: TeamScope 类")
    print("=" * 60)

    try:
        from memory_plugin import TeamScope, GitBranchInfo

        # 测试基本团队作用域
        team = TeamScope(team_id="team-alpha")
        print(f"  团队命名空间：{team.get_namespace()}")
        print(f"  URI 前缀：{team.get_uri_prefix()}")

        # 测试带分支的团队作用域
        branch_info = GitBranchInfo("main")
        team_with_branch = TeamScope(
            team_id="team-engineering",
            project_id="project-webadmin",
            branch_info=branch_info
        )
        print(f"  带分支的命名空间：{team_with_branch.get_namespace()}")
        print(f"  分支感知 URI 前缀：{team_with_branch.get_branch_aware_prefix()}")

        print("✓ TeamScope 类正常")
        return True
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return False


def test_code_analyzer():
    """测试 CodeAnalyzer 类"""
    print("\n" + "=" * 60)
    print("测试 5: CodeAnalyzer 类")
    print("=" * 60)

    try:
        from memory_plugin import CodeAnalyzer

        analyzer = CodeAnalyzer()

        # 测试文件分析
        test_file = "/home/users/humingqing/work/OpenViking/examples/claude-code-memory-plugin/memory_plugin.py"
        if __import__('os').path.exists(test_file):
            result = analyzer.analyze_file(test_file)
            if 'error' not in result:
                print(f"  文件：{result.get('file_path', 'N/A')}")
                print(f"  语言：{result.get('language', 'N/A')}")
                print(f"  函数数：{len(result.get('functions', []))}")
                print(f"  类数：{len(result.get('classes', []))}")
                print(f"  导入数：{len(result.get('imports', []))}")
                print("✓ CodeAnalyzer 类正常")
                return True
            else:
                print(f"✗ 分析失败：{result.get('error')}")
                return False
        else:
            print("  跳过（测试文件不存在）")
            return True
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return False


def test_plugin_initialization():
    """测试插件初始化"""
    print("\n" + "=" * 60)
    print("测试 6: 插件初始化")
    print("=" * 60)

    try:
        from memory_plugin import RemoteMemoryPlugin, TeamScope, GitBranchInfo

        # 测试基本初始化
        plugin = RemoteMemoryPlugin(
            openviking_url="http://localhost:1933",
            api_key="test-key"
        )
        print(f"  插件初始化成功")
        print(f"  Base URL: {plugin.client.base_url}")
        print(f"  用户 ID: {plugin.user_id}")

        # 测试带团队作用域的初始化
        branch_info = GitBranchInfo("main")
        team_scope = TeamScope(team_id="individual", branch_info=branch_info)
        plugin_with_scope = RemoteMemoryPlugin(
            openviking_url="http://localhost:1933",
            api_key="test-key",
            team_scope=team_scope,
            user_id="claude-user"
        )
        print(f"  带团队作用域的插件初始化成功")
        print(f"  团队作用域：{plugin_with_scope.team_scope}")

        print("✓ 插件初始化正常")
        return True
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return False


def test_bridge_script():
    """测试 bridge 脚本"""
    print("\n" + "=" * 60)
    print("测试 7: Bridge 脚本")
    print("=" * 60)

    import subprocess

    try:
        # 测试 analyze-file 命令
        test_file = "/home/users/humingqing/work/OpenViking/examples/claude-code-memory-plugin/memory_plugin.py"
        if __import__('os').path.exists(test_file):
            result = subprocess.run(
                ["python3", "/home/users/humingqing/work/OpenViking/examples/claude-code-memory-plugin/scripts/memory_bridge.py",
                 "analyze-file", "--file-path", test_file],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                output = json.loads(result.stdout)
                print(f"  返回状态：{output.get('ok', False)}")
                if output.get('ok'):
                    print(f"  URI: {output.get('uri', 'N/A')}")
                    print(f"  函数数：{output.get('functions', 0)}")
                    print(f"  类数：{output.get('classes', 0)}")
                    print("✓ Bridge 脚本 analyze-file 命令正常")
                    return True
                else:
                    print(f"✗ 命令失败：{output.get('error')}")
                    return False
            else:
                print(f"✗ 命令执行失败：{result.stderr}")
                return False
        else:
            print("  跳过（测试文件不存在）")
            return True
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Claude Code Memory Plugin 接口测试")
    print("=" * 60)

    tests = [
        test_imports,
        test_memory_type_enum,
        test_git_branch_info,
        test_team_scope,
        test_code_analyzer,
        test_plugin_initialization,
        test_bridge_script,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n✗ 测试异常：{e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过：{passed}/{total}")

    if passed == total:
        print("\n✓ 所有测试通过！插件接口正常工作。")
        return 0
    else:
        print(f"\n✗ 有 {total - passed} 个测试失败。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
