#!/usr/bin/env python3
"""
Auto Memory Hook - 自动记忆功能
在读取代码文件时自动分析并存储记忆到 OpenViking
"""

import os
import sys
import json
import subprocess

# 获取插件根目录
PLUGIN_ROOT = os.environ.get('CLAUDE_PLUGIN_ROOT')
if not PLUGIN_ROOT:
    print(json.dumps({"systemMessage": "CLAUDE_PLUGIN_ROOT not set"}), file=sys.stdout)
    sys.exit(0)

# 添加插件路径
sys.path.insert(0, PLUGIN_ROOT)

try:
    from memory_plugin import RemoteMemoryPlugin, GitBranchInfo, TeamScope, MemoryType
except ImportError as e:
    print(json.dumps({"systemMessage": f"Import error: {e}"}), file=sys.stdout)
    sys.exit(0)


def should_auto_memory(input_data):
    """判断是否需要自动存储记忆"""
    tool_name = input_data.get('tool_name', '')

    # 只在读取文件时触发
    if tool_name != 'Read':
        return False

    # 检查文件类型
    file_path = input_data.get('file_path', '')
    if not file_path:
        return False

    # 只分析代码文件
    code_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.c', '.cpp', '.h', '.php', '.rb', '.swift', '.kt', '.scala']
    if not any(file_path.endswith(ext) for ext in code_extensions):
        return False

    return True


def get_git_branch(repo_path=None):
    """获取当前 Git 分支名称"""
    if not repo_path:
        repo_path = os.getcwd()

    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_openviking_config():
    """获取 OpenViking 配置"""
    config_path = os.path.expanduser("~/.claude/code-memory-config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            pass

    return {
        'openviking_url': os.environ.get('OPENVIKING_URL', 'http://localhost:1933'),
        'api_key': os.environ.get('OPENVIKING_API_KEY', ''),
        'use_branch_aware': True
    }


def main():
    """主函数"""
    try:
        # 读取输入
        input_data = json.load(sys.stdin)

        # 判断是否需要触发
        if not should_auto_memory(input_data):
            print(json.dumps({}), file=sys.stdout)
            sys.exit(0)

        # 获取配置
        config = get_openviking_config()
        if not config.get('openviking_url'):
            print(json.dumps({"systemMessage": "OpenViking URL not configured"}), file=sys.stdout)
            sys.exit(0)

        # 获取文件路径
        file_path = input_data.get('file_path', '')

        # 检测 Git 分支
        branch = get_git_branch(os.path.dirname(file_path))
        use_branch_aware = config.get('use_branch_aware', True)

        # 初始化插件
        if use_branch_aware and branch:
            branch_info = GitBranchInfo(branch, repo_path=os.path.dirname(file_path))
            team_scope = TeamScope(
                team_id="individual",
                branch_info=branch_info
            )
            plugin = RemoteMemoryPlugin(
                openviking_url=config['openviking_url'],
                api_key=config.get('api_key', ''),
                team_scope=team_scope,
                user_id="claude-user"
            )
        else:
            plugin = RemoteMemoryPlugin(
                openviking_url=config['openviking_url'],
                api_key=config.get('api_key', '')
            )

        # 自动分析并存储
        try:
            entry = plugin.analyze_and_store_file(file_path, auto_store=True)

            # 构建成功消息
            msg_parts = [f"✅ 已自动存储代码记忆：{entry.title}"]
            msg_parts.append(f"📁 {entry.uri}")
            msg_parts.append(f"📊 函数：{len(entry.metadata.get('functions', []))}, 类：{len(entry.metadata.get('classes', []))}")

            if use_branch_aware and branch:
                msg_parts.append(f"🌿 分支：{branch}")

            result = {
                "systemMessage": "\n".join(msg_parts)
            }
        except Exception as e:
            result = {
                "systemMessage": f"⚠️ 自动存储失败：{str(e)}\n💡 可以使用 /memory analyze 手动存储"
            }

        print(json.dumps(result), file=sys.stdout)

    except Exception as e:
        error_output = {
            "systemMessage": f"Memory hook error: {str(e)}"
        }
        print(json.dumps(error_output), file=sys.stdout)
    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
