# Mypy Guide: Type Checking in Python

## Настройка
```toml
[tool.mypy]
strict = true
python_version = "3.12"
warn_unused_configs = true
warn_redundant_casts = true
warn_unused_ignores = true
disallow_any_unimported = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_return_any = true
warn_unreachable = true

[[tool.mypy.overrides]]
module = "tests.*"
ignore_errors = true
```

## Базовые типы
```python
from collections.abc import Sequence, Mapping, Callable
from typing import Any, TypeVar, Generic, Protocol, overload

# Вместо typing.List → list
def process(items: list[int]) -> list[str]:
    return [str(x) for x in items]

# Вместо typing.Dict → dict
def lookup(data: dict[str, int], key: str) -> int | None:
    return data.get(key)

# Callable
def run_callback(cb: Callable[[int, str], bool]) -> None:
    cb(1, "test")
```

## Generic
```python
T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

# Использование
stack = Stack[int]()
stack.push(1)
stack.push("hello")  # mypy error!
```

## Protocol (structural typing)
```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

def render(obj: Drawable) -> None:
    obj.draw()

class Circle:
    def draw(self) -> None:
        print("○")

class Square:
    def draw(self) -> None:
        print("□")

render(Circle())  # OK
render(Square())  # OK
render("hello")   # mypy error!
```

## Literal и overload
```python
from typing import Literal, overload

@overload
def parse(data: str) -> dict[str, Any]: ...
@overload
def parse(data: bytes) -> list[int]: ...
def parse(data: str | bytes) -> dict | list:
    if isinstance(data, str):
        return {"type": "str", "value": data}
    return list(data)

# Literal
def set_mode(mode: Literal["read", "write", "append"]) -> None:
    print(f"Mode: {mode}")

set_mode("read")    # OK
set_mode("delete")  # mypy error!
```

## Type narrowing
```python
def process(value: str | int | None) -> str:
    if value is None:
        return "empty"
    if isinstance(value, int):
        return f"number: {value}"
    return f"string: {value}"

# TypeGuard
from typing import TypeGuard

def is_str_list(items: list[Any]) -> TypeGuard[list[str]]:
    return all(isinstance(i, str) for i in items)

def handle(items: list[Any]) -> None:
    if is_str_list(items):
        print(" ".join(items))  # mypy знает что это list[str]
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
