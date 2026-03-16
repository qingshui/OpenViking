"""
测试代码自动记忆功能
"""

import sys
import os

# 添加插件目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from memory_plugin import (
    RemoteMemoryPlugin,
    CodeAnalyzer,
    MemoryType,
    GitBranchInfo,
    TeamScope
)


def test_code_analyzer():
    """测试代码分析器"""
    print("=" * 50)
    print("测试 CodeAnalyzer")
    print("=" * 50)

    analyzer = CodeAnalyzer()

    # 测试语言检测
    test_files = [
        "test.py",
        "app.js",
        "component.tsx",
        "Main.java",
        "main.go",
        "app.rs",
        "script.sh"
    ]

    print("\n1. 语言检测测试:")
    for f in test_files:
        lang = analyzer.detect_language(f)
        print(f"   {f} -> {lang}")

    # 测试分析本地插件文件
    plugin_path = os.path.join(os.path.dirname(__file__), "memory_plugin.py")
    if os.path.exists(plugin_path):
        print(f"\n2. 分析本地文件：{plugin_path}")
        result = analyzer.analyze_file(plugin_path)

        if "error" not in result:
            print(f"   语言：{result['language']}")
            print(f"   总行数：{result['total_lines']}")
            print(f"   函数数量：{len(result.get('functions', []))}")
            print(f"   类数量：{len(result.get('classes', []))}")
            print(f"   导入模块：{result.get('imports', [])}")

            # 显示前几个函数
            if result.get('functions'):
                print("\n   前 5 个函数:")
                for func in result['functions'][:5]:
                    params_str = ', '.join([f"{p['name']}: {p['type']}" for p in func['params']])
                    print(f"     - {func['name']}({params_str}) -> {func['return_type']}")

            # 显示前几个类
            if result.get('classes'):
                print("\n   前 5 个类:")
                for cls in result['classes'][:5]:
                    print(f"     - {cls['name']}({cls['inherits']})")
        else:
            print(f"   错误：{result['error']}")

    # 测试目录分析
    example_dir = os.path.dirname(__file__)
    print(f"\n3. 分析目录：{example_dir}")
    dir_result = analyzer.analyze_directory(example_dir, ['.py'])

    print(f"   总文件数：{dir_result['summary']['total_files']}")
    print(f"   总函数数：{dir_result['summary']['total_functions']}")
    print(f"   总类数：{dir_result['summary']['total_classes']}")
    print(f"   使用的库：{dir_result['summary']['libraries']}")

    return analyzer


def test_auto_memory_plugin(client=None):
    """测试自动记忆插件"""
    print("\n" + "=" * 50)
    print("测试自动记忆插件")
    print("=" * 50)

    plugin = RemoteMemoryPlugin(
        openviking_url="http://localhost:1933",
        api_key="6z_TTilwV_CM16qV3ExG1PAVFCptrLp-ver8Xb1lGD8"
    )

    # 测试存储代码片段
    print("\n1. 存储代码片段...")
    snippet = plugin.store_code_snippet(
        title="test_function",
        content='''def process_data(data: list) -> dict:
    """Process input data and return results"""
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return {"count": len(result), "data": result}''',
        language="python",
        tags=["test", "utility"]
    )
    print(f"   存储成功：{snippet.uri}")

    # 测试分析本地文件（如果 OpenViking 可用）
    plugin_path = os.path.join(os.path.dirname(__file__), "memory_plugin.py")
    if os.path.exists(plugin_path):
        print("\n2. 分析并存储本地文件...")
        try:
            file_entry = plugin.analyze_and_store_file(plugin_path, auto_store=True)
            print(f"   存储成功：{file_entry.uri}")
            print(f"   提取的函数数：{len(file_entry.metadata.get('functions', []))}")
            print(f"   提取的类数：{len(file_entry.metadata.get('classes', []))}")
        except Exception as e:
            print(f"   跳过（OpenViking 服务可能不可用）: {e}")

    # 测试存储设计文档用于搜索测试
    print("\n3. 存储测试数据用于搜索...")
    try:
        plugin.store_design_doc(
            title="Auto Memory Feature",
            content="# Auto Memory Feature\n\nCode analysis and automatic memory storage.",
            tags=["auto", "memory", "code"]
        )
        print("   设计文档存储成功")
    except Exception as e:
        print(f"   跳过：{e}")

    # 测试搜索
    print("\n4. 搜索记忆...")
    try:
        memories = plugin.search_memories("code memory", limit=3)
        print(f"   找到 {len(memories)} 个记忆:")
        for m in memories:
            print(f"     - {m.title} [{m.memory_type.value}]")
    except Exception as e:
        print(f"   跳过：{e}")

    return plugin


