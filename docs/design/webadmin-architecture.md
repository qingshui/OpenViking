# OpenViking Web Admin 架构设计文档

## 概述

OpenViking Web Admin 是一个完全独立的 React 前端管理界面，通过 HTTP API 与现有 OpenViking 服务器通信，**不修改任何现有后端代码**。

## 技术架构

### 前端技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 框架 | React 18 + TypeScript | 类型安全的组件化开发 |
| 构建工具 | Vite 5.4 | 快速的热模块替换 (HMR) |
| HTTP 客户端 | Axios | 请求拦截器 + 统一错误处理 |
| 路由 | React Router 7 | 客户端路由管理 |
| 状态管理 | Zustand + React Query | 全局状态 + 服务端状态缓存 |
| 样式 | Tailwind CSS | 原子化 CSS 框架 |
| 图表 | Recharts | 数据可视化 |
| 日期处理 | date-fns | 日期格式化 |

### 架构分层

```
┌─────────────────────────────────────────────────────────────┐
│                    WebAdmin Frontend                         │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐  │
│  │              API Service Layer (核心)                  │  │
│  │  - api.ts (基础 HTTP 客户端 + 认证 + 拦截器)            │  │
│  │  - auth.ts (认证管理)                                 │  │
│  │  - monitoring.ts (监控数据获取)                        │  │
│  │  - resources.ts (资源管理)                            │  │
│  │  - sessions.ts (会话管理)                             │  │
│  │  - filesystem.ts (文件系统)                           │  │
│  │  - search.ts (搜索)                                   │  │
│  │  - tasks.ts (任务追踪)                                │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Global State Management                   │  │
│  │  - AuthContext (认证上下文)                           │  │
│  │  - MonitoringContext (监控数据上下文)                  │  │
│  │  - Store (Zustand 全局状态)                           │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                UI Components                           │  │
│  │  - Layout (布局)                                      │  │
│  │  - Dashboard (仪表盘 - 监控)                          │  │
│  │  - ResourceManager (资源管理)                         │  │
│  │  - SessionManager (会话管理)                          │  │
│  │  - FileExplorer (文件浏览器)                          │  │
│  │  - SearchPanel (搜索面板)                             │  │
│  │  - AdminPanel (管理面板)                              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

```
┌─────────────────┐         ┌──────────────────────────────────┐
│   Web Browser   │         │         OpenViking API           │
│                 │         │  (Python:1933)                   │
│  - React SPA    │────────▶│  - REST API                      │
│  - UI Components│         │  - Business Logic                │
│  - Local State  │         │  - VikingDB (Vector DB)          │
└─────────────────┘         └──────────────────────────────────┘
         │
         │  X-API-Key Header
         ▼
┌──────────────────────────────────────────────────────────────┐
│                    Service Layer                              │
│  - Axios with Interceptors                                   │
│  - Request/Response Error Handling                           │
│  - React Query Caching                                       │
└──────────────────────────────────────────────────────────────┘
```

## 项目结构

```
webadmin/
├── package.json                 # 依赖配置
├── tsconfig.json                # TypeScript 配置
├── vite.config.ts               # Vite 配置
├── tailwind.config.js           # Tailwind 配置
├── .env                         # 环境变量
├── index.html                   # HTML 入口
├── public/                      # 静态资源
│   └── favicon.ico
└── src/
    ├── main.tsx                 # React 入口
    ├── App.tsx                  # 主应用
    ├── services/                # API 服务层
    │   ├── api.ts              # 基础 HTTP 客户端
    │   ├── auth.ts             # 认证服务
    │   ├── monitoring.ts       # 监控服务
    │   ├── resources.ts        # 资源服务
    │   ├── sessions.ts         # 会话服务
    │   ├── filesystem.ts       # 文件系统服务
    │   ├── search.ts           # 搜索服务
    │   └── tasks.ts            # 任务服务
    ├── types/                   # TypeScript 类型定义
    │   ├── api.ts              # API 响应类型
    │   ├── resource.ts         # 资源类型
    │   ├── session.ts          # 会话类型
    │   ├── filesystem.ts       # 文件系统类型
    │   └── monitoring.ts       # 监控数据类型
    ├── hooks/                   # React Query Hooks
    │   ├── useAuth.ts
    │   ├── useMonitoring.ts
    │   ├── useResources.ts
    │   ├── useSessions.ts
    │   ├── useFilesystem.ts
    │   ├── useSearch.ts
    │   └── useTasks.ts
    ├── components/              # UI 组件
    │   ├── common/
    │   │   ├── Layout.tsx
    │   │   ├── Sidebar.tsx
    │   │   ├── Topbar.tsx
    │   │   ├── LoadingSpinner.tsx
    │   │   ├── Modal.tsx
    │   │   ├── StatusIndicator.tsx
    │   │   ├── MonitoringAlert.tsx
    │   │   └── ToastProvider.tsx
    │   └── ui/
    │       ├── Button.tsx
    │       ├── Input.tsx
    │       ├── Card.tsx
    │       ├── Table.tsx
    │       └── Toast.tsx
    ├── pages/                   # 页面组件
    │   ├── Login.tsx
    │   ├── Dashboard.tsx
    │   ├── ResourceManagement.tsx
    │   ├── ResourceDetail.tsx
    │   ├── SessionManagement.tsx
    │   ├── FileExplorer.tsx
    │   ├── SemanticSearch.tsx
    │   └── AdminPanel.tsx
    └── contexts/                # React Context
        ├── AuthContext.tsx
        └── MonitoringContext.tsx
