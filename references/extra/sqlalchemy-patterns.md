# SQLAlchemy 2.0 Patterns

**Проверенные паттерны работы с SQLAlchemy 2.0 async. Реальные продакшен-приёмы.**

---

## 1. Engine + Session (asyncio)

```python
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncSession, 
    async_sessionmaker,
)

# Engine — один на весь проект
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost:5432/db",
    pool_size=10,           # постоянных соединений
    max_overflow=20,        # доп. при нагрузке
    pool_pre_ping=True,     # проверка здоровья
    echo=False,             # SQL логи (только dev)
)

# SessionFactory — один на весь проект
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,  # доступ к объектам после commit
    class_=AsyncSession,
)
```

## 2. Repository Pattern

```python
from collections.abc import Sequence
from typing import Any, TypeVar

T = TypeVar("T")

class BaseRepository(Generic[T]):
    """Базовый репозиторий с CRUD."""
    
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

# Конкретный репозиторий
class UserRepository(BaseRepository[User]):
    _model = User
    
    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_active(self, limit: int = 100) -> Sequence[User]:
        stmt = select(User).where(User.is_active == True).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()
    
    async def count_active(self) -> int:
        stmt = select(func.count(User.id)).where(User.is_active == True)
        result = await self._session.execute(stmt)
        return result.scalar() or 0
```

## 3. Unit of Work (Transaction Management)

```python
from contextlib import asynccontextmanager

class UnitOfWork:
    """Управление транзакциями с DI."""
    
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session_factory
    
    @asynccontextmanager
    async def __call__(self) -> AsyncIterator[AsyncSession]:
        async with self._factory() as session:
            try:
                async with session.begin():
                    yield session
                # session.commit() вызывается автоматически при выходе из session.begin()
            except Exception:
                # session.rollback() вызывается автоматически
                raise

# Использование:
uow = UnitOfWork(AsyncSessionLocal)

@asynccontextmanager
async def get_db() -> AsyncIterator[AsyncSession]:
    """Dependency injection для FastAPI."""
    async with uow() as session:
        yield session
```

## 4. Pagination (Cursor vs Offset)

```python
# Offset пагинация (простая)
@app.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> list[User]:
    stmt = select(User).offset(skip).limit(limit).order_by(User.id)
    result = await db.execute(stmt)
    return result.scalars().all()

# Cursor пагинация (для больших таблиц)
@app.get("/users/cursor")
async def list_users_cursor(
    cursor: int | None = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> dict:
    stmt = select(User)
    if cursor:
        stmt = stmt.where(User.id > cursor)
    stmt = stmt.order_by(User.id).limit(limit + 1)
    
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    has_more = len(users) > limit
    next_cursor = users[-2].id if has_more else None
    
    return {
        "data": users[:limit],
        "next_cursor": next_cursor,
        "has_more": has_more,
    }
```

## 5. Eager Loading (N+1 prevention)

```python
from sqlalchemy.orm import selectinload, joinedload

# ❌ N+1: для каждого user отдельный запрос к orders
users = await db.execute(select(User))
for user in users.scalars():
    print(user.orders)  # N дополнительных запросов

# ✅ selectinload: один запрос на всех
stmt = select(User).options(selectinload(User.orders))
users = await db.execute(stmt)
for user in users.scalars():
    print(user.orders)  # нет доп. запросов

# joinedload: JOIN в одном запросе (для многих-к-одному)
stmt = select(Order).options(joinedload(Order.user))
orders = await db.execute(stmt)
for order in orders.scalars():
    print(order.user.name)  # уже загружен
```

## 6. Soft Delete

```python
from sqlalchemy import event

class SoftDeleteMixin:
    """Mixin для soft delete (логическое удаление)."""
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    def soft_delete(self) -> None:
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)

class User(Base, SoftDeleteMixin):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_not_deleted", "is_deleted", postgresql_where=not_(text("is_deleted"))),
    )

# Фильтр по умолчанию
@event.listens_for(select(User), "before_compile", retval=True)
def _add_filter(query: Any) -> Any:
    # Автоматически добавлять WHERE NOT is_deleted
    for desc in query.column_descriptions:
        entity = desc["entity"]
        if hasattr(entity, "is_deleted"):
            query = query.where(entity.is_deleted == False)
    return query
```

## 7. Audit Log (CUD события)

```python
class Auditable:
    """Mixin для аудита изменений."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

class Product(Base, Auditable):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[float]
```

## 8. JSON/JSONB fields

```python
# PostgreSQL JSONB (с индексами)
class Event(Base):
    __tablename__ = "events"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    
    __table_args__ = (
        Index("ix_events_payload", payload, postgresql_using="gin"),
    )

# Запросы к JSONB
stmt = select(Event).where(Event.payload["user_id"].as_integer() == 42)
stmt = select(Event).where(Event.payload.has_key("email"))
```

## 9. Database migrations (Alembic)

```python
# alembic init migrations
# alembic revision --autogenerate -m "add users"
# alembic upgrade head

# Важные команды:
# alembic history        — история миграций
# alembic current        — текущая версия
# alembic downgrade -1   — откатить на 1 шаг
# alembic merge heads    — слить конфликтующие миграции
```

## 10. Async Session Mixin

```python
class AsyncSessionMixin:
    """Упрощает работу с async session в тестах."""
    
    @pytest_asyncio.fixture
    async def db_session(self) -> AsyncIterator[AsyncSession]:
        engine = create_async_engine("sqlite+aiosqlite://")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with AsyncSession(engine, expire_on_commit=False) as session:
            yield session
        
        await engine.dispose()
    
    @pytest_asyncio.fixture
    async def user_repo(self, db_session) -> UserRepository:
        return UserRepository(db_session)
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
