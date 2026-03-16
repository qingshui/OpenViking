#!/usr/bin/env python3
"""
Memory Command Script
处理 /memory 命令的执行
"""

import os
import sys
import json
import argparse

# 获取插件根目录
PLUGIN_ROOT = os.environ.get('CLAUDE_PLUGIN_ROOT')
if not PLUGIN_ROOT:
    PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, PLUGIN_ROOT)

try:
    from memory_plugin import (
        RemoteMemoryPlugin,
        GitBranchInfo,
        TeamScope,
        MemoryType,
        CodeAnalyzer
    )
except ImportError as e:
    print(json.dumps({"error": f"Import error: {e}"}))
    sys.exit(1)


def get_plugin():
    """获取插件实例 - 从配置文件读取"""
    config_path = os.path.expanduser("~/.claude/code-memory-config.json")
    openviking_url = os.environ.get('OPENVIKING_URL', 'http://localhost:1933')
    api_key = os.environ.get('OPENVIKING_API_KEY', '')

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            openviking_url = config.get('openviking_url', openviking_url)
            api_key = config.get('api_key', api_key)
        except Exception as e:
            print(json.dumps({"error": f"Config read error: {e}"}))

    return RemoteMemoryPlugin(
        openviking_url=openviking_url,
        api_key=api_key
    )


def main():
    """主函数 - 提供自动记忆辅助功能"""
    parser = argparse.ArgumentParser(description='Memory Plugin Commands')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a code file')
    analyze_parser.add_argument('file_path', help='Path to the file to analyze')

    # store-email 命令
    email_parser = subparsers.add_parser('store-email', help='Store user email')
    email_parser.add_argument('email', help='Email address')
    email_parser.add_argument('--description', help='Description')

    # store-phone 命令
    phone_parser = subparsers.add_parser('store-phone', help='Store user phone')
    phone_parser.add_argument('phone', help='Phone number')
    phone_parser.add_argument('--description', help='Description')

    # store-address 命令
    address_parser = subparsers.add_parser('store-address', help='Store user address')
    address_parser.add_argument('address', help='Address')
    address_parser.add_argument('--description', help='Description')

    # get-user-info 命令
    info_parser = subparsers.add_parser('get-user-info', help='Get user info')
    info_parser.add_argument('info_type', help='Info type (email, phone, address)')

    args = parser.parse_args()

    if args.command == 'analyze':
        plugin = get_plugin()
        try:
            entry = plugin.analyze_and_store_file(args.file_path, auto_store=True)
            print(json.dumps({
                "success": True,
                "message": f"✅ 已存储：{entry.title}",
                "uri": entry.uri,
                "functions": len(entry.metadata.get('functions', [])),
                "classes": len(entry.metadata.get('classes', []))
            }))
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}))

    elif args.command == 'store-email':
        plugin = get_plugin()
        try:
            entry = plugin.store_email(
                email=args.email,
                description=getattr(args, 'description', None)
            )
            print(json.dumps({
                "success": True,
                "message": f"✅ 邮箱已存储：{entry.title}",
                "uri": entry.uri,
                "email": entry.metadata.get('value')
            }))
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}))

    elif args.command == 'store-phone':
        plugin = get_plugin()
        try:
            entry = plugin.store_phone(
                phone=args.phone,
                description=getattr(args, 'description', None)
            )
            print(json.dumps({
                "success": True,
                "message": f"✅ 电话已存储：{entry.title}",
                "uri": entry.uri,
                "phone": entry.metadata.get('value')
            }))
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}))

    elif args.command == 'store-address':
        plugin = get_plugin()
        try:
            entry = plugin.store_address(
                address=args.address,
                description=getattr(args, 'description', None)
            )
            print(json.dumps({
                "success": True,
                "message": f"✅ 地址已存储：{entry.title}",
                "uri": entry.uri,
                "address": entry.metadata.get('value')
            }))
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}))

    elif args.command == 'get-user-info':
        plugin = get_plugin()
        try:
            info_type = args.info_type.lower()
            entry = plugin.get_user_info(info_type)
            if entry:
                print(json.dumps({
                    "success": True,
                    "info_type": info_type,
                    "uri": entry.uri,
                    "content": entry.content,
                    "metadata": entry.metadata
                }))
            else:
                print(json.dumps({
                    "success": False,
                    "error": f"未找到 {info_type} 信息"
                }))
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
