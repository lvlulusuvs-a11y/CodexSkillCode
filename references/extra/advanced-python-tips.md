# Advanced Python Tips

**Приёмы Python, которые используют senior-разработчики.**

---

## 1. Context Manager for Timing

```python
from contextlib import contextmanager
from time import perf_counter
import logging

logger = logging.getLogger(__name__)

@contextmanager
def timer(name: str = "operation"):
    start = perf_counter()
    try:
        yield
    finally:
        elapsed = perf_counter() - start
        logger.info("%s took %.2fms", name, elapsed * 1000)

# Usage
with timer("database query"):
    users = await db.fetch_all("SELECT * FROM users")
```

## 2. Lazy Initialization with cached_property

```python
from functools import cached_property
import json

class ExpensiveObject:
    @cached_property
    def data(self) -> dict:
        """Computed once, cached forever (or until instance is recreated)."""
        print("Loading data...")
        with open("large_file.json") as f:
            return json.load(f)

obj = ExpensiveObject()
print(obj.data)  # loads
print(obj.data)  # cached
```

## 3. Sentinel Values for Optional Arguments

```python
_sentinel = object()

def get_user(user_id: int, default: Any = _sentinel) -> User:
    if user := db.get(User, user_id):
        return user
    if default is _sentinel:
        raise NotFoundError(f"User {user_id} not found")
    return default

# Usage
get_user(1)  # raises if not found
get_user(1, None)  # returns None if not found
```

## 4. Structural Pattern Matching

```python
from dataclasses import dataclass

@dataclass
class Success:
    data: Any

@dataclass
class Failure:
    error: str
    code: int

def handle(result: Success | Failure) -> str:
    match result:
        case Success(data):
            return f"Success: {data}"
        case Failure(error, code):
            return f"Error {code}: {error}"
```

## 5. Iterator Protocol

```python
class Range:
    def __init__(self, start, end):
        self._start = start
        self._end = end
    
    def __iter__(self):
        return RangeIterator(self._start, self._end)

class RangeIterator:
    def __init__(self, current, end):
        self._current = current
        self._end = end
    
    def __next__(self):
        if self._current >= self._end:
            raise StopIteration
        value = self._current
        self._current += 1
        return value

# Or simpler with generator
def range_gen(start, end):
    while start < end:
        yield start
        start += 1
```

## 6. Context Variables (asyncio)

```python
from contextvars import ContextVar
import uuid

request_id: ContextVar[str] = ContextVar("request_id", default="")

async def handler():
    request_id.set(uuid.uuid4().hex[:8])
    await process()

async def process():
    print(f"Processing request {request_id.get()}")

# Thread-safe, async-safe, no global state issues
```

## 7. Property Descriptors

```python
class PositiveNumber:
    def __set_name__(self, owner, name):
        self._name = f"_{name}"
    
    def __get__(self, obj, objtype=None):
        return getattr(obj, self._name, 0)
    
    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self._name[1:]} must be positive")
        setattr(obj, self._name, value)

class Account:
    balance = PositiveNumber()
    
    def __init__(self, balance):
        self.balance = balance  # calls PositiveNumber.__set__

# account.balance = -100 → raises ValueError
```

## 8. __init_subclass__ for Registry

```python
class Plugin:
    _registry: dict[str, type] = {}
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._registry[cls.__name__] = cls

class JSONExporter(Plugin): pass
class CSVExporter(Plugin): pass

print(Plugin._registry)  # {'JSONExporter': ..., 'CSVExporter': ...}
```

## 9. WeakRef for Cache

```python
import weakref

class ObjectCache:
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()
    
    def get(self, key):
        return self._cache.get(key)
    
    def set(self, key, value):
        self._cache[key] = value

# Objects are automatically removed when no external references exist
```

## 10. Dataclass with Validation

```python
from dataclasses import dataclass
from typing import Self

@dataclass(frozen=True)
class User:
    id: int
    name: str
    email: str
    
    def __post_init__(self: Self) -> None:
        if not self.name.strip():
            raise ValueError("Name cannot be empty")
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")

# Frozen = immutable, hashable, can be used in sets
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
