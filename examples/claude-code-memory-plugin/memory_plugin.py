"""
Claude Code Memory Plugin
基于 OpenViking API 实现自动内存记忆功能

支持功能：
- 自动更新内存记忆
- 设计文档存储
- 代码规范存储
- 函数 API 接口存储
- 会话记忆管理
"""

import json
import time
import hashlib
import urllib.request
import urllib.error
import tempfile
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
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
    id: str
    title: str
    content: str
    memory_type: MemoryType
    tags: List[str]
    created_at: float
    updated_at: float
    metadata: Dict[str, Any]
    uri: Optional[str] = None


class OpenVikingClient:
    """OpenViking API 客户端"""

    def __init__(self, base_url: str = "http://localhost:1933", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key} if api_key else {}

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

    def add_resource(self, uri: str, content: str, wait: bool = False) -> Dict[str, Any]:
        """添加资源"""
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"openviking_temp_{int(time.time())}.txt")

        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(content)

        try:
            return self._make_request("POST", "/api/v1/resources", {
                "temp_path": temp_path,
                "target": uri,
                "reason": "Memory storage",
                "wait": wait
            })
        except Exception as e:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e

    def search_find(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """搜索查找"""
        return self._make_request("POST", "/api/v1/search/find", {
            "query": query,
            "limit": limit
        })

    def fs_ls(self, uri: str) -> Dict[str, Any]:
        """列出文件"""
        return self._make_request("GET", "/api/v1/fs/ls", {"uri": uri})

    def content_read(self, uri: str) -> Dict[str, Any]:
        """读取内容"""
        return self._make_request("GET", "/api/v1/content/read", {"uri": uri})

    def content_abstract(self, uri: str) -> Dict[str, Any]:
        """获取摘要"""
        return self._make_request("GET", "/api/v1/content/abstract", {"uri": uri})

    def content_overview(self, uri: str) -> Dict[str, Any]:
        """获取概览"""
        return self._make_request("GET", "/api/v1/content/overview", {"uri": uri})

    def delete_resource(self, uri: str) -> Dict[str, Any]:
        """删除资源"""
        return self._make_request("DELETE", "/api/v1/fs", {"uri": uri, "recursive": True})


class MemoryManager:
    """记忆管理器"""

    def __init__(self, client: OpenVikingClient):
        self.client = client
        self.base_uri = "viking://resources/memories/"

    def _generate_id(self, title: str) -> str:
        """生成唯一 ID"""
        return hashlib.md5(f"{title}{time.time()}".encode()).hexdigest()[:12]

    def _generate_uri(self, memory_type: MemoryType, title: str) -> str:
        """生成 URI"""
        safe_title = "".join(c for c in title if c.isalnum() or c in '_-').lower()
        return f"{self.base_uri}{memory_type.value}/{safe_title}"

    def create_memory(self, title: str, content: str, memory_type: MemoryType,
                      tags: Optional[List[str]] = None, metadata: Optional[Dict] = None) -> MemoryEntry:
        """创建记忆"""
        memory_id = self._generate_id(title)
        uri = self._generate_uri(memory_type, title)

        entry = MemoryEntry(
            id=memory_id,
            title=title,
            content=content,
            memory_type=memory_type,
            tags=tags or [],
            created_at=time.time(),
            updated_at=time.time(),
            metadata=metadata or {},
            uri=uri
        )

        # 如果 URI 已存在，先删除
        try:
            self.client.delete_resource(uri)
        except:
            pass

        # 存储到 OpenViking
        result = self.client.add_resource(uri, content, wait=False)
        if result.get("status") == "error":
            errors = result.get("result", {}).get("errors", [result.get("error", "Unknown error")])
            raise Exception(f"Failed to store memory: {errors}")

        return entry

    def search_memories(self, query: str, memory_type: Optional[MemoryType] = None,
                        limit: int = 10) -> List[MemoryEntry]:
        """搜索记忆"""
        result = self.client.search_find(query, limit=limit)

        if "error" in result or "result" not in result:
            return []

        memories = []
        for resource in result.get("result", {}).get("resources", []):
            uri = resource.get("uri", "")
            if not uri.endswith(".abstract.md") and not uri.endswith(".overview.md"):
                memories.append(self._parse_search_result(resource))

        return memories

    def _parse_search_result(self, resource: Dict) -> MemoryEntry:
        """解析搜索结果"""
        uri = resource.get("uri", "")
        parts = uri.split("/")
        if len(parts) >= 4:
            title = parts[-1].replace(".md", "").replace("_", " ").title()
        else:
            title = "Unknown"

        return MemoryEntry(
            id="",
            title=title,
            content=resource.get("abstract", ""),
            memory_type=MemoryType.SESSION,
            tags=[],
            created_at=0,
            updated_at=0,
            metadata={"score": resource.get("score", 0)},
            uri=uri
        )

    def get_memory(self, uri: str) -> Optional[MemoryEntry]:
        """获取记忆"""
        result = self.client.content_abstract(uri)
        if "error" in result or "result" not in result:
            return None

        data = result.get("result", {})
        return MemoryEntry(
            id="",
            title=uri.split("/")[-1].replace(".md", "").title(),
            content=data.get("content", ""),
            memory_type=MemoryType.SESSION,
            tags=[],
            created_at=0,
            updated_at=0,
            metadata={},
            uri=uri
        )

    def update_memory(self, uri: str, content: str) -> Optional[MemoryEntry]:
        """更新记忆"""
        # 删除旧资源
        self.client.delete_resource(uri)

        # 添加新资源
        result = self.client.add_resource(uri, content, wait=False)
        if result.get("status") == "error":
            return None

        return self.get_memory(uri)

    def delete_memory(self, uri: str) -> bool:
        """删除记忆"""
        result = self.client.delete_resource(uri)
        return result.get("status") == "ok"


class ClaudeCodeMemoryPlugin:
    """Claude Code 记忆插件"""

    def __init__(self, openviking_url: str = "http://localhost:1933",
                 api_key: Optional[str] = None):
        self.client = OpenVikingClient(openviking_url, api_key)
        self.manager = MemoryManager(self.client)
        self.current_session = None

    def initialize_session(self, session_id: str, context: str) -> None:
        """初始化会话"""
        self.current_session = session_id
        uri = f"{self.manager.base_uri}session/{session_id}"

        session_data = {
            "session_id": session_id,
            "context": context,
            "start_time": time.time(),
            "updates": []
        }

        self.manager.create_memory(
            title=f"Session {session_id}",
            content=json.dumps(session_data),
            memory_type=MemoryType.SESSION,
            metadata={"session_id": session_id}
        )

    def update_session(self, new_context: str) -> None:
        """更新会话"""
        if not self.current_session:
            return

        uri = f"{self.manager.base_uri}session/{self.current_session}"
        memory = self.manager.get_memory(uri)

        if memory:
            data = json.loads(memory.content)
            data["context"] = new_context
            data["updates"].append({
                "time": time.time(),
                "context": new_context
            })
            self.manager.update_memory(uri, json.dumps(data))

    def store_design_doc(self, title: str, content: str, tags: Optional[List[str]] = None) -> MemoryEntry:
        """存储设计文档"""
        return self.manager.create_memory(
            title=title,
            content=content,
            memory_type=MemoryType.DESIGN_DOC,
            tags=tags or ["design", "architecture"]
        )

    def store_code_style(self, title: str, content: str, tags: Optional[List[str]] = None) -> MemoryEntry:
        """存储代码规范"""
        return self.manager.create_memory(
            title=title,
            content=content,
            memory_type=MemoryType.CODE_STYLE,
            tags=tags or ["code", "style", "convention"]
        )

    def store_api_interface(self, title: str, content: str,
                            params: Optional[List[Dict]] = None,
                            returns: Optional[Dict] = None,
                            tags: Optional[List[str]] = None) -> MemoryEntry:
        """存储函数 API 接口"""
        metadata = {
            "params": params or [],
            "returns": returns or {},
            "signature": content.split(":")[0] if ":" in content else content
        }

        return self.manager.create_memory(
            title=title,
            content=content,
            memory_type=MemoryType.API_INTERFACE,
            tags=tags or ["api", "function"],
            metadata=metadata
        )

    def get_relevant_memories(self, context: str, memory_types: Optional[List[MemoryType]] = None,
                              limit: int = 5) -> List[MemoryEntry]:
        """获取相关记忆"""
        memories = []

        if memory_types:
            for mem_type in memory_types:
                results = self.manager.search_memories(context, mem_type, limit=limit)
                memories.extend(results)
        else:
            memories = self.manager.search_memories(context, limit=limit)

        return memories[:limit]

    def get_memory_summary(self, uri: str) -> Optional[Dict]:
        """获取记忆摘要"""
        abstract_result = self.client.content_abstract(uri)
        overview_result = self.client.content_overview(uri)

        summary = {}
        if "result" in abstract_result:
            summary["abstract"] = abstract_result.get("result", {})
        if "result" in overview_result:
            summary["overview"] = overview_result.get("result", {})

        return summary


# 使用示例
if __name__ == "__main__":
    # 初始化插件
    plugin = ClaudeCodeMemoryPlugin(
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
        content="""
        # Project Architecture

        ## Overview
        This is a Python web application built with FastAPI.

        ## Components
        - API Server: FastAPI
        - Database: PostgreSQL
        - Cache: Redis
        """,
        tags=["architecture", "backend"]
    )

    # 存储代码规范
    plugin.store_code_style(
        title="Python Coding Standards",
        content="""
        # Python Coding Standards

        ## Naming Conventions
        - Variables: snake_case
        - Classes: PascalCase
        - Constants: UPPER_SNAKE_CASE

        ## Code Structure
        - Maximum line length: 88 characters
        - Use type hints
        - Follow PEP 8
        """,
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
    relevant_memories = plugin.get_relevant_memories("Python FastAPI database")
    print(f"Found {len(relevant_memories)} relevant memories")

    # 更新会话
    plugin.update_session("正在开发 Python Web 应用，使用 FastAPI 框架和 PostgreSQL 数据库")
