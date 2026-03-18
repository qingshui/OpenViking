# OpenViking 架构设计文档

## 1. 项目概述

OpenViking 是一个开源上下文数据库，专为 AI Agent 设计。它使用文件系统范式的统一内存、资源和技能的组织，通过分层上下文加载和目录递归检索实现高效的知识管理。

### 1.1 核心特性

- **Viking URI 协议**：所有上下文使用 `viking://` 协议统一标识
- **分层上下文加载**：L0 (摘要) → L1 (概述) → L2 (详情)
- **目录递归检索**：向量搜索与目录遍历相结合
- **多语言支持**：代码解析支持 Python/C++/JS/TS/Java/Rust/Go/C#
- **多租户架构**：支持多个租户和 API 密钥管理
- **会话管理**：自动内存提取和压缩

---

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        OpenViking System                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Web Admin   │  │   OV CLI     │  │  VikingBot   │          │
│  │  (5173)      │  │  (Rust)      │  │  (Agent)     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│                    ┌──────▼──────┐                              │
│                    │   REST API  │                              │
│                    │  (Port 1933)│                              │
│                    │  Python     │                              │
│                    └──────┬──────┘                              │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                  │
│         │                 │                 │                   │
│    ┌────▼────┐      ┌────▼────┐      ┌────▼────┐               │
│    │ AGFS    │      │ C++     │      │  Web    │               │
│    │ (1833)  │      │ Engine  │      │ Admin   │               │
│    │ Go      │      │ PyBind11│      │ React   │               │
│    └─────────┘      └─────────┘      └─────────┘               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 组件职责

| 组件 | 端口 | 语言 | 职责 |
|------|------|------|------|
| **AGFS** | 1833 | Go | Agent 文件系统，提供虚拟文件访问 |
| **OpenViking Server** | 1933 | Python | REST API 服务端，核心业务逻辑 |
| **Web Admin** | 5173 | React + Vite | 前端管理界面 |
| **VikingBot** | - | Python | AI Agent 框架 |
| **OV CLI** | - | Rust | 命令行工具 |
| **C++ Extensions** | - | C++ | 高性能核心引擎 (索引/存储) |

---

## 3. Python 核心架构

### 3.1 包结构

