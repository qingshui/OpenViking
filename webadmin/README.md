# OpenViking Web Admin

## 架构

WebAdmin 分为两部分：

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Web Browser   │         │  WebAdmin Backend│         │ OpenViking API  │
│                 │         │  (Node.js:3000)  │         │  (Python:1933)  │
│  - React SPA    │────────▶│  - Config Mgmt   │────────▶│  - REST API     │
│  - UI Components│         │  - API Proxy     │         │  - Business Log │
└─────────────────┘         └──────────────────┘         └─────────────────┘
         │                           │                          │
         │  (nginx:8173)             │  (nginx:8173 /api)       │  (nginx:8933)
         ▼                           ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Production Environment                            │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                        Nginx Proxy                                 │ │
│  │  - Port 8173 → WebAdmin Frontend (5173)                           │ │
│  │  - /api → WebAdmin Backend (3000)                                 │ │
│  │  - Port 8933 → OpenViking API (1933)                              │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## 部署

### 本地开发

```bash
# Terminal 1: OpenViking API
openviking-server

# Terminal 2: WebAdmin Backend
cd webadmin/backend
npm install
npm start

# Terminal 3: WebAdmin Frontend
cd webadmin
npm install
npm run dev
```

访问：http://localhost:5173

### 生产环境部署

将 Web Admin 部署到 `$HOME/.openviking/webadmin/` 目录：

```bash
# 从代码库运行部署脚本
bash scripts/webadmin-deploy.sh deploy
```

部署后，使用主服务管理脚本启动服务：

```bash
# 启动所有服务 (AGFS + OpenViking Server + Web Admin)
~/.openviking/services.sh start

# 仅启动 Web Admin (前后端)
~/.openviking/services.sh start-webadmin

# 仅启动 Web Admin 前端 (Node.js + Vite)
~/.openviking/services.sh start-webadmin-frontend

# 仅启动 Web Admin 后端 (Node.js)
~/.openviking/services.sh start-webadmin-backend

# 停止 Web Admin
~/.openviking/services.sh stop-webadmin

# 查看服务状态
~/.openviking/services.sh status
```

**前端启动方式**：生产环境中，Web Admin 前端使用 Node.js + Vite 启动：
```bash
node ~/.openviking/webadmin/node_modules/vite/bin/vite.js --host 0.0.0.0
```

## 主服务管理脚本

使用 `$HOME/.openviking/services.sh` 统一管理所有 OpenViking 服务：

```bash
# 启动所有服务 (AGFS + OpenViking Server + Web Admin)
~/.openviking/services.sh start

# 仅启动 Web Admin
~/.openviking/services.sh start-webadmin

# 查看服务状态
~/.openviking/services.sh status
```

### 服务状态输出

```
=== OpenViking 服务器 ===
状态：运行中
PID: 12345
访问：http://localhost:1933

=== Web Admin 后端 (端口 3000) ===
状态：运行中
PID: 12346
访问：http://localhost:3000/api/proxy

=== Web Admin 前端 (端口 5173) ===
状态：运行中 (Node.js + Vite)
访问：http://0.0.0.0:5173

=== AGFS 服务 ===
状态：运行中
PID: 12344
访问：localhost:1833
```

## 生产环境 Nginx 配置（可选）

```nginx
# WebAdmin Frontend
server {
    listen 8173;
    server_name <your-server-hostname>;

    # Frontend static files
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# OpenViking API
server {
    listen 8933;
    server_name <your-server-hostname>;

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

## 配置管理

配置存储在 WebAdmin 后端服务的内存中，通过 API 进行管理：

**API 端点：**
- `PUT /api/config` - 更新配置
- `GET /api/config` - 获取当前配置

**配置项：**
- `host`: OpenViking API 主机地址
- `port`: OpenViking API 端口
- `root_api_key`: API 认证密钥
- `cors_origins`: 允许的 CORS 来源
- `with_bot`: 是否启用 Bot API
- `bot_api_url`: Bot API 地址

**使用示例：**

```bash
# 更新配置
curl -X PUT http://localhost:3000/api/config \
  -H "Content-Type: application/json" \
  -d '{"host": "localhost", "port": 1933, "root_api_key": "your-api-key"}'

# 获取配置
curl http://localhost:3000/api/config
```

## API 路由

### WebAdmin Backend API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/config` | 获取当前配置 |
| PUT | `/api/config` | 更新配置 |
| GET | `/api/health` | 测试连接 |
| POST | `/api/proxy` | 代理请求到 OpenViking API |

### OpenViking API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/system/status` | 系统状态 |
| POST | `/api/v1/search/find` | 搜索 |
| GET | `/api/v1/fs/ls` | 文件列表 |
| POST | `/api/v1/resources` | 添加资源 |
| DELETE | `/api/v1/fs` | 删除资源 |
| GET | `/api/v1/content/read` | 读取内容 |
| GET | `/api/v1/content/abstract` | 获取摘要 |
| GET | `/api/v1/content/overview` | 获取概览 |

## 项目结构

```
webadmin/
├── backend/                  # Node.js 后端服务
│   ├── server.js            # Express 服务器
│   ├── package.json         # 依赖配置
│   └── package-lock.json
├── src/                     # React 前端代码
│   ├── services/            # API 服务层
│   │   ├── api.ts          # API 客户端 (代理到 backend)
│   │   ├── resources.ts    # 资源服务
│   │   ├── sessions.ts     # 会话服务
│   │   ├── filesystem.ts   # 文件系统服务
│   │   └── search.ts       # 搜索服务
│   ├── pages/              # 页面组件
│   │   ├── Dashboard.tsx
│   │   ├── Resources.tsx
│   │   ├── Sessions.tsx
│   │   ├── Filesystem.tsx
│   │   └── Search.tsx
│   └── components/         # UI 组件
├── nginx.conf              # Nginx 配置模板
├── vite.config.ts          # Vite 配置
└── README.md               # 本文档

部署目录 (~/.openviking/webadmin/):
├── backend/                # 后端服务运行时
│   ├── server.js
│   ├── package.json
│   ├── package-lock.json
│   └── node_modules/
├── node_modules/           # 前端依赖
├── dist/                   # 前端构建产物
│   ├── index.html
│   └── assets/
├── services.sh             # 服务管理脚本
├── nginx.conf              # Nginx 配置
├── backend.log             # 后端日志
└── frontend.log            # 前端日志
```

## 注意事项

- 前端只与 WebAdmin 后端服务交互 (`/api` 路由)
- WebAdmin 后端负责调用 OpenViking API (localhost:1933)
- 配置管理完全在后端进行，前端只负责展示和提交配置
- 前端使用 Node.js + Vite 启动，而不是 Python HTTP server
- 前端不需要硬编码 OpenViking API 地址，完全由后端管理
