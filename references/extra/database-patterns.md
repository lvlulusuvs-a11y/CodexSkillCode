# Database Patterns

**Проверенные паттерны работы с БД в Python.**

---

## 1. Connection Management

```python
# Connection pool (обязательно)
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,           # постоянные соединения
    max_overflow=20,        # доп. при пике
    pool_pre_ping=True,     # проверка здоровья
    pool_recycle=3600,      # пересоздавать каждый час
    echo=False,             # SQL логи в dev
)
```

## 2. Repository Pattern

```python
from typing import Any, TypeVar, Generic

T = TypeVar("T")

class BaseRepository(Generic[T]):
    """CRUD с типизацией."""
    
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def get(self, id: Any) -> T | None:
        return await self._session.get(self._model, id)
    
    async def list(self, skip: int = 0, limit: int = 100) -> Sequence[T]:
        stmt = select(self._model).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()
    
    async def add(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.flush()
        return entity
    
    async def delete(self, entity: T) -> None:
        await self._session.delete(entity)
        await self._session.flush()
```

## 3. Unit of Work (Transaction)

```python
from contextlib import asynccontextmanager

class UnitOfWork:
    """Управление транзакциями."""
    
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    @asynccontextmanager
    async def __call__(self) -> AsyncIterator[AsyncSession]:
        try:
            async with self._session.begin():
                yield self._session
        except Exception:
            await self._session.rollback()
            raise
```

## 4. Cursor Pagination

```python
# Для таблиц >100K записей — cursor, не offset
async def list_users(cursor: str | None = None, limit: int = 100) -> dict:
    stmt = select(User).order_by(User.id).limit(limit + 1)
    
    if cursor:
        stmt = stmt.where(User.id > cursor)
    
    result = await session.execute(stmt)
    users = result.scalars().all()
    
    has_more = len(users) > limit
    next_cursor = users[-2].id if has_more else None
    
    return {
        "data": [u.to_dict() for u in users[:limit]],
        "next_cursor": next_cursor,
        "has_more": has_more,
    }
```

## 5. N+1 Prevention

```python
# N+1: slow query
users = await db.execute(select(User))
for user in users.scalars():
    print(user.orders)  # ❌ N доп. запросов

# Fix: eager loading
from sqlalchemy.orm import selectinload

stmt = select(User).options(selectinload(User.orders))
users = await db.execute(stmt)
for user in users.scalars():
    print(user.orders)  # ✅ 1 запрос
```

## 6. Soft Delete

```python
class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    def soft_delete(self) -> None:
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
```

## 7. Audit Log

```python
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
```

## 8. Query Optimization

```python
# Только нужные поля
stmt = select(User.id, User.name, User.email)  # ❌ не select(User)

# Пагинация
stmt = stmt.limit(limit).offset(offset)

# Индексы
class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email", "email"),  # для поиска по email
        Index("ix_users_created", "created_at"),  # для сортировки
    )
```

## 9. Read Replicas

```python
# Разделение чтения и записи
writer = create_async_engine(PRIMARY_URL)
reader = create_async_engine(REPLICA_URL)

class Router(Session):
    def get_bind(self, *args, **kwargs):
        if self._flushing or self.info.get("write"):
            return writer.sync_engine
        return reader.sync_engine
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
