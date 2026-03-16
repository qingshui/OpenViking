#!/bin/bash
#
# OpenViking Web Admin 安装脚本
# 不依赖 Docker，直接编译安装
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 检查系统类型
check_system() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        SYSTEM="macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        SYSTEM="linux"
    else
        log_warn "未知系统类型：$OSTYPE"
        SYSTEM="unknown"
    fi
    log_info "检测到系统：$SYSTEM"
}

# 检查并安装依赖
install_dependencies() {
    log_step "检查依赖..."

    # 检查基础工具
    check_command git
    check_command curl

    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        check_command python
    fi

    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        if [[ "$SYSTEM" == "linux" ]]; then
            log_info "在 Ubuntu/Debian 上安装 Node.js:"
            log_info "  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -"
            log_info "  sudo apt-get install -y nodejs"
        elif [[ "$SYSTEM" == "macos" ]]; then
            log_info "在 macOS 上安装 Node.js:"
            log_info "  brew install node"
        fi
        exit 1
    fi

    # 检查 uv (推荐) 或 pip
    if ! command -v uv &> /dev/null; then
        log_warn "uv 未安装，尝试使用 pip"
        if ! command -v pip &> /dev/null; then
            log_error "pip 未安装，请先安装 pip"
            exit 1
        fi
    fi

    log_info "依赖检查完成"
}

# 安装 Python 依赖
install_python_deps() {
    log_step "安装 Python 依赖..."

    local PYTHON_CMD="python3"
    if ! command -v python3 &> /dev/null; then
        PYTHON_CMD="python"
    fi

    log_info "使用当前 Python 环境：$PYTHON_CMD"

    # 检查 uv
    if command -v uv &> /dev/null; then
        log_info "使用 uv 安装依赖..."
        uv pip install -e . --force-reinstall
    else
        # 使用 pip 直接安装到当前环境
        $PYTHON_CMD -m pip install -e . --force-reinstall
    fi

    log_info "Python 依赖安装完成"
}

# 安装 Node.js 依赖
install_node_deps() {
    log_step "安装 Node.js 依赖..."

    cd webadmin

    # 检查 npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装"
        exit 1
    fi

    # 使用 npm 或 yarn 或 pnpm
    if command -v yarn &> /dev/null; then
        log_info "使用 yarn 安装依赖..."
        yarn install
    elif command -v pnpm &> /dev/null; then
        log_info "使用 pnpm 安装依赖..."
        pnpm install
    else
        log_info "使用 npm 安装依赖..."
        npm install
    fi

    cd ..
    log_info "Node.js 依赖安装完成"
}

# 生成配置文件
generate_config() {
    log_step "生成配置文件..."

    # 创建配置目录
    local CONFIG_DIR="$HOME/.openviking"
    mkdir -p "$CONFIG_DIR"

    # 检查是否已有配置
    if [[ -f "$CONFIG_DIR/ov.conf" ]]; then
        log_warn "配置文件已存在：$CONFIG_DIR/ov.conf"
        log_info "跳过配置生成，如需重新生成请先删除现有配置"
    else
        # 生成默认配置
        cat > "$CONFIG_DIR/ov.conf" << 'EOF'
{
  "server": {
    "host": "0.0.0.0",
    "port": 1933,
    "root_api_key": "your-root-api-key-here"
  },
  "storage": {
    "workspace": "$HOME/.openviking/data",
    "agfs": {
      "port": 1833,
      "log_level": "warn",
      "backend": "local",
      "timeout": 10,
      "retry_times": 3
    },
    "vectordb": {
      "name": "context",
      "backend": "local",
      "project": "default"
    }
  },
  "log": {
    "level": "INFO",
    "output": "stdout"
  },
  "embedding": {
    "max_concurrent": 10,
    "dense": {
      "provider": "openai_compatible",
      "api_key": "your-api-key-here",
      "api_base": "http://your-embedding-server:port",
      "model": "your-embedding-model",
      "dimension": 1024
    }
  },
  "vlm": {
    "provider": "openai",
    "api_key": "your-api-key-here",
    "api_base": "http://your-llm-server:port",
    "model": "your-llm-model"
  }
}
EOF

        # 替换 HOME 路径
        sed -i.bak "s|\$HOME|$HOME|g" "$CONFIG_DIR/ov.conf" 2>/dev/null || \
        sed -i.bak "s|\$HOME|$HOME|g" "$CONFIG_DIR/ov.conf"

        # 删除备份文件
        rm -f "$CONFIG_DIR/ov.conf.bak"

        log_info "配置文件已生成：$CONFIG_DIR/ov.conf"
        log_warn "请编辑配置文件，设置正确的 API Key 和其他参数"
    fi

    # 生成 Web Admin 配置
    if [[ ! -f "webadmin/.env" ]]; then
        cp webadmin/.env.example webadmin/.env
        log_info "Web Admin 配置文件已生成：webadmin/.env"
        log_warn "请编辑 webadmin/.env，设置正确的管理密码"
    fi
}

