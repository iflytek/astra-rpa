# =============================================================================
# Common Variables and Functions - Makefile Module
# =============================================================================

# Project detection variables (Cross-platform compatible)
ifeq ($(OS),Windows_NT)
    HAS_GO := $(shell if exist "backend-go" echo true)
    HAS_TS := $(shell if exist "frontend" echo true)
    HAS_JAVA := $(shell if exist "backend-java" echo true)
    HAS_PYTHON := $(shell if exist "backend-python" echo true)
else
    HAS_GO := $(shell [ -d "backend-go" ] && echo "true")
    HAS_TS := $(shell [ -d "frontend" ] && echo "true")
    HAS_JAVA := $(shell [ -d "backend-java" ] && echo "true")
    HAS_PYTHON := $(shell [ -d "backend-python" ] && echo "true")
endif

# Color output definitions
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
RESET := \033[0m

# Project status check
project-status: ## Show detected project status
	@echo "$(BLUE)Detected Projects:$(RESET)"
ifeq ($(OS),Windows_NT)
	@if "$(HAS_GO)"=="true" (echo "  $(GREEN)✓ Go Backend$(RESET)       (backend-go/)") else (echo "  $(RED)✗ Go Backend$(RESET)       (backend-go/)")
	@if "$(HAS_TS)"=="true" (echo "  $(GREEN)✓ TypeScript Frontend$(RESET) (frontend/)") else (echo "  $(RED)✗ TypeScript Frontend$(RESET) (frontend/)")
	@if "$(HAS_JAVA)"=="true" (echo "  $(GREEN)✓ Java Backend$(RESET)      (backend-java/)") else (echo "  $(RED)✗ Java Backend$(RESET)      (backend-java/)")
	@if "$(HAS_PYTHON)"=="true" (echo "  $(GREEN)✓ Python Backend$(RESET)    (backend-python/)") else (echo "  $(RED)✗ Python Backend$(RESET)    (backend-python/)")
else
	@if [ "$(HAS_GO)" = "true" ]; then echo "  $(GREEN)✓ Go Backend$(RESET)       (backend-go/)"; else echo "  $(RED)✗ Go Backend$(RESET)       (backend-go/)"; fi
	@if [ "$(HAS_TS)" = "true" ]; then echo "  $(GREEN)✓ TypeScript Frontend$(RESET) (frontend/)"; else echo "  $(RED)✗ TypeScript Frontend$(RESET) (frontend/)"; fi
	@if [ "$(HAS_JAVA)" = "true" ]; then echo "  $(GREEN)✓ Java Backend$(RESET)      (backend-java/)"; else echo "  $(RED)✗ Java Backend$(RESET)      (backend-java/)"; fi
	@if [ "$(HAS_PYTHON)" = "true" ]; then echo "  $(GREEN)✓ Python Backend$(RESET)    (backend-python/)"; else echo "  $(RED)✗ Python Backend$(RESET)    (backend-python/)"; fi
endif

# Multi-language tool installation aggregate command
install-tools: ## Install formatting and checking tools for all languages
	@echo "$(YELLOW)Installing multi-language development tools...$(RESET)"
	@make --no-print-directory install-tools-go
	@make --no-print-directory install-tools-typescript
	@make --no-print-directory install-tools-java
	@make --no-print-directory install-tools-python
	@echo "$(GREEN)All multi-language tools installation completed!$(RESET)"

# Multi-language tool check aggregate command
check-tools: ## Check if development tools for all languages are installed
	@echo "$(YELLOW)Checking multi-language development tools...$(RESET)"
	@make --no-print-directory check-tools-go
	@make --no-print-directory check-tools-typescript  
	@make --no-print-directory check-tools-java
	@make --no-print-directory check-tools-python
	@echo "$(GREEN)Multi-language tools check completed!$(RESET)"

# Multi-language formatting aggregate command
fmt: fmt-all ## Format all project code

fmt-all: ## Format code for all language projects
	@echo "$(YELLOW)Formatting all projects...$(RESET)"
	@make --no-print-directory fmt-go
	@make --no-print-directory fmt-typescript
	@make --no-print-directory fmt-java
	@make --no-print-directory fmt-python
	@echo "$(GREEN)All projects formatted!$(RESET)"

# Multi-language code quality check aggregate command
check: check-all ## Run all code quality checks

check-all: ## Check code quality for all language projects
	@echo "$(YELLOW)Running code quality checks for all projects...$(RESET)"
	@make --no-print-directory check-go
	@make --no-print-directory check-typescript
	@make --no-print-directory check-java
	@make --no-print-directory check-python
	@echo "$(GREEN)All code quality checks completed!$(RESET)"

# Format check (without modifying files)
fmt-check: ## Check if code format meets standards (without modifying files)
	@echo "$(YELLOW)Checking code formatting...$(RESET)"
	@make --no-print-directory fmt-check-go
	@make --no-print-directory fmt-check-typescript
	@make --no-print-directory fmt-check-java
	@make --no-print-directory fmt-check-python
	@echo "$(GREEN)Code formatting checks passed$(RESET)"

# Development environment setup
dev-setup: install-tools hooks-install branch-setup ## Setup complete development environment
	@echo "$(GREEN)Development environment setup completed!$(RESET)"
	@echo ""
	@echo "$(BLUE)Available code check commands:$(RESET)"
	@echo "  make check                       - Run all code quality checks"
	@echo "  make check-gocyclo               - Check cyclomatic complexity"
	@echo "  make check-staticcheck           - Run static analysis checks"
	@echo "  make explain-staticcheck code=XX - Explain staticcheck error codes"
	@echo "  make check-golangci-lint         - Run comprehensive lint checks"
	@echo ""
	@echo "$(BLUE)Available Git Hook commands:$(RESET)"
	@echo "  Installation commands:"
	@echo "    make hooks-install       - Install all hooks (recommended)"
	@echo "    make hooks-install-basic - Install basic hooks (lightweight)"
	@echo "    make hooks-check-all     - Pre-commit only (full checks)"
	@echo "    make hooks-fmt           - Pre-commit only (formatting)"
	@echo "    make hooks-commit-msg    - Commit-msg validation only"
	@echo "  Uninstall commands:"
	@echo "    make hooks-uninstall     - Uninstall all hooks"
	@echo "    make hooks-uninstall-pre - Uninstall pre-commit hook"
	@echo "    make hooks-uninstall-msg - Uninstall commit-msg hook"