def test_branch_aware_memory():
    """测试分支感知记忆功能"""
    print("\n" + "=" * 50)
    print("测试分支感知记忆")
    print("=" * 50)

    # 测试 GitBranchInfo
    print("\n1. GitBranchInfo 测试:")
    branches = [
        "main",
        "develop",
        "feature/user-authentication",
        "release/v1.0.0",
        "hotfix/security-patch"
    ]

    for branch_name in branches:
        git_info = GitBranchInfo(branch_name)
        print(f"   {branch_name}:")
        print(f"      规范化：{git_info.get_branch_prefix()}")
        print(f"      主分支：{git_info.is_main_branch()}")
        print(f"      开发分支：{git_info.is_dev_branch()}")
        print(f"      功能分支：{git_info.is_feature_branch()}")

    # 测试 TeamScope 与分支
    print("\n2. TeamScope 分支感知测试:")
    team_scope = TeamScope(
        team_id="engineering",
        project_id="viking",
        branch_info=GitBranchInfo("feature/api-v2")
    )
    print(f"   命名空间：{team_scope.get_namespace()}")
    print(f"   URI 前缀：{team_scope.get_uri_prefix()}")
    print(f"   分支感知 URI: {team_scope.get_branch_aware_prefix()}")

    # 测试分支特定的记忆存储
    print("\n3. 分支记忆存储测试:")
    plugin = RemoteMemoryPlugin(
        openviking_url="http://localhost:1933",
        api_key="6z_TTilwV_CM16qV3ExG1PAVFCptrLp-ver8Xb1lGD8",
        team_scope=TeamScope("engineering", "viking", GitBranchInfo("main"))
    )

    # 存储 main 分支的设计文档
    try:
        main_doc = plugin.store_design_doc(
            title="API Design",
            content="# API Design for Main Branch\n\n## Overview\nMain branch API design.",
            tags=["api", "main"],
            branch_aware=True
        )
        print(f"   Main 分支存储：{main_doc.uri}")
        print(f"   元数据：{main_doc.metadata}")
    except Exception as e:
        print(f"   跳过（OpenViking 不可用）: {e}")

    # 测试分支特定的搜索
    print("\n4. 分支搜索测试:")
    try:
        # 搜索 main 分支的记忆
        main_memories = plugin.search_memories("API", branch="main")
        print(f"   Main 分支找到 {len(main_memories)} 个记忆")

        # 搜索所有分支的记忆
        all_memories = plugin.search_memories("API")
        print(f"   所有分支找到 {len(all_memories)} 个记忆")
    except Exception as e:
        print(f"   跳过：{e}")

    return plugin


def test_hooks():
    """测试钩子系统"""
    print("\n" + "=" * 50)
    print("测试钩子系统")
    print("=" * 50)

    import subprocess
    import json

    install_dir = "/root/.claude/claude-code-memory-plugin"

    # 测试 PreToolUse 钩子
    print("\n1. PreToolUse 钩子测试:")
    hook_file = os.path.join(install_dir, "hooks", "auto_memory_hook.sh")
    if os.path.exists(hook_file):
        result = subprocess.run(
            ["bash", hook_file],
            input='{"tool_name": "Read", "file_path": "/home/users/humingqing/work/OpenViking/openviking/core/context.py"}',
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, 'CLAUDE_PLUGIN_ROOT': install_dir}
        )

        if result.returncode == 0:
            output = json.loads(result.stdout)
            print(f"   ✓ 钩子执行成功")
            print(f"   - 返回：{json.dumps(output, ensure_ascii=False)}")
        else:
            print(f"   ✗ 钩子执行失败：{result.stderr}")
    else:
        print(f"   ✗ 钩子文件不存在：{hook_file}")

    # 测试 PostToolUse 钩子
    print("\n2. PostToolUse 钩子测试:")
    hook_file = os.path.join(install_dir, "hooks", "auto_record_hook.sh")
    if os.path.exists(hook_file):
        result = subprocess.run(
            ["bash", hook_file],
            input='{"tool_name": "Write", "tool_result": "Successfully wrote file"}',
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, 'CLAUDE_PLUGIN_ROOT': install_dir}
        )

        if result.returncode == 0:
            output = json.loads(result.stdout)
            print(f"   ✓ 钩子执行成功")
            print(f"   - 返回：{json.dumps(output, ensure_ascii=False)}")
        else:
            print(f"   ✗ 钩子执行失败：{result.stderr}")
    else:
        print(f"   ✗ 钩子文件不存在：{hook_file}")

    # 测试 SessionStart 钩子
    print("\n3. SessionStart 钩子测试:")
    hook_file = os.path.join(install_dir, "hooks", "session_start.sh")
    if os.path.exists(hook_file):
        result = subprocess.run(
            ["bash", hook_file],
            input='{"session_id": "test-session"}',
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, 'CLAUDE_PLUGIN_ROOT': install_dir}
        )

        if result.returncode == 0:
            output = json.loads(result.stdout)
            print(f"   ✓ 钩子执行成功")
            print(f"   - 返回：{json.dumps(output, ensure_ascii=False)}")
        else:
            print(f"   ✗ 钩子执行失败：{result.stderr}")
    else:
        print(f"   ✗ 钩子文件不存在：{hook_file}")


def main():
    """主测试函数"""
    print("\n" + "#" * 60)
    print("# Code Auto Memory Feature 测试")
    print("# 代码自动记忆功能测试")
    print("#" * 60)

    # 测试代码分析器
    analyzer = test_code_analyzer()

    # 测试自动记忆插件
    plugin = test_auto_memory_plugin()

    # 测试分支感知功能
    branch_plugin = test_branch_aware_memory()

    # 测试钩子系统
    test_hooks()

    print("\n" + "=" * 50)
    print("所有测试完成！")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
