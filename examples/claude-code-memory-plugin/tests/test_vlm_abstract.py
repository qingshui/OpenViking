#!/usr/bin/env python3
"""
测试 VLM 摘要生成结果。
专门验证 VLM 处理后的摘要和概览内容。
"""

import sys
import json
import time
import urllib.request
import urllib.error

# 配置
OPENVIKING_URL = "http://localhost:1933"
API_KEY = "6z_TTilwV_CM16qV3ExG1PAVFCptrLp-ver8Xb1lGD8"

HEADERS = {"X-API-Key": API_KEY}

def make_request(method, path, query_params=None):
    """发送 API 请求"""
    url = f"{OPENVIKING_URL}{path}"
    if query_params:
        from urllib.parse import urlencode
        url += "?" + urlencode(query_params)

    req = urllib.request.Request(url, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"error": str(e), "code": e.code}

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def test_vlm_abstract_generation():
    """测试 VLM 摘要生成"""
    print_section("VLM 摘要生成测试")

    # 存储一个设计文档
    title = f"VLM Test {int(time.time())}"
    content = """# VLM Abstract Test

## Overview
This document is designed to test the VLM abstract generation functionality.

## Components
- Frontend: React
- Backend: Python FastAPI
- Database: PostgreSQL

## Architecture
1. User request → API Gateway
2. API Gateway → Service Layer
3. Service Layer → Database

## Key Features
- Scalable microservices architecture
- RESTful API design
- Database connection pooling
"""

    uri = f"viking://resources/memories/design_doc/{title.replace(' ', '').lower()}"

    print(f"\n1. 存储设计文档")
    print(f"   Title: {title}")
    print(f"   URI: {uri}")

    # 上传临时文件
    import tempfile
    import os

    temp_path = os.path.join(tempfile.gettempdir(), f"vlm_test_{int(time.time())}.txt")
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # 上传到服务器
    upload_url = f"{OPENVIKING_URL}/api/v1/resources/temp_upload"
    with open(temp_path, 'rb') as f:
        file_data = f.read()

    boundary = f"----WebKitFormBoundary{int(time.time())}"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="test.txt"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode('utf-8') + file_data + f"\r\n--{boundary}--\r\n".encode('utf-8')

    req = urllib.request.Request(
        upload_url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
            **HEADERS
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        upload_result = json.loads(response.read().decode('utf-8'))
        temp_path_on_server = upload_result['result']['temp_path']

    print(f"   ✓ 文件上传成功：{temp_path_on_server}")

    # 创建资源
    create_url = f"{OPENVIKING_URL}/api/v1/resources"
    data = json.dumps({
        "temp_path": temp_path_on_server,
        "to": uri,
        "reason": "VLM abstract test",
        "summarize": True
    }).encode('utf-8')

    req = urllib.request.Request(
        create_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            **HEADERS
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        create_result = json.loads(response.read().decode('utf-8'))
        print(f"   ✓ 资源创建成功：{create_result['result'].get('root_uri')}")

    os.unlink(temp_path)

    # 等待 VLM 处理
    print(f"\n2. 等待 VLM 处理摘要生成...")
    print(f"   (VLM 处理需要 30-90 秒)")

    for i in range(60):
        time.sleep(1)

        # 检查摘要
        abstract_result = make_request("GET", "/api/v1/content/abstract", {"uri": uri})

        if abstract_result.get("status") == "ok":
            abstract = abstract_result.get("result", "")
            if abstract and len(abstract) > 50:
                print(f"   ✓ 摘要生成成功 (耗时 {i+1} 秒)")
                print(f"\n3. VLM 生成的摘要:")
                print(f"{'-'*70}")
                print(abstract)
                print(f"{'-'*70}")
                return abstract

        if i % 10 == 0:
            print(f"   等待中... ({i+1}/60 秒)")

    print(f"   ✗ 摘要生成超时")
    return None

def test_existing_resources():
    """测试现有资源的 VLM 摘要"""
    print_section("现有资源 VLM 摘要测试")

    test_resources = [
        "viking://resources/memories/design_doc/design_docabstracttest1773666904",
        "viking://resources/memories/design_doc/design_docabstracttest1773667049",
        "viking://resources/memories/design_doc/api_test",
    ]

    for uri in test_resources:
        print(f"\n资源：{uri}")

        # 读取摘要
        abstract_result = make_request("GET", "/api/v1/content/abstract", {"uri": uri})
        if abstract_result.get("status") == "ok":
            abstract = abstract_result.get("result", "")
            if abstract:
                print(f"   ✓ 摘要 (L0):")
                print(f"   {'-'*70}")
                print(f"   {abstract[:200]}...")
                print(f"   {'-'*70}")
            else:
                print(f"   ✗ 摘要为空")
        else:
            print(f"   ✗ 摘要读取失败：{abstract_result}")

        # 读取概览
        overview_result = make_request("GET", "/api/v1/content/overview", {"uri": uri})
        if overview_result.get("status") == "ok":
            overview = overview_result.get("result", "")
            if overview:
                print(f"   ✓ 概览 (L1):")
                print(f"   {'-'*70}")
                print(f"   {overview[:200]}...")
                print(f"   {'-'*70}")
            else:
                print(f"   ✗ 概览为空")
        else:
            print(f"   ✗ 概览读取失败：{overview_result}")

def main():
    print("\n" + "="*70)
    print("  VLM Abstract Generation Test")
    print("  Test Time: {}".format(time.strftime("%Y-%m-%d %H:%M:%S")))
    print("="*70)

    # 测试 VLM 摘要生成
    new_abstract = test_vlm_abstract_generation()

    # 测试现有资源
    test_existing_resources()

    print_section("测试完成")
    print("\nVLM 摘要功能验证完成！")
    print("说明:")
    print("  - L0 (Abstract): VLM 生成的简短摘要，用于快速了解内容")
    print("  - L1 (Overview): VLM 生成的详细概览，包含导航和详细描述")
    print("  - VLM 处理需要 30-90 秒，请耐心等待")

if __name__ == "__main__":
    main()