# 构建 Web Admin
build_webadmin() {
    log_step "构建 Web Admin..."

    cd webadmin

    # 检查是否有构建产物
    if [[ -d "dist" ]]; then
        log_warn "构建产物已存在，跳过构建"
        read -p "是否重新构建？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            npm run build
        fi
    else
        npm run build
    fi

    cd ..
    log_info "Web Admin 构建完成"
}

# 启动 AGFS 服务
start_agfs() {
    log_step "启动 AGFS 服务..."

    # 检查 AGFS 二进制文件（优先使用部署目录，其次使用本地）
    local AGFS_BIN="$HOME/.openviking/agfs/agfs-server"
    if [[ ! -f "$AGFS_BIN" ]]; then
        AGFS_BIN="openviking/bin/agfs-server"
        if [[ ! -f "$AGFS_BIN" ]]; then
            log_warn "AGFS 服务器二进制文件不存在，请先生成配置文件并安装依赖"
            return 1
        fi
    fi

    # 检查 AGFS 配置文件（优先使用部署目录，其次使用本地）
    local AGFS_CONFIG="$HOME/.openviking/agfs/config.yaml"
    if [[ ! -f "$AGFS_CONFIG" ]]; then
        AGFS_CONFIG="third_party/agfs/agfs-server/config.yaml"
        if [[ ! -f "$AGFS_CONFIG" ]]; then
            log_warn "AGFS 配置文件不存在：$AGFS_CONFIG"
            return 1
        fi
    fi

    # 检查是否已在运行
    if pgrep -f "agfs-server" > /dev/null; then
        log_warn "AGFS 服务已在运行"
        read -p "是否重启 AGFS 服务？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pkill -f "agfs-server"
            sleep 2
        else
            log_info "跳过重启"
            return 0
        fi
    fi

    # 启动 AGFS 服务器
    log_info "启动 AGFS 服务器..."
    mkdir -p "$HOME/.openviking/log"
    nohup "$AGFS_BIN" -addr :1833 -c "$AGFS_CONFIG" > "$HOME/.openviking/log/agfs.log" 2>&1 &
    AGFS_PID=$!
    echo $AGFS_PID > "$HOME/.openviking/agfs.pid"

    # 等待 AGFS 启动
    log_info "等待 AGFS 启动..."
    sleep 3

    # 检查 AGFS 状态
    if pgrep -f "agfs-server" > /dev/null; then
        log_info "AGFS 服务启动成功 (PID: $AGFS_PID)"
    else
        log_warn "AGFS 服务可能未完全启动，请检查日志：$HOME/.openviking/log/agfs.log"
    fi
}

# 启动服务
start_services() {
    log_step "启动服务..."

    # 设置环境变量
    export OPENVIKING_CONFIG_FILE="$HOME/.openviking/ov.conf"

    # 检查是否已在运行
    if pgrep -f "openviking-server" > /dev/null; then
        log_warn "OpenViking 服务器已在运行"
        read -p "是否重启服务器？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pkill -f "openviking-server"
            sleep 2
        else
            log_info "跳过重启"
        fi
    fi

    # 启动 AGFS 服务
    start_agfs

    # 启动 OpenViking 服务器
    log_info "启动 OpenViking 服务器..."
    nohup openviking-server > "$HOME/.openviking/server.log" 2>&1 &
    SERVER_PID=$!
    echo $SERVER_PID > "$HOME/.openviking/server.pid"

    # 等待服务器启动
    log_info "等待服务器启动..."
    sleep 5

    # 检查服务器状态
    if curl -s http://localhost:1933/health > /dev/null 2>&1; then
        log_info "OpenViking 服务器启动成功 (PID: $SERVER_PID)"
    else
        log_warn "服务器可能未完全启动，请检查日志：$HOME/.openviking/server.log"
    fi

    # 启动 Web Admin 前端
    log_info "启动 Web Admin 前端..."
    cd webadmin
    nohup npm run dev > "$HOME/.openviking/log/webadmin.log" 2>&1 &
    WEBADMIN_PID=$!
    echo $WEBADMIN_PID > "$HOME/.openviking/webadmin.pid"
    cd ..

    log_info "Web Admin 前端启动成功 (PID: $WEBADMIN_PID)"
}

