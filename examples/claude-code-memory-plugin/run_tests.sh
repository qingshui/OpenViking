#!/bin/bash
# Claude Code Memory Plugin 测试脚本

set -e

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="$PLUGIN_ROOT/tests"

echo "========================================"
echo "Claude Code Memory Plugin 测试套件"
echo "========================================"
echo ""
echo "测试目录：$TESTS_DIR"
echo ""

# 检查测试目录
if [ ! -d "$TESTS_DIR" ]; then
    echo "错误：测试目录不存在"
    exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误：python3 未安装"
    exit 1
fi

# 运行所有测试
echo "运行测试..."
echo ""

for test_file in "$TESTS_DIR"/test_*.py; do
    if [ -f "$test_file" ]; then
        test_name=$(basename "$test_file")
        echo "----------------------------------------"
        echo "测试：$test_name"
        echo "----------------------------------------"

        cd "$TESTS_DIR"
        if python3 "$test_name"; then
            echo "✓ $test_name 通过"
        else
            echo "✗ $test_name 失败"
        fi
        echo ""
    fi
done

echo "========================================"
echo "测试完成"
echo "========================================"
