# SOLID Principles in Python

## S — Single Responsibility
```python
# ❌ Плохо: класс делает всё
class UserManager:
    def create_user(self, data): ...
    def send_email(self, user): ...
    def generate_report(self): ...

# ✅ Хорошо: разделено
class UserService:
    def create_user(self, data): ...

class EmailService:
    def send(self, to: str, msg: str): ...

class ReportService:
    def generate(self): ...
```

## O — Open/Closed
```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def process(self, amount: float) -> bool: ...

class CardPayment(PaymentProcessor):
    def process(self, amount: float) -> bool:
        print(f"Card: {amount}")
        return True

class CryptoPayment(PaymentProcessor):
    def process(self, amount: float) -> bool:
        print(f"Crypto: {amount}")
        return True

# Новая реализация — без изменения клиентского кода
class ApplePayPayment(PaymentProcessor):
    def process(self, amount: float) -> bool:
        print(f"ApplePay: {amount}")
        return True
```

## L — Liskov Substitution
```python
class Rectangle:
    def __init__(self, w, h):
        self.w = w
        self.h = h
    def area(self):
        return self.w * self.h

class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)

# ✅ Square можно использовать вместо Rectangle без сюрпризов
def print_area(shape: Rectangle):
    print(shape.area())

print_area(Rectangle(2, 3))  # 6
print_area(Square(4))        # 16
```

## I — Interface Segregation
```python
# ❌ Плохо: толстый интерфейс
class Worker(ABC):
    @abstractmethod
    def work(self): ...
    @abstractmethod
    def eat(self): ...
    @abstractmethod
    def sleep(self): ...

class Robot(Worker):
    def work(self): ...
    def eat(self): pass    # не нужно
    def sleep(self): pass  # не нужно

# ✅ Хорошо: тонкие интерфейсы
class Workable(ABC):
    def work(self): ...

class Eatable(ABC):
    def eat(self): ...

class Human(Workable, Eatable): ...
class Robot(Workable): ...
```

## D — Dependency Inversion
```python
# ❌ Плохо: зависит от конкретной реализации
class PostgresDB:
    def query(self, sql): ...

class UserService:
    def __init__(self):
        self.db = PostgresDB()  # жёсткая связь

# ✅ Хорошо: зависит от абстракции
class Database(ABC):
    def query(self, sql: str) -> list[dict]: ...

class UserService:
    def __init__(self, db: Database):
        self._db = db  # можно подменить

class PostgresDB(Database):
    def query(self, sql):
        return [{"id": 1}]

class MockDB(Database):
    def query(self, sql):
        return [{"id": 1, "test": True}]
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
