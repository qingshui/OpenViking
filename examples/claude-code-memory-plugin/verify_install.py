#!/usr/bin/env python3
"""
验证安装脚本
检查插件是否正确安装和配置
"""

import sys
import os
import json as json_module

# 颜色定义
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color

def print_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")

def print_success(msg):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {msg}")

def print_error(msg):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}")

def check_python_version():
    """检查 Python 版本"""
    print_info("检查 Python 版本...")

    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")

    if version >= (3, 10):
        print_success("Python 版本满足要求 (>= 3.10)")
        return True
    else:
        print_error("Python 版本需要 >= 3.10")
        return False

def check_plugin_import():
    """检查插件导入"""
    print_info("检查插件导入...")

    # 尝试从默认位置导入（当前工作目录）
    install_dir = os.path.join(os.getcwd(), "claude-code-memory-plugin")

    if os.path.exists(install_dir):
        sys.path.insert(0, install_dir)
        print(f"  插件目录：{install_dir}")
    else:
        # 尝试从当前目录导入
        current_dir = os.path.dirname(__file__)
        sys.path.insert(0, current_dir)
        print(f"  插件目录：{current_dir}")

    try:
        from memory_plugin import (
            RemoteMemoryPlugin,
            CodeAnalyzer,
            GitBranchInfo,
            TeamScope,
            MemoryType,
            MemoryEntry
        )
        print_success("所有模块导入成功")
        print_success("  - RemoteMemoryPlugin")
        print_success("  - CodeAnalyzer")
        print_success("  - GitBranchInfo")
        print_success("  - TeamScope")
        print_success("  - MemoryType")
        print_success("  - MemoryEntry")
        return True
    except ImportError as e:
        print_error(f"模块导入失败：{e}")
        return False

def check_config_file():
    """检查配置文件"""
    print_info("检查配置文件...")

    config_path = os.path.expanduser("~/.claude/code-memory-config.json")

    if os.path.exists(config_path):
        print(f"  配置文件：{config_path}")

        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)

            print_success("配置文件格式正确")

            if 'openviking_url' in config_data:
                print_success(f"  OpenViking URL: {config_data['openviking_url']}")
            else:
                print_warning("  缺少 openviking_url")

            if 'api_key' in config_data:
                print_success("  API Key: 已配置")
            else:
                print_warning("  API Key: 未配置（可选）")

            return True
        except json.JSONDecodeError as e:
            print_error(f"配置文件格式错误：{e}")
            return False
    else:
        print_warning("配置文件不存在")
        print_info("可以使用以下环境变量:")
        print("  export OPENVIKING_URL='http://localhost:1933'")
        print("  export OPENVIKING_API_KEY='your-api-key'")
        return True  # 配置文件是可选的

def check_git_branch_info():
    """测试 GitBranchInfo"""
    print_info("测试 GitBranchInfo...")

    try:
        from memory_plugin import GitBranchInfo

        test_branches = [
            "main",
            "develop",
            "feature/user-auth",
            "release/v1.0.0",
            "hotfix/security-patch"
        ]

        for branch_name in test_branches:
            git_info = GitBranchInfo(branch_name)
            print(f"  {branch_name} -> {git_info.get_branch_prefix()}")

        print_success("GitBranchInfo 测试通过")
        return True
    except Exception as e:
        print_error(f"GitBranchInfo 测试失败：{e}")
        return False

def check_code_analyzer():
    """测试 CodeAnalyzer"""
    print_info("测试 CodeAnalyzer...")

    try:
        from memory_plugin import CodeAnalyzer

        analyzer = CodeAnalyzer()

        # 测试语言检测
        test_files = ["test.py", "app.js", "component.tsx"]
        for f in test_files:
            lang = analyzer.detect_language(f)
            print(f"  {f} -> {lang}")

        print_success("CodeAnalyzer 测试通过")
        return True
    except Exception as e:
        print_error(f"CodeAnalyzer 测试失败：{e}")
        return False

def check_team_scope():
    """测试 TeamScope"""
    print_info("测试 TeamScope...")

    try:
        from memory_plugin import GitBranchInfo, TeamScope

        # 测试分支感知
        team_scope = TeamScope(
            team_id="engineering",
            project_id="viking",
            branch_info=GitBranchInfo("feature/api-v2")
        )

        print(f"  命名空间：{team_scope.get_namespace()}")
        print(f"  URI 前缀：{team_scope.get_uri_prefix()}")

        print_success("TeamScope 测试通过")
        return True
    except Exception as e:
        print_error(f"TeamScope 测试失败：{e}")
        return False

def check_openviking_connection():
    """检查 OpenViking 连接"""
    print_info("检查 OpenViking 连接...")

    # 从配置文件或环境变量获取 URL
    config_path = os.path.expanduser("~/.claude/code-memory-config.json")
    openviking_url = os.environ.get("OPENVIKING_URL", "http://localhost:1933")

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        openviking_url = config_data.get("openviking_url", openviking_url)

    print(f"  OpenViking URL: {openviking_url}")

    try:
        import urllib.request

        req = urllib.request.Request(f"{openviking_url}/health")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json_module.loads(response.read().decode('utf-8'))

        if data.get("status") == "ok":
            print_success("OpenViking 服务可用")
            return True
        else:
            print_warning("OpenViking 服务响应异常")
            return False
    except Exception as e:
        print_warning(f"无法连接 OpenViking 服务：{e}")
        print_info("这不影响插件安装，只是无法使用远程功能")
        return True  # 连接失败不影响安装验证

def main():
    print("")
    print("=" * 50)
    print("  Claude Code Memory Plugin 安装验证")
    print("=" * 50)
    print("")

    results = []

    # 运行所有检查
    results.append(("Python 版本", check_python_version()))
    results.append(("插件导入", check_plugin_import()))
    results.append(("配置文件", check_config_file()))
    results.append(("GitBranchInfo", check_git_branch_info()))
    results.append(("CodeAnalyzer", check_code_analyzer()))
    results.append(("TeamScope", check_team_scope()))
    results.append(("OpenViking 连接", check_openviking_connection()))

    # 汇总结果
    print("")
    print("=" * 50)
    print("  验证结果汇总")
    print("=" * 50)
    print("")

    all_passed = True
    for name, passed in results:
        if passed:
            print(f"{Colors.GREEN}[PASS]{Colors.NC} {name}")
        else:
            print(f"{Colors.RED}[FAIL]{Colors.NC} {name}")
            all_passed = False

    print("")
    if all_passed:
        print_success("所有验证通过！")
    else:
        print_error("部分验证失败，请检查上述错误信息")

    print("=" * 50)
    print("")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
