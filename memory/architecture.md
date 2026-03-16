# OpenViking 架构梳理

## 一、项目整体架构

### 1.1 核心组件结构

```
OpenViking/
├── openviking/                # Python SDK 和 HTTP 服务器
│   ├── async_client.py        # 异步客户端（嵌入式模式，单例模式）
│   ├── sync_client.py         # 同步客户端包装器
│   ├── client.py              # 本地客户端实现 (LocalClient)
│   ├── service/               # 业务逻辑层 (7 个服务)
│   │   ├── core.py            # 服务核心，组合所有子服务
│   │   ├── fs_service.py      # 文件系统服务
│   │   ├── search_service.py  # 搜索服务
│   │   ├── resource_service.py# 资源服务
│   │   ├── session_service.py # 会话服务
│   │   ├── relation_service.py# 关系服务
│   │   ├── pack_service.py    # 打包服务
│   │   └── debug_service.py   # 调试服务
│   ├── server/                # FastAPI HTTP 服务器
│   │   ├── app.py             # FastAPI 应用创建
│   │   ├── bootstrap.py       # 服务器启动入口
│   │   ├── routers/           # API 路由模块
│   │   └── config.py          # 服务器配置
│   ├── storage/               # 存储层
│   │   ├── viking_fs.py       # 虚拟文件系统抽象
│   │   ├── viking_vector_index_backend.py  # 向量索引后端
│   │   ├── queuefs/           # 异步队列系统
│   │   └── collection_schemas.py  # 集合 Schema
│   ├── parse/                 # 文档解析层
│   │   ├── parsers/           # 各种文档解析器
│   │   └── tree_builder.py    # 树结构构建
│   ├── retrieve/              # 检索层
│   │   ├── hierarchical_retriever.py  # 分层检索器
│   │   ├── intent_analyzer.py # 意图分析器
│   │   └── memory_lifecycle.py# 记忆生命周期
│   ├── session/               # 会话层
│   │   └── compressor.py      # 会话压缩器
│   ├── models/                # 模型层
│   │   └── embedder/          # Embedding 模型后端
│   ├── utils/                 # 工具层
│   └── core/                  # 核心层
│
├── bot/vikingbot/             # AI Agent 框架
│   ├── agent/                 # Agent 核心
│   │   ├── loop.py            # 主循环
│   │   ├── context.py         # 上下文管理
│   │   └── tools/             # Agent 工具
│   ├── channels/              # 多通道支持
│   ├── providers/             # LLM 提供者抽象
│   └── openviking_mount/      # OpenViking 集成层
│
├── crates/ov_cli/             # Rust CLI 客户端
│   ├── main.rs                # CLI 入口
│   ├── commands/              # 命令实现
│   └── tui/                   # 终端 UI
│
├── openviking_cli/            # Python CLI 包装器
│   └── rust_cli.py            # Rust CLI 入口
│
├── tests/                     # 测试套件
├── pyproject.toml             # 项目配置和依赖
├── setup.py                   # 构建脚本 (AGFS Go 和 C++ 扩展)
└── README.md                  # 项目说明
```

---

## 二、核心业务流程

### 2.1 上下文添加流程 (Input → Storage → Index)

```
Input → Parser → TreeBuilder → AGFS → SemanticQueue → Vector Index

详细流程:
1. 输入层：本地文件 / URL / GitHub 仓库
2. 解析层：Parser 根据类型选择解析器
   - PDF: pdfplumber, pdfminer
   - HTML: readability, html2text
   - Code: tree-sitter (Python/JS/Java/C++/Rust/Go 等)
   - Office: python-docx, openpyxl, pptx
3. 树构建层：构建层级树结构，分配 Viking URI，生成节点元数据
4. 存储层 (AGFS): L2 原始内容存储，目录结构维护
5. 异步语义处理队列：
   - SemanticProcessor (异步并发处理)
   - 最大并发：embedding=10, semantic=100
   - 队列管理：embedding_queue, semantic_queue, sync_queue
6. 模型处理:
   - VLM Model: 生成 L0 Abstract (~100 tokens), L1 Overview (~2k tokens)
   - Embedding Model: 生成 Dense/Sparse Vector
7. VikingDB: 存储 URI、向量、元数据 (不含文件内容)
```

### 2.2 检索业务流程 (Query → Retrieval → Results)

