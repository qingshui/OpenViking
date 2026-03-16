# OpenViking Web Admin 安装指南

## 概述

本目录提供 OpenViking Web Admin 的编译安装脚本，**不依赖 Docker**，直接在本机环境编译安装。

## 系统要求

### 必需软件

| 软件 | 最低版本 | 说明 |
|------|---------|------|
| Git | 2.0+ | 版本控制 |
| Python | 3.10+ | Python 解释器 |
| Node.js | 18+ | JavaScript 运行时 |
| npm/yarn/pnpm | 任意 | 包管理器 |

### 可选软件

| 软件 | 说明 |
|------|------|
| uv | 推荐的 Python 包管理器（更快） |
| MongoDB | 向量数据库（OpenViking 依赖） |

## 快速开始

### 1. 克隆项目

```bash
cd /Users/humingqing/baidu/work/paddle-serving/baidu/third/OpenViking
```

### 2. 运行安装脚本

```bash
# 完整安装（依赖 + 构建）
chmod +x scripts/install.sh
./scripts/install.sh install

# 或者使用简写
./scripts/install.sh
```

### 3. 配置服务

安装完成后，需要编辑配置文件：

```bash
# OpenViking 服务器配置
nano ~/.openviking/ov.conf

# Web Admin 配置
nano webadmin/.env
```

### 4. 启动服务

```bash
# 启动所有服务
./scripts/install.sh start

# 或者单独启动
./scripts/install.sh start openviking
./scripts/install.sh start webadmin
```

### 5. 访问服务

- **OpenViking API**: http://localhost:1933
- **Web Admin**: http://localhost:5173

## 安装脚本命令

```bash
# 查看帮助
./scripts/install.sh help

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

# 查看服务状态
./scripts/install.sh status

# 生成配置文件
./scripts/install.sh config

# 清理构建产物
./scripts/install.sh clean
```

## 配置说明

### OpenViking 服务器配置 (`~/.openviking/ov.conf`)

```json
{
  "storage": {
    "workspace": "/Users/yourname/.openviking/data",
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
      "api_key": "your-api-key-here",
      "api_base": "https://ark.cn-beijing.volces.com/api/v3",
      "model": "doubao-embedding-vision-250615",
      "dimension": 1024,
      "max_concurrent": 10
    }
  },
  "vlm": {
    "provider": "volcengine",
    "api_key": "your-api-key-here",
    "api_base": "https://ark.cn-beijing.volces.com/api/v3",
    "model": "doubao-seed-2-0-pro-260215",
    "max_concurrent": 100
  }
}
```

**重要配置项：**

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `storage.workspace` | 数据存储路径 | `~/.openviking/data` |
| `embedding.dense.api_key` | 向量模型 API Key | 需配置 |
| `embedding.dense.model` | 向量模型名称 | 需配置 |
| `vlm.api_key` | VLM 模型 API Key | 需配置 |
| `vlm.model` | VLM 模型名称 | 需配置 |

### Web Admin 配置 (`webadmin/.env`)

```env
# OpenViking Server API URL
VITE_API_BASE_URL=http://localhost:1933/api/v1

# Admin credentials (stored locally, not sent to server)
VITE_ADMIN_USERNAME=admin
VITE_ADMIN_PASSWORD=changeme123
```

**重要配置项：**

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `VITE_API_BASE_URL` | OpenViking API 地址 | `http://localhost:1933/api/v1` |
| `VITE_ADMIN_USERNAME` | 管理用户名 | `admin` |
| `VITE_ADMIN_PASSWORD` | 管理密码 | `changeme123` |

## 手动安装（不推荐）

如果脚本安装失败，可以手动安装：

### 1. 安装 Python 依赖

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装 OpenViking
pip install -e . --force-reinstall
```

### 2. 安装 Node.js 依赖

```bash
cd webadmin
npm install
```

### 3. 生成配置文件

```bash
# OpenViking 配置
mkdir -p ~/.openviking
cat > ~/.openviking/ov.conf << 'EOF'
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
EOF

# Web Admin 配置
cp webadmin/.env.example webadmin/.env
```

### 4. 构建 Web Admin

```bash
cd webadmin
npm run build
```

### 5. 启动服务

```bash
# 设置环境变量
export OPENVIKING_CONFIG_FILE=~/.openviking/ov.conf

# 启动 OpenViking 服务器
nohup openviking-server > ~/.openviking/server.log 2>&1 &

# 启动 Web Admin
cd webadmin
nohup npm run dev > ~/.openviking/webadmin.log 2>&1 &
```

## 常见问题

### 1. 依赖安装失败

**问题**: `pip install` 失败

**解决**:
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -e . --force-reinstall -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. Node.js 依赖安装失败

**问题**: `npm install` 失败

**解决**:
```bash
# 使用国内镜像
npm config set registry https://registry.npmmirror.com
npm install

# 或者使用 yarn
yarn install
```

### 3. MongoDB 连接失败

**问题**: OpenViking 启动时报 MongoDB 连接错误

**解决**:
```bash
# 启动 MongoDB
brew services start mongodb-community  # macOS
sudo systemctl start mongod            # Linux

# 检查 MongoDB 是否运行
mongosh --eval "db.adminCommand('ping')"
```

### 4. 端口被占用

**问题**: 端口 1933 或 5173 已被占用

**解决**:
```bash
# 查看端口占用
lsof -i :1933
lsof -i :5173

# 杀死进程
kill -9 <PID>

# 或者修改配置使用其他端口
# 修改 webadmin/.env 中的 VITE_API_BASE_URL
# 修改 openviking/server/config.py 中的端口配置
```

### 5. Web Admin 无法访问

**问题**: 访问 http://localhost:5173 无响应

**解决**:
```bash
# 检查 Web Admin 是否运行
ps aux | grep "node.*vite"

# 查看日志
cat ~/.openviking/webadmin.log

# 重启 Web Admin
./scripts/install.sh restart
```

## 日志文件

| 文件 | 说明 |
|------|------|
| `~/.openviking/server.log` | OpenViking 服务器日志 |
| `~/.openviking/webadmin.log` | Web Admin 日志 |
| `~/.openviking/server.pid` | OpenViking 服务器 PID |
| `~/.openviking/webadmin.pid` | Web Admin PID |

## 卸载

```bash
# 停止服务
./scripts/install.sh stop

# 清理文件
./scripts/install.sh clean

# 删除配置文件
rm -rf ~/.openviking

# 删除虚拟环境
rm -rf .venv
```

## 技术支持

- GitHub Issues: https://github.com/volcengine/OpenViking/issues
- 文档：https://openviking.ai/docs
