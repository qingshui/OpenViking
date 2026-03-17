# OpenViking Web Admin

## 架构

```
┌─────────────────┐         ┌─────────────────┐
│   Web Browser   │         │ OpenViking API  │
│                 │         │  (Python:1933)  │
│  - React SPA    │────────▶│  - REST API     │
│  - UI Components│         │  - Business Log │
└─────────────────┘         └─────────────────┘
         │                          │
         │  (nginx:8173)            │  (nginx:8933)
         ▼                          ▼
┌────────────────────────────────────────────────────────────────┐
│                     Production Environment                      │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                     Nginx Proxy                            ││
│  │  - Port 8173 → WebAdmin Frontend (5173)                   ││
│  │  - Port 8933 → OpenViking API (1933)                      ││
│  └────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────┘
```

## 部署

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

将 Web Admin 部署到 `$HOME/.openviking/webadmin/` 目录：

```bash
# 从代码库运行部署脚本
bash scripts/webadmin-deploy.sh deploy
```

部署后，使用主服务管理脚本启动服务：

```bash
# 启动所有服务 (AGFS + OpenViking Server + Web Admin)
~/.openviking/services.sh start

# 仅启动 Web Admin 前端
~/.openviking/services.sh start-webadmin-frontend

# 停止 Web Admin
~/.openviking/services.sh stop-webadmin-frontend

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

# 仅启动 Web Admin 前端
~/.openviking/services.sh start-webadmin-frontend

# 查看服务状态
~/.openviking/services.sh status
```

### 服务状态输出

```
=== OpenViking 服务器 ===
状态：运行中
PID: 12345
访问：http://localhost:1933

=== Web Admin 前端 (端口 5173, Vite) ===
状态：运行中 (Vite)
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

## API 路由

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
├── src/                     # React 前端代码
│   ├── services/            # API 服务层
│   │   ├── api.ts          # API 客户端 (直接调用 OpenViking API)
│   │   ├── resources.ts    # 资源服务
│   │   ├── sessions.ts     # 会话服务
│   │   ├── filesystem.ts   # 文件系统服务
│   │   └── search.ts       # 搜索服务
│   ├── pages/              # 页面组件
│   │   ├── Dashboard.tsx
│   │   ├── Resources.tsx
│   │   ├── Sessions.tsx
│   │   ├── Filesystem.tsx
│   │   ├── Search.tsx
│   │   └── SessionManagement.tsx
│   └── components/         # UI 组件
├── public/                 # 静态资源
├── index.html              # HTML 入口
├── nginx.conf              # Nginx 配置模板
├── vite.config.ts          # Vite 配置
├── package.json            # 依赖配置
└── README.md               # 本文档

部署目录 (~/.openviking/webadmin/):
├── node_modules/           # 前端依赖
├── dist/                   # 前端构建产物
│   ├── index.html
│   └── assets/
├── services.sh             # 服务管理脚本
├── nginx.conf              # Nginx 配置
└── frontend.log            # 前端日志
```

## 注意事项

- 前端直接调用 OpenViking API (localhost:1933)
- 前端使用 Node.js + Vite 启动
- 通过 Nginx 配置将请求路由到对应服务
- 本地开发时可直接访问 5173 端口
