#!/usr/bin/env python3
"""
测试记忆插件的摘要读写功能。
"""

import sys
import json
import time

sys.path.insert(0, '/home/users/humingqing/work/OpenViking/examples/claude-code-memory-plugin')

from memory_plugin import RemoteMemoryPlugin, MemoryType

# 配置
OPENVIKING_URL = "http://localhost:1933"
API_KEY = "6z_TTilwV_CM16qV3ExG1PAVFCptrLp-ver8Xb1lGD8"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_success(msg):
    print(f"  ✓ {msg}")

def print_error(msg):
    print(f"  ✗ {msg}")

def print_info(msg):
    print(f"  ℹ {msg}")

def test_store_and_read_abstract():
    """测试存储并读取摘要"""
    print_header("测试：存储并读取摘要")

    plugin = RemoteMemoryPlugin(
        openviking_url=OPENVIKING_URL,
        api_key=API_KEY
    )

    # 存储设计文档
    title = f"Abstract Test {int(time.time())}"
    content = """# Test Design Document

## Overview
This is a test document for abstract generation verification.

## Components
- Frontend: React
- Backend: Python FastAPI
- Database: PostgreSQL

## Architecture
1. User request → API Gateway
2. API Gateway → Service Layer
3. Service Layer → Database
"""

    print_info(f"存储设计文档：{title}")
    entry = plugin.store_design_doc(
        title=title,
        content=content,
        tags=["test", "abstract", "verification"]
    )
    print_success(f"存储成功，URI: {entry.uri}")

    # 等待摘要生成（最多 90 秒）
    print_info("等待摘要生成（最多 90 秒）...")
    for i in range(90):
        time.sleep(1)
        result = plugin.client.get_memory_abstract(entry.uri)
        if result.get("status") == "ok" and result.get("result"):
            abstract = result.get("result")
            if abstract and len(abstract) > 10:
                print_success(f"摘要生成成功")
                print_info(f"摘要内容:\n{abstract}")
                return True
        if i % 5 == 0:
            print_info(f"  等待中... ({i+1}/90)")

    # 如果摘要仍然为空，检查资源结构
    print_info("检查资源结构...")
    result = plugin.client.get_memory_abstract(entry.uri)
    print_info(f"摘要 API 返回：{result}")

    # 尝试读取完整内容
    result = plugin.client._make_request("GET", "/api/v1/content/read", query_params={"uri": entry.uri})
    if result.get("status") == "ok":
        print_info(f"完整内容:\n{result.get('result', '')[:500]}...")

    return False

def test_overview():
    """测试读取概览 (L1)"""
    print_header("测试：读取概览 (L1)")

    plugin = RemoteMemoryPlugin(
        openviking_url=OPENVIKING_URL,
        api_key=API_KEY
    )

    # 选择一个已存在的资源
    uri = "viking://resources/memories/design_doc/api_test"

    print_info(f"读取概览：{uri}")
    result = plugin.client._make_request("GET", "/api/v1/content/overview", query_params={"uri": uri})

    if result.get("status") == "ok":
        overview = result.get("result")
        if overview and len(overview) > 10:
            print_success(f"概览读取成功")
            print_info(f"概览内容:\n{overview}")
        else:
            print_error(f"概览为空：{overview}")
    else:
        print_error(f"概览读取失败：{result}")

def test_read():
    """测试读取完整内容 (L2)"""
    print_header("测试：读取完整内容 (L2)")

    plugin = RemoteMemoryPlugin(
        openviking_url=OPENVIKING_URL,
        api_key=API_KEY
    )

    # 选择一个已存在的资源
    uri = "viking://resources/memories/design_doc/api_test"

    print_info(f"读取完整内容：{uri}")
    result = plugin.client._make_request("GET", "/api/v1/content/read", query_params={"uri": uri})

    if result.get("status") == "ok":
        content = result.get("result")
        if content:
            print_success(f"完整内容读取成功")
            print_info(f"内容:\n{content}")
        else:
            print_error(f"内容为空")
    else:
        print_error(f"完整内容读取失败：{result}")

def test_existing_resources():
    """测试现有资源的摘要"""
    print_header("测试：现有资源的摘要")

    plugin = RemoteMemoryPlugin(
        openviking_url=OPENVIKING_URL,
        api_key=API_KEY
    )

    # 测试已知的资源
    test_resources = [
        "viking://resources/memories/design_doc/design_docabstracttest1773666904",
        "viking://resources/memories/design_doc/design_docabstracttest1773667049",
        "viking://resources/memories/design_doc/api_test",
    ]

    for uri in test_resources:
        print_info(f"\n检查：{uri}")

        # 读取摘要
        abstract_result = plugin.client.get_memory_abstract(uri)
        if abstract_result.get("status") == "ok":
            abstract = abstract_result.get("result", "")
            if abstract and len(abstract) > 10:
                print_success(f"  摘要：{abstract[:100]}...")
            else:
                print_error(f"  摘要为空或太短")
        else:
            print_error(f"  摘要读取失败：{abstract_result}")

def main():
    print("\n" + "="*60)
    print("  OpenViking Memory Plugin 摘要功能测试")
    print("  测试时间：{}".format(time.strftime("%Y-%m-%d %H:%M:%S")))
    print("="*60)

    # 测试 1：存储并读取摘要
    test_store_and_read_abstract()

    # 测试 2：读取现有资源的摘要
    test_existing_resources()

    # 测试 3：读取概览
    test_overview()

    # 测试 4：读取完整内容
    test_read()

    print("\n" + "="*60)
    print("  所有测试完成！")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
