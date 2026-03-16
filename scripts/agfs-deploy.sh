#!/bin/bash
#
# OpenViking AGFS 服务部署脚本
# 将 AGFS server 部署到 $HOME/.openviking/目录
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

# 检查 Go 环境
check_go() {
    if ! command -v go &> /dev/null; then
        log_error "Go 未安装，请先安装 Go 1.22+"
        exit 1
    fi
    log_info "Go 版本：$(go version)"
}

# 编译 AGFS server
build_agfs_server() {
    log_step "编译 AGFS server..."

    local AGFS_DIR="third_party/agfs/agfs-server"
    local OUTPUT_DIR="openviking/bin"

    # 检查 Go 模块
    if [[ ! -f "$AGFS_DIR/go.mod" ]]; then
        log_error "AGFS go.mod 文件不存在：$AGFS_DIR/go.mod"
        exit 1
    fi

    # 进入 AGFS 目录编译
    cd "$AGFS_DIR"

    # 编译 Linux 版本
    log_info "编译 Linux 版本..."
    GOOS=linux GOARCH=amd64 go build -o "../agfs-server/bin/agfs-server" ./cmd/server

    cd - > /dev/null
    log_info "AGFS server 编译完成"
}

# 部署 AGFS 服务
deploy_agfs() {
    log_step "部署 AGFS 服务到 $HOME/.openviking/..."

    local CONFIG_DIR="$HOME/.openviking"
    local AGFS_DIR="$CONFIG_DIR/agfs"

    # 创建目录结构
    mkdir -p "$AGFS_DIR"
    mkdir -p "$CONFIG_DIR/agfs_data"
    mkdir -p "$CONFIG_DIR/log"

    # 复制二进制文件
    log_info "复制 AGFS server 二进制文件..."
    cp openviking/bin/agfs-server "$AGFS_DIR/"
    chmod +x "$AGFS_DIR/agfs-server"

    # 复制配置文件
    log_info "复制 AGFS 配置文件..."
    cp third_party/agfs/agfs-server/config.yaml "$AGFS_DIR/config.yaml"

    # 更新配置文件中的路径
    log_info "更新配置文件路径..."
    sed -i.bak "s|/root/.openviking/agfs_data|$CONFIG_DIR/agfs_data|g" "$AGFS_DIR/config.yaml" 2>/dev/null || \
    sed -i.bak "s|/root/.openviking/agfs_data|$CONFIG_DIR/agfs_data|g" "$AGFS_DIR/config.yaml"
    rm -f "$AGFS_DIR/config.yaml.bak"

    # 创建服务管理脚本
    log_info "创建服务管理脚本..."
    cat > "$CONFIG_DIR/agfs-services.sh" << 'EOF'
#!/bin/bash
# AGFS 服务管理脚本

CONFIG_DIR="$HOME/.openviking"
AGFS_DIR="$CONFIG_DIR/agfs"
AGFS_BIN="$AGFS_DIR/agfs-server"
AGFS_CONFIG="$AGFS_DIR/config.yaml"
AGFS_LOG="$CONFIG_DIR/log/agfs.log"
AGFS_PID="$CONFIG_DIR/agfs.pid"

start() {
    if [[ -f "$AGFS_PID" ]]; then
        local PID=$(cat "$AGFS_PID")
        if kill -0 "$PID" 2>/dev/null; then
            echo "AGFS 服务已在运行 (PID: $PID)"
            return 0
        fi
    fi

    echo "启动 AGFS 服务..."
    cd "$AGFS_DIR"
    nohup ./agfs-server -addr :1833 -c config.yaml > "$AGFS_LOG" 2>&1 &
    local pid=$!
    echo $pid > "$AGFS_PID"

    echo "等待 AGFS 启动..."
    sleep 3

    if pgrep -f "agfs-server" > /dev/null; then
        echo "AGFS 服务启动成功 (PID: $pid)"
        echo "访问：http://localhost:1833"
    else
        echo "AGFS 服务启动失败，请检查日志：$AGFS_LOG"
        return 1
    fi
}

stop() {
    if [[ -f "$AGFS_PID" ]]; then
        local PID=$(cat "$AGFS_PID")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            echo "停止 AGFS 服务 (PID: $PID)"
            rm -f "$AGFS_PID"
        else
            rm -f "$AGFS_PID"
        fi
    else
        pkill -f "agfs-server"
        echo "停止 AGFS 服务"
    fi
}

status() {
    if pgrep -f "agfs-server" > /dev/null; then
        echo "状态：运行中"
        echo "PID: $(pgrep -f 'agfs-server' | head -1)"
        echo "访问：http://localhost:1833"
    else
        echo "状态：未运行"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    *)
        echo "用法：$0 {start|stop|status|restart}"
        exit 1
        ;;
esac
EOF
    chmod +x "$CONFIG_DIR/agfs-services.sh"

    # 更新主服务管理脚本
    log_info "更新主服务管理脚本..."
    update_main_services_script

    log_info "AGFS 服务部署完成!"
    log_info ""
    log_info "下一步:"
    log_info "  1. 编辑配置文件 $AGFS_DIR/config.yaml"
    log_info "  2. 运行 $CONFIG_DIR/agfs-services.sh start 启动服务"
    log_info "  3. 访问 http://localhost:1833"
}

