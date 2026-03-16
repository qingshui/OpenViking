#!/usr/bin/env python3
"""
Auto Record Hook - 记录工具调用结果
在工具调用后记录结果到 OpenViking
"""

import os
import sys
import json
import time

# 获取插件根目录
PLUGIN_ROOT = os.environ.get('CLAUDE_PLUGIN_ROOT')
if not PLUGIN_ROOT:
    print(json.dumps({"systemMessage": "CLAUDE_PLUGIN_ROOT not set"}), file=sys.stdout)
    sys.exit(0)

# 添加插件路径
sys.path.insert(0, PLUGIN_ROOT)

try:
    from memory_plugin import RemoteMemoryPlugin, MemoryType, GitBranchInfo, TeamScope
except ImportError as e:
    print(json.dumps({"systemMessage": f"Import error: {e}"}), file=sys.stdout)
    sys.exit(0)


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


def should_record(input_data):
    """判断是否需要记录工具调用"""
    tool_name = input_data.get('tool_name', '')
    tool_result = input_data.get('tool_result', '')

    # 只在工具调用有结果时记录
    if not tool_name or not tool_result:
        return False

    # 记录重要的工具调用
    important_tools = ['Read', 'Write', 'Edit', 'Exec', 'Search', 'Message', 'WebFetch', 'Bash']
    return tool_name in important_tools


def main():
    """主函数"""
    try:
        # 读取输入
        input_data = json.load(sys.stdin)

        # 判断是否需要触发
        if not should_record(input_data):
            print(json.dumps({}), file=sys.stdout)
            sys.exit(0)

        # 获取配置
        config = get_openviking_config()
        if not config.get('openviking_url'):
            print(json.dumps({"systemMessage": "OpenViking URL not configured"}), file=sys.stdout)
            sys.exit(0)

        # 初始化插件
        plugin = RemoteMemoryPlugin(
            openviking_url=config['openviking_url'],
            api_key=config.get('api_key', '')
        )

        # 获取工具信息（根据 Claude Code 官方文档）
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})  # 官方字段名是 tool_input
        tool_result = input_data.get('tool_result', '')
        session_id = input_data.get('session_id', '')

        # 构建记录内容
        record_title = f"Tool Call: {tool_name}"
        record_content = f"""# Tool Call Record

## Tool Information
- **Tool Name**: {tool_name}
- **Input**: {json.dumps(tool_input, indent=2, ensure_ascii=False)[:1000]}
- **Session**: {session_id}
- **Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Result
{tool_result[:2000] if len(tool_result) > 2000 else tool_result}

---
*Recorded by Claude Code Memory Plugin*
"""

        # 存储为任务记忆
        try:
            entry = plugin.store_api_interface(
                title=record_title,
                content=record_content,
                tags=['tool_call', tool_name.lower(), 'record'],
                auto_store=True
            )

            result = {
                "systemMessage": f"✅ 已记录工具调用：{tool_name}\n📁 {entry.uri}"
            }
        except Exception as e:
            result = {
                "systemMessage": f"⚠️ 记录工具调用失败：{str(e)}"
            }

        print(json.dumps(result), file=sys.stdout)

    except Exception as e:
        error_output = {
            "systemMessage": f"记录工具调用失败：{str(e)}"
        }
        print(json.dumps(error_output), file=sys.stdout)
    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