# 显示状态
show_status() {
    log_step "服务状态:"

    echo ""
    echo "=== OpenViking 服务器 ==="
    if pgrep -f "openviking-server" > /dev/null; then
        echo "状态：运行中"
        local PID=$(pgrep -f "openviking-server" | head -1)
        echo "PID: $PID"
        echo "访问：http://localhost:1933"
    else
        echo "状态：未运行"
    fi

    echo ""
    echo "=== Web Admin ==="
    if pgrep -f "npm run dev" > /dev/null || pgrep -f "node.*vite" > /dev/null; then
        echo "状态：运行中"
        local PID=$(pgrep -f "node.*vite" | head -1)
        echo "PID: $PID"
        echo "访问：http://0.0.0.0:5173 (支持内网访问)"
    else
        echo "状态：未运行"
    fi

    echo ""
    echo "=== 日志文件 ==="
    echo "AGFS 日志：$HOME/.openviking/log/agfs.log"
    echo "服务器日志：$HOME/.openviking/server.log"
    echo "Web Admin 日志：$HOME/.openviking/log/webadmin.log"
}

# 停止 AGFS 服务
stop_agfs() {
    if [[ -f "$HOME/.openviking/agfs.pid" ]]; then
        local PID=$(cat "$HOME/.openviking/agfs.pid")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            log_info "停止 AGFS 服务 (PID: $PID)"
        fi
        rm -f "$HOME/.openviking/agfs.pid"
    else
        pkill -f "agfs-server"
        log_info "停止 AGFS 服务"
    fi
}

# 停止服务
stop_services() {
    log_step "停止服务..."

    # 停止 AGFS 服务
    stop_agfs

    # 停止 OpenViking 服务器
    if [[ -f "$HOME/.openviking/server.pid" ]]; then
        local PID=$(cat "$HOME/.openviking/server.pid")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            log_info "停止 OpenViking 服务器 (PID: $PID)"
        fi
        rm -f "$HOME/.openviking/server.pid"
    else
        pkill -f "openviking-server"
        log_info "停止 OpenViking 服务器"
    fi

    # 停止 Web Admin
    if [[ -f "$HOME/.openviking/webadmin.pid" ]]; then
        local PID=$(cat "$HOME/.openviking/webadmin.pid")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            log_info "停止 Web Admin (PID: $PID)"
        fi
        rm -f "$HOME/.openviking/webadmin.pid"
    else
        pkill -f "node.*vite"
        pkill -f "npm run dev"
        log_info "停止 Web Admin"
    fi

    log_info "所有服务已停止"
}

# 显示帮助
show_help() {
    echo "OpenViking Web Admin 安装脚本"
    echo ""
    echo "用法：$0 [命令]"
    echo ""
    echo "命令:"
    echo "  install     安装所有依赖并构建 (默认)"
    echo "  deps        仅安装依赖"
    echo "  build       仅构建 Web Admin"
    echo "  start       启动服务"
    echo "  stop        停止服务"
    echo "  status      显示服务状态"
    echo "  restart     重启服务"
    echo "  config      生成配置文件"
    echo "  clean       清理构建产物"
    echo "  help        显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 install    # 完整安装"
    echo "  $0 start      # 启动服务"
    echo "  $0 status     # 查看状态"
}

# 清理
clean() {
    log_step "清理..."

    # 清理 Python 虚拟环境
    if [[ -d ".venv" ]]; then
        rm -rf .venv
        log_info "清理 Python 虚拟环境"
    fi

    # 清理 Node 模块
    if [[ -d "webadmin/node_modules" ]]; then
        rm -rf webadmin/node_modules
        log_info "清理 Node 模块"
    fi

    # 清理构建产物
    if [[ -d "webadmin/dist" ]]; then
        rm -rf webadmin/dist
        log_info "清理构建产物"
    fi

    # 清理部署目录
    local CONFIG_DIR="$HOME/.openviking"
    if [[ -d "$CONFIG_DIR/log" ]]; then
        rm -rf "$CONFIG_DIR/log"
        log_info "清理日志目录"
    fi

    log_info "清理完成"
}

# 主函数
main() {
    local COMMAND="${1:-install}"

    case $COMMAND in
        install)
            check_system
            install_dependencies
            install_python_deps
            install_node_deps
            generate_config
            build_webadmin
            log_info "安装完成!"
            log_info ""
            log_info "下一步:"
            log_info "  1. 编辑配置文件 $HOME/.openviking/ov.conf"
            log_info "  2. 编辑配置文件 webadmin/.env"
            log_info "  3. 部署 AGFS: bash scripts/agfs-deploy.sh deploy"
            log_info "  4. 运行 $0 start 启动服务 (包括 AGFS)"
            log_info "  5. 访问 http://localhost:5173"
            ;;
        deps)
            check_system
            install_dependencies
            install_python_deps
            install_node_deps
            log_info "依赖安装完成"
            ;;
        build)
            install_node_deps
            build_webadmin
            log_info "构建完成"
            ;;
        start)
            start_services
            show_status
            ;;
        stop)
            stop_services
            ;;
        status)
            show_status
            ;;
        restart)
            stop_services
            sleep 2
            start_services
            ;;
        config)
            generate_config
            log_info "配置生成完成"
            ;;
        clean)
            clean
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令：$COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
