# Advanced Testing Patterns

**Продвинутые техники тестирования для продакшена.**

---

## 1. Snapshot Testing

```python
# pip install pytest-snapshot

def test_api_response(snapshot):
    response = client.get("/users/1")
    snapshot.assert_match(response.json(), "user_response.json")

# При первом запуске создаёт эталон
# При повторных — сравнивает
# Обновить: pytest --snapshot-update
```

## 2. Property-Based Testing

```python
# pip install hypothesis

from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_always_sorted(items):
    result = sorted(items)
    for i in range(len(result) - 1):
        assert result[i] <= result[i + 1]

@given(st.text(), st.text())
def test_string_concat(a, b):
    result = a + b
    assert len(result) == len(a) + len(b)
    assert result.startswith(a)
    assert result.endswith(b)
```

## 3. Freezing Time

```python
from freezegun import freeze_time
from datetime import datetime

@freeze_time("2024-01-15 10:00:00")
def test_order_creation():
    order = create_order(data)
    assert order.created_at == datetime(2024, 1, 15, 10, 0, 0)

# Для async
@freeze_time("2024-01-15")
async def test_async_with_time():
    result = await process()
    assert result["date"] == "2024-01-15"
```

## 4. Testing Database Migrations

```python
# alembic head → downgrade → upgrade test

def test_migration_upgrade(alembic_runner):
    alembic_runner.upgrade("head")
    alembic_runner.downgrade("base")
    alembic_runner.upgrade("head")

# Проверка, что миграции идемпотентны
def test_migration_idempotent(alembic_runner):
    alembic_runner.upgrade("head")
    alembic_runner.downgrade("base")
    alembic_runner.upgrade("head")
    # Никаких ошибок — успех
```

## 5. Load Testing

```python
# pip install locust

from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)
    
    @task(3)
    def view_users(self):
        self.client.get("/users")
    
    @task(1)
    def create_user(self):
        self.client.post("/users", json={"name": "Test", "email": "test@test.com"})

# Запуск: locust -f test_load.py --host=http://localhost:8000
```

## 6. Test Fixtures with Async

```python
@pytest_asyncio.fixture
async def created_user(db_session) -> AsyncIterator[User]:
    """Create + cleanup user."""
    user = User(name="Test", email="test@test.com")
    db_session.add(user)
    await db_session.flush()
    yield user
    await db_session.delete(user)
    await db_session.flush()

@pytest.mark.asyncio
async def test_user_orders(created_user: User, db_session: AsyncSession):
    order = Order(user_id=created_user.id, total=100)
    db_session.add(order)
    await db_session.flush()
    
    assert order.user_id == created_user.id
```

## 7. Mocking External APIs

```python
# pip install pytest-httpx

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_external_api(httpx_mock):
    httpx_mock.add_response(
        url="https://api.example.com/users/1",
        json={"id": 1, "name": "Alice"},
        status_code=200,
    )
    
    async with AsyncClient() as client:
        response = await client.get("https://api.example.com/users/1")
        assert response.json()["name"] == "Alice"

# With respx (alternative)
import respx

@respx.mock
async def test_with_respx():
    route = respx.get("https://api.example.com/users").respond(200, json={"users": []})
    
    result = await get_users()
    assert result == []
    assert route.called
```

## 8. Testing with Testcontainers

```python
# pip install testcontainers[postgres]

from testcontainers.postgres import PostgresContainer

@pytest.mark.asyncio
async def test_with_real_db():
    with PostgresContainer("postgres:16-alpine") as pg:
        db_url = pg.get_connection_url().replace("psycopg2", "asyncpg")
        
        engine = create_async_engine(db_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with AsyncSession(engine) as session:
            session.add(User(name="Test"))
            await session.flush()
        
        await engine.dispose()
```

## 9. Testing Race Conditions

```python
@pytest.mark.asyncio
async def test_race_condition():
    """Тест, который ловит race condition."""
    results = []
    
    async def increment():
        nonlocal results
        await asyncio.sleep(0.01)  # симуляция I/O
        results.append(1)
    
    # Запускаем 100 concurrent задач
    tasks = [increment() for _ in range(100)]
    await asyncio.gather(*tasks)
    
    assert len(results) == 100  # если race — будет меньше
```

## 10. Mutation Testing

```python
# pip install mutmut

# Mutmut меняет код (например, > на <, True на False)
# и проверяет, упадут ли тесты
# Если тесты не упали — слабое покрытие

# Запуск: mutmut run --paths-to-mutate src/
# Результат: mutmut results
```

## 11. Test Coverage Quality

```python
# ❌ Плохой тест (тестирует реализацию)
def test_sort():
    items = [3, 1, 2]
    result = sort(items)
    assert result == [1, 2, 3]
    assert items is not result  # ❌ тестирует, что вернула НОВЫЙ список

# ✅ Хороший тест (тестирует поведение)
def test_sort_returns_sorted():
    items = [3, 1, 2]
    result = sort(items)
    assert result == [1, 2, 3]

# ❌ Тест зависит от данных в БД
def test_user_exists():
    user = db.get(User, 1)  # может не существовать
    assert user is not None

# ✅ Тест сам создаёт данные
def test_user_exists(user_factory):
    user = user_factory()
    assert db.get(User, user.id) is not None

# ❌ Тест слишком детальный
def test_api_format():
    response = client.get("/users/1")
    assert response.json() == {
        "id": 1, "name": "Alice", "email": "alice@test.com",
        "created_at": "2024-01-15T10:00:00",  # ❌ хрупко
        "updated_at": "2024-01-15T10:00:00",  # ❌ хрупко
    }

# ✅ Тест проверяет только важное
def test_api_returns_user():
    response = client.get("/users/1")
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Alice"
    assert "email" in data
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
