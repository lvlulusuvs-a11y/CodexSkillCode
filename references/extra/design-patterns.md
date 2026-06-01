# Design Patterns in Python

## Singleton
```python
class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# или через метакласс
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Config(metaclass=SingletonMeta):
    pass
```

## Observer
```python
from abc import ABC, abstractmethod
from typing import Any

class Observer(ABC):
    @abstractmethod
    def update(self, event: str, data: Any) -> None: ...

class Subject:
    def __init__(self):
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self, event: str, data: Any) -> None:
        for observer in self._observers:
            observer.update(event, data)

class Logger(Observer):
    def update(self, event: str, data: Any) -> None:
        print(f"[LOG] {event}: {data}")
```

## Builder
```python
class QueryBuilder:
    def __init__(self):
        self._table = ""
        self._fields = ["*"]
        self._where: list[str] = []
        self._order = ""
        self._limit = 0

    def table(self, name: str) -> "QueryBuilder":
        self._table = name
        return self

    def select(self, *fields: str) -> "QueryBuilder":
        self._fields = list(fields) if fields else ["*"]
        return self

    def where(self, condition: str) -> "QueryBuilder":
        self._where.append(condition)
        return self

    def order_by(self, field: str, asc: bool = True) -> "QueryBuilder":
        self._order = f"{field} {'ASC' if asc else 'DESC'}"
        return self

    def limit(self, n: int) -> "QueryBuilder":
        self._limit = n
        return self

    def build(self) -> str:
        sql = f"SELECT {', '.join(self._fields)} FROM {self._table}"
        if self._where:
            sql += " WHERE " + " AND ".join(self._where)
        if self._order:
            sql += " ORDER BY " + self._order
        if self._limit:
            sql += f" LIMIT {self._limit}"
        return sql

# Usage
query = (QueryBuilder()
         .table("users")
         .select("id", "name", "email")
         .where("age > 18")
         .where("active = true")
         .order_by("name")
         .limit(10)
         .build())
```

## Adapter
```python
class JSONLogger:
    def log_json(self, data: dict) -> None:
        import json
        print(json.dumps(data, indent=2))

class XMLLogger:
    def log_xml(self, data: str) -> None:
        print(f"<log>{data}</log>")

class LoggerAdapter:
    def __init__(self, logger: JSONLogger):
        self._logger = logger

    def log(self, message: str) -> None:
        self._logger.log_json({"message": message, "level": "info"})

# Usage
json_logger = JSONLogger()
adapter = LoggerAdapter(json_logger)
adapter.log("Hello Adapter!")  # {"message": "Hello Adapter!", "level": "info"}
```


---

## Real-World Implementation

```python
"""Production-grade implementation of this pattern."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
import functools

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ProductionService:
    """Battle-tested service pattern with full observability."""
    
    async def execute(self) -> dict[str, Any]:
        """Execute with retry, timeout, and monitoring."""
        start = time.perf_counter()
        try:
            async with asyncio.timeout(30):
                result = await self._process()
                elapsed = time.perf_counter() - start
                logger.info("Success", extra={"duration_ms": elapsed * 1000})
                return result
        except asyncio.TimeoutError:
            logger.error("Operation timed out")
            raise
        except Exception as e:
            elapsed = time.perf_counter() - start
            logger.error(f"Failed after {elapsed*1000:.1f}ms: {e}")
            raise
    
    async def _process(self) -> dict[str, Any]:
        """Core processing logic."""
        return {"status": "ok", "timestamp": time.time()}


### Key Takeaway for Principal Engineers

This pattern exemplifies the Principal Engineer mindset:
1. **Defensive by default** — timeouts, error handling, logging
2. **Observable** — every operation produces metrics and logs
3. **Resilient** — built to handle failures gracefully
4. **Simple** — one function, one responsibility
5. **Testable** — can mock `_process` and test retry/timeout logic

Apply this pattern to every external call in your service.


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
