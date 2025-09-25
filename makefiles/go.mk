# =============================================================================
# Go Language Support - Makefile Module
# =============================================================================

# Go tool definitions
GOIMPORTS := goimports
GOFUMPT := gofumpt
GOLINES := golines
GOCYCLO := gocyclo
STATICCHECK := staticcheck
GOLANGCI_LINT := golangci-lint

# Go project variables
GO := go
ifeq ($(OS),Windows_NT)
    GOFILES := $(shell dir /s /b backend-go\*.go 2>nul)
else
    GOFILES := $(shell find backend-go -name "*.go" 2>/dev/null || true)
endif
ifeq ($(OS),Windows_NT)
    GOMODULES := $(shell cd backend-go 2>nul && $(GO) list -m 2>nul || echo "No Go module")
else
    GOMODULES := $(shell cd backend-go && $(GO) list -m 2>/dev/null || echo "No Go module")
endif

# =============================================================================
# Go Tool Installation
# =============================================================================

install-tools-go: ## Install Go development tools
	@if [ "$(HAS_GO)" = "true" ]; then \
		echo "$(YELLOW)Installing Go tools...$(RESET)"; \
		$(GO) install golang.org/x/tools/cmd/goimports@latest; \
		$(GO) install mvdan.cc/gofumpt@latest; \
		$(GO) install github.com/segmentio/golines@latest; \
		$(GO) install github.com/fzipp/gocyclo/cmd/gocyclo@latest; \
		$(GO) install honnef.co/go/tools/cmd/staticcheck@2025.1.1; \
		$(GO) install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.3.0; \
		echo "$(GREEN)Go tools installed$(RESET)"; \
	else \
		echo "$(BLUE)Skipping Go tools (no Go project detected)$(RESET)"; \
	fi

check-tools-go: ## Check Go development tools
	@if [ "$(HAS_GO)" = "true" ]; then \
		echo "$(YELLOW)Checking Go tools...$(RESET)"; \
		command -v $(GO) >/dev/null 2>&1 || (echo "$(RED)go is not installed$(RESET)" && exit 1); \
		command -v $(GOIMPORTS) >/dev/null 2>&1 || (echo "$(RED)goimports is not installed. Run 'make install-tools-go'$(RESET)" && exit 1); \
		command -v $(GOFUMPT) >/dev/null 2>&1 || (echo "$(RED)gofumpt is not installed. Run 'make install-tools-go'$(RESET)" && exit 1); \
		command -v $(GOLINES) >/dev/null 2>&1 || (echo "$(RED)golines is not installed. Run 'make install-tools-go'$(RESET)" && exit 1); \
		command -v $(GOCYCLO) >/dev/null 2>&1 || (echo "$(RED)gocyclo is not installed. Run 'make install-tools-go'$(RESET)" && exit 1); \
		command -v $(STATICCHECK) >/dev/null 2>&1 || (echo "$(RED)staticcheck is not installed. Run 'make install-tools-go'$(RESET)" && exit 1); \
		command -v $(GOLANGCI_LINT) >/dev/null 2>&1 || (echo "$(RED)golangci-lint is not installed. Run 'make install-tools-go'$(RESET)" && exit 1); \
		echo "$(GREEN)Go tools available$(RESET)"; \
	fi

# =============================================================================
# Go Code Formatting
# =============================================================================

fmt-go: ## Format Go code
	@if [ "$(HAS_GO)" = "true" ]; then \
		echo "$(YELLOW)Formatting Go code...$(RESET)"; \
		if [ -d backend-go ]; then \
			cd backend-go && $(GO) fmt ./...; \
		fi; \
		if [ -n "$(GOFILES)" ]; then \
			if command -v $(GOIMPORTS) >/dev/null 2>&1; then \
				$(GOIMPORTS) -w $(GOFILES) >/dev/null 2>&1 || true; \
			fi; \
			if command -v $(GOFUMPT) >/dev/null 2>&1; then \
				$(GOFUMPT) -w $(GOFILES) >/dev/null 2>&1 || true; \
			fi; \
			if command -v $(GOLINES) >/dev/null 2>&1; then \
				$(GOLINES) -w -m 120 $(GOFILES) >/dev/null 2>&1 || true; \
			fi; \
		else \
			echo "$(BLUE)No Go files found to format$(RESET)"; \
		fi; \
		echo "$(GREEN)Go code formatted$(RESET)"; \
	else \
		echo "$(BLUE)Skipping Go formatting (no Go project)$(RESET)"; \
	fi

# =============================================================================
# Go Code Quality Checks
# =============================================================================

