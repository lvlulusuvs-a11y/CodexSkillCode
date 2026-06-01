# Production Python

**Как писать Python для продакшена. От первого коммита до деплоя.**

---

## 1. pyproject.toml

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "myapp"
version = "0.1.0"
description = "Production Python application"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [{name = "Developer", email = "dev@example.com"}]

dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.29.0",
    "sqlalchemy[asyncio]>=2.0.30",
    "asyncpg>=0.29.0",
    "alembic>=1.13.0",
    "pydantic>=2.7.0",
    "pydantic-settings>=2.2.0",
    "redis[hiredis]>=5.0.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=5.0",
    "ruff>=0.4.0",
    "mypy>=1.9.0",
    "pre-commit>=3.7.0",
]

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM", "ARG", "C4"]

[tool.mypy]
strict = true
python_version = "3.12"
warn_unused_ignores = true
warn_redundant_casts = true
warn_unused_configs = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

## 2. ASGI Entry Point

```python
# asgi.py
import uvicorn
from src.main import app

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
        workers=4,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
```

## 3. Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir build && \
    pip install --no-cache-dir -e ".[dev]" && \
    python -m build --wheel

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /app/dist/*.whl .
RUN pip install --no-cache-dir *.whl && rm *.whl && \
    groupadd -r app && useradd -r -g app app && \
    mkdir -p /data && chown app:app /data
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
CMD ["uvicorn", "myapp.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 4. Application Configuration

```python
# config.py
from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

@dataclass(frozen=True)
class DatabaseConfig:
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_pre_ping: bool = True
    echo: bool = False

@dataclass(frozen=True)  
class RedisConfig:
    url: str = "redis://localhost:6379/0"
    socket_timeout: float = 5.0
    retry_on_timeout: bool = True

@dataclass(frozen=True)
class AuthConfig:
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

@dataclass(frozen=True)
class Settings:
    app_name: str = "MyApp"
    debug: bool = False
    log_level: str = "INFO"
    database: DatabaseConfig = field(default_factory=lambda: DatabaseConfig(
        url=os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost:5432/app"),
    ))
    redis: RedisConfig = field(default_factory=lambda: RedisConfig(
        url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    ))
    auth: AuthConfig = field(default_factory=lambda: AuthConfig(
        secret_key=os.getenv("SECRET_KEY", "change-me-in-production"),
    ))

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

## 5. Database Setup

```python
# database.py
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database.url,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_pre_ping=settings.database.pool_pre_ping,
    echo=settings.database.echo,
)

SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

class Base(DeclarativeBase):
    pass

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db() -> None:
    await engine.dispose()

async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

## 6. Health Check

```python
# health.py
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

@dataclass
class HealthCheck:
    name: str
    _checks: dict[str, Any] = field(default_factory=dict)
    _start_time: float = field(default_factory=time.monotonic)
    
    def add_check(self, name: str, check_func: Any) -> None:
        self._checks[name] = check_func
    
    async def check(self) -> dict[str, Any]:
        status = "healthy"
        details = {}
        
        for name, check_func in self._checks.items():
            try:
                result = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
                details[name] = {"status": "ok", "detail": result}
            except Exception as e:
                details[name] = {"status": "error", "detail": str(e)}
                status = "degraded"
        
        return {
            "status": status,
            "version": "1.0.0",
            "uptime": time.monotonic() - self._start_time,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": details,
        }

health = HealthCheck("app")

async def check_database() -> str:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return "database ok"

async def check_redis() -> str:
    await redis.ping()
    return "redis ok"

health.add_check("database", check_database)
health.add_check("redis", check_redis)

@router.get("/health")
async def health_endpoint() -> dict[str, Any]:
    return await health.check()
```

## 7. Middleware Stack

```python
# middleware.py
from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[..., Awaitable[Response]]) -> Response:
        request_id = uuid.uuid4().hex[:8]
        structlog.contextvars.bind_contextvars(request_id=request_id)
        
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        
        logger.info(
            "request_completed",
            method=request.method,
            path=str(request.url),
            status=response.status_code,
            duration_ms=f"{duration*1000:.0f}",
        )
        
        response.headers["X-Request-ID"] = request_id
        return response

class CORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method == "OPTIONS":
            return Response(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    "Access-Control-Max-Age": "3600",
                },
            )
        
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
```

## 8. Error Handlers

```python
# exceptions.py
from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

class AppError(Exception):
    def __init__(self, message: str, code: str | None = None, status_code: int = 400) -> None:
        self.message = message
        self.code = code or type(self).__name__
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message=message, status_code=404)

class ConflictError(AppError):
    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__(message=message, status_code=409)

class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message=message, status_code=422)

class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message=message, status_code=401)

class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message=message, status_code=403)

def setup_error_handlers(app: Any) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "app_error",
            path=str(request.url),
            error=exc.message,
            code=exc.code,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.code, "message": exc.message},
        )
    
    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_error", path=str(request.url))
        return JSONResponse(
            status_code=500,
            content={"error": "INTERNAL_ERROR", "message": "Internal server error"},
        )
```

## 9. Rate Limiter

```python
# ratelimit.py
from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request

class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._requests: dict[str, list[float]] = {}
    
    async def check(self, key: str, max_requests: int = 100, window: float = 60.0) -> bool:
        now = time.monotonic()
        cutoff = now - window
        
        if key not in self._requests:
            self._requests[key] = []
        
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]
        
        if len(self._requests[key]) >= max_requests:
            return False
        
        self._requests[key].append(now)
        return True

rate_limiter = InMemoryRateLimiter()

async def rate_limit_middleware(request: Request, call_next: Callable) -> Any:
    client_ip = request.client.host if request.client else "unknown"
    
    if not await rate_limiter.check(f"ip:{client_ip}"):
        raise HTTPException(status_code=429, detail="Too many requests")
    
    return await call_next(request)
```

## 10. Logging Setup

```python
# logging_setup.py
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }
        
        if hasattr(record, "extra"):
            log_entry.update(record.extra)
        
        return json.dumps(log_entry, default=str)

def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    
    # Убрать дублирование из uvicorn
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logging.getLogger(logger_name).handlers.clear()
        logging.getLogger(logger_name).propagate = False
```


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
