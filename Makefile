.PHONY: install test lint format clean build check review metrics ci help

# ═══════════════════════════════════════════════════════════════════
# Mega-Coding Makefile — Principal Engineer Edition
# ═══════════════════════════════════════════════════════════════════

install:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest -v --tb=short --cov=src --cov-report=term-missing

lint:
	@echo "🔍 Running linters..."
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff format src/ tests/

check:
	@echo "⚡ Running full quality check..."
	python scripts/check-quality.py src/
	python scripts/security-check.py src/
	python scripts/check-complexity.py src/
	python scripts/check-types.py src/

review:
	@echo "🌳 Running code review + tree voting..."
	python scripts/code-review-bot.py --path src/
	python scripts/tree-voting/evaluate.py src/

metrics:
	@echo "📊 Collecting quality metrics..."
	python metrics/quality-metrics.py src/ --save current
	python metrics/quality-metrics.py src/ --diff previous || true

ci: lint test
	@echo "⚡ Running CI pipeline..."
	python scripts/mega.py check src/
	python scripts/mega.py review src/
	python scripts/mega.py metrics src/

clean:
	rm -rf .pytest_cache __pycache__
	rm -rf *.egg-info dist build
	rm -rf .coverage coverage.xml
	rm -rf .mypy_cache .ruff_cache
	find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

build: test lint
	python -m build

dev:
	@echo "🚀 Starting development server..."
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t mega-coding:latest .

docker-run:
	docker run -p 8000:8000 mega-coding:latest

update:
	@echo "📦 Updating dependencies..."
	pip install --upgrade pip
	pip install -e ".[dev]"
	pre-commit autoupdate

help:
	@echo "Mega-Coding Makefile"
	@echo "━━━━━━━━━━━━━━━━━━━"
	@echo "install   — Install dependencies + pre-commit hooks"
	@echo "test      — Run tests with coverage"
	@echo "lint      — Run ruff linter + formatter check"
	@echo "format    — Auto-format code with ruff"
	@echo "check     — Full quality check (security, complexity, types)"
	@echo "review    — Code review + tree voting"
	@echo "metrics   — Collect quality metrics and show diff"
	@echo "ci        — Full CI pipeline (lint + test + check + review)"
	@echo "clean     — Clean build artifacts"
	@echo "build     — Build distribution"
	@echo "dev       — Start dev server with hot reload"
	@echo "docker    — Build/run Docker container"
	@echo "update    — Update dependencies"
