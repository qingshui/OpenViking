"""
Claude Code Memory Plugin
基于远程 OpenViking API 的轻量级内存记忆插件

无需本地安装，所有记忆直接存储到远程 OpenViking 服务。

支持功能：
- 远程存储设计文档、代码规范、API 接口
- 会话记忆管理
- 语义搜索
"""

import json
import time
import hashlib
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class MemoryType(Enum):
    """记忆类型"""
    DESIGN_DOC = "design_doc"           # 设计文档
    CODE_STYLE = "code_style"           # 代码规范
    API_INTERFACE = "api_interface"     # 函数 API 接口
    SESSION = "session"                 # 会话记忆
    TASK = "task"                       # 任务记忆
    PREFERENCE = "preference"           # 用户偏好


@dataclass
class MemoryEntry:
    """记忆条目"""
    title: str
    content: str
    memory_type: MemoryType
    tags: List[str]
    metadata: Dict[str, Any]
    uri: Optional[str] = None


class OpenVikingClient:
    """OpenViking API 客户端 - 轻量级远程调用"""

    def __init__(self, base_url: str = "http://localhost:1933", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key, "Content-Type": "application/json"} if api_key else {"Content-Type": "application/json"}

    def _make_request(self, method: str, path: str, data: Optional[Dict] = None,
                      query_params: Optional[Dict] = None) -> Dict[str, Any]:
        """发送 API 请求"""
        url = f"{self.base_url}{path}"
        if query_params:
            from urllib.parse import urlencode
            url += "?" + urlencode(query_params)

        if data:
            data = json.dumps(data).encode('utf-8')

        req = urllib.request.Request(url, data=data, headers=self.headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            return {"error": str(e), "code": e.code}

    def add_memory(self, uri: str, content: str, reason: str = "Memory storage") -> Dict[str, Any]:
        """向远程 OpenViking 存储记忆"""
        # 使用临时文件方式存储内容到 OpenViking
        import tempfile
        import os

        temp_path = os.path.join(tempfile.gettempdir(), f"mv_temp_{int(time.time())}.txt")

        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return self._make_request("POST", "/api/v1/resources", {
                "temp_path": temp_path,
                "to": uri,
                "reason": reason,
                "summarize": True
            })
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def search_memories(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """搜索远程记忆"""
        return self._make_request("POST", "/api/v1/search/find", {
            "query": query,
            "limit": limit
        })

    def get_memory_abstract(self, uri: str) -> Dict[str, Any]:
        """获取记忆摘要"""
        return self._make_request("GET", "/api/v1/content/abstract", query_params={"uri": uri})

    def delete_memory(self, uri: str) -> Dict[str, Any]:
        """删除记忆"""
        return self._make_request("DELETE", "/api/v1/fs", {"uri": uri, "recursive": True})


class RemoteMemoryPlugin:
    """远程记忆插件 - 所有数据存储在 OpenViking 服务"""

    def __init__(self, openviking_url: str = "http://localhost:1933",
                 api_key: Optional[str] = None):
        """
        初始化远程记忆插件

        Args:
            openviking_url: OpenViking API 地址
            api_key: API 密钥
        """
        self.client = OpenVikingClient(openviking_url, api_key)
        self.base_uri = "viking://resources/memories/"
        self.current_session = None

    def _generate_uri(self, memory_type: MemoryType, title: str) -> str:
        """生成记忆 URI"""
        safe_title = "".join(c for c in title if c.isalnum() or c in '_-').lower()
        return f"{self.base_uri}{memory_type.value}/{safe_title}"

    def store_design_doc(self, title: str, content: str, tags: Optional[List[str]] = None,
                         remote_key: Optional[str] = None) -> MemoryEntry:
        """
        存储设计文档到远程 OpenViking

        Args:
            title: 文档标题
            content: 文档内容
            tags: 标签列表
            remote_key: 自定义远程键（用于复用同一记忆）

        Returns:
            MemoryEntry 对象
        """
        key = remote_key or f"design_doc:{title}"
        uri = self._generate_uri(MemoryType.DESIGN_DOC, key)

        metadata = {"tags": tags or ["design", "architecture"], "type": "design_doc"}

        result = self.client.add_memory(uri, content, reason=f"Store design doc: {title}")
        if result.get("status") == "error":
            raise Exception(f"Failed to store design doc: {result.get('result', {}).get('errors', [])}")

        return MemoryEntry(
            title=title,
            content=content,
            memory_type=MemoryType.DESIGN_DOC,
            tags=metadata["tags"],
            metadata=metadata,
            uri=uri
        )

    def store_code_style(self, title: str, content: str, tags: Optional[List[str]] = None,
                         remote_key: Optional[str] = None) -> MemoryEntry:
        """
        存储代码规范到远程 OpenViking

        Args:
            title: 规范标题
            content: 规范内容
            tags: 标签列表
            remote_key: 自定义远程键

        Returns:
            MemoryEntry 对象
        """
        key = remote_key or f"code_style:{title}"
        uri = self._generate_uri(MemoryType.CODE_STYLE, key)

        metadata = {"tags": tags or ["code", "style", "convention"], "type": "code_style"}

        result = self.client.add_memory(uri, content, reason=f"Store code style: {title}")
        if result.get("status") == "error":
            raise Exception(f"Failed to store code style: {result.get('result', {}).get('errors', [])}")

        return MemoryEntry(
            title=title,
            content=content,
            memory_type=MemoryType.CODE_STYLE,
            tags=metadata["tags"],
            metadata=metadata,
            uri=uri
        )

    def store_api_interface(self, title: str, content: str,
                            params: Optional[List[Dict]] = None,
                            returns: Optional[Dict] = None,
                            tags: Optional[List[str]] = None,
                            remote_key: Optional[str] = None) -> MemoryEntry:
        """
        存储 API 接口到远程 OpenViking

        Args:
            title: 接口名称
            content: 接口签名
            params: 参数列表
            returns: 返回值信息
            tags: 标签列表
            remote_key: 自定义远程键

        Returns:
            MemoryEntry 对象
        """
        key = remote_key or f"api_interface:{title}"
        uri = self._generate_uri(MemoryType.API_INTERFACE, key)

        metadata = {
            "params": params or [],
            "returns": returns or {},
            "tags": tags or ["api", "function"],
            "type": "api_interface"
        }

        content_with_meta = f"## Signature\n{content}\n\n## Params\n{json.dumps(params, indent=2)}\n\n## Returns\n{json.dumps(returns, indent=2)}"

        result = self.client.add_memory(uri, content_with_meta, reason=f"Store API: {title}")
        if result.get("status") == "error":
            raise Exception(f"Failed to store API: {result.get('result', {}).get('errors', [])}")

        return MemoryEntry(
            title=title,
            content=content,
            memory_type=MemoryType.API_INTERFACE,
            tags=metadata["tags"],
            metadata=metadata,
            uri=uri
        )

    def initialize_session(self, session_id: str, context: str) -> None:
        """
        初始化会话（存储在远程）

        Args:
            session_id: 会话 ID
            context: 初始上下文
        """
        self.current_session = session_id
        uri = f"{self.base_uri}session/{session_id}"

        session_data = {
            "session_id": session_id,
            "context": context,
            "start_time": time.time(),
            "updates": []
        }

        result = self.client.add_memory(uri, json.dumps(session_data, indent=2),
                                        reason=f"Initialize session: {session_id}")
        if result.get("status") == "error":
            print(f"Warning: Failed to initialize session: {result.get('result', {}).get('errors', [])}")

    def update_session(self, new_context: str) -> None:
        """
        更新会话上下文（远程更新）

        Args:
            new_context: 新的上下文
        """
        if not self.current_session:
            return

        uri = f"{self.base_uri}session/{self.current_session}"

        # 先获取当前会话
        result = self.client.get_memory_abstract(uri)
        if result.get("status") == "ok" and "result" in result:
            try:
                # result["result"] 可能是字符串或字典
                result_data = result["result"]
                if isinstance(result_data, str):
                    content = result_data
                else:
                    content = result_data.get("content", "{}")

                data = json.loads(content)
                data["context"] = new_context
                data["updates"].append({
                    "time": time.time(),
                    "context": new_context
                })
                self.client.add_memory(uri, json.dumps(data, indent=2),
                                       reason=f"Update session: {self.current_session}")
            except (json.JSONDecodeError, AttributeError, TypeError):
                # 如果内容不是 JSON，创建新的
                new_data = {
                    "session_id": self.current_session,
                    "context": new_context,
                    "start_time": time.time(),
                    "updates": [{"time": time.time(), "context": new_context}]
                }
                self.client.add_memory(uri, json.dumps(new_data, indent=2),
                                       reason=f"Update session: {self.current_session}")

    def search_memories(self, query: str, memory_types: Optional[List[MemoryType]] = None,
                        limit: int = 5) -> List[MemoryEntry]:
        """
        搜索远程记忆

        Args:
            query: 搜索关键词
            memory_types: 过滤的记忆类型
            limit: 返回数量限制

        Returns:
            MemoryEntry 列表
        """
        result = self.client.search_memories(query, limit=limit)

        if result.get("status") != "ok" or "result" not in result:
            return []

        memories = []
        for resource in result.get("result", {}).get("resources", []):
            uri = resource.get("uri", "")
            if not uri.endswith(".abstract.md") and not uri.endswith(".overview.md"):
                # 从 URI 推断记忆类型
                parts = uri.split("/")
                if len(parts) >= 4:
                    mem_type_str = parts[3]
                    try:
                        mem_type = MemoryType(mem_type_str)
                    except ValueError:
                        mem_type = MemoryType.SESSION

                memories.append(MemoryEntry(
                    title=parts[-1].replace(".md", "").replace("_", " ").title(),
                    content=resource.get("abstract", ""),
                    memory_type=mem_type,
                    tags=[],
                    metadata={"score": resource.get("score", 0)},
                    uri=uri
                ))

        return memories[:limit]

    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        获取会话数据（从远程）

        Args:
            session_id: 会话 ID

        Returns:
            会话数据字典或 None
        """
        uri = f"{self.base_uri}session/{session_id}"
        result = self.client.get_memory_abstract(uri)

        if result.get("status") == "ok" and "result" in result:
            try:
                # result["result"] 可能是字符串或字典
                result_data = result["result"]
                if isinstance(result_data, str):
                    # 如果是字符串，直接使用
                    content = result_data
                else:
                    # 如果是字典，获取 content 字段
                    content = result_data.get("content", "{}")

                return json.loads(content)
            except (json.JSONDecodeError, AttributeError, TypeError):
                return None

        return None

    def get_all_memories(self, memory_type: Optional[MemoryType] = None) -> List[str]:
        """
        列出所有记忆 URI

        Args:
            memory_type: 过滤的记忆类型

        Returns:
            URI 列表
        """
        if memory_type:
            uri = f"{self.base_uri}{memory_type.value}/"
        else:
            uri = self.base_uri

        result = self.client._make_request("GET", "/api/v1/fs/ls", {"uri": uri})
        if result.get("status") == "ok" and "result" in result:
            return [item.get("uri") for item in result["result"].get("items", [])]

        return []


# 使用示例
if __name__ == "__main__":
    # 初始化插件（使用远程 OpenViking 服务）
    plugin = RemoteMemoryPlugin(
        openviking_url="http://localhost:1933",
        api_key="6z_TTilwV_CM16qV3ExG1PAVFCptrLp-ver8Xb1lGD8"
    )

    # 初始化会话
    plugin.initialize_session(
        session_id="session-001",
        context="正在开发一个 Python Web 应用"
    )

    # 存储设计文档
    plugin.store_design_doc(
        title="Project Architecture",
        content="# Project Architecture\n\n## Overview\nThis is a Python web application built with FastAPI.",
        tags=["architecture", "backend"]
    )

    # 存储代码规范
    plugin.store_code_style(
        title="Python Coding Standards",
        content="# Python Coding Standards\n\n## Naming Conventions\n- Variables: snake_case\n- Classes: PascalCase",
        tags=["python", "standards"]
    )

    # 存储 API 接口
    plugin.store_api_interface(
        title="create_user",
        content="create_user(name: str, email: str) -> User",
        params=[
            {"name": "name", "type": "str", "description": "User name"},
            {"name": "email", "type": "str", "description": "User email"}
        ],
        returns={"type": "User", "description": "Created user object"},
        tags=["api", "user"]
    )

    # 搜索相关记忆
    relevant_memories = plugin.search_memories("Python FastAPI database")
    print(f"Found {len(relevant_memories)} relevant memories")
    for m in relevant_memories:
        print(f"  - {m.title} [{m.memory_type.value}]")

    # 更新会话
    plugin.update_session("正在开发 Python Web 应用，使用 FastAPI 框架和 PostgreSQL 数据库")