```

## 核心服务层

### API 客户端 (api.ts)

```typescript
const API_BASE = import.meta.env.VITE_API_BASE_URL

export const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加 API Key
apiClient.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('ov_api_key')
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey
  }
  return config
})

// 响应拦截器 - 错误处理
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('ov_api_key')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

### 服务层职责

| 服务 | 职责 | API 映射 |
|------|------|---------|
| `api.ts` | 基础 HTTP 客户端、拦截器、错误处理 | N/A |
| `auth.ts` | 登录/登出、API Key 管理 | N/A (本地) |
| `monitoring.ts` | 系统状态、队列、VikingDB、VLM | `/api/v1/observer/*` |
| `resources.ts` | 资源 CRUD、内容读取 | `/api/v1/resources`, `/api/v1/content/*` |
| `sessions.ts` | 会话 CRUD、消息、提交 | `/api/v1/sessions/*` |
| `filesystem.ts` | 目录浏览、树形结构、文件操作 | `/api/v1/fs/*` |
| `search.ts` | 语义搜索、正则搜索 | `/api/v1/search/*` |
| `tasks.ts` | 任务状态查询 | `/api/v1/tasks/*` |

## API 接口映射

### 监控相关 API

| 功能 | API 路径 | 说明 |
|------|---------|------|
| 系统状态 | `GET /api/v1/system/status` | 系统健康状态 |
| 队列状态 | `GET /api/v1/observer/queue` | Embedding/Semantic 队列 |
| VikingDB 状态 | `GET /api/v1/observer/vikingdb` | 向量数据库状态 |
| VLM 状态 | `GET /api/v1/observer/vlm` | VLM Token 使用情况 |
| 系统整体 | `GET /api/v1/observer/system` | 系统整体状态 |

### 资源管理 API

| 功能 | API 路径 | 说明 |
|------|---------|------|
| 列出资源 | `GET /api/v1/fs/ls` | 查询参数：uri, recursive, limit |
| 添加资源 | `POST /api/v1/resources` | 请求体：path, parent, reason |
| 删除资源 | `DELETE /api/v1/fs` | 查询参数：uri, recursive |
| 读取 L0 | `GET /api/v1/content/abstract` | 查询参数：uri |
| 读取 L1 | `GET /api/v1/content/overview` | 查询参数：uri |
| 读取 L2 | `GET /api/v1/content/read` | 查询参数：uri, offset, limit |

### 会话管理 API

| 功能 | API 路径 | 说明 |
|------|---------|------|
| 创建会话 | `POST /api/v1/sessions` | - |
| 列出会话 | `GET /api/v1/sessions` | - |
| 会话详情 | `GET /api/v1/sessions/{session_id}` | - |
| 添加消息 | `POST /api/v1/sessions/{session_id}/messages` | 请求体：role, content |
| 提交会话 | `POST /api/v1/sessions/{session_id}/commit` | 查询参数：wait |
| 删除会话 | `DELETE /api/v1/sessions/{session_id}` | - |

### 文件系统 API

| 功能 | API 路径 | 说明 |
|------|---------|------|
| 列出目录 | `GET /api/v1/fs/ls` | 查询参数：uri, recursive, simple |
| 目录树 | `GET /api/v1/fs/tree` | 查询参数：uri, level_limit |
| 资源状态 | `GET /api/v1/fs/stat` | 查询参数：uri |
| 创建目录 | `POST /api/v1/fs/mkdir` | 请求体：uri |
| 移动资源 | `POST /api/v1/fs/mv` | 请求体：from_uri, to_uri |

### 搜索 API

| 功能 | API 路径 | 说明 |
|------|---------|------|
| 语义搜索 | `POST /api/v1/search/find` | 请求体：query, target_uri, limit |
| 带会话搜索 | `POST /api/v1/search/search` | 请求体：query, session_id |
| 内容搜索 | `POST /api/v1/search/grep` | 请求体：uri, pattern |
| 模式匹配 | `POST /api/v1/search/glob` | 请求体：pattern, uri |

### 任务追踪 API

