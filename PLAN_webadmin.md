# OpenViking Web Admin 实现计划

## 概述

创建完全独立的 Web 管理界面，通过 HTTP API 与现有 OpenViking 服务器通信，**不修改任何现有代码**。

## 技术架构

### 前端
- React 18 + TypeScript
- Vite 构建工具
- Axios HTTP 客户端
- React Router 路由
- React Context 状态管理
- Tailwind CSS 样式

### 后端
- **复用现有 OpenViking 服务器**
- 通过 HTTP API 调用现有接口
- 可选：轻量级 Node.js 代理服务器（可选，用于处理 CORS）

---

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
    │   │   ├── LoadingSpinner.tsx
    │   │   └── Modal.tsx
    │   ├── resources/
    │   │   ├── ResourceList.tsx
    │   │   ├── ResourceForm.tsx
    │   │   └── ResourceCard.tsx
    │   ├── sessions/
    │   │   ├── SessionList.tsx
    │   │   ├── SessionDetail.tsx
    │   │   └── MessageList.tsx
    │   ├── filesystem/
    │   │   ├── FileExplorer.tsx
    │   │   ├── FileTree.tsx
    │   │   └── BreadcrumbNav.tsx
    │   └── search/
    │       ├── SearchBar.tsx
    │       └── SearchResult.tsx
    ├── contexts/
    │   ├── AuthContext.tsx
    │   └── ApiContext.tsx
    ├── services/
    │   ├── api.ts
    │   ├── resources.ts
    │   ├── sessions.ts
    │   ├── filesystem.ts
    │   └── search.ts
    ├── types/
    │   ├── api.ts
    │   ├── resource.ts
    │   ├── session.ts
    │   └── filesystem.ts
    ├── hooks/
    │   ├── useAuth.ts
    │   ├── useFileSystem.ts
    │   └── useSearch.ts
    └── pages/
        ├── Login.tsx
        ├── Dashboard.tsx
        ├── ResourceManagement.tsx
        ├── SessionManagement.tsx
        ├── FileExplorer.tsx
        └── SemanticSearch.tsx
```

---

## 现有 API 接口映射

### 认证（简易密码，本地存储）

**前端本地实现**（不修改后端）：
- 用户名密码在本地验证（可配置）
- Token 存储在 localStorage
- 使用现有的 `X-API-Key`  header

### 资源管理

| 功能 | 现有 API 接口 | 说明 |
|------|--------------|------|
| 列出资源 | `GET /api/v1/fs/ls` | 查询参数：uri, recursive, limit |
| 添加资源 | `POST /api/v1/resources` | 请求体：path, parent, reason 等 |
| 删除资源 | `DELETE /api/v1/fs` | 查询参数：uri, recursive |
| 读取内容 | `GET /api/v1/content/read` | 查询参数：uri, offset, limit |
| 读取 L0 | `GET /api/v1/content/abstract` | 查询参数：uri |
| 读取 L1 | `GET /api/v1/content/overview` | 查询参数：uri |

### 会话管理

| 功能 | 现有 API 接口 | 说明 |
|------|--------------|------|
| 创建会话 | `POST /api/v1/sessions` | - |
| 列出会话 | `GET /api/v1/sessions` | - |
| 会话详情 | `GET /api/v1/sessions/{session_id}` | - |
| 添加消息 | `POST /api/v1/sessions/{session_id}/messages` | 请求体：role, content, parts |
| 提交会话 | `POST /api/v1/sessions/{session_id}/commit` | 查询参数：wait |
| 删除会话 | `DELETE /api/v1/sessions/{session_id}` | - |

### 文件系统

| 功能 | 现有 API 接口 | 说明 |
|------|--------------|------|
| 列出目录 | `GET /api/v1/fs/ls` | 查询参数：uri, recursive, simple |
| 目录树 | `GET /api/v1/fs/tree` | 查询参数：uri, level_limit |
| 资源状态 | `GET /api/v1/fs/stat` | 查询参数：uri |
| 创建目录 | `POST /api/v1/fs/mkdir` | 请求体：uri |
| 移动资源 | `POST /api/v1/fs/mv` | 请求体：from_uri, to_uri |

### 搜索

| 功能 | 现有 API 接口 | 说明 |
|------|--------------|------|
| 语义搜索 | `POST /api/v1/search/find` | 请求体：query, target_uri, limit |
| 带会话搜索 | `POST /api/v1/search/search` | 请求体：query, session_id |
| 内容搜索 | `POST /api/v1/search/grep` | 请求体：uri, pattern |
| 模式匹配 | `POST /api/v1/search/glob` | 请求体：pattern, uri |

---

## 实现步骤

### 第一步：创建前端项目

```bash
# 创建项目目录
mkdir -p webadmin/src/{components/{common,resources,sessions,filesystem,search},contexts,services,types,hooks,pages}

