#!/bin/bash

# Claude Code Memory Plugin 自动安装脚本
# 支持远程 OpenViking 服务配置

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
DEFAULT_OPENVIKING_URL="${OPENVIKING_URL:-http://localhost:1933}"
DEFAULT_API_KEY="${OPENVIKING_API_KEY:-}"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.claude/claude-code-memory-plugin}"

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 未安装，请先安装 $1"
        return 1
    fi
    return 0
}

# 检查 Python 版本
check_python() {
    print_info "检查 Python 版本..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        return 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    print_success "Python 版本：$PYTHON_VERSION"

    # 检查版本是否 >= 3.10
    VERSION_OK=$(python3 -c 'import sys; print("yes" if sys.version_info >= (3, 10) else "no")')
    if [ "$VERSION_OK" != "yes" ]; then
        print_error "Python 版本需要 >= 3.10，当前版本：$PYTHON_VERSION"
        return 1
    fi
    return 0
}

# 检查 OpenViking 服务
check_openviking() {
    print_info "检查 OpenViking 服务..."

    if [ -z "$OPENVIKING_URL" ]; then
        print_warning "OPENVIKING_URL 未设置，使用默认值：$DEFAULT_OPENVIKING_URL"
        OPENVIKING_URL="$DEFAULT_OPENVIKING_URL"
    fi

    # 测试连接
    if command -v curl &> /dev/null; then
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$OPENVIKING_URL/health" 2>/dev/null || echo "000")
        if [ "$RESPONSE" == "200" ]; then
            print_success "OpenViking 服务可用：$OPENVIKING_URL"
            return 0
        else
            print_warning "OpenViking 服务不可达（HTTP $RESPONSE）"
            print_warning "如果这是首次安装，可以稍后配置"
            return 0
        fi
    else
        print_warning "curl 未安装，跳过服务检查"
        return 0
    fi
}

# 交互式配置
interactive_config() {
    print_info "开始配置..."
    echo ""

    # OpenViking URL
    read -p "OpenViking API 地址 [默认：$DEFAULT_OPENVIKING_URL]: " INPUT_URL
    if [ -n "$INPUT_URL" ]; then
        OPENVIKING_URL="$INPUT_URL"
    fi

    # API Key
    read -sp "API 密钥 [可选]: " INPUT_KEY
    echo ""
    if [ -n "$INPUT_KEY" ]; then
        API_KEY="$INPUT_KEY"
    else
        API_KEY=""
        print_warning "API 密钥为空，可以使用环境变量配置"
    fi

    # 安装目录
    read -p "安装目录 [默认：$INSTALL_DIR]: " INPUT_DIR
    if [ -n "$INPUT_DIR" ]; then
        INSTALL_DIR="$INPUT_DIR"
    fi

    echo ""
    print_info "配置摘要:"
    print_info "  OpenViking URL: $OPENVIKING_URL"
    if [ -n "$API_KEY" ]; then
        print_info "  API Key: ******"
    else
        print_info "  API Key: 未设置（可选）"
    fi
    print_info "  安装目录：$INSTALL_DIR"
    echo ""

    read -p "确认配置？(y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "取消安装"
        exit 1
    fi
}

# 自动配置（使用环境变量）
auto_config() {
    OPENVIKING_URL="${OPENVIKING_URL:-$DEFAULT_OPENVIKING_URL}"
    API_KEY="${OPENVIKING_API_KEY:-}"
    INSTALL_DIR="${INSTALL_DIR:-$HOME/.claude/claude-code-memory-plugin}"

    print_info "使用环境变量配置:"
    print_info "  OpenViking URL: $OPENVIKING_URL"
    if [ -n "$API_KEY" ]; then
        print_info "  API Key: ******"
    else
        print_info "  API Key: 未设置（可选）"
    fi
    print_info "  安装目录：$INSTALL_DIR"
    print_info "  注意：环境变量优先级高于配置文件"
}

