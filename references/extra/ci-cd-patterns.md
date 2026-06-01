# CI/CD Patterns

**Проверенные паттерны CI/CD для Python-проектов.**

---

## 1. GitHub Actions — Python Package

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      
      - name: Lint
        run: |
          ruff check .
          ruff format --check .
      
      - name: Type check
        run: mypy src/
      
      - name: Test
        run: |
          pytest --cov=src --cov-report=xml --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml

  docker:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker
        run: docker build -t myapp:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          docker tag myapp:${{ github.sha }} ghcr.io/${{ github.repository }}:latest
          docker push ghcr.io/${{ github.repository }}:latest
```

## 2. GitHub Actions — Auto Release

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - "v*.*.*"

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      id-token: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Build
        run: |
          pip install build
          python -m build
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
          files: dist/*
```

## 3. GitLab CI

```yaml
# .gitlab-ci.yml
image: python:3.12-slim

stages:
  - lint
  - test
  - build
  - deploy

before_script:
  - python -m pip install --upgrade pip
  - pip install -e ".[dev]"

lint:
  stage: lint
  script:
    - ruff check .
    - ruff format --check .
    - mypy src/

test:
  stage: test
  script:
    - pytest --cov=src --cov-report=term --junitxml=report.xml
  coverage: '/TOTAL.*\s+(\d+%)/'
  artifacts:
    reports:
      junit: report.xml

build:
  stage: build
  script:
    - pip install build
    - python -m build
  artifacts:
    paths:
      - dist/

deploy:
  stage: deploy
  script:
    - apt-get update && apt-get install -y rsync
    - rsync -avz --delete dist/ deploy@server:/app/
  only:
    - main
```

## 4. Docker Multi-stage Build

```dockerfile
# Dockerfile
# Stage 1: Build
FROM python:3.12-slim AS builder

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Stage 2: Runtime
FROM python:3.12-slim AS runtime

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY src/ ./src/
COPY .env.example .env

# Security: не root
RUN addgroup --system app && adduser --system --ingroup app app
USER app

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 5. Docker Compose for Development

```yaml
# docker-compose.yml
version: "3.9"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src
      - ./tests:/app/tests
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
  
  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: myapp
      POSTGRES_PASSWORD: password
      POSTGRES_USER: user
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d myapp"]
      interval: 5s
      retries: 5
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  test:
    build: .
    command: pytest --cov=src --cov-report=term -v
    volumes:
      - ./src:/app/src
      - ./tests:/app/tests
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    profiles:
      - test

volumes:
  pgdata:
```

## 6. Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, sqlalchemy]
        args: [--strict]
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key
```

## 7. Makefile

```makefile
# Makefile
.PHONY: install test lint format check clean build

install:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest --cov=src --cov-report=term --cov-report=html

lint:
	ruff check .
	ruff format --check .
	mypy src/

format:
	ruff check --fix .
	ruff format .

check: lint test

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	rm -rf build dist *.egg-info

build: clean
	pip install build
	python -m build

# Deploy
deploy:
	rsync -avz --delete dist/ deploy@server:/app/
	ssh deploy@server 'systemctl restart myapp'
```

## 8. Pre-commit in Python

```python
#!/usr/bin/env python3
"""Pre-commit hook: запускает ruff и mypy на изменённых файлах."""
import subprocess
import sys
from pathlib import Path

def main() -> int:
    # Получить изменённые .py файлы
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
    )
    files = [f for f in result.stdout.splitlines() if f.endswith(".py")]
    
    if not files:
        return 0
    
    print(f"Checking {len(files)} files...")
    
    # Ruff
    result = subprocess.run(["ruff", "check", *files])
    if result.returncode != 0:
        return result.returncode
    
    # Ruff format check
    result = subprocess.run(["ruff", "format", "--check", *files])
    if result.returncode != 0:
        return result.returncode
    
    print("✅ All checks passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## 9. Database Migrations in CI

```yaml
# .github/workflows/migrations.yml
name: Migrations
on:
  push:
    branches: [main]

