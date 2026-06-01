"""FastAPI production template."""
from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr

# ── Models ────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserCreate(BaseModel):
    name: str
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None


# ── Fake repo (заменить на SQLAlchemy) ──
class UserRepo:
    def __init__(self) -> None:
        self._users: dict[int, dict[str, Any]] = {}
        self._next_id = 1

    async def create(self, data: UserCreate) -> dict[str, Any]:
        user = {"id": self._next_id, "name": data.name, "email": data.email}
        self._users[self._next_id] = user
        self._next_id += 1
        return user

    async def get(self, user_id: int) -> dict[str, Any] | None:
        return self._users.get(user_id)

    async def list(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        return list(self._users.values())[skip : skip + limit]


repo = UserRepo()


# ── Lifespan ───────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("starting up")
    # Тут: подключение к БД, инициализация
    yield
    logger.info("shutting down")
    # Тут: закрытие соединений


# ── App ────────────────────────────────────────
app = FastAPI(title="FastAPI Template", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate) -> dict[str, Any]:
    user = await repo.create(data)
    logger.info("user_created", extra={"user_id": user["id"]})
    return user


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int) -> dict[str, Any]:
    if user := await repo.get(user_id):
        return user
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/users", response_model=list[UserResponse])
async def list_users(skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
    return await repo.list(skip, limit)


# ── Error handlers ─────────────────────────────
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Any, exc: HTTPException) -> Any:
    return ErrorResponse(detail=exc.detail)


# ═══════════════════════════════════════════════════════════════════
# Extended Production Implementation
# ═══════════════════════════════════════════════════════════════════

"""Production-grade extensions with error handling, retry, 
monitoring, and graceful shutdown."""

from __future__ import annotations
from typing import Any
from dataclasses import dataclass
import asyncio
import logging
import time
import functools
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


# ── Resilience Patterns ──────────────────────────────────────────

def with_retry(max_retries: int = 3, base_delay: float = 1.0):
    """Retry with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Retry {attempt+1}/{max_retries} in {delay:.1f}s")
                        await asyncio.sleep(delay)
            raise last_error
        return wrapper
    return decorator


@dataclass
class CircuitBreaker:
    """Simple circuit breaker for external dependencies."""
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    
    def __post_init__(self):
        self._failures = 0
        self._last_failure = 0.0
        self._state = "closed"
    
    async def call(self, fn, fallback=None, *args, **kwargs):
        if self._state == "open":
            if time.monotonic() - self._last_failure >= self.recovery_timeout:
                self._state = "half-open"
                logger.info("Circuit half-open, testing recovery")
            elif fallback:
                return await fallback(*args, **kwargs)
            else:
                raise RuntimeError("Circuit breaker is open")
        
        try:
            result = await fn(*args, **kwargs)
            self._failures = 0
            self._state = "closed"
            return result
        except Exception as e:
            self._failures += 1
            self._last_failure = time.monotonic()
            if self._failures >= self.failure_threshold:
                self._state = "open"
                logger.error(f"Circuit opened after {self._failures} failures")
            raise


@asynccontextmanager
async def db_transaction(pool):
    """Database transaction with automatic rollback."""
    conn = await pool.acquire()
    try:
        await conn.execute("BEGIN")
        yield conn
        await conn.execute("COMMIT")
    except Exception:
        await conn.execute("ROLLBACK")
        raise
    finally:
        await pool.release(conn)


# ── Observability ────────────────────────────────────────────────

def monitor(name: str = ""):
    """Monitor function execution time and errors."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                logger.info(f"{name or func.__name__}: {elapsed*1000:.1f}ms")
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start
                logger.error(f"{name or func.__name__} failed after {elapsed*1000:.1f}ms: {e}")
                raise
        return wrapper
    return decorator


# ── Graceful Shutdown ────────────────────────────────────────────

class GracefulShutdown:
    """Managed graceful shutdown with proper ordering."""
    
    def __init__(self):
        self._hooks: list[tuple[str, callable, int]] = []
        self._shutting_down = False
    
    def register(self, name: str, hook: callable, order: int = 10):
        self._hooks.append((name, hook, order))
    
    async def shutdown(self):
        self._shutting_down = True
        logger.info("Initiating graceful shutdown...")
        
        for name, hook, _ in sorted(self._hooks, key=lambda x: -x[2]):
            try:
                async with asyncio.timeout(10):
                    await hook()
                    logger.info(f"Shutdown: {name} completed")
            except asyncio.TimeoutError:
                logger.warning(f"Shutdown: {name} timed out")
            except Exception as e:
                logger.error(f"Shutdown: {name} failed: {e}")
        
        logger.info("Graceful shutdown complete")


# ── Configuration ────────────────────────────────────────────────

@dataclass
class Settings:
    """12-factor app configuration from environment."""
    debug: bool = False
    database_url: str = ""
    redis_url: str = ""
    log_level: str = "INFO"
    api_port: int = 8000
    api_workers: int = 4
    cors_origins: list[str] = None
    jwt_secret: str = ""
    feature_flags: dict[str, bool] = None
    
    @classmethod
    def from_env(cls) -> "Settings":
        import os
        return cls(
            debug=os.getenv("DEBUG", "0") == "1",
            database_url=os.getenv("DATABASE_URL", ""),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            api_port=int(os.getenv("PORT", "8000")),
            api_workers=int(os.getenv("WORKERS", "4")),
            cors_origins=os.getenv("CORS_ORIGINS", "*").split(","),
            jwt_secret=os.getenv("JWT_SECRET", ""),
            feature_flags={
                "new_pipeline": os.getenv("FEATURE_NEW_PIPELINE", "0") == "1",
                "enhanced_search": os.getenv("FEATURE_ENHANCED_SEARCH", "0") == "1",
            },
        )
    
    def validate(self) -> None:
        """Validate critical settings."""
        errors = []
        if not self.database_url:
            errors.append("DATABASE_URL is required")
        if not self.jwt_secret and not self.debug:
            errors.append("JWT_SECRET is required")
        if errors:
            raise ValueError("; ".join(errors))


# ── Health Checks ─────────────────────────────────────────────────

@dataclass
class HealthCheck:
    """Composite health check for microservice."""
    
    async def check_liveness(self) -> dict:
        return {"status": "alive", "timestamp": time.time()}
    
    async def check_readiness(self, deps: dict[str, callable]) -> dict:
        status = "healthy"
        checks = {}
        for name, check_fn in deps.items():
            try:
                async with asyncio.timeout(2):
                    await check_fn()
                checks[name] = "healthy"
            except Exception as e:
                checks[name] = f"unhealthy: {e}"
                status = "unhealthy"
        return {"status": status, "checks": checks}
    
    async def check_startup(self) -> dict:
        return {"status": "started", "timestamp": time.time()}