# 复制插件文件
copy_files() {
    print_info "复制插件文件到 $INSTALL_DIR..."

    # 创建目标目录
    mkdir -p "$INSTALL_DIR"

    # 复制所有文件（包括隐藏文件如 .claude-plugin）
    cp -r "$SCRIPT_DIR"/.* "$INSTALL_DIR/" 2>/dev/null || true
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"

    # 设置脚本执行权限
    chmod +x "$INSTALL_DIR/hooks"/*.sh 2>/dev/null || true
    chmod +x "$INSTALL_DIR/scripts"/*.py 2>/dev/null || true

    print_success "文件复制完成"
}

# 验证安装
verify_installation() {
    print_info "验证安装..."

    # 检查必要文件（Claude Code 插件架构）
    REQUIRED_FILES=(
        ".claude-plugin/plugin.json"
        "hooks/hooks.json"
        "hooks/common.sh"
        "hooks/auto_memory_hook.sh"
        "hooks/auto_record_hook.sh"
        "hooks/user_prompt_submit.sh"
        "hooks/session_start.sh"
        "hooks/session_end.sh"
        "hooks/stop.sh"
        "commands/memory.md"
        "scripts/memory_bridge.py"
        "scripts/memory_command.py"
        "memory_plugin.py"
        "skills/memory-recall/SKILL.md"
        "README.md"
        "INSTALL.md"
        "DESIGN.md"
        "CLAUDE_CODE_INTEGRATION.md"
        "HOOKS_FIX.md"
        "test_memory_plugin.py"
        "test_auto_memory.py"
    )

    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$INSTALL_DIR/$file" ]; then
            print_success "  $file"
        else
            print_error "  $file 缺失"
            return 1
        fi
    done

    # 运行基本测试
    print_info "运行基本测试..."
    cd "$INSTALL_DIR"

    # 测试语法
    if python3 -m py_compile memory_plugin.py 2>/dev/null; then
        print_success "Python 语法检查通过"
    else
        print_error "Python 语法检查失败"
        return 1
    fi

    # 测试导入
    if python3 -c "from memory_plugin import RemoteMemoryPlugin, MemoryType, MemoryEntry, OpenVikingClient" 2>/dev/null; then
        print_success "模块导入测试通过"
    else
        print_error "模块导入测试失败"
        return 1
    fi

    return 0
}

# 配置环境变量
configure_env() {
    print_info "配置环境变量..."

    # 检测 shell
    SHELL_TYPE=$(echo "$SHELL" | rev | cut -d'/' -f1 | rev)

    # 创建配置文件（优先级：环境变量 > 配置文件）
    CONFIG_FILE="$HOME/.claude/code-memory-config.json"
    mkdir -p "$(dirname "$CONFIG_FILE")"

    cat > "$CONFIG_FILE" << EOF
{
  "openviking_url": "$OPENVIKING_URL",
  "api_key": "$API_KEY",
  "search_limit": 5,
  "install_dir": "$INSTALL_DIR"
}
EOF

    print_success "配置文件已创建：$CONFIG_FILE"
    print_info "注意：环境变量优先级高于配置文件"

    # 添加到 shell 配置文件（可选）
    RC_FILE=""
    case "$SHELL_TYPE" in
        bash)
            RC_FILE="$HOME/.bashrc"
            ;;
        zsh)
            RC_FILE="$HOME/.zshrc"
            ;;
        fish)
            RC_FILE="$HOME/.config/fish/config.fish"
            ;;
        *)
            print_warning "无法自动检测 shell 类型"
            ;;
    esac

    if [ -n "$RC_FILE" ] && [ -f "$RC_FILE" ]; then
        # 检查是否已存在配置
        if ! grep -q "OPENVIKING_URL" "$RC_FILE" 2>/dev/null; then
            cat >> "$RC_FILE" << EOF

# Claude Code Memory Plugin 配置
export OPENVIKING_URL="$OPENVIKING_URL"
EOF
            if [ -n "$API_KEY" ]; then
                echo "export OPENVIKING_API_KEY=\"$API_KEY\"" >> "$RC_FILE"
            fi
            echo "export INSTALL_DIR=\"$INSTALL_DIR\"" >> "$RC_FILE"

            print_success "环境变量已添加到 $RC_FILE"
            print_info "请运行 'source $RC_FILE' 使配置生效"
        else
            print_warning "环境变量已存在于 $RC_FILE"
        fi
    else
        print_warning "请手动添加环境变量到 shell 配置:"
        echo ""
        echo "  export OPENVIKING_URL=\"$OPENVIKING_URL\""
        if [ -n "$API_KEY" ]; then
            echo "  export OPENVIKING_API_KEY=\"$API_KEY\""
        fi
        echo "  export INSTALL_DIR=\"$INSTALL_DIR\""
        echo ""
    fi
}

# 显示使用指南
show_usage_guide() {
    echo ""
    echo "=========================================="
    echo -e "${GREEN}安装完成！${NC}"
    echo "=========================================="
    echo ""
    echo "配置方式:"
    echo ""
    echo "1. 配置文件（已创建）:"
    echo "   $CONFIG_FILE"
    echo ""
    echo "2. 环境变量（可选，优先级更高）:"
    echo "   export OPENVIKING_URL=\"$OPENVIKING_URL\""
    if [ -n "$API_KEY" ]; then
        echo "   export OPENVIKING_API_KEY=\"$API_KEY\""
    fi
    echo ""
    echo "3. 验证安装:"
    echo "   cd $INSTALL_DIR"
    echo "   python3 test_memory_plugin.py"
    echo ""
    echo "4. 在 Claude Code 中使用:"
    echo "   # 查看帮助"
    echo "   /memory"
    echo ""
    echo "   # 自动触发 - 读取代码文件时自动存储"
    echo "   Read src/main.py"
    echo ""
    echo "   # 手动命令"
    echo "   /memory analyze src/main.py"
    echo "   /memory search \"Python FastAPI\""
    echo "   /memory list"
    echo "   /memory branches"
    echo ""
    echo "5. 使用记忆回忆技能:"
    echo "   /memory-recall \"用户认证模块的改动\""
    echo ""
    echo "6. 查看文档:"
    echo "   cat $INSTALL_DIR/README.md"
    echo "   cat $INSTALL_DIR/HOOKS_FIX.md"
    echo ""
    echo "=========================================="
    echo ""
    echo "钩子系统:"
    echo ""
    echo "  - PreToolUse: 读取文件时自动分析代码"
    echo "  - PostToolUse: 工具调用后自动记录结果"
    echo "  - UserPromptSubmit: 用户提交消息时提示记忆可用性"
    echo "  - SessionStart: 会话开始时初始化"
    echo "  - SessionEnd: 会话结束时提交"
    echo "  - Stop: 会话停止时清理"
    echo ""
    echo "=========================================="
}

# 显示帮助
show_help() {
    cat << EOF
用法：$0 [选项]

选项:
    -i, --interactive    交互式配置
    -a, --auto           使用环境变量自动配置（默认）
    -d, --dir DIR        指定安装目录
    -u, --url URL        指定 OpenViking URL
    -k, --key KEY        指定 API 密钥
    -h, --help           显示帮助信息

配置方式:
    1. 环境变量（优先级最高）
       export OPENVIKING_URL="http://localhost:1933"
       export OPENVIKING_API_KEY="your-api-key"

    2. 配置文件：$HOME/.claude/code-memory-config.json
       {
         "openviking_url": "http://localhost:1933",
         "api_key": "your-api-key"
       }

    3. 命令行参数或交互式输入

示例:
    # 交互式安装
    $0 -i

    # 使用环境变量自动安装
    export OPENVIKING_URL="http://localhost:1933"
    $0 -a

    # 指定参数安装
    $0 -u "http://localhost:1933" -k "your-api-key"

    # 安装到自定义目录
    $0 -d ~/my-plugins/claude-memory

EOF
}

# 主函数
main() {
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # 解析参数
    MODE="auto"
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--interactive)
                MODE="interactive"
                shift
                ;;
            -a|--auto)
                MODE="auto"
                shift
                ;;
            -d|--dir)
                INSTALL_DIR="$2"
                shift 2
                ;;
            -u|--url)
                OPENVIKING_URL="$2"
                shift 2
                ;;
            -k|--key)
                API_KEY="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "未知选项：$1"
                show_help
                exit 1
                ;;
        esac
    done

    echo ""
    echo "=========================================="
    echo "  Claude Code Memory Plugin 安装脚本"
    echo "=========================================="
    echo ""

    # 检查前置条件
    check_command python3 || exit 1
    check_python || exit 1

    # 根据模式配置
    if [ "$MODE" == "interactive" ]; then
        interactive_config
    else
        auto_config
    fi

    # 检查 OpenViking 服务
    check_openviking

    # 复制文件
    copy_files

    # 验证安装
    verify_installation || exit 1

    # 配置环境变量
    configure_env

    # 显示使用指南
    show_usage_guide
}

# 执行主函数
main "$@"
