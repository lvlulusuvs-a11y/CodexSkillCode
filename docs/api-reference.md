# Mega-Coding API Reference

**Complete API documentation for all mega-coding tools, scripts, and integrations.**

---

## 1. Unified CLI (`scripts/mega.py`)

### mega lint
```bash
python scripts/mega.py lint [path]
# Runs: ruff check, ruff format --check, mypy, bandit
# Default path: "."
```

### mega review
```bash
python scripts/mega.py review [path]
# 1. Static analysis (code-review-bot)
# 2. Tree voting (tree-voting/evaluate.py)
# Returns: exit code = number of issues found
```

### mega check
```bash
python scripts/mega.py check [path]
# Full quality check pipeline:
# 1. Syntax validation
# 2. Complexity analysis
# 3. Docstrings check
# 4. Type hints check
# 5. Security scan
# 6. Dead code detection
# 7. Unused imports
# 8. Trees Club evaluation
# 9. Quality metrics
```

### mega metrics
```bash
python scripts/mega.py metrics [path]
# Collects: total functions, avg complexity, type hint ratio, etc.
# Output: Health score 0-100
```

### mega diff
```bash
python scripts/mega.py diff [commit]
# Analyzes changes between commit and HEAD
# Shows complexity changes per file
```

### mega ci
```bash
python scripts/mega.py ci
# Full CI pipeline:
# 1. pytest (tests)
# 2. mega check (quality)
# 3. mega metrics (metrics)
```

## 2. Trees Club (`scripts/tree-voting/evaluate.py`)

### File Evaluation
```bash
python scripts/tree-voting/evaluate.py path/to/file.py
# Output: 6 tree verdicts + pass/fail
```

### Git Diff Evaluation
```bash
python scripts/tree-voting/evaluate.py --diff
# Evaluates only changed lines
```

### CI Integration
```bash
python scripts/tree-voting/evaluate.py src/ --ci
# JSON output for CI parsing
```

### PR Comments
```bash
python scripts/tree-voting/evaluate.py --pr-comment
# GitHub PR comment format with badges
```

## 3. Quality Metrics (`metrics/quality-metrics.py`)

### Collect Metrics
```bash
python metrics/quality-metrics.py src/
# CSV/JSON output with all quality dimensions
```

### Save Snapshot
```bash
python metrics/quality-metrics.py src/ --save v1.0
# Saves to ~/.mega-coding/metrics/v1.0.json
```

### Compare
```bash
python metrics/quality-metrics.py src/ --diff v1.0
# Shows quality improvement/regression
```

### Dashboard
```bash
python metrics/quality-metrics.py src/ --dashboard
# Shows trend over all saved snapshots
```

## 4. Code Review Bot (`scripts/code-review-bot.py`)

### File Review
```bash
python scripts/code-review-bot.py --path src/myfile.py
# Analyzes single file or directory
```

### Git Diff
```bash
git diff main..feature | python scripts/code-review-bot.py
# Reviews staged changes
```

### Commit Review
```bash
python scripts/code-review-bot.py --commit HEAD~1
# Reviews specific commit
```

## 5. Individual Check Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| lint-runner.py | `python scripts/lint-runner.py` | Run all linters |
| check-quality.py | `python scripts/check-quality.py src/` | 15 quality checks |
| check-complexity.py | `python scripts/check-complexity.py src/` | Cyclomatic complexity |
| check-dead-code.py | `python scripts/check-dead-code.py src/` | Dead code detection |
| check-docstrings.py | `python scripts/check-docstrings.py src/` | Docstring coverage |
| check-types.py | `python scripts/check-types.py src/` | Type hints coverage |
| check-unused-imports.py | `python scripts/check-unused-imports.py src/` | Unused imports |
| security-check.py | `python scripts/security-check.py src/` | Security vulnerabilities |
| benchmark.py | `python scripts/benchmark.py` | Performance benchmarking |

## 6. Makefile Targets

```bash
make install    # Install dependencies + pre-commit
make test       # Run tests with coverage
make lint       # Run ruff linter
make format     # Auto-format with ruff
make check      # Full quality check
make review     # Code review + trees
make metrics    # Quality metrics
make ci         # Full CI pipeline
make clean      # Clean artifacts
make build      # Build distribution
```

## 7. GitHub Actions Integration

### Full CI Workflow
```yaml
name: Mega-Coding CI
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: mypy src/
      - run: python scripts/mega.py check src/
      - run: python scripts/tree-voting/evaluate.py src/ --ci
      - run: python metrics/quality-metrics.py src/
```

## 8. Pre-commit Hooks

```yaml
repos:
  - repo: local
    hooks:
      - id: mega-check
        name: Mega-Coding Quality Check
        entry: python scripts/check-quality.py
        language: system
        files: \.py$
      - id: mega-trees
        name: Trees Club Evaluation
        entry: python scripts/tree-voting/evaluate.py
        language: system
        files: \.py$
```