```
openviking/
├── __init__.py              # 包入口
├── client.py                # 主客户端接口 (SyncOpenViking, AsyncOpenViking)
├── async_client.py          # 异步客户端实现
├── sync_client.py           # 同步客户端实现
├── agfs_manager.py          # AGFS 管理器
│
├── core/                    # 核心数据模型
│   ├── context.py           # Context 类 (统一上下文)
│   ├── directories.py       # 目录管理
│   ├── building_tree.py     # 树构建逻辑
│   ├── skill_loader.py      # 技能加载器
│   └── mcp_converter.py     # MCP 转换器
│
├── message/                 # 消息处理
│   ├── message.py           # Message 类
│   └── part.py              # Part 定义 (TextPart, ToolPart, ContextPart)
│
├── models/                  # 模型实现
│   ├── embedder/            # 嵌入模型
│   │   ├── base.py          # BaseEmbedder 接口
│   │   ├── openai_embedders.py
│   │   ├── jina_embedders.py
│   │   ├── volcengine_embedders.py
│   │   └── vikingdb_embedders.py
│   │
│   └── vlm/                 # 视觉语言模型
│       ├── base.py          # BaseVLM 接口
│       ├── registry.py      # VLM 注册表
│       ├── token_usage.py   # Token 用量统计
│       └── backends/
│           ├── openai_vlm.py
│           ├── volcengine_vlm.py
│           └── litellm_vlm.py
│
├── parse/                   # 资源解析
│   ├── base.py              # BaseParser 接口
│   ├── registry.py          # 解析器注册表
│   ├── converter.py         # 格式转换器
│   ├── directory_scan.py    # 目录扫描
│   ├── tree_builder.py      # 树构建
│   ├── ovpack/              # OVPack 格式
│   └── parsers/             # 具体解析器
│       ├── text.py
│       ├── markdown.py
│       ├── html.py
│       ├── pdf.py
│       ├── word.py
│       ├── powerpoint.py
│       ├── excel.py
│       ├── epub.py
│       ├── zip_parser.py
│       ├── directory.py
│       ├── code/            # 代码解析
│       │   ├── code.py
│       │   ├── ast/
│       │   │   ├── extractor.py
│       │   │   ├── skeleton.py
│       │   │   └── languages/  # Python/C++/JS/TS/Java/Rust/Go/C#
│       │   └── media/        # 媒体解析
│       │       ├── image.py
│       │   └── video.py
│       │   └── audio.py
│       └── upload_utils.py
│
├── storage/                 # 存储系统
│   ├── local_fs.py          # 本地文件系统
│   ├── observers/           # 观察者模式
│   │   ├── base_observer.py
│   │   ├── vlm_observer.py
│   │   ├── transaction_observer.py
│   │   ├── queue_observer.py
│   │   └── vikingdb_observer.py
│   │
│   └── vectordb/            # 向量数据库
│       ├── collection/      # 集合管理
│       │   ├── collection.py        # Collection 接口
│       │   ├── local_collection.py
│       │   ├── vikingdb_collection.py
│       │   ├── volcengine_collection.py
│       │   └── http_collection.py
│       │
│       ├── project/         # 项目管理
│       │   ├── project.py           # Project 接口
│       │   ├── local_project.py
│       │   ├── vikingdb_project.py
│       │   └── volcengine_project.py
│       │
│       ├── store/           # 数据存储
│       │   ├── store.py             # Store 接口
│       │   ├── local_store.py
│       │   └── file_store.py
│       │
│       ├── meta/            # 元数据管理
│       │   ├── dict.py
│       │   ├── collection_meta.py
│       │   └── index_meta.py
│       │
│       ├── vectorize/       # 向量化
│       │   ├── vectorizer.py      # Vectorizer 接口
│       │   ├── base.py
│       │   └── volcengine_vectorizer.py
│       │
│       ├── service/         # 服务层
│       │   ├── api_fastapi.py
│       │   └── server_fastapi.py
│       │
│       └── utils/           # 工具函数
│
├── session/                 # 会话管理
│   ├── extractor.py         # 会话提取器
│   ├── compressor.py        # 会话压缩器
│   └── ...
│
├── retrieve/                # 检索模块
│   ├── hierarchical_retriever.py  # 分层检索器
│   └── ...
│
├── service/                 # 服务层
│   └── ...
│
├── eval/                    # 评估模块 (RAGAS)
│   ├── ragas/               # RAGAS 评估管线
│   │   ├── base.py
│   │   ├── pipeline.py
│   │   ├── generator.py
│   │   ├── rag_eval.py
│   │   └── playback.py
│   │
│   └── recorder/            # 记录器
│       ├── recorder.py
│       ├── recording_client.py
│       └── wrapper.py
│
├── utils/                   # 工具函数
│   └── ...
│
└── server/                  # REST API 服务端
    ├── app.py               # FastAPI 应用
    ├── config.py            # 服务端配置
    ├── auth.py              # 认证模块
    ├── api_keys.py          # API 密钥管理
    ├── dependencies.py      # 依赖注入
    ├── identity.py          # 身份识别
    └── routers/             # API 路由
        ├── admin.py         # 管理员接口
        ├── admin_keys.py    # API 密钥管理
        ├── bot.py           # Bot 接口
        ├── content.py       # 内容接口
        ├── debug.py         # 调试接口
        ├── filesystem.py    # 文件系统接口
        ├── observer.py      # 观察者接口
        ├── pack.py          # 打包接口
        ├── relations.py     # 关系接口
        ├── resources.py     # 资源接口
        ├── search.py        # 搜索接口
        ├── sessions.py      # 会话接口
        └── system.py        # 系统接口
```

### 3.2 核心数据模型

#### 3.2.1 Context 类 (统一上下文)

位于 `openviking/core/context.py`：

```python
class Context:
    """
    统一上下文数据模型，支持分层加载

    属性:
        uri: Viking URI 标识符
        content_type: 内容类型 (TEXT, CODE, MEDIA 等)
        level: 层级 (L0=摘要，L1=概述，L2=详情)
        content: 上下文内容
        vector: 向量表示 (用于检索)
        metadata: 元数据
    """
```

