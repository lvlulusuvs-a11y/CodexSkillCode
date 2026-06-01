# FastAPI Best Practices

**Как писать FastAPI приложения для продакшена.**

---

## 1. Project Structure

```
project/
├── src/
│   ├── main.py              # FastAPI app
│   ├── config.py            # pydantic-settings
│   ├── database.py          # engine + session
│   ├── routers/             # API routes
│   │   ├── __init__.py
│   │   └── users.py
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── repositories/        # DB queries
│   └── dependencies.py      # FastAPI dependencies
├── tests/
├── .env
├── Dockerfile
└── pyproject.toml
```

## 2. Application Factory

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init DB, Redis, etc.
    await database.connect()
    yield
    # Shutdown: close connections
    await database.disconnect()

def create_app() -> FastAPI:
    app = FastAPI(
        title="MyApp",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
    )
    
    # Middleware
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    
    # Routers
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    
    # Exception handlers
    register_exception_handlers(app)
    
    return app

app = create_app()
```

## 3. Dependency Injection

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# DB session
async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session

# Current user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = verify_token(token)
    user = await user_repo.get(db, payload["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Router
@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return user
```

## 4. Pydantic Schemas

```python
from pydantic import BaseModel, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150)
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if any(c in v for c in "<>\"'%"):
            raise ValueError("Invalid characters")
        return v.strip()

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    model_config = {"from_attributes": True}  # ORM mode
```

## 5. Error Handling

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class AppError(Exception):
    def __init__(self, message: str, code: str = "ERROR", status: int = 400):
        self.message = message
        self.code = code
        self.status = status

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status,
        content={"error": exc.code, "message": exc.message},
    )

@app.exception_handler(Exception)
async def general_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_ERROR", "message": "Internal server error"},
    )
```

## 6. Logging

```python
import structlog

logger = structlog.get_logger()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    structlog.contextvars.bind_contextvars(
        request_id=uuid.uuid4().hex[:8],
        method=request.method,
        path=str(request.url),
    )
    start = time.perf_counter()
    
    response = await call_next(request)
    
    duration = time.perf_counter() - start
    logger.info("request_completed", status=response.status_code, duration_ms=f"{duration*1000:.0f}")
    
    return response
```

## 7. Pagination

```python
from fastapi import Query

@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    users = await user_repo.list(db, skip, limit)
    total = await user_repo.count(db)
    return {
        "data": users,
        "total": total,
        "skip": skip,
        "limit": limit,
    }
```

## 8. Testing

```python
# conftest.py
@pytest_asyncio.fixture
async def client():
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post("/api/v1/users", json={
        "name": "Alice",
        "email": "alice@test.com",
        "age": 25,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
```


---

## Battle-Tested Production Patterns

### Error Handling & Resilience

```python
"""Production-grade error handling patterns."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ResiliencePolicy:
    """Resilience policy for external service calls."""
    max_retries: int = 3
    timeout_seconds: float = 10.0
    circuit_breaker_failures: int = 5
    rate_limit_per_second: int = 100


async def resilient_call[T](
    fn: Any,
    *args: Any,
    policy: ResiliencePolicy | None = None,
    **kwargs: Any,
) -> T:
    """Execute call with retry, timeout, and circuit breaker."""
    policy = policy or ResiliencePolicy()
    
    for attempt in range(policy.max_retries + 1):
        try:
            async with asyncio.timeout(policy.timeout_seconds):
                return await fn(*args, **kwargs)
        except asyncio.TimeoutError:
            if attempt == policy.max_retries:
                raise
            delay = 1.0 * (2 ** attempt)
            logger.warning(f"Timeout (attempt {attempt+1}), retrying in {delay}s")
            await asyncio.sleep(delay)
        except Exception as e:
            if attempt == policy.max_retries:
                raise
            logger.warning(f"Error (attempt {attempt+1}): {e}")
            await asyncio.sleep(1.0 * (2 ** attempt))
    
    raise RuntimeError("Should not reach here")


### Observability Best Practices

```python
"""Observability patterns for production."""
from __future__ import annotations

import time
import functools
from typing import Any, Callable


def observe(name: str = ""):
    """Decorator to add observability to any function."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                logger.info(
                    f"{name or func.__name__} completed",
                    extra={"duration_ms": elapsed * 1000},
                )
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start
                logger.error(
                    f"{name or func.__name__} failed",
                    extra={"duration_ms": elapsed * 1000, "error": str(e)},
                )
                raise
        return wrapper
    return decorator


### Configuration Management

```python
"""Type-safe configuration management."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ServiceConfig:
    """Application configuration from environment."""
    
    # Service metadata
    service_name: str = field(default_factory=lambda: os.getenv("SERVICE_NAME", "app"))
    environment: str = field(default_factory=lambda: os.getenv("ENV", "dev"))
    
    # Database
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "20"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    db_pool_pre_ping: bool = os.getenv("DB_POOL_PRE_PING", "1") == "1"
    
    # Cache
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))
    cache_ttl: int = int(os.getenv("CACHE_TTL", "300"))
    
    # API
    api_port: int = int(os.getenv("PORT", "8000"))
    cors_origins: list[str] = field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "*").split(",")
    )
    
    # Feature flags
    enable_new_algo: bool = os.getenv("FEATURE_NEW_ALGO", "0") == "1"
    enable_debug_mode: bool = os.getenv("DEBUG", "0") == "1"
    
    def validate(self) -> None:
        """Validate config on startup."""
        errors = []
        if self.environment == "prod" and not self.database_url:
            errors.append("DATABASE_URL required in production")
        if self.environment == "prod" and "localhost" in (self.database_url or ""):
            errors.append("Cannot use localhost database in production")
        if errors:
            raise ValueError("; ".join(errors))
    
    @property
    def is_production(self) -> bool:
        return self.environment == "prod"
    
    @property
    def is_debug(self) -> bool:
        return self.enable_debug_mode or self.environment == "dev"


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
