# Testing Guide (Complete)

**Полное руководство по тестированию Python-приложений.**

---

## 1. Test Structure

### AAA Pattern (Arrange-Act-Assert)
```python
def test_discount_calculation() -> None:
    # Arrange
    order = Order(total=1000, user=User(tier="gold"))
    
    # Act
    discount = calculate_discount(order)
    
    # Assert
    assert discount == 100  # 10% for gold
```

### Given-When-Then (BDD)
```python
def test_order_cancellation() -> None:
    # Given a confirmed order
    order = Order(status="confirmed", payment_id=123)
    
    # When cancelled
    result = cancel_order(order.id)
    
    # Then status changes and payment is refunded
    assert result.status == "cancelled"
    assert result.refunded is True
```

## 2. Running Tests

```bash
# Basic
pytest

# Verbose
pytest -v

# With coverage
pytest --cov=src --cov-report=term-missing

# Parallel
pip install pytest-xdist
pytest -n auto

# Specific tests
pytest tests/test_users.py
pytest tests/test_users.py::test_create_user
pytest -k "user and not slow"

# Failed first
pytest --ff

# Last failed
pytest --lf

# Exit on first failure
pytest -x

# Debug on failure
pytest --pdb
```

## 3. Fixtures

### Basic Fixtures
```python
import pytest

@pytest.fixture
def user_data() -> dict:
    return {"name": "Alice", "email": "alice@test.com"}

@pytest.fixture
def created_user(db_session, user_data) -> User:
    user = User(**user_data)
    db_session.add(user)
    db_session.flush()
    return user

def test_user_creation(created_user: User) -> None:
    assert created_user.name == "Alice"
    assert created_user.email == "alice@test.com"
```

### Fixture Scopes
```python
@pytest.fixture(scope="session")  # один раз на сессию
def db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture(scope="module")  # один раз на модуль
def db_session(db_engine):
    session = Session(db_engine)
    yield session
    session.close()

@pytest.fixture(scope="function")  # каждый тест заново
def clean_db(db_session):
    yield db_session
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
```

### Async Fixtures
```python
import pytest_asyncio

@pytest_asyncio.fixture
async def async_db_session():
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_async_create(async_db_session):
    user = User(name="Alice")
    async_db_session.add(user)
    await async_db_session.flush()
    assert user.id is not None
```

## 4. Parametrization

```python
import pytest

# Single parameter
@pytest.mark.parametrize("email", [
    "alice@test.com",
    "bob@example.org",
    "charlie@company.co.uk",
])
def test_valid_emails(email: str) -> None:
    assert is_valid_email(email)

# Multiple parameters
@pytest.mark.parametrize("total,tier,expected", [
    (100, "regular", 0),
    (500, "regular", 25),
    (1000, "regular", 50),
    (100, "gold", 10),
    (1000, "gold", 100),
    (0, "regular", 0),
    (-100, "regular", 0),
])
def test_discount(total: int, tier: str, expected: float) -> None:
    assert calculate_discount(total, tier) == expected

# With IDs
@pytest.mark.parametrize("input,expected", [
    pytest.param("hello", "HELLO", id="lowercase"),
    pytest.param("HELLO", "HELLO", id="already_upper"),
    pytest.param("HeLLo", "HELLO", id="mixed_case"),
    pytest.param("", "", id="empty_string"),
])
def test_uppercase(input: str, expected: str) -> None:
    assert input.upper() == expected
```

## 5. Mocking

```python
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Basic mock
def test_service_call() -> None:
    mock_repo = Mock()
    mock_repo.get.return_value = User(id=1, name="Alice")
    
    service = UserService(mock_repo)
    user = service.get(1)
    
    assert user.name == "Alice"
    mock_repo.get.assert_called_once_with(1)

# Async mock
@pytest.mark.asyncio
async def test_async_service() -> None:
    mock_repo = AsyncMock()
    mock_repo.get.return_value = User(id=1, name="Alice")
    
    service = UserService(mock_repo)
    user = await service.get(1)
    
    assert user.name == "Alice"

# Patch
@patch("myapp.service.requests.get")
def test_external_api(mock_get: Mock) -> None:
    mock_get.return_value = Mock(status_code=200, json=lambda: {"data": []})
    
    result = fetch_data()
    assert result == {"data": []}

# Context manager patch
def test_with_patch() -> None:
    with patch("myapp.service.redis_client") as mock_redis:
        mock_redis.get.return_value = None
        result = process_with_cache()
        assert result is not None
```

