#!/usr/bin/env python3
"""
显示 VLM 摘要生成的完整结果。
"""

import sys
import json
import urllib.request
import urllib.error

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
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")

def print_result(title, content):
    """打印结果"""
    print(f"\n{title}")
    print(f"{'-'*80}")
    print(content)
    print(f"{'-'*80}")

def main():
    print("\n" + "="*80)
    print("  VLM Abstract Generation Results")
    print("="*80)

    # 测试资源
    resources = [
        "viking://resources/memories/design_doc/design_docabstracttest1773666904",
        "viking://resources/memories/design_doc/design_docabstracttest1773667049",
        "viking://resources/memories/design_doc/vlmtest1773668189",
        "viking://resources/memories/design_doc/api_test",
    ]

    for uri in resources:
        print_section(f"资源：{uri}")

        # 读取摘要 (L0)
        abstract_result = make_request("GET", "/api/v1/content/abstract", {"uri": uri})
        if abstract_result.get("status") == "ok":
            abstract = abstract_result.get("result", "")
            if abstract:
                print_result("L0 Abstract (VLM Generated Summary)", abstract)
            else:
                print_result("L0 Abstract", "(Empty)")
        else:
            print_result("L0 Abstract", f"Error: {abstract_result}")

        # 读取概览 (L1)
        overview_result = make_request("GET", "/api/v1/content/overview", {"uri": uri})
        if overview_result.get("status") == "ok":
            overview = overview_result.get("result", "")
            if overview:
                # 截取前 500 字符
                preview = overview[:500] + "..." if len(overview) > 500 else overview
                print_result("L1 Overview (Detailed Summary)", preview)
            else:
                print_result("L1 Overview", "(Empty)")
        else:
            print_result("L1 Overview", f"Error: {overview_result}")

    print_section("总结")
    print("""
VLM 摘要生成功能验证结果:

1. L0 Abstract (摘要):
   - 由 VLM 模型生成的简短摘要
   - 用于快速了解资源内容
   - 适合语义搜索和索引

2. L1 Overview (概览):
   - 由 VLM 模型生成的详细概览
   - 包含导航链接和详细描述
   - 适合快速浏览和了解结构

3. VLM 处理时间:
   - 新资源需要 30-90 秒生成摘要
   - 摘要和概览文件自动保存到 .abstract.md 和 .overview.md

4. 使用场景:
   - Tiered Context Loading (分层上下文加载)
   - 快速检索和语义搜索
   - 资源内容预览
    """)

if __name__ == "__main__":
    main()
