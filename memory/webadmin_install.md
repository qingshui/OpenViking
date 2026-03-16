# OpenViking Web Admin 安装文档

## 概述

OpenViking Web Admin 是一个完全独立的 Web 管理界面，通过 HTTP API 与 OpenViking 服务器通信，**不修改任何现有代码**。

## 项目结构

```
OpenViking/
├── webadmin/                    # Web Admin 项目
│   ├── public/
│   │   └── vite.svg
│   ├── src/
│   │   ├── components/
│   │   │   └── common/
│   │   │       └── Layout.tsx
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── ResourceManagement.tsx
│   │   │   ├── SessionManagement.tsx
│   │   │   ├── FileExplorer.tsx
│   │   │   └── SemanticSearch.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── resources.ts
│   │   │   ├── sessions.ts
│   │   │   ├── filesystem.ts
│   │   │   └── search.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── .env
│   ├── .env.example
│   ├── .gitignore
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── scripts/
│   ├── install.sh               # 安装脚本
│   └── README.md                # 安装指南
└── memory/
    ├── webadmin_design.md       # 设计文档
    └── webadmin_install.md      # 安装文档（本文件）
```

## 快速安装

### 1. 运行安装脚本

```bash
cd /Users/humingqing/baidu/work/paddle-serving/baidu/third/OpenViking
chmod +x scripts/install.sh
./scripts/install.sh
```

### 2. 编辑配置文件

```bash
# OpenViking 服务器配置
nano ~/.openviking/ov.conf

# Web Admin 配置
nano webadmin/.env
```

### 3. 启动服务

```bash
./scripts/install.sh start
```

### 4. 访问服务

- **Web Admin**: http://localhost:5173
- **登录凭据**: admin / changeme123 (默认，请修改)

## 功能模块

### 1. 登录认证
- 本地用户名密码验证
- 生成 API Key 与 OpenViking 服务器通信
- Token 存储在 localStorage

### 2. 资源管理
- 列出所有资源
- 添加新资源
- 删除资源
- 查看资源详情（L0/L1/L2 内容）

### 3. 会话管理
- 列出所有会话
- 查看会话详情和消息历史
- 添加新消息
- 提交会话
- 删除会话

### 4. 文件浏览器
- 浏览 viking://文件系统
- 查看目录树
- 读取文件内容（L0/L1/L2）
- 创建目录

### 5. 语义搜索
- 语义搜索
- 内容搜索
- 模式匹配

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2.0 | UI 框架 |
| TypeScript | 5.2.2 | 类型安全 |
| Vite | 5.0.8 | 构建工具 |
| React Router | 6.20.0 | 路由 |
| Axios | 1.6.0 | HTTP 客户端 |
| Tailwind CSS | 3.3.6 | 样式 |

## API 接口

Web Admin 使用现有的 OpenViking API 接口：

| 功能 | API 端点 |
|------|---------|
| 资源管理 | `/api/v1/fs/ls`, `/api/v1/resources`, `/api/v1/fs` |
| 会话管理 | `/api/v1/sessions`, `/api/v1/sessions/{id}` |
| 文件系统 | `/api/v1/fs/tree`, `/api/v1/fs/stat`, `/api/v1/fs/mkdir` |
| 内容读取 | `/api/v1/content/read`, `/api/v1/content/abstract`, `/api/v1/content/overview` |
| 搜索 | `/api/v1/search/find`, `/api/v1/search/grep` |

## 配置说明

### OpenViking 配置 (`~/.openviking/ov.conf`)

```json
{
  "storage": {
    "workspace": "~/.openviking/data"
  },
  "embedding": {
    "dense": {
      "provider": "volcengine",
      "api_key": "your-api-key",
      "model": "doubao-embedding-vision-250615",
      "dimension": 1024
    }
  },
  "vlm": {
    "provider": "volcengine",
    "api_key": "your-api-key",
    "model": "doubao-seed-2-0-pro-260215"
  }
}
```

### Web Admin 配置 (`webadmin/.env`)

```env
VITE_API_BASE_URL=http://localhost:1933/api/v1
VITE_ADMIN_USERNAME=admin
VITE_ADMIN_PASSWORD=changeme123
```

## 安装脚本命令

```bash
# 安装所有依赖并构建
./scripts/install.sh install

# 仅安装依赖
./scripts/install.sh deps

# 仅构建 Web Admin
./scripts/install.sh build

# 启动服务
./scripts/install.sh start

# 停止服务
./scripts/install.sh stop

# 重启服务
./scripts/install.sh restart

# 查看状态
./scripts/install.sh status

# 生成配置
./scripts/install.sh config

# 清理
./scripts/install.sh clean
```

## 日志文件

| 文件 | 说明 |
|------|------|
| `~/.openviking/server.log` | OpenViking 服务器日志 |
| `~/.openviking/webadmin.log` | Web Admin 日志 |

## 卸载

```bash
# 停止服务
./scripts/install.sh stop

# 清理文件
./scripts/install.sh clean

# 删除配置
rm -rf ~/.openviking
```

## 注意事项

1. **OpenViking 服务器必须先启动**：Web Admin 依赖 OpenViking 的 API
2. **密码本地验证**：密码不会发送到服务器，只在本地验证
3. **API Key 生成**：验证通过后自动生成 UUID 作为 API Key
4. **CORS 配置**：开发环境使用 Vite 代理，生产环境需配置服务器 CORS

## 相关文档

- [设计文档](./webadmin_design.md)
- [安装指南](./scripts/README.md)
- [项目说明](./README.md)