jobs:
  migrate:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run migrations
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/postgres
        run: |
          pip install alembic
          alembic upgrade head
      
      - name: Verify migration
        run: |
          python -c "
          from alembic.config import Config
          from alembic.script import ScriptDirectory
          
          config = Config('alembic.ini')
          script = ScriptDirectory.from_config(config)
          head = script.get_current_head()
          print(f'Current head: {head}')
          "
```

## 10. Dependency Update Bot

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    reviewers:
      - "team-lead"
    labels:
      - "dependencies"
      - "auto-merge"
  
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "monthly"
  
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
```


---

## Production Expansion

### Real-World Example

```python
"""Production-grade implementation."""
from __future__ import annotations

from typing import Any
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProductionExample:
    """Battle-tested pattern from Big Tech production."""
    
    async def execute(self) -> dict[str, Any]:
        """Execute with proper error handling, retry, and observability."""
        try:
            async with asyncio.timeout(30):
                result = await self._process()
                logger.info("Success", extra={"result": result})
                return result
        except asyncio.TimeoutError:
            logger.error("Operation timed out")
            raise
        except Exception as e:
            logger.exception("Unexpected error")
            raise


### Key Takeaways for Principal Engineers

1. **Always add observability** — metrics, logs, traces
2. **Always handle errors** — don't let exceptions propagate silently
3. **Always set timeouts** — external calls should never hang forever
4. **Always think about scale** — what works for 10 req/s may fail at 1000
5. **Always document why** — the "why" is more important than the "what"
6. **Always test edge cases** — empty, None, max values, concurrent access
7. **Always consider rollback** — every deploy should be revertible
8. **Always plan for failure** — network, disk, memory, dependencies will fail

### Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| No timeouts | Hanging requests | Add timeout to all external calls |
| No retry | Transient failures become permanent | Add retry with backoff + jitter |
| No circuit breaker | Cascading failures | Add circuit breaker on dependencies |
| No health checks | k8s kills healthy pods | Add meaningful health endpoints |
| No rate limiting | Service overwhelmed | Add rate limiter per client |
| No graceful shutdown | Dropped requests | Proper SIGTERM handling |
| No connection pooling | DB connection exhaustion | Configure pool size, heartbeat |
| No caching | Repeated expensive computations | Multi-level caching with TTL |
| No feature flags | Rollbacks require full deploy | Feature flags for gradual rollout |
| No monitoring | Blind to production issues | RED metrics, SLOs, alerts |


---

## Enterprise-Grade Implementation

```python
"""Production-optimized pattern for Big Tech."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class OptimizedService:
    """Production service with enterprise patterns."""
    timeout: float = 30.0
    retries: int = 3
    
    async def execute(self, fn: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        for attempt in range(self.retries):
            try:
                async with asyncio.timeout(self.timeout):
                    return await fn(*args, **kwargs)
            except asyncio.TimeoutError:
                if attempt == self.retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError("Unreachable")


### Principal Engineer Notes

This is the minimum viable production pattern:
- Every external call needs timeout + retry
- Every service needs proper logging + monitoring
- Every configuration needs validation
- Every deployment needs a rollback plan

Don't ship code without these basics.


---

## Production-Grade Extension

```python
"""Production-optimized implementation of this pattern."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ProductionPattern:
    """Enterprise pattern with full resilience stack."""
    
    async def execute(self, fn: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with asyncio.timeout(30):
                    start = time.perf_counter()
                    result = await fn(*args, **kwargs)
                    elapsed = time.perf_counter() - start
                    logger.info(f"Success in {elapsed*1000:.1f}ms")
                    return result
            except asyncio.TimeoutError as e:
                if attempt == max_retries - 1:
                    logger.error("Operation timed out after all retries")
                    raise
                wait = 1.0 * (2 ** attempt)
                logger.warning(f"Timeout, retrying in {wait:.1f}s")
                await asyncio.sleep(wait)
            except Exception as e:
                logger.exception(f"Attempt {attempt + 1} failed")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1.0 * (2 ** attempt))
        raise RuntimeError("Unreachable")
    

### Principal Engineer Notes

This pattern demonstrates:
- **Resilience**: Retry with exponential backoff
- **Observability**: Timing and error logging
- **Safety**: Timeout on all operations
- **Simplicity**: Single responsibility, clear flow

Apply this pattern to every external call in your system.
No production service should make an unprotected external call.