```
查询流程:
1. Intent Analyzer (意图分析): LLM 分析会话上下文，生成多类型查询
   - ContextType.MEMORY: 用户/Agent 记忆
   - ContextType.RESOURCE: 项目资源
   - ContextType.SKILL: Agent 技能

2. Hierarchical Retriever (分层检索器):
   Step 1: 确定起始目录
     - 根据 target_directories 或 context_type 确定根目录
     - ROOT 角色：全局搜索所有类型
     - 默认根目录：
       * viking://user/{space}/memories
       * viking://agent/{space}/memories
       * viking://resources
       * viking://agent/{space}/skills

   Step 2: 全局向量搜索 (Global Vector Search)
     - 在全库中搜索 Top-K (默认 3) 高相关目录
     - 补充起始点

   Step 3: 递归搜索 (Recursive Search)
     - 从起始点开始，按优先级队列遍历目录
     - 每层执行:
       1. 子目录向量搜索 (search_children)
       2. Rerank 重排序 (如果配置)
       3. 分数传播：final_score = α * child_score + (1-α) * parent_score (α=0.5)
       4. 收敛检查：连续 3 轮 Top-K 不变则停止
       5. 只递归 L0/L1 目录，L2 文件为终止节点

   Step 4: 结果转换
     - 读取关联上下文 (Relations)
     - 计算热度分数：hotness = f(active_count, updated_at)
     - 综合分数：final = (1-α)*semantic + α*hotness (α=0.2)
     - 添加 L0/L1 后缀到 URI

3. 结果输出: MatchedContext List
   - uri: viking://.../.abstract.md (L0) 或 .overview.md (L1)
   - context_type: MEMORY/RESOURCE/SKILL
   - level: 0/1/2
   - abstract: 摘要内容
   - score: 综合排序分数
   - relations: 关联上下文列表
```

### 2.3 会话管理流程 (Session Management)

```
Session 生命周期:

Create (开始) --> Active (进行中) --> Commit (结束)

- Create:
  - 生成 session_id
  - 初始化历史记录
  - 保存到 VikingDB

- Active:
  - add_message()
  - 存储 User/Assistant 消息
  - 关联上下文
  - 工具调用记录

- Commit:
  - 归档对话历史
  - 提取用户记忆
  - 提取 Agent 经验
  - 更新 user/agent/meories/目录
```

---

## 三、三层内容架构 (L0/L1/L2)

| 层级 | 文件 | Token 数 | 内容描述 | 用途 |
|------|------|--------|---------|------|
| **L0** | `.abstract.md` | ~100 | 一句话摘要 | 快速判断相关性 |
| **L1** | `.overview.md` | ~2k | 核心信息概览 | 规划阶段决策 |
| **L2** | 原始文件 | 完整 | 完整原始数据 | 按需深度阅读 |

访问方式:
```python
# 读取 L0 摘要
await client.abstract("viking://resources/path")

# 读取 L1 概览
await client.overview("viking://resources/path")

# 读取 L2 完整内容
await client.read("viking://resources/path")
```

---

## 四、Viking URI 结构

```
viking://
├── resources/                    # 全局资源 (项目文档、仓库、网页)
│   └── {project_name}/
│       ├── docs/
│       ├── src/
│       └── ...
│
├── user/{space}/                 # 用户个人空间
│   ├── memories/                 # 用户记忆
│   │   ├── preferences/          # 用户偏好
│   │   │   ├── writing_style
│   │   │   └── coding_habits
│   │   └── habits/               # 用户习惯
│   └── ...
│
└── agent/{space}/                # Agent 空间
    ├── skills/                   # Agent 技能
    │   ├── search_code
    │   ├── analyze_data
    │   └── ...
    ├── memories/                 # Agent 任务记忆
    │   ├── operational_tips      # 操作技巧
    │   └── tool_experience       # 工具使用经验
    └── instructions/             # Agent 指令
```

---

## 五、配置系统

### 5.1 配置文件位置

- **服务器配置**: `~/.openviking/ov.conf`
- **CLI 配置**: `~/.openviking/ovcli.conf`
- **环境变量**: `OPENVIKING_CONFIG_FILE`, `OPENVIKING_CLI_CONFIG_FILE`

### 5.2 ov.conf 配置模板