# 初始化 package.json
cd webadmin
npm init -y

# 安装依赖
npm install react react-dom react-router-dom axios
npm install -D typescript @types/react @types/react-dom @types/react-dom @vitejs/plugin-react tailwindcss postcss autoprefixer
```

### 第二步：配置项目

#### vite.config.ts

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:1933',
        changeOrigin: true
      }
    }
  }
})
```

#### .env

```env
VITE_API_BASE_URL=http://localhost:1933/api/v1
VITE_CONSOLE_BASE_URL=http://localhost:1933/console/api/v1
```

### 第三步：核心服务实现

#### src/services/api.ts

```typescript
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL

export const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加 Token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('ov_api_key')
  if (token) {
    config.headers['X-API-Key'] = token
  }
  return config
})

// 响应拦截器 - Token 过期处理
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

export default apiClient
```

#### src/services/resources.ts

```typescript
import apiClient from './api'

export interface ResourceInfo {
  uri: string
  name: string
  type: string
  size: number
  created_at: string
  updated_at: string
}

export const resourceService = {
  // 列出资源
  list: async (uri: string = 'viking://resources/', limit: number = 50) => {
    const response = await apiClient.get('/fs/ls', {
      params: { uri, simple: false, recursive: false, limit }
    })
    return response.data
  },

  // 添加资源
  add: async (path: string, parent: string = 'viking://resources/', reason: string = '') => {
    const response = await apiClient.post('/resources', {
      path,
      parent,
      reason,
      wait: true
    })
    return response.data
  },

  // 删除资源
  delete: async (uri: string, recursive: boolean = false) => {
    await apiClient.delete('/fs', {
      params: { uri, recursive }
    })
  },

  // 读取内容
  read: async (uri: string, offset: number = 0, limit: number = -1) => {
    const response = await apiClient.get('/content/read', {
      params: { uri, offset, limit }
    })
    return response.data
  },

  // 读取 L0 摘要
  getAbstract: async (uri: string) => {
    const response = await apiClient.get('/content/abstract', {
      params: { uri }
    })
    return response.data
  },

  // 读取 L1 概览
  getOverview: async (uri: string) => {
    const response = await apiClient.get('/content/overview', {
      params: { uri }
    })
    return response.data
  }
}
```

#### src/services/sessions.ts

```typescript
import apiClient from './api'

export const sessionService = {
  // 创建会话
  create: async () => {
    const response = await apiClient.post('/sessions')
    return response.data
  },

  // 列出会话
  list: async () => {
    const response = await apiClient.get('/sessions')
    return response.data
  },

  // 获取会话详情
  get: async (session_id: string) => {
    const response = await apiClient.get(`/sessions/${session_id}`)
    return response.data
  },

  // 添加消息
  addMessage: async (session_id: string, role: string, content: string) => {
    const response = await apiClient.post(`/sessions/${session_id}/messages`, {
      role,
      content
    })
    return response.data
  },

  // 提交会话
  commit: async (session_id: string, wait: boolean = true) => {
    const response = await apiClient.post(`/sessions/${session_id}/commit`, null, {
      params: { wait }
    })
    return response.data
  },

  // 删除会话
  delete: async (session_id: string) => {
    await apiClient.delete(`/sessions/${session_id}`)
  }
}
```

#### src/services/filesystem.ts

```typescript
import apiClient from './api'

export interface FileNode {
  uri: string
  name: string
  type: 'file' | 'directory'
  children?: FileNode[]
}

export const filesystemService = {
  // 列出目录
  list: async (uri: string, recursive: boolean = false) => {
    const response = await apiClient.get('/fs/ls', {
      params: { uri, recursive }
    })
    return response.data
  },

  // 获取目录树
  tree: async (uri: string = 'viking://', level_limit: number = 3) => {
    const response = await apiClient.get('/fs/tree', {
      params: { uri, level_limit }
    })
    return response.data
  },

  // 获取资源状态
  stat: async (uri: string) => {
    const response = await apiClient.get('/fs/stat', {
      params: { uri }
    })
    return response.data
  },

  // 创建目录
  mkdir: async (uri: string) => {
    const response = await apiClient.post('/fs/mkdir', { uri })
    return response.data
  },

  // 移动资源
  mv: async (from_uri: string, to_uri: string) => {
    const response = await apiClient.post('/fs/mv', {
      from_uri,
      to_uri
    })
    return response.data
  }
}
```

