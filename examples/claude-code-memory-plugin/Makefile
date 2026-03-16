# Claude Code Memory Plugin Makefile

.PHONY: install uninstall verify verify-plugin verify-basic test test-basic test-auto help clean

# 配置
INSTALL_DIR ?= $(CURDIR)/claude-code-memory-plugin
OPENVIKING_URL ?= http://localhost:1933
OPENVIKING_API_KEY ?=

# 默认目标
help:
	@echo "Claude Code Memory Plugin - Makefile 命令"
	@echo ""
	@echo "可用命令:"
	@echo "  make install      - 安装插件"
	@echo "  make install-auto - 自动安装（使用环境变量）"
	@echo "  make verify       - 验证插件架构和基础安装"
	@echo "  make verify-plugin - 验证插件架构（Claude Code 标准）"
	@echo "  make verify-basic - 验证基础安装"
	@echo "  make test         - 运行测试"
	@echo "  make test-basic   - 运行基础测试"
	@echo "  make test-auto    - 运行自动记忆测试"
	@echo "  make uninstall    - 卸载插件"
	@echo "  make clean        - 清理临时文件"
	@echo ""
	@echo "环境变量:"
	@echo "  INSTALL_DIR       - 安装目录（默认：当前工作目录）"
	@echo "  OPENVIKING_URL    - OpenViking URL（默认：http://localhost:1933）"
	@echo "  OPENVIKING_API_KEY - API 密钥"

# 交互式安装
install:
	@echo "开始交互式安装..."
	@chmod +x install.sh
	@./install.sh -i

# 自动安装
install-auto:
	@echo "开始自动安装..."
	@export OPENVIKING_URL=$(OPENVIKING_URL)
	@if [ -n "$(OPENVIKING_API_KEY)" ]; then \
		export OPENVIKING_API_KEY=$(OPENVIKING_API_KEY); \
		./install.sh -a; \
	else \
		./install.sh -a; \
	fi

# 验证安装
verify: verify-plugin verify-basic

verify-plugin:
	@echo "验证插件架构（Claude Code 标准）..."
	@python3 verify_claude_plugin.py

verify-basic:
	@echo "验证基础安装..."
	@python3 verify_install.py

# 运行所有测试
test: test-basic test-auto

# 基础测试
test-basic:
	@echo "运行基础测试..."
	@python3 test_memory_plugin.py

# 自动记忆测试
test-auto:
	@echo "运行自动记忆测试..."
	@python3 test_auto_memory.py

# 卸载
uninstall:
	@echo "开始卸载..."
	@chmod +x uninstall.sh
	@./uninstall.sh -f

# 清理临时文件
clean:
	@echo "清理临时文件..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type f -name "*.pyo" -delete
	@echo "清理完成"