```json
{
  "storage": {
    "workspace": "~/.openviking/data",
    "agfs": {
      "mode": "http-client",
      "url": "http://localhost:3467",
      "timeout": 300
    },
    "vectordb": {
      "provider": "mongodb",
      "connection_uri": "mongodb://localhost:27017",
      "database": "openviking"
    }
  },
  "log": {
    "level": "INFO",
    "output": "stdout"
  },
  "embedding": {
    "dense": {
      "provider": "volcengine",
      "api_key": "your-api-key",
      "api_base": "https://ark.cn-beijing.volces.com/api/v3",
      "model": "doubao-embedding-vision-250615",
      "dimension": 1024,
      "max_concurrent": 10
    }
  },
  "vlm": {
    "provider": "volcengine",
    "api_key": "your-api-key",
    "api_base": "https://ark.cn-beijing.volces.com/api/v3",
    "model": "doubao-seed-2-0-pro-260215",
    "max_concurrent": 100
  },
  "rerank": {
    "provider": "volcengine",
    "threshold": 0.5
  },
  "parser": {
    "pdf": { ... },
    "code": { ... }
  }
}
```

---

## 六、部署与使用流程

### 6.1 安装流程

```bash
# 1. 安装 uv (推荐包管理器)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 创建虚拟环境并安装依赖
uv venv --python 3.11
source .venv/bin/activate
uv sync --all-extras

# 3. 本地开发安装 (编译 AGFS 和 C++ 扩展)
uv pip install -e . --force-reinstall

# 4. 安装 Bot 支持
uv pip install -e ".[bot]"

# 5. 安装 Rust CLI (可选)
cargo install --path crates/ov_cli
```

### 6.2 服务器启动

```bash
# 基础模式
openviking-server

# 带 Bot 集成
openviking-server --with-bot

# 自定义配置和端口
openviking-server --config ~/.openviking/ov.conf --port 8080

# 后台运行
nohup openviking-server > /data/log/openviking.log 2>&1 &
```

### 6.3 HTTP API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/resources` | POST | 添加资源 |
| `/api/v1/skills` | POST | 添加技能 |
| `/api/v1/fs/ls` | GET | 列出目录 |
| `/api/v1/fs/tree` | GET | 获取目录树 |
| `/api/v1/fs/stat` | GET | 获取资源状态 |
| `/api/v1/fs/mkdir` | POST | 创建目录 |
| `/api/v1/fs/rm` | DELETE | 删除资源 |
| `/api/v1/search/find` | POST | 语义搜索 (无会话) |
| `/api/v1/search/search` | POST | 语义搜索 (有会话) |
| `/api/v1/search/grep` | POST | 内容模式搜索 |
| `/api/v1/sessions` | POST/GET/DELETE | 会话管理 |
| `/api/v1/relations` | GET/POST | 关系管理 |
| `/api/v1/pack/export` | POST | 导出.ovpack |
| `/api/v1/pack/import` | POST | 导入.ovpack |

### 6.4 CLI 使用

```bash
# 状态检查
ov status

# 添加资源
ov add-resource <path-or-url> [--wait]

# 列出目录
ov ls viking://resources/

# 显示树状结构
ov tree viking://resources/volcengine -L 2

# 语义搜索
ov find "what is openviking"

# 内容搜索
ov grep "openviking" --uri viking://resources/volcengine/OpenViking/docs/zh

# 交互式聊天
ov chat
```

---

## 七、技术栈

| 层次 | 技术 | 说明 |
|------|------|------|
| **编程语言** | Python 3.10+, Go 1.22+, Rust 1.88+ | 核心/AGFS/CLI |
| **Web 框架** | FastAPI + Uvicorn | HTTP 服务器 |
| **存储** | MongoDB | 向量索引存储 |
| **文件系统** | AGFS (Go) | 内容存储，支持 HTTP 客户端和动态库绑定 |
| **向量模型** | Volcengine Doubao / OpenAI / LiteLLM | 支持多提供者 |
| **VLM 模型** | Volcengine / OpenAI / LiteLLM | 语义处理 |
| **文档解析** | pdfplumber, readability, tree-sitter | 多格式支持 |
| **包管理** | uv | 推荐包管理器 |
| **CLI** | Rust + TUI | 高性能命令行工具 |

---

## 八、核心设计特点

1. **文件系统范式** - 统一记忆、资源、技能的管理
2. **分层内容加载** - L0/L1/L2 按需加载，节省 Token
3. **目录递归检索** - 结合向量搜索和目录定位，提高检索效果
4. **可视化检索轨迹** - 可观察的检索路径，便于调试
5. **自动会话管理** - 会话结束自动提取记忆，实现自我迭代

---

*文档生成时间：2026-03-16*
*项目地址：https://github.com/volcengine/OpenViking*
