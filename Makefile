.DEFAULT_GOAL := help

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

PYTHON := python
UV := uv
RUFF := $(UV) run ruff
MYPY := $(UV) run mypy
PYTEST := $(UV) run pytest

check: lint types format-check test security

.PHONY: lint
lint: ruff markdownlint

.PHONY: ruff
ruff:
	@echo -e "\n$(YELLOW)Running ruff...$(NC)\n"
	@$(RUFF) check src tests

.PHONY: markdownlint
markdownlint:
	@echo -e "\n$(YELLOW)Running markdownlint...$(NC)\n"
	@which markdownlint-cli2 >/dev/null 2>&1 || { \
		echo "$(RED)Error: 'markdownlint-cli2' is not installed. Please install it first.$(NC)"; \
		exit 1; \
	}
	@markdownlint-cli2 .

.PHONY: format
format:
	@echo -e "\n$(YELLOW)Formatting code...$(NC)\n"
	@$(RUFF) format
	@$(RUFF) check --fix -s
	@which markdownlint-cli2 >/dev/null 2>&1 || { \
		echo "$(RED)Error: 'markdownlint-cli2' is not installed. Please install it first.$(NC)"; \
		exit 1; \
	}
	@markdownlint-cli2 . --fix
	@echo -e "\n$(GREEN)Formatting completed!$(NC)\n"

.PHONY: format-check
format-check:
	@echo -e "\n$(YELLOW)Checking formatting...$(NC)\n"
	@$(RUFF) format --check
	@echo -e "\n$(GREEN)Format check completed!$(NC)\n"

.PHONY: types
types:
	@echo -e "\n$(YELLOW)Checking types...$(NC)\n"
	@$(MYPY) --strict --disallow-untyped-defs --disallow-incomplete-defs src tests
	@echo -e "\n$(GREEN)Type check completed!$(NC)\n"

.PHONY: test
test:
	@echo -e "\n$(YELLOW)Running tests...$(NC)\n"
	@$(PYTEST) -q
	@echo -e "\n$(GREEN)Tests completed!$(NC)\n"

.PHONY: test-cov
test-cov:
	@echo -e "\n$(YELLOW)Running tests with coverage...$(NC)\n"
	@$(PYTEST) --cov=src --cov-report=term-missing:skip-covered --cov-fail-under=70 tests/
	@echo -e "\n$(GREEN)Coverage test completed!$(NC)\n"

.PHONY: security
security:
	@echo -e "\n$(YELLOW)Running security checks...$(NC)\n"
	@uv run bandit -r src/
	@uv run pip-audit
	@echo -e "\n$(GREEN)Security checks completed!$(NC)\n"


.PHONY: requirements
requirements:
	@echo -e "\n$(YELLOW)Sync dependencies...$(NC)\n"
	@$(UV) sync
	@$(UV) pip compile pyproject.toml -o requirements.txt
	@echo -e "\n$(GREEN)Dependencies freezed!$(NC)\n"

.PHONY: venv
venv:
	@echo -e "\n$(YELLOW)Setting up virtual environment...$(NC)\n"
	@$(UV) sync
	@echo -e "\n$(GREEN)Virtual environment ready!$(NC)\n"
	@echo "To activate virtualenv, run:"
	@echo "  source .venv/bin/activate"

pre-commit: requirements format

.PHONY: pre-commit-install
pre-commit-install:
	@echo -e "\n$(YELLOW)Installing pre-commit hooks...$(NC)\n"
	@$(UV) run pre-commit install
	@echo -e "\n$(GREEN)Pre-commit hooks installed successfully!$(NC)"
	@echo -e "\n$(GREEN)Run manually with: make pre-commit$(NC)"
	@echo -e "\n$(YELLOW)To uninstall:$(NC)"
	@echo "  make pre-commit-uninstall"

.PHONY: pre-commit-uninstall
pre-commit-uninstall:
	@echo -e "\n$(YELLOW)Uninstalling pre-commit hooks...$(NC)\n"
	$(UV) run pre-commit uninstall
	@echo -e "$(GREEN)Pre-commit hooks uninstalled!$(NC)"

.PHONY: clean
clean:
	@echo -e "\n$(YELLOW)Cleaning up...$(NC)\n"
	-find . -type f -name "*.pyc" -delete
	-find . -type f -name "*.pyo" -delete
	-find . -type f -name "*.pyd" -delete
	-find . -type f -name ".coverage" -delete
	-find . -type f -name "coverage.xml" -delete
	-find . -type f -name "*.so" -delete
	-find . -type f -name "*.c" -delete
	-find . -type d -name "__pycache__" -exec rm -rf {} +
	-find . -type d -name "*.egg-info" -exec rm -rf {} +
	-find . -type d -name ".pytest_cache" -exec rm -rf {} +
	-find . -type d -name ".ruff_cache" -exec rm -rf {} +
	-find . -type d -name ".mypy_cache" -exec rm -rf {} +
	-find . -type d -name ".hypothesis" -exec rm -rf {} +
	-find . -type d -name "htmlcov" -exec rm -rf {} +
	-find . -type d -name "dist" -exec rm -rf {} +
	-find . -type d -name "build" -exec rm -rf {} +
	-find . -type d -name ".benchmarks" -exec rm -rf {} +
	-rm -rf ".venv"
	-rm -rf "venv"
	-rm -rf "pytest_cache"
	-rm -rf "ruff_cache"
	-rm -rf ".cache"
	-rm -rf ".tox"
	-rm -rf ".eggs"
	-rm -f ".coverage.*"
	-rm -f "*.log"
	-rm -f "*.pid"
	@echo -e "\n$(GREEN)Cleanup completed!$(NC)\n"

.PHONY: help
help:
	@printf "$(GREEN)Available targets:$(NC)\n\n"
	@printf "$(YELLOW)Development:$(NC)\n"
	@printf "  check                      - run lint, types, format-check, test\n"
	@printf "  lint                       - run all linters (ruff, markdownlint)\n"
	@printf "  ruff                       - run ruff checks\n"
	@printf "  markdownlint               - run markdownlint checks\n"
	@printf "  types                      - run mypy type check\n"
	@printf "  format                     - format code with ruff\n"
	@printf "  format-check               - check formatting without changes\n"
	@printf "  security                   - security checks (bandit, pip-audit)\n"
	@printf "\n$(YELLOW)Testing:$(NC)\n"
	@printf "  test                       - run pytest tests\n"
	@printf "  test-cov                   - run tests with coverage report\n"
	@printf "\n$(YELLOW)Pre-commit:$(NC)\n"
	@printf "  pre-commit                 - format code and update requirements.txt\n"
	@printf "  pre-commit-install         - install pre-commit git hooks\n"
	@printf "  pre-commit-uninstall       - remove pre-commit git hooks\n"
	@printf "\n$(YELLOW)Dependencies:$(NC)\n"
	@printf "  venv                       - install deps and activate virtual environment\n"
	@printf "  requirements               - update dependencies\n"
	@printf "\n$(YELLOW)Cleanup:$(NC)\n"
	@printf "  clean                      - remove temporary files and venv\n"
	@printf "\n$(YELLOW)Info:$(NC)\n"
	@printf "  help                       - show this help message\n"