## 6. Test Doubles

```python
# Fake (in-memory implementation)
class FakeUserRepository:
    def __init__(self) -> None:
        self._users: dict[int, dict] = {}
        self._next_id = 1
    
    async def create(self, data: dict) -> User:
        user = User(id=self._next_id, **data)
        self._users[self._next_id] = user
        self._next_id += 1
        return user
    
    async def get(self, user_id: int) -> User | None:
        return self._users.get(user_id)
    
    async def get_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

# Stub (returns fixed data)
class StubPaymentService:
    async def charge(self, amount: float) -> dict:
        return {"status": "success", "transaction_id": "stub_123"}

# Spy (records calls)
class SpyEmailService:
    def __init__(self) -> None:
        self.sent_emails: list[dict] = []
    
    async def send(self, to: str, subject: str, body: str) -> None:
        self.sent_emails.append({"to": to, "subject": subject, "body": body})
```

## 7. Integration Testing

```python
# Database integration
@pytest.mark.asyncio
async def test_user_repository(async_db_session) -> None:
    repo = UserRepository(async_db_session)
    
    # Create
    user = await repo.create({"name": "Alice", "email": "alice@test.com"})
    assert user.id is not None
    assert user.name == "Alice"
    
    # Read
    found = await repo.get(user.id)
    assert found is not None
    assert found.email == "alice@test.com"
    
    # Read by email
    by_email = await repo.get_by_email("alice@test.com")
    assert by_email is not None
    
    # Not found
    not_found = await repo.get(999)
    assert not_found is None

# API integration
@pytest.mark.asyncio
async def test_user_api(client, auth_headers) -> None:
    # Create
    response = await client.post(
        "/api/v1/users",
        json={"name": "Alice", "email": "alice@test.com"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    user_id = response.json()["id"]
    
    # Read
    response = await client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"
    
    # List
    response = await client.get("/api/v1/users", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) > 0
```

## 8. Test Configuration

```python
# conftest.py
import pytest
from typing import AsyncIterator
from httpx import AsyncClient, ASGITransport

@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings(
        DEBUG=True,
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        REDIS_URL="redis://localhost:6379/1",
    )

@pytest_asyncio.fixture
async def db_session(settings) -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        yield session
    await engine.dispose()

@pytest_asyncio.fixture
async def client(db_session) -> AsyncIterator[AsyncClient]:
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def auth_headers(client) -> dict:
    response = await client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123",
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

## 9. Testing Patterns

### Testing Async Code
```python
@pytest.mark.asyncio
async def test_concurrent_operations() -> None:
    """Test that concurrent operations don't race."""
    results = []
    
    async def worker(i: int) -> None:
        await asyncio.sleep(0.01)
        results.append(i)
    
    tasks = [worker(i) for i in range(10)]
    await asyncio.gather(*tasks)
    
    assert len(results) == 10  # no lost updates

### Testing Error Cases
@pytest.mark.asyncio
async def test_not_found(client) -> None:
    response = await client.get("/api/v1/users/999")
    assert response.status_code == 404
    assert response.json()["error"] == "NotFoundError"

@pytest.mark.asyncio
async def test_validation_error(client) -> None:
    response = await client.post("/api/v1/users", json={
        "name": "",  # invalid: empty name
        "email": "invalid",  # invalid: not email
    })
    assert response.status_code == 422

### Testing Timeouts
@pytest.mark.asyncio
async def test_timeout(monkeypatch) -> None:
    async def slow_operation() -> None:
        await asyncio.sleep(10)  # should timeout
    
    monkeypatch.setattr("myapp.service.operation", slow_operation)
    
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(process(), timeout=1.0)
```

## 10. Testing Database

```python
@pytest.mark.asyncio
async def test_database_transaction(db_session) -> None:
    """Test that transactions roll back on error."""
    user = User(name="Alice", email="alice@test.com")
    db_session.add(user)
    await db_session.flush()
    
    # Force error
    with pytest.raises(Exception):
        async with db_session.begin():
            db_session.add(User(name="Bob"))
            raise RuntimeError("Something went wrong")
    
    # Bob should NOT be in DB
    users = await db_session.execute(select(User))
    assert len(users.scalars().all()) == 1  # only Alice