#### 3.2.2 Message 和 Part

位于 `openviking/message/`：

- **Message**: 消息结构 (role + parts)
- **Part** 及其子类:
  - `TextPart`: 文本内容
  - `ToolPart`: 工具调用/结果
  - `ContextPart`: 上下文引用

### 3.3 插件化架构

#### 3.3.1 解析器架构

```
BaseParser (openviking/parse/base.py)
    ↓
注册表 (openviking/parse/registry.py)
    ↓
具体解析器 (openviking/parse/parsers/)
    ├── TextParser - 纯文本文件
    ├── MarkdownParser - Markdown 文档
    ├── HTMLParser - HTML 页面
    ├── PDFParser - PDF 文档
    ├── WordParser - Word 文档
    ├── PowerPointParser - PPT 文件
    ├── ExcelParser - Excel 文件
    ├── EPUBParser - EPUB 电子书
    ├── ZIPParser - 压缩包
    ├── DirectoryParser - 目录扫描
    ├── CodeParser - 代码解析
    │   ├── AST Extractor (Tree-sitter)
    │   └── Languages: Python/C++/JS/TS/Java/Rust/Go/C#
    └── MediaParser - 媒体文件
        ├── ImageParser
        ├── VideoParser
        └── AudioParser
```

#### 3.3.2 VLM 和 Embedder 架构

```
BaseVLM (openviking/models/vlm/base.py)
    ↓
注册表 (openviking/models/vlm/registry.py)
    ↓
实现
    ├── OpenAI VLM
    ├── VolcEngine VLM
    └── LiteLLM VLM

BaseEmbedder (openviking/models/embedder/base.py)
    ↓
注册表
    ↓
实现
    ├── OpenAI Embedder
    ├── Jina Embedder
    ├── VolcEngine Embedder
    └── VikingDB Embedder
```

---

## 4. C++ 核心引擎

### 4.1 架构

位于 `src/`，通过 pybind11 暴露给 Python：

```
src/
├── CMakeLists.txt           # CMake 构建配置
├── pybind11_interface.cpp   # Python 绑定入口
├── py_accessors.h           # Python 访问器头文件
│
├── common/                  # 通用工具
│   └── *.cpp
│
├── index/                   # 索引引擎
│   └── *.cpp
│
└── store/                   # 存储引擎
    └── *.cpp
```

### 4.2 构建流程

1. `setup.py` 调用 CMake 编译
2. 链接 LevelDB 和 SPDLog
3. 使用 pybind11 生成 Python 扩展模块 `engine.so`
4. ARM 平台额外链接 KRL 库

### 4.3 依赖库

| 库 | 用途 | 版本 |
|----|------|------|
| **LevelDB** | 键值存储引擎 | 1.23 |
| **SPDLog** | 日志库 | 1.14.1 |
| **pybind11** | Python 绑定 | - |
| **KRL** | ARM 平台库 | - |
| **RapidJSON** | JSON 解析 | - |
| **Croaring** | 位集库 | - |

---

## 5. Rust CLI

### 5.1 结构

位于 `crates/ov_cli/`：

```
crates/ov_cli/
├── Cargo.toml               # Rust 包配置
├── src/
│   ├── main.rs              # 主入口
│   ├── client.rs            # API 客户端
│   ├── config.rs            # 配置管理
│   ├── error.rs             # 错误处理
│   ├── output.rs            # 输出格式化
│   └── commands/            # 子命令
│       ├── admin.rs         # 管理员命令
│       ├── chat.rs          # 聊天命令
│       ├── content.rs       # 内容命令
│       ├── filesystem.rs    # 文件系统命令
│       ├── observer.rs      # 观察者命令
│       ├── pack.rs          # 打包命令
│       ├── relations.rs     # 关系命令
│       ├── resources.rs     # 资源命令
│       ├── search.rs        # 搜索命令
│       ├── session.rs       # 会话命令
│       └── system.rs        # 系统命令
│
│   └── tui/                 # 终端用户界面
│       ├── app.rs           # TUI 应用状态
│       ├── event.rs         # 事件处理
│       ├── tree.rs          # 树形视图
│       └── ui.rs            # UI 渲染
```

