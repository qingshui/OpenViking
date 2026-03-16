#!/usr/bin/env python3
"""
验证 Claude Code 插件架构
检查插件是否符合 Claude Code 的插件标准
"""

import os
import sys
import json

# 颜色定义
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'

def print_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")

def print_success(msg):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {msg}")

def print_error(msg):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}")

def check_plugin_structure(plugin_dir):
    """检查插件目录结构"""
    print_info("检查插件目录结构...")

    required_dirs = [
        '.claude-plugin',
        'commands',
        'hooks',
    ]

    required_files = [
        '.claude-plugin/plugin.json',
        'hooks/hooks.json',
        'commands/memory.md',
        'scripts/memory_command.py',
    ]

    all_passed = True

    for dir_name in required_dirs:
        dir_path = os.path.join(plugin_dir, dir_name)
        if os.path.isdir(dir_path):
            print_success(f"  目录：{dir_name}/")
        else:
            print_error(f"  目录缺失：{dir_name}/")
            all_passed = False

    for file_name in required_files:
        file_path = os.path.join(plugin_dir, file_name)
        if os.path.isfile(file_path):
            print_success(f"  文件：{file_name}")
        else:
            print_error(f"  文件缺失：{file_name}")
            all_passed = False

    return all_passed


def check_plugin_json(plugin_dir):
    """检查 plugin.json 文件"""
    print_info("检查 .claude-plugin/plugin.json...")

    plugin_json_path = os.path.join(plugin_dir, '.claude-plugin', 'plugin.json')

    if not os.path.exists(plugin_json_path):
        print_error("plugin.json 不存在")
        return False

    try:
        with open(plugin_json_path, 'r') as f:
            plugin_data = json.load(f)

        required_fields = ['name', 'version', 'description']
        all_present = True

        for field in required_fields:
            if field in plugin_data:
                print_success(f"  {field}: {plugin_data[field]}")
            else:
                print_error(f"  缺失字段：{field}")
                all_present = False

        return all_present
    except json.JSONDecodeError as e:
        print_error(f"JSON 格式错误：{e}")
        return False


def check_hooks_json(plugin_dir):
    """检查 hooks.json 文件"""
    print_info("检查 hooks/hooks.json...")

    hooks_json_path = os.path.join(plugin_dir, 'hooks', 'hooks.json')

    if not os.path.exists(hooks_json_path):
        print_error("hooks.json 不存在")
        return False

    try:
        with open(hooks_json_path, 'r') as f:
            hooks_data = json.load(f)

        if 'hooks' in hooks_data:
            print_success("  hooks 配置存在")

            hook_types = list(hooks_data['hooks'].keys())
            for hook_type in hook_types:
                print_success(f"    - {hook_type}")
        else:
            print_error("  缺少 hooks 字段")
            return False

        return True
    except json.JSONDecodeError as e:
        print_error(f"JSON 格式错误：{e}")
        return False


def check_commands(plugin_dir):
    """检查 commands 目录"""
    print_info("检查 commands/目录...")

    commands_dir = os.path.join(plugin_dir, 'commands')

    if not os.path.isdir(commands_dir):
        print_error("commands/目录不存在")
        return False

    md_files = [f for f in os.listdir(commands_dir) if f.endswith('.md')]

    if md_files:
        print_success(f"  找到 {len(md_files)} 个命令文件:")
        for f in md_files:
            print_success(f"    - {f}")
        return True
    else:
        print_warning("  没有找到 .md 命令文件")
        return False


def check_python_syntax(plugin_dir):
    """检查 Python 文件语法"""
    print_info("检查 Python 文件语法...")

    python_files = [
        'memory_plugin.py',
        'hooks/auto_memory_hook.py',
        'scripts/memory_command.py',
        'verify_install.py',
        'test_memory_plugin.py',
        'test_auto_memory.py',
    ]

    all_passed = True

    for py_file in python_files:
        file_path = os.path.join(plugin_dir, py_file)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    compile(f.read(), py_file, 'exec')
                print_success(f"  {py_file}: 语法正确")
            except SyntaxError as e:
                print_error(f"  {py_file}: 语法错误 - {e}")
                all_passed = False
        else:
            print_warning(f"  {py_file}: 文件不存在")

    return all_passed


def main():
    print("")
    print("=" * 50)
    print("  Claude Code 插件架构验证")
    print("=" * 50)
    print("")

    # 获取插件目录
    plugin_dir = os.path.expanduser("~/.claude/claude-code-memory-plugin")

    if not os.path.exists(plugin_dir):
        print_error(f"插件目录不存在：{plugin_dir}")
        print_info("请先运行安装脚本：./install.sh")
        return 1

    results = []

    # 运行所有检查
    results.append(("目录结构", check_plugin_structure(plugin_dir)))
    results.append(("plugin.json", check_plugin_json(plugin_dir)))
    results.append(("hooks.json", check_hooks_json(plugin_dir)))
    results.append(("commands", check_commands(plugin_dir)))
    results.append(("Python 语法", check_python_syntax(plugin_dir)))

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
        print_success("插件架构验证通过！")
        print_info("可以在 Claude Code 中使用 /memory 命令")
    else:
        print_error("插件架构验证失败，请检查上述错误")

    print("=" * 50)
    print("")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
