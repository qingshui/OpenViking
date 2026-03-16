# OpenViking Web Admin

完全独立的 Web 管理界面，通过 HTTP API 与 OpenViking 服务器通信。

## 项目结构

```
webadmin/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── .env
├── public/
│   └── favicon.ico
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── components/
    │   ├── common/
    │   │   ├── Layout.tsx
    │   │   ├── Sidebar.tsx
    │   │   ├── Topbar.tsx
    │   │   └── LoadingSpinner.tsx
    │   ├── resources/
    │   │   ├── ResourceList.tsx
    │   │   └── ResourceForm.tsx
    │   ├── sessions/
    │   │   ├── SessionList.tsx
    │   │   └── SessionDetail.tsx
    │   ├── filesystem/
    │   │   ├── FileExplorer.tsx
    │   │   └── BreadcrumbNav.tsx
    │   └── search/
    │       └── SearchBar.tsx
    ├── contexts/
    │   └── AuthContext.tsx
    ├── services/
    │   ├── api.ts
    │   ├── resources.ts
    │   ├── sessions.ts
    │   ├── filesystem.ts
    │   └── search.ts
    ├── types/
    │   └── api.ts
    ├── hooks/
    │   └── useAuth.ts
    └── pages/
        ├── Login.tsx
        ├── Dashboard.tsx
        ├── ResourceManagement.tsx
        ├── SessionManagement.tsx
        ├── FileExplorer.tsx
        └── SemanticSearch.tsx
```

## 快速开始

### 1. 安装依赖

```bash
cd webadmin
npm install
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
VITE_API_BASE_URL=http://localhost:1933/api/v1
VITE_ADMIN_USERNAME=admin
VITE_ADMIN_PASSWORD=your_password_here
```

### 3. 运行开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 4. 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录。

## 功能模块

### 1. 登录认证

- 用户名密码在本地验证
- 验证通过后生成 API Key 存储在 localStorage
- 所有后续请求通过 `X-API-Key`  header 与 OpenViking 服务器通信

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

### 4. 文件系统浏览

- 浏览 viking://文件系统
- 查看目录树
- 读取文件内容
- 创建目录

### 5. 语义搜索

- 语义搜索
- 内容搜索
- 模式匹配

## API 接口映射

| 功能 | OpenViking API |
|------|---------------|
| 列出资源 | `GET /api/v1/fs/ls` |
| 添加资源 | `POST /api/v1/resources` |
| 删除资源 | `DELETE /api/v1/fs` |
| 读取内容 | `GET /api/v1/content/read` |
| 读取 L0 | `GET /api/v1/content/abstract` |
| 读取 L1 | `GET /api/v1/content/overview` |
| 创建会话 | `POST /api/v1/sessions` |
| 列出会话 | `GET /api/v1/sessions` |
| 会话详情 | `GET /api/v1/sessions/{id}` |
| 添加消息 | `POST /api/v1/sessions/{id}/messages` |
| 提交会话 | `POST /api/v1/sessions/{id}/commit` |
| 删除会话 | `DELETE /api/v1/sessions/{id}` |
| 列出目录 | `GET /api/v1/fs/ls` |
| 目录树 | `GET /api/v1/fs/tree` |
| 创建目录 | `POST /api/v1/fs/mkdir` |
| 语义搜索 | `POST /api/v1/search/find` |
| 内容搜索 | `POST /api/v1/search/grep` |

## 技术栈

- React 18 + TypeScript
- Vite
- Axios
- React Router
- Tailwind CSS

## 注意事项

- 这是一个完全独立的项目，不修改任何 OpenViking 原有代码
- 所有认证逻辑在前端完成
- 通过 HTTP API 与现有 OpenViking 服务器通信
- 需要 OpenViking 服务器运行在 localhost:1933（或配置的其他地址）
