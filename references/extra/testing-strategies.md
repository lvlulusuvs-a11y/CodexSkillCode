# Testing Strategies

**Реальные стратегии тестирования для продакшена. Не "как писать тесты", а "что и когда тестировать".**

---

## I. Пирамида тестов (реальная)

```text
         ╱╲
        ╱ E2E ╲         3-5% — критические сценарии
       ╱────────╲
      ╱ Integration ╲   15-20% — взаимодействие модулей
     ╱──────────────╲
    ╱   Unit Tests    ╲  75-80% — изолированная логика
   ╱────────────────────╲
```

**Правило:**
- Unit-тесты — быстрые (мс), изолированные (моки), покрывают логику
- Integration — поднимают БД/API, проверяют связку
- E2E — полный сценарий, только критические пути

**Не делай:**
- E2E на каждую мелочь (медленно, хрупко)
- Unit без моков на внешние сервисы (тестируешь сеть)
- 100% coverage как самоцель (бессмысленные тесты)

## II. Что тестировать (приоритеты)

### 🔴 Обязательно (без этого — баги в проде)
- **Core бизнес-логика** — расчёты, валидация, статусы
- **Edge cases** — пустой ввод, null, граничные значения
- **Обработка ошибок** — что если БД упала, API не отвечает
- **Безопасность** — SQL injection, XSS, авторизация

### 🟡 Желательно (сэкономит время при рефакторинге)
- **Repository слой** — запросы к БД (интеграционные)
- **API handlers** — статусы ответов, валидация
- **Serialization** — правильные поля, форматы

### 🟢 Хорошо бы (но не критично)
- **UI компоненты** — рендер, клики
- **Configuration** — все комбинации настроек
- **Performance tests** — под нагрузкой

### ⚪ Не трать время
- **Геттеры/сеттеры** (без логики)
- **Plain dataclasses** (без __post_init__)
- **Тривиальные delegation** (обёртки без логики)
- **Тесты на тесты** (coverage 100% ради цифры)

## III. Паттерны тестирования

### 1. Arrange-Act-Assert (AAA) — стандарт

```python
def test_discount_calculation() -> None:
    # Arrange
    order = Order(total=1000, user=User(tier="gold"))
    
    # Act
    discount = calculate_discount(order)
    
    # Assert
    assert discount == 100  # 10% для gold
```

### 2. Given-When-Then (BDD-style)

```python
def test_order_status_transition() -> None:
    # Given новый заказ
    order = Order(status=OrderStatus.PENDING)
    
    # When подтверждаем
    order.confirm()
    
    # Then статус изменился
    assert order.status == OrderStatus.CONFIRMED
```

### 3. Test Parametrization

```python
import pytest

@pytest.mark.parametrize("total,tier,expected", [
    (100, "regular", 0),
    (500, "regular", 25),    # 5%
    (1000, "regular", 50),   # 5% (не 10%)
    (100, "gold", 10),       # 10%
    (1000, "gold", 100),     # 10%
    (5000, "gold", 500),     # 10% (не больше)
    (0, "regular", 0),
    (-100, "regular", 0),    # edge case
])
def test_discount(total: int, tier: str, expected: float) -> None:
    assert calculate_discount(Order(total=total, user=User(tier=tier))) == expected
```

### 4. Fixtures with Cleanup

```python
@pytest_asyncio.fixture
async def db_session():
    """Фикстура с cleanup."""
    session = AsyncSession(engine)
    async with session.begin():
        yield session
    # cleanup автоматически: rollback несохранённого

@pytest_asyncio.fixture
async def test_user(db_session) -> User:
    """Создать тестового пользователя."""
    user = User(name="Test", email="test@example.com")
    db_session.add(user)
    await db_session.flush()
    yield user
    # cleanup: удалить после теста
    await db_session.delete(user)
    await db_session.flush()
```

### 5. Mock External Services

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_send_notification() -> None:
    # Мокаем внешний сервис
    email_service = AsyncMock()
    email_service.send.return_value = True
    
    # Тестируем
    result = await notify_user(
        user_id=1,
        message="Hello",
        email_service=email_service,
    )
    
    assert result is True
    email_service.send.assert_called_once_with(
        to="user@example.com",
        subject="Notification",
        body="Hello",
    )
```

### 6. Integration Test with Test Container

```python
import pytest
import asyncpg

