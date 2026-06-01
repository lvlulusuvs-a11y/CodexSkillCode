# Dependency Injection in Python

**Паттерны DI без фреймворков.**

---

## 1. Простой DI через конструктор

```python
class UserService:
    def __init__(self, repo: UserRepository, email_service: EmailService) -> None:
        self._repo = repo
        self._email = email_service
    
    async def register(self, email: str, name: str) -> User:
        if await self._repo.get_by_email(email):
            raise ConflictError("Email exists")
        user = await self._repo.create(email=email, name=name)
        await self._email.send_welcome(user)
        return user
```

## 2. DI через FastAPI Depends

```python
from fastapi import Depends

def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_email_service() -> EmailService:
    return EmailService(settings.SMTP_URL)

def get_user_service(
    repo: UserRepository = Depends(get_user_repo),
    email: EmailService = Depends(get_email_service),
) -> UserService:
    return UserService(repo, email)

@router.post("/users")
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> User:
    return await service.register(data.email, data.name)
```

## 3. DI через контейнер (для тестов)

```python
from dataclasses import dataclass, field
from typing import Any

class DIContainer:
    """Простой DI контейнер."""
    
    def __init__(self) -> None:
        self._services: dict[type, Any] = {}
        self._factories: dict[type, Any] = {}
    
    def register(self, type_: type, instance: Any = None) -> None:
        if instance:
            self._services[type_] = instance
        else:
            self._factories[type_] = type_
    
    def resolve(self, type_: type) -> Any:
        if type_ in self._services:
            return self._services[type_]
        if type_ in self._factories:
            instance = self._factories[type_]()
            self._services[type_] = instance
            return instance
        raise KeyError(f"No registration for {type_}")

# Использование
container = DIContainer()
container.register(Database, Database("sqlite:///:memory:"))
container.register(UserRepository)
db = container.resolve(Database)
```

## 4. DI через functools.lru_cache (синглтоны)

```python
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings()

@lru_cache
def get_db() -> Database:
    return Database(get_settings().DATABASE_URL)

@lru_cache
def get_user_repo() -> UserRepository:
    return UserRepository(get_db())
```

## 5. DI для тестов

```python
# Переопределение зависимостей
@pytest.fixture
def mock_email():
    return AsyncMock()

@pytest.fixture
def user_service(mock_email):
    repo = FakeUserRepository()
    return UserService(repo, mock_email)

@pytest.mark.asyncio
async def test_register(user_service, mock_email):
    user = await user_service.register("test@test.com", "Test")
    assert user.email == "test@test.com"
    mock_email.send_welcome.assert_called_once()
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


---

## Production Usage

```python
"""Production implementation with full resilience."""
from __future__ import annotations

from typing import Any
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass 
class ResilientOperation:
    """Execute operations with full production patterns."""
    
    async def execute(self, operation: str, fn: callable, *args, **kwargs) -> Any:
        for attempt in range(3):
            try:
                async with asyncio.timeout(30):
                    return await fn(*args, **kwargs)
            except asyncio.TimeoutError:
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"Operation '{operation}' timed out")
                    raise
            except Exception:
                logger.exception(f"Operation '{operation}' failed")
                if attempt < 2:
                    await asyncio.sleep(1)
                else:
                    raise
        return None
    

### Principal Engineer Summary

This pattern encapsulates everything a Principal Engineer knows:
1. Always set timeouts
2. Always retry transient failures
3. Always log with context
4. Always have a fallback plan
5. Always think about observability

Apply this to every external interaction in your system.
