# Error Handling Patterns

**Как обрабатывать ошибки в продакшене. От 404 до circuit breaker.**

---

## 1. Кастомные исключения

```python
# Иерархия исключений приложения
class AppError(Exception):
    """Base exception for the application."""
    def __init__(self, message: str, code: str | None = None, details: dict | None = None) -> None:
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

class NotFoundError(AppError):
    """Resource not found."""
    status_code = 404

class ConflictError(AppError):
    """Resource conflict."""
    status_code = 409

class ValidationError(AppError):
    """Validation failed."""
    status_code = 422

class UnauthorizedError(AppError):
    """Authentication failed."""
    status_code = 401

class ForbiddenError(AppError):
    """Permission denied."""
    status_code = 403

class ServiceError(AppError):
    """External service error."""
    status_code = 502

# Использование
async def get_user(user_id: int) -> User:
    if user := await repo.get(user_id):
        return user
    raise NotFoundError(f"User {user_id} not found", code="USER_NOT_FOUND")
```

## 2. Global Exception Handler (FastAPI)

```python
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse

def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning("app_error", 
                      path=str(request.url),
                      error=exc.message,
                      code=exc.code,
                      details=exc.details)
        return JSONResponse(
            status_code=getattr(exc, "status_code", 500),
            content={
                "error": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )
    
    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_error", path=str(request.url))
        return JSONResponse(
            status_code=500,
            content={"error": "INTERNAL_ERROR", "message": "Internal server error"},
        )
    
    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "HTTP_ERROR", "message": exc.detail},
        )
```

## 3. Error Boundary (Layer Pattern)

```python
# Repository layer — database errors
class UserRepository:
    async def get(self, user_id: int) -> User:
        try:
            return await self._session.get(User, user_id)
        except SQLAlchemyError as e:
            logger.error("db_error", operation="get_user", user_id=user_id, error=str(e))
            raise ServiceError("Database error") from e

# Service layer — business logic errors  
class UserService:
    async def register(self, email: str, password: str) -> User:
        try:
            existing = await self._repo.get_by_email(email)
            if existing:
                raise ConflictError(f"Email {email} already registered")
            return await self._repo.create({"email": email, "password": hash(password)})
        except AppError:
            raise  # пропускаем наши ошибки
        except Exception as e:
            logger.exception("unexpected_error")
            raise ServiceError("Registration failed") from e

# API/Handler layer — catch all, return appropriate response
@router.post("/users")
async def register(data: RegisterSchema, service: UserService = Depends(get_user_service)):
    try:
        user = await service.register(data.email, data.password)
        return UserResponse.from_orm(user)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=e.message)
```

## 4. Result Type (Functional Error Handling)

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Any

T = TypeVar("T")
E = TypeVar("E")

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

@dataclass(frozen=True)
class Err(Generic[E]):
    error: E

type Result[T, E] = Ok[T] | Err[E]

# Функции возвращают Result вместо исключений
def divide(a: float, b: float) -> Result[float, str]:
    if b == 0:
        return Err("division by zero")
    return Ok(a / b)

def parse_int(s: str) -> Result[int, str]:
    try:
        return Ok(int(s))
    except ValueError:
        return Err(f"cannot parse '{s}' as int")

# Композиция
result = parse_int("42")
match result:
    case Ok(val): print(f"Parsed: {val}")
    case Err(e): print(f"Failed: {e}")

# Chain
def process(input: str) -> Result[float, str]:
    r1 = parse_int(input)
    if isinstance(r1, Err):
        return r1
    return divide(r1.value, 2)
```

## 5. Retry Strategy

```python
import asyncio
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")

# Transient errors — можно retry
TRANSIENT_ERRORS = (
    ConnectionError,
    TimeoutError,
    aiohttp.ClientError,
    asyncpg.TooManyConnectionsError,
)

def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    backoff: float = 2.0,
    jitter: float = 0.1,
) -> Callable:
    """Retry with exponential backoff + jitter."""
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_error = None
            wait = base_delay
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except TRANSIENT_ERRORS as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        delay = wait + random.uniform(0, wait * jitter)
                        logger.warning("Retry %d/%d after %.2fs: %s", 
                                     attempt + 1, max_attempts, delay, e)
                        await asyncio.sleep(delay)
                        wait *= backoff
                except Exception as e:
                    # Non-transient — не retry
                    raise
            
            raise last_error  # type: ignore
        return wrapper
    return decorator
```

## 6. Graceful Error Recovery

```python
class GracefulDegradation:
    """Падай gracefully — не обрушивай всё приложение."""
    
    async def get_recommendations(self, user_id: int) -> list[Product]:
        try:
            return await self._ml_service.recommend(user_id)
        except ServiceError:
            logger.warning("ML service down, falling back to popular")
            return await self._popular_products()
        except Exception:
            logger.exception("Unexpected error in recommendations")
            return []  # Пустой список — лучше ошибки

    async def send_notification(self, user_id: int, message: str) -> bool:
        try:
            await self._push_service.send(user_id, message)
            return True
        except Exception as e:
            logger.error("Failed to send notification", error=str(e))
            # Пробуем fallback
            try:
                await self._email_service.send(user_id, message)
                return True
            except Exception:
                logger.critical("All notification channels failed")
                return False  # Сообщаем, что не удалось