### 5.2 主要命令

| 命令 | 描述 |
|------|------|
| `ov admin` | 管理员操作 |
| `ov chat` | 聊天交互 |
| `ov content` | 内容管理 |
| `ov filesystem` | 文件系统操作 |
| `ov observer` | 观察者管理 |
| `ov pack` | 打包/导出 |
| `ov relations` | 关系管理 |
| `ov resources` | 资源管理 |
| `ov search` | 搜索 |
| `ov session` | 会话管理 |
| `ov system` | 系统信息 |

---

## 6. VikingBot AI 框架

### 6.1 架构

位于 `bot/vikingbot/`：

```
bot/vikingbot/
├── agent/                   # Agent 核心
│   ├── context.py           # Agent 上下文
│   ├── loop.py              # 主循环
│   ├── memory.py            # 记忆管理
│   ├── skills.py            # 技能管理
│   ├── subagent.py          # 子 Agent
│   └── tools/               # 工具集
│       ├── base.py
│       ├── cron.py          # 定时任务
│       ├── filesystem.py    # 文件系统
│       ├── image.py         # 图像处理
│       ├── message.py       # 消息工具
│       ├── shell.py         # Shell 执行
│       ├── web.py           # Web 工具
│       └── registry.py      # 工具注册表
│
├── bus/                     # 消息总线
│   ├── events.py
│   └── queue.py
│
├── channels/                # 聊天渠道
│   ├── base.py
│   ├── chat.py
│   ├── dingtalk.py         # 钉钉
│   ├── discord.py          # Discord
│   ├── email.py            # 邮件
│   ├── feishu.py           # 飞书
│   ├── qq.py               # QQ
│   ├── slack.py            # Slack
│   ├── telegram.py         # Telegram
│   └── whatsapp.py         # WhatsApp
│
├── config/                  # 配置管理
│   ├── loader.py
│   └── schema.py
│
├── console/                 # 控制台
│   └── web_console.py      # Web 控制台 (Gradio)
│
├── hooks/                   # Hook 系统
│   ├── base.py
│   ├── manager.py
│   └── builtins/
│       └── openviking_hooks.py
│
├── providers/               # LLM Provider
│   ├── base.py
│   ├── litellm_provider.py
│   └── registry.py
│
├── sandbox/                 # 沙箱环境
│   ├── base.py
│   ├── manager.py
│   └── backends/
│       ├── aiosandbox.py
│       ├── direct.py
│       ├── opensandbox.py
│       └── srt.py
│
└── openviking_mount/        # OpenViking 挂载
    ├── fuse_finder.py
    ├── fuse_proxy.py
    ├── fuse_simple.py
    ├── manager.py
    ├── mount.py
    ├── ov_server.py
    └── viking_fuse.py
```

---

## 7. 存储系统

### 7.1 分层存储架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Storage Layer                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Collection │  │   Project   │  │    Store    │         │
│  │  Interface  │  │  Interface  │  │  Interface  │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                  │
│  ┌──────▼────────────────▼────────────────▼──────┐         │
│  │              Implementation Layer             │         │
│  ├───────────────────────────────────────────────┤         │
│  │  ┌──────────────┐  ┌──────────────┐          │         │
│  │  │ Local        │  │  VikingDB    │          │         │
│  │  │ Implementation│ │  Implementation│         │         │
│  │  └──────────────┘  └──────────────┘          │         │
│  │  ┌──────────────┐  ┌──────────────┐          │         │
│  │  │ VolcEngine   │  │  HTTP        │          │         │
│  │  │ Implementation│ │  Implementation│         │         │
│  │  └──────────────┘  └──────────────┘          │         │
│  └───────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 观察者模式

