# Advanced Type Hints

**Продвинутые приёмы типизации в Python.**

---

## 1. TypeVar + Generic

```python
from typing import TypeVar, Generic

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

class Repository(Generic[T]):
    def get(self, id: int) -> T | None: ...
    def list(self) -> list[T]: ...

# Ограниченные TypeVar
Number = TypeVar("Number", int, float, complex)
class Vector(Generic[Number]):
    def __init__(self, x: Number, y: Number) -> None: ...

# Bound (подтипы)
ModelType = TypeVar("ModelType", bound=BaseModel)
```

## 2. ParamSpec (для декораторов)

```python
from typing import ParamSpec, TypeVar
from functools import wraps

P = ParamSpec("P")
T = TypeVar("T")

def retry(max_attempts: int = 3) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Декоратор с сохранением сигнатуры."""
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for _ in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    pass
            raise RuntimeError
        return wrapper
    return decorator
```

## 3. TypedDict

```python
from typing import TypedDict, NotRequired

class UserDict(TypedDict):
    id: int
    name: str
    email: str
    age: NotRequired[int]  # необязательное поле

user: UserDict = {"id": 1, "name": "Alice", "email": "alice@test.com"}
```

## 4. Literal + Final

```python
from typing import Literal, Final

# Literal: конкретные значения
def set_mode(mode: Literal["read", "write", "append"]) -> None: ...

# Final: константы
MAX_RETRIES: Final = 3
DEFAULT_TIMEOUT: Final[float] = 30.0

# TypeAlias (Python 3.10+)
type JSON = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
type Callback = Callable[..., Any]
```

## 5. Protocol (duck typing)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Stream(Protocol):
    def read(self, size: int) -> bytes: ...
    def write(self, data: bytes) -> int: ...

class FileStream:
    def read(self, size: int) -> bytes: ...
    def write(self, data: bytes) -> int: ...

def process(stream: Stream) -> None:  # любой объект с read/write
    data = stream.read(1024)
```


---

## Production-Grade Implementation

```python
"""Production-grade patterns — battle-tested in Big Tech."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProductionReady:
    """Pattern with proper error handling, retry, and observability."""
    
    async def execute(self) -> dict[str, Any]:
        try:
            async with asyncio.timeout(30):
                result = await self._process()
                logger.info("Success", extra={"result": result})
                return result
        except asyncio.TimeoutError:
            logger.error("Timeout")
            raise
        except Exception:
            logger.exception("Error")
            raise


## Principal Engineer Best Practices

### Error Handling
- Always use specific exceptions (never bare except)
- Always log with context (request_id, user_id, trace_id)
- Always have fallbacks for critical dependencies
- Always set timeouts on external calls

### Performance
- Profile before optimizing (don't guess)
- Use appropriate data structures (dict vs list vs set)
- Batch database operations (never N+1)
- Cache aggressively but with TTL

### Observability
- Add metrics to all external calls
- Add structured logging with correlation IDs
- Add health check endpoints
- Add distributed tracing

### Security
- Validate all inputs (parse, don't validate)
- Never log secrets or PII
- Use parameterized queries (no SQL injection)
- Keep dependencies updated

### Operations
- Feature flags for gradual rollout
- Circuit breakers for dependencies
- Graceful shutdown with proper ordering
- Connection pooling with health checks


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