```

## 7. Logging Errors

```python
# Всегда логируй достаточно контекста
try:
    result = await process_order(order_id, user_id, amount)
except Exception as e:
    logger.exception("order_processing_failed",  # включает traceback
                    order_id=order_id,
                    user_id=user_id,
                    amount=amount)
    # ⚠️ Не логируй пароли, токены, PII
    raise
```

## 8. Error Response Standard

```python
# Стандартный формат ошибки для API
{
    "error": {
        "code": "USER_NOT_FOUND",
        "message": "User 42 not found",
        "details": {
            "user_id": 42,
            "resource": "User"
        },
        "request_id": "abc123",
        "timestamp": "2024-01-15T10:30:00Z"
    }
}

# Pydantic schema
class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = {}
    request_id: str = ""
    timestamp: str = ""
```


---

## Enterprise Implementation Patterns

### Production-Grade Code

```python
"""Enterprise-grade implementation with full resilience."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
import functools
import random

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class EnterpriseService:
    """Production service with all resilience patterns."""
    
    max_retries: int = 3
    timeout_seconds: float = 30.0
    circuit_breaker_threshold: int = 5
    
    def __post_init__(self):
        self._circuit_open = False
        self._failure_count = 0
        self._last_failure_time = 0.0
    
    async def call_with_resilience(
        self,
        fn: Callable[..., Awaitable[T]],
        fallback: Callable[..., Awaitable[T]] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Execute with circuit breaker + retry + timeout."""
        if self._circuit_open:
            if time.monotonic() - self._last_failure_time < 30.0:
                if fallback:
                    return await fallback(*args, **kwargs)
                raise RuntimeError("Circuit breaker is open")
            self._circuit_open = False
            logger.info("Circuit breaker half-open, testing...")
        
        for attempt in range(self.max_retries + 1):
            try:
                async with asyncio.timeout(self.timeout_seconds):
                    result = await fn(*args, **kwargs)
                    self._failure_count = 0
                    return result
            except asyncio.TimeoutError:
                logger.warning(f"Timeout (attempt {attempt+1})")
                if attempt == self.max_retries:
                    self._record_failure()
                    raise
                await asyncio.sleep(1.0 * (2 ** attempt) + random.uniform(0, 0.5))
            except Exception as e:
                logger.warning(f"Error (attempt {attempt+1}): {e}")
                if attempt == self.max_retries:
                    self._record_failure()
                    if fallback:
                        return await fallback(*args, **kwargs)
                    raise
                await asyncio.sleep(1.0 * (2 ** attempt))
        
        raise RuntimeError("Unreachable")
    
    def _record_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.monotonic()
        if self._failure_count >= self.circuit_breaker_threshold:
            self._circuit_open = True
            logger.error(f"Circuit breaker opened after {self._failure_count} failures")


### Configuration Management

@dataclass
class ServiceSettings:
    """Type-safe configuration from environment variables."""
    service_name: str = "my-service"
    environment: str = "dev"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database
    database_url: str = ""
    db_pool_min: int = 5
    db_pool_max: int = 20
    db_timeout: int = 5
    
    # Cache
    redis_url: str = "redis://localhost:6379"
    cache_default_ttl: int = 300
    
    # API
    port: int = 8000
    workers: int = 4
    cors_origins: list[str] = None
    
    # External services
    external_api_timeout: int = 10
    external_api_retries: int = 3
    
    # Feature flags
    enable_new_feature: bool = False
    
    def validate(self) -> None:
        """Validate configuration on startup."""
        errors = []
        if self.environment == "production":
            if not self.database_url:
                errors.append("DATABASE_URL is required")
            if self.debug:
                errors.append("Debug mode must be disabled in production")
            if "localhost" in (self.database_url or ""):
                errors.append("Cannot use localhost in production")
        if errors:
            raise ValueError("; ".join(errors))
    
    @classmethod
    def from_env(cls) -> "ServiceSettings":
        """Load configuration from environment variables."""
        import os
        return cls(
            service_name=os.getenv("SERVICE_NAME", "my-service"),
            environment=os.getenv("ENVIRONMENT", "dev"),
            debug=os.getenv("DEBUG", "0") == "1",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            database_url=os.getenv("DATABASE_URL", ""),
            db_pool_min=int(os.getenv("DB_POOL_MIN", "5")),
            db_pool_max=int(os.getenv("DB_POOL_MAX", "20")),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            port=int(os.getenv("PORT", "8000")),
            external_api_timeout=int(os.getenv("EXTERNAL_API_TIMEOUT", "10")),
            cors_origins=os.getenv("CORS_ORIGINS", "*").split(","),
        )


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