@pytest.mark.asyncio
async def test_unique_constraint(db_session) -> None:
    """Test unique constraint violation."""
    db_session.add(User(email="same@test.com"))
    await db_session.flush()
    
    with pytest.raises(IntegrityError):
        db_session.add(User(email="same@test.com"))  # duplicate
        await db_session.flush()
```

## 11. Testing Configuration

```python
@pytest.fixture(autouse=True)
def test_settings(monkeypatch):
    """Override settings for all tests."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/1")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("DEBUG", "true")
    
    # Clear cached settings
    get_settings.cache_clear()
```

## 12. Factories (Test Data)

```python
# factories.py
from collections.abc import Callable
from typing import Any

class UserFactory:
    _next_id = 1
    
    @classmethod
    def build(cls, **overrides: Any) -> dict:
        defaults = {
            "name": f"User {cls._next_id}",
            "email": f"user{cls._next_id}@test.com",
            "age": 25,
            "is_active": True,
        }
        defaults.update(overrides)
        cls._next_id += 1
        return defaults
    
    @classmethod
    async def create(cls, session: AsyncSession, **overrides: Any) -> User:
        data = cls.build(**overrides)
        user = User(**data)
        session.add(user)
        await session.flush()
        return user

# Usage
user = await UserFactory.create(db_session, name="Alice")
admin = await UserFactory.create(db_session, role="admin", is_active=True)
```

## 13. Markers

```python
import pytest

# Custom markers
@pytest.mark.slow
def test_heavy_computation() -> None:
    ...

@pytest.mark.integration
def test_database_integration() -> None:
    ...

@pytest.mark.smoke
def test_health_endpoint() -> None:
    ...

# Skip conditions
@pytest.mark.skipif(sys.version_info < (3, 11), reason="Requires Python 3.11+")
def test_new_feature() -> None:
    ...

# Run only
# pytest -m "not slow"
# pytest -m "smoke or integration"
# pytest -m "slow and not integration"
```

## 14. Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=term-missing --cov-report=html

# Coverage config (.coveragerc)
[run]
source = src
omit = */tests/*, */migrations/*, *__init__*, setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == "__main__":
    pass

# Minimum coverage
# pytest --cov=src --cov-fail-under=80
```

## 15. Tox (multiple Python versions)

```ini
# tox.ini
[tox]
envlist = py310, py311, py312
isolated_build = True

[testenv]
deps =
    pytest
    pytest-asyncio
    pytest-cov
commands =
    pytest --cov=src --cov-report=term
```

## 16. Best Practices Checklist

```python
# ✅ DO:
# - Test behavior, not implementation
# - One assertion concept per test
# - Descriptive test names
# - Independent tests (no shared state)
# - Use fixtures for setup/teardown
# - Parametrize for multiple inputs
# - Test edge cases (empty, None, boundary)

# ❌ DON'T:
# - Test private methods (test public behavior)
# - Use sleep() for timing
# - Hard-code test data in each test
# - Test external services without mocking
# - Write tests that depend on each other
# - Test obvious getters/setters
```

## 17. Quick Reference

```bash
# Installation
pip install pytest pytest-asyncio pytest-cov pytest-xdist

# Running
pytest                                    # all tests
pytest -v                                 # verbose
pytest -x                                 # stop on first fail
pytest --ff                               # failed first
pytest -k "user"                          # filter by name
pytest -m "slow"                          # filter by marker
pytest tests/test_users.py::test_create   # single test
pytest --cov=src                          # coverage
pytest -n auto                            # parallel
pytest --pdb                              # debug on fail

# Fixture scopes: session > module > class > function
# Autouse: @pytest.fixture(autouse=True)
# Async: pytest-asyncio
# Mock: from unittest.mock import Mock, AsyncMock, patch
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
