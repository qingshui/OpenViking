#!/bin/bash
#
# OpenViking Web Admin 部署脚本
# 将 Web Admin 前后端分离部署到 $HOME/.openviking/webadmin/目录
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

# 检查 Node.js 环境
check_node() {
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装，请先安装 Node.js 18+"
        exit 1
    fi
    log_info "Node.js 版本：$(node --version)"

    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装，请先安装 npm"
        exit 1
    fi
    log_info "npm 版本：$(npm --version)"
}

# 构建 Web Admin 前端
build_frontend() {
    log_step "构建 Web Admin 前端..."

    cd webadmin

    # 检查是否有 node_modules
    if [[ ! -d "node_modules" ]]; then
        log_info "安装前端依赖..."
        npm install
    fi

    # 构建生产版本
    log_info "构建前端..."
    npm run build

    cd - > /dev/null
    log_info "前端构建完成"
}

# 部署 Web Admin 服务
deploy_webadmin() {
    log_step "部署 Web Admin 到 $HOME/.openviking/webadmin/..."

    local CONFIG_DIR="$HOME/.openviking"
    local WEBADMIN_DIR="$CONFIG_DIR/webadmin"

    # 创建目录结构
    mkdir -p "$WEBADMIN_DIR/backend"
    mkdir -p "$WEBADMIN_DIR/dist"
    mkdir -p "$CONFIG_DIR/log"

    # 构建前端
    build_frontend

    # 复制前端构建产物
    log_info "复制前端构建产物..."
    cp -r webadmin/dist/* "$WEBADMIN_DIR/dist/"

    # 复制前端 package.json 和 node_modules
    log_info "复制前端依赖..."
    cp webadmin/package.json "$WEBADMIN_DIR/"
    if [[ -d "webadmin/node_modules" ]]; then
        cp -r webadmin/node_modules "$WEBADMIN_DIR/"
    fi

    # 复制后端服务
    log_info "复制后端服务..."
    cp webadmin/backend/server.js "$WEBADMIN_DIR/backend/"
    cp webadmin/backend/package.json "$WEBADMIN_DIR/backend/"
    if [[ -d "webadmin/backend/node_modules" ]]; then
        cp -r webadmin/backend/node_modules "$WEBADMIN_DIR/backend/"
    fi

    # 安装后端依赖
    log_info "安装后端依赖..."
    cd "$WEBADMIN_DIR/backend"
    if [[ ! -d "node_modules" ]]; then
        npm install
    fi
    cd - > /dev/null

    # 创建前端静态文件服务器脚本（使用 Python）
    log_info "创建前端静态文件服务器..."
    cat > "$WEBADMIN_DIR/start-frontend.sh" << 'EOF'
#!/bin/bash
# 使用 Python 静态文件服务器启动前端

cd ~/.openviking/webadmin/dist
python3 -m http.server 5173 --bind 0.0.0.0
EOF
    chmod +x "$WEBADMIN_DIR/start-frontend.sh"

    # 复制 Nginx 配置
    log_info "复制 Nginx 配置..."
    cp webadmin/nginx.conf "$CONFIG_DIR/"

    # 创建后端服务管理脚本
    log_info "创建后端服务管理脚本..."
    cat > "$WEBADMIN_DIR/services.sh" << 'EOF'
#!/bin/bash
# Web Admin 服务管理脚本 (前后端分离)

CONFIG_DIR="$HOME/.openviking"
WEBADMIN_DIR="$CONFIG_DIR/webadmin"
BACKEND_DIR="$WEBADMIN_DIR/backend"
BACKEND_BIN="$BACKEND_DIR/server.js"
BACKEND_LOG="$CONFIG_DIR/log/webadmin-backend.log"
BACKEND_PID="$CONFIG_DIR/webadmin/backend.pid"

FRONTEND_DIR="$WEBADMIN_DIR"
FRONTEND_LOG="$CONFIG_DIR/log/webadmin-frontend.log"
FRONTEND_PID="$CONFIG_DIR/webadmin/frontend.pid"

start_backend() {
    if [[ -f "$BACKEND_PID" ]]; then
        local PID=$(cat "$BACKEND_PID")
        if kill -0 "$PID" 2>/dev/null; then
            echo "Web Admin 后端已在运行 (PID: $PID)"
            return 0
        fi
    fi

    echo "启动 Web Admin 后端服务..."
    cd "$BACKEND_DIR"
    nohup node server.js > "$BACKEND_LOG" 2>&1 &
    local pid=$!
    echo $pid > "$BACKEND_PID"

    echo "等待后端启动..."
    sleep 3

    if pgrep -f "node.*server.js" > /dev/null; then
        echo "Web Admin 后端启动成功 (PID: $pid)"
        echo "访问：http://localhost:3000/api/proxy"
    else
        echo "Web Admin 后端启动失败，请检查日志：$BACKEND_LOG"
        return 1
    fi
}

stop_backend() {
    if [[ -f "$BACKEND_PID" ]]; then
        local PID=$(cat "$BACKEND_PID")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            echo "停止 Web Admin 后端 (PID: $PID)"
        fi
        rm -f "$BACKEND_PID"
    else
        pkill -f "node.*server.js"
        echo "停止 Web Admin 后端"
    fi
}

start_frontend() {
    if [[ -f "$FRONTEND_PID" ]]; then
        local PID=$(cat "$FRONTEND_PID")
        if kill -0 "$PID" 2>/dev/null; then
            echo "Web Admin 前端已在运行 (PID: $PID)"
            return 0
        fi
    fi

    echo "启动 Web Admin 前端服务..."
    cd "$FRONTEND_DIR/dist"
    nohup python3 -m http.server 5173 --bind 0.0.0.0 > "$FRONTEND_LOG" 2>&1 &
    local pid=$!
    echo $pid > "$FRONTEND_PID"

    echo "等待前端启动..."
    sleep 3

    if netstat -tlnp 2>/dev/null | grep -q ":5173" || ss -tlnp 2>/dev/null | grep -q ":5173"; then
        echo "Web Admin 前端启动成功 (PID: $pid)"
        echo "访问：http://localhost:5173"
    else
        echo "Web Admin 前端启动失败，请检查日志：$FRONTEND_LOG"
        return 1
    fi
}

stop_frontend() {
    if [[ -f "$FRONTEND_PID" ]]; then
        local PID=$(cat "$FRONTEND_PID")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            echo "停止 Web Admin 前端 (PID: $PID)"
        fi
        rm -f "$FRONTEND_PID"
    else
        pkill -f "python3.*http.server.*5173" 2>/dev/null || true
        echo "停止 Web Admin 前端"
    fi
}

start_all() {
    start_backend
    start_frontend
}

stop_all() {
    stop_frontend
    stop_backend
}

show_status() {
    echo "=== Web Admin 后端 (端口 3000) ==="
    if pgrep -f "node.*server.js" > /dev/null; then
        echo "状态：运行中"
        echo "PID: $(pgrep -f 'node.*server.js' | head -1)"
        echo "访问：http://localhost:3000/api/proxy"
    else
        echo "状态：未运行"
    fi

    echo ""
    echo "=== Web Admin 前端 (端口 5173) ==="
    if netstat -tlnp 2>/dev/null | grep -q ":5173" || ss -tlnp 2>/dev/null | grep -q ":5173"; then
        echo "状态：运行中"
        echo "访问：http://localhost:5173"
    else
        echo "状态：未运行"
    fi
}

case "$1" in
    backend)
        case "$2" in
            start)
                start_backend
                ;;
            stop)
                stop_backend
                ;;
            status)
                if pgrep -f "node.*server.js" > /dev/null; then
                    echo "状态：运行中"
                    echo "PID: $(pgrep -f 'node.*server.js' | head -1)"
                else
                    echo "状态：未运行"
                fi
                ;;
            restart)
                stop_backend
                sleep 2
                start_backend
                ;;
            *)
                echo "用法：$0 backend {start|stop|status|restart}"
                exit 1
                ;;
        esac
        ;;
    frontend)
        case "$2" in
            start)
                start_frontend
                ;;
            stop)
                stop_frontend
                ;;
            status)
                if netstat -tlnp 2>/dev/null | grep -q ":5173" || ss -tlnp 2>/dev/null | grep -q ":5173"; then
                    echo "状态：运行中"
                else
                    echo "状态：未运行"
                fi
                ;;
            restart)
                stop_frontend
                sleep 2
                start_frontend
                ;;
            *)
                echo "用法：$0 frontend {start|stop|status|restart}"
                exit 1
                ;;
        esac
        ;;
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    status)
        show_status
        ;;
    restart)
        stop_all
        sleep 2
        start_all
        ;;
    *)
        echo "用法：$0 {backend|frontend|start|stop|status|restart}"
        echo ""
        echo "命令:"
        echo "  backend    后端服务管理"
        echo "  frontend   前端服务管理"
        echo "  start      启动所有服务"
        echo "  stop       停止所有服务"
        echo "  status     显示服务状态"
        echo "  restart    重启所有服务"
        exit 1
        ;;
esac
EOF
    chmod +x "$WEBADMIN_DIR/services.sh"

    # 更新主服务管理脚本
    log_info "更新主服务管理脚本..."
    update_main_services_script

    log_info "Web Admin 服务部署完成!"
    log_info ""
    log_info "下一步:"
    log_info "  1. 运行 $WEBADMIN_DIR/services.sh start 启动服务"
    log_info "  2. 访问 http://localhost:5173"
}

# 更新主服务管理脚本
update_main_services_script() {
    local SERVICES_SCRIPT="$HOME/.openviking/services.sh"

    if [[ ! -f "$SERVICES_SCRIPT" ]]; then
        log_warn "主服务管理脚本不存在：$SERVICES_SCRIPT"
        return 0
    fi

    # 检查是否已包含 Web Admin 配置
    if grep -q "WEBADMIN_DIR" "$SERVICES_SCRIPT"; then
        log_info "Web Admin 配置已存在于主服务管理脚本中"
        return 0
    fi

    log_info "在 main services.sh 中添加 Web Admin 配置..."

    # 创建临时文件
    local TEMP_FILE=$(mktemp)

    # 读取原文件并在 CONFIG_DIR 定义后添加 Web Admin 配置
    local ADDED=false
    while IFS= read -r line || [[ -n "$line" ]]; do
        echo "$line" >> "$TEMP_FILE"

        if [[ "$ADDED" == false ]] && [[ "$line" =~ ^CONFIG_DIR= ]]; then
            # 添加 Web Admin 相关配置
            cat >> "$TEMP_FILE" << 'EOF'

# Web Admin 服务配置 (前后端分离)
WEBADMIN_DIR="$CONFIG_DIR/webadmin"
BACKEND_DIR="$WEBADMIN_DIR/backend"
BACKEND_PID_FILE="$CONFIG_DIR/webadmin/backend.pid"
BACKEND_LOG="$CONFIG_DIR/log/webadmin-backend.log"
FRONTEND_PID_FILE="$CONFIG_DIR/webadmin/frontend.pid"
FRONTEND_LOG="$CONFIG_DIR/log/webadmin-frontend.log"
EOF
            ADDED=true
        fi
    done < "$SERVICES_SCRIPT"

    # 添加 Web Admin 服务管理函数到文件末尾（在 show_status 之前）
    local BEFORE_STATUS=$(mktemp)
    local AFTER_STATUS=$(mktemp)

    awk '/^show_status\(\)/ {found=1} found {print > "'"$AFTER_STATUS"'"} !found {print > "'"$BEFORE_STATUS"'"}' "$TEMP_FILE"

    # 合并文件
    cat "$BEFORE_STATUS" > "$TEMP_FILE"

    # 添加 Web Admin 服务管理函数
    cat >> "$TEMP_FILE" << 'EOF'

# Web Admin 后端服务管理
start_webadmin_backend() {
    log_step "启动 Web Admin 后端服务..."

    if [[ ! -f "$BACKEND_DIR/server.js" ]]; then
        log_error "Web Admin 后端文件不存在：$BACKEND_DIR/server.js"
        return 1
    fi

    # 检查是否已在运行
    if pgrep -f "node.*server.js" > /dev/null; then
        log_warn "Web Admin 后端已在运行"
        read -p "是否重启 Web Admin 后端？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            stop_webadmin_backend
            sleep 2
        else
            log_info "跳过重启"
            return 0
        fi
    fi

    # 启动 Web Admin 后端
    log_info "启动 Web Admin 后端..."
    mkdir -p "$CONFIG_DIR/log"
    cd "$BACKEND_DIR"
    nohup node server.js > "$BACKEND_LOG" 2>&1 &
    local pid=$!
    echo $pid > "$BACKEND_PID_FILE"

    # 等待启动
    log_info "等待 Web Admin 后端启动..."
    sleep 3

    if pgrep -f "node.*server.js" > /dev/null; then
        log_info "Web Admin 后端启动成功 (PID: $pid)"
    else
        log_warn "Web Admin 后端可能未完全启动，请检查日志：$BACKEND_LOG"
    fi
}

stop_webadmin_backend() {
    if [[ -f "$BACKEND_PID_FILE" ]]; then
        local PID=$(cat "$BACKEND_PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            log_info "停止 Web Admin 后端 (PID: $PID)"
        fi
        rm -f "$BACKEND_PID_FILE"
    else
        pkill -f "node.*server.js"
        log_info "停止 Web Admin 后端"
    fi
}

# Web Admin 前端服务管理
start_webadmin_frontend() {
    log_step "启动 Web Admin 前端服务..."

    # 检查是否已在运行
    if netstat -tlnp 2>/dev/null | grep -q ":5173" || ss -tlnp 2>/dev/null | grep -q ":5173"; then
        log_warn "Web Admin 前端已在运行"
        read -p "是否重启 Web Admin 前端？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            stop_webadmin_frontend
            sleep 2
        else
            log_info "跳过重启"
            return 0
        fi
    fi

    # 启动 Web Admin 前端
    log_info "启动 Web Admin 前端..."
    mkdir -p "$CONFIG_DIR/log"
    cd "$WEBADMIN_DIR/dist"
    nohup python3 -m http.server 5173 --bind 0.0.0.0 > "$FRONTEND_LOG" 2>&1 &
    local pid=$!
    echo $pid > "$FRONTEND_PID_FILE"

    # 等待启动
    log_info "等待 Web Admin 前端启动..."
    sleep 3

    if netstat -tlnp 2>/dev/null | grep -q ":5173" || ss -tlnp 2>/dev/null | grep -q ":5173"; then
        log_info "Web Admin 前端启动成功 (PID: $pid)"
    else
        log_warn "Web Admin 前端可能未完全启动，请检查日志：$FRONTEND_LOG"
    fi
}

stop_webadmin_frontend() {
    if [[ -f "$FRONTEND_PID_FILE" ]]; then
        local PID=$(cat "$FRONTEND_PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            log_info "停止 Web Admin 前端 (PID: $PID)"
        fi
        rm -f "$FRONTEND_PID_FILE"
    else
        pkill -f "python3.*http.server.*5173" 2>/dev/null || true
        log_info "停止 Web Admin 前端"
    fi
}

# 修改 start_webadmin 和 stop_webadmin 函数
start_webadmin() {
    start_webadmin_backend
    start_webadmin_frontend
}

stop_webadmin() {
    stop_webadmin_frontend
    stop_webadmin_backend
}
EOF

    # 添加 show_status 函数
    cat "$AFTER_STATUS" >> "$TEMP_FILE"

    # 替换原文件
    mv "$TEMP_FILE" "$SERVICES_SCRIPT"
    chmod +x "$SERVICES_SCRIPT"

    # 清理临时文件
    rm -f "$BEFORE_STATUS" "$AFTER_STATUS"

    log_info "主服务管理脚本已更新"
}

# 清理
clean() {
    log_step "清理..."

    local CONFIG_DIR="$HOME/.openviking"

    # 清理 Web Admin 服务
    if [[ -f "$CONFIG_DIR/webadmin/services.sh" ]]; then
        "$CONFIG_DIR/webadmin/services.sh" stop 2>/dev/null || true
    fi

    # 清理 Web Admin 目录
    if [[ -d "$CONFIG_DIR/webadmin" ]]; then
        rm -rf "$CONFIG_DIR/webadmin"
        log_info "清理 Web Admin 目录"
    fi

    log_info "清理完成"
}

# 显示帮助
show_help() {
    echo "OpenViking Web Admin 部署脚本"
    echo ""
    echo "用法：$0 [命令]"
    echo ""
    echo "命令:"
    echo "  deploy      部署 Web Admin 到 $HOME/.openviking/webadmin/"
    echo "  start       启动 Web Admin 服务"
    echo "  stop        停止 Web Admin 服务"
    echo "  status      显示 Web Admin 服务状态"
    echo "  restart     重启 Web Admin 服务"
    echo "  clean       清理 Web Admin 服务"
    echo "  help        显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 deploy     # 部署 Web Admin"
    echo "  $0 start      # 启动 Web Admin"
    echo "  $0 status     # 查看状态"
}

# 主函数
main() {
    local COMMAND="${1:-deploy}"

    case $COMMAND in
        deploy)
            check_node
            deploy_webadmin
            ;;
        start)
            if [[ -f "$HOME/.openviking/webadmin/services.sh" ]]; then
                "$HOME/.openviking/webadmin/services.sh" start
            else
                log_error "Web Admin 服务未部署，请先运行 $0 deploy"
                exit 1
            fi
            ;;
        stop)
            if [[ -f "$HOME/.openviking/webadmin/services.sh" ]]; then
                "$HOME/.openviking/webadmin/services.sh" stop
            else
                log_error "Web Admin 服务未部署，请先运行 $0 deploy"
                exit 1
            fi
            ;;
        status)
            if [[ -f "$HOME/.openviking/webadmin/services.sh" ]]; then
                "$HOME/.openviking/webadmin/services.sh" status
            else
                log_error "Web Admin 服务未部署，请先运行 $0 deploy"
                exit 1
            fi
            ;;
        restart)
            if [[ -f "$HOME/.openviking/webadmin/services.sh" ]]; then
                "$HOME/.openviking/webadmin/services.sh" restart
            else
                log_error "Web Admin 服务未部署，请先运行 $0 deploy"
                exit 1
            fi
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