@pytest.mark.asyncio
async def test_user_crud(postgres_container: str) -> None:
    """Тест с реальной PostgreSQL."""
    conn = await asyncpg.connect(postgres_container)
    try:
        # Create
        await conn.execute(
            "INSERT INTO users (name, email) VALUES ($1, $2)",
            "Test", "test@example.com",
        )
        
        # Read
        row = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1",
            "test@example.com",
        )
        assert row["name"] == "Test"
    finally:
        await conn.close()
```

## IV. Как тестировать асинхронный код

### Основные принципы

```python
import pytest
from unittest.mock import AsyncMock, patch

# Асинхронные тесты
@pytest.mark.asyncio
async def test_async_service() -> None:
    result = await my_async_function()
    assert result == expected

# Моки для async функций
async def test_with_async_mock() -> None:
    mock = AsyncMock()
    mock.fetch.return_value = {"id": 1}
    
    result = await service.get_data(mock)
    assert result["id"] == 1

# Контекстный менеджер async mock
async def test_with_async_context_manager() -> None:
    mock = AsyncMock()
    mock.__aenter__.return_value = mock
    
    async with mock as m:
        pass  # работает

# Таймауты для тестов (защита от вечно висящих)
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_with_timeout() -> None:
    result = await potentially_slow_function()
    assert result is not None