```
┌─────────────────────────────────────────────────────────────┐
│                   Observer Pattern                           │
├─────────────────────────────────────────────────────────────┤
│  BaseObserver                                              │
│      ↑                                                     │
│  ┌──┴──────────┬──────────┬──────────┬──────────┐         │
│  │             │          │          │          │         │
│  ↓             ↓          ↓          ↓          ↓         │
│ VLMObserver  TransactionObserver  QueueObserver  ...       │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. 会话管理

### 8.1 会话生命周期

```
┌─────────────────────────────────────────────────────────────┐
│                  Session Lifecycle                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Session Start                                              │
│       ↓                                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Message Exchange (User ↔ Agent)                    │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │  Auto-Extraction (extractor.py)            │   │   │
│  │  │  - Action Extraction                       │   │   │
│  │  │  - Memory Deduplication                    │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│       ↓                                                      │
│  Session Commit                                             │
│       ↓                                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Compression (compressor.py)                        │   │
│  │  - Context Compression                              │   │
│  │  - VectorDB Storage                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. 检索系统

### 9.1 分层检索器

位于 `openviking/retrieve/hierarchical_retriever.py`：

```
分层检索流程:
1. L0 (摘要层) - 快速获取上下文概览
2. L1 (概述层) - 扩展关键信息
3. L2 (详情层) - 深入细节内容

结合:
- 向量搜索 (语义匹配)
- 目录遍历 (结构检索)
- 目标目录限定 (定向检索)
```

---

## 10. 评估系统

### 10.1 RAGAS 评估管线

位于 `openviking/eval/ragas/`：

```
评估流程:
1. Dataset Generation (generator.py)
2. Pipeline Execution (pipeline.py)
3. RAG Evaluation (rag_eval.py)
4. Record Analysis (record_analysis.py)
5. Playback (playback.py)
```

---

## 11. REST API 架构

### 11.1 API 路由

位于 `openviking/server/routers/`：

| 路由 | 职责 |
|------|------|
| `/admin` | 管理员操作 |
| `/admin/keys` | API 密钥管理 |
| `/bot` | Bot 接口 |
| `/content` | 内容管理 |
| `/debug` | 调试接口 |
| `/filesystem` | 文件系统操作 |
| `/observer` | 观察者管理 |
| `/pack` | 打包/导出 |
| `/relations` | 关系管理 |
| `/resources` | 资源管理 |
| `/search` | 搜索接口 |
| `/sessions` | 会话管理 |
| `/system` | 系统信息 |

### 11.2 认证与授权

- **API Keys**: `openviking/server/api_keys.py`
- **Auth**: `openviking/server/auth.py`
- **Identity**: `openviking/server/identity.py`
- **Dependencies**: `openviking/server/dependencies.py`

---

## 12. 第三方组件

### 12.1 AGFS (Agent File System)

位于 `third_party/agfs/`，Go 实现：

- 提供虚拟文件系统访问
- 端口：1833
- 支持本地和 S3 存储

### 12.2 Web Admin

位于 `webadmin/`，React + Vite：

- 前端管理界面
- 端口：5173
- 无后端，直接调用 REST API

---

## 13. 配置文件

### 13.1 服务端配置 (ov.conf)

```json
{
  "storage": {
    "workspace": "/home/user/openviking_workspace"
  },
  "embedding": {
    "dense": {
      "provider": "openai",
      "api_key": "...",
      "api_base": "...",
      "model": "text-embedding-3-large",
      "dimension": 3072
    }
  },
  "vlm": {
    "provider": "openai",
    "api_key": "...",
    "api_base": "...",
    "model": "gpt-4-vision-preview"
  }
}
```

### 13.2 CLI 配置 (ovcli.conf)

```json
{
  "url": "http://localhost:1933",
  "timeout": 60.0,
  "output": "table"
}
```

---

## 14. 依赖管理

### 14.1 Python 依赖

核心依赖：

- `pydantic>=2.0.0` - 数据验证
- `httpx>=0.25.0` - HTTP 客户端
- `fastapi>=0.128.0`, `uvicorn>=0.39.0` - Web 框架
- `pyyaml>=6.0` - YAML 解析
- `openai>=1.0.0`, `litellm>=1.0.0` - VLM 集成
- `volcengine>=1.0.216` - 火山引擎集成
- `loguru>=0.7.3` - 日志
- `apscheduler>=3.11.0` - 定时任务

文档解析：

- `pdfplumber`, `readabilipy`, `markdownify`
- `python-docx`, `python-pptx`, `openpyxl`, `ebooklib`