check-go: ## Check Go code quality
	@if [ "$(HAS_GO)" = "true" ]; then \
		echo "$(YELLOW)Checking Go code quality...$(RESET)"; \
		cd backend-go; \
		if command -v $(GOCYCLO) >/dev/null 2>&1; then \
			echo "$(YELLOW)Running gocyclo...$(RESET)"; \
			$(GOCYCLO) -over 10 . || (echo "$(RED)High cyclomatic complexity detected$(RESET)" && exit 1); \
		else \
			echo "$(YELLOW)gocyclo not available, skipping complexity check$(RESET)"; \
		fi; \
		if command -v $(STATICCHECK) >/dev/null 2>&1; then \
			echo "$(YELLOW)Running staticcheck...$(RESET)"; \
			$(STATICCHECK) ./...; \
		else \
			echo "$(YELLOW)staticcheck not available, skipping static analysis$(RESET)"; \
		fi; \
		if command -v $(GOLANGCI_LINT) >/dev/null 2>&1; then \
			echo "$(YELLOW)Running golangci-lint...$(RESET)"; \
			$(GOLANGCI_LINT) run ./...; \
		else \
			echo "$(YELLOW)golangci-lint not available, skipping lint check$(RESET)"; \
		fi; \
		echo "$(GREEN)Go code quality checks completed$(RESET)"; \
	else \
		echo "$(BLUE)Skipping Go checks (no Go project)$(RESET)"; \
	fi

# =============================================================================
# Go Specific Quality Check Tools
# =============================================================================

check-gocyclo: check-gocyclo-tool ## Check cyclomatic complexity
	@echo "$(YELLOW)Running gocyclo check...$(RESET)"
	@$(GOCYCLO) -over 10 $(GOFILES) || (echo "$(RED)High cyclomatic complexity detected$(RESET)" && exit 1)
	@echo "$(GREEN)Cyclomatic complexity check passed$(RESET)"

check-staticcheck: check-staticcheck-tool ## Run static analysis checks
	@echo "$(YELLOW)Running staticcheck...$(RESET)"
	@$(STATICCHECK) ./...
	@echo "$(GREEN)Staticcheck passed$(RESET)"

explain-staticcheck: check-staticcheck-tool ## Explain staticcheck error codes (usage: make explain-staticcheck code=ST1008)
	@if [ -z "$(code)" ]; then \
		echo "$(RED)Please provide error code, example: make explain-staticcheck code=ST1008$(RESET)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Explaining staticcheck error code $(code):$(RESET)"
	@$(STATICCHECK) -explain $(code)

check-golangci-lint: check-golangci-lint-tool ## Run comprehensive golangci-lint checks
	@echo "$(YELLOW)Running golangci-lint...$(RESET)"
	@$(GOLANGCI_LINT) run ./...
	@echo "$(GREEN)Golangci-lint check passed$(RESET)"

# Check individual tools
check-gocyclo-tool:
	@command -v $(GOCYCLO) >/dev/null 2>&1 || (echo "$(RED)gocyclo is not installed. Run 'make install-tools'$(RESET)" && exit 1)

check-staticcheck-tool:
	@command -v $(STATICCHECK) >/dev/null 2>&1 || (echo "$(RED)staticcheck is not installed. Run 'make install-tools'$(RESET)" && exit 1)

check-golangci-lint-tool:
	@command -v $(GOLANGCI_LINT) >/dev/null 2>&1 || (echo "$(RED)golangci-lint is not installed. Run 'make install-tools'$(RESET)" && exit 1)

check-gofumpt:
	@command -v $(GOFUMPT) >/dev/null 2>&1 || (echo "$(RED)gofumpt is not installed. Run 'make install-tools'$(RESET)" && exit 1)

check-golines:
	@command -v $(GOLINES) >/dev/null 2>&1 || (echo "$(RED)golines is not installed. Run 'make install-tools'$(RESET)" && exit 1)

# Show Go project information
info-go: ## Show Go project information
	@echo "$(BLUE)Go Project Information:$(RESET)"
	@echo "  Module: $(GOMODULES)"
	@echo "  Go files: $(words $(GOFILES))"
	@echo "  Go version: $$($(GO) version)"

# Format check (without modifying files)
fmt-check-go: ## Check if Go code format meets standards (without modifying files)
	@echo "$(YELLOW)Checking Go code formatting...$(RESET)"
	@if [ "$(HAS_GO)" = "true" ]; then \
		cd backend-go; \
		if [ -n "$$($(GO) fmt ./...)" ]; then \
			echo "$(RED)Go code is not formatted. Run 'make fmt-go' to fix.$(RESET)"; \
			exit 1; \
		fi; \
	fi
	@echo "$(GREEN)Go code formatting checks passed$(RESET)"