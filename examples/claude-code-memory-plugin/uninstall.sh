#!/bin/bash

# Claude Code Memory Plugin 卸载脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 默认安装目录
INSTALL_DIR="${INSTALL_DIR:-$HOME/.claude/claude-code-memory-plugin}"

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

show_help() {
    cat << EOF
用法：$0 [选项]

选项:
    -f, --force      强制卸载（不确认）
    -c, --config     只删除配置文件
    -d, --dir DIR    指定要卸载的目录
    -h, --help       显示帮助信息

默认卸载目录：$INSTALL_DIR
EOF
}

main() {
    FORCE=""

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--force)
                FORCE="yes"
                shift
                ;;
            -c|--config)
                ONLY_CONFIG="yes"
                shift
                ;;
            -d|--dir)
                INSTALL_DIR="$2"
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
    echo "  Claude Code Memory Plugin 卸载脚本"
    echo "=========================================="
    echo ""

    # 检查安装目录
    if [ ! -d "$INSTALL_DIR" ]; then
        print_warning "安装目录不存在：$INSTALL_DIR"

        if [ -z "$ONLY_CONFIG" ]; then
            print_info "检查默认目录..."
            if [ ! -d "$HOME/.openviking/claude-code-memory-plugin" ]; then
                print_warning "未找到安装的插件"
                exit 0
            fi
            INSTALL_DIR="$HOME/.openviking/claude-code-memory-plugin"
        fi
    fi

    if [ -z "$ONLY_CONFIG" ]; then
        echo "将要卸载:"
        echo "  插件目录：$INSTALL_DIR"
        echo ""

        if [ -z "$FORCE" ]; then
            read -p "确认卸载？(y/n): " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_warning "取消卸载"
                exit 0
            fi
        fi

        # 删除插件目录
        if [ -d "$INSTALL_DIR" ]; then
            rm -rf "$INSTALL_DIR"
            print_success "插件目录已删除：$INSTALL_DIR"
        fi

    # 清理验证脚本
    VERIFY_SCRIPT="$HOME/.claude/verify_claude_plugin.py"
    if [ -f "$VERIFY_SCRIPT" ]; then
        rm -f "$VERIFY_SCRIPT"
        print_success "验证脚本已删除"
    fi
    fi

    # 删除配置文件
    CONFIG_FILE="$HOME/.claude/code-memory-config.json"
    if [ -f "$CONFIG_FILE" ]; then
        echo ""
        echo "配置文件：$CONFIG_FILE"

        if [ -z "$FORCE" ]; then
            read -p "删除配置文件？(y/n): " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_warning "保留配置文件"
            else
                rm -f "$CONFIG_FILE"
                print_success "配置文件已删除"
            fi
        else
            rm -f "$CONFIG_FILE"
            print_success "配置文件已删除"
        fi
    fi

    # 清理 shell 环境变量
    echo ""
    print_info "清理 shell 环境变量..."

    SHELL_TYPE=$(echo "$SHELL" | rev | cut -d'/' -f1 | rev)

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
    esac

    if [ -n "$RC_FILE" ] && [ -f "$RC_FILE" ]; then
        # 创建临时文件
        TEMP_FILE=$(mktemp)

        # 移除相关配置行
        grep -v "OPENVIKING_URL" "$RC_FILE" > "$TEMP_FILE" 2>/dev/null || true
        grep -v "OPENVIKING_API_KEY" "$TEMP_FILE" > "$RC_FILE" 2>/dev/null || true
        grep -v "INSTALL_DIR" "$RC_FILE" > "$TEMP_FILE" 2>/dev/null || true
        mv "$TEMP_FILE" "$RC_FILE"

        print_success "环境变量已从 $RC_FILE 中移除"
        print_info "请运行 'source $RC_FILE' 使更改生效"
    fi

    echo ""
    echo "=========================================="
    print_success "卸载完成！"
    echo "=========================================="
}

main "$@"