#### src/services/search.ts

```typescript
import apiClient from './api'

export interface SearchResult {
  uri: string
  context_type: string
  level: number
  abstract: string
  score: number
}

export const searchService = {
  // 语义搜索
  find: async (query: string, limit: number = 10, target_uri?: string) => {
    const response = await apiClient.post('/search/find', {
      query,
      limit,
      target_uri
    })
    return response.data
  },

  // 带会话搜索
  search: async (query: string, session_id: string, limit: number = 10) => {
    const response = await apiClient.post('/search/search', {
      query,
      session_id,
      limit
    })
    return response.data
  },

  // 内容搜索
  grep: async (uri: string, pattern: string) => {
    const response = await apiClient.post('/search/grep', {
      uri,
      pattern
    })
    return response.data
  },

  // 模式匹配
  glob: async (pattern: string, uri: string = 'viking://') => {
    const response = await apiClient.post('/search/glob', {
      pattern,
      uri
    })
    return response.data
  }
}
```

### 第四步：认证上下文

#### src/contexts/AuthContext.tsx

```typescript
import React, { createContext, useContext, useState, useEffect } from 'react'

interface AuthContextType {
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('ov_api_key')
    setIsAuthenticated(!!token)
  }, [])

  const login = async (username: string, password: string) => {
    // 简易密码验证（本地配置）
    const ADMIN_USER = import.meta.env.VITE_ADMIN_USERNAME || 'admin'
    const ADMIN_PASS = import.meta.env.VITE_ADMIN_PASSWORD || ''

    if (username === ADMIN_USER && password === ADMIN_PASS) {
      // 生成或获取 API Key（可以是固定值或随机生成）
      const apiKey = localStorage.getItem('ov_api_key') || crypto.randomUUID()
      localStorage.setItem('ov_api_key', apiKey)
      setIsAuthenticated(true)
    } else {
      throw new Error('Invalid username or password')
    }
  }

  const logout = () => {
    localStorage.removeItem('ov_api_key')
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
```

### 第五步：页面组件

#### src/pages/Login.tsx

```typescript
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const Login: React.FC = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await login(username, password)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center">OpenViking Admin</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-2 mb-4 border rounded"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 mb-4 border rounded"
          />
          {error && <div className="text-red-500 mb-4">{error}</div>}
          <button
            type="submit"
            className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
          >
            Login
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login
```

#### src/pages/ResourceManagement.tsx

```typescript
import React, { useState, useEffect } from 'react'
import { resourceService } from '../services/resources'

const ResourceManagement: React.FC = () => {
  const [resources, setResources] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadResources()
  }, [])

  const loadResources = async () => {
    try {
      const data = await resourceService.list()
      setResources(data)
    } catch (error) {
      console.error('Failed to load resources:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">资源管理</h1>
      {loading ? (
        <div>加载中...</div>
      ) : (
        <table className="min-w-full border">
          <thead>
            <tr className="bg-gray-100">
              <th className="border px-4 py-2">URI</th>
              <th className="border px-4 py-2">名称</th>
              <th className="border px-4 py-2">类型</th>
              <th className="border px-4 py-2">操作</th>
            </tr>
          </thead>
          <tbody>
            {resources.map((res) => (
              <tr key={res.uri}>
                <td className="border px-4 py-2">{res.uri}</td>
                <td className="border px-4 py-2">{res.name}</td>
                <td className="border px-4 py-2">{res.type}</td>
                <td className="border px-4 py-2">
                  <button className="text-blue-500">查看</button>
                  <button className="text-red-500 ml-2">删除</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default ResourceManagement
```

#### src/pages/FileExplorer.tsx

```typescript
import React, { useState } from 'react'
import { filesystemService } from '../services/filesystem'

const FileExplorer: React.FC = () => {
  const [currentUri, setCurrentUri] = useState('viking://resources/')
  const [files, setFiles] = useState<any[]>([])

  const loadFiles = async () => {
    const data = await filesystemService.list(currentUri)
    setFiles(data)
  }

  return (
    <div className="p-6">
      <div className="mb-4">
        <input
          type="text"
          value={currentUri}
          onChange={(e) => setCurrentUri(e.target.value)}
          className="border px-4 py-2 w-full"
        />
        <button onClick={loadFiles} className="ml-2 bg-blue-500 text-white px-4 py-2 rounded">
          加载
        </button>
      </div>
      <div className="grid grid-cols-3 gap-4">
        {files.map((file) => (
          <div key={file.uri} className="border p-4 rounded">
            <div className="font-bold">{file.name}</div>
            <div className="text-sm text-gray-600">{file.uri}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default FileExplorer
```