代码解析：

- `tree-sitter-python`, `tree-sitter-cpp`, `tree-sitter-javascript`
- `tree-sitter-typescript`, `tree-sitter-java`, `tree-sitter-rust`
- `tree-sitter-go`, `tree-sitter-c_sharp`

### 14.2 Rust 依赖

详见 `crates/ov_cli/Cargo.toml`

### 14.3 C++ 依赖

详见 `src/CMakeLists.txt` 和 `third_party/`

---

## 15. 测试架构

### 15.1 测试分类

```
tests/
├── unit/                    # 单元测试
├── client/                  # 客户端测试
├── server/                  # 服务端测试
├── parse/                   # 解析器测试
├── session/                 # 会话测试
├── storage/                 # 存储测试
├── vectordb/                # 向量数据库测试
├── engine/                  # C++ 引擎测试
├── integration/             # 集成测试
├── eval/                    # RAGAS 评估测试
├── agfs/                    # AGFS 测试
├── retrieve/                # 检索测试
├── cli/                     # CLI 测试
└── misc/                    # 杂项测试
```

### 15.2 测试运行

```bash
# 运行全部测试
uv run pytest tests/ -v --cov=openviking

# 运行单元测试
uv run pytest tests/unit/ -v

# 运行服务端测试
uv run pytest tests/server/ -v

# 运行特定测试
uv run pytest tests/client/test_search.py -v
```

---

## 16. 部署架构

### 16.1 本地部署

```bash
# 1. 构建所有组件
make build

# 2. 安装依赖
uv sync --frozen --extra test

# 3. 部署 AGFS
bash scripts/agfs-deploy.sh deploy

# 4. 启动服务
~/.openviking/services.sh start
```

### 16.2 Docker 部署

```bash
# 使用 docker-compose.yml
docker-compose up -d

# 服务:
# - openviking-server (Port 1933)
# - agfs (Port 1833)
# - webadmin (Port 5173)
```

### 16.3 Kubernetes 部署

```bash
# 使用 Helm Chart (examples/k8s-helm/)
helm install openviking examples/k8s-helm/
```

---

## 17. 设计原则

### 17.1 核心设计原则

1. **统一上下文模型**: 所有数据通过 `Context` 类统一表示
2. **分层加载**: L0/L1/L2 分层加载，平衡性能与完整性
3. **插件化架构**: 解析器、VLM、Embedder 等插件化，易于扩展
4. **多租户支持**: 支持多租户和 API 密钥管理
5. **观察者模式**: 存储系统使用观察者模式实现异步处理
6. **接口优先**: 定义清晰的接口，实现可替换

### 17.2 扩展性设计

- **新解析器**: 实现 `BaseParser` 接口，注册到 `registry.py`
- **新 VLM**: 实现 `BaseVLM` 接口，注册到 `registry.py`
- **新 Embedder**: 实现 `BaseEmbedder` 接口，注册到 `registry.py`
- **新存储后端**: 实现 `Collection`/`Project`/`Store` 接口

---

## 18. 未来规划

### 18.1 短期目标

- 完善 Claude Memory Plugin 集成
- 优化向量数据库性能
- 增强代码解析能力
- 完善评估体系

### 18.2 长期目标

- 支持更多 LLM 提供商
- 增强多 Agent 协作能力
- 优化分布式部署
- 完善 MCP 集成

---

## 附录

### A. 术语表

| 术语 | 描述 |
|------|------|
| **Viking URI** | `viking://` 协议统一标识符 |
| **VLM** | Vision-Language Model，视觉语言模型 |
| **Embedder** | 文本嵌入模型 |
| **AGFS** | Agent File System，虚拟文件系统 |
| **L0/L1/L2** | 分层上下文加载级别 |
| **OVPack** | OpenViking 打包格式 |

### B. 参考资料

- [CLAUDE.md](/home/users/humingqing/work/OpenViking/CLAUDE.md) - 项目指南
- [docs/en/](/home/users/humingqing/work/OpenViking/docs/en/) - 完整文档
- [pyproject.toml](/home/users/humingqing/work/OpenViking/pyproject.toml) - Python 依赖