# 更新主服务管理脚本
update_main_services_script() {
    local SERVICES_SCRIPT="$HOME/.openviking/services.sh"

    if [[ ! -f "$SERVICES_SCRIPT" ]]; then
        log_warn "主服务管理脚本不存在：$SERVICES_SCRIPT"
        return 0
    fi

    # 检查是否已包含 AGFS 配置
    if grep -q "AGFS_DIR" "$SERVICES_SCRIPT"; then
        log_info "AGFS 配置已存在于主服务管理脚本中"
        return 0
    fi

    log_info "在 main services.sh 中添加 AGFS 配置..."

    # 创建临时文件
    local TEMP_FILE=$(mktemp)

    # 读取原文件并在 CONFIG_DIR 定义后添加 AGFS 配置
    local ADDED=false
    while IFS= read -r line || [[ -n "$line" ]]; do
        echo "$line" >> "$TEMP_FILE"

        if [[ "$ADDED" == false ]] && [[ "$line" =~ ^CONFIG_DIR= ]]; then
            # 添加 AGFS 相关配置
            cat >> "$TEMP_FILE" << 'EOF'

# AGFS 服务配置
AGFS_DIR="$CONFIG_DIR/agfs"
AGFS_BIN="$AGFS_DIR/agfs-server"
AGFS_CONFIG="$AGFS_DIR/config.yaml"
AGFS_LOG="$CONFIG_DIR/log/agfs.log"
AGFS_PID="$CONFIG_DIR/agfs.pid"
EOF
            ADDED=true
        fi
    done < "$SERVICES_SCRIPT"

    # 添加 AGFS 服务管理函数到文件末尾（在 show_status 之前）
    # 先找到 show_status 函数的位置
    local BEFORE_STATUS=$(mktemp)
    local AFTER_STATUS=$(mktemp)

    awk '/^show_status\(\)/ {found=1} found {print > "'"$AFTER_STATUS"'"} !found {print > "'"$BEFORE_STATUS"'"}' "$TEMP_FILE"

    # 合并文件
    cat "$BEFORE_STATUS" > "$TEMP_FILE"

    # 添加 AGFS 服务管理函数
    cat >> "$TEMP_FILE" << 'EOF'

# AGFS 服务管理
start_agfs() {
    log_step "启动 AGFS 服务..."

    if [[ ! -f "$AGFS_BIN" ]]; then
        log_error "AGFS 二进制文件不存在：$AGFS_BIN"
        return 1
    fi

    if [[ ! -f "$AGFS_CONFIG" ]]; then
        log_error "AGFS 配置文件不存在：$AGFS_CONFIG"
        return 1
    fi

    # 检查是否已在运行
    if pgrep -f "agfs-server" > /dev/null; then
        log_warn "AGFS 服务已在运行"
        read -p "是否重启 AGFS 服务？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            stop_agfs
            sleep 2
        else
            log_info "跳过重启"
            return 0
        fi
    fi

    # 启动 AGFS 服务器
    log_info "启动 AGFS 服务器..."
    mkdir -p "$CONFIG_DIR/log"
    nohup "$AGFS_BIN" -addr :1833 -c "$AGFS_CONFIG" > "$AGFS_LOG" 2>&1 &
    local AGFS_PID=$!
    echo $AGFS_PID > "$AGFS_PID"

    # 等待 AGFS 启动
    log_info "等待 AGFS 启动..."
    sleep 3

    # 检查 AGFS 状态
    if pgrep -f "agfs-server" > /dev/null; then
        log_info "AGFS 服务启动成功 (PID: $AGFS_PID)"
    else
        log_warn "AGFS 服务可能未完全启动，请检查日志：$AGFS_LOG"
    fi
}

stop_agfs() {
    if [[ -f "$AGFS_PID" ]]; then
        local PID=$(cat "$AGFS_PID")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            log_info "停止 AGFS 服务 (PID: $PID)"
        fi
        rm -f "$AGFS_PID"
    else
        pkill -f "agfs-server"
        log_info "停止 AGFS 服务"
    fi
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

    # 清理 AGFS 服务
    if [[ -f "$CONFIG_DIR/agfs-services.sh" ]]; then
        "$CONFIG_DIR/agfs-services.sh" stop 2>/dev/null || true
    fi

    # 清理 AGFS 目录
    if [[ -d "$CONFIG_DIR/agfs" ]]; then
        rm -rf "$CONFIG_DIR/agfs"
        log_info "清理 AGFS 目录"
    fi

    # 清理 AGFS 数据
    if [[ -d "$CONFIG_DIR/agfs_data" ]]; then
        rm -rf "$CONFIG_DIR/agfs_data"
        log_info "清理 AGFS 数据目录"
    fi

    log_info "清理完成"
}

# 显示帮助
show_help() {
    echo "OpenViking AGFS 服务部署脚本"
    echo ""
    echo "用法：$0 [命令]"
    echo ""
    echo "命令:"
    echo "  build       编译 AGFS server"
    echo "  deploy      部署 AGFS 服务到 $HOME/.openviking/"
    echo "  start       启动 AGFS 服务"
    echo "  stop        停止 AGFS 服务"
    echo "  status      显示 AGFS 服务状态"
    echo "  restart     重启 AGFS 服务"
    echo "  clean       清理 AGFS 服务"
    echo "  help        显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 build      # 编译 AGFS server"
    echo "  $0 deploy     # 部署 AGFS 服务"
    echo "  $0 start      # 启动 AGFS 服务"
    echo "  $0 status     # 查看状态"
}

# 主函数
main() {
    local COMMAND="${1:-deploy}"

    case $COMMAND in
        build)
            check_go
            build_agfs_server
            log_info "构建完成"
            ;;
        deploy)
            check_go
            build_agfs_server
            deploy_agfs
            ;;
        start)
            if [[ -f "$HOME/.openviking/agfs-services.sh" ]]; then
                "$HOME/.openviking/agfs-services.sh" start
            else
                log_error "AGFS 服务未部署，请先运行 $0 deploy"
                exit 1
            fi
            ;;
        stop)
            if [[ -f "$HOME/.openviking/agfs-services.sh" ]]; then
                "$HOME/.openviking/agfs-services.sh" stop
            else
                log_error "AGFS 服务未部署，请先运行 $0 deploy"
                exit 1
            fi
            ;;
        status)
            if [[ -f "$HOME/.openviking/agfs-services.sh" ]]; then
                "$HOME/.openviking/agfs-services.sh" status
            else
                log_error "AGFS 服务未部署，请先运行 $0 deploy"
                exit 1
            fi
            ;;
        restart)
            if [[ -f "$HOME/.openviking/agfs-services.sh" ]]; then
                "$HOME/.openviking/agfs-services.sh" restart
            else
                log_error "AGFS 服务未部署，请先运行 $0 deploy"
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