#### src/pages/SemanticSearch.tsx

```typescript
import React, { useState } from 'react'
import { searchService } from '../services/search'

const SemanticSearch: React.FC = () => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    try {
      const data = await searchService.find(query)
      setResults(data)
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">语义搜索</h1>
      <div className="flex gap-4 mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="输入搜索关键词..."
          className="border px-4 py-2 flex-1"
        />
        <button
          onClick={handleSearch}
          className="bg-blue-500 text-white px-6 py-2 rounded"
        >
          搜索
        </button>
      </div>
      {loading && <div>搜索中...</div>}
      <div className="space-y-4">
        {results.map((result, index) => (
          <div key={index} className="border p-4 rounded">
            <div className="font-bold">{result.uri}</div>
            <div className="text-sm text-gray-600 mb-2">{result.abstract}</div>
            <div className="text-xs text-gray-400">得分：{result.score}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default SemanticSearch
```

### 第六步：主应用

#### src/App.tsx

```typescript
import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Login from './pages/Login'
import ResourceManagement from './pages/ResourceManagement'
import SessionManagement from './pages/SessionManagement'
import FileExplorer from './pages/FileExplorer'
import SemanticSearch from './pages/SemanticSearch'
import Layout from './components/common/Layout'

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

const AppContent: React.FC = () => {
  return (
    <Layout>
      <Routes>
        <Route path="/resources" element={<ProtectedRoute><ResourceManagement /></ProtectedRoute>} />
        <Route path="/sessions" element={<ProtectedRoute><SessionManagement /></ProtectedRoute>} />
        <Route path="/filesystem" element={<ProtectedRoute><FileExplorer /></ProtectedRoute>} />
        <Route path="/search" element={<ProtectedRoute><SemanticSearch /></ProtectedRoute>} />
        <Route path="/" element={<ProtectedRoute><div>欢迎使用 OpenViking Admin</div></ProtectedRoute>} />
      </Routes>
    </Layout>
  )
}

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*" element={<AppContent />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
```

---

## 部署步骤

### 1. 配置环境变量

```bash
# .env
VITE_API_BASE_URL=http://localhost:1933/api/v1
VITE_ADMIN_USERNAME=admin
VITE_ADMIN_PASSWORD=your_password
```

### 2. 构建前端

```bash
cd webadmin
npm install
npm run build
```

### 3. 运行开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 4. 生产部署

将 `dist` 目录部署到静态文件服务器，或配置 Nginx 反向代理：

```nginx
server {
    listen 80;
    server_name openviking.example.com;

    location / {
        root /path/to/webadmin/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:1933;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 关键特性

1. **完全独立** - 不修改任何现有 OpenViking 代码
2. **简单认证** - 本地用户名密码验证，生成 API Key 与后端通信
3. **完整功能** - 资源管理、会话管理、文件浏览、语义搜索
4. **现代化 UI** - React + Tailwind CSS 响应式设计
5. **类型安全** - TypeScript 提供类型检查

---

## 文件清单

### 后端（无需修改）
- 复用现有 OpenViking 服务器的所有 API 接口

### 前端（新建）
- `/webadmin/package.json` - 项目配置
- `/webadmin/vite.config.ts` - Vite 配置
- `/webadmin/.env` - 环境变量
- `/webadmin/src/main.tsx` - 入口文件
- `/webadmin/src/App.tsx` - 主应用
- `/webadmin/src/contexts/AuthContext.tsx` - 认证上下文
- `/webadmin/src/services/api.ts` - API 客户端
- `/webadmin/src/services/resources.ts` - 资源服务
- `/webadmin/src/services/sessions.ts` - 会话服务
- `/webadmin/src/services/filesystem.ts` - 文件系统服务
- `/webadmin/src/services/search.ts` - 搜索服务
- `/webadmin/src/pages/Login.tsx` - 登录页
- `/webadmin/src/pages/ResourceManagement.tsx` - 资源管理
- `/webadmin/src/pages/SessionManagement.tsx` - 会话管理
- `/webadmin/src/pages/FileExplorer.tsx` - 文件浏览
- `/webadmin/src/pages/SemanticSearch.tsx` - 语义搜索
- `/webadmin/src/components/common/Layout.tsx` - 布局组件
- `/webadmin/tsconfig.json` - TypeScript 配置
- `/webadmin/tailwind.config.js` - Tailwind 配置