| 功能 | API 路径 | 说明 |
|------|---------|------|
| 查询任务 | `GET /api/v1/tasks/{task_id}` | - |
| 列出任务 | `GET /api/v1/tasks` | - |

## 页面组件

### Dashboard.tsx - 监控仪表盘

显示系统整体状态：
- 系统状态指示灯
- 资源统计（总数、存储量）
- 队列监控（Embedding、Semantic 队列长度）
- VikingDB 状态（集合数、向量数、存储使用）
- VLM 状态（Token 使用、请求次数）
- 任务监控（进行中、失败任务）
- 队列长度图表

### ResourceManagement.tsx - 资源管理

- 资源列表表格
- 添加资源表单
- 删除资源确认
- 资源详情查看

### ResourceDetail.tsx - 资源详情

- 资源内容展示（L0/L1/L2）
- 元信息显示

### SessionManagement.tsx - 会话管理

- 会话列表
- 会话消息展示
- 添加消息
- 提交会话（压缩）

### FileExplorer.tsx - 文件浏览器

- 目录浏览
- 创建目录
- 文件内容预览（L0/L1/L2）

### SemanticSearch.tsx - 语义搜索

- 语义搜索（向量搜索）
- 内容搜索（正则搜索）
- 搜索结果展示

### AdminPanel.tsx - 管理面板

- 账户管理
- 用户管理
- 系统配置

## 认证机制

### 认证流程

1. 用户访问系统，重定向到登录页
2. 输入 API Key（或用户名密码）
3. 验证成功后，API Key 存储到 localStorage
4. 所有 API 请求通过 Axios 拦截器自动添加 `X-API-Key` header
5. 401 响应自动清空 Token 并跳转登录页

### 安全考虑

- API Key 存储在 localStorage（非 HTTP-only cookie）
- 所有 API 请求需要认证
- 401 响应自动处理
- 生产环境建议使用 HTTPS

## 状态管理

### Zustand 全局状态

```typescript
interface AppState {
  // 认证状态
  isAuthenticated: boolean
  apikey: string | null
  user: User | null
  login: (apikey: string) => Promise<void>
  logout: () => void

  // 监控数据
  systemStatus: SystemStatus | null
  queueStats: QueueStats | null
  resourceStats: ResourceStats | null
  refreshMonitoring: () => Promise<void>

  // 全局错误
  error: ErrorInfo | null
  setError: (error: ErrorInfo | null) => void
}
```

### React Query 数据获取

每个服务都有对应的 hook：

```typescript
export const useMonitoring = () => {
  return useQuery({
    queryKey: ['monitoring'],
    queryFn: monitoringService.getAll,
    refetchInterval: 30000, // 30 秒自动刷新
  })
}
```

## 部署方案

### 本地开发

```bash
# Terminal 1: OpenViking API
openviking-server

# Terminal 2: WebAdmin Frontend
cd webadmin
npm install
npm run dev
```

访问：http://localhost:5173

### 生产环境部署

部署到 `$HOME/.openviking/webadmin/` 目录：

```bash
# 构建前端
cd webadmin
npm run build

# 部署脚本
bash scripts/webadmin-deploy.sh deploy
```

### 服务管理

```bash
# 启动所有服务
~/.openviking/services.sh start

# 仅启动 Web Admin
~/.openviking/services.sh start-webadmin-frontend

# 停止 Web Admin
~/.openviking/services.sh stop-webadmin-frontend
```

### Nginx 配置（可选）

```nginx
# WebAdmin Frontend
server {
    listen 8173;
    server_name openviking.example.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# OpenViking API
server {
    listen 8933;
    server_name openviking.example.com;

    location / {
        proxy_pass http://localhost:1933;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 构建产物

```bash
# 构建后生成
dist/
├── index.html              # 入口 HTML
└── assets/
    ├── index-*.css         # 样式文件
    └── index-*.js          # JS 文件（含 React + 业务逻辑）
```

## 关键特性

1. **完全独立** - 不修改任何现有 OpenViking 后端代码
2. **API 驱动** - 所有功能通过 HTTP API 实现
3. **类型安全** - TypeScript 提供编译时类型检查
4. **现代化 UI** - React + Tailwind CSS 响应式设计
5. **高效缓存** - React Query 自动缓存和刷新
6. **统一错误处理** - Axios 拦截器全局错误处理
7. **实时监控** - 30 秒自动刷新监控数据

## 扩展方向

1. **WebSocket 实时推送** - 替代轮询实现实时监控
2. **数据导出** - 监控数据导出为 CSV/PDF
3. **告警配置** - 配置监控告警阈值
4. **自定义仪表板** - 用户自定义监控面板
5. **多租户管理** - 多租户切换和隔离

## 版本信息

- **当前版本**: 0.1.0
- **React 版本**: 18.x
- **TypeScript 版本**: 5.x
- **Vite 版本**: 5.4.x
- **构建时间**: 2026-03-18