```

## V. Как тестировать работу с БД

### Стратегии
1. **In-memory SQLite** — быстро, подходит для тестов с SQLAlchemy
2. **Testcontainers** — реальная БД в Docker, медленно, но надёжно
3. **Фикстуры с транзакциями** — rollback после каждого теста

### Пример с SQLAlchemy (in-memory)

```python
@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine("sqlite+aiosqlite://", echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def session(async_engine) -> AsyncIterator[AsyncSession]:
    async with AsyncSession(async_engine, expire_on_commit=False) as sess:
        async with sess.begin():
            yield sess
            await sess.rollback()  # откат после каждого теста
```

## VI. Test Coverage (реальное использование)

```bash
# Запуск с coverage
pytest --cov=src --cov-report=term-missing --cov-report=html

# Проверить только изменённые файлы
pytest --cov=$(git diff --name-only main | grep '\.py$' | tr '\n' ' ')

# Игнорировать тесты, __init__.py, manage.py
# .coveragerc:
[run]
omit = */tests/*, */migrations/*, *__init__*, setup.py
```

**Реальные цели coverage:**
- 80%+ — хорошо
- 90%+ — отлично
- 60-80% — нормально для легаси
- <60% — тревожный сигнал

**Важно:** 100% coverage ≠ нет багов. Самое важное — покрытие бизнес-логики и edge cases.

## VII. Test Doubles Guide

| Тип | Когда использовать | Пример |
|-----|-------------------|--------|
| **Dummy** | Нужен параметр, который не используется | `None`, `MagicMock()` |
| **Fake** | Нужна работающая, но упрощённая реализация | in-memory DB вместо PostgreSQL |
| **Stub** | Нужен предсказуемый ответ | `mock.return_value = 42` |
| **Spy** | Нужно проверить, что вызвалось | `assert mock.call_count == 1` |
| **Mock** | Нужно проверить, как вызвалось | `mock.assert_called_with(1, 2)` |

**Fake example:**
```python
class FakeUserRepo:
    """In-memory реализация UserRepository для тестов."""
    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._next_id = 1
    
    async def add(self, user: User) -> User:
        user.id = self._next_id
        self._next_id += 1
        self._users[user.id] = user
        return user
    
    async def get(self, user_id: int) -> User | None:
        return self._users.get(user_id)

# В тесте:
repo = FakeUserRepo()
service = UserService(repo)
await service.register("test@example.com")
user = await repo.get(1)
assert user.email == "test@example.com"
```

## VIII. Когда НЕ писать тест

- **Одноразовый скрипт** — миграция данных, разовый импорт
- **Prototype/Proof of concept** — выкинешь после проверки
- **UI, который меняется каждый спринт** — тесты будут мешать
- **Очевидный код** — тривиальные геттеры/сеттеры
- **Чужая ответственность** — не тестируй библиотеки

## IX. Bad Test Smells

```python
# ❌ Тест тестирует две вещи
def test_user_creation_and_validation():
    ...

# ✅ Раздели
def test_user_creation():
    ...

def test_user_validation():
    ...

# ❌ Тест зависит от других тестов
def test_user():  # предполагает, что test_setup уже выполнился
    ...

# ✅ Каждый тест независим
@pytest.fixture
def user():
    return User(name="Test")

def test_user_has_name(user):
    assert user.name == "Test"

# ❌ Тест использует реальную сеть
def test_external_api():
    response = requests.get("https://api.example.com/data")
    assert response.status_code == 200  # упадёт без интернета

# ✅ Мокаем внешние вызовы
def test_external_api(mock_api):
    mock_api.get.return_value = Mock(status_code=200)
    ...

# ❌ Тест проверяет реализацию, а не поведение
def test_sort():
    items = [3, 1, 2]
    result = sort(items)
    assert result == [1, 2, 3]
    assert items is not result  # ❌ проверка, что вернул НОВЫЙ список, а не изменил старый
    # Если реализация изменится — тест упадёт, хотя поведение верное

# ✅ Проверяй поведение
def test_sort_does_not_mutate_input():
    items = [3, 1, 2]
    result = sort(items)
    assert result == [1, 2, 3]
    # sorted() не меняет исходный

# ❌ Хрупкий тест (тестирует слишком много)
def test_api_response():
    response = client.get("/users/1")
    assert response.json() == {
        "id": 1, "name": "Alice", "email": "alice@example.com",
        "created_at": "2024-01-01T00:00:00", # ❌ depends on exact timestamp
        "orders_count": 5,
        ...
    }

# ✅ Тестируй только важное
def test_api_returns_user_data():
    response = client.get("/users/1")
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Alice"
    assert response.status_code == 200
```

## X. Quick Start: минимальный набор фикстур

```python
# conftest.py
import pytest_asyncio
from typing import AsyncIterator
from unittest.mock import AsyncMock

@pytest_asyncio.fixture
async def db() -> AsyncIterator[...]:
    """In-memory БД для тестов."""
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        yield session
    await engine.dispose()

@pytest.fixture
def mock_email() -> AsyncMock:
    """Mock email сервиса."""
    return AsyncMock()

@pytest.fixture
def user_repo(db) -> UserRepository:
    """Repository с реальной in-memory БД."""
    return UserRepository(db)

@pytest.fixture
def user_service(user_repo, mock_email) -> UserService:
    """Сервис с реальным repo и mock email."""
    return UserService(repo=user_repo, email_service=mock_email)
```


---

## Part 3: Advanced Testing Patterns

### 3.1 Testing Async Code

```python
"""Async testing patterns."""
from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


# Fixtures for async resources
@pytest_asyncio.fixture
async def db_session():
    """Async fixture with setup/teardown."""
    session = await create_session()
    yield session
    await session.close()


@pytest.mark.asyncio
async def test_create_user(db_session):
    user = await create_user(db_session, name="Test")
    assert user.id is not None
    assert user.name == "Test"


# Testing timeouts
@pytest.mark.asyncio
async def test_operation_timeout():
    """Verify operation respects timeout."""
    with pytest.raises(asyncio.TimeoutError):
        async with asyncio.timeout(0.1):
            await slow_operation(10)  # Would take 10s


# Testing race conditions
@pytest.mark.asyncio
async def test_concurrent_writes():
    """Test concurrent operations."""
    results = await asyncio.gather(
        update_counter(1),
        update_counter(2),
        update_counter(3),
        return_exceptions=True,
    )
    # With proper locking, all should succeed
    assert all(r is None for r in results)


# Mocking external services
@pytest.mark.asyncio
async def test_with_mocked_http():
    mock_response = AsyncMock()
    mock_response.json.return_value = {"id": 1, "name": "Mocked"}
    mock_response.status = 200
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await fetch_user(1)
        assert result.id == 1
```

### 3.2 Property-Based Testing

```python
"""Hypothesis property-based testing."""
from __future__ import annotations

from hypothesis import given, strategies as st, assume
import pytest


# Test that our sort is idempotent
@given(st.lists(st.integers()))
def test_sort_idempotent(items):
    sorted_once = sorted(items)
    sorted_twice = sorted(sorted_once)
    assert sorted_once == sorted_twice


# Test that our parser handles any string
@given(st.text())
def test_parse_never_crashes(text):
    assume(text)  # Skip empty
    try:
        result = parse_csv_line(text)
        # Should never throw for any input
        assert isinstance(result, list)
    except ValueError:
        pass  # Acceptable for invalid format
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


# Test that our date formatter is always valid
@given(st.datetimes())
def test_date_format(dt):
    formatted = format_date(dt)
    assert isinstance(formatted, str)
    assert len(formatted) == 10  # YYYY-MM-DD
    assert formatted[4] == '-'
    assert formatted[7] == '-'
```

### 3.3 Integration Testing with Testcontainers

```python
"""Integration tests with real dependencies."""
from __future__ import annotations

import pytest
import asyncio
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from testcontainers.kafka import KafkaContainer
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.fixture(scope="session")
def postgres():
    """PostgreSQL container for integration tests."""
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


@pytest.fixture(scope="session")
def redis():
    """Redis container."""
    with RedisContainer("redis:7-alpine") as r:
        yield r


@pytest.mark.asyncio
async def test_full_flow(postgres, redis):
    """End-to-end integration test with real dependencies."""
    dsn = postgres.get_connection_url().replace(
        "postgresql://", "postgresql+asyncpg://"
    )
    engine = create_async_engine(dsn)
    
    # Test actual database operations
    async with engine.begin() as conn:
        await conn.execute(text("CREATE TABLE test (id serial primary key, name text)"))
        await conn.execute(text("INSERT INTO test (name) VALUES ('integration')"))
        result = await conn.execute(text("SELECT * FROM test"))
        rows = result.fetchall()
        assert len(rows) == 1
        assert rows[0].name == "integration"


@pytest.mark.asyncio
async def test_kafka_integration(kafka):
    """Test Kafka producer/consumer."""
    bootstrap = kafka.get_bootstrap_server()
    # Use aiokafka to produce and consume
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap)
    await producer.start()
    await producer.send("test-topic", b"test message")
    await producer.stop()
    
    consumer = AIOKafkaConsumer(
        "test-topic",
        bootstrap_servers=bootstrap,
        group_id="test-group",
    )
    await consumer.start()
    msg = await asyncio.wait_for(consumer.__anext__(), timeout=5)
    assert msg.value == b"test message"
    await consumer.stop()
```

### 3.4 Contract Testing

```python
"""Contract tests for service boundaries."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class APIContract:
    """Define what our API guarantees."""
    status_code: int
    content_type: str = "application/json"
    required_fields: list[str] = None
    max_response_time_ms: int = 500


def test_get_user_contract():
    """Verify API contract is satisfied."""
    response = client.get("/api/users/1")
    contract = APIContract(
        status_code=200,
        required_fields=["id", "name", "email"],
    )
    
    assert response.status_code == contract.status_code
    assert response.headers["content-type"] == contract.content_type
    data = response.json()
    for field in contract.required_fields:
        assert field in data, f"Missing required field: {field}"
    assert response.elapsed.total_seconds() * 1000 < contract.max_response_time_ms
```

### 3.5 Snapshot Testing

```python
"""Snapshot testing for stable outputs."""
from __future__ import annotations

import json
from pathlib import Path


class Snapshot:
    """Simple inline snapshot testing."""
    
    def __init__(self, snapshot_dir: str = "__snapshots__"):
        self._dir = Path(snapshot_dir)
        self._dir.mkdir(exist_ok=True)
    
    def assert_match(self, value: Any, name: str) -> None:
        path = self._dir / f"{name}.snap"
        serialized = json.dumps(value, indent=2, default=str)
        
        if not path.exists():
            path.write_text(serialized)
            raise AssertionError(f"Snapshot created: {name}. Verify and re-run.")
        
        existing = path.read_text()
        if serialized != existing:
            diff = self._diff(existing, serialized)
            raise AssertionError(f"Snapshot mismatch: {name}\n{diff}")


# Usage:
# snapshot = Snapshot()
# snapshot.assert_match(api_response, "get_users")
```

### 3.6 Load Testing

```python
"""Load test patterns."""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from statistics import median, pstdev
from typing import Any


@dataclass
class LoadTestResult:
    """Load test results."""
    total_requests: int
    successful: int
    failed: int
    duration_s: float
    latencies: list[float] = field(default_factory=list)
    
    @property
    def rps(self) -> float:
        return self.total_requests / self.duration_s if self.duration_s else 0
    
    @property
    def p50(self) -> float:
        return median(self.latencies) * 1000 if self.latencies else 0
    
    @property
    def p99(self) -> float:
        if not self.latencies:
            return 0
        sorted_lats = sorted(self.latencies)
        idx = int(len(sorted_lats) * 0.99)
        return sorted_lats[idx] * 1000


async def load_test(
    url: str,
    concurrency: int = 10,
    duration_s: int = 10,
) -> LoadTestResult:
    """Simple load test with concurrency."""
    import aiohttp
    latencies = []
    successful = 0
    failed = 0
    start = time.monotonic()
    
    async def worker():
        nonlocal successful, failed
        async with aiohttp.ClientSession() as session:
            while time.monotonic() - start < duration_s:
                req_start = time.monotonic()
                try:
                    async with session.get(url) as resp:
                        if resp.status < 500:
                            successful += 1
                        else:
                            failed += 1
                except Exception:
                    failed += 1
                latencies.append(time.monotonic() - req_start)
    
    workers = [asyncio.create_task(worker()) for _ in range(concurrency)]
    await asyncio.gather(*workers)
    
    result = LoadTestResult(
        total_requests=successful + failed,
        successful=successful,
        failed=failed,
        duration_s=time.monotonic() - start,
        latencies=latencies,
    )
    
    print(f"Requests: {result.total_requests}")
    print(f"RPS: {result.rps:.0f}")
    print(f"Success: {result.successful} / Fail: {result.failed}")
    print(f"p50: {result.p50:.1f}ms / p99: {result.p99:.1f}ms")
    
    return result
```

### 3.7 Mutation Testing

```python
"""Simple mutation testing to verify test quality."""
from __future__ import annotations

import ast
import copy
from typing import Any


class MutationOperator(ast.NodeTransformer):
    """Apply code mutations for testing test coverage quality."""
    
    def visit_If(self, node: ast.If) -> Any:
        # Flip if conditions
        if isinstance(node.test, ast.Compare):
            mutated = copy.deepcopy(node)
            if isinstance(mutated.test.ops[0], ast.Eq):
                mutated.test.ops[0] = ast.NotEq()
            elif isinstance(mutated.test.ops[0], ast.NotEq):
                mutated.test.ops[0] = ast.Eq()
            elif isinstance(mutated.test.ops[0], ast.Lt):
                mutated.test.ops[0] = ast.Gt()
            elif isinstance(mutated.test.ops[0], ast.Gt):
                mutated.test.ops[0] = ast.Lt()
            return mutated
        return node
    
    def visit_Return(self, node: ast.Return) -> Any:
        # Remove return values
        if node.value is not None and not isinstance(node.value, ast.Constant):
            return ast.Return(value=None)
        return node


# Usage in tests:
# def test_mutation_survives():
#     """If tests are good, mutations should be caught."""
#     mutator = MutationOperator()
#     mutated_source = mutator.visit(ast.parse(original_source))
```

### 3.8 Testing Checklist

```text
Unit Tests:
  □ Pure functions tested with multiple inputs
  □ Edge cases: empty, None, boundary values
  □ Error paths tested (not just happy path)
  □ Mocked external dependencies
  □ Property-based tests for critical logic

Integration Tests:
  □ Real database (testcontainers)
  □ Real message queue
  □ Real cache (Redis)
  □ Service-to-service calls

E2E Tests:
  □ Critical user journeys
  □ Payment flow (if applicable)
  □ Auth/authorization flow
  □ Error pages/handling

Performance Tests:
  □ Load test (expected traffic)
  □ Stress test (2x expected traffic)
  □ Soak test (sustained load for 1h+)
  □ Spike test (sudden traffic increase)

Quality Gates:
  □ Coverage > 80%
  □ Mutation score > 70%
  □ No flaky tests
  □ Tests run in < 5 min
  □ CI fails on test failure
```

### 3.9 Test Doubles: When to Use What

```python
# Dummy — passed but not used
repository = MagicMock()  # Dummy

# Fake — simplified but working implementation
class FakeDatabase:
    """In-memory DB for tests."""
    def __init__(self):
        self._data: dict = {}
    
    async def get(self, key):
        return self._data.get(key)

# Stub — returns predefined values
stub_repo = MagicMock()
stub_repo.get.return_value = User(id=1, name="Stub")

# Spy — records interactions
spy = MagicMock(wraps=real_service)
result = function_under_test(spy)
spy.process.assert_called_once_with(data)

# Mock — verifies expectations
mock = AsyncMock()
function_under_test(mock)
mock.send.assert_awaited_once_with("message")

# Fake is better than Mock when:
# - The dependency is complex
# - You need to test state changes
# - You want to test error recovery
# - Multiple tests share the same setup
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
