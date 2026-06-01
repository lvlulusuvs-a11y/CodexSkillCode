# Performance Tips Quick Reference

**Конкретные приёмы ускорения Python-кода. От простого к сложному.**

---

## Быстрые победы (5 минут на внедрение)

### 1. Local variable bindings
```python
# ❌ Глобальный lookup на каждой итерации
for item in items:
    process(item)

# ✅ Local reference
process_func = process  # bound once
for item in items:
    process_func(item)

# ✅ Для методов — ещё важнее
append = result.append
for item in items:
    append(item)  # вместо result.append(item)
```

### 2. Set вместо list для поиска
```python
# ❌ O(n) поиск
if x in huge_list: ...

# ✅ O(1) поиск
huge_set = set(huge_list)
if x in huge_set: ...
```

### 3. Join вместо конкатенации
```python
# ❌ O(n²) — создаёт новую строку на каждую итерацию
s = ""
for part in parts:
    s += part

# ✅ O(n) — одна аллокация
s = "".join(parts)
```

### 4. Generator вместо list
```python
# ❌ list: вся память сразу
all_data = [process(x) for x in huge_data]
result = sum(all_data)

# ✅ generator: лениво
result = sum(process(x) for x in huge_data)
```

## Средние улучшения (30 минут)

### 5. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=256)
def expensive_calc(x: int) -> int:
    return complex_computation(x)

# cache_clear() при необходимости
expensive_calc.cache_clear()
```

### 6. Batch processing
```python
# ❌ N запросов к БД
for item in items:
    await db.save(item)

# ✅ 1 запрос
await db.save_all(items)
```

### 7. Connection pooling
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,       # 10 постоянных соединений
    pool_pre_ping=True, # проверка здоровья
)
```

## Продвинутые техники (2+ часа)

### 8. NumPy для численных данных
```python
import numpy as np

# Python loop: ~0.5s для 10M элементов
total = sum(x * x for x in range(10_000_000))

# NumPy: ~0.02s для 10M элементов
total = np.sum(np.arange(10_000_000) ** 2)
```

### 9. __slots__ для тысяч объектов
```python
class Point:
    __slots__ = ("x", "y")  # -50% памяти
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

### 10. Правильный алгоритм
```python
# ❌ O(n²) — пузырьковая сортировка
for i in range(len(items)):
    for j in range(i, len(items)):
        if items[i] > items[j]:
            items[i], items[j] = items[j], items[i]

# ✅ O(n log n) — встроенная
items.sort()

# ❌ O(n²) — ручной поиск
def find(items, target):
    for i, item in enumerate(items):
        if item == target:
            return i
    return -1

# ✅ O(log n) — бинарный поиск
import bisect
idx = bisect.bisect_left(sorted_items, target)
```

## Инструменты профилирования

```bash
# CPU
python -m cProfile -s time my_script.py | head -20  # встроенный
pip install py-spy && py-spy record -o profile.svg -- python my_script.py  # flamegraph

# Memory
pip install memory_profiler
python -m memory_profiler my_script.py

# Line-by-line
pip install line_profiler
kernprof -l -v my_script.py  # требует @profile декоратор
```

## Шпаргалка: что оптимизировать

| Симптом | Причина | Решение |
|---------|---------|---------|
| Долгий цикл с dot | Global lookup | Local reference |
| Много аллокаций строк | String += | join() |
| Много аллокаций list | Comprehension | Generator |
| Большой список поиск | O(n) в list | set / dict |
| Много объектов | __dict__ | __slots__ |
| Много запросов к БД | N+1 | batch / join |
| Медленный map/sort | Python loop | NumPy / builtins |
| Cache miss | Без кэша | lru_cache / Redis |
| CPU 100% в 1 ядре | GIL | multiprocessing / numba |
| Память растёт | Циклы ссылок | weakref / gc |


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
