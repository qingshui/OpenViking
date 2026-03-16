#!/usr/bin/env python3
"""
OpenViking API 快速验证脚本
仅使用 Python 标准库 (urllib, json)，无需额外依赖
"""

import json
import sys
import urllib.request
import urllib.error
from typing import Any, Dict, Optional


class OpenVikingAPIVerifier:
    """OpenViking API 验证器"""

    def __init__(self, base_url: str = "http://localhost:1933", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
        }
        if api_key:
            self.headers["X-API-Key"] = api_key

    def make_request(self, method: str, path: str, data: Optional[Dict] = None,
                     query_params: Optional[Dict] = None) -> Dict[str, Any]:
        """发送 API 请求"""
        url = f"{self.base_url}{path}"

        # 添加查询参数
        if query_params:
            from urllib.parse import urlencode
            url += "?" + urlencode(query_params)

        # 准备请求数据
        request_data = None
        if data:
            request_data = json.dumps(data).encode("utf-8")

        # 创建请求
        req = urllib.request.Request(
            url,
            data=request_data,
            headers=self.headers,
            method=method
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                return {"success": True, "data": result, "status": response.status}
        except urllib.error.HTTPError as e:
            try:
                error_data = json.loads(e.read().decode("utf-8"))
            except:
                error_data = {"error": e.read().decode("utf-8")}
            return {"success": False, "error": error_data, "status": e.code}
        except urllib.error.URLError as e:
            return {"success": False, "error": {"error": str(e.reason)}}
        except Exception as e:
            return {"success": False, "error": {"error": str(e)}}

    def check_health(self) -> bool:
        """检查 API 健康状态"""
        print(f"\n{'='*60}")
        print(f"检查 API 健康状态：{self.base_url}")
        print(f"{'='*60}")

        result = self.make_request("GET", "/health")
        if result["success"]:
            print(f"[OK] 健康检查通过")
            print(f"    状态码：{result['status']}")
            return True
        else:
            print(f"[FAIL] 健康检查失败")
            print(f"    错误：{result['error']}")
            return False

    def check_system_status(self) -> bool:
        """检查系统状态"""
        print(f"\n{'='*60}")
        print(f"检查系统状态：/api/v1/system/status")
        print(f"{'='*60}")

        result = self.make_request("GET", "/api/v1/system/status")
        if result["success"]:
            print(f"[OK] 系统状态查询成功")
            data = result["data"]
            if "response" in data:
                response = data["response"]
                print(f"    版本：{response.get('version', 'N/A')}")
                print(f"    运行时间：{response.get('uptime_seconds', 'N/A')} 秒")
                print(f"    会话数：{response.get('session_count', 'N/A')}")
                print(f"    资源数：{response.get('resource_count', 'N/A')}")
            return True
        else:
            print(f"[FAIL] 系统状态查询失败")
            print(f"    错误：{result['error']}")
            return False

    def check_filesystem(self) -> bool:
        """检查文件系统"""
        print(f"\n{'='*60}")
        print(f"检查文件系统：/api/v1/fs/ls")
        print(f"{'='*60}")

        result = self.make_request("GET", "/api/v1/fs/ls", query_params={"uri": "/"})
        if result["success"]:
            print(f"[OK] 文件系统列表查询成功")
            data = result["data"]
            if "response" in data:
                response = data["response"]
                items = response.get("items", [])
                print(f"    根目录项目数：{len(items)}")
                for item in items[:5]:  # 只显示前 5 个
                    print(f"    - {item.get('name', 'N/A')} ({item.get('type', 'N/A')})")
                if len(items) > 5:
                    print(f"    ... 还有 {len(items) - 5} 个项目")
            return True
        else:
            print(f"[FAIL] 文件系统列表查询失败")
            print(f"    错误：{result['error']}")
            return False

    def check_sessions(self) -> bool:
        """检查会话"""
        print(f"\n{'='*60}")
        print(f"检查会话：/api/v1/sessions")
        print(f"{'='*60}")

        result = self.make_request("GET", "/api/v1/sessions")
        if result["success"]:
            print(f"[OK] 会话列表查询成功")
            data = result["data"]
            if "result" in data:
                result_data = data["result"]
                sessions = result_data.get("sessions", []) if isinstance(result_data, dict) else []
                print(f"    会话总数：{len(sessions)}")
                for session in sessions[:3]:  # 只显示前 3 个
                    if isinstance(session, dict):
                        print(f"    - {session.get('session_id', 'N/A')}: {session.get('title', 'N/A')[:50]}")
            return True
        else:
            print(f"[FAIL] 会话列表查询失败")
            print(f"    错误：{result['error']}")
            return False

    def check_resources(self) -> bool:
        """检查资源信息"""
        print(f"\n{'='*60}")
        print(f"检查资源信息：/api/v1/system/status")
        print(f"{'='*60}")

        result = self.make_request("GET", "/api/v1/system/status")
        if result["success"]:
            print(f"[OK] 资源信息获取成功")
            data = result["data"]
            if "response" in data:
                response = data["response"]
                print(f"    资源总数：{response.get('resource_count', 'N/A')}")
                print(f"    内存使用：{response.get('memory_usage', 'N/A')}")
            return True
        else:
            print(f"[FAIL] 资源信息获取失败")
            print(f"    错误：{result['error']}")
            return False

    def test_post_request(self) -> bool:
        """测试 POST 请求"""
        print(f"\n{'='*60}")
        print(f"测试 POST 请求：/api/v1/fs/mkdir")
        print(f"{'='*60}")

        # 测试创建一个临时目录
        import time
        test_dir = f"/test_{int(time.time())}"

        result = self.make_request("POST", "/api/v1/fs/mkdir", data={"uri": test_dir})
        if result["success"]:
            print(f"[OK] POST 请求测试成功")
            print(f"    创建目录：{test_dir}")
            # 清理测试目录
            cleanup = self.make_request("DELETE", "/api/v1/fs", data={"uri": test_dir, "recursive": True})
            if cleanup["success"]:
                print(f"    清理目录：{test_dir}")
            return True
        else:
            print(f"[FAIL] POST 请求测试失败")
            print(f"    错误：{result['error']}")
            return False

    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("\n" + "="*60)
        print("OpenViking API 验证")
        print(f"目标：{self.base_url}")
        print("="*60)

        results = []

        # 1. 健康检查
        results.append(("健康检查", self.check_health()))

        # 2. 系统状态
        results.append(("系统状态", self.check_system_status()))

        # 3. 文件系统
        results.append(("文件系统", self.check_filesystem()))

        # 4. 会话列表
        results.append(("会话列表", self.check_sessions()))

        # 5. 资源信息
        results.append(("资源信息", self.check_resources()))

        # 6. POST 请求测试
        results.append(("POST 请求", self.test_post_request()))

        # 汇总结果
        print(f"\n{'='*60}")
        print("测试汇总")
        print(f"{'='*60}")

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for name, result in results:
            status = "[PASS]" if result else "[FAIL]"
            print(f"  {status} {name}")

        print(f"\n总计：{passed}/{total} 通过")

        return passed == total


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenViking API 快速验证")
    parser.add_argument("--url", default="http://localhost:1933",
                        help="OpenViking API 地址 (默认：http://localhost:1933)")
    parser.add_argument("--api-key", default=None,
                        help="API 密钥 (可选)")

    args = parser.parse_args()

    verifier = OpenVikingAPIVerifier(base_url=args.url, api_key=args.api_key)
    success = verifier.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
